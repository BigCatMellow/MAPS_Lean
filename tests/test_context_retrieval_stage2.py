import copy
import json
from pathlib import Path
import unittest

from runtime.context_retrieval_eval import (
    RetrievalEvaluationError,
    evaluate_source_rankings,
    explicit_only_rankings,
    lexical_negative_control_rankings,
    run_stage2_controls,
    same_path_drift_rankings,
)


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "work" / "evals" / "context-builder-evidence-integrity-v1.json"
OVERLAY_PATH = ROOT / "work" / "evals" / "context-builder-retrieval-stage2-v1.json"


class ContextRetrievalStage2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
        cls.overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
        cls.cases = {item["id"]: item for item in cls.corpus["cases"]}

    @staticmethod
    def _index(predictions):
        return {item["case_id"]: item["source_ids"] for item in predictions}

    def _ideal_predictions(self):
        predictions = []
        explicit = {
            item["case_id"]: item["explicit_source_ids"]
            for item in self.overlay["cases"]
        }
        for case in self.corpus["cases"]:
            if case["expected_outcome"] == "ABSTAIN":
                source_ids = []
            elif case["expected_outcome"] == "DRIFT_REPORTED":
                source_ids = [
                    case["drift"]["frozen_source_id"],
                    case["drift"]["current_source_id"],
                ]
            else:
                source_ids = [case["expected_cards"][0]["source_id"]]
            # This fixture represents an ideal externally supplied candidate,
            # not a production retriever. Preserve any frozen explicit prefix.
            prefix = explicit[case["id"]]
            source_ids = list(prefix) + [x for x in source_ids if x not in prefix]
            predictions.append({"case_id": case["id"], "source_ids": source_ids})
        return predictions

    def test_explicit_only_preserves_frozen_explicit_inputs(self):
        selected = self._index(explicit_only_rankings(self.corpus, self.overlay))

        self.assertEqual(selected["CBI-001"], ["CB-SRC-001"])
        self.assertEqual(selected["CBI-004"], [])
        self.assertEqual(selected["CBI-012"], ["CB-SRC-011"])
        self.assertEqual(selected["CBI-016"], ["CB-SRC-007"])

    def test_same_path_drift_control_adds_current_sibling_only_for_stale_explicit_source(self):
        selected = self._index(same_path_drift_rankings(self.corpus, self.overlay))

        self.assertEqual(selected["CBI-012"], ["CB-SRC-011", "CB-SRC-007"])
        self.assertEqual(selected["CBI-013"], ["CB-SRC-012", "CB-SRC-006"])
        # Current explicit evidence is not polluted by a frozen sibling merely
        # because the same repository path also exists in history.
        self.assertEqual(selected["CBI-016"], ["CB-SRC-007"])

    def test_lexical_negative_control_false_activates_hard_negatives(self):
        selected = self._index(
            lexical_negative_control_rankings(self.corpus, self.overlay)
        )

        self.assertTrue(selected["CBI-006"])
        self.assertTrue(selected["CBI-007"])
        # The corpus intentionally contains tempting lexical overlap for these
        # no-answer questions; selecting a source is therefore unsafe behavior.
        report = evaluate_source_rankings(
            self.corpus,
            self.overlay,
            lexical_negative_control_rankings(self.corpus, self.overlay),
            label="lexical-negative-control-test",
        )
        self.assertLess(report["metrics"]["hard_negative_abstention_accuracy"], 1.0)
        self.assertFalse(
            report["candidate_gate"]["gates"][
                "hard_negative_abstention_perfect"
            ]
        )

    def test_control_comparison_shows_structural_drift_gain_without_promoting_lexical(self):
        report = run_stage2_controls(self.corpus, self.overlay)
        explicit = report["controls"]["explicit_only"]
        drift = report["controls"]["same_path_drift"]
        lexical = report["controls"]["lexical_negative_control"]

        self.assertEqual(explicit["metrics"]["drift_pair_recall"], 0.0)
        self.assertEqual(drift["metrics"]["drift_pair_recall"], 1.0)
        self.assertFalse(lexical["candidate_gate"]["eligible_for_proposal"])
        self.assertIn("negative control", lexical["candidate_gate"]["forced_non_candidate_reason"])
        self.assertFalse(report["promotion"]["automatic"])

    def test_future_external_candidate_can_use_same_evaluator(self):
        report = evaluate_source_rankings(
            self.corpus,
            self.overlay,
            self._ideal_predictions(),
            label="ideal-external-candidate-contract-test",
        )

        self.assertTrue(report["candidate_gate"]["eligible_for_proposal"])
        self.assertFalse(report["candidate_gate"]["automatic_promotion"])
        self.assertEqual(report["metrics"]["hard_negative_abstention_accuracy"], 1.0)
        self.assertEqual(report["metrics"]["evidence_source_recall"], 1.0)
        self.assertEqual(report["metrics"]["evidence_source_precision"], 1.0)
        self.assertEqual(report["metrics"]["drift_pair_recall"], 1.0)

    def test_source_pollution_blocks_future_candidate_proposal(self):
        predictions = self._ideal_predictions()
        polluted = next(
            item for item in predictions if item["case_id"] == "CBI-004"
        )
        self.assertNotIn("CB-SRC-006", polluted["source_ids"])
        polluted["source_ids"].append("CB-SRC-006")

        report = evaluate_source_rankings(
            self.corpus,
            self.overlay,
            predictions,
            label="polluted-external-candidate",
        )

        self.assertEqual(report["metrics"]["evidence_source_recall"], 1.0)
        self.assertLess(report["metrics"]["evidence_source_precision"], 1.0)
        self.assertFalse(
            report["candidate_gate"]["gates"]["evidence_precision_perfect"]
        )
        self.assertFalse(report["candidate_gate"]["eligible_for_proposal"])

    def test_overlay_must_cover_every_case_and_reference_known_sources(self):
        overlay = copy.deepcopy(self.overlay)
        overlay["cases"].pop()
        with self.assertRaises(RetrievalEvaluationError):
            explicit_only_rankings(self.corpus, overlay)

        overlay = copy.deepcopy(self.overlay)
        overlay["cases"][0]["explicit_source_ids"] = ["CB-SRC-NOT-REAL"]
        with self.assertRaises(RetrievalEvaluationError):
            explicit_only_rankings(self.corpus, overlay)

    def test_predictions_fail_closed_on_missing_unknown_or_duplicate_sources(self):
        predictions = explicit_only_rankings(self.corpus, self.overlay)
        with self.assertRaises(RetrievalEvaluationError):
            evaluate_source_rankings(
                self.corpus,
                self.overlay,
                predictions[:-1],
                label="missing-case",
            )

        unknown = copy.deepcopy(predictions)
        unknown[0]["source_ids"] = ["CB-SRC-NOT-REAL"]
        with self.assertRaises(RetrievalEvaluationError):
            evaluate_source_rankings(
                self.corpus,
                self.overlay,
                unknown,
                label="unknown-source",
            )

        duplicate = copy.deepcopy(predictions)
        duplicate[0]["source_ids"] = ["CB-SRC-001", "CB-SRC-001"]
        with self.assertRaises(RetrievalEvaluationError):
            evaluate_source_rankings(
                self.corpus,
                self.overlay,
                duplicate,
                label="duplicate-source",
            )

    def test_retrieval_report_never_claims_runtime_or_automatic_authority(self):
        report = run_stage2_controls(self.corpus, self.overlay)

        self.assertFalse(report["promotion"]["automatic"])
        for control in report["controls"].values():
            self.assertFalse(control["candidate_gate"]["automatic_promotion"])


if __name__ == "__main__":
    unittest.main()
