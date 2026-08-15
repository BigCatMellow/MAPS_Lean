from __future__ import annotations

from contextlib import closing, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from runtime.cli import main as cli_main
from runtime.state import TaskStore
from runtime.state.observability import redact_sensitive_text


def ready_contract() -> dict:
    return {
        "title": "Trace task",
        "outcome": "Trace reconstructs canonical task evidence.",
        "task_type": "IMPLEMENTATION",
        "owner": "owner-a",
        "risk": "MEDIUM",
        "decision_authority": "Implementation choices inside declared scope.",
        "verification": "Run trace/redaction unit tests.",
        "evidence_expected": "Passing test output.",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "Stop on scope, security, or dependency changes.",
        "inputs": ["README.md"],
        "sources": ["AGENTS.md"],
        "dependencies": [],
        "output_paths": ["out.txt"],
        "non_goals": ["Do not widen task authority."],
        "acceptance_criteria": ["Trace is read-only and reports source coverage."],
        "stop_conditions": ["Canonical evidence is unavailable."],
    }


class TraceAndRedactionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = self.root / "maps.db"
        self.store = TaskStore(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def test_sensitive_text_is_replaced_with_explicit_markers(self):
        secret = (
            "Authorization: Bearer bearer-value-123 "
            "password=hunter2 "
            "session_token=session-value "
            "secret=plain-secret "
            "api_key=sk-proj-1234567890abcdefghijkl "
            "ghp_1234567890abcdefghijklmnop"
        )
        redacted = redact_sensitive_text(secret)
        for value in (
            "bearer-value-123",
            "hunter2",
            "session-value",
            "plain-secret",
            "sk-proj-1234567890abcdefghijkl",
            "ghp_1234567890abcdefghijklmnop",
        ):
            self.assertNotIn(value, redacted)
        self.assertIn("[REDACTED:TOKEN]", redacted)
        self.assertIn("[REDACTED:SECRET]", redacted)

    def test_event_write_boundary_redacts_free_text(self):
        created = self.store.create_task(title="redaction")
        task_id = created.task["task_id"]
        with closing(self.store._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            self.store._append_event(
                conn,
                task_id,
                "TEST_EVENT",
                "tester",
                "password=hunter2 Authorization: Bearer bearer-value-123",
            )
            conn.commit()

        event = self.store.list_events(task_id)[-1]
        self.assertNotIn("hunter2", event["summary"])
        self.assertNotIn("bearer-value-123", event["summary"])
        self.assertIn("[REDACTED:", event["summary"])

    def test_diagnostic_reads_redact_older_raw_rows_without_rewriting_them(self):
        created = self.store.create_task(title="legacy diagnostic row")
        task_id = created.task["task_id"]
        with closing(self.store._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """
                INSERT INTO reviews(task_id, reviewer_id, summary, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    task_id,
                    "reviewer-a",
                    "token=old-review-secret",
                    "2026-08-15T12:00:00Z",
                ),
            )
            conn.execute(
                """
                INSERT INTO task_events(task_id, event_type, actor, summary, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    "LEGACY_EVENT",
                    "tester",
                    "secret=old-event-secret",
                    "2026-08-15T12:00:00Z",
                ),
            )
            conn.commit()

        self.assertNotIn("old-review-secret", json.dumps(self.store.list_reviews(task_id)))
        self.assertNotIn("old-event-secret", json.dumps(self.store.list_events(task_id)))

        with closing(self.store._connect()) as conn:
            stored_review = conn.execute(
                "SELECT summary FROM reviews WHERE task_id = ?", (task_id,)
            ).fetchone()["summary"]
            stored_event = conn.execute(
                "SELECT summary FROM task_events WHERE task_id = ? AND event_type = 'LEGACY_EVENT'",
                (task_id,),
            ).fetchone()["summary"]
        self.assertEqual(stored_review, "token=old-review-secret")
        self.assertEqual(stored_event, "secret=old-event-secret")

    def test_trace_is_read_only_omits_raw_submission_and_reports_gaps(self):
        (self.root / "README.md").write_text("context", encoding="utf-8")
        created = self.store.create_task()
        task_id = created.task["task_id"]
        self.assertTrue(self.store.update_contract(task_id, ready_contract()).ok)
        self.assertTrue(self.store.promote_ready(task_id, actor="shaper").ok)
        self.assertTrue(self.store.claim_task(task_id, "worker-a").ok)

        run = self.store.create_run_manifest(
            task_id,
            "worker-a",
            repo_root=self.root,
            created_by="worker-a",
            context_paths=["README.md"],
        )
        self.assertTrue(run.ok, run)

        self.assertTrue(
            self.store.submit_task(
                task_id,
                "worker-a",
                "password=submission-secret tests passed",
            ).ok
        )
        self.assertTrue(self.store.claim_review(task_id, "reviewer-b").ok)
        self.assertTrue(
            self.store.record_review(
                task_id,
                "reviewer-b",
                "CHANGES_REQUESTED",
                "Authorization: Bearer review-secret fix criterion 1",
            ).ok
        )

        before_events = self.store.list_events(task_id)
        trace = self.store.trace_task(task_id)
        after_events = self.store.list_events(task_id)

        self.assertEqual(before_events, after_events)
        self.assertIsNotNone(trace)
        self.assertEqual(trace["task_id"], task_id)
        self.assertEqual(len(trace["runs"]), 1)
        self.assertTrue(trace["submission"]["evidence"]["present"])
        self.assertFalse(trace["submission"]["evidence"]["included"])
        serialized = json.dumps(trace)
        self.assertNotIn("submission-secret", serialized)
        self.assertNotIn("review-secret", serialized)
        self.assertFalse(trace["coverage"]["communication"]["included"])
        self.assertFalse(trace["coverage"]["communication"]["complete"])
        self.assertFalse(trace["coverage"]["external_runtime_evidence"]["included"])

    def test_cli_trace_emits_json(self):
        created = self.store.create_task(title="cli trace")
        task_id = created.task["task_id"]
        output = StringIO()
        with redirect_stdout(output):
            code = cli_main(["--db", str(self.db), "trace", task_id])
        self.assertEqual(code, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["task_id"], task_id)
        self.assertEqual(
            payload["coverage"]["canonical_task_db"]["timeline_source"],
            "task_events",
        )


if __name__ == "__main__":
    unittest.main()
