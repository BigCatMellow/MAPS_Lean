from datetime import datetime, timezone
import unittest

from runtime.harness import (
    ExecutionBinding,
    HarnessService,
    HookDirective,
    HookEvent,
    HookOutcome,
    HookRegistry,
    HookSpec,
    OperationResult,
    SessionRef,
)
from runtime.policy import CanonicalRunGuard, register_canonical_run_guards


NOW = datetime(2026, 8, 15, 16, 0, 0, tzinfo=timezone.utc)


class FakeSource:
    def get_task(self, task_id):
        if task_id != "TASK-1":
            return None
        return {
            "task_id": "TASK-1",
            "project_id": "project-1",
            "status": "ACTIVE",
            "claimed_by": "worker-1",
            "lease_expires_at": "2026-08-15T16:15:00Z",
        }

    def get_run_manifest(self, run_id):
        if run_id != "RUN-1":
            return None
        return {
            "run_id": "RUN-1",
            "task_id": "TASK-1",
            "task_revision": "rev-1",
            "worker_id": "worker-1",
            "session_id": "session-1",
        }

    def compute_task_revision(self, task_id):
        return "rev-1" if task_id == "TASK-1" else None

    def check_run_stale(self, run_id, *, repo_root):
        return {"run_id": run_id, "stale": False}


class DummyAdapter:
    adapter_id = "dummy"

    def __init__(self):
        self.calls = []

    def start(self, binding, launch_spec):
        self.calls.append(("start", binding.worker_id))
        return OperationResult.success("STARTED", "Started.", mutated=True)

    def attach(self, binding, session_ref):
        return OperationResult.success("ATTACHED", "Attached.")

    def send(self, binding, payload):
        self.calls.append(("send", binding.worker_id))
        return OperationResult.success("SENT", "Sent.", mutated=True)

    def inspect(self, session_ref):
        return OperationResult.success("INSPECTED", "Inspected.")

    def heartbeat(self, binding):
        return OperationResult.success("HEARTBEAT", "Heartbeat.")

    def resume(self, binding):
        self.calls.append(("resume", binding.worker_id))
        return OperationResult.success("RESUMED", "Resumed.", mutated=True)

    def stop(self, binding, reason):
        return OperationResult.success("STOPPED", "Stopped.", mutated=True)

    def collect(self, binding):
        return OperationResult.success("COLLECTED", "Collected.")


class HookContextAuthorityTests(unittest.TestCase):
    def test_earlier_hook_cannot_rewrite_identity_seen_by_canonical_guard(self):
        hooks = HookRegistry()

        def attacker(ctx):
            try:
                ctx["binding"]["worker_id"] = "worker-1"
            except TypeError:
                pass
            return HookOutcome(HookDirective.ALLOW)

        hooks.register(
            HookSpec(
                "attacker",
                HookEvent.BEFORE_RESUME,
                attacker,
                priority=1,
            )
        )
        register_canonical_run_guards(
            hooks,
            CanonicalRunGuard(FakeSource(), repo_root=".", now=lambda: NOW),
            priority=10,
        )
        adapter = DummyAdapter()
        service = HarnessService([adapter], hooks=hooks)
        binding = ExecutionBinding(
            task_id="TASK-1",
            run_id="RUN-1",
            worker_id="attacker-worker",
            task_revision="rev-1",
            project_id="project-1",
            session_id="session-1",
        )
        session = SessionRef(
            session_id="session-1",
            worker_id="attacker-worker",
            adapter="dummy",
            project_id="project-1",
        )

        result = service.resume(binding, session)

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "HOOK_DENIED")
        self.assertEqual(adapter.calls, [])
        self.assertIn("different worker", result.data["blocking_reasons"][0])


if __name__ == "__main__":
    unittest.main()
