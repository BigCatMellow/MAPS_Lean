from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.benchmark_results import BenchmarkResultError, evaluate_benchmark_results


PROTOCOL_PATH = (
    Path(__file__).resolve().parents[1]
    / "work"
    / "evals"
    / "maps-end-to-end-benchmark-v1.json"
)
FROZEN_PROTOCOL_GIT_BLOB = (
    "git-blob-sha1:1de87962caa9f66319dbb9f6f192254569ab0cd3"
)


class BenchmarkResultEvidenceBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
        cls.scenarios = {item["id"]: item for item in cls.protocol["scenarios"]}

    @staticmethod
    def _copy(value):
        return json.loads(json.dumps(value))

    @staticmethod
    def _prov(state: str, ref: str | None = None) -> dict:
        return {"state": state, "ref": ref}

    def _result(self, scenario_id: str) -> dict:
        scenario = self.scenarios[scenario_id]
        layer = scenario["layer"]
        result = {
            "scenario_id": scenario_id,
            "evidence_class": layer,
            "fixture_kind": (
                "CONTROLLED_SYNTHETIC"
                if layer == "LAYER_2_CONTROLLED"
                else "REAL_PRODUCTION"
            ),
            "properties": {
                prop["id"]: {
                    "state": "PASS",
                    "evidence_refs": [f"evidence:{scenario_id}:{prop['id']}"],
                }
                for prop in scenario["properties"]
            },
            "measurements": {},
        }
        if layer == "LAYER_3_PRODUCTION_OUTCOME":
            result["provenance"] = {
                "task": self._prov("VERIFIED", f"task:{scenario_id}"),
                "run": self._prov("VERIFIED", f"run:{scenario_id}"),
                "outcome": self._prov("VERIFIED", f"outcome:{scenario_id}"),
                "operator_visible_result": self._prov("NOT_APPLICABLE"),
                "external_authority": self._prov("NOT_APPLICABLE"),
                "operator_intervention": self._prov("NOT_APPLICABLE"),
            }
            if scenario_id == "E2E-L3-001":
                result["provenance"]["operator_visible_result"] = self._prov(
                    "VERIFIED", "artifact:operator-visible"
                )
                result["provenance"]["external_authority"] = self._prov(
                    "VERIFIED", "authority:task-scope"
                )
            result["measurements"]["operator_intervention_count"] = 0
        return result

    @staticmethod
    def _scenario(report: dict, scenario_id: str) -> dict:
        return next(
            item
            for item in report["scenarios"]
            if item["scenario_id"] == scenario_id
        )

    def test_same_version_changed_protocol_truth_is_rejected(self):
        altered = self._copy(self.protocol)
        altered["scenarios"][0]["properties"][0]["required"] = False

        with self.assertRaisesRegex(
            BenchmarkResultError,
            "does not match frozen content",
        ):
            evaluate_benchmark_results(altered, [], label="tampered-protocol")

    def test_report_records_exact_frozen_protocol_identity(self):
        report = evaluate_benchmark_results(self.protocol, [], label="identity")

        self.assertEqual(
            report["protocol_identity"]["git_blob"],
            FROZEN_PROTOCOL_GIT_BLOB,
        )
        self.assertRegex(
            report["protocol_identity"]["content"],
            r"^sha256:[0-9a-f]{64}$",
        )

    def test_property_evidence_refs_are_preserved_and_change_evidence_identity(self):
        result = self._result("E2E-L2-001")
        report = evaluate_benchmark_results(
            self.protocol,
            [result],
            label="evidence-a",
        )
        scenario = self._scenario(report, "E2E-L2-001")
        row = next(
            item
            for item in scenario["properties"]
            if item["property_id"] == "orientation.authority_loaded"
        )
        expected_ref = "evidence:E2E-L2-001:orientation.authority_loaded"
        self.assertEqual(row["evidence_refs"], [expected_ref])
        self.assertEqual(row["evidence_ref_count"], 1)

        changed = self._copy(result)
        changed["properties"]["orientation.authority_loaded"]["evidence_refs"] = [
            "evidence:E2E-L2-001:orientation.authority_loaded:changed"
        ]
        changed_report = evaluate_benchmark_results(
            self.protocol,
            [changed],
            label="evidence-a",
        )
        self.assertNotEqual(
            report["result_evidence_ref"],
            changed_report["result_evidence_ref"],
        )

    def test_verified_provenance_is_preserved_and_changes_evidence_identity(self):
        result = self._result("E2E-L3-001")
        report = evaluate_benchmark_results(
            self.protocol,
            [result],
            label="provenance-a",
        )
        scenario = self._scenario(report, "E2E-L3-001")
        self.assertEqual(
            scenario["provenance"]["run"],
            {"state": "VERIFIED", "ref": "run:E2E-L3-001"},
        )
        self.assertEqual(
            scenario["provenance"]["external_authority"],
            {"state": "VERIFIED", "ref": "authority:task-scope"},
        )

        changed = self._copy(result)
        changed["provenance"]["run"]["ref"] = "run:E2E-L3-001:changed"
        changed_report = evaluate_benchmark_results(
            self.protocol,
            [changed],
            label="provenance-a",
        )
        self.assertNotEqual(
            report["result_evidence_ref"],
            changed_report["result_evidence_ref"],
        )

    def test_evidence_ref_order_is_normalized_for_identity(self):
        result = self._result("E2E-L2-001")
        result["properties"]["orientation.authority_loaded"]["evidence_refs"] = [
            "evidence:z",
            "evidence:a",
        ]
        forward = evaluate_benchmark_results(
            self.protocol,
            [result],
            label="stable",
        )

        reversed_refs = self._copy(result)
        reversed_refs["properties"]["orientation.authority_loaded"]["evidence_refs"].reverse()
        reverse = evaluate_benchmark_results(
            self.protocol,
            [reversed_refs],
            label="stable",
        )

        self.assertEqual(forward, reverse)


if __name__ == "__main__":
    unittest.main()
