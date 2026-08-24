from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping, Sequence

from runtime.state import MutationResult, TaskStore


def _mutation_payload(result: MutationResult) -> dict[str, Any]:
    return asdict(result)


def _failed(step: str, result: MutationResult | Mapping[str, Any]) -> dict[str, Any]:
    payload = _mutation_payload(result) if isinstance(result, MutationResult) else dict(result)
    return {
        "ok": False,
        "code": "FLOW_STEP_FAILED",
        "failed_step": step,
        "step_result": payload,
    }


def _subject_requested(
    freshness_mode: str | None,
    run_id: str | None,
    artifact_refs: Sequence[str],
) -> bool:
    return bool(
        (freshness_mode is not None and freshness_mode.strip())
        or (run_id is not None and run_id.strip())
        or artifact_refs
    )


def _open_review_for(
    reviews: Sequence[Mapping[str, Any]],
    reviewer_id: str,
) -> Mapping[str, Any] | None:
    for review in reversed(reviews):
        if review.get("completed_at") is None and review.get("reviewer_id") == reviewer_id:
            return review
    return None


def flow_review_start(
    store: TaskStore,
    task_id: str,
    *,
    reviewer_id: str,
    freshness_mode: str | None = None,
    run_id: str | None = None,
    artifact_refs: Sequence[str] = (),
) -> dict[str, Any]:
    """Start deterministic review work without recording a verdict.

    The flow composes existing guarded operations in order:

    1. preflight whether consequential work needs immutable subject evidence;
    2. claim the review for an explicit reviewer;
    3. optionally bind the exact review subject;
    4. stop before verdict/approval.

    It intentionally does not choose a reviewer, write evidence, approve work,
    or record `CHANGES_REQUESTED` / `BLOCKED`.
    """

    requirement = store.review_subject_required(task_id)
    if not requirement.ok:
        return _failed("preflight", requirement)

    requested_subject = _subject_requested(freshness_mode, run_id, artifact_refs)
    requires_subject = bool((requirement.task or {}).get("required"))
    if requires_subject and not requested_subject:
        return _failed(
            "review_subject_preflight",
            MutationResult(
                False,
                "REVIEW_SUBJECT_REQUIRED",
                "consequential review-start requires run_id, artifact refs, or freshness mode",
                requirement.task,
            ),
        )

    if requested_subject:
        claim = store.claim_review_with_subject(
            task_id,
            reviewer_id,
            freshness_mode=freshness_mode or "REVISION_BOUND",
            run_id=run_id,
            artifact_refs=artifact_refs,
        )
        if not claim.ok:
            return _failed("claim_with_subject", claim)
        payload = claim.task or {}
        review = payload.get("review")
        subject = payload.get("review_subject")
        if not isinstance(review, Mapping) or not isinstance(subject, Mapping):
            return _failed(
                "review_lookup",
                MutationResult(
                    False,
                    "OPEN_REVIEW_NOT_FOUND",
                    "atomic review claim succeeded but review subject did not resolve",
                    claim.task,
                ),
            )
    else:
        claim = store.claim_review(task_id, reviewer_id)
        if not claim.ok:
            return _failed("claim", claim)

        review = _open_review_for(store.list_reviews(task_id), reviewer_id)
        if review is None:
            return _failed(
                "review_lookup",
                MutationResult(
                    False,
                    "OPEN_REVIEW_NOT_FOUND",
                    "review claim succeeded but no open review resolved",
                    claim.task,
                ),
            )
        subject = None

    return {
        "ok": True,
        "code": "FLOW_REVIEW_STARTED",
        "task_id": task_id,
        "reviewer_id": reviewer_id,
        "review": dict(review),
        "review_subject_required": requires_subject,
        "review_subject": subject,
        "claim": _mutation_payload(claim),
        "next_step": {
            "state": "STOPPED_BEFORE_REVIEW_VERDICT",
            "reason": (
                "flow review-start does not record review evidence, verdicts, "
                "approval, changes requested, or blocked outcomes"
            ),
        },
    }
