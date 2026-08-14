from __future__ import annotations

import unittest

from MAP_System.scripts import task_memory_capsule_pilot as capsule
from MAP_System.scripts import task_memory_packet_selector as frozen


VALID = """# Example

## Retrieval capsule

- Purpose: Defines deterministic helper capacity accounting metadata for visible manual assignments and gives bounded readers a concise description before they inspect the full operating guide.
- Proves: The exact fields and active status values used to count a helper against available capacity, plus the owner responsible for closing the assignment.
- Applies to: MAP helper notes created by core agents for visible Codex, Claude, Pi, or local-model work.
- Does not provide: Task ownership, approval, release authority, permission to hide model work, or evidence that a helper actually completed its assignment.
- Evidence type: governing_rule
- Status: current

## Body
"""


class ParserTests(unittest.TestCase):
    def test_valid_capsule_parses(self) -> None:
        parsed, errors = capsule.parse_capsule_text(VALID)
        self.assertEqual([], errors)
        self.assertIsNotNone(parsed)
        self.assertEqual("governing_rule", parsed.evidence_type)
        self.assertGreaterEqual(parsed.word_count, 60)

    def test_missing_capsule_is_valid_fallback(self) -> None:
        parsed, errors = capsule.parse_capsule_text("# Ordinary document\n\nBody.\n")
        self.assertIsNone(parsed)
        self.assertEqual([], errors)

    def test_duplicate_heading_is_rejected(self) -> None:
        parsed, errors = capsule.parse_capsule_text(VALID + "\n## Retrieval capsule\n")
        self.assertIsNone(parsed)
        self.assertTrue(any("duplicate" in error for error in errors))

    def test_example_heading_inside_fence_is_ignored(self) -> None:
        parsed, errors = capsule.parse_capsule_text(
            VALID + "\n```md\n## Retrieval capsule\n```\n"
        )
        self.assertEqual([], errors)
        self.assertIsNotNone(parsed)

    def test_missing_unknown_and_out_of_order_fields_are_rejected(self) -> None:
        broken = VALID.replace("- Purpose:", "- Keywords:").replace(
            "- Evidence type: governing_rule\n- Status: current",
            "- Status: current\n- Evidence type: governing_rule",
        )
        parsed, errors = capsule.parse_capsule_text(broken)
        self.assertIsNone(parsed)
        self.assertTrue(any("unknown" in error for error in errors))
        self.assertTrue(any("missing" in error for error in errors))

    def test_invalid_type_status_and_short_boundary_are_rejected(self) -> None:
        broken = VALID.replace("Does not provide: Task ownership, approval, release authority, permission to hide model work, or evidence that a helper actually completed its assignment.", "Does not provide: No authority.")
        broken = broken.replace("governing_rule", "keyword_cloud").replace("current", "forever")
        _parsed, errors = capsule.parse_capsule_text(broken)
        self.assertTrue(any("invalid evidence" in error for error in errors))
        self.assertTrue(any("invalid status" in error for error in errors))
        self.assertTrue(any("meaningful boundary" in error for error in errors))

    def test_excessive_and_too_short_capsules_are_rejected(self) -> None:
        short = """# X
## Retrieval capsule
- Purpose: Finds one thing.
- Proves: One fact only.
- Applies to: This file only.
- Does not provide: Any task or release authority.
- Evidence type: procedure
- Status: current
"""
        _parsed, short_errors = capsule.parse_capsule_text(short)
        self.assertTrue(any("outside 60-120" in error for error in short_errors))
        long = VALID.replace(
            "- Purpose:",
            "- Purpose: " + "word " * 80,
        )
        _parsed, long_errors = capsule.parse_capsule_text(long)
        self.assertTrue(any("outside 60-120" in error for error in long_errors))


class ScoringTests(unittest.TestCase):
    def _capsule(self, text: str = VALID):
        parsed, errors = capsule.parse_capsule_text(text)
        self.assertEqual([], errors)
        return parsed

    def test_positive_proof_terms_raise_score_and_boundary_terms_lower_it(self) -> None:
        item = {
            "path": "guide.md",
            "base_score": 10.0,
            "role_fit": 0.0,
            "role": "artifact",
            "exists_now": 1,
            "matched_terms": [],
            "clause_matches": [],
            "linked_selected_tasks": ["TASK-001"],
            "rrf_score": 0.0,
            "global_source_rank": None,
        }
        original = capsule.parse_capsule_path
        try:
            capsule.parse_capsule_path = lambda _path: (self._capsule(), [])
            positive = capsule.augment_candidates([item], "helper capacity accounting metadata")[0]
            boundary = capsule.augment_candidates([item], "release authority approval")[0]
        finally:
            capsule.parse_capsule_path = original
        self.assertGreater(positive["base_score"], 10.0)
        self.assertLess(boundary["base_score"], positive["base_score"])
        self.assertEqual("validated_capsule", positive["capsule_provenance"])

    def test_fallback_and_allocation_remain_deterministic(self) -> None:
        candidates = [
            {
                "path": name,
                "base_score": 10.0,
                "role_fit": 0.0,
                "role": "test",
                "exists_now": 1,
                "matched_terms": ["test"],
                "clause_matches": [0],
                "linked_selected_tasks": ["TASK-001"],
                "rrf_score": 0.0,
                "global_source_rank": None,
            }
            for name in ("a.txt", "b.txt")
        ]
        augmented = capsule.augment_candidates(candidates, "test")
        self.assertTrue(all(item["capsule_provenance"] == "fallback" for item in augmented))
        first = frozen.allocate_evidence(augmented, limit=2)
        second = frozen.allocate_evidence(reversed(augmented), limit=2)
        self.assertEqual([item["path"] for item in first], [item["path"] for item in second])

    def test_status_bonus_preserves_temporal_warning(self) -> None:
        current = dict(capsule.STATUS_BONUS)
        self.assertGreater(current["current"], current["historical"])
        self.assertGreater(current["historical"], current["superseded"])


class RepositoryPilotTests(unittest.TestCase):
    def test_all_six_pilot_documents_have_valid_capsules(self) -> None:
        result = capsule.validate_pilot_documents()
        self.assertTrue(result["valid"])
        self.assertEqual(6, len(result["documents"]))
        self.assertTrue(all(item["word_count"] >= 60 for item in result["documents"]))
        guide, errors = capsule.parse_capsule_path(
            capsule.ROOT / "notes" / "retrieval-capsule-guide.md"
        )
        self.assertEqual([], errors)
        self.assertIsNotNone(guide)


if __name__ == "__main__":
    unittest.main()
