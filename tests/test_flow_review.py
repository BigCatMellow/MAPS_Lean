from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.cli import main
from runtime.flow_review import flow_review_record, flow_review_start
from runtime.state import TaskStore


SHA_A = "sha256:" + "a" * 64


def policy(**changes) -> dict:
    value = {
        "requires_operator_approval": False,
        "destructive_action": False,
        "external_side_effect": False,
        "security_sensitive": False,
        "broad_architecture": False,
        "paid_execution": False,
    }
    value.update(changes)
    return value


def contract(
    *,
    risk: str = "LOW",
    review_required: str = "INDEPENDENT_REVIEW",
    output_paths: list[str] | None = None,
) -> dict:
    return {
        "title": "Flow review fixture",
        "outcome": "Review can start deterministically",
        "task_type": "IMPLEMENTATION",
        "owner": "author",
        "risk": risk,
        "decision_authority": "bounded implementation",
        "verification": "flow review tests",
        "evidence_expected": "test output",
        "review_required": review_required,
        "escalation": "operator on scope change",
        "inputs": ["README.md"],
        "sources": ["AGENTS.md"],
        "dependencies": [],
        "output_paths": output_paths or ["src"],
        "non_goals": ["no verdict flow"],
        "acceptance_criteria": ["review subject is explicit when required"],
        "stop_conditions": ["stop on stale subject"],
        "policy": policy(),
    }


class FlowReviewTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "README.md").write_text("fixture\n", encoding="utf-8")
        (self.repo / "AGENTS.md").write_text("authority\n", encoding="utf-8")
        self.store = TaskStore(self.root / "maps.db")

    def submitted(
        self,
        *,
        risk: str = "LOW",
        review_required: str = "INDEPENDENT_REVIEW",
        output_paths: list[str] | None = None,
    ):
        for output_path in output_paths or ["src"]:
            (self.repo / output_path).mkdir(exist_ok=True)
        created = self.store.create_task(title="flow review fixture")
        self.assertTrue(created.ok, created.message)
        task_id = created.task["task_id"]
        shaped = self.store.update_contract(
            task_id,
            contract(
                risk=risk,
                review_required=review_required,
                output_paths=output_paths,
            ),
        )
        self.assertTrue(shaped.ok, shaped.message)
        self.assertTrue(self.store.promote_ready(task_id).ok)
        self.assertTrue(self.store.claim_task(task_id, "author", lease_seconds=600).ok)
        run = self.store.create_run_manifest(
            task_id,
            "author",
            repo_root=self.repo,
            created_by="tester",
            readable_paths=["."],
            writable_paths=output_paths or ["src"],
            base_revision="base",
        )
        self.assertTrue(run.ok, run.message)
        submitted = self.store.submit_task(task_id, "author", "ready for review")
        self.assertTrue(submitted.ok, submitted.message)
        return task_id, run.task

    def test_flow_review_start_claims_simple_review_without_subject(self):
        task_id, _ = self.submitted(risk="LOW")

        result = flow_review_start(self.store, task_id, reviewer_id="reviewer")

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["code"], "FLOW_REVIEW_STARTED")
        self.assertEqual(result["reviewer_id"], "reviewer")
        self.assertFalse(result["review_subject_required"])
        self.assertIsNone(result["review_subject"])
        self.assertEqual(result["claim"]["code"], "REVIEW_CLAIMED")
        self.assertEqual(
            result["next_step"]["state"],
            "STOPPED_BEFORE_REVIEW_VERDICT",
        )
        self.assertEqual(self.store.get_task(task_id)["status"], "READY_FOR_REVIEW")

    def test_consequential_review_requires_subject_before_claim(self):
        task_id, _ = self.submitted(risk="HIGH")

        result = flow_review_start(self.store, task_id, reviewer_id="reviewer")

        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "review_subject_preflight")
        self.assertEqual(result["step_result"]["code"], "REVIEW_SUBJECT_REQUIRED")
        self.assertEqual(self.store.list_reviews(task_id), [])

    def test_flow_review_start_binds_subject_when_supplied(self):
        task_id, run = self.submitted(risk="HIGH")

        result = flow_review_start(
            self.store,
            task_id,
            reviewer_id="reviewer",
            run_id=run["run_id"],
            artifact_refs=[SHA_A],
        )

        self.assertTrue(result["ok"], result)
        self.assertTrue(result["review_subject_required"])
        subject = result["review_subject"]
        self.assertIsNotNone(subject)
        self.assertEqual(subject["run_id"], run["run_id"])
        self.assertEqual(subject["artifact_refs"], [SHA_A])
        self.assertEqual(subject["freshness_mode"], "REVISION_BOUND")
        self.assertEqual(self.store.get_task(task_id)["status"], "READY_FOR_REVIEW")

    def test_flow_review_start_stops_when_claim_fails(self):
        created = self.store.create_task(title="unreviewable")
        self.assertTrue(created.ok, created.message)

        result = flow_review_start(
            self.store,
            created.task["task_id"],
            reviewer_id="reviewer",
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "claim")
        self.assertEqual(result["step_result"]["code"], "NOT_REVIEWABLE")

    def test_invalid_subject_does_not_leave_open_review(self):
        task_id, run = self.submitted(risk="HIGH")

        result = flow_review_start(
            self.store,
            task_id,
            reviewer_id="reviewer",
            run_id=run["run_id"],
            artifact_refs=["build/release.zip"],
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "claim_with_subject")
        self.assertEqual(result["step_result"]["code"], "INVALID_ARTIFACT_REF")
        self.assertEqual(self.store.list_reviews(task_id), [])

    def test_invalid_freshness_mode_does_not_leave_open_review(self):
        task_id, run = self.submitted(risk="HIGH")

        result = flow_review_start(
            self.store,
            task_id,
            reviewer_id="reviewer",
            freshness_mode="STALE",
            run_id=run["run_id"],
            artifact_refs=[SHA_A],
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "claim_with_subject")
        self.assertEqual(result["step_result"]["code"], "INVALID_FRESHNESS_MODE")
        self.assertEqual(self.store.list_reviews(task_id), [])

    def test_foreign_run_does_not_leave_open_review(self):
        task_id, _ = self.submitted(risk="HIGH")
        other_task_id, other_run = self.submitted(risk="LOW", output_paths=["other-src"])

        result = flow_review_start(
            self.store,
            task_id,
            reviewer_id="reviewer",
            run_id=other_run["run_id"],
            artifact_refs=[SHA_A],
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "claim_with_subject")
        self.assertEqual(result["step_result"]["code"], "INVALID_REVIEW_RUN")
        self.assertEqual(self.store.list_reviews(task_id), [])
        self.assertEqual(self.store.list_reviews(other_task_id), [])

    def test_stale_run_does_not_leave_open_review(self):
        task_id, run = self.submitted(risk="HIGH")
        with self.store._connect() as conn:
            conn.execute(
                "UPDATE tasks SET title = 'changed behind run' WHERE task_id = ?",
                (task_id,),
            )

        result = flow_review_start(
            self.store,
            task_id,
            reviewer_id="reviewer",
            run_id=run["run_id"],
            artifact_refs=[SHA_A],
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "claim_with_subject")
        self.assertEqual(result["step_result"]["code"], "STALE_REVIEW_RUN")
        self.assertEqual(self.store.list_reviews(task_id), [])

    def test_cli_flow_review_start_emits_json_success(self):
        task_id, run = self.submitted(risk="HIGH")
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            exit_code = main(
                [
                    "--db",
                    str(self.root / "maps.db"),
                    "flow",
                    "review-start",
                    task_id,
                    "--reviewer-id",
                    "reviewer",
                    "--run-id",
                    run["run_id"],
                    "--artifact-ref",
                    SHA_A,
                ]
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["code"], "FLOW_REVIEW_STARTED")
        self.assertEqual(payload["review_subject"]["artifact_refs"], [SHA_A])

    def test_cli_flow_review_start_failure_exits_nonzero(self):
        task_id, _ = self.submitted(risk="HIGH")
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            exit_code = main(
                [
                    "--db",
                    str(self.root / "maps.db"),
                    "flow",
                    "review-start",
                    task_id,
                    "--reviewer-id",
                    "reviewer",
                ]
            )

        self.assertEqual(exit_code, 2)
        payload = json.loads(buffer.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["failed_step"], "review_subject_preflight")


SHA_B = "sha256:" + "b" * 64


class FlowReviewRecordTests(unittest.TestCase):
    """`flow_review_record` — verdict recording as a composition over
    `record_review`, adding freshness-mode-aware re-derived artifact refs."""

    # Reuse the fixture builders from FlowReviewTests without inheriting (and
    # re-running) its test methods.
    setUp = FlowReviewTests.setUp
    submitted = FlowReviewTests.submitted

    def _started(self, *, risk="LOW", reviewer="reviewer", **start_kwargs):
        task_id, run = self.submitted(risk=risk)
        started = flow_review_start(
            self.store, task_id, reviewer_id=reviewer, **start_kwargs
        )
        self.assertTrue(started["ok"], started)
        return task_id, run

    def test_revision_bound_subject_approved_goes_done(self):
        task_id, run = self._started(
            run_id=None, freshness_mode="REVISION_BOUND", artifact_refs=[SHA_A]
        )

        result = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="APPROVED",
            summary="verified independently",
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["code"], "FLOW_REVIEW_RECORDED")
        self.assertEqual(result["verdict"], "APPROVED")
        self.assertEqual(result["new_status"], "DONE")
        self.assertEqual(result["review"]["verdict"], "APPROVED")
        self.assertIsNotNone(result["review"]["completed_at"])
        self.assertEqual(self.store.get_task(task_id)["status"], "DONE")
        # Deterministic-flow family convention: a machine-readable next_step in
        # the same {state, reason} shape as flow_start / flow_review_start.
        self.assertEqual(result["next_step"]["state"], "REVIEW_RECORDED")
        self.assertIn("DONE", result["next_step"]["reason"])
        self.assertIn("does not", result["next_step"]["reason"])

    def test_rederived_subject_approved_with_matching_refs_goes_done(self):
        task_id, _ = self._started(
            freshness_mode="REDERIVED_AT_REVIEW", artifact_refs=[SHA_A]
        )

        result = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="APPROVED",
            summary="re-derived and matched",
            rederived_artifact_refs=[SHA_A],
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["new_status"], "DONE")
        self.assertEqual(self.store.get_task(task_id)["status"], "DONE")

    def test_rederived_subject_approved_without_refs_fails_early(self):
        task_id, _ = self._started(
            freshness_mode="REDERIVED_AT_REVIEW", artifact_refs=[SHA_A]
        )

        result = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="APPROVED",
            summary="forgot to pass refs",
        )

        self.assertFalse(result["ok"])
        # Early deterministic preflight, NOT a raw hook error surfaced from deep
        # inside record_review.
        self.assertEqual(result["failed_step"], "rederivation_preflight")
        self.assertEqual(
            result["step_result"]["code"], "REVIEW_REDERIVATION_REQUIRED"
        )
        # Nothing recorded; the review is still open and the task unchanged.
        self.assertEqual(self.store.get_task(task_id)["status"], "READY_FOR_REVIEW")
        open_reviews = [
            r for r in self.store.list_reviews(task_id) if r["completed_at"] is None
        ]
        self.assertEqual(len(open_reviews), 1)

    def test_rederived_subject_mismatched_refs_rejected_by_store(self):
        task_id, _ = self._started(
            freshness_mode="REDERIVED_AT_REVIEW", artifact_refs=[SHA_A]
        )

        result = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="APPROVED",
            summary="wrong refs",
            rederived_artifact_refs=[SHA_B],
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "record")
        self.assertEqual(
            result["step_result"]["code"], "REVIEW_REDERIVATION_MISMATCH"
        )

    def test_non_owner_reviewer_rejected_by_store(self):
        task_id, _ = self._started(
            freshness_mode="REVISION_BOUND", artifact_refs=[SHA_A]
        )

        result = flow_review_record(
            self.store,
            task_id,
            reviewer_id="someone-else",
            verdict="APPROVED",
            summary="not my review",
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "record")
        self.assertEqual(result["step_result"]["code"], "NOT_REVIEW_OWNER")
        # The subject binding must NOT leak to a non-owner: the flow skips its
        # own preflight entirely when the caller does not hold the review.
        self.assertNotIn("rederiv", json.dumps(result).lower())
        self.assertNotIn("freshness_mode", json.dumps(result))

    def test_non_owner_of_rederived_review_sees_no_subject(self):
        task_id, _ = self._started(
            freshness_mode="REDERIVED_AT_REVIEW", artifact_refs=[SHA_A]
        )

        result = flow_review_record(
            self.store,
            task_id,
            reviewer_id="someone-else",
            verdict="APPROVED",
            summary="not my review",
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "record")
        self.assertEqual(result["step_result"]["code"], "NOT_REVIEW_OWNER")
        self.assertNotIn("REDERIVED_AT_REVIEW", json.dumps(result))
        self.assertNotIn(SHA_A, json.dumps(result))

    def test_verdict_is_normalized_in_result(self):
        task_id, _ = self._started(
            freshness_mode="REVISION_BOUND", artifact_refs=[SHA_A]
        )

        result = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="approved",
            summary="lowercase verdict still works",
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["verdict"], "APPROVED")
        self.assertEqual(result["new_status"], "DONE")

    def test_no_open_review_rejected_by_store(self):
        task_id, _ = self.submitted(risk="LOW")

        result = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="APPROVED",
            summary="nobody claimed",
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "record")
        self.assertEqual(result["step_result"]["code"], "NO_OPEN_REVIEW")

    def test_changes_requested_sets_status(self):
        task_id, _ = self._started(
            freshness_mode="REVISION_BOUND", artifact_refs=[SHA_A]
        )

        result = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="CHANGES_REQUESTED",
            summary="please fix",
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["new_status"], "CHANGES_REQUESTED")
        self.assertEqual(
            self.store.get_task(task_id)["status"], "CHANGES_REQUESTED"
        )

    def test_blocked_sets_status(self):
        task_id, _ = self._started(
            freshness_mode="REVISION_BOUND", artifact_refs=[SHA_A]
        )

        result = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="BLOCKED",
            summary="external blocker",
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["new_status"], "BLOCKED")
        self.assertEqual(self.store.get_task(task_id)["status"], "BLOCKED")

    def test_blocked_on_rederived_subject_needs_no_refs(self):
        # The rederivation preflight mirrors the hook, which is APPROVED-only.
        task_id, _ = self._started(
            freshness_mode="REDERIVED_AT_REVIEW", artifact_refs=[SHA_A]
        )

        result = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="BLOCKED",
            summary="blocked before re-derivation",
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["new_status"], "BLOCKED")

    def test_not_ready_for_review_rejected_by_store(self):
        task_id, _ = self._started(
            freshness_mode="REVISION_BOUND", artifact_refs=[SHA_A]
        )
        first = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="CHANGES_REQUESTED",
            summary="round one",
        )
        self.assertTrue(first["ok"], first)

        # Task is now CHANGES_REQUESTED; a second record has no open review.
        second = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="APPROVED",
            summary="round two",
        )
        self.assertFalse(second["ok"])
        self.assertEqual(second["failed_step"], "record")
        self.assertEqual(second["step_result"]["code"], "NO_OPEN_REVIEW")

    def test_cli_flow_review_record_end_to_end(self):
        task_id, _ = self.submitted(risk="LOW")
        db = str(self.root / "maps.db")

        with redirect_stdout(io.StringIO()):
            start_code = main(
                [
                    "--db", db, "flow", "review-start", task_id,
                    "--reviewer-id", "reviewer",
                    "--freshness-mode", "REDERIVED_AT_REVIEW",
                    "--artifact-ref", SHA_A,
                ]
            )
        self.assertEqual(start_code, 0)

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(
                [
                    "--db", db, "flow", "review-record", task_id,
                    "--reviewer-id", "reviewer",
                    "--verdict", "APPROVED",
                    "--summary", "cli approved after re-derivation",
                    "--rederived-artifact-ref", SHA_A,
                ]
            )

        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["code"], "FLOW_REVIEW_RECORDED")
        self.assertEqual(payload["new_status"], "DONE")
        self.assertEqual(self.store.get_task(task_id)["status"], "DONE")

    def test_cli_flow_review_record_missing_refs_exits_nonzero(self):
        task_id, _ = self.submitted(risk="LOW")
        db = str(self.root / "maps.db")
        with redirect_stdout(io.StringIO()):
            start_code = main(
                [
                    "--db", db, "flow", "review-start", task_id,
                    "--reviewer-id", "reviewer",
                    "--freshness-mode", "REDERIVED_AT_REVIEW",
                    "--artifact-ref", SHA_A,
                ]
            )
        self.assertEqual(start_code, 0)

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(
                [
                    "--db", db, "flow", "review-record", task_id,
                    "--reviewer-id", "reviewer",
                    "--verdict", "APPROVED",
                    "--summary", "no refs supplied",
                ]
            )

        self.assertEqual(code, 2)
        payload = json.loads(buffer.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["failed_step"], "rederivation_preflight")


class FlowReviewSequenceTests(unittest.TestCase):
    """`flow_review_start` -> `flow_review_record` as one coherent deterministic
    sequence: the subject bound by start is exactly the one record validates
    against, and the review row is the same across both verbs."""

    setUp = FlowReviewTests.setUp
    submitted = FlowReviewTests.submitted

    def test_revision_bound_start_then_record_is_coherent(self):
        task_id, _ = self.submitted(risk="HIGH")

        started = flow_review_start(
            self.store,
            task_id,
            reviewer_id="reviewer",
            freshness_mode="REVISION_BOUND",
            artifact_refs=[SHA_A],
        )
        self.assertTrue(started["ok"], started)
        self.assertEqual(started["next_step"]["state"], "STOPPED_BEFORE_REVIEW_VERDICT")
        started_review_id = started["review"]["id"]
        self.assertEqual(started["review_subject"]["artifact_refs"], [SHA_A])

        recorded = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="APPROVED",
            summary="coherent sequence",
        )
        self.assertTrue(recorded["ok"], recorded)
        # Same review row closed that start opened.
        self.assertEqual(recorded["review"]["id"], started_review_id)
        self.assertEqual(recorded["new_status"], "DONE")
        self.assertEqual(recorded["next_step"]["state"], "REVIEW_RECORDED")
        self.assertEqual(self.store.get_task(task_id)["status"], "DONE")

    def test_rederived_start_then_record_matching_refs_is_coherent(self):
        task_id, _ = self.submitted(risk="HIGH")

        started = flow_review_start(
            self.store,
            task_id,
            reviewer_id="reviewer",
            freshness_mode="REDERIVED_AT_REVIEW",
            artifact_refs=[SHA_A],
        )
        self.assertTrue(started["ok"], started)
        bound_refs = started["review_subject"]["artifact_refs"]
        self.assertEqual(bound_refs, [SHA_A])

        # Record consuming exactly the refs start bound -> DONE.
        recorded = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="APPROVED",
            summary="re-derived to the bound subject",
            rederived_artifact_refs=bound_refs,
        )
        self.assertTrue(recorded["ok"], recorded)
        self.assertEqual(recorded["review"]["id"], started["review"]["id"])
        self.assertEqual(recorded["new_status"], "DONE")

    def test_second_round_review_resolves_the_latest_completed_review(self):
        # Round 1: CHANGES_REQUESTED. Author resubmits. Round 2: APPROVED.
        # flow_review_record must report the round-2 review, not round 1.
        task_id, _ = self.submitted(risk="LOW")

        r1_start = flow_review_start(self.store, task_id, reviewer_id="reviewer")
        self.assertTrue(r1_start["ok"], r1_start)
        r1 = flow_review_record(
            self.store, task_id, reviewer_id="reviewer",
            verdict="CHANGES_REQUESTED", summary="round one",
        )
        self.assertTrue(r1["ok"], r1)
        r1_review_id = r1["review"]["id"]

        # author re-claims CHANGES_REQUESTED, addresses feedback, resubmits
        self.assertTrue(
            self.store.claim_task(task_id, "author", lease_seconds=600).ok
        )
        self.assertTrue(
            self.store.submit_task(task_id, "author", "round two ready").ok
        )
        r2_start = flow_review_start(self.store, task_id, reviewer_id="reviewer")
        self.assertTrue(r2_start["ok"], r2_start)
        r2 = flow_review_record(
            self.store, task_id, reviewer_id="reviewer",
            verdict="APPROVED", summary="round two",
        )
        self.assertTrue(r2["ok"], r2)
        self.assertNotEqual(r2["review"]["id"], r1_review_id)
        self.assertEqual(r2["review"]["id"], r2_start["review"]["id"])
        self.assertEqual(r2["review"]["verdict"], "APPROVED")
        self.assertEqual(r2["new_status"], "DONE")

    def test_rederived_start_then_record_mismatched_refs_rejected_by_store(self):
        task_id, _ = self.submitted(risk="HIGH")

        started = flow_review_start(
            self.store,
            task_id,
            reviewer_id="reviewer",
            freshness_mode="REDERIVED_AT_REVIEW",
            artifact_refs=[SHA_A],
        )
        self.assertTrue(started["ok"], started)

        recorded = flow_review_record(
            self.store,
            task_id,
            reviewer_id="reviewer",
            verdict="APPROVED",
            summary="re-derived to the wrong subject",
            rederived_artifact_refs=[SHA_B],
        )
        self.assertFalse(recorded["ok"])
        self.assertEqual(recorded["failed_step"], "record")
        self.assertEqual(
            recorded["step_result"]["code"], "REVIEW_REDERIVATION_MISMATCH"
        )
        # Review still open — the sequence did not close it on a store rejection.
        self.assertEqual(
            self.store.get_task(task_id)["status"], "READY_FOR_REVIEW"
        )


if __name__ == "__main__":
    unittest.main()
