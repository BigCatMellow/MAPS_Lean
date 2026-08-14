"""Durable submission-author identity and no-self-review enforcement.

Absence is deliberately UNKNOWN, never independent.  Callers at review gates
must surface ``UnknownSubmissionAuthor`` and route the task for migration or
operator disposition instead of allowing review to continue.
"""

from __future__ import annotations

import sqlite3


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS task_submission_authorship (
    task_id           TEXT PRIMARY KEY REFERENCES tasks(task_id),
    author_id         TEXT NOT NULL REFERENCES agents(agent_id),
    submission_count  INTEGER NOT NULL DEFAULT 1 CHECK (submission_count > 0),
    first_submitted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    submitted_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
)
"""


class UnknownSubmissionAuthor(RuntimeError):
    """Raised when a submitted task has no canonical author identity."""


def ensure_authorship_schema(conn: sqlite3.Connection) -> None:
    """Apply the additive TASK-278 table for existing databases."""
    conn.execute(CREATE_TABLE_SQL)


def record_submission_author(
    conn: sqlite3.Connection,
    task_id: str,
    author_id: str,
) -> None:
    """Record the current submission author inside the status transaction."""
    author = author_id.strip() if author_id else ""
    if not author:
        raise ValueError("submission author must not be blank")
    ensure_authorship_schema(conn)
    conn.execute(
        """
        INSERT INTO task_submission_authorship (task_id, author_id)
        VALUES (?, ?)
        ON CONFLICT(task_id) DO UPDATE SET
            author_id = excluded.author_id,
            submission_count = task_submission_authorship.submission_count + 1,
            submitted_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
        """,
        (task_id, author),
    )


def get_submission_author(conn: sqlite3.Connection, task_id: str) -> str | None:
    """Return the current canonical author, or None for legacy/unknown state."""
    table = conn.execute(
        """
        SELECT 1 FROM sqlite_master
        WHERE type='table' AND name='task_submission_authorship'
        """
    ).fetchone()
    if table is None:
        return None
    row = conn.execute(
        "SELECT author_id FROM task_submission_authorship WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return None if row is None else row[0]


def require_independent_reviewer(
    conn: sqlite3.Connection,
    task_id: str,
    reviewer_id: str,
) -> str:
    """Return the author or fail closed for unknown/self-review identity."""
    reviewer = reviewer_id.strip() if reviewer_id else ""
    if not reviewer:
        raise ValueError("reviewer identity must not be blank")
    author = get_submission_author(conn, task_id)
    if not author:
        raise UnknownSubmissionAuthor(
            f"{task_id} has UNKNOWN SUBMISSION AUTHOR; review requires "
            "explicit migration evidence or operator disposition"
        )
    if author.casefold() == reviewer.casefold():
        raise PermissionError(
            f"SELF_REVIEW: reviewer '{reviewer}' is canonical submission "
            f"author for {task_id}"
        )
    return author
