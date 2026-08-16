from __future__ import annotations

from contextlib import closing
import json
from typing import Any

from runtime.environment import (
    EnvironmentFingerprint,
    EnvironmentSpec,
    evaluate_environment_compatibility,
)

from .common import MutationResult, iso_z, utc_now
from .observability import redact_sensitive_text


class EnvironmentEvidenceMixin:
    """Append-only environment evidence bound to immutable runs.

    Environment evidence describes where/how a run was observed. It does not
    grant task ownership, renew a lease, approve policy, or authorize recovery.
    """

    @staticmethod
    def _canonical_json(value: object) -> str:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    @staticmethod
    def _decode_environment_row(row: Any) -> dict[str, Any]:
        record = dict(row)
        for field in (
            "spec_snapshot",
            "fingerprint_snapshot",
            "compatibility_snapshot",
        ):
            record[field] = json.loads(record[field])
        return record

    def record_run_environment_evidence(
        self,
        run_id: str,
        *,
        spec: EnvironmentSpec,
        fingerprint: EnvironmentFingerprint,
        spec_ref: str,
        recorded_by: str,
        reference: EnvironmentFingerprint | None = None,
    ) -> MutationResult:
        run_id = run_id.strip()
        spec_ref = spec_ref.strip()
        recorded_by = recorded_by.strip()
        if not run_id:
            return MutationResult(False, "INVALID_ENVIRONMENT_EVIDENCE", "run_id is required")
        if not spec_ref:
            return MutationResult(
                False,
                "INVALID_ENVIRONMENT_EVIDENCE",
                "spec_ref is required",
            )
        if not recorded_by:
            return MutationResult(
                False,
                "INVALID_ENVIRONMENT_EVIDENCE",
                "recorded_by is required",
            )
        if redact_sensitive_text(spec_ref) != spec_ref:
            return MutationResult(
                False,
                "SENSITIVE_ENVIRONMENT_REFERENCE",
                "spec_ref appears to contain sensitive text",
            )
        if fingerprint.environment_spec_hash != spec.sha256:
            return MutationResult(
                False,
                "ENVIRONMENT_SPEC_FINGERPRINT_MISMATCH",
                "fingerprint is bound to a different EnvironmentSpec hash",
            )

        report = evaluate_environment_compatibility(
            spec,
            fingerprint,
            reference=reference,
        )
        spec_snapshot = self._canonical_json(spec.to_dict())
        fingerprint_snapshot = self._canonical_json(fingerprint.to_dict())
        compatibility_snapshot = self._canonical_json(report.to_dict())
        for label, snapshot in (
            ("EnvironmentSpec", spec_snapshot),
            ("EnvironmentFingerprint", fingerprint_snapshot),
            ("compatibility report", compatibility_snapshot),
        ):
            if redact_sensitive_text(snapshot) != snapshot:
                return MutationResult(
                    False,
                    "SENSITIVE_ENVIRONMENT_EVIDENCE",
                    f"{label} contains text that must not be persisted as run evidence",
                )
        created_at = iso_z(utc_now())

        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            run = conn.execute(
                "SELECT run_id, task_id FROM run_manifests WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            if run is None:
                conn.rollback()
                return MutationResult(
                    False,
                    "RUN_NOT_FOUND",
                    f"{run_id} does not exist",
                )

            cursor = conn.execute(
                """
                INSERT INTO run_environment_evidence(
                    run_id, spec_ref, environment_spec_hash,
                    fingerprint_sha256, compatibility_state,
                    reference_fingerprint_sha256, spec_snapshot,
                    fingerprint_snapshot, compatibility_snapshot,
                    recorded_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    spec_ref,
                    spec.sha256,
                    fingerprint.sha256,
                    report.state.value,
                    reference.sha256 if reference is not None else None,
                    spec_snapshot,
                    fingerprint_snapshot,
                    compatibility_snapshot,
                    recorded_by,
                    created_at,
                ),
            )
            evidence_id = int(cursor.lastrowid)
            self._append_event(
                conn,
                run["task_id"],
                "RUN_ENVIRONMENT_RECORDED",
                recorded_by,
                f"{run_id} environment evidence {evidence_id}: {report.state.value}",
            )
            conn.commit()

        evidence = self.get_run_environment_evidence(evidence_id)
        return MutationResult(
            True,
            "RUN_ENVIRONMENT_RECORDED",
            f"recorded environment evidence {evidence_id} for {run_id}",
            evidence,
        )

    def get_run_environment_evidence(
        self,
        evidence_id: int,
    ) -> dict[str, Any] | None:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM run_environment_evidence WHERE id = ?",
                (evidence_id,),
            ).fetchone()
        return self._decode_environment_row(row) if row is not None else None

    def list_run_environment_evidence(self, run_id: str) -> list[dict[str, Any]]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT * FROM run_environment_evidence
                WHERE run_id = ?
                ORDER BY id
                """,
                (run_id,),
            ).fetchall()
        return [self._decode_environment_row(row) for row in rows]

    def trace_task(self, task_id: str) -> dict[str, Any] | None:
        """Extend the existing read-only trace with canonical environment evidence."""

        trace = super().trace_task(task_id)
        if trace is None:
            return None
        for run in trace.get("runs", []):
            run["environment_evidence"] = self.list_run_environment_evidence(
                run["run_id"]
            )
        coverage = trace.get("coverage", {}).get("canonical_task_db")
        if isinstance(coverage, dict):
            coverage["run_environment_evidence_included"] = True
        return trace
