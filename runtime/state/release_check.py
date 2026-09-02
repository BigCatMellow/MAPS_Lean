from __future__ import annotations

from contextlib import closing
import json
from typing import Any, Sequence

from .common import MutationResult, iso_z, utc_now


_ARTIFACT_IDENTITY_STATES = {"PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"}
_RELEASE_SMOKE_STATES = {"COMPLETE", "FAIL", "INCOMPLETE", "NOT_APPLICABLE"}
_COMPOSITE_STATES = {"READY_FOR_OPERATOR_VERDICT", "BLOCKED"}


class ReleaseCheckMixin:
    """Append-only storage for `maps flow release-check` summaries (6.21).

    A row is the evidence assembled *before* the review verdict for an
    `OPERATOR_VISIBLE_RELEASE_CHECK` task: the artifact-identity aggregate, the
    release-path-smoke aggregate, the composite state, and the full summary
    snapshot. This mixin records; it never records a review verdict and never
    gates `record_review` (that is a later hardening slice). Re-running the
    check appends a new row; `latest_release_check` returns the newest by id.
    """

    @staticmethod
    def _canonical_json(value: object) -> str:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )

    @staticmethod
    def _decode_release_check(row: Any | None) -> dict[str, Any] | None:
        if row is None:
            return None
        record = dict(row)
        for field in ("input_evidence_refs", "summary_snapshot"):
            raw = record.get(field)
            if isinstance(raw, str):
                try:
                    record[field] = json.loads(raw)
                except json.JSONDecodeError:
                    pass
        return record

    def record_release_check(
        self,
        task_id: str,
        review_id: int,
        *,
        artifact_identity_state: str,
        release_smoke_state: str,
        composite_state: str,
        summary: dict[str, Any],
        recorded_by: str,
        subject_run_id: str | None = None,
        artifact_identity_report_ref: str | None = None,
        release_smoke_report_ref: str | None = None,
        input_evidence_refs: Sequence[str] = (),
        operator_ack_ref: str | None = None,
    ) -> MutationResult:
        task_id = task_id.strip()
        recorded_by = recorded_by.strip()
        artifact_identity_state = str(artifact_identity_state).strip().upper()
        release_smoke_state = str(release_smoke_state).strip().upper()
        composite_state = str(composite_state).strip().upper()

        if not task_id:
            return MutationResult(False, "INVALID_RELEASE_CHECK", "task_id is required")
        if not recorded_by:
            return MutationResult(
                False, "INVALID_RELEASE_CHECK", "recorded_by is required"
            )
        if not isinstance(review_id, int) or isinstance(review_id, bool) or review_id <= 0:
            return MutationResult(
                False, "INVALID_RELEASE_CHECK", "review_id must be a positive integer"
            )
        if artifact_identity_state not in _ARTIFACT_IDENTITY_STATES:
            return MutationResult(
                False,
                "INVALID_RELEASE_CHECK",
                "artifact_identity_state must be one of "
                + ", ".join(sorted(_ARTIFACT_IDENTITY_STATES)),
            )
        if release_smoke_state not in _RELEASE_SMOKE_STATES:
            return MutationResult(
                False,
                "INVALID_RELEASE_CHECK",
                "release_smoke_state must be one of "
                + ", ".join(sorted(_RELEASE_SMOKE_STATES)),
            )
        if composite_state not in _COMPOSITE_STATES:
            return MutationResult(
                False,
                "INVALID_RELEASE_CHECK",
                "composite_state must be READY_FOR_OPERATOR_VERDICT or BLOCKED",
            )

        refs = tuple(
            r.strip() for r in input_evidence_refs if isinstance(r, str) and r.strip()
        )
        created_at = iso_z(utc_now())
        summary_snapshot = self._canonical_json(summary)

        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            task = conn.execute(
                "SELECT task_id FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if task is None:
                conn.rollback()
                return MutationResult(
                    False, "TASK_NOT_FOUND", f"{task_id} does not exist"
                )
            review = conn.execute(
                "SELECT id, task_id FROM reviews WHERE id = ?", (review_id,)
            ).fetchone()
            if review is None:
                conn.rollback()
                return MutationResult(
                    False, "REVIEW_NOT_FOUND", f"review {review_id} does not exist"
                )
            if str(review["task_id"]) != task_id:
                conn.rollback()
                return MutationResult(
                    False,
                    "RELEASE_CHECK_TASK_MISMATCH",
                    f"review {review_id} belongs to {review['task_id']}, not {task_id}",
                )

            cursor = conn.execute(
                """
                INSERT INTO release_checks(
                    task_id, review_id, subject_run_id,
                    artifact_identity_state, artifact_identity_report_ref,
                    release_smoke_state, release_smoke_report_ref,
                    input_evidence_refs, composite_state, summary_snapshot,
                    operator_ack_ref, recorded_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    review_id,
                    subject_run_id,
                    artifact_identity_state,
                    artifact_identity_report_ref,
                    release_smoke_state,
                    release_smoke_report_ref,
                    json.dumps(list(refs)),
                    composite_state,
                    summary_snapshot,
                    operator_ack_ref,
                    recorded_by,
                    created_at,
                ),
            )
            release_check_id = int(cursor.lastrowid)
            self._append_event(
                conn,
                task_id,
                "RELEASE_CHECK_RECORDED",
                recorded_by,
                f"release check {release_check_id} for review {review_id}: "
                f"{composite_state}",
            )
            conn.commit()

        return MutationResult(
            True,
            "RELEASE_CHECK_RECORDED",
            f"recorded release check {release_check_id} for {task_id}",
            self.get_release_check(release_check_id),
        )

    def get_release_check(self, release_check_id: int) -> dict[str, Any] | None:
        if (
            not isinstance(release_check_id, int)
            or isinstance(release_check_id, bool)
            or release_check_id <= 0
        ):
            return None
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM release_checks WHERE id = ?", (release_check_id,)
            ).fetchone()
        return self._decode_release_check(row)

    def latest_release_check(
        self, task_id: str, review_id: int
    ) -> dict[str, Any] | None:
        task_id = task_id.strip() if isinstance(task_id, str) else ""
        if not task_id or not isinstance(review_id, int) or review_id <= 0:
            return None
        with closing(self._connect()) as conn:
            row = conn.execute(
                """
                SELECT * FROM release_checks
                WHERE task_id = ? AND review_id = ?
                ORDER BY id DESC LIMIT 1
                """,
                (task_id, review_id),
            ).fetchone()
        return self._decode_release_check(row)

    def list_release_checks(self, task_id: str) -> list[dict[str, Any]]:
        task_id = task_id.strip() if isinstance(task_id, str) else ""
        if not task_id:
            return []
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT * FROM release_checks WHERE task_id = ? ORDER BY id",
                (task_id,),
            ).fetchall()
        return [self._decode_release_check(row) for row in rows]
