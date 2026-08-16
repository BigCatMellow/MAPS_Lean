from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence

from runtime.policy.evaluator import task_needs_operator_approval


class WaitProjectionSource(Protocol):
    def get_task(self, task_id: str) -> dict[str, Any] | None: ...

    def list_reviews(self, task_id: str) -> list[dict[str, Any]]: ...


_DEPENDENCY_GATED_STATUSES = {
    "NEEDS_SHAPING",
    "READY",
    "ACTIVE",
    "CHANGES_REQUESTED",
    "BLOCKED",
}
_APPROVAL_GATED_STATUSES = {"READY", "CHANGES_REQUESTED"}


def _reason(
    code: str,
    classification: str,
    *,
    source_refs: Sequence[str] = (),
    details: Mapping[str, object] | None = None,
) -> dict[str, object]:
    return {
        "code": code,
        "classification": classification,
        "source_refs": sorted(dict.fromkeys(str(ref) for ref in source_refs)),
        "details": dict(details or {}),
    }


def _review_wait_reasons(
    source: WaitProjectionSource,
    task: Mapping[str, Any],
) -> tuple[list[dict[str, object]], str]:
    if str(task.get("status", "")).upper() != "READY_FOR_REVIEW":
        return [], "NOT_APPLICABLE"

    task_id = str(task.get("task_id", ""))
    submission = task.get("submission")
    if not isinstance(submission, Mapping):
        return [
            _reason(
                "REVIEW_GATE_EVIDENCE_INCOMPLETE",
                "UNKNOWN",
                source_refs=(f"task:{task_id}",),
                details={"missing": "submission"},
            )
        ], "UNKNOWN"

    reviews = source.list_reviews(task_id)
    if not isinstance(reviews, list) or any(not isinstance(item, Mapping) for item in reviews):
        return [
            _reason(
                "REVIEW_GATE_EVIDENCE_INCOMPLETE",
                "UNKNOWN",
                source_refs=(f"task:{task_id}",),
                details={"missing": "valid_review_rows"},
            )
        ], "UNKNOWN"

    open_reviews = [item for item in reviews if item.get("completed_at") is None]
    if not open_reviews:
        return [
            _reason(
                "WAIT_REVIEW_UNCLAIMED",
                "VERIFIED_WAIT",
                source_refs=(
                    f"task:{task_id}",
                    f"submission:{task_id}:{submission.get('submission_count', 'UNKNOWN')}",
                ),
                details={
                    "submission_count": submission.get("submission_count"),
                    "open_review_count": 0,
                },
            )
        ], "VERIFIED"

    if len(open_reviews) != 1:
        return [
            _reason(
                "REVIEW_GATE_AMBIGUOUS",
                "UNKNOWN",
                source_refs=(f"task:{task_id}",),
                details={"open_review_count": len(open_reviews)},
            )
        ], "UNKNOWN"

    review = open_reviews[0]
    reviewer_id = review.get("reviewer_id")
    review_id = review.get("id")
    if not isinstance(reviewer_id, str) or not reviewer_id.strip() or review_id is None:
        return [
            _reason(
                "REVIEW_GATE_EVIDENCE_INCOMPLETE",
                "UNKNOWN",
                source_refs=(f"task:{task_id}",),
                details={"missing": "review_identity"},
            )
        ], "UNKNOWN"

    return [
        _reason(
            "WAIT_REVIEW_IN_PROGRESS",
            "VERIFIED_WAIT",
            source_refs=(f"task:{task_id}", f"review:{review_id}"),
            details={
                "review_id": review_id,
                "reviewer_id": reviewer_id.strip(),
                "created_at": review.get("created_at"),
            },
        )
    ], "VERIFIED"


def _dependency_wait_reasons(
    source: WaitProjectionSource,
    task: Mapping[str, Any],
) -> tuple[list[dict[str, object]], str]:
    status = str(task.get("status", "")).upper()
    if status not in _DEPENDENCY_GATED_STATUSES:
        return [], "NOT_APPLICABLE"

    task_id = str(task.get("task_id", ""))
    dependencies = task.get("dependencies", [])
    if not isinstance(dependencies, Sequence) or isinstance(dependencies, (str, bytes)):
        return [
            _reason(
                "DEPENDENCY_EVIDENCE_INCOMPLETE",
                "UNKNOWN",
                source_refs=(f"task:{task_id}",),
                details={"missing": "dependency_list"},
            )
        ], "UNKNOWN"

    reasons: list[dict[str, object]] = []
    for raw_dependency in dependencies:
        if not isinstance(raw_dependency, str) or not raw_dependency.strip():
            return [
                _reason(
                    "DEPENDENCY_EVIDENCE_INCOMPLETE",
                    "UNKNOWN",
                    source_refs=(f"task:{task_id}",),
                    details={"invalid_dependency_id": raw_dependency},
                )
            ], "UNKNOWN"
        dependency_id = raw_dependency.strip()
        dependency = source.get_task(dependency_id)
        if dependency is None:
            reasons.append(
                _reason(
                    "WAIT_DEPENDENCY",
                    "VERIFIED_WAIT",
                    source_refs=(f"task:{task_id}", f"task:{dependency_id}"),
                    details={
                        "dependency_id": dependency_id,
                        "dependency_status": "MISSING",
                    },
                )
            )
            continue
        dependency_status = str(dependency.get("status", "")).upper() or "UNKNOWN"
        if dependency_status != "DONE":
            reasons.append(
                _reason(
                    "WAIT_DEPENDENCY",
                    "VERIFIED_WAIT",
                    source_refs=(f"task:{task_id}", f"task:{dependency_id}"),
                    details={
                        "dependency_id": dependency_id,
                        "dependency_status": dependency_status,
                    },
                )
            )
    return reasons, "VERIFIED"


def _approval_wait_reasons(
    task: Mapping[str, Any],
) -> tuple[list[dict[str, object]], str]:
    status = str(task.get("status", "")).upper()
    if status not in _APPROVAL_GATED_STATUSES:
        return [], "NOT_APPLICABLE"
    task_id = str(task.get("task_id", ""))
    if str(task.get("agi_status", "")).upper() != "AGI READY":
        return [], "VERIFIED"

    policy = task.get("policy")
    if not isinstance(policy, Mapping):
        return [
            _reason(
                "OPERATOR_APPROVAL_EVIDENCE_INCOMPLETE",
                "UNKNOWN",
                source_refs=(f"task:{task_id}",),
                details={"missing": "policy"},
            )
        ], "UNKNOWN"

    needs_approval, trigger_reasons = task_needs_operator_approval(task)
    if not needs_approval:
        return [], "VERIFIED"

    approved_by = policy.get("approved_by")
    approved_at = policy.get("approved_at")
    has_by = isinstance(approved_by, str) and bool(approved_by.strip())
    has_at = isinstance(approved_at, str) and bool(approved_at.strip())
    if has_by != has_at:
        return [
            _reason(
                "OPERATOR_APPROVAL_EVIDENCE_INCOMPLETE",
                "UNKNOWN",
                source_refs=(f"task:{task_id}", f"policy:{task_id}"),
                details={"inconsistent_approval_identity": True},
            )
        ], "UNKNOWN"
    if has_by and has_at:
        return [], "VERIFIED"

    return [
        _reason(
            "WAIT_OPERATOR_APPROVAL",
            "VERIFIED_WAIT",
            source_refs=(f"task:{task_id}", f"policy:{task_id}"),
            details={"approval_triggers": list(trigger_reasons)},
        )
    ], "VERIFIED"


def _sort_reasons(reasons: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    return sorted(
        (dict(reason) for reason in reasons),
        key=lambda item: (
            str(item.get("code", "")),
            str(item.get("classification", "")),
            repr(item.get("details", {})),
        ),
    )


def project_task_waits(
    source: WaitProjectionSource,
    task_id: str,
) -> dict[str, object] | None:
    """Derive current wait/block explanations without mutating canonical state."""

    resolved_task_id = task_id.strip() if isinstance(task_id, str) else ""
    if not resolved_task_id:
        return None
    task = source.get_task(resolved_task_id)
    if task is None:
        return None

    status = str(task.get("status", "")).upper() or "UNKNOWN"
    if status == "DONE":
        return {
            "task_id": resolved_task_id,
            "lifecycle_status": status,
            "summary_state": "NO_VERIFIED_WAIT",
            "reasons": [],
            "coverage": {
                "task_state": "VERIFIED",
                "dependencies": "NOT_APPLICABLE",
                "review": "NOT_APPLICABLE",
                "operator_approval": "NOT_APPLICABLE",
                "communication": "UNKNOWN",
                "recovery": "UNKNOWN",
                "helpers": "UNKNOWN",
            },
            "authority": "DERIVED_READ_ONLY",
            "runnable_claimed": False,
        }

    dependency_reasons, dependency_coverage = _dependency_wait_reasons(source, task)
    review_reasons, review_coverage = _review_wait_reasons(source, task)
    approval_reasons, approval_coverage = _approval_wait_reasons(task)
    reasons = dependency_reasons + review_reasons + approval_reasons

    verified_waits = [
        reason
        for reason in reasons
        if reason.get("classification") == "VERIFIED_WAIT"
    ]
    unknown_reasons = [
        reason for reason in reasons if reason.get("classification") == "UNKNOWN"
    ]

    if status == "BLOCKED":
        if not verified_waits:
            reasons.append(
                _reason(
                    "BLOCKED_CAUSE_UNPROVEN",
                    "UNKNOWN",
                    source_refs=(f"task:{resolved_task_id}",),
                    details={"lifecycle_status": "BLOCKED"},
                )
            )
        summary = "BLOCKED" if verified_waits else "UNKNOWN"
    elif verified_waits:
        summary = "WAITING"
    elif unknown_reasons:
        summary = "UNKNOWN"
    else:
        summary = "NO_VERIFIED_WAIT"

    return {
        "task_id": resolved_task_id,
        "lifecycle_status": status,
        "summary_state": summary,
        "reasons": _sort_reasons(reasons),
        "coverage": {
            "task_state": "VERIFIED",
            "dependencies": dependency_coverage,
            "review": review_coverage,
            "operator_approval": approval_coverage,
            "communication": "UNKNOWN",
            "recovery": "UNKNOWN",
            "helpers": "UNKNOWN",
        },
        "authority": "DERIVED_READ_ONLY",
        "runnable_claimed": False,
    }
