from __future__ import annotations

from collections import defaultdict
from typing import Mapping, Sequence

from .hcom_adapter import VALID_INTENTS


class MessageLineageError(ValueError):
    pass


_OPTIONAL_CORRELATION_FIELDS = (
    "mentions",
    "intent",
    "thread",
    "reply_to",
    "reply_to_local",
)
_REQUIRED_EVENT_KEYS = {
    "event_id",
    "timestamp",
    "instance",
    "sender",
    "delivered_to",
    *_OPTIONAL_CORRELATION_FIELDS,
    "coverage",
}


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MessageLineageError(f"{field} must be non-empty text")
    return value.strip()


def _text_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list):
        raise MessageLineageError(f"{field} must be a list")
    output = []
    for item in value:
        normalized = _text(item, field)
        if normalized not in output:
            output.append(normalized)
    return output


def _optional_text(value: object, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise MessageLineageError(f"{field} must be text or null")
    value = value.strip()
    return value or None


def _optional_scalar(value: object, field: str) -> int | str | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise MessageLineageError(f"{field} must be integer/text/null")
    if isinstance(value, int):
        if value < 1:
            raise MessageLineageError(f"{field} integer must be positive")
        return value
    value = value.strip()
    return value or None


def _field_presence(coverage: Mapping[str, object]) -> dict[str, bool]:
    raw_presence = coverage.get("field_presence")
    if not isinstance(raw_presence, Mapping):
        raise MessageLineageError("coverage.field_presence must be a mapping")
    if set(raw_presence) != set(_OPTIONAL_CORRELATION_FIELDS):
        missing = sorted(set(_OPTIONAL_CORRELATION_FIELDS) - set(raw_presence))
        extra = sorted(set(raw_presence) - set(_OPTIONAL_CORRELATION_FIELDS))
        raise MessageLineageError(
            "coverage.field_presence shape mismatch; "
            f"missing={missing} extra={extra}"
        )
    presence: dict[str, bool] = {}
    for field in _OPTIONAL_CORRELATION_FIELDS:
        value = raw_presence[field]
        if not isinstance(value, bool):
            raise MessageLineageError(
                f"coverage.field_presence.{field} must be boolean"
            )
        presence[field] = value
    return presence


def _normalize_event(raw: Mapping[str, object]) -> dict[str, object]:
    if set(raw) != _REQUIRED_EVENT_KEYS:
        missing = sorted(_REQUIRED_EVENT_KEYS - set(raw))
        extra = sorted(set(raw) - _REQUIRED_EVENT_KEYS)
        raise MessageLineageError(
            f"message lineage event shape mismatch; missing={missing} extra={extra}"
        )

    event_id = raw.get("event_id")
    if isinstance(event_id, bool) or not isinstance(event_id, int) or event_id < 1:
        raise MessageLineageError("event_id must be a positive integer")

    coverage = raw.get("coverage")
    if not isinstance(coverage, Mapping):
        raise MessageLineageError("coverage must be a mapping")
    if coverage.get("message_body_included") is not False:
        raise MessageLineageError(
            "message relationship input must preserve the body-free lineage boundary"
        )
    if coverage.get("full_fidelity_read") is not True:
        raise MessageLineageError(
            "message relationship input must come from a full-fidelity lineage read"
        )
    presence = _field_presence(coverage)

    for field in _OPTIONAL_CORRELATION_FIELDS:
        if not presence[field] and raw.get(field) is not None:
            raise MessageLineageError(
                f"{field} has a value but coverage.field_presence marks it absent"
            )

    mentions = raw.get("mentions")
    if presence["mentions"]:
        mentions = _text_list(mentions, "mentions")
    else:
        mentions = None

    intent = raw.get("intent")
    if presence["intent"]:
        intent = _text(intent, "intent").lower()
        if intent not in VALID_INTENTS:
            raise MessageLineageError(f"unsupported intent: {intent!r}")
    else:
        intent = None

    thread = (
        _optional_text(raw.get("thread"), "thread")
        if presence["thread"]
        else None
    )
    reply_to = (
        _optional_scalar(raw.get("reply_to"), "reply_to")
        if presence["reply_to"]
        else None
    )

    reply_to_local = raw.get("reply_to_local") if presence["reply_to_local"] else None
    if reply_to_local is not None and (
        isinstance(reply_to_local, bool)
        or not isinstance(reply_to_local, int)
        or reply_to_local < 1
    ):
        raise MessageLineageError("reply_to_local must be a positive integer or null")
    if reply_to_local == event_id:
        raise MessageLineageError("a message event cannot reply to itself")

    return {
        "event_id": event_id,
        "timestamp": _text(raw.get("timestamp"), "timestamp"),
        "instance": _text(raw.get("instance"), "instance"),
        "sender": _text(raw.get("sender"), "sender"),
        "delivered_to": _text_list(raw.get("delivered_to"), "delivered_to"),
        "mentions": mentions,
        "intent": intent,
        "thread": thread,
        "reply_to": reply_to,
        "reply_to_local": reply_to_local,
    }


def resolve_message_relationships(
    events: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Resolve exact provider-local message relationships from bounded input.

    Only explicit hcom metadata is used. Thread membership does not imply a reply,
    and absence of a reply/ack in the bounded input does not imply a global
    unanswered/pending state.
    """

    normalized = [_normalize_event(event) for event in events]
    ids = [int(event["event_id"]) for event in normalized]
    if len(ids) != len(set(ids)):
        raise MessageLineageError("duplicate event_id in message relationship input")

    ordered = sorted(normalized, key=lambda item: int(item["event_id"]))
    by_id = {int(item["event_id"]): item for item in ordered}

    reply_links = []
    children_by_parent: dict[int, list[dict[str, object]]] = defaultdict(list)
    delivery_edges = []
    thread_events: dict[str, list[int]] = defaultdict(list)

    for event in ordered:
        event_id = int(event["event_id"])
        for recipient in event["delivered_to"]:
            delivery_edges.append(
                {
                    "event_id": event_id,
                    "sender": event["sender"],
                    "recipient": recipient,
                }
            )

        thread = event["thread"]
        if isinstance(thread, str):
            thread_events[thread].append(event_id)

        parent_id = event["reply_to_local"]
        if isinstance(parent_id, int):
            parent_state = "IN_INPUT" if parent_id in by_id else "PARENT_NOT_IN_INPUT"
            link = {
                "child_event_id": event_id,
                "parent_event_id": parent_id,
                "parent_state": parent_state,
                "child_intent": event["intent"],
            }
            reply_links.append(link)
            if parent_state == "IN_INPUT":
                children_by_parent[parent_id].append(event)

    requests = []
    for event in ordered:
        if event["intent"] != "request":
            continue
        event_id = int(event["event_id"])
        children = sorted(
            children_by_parent.get(event_id, []),
            key=lambda item: int(item["event_id"]),
        )
        response_ids = [int(item["event_id"]) for item in children]
        ack_ids = [
            int(item["event_id"])
            for item in children
            if item["intent"] == "ack"
        ]
        requests.append(
            {
                "request_event_id": event_id,
                "thread": event["thread"],
                "delivered_to": list(event["delivered_to"]),
                "response_event_ids": response_ids,
                "ack_event_ids": ack_ids,
                "response_observation": (
                    "OBSERVED_IN_INPUT" if response_ids else "NOT_OBSERVED_IN_INPUT"
                ),
                "ack_observation": (
                    "OBSERVED_IN_INPUT" if ack_ids else "NOT_OBSERVED_IN_INPUT"
                ),
            }
        )

    threads = [
        {"thread": thread, "event_ids": sorted(event_ids)}
        for thread, event_ids in sorted(thread_events.items())
    ]

    return {
        "projection_version": 1,
        "projection_kind": "HCOM_MESSAGE_RELATIONSHIPS",
        "events": [
            {
                "event_id": event["event_id"],
                "sender": event["sender"],
                "delivered_to": list(event["delivered_to"]),
                "intent": event["intent"],
                "thread": event["thread"],
                "reply_to_local": event["reply_to_local"],
            }
            for event in ordered
        ],
        "delivery_edges": delivery_edges,
        "reply_links": sorted(
            reply_links,
            key=lambda item: (item["child_event_id"], item["parent_event_id"]),
        ),
        "threads": threads,
        "requests": requests,
        "coverage": {
            "bounded_input": True,
            "input_event_count": len(ordered),
            "reply_links_exact_only": True,
            "thread_grouping_is_not_reply_inference": True,
            "absence_is_not_global_negative": True,
            "message_body_included": False,
            "task_run_correlation_included": False,
            "wait_state_included": False,
        },
        "authority": {
            "kind": "DERIVED_COMMUNICATION_EVIDENCE",
            "can_grant_task_authority": False,
            "can_grant_session_authority": False,
            "can_grant_review_or_approval": False,
        },
    }
