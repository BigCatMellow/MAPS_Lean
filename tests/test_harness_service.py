from datetime import datetime, timezone
import unittest

from runtime.harness import (
    ExecutionBinding,
    HookDirective,
    HookEvent,
    HookOutcome,
    HookRegistry,
    HookSpec,
    OperationResult,
    SessionRef,
)
from runtime.harness.service import HarnessService
from runtime.policy import CanonicalRunGuard, register_canonical_run_guards


NOW = datetime(2026, 8, 15, 16, 0, 0, tzinfo=timezone.utc)


class FakeCanonicalSource:
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
        self.session_adapter = "dummy"

    def get_task(self, task_id):
        return dict(self.task) if task_id == "TASK-1" else None

    def get_run_manifest(self, run_id):
        return dict(self.manifest) if run_id == "RUN-1" else None

    def compute_task_revision(self, task_id):
        return "rev-1" if task_id == "TASK-1" else None

    def check_run_stale(self, run_id, *, repo_root):
        return {"run_id": run_id, "stale": False}

    def resolve_run_session(self, run_id):
        if run_id != "RUN-1":
            return None
        session_id = self.manifest.get("session_id")
        if not session_id:
            return {
                "run_id": run_id,
                "state": "UNBOUND",
                "current": None,
                "history": [],
            }
        if not self.session_adapter:
            return {
                "run_id": run_id,
                "state": "ADAPTER_UNPROVEN",
                "current": {
                    "link_id": None,
                    "adapter_id": None,
                    "session_id": session_id,
                },
                "history": [],
            }
        return {
            "run_id": run_id,
            "state": "EXPLICIT",
            "current": {
                "link_id": 1,
                "adapter_id": self.session_adapter,
                "session_id": session_id,
            },
            "history": [],
        }


class DummyAdapter:
    adapter_id = "dummy"

    def __init__(self):
        self.calls = []

    def start(self, binding, launch_spec):
        self.calls.append(("start", binding.run_id, dict(launch_spec)))
        return OperationResult.success("STARTED", "Started.", mutated=True)

    def attach(self, binding, session_ref):
        self.calls.append(("attach", binding.run_id, session_ref.session_id))
        return OperationResult.success("ATTACHED", "Attached.")

    def send(self, binding, payload):
        self.calls.append(("send", binding.run_id, dict(payload)))
        return OperationResult.success("SENT", "Sent.", mutated=True)

    def inspect(self, session_ref):
        self.calls.append(("inspect", session_ref.session_id))
        return OperationResult.success("INSPECTED", "Inspected.")

    def heartbeat(self, binding):
        self.calls.append(("heartbeat", binding.run_id))
        return OperationResult.success("HEARTBEAT", "Heartbeat.")

    def resume(self, binding):
        self.calls.append(("resume", binding.run_id))
        return OperationResult.success("RESUMED", "Resumed.", mutated=True)

    def stop(self, binding, reason):
        self.calls.append(("stop", binding.run_id, reason))
        return OperationResult.success("STOPPED", "Stopped.", mutated=True)

    def collect(self, binding):
        self.calls.append(("collect", binding.run_id))
        return OperationResult.success("COLLECTED", "Collected.")


def binding(*, session_id="session-1", worker_id="worker-1", project_id="project-1"):
    return ExecutionBinding(
        task_id="TASK-1",
        run_id="RUN-1",
        worker_id=worker_id,
        task_revision="rev-1",
        project_id=project_id,
        session_id=session_id,
    )


def ref(*, session_id="session-1", worker_id="worker-1", project_id="project-1"):
    return SessionRef(
        session_id=session_id,
        worker_id=worker_id,
        adapter="dummy",
        project_id=project_id,
        remote_ref="dummy-1",
    )


class HarnessServiceTests(unittest.TestCase):
    def setUp(self):
        self.adapter = DummyAdapter()
        self.hooks = HookRegistry()
        register_canonical_run_guards(
            self.hooks,
            CanonicalRunGuard(FakeCanonicalSource(), repo_root=".", now=lambda: NOW),
        )
        self.service = HarnessService([self.adapter], hooks=self.hooks)

    def test_adapter_registration_is_explicit_and_unique(self):
        self.assertEqual(self.service.adapter_ids, ("dummy",))
        with self.assertRaises(ValueError):
            self.service.register_adapter(self.adapter)

    def test_unknown_adapter_is_structured_failure(self):
        unknown = SessionRef(
            session_id="session-1",
            worker_id="worker-1",
            adapter="missing",
            project_id="project-1",
        )
        result = self.service.inspect(unknown)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "ADAPTER_NOT_FOUND")

    def test_inspect_routes_by_session_ref_adapter(self):
        result = self.service.inspect(ref())
        self.assertTrue(result.ok)
        self.assertEqual(self.adapter.calls, [("inspect", "session-1")])

    def test_send_requires_exact_binding_session_identity(self):
        wrong_session = self.service.send(binding(session_id="different"), ref(), {"message": "hello"})
        wrong_worker = self.service.send(binding(worker_id="other"), ref(), {"message": "hello"})
        wrong_project = self.service.send(binding(project_id="other"), ref(), {"message": "hello"})
        self.assertEqual(wrong_session.code, "SESSION_MISMATCH")
        self.assertEqual(wrong_worker.code, "WORKER_MISMATCH")
        self.assertEqual(wrong_project.code, "PROJECT_MISMATCH")
        self.assertEqual(self.adapter.calls, [])

    def test_send_deny_hook_blocks_adapter(self):
        self.hooks.register(
            HookSpec(
                "deny-send",
                HookEvent.BEFORE_SEND,
                lambda ctx: HookOutcome(HookDirective.DENY, "Blocked by guard."),
            )
        )
        result = self.service.send(binding(), ref(), {"message": "hello"})
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "HOOK_DENIED")
        self.assertEqual(result.data["blocking_reasons"], ("Blocked by guard.",))
        self.assertEqual(self.adapter.calls, [])

    def test_send_approval_hook_blocks_without_granting_approval(self):
        self.hooks.register(
            HookSpec(
                "approval",
                HookEvent.BEFORE_SEND,
                lambda ctx: HookOutcome(
                    HookDirective.REQUIRE_APPROVAL,
                    "Operator approval required.",
                ),
            )
        )
        result = self.service.send(binding(), ref(), {"message": "hello"})
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "APPROVAL_REQUIRED")
        self.assertEqual(self.adapter.calls, [])

    def test_allowed_send_calls_adapter(self):
        result = self.service.send(binding(), ref(), {"message": "hello"})
        self.assertTrue(result.ok)
        self.assertEqual(result.code, "SENT")
        self.assertEqual(self.adapter.calls[0][0], "send")

    def test_stop_uses_session_stopping_hook(self):
        seen = []

        def guard(ctx):
            seen.append(ctx["details"]["reason"])
            return HookOutcome(HookDirective.DENY, "Do not stop.")

        self.hooks.register(HookSpec("stop-guard", HookEvent.SESSION_STOPPING, guard))
        result = self.service.stop(binding(), ref(), "recovery wants replacement")
        self.assertEqual(result.code, "HOOK_DENIED")
        self.assertEqual(seen, ["recovery wants replacement"])
        self.assertEqual(self.adapter.calls, [])

    def test_start_pre_hook_blocks_before_adapter(self):
        self.hooks.register(
            HookSpec(
                "start-guard",
                HookEvent.RUN_STARTING,
                lambda ctx: HookOutcome(HookDirective.DENY, "Start denied."),
            )
        )
        result = self.service.start("dummy", binding(session_id=None), {"tool": "x"})
        self.assertEqual(result.code, "HOOK_DENIED")
        self.assertEqual(self.adapter.calls, [])

    def test_start_hook_observes_canonical_selected_adapter_id(self):
        seen = []

        def guard(ctx):
            seen.append(ctx["adapter_id"])
            return HookOutcome(HookDirective.ALLOW)

        self.hooks.register(HookSpec("start-id", HookEvent.RUN_STARTING, guard))
        result = self.service.start(" dummy ", binding(session_id=None), {"tool": "x"})
        self.assertTrue(result.ok)
        self.assertEqual(seen, ["dummy"])
        self.assertEqual(self.adapter.calls[0][0], "start")

    def test_post_start_block_preserves_that_mutation_already_happened(self):
        self.hooks.register(
            HookSpec(
                "post-start",
                HookEvent.RUN_STARTED,
                lambda ctx: HookOutcome(HookDirective.DENY, "Post-start check failed."),
            )
        )
        result = self.service.start("dummy", binding(session_id=None), {"tool": "x"})
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "HOOK_DENIED")
        self.assertTrue(result.mutated)
        self.assertEqual(result.data["adapter_result"]["code"], "STARTED")
        self.assertEqual(self.adapter.calls[0][0], "start")

    def test_attach_allows_unbound_binding_but_checks_worker_and_project(self):
        result = self.service.attach(binding(session_id=None), ref())
        self.assertTrue(result.ok)
        self.assertEqual(self.adapter.calls[0][0], "attach")
        wrong = self.service.attach(binding(session_id=None, worker_id="other"), ref())
        self.assertEqual(wrong.code, "WORKER_MISMATCH")

    def test_mutations_require_canonical_guard(self):
        adapter = DummyAdapter()
        service = HarnessService([adapter])
        results = (
            service.start("dummy", binding(session_id=None), {"tool": "x"}),
            service.send(binding(), ref(), {"message": "hello"}),
            service.resume(binding(), ref()),
            service.stop(binding(), ref(), "cleanup"),
        )
        self.assertTrue(all(result.code == "CANONICAL_GUARD_REQUIRED" for result in results))
        self.assertEqual(adapter.calls, [])

    def test_plain_allow_hook_is_not_canonical_guard(self):
        adapter = DummyAdapter()
        hooks = HookRegistry()
        hooks.register(
            HookSpec(
                "allow",
                HookEvent.BEFORE_SEND,
                lambda ctx: HookOutcome(HookDirective.ALLOW),
            )
        )
        service = HarnessService([adapter], hooks=hooks)
        result = service.send(binding(), ref(), {"message": "hello"})
        self.assertEqual(result.code, "CANONICAL_GUARD_REQUIRED")
        self.assertEqual(adapter.calls, [])


if __name__ == "__main__":
    unittest.main()
