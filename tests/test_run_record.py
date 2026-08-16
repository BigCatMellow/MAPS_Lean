from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.run_record import CoverageState, RunRecordError, build_run_record, dumps_run_record
from runtime.state import TaskStore


class FakeTraceSource:
    def __init__(self, trace):
        self.trace = trace

    def trace_task(self, task_id):
        if self.trace and self.trace.get("task_id") == task_id:
            return self.trace
        return None


def contract():
    return {
        "title": "PRIVATE-TITLE-MARKER",
        "outcome": "PRIVATE-OUTCOME-MARKER",
        "task_type": "IMPLEMENTATION",
        "owner": "author",
        "risk": "LOW",
        "decision_authority": "PRIVATE-AUTHORITY-MARKER",
        "verification": "PRIVATE-VERIFICATION-MARKER",
        "evidence_expected": "PRIVATE-EVIDENCE-EXPECTED-MARKER",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "PRIVATE-ESCALATION-MARKER",
        "inputs": ["private-input"],
        "sources": ["private-source"],
        "dependencies": [],
        "output_paths": ["src"],
        "non_goals": ["private-non-goal"],
        "acceptance_criteria": ["criterion one"],
        "stop_conditions": ["private-stop-condition"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class PortableRunRecordTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "src" / "context.txt").write_text("context\n", encoding="utf-8")
        self.store = TaskStore(self.root / "maps.db")
        self.assertTrue(self.store.create_task(task_id="TASK-RR").ok)
        self.assertTrue(self.store.update_contract("TASK-RR", contract()).ok)
        self.assertTrue(self.store.promote_ready("TASK-RR").ok)
        self.assertTrue(self.store.claim_task("TASK-RR", "author", lease_seconds=600).ok)
        run = self.store.create_run_manifest(
            "TASK-RR",
            "author",
            repo_root=self.repo,
            created_by="dispatcher",
            context_paths=["src/context.txt"],
            readable_paths=["."],
            writable_paths=["src"],
            runtime_limits={"max_attempts": 2},
            base_revision="abc123",
        )
        self.assertTrue(run.ok, run.message)
        self.run_id = run.task["run_id"]
        self.assertTrue(
            self.store.submit_task(
                "TASK-RR",
                "author",
                "PRIVATE-SUBMISSION-EVIDENCE-MARKER",
            ).ok
        )
        self.assertTrue(self.store.claim_review("TASK-RR", "reviewer").ok)
        self.assertTrue(
            self.store.record_review(
                "TASK-RR",
                "reviewer",
                "APPROVED",
                "PRIVATE-REVIEW-SUMMARY-MARKER",
            ).ok
        )
        outcome = self.store.record_outcome(
            "TASK-RR",
            "SUCCESS",
            source="PRIVATE-OUTCOME-SOURCE-MARKER",
            actor_class="OPERATOR",
            actor_id="operator",
            run_id=self.run_id,
            failure_class="",
            notes="PRIVATE-OUTCOME-NOTES-MARKER",
        )
        self.assertTrue(outcome.ok, outcome.message)

    def test_record_selects_exact_run_and_is_deterministic(self):
        first = build_run_record(self.store, "TASK-RR", self.run_id)
        second = build_run_record(self.store, "TASK-RR", self.run_id)
        self.assertEqual(first, second)
        self.assertEqual(first["record_version"], 1)
        self.assertEqual(first["record_kind"], "MAPS_PORTABLE_RUN_RECORD")
        self.assertEqual(first["run"]["run_id"], self.run_id)
        self.assertEqual(first["record_id"], f"RR-{first['content_sha256']}")
        self.assertEqual(len(first["content_sha256"]), 64)
        self.assertFalse(first["replay"]["complete"])

    def test_default_record_omits_free_text_bodies(self):
        record = build_run_record(self.store, "TASK-RR", self.run_id)
        rendered = dumps_run_record(record)
        for marker in (
            "PRIVATE-TITLE-MARKER",
            "PRIVATE-OUTCOME-MARKER",
            "PRIVATE-AUTHORITY-MARKER",
            "PRIVATE-VERIFICATION-MARKER",
            "PRIVATE-EVIDENCE-EXPECTED-MARKER",
            "PRIVATE-ESCALATION-MARKER",
            "PRIVATE-SUBMISSION-EVIDENCE-MARKER",
            "PRIVATE-REVIEW-SUMMARY-MARKER",
            "PRIVATE-OUTCOME-SOURCE-MARKER",
            "PRIVATE-OUTCOME-NOTES-MARKER",
        ):
            self.assertNotIn(marker, rendered)
        self.assertTrue(record["task"]["text"]["title"]["present"])
        self.assertFalse(record["task"]["text"]["title"]["included"])
        self.assertFalse(record["completion"]["submission"]["evidence"]["included"])

    def test_context_preserves_hash_refs_not_file_contents(self):
        record = build_run_record(self.store, "TASK-RR", self.run_id)
        refs = record["context"]["refs"]
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["path"], "src/context.txt")
        self.assertEqual(len(refs[0]["sha256"]), 64)
        self.assertFalse(record["context"]["content_included"])
        self.assertNotIn("context\n", json.dumps(record))

    def test_outcomes_are_split_by_run_binding(self):
        record = build_run_record(self.store, "TASK-RR", self.run_id)
        self.assertEqual(len(record["outcomes"]["run_bound"]), 1)
        self.assertEqual(record["outcomes"]["run_bound"][0]["run_id"], self.run_id)
        self.assertEqual(record["outcomes"]["task_unbound"], [])

    def test_coverage_is_honest_about_missing_external_trajectory(self):
        record = build_run_record(self.store, "TASK-RR", self.run_id)
        coverage = record["coverage"]
        self.assertEqual(coverage["canonical_task_db"]["state"], CoverageState.VERIFIED.value)
        self.assertEqual(coverage["context_refs"]["state"], CoverageState.VERIFIED.value)
        self.assertEqual(coverage["communication"]["state"], CoverageState.UNKNOWN.value)
        self.assertEqual(
            coverage["session_helper_recovery_lineage"]["state"],
            CoverageState.UNKNOWN.value,
        )
        self.assertEqual(
            coverage["harness_operation_trajectory"]["state"],
            CoverageState.MISSING.value,
        )
        self.assertEqual(coverage["environment"]["state"], CoverageState.MISSING.value)
        self.assertTrue(coverage["environment"]["source_available"])
        self.assertFalse(coverage["environment"]["included"])
        self.assertEqual(record["environment"], [])
        self.assertEqual(coverage["review_subject"]["state"], CoverageState.UNKNOWN.value)

    def test_task_level_reviews_and_timeline_are_not_claimed_as_run_joined(self):
        record = build_run_record(self.store, "TASK-RR", self.run_id)
        self.assertEqual(
            record["completion"]["reviews"]["join_state"],
            CoverageState.UNKNOWN.value,
        )
        self.assertEqual(record["timeline"]["join_state"], CoverageState.UNKNOWN.value)

    def test_criterion_evidence_is_filtered_to_exact_selected_run(self):
        trace = self.store.trace_task("TASK-RR")
        self.assertIsNotNone(trace)
        trace["criterion_evidence"] = {
            "claims": [
                {
                    "id": "claim-selected",
                    "task_id": "TASK-RR",
                    "criterion_id": "criterion-1",
                    "claimed_status": "PASS",
                    "evidence_refs": ["sha256:" + "a" * 64],
                    "task_revision": trace["task_revision"],
                    "run_id": self.run_id,
                    "author_id": "author",
                },
                {
                    "id": "claim-other",
                    "task_id": "TASK-RR",
                    "criterion_id": "criterion-1",
                    "claimed_status": "PASS",
                    "evidence_refs": ["sha256:" + "b" * 64],
                    "task_revision": trace["task_revision"],
                    "run_id": "RUN-OTHER",
                    "author_id": "other-worker",
                },
                {
                    "id": "claim-unbound",
                    "task_id": "TASK-RR",
                    "criterion_id": "criterion-1",
                    "claimed_status": "PASS",
                    "evidence_refs": ["sha256:" + "c" * 64],
                    "task_revision": trace["task_revision"],
                    "run_id": None,
                    "author_id": "author",
                },
            ],
            "verdicts": [
                {"id": "verdict-selected", "claim_id": "claim-selected", "verified_status": "PASS"},
                {"id": "verdict-other", "claim_id": "claim-other", "verified_status": "PASS"},
                {"id": "verdict-unbound", "claim_id": "claim-unbound", "verified_status": "PASS"},
            ],
        }

        record = build_run_record(FakeTraceSource(trace), "TASK-RR", self.run_id)
        evidence = record["completion"]["criterion_evidence"]
        self.assertEqual([item["id"] for item in evidence["claims"]], ["claim-selected"])
        self.assertEqual([item["id"] for item in evidence["verdicts"]], ["verdict-selected"])
        self.assertEqual(evidence["join_state"], CoverageState.VERIFIED.value)
        self.assertEqual(evidence["omitted_task_unbound_claims"], 1)
        self.assertEqual(evidence["omitted_other_run_claims"], 1)

    def test_review_subject_presence_without_selected_run_binding_is_unknown(self):
        trace = self.store.trace_task("TASK-RR")
        self.assertIsNotNone(trace)
        trace["reviews"][0]["subject"] = {
            "review_id": trace["reviews"][0]["id"],
            "run_id": "RUN-OTHER",
            "task_revision": trace["task_revision"],
            "artifact_refs": ["sha256:" + "a" * 64],
        }
        trace["coverage"]["canonical_task_db"]["review_subjects_included"] = True

        record = build_run_record(FakeTraceSource(trace), "TASK-RR", self.run_id)
        self.assertTrue(record["coverage"]["review_subject"]["included"])
        self.assertEqual(
            record["coverage"]["review_subject"]["state"],
            CoverageState.UNKNOWN.value,
        )

    def test_wrong_run_or_task_fails_explicitly(self):
        with self.assertRaisesRegex(RunRecordError, "not bound"):
            build_run_record(self.store, "TASK-RR", "RUN-does-not-exist")
        with self.assertRaisesRegex(RunRecordError, "task not found"):
            build_run_record(self.store, "TASK-does-not-exist", self.run_id)

    def test_future_trace_enrichments_are_detected_without_claiming_replay_complete(self):
        trace = self.store.trace_task("TASK-RR")
        self.assertIsNotNone(trace)
        trace["runs"][0]["environment_evidence"] = [
            {"id": 1, "compatibility_state": "COMPATIBLE", "fingerprint_sha256": "f" * 64}
        ]
        trace["reviews"][0]["subject"] = {
            "review_id": trace["reviews"][0]["id"],
            "run_id": self.run_id,
            "task_revision": trace["task_revision"],
            "artifact_refs": ["sha256:" + "a" * 64],
        }
        trace["coverage"]["canonical_task_db"]["review_subjects_included"] = True

        record = build_run_record(FakeTraceSource(trace), "TASK-RR", self.run_id)
        self.assertEqual(record["coverage"]["environment"]["state"], CoverageState.VERIFIED.value)
        self.assertTrue(record["coverage"]["environment"]["source_available"])
        self.assertTrue(record["coverage"]["environment"]["included"])
        self.assertEqual(record["coverage"]["review_subject"]["state"], CoverageState.VERIFIED.value)
        self.assertEqual(record["environment"][0]["compatibility_state"], "COMPATIBLE")
        self.assertFalse(record["replay"]["complete"])

    def test_malformed_projected_environment_evidence_fails_explicitly(self):
        trace = self.store.trace_task("TASK-RR")
        self.assertIsNotNone(trace)
        trace["runs"][0]["environment_evidence"] = {"not": "a list"}

        with self.assertRaisesRegex(RunRecordError, "environment_evidence must be a list"):
            build_run_record(FakeTraceSource(trace), "TASK-RR", self.run_id)

    def test_json_dump_round_trips(self):
        record = build_run_record(self.store, "TASK-RR", self.run_id)
        rendered = dumps_run_record(record)
        self.assertEqual(json.loads(rendered), record)


if __name__ == "__main__":
    unittest.main()
