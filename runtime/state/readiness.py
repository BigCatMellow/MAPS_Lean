from __future__ import annotations

from contextlib import closing
from pathlib import PurePosixPath
import sqlite3

from .common import (
    ACTIVE_SCOPE_STATUSES,
    VALID_REVIEW,
    VALID_RISKS,
    VALID_TASK_TYPES,
    MutationResult,
    ValidationResult,
    iso_z,
    utc_now,
)
from .environment_contract import validate_persisted_environment_contract


class ReadinessMixin:
    @staticmethod
    def _normalize_output_scope(value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("output path cannot be empty")
        if "\\" in text:
            raise ValueError("output paths must use repository-style '/' separators")
        path = PurePosixPath(text)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("output path must stay inside the repository")
        normalized = path.as_posix()
        return normalized if normalized else "."

    @staticmethod
    def _scope_overlap(left: str, right: str) -> bool:
        if left == "." or right == ".":
            return True
        left_path = PurePosixPath(left)
        right_path = PurePosixPath(right)
        return (
            left_path == right_path
            or left_path in right_path.parents
            or right_path in left_path.parents
        )

    def validate_ready(self, task_id: str) -> ValidationResult:
        with closing(self._connect()) as conn:
            return self._validate_ready_conn(conn, task_id)

    def _validate_ready_conn(
        self,
        conn: sqlite3.Connection,
        task_id: str,
    ) -> ValidationResult:
        row = conn.execute(
            "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
        ).fetchone()
        if row is None:
            return ValidationResult(
                False,
                "AGI FAIL — NEEDS_SHAPING",
                ("task does not exist",),
            )

        reasons: list[str] = []
        required_scalars = {
            "title": row["title"],
            "outcome": row["outcome"],
            "owner": row["owner"],
            "decision authority": row["decision_authority"],
            "verification": row["verification"],
            "expected evidence": row["evidence_expected"],
            "escalation boundary": row["escalation"],
        }
        for label, value in required_scalars.items():
            if not str(value).strip():
                reasons.append(f"missing {label}")

        if row["task_type"] not in VALID_TASK_TYPES:
            reasons.append(
                "task_type must be one of: " + ", ".join(sorted(VALID_TASK_TYPES))
            )
        if row["risk"] not in VALID_RISKS:
            reasons.append("risk must be LOW, MEDIUM, or HIGH")
        if row["review_required"] not in VALID_REVIEW:
            reasons.append(
                "review_required must be OWNER_CHECK, INDEPENDENT_REVIEW, "
                "or OPERATOR_VISIBLE_RELEASE_CHECK"
            )

        collections = {
            "inputs": self._values(conn, "task_inputs", "value", task_id),
            "sources of truth": self._values(conn, "task_sources", "value", task_id),
            "output paths": self._values(conn, "task_output_paths", "path", task_id),
            "acceptance criteria": self._values(
                conn, "task_acceptance_criteria", "criterion", task_id
            ),
            "stop conditions": self._values(
                conn, "task_stop_conditions", "condition", task_id
            ),
        }
        for label, values in collections.items():
            if not values:
                reasons.append(f"missing {label}")

        dependencies = self._values(
            conn, "task_dependencies", "depends_on", task_id
        )
        if task_id in dependencies:
            reasons.append("task cannot depend on itself")

        environment = conn.execute(
            """
            SELECT spec_ref, max_age_seconds, required_for_routing,
                   allow_older_task_revision
            FROM task_environment WHERE task_id = ?
            """,
            (task_id,),
        ).fetchone()
        if environment is not None:
            validation = validate_persisted_environment_contract(dict(environment))
            if validation is not None:
                reasons.append(f"invalid environment contract: {validation.message}")

        # PR #194 residual (6.4 / SEC3): a task whose envelope permits a
        # destructive or external-side-effect action must also require operator
        # reauthorization, otherwise the runtime destructive-action enforcement
        # reaches its ALLOW path with no human in the loop. Closes the
        # "destructive_action=True while requires_operator_approval=False" gap.
        policy = conn.execute(
            """
            SELECT destructive_action, external_side_effect,
                   requires_operator_approval
            FROM task_policy WHERE task_id = ?
            """,
            (task_id,),
        ).fetchone()
        if (
            policy is not None
            and (policy["destructive_action"] or policy["external_side_effect"])
            and not policy["requires_operator_approval"]
        ):
            reasons.append(
                "destructive/external envelope requires operator reauthorization "
                "(set requires_operator_approval)"
            )

        dependency_blockers: list[str] = []
        for dependency in dependencies:
            dep_row = conn.execute(
                "SELECT status FROM tasks WHERE task_id = ?", (dependency,)
            ).fetchone()
            if dep_row is None:
                dependency_blockers.append(f"dependency {dependency} does not exist")
            elif dep_row["status"] != "DONE":
                dependency_blockers.append(
                    f"dependency {dependency} is {dep_row['status']}, not DONE"
                )

        raw_outputs = collections["output paths"]
        normalized_outputs: list[str] = []
        for output in raw_outputs:
            try:
                normalized_outputs.append(self._normalize_output_scope(output))
            except ValueError as exc:
                reasons.append(f"invalid output path {output!r}: {exc}")

        if normalized_outputs:
            status_marks = ",".join("?" for _ in ACTIVE_SCOPE_STATUSES)
            conflicts = conn.execute(
                f"""
                SELECT DISTINCT o.path, o.task_id
                FROM task_output_paths o
                JOIN tasks t ON t.task_id = o.task_id
                WHERE o.task_id <> ?
                  AND t.status IN ({status_marks})
                ORDER BY o.task_id, o.path
                """,
                (task_id, *sorted(ACTIVE_SCOPE_STATUSES)),
            ).fetchall()
            reported: set[tuple[str, str, str]] = set()
            for conflict in conflicts:
                try:
                    reserved = self._normalize_output_scope(conflict["path"])
                except ValueError:
                    reasons.append(
                        f"reserved output path {conflict['path']!r} on "
                        f"{conflict['task_id']} is invalid; repair that task first"
                    )
                    continue
                for output in normalized_outputs:
                    if not self._scope_overlap(output, reserved):
                        continue
                    key = (output, reserved, conflict["task_id"])
                    if key in reported:
                        continue
                    reported.add(key)
                    reasons.append(
                        f"output scope {output} overlaps {reserved} already reserved by "
                        f"{conflict['task_id']}"
                    )

        if dependency_blockers and not reasons:
            return ValidationResult(
                False,
                "AGI FAIL — BLOCKED_ON_DEPENDENCY",
                tuple(dependency_blockers),
            )
        reasons.extend(dependency_blockers)
        if reasons:
            return ValidationResult(
                False,
                "AGI FAIL — NEEDS_SHAPING",
                tuple(reasons),
            )
        return ValidationResult(True, "AGI READY", ())

    def promote_ready(
        self,
        task_id: str,
        actor: str | None = None,
    ) -> MutationResult:
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if row is None:
                conn.rollback()
                return MutationResult(False, "NOT_FOUND", f"{task_id} does not exist")
            if row["status"] not in {"NEEDS_SHAPING", "BLOCKED"}:
                conn.rollback()
                return MutationResult(
                    False,
                    "INVALID_STATE",
                    f"cannot promote from {row['status']}",
                    dict(row),
                )

            # AGI validation and READY mutation share this write transaction.
            validation = self._validate_ready_conn(conn, task_id)
            if not validation.ok:
                conn.execute(
                    "UPDATE tasks SET agi_status = ?, updated_at = ? WHERE task_id = ?",
                    (validation.agi_status, iso_z(utc_now()), task_id),
                )
                self._append_event(
                    conn,
                    task_id,
                    "TASK_READY_REJECTED",
                    actor,
                    "; ".join(validation.reasons),
                )
                conn.commit()
                return MutationResult(
                    False,
                    "AGI_NOT_READY",
                    "; ".join(validation.reasons),
                    self.get_task(task_id),
                )

            conn.execute(
                """
                UPDATE tasks
                SET status = 'READY', agi_status = 'AGI READY', updated_at = ?
                WHERE task_id = ?
                """,
                (iso_z(utc_now()), task_id),
            )
            self._append_event(
                conn,
                task_id,
                "TASK_PROMOTED_READY",
                actor,
                "AGI gate passed",
            )
            conn.commit()
        return MutationResult(True, "READY", f"{task_id} is READY", self.get_task(task_id))
