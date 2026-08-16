import copy
import json
from pathlib import Path
import unittest

from runtime.acquisition_evidence import (
    AcquisitionEvidenceError,
    evaluate_acquisition_evidence,
)
from runtime.benchmark_results import evaluate_benchmark_results


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "work" / "evals" / "maps-end-to-end-benchmark-v1.json"
SHA_A = "sha256:" + "a" * 64
SHA_B = "sha256:" + "b" * 64
SHA_C = "sha256:" + "c" * 64


def manifest():
    return {
        "version": "maps-acquisition-paths-v1",
        "release_id": "release-1",
        "paths": [
            {
                "path_id": "download",
                "kind": "DOWNLOAD",
                "expected_ref": SHA_A,
                "operator_visible": True,
                "allow_not_applicable": False,
            },
            {
                "path_id": "archive",
                "kind": "ARCHIVE",
                "expected_ref": SHA_B,
                "operator_visible": True,
                "allow_not_applicable": True,
            },
        ],
    }


def observed(path_id, ref, suffix):
    return {
        "path_id": path_id,
        "acquisition_state": "OBSERVED",
        "observed_ref": ref,
        "acquisition_evidence_ref": f"acquisition:{suffix}",
        "usability_state": "VERIFIED",
        "usability_evidence_ref": f"usability:{suffix}",
        "not_applicable_decision_ref": None,
    }


def not_applicable(path_id):
    return {
        "path_id": path_id,
        "acquisition_state": "NOT_APPLICABLE",
        "observed_ref": None,
        "acquisition_evidence_ref": None,
        "usability_state": "NOT_APPLICABLE",
        "usability_evidence_ref": None,
        "not_applicable_decision_ref": "decision:archive-na",
    }


class AcquisitionEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))

    def test_exact_real_path_observations_produce_pass_fragments(self):
        report = evaluate_acquisition_evidence(
            manifest(),
            [observed("download", SHA_A, "download"), observed("archive", SHA_B, "archive")],
            label="exact-paths",
        )

        fragments = report["benchmark_property_fragments"]
        self.assertEqual(fragments["release.acquisition_paths_verified"]["state"], "PASS")
        self.assertEqual(fragments["release.no_stale_visible_artifact"]["state"], "PASS")
        self.assertEqual(fragments["operator.result_usable"]["state"], "PASS")
        self.assertEqual(report["immutable_ref_mismatch_count"], 0)
        self.assertEqual(report["missing_observation_count"], 0)
        for fragment in fragments.values():
            self.assertEqual(len(fragment["evidence_refs"]), 1)
            self.assertTrue(fragment["evidence_refs"][0].startswith("acquisition-report:"))

    def test_stale_but_usable_artifact_fails_content_and_stale_properties(self):
        report = evaluate_acquisition_evidence(
            manifest(),
            [observed("download", SHA_C, "stale-download"), observed("archive", SHA_B, "archive")],
            label="stale-path",
        )

        fragments = report["benchmark_property_fragments"]
        self.assertEqual(fragments["release.acquisition_paths_verified"]["state"], "FAIL")
        self.assertEqual(fragments["release.no_stale_visible_artifact"]["state"], "FAIL")
        # A stale artifact may still be technically consumable. Usability does
        # not erase the immutable-content failure.
        self.assertEqual(fragments["operator.result_usable"]["state"], "PASS")
        self.assertEqual(report["immutable_ref_mismatch_count"], 1)
        stale = next(item for item in report["paths"] if item["path_id"] == "download")
        self.assertEqual(stale["reason"], "immutable_ref_mismatch")

    def test_missing_observation_preserves_unknown_instead_of_passing_coverage(self):
        report = evaluate_acquisition_evidence(
            manifest(),
            [observed("download", SHA_A, "download")],
            label="missing-archive",
        )

        fragments = report["benchmark_property_fragments"]
        self.assertEqual(fragments["release.acquisition_paths_verified"]["state"], "UNKNOWN")
        self.assertEqual(fragments["release.no_stale_visible_artifact"]["state"], "UNKNOWN")
        self.assertEqual(fragments["operator.result_usable"]["state"], "UNKNOWN")
        self.assertEqual(report["missing_observation_count"], 1)
        self.assertEqual(
            fragments["release.acquisition_paths_verified"]["evidence_refs"], []
        )

    def test_explicit_allowed_not_applicable_is_not_silent_omission(self):
        report = evaluate_acquisition_evidence(
            manifest(),
            [observed("download", SHA_A, "download"), not_applicable("archive")],
            label="archive-na",
        )

        fragments = report["benchmark_property_fragments"]
        self.assertEqual(fragments["release.acquisition_paths_verified"]["state"], "PASS")
        self.assertEqual(fragments["release.no_stale_visible_artifact"]["state"], "PASS")
        self.assertEqual(fragments["operator.result_usable"]["state"], "PASS")
        archive = next(item for item in report["paths"] if item["path_id"] == "archive")
        self.assertEqual(archive["reason"], "explicit_not_applicable")
        self.assertEqual(
            archive["evidence"]["not_applicable_decision_ref"],
            "decision:archive-na",
        )

    def test_not_applicable_requires_manifest_permission(self):
        value = manifest()
        value["paths"][1]["allow_not_applicable"] = False
        report = evaluate_acquisition_evidence(
            value,
            [observed("download", SHA_A, "download"), not_applicable("archive")],
            label="forbidden-na",
        )

        self.assertEqual(
            report["benchmark_property_fragments"]["release.acquisition_paths_verified"]["state"],
            "FAIL",
        )
        archive = next(item for item in report["paths"] if item["path_id"] == "archive")
        self.assertEqual(archive["reason"], "not_applicable_not_allowed")

    def test_unreachable_path_is_failure_but_does_not_invent_stale_content(self):
        unreachable = {
            "path_id": "archive",
            "acquisition_state": "UNREACHABLE",
            "observed_ref": None,
            "acquisition_evidence_ref": "acquisition:archive-unreachable",
            "usability_state": "FAILED",
            "usability_evidence_ref": "usability:archive-unreachable",
            "not_applicable_decision_ref": None,
        }
        report = evaluate_acquisition_evidence(
            manifest(),
            [observed("download", SHA_A, "download"), unreachable],
            label="unreachable",
        )

        fragments = report["benchmark_property_fragments"]
        self.assertEqual(fragments["release.acquisition_paths_verified"]["state"], "FAIL")
        self.assertEqual(fragments["release.no_stale_visible_artifact"]["state"], "UNKNOWN")
        self.assertEqual(fragments["operator.result_usable"]["state"], "FAIL")
        self.assertEqual(report["immutable_ref_mismatch_count"], 0)

    def test_observation_schema_fails_closed(self):
        bad = observed("download", SHA_A, "download")
        bad["acquisition_evidence_ref"] = None
        with self.assertRaises(AcquisitionEvidenceError):
            evaluate_acquisition_evidence(
                manifest(),
                [bad, observed("archive", SHA_B, "archive")],
                label="missing-acquisition-proof",
            )

        unknown = {
            "path_id": "download",
            "acquisition_state": "UNKNOWN",
            "observed_ref": SHA_A,
            "acquisition_evidence_ref": None,
            "usability_state": "UNKNOWN",
            "usability_evidence_ref": None,
            "not_applicable_decision_ref": None,
        }
        with self.assertRaises(AcquisitionEvidenceError):
            evaluate_acquisition_evidence(
                manifest(),
                [unknown],
                label="unknown-with-claimed-ref",
            )

    def test_unknown_and_duplicate_path_observations_fail_closed(self):
        unknown_path = observed("other", SHA_A, "other")
        with self.assertRaises(AcquisitionEvidenceError):
            evaluate_acquisition_evidence(manifest(), [unknown_path], label="unknown-path")

        duplicate = observed("download", SHA_A, "download")
        with self.assertRaises(AcquisitionEvidenceError):
            evaluate_acquisition_evidence(
                manifest(),
                [duplicate, copy.deepcopy(duplicate)],
                label="duplicate-path",
            )

    def test_report_identity_is_deterministic_across_observation_order(self):
        first = evaluate_acquisition_evidence(
            manifest(),
            [observed("download", SHA_A, "download"), observed("archive", SHA_B, "archive")],
            label="deterministic",
        )
        second = evaluate_acquisition_evidence(
            manifest(),
            [observed("archive", SHA_B, "archive"), observed("download", SHA_A, "download")],
            label="deterministic",
        )

        self.assertEqual(first["report_id"], second["report_id"])
        self.assertEqual(first["manifest_sha256"], second["manifest_sha256"])

    def test_report_does_not_claim_real_world_provenance_or_authority(self):
        report = evaluate_acquisition_evidence(
            manifest(),
            [observed("download", SHA_A, "download"), observed("archive", SHA_B, "archive")],
            label="authority-boundary",
        )

        self.assertFalse(report["coverage"]["acquisition_performed_by_this_report"])
        self.assertFalse(report["coverage"]["network_or_install_execution"])
        self.assertFalse(report["coverage"]["real_world_provenance_verified_by_this_report"])
        self.assertFalse(report["authority"]["external_action_authorized"])
        self.assertFalse(report["authority"]["publication_authorized"])
        self.assertFalse(report["authority"]["automatic_benchmark_pass"])

    def test_property_fragments_fit_layer3_result_validator_without_bypassing_provenance(self):
        acquisition = evaluate_acquisition_evidence(
            manifest(),
            [observed("download", SHA_A, "download"), observed("archive", SHA_B, "archive")],
            label="benchmark-bridge",
        )
        properties = {
            "external.authority_preserved": {
                "state": "PASS",
                "evidence_refs": ["authority:task-1"],
            },
            **acquisition["benchmark_property_fragments"],
            "outcome.real_observation_recorded": {
                "state": "PASS",
                "evidence_refs": ["outcome:1"],
            },
        }
        result = {
            "scenario_id": "E2E-L3-001",
            "evidence_class": "LAYER_3_PRODUCTION_OUTCOME",
            "fixture_kind": "REAL_PRODUCTION",
            "properties": properties,
            "provenance": {
                "task": {"state": "VERIFIED", "ref": "task:TASK-1"},
                "run": {"state": "VERIFIED", "ref": "run:RUN-1"},
                "outcome": {"state": "VERIFIED", "ref": "outcome:1"},
                "operator_visible_result": {
                    "state": "VERIFIED",
                    "ref": "artifact:release-1",
                },
                "external_authority": {
                    "state": "VERIFIED",
                    "ref": "authority:task-1",
                },
                "operator_intervention": {
                    "state": "NOT_APPLICABLE",
                    "ref": None,
                },
            },
            "measurements": {},
        }

        benchmark = evaluate_benchmark_results(
            self.protocol,
            [result],
            label="acquisition-bridge-test",
        )
        scenario = next(
            item for item in benchmark["scenarios"] if item["scenario_id"] == "E2E-L3-001"
        )
        self.assertEqual(scenario["status"], "PASS")
        # Other required benchmark scenarios are absent, so the acquisition
        # report cannot turn one valid Layer-3 case into global completion.
        self.assertEqual(benchmark["benchmark_status"], "INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
