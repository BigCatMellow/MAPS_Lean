#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from MAP_System.scripts import task_fingerprint_pilot as base
from MAP_System.scripts import task_fingerprint_source_holdout as source


class SourceExtractionTests(unittest.TestCase):
    def test_python_extracts_docstring_and_behavior_names(self) -> None:
        text = '''"""Build a disposable local replay view."""
def query_agent_trace():
    pass
def test_drift_reports_unsafe():
    pass
'''
        description = source.python_description(text)
        self.assertIn("disposable local replay", description)
        self.assertIn("query agent trace", description)
        self.assertIn("test drift reports unsafe", description)

    def test_markdown_extracts_headings_and_first_prose(self) -> None:
        text = "# Backup Verification\n\n## Round trip\n\nAll project fields survived restore.\n"
        description = source.markdown_description(text)
        self.assertIn("Backup Verification", description)
        self.assertIn("Round trip", description)
        self.assertIn("survived restore", description)

    def test_source_fingerprint_is_bounded_and_hashed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = repo / "test_example.py"
            path.write_text('"""Example behavior."""\ndef test_example():\n    pass\n')
            result = source.source_fingerprint("test_example.py", repo)
            self.assertTrue(result["exists"])
            self.assertEqual(result["derivation"], "bounded_content_extract")
            self.assertEqual(len(result["sha256"]), 64)
            self.assertLessEqual(len(result["description"].split()), source.MAX_SOURCE_WORDS)


class RetrievalBehaviorTests(unittest.TestCase):
    def test_fuzzy_matching_handles_simple_inflection(self) -> None:
        exact, fuzzy = source.lexical_matches("resume may hang", "hung resume subprocess")
        self.assertIn("resume", exact)
        self.assertIn("hang~hung", fuzzy)

    def test_compound_query_is_bounded_and_split(self) -> None:
        parts = source.query_parts(
            "A session may already be active, or resume may hang. Which fixes cover both?"
        )
        self.assertLessEqual(len(parts), source.MAX_QUERY_PARTS)
        self.assertGreaterEqual(len(parts), 3)
        self.assertTrue(any("already be active" in part for part in parts))
        self.assertTrue(any("resume may hang" in part for part in parts))

    def test_evidence_selection_uses_distinct_proof_groups(self) -> None:
        fingerprint = {
            "source_fingerprints": [
                {"path": "MAP_System/tasks/TASK-999.json", "role": "task_scope", "description": "scope and owner", "exists": True, "sha256": "a", "derivation": "bounded_content_extract"},
                {"path": "MAP_System/scripts/fix.py", "role": "implementation", "description": "prevent duplicate reviewer claim race", "exists": True, "sha256": "b", "derivation": "bounded_content_extract"},
                {"path": "MAP_System/tests/test_fix.py", "role": "test", "description": "test duplicate reviewer claim race", "exists": True, "sha256": "c", "derivation": "bounded_content_extract"},
            ]
        }
        selected = source.diverse_sources(
            fingerprint,
            "What prevents a duplicate reviewer claim race?",
            limit=2,
        )
        groups = {source.ROLE_GROUP[item["role"]] for item in selected}
        self.assertEqual(len(groups), 2)
        self.assertIn("implementation", groups)
        self.assertIn("verification", groups)
        self.assertNotIn("task_scope", {item["role"] for item in selected})

    def test_abstention_requires_score_and_coverage(self) -> None:
        weak = source.assess_strength("unrelated historical question", 40, {"parts": []})
        self.assertEqual(weak["recommendation"], "no_strong_match")


class DevelopmentRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = base.load_json(source.REGRESSION_SPEC)
        cls.index = source.build_source_index(cls.spec)

    def test_index_has_deterministic_source_fingerprints(self) -> None:
        self.assertEqual(self.index["missing_task_ids"], [])
        self.assertTrue(self.index["fingerprints"])
        for fingerprint in self.index["fingerprints"]:
            self.assertTrue(fingerprint["source_fingerprints"])
            self.assertEqual(
                fingerprint["curation"],
                "deterministic_task_and_registered_source_extract",
            )
            self.assertTrue(
                all(item["derivation"] == "bounded_content_extract" for item in fingerprint["source_fingerprints"])
            )

    def test_known_regression_does_not_drop_task_or_source_recall(self) -> None:
        metrics = source.algorithm_metrics(self.spec, self.index)
        self.assertGreaterEqual(metrics["task_hits"], 7, metrics)
        self.assertGreaterEqual(metrics["visible_expected_sources"], 10, metrics)

    def test_regression_serialization_contains_no_manual_curation(self) -> None:
        serialized = json.dumps(self.index)
        self.assertNotIn("frozen_owner_curation", serialized)


if __name__ == "__main__":
    unittest.main()
