from __future__ import annotations

from contextlib import closing
import json
import sqlite3
from typing import Any

from runtime.incident_taxonomy import classify_failure_text
from runtime.text_redaction import redact_sensitive_text

from .common import iso_z, utc_now

__all__ = ["ObservabilityMixin", "redact_sensitive_text"]


def _redact_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact_sensitive_text(value)
    if isinstance(value, dict):
        return {key: _redact_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact_value(item) for item in value]
    return value


class ObservabilityMixin:
    """Secret-safer events plus a read-only trace projection.

    Canonical evidence remains in its owning tables. Diagnostic reads are
    redacted, and trace is disposable and explicit about source gaps.
    """

    @staticmethod
    def _append_event(
        conn: sqlite3.Connection,
        task_id: str,
        event_type: str,
        actor: str | None,
        summary: str,
    ) -> None:
        conn.execute(
            """
            INSERT INTO task_events(task_id, event_type, actor, summary, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                task_id,
                event_type,
                actor,
                redact_sensitive_text(summary),
                iso_z(utc_now()),
            ),
        )

    def list_events(self, task_id: str) -> list[dict[str, Any]]:
        """Return a redacted diagnostic view without rewriting stored history."""

        with closing(self._connect()) as conn:
            rows = [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM task_events WHERE task_id = ? ORDER BY id",
                    (task_id,),
                ).fetchall()
            ]
        return _redact_value(rows)

    def list_reviews(self, task_id: str) -> list[dict[str, Any]]:
        """Return redacted review text while preserving canonical review rows."""

        with closing(self._connect()) as conn:
            rows = [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM reviews WHERE task_id = ? ORDER BY id",
                    (task_id,),
                ).fetchall()
            ]
        return _redact_value(rows)

    @staticmethod
    def _decode_json_fields(record: dict[str, Any], fields: tuple[str, ...]) -> None:
        for field in fields:
            raw = record.get(field)
            if isinstance(raw, str):
                try:
                    record[field] = json.loads(raw)
                except json.JSONDecodeError:
                    record[field] = raw

    def trace_task(self, task_id: str) -> dict[str, Any] | None:
        task = self.get_task(task_id)
        if task is None:
            return None

        with closing(self._connect()) as conn:
            submission_row = conn.execute(
                "SELECT * FROM task_submissions WHERE task_id = ?", (task_id,)
            ).fetchone()
            submission = dict(submission_row) if submission_row else None
            if submission is not None:
                evidence = str(submission.pop("evidence", ""))
                submission["evidence"] = {
                    "included": False,
                    "present": bool(evidence),
                    "characters": len(evidence),
                    "reason": "raw submission evidence is omitted from trace v1",
                }

            reviews = [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM reviews WHERE task_id = ? ORDER BY id",
                    (task_id,),
                ).fetchall()
            ]
            events = [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM task_events WHERE task_id = ? ORDER BY id",
                    (task_id,),
                ).fetchall()
            ]

            runs: list[dict[str, Any]] = []
            for row in conn.execute(
                "SELECT * FROM run_manifests WHERE task_id = ? ORDER BY created_at, run_id",
                (task_id,),
            ).fetchall():
                run = dict(row)
                self._decode_json_fields(
                    run,
                    (
                        "readable_scope",
                        "writable_scope",
                        "forbidden_scope",
                        "runtime_limits",
                    ),
                )
                run["context_refs"] = [
                    dict(ref)
                    for ref in conn.execute(
                        """
                        SELECT path, sha256
                        FROM run_context_refs
                        WHERE run_id = ?
                        ORDER BY path
                        """,
                        (run["run_id"],),
                    ).fetchall()
                ]
                worktree = conn.execute(
                    "SELECT * FROM run_worktree_bindings WHERE run_id = ?",
                    (run["run_id"],),
                ).fetchone()
                run["worktree"] = dict(worktree) if worktree is not None else None
                runs.append(run)

            policy_row = conn.execute(
                "SELECT * FROM task_policy WHERE task_id = ?", (task_id,)
            ).fetchone()
            policy = dict(policy_row) if policy_row else None

            criterion_claims: list[dict[str, Any]] = []
            claim_ids: list[int] = []
            for row in conn.execute(
                """
                SELECT *
                FROM submission_criterion_claims
                WHERE task_id = ?
                ORDER BY id
                """,
                (task_id,),
            ).fetchall():
                claim = dict(row)
                self._decode_json_fields(claim, ("evidence_refs",))
                criterion_claims.append(claim)
                claim_ids.append(int(claim["id"]))

            criterion_verdicts: list[dict[str, Any]] = []
            if claim_ids:
                placeholders = ",".join("?" for _ in claim_ids)
                criterion_verdicts = [
                    dict(row)
                    for row in conn.execute(
                        f"""
                        SELECT *
                        FROM submission_criterion_verdicts
                        WHERE claim_id IN ({placeholders})
                        ORDER BY id
                        """,
                        tuple(claim_ids),
                    ).fetchall()
                ]

            outcomes = [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM task_outcomes WHERE task_id = ? ORDER BY id",
                    (task_id,),
                ).fetchall()
            ]
            for outcome in outcomes:
                outcome["escaped_defect"] = bool(outcome["escaped_defect"])
                outcome["incident_class"] = classify_failure_text(
                    outcome.get("failure_class")
                ).value

            revision_method = getattr(self, "_task_revision_conn", None)
            task_revision = (
                revision_method(conn, task_id) if callable(revision_method) else None
            )

        return _redact_value(
            {
                "task_id": task_id,
                "task_revision": task_revision,
                "task": task,
                "policy": policy,
                "submission": submission,
                "reviews": reviews,
                "runs": runs,
                "outcomes": outcomes,
                "criterion_evidence": {
                    "claims": criterion_claims,
                    "verdicts": criterion_verdicts,
                },
                "timeline": events,
                "coverage": {
                    "canonical_task_db": {
                        "included": True,
                        "timeline_source": "task_events",
                        "outcomes_included": True,
                    },
                    "communication": {
                        "included": False,
                        "complete": False,
                        "sources": ["hcom"],
                        "reason": (
                            "trace v1 does not yet correlate hcom messages to tasks"
                        ),
                    },
                    "external_runtime_evidence": {
                        "included": False,
                        "complete": False,
                        "sources": [
                            ".maps/state/recovery.json",
                            ".maps/state/helper-runs.json",
                            ".maps/state/escalations/",
                        ],
                        "reason": "trace v1 is a canonical task-DB projection only",
                    },
                },
            }
        )
