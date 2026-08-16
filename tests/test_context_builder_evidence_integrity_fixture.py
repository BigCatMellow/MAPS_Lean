from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


CORPUS = (
    Path(__file__).resolve().parents[1]
    / "work"
    / "evals"
    / "context-builder-evidence-integrity-v1.json"
)


class ContextBuilderEvidenceIntegrityFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(CORPUS.read_text(encoding="utf-8"))
        cls.sources = {source["id"]: source for source in cls.data["sources"]}

    def test_frozen_identity_and_output_contract(self):
        self.assertEqual(
            self.data["version"],
            "context-builder-evidence-integrity-v1",
        )
        self.assertEqual(
            self.data["status"],
            "FROZEN_EVALUATION_INPUT_NOT_RUNTIME_AUTHORITY",
        )
        self.assertEqual(
            set(self.data["candidate_output_contract"]["outcome"]),
            {"EVIDENCE", "ABSTAIN", "DRIFT_REPORTED", "UNKNOWN"},
        )

    def test_source_ids_and_hashes_are_exact(self):
        source_list = self.data["sources"]
        self.assertEqual(len(source_list), len(self.sources))
        for source in source_list:
            observed = hashlib.sha256(source["content"].encode("utf-8")).hexdigest()
            self.assertEqual(observed, source["sha256"], source["id"])

    def test_case_ids_are_unique_and_required_classes_are_present(self):
        cases = self.data["cases"]
        case_ids = [case["id"] for case in cases]
        self.assertEqual(len(case_ids), len(set(case_ids)))
        categories = {case["category"] for case in cases}
        required = {
            "DIRECT_CURRENT",
            "PARAPHRASE",
            "VOCABULARY_SHIFT",
            "HARD_NEGATIVE",
            "TEMPORAL_CURRENT",
            "TEMPORAL_HISTORICAL",
            "AUTHORITY_STATUS",
            "NEGATIVE_BOUNDARY",
            "SOURCE_DRIFT",
            "SUBSTITUTE_CREDIT",
        }
        self.assertTrue(required.issubset(categories))

    def test_expected_cards_reference_exact_sources_hashes_and_anchors(self):
        for case in self.data["cases"]:
            for card in case.get("expected_cards", []):
                self._assert_card_resolves(case["id"], card)
            for card in case.get("acceptable_substitutes", []):
                self.assertTrue(card["credit_only_if_retrieved"], case["id"])
                self._assert_card_resolves(case["id"], card)

    def test_abstain_cases_do_not_smuggle_positive_truth(self):
        for case in self.data["cases"]:
            if case["expected_outcome"] == "ABSTAIN":
                self.assertEqual(case.get("expected_cards", []), [], case["id"])
                self.assertEqual(case.get("acceptable_substitutes", []), [], case["id"])

    def test_drift_cases_bind_same_path_but_different_hashes(self):
        drift_cases = [case for case in self.data["cases"] if "drift" in case]
        self.assertGreaterEqual(len(drift_cases), 2)
        for case in drift_cases:
            self.assertEqual(case["expected_outcome"], "DRIFT_REPORTED")
            frozen = self.sources[case["drift"]["frozen_source_id"]]
            current = self.sources[case["drift"]["current_source_id"]]
            self.assertEqual(frozen["path"], current["path"], case["id"])
            self.assertNotEqual(frozen["sha256"], current["sha256"], case["id"])
            self.assertTrue(case["drift"]["must_report_hash_mismatch"], case["id"])

    def test_forbidden_credit_sources_exist(self):
        for case in self.data["cases"]:
            for item in case.get("forbidden_credit", []):
                self.assertIn(item["source_id"], self.sources, case["id"])
                self.assertTrue(item["reason"].strip(), case["id"])

    def _assert_card_resolves(self, case_id: str, card: dict) -> None:
        source_id = card["source_id"]
        self.assertIn(source_id, self.sources, case_id)
        source = self.sources[source_id]
        self.assertEqual(card["source_sha256"], source["sha256"], case_id)

        anchor = card["anchor"]
        anchor_type = anchor["type"]
        value = anchor["value"]
        content = source["content"]

        if anchor_type == "MARKDOWN_SECTION":
            self.assertTrue(
                f"# {value}" in content or f"## {value}" in content,
                f"{case_id}: missing markdown anchor {value!r}",
            )
        elif anchor_type == "DOCUMENT_STATUS":
            self.assertIn(value, content, case_id)
        elif anchor_type == "CODE_SYMBOL":
            owner, symbol = value.rsplit(".", 1)
            self.assertIn(f"class {owner}", content, case_id)
            self.assertIn(f"def {symbol}", content, case_id)
        else:
            self.fail(f"{case_id}: unsupported anchor type {anchor_type!r}")


if __name__ == "__main__":
    unittest.main()
