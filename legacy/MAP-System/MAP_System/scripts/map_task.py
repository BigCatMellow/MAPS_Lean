#!/usr/bin/env python3
"""Manage MAP tasks in SQLite and sync file mirrors."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from MAP_System.db.authority import guard_production_write
    from MAP_System.scripts.event_trace import add_trace_fields
    from MAP_System.scripts.validate_task_schema import load_role_registry, normalize_role
except ModuleNotFoundError:  # direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from MAP_System.db.authority import guard_production_write
    from event_trace import add_trace_fields
    from validate_task_schema import load_role_registry, normalize_role

VALIDATE_REVIEW = Path(__file__).resolve().parent / "validate_review.py"
RELEASE_TASK = Path(__file__).resolve().parent / "release_task.py"
VALIDATE_TASK_MIRRORS = Path(__file__).resolve().parent / "validate_task_mirrors.py"


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "map.db"
EXPORTER = ROOT / "migration" / "export_to_files.py"
EVENT_LOG = ROOT / "events" / "events.jsonl"


class UsageError(RuntimeError):
    pass


def connect(db_path: Path) -> sqlite3.Connection:
    guard_production_write(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def project_id(conn: sqlite3.Connection) -> str:
    row = conn.execute("SELECT project_id FROM tasks ORDER BY task_id LIMIT 1").fetchone()
    return row["project_id"] if row else "MAP-BOOTSTRAP-20260617"


def ensure_agent(conn: sqlite3.Connection, agent_id: str | None) -> None:
    if not agent_id:
        return
    conn.execute(
        """
        INSERT OR IGNORE INTO agents (agent_id, label, agent_type, status)
        VALUES (?, ?, 'core', 'available')
        """,
        (agent_id, agent_id.replace("-", " ").title()),
    )


def task_payload(conn: sqlite3.Connection, task_id: str) -> dict[str, Any]:
    task = conn.execute(
        """
        SELECT task_id, project_id, title, description, task_type, role, status,
               priority, required_agent, owner, claimed_by, lease_expires_at,
               heartbeat_at, attempt, max_attempts, created_at, updated_at
        FROM tasks
        WHERE task_id=?
        """,
        (task_id,),
    ).fetchone()
    if task is None:
        raise UsageError(f"unknown task: {task_id}")
    payload = dict(task)
    payload["dependencies"] = [
        row["depends_on"]
        for row in conn.execute(
            "SELECT depends_on FROM task_dependencies WHERE task_id=? ORDER BY depends_on",
            (task_id,),
        )
    ]
    payload["output_paths"] = [
        row["path"]
        for row in conn.execute(
            "SELECT path FROM task_output_paths WHERE task_id=? ORDER BY path",
            (task_id,),
        )
    ]
    payload["acceptance_criteria"] = [
        row["criterion"]
        for row in conn.execute(
            "SELECT criterion FROM task_acceptance_criteria WHERE task_id=? ORDER BY id",
            (task_id,),
        )
    ]
    return payload


def append_event(
    db_path: Path,
    event_log: Path,
    event_type: str,
    task_id: str,
    sender: str,
    summary: str,
    paths: list[str],
) -> None:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    payload = {
        "created_at": created_at,
        "type": event_type,
        "task_id": task_id,
        "sender": sender,
        "summary": summary,
        "artifact_paths": paths,
    }
    add_trace_fields(payload, actor=sender, action=event_type.lower(), target=task_id)
    event_log.parent.mkdir(parents=True, exist_ok=True)
    with event_log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, separators=(",", ":")) + "\n")
    with connect(db_path) as conn:
        ensure_agent(conn, sender)
        conn.execute(
            """
            INSERT OR IGNORE INTO events
                (event_type, task_id, sender_id, summary, artifact_paths, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (event_type, task_id, sender, summary, json.dumps(paths), created_at),
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


def is_review_shape(task_type: str, role: str) -> bool:
    return task_type.lower() == "review" or role.lower() == "reviewer"


def next_task_id(conn: sqlite3.Connection) -> str:
    rows = conn.execute("SELECT task_id FROM tasks WHERE task_id GLOB 'TASK-[0-9]*'").fetchall()
    highest = 0
    for row in rows:
        suffix = str(row["task_id"]).split("-", 1)[-1]
        if suffix.isdigit():
            highest = max(highest, int(suffix))
    return f"TASK-{highest + 1:03d}"


def create_task(args: argparse.Namespace) -> int:
    # Validate before opening the write transaction: unknown roles must not
    # create a task, event, mirror, or any other durable mutation.
    role_id, _ = normalize_role(args.role, load_role_registry())
    if role_id is None:
        raise UsageError(
            f"unknown role {args.role!r}; use a stable role ID or an explicit "
            "historical compatibility alias"
        )
    initial_status = (
        "READY"
        if args.description.strip() and args.output_path and args.criterion
        else "NEEDS_SHAPING"
    )
    with connect(args.db) as conn:
        # Reserve auto IDs under an immediate write lock so concurrent agents do
        # not both read the same highest TASK-NNN before either inserts.
        conn.execute("BEGIN IMMEDIATE")
        task_id = next_task_id(conn) if args.task_id.lower() == "auto" else args.task_id
        if is_review_shape(args.task_type, args.role) and args.owner.lower() == args.actor.lower():
            print(
                f"warning: {task_id} is review-shaped and owner matches actor; "
                "the claim gate will block self-review claims",
                file=sys.stderr,
            )
        if conn.execute("SELECT 1 FROM tasks WHERE task_id=?", (task_id,)).fetchone():
            raise UsageError(f"task already exists: {task_id}")
        ensure_agent(conn, args.owner)
        ensure_agent(conn, args.required_agent)
        conn.execute(
            """
            INSERT INTO tasks
                (task_id, project_id, title, description, task_type, role, status,
                 priority, required_agent, owner, attempt, max_attempts,
                 decision_class, risk_class, risk_severity, task_tier,
                 requires_operator_approval,
                 destructive_action, final_review, final_decision,
                 broad_architecture, broad_rewrite, canonical_map_mutation,
                 shell_required, trust_boundary_crossing)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                project_id(conn),
                args.title,
                args.description or "",
                args.task_type,
                args.role,
                initial_status,
                args.priority,
                args.required_agent,
                args.owner,
                args.max_attempts,
                args.decision_class,
                args.risk_class,
                args.risk_severity,
                args.task_tier,
                int(args.requires_operator_approval),
                1 if args.destructive_action else None,
                1 if args.final_review else None,
                1 if args.final_decision else None,
                1 if args.broad_architecture else None,
                1 if args.broad_rewrite else None,
                1 if args.canonical_map_mutation else None,
                1 if args.shell_required else None,
                1 if args.trust_boundary_crossing else None,
            ),
        )
        for dep in args.depends_on:
            if not conn.execute("SELECT 1 FROM tasks WHERE task_id=?", (dep,)).fetchone():
                raise UsageError(f"unknown dependency: {dep}")
            conn.execute(
                "INSERT INTO task_dependencies (task_id, depends_on) VALUES (?, ?)",
                (task_id, dep),
            )
        for path in args.output_path:
            conn.execute(
                "INSERT INTO task_output_paths (task_id, path) VALUES (?, ?)",
                (task_id, path),
            )
        for criterion in args.criterion:
            conn.execute(
                "INSERT INTO task_acceptance_criteria (task_id, criterion) VALUES (?, ?)",
                (task_id, criterion),
            )
    paths = [f"MAP_System/tasks/{task_id}.json", "MAP_System/workflow/task_graph.json"]
    append_event(args.db, args.event_log, "PROGRESS", task_id, args.actor, f"Created {task_id}: {args.title} ({initial_status})", paths)
    sync_files(args.db, args.output_dir)
    print(json.dumps({"created": task_id}, separators=(",", ":")))
    return 0


def set_review_state(args: argparse.Namespace, *, approved: bool) -> int:
    status = "APPROVED" if approved else "CHANGES_REQUESTED"
    event_type = "APPROVED" if approved else "CHANGES_REQUESTED"

    # HPOM-004: review record is mandatory for APPROVED status
    if approved:
        if not getattr(args, "review_record", None):
            raise UsageError(
                "--review-record is required for APPROVED status (HPOM-004); "
                "provide a review record file validated by validate_review.py"
            )
        result = subprocess.run(
            [sys.executable, str(VALIDATE_REVIEW),
             "--review-record", str(args.review_record),
             "--task-id", args.task_id,
             "--db", str(args.db),
             "--reviewer", args.reviewer],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr, end="")
            raise UsageError(f"review record validation failed for {args.task_id}")

    validate_task_mirrors(args.db, args.output_dir)

    try:
        from MAP_System.db.review_authorship import (
            UnknownSubmissionAuthor,
            require_independent_reviewer,
        )
    except ModuleNotFoundError:  # direct script execution
        sys.path.insert(0, str(ROOT.parent))
        from MAP_System.db.review_authorship import (
            UnknownSubmissionAuthor,
            require_independent_reviewer,
        )

    with connect(args.db) as conn:
        task = conn.execute("SELECT status, title FROM tasks WHERE task_id=?", (args.task_id,)).fetchone()
        if task is None:
            raise UsageError(f"unknown task: {args.task_id}")
        if task["status"] != "SUBMITTED":
            raise UsageError(f"{args.task_id} is {task['status']}, not SUBMITTED")
        ensure_agent(conn, args.reviewer)
        try:
            require_independent_reviewer(conn, args.task_id, args.reviewer)
        except (UnknownSubmissionAuthor, PermissionError, ValueError) as exc:
            raise UsageError(str(exc)) from exc
        cursor = conn.execute(
            """
            UPDATE tasks
            SET status=?, claimed_by=NULL, lease_expires_at=NULL, heartbeat_at=NULL,
                updated_at=datetime('now')
            WHERE task_id=? AND status='SUBMITTED'
            """,
            (status, args.task_id),
        )
        if cursor.rowcount != 1:
            raise UsageError(
                f"{args.task_id} terminal review verdict lost atomic arbitration"
            )
        # TASK-199 (IDEA-0017): best-effort release of an open review claim
        # this reviewer holds. Not required -- a reviewer who never called
        # claim_review() can still approve/reject normally.
        conn.execute(
            """
            UPDATE reviews
            SET verdict=?, completed_at=datetime('now')
            WHERE task_id=? AND reviewer_id=? AND completed_at IS NULL
            """,
            (status, args.task_id, args.reviewer),
        )
    summary = (
        f"{args.task_id} approved by {args.reviewer}."
        if approved
        else f"{args.task_id} rejected by {args.reviewer}: {args.reason}"
    )
    append_event(
        args.db,
        args.event_log,
        event_type,
        args.task_id,
        args.reviewer,
        summary,
        [f"MAP_System/tasks/{args.task_id}.json", "MAP_System/workflow/task_graph.json"],
    )
    sync_files(args.db, args.output_dir)
    print(json.dumps({"task_id": args.task_id, "status": status}, separators=(",", ":")))
    return 0


def rework_task(args: argparse.Namespace) -> int:
    with connect(args.db) as conn:
        task = conn.execute("SELECT status, owner FROM tasks WHERE task_id=?", (args.task_id,)).fetchone()
        if task is None:
            raise UsageError(f"unknown task: {args.task_id}")
        if task["status"] != "CHANGES_REQUESTED":
            raise UsageError(f"{args.task_id} is {task['status']}, not CHANGES_REQUESTED")
        ensure_agent(conn, args.actor)
        conn.execute(
            """
            UPDATE tasks
            SET status='READY',
                claimed_by=NULL,
                lease_expires_at=NULL,
                heartbeat_at=NULL,
                updated_at=datetime('now')
            WHERE task_id=?
            """,
            (args.task_id,),
        )
    append_event(
        args.db,
        args.event_log,
        "PROGRESS",
        args.task_id,
        args.actor,
        f"{args.task_id} returned to READY for rework by {args.actor}: {args.reason}",
        [f"MAP_System/tasks/{args.task_id}.json", "MAP_System/workflow/task_graph.json"],
    )
    sync_files(args.db, args.output_dir)
    print(json.dumps({"task_id": args.task_id, "status": "READY"}, separators=(",", ":")))
    return 0


def submit_task_state(args: argparse.Namespace) -> int:
    """Submit the caller's live claim, record it, and synchronize mirrors.

    ``db.claims.submit_task`` owns the guarded SQLite transition and canonical
    event. Agents use this command as the sanctioned lifecycle verb so the
    transition, event-log destination, and human-readable mirrors remain
    synchronized without duplicate event emission in the CLI layer.
    """
    try:
        from MAP_System.db.claims import submit_task as submit_claim
    except ModuleNotFoundError:  # direct script execution
        sys.path.insert(0, str(ROOT.parent))
        from MAP_System.db.claims import submit_task as submit_claim

    actor = args.actor.strip()
    if not actor:
        raise UsageError("--actor must not be blank")

    with connect(args.db) as conn:
        task = conn.execute(
            "SELECT status, claimed_by FROM tasks WHERE task_id=?",
            (args.task_id,),
        ).fetchone()
        if task is None:
            raise UsageError(f"unknown task: {args.task_id}")
        if task["status"] != "IN_PROGRESS" or task["claimed_by"] != actor:
            raise UsageError(
                f"{args.task_id} is not claimed by {actor}: "
                f"status={task['status']}, claimed_by={task['claimed_by']}"
            )
    # The low-level API commits before emitting the canonical event. Passing
    # the CLI-selected log path preserves scratch/test isolation.
    if not submit_claim(
        args.task_id,
        actor,
        db_path=args.db,
        event_log=args.event_log,
    ):
        raise UsageError(
            f"{args.task_id} submission lost its live claim before transition; "
            "no SUBMISSION event was written"
        )

    sync_files(args.db, args.output_dir)
    print(
        json.dumps(
            {"task_id": args.task_id, "status": "SUBMITTED", "submitted_by": actor},
            separators=(",", ":"),
        )
    )
    return 0


def recover_orphan(args: argparse.Namespace) -> int:
    """Return an orphaned IN_PROGRESS task (no claimant, no live lease) to READY."""
    try:
        from MAP_System.db.claims import recover_orphan_task
    except ModuleNotFoundError:  # direct script execution
        sys.path.insert(0, str(ROOT.parent))
        from MAP_System.db.claims import recover_orphan_task

    try:
        result = recover_orphan_task(
            args.task_id, args.actor, args.reason, db_path=args.db
        )
    except ValueError as exc:  # empty actor or reason: report cleanly, not as a traceback
        raise UsageError(str(exc)) from exc
    if result is None:
        with connect(args.db) as conn:
            task = conn.execute(
                "SELECT status, claimed_by, lease_expires_at FROM tasks WHERE task_id=?",
                (args.task_id,),
            ).fetchone()
        if task is None:
            raise UsageError(f"unknown task: {args.task_id}")
        raise UsageError(
            f"{args.task_id} is not an orphan: status={task['status']}, "
            f"claimed_by={task['claimed_by']}, lease_expires_at={task['lease_expires_at']}. "
            "Recovery only applies to IN_PROGRESS with no claimant and no live lease; "
            "use rework (CHANGES_REQUESTED), reject (SUBMITTED), or let the lease expire."
        )

    # Use the normalized actor the recovery returned, never the raw argument:
    # otherwise the agent row, event sender, and summary record a padded
    # identity while the result reports the stripped one, and the five records
    # of "who acted" disagree.
    actor = result["recovered_by"]

    with connect(args.db) as conn:
        ensure_agent(conn, actor)

    append_event(
        args.db,
        args.event_log,
        "PROGRESS",
        args.task_id,
        actor,
        (
            f"{args.task_id} recovered from orphaned IN_PROGRESS to READY by {actor}. "
            f"Prior owner: {result['prior_owner']}. Reason: {result['reason']}"
        ),
        [f"MAP_System/tasks/{args.task_id}.json", "MAP_System/workflow/task_graph.json"],
    )
    sync_files(args.db, args.output_dir)
    print(json.dumps({**result, "status": "READY"}, separators=(",", ":")))
    return 0


def reassign_owner(args: argparse.Namespace) -> int:
    """Change only a nonterminal task's durable owner and record why."""
    try:
        from MAP_System.db.claims import reassign_task_owner
    except ModuleNotFoundError:  # direct script execution
        sys.path.insert(0, str(ROOT.parent))
        from MAP_System.db.claims import reassign_task_owner

    try:
        result = reassign_task_owner(
            args.task_id,
            args.actor,
            args.new_owner,
            args.reason,
            db_path=args.db,
        )
    except ValueError as exc:
        raise UsageError(str(exc)) from exc
    if result is None:
        with connect(args.db) as conn:
            task = conn.execute(
                "SELECT status, owner FROM tasks WHERE task_id=?",
                (args.task_id,),
            ).fetchone()
        if task is None:
            raise UsageError(f"unknown task: {args.task_id}")
        raise UsageError(
            f"{args.task_id} is {task['status']}, not reassignable. "
            "Owner reassignment refuses terminal DONE/RELEASED/RETIRED tasks."
        )

    actor = result["reassigned_by"]
    with connect(args.db) as conn:
        ensure_agent(conn, actor)

    append_event(
        args.db,
        args.event_log,
        "PROGRESS",
        args.task_id,
        actor,
        (
            f"{args.task_id} owner reassigned by {actor}: "
            f"{result['prior_owner']} -> {result['new_owner']}. "
            f"Reason: {result['reason']}"
        ),
        [f"MAP_System/tasks/{args.task_id}.json", "MAP_System/workflow/task_graph.json"],
    )
    sync_files(args.db, args.output_dir)
    print(json.dumps(result, separators=(",", ":")))
    return 0


def extend_attempts(args: argparse.Namespace) -> int:
    """Raise a nonterminal task's max_attempts and record why (TASK-293)."""
    try:
        from MAP_System.db.claims import extend_task_attempts
    except ModuleNotFoundError:  # direct script execution
        sys.path.insert(0, str(ROOT.parent))
        from MAP_System.db.claims import extend_task_attempts

    if (args.max_attempts is None) == (args.add is None):
        raise UsageError("exactly one of --max-attempts or --add is required")

    with connect(args.db) as conn:
        row = conn.execute(
            "SELECT max_attempts FROM tasks WHERE task_id=?", (args.task_id,)
        ).fetchone()
    if row is None:
        raise UsageError(f"unknown task: {args.task_id}")

    if args.add is not None:
        if args.add <= 0:
            raise UsageError("--add must be a positive integer")
        new_max_attempts = row["max_attempts"] + args.add
    else:
        new_max_attempts = args.max_attempts

    try:
        result = extend_task_attempts(
            args.task_id, args.actor, new_max_attempts, args.reason, db_path=args.db
        )
    except ValueError as exc:  # blank actor/reason or non-positive target: report cleanly
        raise UsageError(str(exc)) from exc

    if result is None:
        with connect(args.db) as conn:
            task = conn.execute(
                "SELECT status, attempt, max_attempts FROM tasks WHERE task_id=?",
                (args.task_id,),
            ).fetchone()
        raise UsageError(
            f"{args.task_id} extend-attempts refused: status={task['status']}, "
            f"attempt={task['attempt']}, max_attempts={task['max_attempts']}, "
            f"requested={new_max_attempts}. Refuses terminal statuses "
            "(APPROVED/RELEASED/RETIRED/DONE) and lowering max_attempts below "
            "the task's current attempt count."
        )

    actor = result["extended_by"]
    with connect(args.db) as conn:
        ensure_agent(conn, actor)

    append_event(
        args.db,
        args.event_log,
        "PROGRESS",
        args.task_id,
        actor,
        (
            f"{args.task_id} max_attempts extended by {actor}: "
            f"{result['prior_max_attempts']} -> {result['new_max_attempts']} "
            f"(attempt={result['attempt']}). Reason: {result['reason']}"
        ),
        [f"MAP_System/tasks/{args.task_id}.json", "MAP_System/workflow/task_graph.json"],
    )
    sync_files(args.db, args.output_dir)
    print(json.dumps(result, separators=(",", ":")))
    return 0


def retire_task_state(args: argparse.Namespace) -> int:
    """Move a nonterminal task to RETIRED and record why (TASK-295)."""
    try:
        from MAP_System.db.claims import retire_task
    except ModuleNotFoundError:  # direct script execution
        sys.path.insert(0, str(ROOT.parent))
        from MAP_System.db.claims import retire_task

    try:
        result = retire_task(args.task_id, args.actor, args.reason, db_path=args.db)
    except ValueError as exc:  # blank actor/reason: report cleanly, not as a traceback
        raise UsageError(str(exc)) from exc

    if result is None:
        with connect(args.db) as conn:
            task = conn.execute(
                "SELECT status FROM tasks WHERE task_id=?", (args.task_id,)
            ).fetchone()
        if task is None:
            raise UsageError(f"unknown task: {args.task_id}")
        raise UsageError(
            f"{args.task_id} retire refused: status={task['status']}. "
            "Refuses tasks already terminal (DONE/RELEASED/RETIRED); retirement "
            "closes out abandoned or superseded work, it does not reopen or "
            "overwrite a completed one."
        )

    actor = result["retired_by"]
    with connect(args.db) as conn:
        ensure_agent(conn, actor)

    append_event(
        args.db,
        args.event_log,
        "PROGRESS",
        args.task_id,
        actor,
        (
            f"{args.task_id} retired by {actor} (was {result['prior_status']}). "
            f"Reason: {result['reason']}"
        ),
        [f"MAP_System/tasks/{args.task_id}.json", "MAP_System/workflow/task_graph.json"],
    )
    sync_files(args.db, args.output_dir)
    print(json.dumps({**result, "status": "RETIRED"}, separators=(",", ":")))
    return 0


def amend_criteria(args: argparse.Namespace) -> int:
    """Amend one acceptance criterion's text, citing recorded authority (TASK-297)."""
    try:
        from MAP_System.db.claims import amend_task_criterion
    except ModuleNotFoundError:  # direct script execution
        sys.path.insert(0, str(ROOT.parent))
        from MAP_System.db.claims import amend_task_criterion

    try:
        result = amend_task_criterion(
            args.task_id,
            args.criterion_id,
            args.new_text,
            args.actor,
            args.reason,
            args.authority,
            db_path=args.db,
        )
    except ValueError as exc:  # blank field or nonexistent authority: report cleanly
        raise UsageError(str(exc)) from exc

    if result is None:
        with connect(args.db) as conn:
            task = conn.execute(
                "SELECT status FROM tasks WHERE task_id=?", (args.task_id,)
            ).fetchone()
            count = conn.execute(
                "SELECT COUNT(*) FROM task_acceptance_criteria WHERE task_id=?",
                (args.task_id,),
            ).fetchone()[0]
        if task is None:
            raise UsageError(f"unknown task: {args.task_id}")
        raise UsageError(
            f"{args.task_id} amend-criteria refused: status={task['status']}, "
            f"criterion_id={args.criterion_id}, criteria_count={count}. Refuses "
            "terminal statuses (APPROVED/RELEASED/RETIRED/DONE) and an "
            "out-of-range --criterion-id."
        )

    actor = result["amended_by"]
    with connect(args.db) as conn:
        ensure_agent(conn, actor)

    append_event(
        args.db,
        args.event_log,
        "PROGRESS",
        args.task_id,
        actor,
        (
            f"{args.task_id} acceptance criterion {result['criterion_index']} amended by "
            f"{actor}, citing authority {result['authority']}. Reason: {result['reason']}. "
            f"Prior text: {result['old_text']!r}. New text: {result['new_text']!r}."
        ),
        [f"MAP_System/tasks/{args.task_id}.json", "MAP_System/workflow/task_graph.json"],
    )
    sync_files(args.db, args.output_dir)
    print(json.dumps(result, separators=(",", ":")))
    return 0


def describe_task_state(args: argparse.Namespace) -> int:
    """Set a NEEDS_SHAPING task's description, promoting to READY if the
    resulting task now clears the READY gate (TASK-317)."""
    try:
        from MAP_System.db.claims import describe_task
    except ModuleNotFoundError:  # direct script execution
        sys.path.insert(0, str(ROOT.parent))
        from MAP_System.db.claims import describe_task

    try:
        result = describe_task(
            args.task_id, args.actor, args.description, args.reason, db_path=args.db
        )
    except ValueError as exc:  # blank field: report cleanly, not as a traceback
        raise UsageError(str(exc)) from exc

    if result is None:
        with connect(args.db) as conn:
            task = conn.execute(
                "SELECT status FROM tasks WHERE task_id=?", (args.task_id,)
            ).fetchone()
        if task is None:
            raise UsageError(f"unknown task: {args.task_id}")
        raise UsageError(
            f"{args.task_id} describe refused: status={task['status']}. "
            "describe only accepts a task currently in NEEDS_SHAPING."
        )

    actor = result["described_by"]
    with connect(args.db) as conn:
        ensure_agent(conn, actor)

    new_status = "READY" if result["promoted_to_ready"] else "NEEDS_SHAPING"
    append_event(
        args.db,
        args.event_log,
        "PROGRESS",
        args.task_id,
        actor,
        (
            f"{args.task_id} described by {actor}: {result['description']!r}. "
            f"Reason: {result['reason']}. "
            + (
                "Promoted to READY (output_paths and acceptance_criteria already present)."
                if result["promoted_to_ready"]
                else "Still NEEDS_SHAPING (output_paths or acceptance_criteria missing)."
            )
        ),
        [f"MAP_System/tasks/{args.task_id}.json", "MAP_System/workflow/task_graph.json"],
    )
    sync_files(args.db, args.output_dir)
    print(json.dumps({**result, "status": new_status}, separators=(",", ":")))
    return 0


def add_output_path(args: argparse.Namespace) -> int:
    """Register an additional output path on an existing task.

    Fills a real gap: before this, the only sanctioned way to change
    output_paths after `create` was to hand-edit the file mirrors, which a
    later `sync_files()` call (triggered by any other map_task.py command,
    e.g. another task's approve) silently overwrites back to the DB's
    stale value — found live during TASK-141/REPAIR-0005.
    """
    editable_states = {"NEEDS_SHAPING", "READY", "IN_PROGRESS", "CHANGES_REQUESTED"}
    with connect(args.db) as conn:
        row = conn.execute("SELECT status FROM tasks WHERE task_id=?", (args.task_id,)).fetchone()
        if row is None:
            raise UsageError(f"unknown task: {args.task_id}")
        status = row["status"]
        if status not in editable_states:
            raise UsageError(
                f"{args.task_id} is {status}, not editable "
                f"(add-output-path only allows {sorted(editable_states)})"
            )
        exists = conn.execute(
            "SELECT 1 FROM task_output_paths WHERE task_id=? AND path=?",
            (args.task_id, args.path),
        ).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO task_output_paths (task_id, path) VALUES (?, ?)",
                (args.task_id, args.path),
            )
        ensure_agent(conn, args.actor)
    append_event(
        args.db,
        args.event_log,
        "PROGRESS",
        args.task_id,
        args.actor,
        f"{args.task_id} output_paths: registered {args.path}",
        [f"MAP_System/tasks/{args.task_id}.json", "MAP_System/workflow/task_graph.json"],
    )
    sync_files(args.db, args.output_dir)
    print(json.dumps({"task_id": args.task_id, "added": args.path}, separators=(",", ":")))
    return 0


def show_task(args: argparse.Namespace) -> int:
    with connect(args.db) as conn:
        print(json.dumps(task_payload(conn, args.task_id), indent=2))
    return 0


def log_task(args: argparse.Namespace) -> int:
    """Print a readable timeline for a task: record + events + linked artifacts."""
    with connect(args.db) as conn:
        payload = task_payload(conn, args.task_id)

    num = args.task_id.split("-", 1)[-1].lower()  # "052" from "TASK-052"
    artifacts_dir = ROOT / "artifacts"
    handoffs_dir = ROOT / "handoffs"

    reviews = sorted((artifacts_dir / "reviews").glob(f"task{num}*.md"))
    releases = sorted((artifacts_dir / "releases").glob(f"task-{num}*.md"))
    handoffs = sorted(handoffs_dir.glob(f"*TASK-{num.upper()}*.md"))

    events: list[dict] = []
    if args.event_log.exists():
        with args.event_log.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("task_id") == args.task_id:
                    events.append(ev)

    sep = "─" * 60
    print(f"\n{sep}")
    print(f"  TASK LOG  {args.task_id}: {payload['title']}")
    print(sep)

    print(f"\nStatus   : {payload['status']}")
    print(f"Owner    : {payload['owner']}")
    print(f"Type     : {payload['task_type']} / {payload['role']}")
    print(f"Created  : {payload['created_at']}")
    print(f"Updated  : {payload['updated_at']}")

    if payload.get("dependencies"):
        print(f"Deps     : {', '.join(payload['dependencies'])}")

    print("\nAcceptance criteria:")
    for i, c in enumerate(payload.get("acceptance_criteria", []), 1):
        print(f"  {i}. {c}")

    print(f"\n{sep}")
    print(f"  EVENT TIMELINE  ({len(events)} events)")
    print(sep)
    if events:
        for ev in events:
            ts = ev.get("created_at", "?")
            sender = ev.get("sender", "?")
            etype = ev.get("type", "?")
            summary = ev.get("summary", "")
            paths = ev.get("artifact_paths", [])
            print(f"\n[{ts}] {etype}  ({sender})")
            print(f"  {summary}")
            for p in paths:
                print(f"    → {p}")
    else:
        print("  (no events recorded)")

    if reviews or releases or handoffs:
        print(f"\n{sep}")
        print("  LINKED ARTIFACTS")
        print(sep)
        for p in reviews:
            print(f"  review   : MAP_System/artifacts/reviews/{p.name}")
        for p in releases:
            print(f"  release  : MAP_System/artifacts/releases/{p.name}")
        for p in handoffs:
            print(f"  handoff  : MAP_System/handoffs/{p.name}")

    print(f"\n{sep}\n")
    return 0


def release_task_state(args: argparse.Namespace) -> int:
    cmd = [
        sys.executable,
        str(RELEASE_TASK),
        args.task_id,
        "--released-by",
        args.released_by,
        "--checklist",
        str(args.checklist),
        "--db",
        str(args.db),
        "--event-log",
        str(args.event_log),
    ]
    if args.summary:
        cmd.extend(["--summary", args.summary])
    if args.output_dir:
        cmd.extend(["--output-dir", str(args.output_dir)])
    subprocess.run(cmd, cwd=ROOT.parent, check=True)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--event-log", type=Path, default=EVENT_LOG)
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("--task-id", required=True, help="Task ID or 'auto' for the next atomic TASK-NNN")
    create.add_argument("--title", required=True)
    create.add_argument("--owner", required=True)
    create.add_argument("--description", default="")
    create.add_argument("--task-type", default="implementation")
    create.add_argument("--role", default="implementer")
    create.add_argument("--priority", type=int, default=3)
    create.add_argument("--required-agent")
    create.add_argument("--max-attempts", type=int, default=3)
    create.add_argument("--depends-on", nargs="*", default=[])
    create.add_argument("--output-path", action="append", default=[])
    create.add_argument("--criterion", action="append", default=[])
    create.add_argument("--actor", default="map-task")
    create.add_argument("--decision-class", choices=["ARCHITECTURE", "OWNERSHIP", "SCOPE", "AUTHORITY", "POLICY"])
    create.add_argument("--risk-class", choices=["SECURITY", "DATA", "PROCESS", "AVAILABILITY", "KNOWLEDGE"])
    create.add_argument("--risk-severity", choices=["COSMETIC", "DRIFT", "BLOCKING", "STRUCTURAL"])
    create.add_argument("--task-tier", choices=["mechanical", "bounded", "architecture", "policy", "operator"])
    create.add_argument("--requires-operator-approval", action="store_true")
    create.add_argument("--destructive-action", action="store_true")
    create.add_argument("--final-review", action="store_true")
    create.add_argument("--final-decision", action="store_true")
    create.add_argument("--broad-architecture", action="store_true")
    create.add_argument("--broad-rewrite", action="store_true")
    create.add_argument("--canonical-map-mutation", action="store_true")
    create.add_argument("--shell-required", action="store_true")
    create.add_argument("--trust-boundary-crossing", action="store_true")
    create.set_defaults(func=create_task)

    approve = sub.add_parser("approve")
    approve.add_argument("task_id")
    approve.add_argument("--reviewer", required=True)
    approve.add_argument("--review-record", type=Path, default=None,
                         help="Path to review record file (HPOM-004: required for APPROVED status)")
    approve.set_defaults(func=lambda args: set_review_state(args, approved=True))

    reject = sub.add_parser("reject")
    reject.add_argument("task_id")
    reject.add_argument("--reviewer", required=True)
    reject.add_argument("--reason", required=True)
    reject.set_defaults(func=lambda args: set_review_state(args, approved=False))

    rework = sub.add_parser("rework", help="Return a CHANGES_REQUESTED task to READY for revision")
    rework.add_argument("task_id")
    rework.add_argument("--actor", required=True)
    rework.add_argument("--reason", required=True)
    rework.set_defaults(func=rework_task)

    submit = sub.add_parser(
        "submit",
        help="Submit the actor's live claim, append a SUBMISSION event, and sync mirrors",
    )
    submit.add_argument("task_id")
    submit.add_argument("--actor", required=True)
    submit.set_defaults(func=submit_task_state)

    release = sub.add_parser("release")
    release.add_argument("task_id")
    release.add_argument("--released-by", required=True)
    release.add_argument("--checklist", type=Path, required=True)
    release.add_argument("--summary", default="")
    release.set_defaults(func=release_task_state)

    recover = sub.add_parser(
        "recover-orphan",
        help="Return an orphaned IN_PROGRESS task (no claimant, no live lease) to READY",
    )
    recover.add_argument("task_id")
    recover.add_argument("--actor", required=True)
    recover.add_argument("--reason", required=True)
    recover.set_defaults(func=recover_orphan)

    reassign = sub.add_parser(
        "reassign-owner",
        help="Reassign a nonterminal task owner without changing claim state",
    )
    reassign.add_argument("task_id")
    reassign.add_argument("--actor", required=True)
    reassign.add_argument("--new-owner", required=True)
    reassign.add_argument("--reason", required=True)
    reassign.set_defaults(func=reassign_owner)

    extend = sub.add_parser(
        "extend-attempts",
        help="Raise a nonterminal task's max_attempts so a further claim can succeed",
    )
    extend.add_argument("task_id")
    extend.add_argument("--actor", required=True)
    extend.add_argument("--max-attempts", type=int, default=None, help="Absolute new max_attempts")
    extend.add_argument("--add", type=int, default=None, help="Add this many attempts to the current max_attempts")
    extend.add_argument("--reason", required=True)
    extend.set_defaults(func=extend_attempts)

    retire = sub.add_parser(
        "retire",
        help="Move a nonterminal task to RETIRED (abandoned/superseded, not released)",
    )
    retire.add_argument("task_id")
    retire.add_argument("--actor", required=True)
    retire.add_argument("--reason", required=True)
    retire.set_defaults(func=retire_task_state)

    amend = sub.add_parser(
        "amend-criteria",
        help="Amend one acceptance criterion's text, citing recorded DEC/REPAIR authority",
    )
    amend.add_argument("task_id")
    amend.add_argument("--criterion-id", required=True, type=int, help="1-based criterion position")
    amend.add_argument("--new-text", required=True)
    amend.add_argument("--actor", required=True)
    amend.add_argument("--reason", required=True)
    amend.add_argument(
        "--authority", required=True, help="Recorded DEC-NNN or REPAIR-NNNN authorizing this amendment"
    )
    amend.set_defaults(func=amend_criteria)

    describe = sub.add_parser(
        "describe",
        help="Set a NEEDS_SHAPING task's description, promoting to READY if the READY gate now passes",
    )
    describe.add_argument("task_id")
    describe.add_argument("--description", required=True)
    describe.add_argument("--actor", required=True)
    describe.add_argument("--reason", required=True)
    describe.set_defaults(func=describe_task_state)

    add_output = sub.add_parser("add-output-path", help="Register an additional output path on an existing task")
    add_output.add_argument("task_id")
    add_output.add_argument("--path", required=True)
    add_output.add_argument("--actor", required=True)
    add_output.set_defaults(func=add_output_path)

    show = sub.add_parser("show")
    show.add_argument("task_id")
    show.set_defaults(func=show_task)

    log = sub.add_parser("log", help="Print a readable timeline for a task")
    log.add_argument("task_id")
    log.set_defaults(func=log_task)

    return parser.parse_args()


def main() -> int:
    try:
        args = parse_args()
        return args.func(args)
    except (sqlite3.Error, subprocess.CalledProcessError, UsageError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
