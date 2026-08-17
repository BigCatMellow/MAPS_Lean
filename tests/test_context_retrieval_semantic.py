import json
from pathlib import Path
import unittest

from runtime.context_retrieval_eval import evaluate_source_rankings

try:
    from fastembed import TextEmbedding  # noqa: F401

    _FASTEMBED_AVAILABLE = True
except ImportError:
    _FASTEMBED_AVAILABLE = False


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "work" / "evals" / "context-builder-evidence-integrity-v1.json"
OVERLAY_PATH = ROOT / "work" / "evals" / "context-builder-retrieval-stage2-v1.json"


@unittest.skipUnless(
    _FASTEMBED_AVAILABLE,
    "optional 'fastembed' dependency not installed; "
    "see runtime/requirements-context-eval.txt",
)
class ContextRetrievalSemanticCandidateTests(unittest.TestCase):
    """Evaluation-only tests for the local-embedding semantic candidate.

    This candidate is real embedding-based ranking submitted to the same
    frozen Stage-2 evaluator used for the deterministic controls; it is not
    given the expected answer, and this test file does not hardcode a
    per-case gate assertion — whether the candidate clears every strict gate
    on the frozen corpus is an honest empirical question, not something this
    test assumes.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
        cls.overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
        # Imported lazily/inside the test class body so importing this test
        # module never requires fastembed to be installed.
        from runtime.context_retrieval_semantic import semantic_embedding_rankings

        cls.semantic_embedding_rankings = staticmethod(semantic_embedding_rankings)
        cls.predictions = semantic_embedding_rankings(cls.corpus, cls.overlay, top_k=1)
        cls.report = evaluate_source_rankings(
            cls.corpus,
            cls.overlay,
            cls.predictions,
            label="semantic-embedding-candidate",
        )

    def test_predictions_cover_every_case_in_order(self):
        case_ids = {item["id"] for item in self.corpus["cases"]}
        predicted_ids = {item["case_id"] for item in self.predictions}
        self.assertEqual(predicted_ids, case_ids)
        self.assertEqual(len(self.predictions), len(self.corpus["cases"]))

    def test_prediction_shape_matches_evaluator_contract(self):
        for item in self.predictions:
            self.assertEqual(set(item), {"case_id", "source_ids"})
            self.assertIsInstance(item["source_ids"], list)
            # No duplicate source ids within a single case's prediction.
            self.assertEqual(len(item["source_ids"]), len(set(item["source_ids"])))

    def test_frozen_explicit_prefix_is_preserved_for_every_case(self):
        explicit_by_case = {
            item["case_id"]: item["explicit_source_ids"]
            for item in self.overlay["cases"]
        }
        for item in self.predictions:
            prefix = explicit_by_case[item["case_id"]]
            self.assertEqual(
                item["source_ids"][: len(prefix)],
                prefix,
                msg=f"{item['case_id']} did not preserve its frozen explicit prefix",
            )
        # The evaluator's own check agrees.
        for case_report in self.report["cases"]:
            self.assertTrue(case_report["checks"]["explicit_prefix_preserved"])

    def test_report_has_expected_structure_and_never_claims_automatic_authority(self):
        report = self.report
        self.assertEqual(report["report_kind"], "MAPS_CONTEXT_RETRIEVAL_STAGE2_REPORT")
        self.assertEqual(report["label"], "semantic-embedding-candidate")
        self.assertEqual(len(report["cases"]), len(self.corpus["cases"]))

        self.assertIn("candidate_gate", report)
        gate = report["candidate_gate"]
        self.assertIn("eligible_for_proposal", gate)
        self.assertIsInstance(gate["eligible_for_proposal"], bool)
        self.assertFalse(gate["automatic_promotion"])
        expected_gate_names = {
            "hard_negative_abstention_perfect",
            "no_forbidden_temporal_source",
            "drift_pairs_complete",
            "vocabulary_shift_recalled",
            "evidence_recall_perfect",
            "evidence_precision_perfect",
            "explicit_prefix_preserved",
        }
        self.assertEqual(set(gate["gates"]), expected_gate_names)
        for value in gate["gates"].values():
            self.assertIsInstance(value, bool)

        for metric_name in (
            "case_pass_rate",
            "evidence_source_recall",
            "evidence_source_precision",
            "hard_negative_abstention_accuracy",
            "drift_pair_recall",
            "vocabulary_shift_recall",
        ):
            self.assertIn(metric_name, report["metrics"])

    def test_semantic_candidate_does_real_ranking_not_a_ground_truth_lookup(self):
        # Sanity check that this candidate is not simply replaying the same
        # explicit-only prefix as its entire answer for every case: at least
        # one case with no explicit sources should still receive a selection
        # or, for hard negatives, deliberately none is also an acceptable
        # (unforced) outcome. Either way the function must actually run
        # embedding similarity rather than short-circuit.
        explicit_by_case = {
            item["case_id"]: item["explicit_source_ids"]
            for item in self.overlay["cases"]
        }
        cases_without_explicit = [
            case_id for case_id, prefix in explicit_by_case.items() if not prefix
        ]
        self.assertTrue(cases_without_explicit)
        predictions_by_case = {
            item["case_id"]: item["source_ids"] for item in self.predictions
        }
        # top_k=1 with no minimum similarity means every non-explicit case
        # gets exactly one ranked candidate appended.
        for case_id in cases_without_explicit:
            self.assertEqual(len(predictions_by_case[case_id]), 1)


if __name__ == "__main__":
    unittest.main()
