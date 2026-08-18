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


class OperationalLessonAuthorityTests(unittest.TestCase):
    """Authority-1: operator-only promotion/retirement mechanism."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.store = TaskStore(self.root / "maps.db")

    def _seed(self, lesson_id: str) -> None:
        self.assertTrue(
            self.store.record_operational_lesson_candidate(
                lesson_record(lesson_id), created_by="observer-a"
            ).ok
        )

    def test_promote_unknown_lesson_is_rejected(self):
        result = self.store.promote_operational_lesson(
            "MISSING",
            decision_ref="decision:1",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2026-08-20T19:00:00Z",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "LESSON_NOT_FOUND")

    def test_promote_then_composed_view_reports_active(self):
        self._seed("LESSON-P1")
        result = self.store.promote_operational_lesson(
            "LESSON-P1",
            decision_ref="decision:1",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2026-08-20T19:00:00Z",
        )
        self.assertTrue(result.ok, result.message)
        self.assertEqual(result.code, "LESSON_PROMOTED")

        fetched = self.store.get_operational_lesson("LESSON-P1")
        self.assertEqual(fetched["status"], "ACTIVE")
        self.assertEqual(fetched["promotion"]["decision_ref"], "decision:1")
        self.assertEqual(fetched["promotion"]["promoted_by"], "operator-a")
        self.assertIsNone(fetched["retirement"])

    def test_promoted_lesson_no_longer_lists_as_candidate(self):
        self._seed("LESSON-P2")
        self.store.promote_operational_lesson(
            "LESSON-P2",
            decision_ref="decision:1",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2026-08-20T19:00:00Z",
        )
        listed = self.store.list_operational_lesson_candidates()
        self.assertNotIn("LESSON-P2", [item["lesson_id"] for item in listed])

    def test_repromotion_is_rejected(self):
        self._seed("LESSON-P3")
        first = self.store.promote_operational_lesson(
            "LESSON-P3",
            decision_ref="decision:1",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2026-08-20T19:00:00Z",
        )
        self.assertTrue(first.ok)
        second = self.store.promote_operational_lesson(
            "LESSON-P3",
            decision_ref="decision:2",
            promoted_by="operator-a",
            starts_at="2026-08-18T19:00:00Z",
            review_at="2026-08-21T19:00:00Z",
        )
        self.assertFalse(second.ok)
        self.assertEqual(second.code, "ALREADY_PROMOTED")

    def test_promotion_requires_actor(self):
        self._seed("LESSON-P4")
        result = self.store.promote_operational_lesson(
            "LESSON-P4",
            decision_ref="decision:1",
            promoted_by="  ",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2026-08-20T19:00:00Z",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "INVALID_ACTOR")
        self.assertEqual(self.store.get_operational_lesson("LESSON-P4")["status"], "CANDIDATE")

    def test_retire_candidate_directly_without_promotion(self):
        self._seed("LESSON-R1")
        result = self.store.retire_operational_lesson(
            "LESSON-R1",
            decision_ref="decision:1",
            retired_by="operator-b",
            retired_at="2026-08-17T19:00:00Z",
        )
        self.assertTrue(result.ok, result.message)
        fetched = self.store.get_operational_lesson("LESSON-R1")
        self.assertEqual(fetched["status"], "RETIRED")
        self.assertIsNone(fetched["promotion"])
        self.assertEqual(fetched["retirement"]["retired_by"], "operator-b")

    def test_retire_active_lesson_preserves_promotion_record(self):
        self._seed("LESSON-R2")
        self.store.promote_operational_lesson(
            "LESSON-R2",
            decision_ref="decision:1",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2026-08-20T19:00:00Z",
        )
        result = self.store.retire_operational_lesson(
            "LESSON-R2",
            decision_ref="decision:2",
            retired_by="operator-b",
            retired_at="2026-08-21T19:00:00Z",
        )
        self.assertTrue(result.ok, result.message)
        fetched = self.store.get_operational_lesson("LESSON-R2")
        self.assertEqual(fetched["status"], "RETIRED")
        self.assertIsNotNone(fetched["promotion"])
        self.assertEqual(fetched["promotion"]["decision_ref"], "decision:1")
        self.assertEqual(fetched["retirement"]["decision_ref"], "decision:2")

    def test_retirement_is_terminal_no_re_retirement(self):
        self._seed("LESSON-R3")
        first = self.store.retire_operational_lesson(
            "LESSON-R3",
            decision_ref="decision:1",
            retired_by="operator-b",
            retired_at="2026-08-17T19:00:00Z",
        )
        self.assertTrue(first.ok)
        second = self.store.retire_operational_lesson(
            "LESSON-R3",
            decision_ref="decision:2",
            retired_by="operator-b",
            retired_at="2026-08-18T19:00:00Z",
        )
        self.assertFalse(second.ok)
        self.assertEqual(second.code, "ALREADY_RETIRED")

    def test_promotion_after_retirement_is_rejected(self):
        self._seed("LESSON-R4")
        self.store.retire_operational_lesson(
            "LESSON-R4",
            decision_ref="decision:1",
            retired_by="operator-b",
            retired_at="2026-08-17T19:00:00Z",
        )
        result = self.store.promote_operational_lesson(
            "LESSON-R4",
            decision_ref="decision:2",
            promoted_by="operator-a",
            starts_at="2026-08-18T19:00:00Z",
            review_at="2026-08-21T19:00:00Z",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "LESSON_RETIRED")

    def test_composed_active_view_passes_validate_lesson_record(self):
        from runtime.operational_learning import validate_lesson_record

        self._seed("LESSON-V1")
        self.store.promote_operational_lesson(
            "LESSON-V1",
            decision_ref="decision:1",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2026-08-20T19:00:00Z",
        )
        fetched = self.store.get_operational_lesson("LESSON-V1")
        # get_operational_lesson() already re-validates internally; re-running
        # it here proves the returned dict is itself a valid input, not just
        # that the internal call succeeded.
        revalidated = validate_lesson_record(fetched)
        self.assertEqual(revalidated["status"], "ACTIVE")

    def test_decision_history_is_ordered_and_immutable_in_practice(self):
        self._seed("LESSON-D1")
        self.store.promote_operational_lesson(
            "LESSON-D1",
            decision_ref="decision:1",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2026-08-20T19:00:00Z",
        )
        self.store.retire_operational_lesson(
            "LESSON-D1",
            decision_ref="decision:2",
            retired_by="operator-b",
            retired_at="2026-08-21T19:00:00Z",
        )
        history = self.store.list_operational_lesson_decisions("LESSON-D1")
        self.assertEqual([d["decision_kind"] for d in history], ["PROMOTE", "RETIRE"])
        self.assertEqual(history[0]["decided_by"], "operator-a")
        self.assertEqual(history[1]["decided_by"], "operator-b")

    def test_direct_sql_second_promote_decision_violates_trigger(self):
        self._seed("LESSON-SQL1")
        self.store.promote_operational_lesson(
            "LESSON-SQL1",
            decision_ref="decision:1",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2026-08-20T19:00:00Z",
        )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    "INSERT INTO operational_lesson_decisions("
                    "lesson_id, decision_kind, decision_payload, decided_by, "
                    "decided_at, created_at) VALUES ("
                    "'LESSON-SQL1', 'PROMOTE', '{}', 'sneaky', "
                    "'2026-08-18T19:00:00Z', '2026-08-18T19:00:00Z')"
                )

    def test_direct_sql_decision_after_retire_violates_trigger(self):
        self._seed("LESSON-SQL2")
        self.store.retire_operational_lesson(
            "LESSON-SQL2",
            decision_ref="decision:1",
            retired_by="operator-b",
            retired_at="2026-08-17T19:00:00Z",
        )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    "INSERT INTO operational_lesson_decisions("
                    "lesson_id, decision_kind, decision_payload, decided_by, "
                    "decided_at, created_at) VALUES ("
                    "'LESSON-SQL2', 'PROMOTE', '{}', 'sneaky', "
                    "'2026-08-18T19:00:00Z', '2026-08-18T19:00:00Z')"
                )

    def test_direct_sql_decisions_are_immutable(self):
        self._seed("LESSON-SQL3")
        self.store.promote_operational_lesson(
            "LESSON-SQL3",
            decision_ref="decision:1",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2026-08-20T19:00:00Z",
        )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    "UPDATE operational_lesson_decisions SET decided_by = 'x' "
                    "WHERE lesson_id = 'LESSON-SQL3'"
                )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    "DELETE FROM operational_lesson_decisions "
                    "WHERE lesson_id = 'LESSON-SQL3'"
                )

    def test_storage0_status_check_constraint_still_holds(self):
        # Authority-1 must not have loosened Storage-0's own boundary.
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO operational_lessons(
                        lesson_id, lesson_version, status, claim, source_kind,
                        source_refs, applicability, created_by, created_at,
                        promotion, retirement, superseded_by
                    ) VALUES (
                        'LESSON-STILL-LOCKED', 1, 'ACTIVE', 'x', 'TASK_OUTCOME',
                        '["outcome:x"]', '{"global": true, "project_ids": [], "task_types": [], "risk_levels": [], "path_prefixes": []}',
                        'observer-a', '2026-08-17T19:00:00Z', NULL, NULL, NULL
                    )
                    """
                )


if __name__ == "__main__":
    unittest.main()
