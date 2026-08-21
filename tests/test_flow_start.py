from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.cli import main
from runtime.flow_start import flow_start
from runtime.state import TaskStore


def contract(*, output_path: str = "src") -> dict:
    return {
        "title": "Flow start fixture",
        "outcome": "A deterministic flow can start a task",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "bounded implementation",
        "verification": "flow start tests",
        "evidence_expected": "test output",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "operator on scope change",
        "inputs": ["README.md"],
        "sources": ["AGENTS.md"],
        "dependencies": [],
        "output_paths": [output_path],
        "non_goals": ["no provider launch"],
        "acceptance_criteria": ["run manifest is bound"],
        "stop_conditions": ["stop on ambiguous worker"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class FlowStartTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "README.md").write_text("fixture\n", encoding="utf-8")
        (self.repo / "AGENTS.md").write_text("authority\n", encoding="utf-8")
        self.store = TaskStore(self.root / "maps.db")

    def make_ready(self) -> str:
        created = self.store.create_task(title="flow fixture")
        self.assertTrue(created.ok, created.message)
        task_id = created.task["task_id"]
        shaped = self.store.update_contract(task_id, contract())
        self.assertTrue(shaped.ok, shaped.message)
        promoted = self.store.promote_ready(task_id, actor="tester")
        self.assertTrue(promoted.ok, promoted.message)
        return task_id

    def test_flow_start_claims_builds_context_and_binds_run(self):
        task_id = self.make_ready()

        result = flow_start(
            self.store,
            task_id,
            worker_id="worker-1",
            repo_root=self.repo,
            created_by="tester",
            context_paths=["README.md"],
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["code"], "FLOW_STARTED")
        self.assertEqual(result["claim"]["code"], "CLAIMED")
        self.assertEqual(result["context_plan"]["task_id"], task_id)
        self.assertTrue(result["context_plan"]["coverage"]["explicit_task_relationships"])
        manifest = result["run_manifest"]
        self.assertEqual(manifest["task_id"], task_id)
        self.assertEqual(manifest["worker_id"], "worker-1")
        self.assertEqual(manifest["context_refs"][0]["path"], "README.md")
        self.assertEqual(
            result["next_step"]["state"],
            "STOPPED_BEFORE_PROVIDER_SESSION",
        )

    def test_flow_start_stops_when_claim_fails(self):
        created = self.store.create_task(title="unready")
        self.assertTrue(created.ok, created.message)

        result = flow_start(
            self.store,
            created.task["task_id"],
            worker_id="worker-1",
            repo_root=self.repo,
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "claim")
        self.assertEqual(result["step_result"]["code"], "NOT_CLAIMABLE")

    def test_flow_start_stops_when_context_path_cannot_be_bound(self):
        task_id = self.make_ready()

        result = flow_start(
            self.store,
            task_id,
            worker_id="worker-1",
            repo_root=self.repo,
            created_by="tester",
            context_paths=["missing.md"],
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_step"], "run_manifest")
        self.assertEqual(result["step_result"]["code"], "INVALID_CONTEXT")

    def test_cli_flow_start_emits_json_success(self):
        task_id = self.make_ready()
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            exit_code = main(
                [
                    "--db",
                    str(self.root / "maps.db"),
                    "flow",
                    "start",
                    task_id,
                    "--worker-id",
                    "worker-1",
                    "--repo-root",
                    str(self.repo),
                    "--created-by",
                    "tester",
                    "--context-path",
                    "README.md",
                ]
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["code"], "FLOW_STARTED")
        self.assertEqual(payload["run_manifest"]["task_id"], task_id)

    def test_cli_flow_start_failure_exits_nonzero(self):
        created = self.store.create_task(title="unready")
        self.assertTrue(created.ok, created.message)
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            exit_code = main(
                [
                    "--db",
                    str(self.root / "maps.db"),
                    "flow",
                    "start",
                    created.task["task_id"],
                    "--worker-id",
                    "worker-1",
                    "--repo-root",
                    str(self.repo),
                ]
            )

        self.assertEqual(exit_code, 2)
        payload = json.loads(buffer.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["failed_step"], "claim")


if __name__ == "__main__":
    unittest.main()
