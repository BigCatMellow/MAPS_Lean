from __future__ import annotations

import unittest

from runtime.operational_learning import OperationalLearningError, validate_lesson_record


class OperationalLearningSchemaTests(unittest.TestCase):
    @staticmethod
    def _record() -> dict:
        return {
            "lesson_version": 1,
            "lesson_id": "LESSON-SCHEMA",
            "status": "CANDIDATE",
            "claim": "Use exact source evidence.",
            "source_kind": "RESEARCH",
            "source_refs": ["research:1"],
            "applicability": {
                "global": False,
                "project_ids": ["PROJECT-A"],
                "task_types": [],
                "risk_levels": [],
                "path_prefixes": [],
            },
            "created_by": "observer-a",
            "created_at": "2026-08-15T20:00:00-04:00",
            "promotion": None,
            "superseded_by": None,
            "retirement": None,
        }

    def test_unknown_top_level_fields_fail_closed(self):
        record = self._record()
        record["policy_override"] = True
        with self.assertRaises(OperationalLearningError):
            validate_lesson_record(record)

    def test_missing_nullable_contract_field_fails_closed(self):
        record = self._record()
        record.pop("promotion")
        with self.assertRaises(OperationalLearningError):
            validate_lesson_record(record)

    def test_non_mapping_record_fails_with_bounded_domain_error(self):
        with self.assertRaises(OperationalLearningError):
            validate_lesson_record([])  # type: ignore[arg-type]

    def test_complete_candidate_schema_remains_valid(self):
        validated = validate_lesson_record(self._record())
        self.assertEqual(validated["lesson_id"], "LESSON-SCHEMA")
        self.assertEqual(validated["status"], "CANDIDATE")
        self.assertIsNone(validated["promotion"])


if __name__ == "__main__":
    unittest.main()
