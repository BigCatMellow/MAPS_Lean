from pathlib import Path
import tempfile
import unittest

from runtime.communication import HcomError
from runtime.harness import ExecutionBinding, SessionRef
from runtime.harness.adapters import HcomHarnessAdapter
from runtime.state import TaskStore


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

    def test_stop_normalizes_low_level_value_error(self):
        def reject(name):
            raise ValueError("provider-controlled invalid target")

        self.backend.stop = reject
        result = self.adapter.stop(binding(), "operator requested stop")

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "INVALID_ARGUMENT")
        self.assertEqual(result.data["error_type"], "ValueError")
        self.assertNotIn("provider-controlled", result.summary)

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


def _contract(*, output_path="src"):
    return {
        "title": "hcom attach lineage",
        "outcome": "hcom attach durably binds a session to a run",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "bounded implementation only",
        "verification": "harness adapter lineage tests",
        "evidence_expected": "test output",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "operator on authority conflict",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": [output_path],
        "non_goals": ["no task authority changes"],
        "acceptance_criteria": ["attach is durable"],
        "stop_conditions": ["stop on ambiguous identity"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class HcomHarnessAdapterLineageWriterTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        self.store = TaskStore(self.root / "maps.db")
        self.backend = FakeHcom()
        self.adapter = HcomHarnessAdapter(
            self.backend, project_id="default", lineage_writer=self.store
        )

    def _make_run(self, worker="worker-1"):
        created = self.store.create_task(title="x")
        self.assertTrue(created.ok)
        task_id = created.task["task_id"]
        self.assertTrue(self.store.update_contract(task_id, _contract()).ok)
        self.assertTrue(self.store.promote_ready(task_id).ok)
        self.assertTrue(self.store.claim_task(task_id, worker, lease_seconds=600).ok)
        result = self.store.create_run_manifest(
            task_id,
            worker,
            repo_root=self.repo,
            created_by="dispatcher",
            readable_paths=["."],
            writable_paths=["src"],
        )
        self.assertTrue(result.ok, result.message)
        return result.task

    def _binding(self, run, *, worker="worker-1", session_id="s1"):
        return ExecutionBinding(
            task_id=run["task_id"],
            run_id=run["run_id"],
            worker_id=worker,
            task_revision=run["task_revision"],
            project_id="default",
            session_id=session_id,
        )

    def _session_ref(self, *, worker="worker-1", session_id="s1", remote_ref="codex-1"):
        return SessionRef(
            session_id=session_id,
            worker_id=worker,
            adapter="hcom",
            project_id="default",
            remote_ref=remote_ref,
        )

    def test_first_attach_records_link_and_mutates(self):
        run = self._make_run()
        result = self.adapter.attach(self._binding(run), self._session_ref())

        self.assertTrue(result.ok, result.summary)
        self.assertEqual(result.code, "SESSION_ATTACHED")
        self.assertTrue(result.mutated)

        resolved = self.store.resolve_run_session(run["run_id"])
        self.assertEqual(resolved["state"], "EXPLICIT")
        self.assertEqual(resolved["current"]["session_id"], "s1")
        self.assertEqual(resolved["current"]["adapter_id"], "hcom")

    def test_repeated_attach_to_same_session_is_idempotent(self):
        run = self._make_run()
        first = self.adapter.attach(self._binding(run), self._session_ref())
        self.assertTrue(first.ok)

        second = self.adapter.attach(self._binding(run), self._session_ref())
        self.assertTrue(second.ok)
        self.assertEqual(second.code, "SESSION_ALREADY_ATTACHED")
        self.assertFalse(second.mutated)

        history = self.store.resolve_run_session(run["run_id"])["history"]
        self.assertEqual(len(history), 1)

    def test_attach_to_different_session_records_replace(self):
        run = self._make_run()
        first = self.adapter.attach(self._binding(run), self._session_ref())
        self.assertTrue(first.ok)

        replace = self.adapter.attach(
            self._binding(run, session_id="s2"),
            self._session_ref(session_id="s2", remote_ref="codex-2"),
        )
        self.assertTrue(replace.ok, replace.summary)
        self.assertEqual(replace.code, "SESSION_REPLACED")
        self.assertTrue(replace.mutated)

        resolved = self.store.resolve_run_session(run["run_id"])
        self.assertEqual(resolved["current"]["session_id"], "s2")
        self.assertEqual(len(resolved["history"]), 2)

    def test_attach_unknown_run_fails_closed(self):
        binding = ExecutionBinding(
            task_id="TASK-MISSING",
            run_id="RUN-MISSING",
            worker_id="worker-1",
            task_revision="rev-x",
            project_id="default",
            session_id="s1",
        )
        result = self.adapter.attach(binding, self._session_ref())

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "RUN_NOT_FOUND")

    def test_attach_rejection_from_writer_is_surfaced_verbatim(self):
        run = self._make_run(worker="worker-1")
        # A different worker than the run's immutable worker_id triggers
        # record_run_session_link's own RUN_WORKER_MISMATCH rejection.
        other_worker_binding = self._binding(run, worker="worker-2")
        result = self.adapter.attach(other_worker_binding, self._session_ref(worker="worker-2"))

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "RUN_WORKER_MISMATCH")

        resolved = self.store.resolve_run_session(run["run_id"])
        self.assertEqual(resolved["state"], "UNBOUND")


if __name__ == "__main__":
    unittest.main()
