#!/usr/bin/env python3
"""Verified context rotation with a durable human-readable continuity ledger.

TASK-271 implements a two-phase protocol:

1. prepare: validate and freeze a STATE_SNAPSHOT v2, then commit its hash and
   canonical task/path digests to shared/context-continuity.md under a lock;
2. acknowledge: a different, live replacement session proves it loaded the
   exact snapshot hash while canonical state is still unchanged;
3. finalize: atomically transfer the old session's live task claims, export
   mirrors, mark the old identity session_superseded, and commit the ledger.

Raw transcripts and snapshots are never deleted.  The Markdown ledger contains
an embedded JSON state block so humans and validators read the same record.
"""

from __future__ import annotations

import argparse
import contextlib
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from typing import Any, Iterable

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
    raise SystemExit("PyYAML is required; run with MAP_System/.venv/bin/python") from exc


ROOT = Path(__file__).resolve().parents[1]

# Shared files that legitimately mutate from concurrent, unrelated agent/
# background activity (e.g. limit_watcher's own checkpoint notices appending
# to events.jsonl). Exact-content drift on these paths does not indicate a
# problem with the rotating agent's own work, so they are excluded from the
# strict touched_path content match the same way protocol-generated files
# are (see stable_path_evidence). Unlike protocol-generated files, a size
# regression on an append-only path is still flagged: that would indicate
# truncation/corruption rather than ordinary concurrent appends.
VOLATILE_SHARED_PATHS = {
    "MAP_System/events/events.jsonl",
    "MAP_System/agents/status.json",
    "MAP_System/agents/limit-watcher-state.json",
}
APPEND_ONLY_PATHS = {
    "MAP_System/events/events.jsonl",
}
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
DEFAULT_DB = ROOT / "map.db"
DEFAULT_MASTER = ROOT / "shared" / "context-continuity.md"
DEFAULT_LOCK = ROOT / ".locks" / "context-rotation.lock"
# Coordinator-tuned defaults. A session holding several in-flight helper lanes
# plus roadmap state across round-trips needs more headroom than a single-task
# implementer; a mid-arc rotation there disrupts more than it helps. With
# lossless SessionStart handoff injection a rotation costs ~5k re-orientation,
# not ~40k, so the higher marks are safe.
#   flat default:  soft checkpoint at 0.80 * 185k = 148k, rotate at 185k
#   known window:  soft at min(148k, window * 0.78), rotate at min(185k, window * 0.90)
DEFAULT_THRESHOLD_TOKENS = 185_000
SOFT_FRACTION = 0.78
HARD_FRACTION = 0.90
MASTER_PREFIX = "<!-- context-rotation-state\n"
MASTER_SUFFIX = "\n-->"
SAFE_ID = re.compile(r"[^A-Za-z0-9_.-]+")


class RotationError(RuntimeError):
    """A safe refusal: no destructive/superseding action should follow."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime | None = None) -> str:
    value = value or utc_now()
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_bytes(raw.encode("utf-8"))


def path_digest(records: Iterable[dict[str, Any]]) -> str:
    """Digest touched-path evidence for drift comparison, excluding `size`.

    `size` is retained on each record so append_only_regressions can compare
    frozen vs. live byte length for APPEND_ONLY_PATHS, but it must not
    participate in the strict content-match digest: a volatile shared file's
    size legitimately changes from concurrent unrelated activity (the same
    reason its sha256 is nulled in stable_path_evidence), and including it
    here would silently reintroduce false drift through a second field.
    """
    stripped = [{k: v for k, v in dict(row).items() if k != "size"} for row in records]
    return canonical_digest(stripped)


def rotation_advice(
    used_tokens: int | None,
    *,
    context_window: int | None = None,
    threshold_tokens: int = DEFAULT_THRESHOLD_TOKENS,
) -> dict[str, Any]:
    """Classify a current-context estimate without treating cumulative usage as context."""
    if threshold_tokens <= 0:
        raise ValueError("threshold_tokens must be positive")
    if used_tokens is None or used_tokens < 0:
        return {
            "state": "unknown",
            "used_tokens": used_tokens,
            "threshold_tokens": threshold_tokens,
            "soft_at": None,
            "rotate_at": None,
            "used_percent": None,
        }
    rotate_at = threshold_tokens
    soft_at = int(threshold_tokens * 0.80)
    used_percent = None
    if context_window and context_window > 0:
        rotate_at = min(rotate_at, int(context_window * HARD_FRACTION))
        soft_at = min(soft_at, int(context_window * SOFT_FRACTION))
        used_percent = round((used_tokens / context_window) * 100, 1)
    state = "rotation_due" if used_tokens >= rotate_at else (
        "checkpoint_due" if used_tokens >= soft_at else "below_threshold"
    )
    return {
        "state": state,
        "used_tokens": used_tokens,
        "context_window": context_window,
        "threshold_tokens": threshold_tokens,
        "soft_at": soft_at,
        "rotate_at": rotate_at,
        "used_percent": used_percent,
    }


def agent_advice(agent: str, *, threshold_tokens: int = DEFAULT_THRESHOLD_TOKENS) -> dict[str, Any]:
    from MAP_System.scripts.agent_token_status import build_status

    status = build_status(recent_hours=0)
    row = next((item for item in status.get("agents", []) if item.get("name") == agent), None)
    if row is None:
        raise RotationError(f"agent not found in live token status: {agent}")
    metrics = row.get("metrics") or {}
    tool = row.get("tool")
    if tool == "codex":
        used = metrics.get("last_tokens")
        window = metrics.get("context_window")
        source = "codex_last_context_tokens"
    elif tool == "claude":
        used = metrics.get("latest_context_tokens")
        window = metrics.get("context_window")
        source = "claude_latest_prompt_input_estimate"
    else:
        used = None
        window = None
        source = "unavailable"
    return {
        "agent": agent,
        "tool": tool,
        "metric_source": source,
        **rotation_advice(used, context_window=window, threshold_tokens=threshold_tokens),
    }


def _empty_master() -> dict[str, Any]:
    return {"schema_version": 1, "revision": 0, "updated_at": None,
            "rotations": {}, "history": []}


def parse_master(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _empty_master()
    text = path.read_text(encoding="utf-8")
    start = text.find(MASTER_PREFIX)
    if start < 0:
        raise RotationError(f"master ledger missing embedded state marker: {path}")
    start += len(MASTER_PREFIX)
    end = text.find(MASTER_SUFFIX, start)
    if end < 0:
        raise RotationError(f"master ledger state marker is unterminated: {path}")
    try:
        state = json.loads(text[start:end])
    except json.JSONDecodeError as exc:
        raise RotationError(f"master ledger embedded state is invalid JSON: {exc}") from exc
    if state.get("schema_version") != 1 or not isinstance(state.get("rotations"), dict):
        raise RotationError("unsupported master ledger schema")
    state.setdefault("history", [])
    if not isinstance(state["history"], list):
        raise RotationError("master ledger history must be a list")
    return state


def render_master(state: dict[str, Any]) -> str:
    updated = state.get("updated_at") or "1970-01-01T00:00:00Z"
    date = str(updated)[:10]
    embedded = json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False)
    lines = [
        "<!-- hpom: file: shared/context-continuity.md -->",
        "<!-- hpom: project: MAP -->",
        "<!-- hpom: state_owner: context-rotation -->",
        "<!-- hpom: status: CURRENT -->",
        f"<!-- hpom: last_verified: {date} -->",
        "<!-- hpom: verified_against: TASK-271 context rotation ledger validator -->",
        "<!-- hpom: confidence: HIGH -->",
        "<!-- hpom: supersedes: NONE -->",
        "<!-- hpom: superseded_by: NONE -->",
        "",
        "# Context Continuity Ledger",
        "",
        "Generated by `scripts/context_rotation.py`. Do not hand-edit. Each row",
        "points at an immutable snapshot; the embedded state below is the same",
        "data the validator reads. SQLite, task files, and decisions remain",
        "canonical. This ledger detects continuity drift; it does not override it.",
        "",
        f"- revision: {state.get('revision', 0)}",
        f"- updated_at: {updated}",
        "",
        "| Old agent | Phase | Snapshot | SHA-256 | Replacement | Updated |",
        "|---|---|---|---|---|---|",
    ]
    rotations = state.get("rotations", {})
    for agent in sorted(rotations):
        entry = rotations[agent]
        replacement = (entry.get("ack") or {}).get("replacement_agent") or "-"
        lines.append(
            f"| `{agent}` | {entry.get('phase', '?')} | "
            f"`{entry.get('snapshot_path', '?')}` | `{entry.get('snapshot_sha256', '?')[:12]}…` | "
            f"`{replacement}` | {entry.get('updated_at', '-')} |"
        )
    if not rotations:
        lines.append("| - | no rotations recorded | - | - | - | - |")
    history = state.get("history", [])
    lines.extend(["", "## Prior Attempts", ""])
    if history:
        for prior in history:
            lines.append(
                f"- `{prior.get('old_agent', '?')}` {prior.get('phase', '?')}: "
                f"`{prior.get('snapshot_path', '?')}` ({prior.get('snapshot_sha256', '?')[:12]}…)"
            )
    else:
        lines.append("- None.")
    lines.extend(["", MASTER_PREFIX.rstrip("\n"), embedded + MASTER_SUFFIX, ""])
    return "\n".join(lines)


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw_tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp = Path(raw_tmp)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


@contextlib.contextmanager
def rotation_lock(path: Path = DEFAULT_LOCK):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _task_ids(snapshot: dict[str, Any]) -> list[str]:
    context = snapshot.get("task_context") or {}
    values: list[Any] = [context.get("current_task")]
    values.extend(context.get("owned_tasks") or [])
    values.extend(context.get("pending_reviews") or [])
    values.extend(item.get("task_id") for item in snapshot.get("forward_tasks") or [] if isinstance(item, dict))
    return sorted({str(value) for value in values if value})


def capture_tasks(db_path: Path, task_ids: Iterable[str]) -> list[dict[str, Any]]:
    task_ids = sorted(set(task_ids))
    if not task_ids:
        return []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        result = []
        for task_id in task_ids:
            row = conn.execute(
                "SELECT task_id,status,owner,claimed_by,lease_expires_at,heartbeat_at,updated_at "
                "FROM tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise RotationError(f"snapshot references unknown task: {task_id}")
            result.append(dict(row))
        return result


def active_claims(db_path: Path, agent: str) -> list[str]:
    with sqlite3.connect(db_path) as conn:
        return [
            row[0]
            for row in conn.execute(
                "SELECT task_id FROM tasks WHERE status='IN_PROGRESS' AND claimed_by=? ORDER BY task_id",
                (agent,),
            )
        ]


def _workspace_path(raw: str, repo: Path) -> tuple[Path | None, str]:
    path = Path(raw)
    candidate = path.resolve() if path.is_absolute() else (repo / path).resolve()
    try:
        candidate.relative_to(repo.resolve())
    except ValueError:
        return None, "outside_workspace"
    return candidate, "workspace"


def capture_paths(paths: Iterable[str], repo: Path) -> list[dict[str, Any]]:
    result = []
    for raw in sorted(set(str(item) for item in paths)):
        path, scope = _workspace_path(raw, repo)
        if path is None:
            result.append({"path": raw, "scope": scope, "sha256": None, "size": None, "state": "unverified"})
        elif path.is_file():
            data = path.read_bytes()
            result.append({"path": raw, "scope": scope, "sha256": sha256_bytes(data), "size": len(data), "state": "file"})
        elif path.exists():
            result.append({"path": raw, "scope": scope, "sha256": None, "size": None, "state": "non_file"})
        else:
            result.append({"path": raw, "scope": scope, "sha256": None, "size": None, "state": "missing"})
    return result


def stable_path_evidence(
    records: Iterable[dict[str, Any]], repo: Path, protocol_generated: Iterable[Path]
) -> list[dict[str, Any]]:
    """Normalize files whose exact content is not a meaningful drift signal.

    Two cases are nulled out of the strict content match:

    - protocol-generated files the rotation protocol itself necessarily
      rewrites (e.g. the master ledger). Hashing the master commit pointer
      into the state that rewrites that pointer would be self-referential
      and would guarantee false drift immediately after every prepare.
    - known volatile shared files (VOLATILE_SHARED_PATHS) that legitimately
      mutate from concurrent, unrelated agent/background activity (e.g. a
      limit_watcher checkpoint note appending to events.jsonl). Their exact
      content is not a meaningful signal about the rotating agent's own
      work; `size` is preserved so callers can still catch a regression
      (truncation/corruption) on append-only paths.
    """
    generated = {path.resolve() for path in protocol_generated}
    result = []
    for original in records:
        row = dict(original)
        path, _ = _workspace_path(str(row.get("path", "")), repo)
        resolved = path.resolve() if path is not None else None
        if resolved is not None and resolved in generated:
            row.update({"scope": "protocol_generated", "sha256": None,
                        "state": "tracked_by_ledger_revision"})
        elif str(row.get("path", "")) in VOLATILE_SHARED_PATHS:
            row.update({"scope": "volatile_shared", "sha256": None,
                        "state": "excluded_from_content_match"})
        result.append(row)
    return result


def append_only_regressions(
    expected_paths: Iterable[dict[str, Any]], live_paths: Iterable[dict[str, Any]]
) -> list[str]:
    """Flag a size regression on a path expected to be append-only.

    stable_path_evidence excludes VOLATILE_SHARED_PATHS from the strict
    content match so ordinary concurrent appends do not block a rotation.
    This still catches the failure mode that exclusion would otherwise
    hide: the file got shorter, which append-only writers never do.
    """
    expected_by_path = {str(row.get("path")): row for row in expected_paths}
    issues = []
    for row in live_paths:
        path = str(row.get("path"))
        if path not in APPEND_ONLY_PATHS:
            continue
        expected = expected_by_path.get(path)
        if expected is None:
            continue
        expected_size = expected.get("size")
        live_size = row.get("size")
        if isinstance(expected_size, int) and isinstance(live_size, int) and live_size < expected_size:
            issues.append(f"append_only_shrunk:{path}")
    return issues


def validate_snapshot_v2(snapshot: dict[str, Any], *, expected_agent: str | None = None) -> None:
    required = [
        "kind", "snapshot_version", "created_at", "project_id", "agent_id",
        "session_id", "status", "task_context", "active_constraints",
        "forward_tasks", "lexicon", "rotation",
    ]
    missing = [key for key in required if key not in snapshot]
    if missing:
        raise RotationError(f"snapshot missing required fields: {', '.join(missing)}")
    if snapshot.get("kind") != "STATE_SNAPSHOT" or snapshot.get("snapshot_version") != 2:
        raise RotationError("rotation requires kind=STATE_SNAPSHOT and snapshot_version=2")
    if snapshot.get("status") != "handing_off":
        raise RotationError("rotation snapshot status must be handing_off")
    if expected_agent and snapshot.get("agent_id") != expected_agent:
        raise RotationError(
            f"snapshot agent_id {snapshot.get('agent_id')!r} does not match {expected_agent!r}"
        )
    context = snapshot.get("task_context")
    if not isinstance(context, dict) or not isinstance(context.get("touched_paths", []), list):
        raise RotationError("task_context must be an object and touched_paths must be a list")
    rotation = snapshot.get("rotation")
    if not isinstance(rotation, dict):
        raise RotationError("rotation must be an object")
    for key in ("reason", "summary", "next_action", "used_tokens", "threshold_tokens", "metric_source"):
        if key not in rotation:
            raise RotationError(f"rotation missing required field: {key}")
    if not str(rotation.get("summary") or "").strip() or not str(rotation.get("next_action") or "").strip():
        raise RotationError("rotation summary and next_action must be non-empty")
    used = rotation.get("used_tokens")
    threshold = rotation.get("threshold_tokens")
    if not isinstance(used, int) or used < 0 or not isinstance(threshold, int) or threshold <= 0:
        raise RotationError("rotation token values must be non-negative/positive integers")


def prepare_rotation(
    draft_path: Path,
    *,
    agent: str,
    root: Path = ROOT,
    db_path: Path | None = None,
    master_path: Path | None = None,
    lock_path: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    db_path = db_path or root / "map.db"
    master_path = master_path or root / "shared" / "context-continuity.md"
    lock_path = lock_path or root / ".locks" / "context-rotation.lock"
    repo = root.parent
    snapshot = yaml.safe_load(draft_path.read_text(encoding="utf-8"))
    if not isinstance(snapshot, dict):
        raise RotationError("snapshot draft must contain one YAML object")
    validate_snapshot_v2(snapshot, expected_agent=agent)
    listed_owned = sorted(set(snapshot["task_context"].get("owned_tasks") or []))
    live_claims = active_claims(db_path, agent)
    if listed_owned != live_claims:
        raise RotationError(
            f"owned_tasks must exactly match live IN_PROGRESS claims; draft={listed_owned}, sqlite={live_claims}"
        )

    tasks = capture_tasks(db_path, _task_ids(snapshot))
    paths = stable_path_evidence(
        capture_paths(snapshot["task_context"].get("touched_paths") or [], repo),
        repo, [master_path],
    )
    prepared_at = iso_utc(now)
    snapshot["created_at"] = prepared_at
    snapshot["integrity"] = {
        "prepared_at": prepared_at,
        "canonical_tasks": tasks,
        "canonical_tasks_sha256": canonical_digest(tasks),
        "touched_paths": paths,
        "touched_paths_sha256": path_digest(paths),
    }
    safe_agent = SAFE_ID.sub("-", agent).strip("-")
    stamp = prepared_at.replace("-", "").replace(":", "").replace("T", "T").replace("Z", "Z")
    snapshot_path = root / "handoffs" / f"STATE_SNAPSHOT-{safe_agent}-{stamp}.yaml"
    # Context summaries are durable capture records. Reuse MAP's established
    # redaction guard so a copied credential cannot be preserved merely because
    # it appeared in chat context.
    from MAP_System.scripts.redaction import guard as redaction_guard

    snapshot_text = yaml.safe_dump(snapshot, sort_keys=False, allow_unicode=True)
    snapshot_text = redaction_guard(snapshot_text, f"context rotation {agent}")
    redacted_snapshot = yaml.safe_load(snapshot_text)
    validate_snapshot_v2(redacted_snapshot, expected_agent=agent)
    snapshot = redacted_snapshot
    snapshot_bytes = snapshot_text.encode("utf-8")
    snapshot_hash = sha256_bytes(snapshot_bytes)

    with rotation_lock(lock_path):
        state = parse_master(master_path)
        existing = state["rotations"].get(agent)
        if existing and existing.get("phase") in {"prepared", "acknowledged"}:
            raise RotationError(f"agent already has an unfinished rotation: {existing.get('snapshot_path')}")
        if existing:
            state.setdefault("history", []).append(json.loads(json.dumps(existing)))
        if snapshot_path.exists():
            raise RotationError(f"snapshot already exists: {snapshot_path}")
        _atomic_write(snapshot_path, snapshot_bytes)
        rel_snapshot = str(snapshot_path.relative_to(repo))
        state["revision"] = int(state.get("revision", 0)) + 1
        state["updated_at"] = prepared_at
        state["rotations"][agent] = {
            "phase": "prepared",
            "old_agent": agent,
            "old_session": snapshot.get("session_id"),
            "snapshot_path": rel_snapshot,
            "snapshot_sha256": snapshot_hash,
            "canonical_tasks_sha256": snapshot["integrity"]["canonical_tasks_sha256"],
            "touched_paths_sha256": snapshot["integrity"]["touched_paths_sha256"],
            "used_tokens": snapshot["rotation"]["used_tokens"],
            "threshold_tokens": snapshot["rotation"]["threshold_tokens"],
            "metric_source": snapshot["rotation"]["metric_source"],
            "ack": None,
            "created_at": prepared_at,
            "updated_at": prepared_at,
        }
        _atomic_write(master_path, render_master(state).encode("utf-8"))
    return state["rotations"][agent]


def _entry_snapshot(entry: dict[str, Any], repo: Path) -> tuple[Path, dict[str, Any], str]:
    path = (repo / entry["snapshot_path"]).resolve()
    try:
        path.relative_to(repo.resolve())
    except ValueError as exc:
        raise RotationError("master snapshot path escapes workspace") from exc
    if not path.is_file():
        raise RotationError(f"snapshot missing: {path}")
    raw = path.read_bytes()
    digest = sha256_bytes(raw)
    if digest != entry.get("snapshot_sha256"):
        raise RotationError(f"snapshot hash drift: {entry.get('snapshot_path')}")
    snapshot = yaml.safe_load(raw)
    if not isinstance(snapshot, dict):
        raise RotationError("snapshot is not a YAML object")
    return path, snapshot, digest


def validate_entry(
    entry: dict[str, Any], *, root: Path, db_path: Path, strict_canonical: bool
) -> dict[str, Any]:
    path, snapshot, digest = _entry_snapshot(entry, root.parent)
    validate_snapshot_v2(snapshot, expected_agent=entry.get("old_agent"))
    issues: list[str] = []
    tasks = capture_tasks(db_path, _task_ids(snapshot))
    expected_paths = stable_path_evidence(
        snapshot.get("integrity", {}).get("touched_paths") or [],
        root.parent, [root / "shared" / "context-continuity.md"],
    )
    paths = stable_path_evidence(
        capture_paths(snapshot["task_context"].get("touched_paths") or [], root.parent),
        root.parent, [root / "shared" / "context-continuity.md"],
    )
    task_drift = canonical_digest(tasks) != entry.get("canonical_tasks_sha256")
    path_drift = path_digest(paths) != path_digest(expected_paths)
    if strict_canonical and task_drift:
        issues.append("canonical_task_drift")
    if strict_canonical and path_drift:
        issues.append("touched_path_drift")
    if strict_canonical:
        issues.extend(append_only_regressions(expected_paths, paths))
    return {
        "snapshot_path": str(path),
        "snapshot_sha256": digest,
        "task_drift": task_drift,
        "path_drift": path_drift,
        "issues": issues,
    }


def validate_continuity(
    *, root: Path = ROOT, db_path: Path | None = None, master_path: Path | None = None
) -> dict[str, Any]:
    db_path = db_path or root / "map.db"
    master_path = master_path or root / "shared" / "context-continuity.md"
    state = parse_master(master_path)
    issues: list[str] = []
    if master_path.exists() and master_path.read_text(encoding="utf-8") != render_master(state):
        issues.append("master_render_drift")
    entries = {}
    for agent, entry in sorted(state.get("rotations", {}).items()):
        try:
            result = validate_entry(
                entry,
                root=root,
                db_path=db_path,
                strict_canonical=entry.get("phase") == "prepared",
            )
        except RotationError as exc:
            result = {"issues": [str(exc)]}
        entries[agent] = result
        issues.extend(f"{agent}:{issue}" for issue in result.get("issues", []))
    for index, entry in enumerate(state.get("history", [])):
        label = f"history:{index}:{entry.get('old_agent', '?')}"
        try:
            result = validate_entry(entry, root=root, db_path=db_path, strict_canonical=False)
        except RotationError as exc:
            result = {"issues": [str(exc)]}
        entries[label] = result
        issues.extend(f"{label}:{issue}" for issue in result.get("issues", []))
    return {"ok": not issues, "issues": issues, "entries": entries, "revision": state.get("revision", 0)}


def abandon_rotation(
    *, old_agent: str, reason: str, root: Path = ROOT,
    master_path: Path | None = None, lock_path: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Abandon an unacknowledged attempt without deleting its snapshot."""
    if not reason.strip():
        raise RotationError("abandon reason must be non-empty")
    master_path = master_path or root / "shared" / "context-continuity.md"
    lock_path = lock_path or root / ".locks" / "context-rotation.lock"
    when = iso_utc(now)
    with rotation_lock(lock_path):
        state = parse_master(master_path)
        entry = state.get("rotations", {}).get(old_agent)
        if not entry or entry.get("phase") != "prepared" or entry.get("ack"):
            raise RotationError("only an unacknowledged prepared rotation may be abandoned")
        entry["phase"] = "abandoned"
        entry["abandoned_at"] = when
        entry["abandon_reason"] = reason.strip()
        entry["updated_at"] = when
        state["revision"] += 1
        state["updated_at"] = when
        _atomic_write(master_path, render_master(state).encode("utf-8"))
        return entry


def live_agent_sessions() -> dict[str, str]:
    try:
        result = subprocess.run(
            ["hcom", "list", "--json"], cwd=REPO, text=True,
            capture_output=True, timeout=15, check=False,
        )
        rows = json.loads(result.stdout) if result.returncode == 0 else []
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return {}
    return {
        str(row["name"]): str(row["session_id"])
        for row in rows
        if row.get("name") and row.get("session_id")
        and row.get("process_bound") is not False
    }


def _require_master_render_clean(master_path: Path, state: dict[str, Any], action: str) -> None:
    if master_path.exists() and master_path.read_text(encoding="utf-8") != render_master(state):
        raise RotationError(f"{action} refused: master_render_drift")


def acknowledge_rotation(
    *,
    old_agent: str,
    replacement_agent: str,
    replacement_session: str,
    snapshot_sha256: str,
    root: Path = ROOT,
    db_path: Path | None = None,
    master_path: Path | None = None,
    lock_path: Path | None = None,
    live_agents: dict[str, str] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    if replacement_agent == old_agent:
        raise RotationError("replacement must be a fresh agent identity")
    db_path = db_path or root / "map.db"
    master_path = master_path or root / "shared" / "context-continuity.md"
    lock_path = lock_path or root / ".locks" / "context-rotation.lock"
    live_agents = live_agent_sessions() if live_agents is None else live_agents
    live_session = live_agents.get(replacement_agent)
    if live_session is None:
        raise RotationError(f"replacement agent is not live: {replacement_agent}")
    if live_session != replacement_session:
        raise RotationError(
            f"replacement session does not match live hcom session for {replacement_agent}"
        )
    when = iso_utc(now)
    with rotation_lock(lock_path):
        state = parse_master(master_path)
        _require_master_render_clean(master_path, state, "acknowledgement")
        entry = state.get("rotations", {}).get(old_agent)
        if not entry or entry.get("phase") != "prepared":
            raise RotationError("no prepared rotation is awaiting acknowledgement")
        if snapshot_sha256 != entry.get("snapshot_sha256"):
            raise RotationError("replacement acknowledged the wrong snapshot hash")
        validation = validate_entry(entry, root=root, db_path=db_path, strict_canonical=True)
        if validation["issues"]:
            raise RotationError("pre-resume drift blocks acknowledgement: " + ",".join(validation["issues"]))
        _register_replacement_agent(replacement_agent, db_path)
        entry["phase"] = "acknowledged"
        entry["ack"] = {
            "replacement_agent": replacement_agent,
            "replacement_session": replacement_session,
            "snapshot_sha256": snapshot_sha256,
            "acknowledged_at": when,
        }
        entry["updated_at"] = when
        state["revision"] += 1
        state["updated_at"] = when
        _atomic_write(master_path, render_master(state).encode("utf-8"))
        return entry


def _run_exporter(root: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(root / "migration" / "export_to_files.py")],
        cwd=root.parent, text=True, capture_output=True, timeout=60, check=False,
    )
    if result.returncode != 0:
        raise RotationError(f"mirror export failed: {result.stderr.strip()}")


def _is_mirror_write(db_path: Path) -> bool:
    """True when db_path is the production map.db on a configured mirror host.

    A fixture/test database (any path other than the real production map.db)
    always writes locally, matching db/authority.guard_production_write's own
    exemption -- see test_mirror_guard_blocks_only_production_database. Only
    the real production db on a host configured with mode=mirror (TASK-298:
    KUDU mirrors RUKI's single writable map.db) needs to route through the
    map-authority gateway instead of a direct sqlite3 write.
    """
    from MAP_System.db.authority import is_production_db, load_authority_config

    if not is_production_db(db_path):
        return False
    return load_authority_config().get("mode") == "mirror"


def _run_authority_operation(operation: str, args: list[str], *, root: Path = ROOT) -> dict[str, Any]:
    completed = subprocess.run(
        [str(root / ".venv" / "bin" / "python"), str(root / "scripts" / "map_authority.py"), operation, *args],
        cwd=root.parent, text=True, capture_output=True, timeout=60, check=False,
    )
    if completed.returncode != 0:
        raise RotationError(
            f"map-authority {operation} failed: {(completed.stderr or completed.stdout).strip()}"
        )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RotationError(f"map-authority {operation} returned invalid JSON: {exc}") from exc


def _register_replacement_agent(replacement_agent: str, db_path: Path) -> None:
    if _is_mirror_write(db_path):
        response = _run_authority_operation("register-agent", [replacement_agent])
        if not response.get("ok"):
            raise RotationError(f"register-agent refused: {response.get('error') or response}")
        return
    from MAP_System.db.claims import register_agent

    register_agent(replacement_agent, db_path=db_path)


def _transfer_claims(
    old_agent: str, replacement_agent: str, expected_claims: list[str], db_path: Path
) -> str:
    """Returns an opaque transfer_id (TASK-307 security fix) that
    _restore_claims can later reference to undo exactly this transfer -- the
    caller never holds or re-transmits raw row data."""
    if _is_mirror_write(db_path):
        response = _run_authority_operation(
            "rotation-transfer", [old_agent, replacement_agent, *expected_claims]
        )
        if not response.get("ok"):
            raise RotationError(f"finalize refused: {response.get('error') or response}")
        return response["transfer_id"]
    from MAP_System.db.claims import transfer_rotation_claims

    try:
        snapshot = transfer_rotation_claims(old_agent, replacement_agent, expected_claims, db_path=db_path)
    except ValueError as exc:
        raise RotationError(f"finalize refused: {exc}") from exc
    return snapshot["transfer_id"]


def _restore_claims(transfer_id: str, db_path: Path) -> None:
    if _is_mirror_write(db_path):
        response = _run_authority_operation("rotation-restore", [transfer_id])
        if not response.get("ok"):
            raise RotationError(f"restore refused: {response.get('error') or response}")
        return
    from MAP_System.db.claims import restore_rotation_claims

    restore_rotation_claims(transfer_id, db_path=db_path)


def _close_session(agent: str, root: Path) -> None:
    """Close a superseded agent's terminal pane (bigboss 2026-07-29): rotations
    kept accumulating idle tabs because finalize only ever flipped a DB flag
    and never touched the actual process. Best-effort by design -- the caller
    treats any failure here as non-fatal, since a missing/untracked PID or an
    already-closed pane must never turn a successful finalize into a reported
    failure.
    """
    if shutil.which("hcom") is None:
        return
    subprocess.run(
        ["hcom", "kill", agent],
        cwd=root.parent, text=True, capture_output=True, timeout=15, check=False,
    )


def finalize_rotation(
    *,
    old_agent: str,
    root: Path = ROOT,
    db_path: Path | None = None,
    master_path: Path | None = None,
    lock_path: Path | None = None,
    exporter=None,
    master_writer=None,
    session_closer=None,
    live_agents: dict[str, str] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    db_path = db_path or root / "map.db"
    master_path = master_path or root / "shared" / "context-continuity.md"
    lock_path = lock_path or root / ".locks" / "context-rotation.lock"
    exporter = exporter or (lambda: _run_exporter(root))
    master_writer = master_writer or _atomic_write
    session_closer = session_closer or (lambda agent: _close_session(agent, root))
    when = iso_utc(now)
    with rotation_lock(lock_path):
        state = parse_master(master_path)
        _require_master_render_clean(master_path, state, "finalize")
        entry = state.get("rotations", {}).get(old_agent)
        if not entry or entry.get("phase") != "acknowledged" or not entry.get("ack"):
            raise RotationError("finalize refused: checksum-bound replacement acknowledgement is missing")
        _, snapshot, _ = _entry_snapshot(entry, root.parent)
        replacement = entry["ack"]["replacement_agent"]
        replacement_session = entry["ack"]["replacement_session"]
        live_agents = live_agent_sessions() if live_agents is None else live_agents
        if live_agents.get(replacement) != replacement_session:
            raise RotationError(
                "finalize refused: acknowledged replacement identity/session is no longer live"
            )
        expected_claims = sorted(snapshot["task_context"].get("owned_tasks") or [])
        if active_claims(db_path, old_agent) != expected_claims:
            raise RotationError("finalize refused: live claims drifted after snapshot")

        transfer_id = _transfer_claims(
            old_agent, replacement, expected_claims, db_path
        )

        def restore_canonical_state() -> None:
            _restore_claims(transfer_id, db_path)

        try:
            exporter()
        except Exception as exc:
            # Restore canonical state before reporting failure; the old session
            # remains recoverable and the ledger remains acknowledged.
            restore_canonical_state()
            try:
                exporter()
            except Exception:
                pass
            raise RotationError(f"finalize rolled back after export failure: {exc}") from exc

        entry["phase"] = "finalized"
        entry["finalized_at"] = when
        entry["updated_at"] = when
        state["revision"] += 1
        state["updated_at"] = when
        try:
            master_writer(master_path, render_master(state).encode("utf-8"))
        except Exception as exc:
            # The ledger is the commit pointer. If it cannot advance, restore
            # SQLite and exported mirrors so the acknowledged old session is
            # still authoritative and the protocol can be retried safely.
            restore_canonical_state()
            try:
                exporter()
            except Exception:
                pass
            raise RotationError(f"finalize rolled back after master ledger failure: {exc}") from exc
        # The master ledger is the continuity authority; the ordinary event
        # stream also gets a compact audit pointer when this is a real MAP DB.
        with sqlite3.connect(db_path) as audit_conn:
            has_events = audit_conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='events'"
            ).fetchone()
        if has_events:
            try:
                from MAP_System.scripts.map_task import append_event

                append_event(
                    db_path,
                    root / "events" / "events.jsonl",
                    "HANDOFF",
                    "TASK-271",
                    replacement,
                    (
                        f"Verified context rotation finalized: {old_agent} -> {replacement}; "
                        f"snapshot {entry['snapshot_path']} sha256={entry['snapshot_sha256']}. "
                        f"Transferred claims: {', '.join(expected_claims) or 'none'}."
                    ),
                    [entry["snapshot_path"], "MAP_System/shared/context-continuity.md"],
                )
            except Exception as exc:
                print(f"warning: rotation finalized but audit event append failed: {exc}", file=sys.stderr)
        try:
            session_closer(old_agent)
        except Exception as exc:
            print(f"warning: rotation finalized but closing {old_agent}'s tab failed: {exc}", file=sys.stderr)
        return entry


def notify_agent(advice: dict[str, Any]) -> bool:
    if advice.get("state") not in {"checkpoint_due", "rotation_due"}:
        return False
    prefix = (
        f"REMINDER (you have not rotated since the first notice) -- Context rotation "
        f"{advice['state']}"
        if advice.get("renotify") else f"Context rotation {advice['state']}"
    )
    message = (
        f"{prefix}: current estimate {advice.get('used_tokens')} tokens; "
        f"soft={advice.get('soft_at')} rotate={advice.get('rotate_at')}. "
        "Write and validate a STATE_SNAPSHOT v2, run context_rotation.py prepare, "
        "start a fresh visible session, and do not supersede this session until the replacement ACKs the snapshot hash."
    )
    result = subprocess.run(
        ["hcom", "send", f"@{advice['agent']}", "--intent", "inform", "--from", "limit_watcher", "--", message],
        cwd=REPO, text=True, capture_output=True, timeout=15, check=False,
    )
    return result.returncode == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    advise = sub.add_parser("advise")
    advise.add_argument("--agent", required=True)
    advise.add_argument("--threshold-tokens", type=int, default=DEFAULT_THRESHOLD_TOKENS)
    advise.add_argument("--notify", action="store_true")

    prepare = sub.add_parser("prepare")
    prepare.add_argument("--agent", required=True)
    prepare.add_argument("--draft", type=Path, required=True)

    ack = sub.add_parser("ack")
    ack.add_argument("--old-agent", required=True)
    ack.add_argument("--replacement-agent", required=True)
    ack.add_argument("--replacement-session", required=True)
    ack.add_argument("--snapshot-sha256", required=True)

    finalize = sub.add_parser("finalize")
    finalize.add_argument("--old-agent", required=True)

    abandon = sub.add_parser("abandon")
    abandon.add_argument("--old-agent", required=True)
    abandon.add_argument("--reason", required=True)

    sub.add_parser("validate")

    args = parser.parse_args(argv)
    try:
        if args.command == "advise":
            result = agent_advice(args.agent, threshold_tokens=args.threshold_tokens)
            if args.notify:
                result["notified"] = notify_agent(result)
        elif args.command == "prepare":
            result = prepare_rotation(args.draft, agent=args.agent)
        elif args.command == "ack":
            result = acknowledge_rotation(
                old_agent=args.old_agent,
                replacement_agent=args.replacement_agent,
                replacement_session=args.replacement_session,
                snapshot_sha256=args.snapshot_sha256,
            )
        elif args.command == "finalize":
            result = finalize_rotation(old_agent=args.old_agent)
        elif args.command == "abandon":
            result = abandon_rotation(old_agent=args.old_agent, reason=args.reason)
        else:
            result = validate_continuity()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result.get("ok", True) else 1
    except (OSError, sqlite3.Error, RotationError, ValueError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
