from __future__ import annotations

from contextlib import closing
import sqlite3
from typing import Any

from runtime.incident_taxonomy import classify_failure_text

from .common import MutationResult, iso_z, utc_now
from .observability import redact_sensitive_text

VALID_OUTCOME_STATUSES = {"SUCCESS", "PARTIAL", "FAILURE", "UNKNOWN"}
VALID_ACTOR_CLASSES = {"OPERATOR", "CORE_AGENT", "HELPER", "SYSTEM", "UNKNOWN"}


def _outcome_read_model(record: dict[str, Any]) -> dict[str, Any]:
    """Add non-persistent presentation fields to one outcome record."""

    record["escaped_defect"] = bool(record["escaped_defect"])
    record["incident_class"] = classify_failure_text(record.get("failure_class")).value
    return record


class OutcomeMixin:
    """Append-only post-completion outcome observations.

    Outcomes are later evidence about whether completed work actually succeeded.
    They never change task lifecycle, ownership, policy, or review authority.
    """

    def record_outcome(
        self,
        task_id: str,
        outcome_status: str,
        *,
        source: str,
        actor_class: str = "UNKNOWN",
        actor_id: str = "",
        run_id: str | None = None,
        failure_class: str = "",
        escaped_defect: bool = False,
        rework_count: int = 0,
        operator_intervention_count: int = 0,
        notes: str = "",
        supersedes_outcome_id: int | None = None,
    ) -> MutationResult:
        status = outcome_status.strip().upper()
        actor_class = actor_class.strip().upper()
        actor_id = actor_id.strip()
        source = source.strip()
        failure_class = failure_class.strip()

        if status not in VALID_OUTCOME_STATUSES:
            return MutationResult(
                False,
                "INVALID_OUTCOME_STATUS",
                "outcome_status must be SUCCESS, PARTIAL, FAILURE, or UNKNOWN",
            )
        if actor_class not in VALID_ACTOR_CLASSES:
            return MutationResult(
                False,
                "INVALID_ACTOR_CLASS",
                "actor_class must be OPERATOR, CORE_AGENT, HELPER, SYSTEM, or UNKNOWN",
            )
        if actor_class != "UNKNOWN" and not actor_id:
            return MutationResult(
                False,
                "MISSING_ACTOR_ID",
                "actor_id is required when actor_class is known",
            )
        if not source:
            return MutationResult(False, "MISSING_OUTCOME_SOURCE", "source is required")
        if rework_count < 0 or operator_intervention_count < 0:
            return MutationResult(
                False,
                "INVALID_OUTCOME_METRIC",
                "rework and operator-intervention counts must be >= 0",
            )
        if status == "FAILURE" and not failure_class:
            failure_class = "UNKNOWN"

        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            task = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if task is None:
                conn.rollback()
                return MutationResult(False, "NOT_FOUND", f"{task_id} does not exist")
            if task["status"] != "DONE":
                conn.rollback()
                return MutationResult(
                    False,
                    "OUTCOME_REQUIRES_DONE",
                    f"task status is {task['status']}; outcome observations require DONE",
                    dict(task),
                )

            if run_id:
                run = conn.execute(
                    "SELECT task_id FROM run_manifests WHERE run_id = ?", (run_id,)
                ).fetchone()
                if run is None:
                    conn.rollback()
                    return MutationResult(False, "RUN_NOT_FOUND", f"{run_id} does not exist")
                if run["task_id"] != task_id:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "OUTCOME_RUN_MISMATCH",
                        f"{run_id} belongs to {run['task_id']}, not {task_id}",
                    )

            if supersedes_outcome_id is not None:
                prior = conn.execute(
                    "SELECT task_id FROM task_outcomes WHERE id = ?",
                    (supersedes_outcome_id,),
                ).fetchone()
                if prior is None:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "SUPERSEDED_OUTCOME_NOT_FOUND",
                        f"outcome {supersedes_outcome_id} does not exist",
                    )
                if prior["task_id"] != task_id:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "CROSS_TASK_OUTCOME_SUPERSESSION",
                        "an outcome may supersede only an observation for the same task",
                    )

            revision_method = getattr(self, "_task_revision_conn", None)
            task_revision = (
                revision_method(conn, task_id) if callable(revision_method) else ""
            )
            stamp = iso_z(utc_now())
            cursor = conn.execute(
                """
                INSERT INTO task_outcomes(
                    task_id, run_id, outcome_status, failure_class,
                    escaped_defect, rework_count, operator_intervention_count,
                    actor_id, actor_class, source, notes, task_revision,
                    supersedes_outcome_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    run_id,
                    status,
                    failure_class,
                    int(bool(escaped_defect)),
                    rework_count,
                    operator_intervention_count,
                    actor_id,
                    actor_class,
                    redact_sensitive_text(source),
                    redact_sensitive_text(notes.strip()),
                    task_revision,
                    supersedes_outcome_id,
                    stamp,
                ),
            )
            outcome_id = int(cursor.lastrowid)
            self._append_event(
                conn,
                task_id,
                "OUTCOME_RECORDED",
                actor_id or None,
                f"outcome {outcome_id}: {status}",
            )
            conn.commit()

        record = self.get_outcome(outcome_id)
        payload = self.get_task(task_id) or {}
        payload["outcome_record"] = record
        return MutationResult(
            True,
            "OUTCOME_RECORDED",
            f"recorded outcome {outcome_id} for {task_id}",
            payload,
        )

    def get_outcome(self, outcome_id: int) -> dict[str, Any] | None:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM task_outcomes WHERE id = ?", (outcome_id,)
            ).fetchone()
        if row is None:
            return None
        return _outcome_read_model(dict(row))

    def list_outcomes(self, task_id: str) -> list[dict[str, Any]]:
        with closing(self._connect()) as conn:
            rows = [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM task_outcomes WHERE task_id = ? ORDER BY id",
                    (task_id,),
                ).fetchall()
            ]
        return [_outcome_read_model(row) for row in rows]
