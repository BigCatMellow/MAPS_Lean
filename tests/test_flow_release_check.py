from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.cli import main as cli_main
from runtime.flow_release_check import flow_release_check
from runtime.flow_review import flow_review_record, flow_review_start
from runtime.state import TaskStore


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_PROTOCOL = json.loads(
    (ROOT / "work" / "evals" / "maps-end-to-end-benchmark-v1.json").read_text(
        encoding="utf-8"
    )
)
SHA_A = "sha256:" + "a" * 64
SHA_B = "sha256:" + "b" * 64


def _release_contract(**changes):
    value = {
        "title": "Ship the release",
        "outcome": "The release is verified and shipped.",
        "task_type": "IMPLEMENTATION",
        "owner": "owner-a",
        "risk": "MEDIUM",
        "decision_authority": "Release verification inside the declared scope.",
        "verification": "Run the release checks.",
        "evidence_expected": "Release check summary.",
        "review_required": "OPERATOR_VISIBLE_RELEASE_CHECK",
        "escalation": "Stop on any failed release check.",
        "inputs": ["README.md"],
        "sources": ["AGENTS.md"],
        "dependencies": [],
        "output_paths": ["runtime/example.py"],
        "non_goals": ["No unrelated changes."],
        "acceptance_criteria": ["Release checks pass."],
        "stop_conditions": ["A release check fails."],
    }
    value.update(changes)
    return value


def _acquisition_bundle(observed_ref: str = SHA_A):
    """A one-path acquisition manifest + a matching (or mismatching) observation."""
    return {
        "manifest": {
            "version": "maps-acquisition-paths-v1",
            "release_id": "release-1",
            "paths": [
                {
                    "path_id": "artifact",
                    "kind": "OPERATOR_ARTIFACT",
                    "expected_ref": SHA_A,
                    "operator_visible": True,
                    "allow_not_applicable": True,
                }
            ],
        },
        "observations": [
            {
                "path_id": "artifact",
                "acquisition_state": "OBSERVED",
                "observed_ref": observed_ref,
                "acquisition_evidence_ref": "acquisition:artifact",
                "usability_state": "VERIFIED",
                "usability_evidence_ref": "usability:artifact",
                "not_applicable_decision_ref": None,
            }
        ],
    }


def _failing_benchmark_results():
    """Perfect results except one BLOCKER property forced to FAIL, so
    ``evaluate_benchmark_results`` returns ``benchmark_status == "FAIL"``."""
    results = _perfect_benchmark_results()
    first = BENCHMARK_PROTOCOL["scenarios"][0]
    blocker = next(p["id"] for p in first["properties"] if p["kind"] == "BLOCKER")
    for result in results:
        if result["scenario_id"] == first["id"]:
            result["properties"][blocker] = {
                "state": "FAIL",
                "evidence_refs": [f"evidence:{first['id']}:{blocker}"],
            }
    return results


def _perfect_benchmark_results():
    results = []
    for scenario in BENCHMARK_PROTOCOL["scenarios"]:
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
                    "evidence_refs": [f"evidence:{scenario['id']}:{prop['id']}"],
                }
                for prop in scenario["properties"]
            },
            "measurements": {},
        }
        if layer == "LAYER_3_PRODUCTION_OUTCOME":
            prov = {
                key: {"state": "NOT_APPLICABLE", "ref": None}
                for key in (
                    "task",
                    "run",
                    "outcome",
                    "operator_visible_result",
                    "external_authority",
                    "operator_intervention",
                )
            }
            for key in ("task", "run", "outcome"):
                prov[key] = {"state": "VERIFIED", "ref": f"{key}:{scenario['id']}"}
            if scenario["id"] == "E2E-L3-001":
                prov["operator_visible_result"] = {
                    "state": "VERIFIED",
                    "ref": "artifact:operator-visible",
                }
                prov["external_authority"] = {
                    "state": "VERIFIED",
                    "ref": "authority:task-scope",
                }
            result["provenance"] = prov
            result["measurements"]["operator_intervention_count"] = 0
        results.append(result)
    return results


class FlowReleaseCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = TaskStore(Path(self.tmp.name) / "maps.db")

    def _ready_for_review(self, task_id="REL-1", **contract_changes):
        contract_changes.setdefault(
            "output_paths", [f"runtime/{task_id.lower()}_out.py"]
        )
        self.assertTrue(self.store.create_task(task_id=task_id).ok)
        self.assertTrue(
            self.store.update_contract(
                task_id, _release_contract(**contract_changes)
            ).ok
        )
        self.assertTrue(self.store.promote_ready(task_id).ok)
        self.assertTrue(self.store.claim_task(task_id, "worker-a").ok)
        self.assertTrue(self.store.submit_task(task_id, "worker-a", "shipped").ok)
        return task_id

    def _bind_review_subject(self, task_id):
        result = flow_review_start(
            self.store,
            task_id,
            reviewer_id="reviewer-b",
            freshness_mode="REVISION_BOUND",
            artifact_refs=[SHA_B],
        )
        self.assertTrue(result["ok"], result)
        return int(result["review"]["id"])

    # --- happy paths ---------------------------------------------------

    def test_no_evidence_is_not_applicable_and_ready(self):
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)

        result = flow_release_check(self.store, task_id, recorded_by="releaser")

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["code"], "FLOW_RELEASE_CHECK_ASSEMBLED")
        self.assertEqual(result["summary"]["artifact_identity"]["state"], "NOT_APPLICABLE")
        self.assertEqual(result["summary"]["release_smoke"]["state"], "NOT_APPLICABLE")
        self.assertEqual(result["summary"]["composite"], "READY_FOR_OPERATOR_VERDICT")
        self.assertEqual(
            result["next_step"]["state"], "STOPPED_BEFORE_RELEASE_VERDICT"
        )
        # persisted
        stored = self.store.get_release_check(result["release_check_id"])
        self.assertEqual(stored["composite_state"], "READY_FOR_OPERATOR_VERDICT")
        self.assertEqual(stored["task_id"], task_id)

    def test_green_artifact_identity_and_smoke_is_ready(self):
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)

        result = flow_release_check(
            self.store,
            task_id,
            recorded_by="releaser",
            evidence={
                "acquisition": _acquisition_bundle(observed_ref=SHA_A),
                "benchmark": {
                    "protocol": BENCHMARK_PROTOCOL,
                    "results": _perfect_benchmark_results(),
                },
            },
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["summary"]["artifact_identity"]["state"], "PASS")
        self.assertEqual(result["summary"]["release_smoke"]["state"], "COMPLETE")
        self.assertEqual(result["summary"]["composite"], "READY_FOR_OPERATOR_VERDICT")
        self.assertTrue(
            result["summary"]["artifact_identity"]["report_ref"].startswith(
                "acquisition-report:"
            )
        )
        stored = self.store.get_release_check(result["release_check_id"])
        self.assertGreaterEqual(len(stored["input_evidence_refs"]), 2)

    def test_failing_release_smoke_blocks_with_passing_artifact_identity(self):
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)

        result = flow_release_check(
            self.store,
            task_id,
            recorded_by="releaser",
            evidence={
                "acquisition": _acquisition_bundle(observed_ref=SHA_A),
                "benchmark": {
                    "protocol": BENCHMARK_PROTOCOL,
                    "results": _failing_benchmark_results(),
                },
            },
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["summary"]["artifact_identity"]["state"], "PASS")
        self.assertEqual(result["summary"]["release_smoke"]["state"], "FAIL")
        self.assertEqual(result["summary"]["composite"], "BLOCKED")
        self.assertEqual(
            self.store.get_release_check(result["release_check_id"])["composite_state"],
            "BLOCKED",
        )

    def test_mismatched_artifact_ref_blocks(self):
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)

        result = flow_release_check(
            self.store,
            task_id,
            recorded_by="releaser",
            evidence={"acquisition": _acquisition_bundle(observed_ref=SHA_B)},
        )

        self.assertTrue(result["ok"], result)  # the flow assembled fine
        self.assertEqual(result["summary"]["artifact_identity"]["state"], "FAIL")
        self.assertEqual(result["summary"]["composite"], "BLOCKED")
        self.assertIn(
            "hard-blocks record_review APPROVED", result["next_step"]["reason"]
        )

    def test_unacked_blocked_composite_refuses_review_approval(self):
        """6.21 slice 3b — an un-acknowledged BLOCKED composite hard-blocks
        record_review APPROVED for an OPERATOR_VISIBLE_RELEASE_CHECK task."""
        task_id = self._ready_for_review()
        review_id = self._bind_review_subject(task_id)

        blocked = flow_release_check(
            self.store,
            task_id,
            recorded_by="releaser",
            evidence={"acquisition": _acquisition_bundle(observed_ref=SHA_B)},
        )
        self.assertEqual(blocked["summary"]["composite"], "BLOCKED")

        approved = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer-b",
            verdict="APPROVED",
            summary="release check BLOCKED, no ack",
            rederived_artifact_refs=[],
        )
        self.assertFalse(approved["ok"], approved)
        self.assertEqual(
            approved["step_result"]["code"], "RELEASE_CHECK_COMPOSITE_BLOCKED"
        )
        self.assertEqual(self.store.get_task(task_id)["status"], "READY_FOR_REVIEW")
        self.assertEqual(
            self.store.latest_release_check(task_id, review_id)["composite_state"],
            "BLOCKED",
        )

    def test_acked_blocked_composite_allows_review_approval(self):
        """A non-empty operator_ack_ref on the latest row is the recorded override."""
        task_id = self._ready_for_review()
        review_id = self._bind_review_subject(task_id)

        blocked = flow_release_check(
            self.store,
            task_id,
            recorded_by="releaser",
            evidence={"acquisition": _acquisition_bundle(observed_ref=SHA_B)},
            operator_ack_ref="operator-note:2026-09-02-override",
        )
        self.assertEqual(blocked["summary"]["composite"], "BLOCKED")

        approved = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer-b",
            verdict="APPROVED",
            summary="release check BLOCKED but operator-acknowledged",
            rederived_artifact_refs=[],
        )
        self.assertTrue(approved["ok"], approved)
        self.assertEqual(self.store.get_task(task_id)["status"], "DONE")
        self.assertEqual(
            self.store.latest_release_check(task_id, review_id)["composite_state"],
            "BLOCKED",
        )

    def test_no_release_check_row_refuses_review_approval(self):
        """No release_checks row for an OPERATOR_VISIBLE_RELEASE_CHECK task
        refuses APPROVED — the check is mandatory for this review type."""
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)

        approved = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer-b",
            verdict="APPROVED",
            summary="no release check recorded",
            rederived_artifact_refs=[],
        )
        self.assertFalse(approved["ok"], approved)
        self.assertEqual(approved["step_result"]["code"], "RELEASE_CHECK_REQUIRED")
        self.assertEqual(self.store.get_task(task_id)["status"], "READY_FOR_REVIEW")

    def test_ready_release_check_allows_review_approval(self):
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)

        check = flow_release_check(
            self.store,
            task_id,
            recorded_by="releaser",
            evidence={"acquisition": _acquisition_bundle(observed_ref=SHA_A)},
        )
        self.assertEqual(check["summary"]["composite"], "READY_FOR_OPERATOR_VERDICT")

        approved = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer-b",
            verdict="APPROVED",
            summary="release check ready",
            rederived_artifact_refs=[],
        )
        self.assertTrue(approved["ok"], approved)
        self.assertEqual(self.store.get_task(task_id)["status"], "DONE")

    def test_rerun_blocked_to_ready_unblocks_review_approval(self):
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)

        first = flow_release_check(
            self.store,
            task_id,
            recorded_by="releaser",
            evidence={"acquisition": _acquisition_bundle(observed_ref=SHA_B)},
        )
        self.assertEqual(first["summary"]["composite"], "BLOCKED")

        blocked = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer-b",
            verdict="APPROVED",
            summary="still blocked",
            rederived_artifact_refs=[],
        )
        self.assertFalse(blocked["ok"], blocked)
        self.assertEqual(
            blocked["step_result"]["code"], "RELEASE_CHECK_COMPOSITE_BLOCKED"
        )

        second = flow_release_check(
            self.store,
            task_id,
            recorded_by="releaser",
            evidence={"acquisition": _acquisition_bundle(observed_ref=SHA_A)},
        )
        self.assertEqual(second["summary"]["composite"], "READY_FOR_OPERATOR_VERDICT")

        approved = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer-b",
            verdict="APPROVED",
            summary="re-run is ready",
            rederived_artifact_refs=[],
        )
        self.assertTrue(approved["ok"], approved)
        self.assertEqual(self.store.get_task(task_id)["status"], "DONE")

    def test_gate_does_not_fire_for_non_release_review_types(self):
        """The 3b gate is scoped to OPERATOR_VISIBLE_RELEASE_CHECK — other
        review types approve with no release_checks row."""
        for review_type in ("INDEPENDENT_REVIEW", "OWNER_CHECK"):
            with self.subTest(review_type=review_type):
                task_id = f"REL-ISO-{review_type}"
                self._ready_for_review(
                    task_id=task_id, review_required=review_type
                )
                self.assertTrue(self.store.claim_review(task_id, "reviewer-b").ok)
                approved = flow_review_record(
                    self.store,
                    task_id,
                    reviewer_id="reviewer-b",
                    verdict="APPROVED",
                    summary="approved without a release check",
                    rederived_artifact_refs=[],
                )
                self.assertTrue(approved["ok"], approved)
                self.assertEqual(self.store.get_task(task_id)["status"], "DONE")

    def test_rerun_appends_a_new_row(self):
        task_id = self._ready_for_review()
        review_id = self._bind_review_subject(task_id)

        first = flow_release_check(
            self.store,
            task_id,
            recorded_by="releaser",
            evidence={"acquisition": _acquisition_bundle(observed_ref=SHA_B)},
        )
        second = flow_release_check(
            self.store,
            task_id,
            recorded_by="releaser",
            evidence={"acquisition": _acquisition_bundle(observed_ref=SHA_A)},
        )
        self.assertNotEqual(first["release_check_id"], second["release_check_id"])
        self.assertEqual(len(self.store.list_release_checks(task_id)), 2)
        self.assertEqual(
            self.store.latest_release_check(task_id, review_id)["composite_state"],
            "READY_FOR_OPERATOR_VERDICT",
        )

    # --- guard failures ----------------------------------------------

    def test_unknown_task(self):
        result = flow_release_check(self.store, "NOPE", recorded_by="releaser")
        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "preflight")
        self.assertEqual(result["step_result"]["code"], "NOT_FOUND")

    def test_wrong_review_type(self):
        task_id = self._ready_for_review(
            task_id="REL-2", review_required="INDEPENDENT_REVIEW"
        )
        result = flow_release_check(self.store, task_id, recorded_by="releaser")
        self.assertFalse(result["ok"])
        self.assertEqual(result["step_result"]["code"], "RELEASE_CHECK_NOT_APPLICABLE")

    def test_no_open_review(self):
        task_id = self._ready_for_review()
        result = flow_release_check(self.store, task_id, recorded_by="releaser")
        self.assertFalse(result["ok"])
        self.assertEqual(
            result["step_result"]["code"], "RELEASE_CHECK_NO_OPEN_REVIEW"
        )

    def test_no_bound_subject(self):
        task_id = self._ready_for_review()
        # claim_review without a subject binding
        self.assertTrue(self.store.claim_review(task_id, "reviewer-b").ok)
        result = flow_release_check(self.store, task_id, recorded_by="releaser")
        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "subject_preflight")
        self.assertEqual(
            result["step_result"]["code"], "RELEASE_CHECK_NO_BOUND_SUBJECT"
        )

    def test_malformed_acquisition_evidence(self):
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)
        result = flow_release_check(
            self.store,
            task_id,
            recorded_by="releaser",
            evidence={"acquisition": {"manifest": {"version": "wrong"}, "observations": []}},
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "artifact_identity")
        self.assertEqual(
            result["step_result"]["code"], "INVALID_ACQUISITION_EVIDENCE"
        )

    def test_malformed_benchmark_evidence(self):
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)
        result = flow_release_check(
            self.store,
            task_id,
            recorded_by="releaser",
            evidence={"benchmark": {"protocol": {"version": "nope"}, "results": []}},
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "release_smoke")
        self.assertEqual(result["step_result"]["code"], "INVALID_BENCHMARK_EVIDENCE")

    def test_missing_recorded_by(self):
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)
        result = flow_release_check(self.store, task_id, recorded_by="  ")
        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "record")

    # --- end to end --------------------------------------------------

    def test_end_to_end_release_check_then_approve(self):
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)

        check = flow_release_check(
            self.store,
            task_id,
            recorded_by="releaser",
            evidence={"acquisition": _acquisition_bundle(observed_ref=SHA_A)},
        )
        self.assertEqual(check["summary"]["composite"], "READY_FOR_OPERATOR_VERDICT")

        recorded = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer-b",
            verdict="APPROVED",
            summary=f"release check {check['release_check_id']}: ready",
            rederived_artifact_refs=[],
        )
        self.assertTrue(recorded["ok"], recorded)
        self.assertEqual(self.store.get_task(task_id)["status"], "DONE")

    def test_cli_flow_release_check_end_to_end(self):
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)
        db = str(Path(self.tmp.name) / "maps.db")
        evidence_path = Path(self.tmp.name) / "evidence.json"
        evidence_path.write_text(
            json.dumps({"acquisition": _acquisition_bundle(observed_ref=SHA_A)}),
            encoding="utf-8",
        )

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = cli_main(
                [
                    "--db", db, "flow", "release-check", task_id,
                    "--recorded-by", "releaser",
                    "--evidence-json", str(evidence_path),
                ]
            )
        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["code"], "FLOW_RELEASE_CHECK_ASSEMBLED")
        self.assertEqual(payload["summary"]["artifact_identity"]["state"], "PASS")

    def test_cli_flow_release_check_bad_evidence_path_exits_nonzero(self):
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)
        db = str(Path(self.tmp.name) / "maps.db")
        with redirect_stdout(io.StringIO()):
            code = cli_main(
                [
                    "--db", db, "flow", "release-check", task_id,
                    "--recorded-by", "releaser",
                    "--evidence-json", str(Path(self.tmp.name) / "nope.json"),
                ]
            )
        self.assertEqual(code, 2)

    def test_store_record_release_check_rejects_cross_task_review(self):
        task_a = self._ready_for_review(task_id="REL-A")
        review_a = self._bind_review_subject(task_a)
        task_b = self._ready_for_review(task_id="REL-B")

        result = self.store.record_release_check(
            task_b,
            review_a,  # a review belonging to task_a
            artifact_identity_state="NOT_APPLICABLE",
            release_smoke_state="NOT_APPLICABLE",
            composite_state="READY_FOR_OPERATOR_VERDICT",
            summary={},
            recorded_by="releaser",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "RELEASE_CHECK_TASK_MISMATCH")
        self.assertEqual(self.store.list_release_checks(task_b), [])

    def test_store_record_release_check_rejects_bad_composite_state(self):
        task_id = self._ready_for_review()
        review_id = self._bind_review_subject(task_id)
        result = self.store.record_release_check(
            task_id,
            review_id,
            artifact_identity_state="NOT_APPLICABLE",
            release_smoke_state="NOT_APPLICABLE",
            composite_state="MAYBE",
            summary={},
            recorded_by="releaser",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "INVALID_RELEASE_CHECK")

    def test_state_store_release_check_is_immutable(self):
        task_id = self._ready_for_review()
        self._bind_review_subject(task_id)
        result = flow_release_check(self.store, task_id, recorded_by="releaser")
        rc_id = result["release_check_id"]
        with self.store._connect() as conn:  # noqa: SLF001 - test asserts the trigger
            with self.assertRaises(Exception):
                conn.execute(
                    "UPDATE release_checks SET composite_state = 'BLOCKED' WHERE id = ?",
                    (rc_id,),
                )
            with self.assertRaises(Exception):
                conn.execute("DELETE FROM release_checks WHERE id = ?", (rc_id,))


if __name__ == "__main__":
    unittest.main()
