from pathlib import Path
import sqlite3
import unittest


SCHEMA = Path(__file__).resolve().parents[1] / "runtime" / "state" / "schema.sql"


class HelperRecoveryLineageSqlTests(unittest.TestCase):
    def test_direct_sql_cannot_create_equal_timestamp_recovery_cycle(self):
        conn = sqlite3.connect(":memory:")
        self.addCleanup(conn.close)
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO tasks(task_id, created_at, updated_at) VALUES ('TASK-1','2026-08-15T09:00:00Z','2026-08-15T09:00:00Z')"
        )
        for run_id in ("RUN-A", "RUN-B"):
            conn.execute(
                """
                INSERT INTO run_manifests(
                    run_id, task_id, task_revision, worker_id,
                    readable_scope, writable_scope, forbidden_scope,
                    runtime_limits, created_by, created_at
                ) VALUES (?, 'TASK-1', 'revision', 'worker', '[]','[]','[]','{}','test','2026-08-15T10:00:00Z')
                """,
                (run_id,),
            )
        conn.execute(
            """
            INSERT INTO run_recovery_links(
                predecessor_run_id, replacement_run_id, recovery_ref,
                evidence_ref, created_by, created_at
            ) VALUES ('RUN-A','RUN-B','incident:ab','evidence:ab','test','2026-08-15T10:01:00Z')
            """
        )
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO run_recovery_links(
                    predecessor_run_id, replacement_run_id, recovery_ref,
                    evidence_ref, created_by, created_at
                ) VALUES ('RUN-B','RUN-A','incident:ba','evidence:ba','test','2026-08-15T10:02:00Z')
                """
            )


if __name__ == "__main__":
    unittest.main()
