from __future__ import annotations

import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.cli import main as cli_main
from runtime.evaluation import (
    IncidentCategory,
    RegressionCaseError,
    dumps_regression_case,
    freeze_regression_case,
)
from runtime.run_record import build_run_record
from runtime.state import TaskStore


def contract():
    return {
        "title": "Regression source task",
        "outcome": "Capture a reproducible failure source",
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
        "acceptance_criteria": ["case source exists"],
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


class FrozenRegressionCaseTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        self.db = self.root / "maps.db"
        self.store = TaskStore(self.db)
        self.assertTrue(self.store.create_task(task_id="TASK-CASE").ok)
        self.assertTrue(self.store.update_contract("TASK-CASE", contract()).ok)
        self.assertTrue(self.store.promote_ready("TASK-CASE").ok)
        self.assertTrue(self.store.claim_task("TASK-CASE", "author", lease_seconds=600).ok)
        run = self.store.create_run_manifest(
            "TASK-CASE",
            "author",
            repo_root=self.repo,
            created_by="dispatcher",
            readable_paths=["."],
            writable_paths=["src"],
            base_revision="abc123",
        )
        self.assertTrue(run.ok, run.message)
        self.run_id = run.task["run_id"]
        self.run_record = build_run_record(self.store, "TASK-CASE", self.run_id)

    def freeze(self, **overrides):
        values = {
            "category": IncidentCategory.ACI_AMBIGUITY,
            "sanitized_fixture": (
                "A tool returned an empty-looking result without distinguishing "
                "zero matches from transport failure."
            ),
            "expected_properties": [
                "operation_result.distinguishes_zero_matches",
                "operation_result.exposes_failure_state",
            ],
            "frozen_by": "reviewer",
            "tags": ["aci", "tool-result"],
        }
        values.update(overrides)
        return freeze_regression_case(self.run_record, **values)

    def test_case_is_deterministic_and_embeds_validated_run_record(self):
        first = self.freeze()
        second = self.freeze()
        self.assertEqual(first, second)
        self.assertEqual(first["case_version"], 1)
        self.assertEqual(first["case_kind"], "MAPS_FROZEN_REGRESSION_CASE")
        self.assertEqual(first["case_id"], f"CASE-{first['content_sha256']}")
        self.assertEqual(first["source_run_record_id"], self.run_record["record_id"])
        self.assertEqual(first["source_run_record"], self.run_record)
        self.assertFalse(first["promotion"]["automatic"])

    def test_tampered_run_record_is_rejected(self):
        tampered = copy.deepcopy(self.run_record)
        tampered["run"]["worker_id"] = "different-worker"
        with self.assertRaisesRegex(RegressionCaseError, "content hash"):
            freeze_regression_case(
                tampered,
                category=IncidentCategory.TOOL_FAILURE,
                sanitized_fixture="A sanitized fixture.",
                expected_properties=["tool.failure_is_reported"],
                frozen_by="reviewer",
            )

    def test_sensitive_fixture_is_rejected_before_freezing(self):
        with self.assertRaisesRegex(RegressionCaseError, "sensitive"):
            self.freeze(sanitized_fixture="API_KEY=supersecretvalue")

    def test_fixture_length_is_bounded(self):
        with self.assertRaisesRegex(RegressionCaseError, "exceeds"):
            self.freeze(sanitized_fixture="x" * 12001)

    def test_expected_properties_are_structured_and_normalized(self):
        case = self.freeze(
            expected_properties=[
                "Result.Exposes_State",
                "result.distinguishes_zero_matches",
            ],
        )
        self.assertEqual(
            case["expected_properties"],
            ["result.distinguishes_zero_matches", "result.exposes_state"],
        )
        with self.assertRaisesRegex(RegressionCaseError, "invalid expected_properties"):
            self.freeze(expected_properties=["free text property with spaces"])

    def test_expected_properties_cannot_be_empty(self):
        with self.assertRaisesRegex(RegressionCaseError, "cannot be empty"):
            self.freeze(expected_properties=[])

    def test_unknown_incident_category_is_rejected(self):
        with self.assertRaisesRegex(RegressionCaseError, "unknown incident category"):
            self.freeze(category="NOT_A_CATEGORY")

    def test_taxonomy_contains_expected_operational_failure_classes(self):
        values = {item.value for item in IncidentCategory}
        for required in (
            "TOOL_FAILURE",
            "CONTEXT_OMISSION",
            "SKILL_ROUTING_ERROR",
            "HELPER_NO_PROGRESS",
            "RECOVERY_FAILURE",
            "ENVIRONMENT_DRIFT",
            "STALE_REVIEW_EVIDENCE",
            "AUTHORITY_VIOLATION_ATTEMPT",
            "ACI_AMBIGUITY",
            "SUPPLY_CHAIN_DEFECT",
            "UNKNOWN",
        ):
            self.assertIn(required, values)

    def test_tags_are_normalized_and_duplicate_tags_fail(self):
        case = self.freeze(tags=["Tool-Result", "ACI"])
        self.assertEqual(case["tags"], ["aci", "tool-result"])
        with self.assertRaisesRegex(RegressionCaseError, "tags contains duplicates"):
            self.freeze(tags=["aci", "ACI"])

    def test_case_json_round_trips(self):
        case = self.freeze()
        rendered = dumps_regression_case(case)
        self.assertEqual(json.loads(rendered), case)

    def test_case_does_not_gain_complete_replay_claim(self):
        case = self.freeze()
        self.assertFalse(case["source_run_record"]["replay"]["complete"])
        self.assertNotIn("replay_complete", case)

    def test_cli_reads_fixture_from_file_and_emits_case_without_writing_state(self):
        fixture = self.root / "fixture.txt"
        fixture.write_text("A sanitized CLI regression fixture.\n", encoding="utf-8")
        before = self.store.trace_task("TASK-CASE")
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = cli_main(
                [
                    "--db",
                    str(self.db),
                    "freeze-case",
                    "TASK-CASE",
                    self.run_id,
                    "--category",
                    "ACI_AMBIGUITY",
                    "--fixture-file",
                    str(fixture),
                    "--expect",
                    "operation_result.exposes_failure_state",
                    "--frozen-by",
                    "reviewer",
                ]
            )
        self.assertEqual(code, 0)
        case = json.loads(stream.getvalue())
        self.assertEqual(case["incident_category"], "ACI_AMBIGUITY")
        self.assertEqual(case["sanitized_fixture"], "A sanitized CLI regression fixture.")
        self.assertEqual(self.store.trace_task("TASK-CASE"), before)


if __name__ == "__main__":
    unittest.main()
