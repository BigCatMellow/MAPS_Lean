from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any

from .hcom_adapter import HcomAdapter, HcomProtocolError, VALID_INTENTS


class HcomLineageProtocolError(HcomProtocolError):
    pass


_OPTIONAL_CORRELATION_FIELDS = (
    "mentions",
    "intent",
    "thread",
    "reply_to",
    "reply_to_local",
)


@dataclass(frozen=True)
class HcomLineageCapability:
    state: str
    reason: str
    observed_message_events: int
    core_fields_verified: bool
    observed_optional_fields: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class HcomLineageAdapter(HcomAdapter):
    """Read-only full-fidelity hcom message metadata for lineage correlation.

    Ordinary ``HcomAdapter.read_events()`` stays lightweight. This path requests
    hcom's explicit ``--full`` event representation and projects only structured
    correlation metadata; message bodies are deliberately omitted.
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
        projected = [self._project_message(event) for event in events]
        self._require_unique_event_identities(projected)
        return projected

    def probe_lineage_capability(self, *, last: int = 25) -> HcomLineageCapability:
        """Probe the configured hcom boundary without trusting a version string.

        A successful command with no message rows proves only that the CLI accepts
        the full-fidelity query; field capability remains UNKNOWN. With message
        rows, stable event identity plus sender/delivery metadata are verified.
        Optional thread/reply/intent fields are reported only when actually
        observed; their absence is never reinterpreted as a default value.
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
                    "available to prove lineage metadata"
                ),
                observed_message_events=0,
                core_fields_verified=False,
                observed_optional_fields=(),
            )

        projected = [self._project_message(event) for event in events]
        self._require_unique_event_identities(projected)
        observed = sorted(
            {
                field
                for item in projected
                for field, present in item["coverage"]["field_presence"].items()
                if present
            }
        )
        return HcomLineageCapability(
            state="SUPPORTED",
            reason=(
                "full message events proved stable event identity, sender, and "
                "delivery metadata; optional correlation fields are verified only "
                "where observed"
            ),
            observed_message_events=len(projected),
            core_fields_verified=True,
            observed_optional_fields=tuple(observed),
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

    @staticmethod
    def _require_unique_event_identities(events: list[dict[str, Any]]) -> None:
        """Fail closed when one provider-local identity names multiple rows.

        ``event_id`` is local evidence at the configured hcom boundary. The
        projection also preserves the event ``instance``; together they form the
        narrow identity this read path can mechanically validate. This does not
        claim global identity across projects/providers.
        """

        seen: set[tuple[str, int]] = set()
        for event in events:
            identity = (event["instance"], event["event_id"])
            if identity in seen:
                raise HcomLineageProtocolError(
                    "hcom events --full returned duplicate provider-local event identity"
                )
            seen.add(identity)

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
            raise HcomLineageProtocolError("full message event data is not an object")

        missing_core = sorted({"from", "delivered_to"} - set(data))
        if missing_core:
            raise HcomLineageProtocolError(
                "full message event is missing required lineage fields: "
                + ", ".join(missing_core)
            )

        sender = cls._required_text(data.get("from"), "from")
        delivered_to = cls._text_list(data.get("delivered_to"), "delivered_to")

        presence = {field: field in data for field in _OPTIONAL_CORRELATION_FIELDS}
        mentions = (
            cls._text_list(data.get("mentions"), "mentions")
            if presence["mentions"]
            else None
        )
        intent = None
        if presence["intent"]:
            intent = cls._required_text(data.get("intent"), "intent").lower()
            if intent not in VALID_INTENTS:
                raise HcomLineageProtocolError(
                    f"full message event has unsupported intent: {intent!r}"
                )
        thread = (
            cls._optional_text(data.get("thread"), "thread")
            if presence["thread"]
            else None
        )
        reply_to = (
            cls._optional_scalar(data.get("reply_to"), "reply_to")
            if presence["reply_to"]
            else None
        )
        reply_to_local = (
            cls._optional_positive_int(data.get("reply_to_local"), "reply_to_local")
            if presence["reply_to_local"]
            else None
        )

        return {
            "event_id": event_id,
            "timestamp": timestamp.strip(),
            "instance": instance.strip(),
            "sender": sender,
            "delivered_to": delivered_to,
            "mentions": mentions,
            "intent": intent,
            "thread": thread,
            "reply_to": reply_to,
            "reply_to_local": reply_to_local,
            "coverage": {
                "source": "hcom events --full",
                "full_fidelity_read": True,
                "message_body_included": False,
                "field_presence": presence,
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
        return value or None

    @staticmethod
    def _optional_positive_int(value: object, field: str) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise HcomLineageProtocolError(
                f"full message event field {field} must be positive integer/null"
            )
        return value
