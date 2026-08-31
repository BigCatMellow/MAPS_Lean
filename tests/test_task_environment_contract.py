from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.policy import WorkerProfile
from runtime.routing import recommend_route
from runtime.state import TaskStore


def ready_contract(**changes):
    value = {
        "title": "Environment contract storage",
        "outcome": "Task environment requirements are durable and optional.",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "bounded state-store implementation",
        "verification": "run focused tests",
        "evidence_expected": "test output",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "operator for a routing behavior change",
        "inputs": ["work/notes/environment.md"],
        "sources": ["work/notes/environment.md"],
        "dependencies": [],
        "output_paths": ["runtime/state/environment_contract.py"],
        "non_goals": ["no routing behavior change"],
        "acceptance_criteria": ["environment contract round-trips"],
        "stop_conditions": ["stop on contract conflict"],
    }
    value.update(changes)
    return value


def environment_contract(**changes):
    value = {
        "spec_ref": "environments/linux-ci.json",
        "max_age_seconds": 900,
        "required_for_routing": False,
        "allow_older_task_revision": False,
    }
    value.update(changes)
    return value


class TaskEnvironmentContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = TaskStore(Path(self.tmp.name) / "maps.db")
        created = self.store.create_task(task_id="TASK-ENV")
        self.assertTrue(created.ok, created.message)
        self.task_id = "TASK-ENV"

    def tearDown(self):
        self.tmp.cleanup()

    def shape(self, **changes):
        result = self.store.update_contract(self.task_id, ready_contract(**changes))
        self.assertTrue(result.ok, result.message)
        return result.task

    def test_absent_environment_defaults_to_none_and_does_not_block_ready(self):
        task = self.shape()
        self.assertIsNone(task["environment"])
        promoted = self.store.promote_ready(self.task_id)
        self.assertTrue(promoted.ok, promoted.message)

    def test_valid_environment_round_trips_and_defaults_optional_flags(self):
        task = self.shape(
            environment={
                "spec_ref": "environments/linux-ci.json",
                "max_age_seconds": 900,
            }
        )
        self.assertEqual(
            task["environment"],
            environment_contract(),
        )

    def test_invalid_environment_contract_is_rejected(self):
        cases = (
            (environment_contract(spec_ref="../outside.json"), "spec_ref"),
            (environment_contract(max_age_seconds=0), "max_age_seconds"),
            (environment_contract(unexpected=True), "unknown environment fields"),
            (environment_contract(required_for_routing=1), "must be boolean"),
            (environment_contract(allow_older_task_revision="false"), "must be boolean"),
        )
        for value, expected_message in cases:
            with self.subTest(value=value):
                result = self.store.update_contract(
                    self.task_id, {"environment": value}
                )
                self.assertFalse(result.ok)
                self.assertEqual(result.code, "INVALID_CONTRACT")
                self.assertIn(expected_message, result.message)

    def test_environment_none_clears_while_omission_preserves(self):
        self.shape(environment=environment_contract())
        preserved = self.store.update_contract(self.task_id, {"title": "renamed"})
        self.assertTrue(preserved.ok, preserved.message)
        self.assertEqual(preserved.task["environment"], environment_contract())
        cleared = self.store.update_contract(self.task_id, {"environment": None})
        self.assertTrue(cleared.ok, cleared.message)
        self.assertIsNone(cleared.task["environment"])

    def test_environment_contract_changes_task_revision(self):
        self.shape()
        before = self.store.compute_task_revision(self.task_id)
        first = self.store.update_contract(
            self.task_id, {"environment": environment_contract()}
        )
        self.assertTrue(first.ok, first.message)
        with_environment = self.store.compute_task_revision(self.task_id)
        self.assertNotEqual(before, with_environment)
        second = self.store.update_contract(
            self.task_id,
            {"environment": environment_contract(max_age_seconds=1800)},
        )
        self.assertTrue(second.ok, second.message)
        self.assertNotEqual(with_environment, self.store.compute_task_revision(self.task_id))

    def test_environment_contract_freezes_after_ready(self):
        self.shape(environment=environment_contract())
        self.assertTrue(self.store.promote_ready(self.task_id).ok)
        changed = self.store.update_contract(
            self.task_id,
            {"environment": environment_contract(max_age_seconds=1800)},
        )
        self.assertFalse(changed.ok)
        self.assertEqual(changed.code, "CONTRACT_FROZEN")

    def test_policy_and_environment_contract_update_together_or_not_at_all(self):
        self.shape()
        rejected = self.store.update_contract(
            self.task_id,
            {
                "policy": {"destructive_action": True},
                "environment": environment_contract(spec_ref="/outside.json"),
            },
        )
        self.assertFalse(rejected.ok)
        unchanged = self.store.get_task(self.task_id)
        self.assertFalse(unchanged["policy"]["destructive_action"])
        self.assertIsNone(unchanged["environment"])

        updated = self.store.update_contract(
            self.task_id,
            {
                "policy": {"destructive_action": True},
                "environment": environment_contract(),
            },
        )
        self.assertTrue(updated.ok, updated.message)
        self.assertTrue(updated.task["policy"]["destructive_action"])
        self.assertEqual(updated.task["environment"], environment_contract())

    def test_readiness_rejects_malformed_persisted_environment_contract(self):
        self.shape(environment=environment_contract())
        with self.store._connect() as conn:
            conn.execute(
                "UPDATE task_environment SET spec_ref = ? WHERE task_id = ?",
                ("../outside.json", self.task_id),
            )
        validation = self.store.validate_ready(self.task_id)
        self.assertFalse(validation.ok)
        self.assertTrue(
            any("invalid environment contract" in reason for reason in validation.reasons)
        )

        with self.store._connect() as conn:
            conn.execute("PRAGMA ignore_check_constraints = ON")
            conn.execute(
                """
                UPDATE task_environment
                SET spec_ref = ?, max_age_seconds = ?
                WHERE task_id = ?
                """,
                ("environments/linux-ci.json", 0, self.task_id),
            )
        validation = self.store.validate_ready(self.task_id)
        self.assertFalse(validation.ok)
        self.assertTrue(
            any("max_age_seconds" in reason for reason in validation.reasons)
        )

        with self.store._connect() as conn:
            conn.execute("PRAGMA ignore_check_constraints = ON")
            conn.execute(
                """
                UPDATE task_environment
                SET max_age_seconds = ?, required_for_routing = ?
                WHERE task_id = ?
                """,
                (900, 2, self.task_id),
            )
        validation = self.store.validate_ready(self.task_id)
        self.assertFalse(validation.ok)
        self.assertTrue(
            any("required_for_routing" in reason for reason in validation.reasons)
        )

    def test_default_environment_contract_does_not_change_missing_report_routing(self):
        # required_for_routing defaults off: a missing report stays non-blocking.
        self.shape(environment=environment_contract())
        self.assertTrue(self.store.promote_ready(self.task_id).ok)
        route = recommend_route(
            [self.store.get_task(self.task_id)], [WorkerProfile("core", "core")]
        )
        self.assertEqual(route.route, "claim_or_assign")
        self.assertEqual(route.task_id, self.task_id)

    def test_required_for_routing_holds_task_until_a_report_exists(self):
        # required_for_routing=1 is a hold (not a hard reject) when no fresh
        # report can be projected for the task (roadmap 6.24).
        self.shape(environment=environment_contract(required_for_routing=True))
        self.assertTrue(self.store.promote_ready(self.task_id).ok)
        route = recommend_route(
            [self.store.get_task(self.task_id)], [WorkerProfile("core", "core")]
        )
        self.assertEqual(route.route, "policy_gate")
        self.assertEqual(route.task_id, self.task_id)
        self.assertEqual(route.reasons, ("environment_report_required",))


if __name__ == "__main__":
    unittest.main()
