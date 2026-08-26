"""Durable storage for Skill trust-lifecycle state (SEC4 / roadmap 6.10, Half 1).

Half 1 of `work/notes/2026-08-25-sec4-skill-lifecycle-persistence-design.md`:
durable storage only. The second half -- real authority wiring (populating
`SkillProvenance.trust_state` from this store, and a first real refusal at
`load_catalog_skill()`) -- is deliberately NOT in this module and has no
caller here. Nothing in `runtime/` outside `runtime/state/store.py` (which
only registers the mixin) calls these methods yet; that call-site question is
answered by the Half-2 task, not by this one.

What this layer does and does not adjudicate:

- It records the *claimed* actor for a transition as a fact. It does not
  verify that `decided_by` names a real, authorized operator -- exactly like
  `OperationalLessonStorageMixin.promote_operational_lesson()`, which requires
  a non-empty `promoted_by` and a `decision_ref` and verifies nothing further.
  Whether a genuine operator-identity source gets checked here or at the read
  side is a Half-2 decision.
- It owns no transition logic. The legal-edge graph and the actor rules live
  in exactly one place, `runtime.skills.lifecycle.transition()`, and this
  module is a *caller* of it -- both when composing the effective state by
  replay and before inserting any new decision row (rule 12, no duplicate
  truth). The SQL `CHECK`s and triggers duplicate a strict subset of those
  rules as defense in depth against direct-SQL writes; they are not the
  primary check and they never widen what the pure module permits.

Behavior questions from the design note, as resolved by this implementation:

1. **`catalog_key` is the primary key.** Identity is content-addressed:
   `"<source_id>:<skill_id>@sha256:<content_sha256>"`. Editing a Skill's
   contents produces a different `catalog_key`, hence a *new* subject that
   starts at `VALIDATED`/`QUARANTINED` and can never inherit the previous
   revision's `APPROVED`/`ACTIVE`. That drift detection is structural -- no
   watcher, no reconciliation pass. `BUNDLED` Skills get no special rule:
   they too need a fresh approval per revision. That is tolerable today
   precisely because nothing consumes this state yet (Half 2 owns the
   question of whether per-revision re-approval needs an ergonomics answer
   for Skills that change with every repo commit).
2. **A Skill that vanishes from disk keeps its row.** Rows are
   trigger-locked immutable and are never deleted, and no read-time
   existence check downgrades a state. A stale subject is harmless: its
   identity is a content hash, so nothing on disk can match it unless the
   exact bytes come back, and activation independently re-verifies the hash
   (`runtime.skills.format.load_skill`). An operator who wants the record to
   say so writes a `RETIRED` decision; the store never infers one.
3. **`DISCOVERED` is never a persisted state.** A subject row is only
   created once a gate report exists, so "discovered but not yet assessed"
   is represented by the *absence* of a row. `get_skill_lifecycle_state()`
   returning `None` means exactly that.
4. **No production caller exists in Half 1**, by design (see above).
8. **`SUPERSEDED` records no successor pointer.** There is no
   `superseded_by` column and no cross-Skill link; a successor, if any, is
   named in the decision's free-text `decision_ref`. Building a supersession
   graph is a non-goal.

`decision_ref` is required and non-empty on *every* decision row, not only
the `-> APPROVED` ones: a transition with no recorded reason is not worth
persisting, and requiring it uniformly keeps the audit trail complete
without adding a second rule to remember.
"""

from __future__ import annotations

from contextlib import closing
import json
import sqlite3
from typing import TYPE_CHECKING, Any

from .common import MutationResult, iso_z, utc_now

if TYPE_CHECKING:  # pragma: no cover - typing only
    from runtime.skills.catalog import SkillCatalogEntry
    from runtime.skills.gate import SkillGateReport
    from runtime.skills.lifecycle import SkillLifecycleState

# `runtime.skills.gate` imports `runtime.state.observability`, and
# `runtime/state/__init__.py` imports `store`, which imports this module. A
# module-level `from runtime.skills...` here would therefore close an import
# cycle whenever `runtime.skills` is the entry point. The imports below are
# done at call time instead. They still resolve to the one canonical
# `runtime.skills.lifecycle`, so patching that module's `transition` is
# observable here -- the storage layer holds no copy of the graph.


def _clean_text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


class SkillLifecycleStorageMixin:
    """Immutable Skill subjects plus append-only lifecycle decisions.

    Effective state is composed by replaying decisions through the pure
    validator, never read from a mutable column.
    """

    # -- row shaping -------------------------------------------------------

    @staticmethod
    def _skill_subject_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "catalog_key": str(row["catalog_key"]),
            "source_id": str(row["source_id"]),
            "source_kind": str(row["source_kind"]),
            "source_ref": row["source_ref"],
            "declared_revision": row["declared_revision"],
            "skill_id": str(row["skill_id"]),
            "skill_name": str(row["skill_name"]),
            "content_sha256": str(row["content_sha256"]),
            "initial_state": str(row["initial_state"]),
            "gate_disposition": str(row["gate_disposition"]),
            "gate_report": json.loads(row["gate_report"]),
            "first_seen_at": str(row["first_seen_at"]),
            "created_at": str(row["created_at"]),
        }

    @staticmethod
    def _skill_decision_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "decision_id": int(row["decision_id"]),
            "catalog_key": str(row["catalog_key"]),
            "from_state": str(row["from_state"]),
            "to_state": str(row["to_state"]),
            "decision_ref": str(row["decision_ref"]),
            "decided_by": row["decided_by"],
            "decided_at": str(row["decided_at"]),
            "created_at": str(row["created_at"]),
        }

    # -- composition -------------------------------------------------------

    @staticmethod
    def _skill_decisions_for(
        conn: sqlite3.Connection, catalog_key: str
    ) -> list[sqlite3.Row]:
        return conn.execute(
            "SELECT * FROM skill_lifecycle_decisions "
            "WHERE catalog_key = ? ORDER BY decision_id",
            (catalog_key,),
        ).fetchall()

    @staticmethod
    def _compose_skill_state(
        base_row: sqlite3.Row, decisions: list[sqlite3.Row]
    ) -> "SkillLifecycleState":
        """Replay the decision chain through the pure validator.

        Raises `SkillLifecycleError` -- loudly, rather than returning a state
        the graph forbids -- if any persisted row implies an illegal edge.
        This is the analogue of `get_operational_lesson()` re-running
        `validate_lesson_record()` on the composed record.
        """

        from runtime.skills import lifecycle as _lifecycle

        SkillLifecycleState = _lifecycle.SkillLifecycleState
        SkillLifecycleError = _lifecycle.SkillLifecycleError

        current = SkillLifecycleState(str(base_row["initial_state"]))
        for decision in decisions:
            recorded_from = SkillLifecycleState(str(decision["from_state"]))
            if recorded_from is not current:
                raise SkillLifecycleError(
                    f"persisted decision {int(decision['decision_id'])} claims "
                    f"from_state {recorded_from.value} but the replayed state is "
                    f"{current.value}"
                )
            target = SkillLifecycleState(str(decision["to_state"]))
            decided_by = decision["decided_by"]
            current = _lifecycle.transition(
                current,
                target,
                actor=decided_by if isinstance(decided_by, str) else None,
            )
        return current

    # -- writes ------------------------------------------------------------

    def record_skill_lifecycle_subject(
        self,
        entry: "SkillCatalogEntry",
        report: "SkillGateReport",
        *,
        first_seen_at: str | None = None,
        now=None,
    ) -> MutationResult:
        """Persist one content-addressed Skill revision and its gate verdict.

        The starting state is derived from the gate report by the existing
        `initial_transition_from_gate_report()`; it is never caller-supplied,
        so a subject cannot be smuggled in already sitting at `APPROVED`.
        """

        from runtime.skills.catalog import SkillCatalogEntry
        from runtime.skills.gate import SkillGateReport
        from runtime.skills.lifecycle import initial_transition_from_gate_report

        current_time = now or utc_now()
        if not isinstance(entry, SkillCatalogEntry):
            return MutationResult(
                False, "INVALID_SKILL_ENTRY", "entry must be a SkillCatalogEntry"
            )
        if not isinstance(report, SkillGateReport):
            return MutationResult(
                False, "INVALID_GATE_REPORT", "report must be a SkillGateReport"
            )
        if report.content_sha256 != entry.descriptor.content_sha256:
            return MutationResult(
                False,
                "GATE_REPORT_MISMATCH",
                "gate report content_sha256 does not match the catalog entry's "
                f"({report.content_sha256} != {entry.descriptor.content_sha256})",
            )

        initial_state = initial_transition_from_gate_report(report)
        catalog_key = entry.catalog_key
        provenance = entry.provenance
        descriptor = entry.descriptor
        recorded_at = iso_z(current_time)
        first_seen = _clean_text(first_seen_at) or recorded_at

        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT 1 FROM skill_lifecycle_subjects WHERE catalog_key = ?",
                (catalog_key,),
            ).fetchone()
            if existing is not None:
                conn.rollback()
                return MutationResult(
                    False,
                    "SKILL_SUBJECT_EXISTS",
                    f"skill lifecycle subject {catalog_key} already exists",
                )
            try:
                conn.execute(
                    """
                    INSERT INTO skill_lifecycle_subjects(
                        catalog_key, source_id, source_kind, source_ref,
                        declared_revision, skill_id, skill_name, content_sha256,
                        initial_state, gate_disposition, gate_report,
                        first_seen_at, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        catalog_key,
                        provenance.source_id,
                        provenance.source_kind.value,
                        provenance.source_ref,
                        provenance.declared_revision,
                        descriptor.skill_id,
                        descriptor.name,
                        descriptor.content_sha256,
                        initial_state.value,
                        report.disposition.value,
                        json.dumps(report.to_dict(), sort_keys=True),
                        first_seen,
                        recorded_at,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                return MutationResult(
                    False,
                    "SKILL_SUBJECT_CONSTRAINT_VIOLATION",
                    f"skill lifecycle subject rejected: {exc}",
                )
            conn.commit()
        return MutationResult(
            True,
            "SKILL_SUBJECT_RECORDED",
            f"skill lifecycle subject {catalog_key} recorded at {initial_state.value}",
            {"catalog_key": catalog_key, "state": initial_state.value},
        )

    def record_skill_lifecycle_transition(
        self,
        catalog_key: str,
        to_state: "SkillLifecycleState",
        *,
        decision_ref: str,
        decided_by: str | None = None,
        now=None,
    ) -> MutationResult:
        """Append one lifecycle decision, validated by the pure state machine.

        The current state is recomputed by replay inside the same transaction
        that inserts, so two concurrent writers cannot both append from the
        same stale state.
        """

        from runtime.skills import lifecycle as _lifecycle

        SkillLifecycleState = _lifecycle.SkillLifecycleState
        SkillLifecycleError = _lifecycle.SkillLifecycleError

        current_time = now or utc_now()
        key = _clean_text(catalog_key)
        if not key:
            return MutationResult(
                False, "INVALID_CATALOG_KEY", "catalog_key is required"
            )
        if not isinstance(to_state, SkillLifecycleState):
            return MutationResult(
                False,
                "INVALID_TARGET_STATE",
                f"to_state must be a SkillLifecycleState, got {to_state!r}",
            )
        ref = _clean_text(decision_ref)
        if not ref:
            return MutationResult(
                False, "INVALID_DECISION_REF", "decision_ref is required"
            )
        actor = _clean_text(decided_by) or None

        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            base_row = conn.execute(
                "SELECT * FROM skill_lifecycle_subjects WHERE catalog_key = ?",
                (key,),
            ).fetchone()
            if base_row is None:
                conn.rollback()
                return MutationResult(
                    False,
                    "SKILL_SUBJECT_NOT_FOUND",
                    f"no skill lifecycle subject {key}",
                )
            decisions = self._skill_decisions_for(conn, key)
            try:
                current = self._compose_skill_state(base_row, decisions)
                _lifecycle.transition(current, to_state, actor=actor)
            except SkillLifecycleError as exc:
                conn.rollback()
                return MutationResult(False, "ILLEGAL_SKILL_TRANSITION", str(exc))

            try:
                conn.execute(
                    """
                    INSERT INTO skill_lifecycle_decisions(
                        catalog_key, from_state, to_state, decision_ref,
                        decided_by, decided_at, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        key,
                        current.value,
                        to_state.value,
                        ref,
                        actor,
                        iso_z(current_time),
                        iso_z(current_time),
                    ),
                )
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                return MutationResult(
                    False,
                    "SKILL_DECISION_CONSTRAINT_VIOLATION",
                    f"skill lifecycle decision rejected: {exc}",
                )
            conn.commit()
        return MutationResult(
            True,
            "SKILL_TRANSITION_RECORDED",
            f"skill {key} moved {current.value} -> {to_state.value}",
            {
                "catalog_key": key,
                "from_state": current.value,
                "to_state": to_state.value,
            },
        )

    # -- reads -------------------------------------------------------------

    def get_skill_lifecycle_state(
        self, catalog_key: str
    ) -> "SkillLifecycleState | None":
        """Composed effective state, or `None` when no subject row exists.

        `None` means "not assessed yet" -- `DISCOVERED` is never persisted.
        """

        key = _clean_text(catalog_key)
        if not key:
            return None
        with closing(self._connect()) as conn:
            base_row = conn.execute(
                "SELECT * FROM skill_lifecycle_subjects WHERE catalog_key = ?",
                (key,),
            ).fetchone()
            if base_row is None:
                return None
            decisions = self._skill_decisions_for(conn, key)
        return self._compose_skill_state(base_row, decisions)

    def get_skill_lifecycle_subject(self, catalog_key: str) -> dict[str, Any] | None:
        """The immutable subject row plus its composed `state`."""

        key = _clean_text(catalog_key)
        if not key:
            return None
        with closing(self._connect()) as conn:
            base_row = conn.execute(
                "SELECT * FROM skill_lifecycle_subjects WHERE catalog_key = ?",
                (key,),
            ).fetchone()
            if base_row is None:
                return None
            decisions = self._skill_decisions_for(conn, key)
        record = self._skill_subject_row(base_row)
        record["state"] = self._compose_skill_state(base_row, decisions).value
        return record

    def list_skill_lifecycle_decisions(self, catalog_key: str) -> list[dict[str, Any]]:
        key = _clean_text(catalog_key)
        if not key:
            return []
        with closing(self._connect()) as conn:
            rows = self._skill_decisions_for(conn, key)
        return [self._skill_decision_row(row) for row in rows]

    def list_skill_lifecycle_subjects(
        self, state: "SkillLifecycleState | None" = None
    ) -> list[dict[str, Any]]:
        """Subjects, optionally filtered to one composed effective state."""

        from runtime.skills.lifecycle import SkillLifecycleError, SkillLifecycleState

        if state is not None and not isinstance(state, SkillLifecycleState):
            raise SkillLifecycleError(f"not a SkillLifecycleState: {state!r}")
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT * FROM skill_lifecycle_subjects "
                "ORDER BY first_seen_at, catalog_key"
            ).fetchall()
            composed = []
            for row in rows:
                record = self._skill_subject_row(row)
                record["state"] = self._compose_skill_state(
                    row, self._skill_decisions_for(conn, str(row["catalog_key"]))
                ).value
                composed.append(record)
        if state is None:
            return composed
        return [record for record in composed if record["state"] == state.value]
