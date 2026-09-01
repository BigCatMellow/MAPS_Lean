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


def _review_by_id(
    reviews: Sequence[Mapping[str, Any]],
    review_id: int,
) -> Mapping[str, Any] | None:
    for review in reviews:
        if int(review["id"]) == review_id:
            return review
    return None


def flow_review_record(
    store: TaskStore,
    task_id: str,
    *,
    reviewer_id: str,
    verdict: str,
    summary: str,
    rederived_artifact_refs: Sequence[str] = (),
) -> dict[str, Any]:
    """Record a review verdict as a pure composition over ``record_review``.

    The flow adds exactly one missing piece to the plain store passthrough:
    freshness-mode-aware re-derived artifact refs. It:

    1. preflights the open review for ``(task_id, reviewer_id)``;
    2. if the verdict is ``APPROVED``, that review's subject is bound
       ``REDERIVED_AT_REVIEW``, and no re-derived refs were supplied, fails
       early and deterministically (mirroring the deep review-binding hook,
       which itself only runs on ``APPROVED``) instead of surfacing a raw
       hook error;
    3. calls ``store.record_review(..., rederived_artifact_refs=...)`` — all
       real enforcement (ownership, reviewability, independence, criterion
       verification, review-binding approval, verdict -> status) stays in the
       store primitive;
    4. stops. No outcome recording, no next-task dispatch, no session action.
    """

    reviews = store.list_reviews(task_id)
    review = _open_review_for(reviews, reviewer_id)
    if review is None:
        # A review claimed by a different identity still resolves here so that
        # ownership is rejected by record_review itself (NOT_REVIEW_OWNER),
        # keeping every real authority check in the store primitive.
        review = next(
            (r for r in reversed(reviews) if r.get("completed_at") is None), None
        )
        if review is None:
            return _failed(
                "preflight",
                MutationResult(
                    False,
                    "NO_OPEN_REVIEW",
                    f"no open review exists for {task_id}",
                ),
            )

    # Mirror the review-binding hook, which only requires re-derived refs on an
    # APPROVED verdict (CHANGES_REQUESTED / BLOCKED never reach that check).
    subject = store.get_review_subject(int(review["id"]))
    if (
        verdict.strip().upper() == "APPROVED"
        and subject is not None
        and subject.get("freshness_mode") == "REDERIVED_AT_REVIEW"
        and not rederived_artifact_refs
    ):
        return _failed(
            "rederivation_preflight",
            MutationResult(
                False,
                "REVIEW_REDERIVATION_REQUIRED",
                "approval of a REDERIVED_AT_REVIEW review requires rederived "
                "immutable artifact/evidence refs",
                dict(subject),
            ),
        )

    recorded = store.record_review(
        task_id,
        reviewer_id,
        verdict,
        summary,
        rederived_artifact_refs=tuple(rederived_artifact_refs) or None,
    )
    if not recorded.ok:
        return _failed("record", recorded)

    closed = _review_by_id(store.list_reviews(task_id), int(review["id"]))
    return {
        "ok": True,
        "code": "FLOW_REVIEW_RECORDED",
        "task_id": task_id,
        "reviewer_id": reviewer_id,
        "verdict": verdict.strip().upper(),
        "new_status": (recorded.task or {}).get("status"),
        "review": dict(closed) if closed is not None else None,
        "record": _mutation_payload(recorded),
    }
