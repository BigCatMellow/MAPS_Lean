from datetime import datetime, timezone
import unittest

from runtime.harness import (
    ExecutionBinding,
    HarnessService,
    HookDirective,
    HookEvent,
    HookRegistry,
    OperationResult,
    SessionRef,
)
from runtime.policy.harness_guard import CanonicalRunGuard, register_canonical_run_guards


NOW = datetime(2026, 8, 15, 16, 0, 0, tzinfo=timezone.utc)


class FakeSource:
    def __init__(self):
        self.task = {
            "task_id": "TASK-1",
            "project_id": "project-1",
            "status": "ACTIVE",
            "claimed_by": "worker-1",
            "lease_expires_at": "2026-08-15T16:15:00Z",
        }
        self.manifest = {
            "run_id": "RUN-1",
            "task_id": "TASK-1",
            "task_revision": "rev-1",
            "worker_id": "worker-1",
            "session_id": "session-1",
        }
        self.current_revision = "rev-1"
        self.stale = False

    def get_task(self, task_id):
        return dict(self.task) if task_id == "TASK-1" else None

    def get_run_manifest(self, run_id):
        return dict(self.manifest) if run_id == "RUN-1" else None

    def compute_task_revision(self, task_id):
        return self.current_revision if task_id == "TASK-1" else None

    def check_run_stale(self, run_id, *, repo_root):
        return {"run_id": run_id, "stale": self.stale}


def binding(*, session_id="session-1"):
    return ExecutionBinding(
        task_id="TASK-1",
        run_id="RUN-1",
        worker_id="worker-1",
        task_revision="rev-1",
        project_id="project-1",
        session_id=session_id,
    )


def ref(*, session_id="session-1"):
    return SessionRef(
        session_id=session_id,
        worker_id="worker-1",
        adapter="dummy",
        project_id="project-1",
    )


def context(operation, *, include_session=True):
    value = {
        "operation": operation,
        "adapter_id": "dummy",
        "binding": binding().to_dict(),
    }
    if include_session:
        value["session_ref"] = ref().to_dict()
    return value


class DummyAdapter:
    adapter_id = "dummy"

    def __init__(self):
        self.calls = []

    def start(self, binding, launch_spec):
        self.calls.append("start")
        return OperationResult.success("STARTED", "Started.", mutated=True)

    def attach(self, binding, session_ref):
        self.calls.append("attach")
        return OperationResult.success("ATTACHED", "Attached.")

    def send(self, binding, payload):
        self.calls.append("send")
        return OperationResult.success("SENT", "Sent.", mutated=True)

    def inspect(self, session_ref):
        self.calls.append("inspect")
        return OperationResult.success("INSPECTED", "Inspected.")

    def heartbeat(self, binding):
        self.calls.append("heartbeat")
        return OperationResult.success("HEARTBEAT", "Heartbeat.")

    def resume(self, binding):
        self.calls.append("resume")
        return OperationResult.success("RESUMED", "Resumed.")

    def stop(self, binding, reason):
        self.calls.append("stop")
        return OperationResult.success("STOPPED", "Stopped.", mutated=True)

    def collect(self, binding):
        self.calls.append("collect")
        return OperationResult.success("COLLECTED", "Collected.")


class CanonicalRunGuardTests(unittest.TestCase):
    def setUp(self):
        self.source = FakeSource()
        self.guard = CanonicalRunGuard(self.source, repo_root=".", now=lambda: NOW)

    def test_valid_start_is_annotated_as_verified(self):
        outcome = self.guard(context("start", include_session=False))

        self.assertEqual(outcome.directive, HookDirective.ANNOTATE)
        self.assertEqual(outcome.annotations["guard_code"], "CANONICAL_RUN_VERIFIED")
        self.assertEqual(outcome.evidence_refs, ("task:TASK-1", "run:RUN-1"))

    def test_send_requires_live_claim(self):
        self.source.task["lease_expires_at"] = "2026-08-15T15:59:59Z"

        outcome = self.guard(context("send"))

        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "LEASE_EXPIRED")

    def test_send_requires_durable_manifest_session(self):
        self.source.manifest["session_id"] = None

        outcome = self.guard(context("send"))

        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(
            outcome.annotations["guard_code"],
            "SESSION_NOT_DURABLY_BOUND",
        )

    def test_session_binding_mismatch_is_denied(self):
        value = context("send")
        value["session_ref"] = ref(session_id="other").to_dict()

        outcome = self.guard(value)

        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "SESSION_BINDING_MISMATCH")

    def test_stale_run_blocks_continuing_execution(self):
        self.source.stale = True

        outcome = self.guard(context("send"))

        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "RUN_STALE")

    def test_changed_task_revision_blocks_continuation(self):
        self.source.current_revision = "rev-2"

        outcome = self.guard(context("send"))

        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "TASK_REVISION_STALE")

    def test_stop_can_target_known_stale_expired_session(self):
        self.source.task["status"] = "READY_FOR_REVIEW"
        self.source.task["claimed_by"] = ""
        self.source.task["lease_expires_at"] = "2026-08-15T15:00:00Z"
        self.source.current_revision = "rev-2"
        self.source.stale = True

        outcome = self.guard(context("stop"))

        self.assertEqual(outcome.directive, HookDirective.ANNOTATE)
        self.assertEqual(outcome.annotations["guard_code"], "CANONICAL_RUN_VERIFIED")

    def test_stop_still_requires_exact_historical_session_identity(self):
        self.source.manifest["session_id"] = "different"

        outcome = self.guard(context("stop"))

        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "SESSION_BINDING_MISMATCH")

    def test_registration_covers_only_pre_mutation_events(self):
        registry = HookRegistry()
        register_canonical_run_guards(registry, self.guard)

        self.assertEqual(len(registry.list_for(HookEvent.RUN_STARTING)), 1)
        self.assertEqual(len(registry.list_for(HookEvent.BEFORE_SEND)), 1)
        self.assertEqual(len(registry.list_for(HookEvent.SESSION_STOPPING)), 1)
        self.assertEqual(len(registry.list_for(HookEvent.RUN_STARTED)), 0)

    def test_service_blocks_adapter_when_canonical_claim_is_invalid(self):
        self.source.task["claimed_by"] = "other-worker"
        registry = HookRegistry()
        register_canonical_run_guards(registry, self.guard)
        adapter = DummyAdapter()
        service = HarnessService([adapter], hooks=registry)

        result = service.send(binding(), ref(), {"message": "continue"})

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "HOOK_DENIED")
        self.assertEqual(adapter.calls, [])
        self.assertEqual(result.data["blocking_reasons"], ["Continuing execution requires the active task claimant."])


if __name__ == "__main__":
    unittest.main()
