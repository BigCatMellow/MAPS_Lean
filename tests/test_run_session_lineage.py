from __future__ import annotations

from datetime import timedelta
from pathlib import Path
import sqlite3
import tempfile
import unittest

from runtime.harness import HookDirective
from runtime.policy.harness_guard import CanonicalRunGuard
from runtime.state import TaskStore
from runtime.state.common import utc_now


def contract():
    return {
        "title": "Run session lineage",
        "outcome": "Provider session identity stays bound to one immutable run",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "HIGH",
        "decision_authority": "bounded implementation only",
        "verification": "run lineage tests",
        "evidence_expected": "test output",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "operator on authority conflict",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": ["src"],
        "non_goals": ["no task authority changes"],
        "acceptance_criteria": ["lineage is append-only"],
        "stop_conditions": ["stop on ambiguous identity"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class RunSessionLineageTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        self.store = TaskStore(self.root / "maps.db")

    def make_active(self, worker="worker"):
        created = self.store.create_task(title="x")
        self.assertTrue(created.ok)
        task_id = created.task["task_id"]
        self.assertTrue(self.store.update_contract(task_id, contract()).ok)
        self.assertTrue(self.store.promote_ready(task_id).ok)
        self.assertTrue(self.store.claim_task(task_id, worker, lease_seconds=600).ok)
        return task_id

    def make_run(self, task_id, *, worker="worker", session_id=None):
        result = self.store.create_run_manifest(
            task_id,
            worker,
            repo_root=self.repo,
            created_by="dispatcher",
            session_id=session_id,
            readable_paths=["."],
            writable_paths=["src"],
        )
        self.assertTrue(result.ok, result.message)
        return result.task

    def attach(self, run, *, session="sess-1", adapter="hcom", replaces=None, worker="worker"):
        return self.store.record_run_session_link(
            run["run_id"],
            worker,
            adapter_id=adapter,
            session_id=session,
            evidence_ref=f"provider:event:{session}",
            created_by="dispatcher",
            replaces_link_id=replaces,
        )

    def guard_context(self, task_id, run, *, session="sess-1", adapter="hcom", operation="send"):
        return {
            "operation": operation,
            "adapter_id": adapter,
            "binding": {
                "task_id": task_id,
                "run_id": run["run_id"],
                "worker_id": run["worker_id"],
                "task_revision": run["task_revision"],
                "project_id": "default",
            },
            "session_ref": {
                "adapter": adapter,
                "session_id": session,
            },
        }

    def test_legacy_resolution_preserves_unbound_and_adapter_unproven(self):
        task_id = self.make_active()
        unbound = self.make_run(task_id)
        self.assertEqual(self.store.resolve_run_session(unbound["run_id"])["state"], "UNBOUND")

        legacy = self.make_run(task_id, session_id="legacy-1")
        resolved = self.store.resolve_run_session(legacy["run_id"])
        self.assertEqual(resolved["state"], "ADAPTER_UNPROVEN")
        self.assertEqual(resolved["current"]["session_id"], "legacy-1")
        self.assertIsNone(resolved["current"]["adapter_id"])

    def test_late_attach_does_not_mutate_run_manifest_and_links_are_immutable(self):
        task_id = self.make_active()
        run = self.make_run(task_id)
        result = self.attach(run)
        self.assertTrue(result.ok, result.message)
        resolved = result.task
        self.assertEqual(resolved["state"], "EXPLICIT")
        self.assertEqual(resolved["current"]["adapter_id"], "hcom")
        self.assertEqual(resolved["current"]["session_id"], "sess-1")
        self.assertIsNone(self.store.get_run_manifest(run["run_id"])["session_id"])

        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    "UPDATE run_session_links SET session_id = 'changed' WHERE id = ?",
                    (resolved["current"]["link_id"],),
                )

    def test_bare_manifest_session_can_only_be_adapter_qualified_for_same_id(self):
        task_id = self.make_active()
        run = self.make_run(task_id, session_id="legacy-1")
        conflict = self.attach(run, session="different")
        self.assertFalse(conflict.ok)
        self.assertEqual(conflict.code, "MANIFEST_SESSION_CONFLICT")

        attached = self.attach(run, session="legacy-1")
        self.assertTrue(attached.ok, attached.message)
        self.assertEqual(attached.task["state"], "EXPLICIT")
        self.assertEqual(attached.task["current"]["adapter_id"], "hcom")

    def test_sqlite_rejects_manifest_conflicting_attach(self):
        task_id = self.make_active()
        run = self.make_run(task_id, session_id="legacy-1")
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO run_session_links(
                        run_id, relation, adapter_id, session_id,
                        replaces_link_id, evidence_ref, created_by, created_at
                    ) VALUES (?, 'ATTACH', 'hcom', 'different', NULL, ?, 'tester', ?)
                    """,
                    (run["run_id"], "provider:event:1", utc_now().isoformat()),
                )

    def test_replacement_is_linear_and_must_name_current_link(self):
        task_id = self.make_active()
        run = self.make_run(task_id)
        first = self.attach(run)
        first_id = first.task["current"]["link_id"]

        missing = self.attach(run, session="sess-2")
        self.assertFalse(missing.ok)
        self.assertEqual(missing.code, "REPLACEMENT_LINK_REQUIRED")

        second = self.attach(run, session="sess-2", replaces=first_id)
        self.assertTrue(second.ok, second.message)
        self.assertEqual(second.code, "SESSION_REPLACED")
        self.assertEqual(len(second.task["history"]), 2)
        second_id = second.task["current"]["link_id"]
        self.assertNotEqual(first_id, second_id)

        stale = self.attach(run, session="sess-3", replaces=first_id)
        self.assertFalse(stale.ok)
        self.assertEqual(stale.code, "STALE_SESSION_LINK")

    def test_sqlite_rejects_cross_run_replacement(self):
        task_id = self.make_active()
        first_run = self.make_run(task_id)
        second_run = self.make_run(task_id)
        first = self.attach(first_run)
        first_id = first.task["current"]["link_id"]
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO run_session_links(
                        run_id, relation, adapter_id, session_id,
                        replaces_link_id, evidence_ref, created_by, created_at
                    ) VALUES (?, 'REPLACE', 'hcom', 'other-session', ?, ?, 'tester', ?)
                    """,
                    (
                        second_run["run_id"],
                        first_id,
                        "provider:event:2",
                        utc_now().isoformat(),
                    ),
                )

    def test_adapter_qualified_provider_session_cannot_bind_to_two_runs(self):
        task_id = self.make_active()
        first = self.make_run(task_id)
        second = self.make_run(task_id)
        self.assertTrue(self.attach(first, session="shared").ok)
        duplicate = self.attach(second, session="shared")
        self.assertFalse(duplicate.ok)
        self.assertEqual(duplicate.code, "SESSION_ALREADY_BOUND")

    def test_worker_lease_and_revision_are_rechecked_before_recording(self):
        task_id = self.make_active()
        run = self.make_run(task_id)

        wrong_worker = self.attach(run, worker="other")
        self.assertFalse(wrong_worker.ok)
        self.assertEqual(wrong_worker.code, "RUN_WORKER_MISMATCH")

        with self.store._connect() as conn:
            conn.execute(
                "UPDATE tasks SET lease_expires_at = ? WHERE task_id = ?",
                ((utc_now() - timedelta(seconds=1)).isoformat(), task_id),
            )
        expired = self.attach(run)
        self.assertFalse(expired.ok)
        self.assertEqual(expired.code, "LEASE_EXPIRED")

        self.assertTrue(self.store.claim_task(task_id, "worker", lease_seconds=600).ok)
        with self.store._connect() as conn:
            conn.execute("UPDATE tasks SET outcome = 'changed' WHERE task_id = ?", (task_id,))
        stale = self.attach(run)
        self.assertFalse(stale.ok)
        self.assertEqual(stale.code, "RUN_STALE")

    def test_canonical_guard_requires_exact_explicit_adapter_qualified_link(self):
        task_id = self.make_active()
        run = self.make_run(task_id, session_id="sess-1")
        guard = CanonicalRunGuard(self.store, repo_root=self.repo)

        before = guard(self.guard_context(task_id, run))
        self.assertEqual(before.directive, HookDirective.DENY)
        self.assertEqual(before.annotations["guard_code"], "SESSION_ADAPTER_UNPROVEN")

        attached = self.attach(run)
        self.assertTrue(attached.ok, attached.message)
        allowed = guard(self.guard_context(task_id, run))
        self.assertEqual(allowed.directive, HookDirective.ANNOTATE)
        self.assertEqual(allowed.annotations["guard_code"], "CANONICAL_RUN_VERIFIED")

        wrong_adapter = guard(self.guard_context(task_id, run, adapter="other"))
        self.assertEqual(wrong_adapter.directive, HookDirective.DENY)
        self.assertEqual(wrong_adapter.annotations["guard_code"], "SESSION_ADAPTER_MISMATCH")

    def test_trace_projects_lineage_without_claiming_complete_external_coverage(self):
        task_id = self.make_active()
        run = self.make_run(task_id)
        self.assertTrue(self.attach(run).ok)
        trace = self.store.trace_task(task_id)
        self.assertIsNotNone(trace)
        traced_run = next(item for item in trace["runs"] if item["run_id"] == run["run_id"])
        self.assertEqual(traced_run["session_lineage"]["state"], "EXPLICIT")
        coverage = trace["coverage"]["run_session_lineage"]
        self.assertTrue(coverage["included"])
        self.assertFalse(coverage["complete"])

    def test_lineage_does_not_create_task_level_current_session_truth(self):
        task_id = self.make_active()
        run = self.make_run(task_id)
        self.assertTrue(self.attach(run).ok)
        with self.store._connect() as conn:
            columns = {
                row["name"] for row in conn.execute("PRAGMA table_info(tasks)").fetchall()
            }
        self.assertNotIn("current_session_id", columns)
        self.assertNotIn("session_id", columns)


if __name__ == "__main__":
    unittest.main()
