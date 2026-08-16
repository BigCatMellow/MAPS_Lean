import json
import os
from pathlib import Path
import stat
import tempfile
import unittest

from runtime.communication.hcom_lineage import (
    HcomLineageAdapter,
    HcomLineageProtocolError,
)


FAKE_HCOM = r'''#!/usr/bin/env python3
import json
import os
import sys

args = sys.argv[1:]
log = os.environ.get("HCOM_LINEAGE_FAKE_LOG")
if log:
    with open(log, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(args) + "\n")

if not args or args[0] != "events":
    print("unsupported", file=sys.stderr)
    raise SystemExit(3)
if "--full" not in args:
    print("full required", file=sys.stderr)
    raise SystemExit(4)
if os.environ.get("HCOM_LINEAGE_EMPTY") == "1":
    raise SystemExit(0)
if os.environ.get("HCOM_LINEAGE_BAD_JSON") == "1":
    print("not json")
    raise SystemExit(0)

simple = {
    "id": 41,
    "ts": "2026-08-15T20:00:00.123456",
    "type": "message",
    "instance": "agent-a",
    "data": {
        "from": "agent-a",
        "text": "private body must not be projected",
        "delivered_to": ["agent-b"]
    }
}
rich = {
    "id": 42,
    "ts": "2026-08-15T20:00:01.654321",
    "type": "message",
    "instance": "agent-b",
    "data": {
        "from": "agent-b",
        "text": "ack private body",
        "delivered_to": ["agent-a"],
        "mentions": ["agent-a"],
        "intent": "ack",
        "thread": "THREAD-1",
        "reply_to": "41",
        "reply_to_local": 41
    }
}

if os.environ.get("HCOM_LINEAGE_MISSING_CORE") == "1":
    simple["data"].pop("delivered_to")
if os.environ.get("HCOM_LINEAGE_BAD_INTENT") == "1":
    rich["data"]["intent"] = "approve"
if os.environ.get("HCOM_LINEAGE_DUPLICATE_IDENTITY") == "1":
    rich["id"] = simple["id"]
    rich["instance"] = simple["instance"]

print(json.dumps(simple))
print(json.dumps(rich))
'''


class HcomLineageTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        root = Path(self.td.name)
        self.fake = root / "hcom"
        self.fake.write_text(FAKE_HCOM, encoding="utf-8")
        self.fake.chmod(self.fake.stat().st_mode | stat.S_IXUSR)
        self.log = root / "calls.jsonl"
        os.environ["HCOM_LINEAGE_FAKE_LOG"] = str(self.log)
        self.addCleanup(os.environ.pop, "HCOM_LINEAGE_FAKE_LOG", None)
        self.adapter = HcomLineageAdapter(
            executable=self.fake,
            hcom_dir=root / ".hcom",
            timeout_seconds=5,
        )

    def calls(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def _env(self, key: str):
        os.environ[key] = "1"
        self.addCleanup(os.environ.pop, key, None)

    def test_full_read_is_bounded_filtered_and_body_free(self):
        events = self.adapter.read_message_lineage(
            last=25,
            intent="ack",
            agent="agent-b",
            thread="THREAD-1",
        )
        self.assertEqual(len(events), 2)
        args = self.calls()[-1]
        self.assertEqual(args[:5], ["events", "--last", "25", "--full", "--type"])
        self.assertEqual(args[5], "message")
        self.assertIn("--intent", args)
        self.assertIn("--agent", args)
        self.assertIn("--thread", args)
        serialized = json.dumps(events)
        self.assertNotIn("private body", serialized)
        self.assertNotIn('"text"', serialized)
        self.assertTrue(events[0]["coverage"]["full_fidelity_read"])
        self.assertFalse(events[0]["coverage"]["message_body_included"])
        with self.assertRaises(ValueError):
            self.adapter.read_message_lineage(last=5001)

    def test_absent_optional_fields_remain_absent_not_inferred(self):
        event = self.adapter.read_message_lineage()[0]
        self.assertEqual(event["event_id"], 41)
        self.assertEqual(event["sender"], "agent-a")
        self.assertEqual(event["delivered_to"], ["agent-b"])
        self.assertIsNone(event["mentions"])
        self.assertIsNone(event["intent"])
        self.assertIsNone(event["thread"])
        self.assertIsNone(event["reply_to"])
        self.assertIsNone(event["reply_to_local"])
        self.assertEqual(
            event["coverage"]["field_presence"],
            {
                "mentions": False,
                "intent": False,
                "thread": False,
                "reply_to": False,
                "reply_to_local": False,
            },
        )

    def test_rich_message_preserves_exact_structured_correlation(self):
        event = self.adapter.read_message_lineage()[1]
        self.assertEqual(event["event_id"], 42)
        self.assertEqual(event["sender"], "agent-b")
        self.assertEqual(event["delivered_to"], ["agent-a"])
        self.assertEqual(event["mentions"], ["agent-a"])
        self.assertEqual(event["intent"], "ack")
        self.assertEqual(event["thread"], "THREAD-1")
        self.assertEqual(event["reply_to"], "41")
        self.assertEqual(event["reply_to_local"], 41)
        self.assertTrue(all(event["coverage"]["field_presence"].values()))

    def test_probe_unknown_when_no_message_can_prove_fields(self):
        self._env("HCOM_LINEAGE_EMPTY")
        capability = self.adapter.probe_lineage_capability(last=10)
        self.assertEqual(capability.state, "UNKNOWN")
        self.assertFalse(capability.core_fields_verified)
        self.assertEqual(capability.observed_message_events, 0)
        self.assertEqual(capability.observed_optional_fields, ())

    def test_probe_reports_only_optional_fields_actually_observed(self):
        capability = self.adapter.probe_lineage_capability(last=10)
        self.assertEqual(capability.state, "SUPPORTED")
        self.assertTrue(capability.core_fields_verified)
        self.assertEqual(capability.observed_message_events, 2)
        self.assertEqual(
            capability.observed_optional_fields,
            ("intent", "mentions", "reply_to", "reply_to_local", "thread"),
        )
        payload = capability.to_dict()
        self.assertEqual(payload["state"], "SUPPORTED")

    def test_duplicate_provider_local_event_identity_fails_closed(self):
        self._env("HCOM_LINEAGE_DUPLICATE_IDENTITY")
        with self.assertRaisesRegex(
            HcomLineageProtocolError,
            "duplicate provider-local event identity",
        ):
            self.adapter.read_message_lineage()
        with self.assertRaisesRegex(
            HcomLineageProtocolError,
            "duplicate provider-local event identity",
        ):
            self.adapter.probe_lineage_capability()

    def test_missing_core_delivery_metadata_fails_closed(self):
        self._env("HCOM_LINEAGE_MISSING_CORE")
        with self.assertRaises(HcomLineageProtocolError):
            self.adapter.read_message_lineage()

    def test_invalid_full_event_json_fails_closed(self):
        self._env("HCOM_LINEAGE_BAD_JSON")
        with self.assertRaises(HcomLineageProtocolError):
            self.adapter.read_message_lineage()

    def test_unsupported_structured_intent_fails_closed(self):
        self._env("HCOM_LINEAGE_BAD_INTENT")
        with self.assertRaises(HcomLineageProtocolError):
            self.adapter.read_message_lineage()

    def test_invalid_filter_values_fail_before_subprocess(self):
        with self.assertRaises(ValueError):
            self.adapter.read_message_lineage(intent="approve")
        with self.assertRaises(ValueError):
            self.adapter.read_message_lineage(agent="bad name")
        with self.assertRaises(ValueError):
            self.adapter.read_message_lineage(thread="bad thread")
        self.assertEqual(self.calls(), [])

    def test_source_has_no_task_store_or_authority_dependency(self):
        source = (
            Path(__file__).parents[1]
            / "runtime"
            / "communication"
            / "hcom_lineage.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("runtime.state", source)
        self.assertNotIn("TaskStore", source)
        self.assertNotIn("maps.db", source)
        self.assertNotIn("ownership", source.lower())
        self.assertNotIn("approval", source.lower())


if __name__ == "__main__":
    unittest.main()
