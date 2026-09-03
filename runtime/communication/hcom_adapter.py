from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import logging
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable

_LOGGER = logging.getLogger(__name__)

_NAME = re.compile(r"^[A-Za-z0-9_.:@-]+$")
_TOOL = re.compile(r"^[A-Za-z0-9_-]+$")
VALID_INTENTS = {"request", "inform", "ack"}

# Lookback for the `hcom events`-derived stopped-session reconstruction that
# `list_sessions(include_stopped=True)` falls back to when an hcom build does not
# honor `--json` for `list --stopped` (hcom 0.7.25 -- see `list_sessions`). Sized
# from the Step-0 probe: a busy 3-agent coordinator emitted ~300 events/hour
# aggregate, the vast majority `status` events (each top-level session stamps its
# own `session_id` on every prompt/listening/tool transition). 2000 events is
# ~6h of that history -- comfortably longer than any plausible recovery
# inter-tick gap plus the silent-stop probe delay, and well under
# `read_events`'s hard cap of 5000. A session that both started and stopped
# entirely outside this window yields a synthetic record with no `session_id`
# (see `_stopped_records_from_events`), i.e. the same unresolved-`run_id`
# degradation Part A already accepts, just over a much smaller exposure window.
_STOPPED_EVENTS_LOOKBACK = 2000

# hcom `data.new_status` value for a session/agent that has exited.
_STOPPED_STATUS_VALUES = {"inactive", "stopped"}


class HcomError(RuntimeError):
    pass


class HcomCommandError(HcomError):
    def __init__(self, result: "HcomCommandResult"):
        super().__init__(
            f"hcom command failed ({result.returncode}): {' '.join(result.argv)}: "
            f"{result.stderr.strip()}"
        )
        self.result = result


class HcomProtocolError(HcomError):
    pass


@dataclass(frozen=True)
class HcomCommandResult:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"ok": self.ok}


class HcomAdapter:
    """Narrow adapter around hcom's CLI.

    This module intentionally has no dependency on the MAPS task store. hcom
    provides communication/session facts and side effects; it never grants task
    ownership, completion, review, approval, or scope authority.
    """

    def __init__(
        self,
        *,
        hcom_dir: str | Path = ".hcom",
        executable: str | Path = "hcom",
        timeout_seconds: float = 30.0,
    ):
        self.hcom_dir = Path(hcom_dir).resolve()
        self.executable = str(executable)
        self.timeout_seconds = float(timeout_seconds)
        self._warned_stopped_nonjson = False

    def environment(self) -> dict[str, str]:
        env = os.environ.copy()
        env["HCOM_DIR"] = str(self.hcom_dir)
        return env

    def _run(
        self,
        args: Iterable[str],
        *,
        input_text: str | None = None,
        timeout_seconds: float | None = None,
        check: bool = True,
    ) -> HcomCommandResult:
        argv = (self.executable, *tuple(str(arg) for arg in args))
        try:
            completed = subprocess.run(
                argv,
                input=input_text,
                text=True,
                capture_output=True,
                shell=False,
                env=self.environment(),
                timeout=timeout_seconds or self.timeout_seconds,
                check=False,
            )
        except FileNotFoundError as exc:
            raise HcomError(f"hcom executable not found: {self.executable}") from exc
        except subprocess.TimeoutExpired as exc:
            raise HcomError(f"hcom command timed out: {' '.join(argv)}") from exc

        result = HcomCommandResult(
            argv=argv,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        if check and not result.ok:
            raise HcomCommandError(result)
        return result

    @staticmethod
    def _validate_name(value: str, label: str = "name") -> str:
        value = value.strip()
        if not value or not _NAME.fullmatch(value):
            raise ValueError(f"invalid hcom {label}: {value!r}")
        return value

    @staticmethod
    def _validate_tool(value: str) -> str:
        value = value.strip()
        if not value or not _TOOL.fullmatch(value):
            raise ValueError(f"invalid hcom tool: {value!r}")
        return value

    def version(self) -> HcomCommandResult:
        return self._run(("--version",))

    def status(self) -> HcomCommandResult:
        return self._run(("status",))

    @staticmethod
    def _parse_session_list(stdout: str) -> list[dict[str, Any]]:
        try:
            payload = json.loads(stdout or "[]")
        except json.JSONDecodeError as exc:
            raise HcomProtocolError("hcom list --json returned invalid JSON") from exc
        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise HcomProtocolError("hcom list --json did not return a JSON array of objects")
        return payload

    def list_sessions(self, *, include_stopped: bool = False) -> list[dict[str, Any]]:
        args = ["list", "--json"]
        if include_stopped:
            args.extend(("--stopped", "--all"))
        result = self._run(args)
        if include_stopped:
            try:
                json.loads(result.stdout or "[]")
            except json.JSONDecodeError:
                # hcom does not honor `--json` for `list --stopped` -- confirmed
                # hcom 0.7.25, where `--json` is documented only for the
                # alive-only and single-agent forms and `--stopped` always emits
                # human-formatted text ("No recently stopped agents (last 60m)"
                # / "Stopped agents (all, showing N): ..."). Aborting here made
                # `maps recovery-tick` unable to reach the supervisor at all
                # (RecoverySupervisor.observe_silent_stops / tick both call this
                # unconditionally). Degrade to the contractual alive-only
                # listing: a stopped session then reads as absent, and
                # session_is_live({}) is already False, so silent-stop
                # *detection* is preserved.
                #
                # The catch is deliberately narrowed to JSONDecodeError (the
                # non-JSON human-text case). A structurally valid JSON payload
                # that fails `_parse_session_list`'s type check -- e.g. a
                # hypothetically `--json`-honoring hcom emitting a malformed
                # typed array -- still raises, surfacing that bug rather than
                # masking it behind the fallback.
                if not self._warned_stopped_nonjson:
                    _LOGGER.warning(
                        "hcom `list --stopped` returned non-JSON output; "
                        "reconstructing stopped-session records from the `hcom "
                        "events` stream (option C) and merging them under the "
                        "alive-only list. Stopped sessions that started and "
                        "stopped outside the events lookback window may still "
                        "open incidents with an unresolved run_id. See "
                        "work/notes/2026-09-03-hcom-list-stopped-nonjson-repair.md "
                        "and work/notes/2026-09-03-item5-optionC-impl.md."
                    )
                    self._warned_stopped_nonjson = True
                fallback = self._run(["list", "--json"])
                alive = self._parse_session_list(fallback.stdout)
                # Part B (option C): rebuild the stopped-session records this
                # build cannot give us as JSON from the contractual
                # `hcom events` stream, and merge them under the alive list so
                # the `session_id -> run_id` reverse lookup
                # (RecoverySupervisor._resolve_run_id) and
                # HcomSessionAdapter._find_by_session_id keep working for
                # silent-stop incidents. `hcom list --stopped` is itself
                # documented as "from events", so this is the same source, just
                # read structurally. Never raises -- a failure here degrades to
                # the Part A alive-only behavior.
                # work/notes/2026-09-03-item5-optionC-impl.md
                alive_names = {str(item.get("name") or "") for item in alive}
                return alive + [
                    record
                    for record in self._stopped_records_from_events()
                    if str(record.get("name") or "") not in alive_names
                ]
        return self._parse_session_list(result.stdout)

    def _stopped_records_from_events(self) -> list[dict[str, Any]]:
        """Synthesize stopped-session records from the `hcom events` stream.

        Only used as the `list_sessions(include_stopped=True)` fallback on an
        hcom build that ignores `--json` for `list --stopped`. On a build that
        honors it, the JSONDecodeError branch is never entered and this is
        defense-in-depth only.

        A record is emitted for every agent `name` that has a stop signal in
        the last ``_STOPPED_EVENTS_LOOKBACK`` events -- a `life` event with
        ``data.action == "stopped"`` or a `status` event whose
        ``data.new_status`` is inactive/stopped. Its ``session_id`` is taken
        from the most recent `status` event for that name carrying a non-null
        ``data.session`` (top-level sessions stamp this on every transition;
        subagent events carry only ``agent_id`` and are irrelevant to recovery,
        which binds worker -> top-level session). If no such event is in the
        window the record still lists the name but omits ``session_id`` -- the
        caller drops names already alive, and downstream `run_id` resolution
        then returns None exactly as in the Part A degradation.

        Shape mirrors the alive `hcom list --json` keys the recovery path reads
        (`name`, `session_id`, `status`, `process_bound`, `status_context`)
        plus namespaced advisory extras (`stopped`, `stop_reason`, `stop_ts`).
        """
        try:
            events = self.read_events(last=_STOPPED_EVENTS_LOOKBACK)
        except HcomError as exc:
            _LOGGER.warning(
                "hcom events-derived stopped-session reconstruction failed (%s); "
                "degrading to the alive-only listing.",
                exc,
            )
            return []

        session_by_name: dict[str, str] = {}
        stop_by_name: dict[str, dict[str, Any]] = {}
        # Names whose stop event explicitly carried `session: null` (+ an
        # `agent_id`) -- the hcom shape for a subagent `exit:idle`. Recovery
        # binds worker -> top-level session, never a subagent, so these are
        # dropped unless a real top-level `session` id was also seen for the
        # name.
        subagent_only: set[str] = set()
        for event in events:
            if not isinstance(event, dict):
                continue
            name = str(event.get("instance") or "").strip()
            if not name:
                continue
            data = event.get("data")
            if not isinstance(data, dict):
                data = {}
            etype = event.get("type")
            ts = event.get("ts")

            if etype == "status":
                session = data.get("session")
                if isinstance(session, str) and session.strip():
                    # Events are returned oldest->newest; last write wins.
                    session_by_name[name] = session.strip()
                new_status = str(data.get("new_status") or "").strip().lower()
                if new_status in _STOPPED_STATUS_VALUES:
                    if "session" in data and data.get("session") is None:
                        subagent_only.add(name)
                    stop_by_name[name] = {
                        "reason": data.get("new_context")
                        or data.get("context")
                        or new_status,
                        "ts": ts,
                    }
                elif new_status:
                    # A later live transition clears a stale stop.
                    stop_by_name.pop(name, None)
            elif etype == "life":
                action = str(data.get("action") or "").strip().lower()
                if action == "stopped":
                    stop_by_name[name] = {
                        "reason": data.get("reason") or "stopped",
                        "ts": ts,
                    }
                elif action in {"ready", "started", "created"}:
                    stop_by_name.pop(name, None)

        records: list[dict[str, Any]] = []
        for name, stop in stop_by_name.items():
            if name in subagent_only and name not in session_by_name:
                continue
            record: dict[str, Any] = {
                "name": name,
                "status": "inactive",
                "process_bound": False,
                "status_context": str(stop.get("reason") or "stopped"),
                "stopped": True,
                "stop_reason": stop.get("reason"),
                "stop_ts": stop.get("ts"),
            }
            session_id = session_by_name.get(name)
            if session_id:
                record["session_id"] = session_id
            records.append(record)
        return records

    def read_events(
        self,
        *,
        last: int = 100,
        event_type: str | None = None,
        intent: str | None = None,
        agent: str | None = None,
        thread: str | None = None,
    ) -> list[dict[str, Any]]:
        if last < 1 or last > 5000:
            raise ValueError("last must be between 1 and 5000")
        args = ["events", "--last", str(last)]
        if event_type:
            args.extend(("--type", self._validate_name(event_type, "event type")))
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
        events: list[dict[str, Any]] = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise HcomProtocolError("hcom events returned a non-JSON record") from exc
            if not isinstance(event, dict):
                raise HcomProtocolError("hcom events record was not an object")
            events.append(event)
        return events

    def send(
        self,
        target: str,
        message: str,
        *,
        intent: str = "inform",
        thread: str | None = None,
        from_name: str | None = None,
    ) -> HcomCommandResult:
        target = self._validate_name(target, "target")
        normalized_intent = intent.strip().lower()
        if normalized_intent not in VALID_INTENTS:
            raise ValueError("intent must be request, inform, or ack")
        if not message.strip():
            raise ValueError("message cannot be empty")
        args = ["send", target if target.startswith("@") else f"@{target}"]
        args.extend(("--intent", normalized_intent))
        if thread:
            args.extend(("--thread", self._validate_name(thread, "thread")))
        if from_name:
            args.extend(("--from", self._validate_name(from_name, "sender")))
        args.extend(("--", message))
        return self._run(args)

    def spawn(
        self,
        tool: str,
        *,
        directory: str | Path,
        prompt: str | None = None,
        headless: bool = False,
        terminal: str | None = None,
    ) -> HcomCommandResult:
        tool = self._validate_tool(tool)
        if headless and terminal:
            raise ValueError("headless and terminal are mutually exclusive")
        args = [tool, "--dir", str(Path(directory).resolve())]
        if headless:
            args.append("--headless")
        elif terminal:
            args.extend(("--terminal", self._validate_tool(terminal)))
        if prompt:
            args.extend(("--hcom-prompt", prompt))
        return self._run(args)

    def resume(
        self,
        name: str,
        *,
        headless: bool = False,
        terminal: str | None = None,
        go: bool = True,
    ) -> HcomCommandResult:
        name = self._validate_name(name)
        if headless and terminal:
            raise ValueError("headless and terminal are mutually exclusive")
        args = ["r"]
        if go:
            args.append("--go")
        args.append(name)
        if headless:
            args.append("--headless")
        elif terminal:
            args.extend(("--terminal", self._validate_tool(terminal)))
        return self._run(args)

    def stop(self, name: str) -> HcomCommandResult:
        name = self._validate_name(name)
        if name in {"all", "tag:"} or name.startswith("tag:"):
            raise ValueError("stop() accepts one explicit agent/session name, not fan-out targets")
        return self._run(("kill", name))
