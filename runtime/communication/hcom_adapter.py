from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable

_NAME = re.compile(r"^[A-Za-z0-9_.:@-]+$")
_TOOL = re.compile(r"^[A-Za-z0-9_-]+$")
VALID_INTENTS = {"request", "inform", "ack"}


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
        try:
            return self._parse_session_list(result.stdout)
        except HcomProtocolError:
            if not include_stopped:
                raise
            # hcom does not honor `--json` for `list --stopped` -- confirmed
            # hcom 0.7.25, where `--json` is documented only for the
            # alive-only and single-agent forms and `--stopped` always emits
            # human-formatted text ("No recently stopped agents (last 60m)"
            # / "Stopped agents (all, showing N): ..."). Aborting here made
            # `maps recovery-tick` unable to reach the supervisor at all
            # (RecoverySupervisor.observe_silent_stops / tick both call this
            # unconditionally). Degrade to the contractual alive-only listing:
            # a stopped session then reads as absent, and session_is_live({})
            # is already False, so silent-stop *detection* is preserved.
            # KNOWN LIMITATION: the stopped session's `session_id` is lost, so
            # RecoverySupervisor._resolve_run_id() and HcomSessionAdapter's
            # session_id reverse lookup degrade to "not found" (run_id lineage
            # unresolved for the incident). The non-degraded fix is tracked in
            # work/notes/2026-09-03-hcom-list-stopped-nonjson-repair.md.
            fallback = self._run(["list", "--json"])
            return self._parse_session_list(fallback.stdout)

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
