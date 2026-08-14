from __future__ import annotations

from contextlib import closing
from typing import Mapping

from .common import MutationResult, iso_z, utc_now

POLICY_FLAGS = (
    "requires_operator_approval",
    "destructive_action",
    "external_side_effect",
    "security_sensitive",
    "broad_architecture",
    "paid_execution",
)
APPROVAL_TRIGGER_FLAGS = (
    "requires_operator_approval",
    "destructive_action",
    "external_side_effect",
    "security_sensitive",
    "broad_architecture",
)


class PolicyStateMixin:
    def update_contract(self, task_id: str, contract: Mapping[str, object]) -> MutationResult:
        raw_policy = contract.get("policy")
        policy: dict[str, bool] | None = None
        if raw_policy is not None:
            if not isinstance(raw_policy, Mapping):
                return MutationResult(False, "INVALID_CONTRACT", "policy must be an object")
            unknown = sorted(set(raw_policy) - set(POLICY_FLAGS))
            if unknown:
                return MutationResult(
                    False,
                    "INVALID_CONTRACT",
                    "unknown policy fields: " + ", ".join(unknown),
                )
            policy = {}
            for field in POLICY_FLAGS:
                if field not in raw_policy:
                    continue
                value = raw_policy[field]
                if not isinstance(value, bool):
                    return MutationResult(
                        False,
                        "INVALID_CONTRACT",
                        f"policy.{field} must be boolean",
                    )
                policy[field] = value

        base_contract = dict(contract)
        base_contract.pop("policy", None)
        result = super().update_contract(task_id, base_contract)
        if not result.ok:
            return result

        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("INSERT OR IGNORE INTO task_policy(task_id) VALUES (?)", (task_id,))
            if policy:
                clause = ", ".join(f"{field} = ?" for field in policy)
                conn.execute(
                    f"UPDATE task_policy SET {clause} WHERE task_id = ?",
                    (*[1 if policy[field] else 0 for field in policy], task_id),
                )
            # Any shaped-contract change invalidates a prior approval.
            conn.execute(
                """
                UPDATE task_policy
                SET approved_by = NULL, approved_at = NULL, approval_note = ''
                WHERE task_id = ?
                """,
                (task_id,),
            )
            self._append_event(
                conn,
                task_id,
                "TASK_POLICY_UPDATED",
                None,
                "Policy contract updated; operator approval reset",
            )
            conn.commit()
        return MutationResult(True, "UPDATED", f"updated {task_id}", self.get_task(task_id))

    def get_task(self, task_id: str) -> dict | None:
        task = super().get_task(task_id)
        if task is None:
            return None
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM task_policy WHERE task_id = ?",
                (task_id,),
            ).fetchone()
            if row is None:
                policy = {
                    "requires_operator_approval": False,
                    "destructive_action": False,
                    "external_side_effect": False,
                    "security_sensitive": False,
                    "broad_architecture": False,
                    "paid_execution": True,
                    "approved_by": None,
                    "approved_at": None,
                    "approval_note": "",
                }
            else:
                policy = dict(row)
                policy.pop("task_id", None)
                for field in POLICY_FLAGS:
                    policy[field] = bool(policy[field])
            task["policy"] = policy
            submission = conn.execute(
                "SELECT * FROM task_submissions WHERE task_id = ?",
                (task_id,),
            ).fetchone()
            task["submission"] = dict(submission) if submission else None
            if submission is None:
                task["review_disqualified_ids"] = []
            else:
                task["review_disqualified_ids"] = sorted(
                    self._continuity_component_conn(conn, submission["author_id"])
                )
        return task

    def list_tasks(
        self,
        *,
        project_id: str | None = None,
        statuses: tuple[str, ...] | None = None,
    ) -> list[dict]:
        clauses: list[str] = []
        params: list[object] = []
        if project_id is not None:
            clauses.append("project_id = ?")
            params.append(project_id)
        if statuses:
            marks = ",".join("?" for _ in statuses)
            clauses.append(f"status IN ({marks})")
            params.extend(status.upper() for status in statuses)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with closing(self._connect()) as conn:
            ids = [
                row["task_id"]
                for row in conn.execute(
                    f"SELECT task_id FROM tasks{where} ORDER BY created_at, task_id",
                    params,
                ).fetchall()
            ]
        return [
            task for task_id in ids if (task := self.get_task(task_id)) is not None
        ]

    def record_operator_approval(
        self,
        task_id: str,
        *,
        approved_by: str,
        note: str,
    ) -> MutationResult:
        if not approved_by.strip():
            return MutationResult(False, "INVALID_APPROVAL", "approved_by is required")
        if not note.strip():
            return MutationResult(False, "INVALID_APPROVAL", "approval note is required")
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            task = conn.execute(
                "SELECT status FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if task is None:
                conn.rollback()
                return MutationResult(False, "NOT_FOUND", f"{task_id} does not exist")
            conn.execute("INSERT OR IGNORE INTO task_policy(task_id) VALUES (?)", (task_id,))
            policy = conn.execute(
                "SELECT * FROM task_policy WHERE task_id = ?", (task_id,)
            ).fetchone()
            if not any(bool(policy[field]) for field in APPROVAL_TRIGGER_FLAGS):
                conn.rollback()
                return MutationResult(
                    False,
                    "NO_APPROVAL_REQUIRED",
                    f"{task_id} has no operator-gated policy flags",
                )
            now = iso_z(utc_now())
            conn.execute(
                """
                UPDATE task_policy
                SET approved_by = ?, approved_at = ?, approval_note = ?
                WHERE task_id = ?
                """,
                (approved_by.strip(), now, note.strip(), task_id),
            )
            self._append_event(
                conn,
                task_id,
                "OPERATOR_APPROVAL_RECORDED",
                approved_by.strip(),
                note.strip(),
            )
            conn.commit()
        return MutationResult(
            True,
            "APPROVED",
            f"operator approval recorded for {task_id}",
            self.get_task(task_id),
        )

    def clear_operator_approval(
        self, task_id: str, *, actor: str, reason: str
    ) -> MutationResult:
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            exists = conn.execute(
                "SELECT 1 FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if not exists:
                conn.rollback()
                return MutationResult(False, "NOT_FOUND", f"{task_id} does not exist")
            conn.execute("INSERT OR IGNORE INTO task_policy(task_id) VALUES (?)", (task_id,))
            conn.execute(
                """
                UPDATE task_policy
                SET approved_by = NULL, approved_at = NULL, approval_note = ''
                WHERE task_id = ?
                """,
                (task_id,),
            )
            self._append_event(
                conn, task_id, "OPERATOR_APPROVAL_CLEARED", actor, reason
            )
            conn.commit()
        return MutationResult(
            True,
            "APPROVAL_CLEARED",
            f"approval cleared for {task_id}",
            self.get_task(task_id),
        )
