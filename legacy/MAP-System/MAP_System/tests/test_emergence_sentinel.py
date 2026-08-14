import json
from pathlib import Path
import tempfile
import unittest

from MAP_System.scripts.emergence_sentinel import curate, detect, main, scan, write_state


class EmergenceSentinelTests(unittest.TestCase):
    def test_detects_repeated_rework_and_blockers(self):
        events = [
            {"task_id": "TASK-1", "type": "CHANGES_REQUESTED"},
            {"task_id": "TASK-1", "type": "CHANGES_REQUESTED"},
            {"task_id": "TASK-2", "type": "BLOCKED"},
            {"task_id": "TASK-2", "type": "BLOCKED"},
        ]
        kinds = {x["signal_type"] for x in detect(events)}
        self.assertEqual({"repeated_rework", "repeated_blocker"}, kinds)

    def test_system_sender_blocked_events_do_not_trigger_repeated_blocker(self):
        # Reproduces the live 2026-07-27 finding (INS-0050): TASK-083 showed
        # 54 "blockers" that were all limit_watcher's own routine operational
        # log entries about OTHER agents, not TASK-083's own progress being
        # blocked. A genuine blocker from a real agent must still fire.
        events = [
            {"task_id": "TASK-083", "type": "BLOCKED", "sender": "limit_watcher"},
            {"task_id": "TASK-083", "type": "BLOCKED", "sender": "limit-watcher"},
            {"task_id": "TASK-083", "type": "BLOCKED", "sender": "limit_watcher"},
            {"task_id": "TASK-189", "type": "BLOCKED", "sender": "codex-lab-nivo"},
            {"task_id": "TASK-189", "type": "BLOCKED", "sender": "codex-lab-nivo"},
        ]
        signals = detect(events)
        subjects = {(x["signal_type"], x["subject"]) for x in signals}
        self.assertNotIn(("repeated_blocker", "TASK-083"), subjects)
        self.assertIn(("repeated_blocker", "TASK-189"), subjects)

    def test_scan_deduplicates_and_never_promotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            events = root / "events.jsonl"
            queue = root / "queue"
            state = root / "state.json"
            lines = [
                {"task_id": "TASK-1", "type": "CHANGES_REQUESTED"},
                {"task_id": "TASK-1", "type": "CHANGES_REQUESTED"},
            ]
            events.write_text("\n".join(json.dumps(x) for x in lines) + "\n")
            first = scan(events, queue, state)
            second = scan(events, queue, state)
            self.assertEqual(1, len(first["created"]))
            self.assertEqual([], second["created"])
            candidate = json.loads(next(queue.glob("CAND-*.json")).read_text())
            self.assertEqual("new", candidate["status"])
            self.assertNotIn("insight_id", candidate)

    def test_visible_curation_records_actor_reason_and_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CAND-X.json"
            path.write_text(json.dumps({"candidate_id": "CAND-X", "status": "new"}))
            item = curate(path, "accepted", "codex-visible", "valid pattern", "INS-9999")
            self.assertEqual("codex-visible", item["curated_by"])
            self.assertEqual("INS-9999", item["resolution_ref"])

    def test_documented_cli_curation_path_records_actor(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp)
            path = queue / "CAND-X.json"
            path.write_text(json.dumps({"candidate_id": "CAND-X", "status": "new"}))
            rc = main(["curate", "CAND-X", "--queue", str(queue), "--action", "parked", "--actor", "codex-visible", "--reason", "duplicate"])
            self.assertEqual(0, rc)
            self.assertEqual("codex-visible", json.loads(path.read_text())["curated_by"])

    def test_stop_blocks_scan_until_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "state.json"
            events = root / "events.jsonl"
            queue = root / "queue"
            events.write_text("")
            write_state(state, stop_requested=True, status="stopped")
            self.assertTrue(scan(events, queue, state)["stopped"])
            self.assertEqual(0, main(["control", "resume", "--state", str(state)]))
            self.assertTrue(scan(events, queue, state)["ok"])

    def test_command_center_exposes_visible_controls_and_schedule(self):
        html = Path("MAP_System/templates/install/command-center-ui/src/chat.html").read_text()
        js = Path("MAP_System/templates/install/command-center-ui/src/chat.js").read_text()
        server = Path("MAP_System/templates/install/command-center-ui/app/server.py").read_text()
        for marker in ("sentinel-status", "sentinel-scan", "sentinel-stop", "sentinel-resume"):
            self.assertIn(marker, html)
        self.assertIn('sentinelAction("scan")', js)
        self.assertIn("30 * 60 * 1000", js)
        self.assertIn("/api/map/emergence-sentinel/control", server)


if __name__ == "__main__":
    unittest.main()
