import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

from runtime.state import TaskStore


def full_contract():
    return {
        "title": "Immutable run",
        "outcome": "Run binding stays immutable",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "HIGH",
        "decision_authority": "bounded implementation",
        "verification": "test",
        "evidence_expected": "test output",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "operator",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": ["src"],
        "non_goals": ["none"],
        "acceptance_criteria": ["immutable"],
        "stop_conditions": ["stale contract"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class RunManifestImmutabilityTests(unittest.TestCase):
    def test_sqlite_rejects_run_manifest_and_context_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            (repo / "src").mkdir(parents=True)
            (repo / "context.md").write_text("context\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "init"], check=True, capture_output=True)
            subprocess.run(
                ["git", "-C", str(repo), "config", "user.email", "maps@example.invalid"],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "config", "user.name", "MAPS Test"],
                check=True,
                capture_output=True,
            )
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True, capture_output=True)
            subprocess.run(
                ["git", "-C", str(repo), "commit", "-m", "base"],
                check=True,
                capture_output=True,
            )
            base = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            store = TaskStore(root / "maps.db")
            created = store.create_task(title="x")
            task_id = created.task["task_id"]
            self.assertTrue(store.update_contract(task_id, full_contract()).ok)
            self.assertTrue(store.promote_ready(task_id).ok)
            self.assertTrue(store.claim_task(task_id, "worker").ok)
            run = store.create_run_manifest(
                task_id,
                "worker",
                repo_root=repo,
                created_by="dispatcher",
                context_paths=["context.md"],
                base_revision=base,
            )
            self.assertTrue(run.ok)
            run_id = run.task["run_id"]
            self.assertIsNotNone(run.task["worktree"])

            with store._connect() as conn:
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        "UPDATE run_manifests SET worker_id = 'other' WHERE run_id = ?",
                        (run_id,),
                    )
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        "UPDATE run_context_refs SET sha256 = 'x' WHERE run_id = ?",
                        (run_id,),
                    )
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        "UPDATE run_worktree_bindings SET repo_root = 'x' WHERE run_id = ?",
                        (run_id,),
                    )
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute("DELETE FROM run_manifests WHERE run_id = ?", (run_id,))
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        "DELETE FROM run_worktree_bindings WHERE run_id = ?",
                        (run_id,),
                    )


if __name__ == "__main__":
    unittest.main()
