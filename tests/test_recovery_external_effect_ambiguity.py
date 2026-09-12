from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from runtime.communication import HcomError
from runtime.harness import (
    ExecutionBinding,
    HarnessService,
    HookRegistry,
    OperationResult,
    RetryDisposition,
    SessionRef,
)
from runtime.harness.adapters import HcomHarnessAdapter
from runtime.policy.harness_guard import CanonicalRunGuard, register_canonical_run_guards
from runtime.recovery import RecoveryStore, RecoverySupervisor
from runtime.state import TaskStore


class _FakeHcom:
    def __init__(self, sessions=None):
        self.sessions = sessions or []
        self.resumes = []
        self.fail = False

    def list_sessions(self, *, include_stopped=False):
        return [dict(item) for item in self.sessions]

    def resume(self, name, *, headless=False, terminal=None, go=True):
        self.resumes.append(
            {"name": name, "headless": headless, "terminal": terminal, "go": go}
        )
        if self.fail:
            raise HcomError("simulated transport failure after resume dispatch")
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
        "title": "Recovery external-effect ambiguity regression",
        "outcome": "Do not blindly repeat an ambiguous harness resume in the same tick",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "bounded recovery hardening",
        "verification": "recovery ambiguity regression test",
        "evidence_expected": "passing ambiguity and reconciliation regression",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "do not infer retry safety from provider failure",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": ["src"],
        "non_goals": ["no general operation ledger or provider idempotency protocol"],
        "acceptance_criteria": [
            "UNKNOWN repeat safety suppresses same-tick direct fallback",
            "next pass re-observes session state before another resume",
        ],
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


class RecoveryExternalEffectAmbiguityTests(unittest.TestCase):
    """Freeze the bounded UNKNOWN-result fallback hardening.

    A returned UNKNOWN disposition means the harness path cannot prove that
    repeating the same external effect is safe. Recovery therefore must not
    perform its legacy direct resume in the same tick. The incident remains
    recoverable and the next tick starts from fresh session observation.
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

    def _schedule(self, task_id, run_id):
        self.recovery_store.schedule(
            task_id=task_id,
            worker_id="worker-1",
            session_name="session-1",
            reason="scheduled",
            resume_after=(self.now - timedelta(seconds=1)).isoformat(),
            run_id=run_id,
        )

    def _scheduled_supervisor(self):
        task_id, run_id = self._make_bound_run()
        self._schedule(task_id, run_id)

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
        return supervisor, harness, direct

    def test_unknown_retry_harness_failure_does_not_direct_fallback_same_tick(self):
        supervisor, harness, direct = self._scheduled_supervisor()

        actions = supervisor.tick(now=self.now)

        self.assertEqual(len(harness.calls), 1)
        self.assertEqual(direct.resumes, [])
        self.assertEqual(actions[0]["action"], "resume_failed")
        self.assertEqual(
            actions[0]["harness_resume"],
            {
                "attempted": True,
                "ok": False,
                "code": "PROVIDER_TIMEOUT",
                "summary": "provider may have accepted resume before acknowledgment was lost",
                "mutated": True,
                "operation_id": "op-ambiguous-resume-1",
                "retry": "UNKNOWN",
            },
        )

        stored = self.recovery_store.load()["incidents"][actions[0]["incident_id"]]
        self.assertEqual(stored["state"], "probing")
        self.assertEqual(stored["attempt"], 1)
        self.assertEqual(
            stored["last_error"],
            "provider may have accepted resume before acknowledgment was lost",
        )

    def test_next_pass_reobserves_live_session_before_any_second_resume(self):
        supervisor, harness, direct = self._scheduled_supervisor()

        first = supervisor.tick(now=self.now)
        self.assertEqual(first[0]["action"], "resume_failed")
        self.assertEqual(len(harness.calls), 1)
        self.assertEqual(direct.resumes, [])

        # Model the ambiguous first attempt having actually succeeded. The next
        # pass must reconcile from current session state before considering a
        # retry; liveness resolves the incident with no second resume call.
        direct.sessions = [
            {
                "name": "session-1",
                "status": "active",
                "process_bound": True,
            }
        ]
        second = supervisor.tick(now=self.now + timedelta(seconds=61))

        self.assertEqual(second[0]["action"], "resolve")
        self.assertEqual(second[0]["reason"], "session_live")
        self.assertEqual(len(harness.calls), 1)
        self.assertEqual(direct.resumes, [])

    def test_real_hcom_transport_failure_unknown_suppresses_direct_fallback(self):
        task_id, run_id = self._make_bound_run()
        self._schedule(task_id, run_id)

        # Exercise the production HarnessService/HcomHarnessAdapter path. The
        # backend records that resume dispatch was attempted, then raises the
        # same HcomError class the adapter normalizes to TRANSPORT_ERROR with
        # retry=UNKNOWN.
        harness_backend = _FakeHcom(
            [
                {
                    "name": "session-1",
                    "session_id": "sess-1",
                    "status": "stopped",
                }
            ]
        )
        harness_backend.fail = True
        adapter = HcomHarnessAdapter(
            harness_backend,
            project_id="proj-1",
            lineage_writer=self.task_store,
        )
        hooks = HookRegistry()
        register_canonical_run_guards(
            hooks,
            CanonicalRunGuard(self.task_store, repo_root=self.repo),
        )
        harness_service = HarnessService([adapter], hooks=hooks)

        direct = _FakeHcom([{"name": "session-1", "status": "stopped"}])
        supervisor = RecoverySupervisor(
            task_reader=self.task_store,
            hcom=direct,
            recovery_store=self.recovery_store,
            backoff_seconds=(60, 120),
            silent_stop_probe_delay_seconds=30,
            harness_service=harness_service,
        )

        actions = supervisor.tick(now=self.now)

        self.assertEqual(len(harness_backend.resumes), 1)
        self.assertEqual(direct.resumes, [])
        self.assertEqual(actions[0]["action"], "resume_failed")
        harness_resume = actions[0]["harness_resume"]
        self.assertEqual(harness_resume["code"], "TRANSPORT_ERROR")
        self.assertEqual(harness_resume["summary"], "hcom operation failed.")
        self.assertEqual(harness_resume["retry"], "UNKNOWN")
        self.assertFalse(harness_resume["mutated"])
        self.assertTrue(harness_resume["operation_id"].startswith("op-"))


if __name__ == "__main__":
    unittest.main()
