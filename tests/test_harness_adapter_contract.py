from __future__ import annotations

import unittest

from runtime.harness import AdapterContractMixin, ExecutionBinding, SessionRef
from runtime.harness.adapters import HcomHarnessAdapter


class _FakeHcomBackend:
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
        self.sent.append({"target": target, "message": message})

    def stop(self, name):
        self.stopped.append(name)


class HcomAdapterContractTests(AdapterContractMixin, unittest.TestCase):
    """Proves `HcomHarnessAdapter` -- the one currently supported adapter --
    satisfies the shared `HarnessAdapter` contract (H5's "contract suite"
    exit gate). `lineage_writer` is intentionally left unconfigured (the
    default-off state); `attach()` returning a structured `UNSUPPORTED`
    result in that configuration still satisfies the contract, which only
    requires a well-typed `OperationResult`, not that every operation be
    normalized yet.
    """

    def setUp(self):
        self.backend = _FakeHcomBackend()
        self.adapter = HcomHarnessAdapter(self.backend, project_id="project-1")
        self.binding = ExecutionBinding(
            task_id="TASK-1",
            run_id="RUN-1",
            worker_id="worker-1",
            task_revision="rev-1",
            project_id="project-1",
            session_id="s1",
        )
        self.session_ref = SessionRef(
            session_id="s1",
            worker_id="worker-1",
            adapter="hcom",
            project_id="project-1",
            remote_ref="codex-1",
        )
        self.launch_spec = {}
        self.payload = {"message": "hello"}
        self.stop_reason = "contract test"


if __name__ == "__main__":
    unittest.main()
