#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import unittest

from MAP_System.scripts import task_fingerprint_holdout as holdout
from MAP_System.scripts import task_fingerprint_pilot as base


class TypedEvidenceRankingTests(unittest.TestCase):
    def test_evidence_roles_are_distinct(self) -> None:
        cases = {
            "MAP_System/tasks/TASK-170.json": "task_scope",
            "MAP_System/artifacts/reviews/task170-review.md": "review",
            "MAP_System/artifacts/releases/task-170-release-checklist.md": "release",
            "MAP_System/artifacts/tests/task170-parity.md": "test",
            "MAP_System/shared/decisions.md": "decision",
            "MAP_System/shared/current-state.md": "current_state",
            "MAP_System/artifacts/research/SUMMARY-170.md": "research",
            "MAP_System/notes/review-guide.md": "guide",
            "MAP_System/scripts/example.py": "implementation",
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                self.assertEqual(holdout.evidence_role(path), expected)

    def test_test_query_ranks_regression_evidence_above_scope_and_code(self) -> None:
        fingerprint = {
            "source_refs": [
                "MAP_System/tasks/TASK-999.json",
                "MAP_System/scripts/example.py",
                "MAP_System/artifacts/tests/task999-regression.md",
            ]
        }
        ranked = holdout.rank_sources(fingerprint, "Which evidence proves the regression fix passed?")
        self.assertEqual(ranked[0]["role"], "test")
        self.assertEqual(ranked[0]["path"], "MAP_System/artifacts/tests/task999-regression.md")

    def test_scope_query_ranks_task_record_above_implementation(self) -> None:
        fingerprint = {
            "source_refs": [
                "MAP_System/tasks/TASK-999.json",
                "MAP_System/scripts/example.py",
            ]
        }
        ranked = holdout.rank_sources(fingerprint, "Which task record defines the scope and owner?")
        self.assertEqual(ranked[0]["role"], "task_scope")


class FrozenHoldoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not holdout.DEFAULT_SPEC.exists():
            raise unittest.SkipTest("holdout spec has not been frozen yet")
        cls.spec = base.load_json(holdout.DEFAULT_SPEC)
        cls.index = base.build_index(cls.spec)

    def test_spec_is_valid_and_uses_eight_queries(self) -> None:
        self.assertEqual(holdout.validate_spec(self.spec), [])
        self.assertEqual(len(self.spec["queries"]), 8)

    def test_holdout_fingerprints_are_uncurated(self) -> None:
        self.assertEqual(self.index["missing_task_ids"], [])
        self.assertTrue(self.index["fingerprints"])
        self.assertTrue(
            all(item["curation"] == "deterministic_task_record" for item in self.index["fingerprints"])
        )

    def test_query_packets_hide_truth_and_meet_budget(self) -> None:
        contract = self.spec["retrieval_contract"]
        for query in self.spec["queries"]:
            results = holdout.search_index(
                self.index,
                query["question"],
                task_limit=contract["max_candidates_per_query"],
                source_limit=contract["max_sources_per_candidate"],
            )
            packet, estimate = holdout.render_query_packet(
                query,
                results,
                corpus_count=self.index["corpus_count"],
                ceiling=contract["discovery_packet_max_estimated_tokens"],
                watermark=self.index["generated_at"],
            )
            self.assertNotIn("expected_task_ids", packet)
            self.assertNotIn("expected_source_paths", packet)
            self.assertLessEqual(estimate, contract["discovery_packet_max_estimated_tokens"])

    def test_expected_sources_receive_typed_roles(self) -> None:
        for query in self.spec["queries"]:
            expected_roles = query["expected_source_roles"]
            self.assertEqual(len(expected_roles), len(query["expected_source_paths"]))
            for path, expected_role in zip(query["expected_source_paths"], expected_roles):
                self.assertEqual(holdout.evidence_role(path), expected_role)
                self.assertTrue(base.resolve_path(path).exists())


if __name__ == "__main__":
    unittest.main()
