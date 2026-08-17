from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest

from runtime.state import TaskStore
from runtime.state.common import utc_now


def lesson_record(
    lesson_id: str,
    *,
    status: str = "CANDIDATE",
    source_kind: str = "TASK_OUTCOME",
    superseded_by: str | None = None,
) -> dict:
    return {
        "lesson_version": 1,
        "lesson_id": lesson_id,
        "status": status,
        "claim": f"Guidance for {lesson_id}.",
        "source_kind": source_kind,
        "source_refs": [f"outcome:{lesson_id}"],
        "applicability": {
            "global": False,
            "project_ids": ["PROJECT-A"],
            "task_types": [],
            "risk_levels": [],
            "path_prefixes": [],
        },
        "created_by": "observer-a",
        "created_at": "2026-08-17T19:00:00Z",
        "promotion": None,
        "superseded_by": superseded_by,
        "retirement": None,
    }


class OperationalLessonStorageTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.store = TaskStore(self.root / "maps.db")

    def test_candidate_round_trips_through_storage(self):
        record = lesson_record("LESSON-001")
        result = self.store.record_operational_lesson_candidate(
            record, created_by="observer-a"
        )
        self.assertTrue(result.ok, result.message)
        self.assertEqual(result.code, "LESSON_CANDIDATE_RECORDED")

        fetched = self.store.get_operational_lesson("LESSON-001")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["lesson_id"], "LESSON-001")
        self.assertEqual(fetched["status"], "CANDIDATE")
        self.assertEqual(fetched["claim"], "Guidance for LESSON-001.")
        self.assertEqual(fetched["source_refs"], ["outcome:LESSON-001"])
        self.assertEqual(
            fetched["applicability"],
            {
                "global": False,
                "project_ids": ["PROJECT-A"],
                "task_types": [],
                "risk_levels": [],
                "path_prefixes": [],
            },
        )
        self.assertIsNone(fetched["promotion"])
        self.assertIsNone(fetched["retirement"])
        self.assertIsNone(fetched["superseded_by"])

    def test_listing_returns_only_candidates_in_created_order(self):
        first = lesson_record("LESSON-A")
        first["created_at"] = "2026-08-17T18:00:00Z"
        second = lesson_record("LESSON-B")
        second["created_at"] = "2026-08-17T19:00:00Z"

        self.assertTrue(
            self.store.record_operational_lesson_candidate(
                second, created_by="observer-a"
            ).ok
        )
        self.assertTrue(
            self.store.record_operational_lesson_candidate(
                first, created_by="observer-a"
            ).ok
        )

        listed = self.store.list_operational_lesson_candidates()
        self.assertEqual([item["lesson_id"] for item in listed], ["LESSON-A", "LESSON-B"])

    def test_non_candidate_status_is_rejected_by_python_layer(self):
        record = lesson_record("LESSON-ACTIVE", status="ACTIVE")
        record["promotion"] = {
            "decision_ref": "decision:1",
            "promoted_by": "operator-a",
            "starts_at": "2026-08-17T19:00:00Z",
            "review_at": "2026-08-20T19:00:00Z",
            "expires_at": None,
        }
        result = self.store.record_operational_lesson_candidate(
            record, created_by="observer-a"
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "LESSON_NOT_CANDIDATE")
        self.assertIsNone(self.store.get_operational_lesson("LESSON-ACTIVE"))

    def test_direct_sql_status_active_violates_schema_check(self):
        # Prove the boundary holds even bypassing the Python validation layer,
        # matching the house pattern of testing SQLite invariants directly.
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO operational_lessons(
                        lesson_id, lesson_version, status, claim, source_kind,
                        source_refs, applicability, created_by, created_at,
                        promotion, retirement, superseded_by
                    ) VALUES (
                        'LESSON-DIRECT', 1, 'ACTIVE', 'x', 'TASK_OUTCOME',
                        '["outcome:x"]', '{"global": true, "project_ids": [], "task_types": [], "risk_levels": [], "path_prefixes": []}',
                        'observer-a', '2026-08-17T19:00:00Z', NULL, NULL, NULL
                    )
                    """
                )

    def test_invalid_record_shape_is_rejected_before_any_row_written(self):
        record = lesson_record("LESSON-BAD")
        del record["claim"]
        result = self.store.record_operational_lesson_candidate(
            record, created_by="observer-a"
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "INVALID_LESSON_RECORD")
        self.assertIsNone(self.store.get_operational_lesson("LESSON-BAD"))

    def test_duplicate_lesson_id_is_rejected(self):
        record = lesson_record("LESSON-DUP")
        self.assertTrue(
            self.store.record_operational_lesson_candidate(
                record, created_by="observer-a"
            ).ok
        )
        result = self.store.record_operational_lesson_candidate(
            lesson_record("LESSON-DUP"), created_by="observer-a"
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "LESSON_ID_CONFLICT")

    def test_rows_are_immutable(self):
        record = lesson_record("LESSON-IMMUTABLE")
        self.assertTrue(
            self.store.record_operational_lesson_candidate(
                record, created_by="observer-a"
            ).ok
        )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    "UPDATE operational_lessons SET claim = 'changed' "
                    "WHERE lesson_id = 'LESSON-IMMUTABLE'"
                )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    "DELETE FROM operational_lessons WHERE lesson_id = 'LESSON-IMMUTABLE'"
                )

    def test_missing_created_by_is_rejected(self):
        result = self.store.record_operational_lesson_candidate(
            lesson_record("LESSON-NO-ACTOR"), created_by="  "
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "INVALID_ACTOR")


if __name__ == "__main__":
    unittest.main()
