#!/usr/bin/env python3
"""Release APPROVED MAP tasks after a completed HPOM checklist."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

try:
    from MAP_System.scripts.event_trace import add_trace_fields
except ModuleNotFoundError:  # direct script execution
    from event_trace import add_trace_fields


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "map.db"
EXPORTER = ROOT / "migration" / "export_to_files.py"
EVENT_LOG = ROOT / "events" / "events.jsonl"
VALIDATE_TASK_MIRRORS = ROOT / "scripts" / "validate_task_mirrors.py"

EMERGENCE_CHECK_RE = re.compile(
    r"^[ \t]*-[ \t]*\[[xX]\][ \t]*Emergence capture considered"
    r"(?:"
    r"[ \t]*$"
    r"|[ \t]+(?:—|-)[ \t]*mechanism:[ \t]*"
    r"(?:sentinel scan|Discovery Agent pass|neither)[ \t]*;"
    r"[ \t]*evidence/reason:(?![ \t]*\[)[ \t]*[^\r\n]*\S[ \t]*$"
    r")",
    re.MULTILINE | re.IGNORECASE,
)

REQUIRED_CHECKS_FULL = {
    "shared-file updates": re.compile(r"^\s*-\s*\[[xX]\]\s*Shared-file updates complete\s*$", re.MULTILINE),
    "decisions recorded": re.compile(r"^\s*-\s*\[[xX]\]\s*Decisions recorded\s*$", re.MULTILINE),
    "follow-up tasks created": re.compile(r"^\s*-\s*\[[xX]\]\s*Follow-up tasks created\s*$", re.MULTILINE),
    "event log entry": re.compile(r"^\s*-\s*\[[xX]\]\s*Event log entry prepared\s*$", re.MULTILINE),
    "emergence capture considered": EMERGENCE_CHECK_RE,
}

# TASK-288/DEC-032: low-risk releases (see classify_release) still need a
# checklist file naming the task, but only the one check DEC-026 made
# mechanically non-optional for every release regardless of risk tier.
REQUIRED_CHECKS_LOW = {
    "emergence capture considered": REQUIRED_CHECKS_FULL["emergence capture considered"],
}

# Back-compat alias: some docs/notes refer to this script's "REQUIRED_CHECKS".
REQUIRED_CHECKS = REQUIRED_CHECKS_FULL

TASK_ID_RE = re.compile(r"task_id\s*:\s*(TASK-\w+)", re.IGNORECASE)

# CHANGE_CONTROL_SYSTEM.md's original rule: the full release checklist is
# mandatory for any task whose output touches shared/, templates/, or
# another system's canonical file. Matched on the output_paths recorded in
# task_output_paths, so it applies even to tasks with no risk_class/
# risk_severity/task_tier classification (most of the pre-TASK-277 backlog).
CANONICAL_FILENAME_RE = re.compile(r"(^|/)(AGENTS\.md|CLAUDE\.md|[A-Z][A-Z0-9_]*_SYSTEM\.md)$")

# TASK-288 independent review (task288-review-valo, 2026-07-28) found that
# the naming-convention regex above misses real MAP_System root-level
# canonical governance docs that don't end in AGENTS.md/CLAUDE.md/
# *_SYSTEM.md. Enumerated explicitly rather than guessed from another
# pattern, so a newly added non-conforming canonical doc has to be added
# here deliberately instead of silently falling through again. This is
# every current MAP_System/*.md file that is not *_SYSTEM.md/AGENTS.md/
# CLAUDE.md and is not README.md (not governance, just descriptive).
CANONICAL_ROOT_DOC_BASENAMES = {
    "AGENT_PERMISSION_LEVELS.md",
    "DECISION_CLASSES.md",
    "DESTRUCTIVE_ACTION_POLICY.md",
    "NEW_PROJECT_WIZARD.md",
}

# notes/review-guide.md's Risk-Tiered Review (2026-07-17): these signals mark
# a task High risk regardless of output path, so it also keeps the full
# checklist even when no canonical path is touched.
HIGH_RISK_SEVERITIES = {"STRUCTURAL", "BLOCKING"}
HIGH_RISK_TASK_TIERS = {"policy", "operator", "architecture"}


class ReleaseError(RuntimeError):
    pass


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS task_release_records (
            task_id         TEXT PRIMARY KEY REFERENCES tasks(task_id),
            checklist_path  TEXT NOT NULL,
            released_by     TEXT NOT NULL REFERENCES agents(agent_id),
            summary         TEXT NOT NULL DEFAULT '',
            release_tier    TEXT NOT NULL DEFAULT 'full',
            tier_reason     TEXT NOT NULL DEFAULT '',
            created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        )
        """
    )
    existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(task_release_records)")}
    if "release_tier" not in existing_cols:
        conn.execute("ALTER TABLE task_release_records ADD COLUMN release_tier TEXT NOT NULL DEFAULT 'full'")
    if "tier_reason" not in existing_cols:
        conn.execute("ALTER TABLE task_release_records ADD COLUMN tier_reason TEXT NOT NULL DEFAULT ''")


def ensure_agent(conn: sqlite3.Connection, agent_id: str) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO agents (agent_id, label, agent_type, status)
        VALUES (?, ?, 'core', 'available')
        """,
        (agent_id, agent_id.replace("-", " ").title()),
    )


def touches_canonical_paths(paths: list[str]) -> list[str]:
    hits = []
    for raw in paths:
        norm = raw.replace("\\", "/")
        segments = norm.split("/")
        basename = segments[-1]
        if any(seg in ("shared", "templates") for seg in segments[:-1]):
            hits.append(raw)
        elif CANONICAL_FILENAME_RE.search(norm):
            hits.append(raw)
        elif basename in CANONICAL_ROOT_DOC_BASENAMES:
            hits.append(raw)
    return hits


def classify_release(conn: sqlite3.Connection, task_id: str) -> tuple[str, str]:
    """Return ("full"|"low", reason) per the reconciled release-tier rule (TASK-288/DEC-032).

    Reconciles notes/review-guide.md's Risk-Tiered Review (skip the standalone
    checklist for low-risk changes) with CHANGE_CONTROL_SYSTEM.md's original
    rule (the checklist is mandatory once output touches shared/, templates/,
    or another system's canonical file). The path rule is checked first and
    alone is enough to require "full" -- it needs no risk classification, so
    it still applies to tasks created before TASK-277 added risk_class/
    risk_severity/task_tier. Explicit high-risk signals on classified tasks
    also force "full" even when no canonical path is touched.
    """
    paths = [
        row["path"]
        for row in conn.execute(
            "SELECT path FROM task_output_paths WHERE task_id = ?", (task_id,)
        ).fetchall()
    ]
    canonical_hits = touches_canonical_paths(paths)
    if canonical_hits:
        return "full", "output touches canonical path(s): " + ", ".join(sorted(canonical_hits))

    meta = conn.execute(
        "SELECT risk_class, risk_severity, task_tier FROM tasks WHERE task_id = ?", (task_id,)
    ).fetchone()
    risk_class = (meta["risk_class"] or "").upper() if meta else ""
    risk_severity = (meta["risk_severity"] or "").upper() if meta else ""
    task_tier = (meta["task_tier"] or "").lower() if meta else ""

    if risk_class == "SECURITY":
        return "full", "risk_class=SECURITY"
    if risk_severity in HIGH_RISK_SEVERITIES:
        return "full", f"risk_severity={risk_severity}"
    if task_tier in HIGH_RISK_TASK_TIERS:
        return "full", f"task_tier={task_tier}"

    return (
        "low",
        f"no canonical-path or high-risk signal (risk_class={meta['risk_class'] if meta else None!r} "
        f"risk_severity={meta['risk_severity'] if meta else None!r} task_tier={meta['task_tier'] if meta else None!r})",
    )


def validate_checklist(path: Path, task_id: str, required_checks: dict[str, re.Pattern] | None = None) -> str:
    if required_checks is None:
        required_checks = REQUIRED_CHECKS_FULL
    if not path.exists():
        raise ReleaseError(f"release checklist not found: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    match = TASK_ID_RE.search(text[:500])
    if not match:
        raise ReleaseError("release checklist is missing task_id header")
    found_id = match.group(1).strip()
    if found_id.upper() != task_id.upper():
        raise ReleaseError(f"release checklist task_id is {found_id}, expected {task_id}")
    missing = [name for name, pattern in required_checks.items() if not pattern.search(text)]
    if missing:
        raise ReleaseError("release checklist incomplete: " + ", ".join(missing))
    return text


def append_event(
    db_path: Path,
    event_log: Path,
    task_id: str,
    released_by: str,
    checklist_path: Path,
    *,
    release_tier: str = "full",
    tier_reason: str = "",
) -> None:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    summary = f"{task_id} released by {released_by} with checklist {checklist_path}."
    if release_tier != "full":
        summary += f" release_tier={release_tier} ({tier_reason})."
    paths = [str(checklist_path), f"MAP_System/tasks/{task_id}.json", "MAP_System/workflow/task_graph.json"]
    payload = {
        "created_at": created_at,
        "type": "RELEASED",
        "task_id": task_id,
        "sender": released_by,
        "summary": summary,
        "artifact_paths": paths,
    }
    add_trace_fields(payload, actor=released_by, action="release", target=task_id)
    event_log.parent.mkdir(parents=True, exist_ok=True)
    with event_log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, separators=(",", ":")) + "\n")
    with connect(db_path) as conn:
        ensure_schema(conn)
        ensure_agent(conn, released_by)
        conn.execute(
            """
            INSERT OR IGNORE INTO events
                (event_type, task_id, sender_id, summary, artifact_paths, created_at)
            VALUES ('RELEASED', ?, ?, ?, ?, ?)
            """,
            (task_id, released_by, summary, json.dumps(paths), created_at),
        )


def sync_files(db_path: Path, output_dir: Path | None) -> None:
    cmd = [sys.executable, str(EXPORTER), "--db", str(db_path)]
    if output_dir:
        cmd.extend(["--output-dir", str(output_dir)])
    subprocess.run(cmd, cwd=ROOT.parent, check=True)


def validate_task_mirrors(db_path: Path, output_dir: Path | None) -> None:
    root = output_dir if output_dir else ROOT
    subprocess.run(
        [sys.executable, str(VALIDATE_TASK_MIRRORS), "--db", str(db_path), "--root", str(root)],
        cwd=ROOT.parent,
        check=True,
    )


def release_task(
    task_id: str,
    released_by: str,
    checklist: Path,
    *,
    db_path: Path = DEFAULT_DB,
    event_log: Path = EVENT_LOG,
    output_dir: Path | None = None,
    summary: str = "",
) -> None:
    with connect(db_path) as conn:
        ensure_schema(conn)
        task = conn.execute("SELECT status FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        if task is None:
            raise ReleaseError(f"unknown task: {task_id}")
        if task["status"] != "APPROVED":
            raise ReleaseError(f"{task_id} is {task['status']}, not APPROVED")
        release_tier, tier_reason = classify_release(conn, task_id)

    required_checks = REQUIRED_CHECKS_FULL if release_tier == "full" else REQUIRED_CHECKS_LOW
    validate_checklist(checklist, task_id, required_checks)
    validate_task_mirrors(db_path, output_dir)
    with connect(db_path) as conn:
        ensure_schema(conn)
        task = conn.execute("SELECT status FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        if task is None:
            raise ReleaseError(f"unknown task: {task_id}")
        if task["status"] != "APPROVED":
            raise ReleaseError(f"{task_id} is {task['status']}, not APPROVED")
        ensure_agent(conn, released_by)
        conn.execute(
            """
            INSERT INTO task_release_records
                (task_id, checklist_path, released_by, summary, release_tier, tier_reason)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (task_id, str(checklist), released_by, summary, release_tier, tier_reason),
        )
        conn.execute(
            """
            UPDATE tasks
            SET status = 'RELEASED',
                claimed_by = NULL,
                lease_expires_at = NULL,
                heartbeat_at = NULL,
                updated_at = datetime('now')
            WHERE task_id = ?
            """,
            (task_id,),
        )
    append_event(
        db_path, event_log, task_id, released_by, checklist,
        release_tier=release_tier, tier_reason=tier_reason,
    )
    sync_files(db_path, output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id")
    parser.add_argument("--released-by", required=True)
    parser.add_argument("--checklist", type=Path, required=True)
    parser.add_argument("--summary", default="")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--event-log", type=Path, default=EVENT_LOG)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        release_task(
            args.task_id,
            args.released_by,
            args.checklist,
            db_path=args.db,
            event_log=args.event_log,
            output_dir=args.output_dir,
            summary=args.summary,
        )
    except (ReleaseError, sqlite3.Error, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"task_id": args.task_id, "status": "RELEASED"}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
