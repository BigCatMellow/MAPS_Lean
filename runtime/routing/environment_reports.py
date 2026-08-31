from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, Iterable, Mapping

from runtime.state import TaskStore

if TYPE_CHECKING:
    from runtime.environment.fingerprint import CompatibilityReport


@dataclass(frozen=True, slots=True)
class RoutingEnvironmentReportSelection:
    reports: dict[str, "CompatibilityReport"] = field(default_factory=dict)
    diagnostics: dict[str, str] = field(default_factory=dict)


def _time(value: object, field_name: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a timestamp string")
    text = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError(f"{field_name} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _positive_int(value: object, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _safe_spec_ref(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("spec_ref must be non-empty text")
    text = value.strip()
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or text in {".", "./"}:
        raise ValueError("spec_ref must be a safe repo-relative path")
    return path.as_posix()


def _report(value: object) -> "CompatibilityReport":
    from runtime.environment.fingerprint import CompatibilityReport, CompatibilityState

    if not isinstance(value, Mapping):
        raise ValueError("report must be an object")
    state = value.get("state")
    reasons = value.get("reasons", [])
    warnings = value.get("warnings", [])
    environment_spec_hash = value.get("environment_spec_hash")
    fingerprint_sha256 = value.get("fingerprint_sha256")
    reference_fingerprint_sha256 = value.get("reference_fingerprint_sha256")
    if not isinstance(state, str):
        raise ValueError("report.state must be a string")
    if not isinstance(reasons, (list, tuple)) or not all(
        isinstance(item, str) for item in reasons
    ):
        raise ValueError("report.reasons must be strings")
    if not isinstance(warnings, (list, tuple)) or not all(
        isinstance(item, str) for item in warnings
    ):
        raise ValueError("report.warnings must be strings")
    if not isinstance(environment_spec_hash, str) or not isinstance(
        fingerprint_sha256, str
    ):
        raise ValueError("report hashes must be strings")
    if reference_fingerprint_sha256 is not None and not isinstance(
        reference_fingerprint_sha256, str
    ):
        raise ValueError("reference_fingerprint_sha256 must be a string or null")
    return CompatibilityReport(
        state=CompatibilityState(state),
        reasons=tuple(reasons),
        warnings=tuple(warnings),
        environment_spec_hash=environment_spec_hash,
        fingerprint_sha256=fingerprint_sha256,
        reference_fingerprint_sha256=reference_fingerprint_sha256,
    )


def _freshness_diagnostic(
    report: "CompatibilityReport",
    *,
    spec_sha256: str,
    produced_at: datetime,
    now: datetime,
    max_age_seconds: int,
    recorded_task_revision: str | None,
    current_task_revision: str | None,
    allow_older_task_revision: bool,
) -> str:
    """Shared freshness predicate for every routing environment-report source.

    Returns ``"fresh"`` when the report may be handed to the pure router, or a
    single diagnostic token naming why it was dropped. Both the caller-supplied
    envelope filter and the recorded-evidence projection call this so the
    freshness rules never diverge (no second copy of the predicate logic).
    """

    if report.environment_spec_hash != spec_sha256:
        return "spec_hash_mismatch"
    if recorded_task_revision != current_task_revision and not allow_older_task_revision:
        return "task_revision_mismatch"
    age = (now - produced_at).total_seconds()
    if age < 0:
        return "produced_at_in_future"
    if age > max_age_seconds:
        return "report_stale"
    return "fresh"


def select_fresh_environment_reports(
    envelopes: Mapping[str, Mapping[str, Any]],
    *,
    store: TaskStore,
    repo_root: str | Path = ".",
    now: datetime | None = None,
) -> RoutingEnvironmentReportSelection:
    """Select fresh caller-supplied routing environment reports.

    This is a pure routing-boundary filter. It never inspects the environment,
    computes a fingerprint, writes state, or turns stale/malformed/missing
    evidence into an incompatibility. Invalid entries are reported in
    diagnostics and omitted from the returned router input.
    """

    root = Path(repo_root).resolve()
    current_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    reports: dict[str, "CompatibilityReport"] = {}
    diagnostics: dict[str, str] = {}

    for raw_key, raw_envelope in envelopes.items():
        task_id = str(raw_key)
        try:
            if not isinstance(raw_envelope, Mapping):
                raise ValueError("envelope must be an object")
            declared_task_id = str(raw_envelope.get("task_id", "")).strip()
            if declared_task_id != task_id:
                raise ValueError("task_id mismatch")
            task = store.get_task(task_id)
            if task is None:
                diagnostics[task_id] = "task_missing"
                continue
            project_id = str(raw_envelope.get("project_id", "")).strip()
            if project_id and project_id != str(task.get("project_id", "")).strip():
                diagnostics[task_id] = "project_mismatch"
                continue
            spec_ref = _safe_spec_ref(raw_envelope.get("spec_ref"))
            from runtime.environment.spec import load_environment_spec

            spec = load_environment_spec(root / spec_ref)
            report = _report(raw_envelope.get("report"))
            task_revision = str(raw_envelope.get("task_revision", "")).strip()
            produced_at = _time(raw_envelope.get("produced_at"), "produced_at")
            max_age_seconds = _positive_int(
                raw_envelope.get("max_age_seconds"), "max_age_seconds"
            )
            diagnostic = _freshness_diagnostic(
                report,
                spec_sha256=spec.sha256,
                produced_at=produced_at,
                now=current_time,
                max_age_seconds=max_age_seconds,
                recorded_task_revision=task_revision,
                current_task_revision=store.compute_task_revision(task_id),
                allow_older_task_revision=False,
            )
            if diagnostic == "fresh":
                reports[task_id] = report
            diagnostics[task_id] = diagnostic
        except Exception:
            diagnostics[task_id] = "malformed_envelope"
    return RoutingEnvironmentReportSelection(reports=reports, diagnostics=diagnostics)


def _latest_recorded_evidence(store: TaskStore, task_id: str) -> dict[str, Any] | None:
    """Return the newest run environment-evidence row for a task, or ``None``.

    Sources only the canonical immutable run-scoped ``run_environment_evidence``
    store via the read-only task trace. It never inspects an environment or
    writes state.
    """

    trace = store.trace_task(task_id)
    if trace is None:
        return None
    latest: dict[str, Any] | None = None
    for run in trace.get("runs", []):
        run_revision = run.get("task_revision")
        for evidence in run.get("environment_evidence", []):
            marker = (str(evidence.get("created_at", "")), int(evidence.get("id", 0)))
            if latest is None or marker > latest["_marker"]:
                latest = {
                    "_marker": marker,
                    "created_at": evidence.get("created_at"),
                    "task_revision": run_revision,
                    "compatibility_snapshot": evidence.get("compatibility_snapshot"),
                }
    return latest


def select_recorded_environment_reports(
    store: TaskStore,
    task_ids: Iterable[str],
    *,
    repo_root: str | Path = ".",
    now: datetime | None = None,
) -> RoutingEnvironmentReportSelection:
    """Project fresh routing environment reports from recorded run evidence.

    This is the production read-side of roadmap 6.24: instead of a caller
    hand-assembling ``--environment-reports-json``, each task's latest
    ``run_environment_evidence`` row (written at ``maps flow start``) is filtered
    through the same freshness predicate as the caller-supplied path
    (:func:`_freshness_diagnostic`) and, when fresh, yielded as a
    ``CompatibilityReport``.

    Like :func:`select_fresh_environment_reports` this is a pure routing-boundary
    filter: it never inspects the environment, computes a fingerprint, writes
    state, or converts stale/malformed/missing evidence into an incompatibility.
    """

    root = Path(repo_root).resolve()
    current_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    reports: dict[str, "CompatibilityReport"] = {}
    diagnostics: dict[str, str] = {}

    from runtime.environment.spec import load_environment_spec

    for raw_key in task_ids:
        task_id = str(raw_key)
        try:
            task = store.get_task(task_id)
            if task is None:
                diagnostics[task_id] = "task_missing"
                continue
            contract = task.get("environment")
            if not isinstance(contract, Mapping):
                diagnostics[task_id] = "no_environment_contract"
                continue
            spec_ref = _safe_spec_ref(contract.get("spec_ref"))
            max_age_seconds = _positive_int(
                contract.get("max_age_seconds"), "max_age_seconds"
            )
            allow_older = bool(contract.get("allow_older_task_revision"))
            spec = load_environment_spec(root / spec_ref)

            evidence = _latest_recorded_evidence(store, task_id)
            if evidence is None:
                diagnostics[task_id] = "no_recorded_report"
                continue
            report = _report(evidence.get("compatibility_snapshot"))
            produced_at = _time(evidence.get("created_at"), "created_at")
            diagnostic = _freshness_diagnostic(
                report,
                spec_sha256=spec.sha256,
                produced_at=produced_at,
                now=current_time,
                max_age_seconds=max_age_seconds,
                recorded_task_revision=evidence.get("task_revision"),
                current_task_revision=store.compute_task_revision(task_id),
                allow_older_task_revision=allow_older,
            )
            if diagnostic == "fresh":
                reports[task_id] = report
            diagnostics[task_id] = diagnostic
        except Exception:
            diagnostics[task_id] = "malformed_evidence"
    return RoutingEnvironmentReportSelection(reports=reports, diagnostics=diagnostics)
