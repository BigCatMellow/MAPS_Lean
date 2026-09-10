from pathlib import Path
import tempfile
import unittest

from runtime.state import TaskStore


def contract(task_id: str, dependencies: list[str]):
    return {
        "title": f"Dependency test {task_id}",
        "outcome": "Dependency readiness is deterministic",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "LOW",
        "decision_authority": "bounded implementation",
        "verification": "run dependency readiness tests",
        "evidence_expected": "passing tests",
        "review_required": "OWNER_CHECK",
        "escalation": "stop on ambiguous dependency state",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": dependencies,
        "output_paths": [f"src/{task_id.lower()}"],
        "non_goals": ["no scheduler changes"],
        "acceptance_criteria": ["dependency graph is diagnosed correctly"],
        "stop_conditions": ["dependency state is ambiguous"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class DependencyCycleReadinessTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.store = TaskStore(Path(self.td.name) / "maps.db")

    def create_tasks(self, *task_ids: str) -> None:
        for task_id in task_ids:
            created = self.store.create_task(task_id=task_id)
            self.assertTrue(created.ok, created.message)

    def shape(self, task_id: str, dependencies: list[str]) -> None:
        result = self.store.update_contract(task_id, contract(task_id, dependencies))
        self.assertTrue(result.ok, result.message)

    def test_mutual_dependency_cycle_is_a_shaping_error(self):
        self.create_tasks("TASK-A", "TASK-B")
        self.shape("TASK-A", ["TASK-B"])
        self.shape("TASK-B", ["TASK-A"])

        result = self.store.validate_ready("TASK-A")

        self.assertFalse(result.ok)
        self.assertEqual(result.agi_status, "AGI FAIL — NEEDS_SHAPING")
        self.assertIn(
            "dependency cycle detected: TASK-A -> TASK-B -> TASK-A",
            result.reasons,
        )
        self.assertEqual(
            sum(reason.startswith("dependency cycle detected:") for reason in result.reasons),
            1,
        )

    def test_reachable_nested_cycle_is_reported_from_cycle_entry(self):
        self.create_tasks("TASK-A", "TASK-B", "TASK-C")
        self.shape("TASK-A", ["TASK-B"])
        self.shape("TASK-B", ["TASK-C"])
        self.shape("TASK-C", ["TASK-B"])

        result = self.store.validate_ready("TASK-A")

        self.assertFalse(result.ok)
        self.assertEqual(result.agi_status, "AGI FAIL — NEEDS_SHAPING")
        self.assertIn(
            "dependency cycle detected: TASK-B -> TASK-C -> TASK-B",
            result.reasons,
        )

    def test_acyclic_unfinished_dependency_remains_blocked_not_malformed(self):
        self.create_tasks("TASK-A", "TASK-B")
        self.shape("TASK-A", ["TASK-B"])
        self.shape("TASK-B", [])

        result = self.store.validate_ready("TASK-A")

        self.assertFalse(result.ok)
        self.assertEqual(result.agi_status, "AGI FAIL — BLOCKED_ON_DEPENDENCY")
        self.assertEqual(
            result.reasons,
            ("dependency TASK-B is NEEDS_SHAPING, not DONE",),
        )

    def test_direct_self_dependency_keeps_existing_reason_without_cycle_duplicate(self):
        self.create_tasks("TASK-A")
        self.shape("TASK-A", ["TASK-A"])

        result = self.store.validate_ready("TASK-A")

        self.assertFalse(result.ok)
        self.assertEqual(result.agi_status, "AGI FAIL — NEEDS_SHAPING")
        self.assertIn("task cannot depend on itself", result.reasons)
        self.assertFalse(
            any(reason.startswith("dependency cycle detected:") for reason in result.reasons)
        )

    def test_missing_dependency_remains_an_ordinary_dependency_blocker(self):
        self.create_tasks("TASK-A")
        self.shape("TASK-A", ["TASK-MISSING"])

        result = self.store.validate_ready("TASK-A")

        self.assertFalse(result.ok)
        self.assertEqual(result.agi_status, "AGI FAIL — BLOCKED_ON_DEPENDENCY")
        self.assertEqual(
            result.reasons,
            ("dependency TASK-MISSING does not exist",),
        )

    def test_done_dependency_terminates_cycle_traversal(self):
        self.create_tasks("TASK-A", "TASK-B", "TASK-C")
        self.shape("TASK-A", ["TASK-B"])
        self.shape("TASK-B", ["TASK-C"])
        self.shape("TASK-C", ["TASK-B"])

        # Readiness already defines DONE as a satisfied dependency. A historical
        # malformed graph under a DONE task must not re-block a new dependent.
        with self.store._connect() as conn:
            conn.execute("UPDATE tasks SET status = 'DONE' WHERE task_id = 'TASK-B'")
            conn.commit()

        result = self.store.validate_ready("TASK-A")

        self.assertTrue(result.ok)
        self.assertEqual(result.agi_status, "AGI READY")
        self.assertEqual(result.reasons, ())


if __name__ == "__main__":
    unittest.main()
