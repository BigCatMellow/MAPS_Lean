from __future__ import annotations

from contextlib import closing
import json
import sqlite3
from typing import Any, Mapping

from runtime.operational_learning import OperationalLearningError, validate_lesson_record

from .common import MutationResult


class OperationalLessonStorageMixin:
    """Append-only storage for CANDIDATE-status operational lesson snapshots.

    This is Storage-0 only: there is no promotion/retirement mechanism. The
    schema restricts `status` to 'CANDIDATE' at the SQLite level, and this
    layer rejects any other status before it ever reaches SQL, as defense in
    depth. A future task implements the operator-only promotion mechanism
    separately; it is not authorized by this file.
    """

    @staticmethod
    def _lesson_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "lesson_version": int(row["lesson_version"]),
            "lesson_id": str(row["lesson_id"]),
            "status": str(row["status"]),
            "claim": str(row["claim"]),
            "source_kind": str(row["source_kind"]),
            "source_refs": json.loads(row["source_refs"]),
            "applicability": json.loads(row["applicability"]),
            "created_by": str(row["created_by"]),
            "created_at": str(row["created_at"]),
            "promotion": json.loads(row["promotion"]) if row["promotion"] is not None else None,
            "retirement": json.loads(row["retirement"]) if row["retirement"] is not None else None,
            "superseded_by": row["superseded_by"],
        }

    def record_operational_lesson_candidate(
        self,
        record: Mapping[str, object],
        *,
        created_by: str,
    ) -> MutationResult:
        """Validate and persist one CANDIDATE-status lesson snapshot.

        Rejects any record whose validated status is not 'CANDIDATE' -- this
        storage layer never persists a promoted/retired lesson, matching the
        schema-level CHECK constraint. Rows are immutable once inserted.
        """

        created_by = created_by.strip() if isinstance(created_by, str) else ""
        if not created_by:
            return MutationResult(False, "INVALID_ACTOR", "created_by is required")

        try:
            validated = validate_lesson_record(record)
        except OperationalLearningError as exc:
            return MutationResult(False, "INVALID_LESSON_RECORD", str(exc))

        if validated["status"] != "CANDIDATE":
            return MutationResult(
                False,
                "LESSON_NOT_CANDIDATE",
                "operational lesson storage only accepts CANDIDATE-status records; "
                "no promotion/retirement mechanism exists yet",
            )

        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT 1 FROM operational_lessons WHERE lesson_id = ?",
                (validated["lesson_id"],),
            ).fetchone()
            if existing is not None:
                conn.rollback()
                return MutationResult(
                    False,
                    "LESSON_ID_CONFLICT",
                    f"lesson_id {validated['lesson_id']} already exists",
                )
            try:
                conn.execute(
                    """
                    INSERT INTO operational_lessons(
                        lesson_id, lesson_version, status, claim, source_kind,
                        source_refs, applicability, created_by, created_at,
                        promotion, retirement, superseded_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        validated["lesson_id"],
                        validated["lesson_version"],
                        validated["status"],
                        validated["claim"],
                        validated["source_kind"],
                        json.dumps(validated["source_refs"]),
                        json.dumps(validated["applicability"]),
                        created_by,
                        validated["created_at"],
                        json.dumps(validated["promotion"]) if validated["promotion"] is not None else None,
                        json.dumps(validated["retirement"]) if validated["retirement"] is not None else None,
                        validated["superseded_by"],
                    ),
                )
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                return MutationResult(
                    False,
                    "LESSON_CONSTRAINT_VIOLATION",
                    f"operational lesson storage constraints rejected the record: {exc}",
                )
            conn.commit()
        return MutationResult(
            True,
            "LESSON_CANDIDATE_RECORDED",
            f"lesson candidate {validated['lesson_id']} recorded",
            dict(validated),
        )

    def get_operational_lesson(self, lesson_id: str) -> dict[str, Any] | None:
        lesson_id = lesson_id.strip() if isinstance(lesson_id, str) else ""
        if not lesson_id:
            return None
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM operational_lessons WHERE lesson_id = ?",
                (lesson_id,),
            ).fetchone()
        return self._lesson_row(row) if row is not None else None

    def list_operational_lesson_candidates(self) -> list[dict[str, Any]]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT * FROM operational_lessons WHERE status = 'CANDIDATE' "
                "ORDER BY created_at, lesson_id"
            ).fetchall()
        return [self._lesson_row(row) for row in rows]
