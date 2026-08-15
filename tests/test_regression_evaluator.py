from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

from runtime.evaluation import (
    ComparisonOutcome,
    EvaluationError,
    PropertyResultState,
    compare_regression_cases,
    evaluate_regression_cases,
    freeze_regression_case,
    validate_regression_case,
)
from runtime.run_record import build_run_record
from runtime.state import TaskStore


def contract():
    return {
        "title": "Evaluator source task",
        "outcome": "Produce frozen evaluation evidence",
        "task_type": "IMPLEMENTATION",
        "owner": "author",
        "risk": "LOW",
        "decision_authority": "Bounded implementation choices",
        "verification": "Run deterministic tests",
        "evidence_expected": "Run evidence",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "Stop on ambiguity",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": ["src"],
        "non_goals": ["No unrelated changes"],
        "acceptance_criteria": ["evaluation evidence exists"],
        "stop_conditions": ["missing evidence"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class RegressionEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        root = Path(self.td.name)
        repo = root / "repo"
        repo.mkdir()
        (repo / "src").mkdir()
        self.store = TaskStore(root / "maps.db")
        self.assertTrue(self.store.create_task(task_id="TASK-EVAL").ok)
        self.assertTrue(self.store.update_contract("TASK-EVAL", contract()).ok)
        self.assertTrue(self.store.promote_ready("TASK-EVAL").ok)
        self.assertTrue(self.store.claim_task("TASK-EVAL", "author", lease_seconds=600).ok)
        run = self.store.create_run_manifest(
            "TASK-EVAL",
            "author",
            repo_root=repo,
            created_by="dispatcher",
            readable_paths=["."],
            writable_paths=["src"],
            base_revision="abc123",
        )
        self.assertTrue(run.ok, run.message)
        record = build_run_record(self.store, "TASK-EVAL", run.task["run_id"])
        self.cases = [
            freeze_regression_case(
                record,
                category="TOOL_FAILURE",
                sanitized_fixture="Case one fixture.",
                expected_properties=["tool.a", "tool.b", "tool.c", "tool.d", "tool.e"],
                frozen_by="reviewer",
                tags=["tool", "core"],
            ),
            freeze_regression_case(
                record,
                category="ACI_AMBIGUITY",
                sanitized_fixture="Case two fixture.",
                expected_properties=["aci.clear"],
                frozen_by="reviewer",
                tags=["aci"],
            ),
        ]

    def result(self, case, properties, measurements=None):
        value = {
            "case_id": case["case_id"],
            "case_sha256": case["content_sha256"],
            "properties": properties,
        }
        if measurements is not None:
            value["measurements"] = measurements
        return value

    @staticmethod
    def case_report(report, case):
        return next(item for item in report["cases"] if item["case_id"] == case["case_id"])

    def test_exact_case_hash_is_revalidated_before_scoring(self):
        self.assertEqual(validate_regression_case(self.cases[0]), self.cases[0])
        tampered = copy.deepcopy(self.cases[0])
        tampered["tags"].append("tampered")
        with self.assertRaisesRegex(EvaluationError, "content hash"):
            evaluate_regression_cases([tampered], [], label="candidate")

    def test_all_external_property_states_and_missing_are_explicit(self):
        report = evaluate_regression_cases(
            self.cases,
            [
                self.result(
                    self.cases[0],
                    {
                        "tool.a": PropertyResultState.PASS,
                        "tool.b": "FAIL",
                        "tool.c": "UNKNOWN",
                        "tool.d": "NOT_RUN",
                    },
                )
            ],
            label="candidate",
        )
        metrics = report["metrics"]["properties"]
        self.assertEqual(metrics["pass"], 1)
        self.assertEqual(metrics["fail"], 1)
        self.assertEqual(metrics["unknown"], 1)
        self.assertEqual(metrics["not_run"], 1)
        self.assertEqual(metrics["missing"], 2)
        self.assertEqual(report["metrics"]["cases"]["incomplete"], 2)
        case_report = self.case_report(report, self.cases[0])
        self.assertEqual(case_report["status"], "INCOMPLETE")
        missing = [row for row in case_report["properties"] if not row["reported"]]
        self.assertEqual(len(missing), 1)
        self.assertIsNone(missing[0]["status"])

    def test_unknown_duplicate_and_hash_mismatched_results_fail(self):
        valid = self.result(self.cases[0], {"tool.a": "PASS"})
        with self.assertRaisesRegex(EvaluationError, "duplicate result"):
            evaluate_regression_cases(self.cases, [valid, valid], label="candidate")
        bad_property = self.result(self.cases[0], {"not.expected": "PASS"})
        with self.assertRaisesRegex(EvaluationError, "unknown properties"):
            evaluate_regression_cases(self.cases, [bad_property], label="candidate")
        bad_hash = self.result(self.cases[0], {"tool.a": "PASS"})
        bad_hash["case_sha256"] = "0" * 64
        with self.assertRaisesRegex(EvaluationError, "hash mismatch"):
            evaluate_regression_cases(self.cases, [bad_hash], label="candidate")

    def test_categories_tags_metrics_and_determinism_are_preserved(self):
        results = [
            self.result(
                self.cases[0],
                {property_id: "PASS" for property_id in self.cases[0]["expected_properties"]},
            ),
            self.result(self.cases[1], {"aci.clear": "FAIL"}),
        ]
        first = evaluate_regression_cases(self.cases, results, label="candidate")
        second = evaluate_regression_cases(
            list(reversed(self.cases)), list(reversed(results)), label="candidate"
        )
        self.assertEqual(first, second)
        tool_case = self.case_report(first, self.cases[0])
        self.assertEqual(tool_case["incident_category"], "TOOL_FAILURE")
        self.assertEqual(tool_case["tags"], ["core", "tool"])
        self.assertEqual(first["metrics"]["cases"]["complete"], 2)
        self.assertEqual(first["metrics"]["cases"]["pass"], 1)
        self.assertEqual(first["metrics"]["cases"]["fail"], 1)
        self.assertFalse(first["promotion"]["automatic"])

    def test_measurements_are_present_only_when_explicitly_supplied(self):
        without = evaluate_regression_cases(self.cases, [], label="candidate")
        self.assertNotIn("measurements", without["metrics"])
        measured = evaluate_regression_cases(
            self.cases,
            [
                self.result(
                    self.cases[0],
                    {property_id: "PASS" for property_id in self.cases[0]["expected_properties"]},
                    {"cost_usd": 0.25, "latency_ms": 1200},
                )
            ],
            label="candidate",
        )
        summary = measured["metrics"]["measurements"]
        self.assertEqual(summary["cost_usd"]["measured_cases"], 1)
        self.assertEqual(summary["cost_usd"]["total"], 0.25)
        self.assertEqual(summary["latency_ms"]["total"], 1200)

    def test_comparison_mechanically_classifies_all_four_outcomes(self):
        case = self.cases[0]
        baseline = [
            self.result(
                case,
                {"tool.a": "FAIL", "tool.b": "PASS", "tool.c": "PASS", "tool.d": "UNKNOWN"},
                {"cost_usd": 1.0, "latency_ms": 1000},
            )
        ]
        candidate = [
            self.result(
                case,
                {"tool.a": "PASS", "tool.b": "FAIL", "tool.c": "PASS", "tool.d": "PASS"},
                {"cost_usd": 0.8, "latency_ms": 900},
            )
        ]
        comparison = compare_regression_cases([case], baseline, candidate)
        outcomes = {
            row["property_id"]: row["outcome"]
            for row in comparison["cases"][0]["properties"]
        }
        self.assertEqual(outcomes["tool.a"], ComparisonOutcome.IMPROVED.value)
        self.assertEqual(outcomes["tool.b"], ComparisonOutcome.REGRESSED.value)
        self.assertEqual(outcomes["tool.c"], ComparisonOutcome.UNCHANGED.value)
        self.assertEqual(outcomes["tool.d"], ComparisonOutcome.INCOMPLETE.value)
        self.assertEqual(outcomes["tool.e"], ComparisonOutcome.INCOMPLETE.value)
        self.assertTrue(comparison["cases"][0]["has_improvement"])
        self.assertTrue(comparison["cases"][0]["has_regression"])
        self.assertEqual(comparison["cases"][0]["outcome"], "INCOMPLETE")
        paired = comparison["measurement_comparison"]
        self.assertEqual(paired["cost_usd"]["paired_cases"], 1)
        self.assertAlmostEqual(paired["cost_usd"]["candidate_minus_baseline"], -0.2)

    def test_evaluation_is_read_only_and_never_authorizes_promotion(self):
        before = self.store.trace_task("TASK-EVAL")
        comparison = compare_regression_cases(self.cases, [], [])
        self.assertEqual(self.store.trace_task("TASK-EVAL"), before)
        self.assertFalse(comparison["promotion"]["automatic"])
        self.assertEqual(
            comparison["promotion"]["path"],
            [
                "frozen cases",
                "candidate results",
                "comparative report",
                "proposal",
                "independent review/operator gate where required",
                "promotion",
            ],
        )


if __name__ == "__main__":
    unittest.main()
