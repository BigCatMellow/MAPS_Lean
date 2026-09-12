from pathlib import Path
import sqlite3
import tempfile
import unittest

from runtime.state import TaskStore


def contract():
    return {
        "title": "Task history retention test",
        "outcome": "Canonical task history remains immutable",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "LOW",
        "decision_authority": "bounded retention guard regression",
        "verification": "run task history retention regressions",
        "evidence_expected": "passing tests",
        "review_required": "OWNER_CHECK",
        "escalation": "stop if normal lifecycle writes require history mutation",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": ["src/history-retention"],
        "non_goals": ["no archive or purge mechanism"],
        "acceptance_criteria": ["history is immutable and tasks are not hard-deletable"],
        "stop_conditions": ["normal lifecycle cannot append events"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class TaskHistoryRetentionTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.db = Path(self.td.name) / "maps.db"
        self.store = TaskStore(self.db)
        created = self.store.create_task(task_id="TASK-HISTORY")
        self.assertTrue(created.ok, created.message)

    def test_task_events_reject_direct_update_and_delete(self):
        before = self.store.list_events("TASK-HISTORY")
        self.assertEqual([event["event_type"] for event in before], ["TASK_CREATED"])

        with self.store._connect() as conn:
            with self.assertRaisesRegex(sqlite3.IntegrityError, "task events are immutable"):
                conn.execute(
                    "UPDATE task_events SET summary = ? WHERE task_id = ?",
                    ("rewritten", "TASK-HISTORY"),
                )
            with self.assertRaisesRegex(sqlite3.IntegrityError, "task events are immutable"):
                conn.execute("DELETE FROM task_events WHERE task_id = ?", ("TASK-HISTORY",))

        self.assertEqual(self.store.list_events("TASK-HISTORY"), before)

    def test_canonical_task_rejects_direct_hard_delete(self):
        with self.store._connect() as conn:
            with self.assertRaisesRegex(
                sqlite3.IntegrityError,
                "canonical tasks cannot be hard-deleted",
            ):
                conn.execute("DELETE FROM tasks WHERE task_id = ?", ("TASK-HISTORY",))

        self.assertIsNotNone(self.store.get_task("TASK-HISTORY"))
        self.assertEqual(
            [event["event_type"] for event in self.store.list_events("TASK-HISTORY")],
            ["TASK_CREATED"],
        )

    def test_normal_lifecycle_still_appends_new_events(self):
        shaped = self.store.update_contract("TASK-HISTORY", contract())
        self.assertTrue(shaped.ok, shaped.message)
        ready = self.store.promote_ready("TASK-HISTORY")
        self.assertTrue(ready.ok, ready.message)
        claimed = self.store.claim_task("TASK-HISTORY", "worker-1", lease_seconds=600)
        self.assertTrue(claimed.ok, claimed.message)

        event_types = [
            event["event_type"] for event in self.store.list_events("TASK-HISTORY")
        ]
        self.assertEqual(
            event_types,
            [
                "TASK_CREATED",
                "TASK_POLICY_UPDATED",
                "TASK_CONTRACT_UPDATED",
                "TASK_PROMOTED_READY",
                "TASK_CLAIMED",
            ],
        )


if __name__ == "__main__":
    unittest.main()
