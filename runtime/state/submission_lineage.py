from __future__ import annotations

from contextlib import closing
from typing import Any, Mapping


class SubmissionRunLineageMixin:
    """Read-only helpers for exact explicit submission-attempt/run relationships."""

    @staticmethod
    def _submission_run_link(row: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "task_id": str(row["task_id"]),
            "submission_count": int(row["submission_count"]),
            "run_id": str(row["run_id"]),
            "linked_at": str(row["linked_at"]),
        }

    def get_submission_run_link(
        self, task_id: str, submission_count: int
    ) -> dict[str, Any] | None:
        task_id = task_id.strip() if isinstance(task_id, str) else ""
        if (
            not task_id
            or isinstance(submission_count, bool)
            or not isinstance(submission_count, int)
            or submission_count <= 0
        ):
            return None
        with closing(self._connect()) as conn:
            row = conn.execute(
                """
                SELECT * FROM submission_run_links
                WHERE task_id = ? AND submission_count = ?
                """,
                (task_id, submission_count),
            ).fetchone()
            return self._submission_run_link(row) if row is not None else None

    def list_submission_run_links(self, task_id: str) -> list[dict[str, Any]]:
        task_id = task_id.strip() if isinstance(task_id, str) else ""
        if not task_id:
            return []
        with closing(self._connect()) as conn:
            return [
                self._submission_run_link(row)
                for row in conn.execute(
                    """
                    SELECT * FROM submission_run_links
                    WHERE task_id = ?
                    ORDER BY submission_count
                    """,
                    (task_id,),
                ).fetchall()
            ]

    def submission_run_attribution(self, task_id: str) -> dict[str, Any]:
        """Derive one attribution state per known submission attempt.

        Missing explicit relationships remain UNKNOWN. The method never infers a
        run from timing, worker identity, or the number of runs on the task.
        """
        task_id = task_id.strip() if isinstance(task_id, str) else ""
        if not task_id:
            return {"task_id": task_id, "attempts": [], "complete": False}
        with closing(self._connect()) as conn:
            submission = conn.execute(
                "SELECT submission_count FROM task_submissions WHERE task_id = ?",
                (task_id,),
            ).fetchone()
            if submission is None:
                return {"task_id": task_id, "attempts": [], "complete": True}
            count = int(submission["submission_count"])
            links = {
                int(row["submission_count"]): self._submission_run_link(row)
                for row in conn.execute(
                    """
                    SELECT * FROM submission_run_links
                    WHERE task_id = ?
                    ORDER BY submission_count
                    """,
                    (task_id,),
                ).fetchall()
            }

        attempts = []
        for submission_count in range(1, count + 1):
            link = links.get(submission_count)
            if link is None:
                attempts.append(
                    {
                        "submission_count": submission_count,
                        "state": "UNKNOWN",
                        "run_id": None,
                        "linked_at": None,
                    }
                )
            else:
                attempts.append(
                    {
                        "submission_count": submission_count,
                        "state": "EXPLICIT",
                        "run_id": link["run_id"],
                        "linked_at": link["linked_at"],
                    }
                )
        return {
            "task_id": task_id,
            "attempts": attempts,
            "complete": all(item["state"] == "EXPLICIT" for item in attempts),
        }
