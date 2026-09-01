"""SEC4 Half 3 -- the authorized-operator registry.

`work/notes/2026-08-31-sec4-operator-lifecycle-transitions-and-identity-design.md`
Item B / Q B1-B5, with the operator-decision answers (session 17): a local
append-only registry in the canonical `TaskStore` SQLite file; genesis row
written by `maps init --operator`; fail-open on an empty registry (identity
checks disabled -- byte-identical to pre-registry behavior); a single opt-in
check site (`maps skill approve`, CLI-side per Q B3).

This layer is a faithful recorder plus the "who may authorize whom" rule the
registry exists to hold:

- an operator is authorized *as of now* iff it has an `authorized_operators`
  row and no `authorized_operator_revocations` row -- composed, never a mutable
  column (house rule, rule 12);
- the first row (empty table) is the genesis row; its `added_by` MUST be the
  ``GENESIS`` sentinel;
- every later `record_authorized_operator` / `revoke_authorized_operator` MUST
  name an `added_by` / `revoked_by` that is itself currently authorized.

It does NOT: verify identity by any means beyond "is this id in the registry",
add login / session / credential machinery, read a config file / IdP / OS
user, retroactively validate any already-recorded `decided_by` string, or
gate any existing caller (the check is opt-in-by-data, applied only at the
`maps skill approve` CLI site when the registry is non-empty).
"""

from __future__ import annotations

from contextlib import closing
import sqlite3
from typing import Any

from .common import MutationResult, iso_z, utc_now

GENESIS_AUTHORIZER = "GENESIS"


def _clean(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


class AuthorizedOperatorStorageMixin:
    """Append-only authorized-operator registry, composed authorization state."""

    @staticmethod
    def _authorized_operator_row(
        row: sqlite3.Row, revocation: sqlite3.Row | None
    ) -> dict[str, Any]:
        return {
            "operator_id": str(row["operator_id"]),
            "display_name": row["display_name"],
            "added_by": str(row["added_by"]),
            "decision_ref": str(row["decision_ref"]),
            "added_at": str(row["added_at"]),
            "authorized": revocation is None,
            "revoked_by": str(revocation["revoked_by"]) if revocation else None,
            "revoked_at": str(revocation["revoked_at"]) if revocation else None,
            "revocation_decision_ref": (
                str(revocation["decision_ref"]) if revocation else None
            ),
        }

    @staticmethod
    def _latest_revocation(conn: sqlite3.Connection, operator_id: str) -> sqlite3.Row | None:
        return conn.execute(
            "SELECT * FROM authorized_operator_revocations "
            "WHERE operator_id = ? ORDER BY revocation_id DESC LIMIT 1",
            (operator_id,),
        ).fetchone()

    @classmethod
    def _is_authorized_conn(cls, conn: sqlite3.Connection, operator_id: str) -> bool:
        if not operator_id:
            return False
        added = conn.execute(
            "SELECT 1 FROM authorized_operators WHERE operator_id = ?",
            (operator_id,),
        ).fetchone()
        if added is None:
            return False
        return cls._latest_revocation(conn, operator_id) is None

    # -- reads ----------------------------------------------------------------

    def has_authorized_operator_registry(self) -> bool:
        """True once at least one operator has ever been recorded. This is the
        opt-in-by-data switch: while it is False, identity checks are inert."""
        with closing(self._connect()) as conn:
            return (
                conn.execute(
                    "SELECT 1 FROM authorized_operators LIMIT 1"
                ).fetchone()
                is not None
            )

    def is_authorized_operator(self, operator_id: str) -> bool:
        with closing(self._connect()) as conn:
            return self._is_authorized_conn(conn, _clean(operator_id))

    def list_authorized_operators(self) -> list[dict[str, Any]]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT * FROM authorized_operators ORDER BY added_at, operator_id"
            ).fetchall()
            return [
                self._authorized_operator_row(
                    row, self._latest_revocation(conn, str(row["operator_id"]))
                )
                for row in rows
            ]

    # -- writes -------------------------------------------------------------

    def record_authorized_operator(
        self,
        operator_id: str,
        *,
        added_by: str,
        decision_ref: str,
        display_name: str | None = None,
        now=None,
    ) -> MutationResult:
        op = _clean(operator_id)
        by = _clean(added_by)
        ref = _clean(decision_ref)
        name = display_name.strip() if isinstance(display_name, str) and display_name.strip() else None
        if not op:
            return MutationResult(False, "INVALID_OPERATOR_ID", "operator_id is required")
        if not by:
            return MutationResult(False, "INVALID_AUTHORIZER", "added_by is required")
        if not ref:
            return MutationResult(False, "INVALID_DECISION_REF", "decision_ref is required")
        stamp = iso_z((now or utc_now()))
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            registry_seeded = (
                conn.execute("SELECT 1 FROM authorized_operators LIMIT 1").fetchone()
                is not None
            )
            if not registry_seeded:
                if by != GENESIS_AUTHORIZER:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "GENESIS_REQUIRED",
                        f"the first authorized operator must be added with "
                        f"added_by={GENESIS_AUTHORIZER!r}",
                    )
            else:
                if by == GENESIS_AUTHORIZER:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "GENESIS_ALREADY_SEEDED",
                        "the registry is already seeded; a later operator must be "
                        "added by an already-authorized operator",
                    )
                if not self._is_authorized_conn(conn, by):
                    conn.rollback()
                    return MutationResult(
                        False,
                        "UNAUTHORIZED_AUTHORIZER",
                        f"{by!r} is not a currently authorized operator",
                    )
            if conn.execute(
                "SELECT 1 FROM authorized_operators WHERE operator_id = ?", (op,)
            ).fetchone():
                conn.rollback()
                return MutationResult(
                    False,
                    "OPERATOR_ALREADY_RECORDED",
                    f"{op!r} is already in the registry",
                )
            try:
                conn.execute(
                    "INSERT INTO authorized_operators("
                    "operator_id, display_name, added_by, decision_ref, "
                    "added_at, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (op, name, by, ref, stamp, stamp),
                )
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                return MutationResult(False, "INVALID_OPERATOR_RECORD", str(exc))
            conn.commit()
        return MutationResult(
            True,
            "OPERATOR_AUTHORIZED",
            f"{op} authorized by {by}",
            {"operator_id": op, "added_by": by},
        )

    def revoke_authorized_operator(
        self,
        operator_id: str,
        *,
        revoked_by: str,
        decision_ref: str,
        now=None,
    ) -> MutationResult:
        op = _clean(operator_id)
        by = _clean(revoked_by)
        ref = _clean(decision_ref)
        if not op:
            return MutationResult(False, "INVALID_OPERATOR_ID", "operator_id is required")
        if not by:
            return MutationResult(False, "INVALID_AUTHORIZER", "revoked_by is required")
        if not ref:
            return MutationResult(False, "INVALID_DECISION_REF", "decision_ref is required")
        stamp = iso_z((now or utc_now()))
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute(
                "SELECT 1 FROM authorized_operators WHERE operator_id = ?", (op,)
            ).fetchone() is None:
                conn.rollback()
                return MutationResult(
                    False, "OPERATOR_NOT_RECORDED", f"{op!r} is not in the registry"
                )
            if self._latest_revocation(conn, op) is not None:
                conn.rollback()
                return MutationResult(
                    False, "OPERATOR_ALREADY_REVOKED", f"{op!r} is already revoked"
                )
            if not self._is_authorized_conn(conn, by):
                conn.rollback()
                return MutationResult(
                    False,
                    "UNAUTHORIZED_AUTHORIZER",
                    f"{by!r} is not a currently authorized operator",
                )
            # Refuse to revoke the last authorized operator: that would leave a
            # non-empty registry with nobody able to pass `maps skill approve`
            # and no in-slice way to re-seed (rotation is out of scope, Q B5).
            other_authorized = conn.execute(
                "SELECT o.operator_id FROM authorized_operators o "
                "WHERE o.operator_id <> ? AND NOT EXISTS ("
                "  SELECT 1 FROM authorized_operator_revocations r "
                "  WHERE r.operator_id = o.operator_id)",
                (op,),
            ).fetchone()
            if other_authorized is None:
                conn.rollback()
                return MutationResult(
                    False,
                    "CANNOT_REVOKE_LAST_OPERATOR",
                    "at least one authorized operator must remain; add another "
                    "before revoking this one",
                )
            conn.execute(
                "INSERT INTO authorized_operator_revocations("
                "operator_id, revoked_by, decision_ref, revoked_at, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (op, by, ref, stamp, stamp),
            )
            conn.commit()
        return MutationResult(
            True, "OPERATOR_REVOKED", f"{op} revoked by {by}", {"operator_id": op}
        )
