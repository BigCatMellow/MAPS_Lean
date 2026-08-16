from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.benchmark_results import BenchmarkResultError, evaluate_benchmark_results


PROTOCOL = json.loads(
    (
        Path(__file__).resolve().parents[1]
        / "work"
        / "evals"
        / "maps-end-to-end-benchmark-v1.json"
    ).read_text(encoding="utf-8")
)


class BenchmarkMeasurementValidationTests(unittest.TestCase):
    @staticmethod
    def _result(measurements: dict) -> dict:
        scenario = next(item for item in PROTOCOL["scenarios"] if item["id"] == "E2E-L2-001")
        return {
            "scenario_id": scenario["id"],
            "evidence_class": scenario["layer"],
            "fixture_kind": "CONTROLLED_SYNTHETIC",
            "properties": {
                prop["id"]: {
                    "state": "PASS",
                    "evidence_refs": [f"evidence:{prop['id']}"],
                }
                for prop in scenario["properties"]
            },
            "measurements": measurements,
        }

    def test_fractional_count_measurements_fail_closed(self):
        for field in (
            "tool_calls",
            "messages",
            "agent_count",
            "operator_intervention_count",
            "rework_count",
        ):
            with self.subTest(field=field):
                with self.assertRaises(BenchmarkResultError):
                    evaluate_benchmark_results(
                        PROTOCOL,
                        [self._result({field: 1.5})],
                        label=f"fractional-{field}",
                    )

    def test_integer_counts_and_numeric_duration_cost_remain_valid(self):
        report = evaluate_benchmark_results(
            PROTOCOL,
            [
                self._result(
                    {
                        "tool_calls": 1,
                        "messages": 2,
                        "agent_count": 1,
                        "operator_intervention_count": 0,
                        "rework_count": 0,
                        "runtime_ms": 12.5,
                        "cost_usd": 0.01,
                    }
                )
            ],
            label="valid-measurements",
        )
        scenario = next(
            item for item in report["scenarios"] if item["scenario_id"] == "E2E-L2-001"
        )
        self.assertEqual(scenario["status"], "PASS")
        self.assertEqual(scenario["measurements"]["tool_calls"], 1)
        self.assertEqual(scenario["measurements"]["runtime_ms"], 12.5)


if __name__ == "__main__":
    unittest.main()
