from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest

from runtime.state import TaskStore


SHA_A = "sha256:" + "a" * 64
SHA_B = "sha256:" + "b" * 64


def policy():
    return {
        "requires_operator_approval": False,
        "destructive_action": False,
        "external_side_effect": False,
        "security_sensitive": False,
        "broad_architecture": False,
        "paid_execution": False,
    }


def contract(*, risk="LOW", criteria=None):
    return {
        "title": "Revision-bound review task",
        "outcome": "The exact reviewed subject is mechanically identifiable",
        "task_type": "IMPLEMENTATION",
        "owner": "author",
        "risk": risk,
        "decision_authority": "Implementation choices inside declared scope",
        "verification": "Run deterministic tests",
        "evidence_expected": "Immutable evidence references",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "Stop on stale or ambiguous review evidence",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": ["src"],
        "non_goals": ["No unrelated changes"],
        "acceptance_criteria": criteria or ["review subject remains exact"],
        "stop_conditions": ["review subject becomes stale"],
        "policy": policy(),
    }


class ReviewSubjectBindingTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "src" / "evidence.txt").write_text("proof\n", encoding="utf-8")
        self.store = TaskStore(self.root / "maps.db")
        self.counter = 0

    def submitted(self, *, risk="LOW", run_count=1, criteria=None):
        self.counter += 1
        task_id = f"TASK-RB-{self.counter}"
        self.assertTrue(self.store.create_task(task_id=task_id).ok)
        shaped = self.store.update_contract(
            task_id,
            contract(risk=risk, criteria=criteria),
        )
        self.assertTrue(shaped.ok, shaped.message)
        self.assertTrue(self.store.promote_ready(task_id).ok)
        self.assertTrue(self.store.claim_task(task_id, "author", lease_seconds=600).ok)
        runs = []
        for index in range(run_count):
            result = self.store.create_run_manifest(
                task_id,
                "author",
                repo_root=self.repo,
                created_by="dispatcher",
                readable_paths=["."],
                writable_paths=["src"],
                base_revision=f"base-{index}",
            )
            self.assertTrue(result.ok, result.message)
            runs.append(result.task)
        submitted = self.store.submit_task(task_id, "author", "general proof")
        self.assertTrue(submitted.ok, submitted.message)
        return task_id, runs

    def claim(self, task_id):
        result = self.store.claim_review(task_id, "reviewer")
        self.assertTrue(result.ok, result.message)
        reviews = self.store.list_reviews(task_id)
        self.assertEqual(len(reviews), 1)
        return reviews[0]["id"]

    def bind(self, task_id, *, mode="REVISION_BOUND", run_id=None, refs=(SHA_A,)):
        return self.store.bind_review_subject(
            task_id,
            "reviewer",
            freshness_mode=mode,
            run_id=run_id,
            artifact_refs=refs,
        )

    def test_low_risk_unflagged_review_remains_simple(self):
        task_id, _ = self.submitted(risk="LOW")
        self.claim(task_id)
        approved = self.store.record_review(
            task_id,
            "reviewer",
            "APPROVED",
            "ordinary low-risk review passed",
        )
        self.assertTrue(approved.ok, approved.message)
        self.assertEqual(self.store.get_task(task_id)["status"], "DONE")

    def test_high_risk_approval_requires_bound_subject(self):
        task_id, _ = self.submitted(risk="HIGH")
        self.claim(task_id)
        approved = self.store.record_review(
            task_id,
            "reviewer",
            "APPROVED",
            "looks good",
        )
        self.assertFalse(approved.ok)
        self.assertEqual(approved.code, "REVIEW_SUBJECT_REQUIRED")
        self.assertEqual(self.store.get_task(task_id)["status"], "READY_FOR_REVIEW")

    def test_high_risk_revision_bound_subject_can_approve(self):
        task_id, runs = self.submitted(risk="HIGH")
        review_id = self.claim(task_id)
        bound = self.bind(task_id, run_id=runs[0]["run_id"])
        self.assertTrue(bound.ok, bound.message)
        self.assertEqual(bound.task["review_id"], review_id)
        self.assertEqual(bound.task["artifact_refs"], [SHA_A])
        approved = self.store.record_review(
            task_id,
            "reviewer",
            "APPROVED",
            "exact revision and digest reviewed",
        )
        self.assertTrue(approved.ok, approved.message)
        self.assertEqual(self.store.get_task(task_id)["status"], "DONE")

    def test_confirmed_criterion_evidence_derives_one_run_subject(self):
        task_id, runs = self.submitted(
            risk="HIGH",
            criteria=["criterion one", "criterion two"],
        )
        criteria = self.store.list_acceptance_criteria(task_id)
        claims = []
        for criterion in criteria:
            claim = self.store.record_criterion_claim(
                task_id,
                criterion["id"],
                "complete",
                author_id="author",
                evidence_refs=["src/evidence.txt"],
                repo_root=self.repo,
                run_id=runs[0]["run_id"],
            )
            self.assertTrue(claim.ok, claim.message)
            claims.append(claim.task["claim_id"])

        review_id = self.claim(task_id)
        for claim_id in claims:
            verdict = self.store.record_criterion_verdict(
                claim_id,
                "confirmed",
                reviewer_id="reviewer",
            )
            self.assertTrue(verdict.ok, verdict.message)

        self.assertIsNone(self.store.get_review_subject(review_id))
        approved = self.store.record_review(
            task_id,
            "reviewer",
            "APPROVED",
            "all criteria confirmed against one run",
        )
        self.assertTrue(approved.ok, approved.message)
        subject = self.store.get_review_subject(review_id)
        self.assertIsNotNone(subject)
        self.assertEqual(subject["freshness_mode"], "REVISION_BOUND")
        self.assertEqual(subject["run_id"], runs[0]["run_id"])
        self.assertEqual(subject["artifact_refs"], [])
        self.assertEqual(subject["task_revision"], self.store.compute_task_revision(task_id))
        events = self.store.list_events(task_id)
        event = next(
            item
            for item in events
            if item["event_type"] == "REVIEW_SUBJECT_BOUND"
        )
        self.assertIn("derived from confirmed criterion evidence", event["summary"])

    def test_revision_bound_requires_run_or_immutable_ref(self):
        task_id, _ = self.submitted(risk="HIGH")
        self.claim(task_id)
        result = self.bind(task_id, refs=())
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "REVISION_BOUND_SUBJECT_REQUIRED")

    def test_non_consequential_mode_is_rejected_for_high_risk_work(self):
        task_id, _ = self.submitted(risk="HIGH")
        self.claim(task_id)
        result = self.bind(task_id, mode="NON_CONSEQUENTIAL", refs=())
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "CONSEQUENTIAL_REVIEW_REQUIRES_FRESHNESS")

    def test_arbitrary_filename_is_not_an_immutable_artifact_ref(self):
        task_id, _ = self.submitted(risk="HIGH")
        self.claim(task_id)
        result = self.bind(task_id, refs=("build/release.zip",))
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "INVALID_ARTIFACT_REF")

    def test_rederived_review_requires_same_immutable_refs_at_approval(self):
        task_id, _ = self.submitted(risk="HIGH")
        self.claim(task_id)
        bound = self.bind(task_id, mode="REDERIVED_AT_REVIEW", refs=(SHA_A,))
        self.assertTrue(bound.ok, bound.message)

        missing = self.store.record_review(
            task_id,
            "reviewer",
            "APPROVED",
            "reran verification",
        )
        self.assertFalse(missing.ok)
        self.assertEqual(missing.code, "REVIEW_REDERIVATION_REQUIRED")

        mismatch = self.store.record_review(
            task_id,
            "reviewer",
            "APPROVED",
            "reran verification",
            rederived_artifact_refs=(SHA_B,),
        )
        self.assertFalse(mismatch.ok)
        self.assertEqual(mismatch.code, "REVIEW_REDERIVATION_MISMATCH")

        approved = self.store.record_review(
            task_id,
            "reviewer",
            "APPROVED",
            "reran verification against exact digest",
            rederived_artifact_refs=(SHA_A,),
        )
        self.assertTrue(approved.ok, approved.message)

    def test_submission_change_after_binding_rejects_approval(self):
        task_id, runs = self.submitted(risk="HIGH")
        self.claim(task_id)
        self.assertTrue(self.bind(task_id, run_id=runs[0]["run_id"]).ok)
        with self.store._connect() as conn:
            conn.execute(
                "UPDATE task_submissions SET submission_count = submission_count + 1 WHERE task_id = ?",
                (task_id,),
            )
        approved = self.store.record_review(
            task_id,
            "reviewer",
            "APPROVED",
            "stale review attempt",
        )
        self.assertFalse(approved.ok)
        self.assertEqual(approved.code, "REVIEW_SUBMISSION_CHANGED")

    def test_task_revision_change_after_binding_rejects_approval(self):
        task_id, runs = self.submitted(risk="HIGH")
        self.claim(task_id)
        self.assertTrue(self.bind(task_id, run_id=runs[0]["run_id"]).ok)
        with self.store._connect() as conn:
            conn.execute(
                "UPDATE tasks SET title = 'changed behind review' WHERE task_id = ?",
                (task_id,),
            )
        approved = self.store.record_review(
            task_id,
            "reviewer",
            "APPROVED",
            "stale revision attempt",
        )
        self.assertFalse(approved.ok)
        self.assertEqual(approved.code, "REVIEW_TASK_REVISION_CHANGED")

    def test_criterion_run_and_overall_subject_run_must_agree(self):
        task_id, runs = self.submitted(risk="HIGH", run_count=2, criteria=["one"])
        criterion_id = self.store.list_acceptance_criteria(task_id)[0]["id"]
        claim = self.store.record_criterion_claim(
            task_id,
            criterion_id,
            "complete",
            author_id="author",
            evidence_refs=["src/evidence.txt"],
            repo_root=self.repo,
            run_id=runs[0]["run_id"],
        )
        self.assertTrue(claim.ok, claim.message)
        self.claim(task_id)
        verdict = self.store.record_criterion_verdict(
            claim.task["claim_id"],
            "confirmed",
            reviewer_id="reviewer",
        )
        self.assertTrue(verdict.ok, verdict.message)
        self.assertTrue(self.bind(task_id, run_id=runs[1]["run_id"]).ok)
        approved = self.store.record_review(
            task_id,
            "reviewer",
            "APPROVED",
            "mismatched run attempt",
        )
        self.assertFalse(approved.ok)
        self.assertEqual(approved.code, "REVIEW_CRITERION_RUN_MISMATCH")

    def test_review_subject_is_sqlite_immutable(self):
        task_id, runs = self.submitted(risk="HIGH")
        review_id = self.claim(task_id)
        self.assertTrue(self.bind(task_id, run_id=runs[0]["run_id"]).ok)
        for sql in (
            "UPDATE review_subjects SET freshness_mode='NON_CONSEQUENTIAL' WHERE review_id=?",
            "DELETE FROM review_subjects WHERE review_id=?",
        ):
            with self.store._connect() as conn:
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(sql, (review_id,))

    def test_review_subject_cannot_be_rebound(self):
        task_id, runs = self.submitted(risk="HIGH")
        self.claim(task_id)
        self.assertTrue(self.bind(task_id, run_id=runs[0]["run_id"]).ok)
        again = self.bind(task_id, run_id=runs[0]["run_id"])
        self.assertFalse(again.ok)
        self.assertEqual(again.code, "REVIEW_SUBJECT_ALREADY_BOUND")

    def test_trace_shows_exact_review_subject(self):
        task_id, runs = self.submitted(risk="HIGH")
        review_id = self.claim(task_id)
        bound = self.bind(task_id, run_id=runs[0]["run_id"])
        self.assertTrue(bound.ok)
        trace = self.store.trace_task(task_id)
        self.assertIsNotNone(trace)
        self.assertEqual(trace["reviews"][0]["id"], review_id)
        subject = trace["reviews"][0]["subject"]
        self.assertEqual(subject["task_revision"], self.store.compute_task_revision(task_id))
        self.assertEqual(subject["run_id"], runs[0]["run_id"])
        self.assertEqual(subject["artifact_refs"], [SHA_A])
        self.assertTrue(
            trace["coverage"]["canonical_task_db"]["review_subjects_included"]
        )

    def test_subject_event_does_not_dump_artifact_refs(self):
        task_id, runs = self.submitted(risk="HIGH")
        self.claim(task_id)
        self.assertTrue(self.bind(task_id, run_id=runs[0]["run_id"]).ok)
        events = self.store.list_events(task_id)
        event = next(item for item in events if item["event_type"] == "REVIEW_SUBJECT_BOUND")
        self.assertIn("REVISION_BOUND", event["summary"])
        self.assertNotIn("sha256", event["summary"])
        self.assertNotIn("a" * 64, event["summary"])


if __name__ == "__main__":
    unittest.main()
