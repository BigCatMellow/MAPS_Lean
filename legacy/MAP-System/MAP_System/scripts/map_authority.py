#!/usr/bin/env python3
"""Single-writer MAP authority gateway and read-only mirror synchronizer.

Smalls runs in ``authority`` mode and owns the writable production ``map.db``.
Biggie runs in ``mirror`` mode, receives consistent snapshots, and sends
allowlisted lifecycle requests over a forced-command SSH key.
"""

from __future__ import annotations

import argparse
import base64
import binascii
from datetime import datetime, timezone
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import time
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.db.authority import load_authority_config  # noqa: E402


PROTOCOL_VERSION = 1
MAX_REQUEST_BYTES = 32 * 1024
MAX_RESPONSE_BYTES = 128 * 1024 * 1024
MAX_ARGUMENTS = 96
MAX_ARGUMENT_BYTES = 4096
DEFAULT_CONFIG = Path.home() / ".config" / "map-authority.json"
DEFAULT_LOCK = ROOT / ".locks" / "map-authority-sync.lock"
DEFAULT_HEALTH_STATE = (
    Path.home() / ".local" / "state" / "map-authority" / "health.json"
)
DEFAULT_FRESHNESS_SECONDS = 180
CLOCK_SKEW_TOLERANCE_SECONDS = 120
MAX_STATUS_ERROR_CHARS = 500
DB_PATH = ROOT / "map.db"
MIRROR_FILES = (
    "workflow/task_graph.json",
    "agents/status.json",
    "events/events.jsonl",
    "shared/current-state.md",
)
# map-rns-watcher.service (limit_watcher.py) is always-on (Restart=always,
# WantedBy=default.target) and never touches map.db. Of its three write
# targets -- agents/limit-watcher-state.json, events/events.jsonl, and
# .locks/limit-watcher.pid -- only events/events.jsonl overlaps a file
# install_snapshot() overwrites wholesale, and it writes there only on
# state-change events (rotation reminders, escalations), not continuously.
# Treating mere process liveness as disqualifying (TASK-310's original,
# coarser check) blocks nearly every sync even though a collision window
# only exists in the seconds around an actual append. TASK-316 narrows the
# signal to that real window instead of blanket-exempting the service.
RNS_WATCHER_SERVICE = "map-rns-watcher.service"
RNS_WATCHER_MIRRORED_WRITE_TARGETS = (ROOT / "events" / "events.jsonl",)
RNS_WATCHER_WRITE_QUIET_SECONDS = 15
CGROUP_ROOT = Path("/sys/fs/cgroup")
WRITER_SERVICE_UNITS = (
    RNS_WATCHER_SERVICE,
    "map-command-center-maintenance.service",
)
WRITER_TIMER_UNITS = ("map-command-center-maintenance.timer",)
ALLOWED_OPERATIONS = {
    "route",
    "task",
    "claim",
    "heartbeat",
    "claim-review",
    "get-open-review",
    "release-review",
    "snapshot",
    "register-agent",
    "rotation-transfer",
    "rotation-restore",
}
FORBIDDEN_TASK_FLAGS = {"--db", "--output-dir", "--event-log"}
ALLOWED_TASK_VERBS = {
    "create",
    "approve",
    "reject",
    "rework",
    "submit",
    "release",
    "recover-orphan",
    "reassign-owner",
    "extend-attempts",
    "retire",
    "describe",
    "amend-criteria",
    "add-output-path",
    "show",
    "log",
}


class AuthorityError(RuntimeError):
    pass


def compact_json(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True)


def result(*, ok: bool, **values: Any) -> dict[str, Any]:
    return {"version": PROTOCOL_VERSION, "ok": ok, **values}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def file_revision(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return None
    return f"sha256:{digest.hexdigest()}"


def consistent_database_revision(db_path: Path = DB_PATH) -> str | None:
    """Hash a SQLite online backup rather than a hot ordinary file copy."""

    if not db_path.is_file():
        return None
    try:
        with tempfile.TemporaryDirectory(prefix="map-authority-revision-") as temp_name:
            db_copy = Path(temp_name) / "map.db"
            source = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=10)
            destination = sqlite3.connect(db_copy)
            try:
                source.backup(destination)
            finally:
                destination.close()
                source.close()
            return file_revision(db_copy)
    except (OSError, sqlite3.Error):
        return None


def load_health_state(path: Path = DEFAULT_HEALTH_STATE) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def authority_status(
    config: dict[str, Any],
    *,
    now: datetime | None = None,
    health_path: Path = DEFAULT_HEALTH_STATE,
    db_path: Path = DB_PATH,
    writer_services: Sequence[str] | None = None,
    database_writable: bool | None = None,
    freshness_threshold_seconds: int = DEFAULT_FRESHNESS_SECONDS,
) -> dict[str, Any]:
    """Return one fail-closed authority/freshness contract for all consumers."""

    now = (now or utc_now()).astimezone(timezone.utc)
    mode = config.get("mode") if config.get("mode") in {"authority", "mirror"} else "unknown"
    writer_probe_error = ""
    writer_probe_source = "not_applicable"
    if writer_services is not None:
        services = list(writer_services)
        writer_probe_source = "provided"
    elif mode == "mirror":
        try:
            services, writer_probe_source = _probe_active_local_writer_services()
        except AuthorityError as exc:
            services = []
            writer_probe_source = "unavailable"
            writer_probe_error = str(exc)[:MAX_STATUS_ERROR_CHARS]
    else:
        services = []
    writable = (
        os.access(db_path, os.W_OK)
        if database_writable is None
        else bool(database_writable)
    )
    topology_valid = mode == "authority" or (
        mode == "mirror" and not writable and not services and not writer_probe_error
    )
    payload: dict[str, Any] = {
        "mode": mode,
        "authority_host": config.get("authority_host") if mode == "mirror" else None,
        "authority_revision": None,
        "authority_observed_at": None,
        "last_successful_sync_at": None,
        "freshness": "UNAVAILABLE",
        "freshness_age_seconds": None,
        "freshness_threshold_seconds": int(freshness_threshold_seconds),
        "last_error": "",
        "topology_valid": topology_valid,
        "local_writer_services": services,
        "writer_service_probe_source": writer_probe_source,
        "writer_service_probe_error": writer_probe_error,
    }

    if mode == "authority":
        payload["authority_revision"] = consistent_database_revision(db_path)
        payload["authority_observed_at"] = utc_text(now)
        if not writable or not db_path.is_file():
            payload["freshness"] = "INVALID"
            payload["topology_valid"] = False
            payload["last_error"] = "authority database is missing or not writable"
        elif payload["authority_revision"] is None:
            payload["freshness"] = "UNAVAILABLE"
            payload["last_error"] = "authority database revision is unavailable"
        else:
            payload["freshness"] = "AUTHORITATIVE"
        return payload

    if mode != "mirror":
        payload["freshness"] = "INVALID"
        payload["topology_valid"] = False
        payload["last_error"] = "MAP authority mode is missing or unsupported"
        return payload

    state = load_health_state(health_path)
    payload["authority_revision"] = state.get("authority_revision")
    payload["authority_observed_at"] = state.get("authority_observed_at")
    payload["last_successful_sync_at"] = state.get("last_success_at")
    payload["last_error"] = str(state.get("last_error") or "")[
        :MAX_STATUS_ERROR_CHARS
    ]

    if not topology_valid:
        payload["freshness"] = "INVALID"
        if writer_probe_error:
            payload["last_error"] = (
                "mirror topology is invalid: writer service inactivity could "
                f"not be established ({writer_probe_error})"
            )
        else:
            payload["last_error"] = (
                "mirror topology is invalid: local database is writable or "
                "authority writer services are active"
            )
        return payload

    success_at = parse_utc(state.get("last_success_at"))
    if success_at is None:
        payload["freshness"] = "UNAVAILABLE"
        if not payload["last_error"]:
            payload["last_error"] = "no valid successful mirror sync is recorded"
        return payload

    age = (now - success_at).total_seconds()
    if age < -CLOCK_SKEW_TOLERANCE_SECONDS:
        payload["freshness"] = "INVALID"
        payload["last_error"] = "last successful sync timestamp is in the future"
        return payload
    payload["freshness_age_seconds"] = max(0, int(age))

    installed_revision = file_revision(db_path)
    if (
        not isinstance(payload["authority_revision"], str)
        or installed_revision != payload["authority_revision"]
    ):
        payload["freshness"] = "INVALID"
        payload["last_error"] = "installed mirror revision does not match sync record"
        return payload

    if state.get("status") == "failing" or age > freshness_threshold_seconds:
        payload["freshness"] = "STALE"
    else:
        payload["freshness"] = "FRESH"
    return payload


NON_FRESH_STATES = {"STALE", "UNAVAILABLE", "INVALID"}


def apply_freshness_gate(routed: dict[str, Any], authority: dict[str, Any]) -> dict[str, Any]:
    """Attach the authority object to a route payload and fail closed.

    LangGraph's runner stays recommendation-only (TASK-304/TASK-310); this is
    the one place every route consumer passes through, so it is where a
    stale, unavailable, or invalid mirror gets stopped from presenting its
    underlying recommendation as current. The original recommendation is
    preserved under the `stale_authority_*` keys rather than discarded, so
    the view stays inspectable ("views may remain readable but must not say
    current, green, or globally healthy" -- ws1-truthful-authority-state.md).
    """
    routed["authority"] = authority
    if authority.get("freshness") in NON_FRESH_STATES:
        routed["stale_authority_next_route"] = routed.get("next_route")
        routed["stale_authority_recommended_action"] = routed.get("recommended_action")
        routed["next_route"] = "STALE_AUTHORITY"
        routed["recommended_action"] = (
            f"Authority freshness is {authority.get('freshness')}: "
            f"{authority.get('last_error') or 'no fresh sync recorded'}. Do not "
            "treat the prior route recommendation as current; resolve authority "
            "sync before dispatching."
        )
    return routed


def require_string(value: Any, name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise AuthorityError(f"{name} must be a string")
    if "\x00" in value:
        raise AuthorityError(f"{name} contains a NUL byte")
    if len(value.encode("utf-8")) > MAX_ARGUMENT_BYTES:
        raise AuthorityError(f"{name} exceeds {MAX_ARGUMENT_BYTES} bytes")
    if not allow_empty and not value.strip():
        raise AuthorityError(f"{name} must not be empty")
    return value


def require_args(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise AuthorityError("args must be a list")
    if len(value) > MAX_ARGUMENTS:
        raise AuthorityError(f"too many arguments; maximum is {MAX_ARGUMENTS}")
    return [require_string(item, f"args[{index}]", allow_empty=True) for index, item in enumerate(value)]


def encode_request(operation: str, args: Sequence[str]) -> str:
    operation = require_string(operation, "operation")
    if operation not in ALLOWED_OPERATIONS:
        raise AuthorityError(f"operation is not allowlisted: {operation}")
    validated_args = require_args(list(args))
    payload = compact_json(
        {
            "version": PROTOCOL_VERSION,
            "operation": operation,
            "args": validated_args,
        }
    ).encode("utf-8")
    if len(payload) > MAX_REQUEST_BYTES:
        raise AuthorityError(f"request exceeds {MAX_REQUEST_BYTES} bytes")
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def decode_request(encoded: str) -> dict[str, Any]:
    if not encoded or len(encoded) > MAX_REQUEST_BYTES * 2:
        raise AuthorityError("encoded request is empty or oversized")
    try:
        padding = "=" * (-len(encoded) % 4)
        raw = base64.b64decode(encoded + padding, altchars=b"-_", validate=True)
    except (binascii.Error, ValueError) as exc:
        raise AuthorityError("request is not valid URL-safe base64") from exc
    if len(raw) > MAX_REQUEST_BYTES:
        raise AuthorityError(f"decoded request exceeds {MAX_REQUEST_BYTES} bytes")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthorityError("request is not valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise AuthorityError("request must be a JSON object")
    if payload.get("version") != PROTOCOL_VERSION:
        raise AuthorityError("unsupported authority protocol version")
    operation = require_string(payload.get("operation"), "operation")
    if operation not in ALLOWED_OPERATIONS:
        raise AuthorityError(f"operation is not allowlisted: {operation}")
    args = require_args(payload.get("args", []))
    return {"operation": operation, "args": args}


def run_checked(command: Sequence[str]) -> dict[str, Any]:
    completed = subprocess.run(
        list(command),
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    return result(
        ok=completed.returncode == 0,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def sync_canonical_mirrors() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "migration" / "export_to_files.py")],
        cwd=REPO,
        check=True,
        stdout=subprocess.DEVNULL,
    )


def dispatch_authority(operation: str, args: Sequence[str]) -> dict[str, Any]:
    config = load_authority_config()
    if config.get("mode") != "authority":
        raise AuthorityError("gateway host is not configured in authority mode")

    if operation == "route":
        if args:
            raise AuthorityError("route accepts no arguments")
        routed = run_checked(
            [str(ROOT / ".venv" / "bin" / "python"), str(ROOT / "graph" / "runner.py"), "--pretty"]
        )
        if not routed.get("ok"):
            return routed
        try:
            payload = json.loads(routed.get("stdout", ""))
        except (TypeError, json.JSONDecodeError) as exc:
            raise AuthorityError("runner returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise AuthorityError("runner returned a non-object JSON payload")
        payload = apply_freshness_gate(payload, authority_status(config))
        routed["stdout"] = json.dumps(payload, indent=2) + "\n"
        return routed

    if operation == "task":
        if not args:
            raise AuthorityError("task requires a map_task.py verb")
        if args[0] not in ALLOWED_TASK_VERBS:
            raise AuthorityError(f"task verb is not allowlisted: {args[0]}")
        if any(
            arg == flag or arg.startswith(f"{flag}=")
            for arg in args
            for flag in FORBIDDEN_TASK_FLAGS
        ):
            raise AuthorityError("task requests may not override canonical paths")
        return run_checked(
            [str(ROOT / ".venv" / "bin" / "python"), str(ROOT / "scripts" / "map_task.py"), *args]
        )

    if operation == "snapshot":
        if args:
            raise AuthorityError("snapshot accepts no arguments")
        archive = build_snapshot()
        files = validate_snapshot(archive)
        return result(
            ok=True,
            sha256=hashlib.sha256(archive).hexdigest(),
            archive_b64=base64.b64encode(archive).decode("ascii"),
            authority_revision=f"sha256:{hashlib.sha256(files['map.db']).hexdigest()}",
            authority_observed_at=utc_text(utc_now()),
        )

    from MAP_System.db.claims import (  # imported only on the authority host
        claim_review,
        claim_task_with_reason,
        get_open_review_claim,
        heartbeat,
        register_agent,
        release_review_claim,
        restore_rotation_claims,
        transfer_rotation_claims,
    )

    if operation == "claim":
        if len(args) not in {2, 3}:
            raise AuthorityError("claim requires TASK-ID AGENT-ID [LEASE-SECONDS]")
        lease = int(args[2]) if len(args) == 3 else 1800
        claimed, reason = claim_task_with_reason(args[0], args[1], lease_seconds=lease)
        if claimed:
            sync_canonical_mirrors()
        return result(ok=claimed, claimed=claimed, reason=reason)

    if operation == "heartbeat":
        if len(args) not in {2, 3}:
            raise AuthorityError("heartbeat requires TASK-ID AGENT-ID [LEASE-SECONDS]")
        lease = int(args[2]) if len(args) == 3 else 1800
        renewed = heartbeat(args[0], args[1], lease_seconds=lease)
        return result(ok=renewed, renewed=renewed)

    if operation == "claim-review":
        if len(args) != 2:
            raise AuthorityError("claim-review requires TASK-ID REVIEWER-ID")
        claimed = claim_review(args[0], args[1])
        return result(ok=claimed, claimed=claimed)

    if operation == "get-open-review":
        if len(args) != 1:
            raise AuthorityError("get-open-review requires TASK-ID")
        claim = get_open_review_claim(args[0])
        return result(ok=True, claim=claim)

    if operation == "release-review":
        if len(args) != 3:
            raise AuthorityError("release-review requires TASK-ID REVIEWER-ID VERDICT")
        released = release_review_claim(args[0], args[1], verdict=args[2])
        return result(ok=released, released=released)

    if operation == "register-agent":
        if len(args) != 1:
            raise AuthorityError("register-agent requires AGENT-ID")
        register_agent(args[0])
        return result(ok=True)

    if operation == "rotation-transfer":
        # TASK-271 context-rotation finalize step, run on the authority host
        # so a mirror host (KUDU) never needs a direct map.db write.
        if len(args) < 2:
            raise AuthorityError("rotation-transfer requires OLD-AGENT REPLACEMENT-AGENT [TASK-ID...]")
        try:
            snapshot = transfer_rotation_claims(args[0], args[1], args[2:])
        except ValueError as exc:
            return result(ok=False, error=str(exc))
        return result(ok=True, **snapshot)

    if operation == "rotation-restore":
        # TASK-307 security fix: transfer_id is an opaque reference to a
        # server-recorded rotation_transfers row, not caller-supplied row
        # data -- see restore_rotation_claims()'s docstring. A malformed or
        # unknown/already-consumed id fails closed via the ValueError branch
        # below, same as any other integrity failure on this gateway.
        if len(args) != 1:
            raise AuthorityError("rotation-restore requires TRANSFER-ID")
        try:
            restore_rotation_claims(args[0])
        except ValueError as exc:
            return result(ok=False, error=str(exc))
        return result(ok=True)

    raise AuthorityError(f"unhandled operation: {operation}")


def snapshot_members(db_copy: Path) -> dict[str, bytes]:
    members: dict[str, bytes] = {"map.db": db_copy.read_bytes()}
    for relative in MIRROR_FILES:
        path = ROOT / relative
        if path.exists():
            members[relative] = path.read_bytes()
    for path in sorted((ROOT / "tasks").glob("TASK-*.json")):
        members[f"tasks/{path.name}"] = path.read_bytes()
    return members


def build_snapshot() -> bytes:
    """Return a consistent SQLite backup plus canonical file mirrors."""

    with tempfile.TemporaryDirectory(prefix="map-authority-snapshot-") as temp_name:
        db_copy = Path(temp_name) / "map.db"
        source = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=10)
        destination = sqlite3.connect(db_copy)
        try:
            source.backup(destination)
        finally:
            destination.close()
            source.close()

        members = snapshot_members(db_copy)
        manifest = {
            name: {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
            for name, data in sorted(members.items())
        }
        members["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")

        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            for name, data in sorted(members.items()):
                info = tarfile.TarInfo(name=name)
                info.size = len(data)
                info.mode = 0o444 if name == "map.db" else 0o664
                archive.addfile(info, io.BytesIO(data))
        return buffer.getvalue()


def validate_snapshot(archive_bytes: bytes) -> dict[str, bytes]:
    if len(archive_bytes) > MAX_RESPONSE_BYTES:
        raise AuthorityError("snapshot archive is oversized")
    extracted: dict[str, bytes] = {}
    total = 0
    try:
        archive = tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz")
    except tarfile.TarError as exc:
        raise AuthorityError("snapshot is not a valid gzip tar archive") from exc
    with archive:
        for member in archive.getmembers():
            path = Path(member.name)
            allowed = (
                member.name in {"map.db", "manifest.json", *MIRROR_FILES}
                or (len(path.parts) == 2 and path.parts[0] == "tasks" and path.name.startswith("TASK-") and path.suffix == ".json")
            )
            if (
                not allowed
                or path.is_absolute()
                or ".." in path.parts
                or not member.isfile()
                or member.name in extracted
            ):
                raise AuthorityError(f"unsafe snapshot member: {member.name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise AuthorityError(f"snapshot member is unreadable: {member.name}")
            data = stream.read(MAX_RESPONSE_BYTES + 1)
            total += len(data)
            if total > MAX_RESPONSE_BYTES:
                raise AuthorityError("snapshot expands beyond the size limit")
            extracted[member.name] = data

    if "map.db" not in extracted or "manifest.json" not in extracted:
        raise AuthorityError("snapshot is missing map.db or manifest.json")
    try:
        manifest = json.loads(extracted.pop("manifest.json").decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthorityError("snapshot manifest is invalid") from exc
    if not isinstance(manifest, dict) or set(manifest) != set(extracted):
        raise AuthorityError("snapshot manifest membership does not match the archive")
    for name, data in extracted.items():
        entry = manifest.get(name)
        if not isinstance(entry, dict):
            raise AuthorityError(f"snapshot manifest entry is invalid: {name}")
        if entry.get("size") != len(data) or entry.get("sha256") != hashlib.sha256(data).hexdigest():
            raise AuthorityError(f"snapshot checksum mismatch: {name}")
    return extracted


def remote_request(config: dict[str, Any], operation: str, args: Sequence[str]) -> dict[str, Any]:
    host = require_string(config.get("authority_host"), "authority_host")
    user = require_string(config.get("authority_user", "home"), "authority_user")
    key = Path(require_string(config.get("authority_key"), "authority_key")).expanduser()
    if not key.is_file():
        raise AuthorityError(f"authority key is missing: {key}")
    encoded = encode_request(operation, args)
    completed = subprocess.run(
        [
            "ssh",
            "-i",
            str(key),
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=10",
            f"{user}@{host}",
            f"map-authority {encoded}",
        ],
        text=True,
        capture_output=True,
        check=False,
        timeout=45,
    )
    if completed.returncode != 0:
        remote_error: str | None = None
        try:
            parsed = json.loads(completed.stdout)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict) and not parsed.get("ok", True):
            remote_error = str(parsed.get("error") or parsed)
        detail = remote_error or completed.stderr.strip() or completed.stdout.strip()
        raise AuthorityError(
            f"authority request failed ({completed.returncode}): {detail}"
        )
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AuthorityError("authority returned invalid JSON") from exc
    if not isinstance(response, dict) or response.get("version") != PROTOCOL_VERSION:
        raise AuthorityError("authority returned an invalid protocol envelope")
    return response


def _recently_written(paths: Sequence[Path], *, quiet_seconds: float) -> bool:
    """True if any path was modified within ``quiet_seconds`` of now.

    A missing file has never been written and is not recent. Any other stat
    failure (e.g. a permission error) means recency cannot be proven, so it
    fails closed as "recently written" rather than silently clearing the
    writer flag.
    """
    now = time.time()
    for path in paths:
        try:
            mtime = path.stat().st_mtime
        except FileNotFoundError:
            continue
        except OSError:
            return True
        if now - mtime < quiet_seconds:
            return True
    return False


def _filter_active_writer_units(units: Sequence[str]) -> list[str]:
    active: list[str] = []
    for unit in units:
        if unit == RNS_WATCHER_SERVICE and not _recently_written(
            RNS_WATCHER_MIRRORED_WRITE_TARGETS,
            quiet_seconds=RNS_WATCHER_WRITE_QUIET_SECONDS,
        ):
            # Running but quiet: no genuine collision window is open against
            # any file install_snapshot() is about to overwrite.
            continue
        active.append(unit)
    return active


def _user_bus_unavailable(probe: subprocess.CompletedProcess[str]) -> bool:
    diagnostic = (probe.stderr or probe.stdout or "").lower()
    return "failed to connect to bus" in diagnostic


def _active_writer_services_from_cgroup_v2(
    *, cgroup_root: Path | None = None, uid: int | None = None
) -> list[str]:
    """Read process-bearing user-service activity without the user D-Bus.

    A Codex sandbox can read cgroup v2 while being unable to connect to the
    host user bus. Missing service cgroups mean those process-bearing units
    have no running process. Timers are deliberately not inferred from a
    missing cgroup: the timer itself is not a writer, while its oneshot writer
    is covered by ``map-command-center-maintenance.service``.
    """

    cgroup_root = CGROUP_ROOT if cgroup_root is None else cgroup_root
    if not (cgroup_root / "cgroup.controllers").is_file():
        raise AuthorityError(
            "writer service fallback unavailable: cgroup v2 is not mounted"
        )
    uid = os.getuid() if uid is None else uid
    service_root = (
        cgroup_root
        / "user.slice"
        / f"user-{uid}.slice"
        / f"user@{uid}.service"
        / "app.slice"
    )
    if not service_root.is_dir():
        raise AuthorityError(
            "writer service fallback unavailable: "
            f"user service cgroup root was not found for uid {uid}"
        )
    active: list[str] = []
    for unit in WRITER_SERVICE_UNITS:
        events = service_root / unit / "cgroup.events"
        try:
            content = events.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise AuthorityError(
                f"writer service fallback could not read {events}: {exc}"
            ) from exc
        populated_values = [
            line.split()[1]
            for line in content.splitlines()
            if len(line.split()) == 2 and line.split()[0] == "populated"
        ]
        if populated_values not in (["0"], ["1"]):
            raise AuthorityError(
                f"writer service fallback found invalid cgroup.events for {unit}"
            )
        if populated_values == ["1"]:
            active.append(unit)
    return _filter_active_writer_units(active)


def active_local_writer_services() -> list[str]:
    services, _source = _probe_active_local_writer_services()
    return services


def _probe_active_local_writer_services() -> tuple[list[str], str]:
    """Return active writers and the evidence source used to classify them."""

    if shutil.which("systemctl") is None:
        raise AuthorityError(
            "writer service probe unavailable: systemctl was not found"
        )
    active: list[str] = []
    for unit in (*WRITER_SERVICE_UNITS, *WRITER_TIMER_UNITS):
        probe = subprocess.run(
            ["systemctl", "--user", "is-active", "--quiet", unit],
            check=False,
            text=True,
            capture_output=True,
        )
        if probe.returncode == 0:
            active.append(unit)
        elif probe.returncode not in {3, 4}:
            if _user_bus_unavailable(probe):
                return (
                    _active_writer_services_from_cgroup_v2(),
                    "cgroup_v2_fallback",
                )
            diagnostic = (probe.stderr or probe.stdout or "unknown error").strip()
            diagnostic = diagnostic[:MAX_STATUS_ERROR_CHARS]
            raise AuthorityError(
                f"writer service probe failed for {unit}: {diagnostic}"
            )
    return _filter_active_writer_units(active), "systemctl"


def atomic_write(path: Path, data: bytes, mode: int) -> None:
    temp = stage_file(path, data, mode)
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def stage_file(path: Path, data: bytes, mode: int) -> Path:
    """Fully write and fsync a sibling file without replacing its target."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp, mode)
        return temp
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def install_snapshot(files: dict[str, bytes]) -> None:
    writers = active_local_writer_services()
    if writers:
        raise AuthorityError(
            "local writer services must be disabled before mirror sync: "
            + ", ".join(writers)
        )
    DEFAULT_LOCK.parent.mkdir(parents=True, exist_ok=True)
    with DEFAULT_LOCK.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        staged: dict[Path, Path] = {}
        for name, data in sorted(files.items()):
            target = DB_PATH if name == "map.db" else ROOT / name
            staged[target] = stage_file(
                target, data, 0o444 if name == "map.db" else 0o664
            )

        changes: list[dict[str, Any]] = []

        def move_existing(target: Path) -> Path | None:
            if not target.exists():
                return None
            descriptor, backup_name = tempfile.mkstemp(
                prefix=f".{target.name}.map-authority-backup-",
                dir=target.parent,
            )
            os.close(descriptor)
            backup = Path(backup_name)
            backup.unlink()
            os.replace(target, backup)
            return backup

        try:
            for target in sorted(path for path in staged if path != DB_PATH):
                # TASK-316 follow-up (independent review, zinu): the initial
                # active_local_writer_services() probe runs before this lock
                # is even acquired, and staging every file above takes real
                # time -- a watcher write can land in that window and then
                # be silently clobbered by the replace below. Re-check the
                # one target the watcher can actually touch immediately
                # before replacing it, inside the lock, to close that gap to
                # a single syscall instead of the whole staging phase.
                if target in RNS_WATCHER_MIRRORED_WRITE_TARGETS and _recently_written(
                    (target,), quiet_seconds=RNS_WATCHER_WRITE_QUIET_SECONDS
                ):
                    raise AuthorityError(
                        "local writer wrote to "
                        f"{target.relative_to(ROOT)} after the writer-service probe "
                        "passed; aborting install to avoid clobbering it"
                    )
                change = {
                    "target": target,
                    "backup": move_existing(target),
                    "installed": False,
                }
                changes.append(change)
                os.replace(staged[target], target)
                change["installed"] = True

            for sidecar in (ROOT / "map.db-wal", ROOT / "map.db-shm"):
                if sidecar.exists():
                    changes.append(
                        {
                            "target": sidecar,
                            "backup": move_existing(sidecar),
                            "installed": False,
                        }
                    )

            db_change = {
                "target": DB_PATH,
                "backup": move_existing(DB_PATH),
                "installed": False,
            }
            changes.append(db_change)
            os.replace(staged[DB_PATH], DB_PATH)
            db_change["installed"] = True
        except BaseException:
            for change in reversed(changes):
                target = change["target"]
                backup = change["backup"]
                if change["installed"]:
                    target.unlink(missing_ok=True)
                if backup is not None and backup.exists():
                    os.replace(backup, target)
            raise
        finally:
            for staged_path in staged.values():
                staged_path.unlink(missing_ok=True)
        for change in changes:
            backup = change["backup"]
            if backup is not None:
                backup.unlink(missing_ok=True)


def sync_mirror(config: dict[str, Any]) -> dict[str, Any]:
    if config.get("mode") != "mirror":
        raise AuthorityError("sync is only valid in mirror mode")
    response = remote_request(config, "snapshot", [])
    if not response.get("ok"):
        raise AuthorityError(f"authority snapshot failed: {response}")
    encoded = response.get("archive_b64")
    if not isinstance(encoded, str):
        raise AuthorityError("authority snapshot omitted archive_b64")
    try:
        archive = base64.b64decode(encoded, validate=True)
    except binascii.Error as exc:
        raise AuthorityError("authority snapshot is not valid base64") from exc
    if hashlib.sha256(archive).hexdigest() != response.get("sha256"):
        raise AuthorityError("authority snapshot transport checksum mismatch")
    files = validate_snapshot(archive)
    installed_revision = f"sha256:{hashlib.sha256(files['map.db']).hexdigest()}"
    reported_revision = response.get("authority_revision")
    if reported_revision is not None and reported_revision != installed_revision:
        raise AuthorityError("authority revision does not match validated database")
    install_snapshot(files)
    return result(
        ok=True,
        installed_files=len(files),
        db_sha256=hashlib.sha256(files["map.db"]).hexdigest(),
        authority_revision=installed_revision,
        authority_observed_at=response.get("authority_observed_at"),
    )


def gateway_main() -> int:
    original = os.environ.get("SSH_ORIGINAL_COMMAND", "")
    prefix = "map-authority "
    if not original.startswith(prefix) or "\n" in original or "\r" in original:
        print(compact_json(result(ok=False, error="invalid forced command")))
        return 2
    try:
        request = decode_request(original[len(prefix) :])
        response = dispatch_authority(request["operation"], request["args"])
    except (AuthorityError, RuntimeError, PermissionError, ValueError, sqlite3.Error) as exc:
        response = result(ok=False, error=str(exc))
    print(compact_json(response))
    return 0 if response.get("ok") else 1


def operation_main(operation: str, args: Sequence[str]) -> int:
    config = load_authority_config()
    if config.get("mode") == "mirror":
        response = remote_request(config, operation, args)
        if operation == "route" and response.get("ok"):
            try:
                routed = json.loads(response.get("stdout", ""))
            except (TypeError, json.JSONDecodeError) as exc:
                raise AuthorityError("authority route returned invalid JSON") from exc
            if not isinstance(routed, dict):
                raise AuthorityError(
                    "authority route returned a non-object JSON payload"
                )
            routed = apply_freshness_gate(routed, authority_status(config))
            response["stdout"] = json.dumps(routed, indent=2) + "\n"
    elif config.get("mode") == "authority":
        response = dispatch_authority(operation, args)
    else:
        raise AuthorityError(
            "MAP authority is not configured; expected authority or mirror mode"
        )
    print(json.dumps(response, indent=2))
    return 0 if response.get("ok") else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("gateway", help=argparse.SUPPRESS)
    sub.add_parser("status")
    sub.add_parser("mode")
    sub.add_parser("prompt-note")
    sub.add_parser("sync")
    sub.add_parser("route")
    task = sub.add_parser("task")
    task.add_argument("task_args", nargs=argparse.REMAINDER)
    for name, minimum, maximum in (
        ("claim", 2, 3),
        ("heartbeat", 2, 3),
        ("claim-review", 2, 2),
        ("get-open-review", 1, 1),
        ("release-review", 3, 3),
        ("register-agent", 1, 1),
        ("rotation-transfer", 2, MAX_ARGUMENTS),
        ("rotation-restore", 1, 1),
    ):
        command = sub.add_parser(name)
        command.add_argument("operation_args", nargs="+")
        command.set_defaults(argument_bounds=(minimum, maximum))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        config = load_authority_config()
        if args.command == "gateway":
            return gateway_main()
        if args.command == "mode":
            print(config.get("mode", "standalone"))
            return 0
        if args.command == "status":
            authority = authority_status(config)
            payload = {
                "mode": config.get("mode", "standalone"),
                "authority_host": config.get("authority_host"),
                "database": str(DB_PATH),
                "database_writable": os.access(DB_PATH, os.W_OK),
                "local_writer_services": authority.get("local_writer_services", []),
                "writer_service_probe_source": authority.get(
                    "writer_service_probe_source", "unavailable"
                ),
                "writer_service_probe_error": authority.get(
                    "writer_service_probe_error", ""
                ),
                "authority": authority,
            }
            print(json.dumps(payload, indent=2))
            return 0
        if args.command == "prompt-note":
            if config.get("mode") == "mirror":
                print(
                    "Cross-PC authority: this host is a read-only MAP mirror. "
                    "Use `map-authority route`, `map-authority claim`, "
                    "`map-authority heartbeat`, and `map-authority task ...`; "
                    "never mutate local MAP_System/map.db."
                )
            return 0
        if args.command == "sync":
            response = sync_mirror(config)
            print(json.dumps(response, indent=2))
            return 0
        if args.command == "route":
            return operation_main("route", [])
        if args.command == "task":
            return operation_main("task", args.task_args)
        operation_args = args.operation_args
        minimum, maximum = args.argument_bounds
        if not minimum <= len(operation_args) <= maximum:
            raise AuthorityError(
                f"{args.command} expects {minimum}"
                + (f"-{maximum}" if minimum != maximum else "")
                + " arguments"
            )
        return operation_main(args.command, operation_args)
    except (AuthorityError, OSError, subprocess.SubprocessError, ValueError) as exc:
        print(f"map-authority error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
