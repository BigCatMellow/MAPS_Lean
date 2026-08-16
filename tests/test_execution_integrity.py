from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

from runtime.integrity import verify_git_run
from runtime.policy import WorkerProfile
from runtime.routing import recommend_route
from runtime.state import TaskStore


def contract(*, outputs=None, criteria=None):
    return {
        "title": "Integrity task",
        "outcome": "Execution remains bound to approved contract and scope",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "HIGH",
        "decision_authority": "bounded implementation only",
        "verification": "run integrity tests",
        "evidence_expected": "test output and evidence files",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "operator on authority/scope conflict",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": outputs or ["src"],
        "non_goals": ["no unrelated changes"],
        "acceptance_criteria": criteria or ["criterion one", "criterion two"],
        "stop_conditions": ["stop on stale contract"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "docs").mkdir()
        (self.repo / "context.md").write_text("context v1\n", encoding="utf-8")
        (self.repo / "src" / "evidence-one.txt").write_text("proof 1\n", encoding="utf-8")
        (self.repo / "src" / "evidence-two.txt").write_text("proof 2\n", encoding="utf-8")
        self.store = TaskStore(self.root / "maps.db")

    def make_active(self, *, worker="worker", outputs=None, criteria=None):
        created = self.store.create_task(title="x")
        self.assertTrue(created.ok)
        task_id = created.task["task_id"]
        self.assertTrue(
            self.store.update_contract(
                task_id, contract(outputs=outputs, criteria=criteria)
            ).ok
        )
        self.assertTrue(self.store.promote_ready(task_id).ok)
        self.assertTrue(self.store.claim_task(task_id, worker, lease_seconds=600).ok)
        return task_id

    def make_run(self, task_id, *, worker="worker", **kwargs):
        result = self.store.create_run_manifest(
            task_id,
            worker,
            repo_root=self.repo,
            created_by="dispatcher",
            context_paths=["context.md"],
            readable_paths=["."],
            base_revision=kwargs.pop("base_revision", None),
            **kwargs,
        )
        self.assertTrue(result.ok, result.message)
        return result.task

    def test_run_requires_active_current_claimant(self):
        created = self.store.create_task(title="x")
        task_id = created.task["task_id"]
        self.store.update_contract(task_id, contract())
        self.store.promote_ready(task_id)
        result = self.store.create_run_manifest(
            task_id,
            "worker",
            repo_root=self.repo,
            created_by="dispatcher",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "RUN_NOT_OWNED")

    def test_run_freezes_revision_context_and_scope(self):
        task_id = self.make_active()
        manifest = self.make_run(
            task_id,
            writable_paths=["src"],
            forbidden_paths=["docs"],
            runtime_limits={"runtime_seconds": 300, "max_tool_failures": 2},
        )
        self.assertEqual(manifest["worker_id"], "worker")
        self.assertEqual(manifest["writable_scope"], ["src"])
        self.assertEqual(manifest["forbidden_scope"], ["docs"])
        self.assertEqual(manifest["runtime_limits"]["runtime_seconds"], 300)
        self.assertEqual(manifest["task_revision"], self.store.compute_task_revision(task_id))
        self.assertEqual(manifest["context_refs"][0]["path"], "context.md")
        self.assertEqual(len(manifest["context_refs"][0]["sha256"]), 64)

    def test_writable_scope_cannot_exceed_task_outputs(self):
        task_id = self.make_active(outputs=["src"])
        result = self.store.create_run_manifest(
            task_id,
            "worker",
            repo_root=self.repo,
            created_by="dispatcher",
            writable_paths=["docs"],
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "WRITE_SCOPE_EXCEEDS_TASK")

    def test_context_change_makes_run_stale(self):
        task_id = self.make_active()
        manifest = self.make_run(task_id)
        self.assertFalse(
            self.store.check_run_stale(manifest["run_id"], repo_root=self.repo)["stale"]
        )
        (self.repo / "context.md").write_text("context v2\n", encoding="utf-8")
        stale = self.store.check_run_stale(manifest["run_id"], repo_root=self.repo)
        self.assertTrue(stale["stale"])
        self.assertEqual(stale["stale_context"][0]["reason"], "changed")

    def test_task_definition_change_makes_run_stale(self):
        task_id = self.make_active()
        manifest = self.make_run(task_id)
        with self.store._connect() as conn:
            conn.execute("UPDATE tasks SET outcome = 'changed contract' WHERE task_id = ?", (task_id,))
        stale = self.store.check_run_stale(manifest["run_id"], repo_root=self.repo)
        self.assertTrue(stale["task_stale"])

    def test_verify_run_changes_reports_out_of_scope_without_repair(self):
        task_id = self.make_active(outputs=["src"])
        manifest = self.make_run(task_id, writable_paths=["src"])
        result = self.store.verify_run_changes(
            manifest["run_id"],
            ["src/a.py", "README.md"],
            repo_root=self.repo,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["out_of_scope"], ["README.md"])

    def init_git_repo(self):
        def git(*args):
            subprocess.run(
                ["git", "-C", str(self.repo), *args],
                check=True,
                capture_output=True,
                text=True,
            )

        git("init")
        git("config", "user.email", "maps@example.invalid")
        git("config", "user.name", "MAPS Test")
        (self.repo / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
        (self.repo / "README.md").write_text("base\n", encoding="utf-8")
        git("add", ".")
        git("commit", "-m", "base")
        base = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return base

    def test_git_scope_verifier_reports_real_worktree_changes(self):
        base = self.init_git_repo()
        task_id = self.make_active(outputs=["src"])
        manifest = self.make_run(task_id, writable_paths=["src"], base_revision=base)
        (self.repo / "src" / "a.py").write_text("x = 2\n", encoding="utf-8")
        (self.repo / "README.md").write_text("changed\n", encoding="utf-8")
        result = verify_git_run(self.store, manifest["run_id"], repo_root=self.repo)
        self.assertFalse(result["ok"])
        self.assertIn("README.md", result["out_of_scope"])
        self.assertIn("src/a.py", result["changed_paths"])
        self.assertEqual((self.repo / "README.md").read_text(), "changed\n")

    def test_continuity_component_is_transitive(self):
        self.assertTrue(
            self.store.record_continuity_link("author", "replacement-1", reason="rotation").ok
        )
        self.assertTrue(
            self.store.record_continuity_link("replacement-1", "replacement-2", reason="rotation").ok
        )
        self.assertEqual(
            self.store.continuity_component("author"),
            {"author", "replacement-1", "replacement-2"},
        )
        self.assertTrue(self.store.same_continuity_lineage("replacement-2", "author"))

    def submit_as(self, author="author"):
        task_id = self.make_active(worker=author)
        self.assertTrue(self.store.submit_task(task_id, author, "general evidence").ok)
        return task_id

    def test_continuation_identity_cannot_claim_review(self):
        task_id = self.submit_as("author")
        self.store.record_continuity_link("author", "replacement", reason="rotation")
        result = self.store.claim_review(task_id, "replacement")
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "CONTINUITY_REVIEW_FORBIDDEN")
        self.assertIn("replacement", self.store.get_task(task_id)["review_disqualified_ids"])
        self.assertTrue(self.store.claim_review(task_id, "independent").ok)

    def test_router_avoids_continuity_disqualified_reviewer(self):
        task_id = self.submit_as("author")
        self.store.record_continuity_link("author", "replacement", reason="rotation")
        snapshot = self.store.get_task(task_id)
        replacement = WorkerProfile(
            "replacement", "core", can_review=True, cost_rank=1
        )
        independent = WorkerProfile(
            "independent", "core", can_review=True, cost_rank=2
        )
        route = recommend_route([snapshot], [replacement, independent])
        self.assertEqual(route.route, "review")
        self.assertEqual(route.worker_id, "independent")

    def test_final_review_rechecks_continuity_added_after_claim(self):
        task_id = self.submit_as("author")
        self.assertTrue(self.store.claim_review(task_id, "reviewer").ok)
        self.store.record_continuity_link("author", "reviewer", reason="late rotation evidence")
        result = self.store.record_review(task_id, "reviewer", "APPROVED", "looks good")
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "CONTINUITY_REVIEW_FORBIDDEN")

    def test_criterion_claim_and_verdict_remain_separate(self):
        task_id = self.make_active(worker="author")
        run = self.make_run(task_id, worker="author")
        self.assertTrue(self.store.submit_task(task_id, "author", "general evidence").ok)
        criterion_id = self.store.list_acceptance_criteria(task_id)[0]["id"]
        claim = self.store.record_criterion_claim(
            task_id,
            criterion_id,
            "complete",
            author_id="author",
            evidence_refs=["src/evidence-one.txt"],
            repo_root=self.repo,
            run_id=run["run_id"],
        )
        self.assertTrue(claim.ok, claim.message)
        claim_id = claim.task["claim_id"]
        self.assertTrue(self.store.claim_review(task_id, "reviewer").ok)
        self.assertTrue(
            self.store.record_criterion_verdict(
                claim_id, "confirmed", reviewer_id="reviewer", notes="verified"
            ).ok
        )
        record = self.store.get_criterion_claims(task_id)[0]
        self.assertEqual(record["claimed_status"], "complete")
        self.assertEqual(record["author_id"], "author")
        self.assertEqual(record["verdicts"][0]["verified_status"], "confirmed")
        self.assertEqual(record["verdicts"][0]["reviewer_id"], "reviewer")

    def test_criterion_mode_blocks_approval_until_every_criterion_confirmed(self):
        task_id = self.make_active(worker="author")
        run = self.make_run(task_id, worker="author")
        self.assertTrue(self.store.submit_task(task_id, "author", "general evidence").ok)
        criteria = self.store.list_acceptance_criteria(task_id)
        first = self.store.record_criterion_claim(
            task_id,
            criteria[0]["id"],
            "complete",
            author_id="author",
            evidence_refs=["src/evidence-one.txt"],
            repo_root=self.repo,
            run_id=run["run_id"],
        )
        self.assertTrue(self.store.claim_review(task_id, "reviewer").ok)
        self.assertTrue(
            self.store.record_criterion_verdict(
                first.task["claim_id"], "confirmed", reviewer_id="reviewer"
            ).ok
        )
        blocked = self.store.record_review(
            task_id, "reviewer", "APPROVED", "first criterion confirmed"
        )
        self.assertFalse(blocked.ok)
        self.assertEqual(blocked.code, "CRITERION_VERIFICATION_INCOMPLETE")

        second = self.store.record_criterion_claim(
            task_id,
            criteria[1]["id"],
            "complete",
            author_id="author",
            evidence_refs=["src/evidence-two.txt"],
            repo_root=self.repo,
            run_id=run["run_id"],
        )
        self.assertTrue(
            self.store.record_criterion_verdict(
                second.task["claim_id"], "confirmed", reviewer_id="reviewer"
            ).ok
        )
        missing_subject = self.store.record_review(
            task_id, "reviewer", "APPROVED", "all criteria confirmed"
        )
        self.assertFalse(missing_subject.ok)
        self.assertEqual(missing_subject.code, "REVIEW_SUBJECT_REQUIRED")
        bound = self.store.bind_review_subject(
            task_id,
            "reviewer",
            freshness_mode="REVISION_BOUND",
            run_id=run["run_id"],
            artifact_refs=("sha256:" + "d" * 64,),
        )
        self.assertTrue(bound.ok, bound.message)
        approved = self.store.record_review(
            task_id, "reviewer", "APPROVED", "all criteria and exact output reviewed"
        )
        self.assertTrue(approved.ok, approved.message)
        self.assertEqual(self.store.get_task(task_id)["status"], "DONE")

    def test_criterion_verdict_rechecks_continuity(self):
        task_id = self.make_active(worker="author", criteria=["only"])
        self.assertTrue(self.store.submit_task(task_id, "author", "general evidence").ok)
        criterion_id = self.store.list_acceptance_criteria(task_id)[0]["id"]
        claim = self.store.record_criterion_claim(
            task_id,
            criterion_id,
            "complete",
            author_id="author",
            evidence_refs=["src/evidence-one.txt"],
            repo_root=self.repo,
        )
        self.assertTrue(self.store.claim_review(task_id, "reviewer").ok)
        self.store.record_continuity_link("author", "reviewer", reason="late rotation evidence")
        verdict = self.store.record_criterion_verdict(
            claim.task["claim_id"], "confirmed", reviewer_id="reviewer"
        )
        self.assertFalse(verdict.ok)
        self.assertEqual(verdict.code, "CONTINUITY_REVIEW_FORBIDDEN")


if __name__ == "__main__":
    unittest.main()
