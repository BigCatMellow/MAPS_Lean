from __future__ import annotations

import copy
import unittest

from runtime.operational_learning import (
    OperationalLearningError,
    project_applicable_lessons,
    validate_lesson_record,
)


NOW = "2026-08-15T21:00:00-04:00"


class OperationalLearningProjectionTests(unittest.TestCase):
    def _record(
        self,
        lesson_id: str,
        *,
        status: str = "ACTIVE",
        source_kind: str = "TASK_OUTCOME",
        applicability: dict | None = None,
        starts_at: str = "2026-08-15T20:00:00-04:00",
        review_at: str = "2026-08-20T20:00:00-04:00",
        expires_at: str | None = "2026-09-01T20:00:00-04:00",
        superseded_by: str | None = None,
    ) -> dict:
        promotion = None
        retirement = None
        if status == "ACTIVE":
            promotion = {
                "decision_ref": f"decision:{lesson_id}",
                "promoted_by": "operator-a",
                "starts_at": starts_at,
                "review_at": review_at,
                "expires_at": expires_at,
            }
        elif status == "RETIRED":
            retirement = {
                "decision_ref": f"retire:{lesson_id}",
                "retired_by": "operator-a",
                "retired_at": "2026-08-15T20:30:00-04:00",
            }
        return {
            "lesson_version": 1,
            "lesson_id": lesson_id,
            "status": status,
            "claim": f"Guidance for {lesson_id}.",
            "source_kind": source_kind,
            "source_refs": [f"outcome:{lesson_id}"],
            "applicability": applicability
            or {
                "global": False,
                "project_ids": ["PROJECT-A"],
                "task_types": [],
                "risk_levels": [],
                "path_prefixes": [],
            },
            "created_by": "observer-a",
            "created_at": "2026-08-15T19:00:00-04:00",
            "promotion": promotion,
            "superseded_by": superseded_by,
            "retirement": retirement,
        }

    @staticmethod
    def _context(**overrides) -> dict:
        context = {
            "project_id": "PROJECT-A",
            "task_type": "IMPLEMENTATION",
            "risk": "MEDIUM",
            "paths": ["runtime/example.py"],
        }
        context.update(overrides)
        return context

    @staticmethod
    def _withheld(projection: dict, lesson_id: str) -> str:
        return next(
            item["reason"]
            for item in projection["withheld"]
            if item["lesson_id"] == lesson_id
        )

    def test_candidate_is_never_projected(self):
        record = self._record(
            "LESSON-CANDIDATE",
            status="CANDIDATE",
            source_kind="NON_TASK_OBSERVATION",
        )
        projection = project_applicable_lessons(
            [record],
            self._context(),
            at=NOW,
        )
        self.assertEqual(projection["projected"], [])
        self.assertEqual(
            self._withheld(projection, "LESSON-CANDIDATE"),
            "CANDIDATE_NOT_PROMOTED",
        )

    def test_matching_active_lesson_projects_as_guidance_only(self):
        record = self._record("LESSON-ACTIVE")
        projection = project_applicable_lessons(
            [record],
            self._context(),
            at=NOW,
        )
        self.assertEqual(len(projection["projected"]), 1)
        projected = projection["projected"][0]
        self.assertEqual(projected["lesson_id"], "LESSON-ACTIVE")
        self.assertEqual(projected["authority"], "GUIDANCE_ONLY")
        self.assertEqual(
            projected["promotion_decision_ref"],
            "decision:LESSON-ACTIVE",
        )
        self.assertFalse(projection["authority"]["can_grant_task_authority"])
        self.assertFalse(projection["authority"]["can_grant_policy_authority"])
        self.assertFalse(projection["authority"]["can_promote_candidates"])

    def test_scoped_mismatch_is_withheld(self):
        record = self._record("LESSON-MISMATCH")
        projection = project_applicable_lessons(
            [record],
            self._context(project_id="PROJECT-B"),
            at=NOW,
        )
        self.assertEqual(
            self._withheld(projection, "LESSON-MISMATCH"),
            "NOT_APPLICABLE",
        )

    def test_missing_required_context_preserves_unknown(self):
        record = self._record("LESSON-UNKNOWN")
        context = self._context()
        context.pop("project_id")
        projection = project_applicable_lessons([record], context, at=NOW)
        self.assertEqual(
            self._withheld(projection, "LESSON-UNKNOWN"),
            "APPLICABILITY_UNKNOWN",
        )
        self.assertEqual(projection["coverage"]["unknown_applicability"], 1)

    def test_path_prefix_match_and_mismatch(self):
        app = {
            "global": False,
            "project_ids": [],
            "task_types": [],
            "risk_levels": [],
            "path_prefixes": ["runtime/state"],
        }
        record = self._record("LESSON-PATH", applicability=app)
        matching = project_applicable_lessons(
            [record],
            self._context(paths=["runtime/state/outcomes.py"]),
            at=NOW,
        )
        self.assertEqual(len(matching["projected"]), 1)

        mismatching = project_applicable_lessons(
            [record],
            self._context(paths=["docs/readme.md"]),
            at=NOW,
        )
        self.assertEqual(
            self._withheld(mismatching, "LESSON-PATH"),
            "NOT_APPLICABLE",
        )

    def test_global_scope_requires_explicit_global_and_no_matchers(self):
        app = {
            "global": True,
            "project_ids": [],
            "task_types": [],
            "risk_levels": [],
            "path_prefixes": [],
        }
        record = self._record("LESSON-GLOBAL", applicability=app)
        projection = project_applicable_lessons(
            [record],
            {},
            at=NOW,
        )
        self.assertEqual(len(projection["projected"]), 1)

        invalid = copy.deepcopy(record)
        invalid["applicability"]["project_ids"] = ["PROJECT-A"]
        with self.assertRaises(OperationalLearningError):
            validate_lesson_record(invalid)

    def test_active_requires_external_promotion_contract(self):
        record = self._record("LESSON-NO-PROMOTION")
        record["promotion"] = None
        with self.assertRaises(OperationalLearningError):
            validate_lesson_record(record)

    def test_candidate_cannot_smuggle_promotion_authority(self):
        record = self._record("LESSON-CAND", status="CANDIDATE")
        record["promotion"] = {
            "decision_ref": "decision:fake",
            "promoted_by": "agent-a",
            "starts_at": "2026-08-15T20:00:00-04:00",
            "review_at": "2026-08-16T20:00:00-04:00",
            "expires_at": None,
        }
        with self.assertRaises(OperationalLearningError):
            validate_lesson_record(record)

    def test_future_review_expiry_supersession_and_retirement_withhold(self):
        future = self._record(
            "LESSON-FUTURE",
            starts_at="2026-08-16T20:00:00-04:00",
            review_at="2026-08-20T20:00:00-04:00",
        )
        review_due = self._record(
            "LESSON-REVIEW",
            review_at="2026-08-15T20:30:00-04:00",
            expires_at="2026-09-01T20:00:00-04:00",
        )
        expired = self._record(
            "LESSON-EXPIRED",
            review_at="2026-09-01T20:00:00-04:00",
            expires_at="2026-08-15T20:30:00-04:00",
        )
        superseded = self._record(
            "LESSON-OLD",
            superseded_by="LESSON-NEW",
        )
        retired = self._record("LESSON-RETIRED", status="RETIRED")

        projection = project_applicable_lessons(
            [future, review_due, expired, superseded, retired],
            self._context(),
            at=NOW,
        )
        self.assertEqual(self._withheld(projection, "LESSON-FUTURE"), "NOT_STARTED")
        self.assertEqual(self._withheld(projection, "LESSON-REVIEW"), "REVIEW_DUE")
        self.assertEqual(self._withheld(projection, "LESSON-EXPIRED"), "EXPIRED")
        self.assertEqual(self._withheld(projection, "LESSON-OLD"), "SUPERSEDED")
        self.assertEqual(self._withheld(projection, "LESSON-RETIRED"), "RETIRED")

    def test_non_task_observation_can_project_only_after_external_promotion(self):
        record = self._record(
            "LESSON-NON-TASK",
            source_kind="NON_TASK_OBSERVATION",
        )
        projection = project_applicable_lessons(
            [record],
            self._context(),
            at=NOW,
        )
        self.assertEqual(len(projection["projected"]), 1)
        self.assertEqual(
            projection["projected"][0]["source_kind"],
            "NON_TASK_OBSERVATION",
        )
        self.assertEqual(
            projection["projected"][0]["promotion_decision_ref"],
            "decision:LESSON-NON-TASK",
        )

    def test_retired_candidate_does_not_require_prior_promotion(self):
        record = self._record("LESSON-DROPPED", status="RETIRED")
        validated = validate_lesson_record(record)
        self.assertIsNone(validated["promotion"])
        projection = project_applicable_lessons(
            [record],
            self._context(),
            at=NOW,
        )
        self.assertEqual(
            self._withheld(projection, "LESSON-DROPPED"),
            "RETIRED",
        )

    def test_invalid_relative_path_scope_fails_closed(self):
        record = self._record(
            "LESSON-BAD-PATH",
            applicability={
                "global": False,
                "project_ids": [],
                "task_types": [],
                "risk_levels": [],
                "path_prefixes": ["../outside"],
            },
        )
        with self.assertRaises(OperationalLearningError):
            validate_lesson_record(record)

    def test_duplicate_lesson_ids_fail_closed(self):
        first = self._record("LESSON-DUP")
        second = copy.deepcopy(first)
        second["claim"] = "Different claim."
        with self.assertRaises(OperationalLearningError):
            project_applicable_lessons(
                [first, second],
                self._context(),
                at=NOW,
            )

    def test_projection_order_is_deterministic(self):
        a = self._record("LESSON-A")
        b = self._record("LESSON-B")
        forward = project_applicable_lessons([a, b], self._context(), at=NOW)
        reverse = project_applicable_lessons([b, a], self._context(), at=NOW)
        self.assertEqual(forward, reverse)

    def test_promotion_cannot_start_before_candidate_creation(self):
        record = self._record(
            "LESSON-TIME",
            starts_at="2026-08-15T18:00:00-04:00",
            review_at="2026-08-20T20:00:00-04:00",
        )
        with self.assertRaises(OperationalLearningError):
            validate_lesson_record(record)


if __name__ == "__main__":
    unittest.main()
