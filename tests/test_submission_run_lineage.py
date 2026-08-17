from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest

from runtime.state import TaskStore
from runtime.state.common import utc_now


def contract(output_paths=None):
    return {
        "title": "Submission run lineage",
        "outcome": "Each explicit submission attempt retains exact run attribution",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "bounded implementation",
        "verification": "submission lineage tests",
        "evidence_expected": "passing tests",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "stop on ambiguous run attribution",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": list(output_paths or ["src"]),
        "non_goals": ["no inferred run attribution"],
        "acceptance_criteria": ["submission attempts retain exact run links"],
        "stop_conditions": ["run identity is ambiguous"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class SubmissionRunLineageTests(unittest.TestCase):
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
        created = self.store.create_task(title="submission")
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

    def request_changes_and_reclaim(self, task_id, worker="worker"):
        claimed = self.store.claim_review(task_id, "reviewer")
        self.assertTrue(claimed.ok, claimed.message)
        reviewed = self.store.record_review(
            task_id, "reviewer", "CHANGES_REQUESTED", "revise"
        )
        self.assertTrue(reviewed.ok, reviewed.message)
        reclaimed = self.store.claim_task(task_id, worker, lease_seconds=600)
        self.assertTrue(reclaimed.ok, reclaimed.message)

    def test_explicit_first_submission_links_attempt_one_atomically(self):
        task_id = self.make_active()
        run = self.make_run(task_id)

        result = self.store.submit_task(
            task_id, "worker", "evidence", run_id=run["run_id"]
        )

        self.assertTrue(result.ok, result.message)
        submission = self.store.get_submission(task_id)
        self.assertEqual(submission["submission_count"], 1)
        link = self.store.get_submission_run_link(task_id, 1)
        self.assertEqual(link["run_id"], run["run_id"])
        attribution = self.store.submission_run_attribution(task_id)
        self.assertTrue(attribution["complete"])
        self.assertEqual(attribution["attempts"][0]["state"], "EXPLICIT")

    def test_explicit_retry_appends_count_two_without_rewriting_count_one(self):
        task_id = self.make_active()
        run = self.make_run(task_id)
        self.assertTrue(
            self.store.submit_task(
                task_id, "worker", "first", run_id=run["run_id"]
            ).ok
        )
        first = dict(self.store.get_submission_run_link(task_id, 1))
        self.request_changes_and_reclaim(task_id)

        second_submit = self.store.submit_task(
            task_id, "worker", "second", run_id=run["run_id"]
        )

        self.assertTrue(second_submit.ok, second_submit.message)
        self.assertEqual(self.store.get_submission(task_id)["submission_count"], 2)
        self.assertEqual(self.store.get_submission_run_link(task_id, 1), first)
        second = self.store.get_submission_run_link(task_id, 2)
        self.assertEqual(second["run_id"], run["run_id"])
        self.assertEqual(len(self.store.list_submission_run_links(task_id)), 2)

    def test_omitted_run_preserves_legacy_submission_and_unknown_attribution(self):
        task_id = self.make_active()
        self.make_run(task_id)

        result = self.store.submit_task(task_id, "worker", "legacy evidence")

        self.assertTrue(result.ok, result.message)
        self.assertIsNone(self.store.get_submission_run_link(task_id, 1))
        attribution = self.store.submission_run_attribution(task_id)
        self.assertFalse(attribution["complete"])
        self.assertEqual(
            attribution["attempts"],
            [
                {
                    "submission_count": 1,
                    "state": "UNKNOWN",
                    "run_id": None,
                    "linked_at": None,
                }
            ],
        )

        trace = self.store.trace_task(task_id)
        self.assertEqual(trace["submission_run_lineage"][0]["state"], "UNKNOWN")
        self.assertFalse(trace["coverage"]["submission_run_lineage"]["complete"])

    def test_missing_explicit_run_rejects_without_submission_mutation(self):
        task_id = self.make_active()

        result = self.store.submit_task(
            task_id, "worker", "evidence", run_id="RUN-MISSING"
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "SUBMISSION_RUN_NOT_FOUND")
        self.assertEqual(self.store.get_task(task_id)["status"], "ACTIVE")
        self.assertIsNone(self.store.get_submission(task_id))
        self.assertEqual(self.store.list_submission_run_links(task_id), [])

    def test_wrong_task_run_is_rejected_without_mutation(self):
        first_task = self.make_active()
        second_task = self.make_active(
            worker="other", output_paths=["src-other"]
        )
        other_run = self.make_run(
            second_task, worker="other", writable="src-other"
        )

        result = self.store.submit_task(
            first_task, "worker", "evidence", run_id=other_run["run_id"]
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "SUBMISSION_RUN_TASK_MISMATCH")
        self.assertEqual(self.store.get_task(first_task)["status"], "ACTIVE")
        self.assertIsNone(self.store.get_submission(first_task))

    def test_old_worker_run_is_rejected_after_claim_recovery(self):
        task_id = self.make_active(worker="worker-a")
        old_run = self.make_run(task_id, worker="worker-a")
        with self.store._connect() as conn:
            conn.execute(
                "UPDATE tasks SET lease_expires_at = ? WHERE task_id = ?",
                ("2000-01-01T00:00:00Z", task_id),
            )
        recovered = self.store.claim_task(
            task_id, "worker-b", lease_seconds=600, now=utc_now()
        )
        self.assertTrue(recovered.ok, recovered.message)

        result = self.store.submit_task(
            task_id, "worker-b", "evidence", run_id=old_run["run_id"]
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "SUBMISSION_RUN_WORKER_MISMATCH")
        self.assertEqual(self.store.get_task(task_id)["status"], "ACTIVE")
        self.assertIsNone(self.store.get_submission(task_id))

    def test_stale_run_revision_is_rejected_without_mutation(self):
        task_id = self.make_active()
        run = self.make_run(task_id)
        with self.store._connect() as conn:
            conn.execute(
                "UPDATE tasks SET outcome = 'changed after run creation' WHERE task_id = ?",
                (task_id,),
            )

        result = self.store.submit_task(
            task_id, "worker", "evidence", run_id=run["run_id"]
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "SUBMISSION_RUN_STALE")
        self.assertEqual(self.store.get_task(task_id)["status"], "ACTIVE")
        self.assertIsNone(self.store.get_submission(task_id))

    def test_forced_link_insert_failure_rolls_back_submission_transaction(self):
        task_id = self.make_active()
        run = self.make_run(task_id)
        with self.store._connect() as conn:
            conn.execute(
                """
                CREATE TRIGGER test_submission_run_abort
                BEFORE INSERT ON submission_run_links
                BEGIN
                    SELECT RAISE(ABORT, 'forced test failure');
                END;
                """
            )

        result = self.store.submit_task(
            task_id, "worker", "evidence", run_id=run["run_id"]
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "SUBMISSION_RUN_LINK_CONFLICT")
        task = self.store.get_task(task_id)
        self.assertEqual(task["status"], "ACTIVE")
        self.assertEqual(task["claimed_by"], "worker")
        self.assertIsNone(self.store.get_submission(task_id))
        self.assertEqual(self.store.list_submission_run_links(task_id), [])

    def test_sqlite_rejects_cross_task_link_and_mutation(self):
        first_task = self.make_active()
        run = self.make_run(first_task)
        self.assertTrue(self.store.submit_task(first_task, "worker", "legacy").ok)

        second_task = self.make_active(
            worker="other", output_paths=["src-other"]
        )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO submission_run_links(
                        task_id, submission_count, run_id, linked_at
                    ) VALUES (?, 1, ?, '2026-08-15T12:00:00Z')
                    """,
                    (second_task, run["run_id"]),
                )

        with self.store._connect() as conn:
            conn.execute(
                """
                INSERT INTO submission_run_links(
                    task_id, submission_count, run_id, linked_at
                ) VALUES (?, 1, ?, '2026-08-15T12:00:00Z')
                """,
                (first_task, run["run_id"]),
            )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    "UPDATE submission_run_links SET run_id = 'different' WHERE task_id = ? AND submission_count = 1",
                    (first_task,),
                )

    def test_no_single_run_or_timestamp_inference(self):
        task_id = self.make_active()
        only_run = self.make_run(task_id)
        self.assertTrue(self.store.submit_task(task_id, "worker", "evidence").ok)

        attribution = self.store.submission_run_attribution(task_id)

        self.assertEqual(len(self.store.list_submission_run_links(task_id)), 0)
        self.assertEqual(attribution["attempts"][0]["state"], "UNKNOWN")
        self.assertIsNone(attribution["attempts"][0]["run_id"])
        self.assertNotEqual(attribution["attempts"][0]["run_id"], only_run["run_id"])


if __name__ == "__main__":
    unittest.main()
