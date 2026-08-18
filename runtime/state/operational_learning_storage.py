from __future__ import annotations

from contextlib import closing
import json
import sqlite3
from typing import Any, Mapping

from runtime.operational_learning import OperationalLearningError, validate_lesson_record

from .common import MutationResult, iso_z, utc_now


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
        """Return the effective composed lesson view: base row plus its decisions.

        The base `operational_lessons` row is always CANDIDATE-shaped (per
        Storage-0); this composes it with any promotion/retirement decisions
        to report the lesson's true current status, then re-validates the
        composed record through `validate_lesson_record()` as defense in
        depth (the same pattern promote/retire use before writing).
        """

        lesson_id = lesson_id.strip() if isinstance(lesson_id, str) else ""
        if not lesson_id:
            return None
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM operational_lessons WHERE lesson_id = ?",
                (lesson_id,),
            ).fetchone()
            if row is None:
                return None
            decisions = self._decisions_for(conn, lesson_id)
        composed = self._compose(row, decisions)
        return validate_lesson_record(composed)

    def list_operational_lesson_candidates(self) -> list[dict[str, Any]]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT * FROM operational_lessons "
                "WHERE status = 'CANDIDATE' AND lesson_id NOT IN ("
                "  SELECT lesson_id FROM operational_lesson_decisions"
                ") ORDER BY created_at, lesson_id"
            ).fetchall()
        return [self._lesson_row(row) for row in rows]

    # -- Authority-1: operator-only promotion / retirement -----------------
    #
    # The base operational_lessons row (above) never changes. A lesson's
    # effective status is composed from that row plus its append-only
    # decisions, never stored as a mutable column. Every promotion and every
    # retirement requires an explicit decision_ref and actor; there is no
    # automatic/evidence-gated path (operator decision recorded 2026-08-17,
    # Option A). Both mutation methods reconstruct the full proposed lesson
    # snapshot and re-validate it through validate_lesson_record() before
    # writing anything, matching Storage-0's defense-in-depth pattern.

    def _decisions_for(self, conn: sqlite3.Connection, lesson_id: str) -> list[sqlite3.Row]:
        return conn.execute(
            "SELECT * FROM operational_lesson_decisions "
            "WHERE lesson_id = ? ORDER BY decision_id",
            (lesson_id,),
        ).fetchall()

    @staticmethod
    def _compose(base_row: sqlite3.Row, decisions: list[sqlite3.Row]) -> dict[str, Any]:
        record = OperationalLessonStorageMixin._lesson_row(base_row)
        promotion = None
        retirement = None
        for decision in decisions:
            payload = json.loads(decision["decision_payload"])
            if decision["decision_kind"] == "PROMOTE":
                promotion = payload
            elif decision["decision_kind"] == "RETIRE":
                retirement = payload
        if retirement is not None:
            record["status"] = "RETIRED"
        elif promotion is not None:
            record["status"] = "ACTIVE"
        record["promotion"] = promotion
        record["retirement"] = retirement
        return record

    def promote_operational_lesson(
        self,
        lesson_id: str,
        *,
        decision_ref: str,
        promoted_by: str,
        starts_at: str,
        review_at: str,
        expires_at: str | None = None,
        now=None,
    ) -> MutationResult:
        """Operator-only CANDIDATE -> ACTIVE promotion. No automatic path exists."""

        current_time = now or utc_now()
        lesson_id = lesson_id.strip() if isinstance(lesson_id, str) else ""
        if not lesson_id:
            return MutationResult(False, "INVALID_LESSON_ID", "lesson_id is required")
        actor = promoted_by.strip() if isinstance(promoted_by, str) else ""
        if not actor:
            return MutationResult(False, "INVALID_ACTOR", "promoted_by is required")

        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            base_row = conn.execute(
                "SELECT * FROM operational_lessons WHERE lesson_id = ?",
                (lesson_id,),
            ).fetchone()
            if base_row is None:
                conn.rollback()
                return MutationResult(False, "LESSON_NOT_FOUND", f"no lesson {lesson_id}")

            decisions = self._decisions_for(conn, lesson_id)
            if any(d["decision_kind"] == "RETIRE" for d in decisions):
                conn.rollback()
                return MutationResult(
                    False, "LESSON_RETIRED", f"lesson {lesson_id} is retired; retirement is terminal"
                )
            if any(d["decision_kind"] == "PROMOTE" for d in decisions):
                conn.rollback()
                return MutationResult(
                    False, "ALREADY_PROMOTED", f"lesson {lesson_id} is already promoted"
                )

            base = self._lesson_row(base_row)
            promotion_payload = {
                "decision_ref": decision_ref,
                "promoted_by": promoted_by,
                "starts_at": starts_at,
                "review_at": review_at,
                "expires_at": expires_at,
            }
            proposed = dict(base)
            proposed["status"] = "ACTIVE"
            proposed["promotion"] = promotion_payload
            proposed["retirement"] = None
            try:
                validated = validate_lesson_record(proposed)
            except OperationalLearningError as exc:
                conn.rollback()
                return MutationResult(False, "INVALID_PROMOTION", str(exc))

            try:
                conn.execute(
                    """
                    INSERT INTO operational_lesson_decisions(
                        lesson_id, decision_kind, decision_payload, decided_by,
                        decided_at, created_at
                    ) VALUES (?, 'PROMOTE', ?, ?, ?, ?)
                    """,
                    (
                        lesson_id,
                        json.dumps(validated["promotion"]),
                        actor,
                        validated["promotion"]["starts_at"],
                        iso_z(current_time),
                    ),
                )
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                return MutationResult(
                    False,
                    "DECISION_CONSTRAINT_VIOLATION",
                    f"promotion decision rejected: {exc}",
                )
            conn.commit()
        return MutationResult(
            True,
            "LESSON_PROMOTED",
            f"lesson {lesson_id} promoted to ACTIVE",
            validated,
        )

    def retire_operational_lesson(
        self,
        lesson_id: str,
        *,
        decision_ref: str,
        retired_by: str,
        retired_at: str,
        now=None,
    ) -> MutationResult:
        """Operator-only CANDIDATE|ACTIVE -> RETIRED retirement. Terminal; no re-retirement."""

        current_time = now or utc_now()
        lesson_id = lesson_id.strip() if isinstance(lesson_id, str) else ""
        if not lesson_id:
            return MutationResult(False, "INVALID_LESSON_ID", "lesson_id is required")
        actor = retired_by.strip() if isinstance(retired_by, str) else ""
        if not actor:
            return MutationResult(False, "INVALID_ACTOR", "retired_by is required")

        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            base_row = conn.execute(
                "SELECT * FROM operational_lessons WHERE lesson_id = ?",
                (lesson_id,),
            ).fetchone()
            if base_row is None:
                conn.rollback()
                return MutationResult(False, "LESSON_NOT_FOUND", f"no lesson {lesson_id}")

            decisions = self._decisions_for(conn, lesson_id)
            if any(d["decision_kind"] == "RETIRE" for d in decisions):
                conn.rollback()
                return MutationResult(
                    False, "ALREADY_RETIRED", f"lesson {lesson_id} is already retired"
                )
            existing_promotion = None
            for decision in decisions:
                if decision["decision_kind"] == "PROMOTE":
                    existing_promotion = json.loads(decision["decision_payload"])

            base = self._lesson_row(base_row)
            retirement_payload = {
                "decision_ref": decision_ref,
                "retired_by": retired_by,
                "retired_at": retired_at,
            }
            proposed = dict(base)
            proposed["status"] = "RETIRED"
            proposed["promotion"] = existing_promotion
            proposed["retirement"] = retirement_payload
            try:
                validated = validate_lesson_record(proposed)
            except OperationalLearningError as exc:
                conn.rollback()
                return MutationResult(False, "INVALID_RETIREMENT", str(exc))

            try:
                conn.execute(
                    """
                    INSERT INTO operational_lesson_decisions(
                        lesson_id, decision_kind, decision_payload, decided_by,
                        decided_at, created_at
                    ) VALUES (?, 'RETIRE', ?, ?, ?, ?)
                    """,
                    (
                        lesson_id,
                        json.dumps(validated["retirement"]),
                        actor,
                        validated["retirement"]["retired_at"],
                        iso_z(current_time),
                    ),
                )
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                return MutationResult(
                    False,
                    "DECISION_CONSTRAINT_VIOLATION",
                    f"retirement decision rejected: {exc}",
                )
            conn.commit()
        return MutationResult(
            True,
            "LESSON_RETIRED",
            f"lesson {lesson_id} retired",
            validated,
        )

    def list_operational_lesson_decisions(self, lesson_id: str) -> list[dict[str, Any]]:
        lesson_id = lesson_id.strip() if isinstance(lesson_id, str) else ""
        if not lesson_id:
            return []
        with closing(self._connect()) as conn:
            rows = self._decisions_for(conn, lesson_id)
        return [
            {
                "decision_id": int(row["decision_id"]),
                "lesson_id": str(row["lesson_id"]),
                "decision_kind": str(row["decision_kind"]),
                "decision_payload": json.loads(row["decision_payload"]),
                "decided_by": str(row["decided_by"]),
                "decided_at": str(row["decided_at"]),
                "created_at": str(row["created_at"]),
            }
            for row in rows
        ]
