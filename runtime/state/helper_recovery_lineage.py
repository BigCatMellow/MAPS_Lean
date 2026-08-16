from __future__ import annotations

from contextlib import closing
from datetime import datetime
import re
import sqlite3
from typing import Any, Mapping

from .common import MutationResult, iso_z, parse_time, utc_now


_HELPER_ID = re.compile(r"^HELP-[0-9a-f]{12}$")
_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:@/#+=-]{0,255}$")


class HelperRecoveryLineageMixin:
    """Append-only cross-source helper and recovery relationships.

    Helper result JSON and RecoveryStore retain ownership of their mutable/result
    facts. These rows record only relationships to immutable MAPS runs.
    """

    @staticmethod
    def _required_text(value: object, field: str, *, limit: int = 128) -> str:
        normalized = value.strip() if isinstance(value, str) else ""
        if not normalized or len(normalized) > limit or any(ord(ch) < 32 for ch in normalized):
            raise ValueError(f"invalid {field}")
        return normalized

    @staticmethod
    def _helper_id(value: object) -> str:
        normalized = value.strip() if isinstance(value, str) else ""
        if not _HELPER_ID.fullmatch(normalized):
            raise ValueError("invalid helper_run_id")
        return normalized

    @staticmethod
    def _ref(value: object, field: str) -> str:
        normalized = value.strip() if isinstance(value, str) else ""
        if not _REF.fullmatch(normalized):
            raise ValueError(f"invalid {field}")
        return normalized

    @staticmethod
    def _helper_link(row: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "helper_run_id": str(row["helper_run_id"]),
            "run_id": str(row["run_id"]),
            "invoker_worker_id": str(row["invoker_worker_id"]),
            "parent_session_link_id": (
                int(row["parent_session_link_id"])
                if row["parent_session_link_id"] is not None
                else None
            ),
            "parent_helper_run_id": (
                str(row["parent_helper_run_id"])
                if row["parent_helper_run_id"] is not None
                else None
            ),
            "evidence_ref": str(row["evidence_ref"]),
            "created_by": str(row["created_by"]),
            "created_at": str(row["created_at"]),
        }

    @staticmethod
    def _recovery_link(row: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "link_id": int(row["id"]),
            "predecessor_run_id": str(row["predecessor_run_id"]),
            "replacement_run_id": str(row["replacement_run_id"]),
            "recovery_ref": str(row["recovery_ref"]),
            "evidence_ref": str(row["evidence_ref"]),
            "created_by": str(row["created_by"]),
            "created_at": str(row["created_at"]),
        }

    def _require_current_run_invoker(
        self,
        conn: sqlite3.Connection,
        run_id: str,
        worker_id: str,
        now: datetime,
    ) -> tuple[sqlite3.Row | None, MutationResult | None]:
        manifest = conn.execute(
            "SELECT * FROM run_manifests WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        if manifest is None:
            return None, MutationResult(False, "RUN_NOT_FOUND", "run does not exist")
        if str(manifest["worker_id"]).strip() != worker_id:
            return None, MutationResult(
                False,
                "RUN_WORKER_MISMATCH",
                "helper lineage requires the immutable run worker",
            )
        task = conn.execute(
            "SELECT * FROM tasks WHERE task_id = ?",
            (manifest["task_id"],),
        ).fetchone()
        if task is None:
            return None, MutationResult(False, "TASK_NOT_FOUND", "run task does not exist")
        if str(task["status"]).upper() != "ACTIVE" or str(task["claimed_by"] or "").strip() != worker_id:
            return None, MutationResult(
                False,
                "RUN_NOT_OWNED",
                "helper lineage requires the current ACTIVE claimant",
            )
        lease = parse_time(task["lease_expires_at"])
        if lease is None or lease <= now:
            return None, MutationResult(
                False,
                "LEASE_EXPIRED",
                "helper lineage requires a live task lease",
            )
        revision = self._task_revision_conn(conn, str(manifest["task_id"]))
        if revision != str(manifest["task_revision"]):
            return None, MutationResult(
                False,
                "RUN_STALE",
                "task definition changed after the run was created",
            )
        return manifest, None

    def record_run_helper_link(
        self,
        run_id: str,
        helper_run_id: str,
        invoker_worker_id: str,
        *,
        evidence_ref: str,
        created_by: str,
        parent_session_link_id: int | None = None,
        parent_helper_run_id: str | None = None,
        now: datetime | None = None,
    ) -> MutationResult:
        try:
            run_id = self._required_text(run_id, "run_id")
            helper_run_id = self._helper_id(helper_run_id)
            invoker_worker_id = self._required_text(invoker_worker_id, "invoker_worker_id")
            evidence_ref = self._ref(evidence_ref, "evidence_ref")
            created_by = self._required_text(created_by, "created_by")
            if parent_helper_run_id is not None:
                parent_helper_run_id = self._helper_id(parent_helper_run_id)
        except ValueError as exc:
            return MutationResult(False, "INVALID_HELPER_LINK", str(exc))
        if parent_session_link_id is not None and (
            isinstance(parent_session_link_id, bool)
            or not isinstance(parent_session_link_id, int)
            or parent_session_link_id <= 0
        ):
            return MutationResult(
                False,
                "INVALID_HELPER_LINK",
                "parent_session_link_id must be a positive integer",
            )
        if parent_session_link_id is not None and parent_helper_run_id is not None:
            return MutationResult(
                False,
                "AMBIGUOUS_HELPER_PARENT",
                "helper invocation may have one immediate parent only",
            )
        if parent_helper_run_id == helper_run_id:
            return MutationResult(False, "HELPER_SELF_PARENT", "helper cannot parent itself")

        current_time = now or utc_now()
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            manifest, error = self._require_current_run_invoker(
                conn, run_id, invoker_worker_id, current_time
            )
            if error is not None:
                conn.rollback()
                return error
            assert manifest is not None

            if parent_session_link_id is not None:
                parent = conn.execute(
                    "SELECT run_id FROM run_session_links WHERE id = ?",
                    (parent_session_link_id,),
                ).fetchone()
                if parent is None or str(parent["run_id"]) != run_id:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "PARENT_SESSION_MISMATCH",
                        "parent session link must belong to the same run",
                    )
            if parent_helper_run_id is not None:
                parent = conn.execute(
                    "SELECT run_id FROM run_helper_links WHERE helper_run_id = ?",
                    (parent_helper_run_id,),
                ).fetchone()
                if parent is None or str(parent["run_id"]) != run_id:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "PARENT_HELPER_MISMATCH",
                        "parent helper must belong to the same run",
                    )

            try:
                conn.execute(
                    """
                    INSERT INTO run_helper_links(
                        helper_run_id, run_id, invoker_worker_id,
                        parent_session_link_id, parent_helper_run_id,
                        evidence_ref, created_by, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        helper_run_id,
                        run_id,
                        invoker_worker_id,
                        parent_session_link_id,
                        parent_helper_run_id,
                        evidence_ref,
                        created_by,
                        iso_z(current_time),
                    ),
                )
            except sqlite3.IntegrityError:
                conn.rollback()
                return MutationResult(
                    False,
                    "HELPER_LINK_CONFLICT",
                    "helper lineage constraints rejected the relationship",
                )
            self._append_event(
                conn,
                str(manifest["task_id"]),
                "RUN_HELPER_LINKED",
                created_by,
                f"helper invocation {helper_run_id} linked to {run_id}",
            )
            conn.commit()
        return MutationResult(
            True,
            "HELPER_LINKED",
            f"helper invocation {helper_run_id} linked to run",
            self.get_run_helper_link(helper_run_id),
        )

    def get_run_helper_link(self, helper_run_id: str) -> dict[str, Any] | None:
        try:
            helper_run_id = self._helper_id(helper_run_id)
        except ValueError:
            return None
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM run_helper_links WHERE helper_run_id = ?",
                (helper_run_id,),
            ).fetchone()
            return self._helper_link(row) if row is not None else None

    def list_run_helper_links(self, run_id: str) -> list[dict[str, Any]]:
        run_id = run_id.strip() if isinstance(run_id, str) else ""
        if not run_id:
            return []
        with closing(self._connect()) as conn:
            return [
                self._helper_link(row)
                for row in conn.execute(
                    "SELECT * FROM run_helper_links WHERE run_id = ? ORDER BY created_at, helper_run_id",
                    (run_id,),
                ).fetchall()
            ]

    def record_run_recovery_link(
        self,
        predecessor_run_id: str,
        replacement_run_id: str,
        *,
        recovery_ref: str,
        evidence_ref: str,
        created_by: str,
        now: datetime | None = None,
    ) -> MutationResult:
        try:
            predecessor_run_id = self._required_text(predecessor_run_id, "predecessor_run_id")
            replacement_run_id = self._required_text(replacement_run_id, "replacement_run_id")
            recovery_ref = self._ref(recovery_ref, "recovery_ref")
            evidence_ref = self._ref(evidence_ref, "evidence_ref")
            created_by = self._required_text(created_by, "created_by")
        except ValueError as exc:
            return MutationResult(False, "INVALID_RECOVERY_LINK", str(exc))
        if predecessor_run_id == replacement_run_id:
            return MutationResult(False, "RECOVERY_SELF_LINK", "recovery replacement must be a different run")

        current_time = now or utc_now()
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            predecessor = conn.execute(
                "SELECT * FROM run_manifests WHERE run_id = ?",
                (predecessor_run_id,),
            ).fetchone()
            replacement = conn.execute(
                "SELECT * FROM run_manifests WHERE run_id = ?",
                (replacement_run_id,),
            ).fetchone()
            if predecessor is None or replacement is None:
                conn.rollback()
                return MutationResult(
                    False,
                    "RUN_NOT_FOUND",
                    "both predecessor and replacement runs must exist",
                )
            if str(predecessor["task_id"]) != str(replacement["task_id"]):
                conn.rollback()
                return MutationResult(
                    False,
                    "RECOVERY_TASK_MISMATCH",
                    "recovery predecessor and replacement must belong to the same task",
                )
            predecessor_time = parse_time(predecessor["created_at"])
            replacement_time = parse_time(replacement["created_at"])
            if (
                predecessor_time is None
                or replacement_time is None
                or replacement_time < predecessor_time
            ):
                conn.rollback()
                return MutationResult(
                    False,
                    "RECOVERY_TIME_CONFLICT",
                    "replacement run cannot predate predecessor run",
                )
            try:
                cursor = conn.execute(
                    """
                    INSERT INTO run_recovery_links(
                        predecessor_run_id, replacement_run_id,
                        recovery_ref, evidence_ref, created_by, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        predecessor_run_id,
                        replacement_run_id,
                        recovery_ref,
                        evidence_ref,
                        created_by,
                        iso_z(current_time),
                    ),
                )
            except sqlite3.IntegrityError:
                conn.rollback()
                return MutationResult(
                    False,
                    "RECOVERY_LINK_CONFLICT",
                    "recovery lineage constraints rejected the relationship",
                )
            link_id = int(cursor.lastrowid)
            self._append_event(
                conn,
                str(predecessor["task_id"]),
                "RUN_RECOVERY_LINKED",
                created_by,
                f"replacement run {replacement_run_id} linked after {predecessor_run_id}",
            )
            conn.commit()
        return MutationResult(
            True,
            "RECOVERY_LINKED",
            f"recovery relationship {link_id} recorded",
            self.get_run_recovery_link(link_id),
        )

    def get_run_recovery_link(self, link_id: int) -> dict[str, Any] | None:
        if isinstance(link_id, bool) or not isinstance(link_id, int) or link_id <= 0:
            return None
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM run_recovery_links WHERE id = ?",
                (link_id,),
            ).fetchone()
            return self._recovery_link(row) if row is not None else None

    def list_run_recovery_links(self, run_id: str) -> list[dict[str, Any]]:
        run_id = run_id.strip() if isinstance(run_id, str) else ""
        if not run_id:
            return []
        with closing(self._connect()) as conn:
            return [
                self._recovery_link(row)
                for row in conn.execute(
                    """
                    SELECT * FROM run_recovery_links
                    WHERE predecessor_run_id = ? OR replacement_run_id = ?
                    ORDER BY id
                    """,
                    (run_id, run_id),
                ).fetchall()
            ]
