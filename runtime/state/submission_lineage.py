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
