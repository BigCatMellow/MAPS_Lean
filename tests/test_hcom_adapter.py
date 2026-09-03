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
    elif os.environ.get("HCOM_FAKE_EVENTS") == "stopped":
        # Real hcom shapes (Step-0 probe 2026-09-03): a top-level session
        # stamps `data.session` on every status transition; its exit is a
        # `life action:stopped` (name, no session) paired with a
        # `status new_status:inactive` (name + session). `still-here` has a
        # status event carrying its session but no stop signal -> not emitted.
        # `ghost` stopped but never had an in-window status event with a
        # session -> emitted without session_id. A subagent `exit:idle`
        # (session:null, agent_id only) must not become a record.
        print(json.dumps({"id": 1, "ts": "2026-09-03T12:00:00", "type": "status", "instance": "nava-worker-1", "data": {"status": "listening", "new_status": "listening", "new_context": "", "session": "sess-nava-uuid"}}))
        print(json.dumps({"id": 2, "ts": "2026-09-03T12:05:00", "type": "status", "instance": "still-here", "data": {"status": "active", "new_status": "active", "session": "sess-still-uuid"}}))
        print(json.dumps({"id": 3, "ts": "2026-09-03T12:10:00", "type": "status", "instance": "nava-worker-1", "data": {"status": "inactive", "new_status": "inactive", "new_context": "exit:clear", "session": "sess-nava-uuid"}}))
        print(json.dumps({"id": 4, "ts": "2026-09-03T12:10:01", "type": "life", "instance": "nava-worker-1", "data": {"action": "stopped", "by": "session", "reason": "exit:clear"}}))
        print(json.dumps({"id": 5, "ts": "2026-09-03T12:11:00", "type": "life", "instance": "ghost", "data": {"action": "stopped", "by": "session", "reason": "exit:timeout"}}))
        print(json.dumps({"id": 6, "ts": "2026-09-03T12:12:00", "type": "status", "instance": "sub_general_purpose_1", "data": {"status": "inactive", "new_status": "inactive", "new_context": "exit:idle", "session": None, "agent_id": "a1b2c3"}}))
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
                # No stop signals in the default events fake -> alive-only
                # payload, never raises.
                self.assertEqual(
                    sorted(item["name"] for item in sessions),
                    ["claude-1", "codex-1"],
                )
                # The `--stopped --all` probe still fires first, then the
                # alive-only fallback, then the events-derived reconstruction
                # (option C). Assert order without pinning it to the tail.
                seq = [c["args"] for c in self.calls()]
                i_stopped = seq.index(["list", "--json", "--stopped", "--all"])
                i_alive = seq.index(["list", "--json"], i_stopped + 1)
                i_events = next(
                    n for n, c in enumerate(seq) if n > i_alive and c[0] == "events"
                )
                self.assertLess(i_stopped, i_alive)
                self.assertLess(i_alive, i_events)

    def test_list_sessions_include_stopped_reconstructs_from_events(self):
        # FROZEN REGRESSION CASE -- 2026-09-03 item 5 / option C. On an hcom
        # build that ignores `--json` for `list --stopped` (real non-JSON text),
        # list_sessions(include_stopped=True) must return the alive list PLUS
        # synthetic stopped records rebuilt from `hcom events`, each carrying the
        # hcom `session_id` when events expose it -- so the
        # session_id -> run_id reverse lookup keeps working for silent stops.
        os.environ["HCOM_FAKE_STOPPED_TEXT"] = "nonempty"
        os.environ["HCOM_FAKE_EVENTS"] = "stopped"
        self.addCleanup(os.environ.pop, "HCOM_FAKE_STOPPED_TEXT", None)
        self.addCleanup(os.environ.pop, "HCOM_FAKE_EVENTS", None)

        sessions = self.adapter.list_sessions(include_stopped=True)
        by_name = {item["name"]: item for item in sessions}

        # No exception; alive records still present and unchanged.
        self.assertEqual(by_name["claude-1"]["session_id"], "s1")
        self.assertEqual(by_name["codex-1"]["status"], "listening")

        # Stopped top-level session reconstructed with its session_id.
        self.assertIn("nava-worker-1", by_name)
        nava = by_name["nava-worker-1"]
        self.assertEqual(nava["session_id"], "sess-nava-uuid")
        self.assertEqual(nava["status"], "inactive")
        self.assertEqual(nava["stop_reason"], "exit:clear")
        self.assertIs(nava["process_bound"], False)

        # A live session seen in events is NOT turned into a stopped record.
        self.assertNotIn("still-here", by_name)
        # A subagent exit:idle (session:null) is dropped.
        self.assertNotIn("sub_general_purpose_1", by_name)
        # A stopped top-level session with no in-window session event still
        # appears (name only) -- run_id will resolve to None, the documented gap.
        self.assertIn("ghost", by_name)
        self.assertNotIn("session_id", by_name["ghost"])

        # The events-derived record reads as not-live for the supervisor.
        from runtime.recovery.supervisor import session_is_live

        self.assertFalse(session_is_live(nava))

        call_args = [c["args"] for c in self.calls()]
        self.assertIn(["list", "--json", "--stopped", "--all"], call_args)
        self.assertIn(["list", "--json"], call_args)
        self.assertTrue(any(c[0] == "events" for c in call_args))

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
