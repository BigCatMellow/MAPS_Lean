#!/usr/bin/env python3
"""Run a MAP mirror sync and notify the operator on failure or recovery."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from typing import Any


DEFAULT_STATE = Path.home() / ".local" / "state" / "map-authority" / "health.json"
DEFAULT_REPEAT_SECONDS = 30 * 60
MAX_ERROR_CHARS = 500


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "unknown", "consecutive_failures": 0}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "unknown", "consecutive_failures": 0}
    return value if isinstance(value, dict) else {
        "status": "unknown",
        "consecutive_failures": 0,
    }


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp, 0o600)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def compact_error(completed: subprocess.CompletedProcess[str]) -> str:
    raw = completed.stderr or completed.stdout or "sync command failed"
    detail = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
    detail = detail.strip()
    detail = " ".join(detail.split())
    return detail[:MAX_ERROR_CHARS]


def sync_payload(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        value = json.loads(completed.stdout or "{}")
    except (TypeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def notify(summary: str, body: str, *, urgency: str) -> bool:
    try:
        completed = subprocess.run(
            [
                "notify-send",
                "--app-name=MAP Connection Watchdog",
                f"--urgency={urgency}",
                summary,
                body,
            ],
            check=False,
            text=True,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return completed.returncode == 0


def run_sync(authority_bin: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [str(authority_bin), "sync"],
            check=False,
            text=True,
            capture_output=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = (
            exc.stdout.decode("utf-8", errors="replace")
            if isinstance(exc.stdout, bytes)
            else (exc.stdout or "")
        )
        stderr = (
            exc.stderr.decode("utf-8", errors="replace")
            if isinstance(exc.stderr, bytes)
            else (exc.stderr or "mirror sync timed out after 60 seconds")
        )
        return subprocess.CompletedProcess(
            args=[str(authority_bin), "sync"],
            returncode=124,
            stdout=stdout,
            stderr=stderr,
        )
    except OSError as exc:
        return subprocess.CompletedProcess(
            args=[str(authority_bin), "sync"],
            returncode=127,
            stdout="",
            stderr=str(exc),
        )


def run_once(
    authority_bin: Path,
    state_path: Path,
    *,
    repeat_seconds: int = DEFAULT_REPEAT_SECONDS,
    now_epoch: float | None = None,
) -> int:
    now_epoch = time.time() if now_epoch is None else now_epoch
    previous = load_state(state_path)
    completed = run_sync(authority_bin)
    hostname = socket.gethostname()

    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.stderr:
        print(
            completed.stderr,
            end="" if completed.stderr.endswith("\n") else "\n",
            file=sys.stderr,
        )

    if completed.returncode == 0:
        sync = sync_payload(completed)
        was_failing = previous.get("status") == "failing"
        failure_notified = bool(previous.get("failure_notified"))
        recovery_pending = bool(previous.get("recovery_pending")) or (
            was_failing and failure_notified
        )
        recovery_notified = False
        if recovery_pending:
            recovery_notified = notify(
                "MAP connection restored",
                f"{hostname} can synchronize with the MAP authority again.",
                urgency="normal",
            )
        atomic_json(
            state_path,
            {
                "status": "healthy",
                "consecutive_failures": 0,
                "last_success_at": utc_now(),
                "authority_revision": sync.get("authority_revision")
                or previous.get("authority_revision"),
                "authority_observed_at": sync.get("authority_observed_at")
                or previous.get("authority_observed_at"),
                "last_error": "",
                "failure_notified": False,
                "recovery_notified": recovery_notified,
                "recovery_pending": recovery_pending and not recovery_notified,
            },
        )
        return 0

    failures = int(previous.get("consecutive_failures", 0)) + 1
    last_notification = previous.get("last_notification_epoch")
    notification_due = (
        previous.get("status") != "failing"
        or not isinstance(last_notification, (int, float))
        or now_epoch - float(last_notification) >= repeat_seconds
    )
    failure_notified = bool(previous.get("failure_notified"))
    if notification_due:
        failure_notified = notify(
            "MAP connection problem",
            (
                f"{hostname} could not synchronize with the MAP authority. "
                "It will retry automatically every minute.\n\n"
                f"{compact_error(completed)}"
            ),
            urgency="critical",
        ) or failure_notified

    state = {
        "status": "failing",
        "consecutive_failures": failures,
        "last_failure_at": utc_now(),
        "last_success_at": previous.get("last_success_at"),
        "authority_revision": previous.get("authority_revision"),
        "authority_observed_at": previous.get("authority_observed_at"),
        "last_error": compact_error(completed),
        "failure_notified": failure_notified,
        "recovery_notified": False,
    }
    if notification_due and failure_notified:
        state["last_notification_epoch"] = now_epoch
        state["last_notification_at"] = utc_now()
    elif isinstance(last_notification, (int, float)):
        state["last_notification_epoch"] = last_notification
        if previous.get("last_notification_at"):
            state["last_notification_at"] = previous["last_notification_at"]
    atomic_json(state_path, state)
    return completed.returncode or 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authority-bin", type=Path, required=True)
    parser.add_argument(
        "--state",
        type=Path,
        default=Path(os.environ.get("MAP_AUTHORITY_HEALTH_STATE", DEFAULT_STATE)),
    )
    parser.add_argument(
        "--repeat-seconds",
        type=int,
        default=DEFAULT_REPEAT_SECONDS,
    )
    args = parser.parse_args()
    if args.repeat_seconds < 60:
        parser.error("--repeat-seconds must be at least 60")
    return run_once(
        args.authority_bin.expanduser(),
        args.state.expanduser(),
        repeat_seconds=args.repeat_seconds,
    )


if __name__ == "__main__":
    raise SystemExit(main())
