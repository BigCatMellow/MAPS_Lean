import tempfile
import unittest
from pathlib import Path

from runtime.policy import HaltRecord, HaltStore, WorkerProfile, evaluate_assignment
from runtime.routing import recommend_route


def task(task_id="TASK-1", **changes):
    value = {
        "task_id": task_id,
        "project_id": "default",
        "status": "READY",
        "agi_status": "AGI READY",
        "task_type": "IMPLEMENTATION",
        "risk": "MEDIUM",
        "output_paths": ["runtime/example.py"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": True,
            "approved_by": None,
            "approved_at": None,
        },
    }
    value.update(changes)
    return value


class PolicyRoutingTests(unittest.TestCase):
    def test_worker_selection_uses_explicit_profile_not_name(self):
        cheap = WorkerProfile(
            "anything-called-claude",
            "bounded",
            supported_task_types=("IMPLEMENTATION",),
            max_risk="MEDIUM",
            cost_rank=5,
        )
        expensive = WorkerProfile(
            "qwen-that-is-core",
            "core",
            supported_task_types=("*",),
            max_risk="HIGH",
            cost_rank=20,
        )
        result = recommend_route([task()], [expensive, cheap])
        self.assertEqual(result.route, "claim_or_assign")
        self.assertEqual(result.worker_id, cheap.worker_id)

    def test_helper_is_proposed_not_auto_assigned(self):
        helper = WorkerProfile(
            "local-helper",
            "helper",
            supported_task_types=("MAINTENANCE",),
            max_risk="LOW",
            cost_rank=1,
        )
        result = recommend_route(
            [task(task_type="MAINTENANCE", risk="LOW")], [helper]
        )
        self.assertEqual(result.route, "propose_helper")

    def test_operator_policy_flag_routes_to_gate(self):
        core = WorkerProfile("core", "core", can_review=True)
        gated = task(policy={**task()["policy"], "destructive_action": True})
        result = recommend_route([gated], [core])
        self.assertEqual(result.route, "policy_gate")
        self.assertIn("destructive_action", result.reasons)

    def test_recorded_approval_allows_route(self):
        core = WorkerProfile("core", "core")
        gated = task(
            policy={
                **task()["policy"],
                "destructive_action": True,
                "approved_by": "operator",
                "approved_at": "2026-08-14T20:00:00Z",
            }
        )
        result = recommend_route([gated], [core])
        self.assertEqual(result.route, "claim_or_assign")

    def test_high_risk_narrow_worker_rejected(self):
        helper = WorkerProfile("helper", "helper", max_risk="HIGH")
        decision = evaluate_assignment(task(risk="HIGH"), helper)
        self.assertFalse(decision.allowed)
        self.assertIn("narrow_worker_high_risk", decision.reasons)

    def test_review_prefers_eligible_independent_reviewer(self):
        review_task = task(
            status="READY_FOR_REVIEW", submission={"author_id": "author"}
        )
        author = WorkerProfile("author", "core", can_review=True, cost_rank=1)
        reviewer = WorkerProfile(
            "reviewer", "helper", can_review=True, max_risk="MEDIUM", cost_rank=2
        )
        result = recommend_route([review_task], [author, reviewer])
        self.assertEqual(result.route, "review")
        self.assertEqual(result.worker_id, "reviewer")

    def test_review_waits_if_only_author_available(self):
        review_task = task(
            status="READY_FOR_REVIEW", submission={"author_id": "author"}
        )
        author = WorkerProfile("author", "core", can_review=True)
        result = recommend_route([review_task], [author])
        self.assertEqual(result.route, "wait_for_agent")

    def test_halt_paid_dispatch_still_allows_review(self):
        halt = HaltRecord(
            halt_id="h",
            state="halt_paid_dispatch",
            reason="budget",
            set_by="core",
            set_at="now",
        )
        core = WorkerProfile("core", "core")
        self.assertEqual(recommend_route([task()], [core], halt).route, "policy_gate")
        review_task = task(
            "TASK-2", status="READY_FOR_REVIEW", submission={"author_id": "author"}
        )
        reviewer = WorkerProfile("reviewer", "core", can_review=True)
        self.assertEqual(
            recommend_route([review_task], [reviewer], halt).route, "review"
        )

    def test_repair_only_blocks_non_repair(self):
        halt = HaltRecord(
            halt_id="h",
            state="repair_only",
            reason="incident",
            set_by="operator",
            set_at="now",
        )
        core = WorkerProfile("core", "core")
        self.assertEqual(recommend_route([task()], [core], halt).route, "policy_gate")
        repair = task(task_type="REPAIR")
        self.assertEqual(
            recommend_route([repair], [core], halt).route, "claim_or_assign"
        )

    def test_halt_store_is_durable_and_clear_requires_authority(self):
        with tempfile.TemporaryDirectory() as td:
            store = HaltStore(Path(td) / "halt.json")
            record = store.set(
                state="halt_paid_dispatch",
                reason="budget",
                actor="core-1",
                authority="core",
                clear_requires="operator",
            )
            self.assertEqual(store.load().halt_id, record.halt_id)
            with self.assertRaises(PermissionError):
                store.clear(actor="core-1", authority="core", reason="fixed")
            cleared = store.clear(actor="human", authority="operator", reason="fixed")
            self.assertEqual(cleared.state, "clear")

    def test_idle_route(self):
        worker = WorkerProfile("core", "core")
        self.assertEqual(recommend_route([], [worker]).route, "wait_or_reconcile")


if __name__ == "__main__":
    unittest.main()
