from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.benchmark_results import (
    BenchmarkResultError,
    evaluate_benchmark_results,
)


PROTOCOL_PATH = (
    Path(__file__).resolve().parents[1]
    / "work"
    / "evals"
    / "maps-end-to-end-benchmark-v1.json"
)


class BenchmarkResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
        cls.scenarios = {item["id"]: item for item in cls.protocol["scenarios"]}

    @staticmethod
    def _prov(state: str, ref: str | None = None) -> dict:
        return {"state": state, "ref": ref}

    def _provenance(self, scenario_id: str) -> dict:
        items = {
            "task": self._prov("NOT_APPLICABLE"),
            "run": self._prov("NOT_APPLICABLE"),
            "outcome": self._prov("NOT_APPLICABLE"),
            "operator_visible_result": self._prov("NOT_APPLICABLE"),
            "external_authority": self._prov("NOT_APPLICABLE"),
            "operator_intervention": self._prov("NOT_APPLICABLE"),
        }
        if scenario_id.startswith("E2E-L3-"):
            items["task"] = self._prov("VERIFIED", f"task:{scenario_id}")
            items["run"] = self._prov("VERIFIED", f"run:{scenario_id}")
            items["outcome"] = self._prov("VERIFIED", f"outcome:{scenario_id}")
        if scenario_id == "E2E-L3-001":
            items["operator_visible_result"] = self._prov(
                "VERIFIED", "artifact:operator-visible"
            )
            items["external_authority"] = self._prov(
                "VERIFIED", "authority:task-scope"
            )
        return items

    def _perfect_result(self, scenario: dict) -> dict:
        layer = scenario["layer"]
        result = {
            "scenario_id": scenario["id"],
            "evidence_class": layer,
            "fixture_kind": (
                "CONTROLLED_SYNTHETIC"
                if layer == "LAYER_2_CONTROLLED"
                else "REAL_PRODUCTION"
            ),
            "properties": {
                prop["id"]: {
                    "state": "PASS",
                    "evidence_refs": [
                        f"evidence:{scenario['id']}:{prop['id']}"
                    ],
                }
                for prop in scenario["properties"]
            },
            "measurements": {},
        }
        if layer == "LAYER_3_PRODUCTION_OUTCOME":
            result["provenance"] = self._provenance(scenario["id"])
            result["measurements"]["operator_intervention_count"] = 0
        return result

    def _perfect_results(self) -> list[dict]:
        return [self._perfect_result(item) for item in self.protocol["scenarios"]]

    @staticmethod
    def _scenario(report: dict, scenario_id: str) -> dict:
        return next(
            item
            for item in report["scenarios"]
            if item["scenario_id"] == scenario_id
        )

    def test_perfect_evidence_completes_protocol_without_authorizing_promotion(self):
        report = evaluate_benchmark_results(
            self.protocol,
            self._perfect_results(),
            label="perfect",
        )
        self.assertEqual(report["benchmark_status"], "COMPLETE")
        self.assertEqual(
            report["cases"],
            {"total": 6, "pass": 6, "fail": 0, "incomplete": 0},
        )
        self.assertTrue(report["external_operator_visible_case_passed"])
        self.assertEqual(
            report["candidate_advancement_gate"],
            "EVALUATION_COMPLETE_NOT_AUTHORIZED",
        )
        self.assertFalse(report["promotion"]["automatic"])

    def test_layer3_synthetic_fixture_fails_mechanically(self):
        results = self._perfect_results()
        target = next(
            item for item in results if item["scenario_id"] == "E2E-L3-001"
        )
        target["fixture_kind"] = "CONTROLLED_SYNTHETIC"

        report = evaluate_benchmark_results(self.protocol, results, label="synthetic")
        scenario = self._scenario(report, "E2E-L3-001")
        self.assertEqual(scenario["status"], "FAIL")
        self.assertIn(
            "layer3_synthetic_or_controlled_fixture_forbidden",
            scenario["eligibility_reasons"],
        )

    def test_layer3_unknown_run_provenance_is_incomplete_not_pass(self):
        results = self._perfect_results()
        target = next(
            item for item in results if item["scenario_id"] == "E2E-L3-002"
        )
        target["provenance"]["run"] = self._prov("UNKNOWN")

        report = evaluate_benchmark_results(self.protocol, results, label="unknown-run")
        scenario = self._scenario(report, "E2E-L3-002")
        self.assertEqual(scenario["status"], "INCOMPLETE")
        self.assertIn("run_provenance_unknown", scenario["eligibility_reasons"])

    def test_external_case_requires_verified_authority_and_real_result(self):
        results = self._perfect_results()
        target = next(
            item for item in results if item["scenario_id"] == "E2E-L3-001"
        )
        target["provenance"]["external_authority"] = self._prov("UNKNOWN")
        target["provenance"]["operator_visible_result"] = self._prov("UNKNOWN")

        report = evaluate_benchmark_results(
            self.protocol,
            results,
            label="missing-external",
        )
        scenario = self._scenario(report, "E2E-L3-001")
        self.assertEqual(scenario["status"], "INCOMPLETE")
        self.assertIn(
            "external_authority_provenance_unknown",
            scenario["eligibility_reasons"],
        )
        self.assertIn(
            "operator_visible_result_provenance_unknown",
            scenario["eligibility_reasons"],
        )
        self.assertFalse(report["external_operator_visible_case_passed"])

    def test_quality_failure_still_fails_scenario(self):
        results = self._perfect_results()
        target = next(
            item for item in results if item["scenario_id"] == "E2E-L2-001"
        )
        target["properties"]["context.explicit_sources_used"] = {
            "state": "FAIL",
            "evidence_refs": ["evidence:quality-failure"],
        }

        report = evaluate_benchmark_results(self.protocol, results, label="quality-fail")
        scenario = self._scenario(report, "E2E-L2-001")
        self.assertEqual(scenario["status"], "FAIL")
        self.assertEqual(scenario["blocker_failures"], [])
        self.assertEqual(report["candidate_advancement_gate"], "BLOCKED")

    def test_blocker_failure_is_reported_as_non_tradeable(self):
        results = self._perfect_results()
        target = next(
            item for item in results if item["scenario_id"] == "E2E-L2-003"
        )
        target["properties"]["review.independence_preserved"] = {
            "state": "FAIL",
            "evidence_refs": ["evidence:continuity-linked-review"],
        }
        target["measurements"] = {"runtime_ms": 1, "cost_usd": 0}

        report = evaluate_benchmark_results(self.protocol, results, label="blocker")
        scenario = self._scenario(report, "E2E-L2-003")
        self.assertEqual(scenario["status"], "FAIL")
        self.assertIn(
            "review.independence_preserved",
            scenario["blocker_failures"],
        )
        self.assertEqual(report["candidate_advancement_gate"], "BLOCKED")

    def test_unknown_required_property_is_incomplete(self):
        results = self._perfect_results()
        target = next(
            item for item in results if item["scenario_id"] == "E2E-L2-004"
        )
        target["properties"]["context.relevant_evidence_visible"] = {
            "state": "UNKNOWN",
            "evidence_refs": [],
        }

        report = evaluate_benchmark_results(self.protocol, results, label="unknown")
        scenario = self._scenario(report, "E2E-L2-004")
        self.assertEqual(scenario["status"], "INCOMPLETE")

    def test_omitted_required_property_becomes_not_run_and_incomplete(self):
        results = self._perfect_results()
        target = next(
            item for item in results if item["scenario_id"] == "E2E-L2-002"
        )
        target["properties"].pop("recovery.lineage_or_unknown_honest")

        report = evaluate_benchmark_results(self.protocol, results, label="partial")
        scenario = self._scenario(report, "E2E-L2-002")
        row = next(
            item
            for item in scenario["properties"]
            if item["property_id"] == "recovery.lineage_or_unknown_honest"
        )
        self.assertEqual(row["state"], "NOT_RUN")
        self.assertEqual(scenario["status"], "INCOMPLETE")

    def test_pass_or_fail_property_requires_evidence_refs(self):
        result = self._perfect_result(self.scenarios["E2E-L2-001"])
        result["properties"]["orientation.authority_loaded"]["evidence_refs"] = []
        with self.assertRaises(BenchmarkResultError):
            evaluate_benchmark_results(
                self.protocol,
                [result],
                label="no-evidence",
            )

    def test_operator_intervention_count_requires_verified_provenance(self):
        results = self._perfect_results()
        target = next(
            item for item in results if item["scenario_id"] == "E2E-L3-002"
        )
        target["measurements"]["operator_intervention_count"] = 2

        report = evaluate_benchmark_results(self.protocol, results, label="intervention")
        scenario = self._scenario(report, "E2E-L3-002")
        self.assertEqual(scenario["status"], "INCOMPLETE")
        self.assertIn(
            "operator_intervention_provenance_unverified",
            scenario["eligibility_reasons"],
        )

        target["provenance"]["operator_intervention"] = self._prov(
            "VERIFIED", "operator-event:123"
        )
        report = evaluate_benchmark_results(
            self.protocol,
            results,
            label="intervention-verified",
        )
        self.assertEqual(self._scenario(report, "E2E-L3-002")["status"], "PASS")

    def test_activity_measurements_cannot_turn_failure_into_success(self):
        results = self._perfect_results()
        target = next(
            item for item in results if item["scenario_id"] == "E2E-L3-002"
        )
        target["properties"]["outcome.provenance_explicit"] = {
            "state": "FAIL",
            "evidence_refs": ["evidence:missing-provenance"],
        }
        target["measurements"].update(
            {
                "runtime_ms": 1,
                "cost_usd": 0,
                "tool_calls": 1,
                "messages": 1,
                "agent_count": 1,
            }
        )

        report = evaluate_benchmark_results(self.protocol, results, label="cheap-fail")
        self.assertEqual(self._scenario(report, "E2E-L3-002")["status"], "FAIL")
        self.assertEqual(report["benchmark_status"], "FAIL")

    def test_result_order_is_deterministic(self):
        results = self._perfect_results()
        forward = evaluate_benchmark_results(self.protocol, results, label="same")
        reverse = evaluate_benchmark_results(
            self.protocol,
            list(reversed(results)),
            label="same",
        )
        self.assertEqual(forward, reverse)

    def test_unknown_property_fails_closed(self):
        result = self._perfect_result(self.scenarios["E2E-L2-001"])
        result["properties"]["invented.metric"] = {
            "state": "PASS",
            "evidence_refs": ["evidence:invented"],
        }
        with self.assertRaises(BenchmarkResultError):
            evaluate_benchmark_results(
                self.protocol,
                [result],
                label="invalid-property",
            )

    def test_unknown_scenario_fails_closed(self):
        result = self._perfect_result(self.scenarios["E2E-L2-001"])
        result["scenario_id"] = "E2E-UNKNOWN"
        with self.assertRaises(BenchmarkResultError):
            evaluate_benchmark_results(
                self.protocol,
                [result],
                label="invalid-scenario",
            )


if __name__ == "__main__":
    unittest.main()
