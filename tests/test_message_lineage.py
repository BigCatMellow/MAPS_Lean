from __future__ import annotations

import copy
import json
import unittest

from runtime.communication.message_lineage import (
    MessageLineageError,
    resolve_message_relationships,
)


class MessageRelationshipTests(unittest.TestCase):
    @staticmethod
    def _event(
        event_id: int,
        *,
        sender: str,
        delivered_to: list[str],
        intent: str | None = None,
        thread: str | None = None,
        reply_to_local: int | None = None,
    ) -> dict:
        return {
            "event_id": event_id,
            "timestamp": f"2026-08-15T20:00:{event_id % 60:02d}.000000",
            "instance": sender,
            "sender": sender,
            "delivered_to": delivered_to,
            "mentions": delivered_to if delivered_to else None,
            "intent": intent,
            "thread": thread,
            "reply_to": str(reply_to_local) if reply_to_local is not None else None,
            "reply_to_local": reply_to_local,
            "coverage": {
                "source": "hcom events --full",
                "full_fidelity_read": True,
                "message_body_included": False,
                "field_presence": {
                    "mentions": bool(delivered_to),
                    "intent": intent is not None,
                    "thread": thread is not None,
                    "reply_to": reply_to_local is not None,
                    "reply_to_local": reply_to_local is not None,
                },
            },
        }

    @staticmethod
    def _request(projection: dict, event_id: int) -> dict:
        return next(
            item
            for item in projection["requests"]
            if item["request_event_id"] == event_id
        )

    def test_exact_reply_and_ack_are_linked_by_reply_to_local(self):
        request = self._event(
            41,
            sender="agent-a",
            delivered_to=["agent-b"],
            intent="request",
            thread="THREAD-1",
        )
        ack = self._event(
            42,
            sender="agent-b",
            delivered_to=["agent-a"],
            intent="ack",
            thread="THREAD-1",
            reply_to_local=41,
        )
        projection = resolve_message_relationships([request, ack])

        self.assertEqual(
            projection["reply_links"],
            [
                {
                    "child_event_id": 42,
                    "parent_event_id": 41,
                    "parent_state": "IN_INPUT",
                    "child_intent": "ack",
                }
            ],
        )
        req = self._request(projection, 41)
        self.assertEqual(req["response_event_ids"], [42])
        self.assertEqual(req["ack_event_ids"], [42])
        self.assertEqual(req["response_observation"], "OBSERVED_IN_INPUT")
        self.assertEqual(req["ack_observation"], "OBSERVED_IN_INPUT")

    def test_same_thread_without_reply_does_not_infer_response(self):
        request = self._event(
            50,
            sender="agent-a",
            delivered_to=["agent-b"],
            intent="request",
            thread="THREAD-X",
        )
        unrelated = self._event(
            51,
            sender="agent-b",
            delivered_to=["agent-a"],
            intent="inform",
            thread="THREAD-X",
        )
        projection = resolve_message_relationships([request, unrelated])
        req = self._request(projection, 50)
        self.assertEqual(req["response_event_ids"], [])
        self.assertEqual(req["ack_event_ids"], [])
        self.assertEqual(req["response_observation"], "NOT_OBSERVED_IN_INPUT")
        self.assertTrue(projection["coverage"]["thread_grouping_is_not_reply_inference"])

    def test_absence_in_bounded_input_is_not_a_pending_or_wait_claim(self):
        request = self._event(
            60,
            sender="agent-a",
            delivered_to=["agent-b"],
            intent="request",
        )
        projection = resolve_message_relationships([request])
        req = self._request(projection, 60)
        self.assertEqual(req["ack_observation"], "NOT_OBSERVED_IN_INPUT")
        self.assertTrue(projection["coverage"]["absence_is_not_global_negative"])
        self.assertFalse(projection["coverage"]["wait_state_included"])
        serialized = json.dumps(projection).lower()
        self.assertNotIn('"pending"', serialized)
        self.assertNotIn('"waiting"', serialized)

    def test_reply_parent_outside_input_is_preserved_not_guessed(self):
        reply = self._event(
            71,
            sender="agent-b",
            delivered_to=["agent-a"],
            intent="ack",
            reply_to_local=12,
        )
        projection = resolve_message_relationships([reply])
        self.assertEqual(
            projection["reply_links"][0]["parent_state"],
            "PARENT_NOT_IN_INPUT",
        )
        self.assertEqual(projection["requests"], [])

    def test_delivery_edges_preserve_exact_sender_recipient_fanout(self):
        event = self._event(
            80,
            sender="agent-a",
            delivered_to=["agent-b", "agent-c"],
            intent="inform",
        )
        projection = resolve_message_relationships([event])
        self.assertEqual(
            projection["delivery_edges"],
            [
                {"event_id": 80, "sender": "agent-a", "recipient": "agent-b"},
                {"event_id": 80, "sender": "agent-a", "recipient": "agent-c"},
            ],
        )

    def test_thread_groups_use_only_explicit_thread_metadata(self):
        threaded_a = self._event(
            90,
            sender="agent-a",
            delivered_to=["agent-b"],
            thread="THREAD-A",
        )
        unthreaded = self._event(
            91,
            sender="agent-b",
            delivered_to=["agent-a"],
        )
        threaded_b = self._event(
            92,
            sender="agent-b",
            delivered_to=["agent-a"],
            thread="THREAD-A",
        )
        projection = resolve_message_relationships(
            [threaded_b, unthreaded, threaded_a]
        )
        self.assertEqual(
            projection["threads"],
            [{"thread": "THREAD-A", "event_ids": [90, 92]}],
        )

    def test_input_order_does_not_change_projection(self):
        a = self._event(
            101,
            sender="agent-a",
            delivered_to=["agent-b"],
            intent="request",
        )
        b = self._event(
            102,
            sender="agent-b",
            delivered_to=["agent-a"],
            intent="ack",
            reply_to_local=101,
        )
        self.assertEqual(
            resolve_message_relationships([a, b]),
            resolve_message_relationships([b, a]),
        )

    def test_duplicate_event_id_fails_closed(self):
        a = self._event(110, sender="agent-a", delivered_to=["agent-b"])
        b = copy.deepcopy(a)
        b["sender"] = "agent-c"
        with self.assertRaises(MessageLineageError):
            resolve_message_relationships([a, b])

    def test_self_reply_fails_closed(self):
        event = self._event(
            120,
            sender="agent-a",
            delivered_to=["agent-b"],
            intent="ack",
            reply_to_local=120,
        )
        with self.assertRaises(MessageLineageError):
            resolve_message_relationships([event])

    def test_invalid_intent_fails_closed(self):
        event = self._event(
            130,
            sender="agent-a",
            delivered_to=["agent-b"],
            intent="approve",
        )
        with self.assertRaises(MessageLineageError):
            resolve_message_relationships([event])

    def test_non_full_or_body_including_input_is_rejected(self):
        event = self._event(140, sender="agent-a", delivered_to=["agent-b"])
        event["coverage"]["full_fidelity_read"] = False
        with self.assertRaises(MessageLineageError):
            resolve_message_relationships([event])

        event = self._event(141, sender="agent-a", delivered_to=["agent-b"])
        event["coverage"]["message_body_included"] = True
        with self.assertRaises(MessageLineageError):
            resolve_message_relationships([event])

    def test_projection_is_explicitly_non_authoritative(self):
        event = self._event(150, sender="agent-a", delivered_to=["agent-b"])
        projection = resolve_message_relationships([event])
        self.assertFalse(projection["authority"]["can_grant_task_authority"])
        self.assertFalse(projection["authority"]["can_grant_session_authority"])
        self.assertFalse(projection["authority"]["can_grant_review_or_approval"])
        self.assertFalse(projection["coverage"]["task_run_correlation_included"])


if __name__ == "__main__":
    unittest.main()
