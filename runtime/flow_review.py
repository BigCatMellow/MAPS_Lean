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


def _latest_completed_review_for(
    reviews: Sequence[Mapping[str, Any]],
    reviewer_id: str,
) -> Mapping[str, Any] | None:
    """The reviewer's most recently completed review on the task (mirrors
    `_open_review_for`'s newest-first scan). After a successful `record_review`
    this is the review that was just closed — resolved without re-indexing on
    the pre-call open-review lookup, which may be `None` on the non-owner path.
    """
    for review in reversed(reviews):
        if (
            review.get("completed_at") is not None
            and review.get("reviewer_id") == reviewer_id
        ):
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

    1. resolves the caller's own open review (if any);
    2. only when the caller holds that review: if the verdict is ``APPROVED``,
       its subject is bound ``REDERIVED_AT_REVIEW``, and no re-derived refs
       were supplied, fails early and deterministically (mirroring the deep
       review-binding hook, which itself only runs on ``APPROVED``) instead of
       surfacing a raw hook error. A caller who does not hold the open review
       never sees this branch — the subject binding is not exposed to a
       non-owner;
    3. calls ``store.record_review(..., rederived_artifact_refs=...)`` — all
       real enforcement (ownership incl. ``NO_OPEN_REVIEW`` /
       ``NOT_REVIEW_OWNER``, reviewability, independence, criterion
       verification, review-binding approval, verdict -> status) stays in the
       store primitive;
    4. stops, returning a ``next_step`` block in the same ``{state, reason}``
       shape as ``flow_start`` / ``flow_review_start``: no real-world outcome
       recording, no next-task dispatch, no session action.
    """

    # Resolve only the caller's *own* open review. If they do not hold one,
    # the rederivation preflight is skipped entirely (it must never expose a
    # subject binding to a non-owner) and record_review is left to reject the
    # call: NO_OPEN_REVIEW when nothing is open, NOT_REVIEW_OWNER when another
    # identity holds it.
    review = _open_review_for(store.list_reviews(task_id), reviewer_id)
    if review is not None:
        # Mirror the review-binding hook, which only requires re-derived refs
        # on an APPROVED verdict (CHANGES_REQUESTED / BLOCKED never reach it).
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

    new_status = (recorded.task or {}).get("status")
    closed = _latest_completed_review_for(store.list_reviews(task_id), reviewer_id)
    return {
        "ok": True,
        "code": "FLOW_REVIEW_RECORDED",
        "task_id": task_id,
        "reviewer_id": reviewer_id,
        "verdict": verdict.strip().upper(),
        "new_status": new_status,
        "review": dict(closed) if closed is not None else None,
        "record": _mutation_payload(recorded),
        "next_step": {
            "state": "REVIEW_RECORDED",
            "reason": (
                f"the task is now {new_status}; flow review-record does not "
                "record real-world outcomes (maps outcome-record) or dispatch "
                "follow-on work"
            ),
        },
    }
