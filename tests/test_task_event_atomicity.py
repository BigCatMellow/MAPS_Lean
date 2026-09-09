from pathlib import Path
import sqlite3
import tempfile
import unittest

from runtime.state import TaskStore


def contract():
    return {
        "title": "Atomic task event test",
        "outcome": "Task state and semantic event commit together",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "LOW",
        "decision_authority": "bounded implementation",
        "verification": "run atomicity regression",
        "evidence_expected": "passing test",
        "review_required": "OWNER_CHECK",
        "escalation": "stop if state/event commit boundaries diverge",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": ["src/atomicity"],
        "non_goals": ["no external outbox implementation"],
        "acceptance_criteria": ["task and event roll back together"],
        "stop_conditions": ["event persistence cannot share task transaction"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class FailingEventStore(TaskStore):
    def _append_event(self, conn, task_id, event_type, actor, summary):
        raise sqlite3.OperationalError("injected task-event persistence failure")


class TaskEventAtomicityTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.db = Path(self.td.name) / "maps.db"
        self.store = TaskStore(self.db)
        created = self.store.create_task(task_id="TASK-ATOMIC")
        self.assertTrue(created.ok, created.message)
        shaped = self.store.update_contract("TASK-ATOMIC", contract())
        self.assertTrue(shaped.ok, shaped.message)
        ready = self.store.promote_ready("TASK-ATOMIC")
        self.assertTrue(ready.ok, ready.message)

    def event_count(self) -> int:
        with self.store._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS count FROM task_events WHERE task_id = ?",
                ("TASK-ATOMIC",),
            ).fetchone()
            return int(row["count"])

    def test_claim_rolls_back_if_semantic_event_append_fails(self):
        before = self.store.get_task("TASK-ATOMIC")
        before_events = self.event_count()
        self.assertEqual(before["status"], "READY")
        self.assertIsNone(before["claimed_by"])
        self.assertEqual(before["attempt"], 0)

        failing = FailingEventStore(self.db)
        with self.assertRaisesRegex(
            sqlite3.OperationalError,
            "injected task-event persistence failure",
        ):
            failing.claim_task("TASK-ATOMIC", "worker-1", lease_seconds=600)

        after = self.store.get_task("TASK-ATOMIC")
        self.assertEqual(after["status"], "READY")
        self.assertIsNone(after["claimed_by"])
        self.assertIsNone(after["lease_expires_at"])
        self.assertIsNone(after["heartbeat_at"])
        self.assertEqual(after["attempt"], 0)
        self.assertEqual(self.event_count(), before_events)


if __name__ == "__main__":
    unittest.main()
