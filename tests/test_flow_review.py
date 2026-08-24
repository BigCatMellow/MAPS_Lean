from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.cli import main
from runtime.flow_review import flow_review_start
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


if __name__ == "__main__":
    unittest.main()
