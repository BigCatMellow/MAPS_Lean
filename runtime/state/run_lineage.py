from __future__ import annotations

from contextlib import closing
from datetime import datetime
import re
import sqlite3
from typing import Any, Mapping, Sequence

from .common import MutationResult, iso_z, parse_time, utc_now


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:@-]{0,127}$")
_REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:@/#+=-]{0,255}$")


class RunSessionLineageMixin:
    """Append-only adapter-qualified run/session relationships.

    These records identify provider sessions for an immutable run. They do not
    grant task authority and do not represent provider liveness/readiness.
    """

    @staticmethod
    def _lineage_id(value: str, field: str) -> str:
        normalized = value.strip() if isinstance(value, str) else ""
        if not _ID_RE.fullmatch(normalized):
            raise ValueError(f"invalid {field}")
        return normalized

    @staticmethod
    def _evidence_ref(value: str) -> str:
        normalized = value.strip() if isinstance(value, str) else ""
        if not _REF_RE.fullmatch(normalized):
            raise ValueError("invalid evidence_ref")
        return normalized

    @staticmethod
    def _actor(value: str) -> str:
        normalized = value.strip() if isinstance(value, str) else ""
        if not normalized or len(normalized) > 128 or any(ord(ch) < 32 for ch in normalized):
            raise ValueError("invalid created_by")
        return normalized

    @staticmethod
    def _public_link(row: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "link_id": int(row["id"]),
            "run_id": str(row["run_id"]),
            "relation": str(row["relation"]),
            "adapter_id": str(row["adapter_id"]),
            "session_id": str(row["session_id"]),
            "replaces_link_id": (
                int(row["replaces_link_id"])
                if row["replaces_link_id"] is not None
                else None
            ),
            "evidence_ref": str(row["evidence_ref"]),
            "created_by": str(row["created_by"]),
            "created_at": str(row["created_at"]),
        }

    def _resolve_run_session_conn(
        self,
        conn: sqlite3.Connection,
        run_id: str,
        *,
        manifest_session_id: str | None = None,
    ) -> dict[str, Any] | None:
        manifest = conn.execute(
            "SELECT run_id, session_id FROM run_manifests WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        if manifest is None:
            return None

        legacy_session = (
            str(manifest_session_id).strip()
            if manifest_session_id is not None
            else str(manifest["session_id"] or "").strip()
        )
        rows = [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM run_session_links WHERE run_id = ? ORDER BY id",
                (run_id,),
            ).fetchall()
        ]
        if not rows:
            if legacy_session:
                return {
                    "run_id": run_id,
                    "state": "ADAPTER_UNPROVEN",
                    "chain_complete": False,
                    "legacy_manifest_session_id": legacy_session,
                    "current": {
                        "link_id": None,
                        "adapter_id": None,
                        "session_id": legacy_session,
                    },
                    "history": [],
                }
            return {
                "run_id": run_id,
                "state": "UNBOUND",
                "chain_complete": True,
                "legacy_manifest_session_id": None,
                "current": None,
                "history": [],
            }

        by_id = {int(row["id"]): row for row in rows}
        roots = [
            row
            for row in rows
            if row["relation"] == "ATTACH" and row["replaces_link_id"] is None
        ]
        if len(roots) != 1:
            return {
                "run_id": run_id,
                "state": "INVALID",
                "chain_complete": False,
                "reason": "root_count",
                "legacy_manifest_session_id": legacy_session or None,
                "current": None,
                "history": [self._public_link(row) for row in rows],
            }

        children: dict[int, list[dict[str, Any]]] = {}
        for row in rows:
            parent = row["replaces_link_id"]
            if parent is None:
                continue
            parent_id = int(parent)
            if parent_id not in by_id:
                return {
                    "run_id": run_id,
                    "state": "INVALID",
                    "chain_complete": False,
                    "reason": "predecessor_outside_run",
                    "legacy_manifest_session_id": legacy_session or None,
                    "current": None,
                    "history": [self._public_link(item) for item in rows],
                }
            children.setdefault(parent_id, []).append(row)

        ordered: list[dict[str, Any]] = []
        seen: set[int] = set()
        current = roots[0]
        while True:
            current_id = int(current["id"])
            if current_id in seen:
                return {
                    "run_id": run_id,
                    "state": "INVALID",
                    "chain_complete": False,
                    "reason": "cycle",
                    "legacy_manifest_session_id": legacy_session or None,
                    "current": None,
                    "history": [self._public_link(item) for item in rows],
                }
            seen.add(current_id)
            ordered.append(current)
            next_rows = children.get(current_id, [])
            if len(next_rows) > 1:
                return {
                    "run_id": run_id,
                    "state": "INVALID",
                    "chain_complete": False,
                    "reason": "branch",
                    "legacy_manifest_session_id": legacy_session or None,
                    "current": None,
                    "history": [self._public_link(item) for item in rows],
                }
            if not next_rows:
                break
            current = next_rows[0]

        if len(seen) != len(rows):
            return {
                "run_id": run_id,
                "state": "INVALID",
                "chain_complete": False,
                "reason": "disconnected_links",
                "legacy_manifest_session_id": legacy_session or None,
                "current": None,
                "history": [self._public_link(item) for item in rows],
            }

        current_link = self._public_link(ordered[-1])
        return {
            "run_id": run_id,
            "state": "EXPLICIT",
            "chain_complete": True,
            "legacy_manifest_session_id": legacy_session or None,
            "current": current_link,
            "history": [self._public_link(row) for row in ordered],
        }

    def resolve_run_session(self, run_id: str) -> dict[str, Any] | None:
        run_id = run_id.strip() if isinstance(run_id, str) else ""
        if not run_id:
            return None
        with closing(self._connect()) as conn:
            return self._resolve_run_session_conn(conn, run_id)

    def record_run_session_link(
        self,
        run_id: str,
        worker_id: str,
        *,
        adapter_id: str,
        session_id: str,
        evidence_ref: str,
        created_by: str,
        replaces_link_id: int | None = None,
        now: datetime | None = None,
    ) -> MutationResult:
        try:
            run_id = self._lineage_id(run_id, "run_id")
            adapter_id = self._lineage_id(adapter_id, "adapter_id")
            session_id = self._lineage_id(session_id, "session_id")
            evidence_ref = self._evidence_ref(evidence_ref)
            created_by = self._actor(created_by)
        except ValueError as exc:
            return MutationResult(False, "INVALID_SESSION_LINK", str(exc))
        worker_id = worker_id.strip() if isinstance(worker_id, str) else ""
        if not worker_id:
            return MutationResult(False, "INVALID_SESSION_LINK", "worker_id is required")
        if replaces_link_id is not None and (
            isinstance(replaces_link_id, bool)
            or not isinstance(replaces_link_id, int)
            or replaces_link_id <= 0
        ):
            return MutationResult(
                False,
                "INVALID_SESSION_LINK",
                "replaces_link_id must be a positive integer",
            )

        current_time = now or utc_now()
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            manifest = conn.execute(
                "SELECT * FROM run_manifests WHERE run_id = ?", (run_id,)
            ).fetchone()
            if manifest is None:
                conn.rollback()
                return MutationResult(False, "RUN_NOT_FOUND", "run does not exist")
            if str(manifest["worker_id"]).strip() != worker_id:
                conn.rollback()
                return MutationResult(
                    False,
                    "RUN_WORKER_MISMATCH",
                    "session lineage requires the immutable run worker",
                )

            task = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (manifest["task_id"],)
            ).fetchone()
            if task is None:
                conn.rollback()
                return MutationResult(False, "TASK_NOT_FOUND", "run task does not exist")
            if str(task["status"]).upper() != "ACTIVE" or str(task["claimed_by"] or "").strip() != worker_id:
                conn.rollback()
                return MutationResult(
                    False,
                    "RUN_NOT_OWNED",
                    "session lineage requires the current ACTIVE claimant",
                )
            lease = parse_time(task["lease_expires_at"])
            if lease is None or lease <= current_time:
                conn.rollback()
                return MutationResult(
                    False,
                    "LEASE_EXPIRED",
                    "session lineage requires a live task lease",
                )
            current_revision = self._task_revision_conn(conn, str(manifest["task_id"]))
            if current_revision != str(manifest["task_revision"]):
                conn.rollback()
                return MutationResult(
                    False,
                    "RUN_STALE",
                    "task definition changed after the run was created",
                )

            lineage = self._resolve_run_session_conn(
                conn,
                run_id,
                manifest_session_id=str(manifest["session_id"] or ""),
            )
            assert lineage is not None
            if lineage["state"] == "INVALID":
                conn.rollback()
                return MutationResult(
                    False,
                    "SESSION_LINEAGE_INVALID",
                    "existing session lineage is not a single linear chain",
                )

            existing_identity = conn.execute(
                """
                SELECT id, run_id FROM run_session_links
                WHERE adapter_id = ? AND session_id = ?
                """,
                (adapter_id, session_id),
            ).fetchone()
            if existing_identity is not None:
                conn.rollback()
                return MutationResult(
                    False,
                    "SESSION_ALREADY_BOUND",
                    "adapter-qualified provider session is already durably bound",
                )

            history: Sequence[Mapping[str, Any]] = lineage["history"]
            legacy_session = str(manifest["session_id"] or "").strip()
            if not history:
                if replaces_link_id is not None:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "UNEXPECTED_REPLACEMENT_LINK",
                        "first explicit session link cannot replace another link",
                    )
                if legacy_session and legacy_session != session_id:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "MANIFEST_SESSION_CONFLICT",
                        "first explicit session link conflicts with immutable manifest session_id",
                    )
                relation = "ATTACH"
                predecessor = None
            else:
                current = lineage["current"]
                assert isinstance(current, Mapping)
                current_link_id = int(current["link_id"])
                if replaces_link_id is None:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "REPLACEMENT_LINK_REQUIRED",
                        "session replacement must name the current link",
                    )
                if replaces_link_id != current_link_id:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "STALE_SESSION_LINK",
                        "session replacement must replace the current link",
                    )
                if (
                    str(current["adapter_id"]) == adapter_id
                    and str(current["session_id"]) == session_id
                ):
                    conn.rollback()
                    return MutationResult(
                        False,
                        "SESSION_UNCHANGED",
                        "replacement must identify a different provider session",
                    )
                relation = "REPLACE"
                predecessor = current_link_id

            try:
                cursor = conn.execute(
                    """
                    INSERT INTO run_session_links(
                        run_id, relation, adapter_id, session_id,
                        replaces_link_id, evidence_ref, created_by, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        relation,
                        adapter_id,
                        session_id,
                        predecessor,
                        evidence_ref,
                        created_by,
                        iso_z(current_time),
                    ),
                )
            except sqlite3.IntegrityError:
                conn.rollback()
                return MutationResult(
                    False,
                    "SESSION_LINK_CONFLICT",
                    "session lineage constraints rejected the relationship",
                )

            link_id = int(cursor.lastrowid)
            self._append_event(
                conn,
                str(manifest["task_id"]),
                "RUN_SESSION_ATTACHED" if relation == "ATTACH" else "RUN_SESSION_REPLACED",
                created_by,
                f"adapter-qualified session link {link_id} recorded for {run_id}",
            )
            conn.commit()

        resolved = self.resolve_run_session(run_id)
        return MutationResult(
            True,
            "SESSION_ATTACHED" if relation == "ATTACH" else "SESSION_REPLACED",
            f"recorded run/session lineage link {link_id}",
            resolved,
        )
