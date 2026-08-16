from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from .hcom_adapter import HcomAdapter, HcomProtocolError, VALID_INTENTS


class HcomLineageProtocolError(HcomProtocolError):
    pass


@dataclass(frozen=True)
class HcomLineageCapability:
    state: str
    reason: str
    observed_message_events: int
    required_fields_verified: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state,
            "reason": self.reason,
            "observed_message_events": self.observed_message_events,
            "required_fields_verified": self.required_fields_verified,
        }


class HcomLineageAdapter(HcomAdapter):
    """Read-only full-fidelity hcom message metadata for lineage correlation.

    This subclass intentionally leaves ordinary HcomAdapter.read_events() unchanged.
    It requests hcom's explicit --full event view and projects only structured
    correlation metadata; message text is not copied into the lineage result.
    """

    def read_message_lineage(
        self,
        *,
        last: int = 100,
        intent: str | None = None,
        agent: str | None = None,
        thread: str | None = None,
    ) -> list[dict[str, Any]]:
        if last < 1 or last > 5000:
            raise ValueError("last must be between 1 and 5000")
        args = ["events", "--last", str(last), "--full", "--type", "message"]
        if intent:
            normalized = intent.strip().lower()
            if normalized not in VALID_INTENTS:
                raise ValueError("intent must be request, inform, or ack")
            args.extend(("--intent", normalized))
        if agent:
            args.extend(("--agent", self._validate_name(agent, "agent")))
        if thread:
            args.extend(("--thread", self._validate_name(thread, "thread")))

        result = self._run(args)
        events = self._parse_json_lines(result.stdout)
        return [self._project_message(event) for event in events]

    def probe_lineage_capability(self, *, last: int = 25) -> HcomLineageCapability:
        """Probe the configured hcom boundary without trusting its version string.

        A successful command with no message records proves --full is accepted but
        cannot prove the required message metadata shape, so capability remains
        UNKNOWN until at least one full message event is observed and validates.
        """

        if last < 1 or last > 5000:
            raise ValueError("last must be between 1 and 5000")
        result = self._run(
            ("events", "--last", str(last), "--full", "--type", "message")
        )
        events = self._parse_json_lines(result.stdout)
        if not events:
            return HcomLineageCapability(
                state="UNKNOWN",
                reason=(
                    "hcom accepted the full-fidelity read but no message event was "
                    "available to prove required lineage fields"
                ),
                observed_message_events=0,
                required_fields_verified=False,
            )

        for event in events:
            self._project_message(event)
        return HcomLineageCapability(
            state="SUPPORTED",
            reason=(
                "full message events exposed stable event identity and the required "
                "structured lineage metadata"
            ),
            observed_message_events=len(events),
            required_fields_verified=True,
        )

    @staticmethod
    def _parse_json_lines(stdout: str) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise HcomLineageProtocolError(
                    "hcom events --full returned a non-JSON record"
                ) from exc
            if not isinstance(event, dict):
                raise HcomLineageProtocolError(
                    "hcom events --full record was not an object"
                )
            events.append(event)
        return events

    @classmethod
    def _project_message(cls, event: dict[str, Any]) -> dict[str, Any]:
        if event.get("type") != "message":
            raise HcomLineageProtocolError(
                "full lineage query returned a non-message event"
            )
        event_id = event.get("id")
        if isinstance(event_id, bool) or not isinstance(event_id, int) or event_id < 1:
            raise HcomLineageProtocolError(
                "full message event is missing a positive integer event id"
            )
        timestamp = event.get("ts")
        if not isinstance(timestamp, str) or not timestamp.strip():
            raise HcomLineageProtocolError(
                "full message event is missing timestamp metadata"
            )
        instance = event.get("instance")
        if not isinstance(instance, str) or not instance.strip():
            raise HcomLineageProtocolError(
                "full message event is missing instance metadata"
            )
        data = event.get("data")
        if not isinstance(data, dict):
            raise HcomLineageProtocolError(
                "full message event data is not an object"
            )

        required_keys = {
            "from",
            "delivered_to",
            "mentions",
            "intent",
            "thread",
            "reply_to",
            "reply_to_local",
        }
        missing = sorted(required_keys - set(data))
        if missing:
            raise HcomLineageProtocolError(
                "full message event is missing required lineage fields: "
                + ", ".join(missing)
            )

        sender = cls._required_text(data.get("from"), "from")
        intent = cls._required_text(data.get("intent"), "intent").lower()
        if intent not in VALID_INTENTS:
            raise HcomLineageProtocolError(
                f"full message event has unsupported intent: {intent!r}"
            )

        delivered_to = cls._text_list(data.get("delivered_to"), "delivered_to")
        mentions = cls._text_list(data.get("mentions"), "mentions")
        thread = cls._optional_text(data.get("thread"), "thread")
        reply_to = cls._optional_scalar(data.get("reply_to"), "reply_to")
        reply_to_local = cls._optional_positive_int(
            data.get("reply_to_local"), "reply_to_local"
        )

        return {
            "event_id": event_id,
            "timestamp": timestamp,
            "instance": instance,
            "sender": sender,
            "delivered_to": delivered_to,
            "mentions": mentions,
            "intent": intent,
            "thread": thread,
            "reply_to": reply_to,
            "reply_to_local": reply_to_local,
            "coverage": {
                "source": "hcom events --full",
                "full_fidelity": True,
                "message_body_included": False,
            },
        }

    @staticmethod
    def _required_text(value: object, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise HcomLineageProtocolError(
                f"full message event field {field} must be non-empty text"
            )
        return value.strip()

    @staticmethod
    def _optional_text(value: object, field: str) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise HcomLineageProtocolError(
                f"full message event field {field} must be text or null"
            )
        value = value.strip()
        return value or None

    @staticmethod
    def _text_list(value: object, field: str) -> list[str]:
        if not isinstance(value, list):
            raise HcomLineageProtocolError(
                f"full message event field {field} must be a list"
            )
        output: list[str] = []
        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise HcomLineageProtocolError(
                    f"full message event field {field} contains invalid identity"
                )
            normalized = item.strip()
            if normalized not in output:
                output.append(normalized)
        return output

    @staticmethod
    def _optional_scalar(value: object, field: str) -> int | str | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, (int, str)):
            raise HcomLineageProtocolError(
                f"full message event field {field} must be integer/text/null"
            )
        if isinstance(value, int):
            if value < 1:
                raise HcomLineageProtocolError(
                    f"full message event field {field} integer must be positive"
                )
            return value
        value = value.strip()
        if not value:
            return None
        return value

    @staticmethod
    def _optional_positive_int(value: object, field: str) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise HcomLineageProtocolError(
                f"full message event field {field} must be positive integer/null"
            )
        return value
