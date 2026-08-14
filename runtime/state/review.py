from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import sqlite3

from .common import MutationResult, iso_z, utc_now


class ReviewMixin:
    def claim_review(
        self,
        task_id: str,
        reviewer_id: str,
        *,
        now: datetime | None = None,
    ) -> MutationResult:
        if not reviewer_id.strip():
            return MutationResult(
                False,
                "INVALID_REVIEWER",
                "reviewer_id is required",
            )
        stamp = iso_z((now or utc_now()).astimezone(timezone.utc))
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            task = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if task is None:
                conn.rollback()
                return MutationResult(False, "NOT_FOUND", f"{task_id} does not exist")
            if task["status"] != "READY_FOR_REVIEW":
                conn.rollback()
                return MutationResult(
                    False,
                    "NOT_REVIEWABLE",
                    f"task status is {task['status']}",
                    dict(task),
                )
            submission = conn.execute(
                "SELECT * FROM task_submissions WHERE task_id = ?", (task_id,)
            ).fetchone()
            if submission is None:
                conn.rollback()
                return MutationResult(
                    False,
                    "MISSING_SUBMISSION",
                    "review requires durable submission authorship",
                )
            if task["review_required"] != "OWNER_CHECK":
                disqualified = self._continuity_component_conn(
                    conn, submission["author_id"]
                )
                if reviewer_id in disqualified:
                    conn.rollback()
                    code = (
                        "SELF_REVIEW_FORBIDDEN"
                        if reviewer_id == submission["author_id"]
                        else "CONTINUITY_REVIEW_FORBIDDEN"
                    )
                    return MutationResult(
                        False,
                        code,
                        "independent review cannot be claimed by the submission "
                        "author or a continuation identity in the same lineage",
                    )

            try:
                cursor = conn.execute(
                    "INSERT INTO reviews(task_id, reviewer_id, created_at) VALUES (?, ?, ?)",
                    (task_id, reviewer_id, stamp),
                )
            except sqlite3.IntegrityError:
                open_review = conn.execute(
                    """
                    SELECT reviewer_id FROM reviews
                    WHERE task_id = ? AND completed_at IS NULL
                    """,
                    (task_id,),
                ).fetchone()
                conn.rollback()
                holder = open_review["reviewer_id"] if open_review else "another reviewer"
                return MutationResult(
                    False,
                    "REVIEW_ALREADY_CLAIMED",
                    f"open review held by {holder}",
                    dict(task),
                )

            self._append_event(
                conn,
                task_id,
                "REVIEW_CLAIMED",
                reviewer_id,
                f"review {cursor.lastrowid} claimed",
            )
            conn.commit()
        return MutationResult(
            True,
            "REVIEW_CLAIMED",
            f"{reviewer_id} claimed review",
            self.get_task(task_id),
        )

    def record_review(
        self,
        task_id: str,
        reviewer_id: str,
        verdict: str,
        summary: str,
        *,
        now: datetime | None = None,
    ) -> MutationResult:
        verdict = verdict.strip().upper()
        if verdict not in {"APPROVED", "CHANGES_REQUESTED", "BLOCKED"}:
            return MutationResult(
                False,
                "INVALID_VERDICT",
                "verdict must be APPROVED, CHANGES_REQUESTED, or BLOCKED",
            )
        if not summary.strip():
            return MutationResult(
                False,
                "MISSING_REVIEW_SUMMARY",
                "review summary is required",
            )
        stamp = iso_z((now or utc_now()).astimezone(timezone.utc))
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            review = conn.execute(
                """
                SELECT * FROM reviews
                WHERE task_id = ? AND completed_at IS NULL
                """,
                (task_id,),
            ).fetchone()
            if review is None:
                conn.rollback()
                return MutationResult(False, "NO_OPEN_REVIEW", "no open review exists")
            if review["reviewer_id"] != reviewer_id:
                conn.rollback()
                return MutationResult(
                    False,
                    "NOT_REVIEW_OWNER",
                    f"review is claimed by {review['reviewer_id']}",
                )
            task = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if task is None or task["status"] != "READY_FOR_REVIEW":
                conn.rollback()
                return MutationResult(
                    False,
                    "NOT_REVIEWABLE",
                    "task is no longer READY_FOR_REVIEW",
                )
            submission = conn.execute(
                "SELECT * FROM task_submissions WHERE task_id = ?", (task_id,)
            ).fetchone()
            if submission is None:
                conn.rollback()
                return MutationResult(
                    False, "MISSING_SUBMISSION", "review requires durable submission"
                )
            if task["review_required"] != "OWNER_CHECK":
                disqualified = self._continuity_component_conn(
                    conn, submission["author_id"]
                )
                if reviewer_id in disqualified:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "CONTINUITY_REVIEW_FORBIDDEN",
                        "reviewer is no longer independent from submission author",
                    )

            if verdict == "APPROVED":
                criterion_issues = self._criterion_approval_issues_conn(conn, task_id)
                if criterion_issues:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "CRITERION_VERIFICATION_INCOMPLETE",
                        "; ".join(criterion_issues),
                    )

            new_status = {
                "APPROVED": "DONE",
                "CHANGES_REQUESTED": "CHANGES_REQUESTED",
                "BLOCKED": "BLOCKED",
            }[verdict]
            conn.execute(
                """
                UPDATE reviews
                SET verdict = ?, summary = ?, completed_at = ?
                WHERE id = ?
                """,
                (verdict, summary.strip(), stamp, review["id"]),
            )
            conn.execute(
                "UPDATE tasks SET status = ?, updated_at = ? WHERE task_id = ?",
                (new_status, stamp, task_id),
            )
            self._append_event(
                conn,
                task_id,
                f"REVIEW_{verdict}",
                reviewer_id,
                summary.strip(),
            )
            conn.commit()
        return MutationResult(
            True,
            verdict,
            f"{task_id} -> {new_status}",
            self.get_task(task_id),
        )
