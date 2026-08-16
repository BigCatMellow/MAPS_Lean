from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from runtime.context_evidence import (
    EvidenceIntegrityError,
    evaluate_evidence_integrity,
    project_evidence_card,
)


CORPUS_PATH = (
    Path(__file__).resolve().parents[1]
    / "work"
    / "evals"
    / "context-builder-evidence-integrity-v1.json"
)


class ContextEvidenceScorerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
        cls.sources = {item["id"]: item for item in cls.corpus["sources"]}
        cls.cases = {item["id"]: item for item in cls.corpus["cases"]}

    def _primary_card(self, case_id: str) -> dict:
        return copy.deepcopy(self.cases[case_id]["expected_cards"][0])

    def _perfect_result(self, case: dict) -> dict:
        result = {
            "case_id": case["id"],
            "outcome": case["expected_outcome"],
            "cards": [],
        }
        if case["expected_outcome"] == "EVIDENCE":
            result["cards"] = [copy.deepcopy(case["expected_cards"][0])]
        elif case["expected_outcome"] == "DRIFT_REPORTED":
            drift = case["drift"]
            frozen = self.sources[drift["frozen_source_id"]]
            current = self.sources[drift["current_source_id"]]
            result["drift"] = {
                "frozen_source_id": frozen["id"],
                "frozen_sha256": frozen["sha256"],
                "current_source_id": current["id"],
                "current_sha256": current["sha256"],
                "same_path": frozen["path"] == current["path"],
                "hash_mismatch": frozen["sha256"] != current["sha256"],
            }
        return result

    def _perfect_results(self) -> list[dict]:
        return [self._perfect_result(case) for case in self.corpus["cases"]]

    @staticmethod
    def _case_report(report: dict, case_id: str) -> dict:
        return next(item for item in report["cases"] if item["case_id"] == case_id)

    @staticmethod
    def _python_source(content: str) -> dict:
        return {
            "id": "CB-SRC-TEST",
            "path": "runtime/test_source.py",
            "version": "current",
            "content": content,
            "sha256": hashlib.sha256(content.encode()).hexdigest(),
        }

    def test_projector_builds_exact_card_from_explicit_source(self):
        card = project_evidence_card(
            self.sources["CB-SRC-001"],
            anchor={"type": "MARKDOWN_SECTION", "value": "Review independence"},
            proof_role="ACTIVE_AUTHORITY",
            polarity="POSITIVE",
            temporal_scope="CURRENT",
        )
        self.assertEqual(card, self.cases["CBI-001"]["expected_cards"][0])

    def test_projector_resolves_exact_owned_code_symbol(self):
        card = project_evidence_card(
            self.sources["CB-SRC-003"],
            anchor={"type": "CODE_SYMBOL", "value": "ReviewMixin.claim_review"},
            proof_role="ACTIVE_MECHANICAL_GUARD",
            polarity="POSITIVE",
            temporal_scope="CURRENT",
        )
        self.assertEqual(card, self.cases["CBI-002"]["expected_cards"][0])

    def test_projector_rejects_structurally_wrong_code_symbols(self):
        cases = {
            "module-level": (
                "class ReviewMixin:\n"
                "    pass\n\n"
                "def claim_review(task_id, reviewer_id):\n"
                "    return None\n"
            ),
            "prefixed-class": (
                "class ReviewMixinOther:\n"
                "    def claim_review(self, task_id, reviewer_id):\n"
                "        return None\n"
            ),
            "prefixed-method": (
                "class ReviewMixin:\n"
                "    def claim_review_old(self, task_id, reviewer_id):\n"
                "        return None\n"
            ),
        }
        for label, content in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(EvidenceIntegrityError):
                    project_evidence_card(
                        self._python_source(content),
                        anchor={
                            "type": "CODE_SYMBOL",
                            "value": "ReviewMixin.claim_review",
                        },
                        proof_role="ACTIVE_MECHANICAL_GUARD",
                        polarity="POSITIVE",
                        temporal_scope="CURRENT",
                    )

    def test_projector_rejects_non_resolving_anchor(self):
        with self.assertRaises(EvidenceIntegrityError):
            project_evidence_card(
                self.sources["CB-SRC-001"],
                anchor={"type": "MARKDOWN_SECTION", "value": "Does not exist"},
                proof_role="ACTIVE_AUTHORITY",
                polarity="POSITIVE",
                temporal_scope="CURRENT",
            )

    def test_perfect_external_results_pass_all_cases(self):
        report = evaluate_evidence_integrity(
            self.corpus,
            self._perfect_results(),
            label="perfect",
        )
        self.assertEqual(
            report["metrics"]["cases"],
            {"total": 16, "pass": 16, "fail": 0, "incomplete": 0},
        )
        self.assertFalse(report["promotion"]["automatic"])

    def test_exact_substitute_receives_credit_only_when_returned(self):
        results = self._perfect_results()
        target = next(item for item in results if item["case_id"] == "CBI-014")
        substitute = copy.deepcopy(
            self.cases["CBI-014"]["acceptable_substitutes"][0]
        )
        substitute.pop("credit_only_if_retrieved")
        target["cards"] = [substitute]

        report = evaluate_evidence_integrity(self.corpus, results, label="substitute")
        case = self._case_report(report, "CBI-014")
        self.assertEqual(case["status"], "PASS")
        self.assertEqual(
            case["metric_states"]["acceptable_substitute_precision"],
            "PASS",
        )

    def test_malformed_substitute_is_not_credited(self):
        results = self._perfect_results()
        target = next(item for item in results if item["case_id"] == "CBI-014")
        substitute = copy.deepcopy(
            self.cases["CBI-014"]["acceptable_substitutes"][0]
        )
        substitute.pop("credit_only_if_retrieved")
        substitute["polarity"] = "NEGATIVE_BOUNDARY"
        target["cards"] = [substitute]

        report = evaluate_evidence_integrity(self.corpus, results, label="bad-sub")
        case = self._case_report(report, "CBI-014")
        self.assertEqual(case["status"], "FAIL")
        self.assertEqual(
            case["metric_states"]["acceptable_substitute_precision"],
            "FAIL",
        )

    def test_forbidden_historical_source_fails_current_case(self):
        results = self._perfect_results()
        target = next(item for item in results if item["case_id"] == "CBI-008")
        target["cards"] = [copy.deepcopy(self.cases["CBI-009"]["expected_cards"][0])]

        report = evaluate_evidence_integrity(self.corpus, results, label="stale")
        case = self._case_report(report, "CBI-008")
        self.assertEqual(case["status"], "FAIL")
        self.assertFalse(case["checks"]["no_forbidden_credit"])
        self.assertEqual(case["metric_states"]["temporal_version_accuracy"], "FAIL")

    def test_hard_negative_rejects_evidence_pollution(self):
        results = self._perfect_results()
        target = next(item for item in results if item["case_id"] == "CBI-006")
        target["outcome"] = "EVIDENCE"
        target["cards"] = [self._primary_card("CBI-001")]

        report = evaluate_evidence_integrity(self.corpus, results, label="polluted")
        case = self._case_report(report, "CBI-006")
        self.assertEqual(case["status"], "FAIL")
        self.assertEqual(
            case["metric_states"]["negative_abstention_accuracy"],
            "FAIL",
        )

    def test_drift_requires_exact_source_hash_pair(self):
        results = self._perfect_results()
        target = next(item for item in results if item["case_id"] == "CBI-012")
        target["drift"]["hash_mismatch"] = False

        report = evaluate_evidence_integrity(self.corpus, results, label="drift")
        case = self._case_report(report, "CBI-012")
        self.assertEqual(case["status"], "FAIL")
        self.assertEqual(
            case["metric_states"]["source_drift_detection_accuracy"],
            "FAIL",
        )

    def test_missing_case_is_incomplete_not_failure(self):
        results = [
            item
            for item in self._perfect_results()
            if item["case_id"] != "CBI-005"
        ]
        report = evaluate_evidence_integrity(self.corpus, results, label="missing")
        case = self._case_report(report, "CBI-005")
        self.assertEqual(case["status"], "INCOMPLETE")
        self.assertEqual(report["metrics"]["cases"]["incomplete"], 1)

    def test_explicit_unknown_preserves_incomplete(self):
        results = self._perfect_results()
        target = next(item for item in results if item["case_id"] == "CBI-005")
        target["outcome"] = "UNKNOWN"
        target["cards"] = []

        report = evaluate_evidence_integrity(self.corpus, results, label="unknown")
        case = self._case_report(report, "CBI-005")
        self.assertEqual(case["status"], "INCOMPLETE")
        self.assertEqual(
            case["metric_states"]["vocabulary_shift_case_accuracy"],
            "INCOMPLETE",
        )

    def test_extra_uncredited_card_fails_even_with_correct_primary(self):
        results = self._perfect_results()
        target = next(item for item in results if item["case_id"] == "CBI-001")
        target["cards"].append(self._primary_card("CBI-016"))

        report = evaluate_evidence_integrity(self.corpus, results, label="extra")
        case = self._case_report(report, "CBI-001")
        self.assertEqual(case["status"], "FAIL")
        self.assertFalse(case["checks"]["card_set_creditable"])

    def test_wrong_hash_is_scored_as_integrity_failure(self):
        results = self._perfect_results()
        target = next(item for item in results if item["case_id"] == "CBI-001")
        target["cards"][0]["source_sha256"] = "0" * 64

        report = evaluate_evidence_integrity(self.corpus, results, label="wrong-hash")
        case = self._case_report(report, "CBI-001")
        self.assertEqual(case["status"], "FAIL")
        self.assertEqual(case["metric_states"]["source_hash_accuracy"], "FAIL")

    def test_result_order_does_not_change_report(self):
        results = self._perfect_results()
        forward = evaluate_evidence_integrity(self.corpus, results, label="same")
        reverse = evaluate_evidence_integrity(
            self.corpus,
            list(reversed(results)),
            label="same",
        )
        self.assertEqual(forward, reverse)

    def test_unknown_result_fields_fail_closed(self):
        result = self._perfect_result(self.cases["CBI-001"])
        result["retrieval_score"] = 0.99
        with self.assertRaises(EvidenceIntegrityError):
            evaluate_evidence_integrity(
                self.corpus,
                [result],
                label="invalid",
            )


if __name__ == "__main__":
    unittest.main()
