import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from MAP_System.scripts.map_steward import deterministic_recommendations, parse_model_output, run


class MapStewardTests(unittest.TestCase):
    def test_deterministic_attention_prioritizes_rework_review_and_ei(self):
        packet = {"actionable_tasks": [{"task_id": "TASK-1", "status": "CHANGES_REQUESTED"}, {"task_id": "TASK-2", "status": "SUBMITTED"}], "lesson_errors": [], "active_lessons": [], "new_ei_candidates": [{"candidate_id": "CAND-X"}]}
        kinds = {x["kind"] for x in deterministic_recommendations(packet)}
        self.assertEqual({"rework", "review", "emergence"}, kinds)

    def test_model_parser_rejects_prose_and_oversized_output(self):
        with self.assertRaises(ValueError):
            parse_model_output("not json")
        with self.assertRaises(ValueError):
            parse_model_output(json.dumps({"recommendations": [{}] * 6}))

    def test_model_failure_falls_back_without_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state.json"
            proc = Mock(returncode=1, stdout="", stderr="offline")
            result = run(True, 1, state, model_runner=lambda *a, **k: proc)
            self.assertEqual("deterministic-fallback", result["mode"])
            self.assertIn("offline", result["last_error"])
            serialized = state.read_text()
            for forbidden in ("hcom send", "claim_task(", "approve_task(", "map_emergence.py promote"):
                self.assertNotIn(forbidden, serialized)

    def test_writes_only_explicit_state_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "state.json"
            run(False, 1, state)
            self.assertEqual([state], list(root.iterdir()))

    def test_stop_persists_until_explicit_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state.json"
            state.write_text(json.dumps({"schema_version": 1, "status": "stopped", "stop_requested": True}))
            stopped = run(False, 1, state)
            self.assertEqual("stopped", stopped["status"])
            self.assertTrue(stopped["stop_requested"])
            resumed = run(False, 1, state, resume=True)
            self.assertEqual("idle", resumed["status"])
            self.assertFalse(resumed["stop_requested"])

    def test_command_center_renders_inputs_and_resume_control(self):
        html = Path("MAP_System/templates/install/command-center-ui/src/chat.html").read_text()
        js = Path("MAP_System/templates/install/command-center-ui/src/chat.js").read_text()
        self.assertIn("steward-inputs", html)
        self.assertIn("steward-resume", html)
        self.assertIn("Inputs:", js)
        self.assertIn('stewardAction("resume")', js)


if __name__ == "__main__":
    unittest.main()
