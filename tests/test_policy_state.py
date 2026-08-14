import tempfile
import unittest
from pathlib import Path

from runtime.state import TaskStore


def full_contract(**changes):
    value = {
        "title": "Policy task",
        "outcome": "A policy-gated task can be routed safely",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "bounded implementation only",
        "verification": "run tests",
        "evidence_expected": "test output",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "operator for consequential choices",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": ["runtime/policy/example.py"],
        "non_goals": ["no unrelated changes"],
        "acceptance_criteria": ["policy gate works"],
        "stop_conditions": ["stop on authority conflict"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": True,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": True,
        },
    }
    value.update(changes)
    return value


class PolicyStateTests(unittest.TestCase):
    def make_store(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return TaskStore(Path(td.name) / "maps.db")

    def test_policy_metadata_is_canonical_task_state(self):
        store = self.make_store()
        task_id = store.create_task(title="x").data["task_id"]
        result = store.update_contract(task_id, full_contract())
        self.assertTrue(result.ok)
        task = store.get_task(task_id)
        self.assertTrue(task["policy"]["destructive_action"])
        self.assertTrue(task["policy"]["paid_execution"])

    def test_operator_approval_requires_explicit_gate(self):
        store = self.make_store()
        task_id = store.create_task(title="x").data["task_id"]
        store.update_contract(task_id, full_contract())
        approval = store.record_operator_approval(
            task_id, approved_by="operator", note="approved exact destructive action"
        )
        self.assertTrue(approval.ok)
        task = store.get_task(task_id)
        self.assertEqual(task["policy"]["approved_by"], "operator")
        self.assertTrue(task["policy"]["approved_at"])

    def test_reshaping_invalidates_prior_approval(self):
        store = self.make_store()
        task_id = store.create_task(title="x").data["task_id"]
        store.update_contract(task_id, full_contract())
        store.record_operator_approval(
            task_id, approved_by="operator", note="approved version one"
        )
        store.update_contract(task_id, {"title": "changed contract"})
        task = store.get_task(task_id)
        self.assertIsNone(task["policy"]["approved_by"])
        self.assertIsNone(task["policy"]["approved_at"])

    def test_list_tasks_returns_policy_and_submission_context(self):
        store = self.make_store()
        task_id = store.create_task(title="x").data["task_id"]
        store.update_contract(task_id, full_contract(policy={
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": True,
        }))
        self.assertTrue(store.promote_ready(task_id).ok)
        self.assertTrue(store.claim_task(task_id, "worker").ok)
        self.assertTrue(store.submit_task(task_id, "worker", "tests pass").ok)
        rows = store.list_tasks(statuses=("READY_FOR_REVIEW",))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["submission"]["author_id"], "worker")
        self.assertIn("policy", rows[0])


if __name__ == "__main__":
    unittest.main()
