#!/usr/bin/env python3
"""Atomic SQLite task-claim helpers for MAP_System."""

from __future__ import annotations

import json
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from MAP_System.scripts.halt_state import dispatch_block_reason_for_task  # noqa: E402
from MAP_System.scripts.pre_dispatch_policy import evaluate_pre_dispatch  # noqa: E402
from MAP_System.db.authority import guard_production_write  # noqa: E402
from MAP_System.db.review_authorship import (  # noqa: E402
    UnknownSubmissionAuthor,
    record_submission_author,
    require_independent_reviewer,
)

DEFAULT_DB = ROOT / "map.db"
DEFAULT_EVENT_LOG = ROOT / "events" / "events.jsonl"
DEFAULT_LEASE_SECONDS = 1800
TERMINAL_TASK_STATUSES = {"DONE", "RELEASED", "RETIRED"}


class ClaimBlocked(RuntimeError):
    """Raised by claim_task_with_reason when a claim violates a MAP gate."""


def connect(db_path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    """Open the task-board database with foreign keys enabled."""
    path = Path(db_path)
    guard_production_write(path)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _lease_modifier(lease_seconds: int) -> str:
    if lease_seconds <= 0:
        raise ValueError("lease_seconds must be positive")
    return f"+{int(lease_seconds)} seconds"


def _is_review_task(row: sqlite3.Row | tuple[str, str] | None) -> bool:
    if row is None:
        return False
    task_type = (row[0] or "").lower()
    role = (row[1] or "").lower()
    return task_type == "review" or role == "reviewer"


def claim_block_reason(
    task_id: str,
    agent_id: str,
    *,
    db_path: str | Path = DEFAULT_DB,
) -> str | None:
    """Return a human-readable claim gate failure reason, or None."""
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT task_id, project_id, title, description, task_type, role, owner
            FROM tasks
            WHERE task_id = ?
            """,
            (task_id,),
        ).fetchone()
        if row is None:
            return "unknown_task"

        task = {
            "task_id": row[0],
            "project_id": row[1],
            "title": row[2],
            "description": row[3],
            "task_type": row[4],
            "role": row[5],
        }
        dispatch_block = dispatch_block_reason_for_task(task)
        if dispatch_block:
            return dispatch_block

        review_row = (row[4], row[5])
        owner = row[6]
        if _is_review_task(review_row) and owner and owner.lower() == agent_id.lower():
            return "self_review"

        has_criteria = conn.execute(
            """
            SELECT 1
            FROM task_acceptance_criteria
            WHERE task_id = ?
              AND trim(criterion) != ''
            LIMIT 1
            """,
            (task_id,),
        ).fetchone()
        if not has_criteria:
            return "missing_acceptance_criteria"

        output_paths = [
            value
            for (value,) in conn.execute(
                "SELECT path FROM task_output_paths WHERE task_id = ? ORDER BY path",
                (task_id,),
            )
        ]
        acceptance_criteria = [
            value
            for (value,) in conn.execute(
                "SELECT criterion FROM task_acceptance_criteria WHERE task_id = ? ORDER BY id",
                (task_id,),
            )
        ]
        task["output_paths"] = output_paths
        task["acceptance_criteria"] = acceptance_criteria
        policy = evaluate_pre_dispatch(task, agent_id)
        if policy["decision"] != "allow":
            return f"policy_{policy['decision']}:{','.join(policy['reasons'])}"

    return None


def claim_task(
    task_id: str,
    agent_id: str,
    *,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
    db_path: str | Path = DEFAULT_DB,
) -> bool:
    """Atomically claim a READY task or an expired in-progress task."""
    if claim_block_reason(task_id, agent_id, db_path=db_path):
        return False
    with connect(db_path) as conn:
        cursor = conn.execute(
            """
            UPDATE tasks
            SET status = 'IN_PROGRESS',
                claimed_by = ?,
                lease_expires_at = datetime('now', ?),
                heartbeat_at = datetime('now'),
                attempt = attempt + 1,
                updated_at = datetime('now')
            WHERE task_id = ?
              AND (
                    status = 'READY'
                    OR (
                        status = 'IN_PROGRESS'
                        AND lease_expires_at IS NOT NULL
                        AND lease_expires_at < datetime('now')
                    )
                  )
              AND attempt < max_attempts
            """,
            (agent_id, _lease_modifier(lease_seconds), task_id),
        )
        return cursor.rowcount == 1


def claim_task_with_reason(
    task_id: str,
    agent_id: str,
    *,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
    db_path: str | Path = DEFAULT_DB,
) -> tuple[bool, str | None]:
    """Claim a task and return a reason when a MAP claim gate blocks it."""
    reason = claim_block_reason(task_id, agent_id, db_path=db_path)
    if reason:
        return False, reason
    claimed = claim_task(task_id, agent_id, lease_seconds=lease_seconds, db_path=db_path)
    return claimed, None if claimed else "not_claimable"


def heartbeat(
    task_id: str,
    agent_id: str,
    *,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
    db_path: str | Path = DEFAULT_DB,
) -> bool:
    """Renew a lease for the agent that currently owns the claim."""
    with connect(db_path) as conn:
        cursor = conn.execute(
            """
            UPDATE tasks
            SET heartbeat_at = datetime('now'),
                lease_expires_at = datetime('now', ?),
                updated_at = datetime('now')
            WHERE task_id = ?
              AND claimed_by = ?
              AND status = 'IN_PROGRESS'
            """,
            (_lease_modifier(lease_seconds), task_id, agent_id),
        )
        return cursor.rowcount == 1


def release_task(
    task_id: str,
    agent_id: str,
    *,
    status: str = "SUBMITTED",
    submission_author: str | None = None,
    db_path: str | Path = DEFAULT_DB,
) -> bool:
    """Release a claimed task, clearing lease fields and setting a final status."""
    if not status:
        raise ValueError("status must not be empty")
    with connect(db_path) as conn:
        cursor = conn.execute(
            """
            UPDATE tasks
            SET status = ?,
                claimed_by = NULL,
                lease_expires_at = NULL,
                heartbeat_at = NULL,
                updated_at = datetime('now')
            WHERE task_id = ?
              AND claimed_by = ?
              AND status = 'IN_PROGRESS'
            """,
            (status, task_id, agent_id),
        )
        if cursor.rowcount == 1 and status == "SUBMITTED":
            record_submission_author(
                conn,
                task_id,
                submission_author if submission_author is not None else agent_id,
            )
        return cursor.rowcount == 1


def submit_task(
    task_id: str,
    agent_id: str,
    *,
    db_path: str | Path = DEFAULT_DB,
    event_log: str | Path | None = None,
) -> bool:
    """Submit a claimed task and record its author after the status commit.

    The Boolean transition contract is unchanged: a guarded update that does
    not match returns ``False`` and emits no event.  Authorship is recorded in
    the same transaction as the guarded status update, so a successful update
    always commits canonical authorship together with the status change; a
    crash after that commit can only lose the subsequent ``SUBMISSION`` event
    append, and can never claim a submission happened when the task row did
    not transition.

    ``event_log`` is explicit for callers that use an isolated database.  When
    omitted, the canonical database uses ``events/events.jsonl`` and any other
    database uses a sibling ``events.jsonl``.  This prevents scratch-DB tests
    from writing into the production event log.
    """
    db_path = Path(db_path)
    actor = agent_id.strip() if agent_id else ""
    if not actor:
        return False

    with connect(db_path) as conn:
        artifact_paths = [
            path
            for (path,) in conn.execute(
                "SELECT path FROM task_output_paths WHERE task_id=? ORDER BY path",
                (task_id,),
            )
        ]

    transitioned = release_task(
        task_id,
        actor,
        status="SUBMITTED",
        submission_author=actor,
        db_path=db_path,
    )
    if not transitioned:
        return False

    resolved_db = db_path.resolve()
    if event_log is None:
        event_log_path = (
            DEFAULT_EVENT_LOG
            if resolved_db == DEFAULT_DB.resolve()
            else db_path.with_name("events.jsonl")
        )
    else:
        event_log_path = Path(event_log)

    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )
    summary = f"{task_id} submitted for independent review by {actor}."
    payload = {
        "created_at": created_at,
        "type": "SUBMISSION",
        "task_id": task_id,
        "sender": actor,
        "summary": summary,
        "artifact_paths": artifact_paths,
        "trace_id": f"task:{task_id}",
        "actor": actor,
        "action": "submission",
        "target": task_id,
    }

    event_log_path.parent.mkdir(parents=True, exist_ok=True)
    with event_log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, separators=(",", ":")) + "\n")

    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO events
                (event_type, task_id, sender_id, summary, artifact_paths, created_at)
            VALUES ('SUBMISSION', ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                actor,
                summary,
                json.dumps(artifact_paths),
                created_at,
            ),
        )
    return True


def expire_leases(*, db_path: str | Path = DEFAULT_DB) -> Sequence[str]:
    """Return expired in-progress claims to READY and return their task IDs."""
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT task_id
            FROM tasks
            WHERE status = 'IN_PROGRESS'
              AND claimed_by IS NOT NULL
              AND lease_expires_at IS NOT NULL
              AND lease_expires_at < datetime('now')
            ORDER BY task_id
            """
        ).fetchall()
        task_ids = [row[0] for row in rows]
        if not task_ids:
            return []
        conn.executemany(
            """
            UPDATE tasks
            SET status = 'READY',
                claimed_by = NULL,
                lease_expires_at = NULL,
                heartbeat_at = NULL,
                updated_at = datetime('now')
            WHERE task_id = ?
            """,
            [(task_id,) for task_id in task_ids],
        )
        return task_ids


def recover_orphan_task(
    task_id: str,
    actor_id: str,
    reason: str,
    *,
    db_path: str | Path = DEFAULT_DB,
) -> dict | None:
    """Return an orphaned IN_PROGRESS task to READY so it can be re-owned.

    An orphan here means status IN_PROGRESS with `claimed_by IS NULL` and no
    live lease. That shape is unreachable by every other recovery path:
    `expire_leases` filters on `claimed_by IS NOT NULL`, `release_task` filters
    on `claimed_by = ?` so NULL never matches, `map_task.py rework` requires
    CHANGES_REQUESTED, and `map_task.py reject` requires SUBMITTED. Since
    AGENTS.md forbids hand-editing SQLite, such a task previously had no exit at
    all -- TASK-186 sat in this state for four days while the advisory monitor
    could see it but nothing could act on it.

    Deliberately narrow. It refuses a task that still has a live claimant or an
    unexpired lease, because those belong to `heartbeat`/`expire_leases` and
    stealing them would let one agent yank work out from under another.

    Returns a dict describing what was recovered, or None when the task does not
    match the orphan shape. Never raises for a non-matching task; raises only on
    a missing reason, since an unexplained recovery is not auditable.
    """
    if not actor_id or not actor_id.strip():
        raise ValueError("actor_id must not be empty: orphan recovery must be attributable")
    if not reason or not reason.strip():
        raise ValueError("reason must not be empty: orphan recovery must be auditable")
    actor_id = actor_id.strip()

    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT status, owner, claimed_by, lease_expires_at
            FROM tasks
            WHERE task_id = ?
            """,
            (task_id,),
        ).fetchone()
        if row is None:
            return None

        status, owner, claimed_by, lease_expires_at = row
        if status != "IN_PROGRESS" or claimed_by is not None:
            return None

        if lease_expires_at is not None:
            still_live = conn.execute(
                "SELECT ? >= datetime('now')", (lease_expires_at,)
            ).fetchone()[0]
            if still_live:
                return None

        cursor = conn.execute(
            """
            UPDATE tasks
            SET status = 'READY',
                claimed_by = NULL,
                lease_expires_at = NULL,
                heartbeat_at = NULL,
                updated_at = datetime('now')
            WHERE task_id = ?
              AND status = 'IN_PROGRESS'
              AND claimed_by IS NULL
            """,
            (task_id,),
        )
        if cursor.rowcount != 1:
            return None

        return {
            "task_id": task_id,
            "prior_owner": owner,
            "prior_status": status,
            "recovered_by": actor_id,
            "reason": reason.strip(),
        }


def reassign_task_owner(
    task_id: str,
    actor_id: str,
    new_owner: str,
    reason: str,
    *,
    db_path: str | Path = DEFAULT_DB,
) -> dict | None:
    """Reassign a nonterminal task's durable owner without changing its claim.

    This is deliberately separate from claiming: `owner` records durable
    accountability, while `claimed_by` and the lease describe who is working
    right now. Reassignment therefore updates only `owner`; it does not touch
    status, claim fields, attempt, or timestamps.

    Returns the normalized ownership change, or None for an unknown or terminal
    task. Blank actor, owner, or reason values raise because an unattributed or
    dangling ownership change is not auditable.
    """
    if not actor_id or not actor_id.strip():
        raise ValueError("actor_id must not be empty: owner reassignment must be attributable")
    if not new_owner or not new_owner.strip():
        raise ValueError("new_owner must not be empty: owner reassignment needs an accountable owner")
    if not reason or not reason.strip():
        raise ValueError("reason must not be empty: owner reassignment must be auditable")

    actor_id = actor_id.strip()
    new_owner = new_owner.strip()
    reason = reason.strip()

    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT status, owner
            FROM tasks
            WHERE task_id = ?
            """,
            (task_id,),
        ).fetchone()
        if row is None:
            return None

        status, prior_owner = row
        if status in TERMINAL_TASK_STATUSES:
            return None

        # Same registration contract as map_task.py ensure_agent() and
        # claim_review(): owner is a foreign key, so sanctioned reassignment
        # must never create a dangling agent reference.
        conn.execute(
            """
            INSERT OR IGNORE INTO agents (agent_id, label, agent_type, status)
            VALUES (?, ?, 'core', 'available')
            """,
            (new_owner, new_owner.replace("-", " ").title()),
        )
        cursor = conn.execute(
            """
            UPDATE tasks
            SET owner = ?
            WHERE task_id = ?
              AND status NOT IN ('DONE', 'RELEASED', 'RETIRED')
              AND owner IS ?
            """,
            (new_owner, task_id, prior_owner),
        )
        if cursor.rowcount != 1:
            return None

        return {
            "task_id": task_id,
            "prior_owner": prior_owner,
            "new_owner": new_owner,
            "reassigned_by": actor_id,
            "reason": reason,
        }


# Tasks in these statuses will never be claimed again, so raising their
# attempt budget has no effect: APPROVED/RELEASED/RETIRED per TASK-293's
# acceptance criteria, plus DONE (validate_task_graph.py's terminal set
# treats it the same way, even though it is a legacy status current code no
# longer produces).
TERMINAL_ATTEMPT_STATUSES = {"APPROVED", "RELEASED", "RETIRED", "DONE"}


def extend_task_attempts(
    task_id: str,
    actor_id: str,
    new_max_attempts: int,
    reason: str,
    *,
    db_path: str | Path = DEFAULT_DB,
) -> dict | None:
    """Raise a task's max_attempts so a further claim can succeed (TASK-293).

    `claim_task` guards every claim with `AND attempt < max_attempts`, so a
    task that exhausts its budget on CHANGES_REQUESTED verdicts is
    permanently unworkable even though `rework` can still move it back to
    READY (REPAIR-0010, REPAIR-0012). Before this verb the only fix was raw
    SQL, which the harness permission classifier now blocks outright since
    it is an unmediated mutation of canonical lifecycle state.

    Deliberately narrow, matching `reassign_task_owner`'s shape: refuses a
    terminal task (see `TERMINAL_ATTEMPT_STATUSES`) and refuses to lower
    `max_attempts` below the task's current `attempt` count, since that
    would let a reviewer's history of CHANGES_REQUESTED verdicts be quietly
    erased by shrinking the budget back under it. Returns None for an
    unknown task, a terminal task, or a refused lowering -- never raises for
    those, since they are ordinary refusals, not usage errors. Raises only
    for a blank actor/reason or a non-positive new_max_attempts, since those
    make the action itself unauditable or meaningless.
    """
    if not actor_id or not actor_id.strip():
        raise ValueError("actor_id must not be empty: attempt-budget extension must be attributable")
    if not reason or not reason.strip():
        raise ValueError("reason must not be empty: attempt-budget extension must be auditable")
    if new_max_attempts is None or new_max_attempts < 1:
        raise ValueError("new_max_attempts must be a positive integer")

    actor_id = actor_id.strip()
    reason = reason.strip()

    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT status, attempt, max_attempts FROM tasks WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            return None

        status, attempt, prior_max_attempts = row
        if status in TERMINAL_ATTEMPT_STATUSES:
            return None
        if new_max_attempts < attempt:
            return None

        cursor = conn.execute(
            """
            UPDATE tasks
            SET max_attempts = ?
            WHERE task_id = ?
              AND status NOT IN ({})
              AND max_attempts = ?
              AND attempt <= ?
            """.format(",".join("?" for _ in TERMINAL_ATTEMPT_STATUSES)),
            (
                new_max_attempts,
                task_id,
                *TERMINAL_ATTEMPT_STATUSES,
                prior_max_attempts,
                new_max_attempts,
            ),
        )
        if cursor.rowcount != 1:
            return None

        return {
            "task_id": task_id,
            "prior_max_attempts": prior_max_attempts,
            "new_max_attempts": new_max_attempts,
            "attempt": attempt,
            "extended_by": actor_id,
            "reason": reason,
        }


def retire_task(
    task_id: str,
    actor_id: str,
    reason: str,
    *,
    db_path: str | Path = DEFAULT_DB,
) -> dict | None:
    """Move a task to RETIRED, closing it out without claiming completion (TASK-295).

    Retirement is for a task whose deliverable is abandoned, superseded, or
    unrecoverable -- e.g. TASK-053's target project no longer existing after
    a host rename, or TASK-241-248 being overwritten serial snapshots folded
    into TASK-254 -- as distinct from `release`, which certifies a live
    deliverable. Before this verb the only way to reach RETIRED was raw SQL:
    sixteen tasks reached RETIRED that way and none went through a gated,
    evented, mirror-synchronized transition, and the harness permission
    classifier now blocks raw SQL against canonical task state outright.

    Deliberately allows retiring from ANY nonterminal status, including
    APPROVED (TASK-053 was APPROVED when retired) and CHANGES_REQUESTED
    (TASK-241-248 were retired while superseded, not completed) -- retirement
    is a closure of abandoned work, not a review verdict, so it does not
    share `extend_task_attempts`'s narrower TERMINAL_ATTEMPT_STATUSES set.
    Refuses a task already in a terminal status (`TERMINAL_TASK_STATUSES`:
    DONE/RELEASED/RETIRED), since retirement closes out live work rather than
    reopening or overwriting a completed one.

    Returns None for an unknown or already-terminal task; never raises for
    those, since they are ordinary refusals matching `reassign_task_owner`/
    `extend_task_attempts`'s shape. Raises only for a blank actor/reason,
    since an unattributed or unexplained retirement is not auditable.
    """
    if not actor_id or not actor_id.strip():
        raise ValueError("actor_id must not be empty: retirement must be attributable")
    if not reason or not reason.strip():
        raise ValueError("reason must not be empty: retirement must be auditable")

    actor_id = actor_id.strip()
    reason = reason.strip()

    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT status FROM tasks WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            return None

        status = row[0]
        if status in TERMINAL_TASK_STATUSES:
            return None

        cursor = conn.execute(
            """
            UPDATE tasks
            SET status = 'RETIRED',
                claimed_by = NULL,
                lease_expires_at = NULL,
                heartbeat_at = NULL,
                updated_at = datetime('now')
            WHERE task_id = ?
              AND status NOT IN ({})
            """.format(",".join("?" for _ in TERMINAL_TASK_STATUSES)),
            (task_id, *TERMINAL_TASK_STATUSES),
        )
        if cursor.rowcount != 1:
            return None

        return {
            "task_id": task_id,
            "prior_status": status,
            "retired_by": actor_id,
            "reason": reason,
        }


def _authority_record_exists(authority: str, *, map_root: Path = ROOT) -> bool:
    """Check that `authority` names a real, recorded DEC-NNN or REPAIR-NNNN.

    DEC records live as `## DEC-NNN: ...` headings in
    `MAP_System/shared/decisions.md`; REPAIR records live as one file per
    record under `MAP_System/repairs/REPAIR-NNNN-*.md`. Only these two
    prefixes are recognized -- anything else (including a plain task_id or
    an agent's own say-so) is not a citable authority for a criterion
    amendment. `map_root` defaults to the real `MAP_System/` root and is
    overridable so callers (tests) can point at an isolated fixture tree.
    """
    if authority.startswith("DEC-"):
        decisions = map_root / "shared" / "decisions.md"
        if not decisions.is_file():
            return False
        needle = f"## {authority}:"
        return any(
            line.startswith(needle) for line in decisions.read_text(encoding="utf-8").splitlines()
        )
    if authority.startswith("REPAIR-"):
        repairs_dir = map_root / "repairs"
        if not repairs_dir.is_dir():
            return False
        return any(repairs_dir.glob(f"{authority}-*.md"))
    return False


def amend_task_criterion(
    task_id: str,
    criterion_index: int,
    new_text: str,
    actor_id: str,
    reason: str,
    authority: str,
    *,
    db_path: str | Path = DEFAULT_DB,
    map_root: Path = ROOT,
) -> dict | None:
    """Amend one acceptance criterion's text, citing recorded authority (TASK-297).

    This is the single most abusable lifecycle mutation in MAP: it is exactly
    how an agent would retroactively lower a bar it failed to clear, leaving
    a task looking cleanly APPROVED against criteria that were rewritten to
    fit the delivery after the fact. It is therefore deliberately harder to
    misuse than the raw-SQL/hand-edit route it replaces:

    - `authority` is REQUIRED and must name a real `DEC-NNN` or `REPAIR-NNNN`
      record (see `_authority_record_exists`); an agent cannot cite itself,
      the amending reason, or nothing at all as its own authorization.
    - The prior criterion text is always returned in full (`old_text`) so the
      caller's event/mirror write preserves it verbatim -- a reader can
      always reconstruct what the task originally promised.
    - Refuses a task in a terminal status (`TERMINAL_ATTEMPT_STATUSES`:
      APPROVED/RELEASED/RETIRED/DONE), matching `extend_task_attempts`'s
      narrower set (not `retire_task`'s), since criteria must not be
      rewritten after a task has already passed or closed review against
      them.

    `criterion_index` is 1-based over the task's own criteria in their
    stored order (matching how criteria are already referred to in task
    descriptions, e.g. "TASK-254's own criterion 4") -- not the shared
    autoincrement `task_acceptance_criteria.id`, which is never exposed to
    callers.

    Returns None for an unknown task, a terminal task, or an out-of-range
    `criterion_index` -- ordinary refusals, matching `retire_task`'s and
    `extend_task_attempts`'s shape. Raises only for blank actor/reason/
    new_text or an authority that does not exist as a recorded DEC/REPAIR,
    since those make the amendment itself unauditable, meaningless, or
    self-authorized.
    """
    if not actor_id or not actor_id.strip():
        raise ValueError("actor_id must not be empty: criterion amendment must be attributable")
    if not reason or not reason.strip():
        raise ValueError("reason must not be empty: criterion amendment must be auditable")
    if not new_text or not new_text.strip():
        raise ValueError("new_text must not be empty")
    if not authority or not authority.strip():
        raise ValueError(
            "authority must not be empty: criterion amendment must cite a recorded "
            "DEC-NNN or REPAIR-NNNN authority"
        )

    actor_id = actor_id.strip()
    reason = reason.strip()
    new_text = new_text.strip()
    authority = authority.strip()

    if not _authority_record_exists(authority, map_root=map_root):
        raise ValueError(
            f"authority {authority!r} does not exist as a recorded DEC-NNN or "
            "REPAIR-NNNN -- an agent cannot self-authorize a criterion amendment"
        )

    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT status FROM tasks WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            return None

        status = row[0]
        if status in TERMINAL_ATTEMPT_STATUSES:
            return None

        criteria = conn.execute(
            "SELECT id, criterion FROM task_acceptance_criteria WHERE task_id = ? ORDER BY id",
            (task_id,),
        ).fetchall()
        if criterion_index < 1 or criterion_index > len(criteria):
            return None
        row_id, old_text = criteria[criterion_index - 1]

        cursor = conn.execute(
            "UPDATE task_acceptance_criteria SET criterion = ? WHERE id = ? AND task_id = ?",
            (new_text, row_id, task_id),
        )
        if cursor.rowcount != 1:
            return None

        return {
            "task_id": task_id,
            "criterion_index": criterion_index,
            "old_text": old_text,
            "new_text": new_text,
            "amended_by": actor_id,
            "reason": reason,
            "authority": authority,
        }


def describe_task(
    task_id: str,
    actor_id: str,
    description: str,
    reason: str,
    *,
    db_path: str | Path = DEFAULT_DB,
) -> dict | None:
    """Set a NEEDS_SHAPING task's description, promoting to READY if it now
    clears the same gate `create_task` applies at creation time (TASK-317).

    `create_task` only reaches READY when description/output_path/criterion
    are all supplied together at creation; a task shaped incrementally (e.g.
    output_paths and acceptance_criteria filled in but description left
    blank, as happened to TASK-316) had no route back to READY afterward --
    the only verbs that touch an existing task's core fields are scoped to
    other purposes (`add_output_path`, `amend_task_criterion`) or later
    lifecycle stages (`rework`, `submit`, `release`). Before this verb the
    only fix was raw SQL (blocked by the harness permission classifier) or
    retiring and recreating the task under a new ID, discarding its history.

    Deliberately the narrowest of the missing-lifecycle-verb fixes: it only
    ever touches a task in NEEDS_SHAPING, and it can only move status
    *forward* to READY, never sideways or backward, and only when the READY
    gate (non-empty description, at least one output_path, at least one
    acceptance_criterion) is satisfied -- it cannot promote an otherwise
    incomplete task. Unlike `amend_task_criterion`, no DEC/REPAIR authority
    citation is required: this cannot retroactively lower a bar a task has
    already been judged against, since a NEEDS_SHAPING task has not yet been
    reviewed against anything.

    Returns None for an unknown task or a task not in NEEDS_SHAPING -- an
    ordinary refusal, not a usage error. Raises only for a blank
    actor/reason/description, since an unattributed or unexplained shaping
    edit is not auditable.
    """
    if not actor_id or not actor_id.strip():
        raise ValueError("actor_id must not be empty: shaping must be attributable")
    if not reason or not reason.strip():
        raise ValueError("reason must not be empty: shaping must be auditable")
    if not description or not description.strip():
        raise ValueError("description must not be empty")

    actor_id = actor_id.strip()
    reason = reason.strip()
    description = description.strip()

    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT status FROM tasks WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            return None
        if row[0] != "NEEDS_SHAPING":
            return None

        cursor = conn.execute(
            "UPDATE tasks SET description = ?, updated_at = datetime('now') "
            "WHERE task_id = ? AND status = 'NEEDS_SHAPING'",
            (description, task_id),
        )
        if cursor.rowcount != 1:
            return None

        has_output_path = (
            conn.execute(
                "SELECT 1 FROM task_output_paths WHERE task_id = ? LIMIT 1",
                (task_id,),
            ).fetchone()
            is not None
        )
        has_criterion = (
            conn.execute(
                "SELECT 1 FROM task_acceptance_criteria WHERE task_id = ? LIMIT 1",
                (task_id,),
            ).fetchone()
            is not None
        )

        promoted = has_output_path and has_criterion
        if promoted:
            conn.execute(
                "UPDATE tasks SET status = 'READY', updated_at = datetime('now') "
                "WHERE task_id = ?",
                (task_id,),
            )

        return {
            "task_id": task_id,
            "description": description,
            "promoted_to_ready": promoted,
            "described_by": actor_id,
            "reason": reason,
        }


def register_agent(
    agent_id: str,
    *,
    db_path: str | Path = DEFAULT_DB,
) -> None:
    """Idempotently register an agent row (INSERT OR IGNORE).

    Extracted from the duplicated inline pattern in claim_review and
    reassign_task_owner so context_rotation.py's ack step can call it
    directly instead of hand-rolling the same SQL a fourth time.
    """
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO agents (agent_id, label, agent_type, status)
            VALUES (?, ?, 'core', 'available')
            """,
            (agent_id, agent_id.replace("-", " ").title()),
        )


def _ensure_rotation_transfers_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS rotation_transfers (
            transfer_id       TEXT PRIMARY KEY,
            old_agent         TEXT NOT NULL,
            replacement_agent TEXT NOT NULL,
            snapshot_json     TEXT NOT NULL,
            created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
            restored_at       TEXT
        )
        """
    )


def transfer_rotation_claims(
    old_agent: str,
    replacement_agent: str,
    task_ids: Sequence[str],
    *,
    db_path: str | Path = DEFAULT_DB,
) -> dict[str, Any]:
    """Atomically transfer live claims from old_agent to replacement_agent
    and flip both agents' lifecycle status (TASK-271 finalize step).

    Records the pre-transfer snapshot (both agent rows, every transferred
    task row) server-side under a fresh, unguessable transfer_id and returns
    only that id. TASK-307 security fix: earlier this returned the raw
    snapshot to the caller, which then had to hand it back verbatim to
    restore_rotation_claims() to undo a failed finalize -- but nothing
    stopped an arbitrary caller with gateway access from fabricating that
    JSON directly and mutating unrelated rows. Binding restore to a
    server-recorded transfer_id closes that: the caller can only reference
    a transfer that really happened, never shape what gets restored.

    Raises ValueError on any integrity mismatch (missing agent/task row,
    claim-transfer race) so partial application never happens silently.

    TASK-307 rework (Smalls-side rereview, codex-lab-vumo): the pre-transfer
    snapshot must be read under the same write lock as the transfer itself.
    BEGIN IMMEDIATE runs first, before any of the SELECTs below, so no
    concurrent writer can change old_row/replacement_row/a task row between
    "what we recorded as the rollback snapshot" and "what we actually
    transferred" -- closing a race where a later restore could silently
    clobber an intervening legitimate write with stale pre-lock state.
    """
    with connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        _ensure_rotation_transfers_table(conn)
        conn.execute("BEGIN IMMEDIATE")
        old_row = conn.execute("SELECT * FROM agents WHERE agent_id=?", (old_agent,)).fetchone()
        replacement_row = conn.execute(
            "SELECT * FROM agents WHERE agent_id=?", (replacement_agent,)
        ).fetchone()
        if old_row is None or replacement_row is None:
            raise ValueError("old or replacement agent is absent from SQLite")
        task_rows = []
        for task_id in task_ids:
            row = conn.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if row is None:
                raise ValueError(f"canonical task disappeared: {task_id}")
            task_rows.append(dict(row))
        snapshot = {
            "old_row": dict(old_row),
            "replacement_row": dict(replacement_row),
            "task_rows": task_rows,
        }
        transfer_id = uuid.uuid4().hex
        conn.execute(
            "INSERT INTO rotation_transfers (transfer_id, old_agent, replacement_agent, snapshot_json) "
            "VALUES (?, ?, ?, ?)",
            (transfer_id, old_agent, replacement_agent, json.dumps(snapshot)),
        )
        for task_id in task_ids:
            cursor = conn.execute(
                "UPDATE tasks SET claimed_by=?, owner=CASE WHEN owner=? THEN ? ELSE owner END, "
                "heartbeat_at=datetime('now'), lease_expires_at=datetime('now','+1800 seconds'), "
                "updated_at=datetime('now') WHERE task_id=? AND status='IN_PROGRESS' AND claimed_by=?",
                (replacement_agent, old_agent, replacement_agent, task_id, old_agent),
            )
            if cursor.rowcount != 1:
                raise ValueError(f"claim transfer race for {task_id}")
        conn.execute(
            "UPDATE agents SET status='inactive',reason='session_superseded',resume_after=NULL,"
            "updated_at=datetime('now') WHERE agent_id=?",
            (old_agent,),
        )
        conn.execute(
            "UPDATE agents SET status='available',reason=NULL,resume_after=NULL,"
            "updated_at=datetime('now') WHERE agent_id=?",
            (replacement_agent,),
        )
        conn.commit()
        return {"transfer_id": transfer_id}


def restore_rotation_claims(
    transfer_id: str,
    *,
    db_path: str | Path = DEFAULT_DB,
) -> None:
    """Undo transfer_rotation_claims by restoring agents/tasks rows to the
    server-recorded pre-transfer snapshot for transfer_id.

    Used when a later finalize step fails after the transfer already
    committed, so the acknowledged old session stays authoritative and the
    protocol can be retried safely.

    TASK-307 security fix: transfer_id is the only input. It must reference
    a transfer_rotation_claims() call that actually happened and has not
    already been restored -- both checked server-side against
    rotation_transfers, never trusting caller-supplied row content. Fails
    closed (ValueError) on an unknown or already-consumed transfer_id, and
    marks the transfer restored so it cannot be replayed.
    """
    with connect(db_path) as conn:
        _ensure_rotation_transfers_table(conn)
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT snapshot_json, restored_at FROM rotation_transfers WHERE transfer_id=?",
            (transfer_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"unknown rotation transfer_id: {transfer_id}")
        snapshot_json, restored_at = row
        if restored_at is not None:
            raise ValueError(f"rotation transfer_id already restored, refusing replay: {transfer_id}")
        snapshot = json.loads(snapshot_json)
        old_row = snapshot["old_row"]
        replacement_row = snapshot["replacement_row"]
        task_rows = snapshot["task_rows"]

        agent_columns = [r[1] for r in conn.execute("PRAGMA table_info(agents)")]
        for saved in (old_row, replacement_row):
            assignments = ",".join(f"{column}=?" for column in agent_columns if column != "agent_id")
            values = [saved[column] for column in agent_columns if column != "agent_id"] + [saved["agent_id"]]
            conn.execute(f"UPDATE agents SET {assignments} WHERE agent_id=?", values)
        task_columns = [r[1] for r in conn.execute("PRAGMA table_info(tasks)")]
        for saved in task_rows:
            assignments = ",".join(f"{column}=?" for column in task_columns if column != "task_id")
            values = [saved[column] for column in task_columns if column != "task_id"] + [saved["task_id"]]
            conn.execute(f"UPDATE tasks SET {assignments} WHERE task_id=?", values)
        conn.execute(
            "UPDATE rotation_transfers SET restored_at=datetime('now') WHERE transfer_id=?",
            (transfer_id,),
        )
        conn.commit()


def claim_review(
    task_id: str,
    reviewer_id: str,
    *,
    db_path: str | Path = DEFAULT_DB,
) -> bool:
    """Atomically claim the review slot for a SUBMITTED task (TASK-199 /
    IDEA-0017): SQLite-arbitrated like claim_task, so two independent
    reviewers can't both start full review work on the same submission
    before either finalizes.

    Returns False when the task doesn't exist, it isn't SUBMITTED, the reviewer
    is the canonical submission author, or another reviewer already holds an
    open claim. Unknown legacy authorship raises ``UnknownSubmissionAuthor`` so
    missing evidence can never be interpreted as independence. The last case is enforced by
    idx_reviews_open_claim, so a genuine race between two concurrent callers
    can only ever let one INSERT succeed.

    Any OTHER integrity failure raises rather than returning False (TASK-270).
    A bare False for an unexpected failure would tell a reviewer to stand down
    for a reason nobody can see -- the exact defect this function was fixed to
    stop. The already-claimed case is identified by re-checking the invariant
    (does an open claim now exist?), not by matching SQLite's error text, so a
    review_id primary-key collision is not mistaken for a taken slot.
    """
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT status FROM tasks WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            return False
        status = row[0]
        if status != "SUBMITTED":
            return False
        try:
            require_independent_reviewer(conn, task_id, reviewer_id)
        except PermissionError:
            return False
        # TASK-270: register the reviewer before inserting. reviews.reviewer_id
        # is a foreign key to agents(agent_id), and this function used to have
        # no registration step while scripts/map_task.py has had ensure_agent
        # all along. An unregistered reviewer therefore hit a FOREIGN KEY
        # violation that the except clause below flattened into a bare False --
        # indistinguishable from "already claimed", which review-guide.md tells
        # reviewers to read as "stand down". Proven live on 2026-07-22: a
        # reviewer self-ejected from an open review queue and the submission
        # stalled with nobody reviewing it. Same INSERT OR IGNORE shape as
        # map_task.py ensure_agent, so identity handling matches across modules.
        conn.execute(
            """
            INSERT OR IGNORE INTO agents (agent_id, label, agent_type, status)
            VALUES (?, ?, 'core', 'available')
            """,
            (reviewer_id, reviewer_id.replace("-", " ").title()),
        )
        review_id = f"REV-{task_id}-{reviewer_id}-{uuid.uuid4().hex[:8]}"
        try:
            conn.execute(
                "INSERT INTO reviews (review_id, task_id, reviewer_id) VALUES (?, ?, ?)",
                (review_id, task_id, reviewer_id),
            )
        except sqlite3.IntegrityError:
            # Classify by the invariant, not by the error text (TASK-270 review).
            # The only integrity failure that means "already claimed" is another
            # agent already holding an OPEN claim on this task, arbitrated by
            # idx_reviews_open_claim. Re-check that directly: if an open claim
            # now exists, this caller lost the slot -> False. If not, the failure
            # was something else (e.g. a reviews.review_id primary-key collision,
            # which also raises "UNIQUE constraint failed" but has nothing to do
            # with the claim slot) and must stay loud, so re-raise.
            open_claim = conn.execute(
                "SELECT 1 FROM reviews WHERE task_id = ? AND completed_at IS NULL",
                (task_id,),
            ).fetchone()
            if open_claim is None:
                raise
            return False
        return True


def get_open_review_claim(
    task_id: str,
    *,
    db_path: str | Path = DEFAULT_DB,
) -> dict | None:
    """Return the open (uncompleted) review claim for a task, or None."""
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT review_id, reviewer_id, created_at
            FROM reviews
            WHERE task_id = ? AND completed_at IS NULL
            """,
            (task_id,),
        ).fetchone()
    if row is None:
        return None
    return {"review_id": row[0], "reviewer_id": row[1], "created_at": row[2]}


def release_review_claim(
    task_id: str,
    reviewer_id: str,
    *,
    verdict: str | None = None,
    summary: str | None = None,
    db_path: str | Path = DEFAULT_DB,
) -> bool:
    """Complete the open review claim held by reviewer_id.

    Returns False (never raises) if no open claim exists for the task or a
    different reviewer holds it -- only the claim holder may release it.
    """
    with connect(db_path) as conn:
        cursor = conn.execute(
            """
            UPDATE reviews
            SET verdict = ?, summary = ?, completed_at = datetime('now')
            WHERE task_id = ? AND reviewer_id = ? AND completed_at IS NULL
            """,
            (verdict, summary, task_id, reviewer_id),
        )
        return cursor.rowcount == 1
