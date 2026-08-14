from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest

from runtime.helpers.common import HelperError, validate_active_scope
from runtime.integrity import check_run_budget, verify_git_run, write_budget_escalation
from runtime.policy import HaltStore, WorkerProfile
from runtime.recovery import RecoveryStore, RecoverySupervisor
from runtime.routing import recommend_route
from runtime.state import TaskStore


def contract(*, outputs=None, policy=None, criteria=None):
    return {
        "title": "Review hardening task",
        "outcome": "The requested state is observable",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "Implementation choices inside declared scope",
        "verification": "Run deterministic tests",
        "evidence_expected": "Passing test output",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "Stop on scope, authority, or safety uncertainty",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": outputs or ["src"],
        "non_goals": ["No unrelated changes"],
        "acceptance_criteria": criteria or ["criterion one"],
        "stop_conditions": ["A required dependency is missing"],
        "policy": policy
        or {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class FailingPolicyStore(TaskStore):
    def _apply_policy_contract_conn(self, conn, task_id, shaped_contract):
        super()._apply_policy_contract_conn(conn, task_id, shaped_contract)
        raise sqlite3.OperationalError("injected policy write failure")


class FakeTasks:
    def __init__(self, rows):
        self.rows = {row["task_id"]: dict(row) for row in rows}

    def get_task(self, task_id):
        row = self.rows.get(task_id)
        return dict(row) if row else None

    def list_tasks(self, *, statuses=None, project_id=None):
        rows = list(self.rows.values())
        if statuses:
            rows = [row for row in rows if row.get("status") in statuses]
        return [dict(row) for row in rows]


class FakeHcom:
    def __init__(self, sessions):
        self.sessions = sessions
        self.resumes = []

    def list_sessions(self, *, include_stopped=False):
        return [dict(row) for row in self.sessions]

    def resume(self, name, *, headless=False, terminal=None, go=True):
        self.resumes.append(name)
        return object()


class RuntimeReviewHardeningTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "src" / "evidence.txt").write_text("proof\n", encoding="utf-8")
        self.db = self.root / "maps.db"
        self.store = TaskStore(self.db)

    def shaped(self, *, task_id=None, outputs=None, policy=None, criteria=None):
        created = self.store.create_task(task_id=task_id)
        self.assertTrue(created.ok, created.message)
        tid = created.task["task_id"]
        result = self.store.update_contract(
            tid, contract(outputs=outputs, policy=policy, criteria=criteria)
        )
        self.assertTrue(result.ok, result.message)
        return tid

    def active(self, *, worker="worker", outputs=None, policy=None, criteria=None):
        tid = self.shaped(outputs=outputs, policy=policy, criteria=criteria)
        self.assertTrue(self.store.promote_ready(tid).ok)
        self.assertTrue(self.store.claim_task(tid, worker, lease_seconds=600).ok)
        return tid

    def make_run(self, task_id, *, worker="worker", **kwargs):
        result = self.store.create_run_manifest(
            task_id,
            worker,
            repo_root=self.repo,
            created_by="dispatcher",
            readable_paths=["."],
            **kwargs,
        )
        self.assertTrue(result.ok, result.message)
        return result.task

    def test_contract_and_policy_shape_rollback_together(self):
        gated = {
            "requires_operator_approval": True,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        }
        tid = self.shaped(policy=gated)
        self.assertTrue(
            self.store.record_operator_approval(
                tid, approved_by="operator", note="approved original contract"
            ).ok
        )
        before = self.store.get_task(tid)

        failing = FailingPolicyStore(self.db)
        changed = contract(policy={**gated, "security_sensitive": True})
        changed["outcome"] = "this must roll back"
        with self.assertRaises(sqlite3.OperationalError):
            failing.update_contract(tid, changed)

        after = self.store.get_task(tid)
        self.assertEqual(after["outcome"], before["outcome"])
        self.assertEqual(after["policy"]["security_sensitive"], False)
        self.assertEqual(after["policy"]["approved_by"], "operator")

    def test_parent_child_output_scope_conflict_blocks_ready(self):
        parent = self.shaped(task_id="TASK-PARENT", outputs=["runtime"])
        self.assertTrue(self.store.promote_ready(parent).ok)
        child = self.shaped(
            task_id="TASK-CHILD", outputs=["runtime/state/store.py"]
        )
        result = self.store.validate_ready(child)
        self.assertFalse(result.ok)
        self.assertTrue(any("already reserved by TASK-PARENT" in item for item in result.reasons))

    def test_output_scope_must_be_repo_relative(self):
        for output in ("../outside", "/tmp/outside"):
            tid = self.shaped(outputs=[output])
            result = self.store.validate_ready(tid)
            self.assertFalse(result.ok)
            self.assertTrue(any("invalid output path" in item for item in result.reasons))

    def test_worker_capability_booleans_are_not_string_coerced(self):
        with self.assertRaises(ValueError):
            WorkerProfile.from_mapping(
                {
                    "worker_id": "worker",
                    "worker_class": "core",
                    "can_review": "false",
                }
            )

    def test_scoped_halt_requires_target(self):
        store = HaltStore(self.root / "halt.json")
        with self.assertRaises(ValueError):
            store.set(
                state="halt_paid_dispatch",
                reason="test",
                actor="operator",
                authority="operator",
                scope="task",
            )

    def test_blocked_low_id_task_does_not_freeze_routable_work(self):
        waiting_review = {
            "task_id": "TASK-0001",
            "status": "READY_FOR_REVIEW",
            "risk": "LOW",
            "submission": {"author_id": "author"},
            "review_disqualified_ids": ["author"],
            "policy": {"paid_execution": False},
        }
        runnable = {
            "task_id": "TASK-0002",
            "status": "READY",
            "agi_status": "AGI READY",
            "task_type": "IMPLEMENTATION",
            "risk": "LOW",
            "output_paths": ["src"],
            "policy": {"paid_execution": False},
        }
        builder = WorkerProfile(
            "builder",
            "bounded",
            supported_task_types=("IMPLEMENTATION",),
            max_risk="LOW",
            can_mutate=True,
            can_review=False,
            cost_rank=1,
        )
        route = recommend_route([waiting_review, runnable], [builder])
        self.assertEqual(route.route, "claim_or_assign")
        self.assertEqual(route.task_id, "TASK-0002")

    def test_recovery_refuses_ambiguous_worker_task_binding(self):
        tasks = [
            {"task_id": "TASK-A", "status": "ACTIVE", "claimed_by": "worker"},
            {"task_id": "TASK-B", "status": "ACTIVE", "claimed_by": "worker"},
        ]
        recovery = RecoveryStore(self.root / "recovery.json")
        hcom = FakeHcom([{"name": "session", "status": "stopped"}])
        supervisor = RecoverySupervisor(
            task_reader=FakeTasks(tasks),
            hcom=hcom,
            recovery_store=recovery,
            backoff_seconds=(60,),
            silent_stop_probe_delay_seconds=1,
        )
        opened = supervisor.observe_silent_stops(
            {"worker": "session"}, now=datetime(2026, 8, 14, tzinfo=timezone.utc)
        )
        self.assertEqual(opened, [])
        state = recovery.load()
        self.assertEqual(state["ambiguous_workers"]["worker"], ["TASK-A", "TASK-B"])
        self.assertEqual(state["incidents"], {})

    def test_helper_scope_rejects_repo_escape_even_if_task_claims_it(self):
        task = {
            "task_id": "TASK-X",
            "status": "ACTIVE",
            "output_paths": ["../outside"],
        }
        with self.assertRaises(HelperError):
            validate_active_scope(task, [self.root / "outside"], repo=self.repo)

    def test_writable_parent_may_not_contain_forbidden_child(self):
        tid = self.active(outputs=["src"])
        result = self.store.create_run_manifest(
            tid,
            "worker",
            repo_root=self.repo,
            created_by="dispatcher",
            readable_paths=["."],
            writable_paths=["src"],
            forbidden_paths=["src/private"],
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "INVALID_SCOPE")
        self.assertIn("overlaps forbidden", result.message)

    def init_git(self):
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
        (self.repo / "secret").mkdir()
        (self.repo / "secret" / "a.txt").write_text("secret\n", encoding="utf-8")
        git("add", ".")
        git("commit", "-m", "base")
        return subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def test_git_rename_preserves_forbidden_source_path(self):
        base = self.init_git()
        tid = self.active(outputs=["src"])
        manifest = self.make_run(
            tid,
            writable_paths=["src"],
            forbidden_paths=["secret"],
            base_revision=base,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "mv",
                "secret/a.txt",
                "src/a.txt",
            ],
            check=True,
        )
        result = verify_git_run(self.store, manifest["run_id"], repo_root=self.repo)
        self.assertFalse(result["ok"])
        self.assertIn("secret/a.txt", result["changed_paths"])
        self.assertIn("secret/a.txt", result["forbidden_changes"])
        self.assertIn("src/a.txt", result["changed_paths"])

    def test_run_budget_exhausts_at_declared_limit_and_can_write_evidence(self):
        tid = self.active(outputs=["src"])
        manifest = self.make_run(
            tid,
            writable_paths=["src"],
            runtime_limits={"max_attempts": 2, "max_tool_failures": 3},
        )
        below = check_run_budget(
            self.store,
            manifest["run_id"],
            actual_attempts=1,
            actual_tool_failures=2,
        )
        self.assertTrue(below["ok"])
        exhausted = check_run_budget(
            self.store,
            manifest["run_id"],
            actual_attempts=2,
            actual_tool_failures=2,
        )
        self.assertFalse(exhausted["ok"])
        self.assertEqual(exhausted["reason"], "budget_exhausted")
        self.assertEqual(exhausted["exceeded"][0]["metric"], "max_attempts")
        artifact = write_budget_escalation(
            exhausted, out_dir=self.root / "escalations"
        )
        self.assertTrue(artifact.is_file())
        self.assertIn(manifest["run_id"], artifact.name)

    def test_run_budget_rejects_negative_measurement(self):
        tid = self.active(outputs=["src"])
        manifest = self.make_run(tid, writable_paths=["src"])
        with self.assertRaises(ValueError):
            check_run_budget(
                self.store, manifest["run_id"], actual_runtime_seconds=-1
            )

    def test_criterion_claims_and_verdicts_are_sqlite_immutable(self):
        tid = self.active(worker="author", outputs=["src"], criteria=["one"])
        self.assertTrue(self.store.submit_task(tid, "author", "general proof").ok)
        criterion_id = self.store.list_acceptance_criteria(tid)[0]["id"]
        claim = self.store.record_criterion_claim(
            tid,
            criterion_id,
            "complete",
            author_id="author",
            evidence_refs=["src/evidence.txt"],
            repo_root=self.repo,
        )
        self.assertTrue(claim.ok, claim.message)
        claim_id = claim.task["claim_id"]
        self.assertTrue(self.store.claim_review(tid, "reviewer").ok)
        verdict = self.store.record_criterion_verdict(
            claim_id, "confirmed", reviewer_id="reviewer"
        )
        self.assertTrue(verdict.ok, verdict.message)
        verdict_id = self.store.get_criterion_claims(tid)[0]["verdicts"][0]["id"]

        for sql, params in (
            (
                "UPDATE submission_criterion_claims SET claimed_status='blocked' WHERE id=?",
                (claim_id,),
            ),
            ("DELETE FROM submission_criterion_claims WHERE id=?", (claim_id,)),
            (
                "UPDATE submission_criterion_verdicts SET verified_status='rejected' WHERE id=?",
                (verdict_id,),
            ),
            ("DELETE FROM submission_criterion_verdicts WHERE id=?", (verdict_id,)),
        ):
            with self.store._connect() as conn:
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(sql, params)


if __name__ == "__main__":
    unittest.main()
