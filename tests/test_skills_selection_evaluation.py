from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.skills import (
    SkillSelectionEvalError,
    SkillSelectionOutcome,
    SkillSelectionPrediction,
    evaluate_skill_selection,
    load_skill_selection_corpus,
)


CORPUS = Path(__file__).resolve().parents[1] / "work" / "evals" / "skill-selection-v1.json"


class SkillSelectionEvaluationTests(unittest.TestCase):
    def load(self):
        return load_skill_selection_corpus(CORPUS)

    @staticmethod
    def perfect_predictions(corpus):
        return [
            SkillSelectionPrediction(
                case_id=case.case_id,
                outcome=case.expected_outcome,
                selected_skills=case.expected_skills,
            )
            for case in corpus.cases
        ]

    def test_frozen_corpus_covers_required_case_classes(self):
        corpus = self.load()
        self.assertEqual(corpus.version, "skill-selection-v1")
        self.assertEqual(len(corpus.candidates), 5)
        self.assertEqual(len(corpus.cases), 24)
        self.assertEqual(len(corpus.sha256), 64)
        categories = {case.category.value for case in corpus.cases}
        self.assertEqual(
            categories,
            {
                "DIRECT",
                "PARAPHRASE",
                "VOCABULARY_SHIFT",
                "NEAR_MISS",
                "HARD_NEGATIVE",
                "NO_SKILL",
                "MULTI_SKILL",
                "AMBIGUOUS",
            },
        )

    def test_perfect_predictions_score_one(self):
        corpus = self.load()
        report = evaluate_skill_selection(corpus, self.perfect_predictions(corpus))
        self.assertEqual(report.exact_cases, report.total_cases)
        self.assertEqual(report.exact_rate, 1.0)
        self.assertEqual(report.selection_precision, 1.0)
        self.assertEqual(report.selection_recall, 1.0)
        self.assertEqual(report.selection_f1, 1.0)
        self.assertEqual(report.abstention_accuracy, 1.0)
        self.assertEqual(report.ambiguity_accuracy, 1.0)
        self.assertEqual(report.false_activation_cases, 0)
        self.assertEqual(report.missed_activation_cases, 0)
        self.assertEqual(report.ambiguity_misses, 0)
        self.assertTrue(all(value == 1.0 for value in report.category_accuracy.values()))

    def test_false_activation_on_abstain_case_reduces_selection_precision(self):
        corpus = self.load()
        predictions = {
            item.case_id: item for item in self.perfect_predictions(corpus)
        }
        predictions["SEL-017"] = SkillSelectionPrediction(
            case_id="SEL-017",
            outcome=SkillSelectionOutcome.SELECT,
            selected_skills=("release-verification",),
        )

        report = evaluate_skill_selection(corpus, predictions.values())

        self.assertEqual(report.false_activation_cases, 1)
        self.assertLess(report.selection_precision, 1.0)
        self.assertLess(report.selection_f1, 1.0)

    def test_failures_are_classified_without_becoming_routing_logic(self):
        corpus = self.load()
        predictions = {
            item.case_id: item for item in self.perfect_predictions(corpus)
        }
        predictions["SEL-017"] = SkillSelectionPrediction(
            case_id="SEL-017",
            outcome=SkillSelectionOutcome.SELECT,
            selected_skills=("release-verification",),
        )
        predictions["SEL-003"] = SkillSelectionPrediction(
            case_id="SEL-003",
            outcome=SkillSelectionOutcome.ABSTAIN,
        )
        predictions["SEL-024"] = SkillSelectionPrediction(
            case_id="SEL-024",
            outcome=SkillSelectionOutcome.SELECT,
            selected_skills=("incident-triage",),
        )

        report = evaluate_skill_selection(corpus, predictions.values())
        self.assertEqual(report.total_cases, 24)
        self.assertEqual(report.exact_cases, 21)
        self.assertEqual(report.false_activation_cases, 1)
        self.assertEqual(report.missed_activation_cases, 1)
        self.assertEqual(report.ambiguity_misses, 1)
        self.assertLess(report.selection_precision, 1.0)
        self.assertLess(report.abstention_accuracy, 1.0)
        self.assertEqual(report.ambiguity_accuracy, 0.0)
        self.assertLess(report.category_accuracy["HARD_NEGATIVE"], 1.0)
        self.assertLess(report.category_accuracy["DIRECT"], 1.0)
        self.assertEqual(report.category_accuracy["PARAPHRASE"], 1.0)

    def test_missing_prediction_is_an_error_not_implicit_abstention(self):
        corpus = self.load()
        predictions = self.perfect_predictions(corpus)[:-1]
        with self.assertRaisesRegex(SkillSelectionEvalError, "missing predictions"):
            evaluate_skill_selection(corpus, predictions)

    def test_unknown_selected_skill_is_rejected(self):
        corpus = self.load()
        predictions = self.perfect_predictions(corpus)
        predictions[0] = SkillSelectionPrediction(
            case_id=predictions[0].case_id,
            outcome=SkillSelectionOutcome.SELECT,
            selected_skills=("not-in-corpus",),
        )
        with self.assertRaisesRegex(SkillSelectionEvalError, "unknown skills"):
            evaluate_skill_selection(corpus, predictions)

    def test_duplicate_prediction_is_rejected(self):
        corpus = self.load()
        predictions = self.perfect_predictions(corpus)
        predictions.append(predictions[0])
        with self.assertRaisesRegex(SkillSelectionEvalError, "duplicate prediction"):
            evaluate_skill_selection(corpus, predictions)

    def test_corpus_rejects_unknown_expected_skill(self):
        payload = {
            "version": "bad",
            "candidates": [
                {"name": "one", "description": "A valid candidate description."}
            ],
            "cases": [
                {
                    "id": "BAD-1",
                    "category": "DIRECT",
                    "task": "Use a missing Skill.",
                    "expected_outcome": "SELECT",
                    "expected_skills": ["missing"],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "corpus.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(SkillSelectionEvalError, "unknown skills"):
                load_skill_selection_corpus(path)

    def test_ambiguous_case_requires_multiple_implicated_skills(self):
        payload = {
            "version": "bad",
            "candidates": [
                {"name": "one", "description": "A valid candidate description."}
            ],
            "cases": [
                {
                    "id": "BAD-2",
                    "category": "AMBIGUOUS",
                    "task": "This case claims ambiguity without alternatives.",
                    "expected_outcome": "AMBIGUOUS",
                    "expected_skills": ["one"],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "corpus.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(SkillSelectionEvalError, "at least two"):
                load_skill_selection_corpus(path)

    def test_report_is_serializable_and_bound_to_corpus_hash(self):
        corpus = self.load()
        report = evaluate_skill_selection(corpus, self.perfect_predictions(corpus))
        rendered = report.to_dict()
        self.assertEqual(rendered["corpus_sha256"], corpus.sha256)
        self.assertEqual(len(rendered["cases"]), len(corpus.cases))
        json.dumps(rendered)


if __name__ == "__main__":
    unittest.main()
