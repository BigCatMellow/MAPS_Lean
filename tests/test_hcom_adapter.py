import json
import os
from pathlib import Path
import stat
import tempfile
import unittest

from runtime.communication import HcomAdapter, HcomCommandError, HcomProtocolError


FAKE_HCOM = r'''#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
log = os.environ.get("HCOM_FAKE_LOG")
if log:
    with open(log, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({"args": args, "hcom_dir": os.environ.get("HCOM_DIR")}) + "\n")

if args == ["--version"]:
    print("hcom fake-1.0")
elif args == ["status"]:
    print("ok")
elif args[:2] == ["list", "--json"] and "--stopped" in args:
    # hcom 0.7.25 ignores --json for --stopped: it always emits human text.
    mode = os.environ.get("HCOM_FAKE_STOPPED_TEXT", "nonempty")
    if mode == "empty":
        print("No recently stopped agents (last 60m)")
    else:
        print("Stopped agents (all, showing 2):\n")
        print("  nava-worker-1 (claude tag:maps-lean) 2h ago  [idle by:subagent]  ~/Projects/MAPS_Lean")
        print("  codex-1 (codex) 5h ago  [timeout by:subagent]  ~/Projects/MAPS_Lean")
elif args[:2] == ["list", "--json"]:
    if os.environ.get("HCOM_FAKE_BAD_LIST") == "1":
        print("not json")
    else:
        print(json.dumps([
            {"name": "claude-1", "session_id": "s1", "status": "active", "tool": "claude"},
            {"name": "codex-1", "session_id": "s2", "status": "listening", "tool": "codex"}
        ]))
elif args and args[0] == "events":
    if os.environ.get("HCOM_FAKE_BAD_EVENTS") == "1":
        print("not json")
    else:
        print(json.dumps({"id": 1, "ts": "2026-08-14T20:00:00", "type": "message", "instance": "x", "data": {"from": "a", "intent": "inform", "text": "hello"}}))
        print(json.dumps({"id": 2, "ts": "2026-08-14T20:00:01", "type": "status", "instance": "x", "data": {"status": "active"}}))
elif args and args[0] in {"send", "r", "kill", "claude", "codex", "qwen", "opencode"}:
    if os.environ.get("HCOM_FAKE_FAIL") == "1":
        print("forced failure", file=sys.stderr)
        raise SystemExit(7)
    print("ok")
else:
    print("unsupported", file=sys.stderr)
    raise SystemExit(3)
'''


class HcomAdapterTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        root = Path(self.td.name)
        self.fake = root / "hcom"
        self.fake.write_text(FAKE_HCOM, encoding="utf-8")
        self.fake.chmod(self.fake.stat().st_mode | stat.S_IXUSR)
        self.hcom_dir = root / ".hcom"
        self.log = root / "calls.jsonl"
        os.environ["HCOM_FAKE_LOG"] = str(self.log)
        self.addCleanup(os.environ.pop, "HCOM_FAKE_LOG", None)
        self.adapter = HcomAdapter(
            executable=self.fake,
            hcom_dir=self.hcom_dir,
            timeout_seconds=5,
        )

    def calls(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_list_sessions_uses_json_and_project_hcom_dir(self):
        sessions = self.adapter.list_sessions()
        self.assertEqual([item["name"] for item in sessions], ["claude-1", "codex-1"])
        call = self.calls()[-1]
        self.assertEqual(call["args"], ["list", "--json"])
        self.assertEqual(call["hcom_dir"], str(self.hcom_dir.resolve()))

    def test_list_sessions_include_stopped_survives_nonjson_stopped_output(self):
        # FROZEN REGRESSION CASE -- 2026-09-03 BLOCKING defect: hcom 0.7.25
        # ignores `--json` for `list --stopped` and returns human-formatted
        # text, which used to raise HcomProtocolError and abort
        # `maps recovery-tick` before it could reach the supervisor.
        # The adapter must now degrade to the alive-only listing, not explode.
        for mode in ("nonempty", "empty"):
            with self.subTest(stopped_output=mode):
                os.environ["HCOM_FAKE_STOPPED_TEXT"] = mode
                self.addCleanup(os.environ.pop, "HCOM_FAKE_STOPPED_TEXT", None)
                sessions = self.adapter.list_sessions(include_stopped=True)
                # Alive-only fallback payload -- never raises.
                self.assertEqual(
                    sorted(item["name"] for item in sessions),
                    ["claude-1", "codex-1"],
                )
                recent = [c["args"] for c in self.calls()][-2:]
                self.assertEqual(recent[0], ["list", "--json", "--stopped", "--all"])
                self.assertEqual(recent[1], ["list", "--json"])

    def test_list_sessions_include_stopped_nonjson_fallback_logs_once(self):
        os.environ["HCOM_FAKE_STOPPED_TEXT"] = "nonempty"
        self.addCleanup(os.environ.pop, "HCOM_FAKE_STOPPED_TEXT", None)
        with self.assertLogs("runtime.communication.hcom_adapter", level="WARNING") as ctx:
            self.adapter.list_sessions(include_stopped=True)
            # Second degraded pass on the same adapter: no additional warning.
            self.adapter.list_sessions(include_stopped=True)
        self.assertEqual(len(ctx.records), 1)
        self.assertIn("non-JSON", ctx.records[0].getMessage())

    def test_list_sessions_alive_only_still_fails_closed_on_bad_json(self):
        # M1 mutation guard: the `if not include_stopped: raise` short-circuit
        # must keep the alive-only path fail-closed on invalid JSON.
        os.environ["HCOM_FAKE_BAD_LIST"] = "1"
        self.addCleanup(os.environ.pop, "HCOM_FAKE_BAD_LIST", None)
        with self.assertRaises(HcomProtocolError):
            self.adapter.list_sessions()
        with self.assertRaises(HcomProtocolError):
            self.adapter.list_sessions(include_stopped=True)

    def test_events_parse_json_lines_and_are_bounded(self):
        events = self.adapter.read_events(last=25, intent="inform", agent="claude-1")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["data"]["text"], "hello")
        args = self.calls()[-1]["args"]
        self.assertEqual(args[:3], ["events", "--last", "25"])
        self.assertIn("--intent", args)
        self.assertIn("--agent", args)
        with self.assertRaises(ValueError):
            self.adapter.read_events(last=5001)

    def test_bad_event_protocol_fails_closed(self):
        os.environ["HCOM_FAKE_BAD_EVENTS"] = "1"
        self.addCleanup(os.environ.pop, "HCOM_FAKE_BAD_EVENTS", None)
        with self.assertRaises(HcomProtocolError):
            self.adapter.read_events()

    def test_send_uses_explicit_argv_and_intent(self):
        result = self.adapter.send(
            "claude-1",
            "Please inspect TASK-1",
            intent="request",
            thread="THREAD-TASK-1-review",
        )
        self.assertTrue(result.ok)
        args = self.calls()[-1]["args"]
        self.assertEqual(args[0:2], ["send", "@claude-1"])
        self.assertIn("--intent", args)
        self.assertEqual(args[-2:], ["--", "Please inspect TASK-1"])

    def test_spawn_has_no_required_terminal_and_supports_headless(self):
        work = Path(self.td.name) / "repo"
        work.mkdir()
        result = self.adapter.spawn(
            "claude", directory=work, prompt="Read task", headless=True
        )
        self.assertTrue(result.ok)
        args = self.calls()[-1]["args"]
        self.assertEqual(args[0], "claude")
        self.assertIn("--headless", args)
        self.assertNotIn("--terminal", args)
        self.assertIn("--dir", args)

    def test_resume_does_not_require_wezterm(self):
        self.adapter.resume("claude-1", headless=True)
        args = self.calls()[-1]["args"]
        self.assertEqual(args[:3], ["r", "--go", "claude-1"])
        self.assertIn("--headless", args)
        self.assertNotIn("wezterm", args)

    def test_stop_rejects_fanout(self):
        with self.assertRaises(ValueError):
            self.adapter.stop("all")
        with self.assertRaises(ValueError):
            self.adapter.stop("tag:workers")
        self.assertTrue(self.adapter.stop("codex-1").ok)
        self.assertEqual(self.calls()[-1]["args"], ["kill", "codex-1"])

    def test_command_failure_is_typed(self):
        os.environ["HCOM_FAKE_FAIL"] = "1"
        self.addCleanup(os.environ.pop, "HCOM_FAKE_FAIL", None)
        with self.assertRaises(HcomCommandError) as caught:
            self.adapter.stop("codex-1")
        self.assertEqual(caught.exception.result.returncode, 7)

    def test_source_has_no_task_store_dependency(self):
        source = Path(__file__).parents[1] / "runtime" / "communication" / "hcom_adapter.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("runtime.state", text)
        self.assertNotIn("TaskStore", text)
        self.assertNotIn("maps.db", text)
        self.assertNotIn("shell=True", text)


if __name__ == "__main__":
    unittest.main()
