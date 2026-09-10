from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.state import TaskStore


def contract() -> dict:
    return {
        "title": "Symlink containment regression",
        "outcome": "Run scope cannot escape the repository through a symlink.",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "Implementation choices inside declared scope.",
        "verification": "Run deterministic tests.",
        "evidence_expected": "Passing test output.",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "Stop on scope or authority ambiguity.",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": ["src"],
        "non_goals": ["No sandbox redesign."],
        "acceptance_criteria": ["Resolved write scope stays under repo root."],
        "stop_conditions": ["Scope resolution is ambiguous."],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class ScopeSymlinkContainmentTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        self.outside = self.root / "outside"
        self.outside.mkdir()
        self.store = TaskStore(self.root / "maps.db")

    def active_task(self) -> str:
        created = self.store.create_task(task_id="TASK-SYMLINK")
        self.assertTrue(created.ok, created)
        shaped = self.store.update_contract("TASK-SYMLINK", contract())
        self.assertTrue(shaped.ok, shaped)
        self.assertTrue(self.store.promote_ready("TASK-SYMLINK").ok)
        claimed = self.store.claim_task("TASK-SYMLINK", "worker", lease_seconds=600)
        self.assertTrue(claimed.ok, claimed)
        return "TASK-SYMLINK"

    def test_writable_scope_symlink_cannot_escape_repo_root(self):
        """Borrowed invariant: authorize the resolved target, not lexical path text."""
        escape = self.repo / "src" / "escape"
        escape.symlink_to(self.outside, target_is_directory=True)
        task_id = self.active_task()

        result = self.store.create_run_manifest(
            task_id,
            "worker",
            repo_root=self.repo,
            created_by="dispatcher",
            readable_paths=["."],
            writable_paths=["src/escape"],
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "INVALID_SCOPE")
        self.assertIn("escapes repo root", result.message)
        self.assertEqual(self.store.trace_task(task_id)["runs"], [])


if __name__ == "__main__":
    unittest.main()
