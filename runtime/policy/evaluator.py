from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from .models import PolicyDecision, WorkerProfile

if TYPE_CHECKING:
    from ..environment.fingerprint import CompatibilityReport

MUTATING_TASK_TYPES = {"IMPLEMENTATION", "MAINTENANCE", "REPAIR", "ARCHITECTURE"}
HIGH_AUTHORITY_TYPES = {"ARCHITECTURE", "PLANNING"}


def _policy(task: Mapping[str, Any]) -> Mapping[str, Any]:
    value = task.get("policy", {})
    return value if isinstance(value, Mapping) else {}


def _approved(task: Mapping[str, Any]) -> bool:
    policy = _policy(task)
    return bool(policy.get("approved_by") and policy.get("approved_at"))


def task_needs_human_reauthorization(
    task: Mapping[str, Any],
) -> tuple[bool, tuple[str, ...]]:
    """Return whether this task explicitly crosses its inherited authority.

    Consequential-policy flags describe risk/review needs; they do not by
    themselves create another human approval gate. The task shaper sets
    ``requires_operator_approval`` only when the resolved action is outside the
    already-approved roadmap/task permission envelope.
    """
    policy = _policy(task)
    if bool(policy.get("requires_operator_approval")):
        return True, ("human_reauthorization_required",)
    return False, ()


def task_needs_operator_approval(
    task: Mapping[str, Any],
) -> tuple[bool, tuple[str, ...]]:
    """Backward-compatible alias for the old policy API name."""
    return task_needs_human_reauthorization(task)


def evaluate_assignment(
    task: Mapping[str, Any],
    worker: WorkerProfile,
    *,
    environment_report: CompatibilityReport | None = None,
) -> PolicyDecision:
    """Evaluate whether ``worker`` may be assigned ``task``.

    ``environment_report``, when supplied, is the environment-availability
    dimension of the least-privilege intersection. Approval is inherited from
    the approved roadmap/task envelope; a fresh human gate exists only when the
    task explicitly marks a boundary crossing.
    """
    reasons: list[str] = []
    if not worker.available:
        return PolicyDecision("reject", ("worker_unavailable",))

    if environment_report is not None:
        from ..environment.fingerprint import CompatibilityState

        if environment_report.state == CompatibilityState.INCOMPATIBLE:
            reasons.append("environment_incompatible")

    status = str(task.get("status", "")).upper()
    if status not in {"READY", "CHANGES_REQUESTED"}:
        reasons.append(f"task_not_executable:{status or 'UNKNOWN'}")
    if str(task.get("agi_status", "")).upper() != "AGI READY":
        reasons.append("agi_not_ready")

    task_type = str(task.get("task_type", "")).upper()
    risk = str(task.get("risk", "")).upper()
    if not worker.supports_task_type(task_type):
        reasons.append("unsupported_task_type")
    if not worker.supports_risk(risk):
        reasons.append("risk_exceeds_worker_profile")
    if task.get("output_paths") and task_type in MUTATING_TASK_TYPES and not worker.can_mutate:
        reasons.append("worker_read_only")

    if worker.worker_class in {"helper", "mechanical"}:
        if risk == "HIGH":
            reasons.append("narrow_worker_high_risk")
        if task_type in HIGH_AUTHORITY_TYPES:
            reasons.append("narrow_worker_authority_task")

    needs_reauthorization, reauthorization_reasons = task_needs_human_reauthorization(task)
    if needs_reauthorization and not _approved(task):
        return PolicyDecision("require_approval", reauthorization_reasons)
    if reasons:
        return PolicyDecision("reject", tuple(reasons))
    return PolicyDecision("allow", ())


def evaluate_review(task: Mapping[str, Any], worker: WorkerProfile) -> PolicyDecision:
    if not worker.available:
        return PolicyDecision("reject", ("worker_unavailable",))
    if not worker.can_review:
        return PolicyDecision("reject", ("worker_cannot_review",))
    if not worker.supports_risk(str(task.get("risk", ""))):
        return PolicyDecision("reject", ("risk_exceeds_worker_profile",))

    disqualified = task.get("review_disqualified_ids", [])
    if isinstance(disqualified, (list, tuple, set)) and worker.worker_id in disqualified:
        return PolicyDecision("reject", ("continuity_review_forbidden",))

    submission = task.get("submission", {})
    author = submission.get("author_id") if isinstance(submission, Mapping) else None
    if author and worker.worker_id == author:
        return PolicyDecision("reject", ("self_review",))
    if worker.worker_class == "mechanical" and str(task.get("risk", "")).upper() != "LOW":
        return PolicyDecision("reject", ("mechanical_reviewer_insufficient",))
    return PolicyDecision("allow", ())
