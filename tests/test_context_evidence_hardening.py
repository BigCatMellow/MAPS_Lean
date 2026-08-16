from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from runtime.context_evidence import EvidenceIntegrityError, evaluate_evidence_integrity


CORPUS_PATH = (
    Path(__file__).resolve().parents[1]
    / "work"
    / "evals"
    / "context-builder-evidence-integrity-v1.json"
)


class ContextEvidenceHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
        cls.cases = {item["id"]: item for item in cls.corpus["cases"]}

    def test_frozen_substitute_must_require_actual_retrieval_credit(self):
        corpus = copy.deepcopy(self.corpus)
        case = next(item for item in corpus["cases"] if item["acceptable_substitutes"])
        case["acceptable_substitutes"][0]["credit_only_if_retrieved"] = False

        with self.assertRaises(EvidenceIntegrityError):
            evaluate_evidence_integrity(corpus, [], label="invalid-substitute-contract")

    def test_unknown_candidate_cannot_hide_returned_evidence(self):
        case = self.cases["CBI-001"]
        result = {
            "case_id": case["id"],
            "outcome": "UNKNOWN",
            "cards": [copy.deepcopy(case["expected_cards"][0])],
        }

        with self.assertRaises(EvidenceIntegrityError):
            evaluate_evidence_integrity(
                self.corpus,
                [result],
                label="unknown-with-card",
            )

    def test_unknown_candidate_cannot_hide_drift_claim(self):
        drift_case = self.cases["CBI-012"]
        frozen_id = drift_case["drift"]["frozen_source_id"]
        current_id = drift_case["drift"]["current_source_id"]
        sources = {item["id"]: item for item in self.corpus["sources"]}
        frozen = sources[frozen_id]
        current = sources[current_id]
        result = {
            "case_id": drift_case["id"],
            "outcome": "UNKNOWN",
            "cards": [],
            "drift": {
                "frozen_source_id": frozen_id,
                "frozen_sha256": frozen["sha256"],
                "current_source_id": current_id,
                "current_sha256": current["sha256"],
                "same_path": frozen["path"] == current["path"],
                "hash_mismatch": frozen["sha256"] != current["sha256"],
            },
        }

        with self.assertRaises(EvidenceIntegrityError):
            evaluate_evidence_integrity(
                self.corpus,
                [result],
                label="unknown-with-drift",
            )

    def test_clean_unknown_remains_incomplete(self):
        result = {
            "case_id": "CBI-001",
            "outcome": "UNKNOWN",
            "cards": [],
        }
        report = evaluate_evidence_integrity(
            self.corpus,
            [result],
            label="clean-unknown",
        )
        case = next(item for item in report["cases"] if item["case_id"] == "CBI-001")
        self.assertEqual(case["status"], "INCOMPLETE")
        self.assertEqual(case["returned_card_count"], 0)


if __name__ == "__main__":
    unittest.main()
