from __future__ import annotations

from datetime import timedelta
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from runtime.helpers import AiderHelper, HelperRunStore, OllamaHelper
from runtime.recovery import RecoveryStore
from runtime.state import TaskStore
from runtime.state.common import utc_now


HELP_1 = "HELP-000000000001"
HELP_2 = "HELP-000000000002"
HELP_3 = "HELP-000000000003"
HELP_4 = "HELP-000000000004"


def contract(output_paths=None):
    return {
        "title": "Helper recovery lineage",
        "outcome": "Helper/recovery relationships remain explicit evidence",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "bounded implementation",
        "verification": "lineage tests",
        "evidence_expected": "passing tests",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "stop on ambiguous lineage",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": list(output_paths or ["src", "work/helper-output.md"]),
        "non_goals": ["no task authority change"],
        "acceptance_criteria": ["relationships are append-only"],
        "stop_conditions": ["lineage identity is ambiguous"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class HelperIdentityTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.repo = Path(self.td.name) / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
        self.run_store = HelperRunStore(Path(self.td.name) / "helper-runs.json")
        self.task = {
            "task_id": "TASK-1",
            "status": "ACTIVE",
            "output_paths": ["src", "work/helper-output.md"],
        }

    def test_aider_allocates_id_before_helper_subprocess_and_preserves_it(self):
        helper = AiderHelper(
            executable="aider",
            git_executable="git",
            run_store=self.run_store,
        )
        order = []

        def fake_run(*args, **kwargs):
            order.append("helper_subprocess")

            class Result:
                returncode = 0
                stderr = ""

            return Result()

        with patch(
            "runtime.helpers.aider.new_helper_run_id",
            side_effect=lambda: order.append("allocate_id") or HELP_1,
        ), patch.object(helper, "_git_changes", side_effect=[set(), set()]), patch(
            "runtime.helpers.aider.subprocess.run", side_effect=fake_run
        ):
            result = helper.run(
                task=self.task,
                repo=self.repo,
                targets=["src/a.py"],
                message="edit",
                scope_summary="bounded",
            )

        self.assertEqual(order, ["allocate_id", "helper_subprocess"])
        self.assertEqual(result.helper_run_id, HELP_1)

    def test_ollama_allocates_id_before_health_or_generation_and_preserves_it(self):
        helper = OllamaHelper(executable="ollama", run_store=self.run_store)
        order = []

        def fake_health():
            order.append("health")

        def fake_run(*args, **kwargs):
            order.append("generation")

            class Result:
                returncode = 0
                stderr = ""
                stdout = "answer"

            return Result()

        with patch(
            "runtime.helpers.ollama.new_helper_run_id",
            side_effect=lambda: order.append("allocate_id") or HELP_2,
        ), patch.object(helper, "health", side_effect=fake_health), patch(
            "runtime.helpers.ollama.subprocess.run", side_effect=fake_run
        ):
            result = helper.run(
                task=self.task,
                repo=self.repo,
                model="qwen3:8b",
                prompt="answer",
                output_path="work/helper-output.md",
                scope_summary="bounded",
            )

        self.assertEqual(order, ["allocate_id", "health", "generation"])
        self.assertEqual(result.helper_run_id, HELP_2)

    def test_explicit_preallocated_id_is_preserved(self):
        helper = OllamaHelper(executable="ollama", run_store=self.run_store)
        with patch.object(helper, "health"), patch(
            "runtime.helpers.ollama.subprocess.run"
        ) as run:
            run.return_value.returncode = 0
            run.return_value.stderr = ""
            run.return_value.stdout = "answer"
            result = helper.run(
                task=self.task,
                repo=self.repo,
                model="qwen3:8b",
                prompt="answer",
                output_path="work/helper-output.md",
                scope_summary="bounded",
                helper_run_id=HELP_3,
            )
        self.assertEqual(result.helper_run_id, HELP_3)


class HelperRecoveryLineageTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "src-other").mkdir()
        self.store = TaskStore(self.root / "maps.db")

    def make_active(self, worker="worker", output_paths=None):
        created = self.store.create_task(title="lineage")
        self.assertTrue(created.ok)
        task_id = created.task["task_id"]
        self.assertTrue(self.store.update_contract(task_id, contract(output_paths)).ok)
        self.assertTrue(self.store.promote_ready(task_id).ok)
        self.assertTrue(self.store.claim_task(task_id, worker, lease_seconds=600).ok)
        return task_id

    def make_run(self, task_id, worker="worker", writable="src"):
        result = self.store.create_run_manifest(
            task_id,
            worker,
            repo_root=self.repo,
            created_by="dispatcher",
            readable_paths=["."],
            writable_paths=[writable],
        )
        self.assertTrue(result.ok, result.message)
        return result.task

    def insert_run(self, run_id, task_id, worker, created_at):
        revision = self.store.compute_task_revision(task_id)
        with self.store._connect() as conn:
            conn.execute(
                """
                INSERT INTO run_manifests(
                    run_id, task_id, task_revision, worker_id, session_id,
                    readable_scope, writable_scope, forbidden_scope, runtime_limits,
                    base_revision, created_by, created_at
                ) VALUES (?, ?, ?, ?, NULL, '[]','[]','[]','{}',NULL,'test',?)
                """,
                (run_id, task_id, revision, worker, created_at),
            )

    def link_helper(self, run, helper_id, **kwargs):
        return self.store.record_run_helper_link(
            run["run_id"],
            helper_id,
            kwargs.pop("worker", "worker"),
            evidence_ref=kwargs.pop(
                "evidence_ref", f"helper:invoke:{helper_id}"
            ),
            created_by=kwargs.pop("created_by", "dispatcher"),
            **kwargs,
        )

    def test_helper_link_is_relationship_only_and_immutable(self):
        task_id = self.make_active()
        run = self.make_run(task_id)
        result = self.link_helper(run, HELP_1)
        self.assertTrue(result.ok, result.message)
        self.assertEqual(result.task["run_id"], run["run_id"])
        self.assertNotIn("status", result.task)
        self.assertNotIn("summary", result.task)
        self.assertNotIn("output_paths", result.task)

        with self.store._connect() as conn:
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(run_helper_links)")
            }
        self.assertNotIn("status", columns)
        self.assertNotIn("summary", columns)
        self.assertNotIn("output_paths", columns)

        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    "UPDATE run_helper_links SET invoker_worker_id = 'other' WHERE helper_run_id = ?",
                    (HELP_1,),
                )

    def test_helper_parent_session_and_parent_helper_must_share_run(self):
        task_id = self.make_active()
        first_run = self.make_run(task_id)
        second_run = self.make_run(task_id)

        session = self.store.record_run_session_link(
            first_run["run_id"],
            "worker",
            adapter_id="hcom",
            session_id="session-1",
            evidence_ref="provider:event:1",
            created_by="dispatcher",
        )
        self.assertTrue(session.ok)
        session_link_id = session.task["current"]["link_id"]

        root = self.link_helper(
            first_run, HELP_1, parent_session_link_id=session_link_id
        )
        self.assertTrue(root.ok, root.message)
        child = self.link_helper(
            first_run, HELP_2, parent_helper_run_id=HELP_1
        )
        self.assertTrue(child.ok, child.message)

        wrong_session = self.link_helper(
            second_run, HELP_3, parent_session_link_id=session_link_id
        )
        self.assertFalse(wrong_session.ok)
        self.assertEqual(wrong_session.code, "PARENT_SESSION_MISMATCH")
        wrong_helper = self.link_helper(
            second_run, HELP_4, parent_helper_run_id=HELP_1
        )
        self.assertFalse(wrong_helper.ok)
        self.assertEqual(wrong_helper.code, "PARENT_HELPER_MISMATCH")

    def test_helper_cannot_claim_two_immediate_parents(self):
        task_id = self.make_active()
        run = self.make_run(task_id)
        session = self.store.record_run_session_link(
            run["run_id"],
            "worker",
            adapter_id="hcom",
            session_id="s1",
            evidence_ref="provider:event:1",
            created_by="dispatcher",
        )
        self.assertTrue(session.ok)
        self.assertTrue(self.link_helper(run, HELP_1).ok)
        result = self.link_helper(
            run,
            HELP_2,
            parent_session_link_id=session.task["current"]["link_id"],
            parent_helper_run_id=HELP_1,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "AMBIGUOUS_HELPER_PARENT")

    def test_helper_link_rechecks_worker_lease_and_revision(self):
        task_id = self.make_active()
        run = self.make_run(task_id)
        wrong_worker = self.link_helper(run, HELP_1, worker="other")
        self.assertFalse(wrong_worker.ok)
        self.assertEqual(wrong_worker.code, "RUN_WORKER_MISMATCH")

        with self.store._connect() as conn:
            conn.execute(
                "UPDATE tasks SET lease_expires_at = ? WHERE task_id = ?",
                ((utc_now() - timedelta(seconds=1)).isoformat(), task_id),
            )
        expired = self.link_helper(run, HELP_2)
        self.assertFalse(expired.ok)
        self.assertEqual(expired.code, "LEASE_EXPIRED")

        self.assertTrue(self.store.claim_task(task_id, "worker", lease_seconds=600).ok)
        with self.store._connect() as conn:
            conn.execute(
                "UPDATE tasks SET outcome = 'changed' WHERE task_id = ?", (task_id,)
            )
        stale = self.link_helper(run, HELP_3)
        self.assertFalse(stale.ok)
        self.assertEqual(stale.code, "RUN_STALE")

    def test_duplicate_helper_identity_is_rejected(self):
        task_id = self.make_active()
        first = self.make_run(task_id)
        second = self.make_run(task_id)
        self.assertTrue(self.link_helper(first, HELP_1).ok)
        duplicate = self.link_helper(second, HELP_1)
        self.assertFalse(duplicate.ok)
        self.assertEqual(duplicate.code, "HELPER_LINK_CONFLICT")

    def test_recovery_link_is_same_task_linear_and_does_not_touch_recovery_store(self):
        task_id = self.make_active()
        first = self.make_run(task_id)
        second = self.make_run(task_id)
        recovery_path = self.root / "recovery.json"
        RecoveryStore(recovery_path)

        result = self.store.record_run_recovery_link(
            first["run_id"],
            second["run_id"],
            recovery_ref="incident:RNS-000000000001",
            evidence_ref="recovery:decision:1",
            created_by="supervisor",
        )
        self.assertTrue(result.ok, result.message)
        self.assertFalse(recovery_path.exists())
        self.assertEqual(result.task["predecessor_run_id"], first["run_id"])
        self.assertEqual(result.task["replacement_run_id"], second["run_id"])

        third = self.make_run(task_id)
        chain = self.store.record_run_recovery_link(
            second["run_id"],
            third["run_id"],
            recovery_ref="incident:RNS-000000000002",
            evidence_ref="recovery:decision:2",
            created_by="supervisor",
        )
        self.assertTrue(chain.ok, chain.message)

        # Pin fourth's created_at to first's rather than letting it fall out
        # naturally at wall-clock speed: the assertions below intend to
        # exercise the link-uniqueness constraint (RECOVERY_LINK_CONFLICT),
        # not chronology (RECOVERY_TIME_CONFLICT). An explicit timestamp
        # equal to first's keeps fourth >= first (needed for the first
        # assertion) and <= second's real created_at (needed for the second
        # assertion) regardless of how fast the test host's clock advances
        # between make_run() calls.
        fourth_run_id = "RUN-FOURTH-BRANCH"
        self.insert_run(fourth_run_id, task_id, "worker", first["created_at"])
        fourth = {"run_id": fourth_run_id}
        branch = self.store.record_run_recovery_link(
            first["run_id"],
            fourth["run_id"],
            recovery_ref="incident:RNS-000000000003",
            evidence_ref="recovery:decision:3",
            created_by="supervisor",
        )
        self.assertFalse(branch.ok)
        self.assertEqual(branch.code, "RECOVERY_LINK_CONFLICT")

        second_predecessor = self.store.record_run_recovery_link(
            fourth["run_id"],
            second["run_id"],
            recovery_ref="incident:RNS-000000000004",
            evidence_ref="recovery:decision:4",
            created_by="supervisor",
        )
        self.assertFalse(second_predecessor.ok)
        self.assertEqual(second_predecessor.code, "RECOVERY_LINK_CONFLICT")

    def test_recovery_cross_task_and_self_links_are_rejected(self):
        first_task = self.make_active()
        first = self.make_run(first_task)
        second_task = self.make_active(
            worker="other", output_paths=["src-other"]
        )
        second = self.make_run(
            second_task, worker="other", writable="src-other"
        )

        cross = self.store.record_run_recovery_link(
            first["run_id"],
            second["run_id"],
            recovery_ref="incident:RNS-cross",
            evidence_ref="recovery:cross",
            created_by="supervisor",
        )
        self.assertFalse(cross.ok)
        self.assertEqual(cross.code, "RECOVERY_TASK_MISMATCH")

        self_link = self.store.record_run_recovery_link(
            first["run_id"],
            first["run_id"],
            recovery_ref="incident:RNS-self",
            evidence_ref="recovery:self",
            created_by="supervisor",
        )
        self.assertFalse(self_link.ok)
        self.assertEqual(self_link.code, "RECOVERY_SELF_LINK")

    def test_recovery_cycle_is_rejected_even_when_run_times_are_equal(self):
        task_id = self.make_active()
        self.insert_run("RUN-A", task_id, "worker", "2026-08-15T10:00:00Z")
        self.insert_run("RUN-B", task_id, "worker", "2026-08-15T10:00:00Z")
        first = self.store.record_run_recovery_link(
            "RUN-A",
            "RUN-B",
            recovery_ref="incident:RNS-ab",
            evidence_ref="recovery:ab",
            created_by="supervisor",
        )
        self.assertTrue(first.ok, first.message)
        cycle = self.store.record_run_recovery_link(
            "RUN-B",
            "RUN-A",
            recovery_ref="incident:RNS-ba",
            evidence_ref="recovery:ba",
            created_by="supervisor",
        )
        self.assertFalse(cycle.ok)
        self.assertEqual(cycle.code, "RECOVERY_CYCLE")

    def test_sqlite_rejects_cross_task_and_reverse_chronology_recovery(self):
        first_task = self.make_active()
        second_task = self.make_active(
            worker="other", output_paths=["src-other"]
        )
        self.insert_run("RUN-OLD", first_task, "worker", "2026-08-15T10:00:00Z")
        self.insert_run("RUN-NEW", first_task, "worker", "2026-08-15T11:00:00Z")
        self.insert_run("RUN-OTHER", second_task, "other", "2026-08-15T12:00:00Z")

        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO run_recovery_links(
                        predecessor_run_id, replacement_run_id, recovery_ref,
                        evidence_ref, created_by, created_at
                    ) VALUES ('RUN-OLD','RUN-OTHER','incident:cross','evidence:cross','test','2026-08-15T12:01:00Z')
                    """
                )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO run_recovery_links(
                        predecessor_run_id, replacement_run_id, recovery_ref,
                        evidence_ref, created_by, created_at
                    ) VALUES ('RUN-NEW','RUN-OLD','incident:reverse','evidence:reverse','test','2026-08-15T12:02:00Z')
                    """
                )

    def test_trace_projects_helper_and_recovery_as_incomplete_relationship_evidence(self):
        task_id = self.make_active()
        first = self.make_run(task_id)
        second = self.make_run(task_id)
        self.assertTrue(self.link_helper(first, HELP_1).ok)
        self.assertTrue(
            self.store.record_run_recovery_link(
                first["run_id"],
                second["run_id"],
                recovery_ref="incident:RNS-trace",
                evidence_ref="recovery:trace",
                created_by="supervisor",
            ).ok
        )

        trace = self.store.trace_task(task_id)
        first_trace = next(
            item for item in trace["runs"] if item["run_id"] == first["run_id"]
        )
        self.assertEqual(
            first_trace["helper_lineage"][0]["helper_run_id"], HELP_1
        )
        self.assertEqual(
            first_trace["recovery_lineage"][0]["replacement_run_id"],
            second["run_id"],
        )
        self.assertFalse(trace["coverage"]["run_helper_lineage"]["complete"])
        self.assertFalse(trace["coverage"]["run_recovery_lineage"]["complete"])


if __name__ == "__main__":
    unittest.main()
