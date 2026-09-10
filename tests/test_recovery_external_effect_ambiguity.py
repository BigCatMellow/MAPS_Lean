from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from runtime.harness import (
    ExecutionBinding,
    OperationResult,
    RetryDisposition,
    SessionRef,
)
from runtime.harness.adapters import HcomHarnessAdapter
from runtime.recovery import RecoveryStore, RecoverySupervisor
from runtime.state import TaskStore


class _FakeHcom:
    def __init__(self, sessions=None):
        self.sessions = sessions or []
        self.resumes = []

    def list_sessions(self, *, include_stopped=False):
        return [dict(item) for item in self.sessions]

    def resume(self, name, *, headless=False, terminal=None, go=True):
        self.resumes.append(
            {"name": name, "headless": headless, "terminal": terminal, "go": go}
        )
        return object()


class _FakeHarnessResume:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def resume(self, binding, session_ref):
        self.calls.append((binding, session_ref))
        return self.result


def _contract():
    return {
        "title": "Recovery external-effect ambiguity characterization",
        "outcome": "Freeze current fallback behavior after an ambiguous harness resume",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "bounded characterization",
        "verification": "recovery ambiguity characterization test",
        "evidence_expected": "passing characterization test",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "do not infer retry safety from provider failure",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": ["src"],
        "non_goals": ["no runtime behavior change"],
        "acceptance_criteria": ["current ambiguous fallback is explicit and observable"],
        "stop_conditions": ["binding lineage is ambiguous"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class RecoveryExternalEffectAmbiguityCharacterizationTests(unittest.TestCase):
    """Characterize current behavior; this is not the desired future policy.

    The purpose is to freeze the exact decision seam identified by the
    borrow-before-build audit before the harness/recovery owner decides how an
    UNKNOWN retry disposition should constrain fallback.
    """

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        self.task_store = TaskStore(self.root / "maps.db")
        self.recovery_store = RecoveryStore(self.root / "recovery.json")
        self.now = datetime(2026, 9, 9, 18, 30, tzinfo=timezone.utc)

    def _make_bound_run(self):
        created = self.task_store.create_task(title="x", project_id="proj-1")
        self.assertTrue(created.ok)
        task_id = created.task["task_id"]
        self.assertTrue(self.task_store.update_contract(task_id, _contract()).ok)
        self.assertTrue(self.task_store.promote_ready(task_id).ok)
        self.assertTrue(
            self.task_store.claim_task(task_id, "worker-1", lease_seconds=600).ok
        )
        manifest = self.task_store.create_run_manifest(
            task_id,
            "worker-1",
            repo_root=self.repo,
            created_by="dispatcher",
            readable_paths=["."],
            writable_paths=["src"],
        )
        self.assertTrue(manifest.ok, manifest.message)
        run_id = manifest.task["run_id"]

        adapter = HcomHarnessAdapter(
            _FakeHcom([]), project_id="proj-1", lineage_writer=self.task_store
        )
        binding = ExecutionBinding(
            task_id=task_id,
            run_id=run_id,
            worker_id="worker-1",
            task_revision=manifest.task["task_revision"],
            project_id="proj-1",
            session_id="sess-1",
        )
        session_ref = SessionRef(
            session_id="sess-1",
            worker_id="worker-1",
            adapter="hcom",
            project_id="proj-1",
            remote_ref="session-1",
        )
        attached = adapter.attach(binding, session_ref)
        self.assertTrue(attached.ok, attached.summary)
        return task_id, run_id

    def test_unknown_retry_harness_failure_is_currently_followed_by_direct_resume(self):
        task_id, run_id = self._make_bound_run()
        self.recovery_store.schedule(
            task_id=task_id,
            worker_id="worker-1",
            session_name="session-1",
            reason="scheduled",
            resume_after=(self.now - timedelta(seconds=1)).isoformat(),
            run_id=run_id,
        )

        ambiguous = OperationResult.failure(
            "PROVIDER_TIMEOUT",
            "provider may have accepted resume before acknowledgment was lost",
            mutated=True,
            operation_id="op-ambiguous-resume-1",
            retry=RetryDisposition.UNKNOWN,
        )
        harness = _FakeHarnessResume(ambiguous)
        direct = _FakeHcom([{"name": "session-1", "status": "stopped"}])
        supervisor = RecoverySupervisor(
            task_reader=self.task_store,
            hcom=direct,
            recovery_store=self.recovery_store,
            backoff_seconds=(60, 120),
            silent_stop_probe_delay_seconds=30,
            harness_service=harness,
        )

        actions = supervisor.tick(now=self.now)

        # First attempt: the harness path reached an external/provider-facing
        # resume and returned an explicitly UNKNOWN repeat-safety result.
        self.assertEqual(len(harness.calls), 1)
        self.assertEqual(ambiguous.retry, RetryDisposition.UNKNOWN)
        self.assertEqual(ambiguous.operation_id, "op-ambiguous-resume-1")

        # Current behavior then performs a second, direct resume in the same
        # tick because only explicit canonical denials suppress fallback.
        self.assertEqual(
            direct.resumes,
            [
                {
                    "name": "session-1",
                    "headless": True,
                    "terminal": None,
                    "go": True,
                }
            ],
        )
        self.assertEqual(actions[0]["action"], "resume")

        # The recovery action projection currently discards both facts needed
        # to reason about ambiguous retry safety at this seam.
        self.assertEqual(
            actions[0]["harness_resume"],
            {
                "attempted": True,
                "ok": False,
                "code": "PROVIDER_TIMEOUT",
                "summary": "provider may have accepted resume before acknowledgment was lost",
            },
        )
        self.assertNotIn("operation_id", actions[0]["harness_resume"])
        self.assertNotIn("retry", actions[0]["harness_resume"])


if __name__ == "__main__":
    unittest.main()
