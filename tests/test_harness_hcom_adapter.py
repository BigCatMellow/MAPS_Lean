import unittest

from runtime.communication import HcomError
from runtime.harness import ExecutionBinding, SessionRef
from runtime.harness.adapters import HcomHarnessAdapter


class FakeHcom:
    def __init__(self):
        self.sessions = [
            {
                "name": "codex-1",
                "session_id": "s1",
                "status": "active",
                "tool": "codex",
            }
        ]
        self.sent = []
        self.stopped = []

    def list_sessions(self, *, include_stopped=False):
        return list(self.sessions)

    def send(self, target, message, *, intent="inform", thread=None, from_name=None):
        self.sent.append(
            {
                "target": target,
                "message": message,
                "intent": intent,
                "thread": thread,
                "from_name": from_name,
            }
        )

    def stop(self, name):
        self.stopped.append(name)


def binding(*, session_id="s1", project_id="project-1"):
    return ExecutionBinding(
        task_id="TASK-1",
        run_id="RUN-1",
        worker_id="worker-1",
        task_revision="rev-1",
        project_id=project_id,
        session_id=session_id,
    )


def session_ref(*, status_adapter="hcom", project_id="project-1", remote_ref="codex-1"):
    return SessionRef(
        session_id="s1",
        worker_id="worker-1",
        adapter=status_adapter,
        project_id=project_id,
        remote_ref=remote_ref,
    )


class HcomHarnessAdapterTests(unittest.TestCase):
    def setUp(self):
        self.backend = FakeHcom()
        self.adapter = HcomHarnessAdapter(self.backend, project_id="project-1")

    def test_inspect_maps_known_state(self):
        result = self.adapter.inspect(session_ref())

        self.assertTrue(result.ok)
        self.assertEqual(result.code, "SESSION_INSPECTED")
        self.assertEqual(result.data["status"]["state"], "RUNNING")
        self.assertEqual(result.data["status"]["raw_state"], "active")
        self.assertFalse(result.mutated)

    def test_inspect_preserves_unknown_provider_state(self):
        self.backend.sessions[0]["status"] = "mystery"

        result = self.adapter.inspect(session_ref())

        self.assertTrue(result.ok)
        self.assertEqual(result.data["status"]["state"], "UNKNOWN")
        self.assertIsNone(result.data["status"]["recoverable"])

    def test_inspect_not_found_is_successful_no_result(self):
        self.backend.sessions = []

        result = self.adapter.inspect(session_ref())

        self.assertTrue(result.ok)
        self.assertEqual(result.code, "SESSION_NOT_FOUND")
        self.assertEqual(result.data["session_id"], "s1")

    def test_inspect_rejects_project_and_adapter_mismatch(self):
        wrong_project = self.adapter.inspect(session_ref(project_id="other"))
        wrong_adapter = self.adapter.inspect(session_ref(status_adapter="other"))

        self.assertFalse(wrong_project.ok)
        self.assertEqual(wrong_project.code, "PROJECT_MISMATCH")
        self.assertFalse(wrong_adapter.ok)
        self.assertEqual(wrong_adapter.code, "ADAPTER_MISMATCH")

    def test_inspect_rejects_identity_mismatch(self):
        result = self.adapter.inspect(session_ref(remote_ref="different-name"))

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "SESSION_IDENTITY_MISMATCH")

    def test_send_resolves_explicit_binding_session(self):
        result = self.adapter.send(
            binding(),
            {
                "message": "Inspect TASK-1",
                "intent": "request",
                "thread": "THREAD-TASK-1",
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.code, "SENT")
        self.assertTrue(result.mutated)
        self.assertEqual(self.backend.sent[0]["target"], "codex-1")
        self.assertEqual(self.backend.sent[0]["intent"], "request")

    def test_send_requires_explicit_session_and_message(self):
        no_session = self.adapter.send(binding(session_id=None), {"message": "x"})
        no_message = self.adapter.send(binding(), {"message": " "})

        self.assertFalse(no_session.ok)
        self.assertEqual(no_session.code, "SESSION_REQUIRED")
        self.assertFalse(no_message.ok)
        self.assertEqual(no_message.code, "INVALID_ARGUMENT")

    def test_stop_requires_reason_and_explicit_session(self):
        missing_reason = self.adapter.stop(binding(), " ")
        stopped = self.adapter.stop(binding(), "operator requested stop")

        self.assertFalse(missing_reason.ok)
        self.assertEqual(missing_reason.code, "INVALID_ARGUMENT")
        self.assertTrue(stopped.ok)
        self.assertEqual(stopped.code, "STOP_REQUESTED")
        self.assertEqual(self.backend.stopped, ["codex-1"])

    def test_provider_failure_is_structured(self):
        def fail(*, include_stopped=False):
            raise HcomError("do not expose me")

        self.backend.list_sessions = fail
        result = self.adapter.inspect(session_ref())

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "TRANSPORT_ERROR")
        self.assertNotIn("do not expose me", result.summary)

    def test_unsupported_operations_are_explicit(self):
        self.assertEqual(self.adapter.start(binding(), {}).code, "UNSUPPORTED")
        self.assertEqual(self.adapter.attach(binding(), session_ref()).code, "UNSUPPORTED")
        self.assertEqual(self.adapter.heartbeat(binding()).code, "UNSUPPORTED")
        self.assertEqual(self.adapter.resume(binding()).code, "UNSUPPORTED")
        self.assertEqual(self.adapter.collect(binding()).code, "UNSUPPORTED")


if __name__ == "__main__":
    unittest.main()
