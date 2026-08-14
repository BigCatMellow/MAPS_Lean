from __future__ import annotations

from contextlib import closing
from datetime import datetime, timedelta, timezone

from .common import MutationResult, iso_z, parse_time, utc_now

class ExecutionMixin:
    def claim_task(
        self,
        task_id: str,
        worker_id: str,
        *,
        lease_seconds: int = 900,
        now: datetime | None = None,
        ) -> MutationResult:
        if not worker_id.strip():
            return MutationResult(False, "INVALID_WORKER", "worker_id is required")
        if lease_seconds <= 0:
            return MutationResult(False, "INVALID_LEASE", "lease_seconds must be > 0")
        current = (now or utc_now()).astimezone(timezone.utc)
        expires = current + timedelta(seconds=lease_seconds)

        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if row is None:
                conn.rollback()
                return MutationResult(False, "NOT_FOUND", f"{task_id} does not exist")

            recover = False
            if row["status"] in {"READY", "CHANGES_REQUESTED"} and not row["claimed_by"]:
                pass
            elif row["status"] == "ACTIVE":
                lease = parse_time(row["lease_expires_at"])
                if row["claimed_by"] == worker_id and lease and lease > current:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "ALREADY_CLAIMED",
                        f"{worker_id} already holds a live claim",
                        dict(row),
                    )
                if lease is None or lease > current:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "LEASE_ACTIVE",
                        f"live claim held by {row['claimed_by']}",
                        dict(row),
                    )
                if row["attempt"] >= row["max_attempts"]:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "ATTEMPT_LIMIT",
                        "expired claim cannot be recovered: max attempts reached",
                        dict(row),
                    )
                recover = True
            else:
                conn.rollback()
                return MutationResult(
                    False,
                    "NOT_CLAIMABLE",
                    f"task status is {row['status']}",
                    dict(row),
                )

            event = "TASK_CLAIM_RECOVERED" if recover else "TASK_CLAIMED"
            if recover:
                summary = f"claim moved from {row['claimed_by']} to {worker_id}"
            else:
                summary = f"claimed by {worker_id}"
            conn.execute(
                """
                UPDATE tasks
                SET status = 'ACTIVE', claimed_by = ?, lease_expires_at = ?,
                    heartbeat_at = ?, attempt = attempt + 1, updated_at = ?
                WHERE task_id = ?
                """,
                (
                    worker_id,
                    iso_z(expires),
                    iso_z(current),
                    iso_z(current),
                    task_id,
                ),
            )
            self._append_event(conn, task_id, event, worker_id, summary)
            conn.commit()
        return MutationResult(
            True,
            "RECOVERED" if recover else "CLAIMED",
            summary,
            self.get_task(task_id),
        )

    def heartbeat(
        self,
        task_id: str,
        worker_id: str,
        *,
        lease_seconds: int = 900,
        now: datetime | None = None,
        ) -> MutationResult:
        if lease_seconds <= 0:
            return MutationResult(False, "INVALID_LEASE", "lease_seconds must be > 0")
        current = (now or utc_now()).astimezone(timezone.utc)
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if row is None:
                conn.rollback()
                return MutationResult(False, "NOT_FOUND", f"{task_id} does not exist")
            if row["status"] != "ACTIVE" or row["claimed_by"] != worker_id:
                conn.rollback()
                return MutationResult(
                    False,
                    "NOT_CLAIM_OWNER",
                    "heartbeat requires the active claimant",
                    dict(row),
                )
            lease = parse_time(row["lease_expires_at"])
            if lease is not None and lease <= current:
                conn.rollback()
                return MutationResult(
                    False,
                    "LEASE_EXPIRED",
                    "claim lease has expired",
                    dict(row),
                )
            expires = current + timedelta(seconds=lease_seconds)
            conn.execute(
                """
                UPDATE tasks
                SET heartbeat_at = ?, lease_expires_at = ?, updated_at = ?
                WHERE task_id = ?
                """,
                (iso_z(current), iso_z(expires), iso_z(current), task_id),
            )
            self._append_event(
                conn,
                task_id,
                "TASK_HEARTBEAT",
                worker_id,
                "claim lease renewed",
            )
            conn.commit()
        return MutationResult(True, "HEARTBEAT", "lease renewed", self.get_task(task_id))

    def submit_task(
        self,
        task_id: str,
        worker_id: str,
        evidence: str,
        *,
        now: datetime | None = None,
        ) -> MutationResult:
        if not evidence.strip():
            return MutationResult(
                False,
                "MISSING_EVIDENCE",
                "submission evidence is required",
            )
        current = (now or utc_now()).astimezone(timezone.utc)
        stamp = iso_z(current)
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if row is None:
                conn.rollback()
                return MutationResult(False, "NOT_FOUND", f"{task_id} does not exist")
            if row["status"] != "ACTIVE" or row["claimed_by"] != worker_id:
                conn.rollback()
                return MutationResult(
                    False,
                    "NOT_CLAIM_OWNER",
                    "submission requires the active claimant",
                    dict(row),
                )
            lease = parse_time(row["lease_expires_at"])
            if lease is not None and lease <= current:
                conn.rollback()
                return MutationResult(
                    False,
                    "LEASE_EXPIRED",
                    "claim lease expired before submission",
                    dict(row),
                )

            existing = conn.execute(
                "SELECT * FROM task_submissions WHERE task_id = ?", (task_id,)
            ).fetchone()
            if existing is None:
                conn.execute(
                    """
                    INSERT INTO task_submissions(
                        task_id, author_id, evidence, first_submitted_at, submitted_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (task_id, worker_id, evidence.strip(), stamp, stamp),
                )
            else:
                conn.execute(
                    """
                    UPDATE task_submissions
                    SET author_id = ?, evidence = ?,
                        submission_count = submission_count + 1, submitted_at = ?
                    WHERE task_id = ?
                    """,
                    (worker_id, evidence.strip(), stamp, task_id),
                )

            conn.execute(
                """
                UPDATE tasks
                SET status = 'READY_FOR_REVIEW', claimed_by = NULL,
                    lease_expires_at = NULL, heartbeat_at = NULL, updated_at = ?
                WHERE task_id = ?
                """,
                (stamp, task_id),
            )
            self._append_event(
                conn,
                task_id,
                "TASK_SUBMITTED",
                worker_id,
                "Task submitted with evidence",
            )
            conn.commit()
        return MutationResult(
            True,
            "SUBMITTED",
            f"{task_id} is READY_FOR_REVIEW",
            self.get_task(task_id),
        )
