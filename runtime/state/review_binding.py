from __future__ import annotations

from contextlib import closing
import json
import re
import sqlite3
from typing import Any, Sequence

from .common import MutationResult, iso_z, utc_now


FRESHNESS_MODES = {
    "REVISION_BOUND",
    "REDERIVED_AT_REVIEW",
    "NON_CONSEQUENTIAL",
}
_CONSEQUENTIAL_POLICY_FLAGS = (
    "requires_operator_approval",
    "destructive_action",
    "external_side_effect",
    "security_sensitive",
    "broad_architecture",
)
_SHA256_REF_RE = re.compile(r"^sha256:[0-9a-fA-F]{64}$")
_GIT_REF_RE = re.compile(r"^git:[0-9a-fA-F]{40}(?:[0-9a-fA-F]{24})?$")


class ReviewBindingMixin:
    """Immutable review-subject bindings and atomic approval validation.

    The binding identifies exactly what a reviewer is reviewing. It does not
    grant reviewer authority, operator approval, task ownership, or capability.
    """

    @staticmethod
    def _normalize_artifact_refs(values: Sequence[str] | None) -> tuple[str, ...]:
        if values is None:
            return ()
        refs: list[str] = []
        for raw in values:
            if not isinstance(raw, str) or not raw.strip():
                raise ValueError("artifact references must be non-empty strings")
            ref = raw.strip()
            if not (_SHA256_REF_RE.fullmatch(ref) or _GIT_REF_RE.fullmatch(ref)):
                raise ValueError(
                    "artifact references must use sha256:<64 hex> or git:<40/64 hex>"
                )
            refs.append(ref.lower())
        if len(set(refs)) != len(refs):
            raise ValueError("artifact references contain duplicates")
        return tuple(sorted(refs))

    @staticmethod
    def _decode_review_subject(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        record = dict(row)
        record["artifact_refs"] = json.loads(record["artifact_refs"])
        return record

    @staticmethod
    def _requires_bound_subject_conn(
        conn: sqlite3.Connection,
        task: sqlite3.Row,
    ) -> bool:
        if str(task["risk"]).upper() == "HIGH":
            return True
        if str(task["review_required"]).upper() == "OPERATOR_VISIBLE_RELEASE_CHECK":
            return True
        policy = conn.execute(
            "SELECT * FROM task_policy WHERE task_id = ?",
            (task["task_id"],),
        ).fetchone()
        return bool(
            policy is not None
            and any(bool(policy[field]) for field in _CONSEQUENTIAL_POLICY_FLAGS)
        )

    def bind_review_subject(
        self,
        task_id: str,
        reviewer_id: str,
        *,
        freshness_mode: str,
        run_id: str | None = None,
        artifact_refs: Sequence[str] = (),
    ) -> MutationResult:
        task_id = task_id.strip()
        reviewer_id = reviewer_id.strip()
        mode = freshness_mode.strip().upper()
        if not task_id or not reviewer_id:
            return MutationResult(
                False,
                "INVALID_REVIEW_SUBJECT",
                "task_id and reviewer_id are required",
            )
        if mode not in FRESHNESS_MODES:
            return MutationResult(
                False,
                "INVALID_FRESHNESS_MODE",
                "freshness_mode must be REVISION_BOUND, REDERIVED_AT_REVIEW, or NON_CONSEQUENTIAL",
            )
        normalized_run = run_id.strip() if isinstance(run_id, str) and run_id.strip() else None
        try:
            refs = self._normalize_artifact_refs(artifact_refs)
        except ValueError as exc:
            return MutationResult(False, "INVALID_ARTIFACT_REF", str(exc))

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
            existing = conn.execute(
                "SELECT 1 FROM review_subjects WHERE review_id = ?",
                (review["id"],),
            ).fetchone()
            if existing is not None:
                conn.rollback()
                return MutationResult(
                    False,
                    "REVIEW_SUBJECT_ALREADY_BOUND",
                    "review subject is immutable once bound",
                )
            task = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?",
                (task_id,),
            ).fetchone()
            if task is None or task["status"] != "READY_FOR_REVIEW":
                conn.rollback()
                return MutationResult(
                    False,
                    "NOT_REVIEWABLE",
                    "task is no longer READY_FOR_REVIEW",
                )
            submission = conn.execute(
                "SELECT * FROM task_submissions WHERE task_id = ?",
                (task_id,),
            ).fetchone()
            if submission is None:
                conn.rollback()
                return MutationResult(
                    False,
                    "MISSING_SUBMISSION",
                    "review subject requires a current submission",
                )
            requires_bound = self._requires_bound_subject_conn(conn, task)
            if mode == "NON_CONSEQUENTIAL" and requires_bound:
                conn.rollback()
                return MutationResult(
                    False,
                    "CONSEQUENTIAL_REVIEW_REQUIRES_FRESHNESS",
                    "consequential work cannot use NON_CONSEQUENTIAL freshness",
                )
            if mode == "REVISION_BOUND" and requires_bound and not refs:
                conn.rollback()
                return MutationResult(
                    False,
                    "CONSEQUENTIAL_REVIEW_ARTIFACT_REQUIRED",
                    "consequential REVISION_BOUND review requires immutable artifact/evidence refs",
                )
            if mode == "REVISION_BOUND" and normalized_run is None and not refs:
                conn.rollback()
                return MutationResult(
                    False,
                    "REVISION_BOUND_SUBJECT_REQUIRED",
                    "REVISION_BOUND review requires run_id or immutable artifact refs",
                )
            if mode == "REDERIVED_AT_REVIEW" and not refs:
                conn.rollback()
                return MutationResult(
                    False,
                    "REDERIVATION_ARTIFACTS_REQUIRED",
                    "REDERIVED_AT_REVIEW requires immutable artifact/evidence refs",
                )

            current_revision = self._task_revision_conn(conn, task_id)
            if normalized_run is not None:
                run = conn.execute(
                    "SELECT * FROM run_manifests WHERE run_id = ?",
                    (normalized_run,),
                ).fetchone()
                if run is None or run["task_id"] != task_id:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "INVALID_REVIEW_RUN",
                        "review run does not belong to task",
                    )
                if run["task_revision"] != current_revision:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "STALE_REVIEW_RUN",
                        "review run is bound to a stale task revision",
                    )

            try:
                conn.execute(
                    """
                    INSERT INTO review_subjects(
                        review_id, task_id, submission_count, task_revision,
                        run_id, artifact_refs, freshness_mode, bound_by, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        review["id"],
                        task_id,
                        submission["submission_count"],
                        current_revision,
                        normalized_run,
                        json.dumps(refs, separators=(",", ":")),
                        mode,
                        reviewer_id,
                        iso_z(utc_now()),
                    ),
                )
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                return MutationResult(False, "REVIEW_SUBJECT_CONFLICT", str(exc))
            self._append_event(
                conn,
                task_id,
                "REVIEW_SUBJECT_BOUND",
                reviewer_id,
                f"review {review['id']} subject bound with {mode}",
            )
            conn.commit()

        return MutationResult(
            True,
            "REVIEW_SUBJECT_BOUND",
            f"review {review['id']} subject bound",
            self.get_review_subject(int(review["id"])),
        )

    def get_review_subject(self, review_id: int) -> dict[str, Any] | None:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM review_subjects WHERE review_id = ?",
                (review_id,),
            ).fetchone()
        return self._decode_review_subject(row)

    def _validate_review_approval_conn(
        self,
        conn: sqlite3.Connection,
        *,
        task: sqlite3.Row,
        submission: sqlite3.Row,
        review: sqlite3.Row,
        rederived_artifact_refs: Sequence[str] | None,
    ) -> tuple[str, str] | None:
        subject_row = conn.execute(
            "SELECT * FROM review_subjects WHERE review_id = ?",
            (review["id"],),
        ).fetchone()
        required = self._requires_bound_subject_conn(conn, task)
        if subject_row is None:
            if required:
                return (
                    "REVIEW_SUBJECT_REQUIRED",
                    "consequential approval requires an immutable review subject binding",
                )
            return None

        subject = dict(subject_row)
        refs = tuple(json.loads(subject["artifact_refs"]))
        if subject["task_id"] != task["task_id"]:
            return "REVIEW_SUBJECT_TASK_MISMATCH", "review subject belongs to another task"
        if int(subject["submission_count"]) != int(submission["submission_count"]):
            return (
                "REVIEW_SUBMISSION_CHANGED",
                "submission changed after review subject was bound",
            )
        current_revision = self._task_revision_conn(conn, task["task_id"])
        if subject["task_revision"] != current_revision:
            return (
                "REVIEW_TASK_REVISION_CHANGED",
                "task revision changed after review subject was bound",
            )
        if required and subject["freshness_mode"] == "NON_CONSEQUENTIAL":
            return (
                "CONSEQUENTIAL_REVIEW_REQUIRES_FRESHNESS",
                "consequential approval cannot use NON_CONSEQUENTIAL freshness",
            )
        if required and not refs:
            return (
                "CONSEQUENTIAL_REVIEW_ARTIFACT_REQUIRED",
                "consequential approval requires immutable artifact/evidence refs for the reviewed output",
            )

        if subject["run_id"]:
            run = conn.execute(
                "SELECT * FROM run_manifests WHERE run_id = ?",
                (subject["run_id"],),
            ).fetchone()
            if run is None or run["task_id"] != task["task_id"]:
                return "REVIEW_RUN_MISSING", "bound review run no longer resolves to task"
            if run["task_revision"] != subject["task_revision"]:
                return "REVIEW_RUN_STALE", "bound review run revision no longer matches subject"

        claims = conn.execute(
            """
            SELECT c.task_revision, c.run_id
            FROM submission_criterion_claims AS c
            JOIN (
                SELECT criterion_id, MAX(id) AS max_id
                FROM submission_criterion_claims
                WHERE task_id = ? AND submission_count = ?
                GROUP BY criterion_id
            ) AS latest ON latest.max_id = c.id
            ORDER BY c.criterion_id
            """,
            (task["task_id"], submission["submission_count"]),
        ).fetchall()
        for claim in claims:
            if claim["task_revision"] != subject["task_revision"]:
                return (
                    "REVIEW_CRITERION_REVISION_MISMATCH",
                    "criterion evidence revision does not match overall review subject",
                )
            if subject["run_id"] and claim["run_id"] and claim["run_id"] != subject["run_id"]:
                return (
                    "REVIEW_CRITERION_RUN_MISMATCH",
                    "criterion evidence run does not match overall review subject run",
                )

        if subject["freshness_mode"] == "REDERIVED_AT_REVIEW":
            try:
                rederived = self._normalize_artifact_refs(rederived_artifact_refs)
            except ValueError as exc:
                return "INVALID_REDERIVED_ARTIFACT_REF", str(exc)
            if not rederived:
                return (
                    "REVIEW_REDERIVATION_REQUIRED",
                    "approval requires rederived immutable artifact/evidence refs",
                )
            if rederived != refs:
                return (
                    "REVIEW_REDERIVATION_MISMATCH",
                    "rederived artifact/evidence refs differ from the bound review subject",
                )
        return None

    def trace_task(self, task_id: str) -> dict[str, Any] | None:
        trace = super().trace_task(task_id)
        if trace is None:
            return None
        for review in trace.get("reviews", []):
            review["subject"] = self.get_review_subject(int(review["id"]))
        coverage = trace.get("coverage", {}).get("canonical_task_db")
        if isinstance(coverage, dict):
            coverage["review_subjects_included"] = True
        return trace
