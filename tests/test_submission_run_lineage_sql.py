from pathlib import Path
import sqlite3
import unittest


SCHEMA = Path(__file__).resolve().parents[1] / "runtime" / "state" / "schema.sql"


class SubmissionRunLineageSqlTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.addCleanup(self.conn.close)
        self.conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        for task_id in ("TASK-A", "TASK-B"):
            self.conn.execute(
                """
                INSERT INTO tasks(task_id, created_at, updated_at)
                VALUES (?, '2026-08-15T10:00:00Z', '2026-08-15T10:00:00Z')
                """,
                (task_id,),
            )
            self.conn.execute(
                """
                INSERT INTO task_submissions(
                    task_id, author_id, evidence, submission_count,
                    first_submitted_at, submitted_at
                ) VALUES (?, 'worker', 'evidence', 1,
                          '2026-08-15T10:01:00Z', '2026-08-15T10:01:00Z')
                """,
                (task_id,),
            )
        self.conn.execute(
            """
            INSERT INTO run_manifests(
                run_id, task_id, task_revision, worker_id,
                readable_scope, writable_scope, forbidden_scope,
                runtime_limits, created_by, created_at
            ) VALUES ('RUN-A', 'TASK-A', 'revision', 'worker',
                      '[]','[]','[]','{}','test','2026-08-15T09:59:00Z')
            """
        )

    def test_cross_task_run_link_is_rejected_even_when_attempt_exists(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                """
                INSERT INTO submission_run_links(
                    task_id, submission_count, run_id, linked_at
                ) VALUES ('TASK-B', 1, 'RUN-A', '2026-08-15T10:02:00Z')
                """
            )

    def test_nonexistent_future_attempt_is_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                """
                INSERT INTO submission_run_links(
                    task_id, submission_count, run_id, linked_at
                ) VALUES ('TASK-A', 2, 'RUN-A', '2026-08-15T10:02:00Z')
                """
            )

    def test_link_is_immutable(self):
        self.conn.execute(
            """
            INSERT INTO submission_run_links(
                task_id, submission_count, run_id, linked_at
            ) VALUES ('TASK-A', 1, 'RUN-A', '2026-08-15T10:02:00Z')
            """
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                """
                UPDATE submission_run_links
                SET run_id = 'different'
                WHERE task_id = 'TASK-A' AND submission_count = 1
                """
            )


if __name__ == "__main__":
    unittest.main()
