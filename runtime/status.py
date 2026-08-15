from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
from typing import Any

from runtime.state import TaskStore
from runtime.state.common import iso_z, parse_time, utc_now

_TASK_STATUSES = (
    "NEEDS_SHAPING",
    "READY",
    "ACTIVE",
    "READY_FOR_REVIEW",
    "CHANGES_REQUESTED",
    "DONE",
    "BLOCKED",
)


def build_status(
    store: TaskStore,
    *,
    now: datetime | None = None,
    recent_limit: int = 10,
) -> dict[str, Any]:
    """Build a disposable operator status view from canonical task DB state."""

    if recent_limit <= 0 or recent_limit > 100:
        raise ValueError("recent_limit must be between 1 and 100")
    current = (now or utc_now()).astimezone(timezone.utc)

    with closing(store._connect()) as conn:
        counts = {status: 0 for status in _TASK_STATUSES}
        for row in conn.execute(
            "SELECT status, COUNT(*) AS count FROM tasks GROUP BY status"
        ).fetchall():
            counts[row["status"]] = int(row["count"])

        active: list[dict[str, Any]] = []
        attention: list[dict[str, Any]] = []
        for row in conn.execute(
            """
            SELECT task_id, title, owner, claimed_by, lease_expires_at,
                   heartbeat_at, attempt, max_attempts
            FROM tasks
            WHERE status = 'ACTIVE'
            ORDER BY task_id
            """
        ).fetchall():
            record = dict(row)
            lease = parse_time(record["lease_expires_at"])
            if lease is None:
                lease_state = "MISSING"
            elif lease <= current:
                lease_state = "EXPIRED"
            else:
                lease_state = "LIVE"
            record["lease_state"] = lease_state
            active.append(record)
            if lease_state != "LIVE":
                attention.append(
                    {
                        "type": "STALE_LEASE",
                        "task_id": record["task_id"],
                        "title": record["title"],
                        "claimed_by": record["claimed_by"],
                        "lease_state": lease_state,
                        "lease_expires_at": record["lease_expires_at"],
                    }
                )

        for row in conn.execute(
            """
            SELECT task_id, title, status, owner, updated_at
            FROM tasks
            WHERE status IN ('READY_FOR_REVIEW', 'BLOCKED')
            ORDER BY task_id
            """
        ).fetchall():
            record = dict(row)
            attention.append(
                {
                    "type": (
                        "REVIEW_NEEDED"
                        if record["status"] == "READY_FOR_REVIEW"
                        else "BLOCKED"
                    ),
                    **record,
                }
            )

        latest_outcomes = conn.execute(
            """
            SELECT o.*
            FROM task_outcomes AS o
            JOIN (
                SELECT task_id, MAX(id) AS max_id
                FROM task_outcomes
                GROUP BY task_id
            ) AS latest ON latest.max_id = o.id
            WHERE o.outcome_status = 'FAILURE'
            ORDER BY o.task_id
            """
        ).fetchall()
        for row in latest_outcomes:
            attention.append(
                {
                    "type": "POST_COMPLETION_FAILURE",
                    "task_id": row["task_id"],
                    "outcome_id": row["id"],
                    "failure_class": row["failure_class"],
                    "escaped_defect": bool(row["escaped_defect"]),
                    "created_at": row["created_at"],
                }
            )

        recent = [
            dict(row)
            for row in conn.execute(
                """
                SELECT id, task_id, event_type, actor, created_at
                FROM task_events
                ORDER BY id DESC
                LIMIT ?
                """,
                (recent_limit,),
            ).fetchall()
        ]

    priority = {
        "BLOCKED": 0,
        "STALE_LEASE": 1,
        "POST_COMPLETION_FAILURE": 2,
        "REVIEW_NEEDED": 3,
    }
    attention.sort(key=lambda item: (priority[item["type"]], item["task_id"]))

    return {
        "generated_at": iso_z(current),
        "tasks": {
            "total": sum(counts.values()),
            "by_status": counts,
        },
        "active": active,
        "attention": attention,
        "recent": recent,
        "coverage": {
            "canonical_task_db": True,
            "communication_hcom": False,
            "recovery_state": False,
            "helper_run_state": False,
            "note": (
                "status v1 is a read-only canonical task-DB projection; omitted "
                "runtime sources are not inferred"
            ),
        },
    }
