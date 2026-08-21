import importlib.util
import tempfile
import unittest
from pathlib import Path

from runtime.policy import HaltRecord, WorkerProfile
from runtime.routing.langgraph_runtime import (
    _deserialize_environment_reports,
    _serialize_environment_reports,
    run_checkpointed_route,
)
from runtime.environment.fingerprint import CompatibilityReport, CompatibilityState

LANGGRAPH_AVAILABLE = (
    importlib.util.find_spec("langgraph") is not None
    and importlib.util.find_spec("langgraph.checkpoint.sqlite") is not None
)


class LangGraphRoutingTests(unittest.TestCase):
    def test_environment_reports_serialize_without_environment_access(self):
        report = CompatibilityReport(
            state=CompatibilityState.INCOMPATIBLE,
            reasons=("missing_tool",),
            warnings=(),
            environment_spec_hash="spec-hash",
            fingerprint_sha256="fingerprint-hash",
        )
        serialized = _serialize_environment_reports({"TASK-1": report})
        restored = _deserialize_environment_reports(serialized)
        self.assertEqual(restored, {"TASK-1": report})

    def test_checkpoint_db_cannot_equal_task_db(self):
        with tempfile.TemporaryDirectory() as td:
            same = Path(td) / "state.db"
            with self.assertRaises(ValueError):
                run_checkpointed_route(
                    tasks=[],
                    workers=[],
                    halt=HaltRecord(),
                    checkpoint_path=same,
                    task_db_path=same,
                )

    @unittest.skipUnless(
        LANGGRAPH_AVAILABLE,
        "langgraph + langgraph-checkpoint-sqlite not installed",
    )
    def test_checkpointed_route_uses_separate_database(self):
        with tempfile.TemporaryDirectory() as td:
            checkpoint = Path(td) / "langgraph-checkpoints.db"
            task_db = Path(td) / "maps.db"
            task = {
                "task_id": "TASK-1",
                "project_id": "default",
                "status": "READY",
                "agi_status": "AGI READY",
                "task_type": "IMPLEMENTATION",
                "risk": "LOW",
                "output_paths": ["runtime/example.py"],
                "policy": {},
            }
            worker = WorkerProfile(
                "worker",
                "bounded",
                supported_task_types=("IMPLEMENTATION",),
                max_risk="LOW",
                cost_rank=1,
            )
            result = run_checkpointed_route(
                tasks=[task],
                workers=[worker],
                halt=HaltRecord(),
                checkpoint_path=checkpoint,
                task_db_path=task_db,
                thread_id="test-routing",
            )
            self.assertEqual(result["route"], "claim_or_assign")
            self.assertTrue(checkpoint.exists())
            self.assertFalse(task_db.exists())


if __name__ == "__main__":
    unittest.main()
