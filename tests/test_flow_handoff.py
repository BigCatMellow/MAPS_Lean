from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.cli import main
from runtime.flow_handoff import flow_handoff
from runtime.state import TaskStore


def _contract() -> dict:
    return {
        "title": "Flow handoff fixture",
        "outcome": "Same-task continuity is recorded",
        "task_type": "IMPLEMENTATION",
        "owner": "worker-a",
        "risk": "LOW",
        "decision_authority": "bounded implementation",
        "verification": "flow handoff tests",
        "evidence_expected": "test output",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "operator on scope change",
        "inputs": ["README.md"],
        "sources": ["AGENTS.md"],
        "dependencies": [],
        "output_paths": ["src"],
        "non_goals": ["no verdict flow"],
        "acceptance_criteria": ["continuity link recorded"],
        "stop_conditions": ["stop before replacement claim"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class FlowHandoffTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.store = TaskStore(self.root / "maps.db")

    def _active_claimed_by(self, worker: str) -> str:
        """A task promoted to READY and claimed by ``worker`` -> ACTIVE."""
        created = self.store.create_task(title="handoff fixture")
        self.assertTrue(created.ok, created.message)
        task_id = created.task["task_id"]
        self.assertTrue(self.store.update_contract(task_id, _contract()).ok)
        self.assertTrue(self.store.promote_ready(task_id).ok)
        self.assertTrue(
            self.store.claim_task(task_id, worker, lease_seconds=600).ok
        )
        self.assertEqual(self.store.get_task(task_id)["status"], "ACTIVE")
        self.assertEqual(self.store.get_task(task_id)["claimed_by"], worker)
        return task_id

    # --- happy path ------------------------------------------------------

    def test_handoff_records_continuity_link_and_stops(self):
        task_id = self._active_claimed_by("worker-a")

        result = flow_handoff(
            self.store,
            task_id,
            from_worker="worker-a",
            to_worker="worker-b",
            reason="context exhausted, delegating continuation",
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["code"], "FLOW_HANDOFF_RECORDED")
        self.assertEqual(result["from_worker"], "worker-a")
        self.assertEqual(result["to_worker"], "worker-b")
        self.assertEqual(result["continuity_link"]["code"], "CONTINUITY_LINKED")
        self.assertEqual(
            result["next_step"]["state"], "STOPPED_BEFORE_REPLACEMENT_CLAIM"
        )
        self.assertIn("claim-recover", result["next_step"]["reason"])
        # The link is real and in {worker-a, worker-b} component.
        self.assertEqual(
            self.store.continuity_component("worker-a"), {"worker-a", "worker-b"}
        )
        # No task-state change: still ACTIVE, still claimed by worker-a.
        task = self.store.get_task(task_id)
        self.assertEqual(task["status"], "ACTIVE")
        self.assertEqual(task["claimed_by"], "worker-a")

    def test_handoff_does_not_check_lease_liveness(self):
        # A handoff normally happens *because* the outgoing session died and its
        # lease is lapsing. An expired-but-still-recorded claim is accepted.
        task_id = self._active_claimed_by("worker-a")
        with self.store._connect() as conn:
            conn.execute(
                "UPDATE tasks SET lease_expires_at = ? WHERE task_id = ?",
                ("2020-01-01T00:00:00Z", task_id),
            )

        result = flow_handoff(
            self.store,
            task_id,
            from_worker="worker-a",
            to_worker="worker-b",
            reason="dead session",
        )
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["continuity_link"]["code"], "CONTINUITY_LINKED")

    # --- review-independence consequence (end to end) -------------------

    def test_continuation_worker_cannot_claim_independent_review(self):
        task_id = self._active_claimed_by("worker-a")

        handoff = flow_handoff(
            self.store,
            task_id,
            from_worker="worker-a",
            to_worker="worker-b",
            reason="delegated continuation",
        )
        self.assertTrue(handoff["ok"], handoff)

        # worker-a still holds the claim and submits the work.
        self.assertTrue(
            self.store.submit_task(task_id, "worker-a", "work product").ok
        )

        # worker-b is now a continuation of the author (worker-a) -> cannot
        # claim independent review. flow_handoff touched no review table; this
        # falls out of the existing continuity-component walk.
        blocked = self.store.claim_review(task_id, "worker-b")
        self.assertFalse(blocked.ok)
        self.assertEqual(blocked.code, "CONTINUITY_REVIEW_FORBIDDEN")

        # A truly independent identity can still review.
        self.assertTrue(self.store.claim_review(task_id, "reviewer-c").ok)

    # --- guard failures ------------------------------------------------

    def test_not_claimant_caller_is_rejected_no_link_written(self):
        task_id = self._active_claimed_by("worker-a")

        result = flow_handoff(
            self.store,
            task_id,
            from_worker="worker-x",
            to_worker="worker-b",
            reason="not my claim",
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "preflight")
        self.assertEqual(result["step_result"]["code"], "HANDOFF_NOT_CLAIMANT")
        self.assertEqual(self.store.continuity_component("worker-x"), {"worker-x"})

    def test_non_active_task_is_rejected(self):
        created = self.store.create_task(title="never claimed")
        self.assertTrue(created.ok)
        task_id = created.task["task_id"]
        self.assertTrue(self.store.update_contract(task_id, _contract()).ok)
        self.assertTrue(self.store.promote_ready(task_id).ok)  # READY, not ACTIVE

        result = flow_handoff(
            self.store, task_id,
            from_worker="worker-a", to_worker="worker-b", reason="too early",
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "preflight")
        self.assertEqual(result["step_result"]["code"], "HANDOFF_NOT_CLAIMANT")

    def test_unknown_task_is_rejected(self):
        result = flow_handoff(
            self.store, "TASK-9999",
            from_worker="worker-a", to_worker="worker-b", reason="ghost",
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "preflight")
        self.assertEqual(result["step_result"]["code"], "NOT_FOUND")

    # --- primitive errors surfaced verbatim ---------------------------

    def test_self_handoff_rejected_by_primitive(self):
        task_id = self._active_claimed_by("worker-a")
        result = flow_handoff(
            self.store, task_id,
            from_worker="worker-a", to_worker="worker-a", reason="self",
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "continuity_link")
        self.assertEqual(result["step_result"]["code"], "INVALID_CONTINUITY_LINK")

    def test_duplicate_handoff_is_idempotent_conflict(self):
        task_id = self._active_claimed_by("worker-a")
        first = flow_handoff(
            self.store, task_id,
            from_worker="worker-a", to_worker="worker-b", reason="round one",
        )
        self.assertTrue(first["ok"], first)

        second = flow_handoff(
            self.store, task_id,
            from_worker="worker-a", to_worker="worker-b", reason="round two",
        )
        self.assertFalse(second["ok"])
        self.assertEqual(second["failed_step"], "continuity_link")
        self.assertEqual(second["step_result"]["code"], "CONTINUITY_CONFLICT")
        # Still exactly one link, first reason preserved.
        self.assertEqual(
            self.store.continuity_component("worker-a"), {"worker-a", "worker-b"}
        )

    def test_empty_reason_rejected_by_primitive(self):
        task_id = self._active_claimed_by("worker-a")
        result = flow_handoff(
            self.store, task_id,
            from_worker="worker-a", to_worker="worker-b", reason="   ",
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "continuity_link")
        self.assertEqual(result["step_result"]["code"], "INVALID_CONTINUITY_LINK")

    # --- CLI end to end ----------------------------------------------

    def test_cli_flow_handoff_end_to_end(self):
        task_id = self._active_claimed_by("worker-a")
        db = str(self.root / "maps.db")

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(
                [
                    "--db", db, "flow", "handoff", task_id,
                    "--from-worker", "worker-a",
                    "--to-worker", "worker-b",
                    "--reason", "cli handoff",
                ]
            )
        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["code"], "FLOW_HANDOFF_RECORDED")
        self.assertEqual(
            payload["next_step"]["state"], "STOPPED_BEFORE_REPLACEMENT_CLAIM"
        )
        self.assertEqual(
            self.store.continuity_component("worker-a"), {"worker-a", "worker-b"}
        )

    def test_cli_flow_handoff_guard_failure_exits_nonzero(self):
        task_id = self._active_claimed_by("worker-a")
        db = str(self.root / "maps.db")

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(
                [
                    "--db", db, "flow", "handoff", task_id,
                    "--from-worker", "worker-x",
                    "--to-worker", "worker-b",
                    "--reason", "not claimant",
                ]
            )
        self.assertEqual(code, 2)
        payload = json.loads(buffer.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["step_result"]["code"], "HANDOFF_NOT_CLAIMANT")


if __name__ == "__main__":
    unittest.main()
