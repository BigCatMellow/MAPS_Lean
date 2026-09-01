from __future__ import annotations

from typing import Any, Mapping, Sequence

from runtime.acquisition_evidence import (
    AcquisitionEvidenceError,
    evaluate_acquisition_evidence,
)
from runtime.benchmark_results import BenchmarkResultError, evaluate_benchmark_results
from runtime.flow_review import _failed, _mutation_payload
from runtime.state import MutationResult, TaskStore


_RELEASE_CHECK_REVIEW = "OPERATOR_VISIBLE_RELEASE_CHECK"


def _open_release_review(reviews: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    for review in reversed(reviews):
        if review.get("completed_at") is None:
            return review
    return None


def flow_release_check(
    store: TaskStore,
    task_id: str,
    *,
    recorded_by: str,
    evidence: Mapping[str, Any] | None = None,
    operator_ack_ref: str | None = None,
) -> dict[str, Any]:
    """Assemble the operator-visible release verdict inputs for a task under an
    ``OPERATOR_VISIBLE_RELEASE_CHECK`` review, then stop before the verdict.

    Composition over three existing primitives, fed by **caller-supplied**
    evidence (nothing here acquires or executes anything):

    1. **verify approved subject** — the open release-check review + its bound
       review subject (mandatory for this review type; see
       ``review_subject_required``). Carries the subject's ``run_id`` forward.
    2. **validate built/acquired artifact identity** — when the caller supplies
       an ``acquisition`` bundle (``{"manifest": …, "observations": [...]}``),
       run ``evaluate_acquisition_evidence`` and take its
       ``release.acquisition_paths_verified`` aggregate (``PASS`` / ``FAIL`` /
       ``UNKNOWN``). Absent bundle → ``NOT_APPLICABLE`` (declared-N/A inside a
       supplied manifest is still ``PASS``/``FAIL`` per that evaluator's rules).
    3. **run release-path smoke** — when the caller supplies a ``benchmark``
       bundle (``{"protocol": …, "results": [...]}``), run
       ``evaluate_benchmark_results`` and take its ``benchmark_status``
       (``COMPLETE`` / ``FAIL`` / ``INCOMPLETE``). Absent bundle →
       ``NOT_APPLICABLE``.
    4. **record operator-visible summary** — persist an append-only
       ``release_checks`` row (``store.record_release_check``) with the two
       aggregates, their report refs, the input evidence refs, and the composite
       state. ``composite == "BLOCKED"`` iff step 2 or step 3 is ``FAIL``; every
       other combination is ``READY_FOR_OPERATOR_VERDICT`` (the operator/reviewer
       weighs any ``UNKNOWN`` / ``INCOMPLETE`` gap). ``BLOCKED`` is **advisory**
       — this flow records no review verdict and does not gate ``record_review``.

    Stop boundary — **before the review verdict.** The caller then runs
    ``maps flow review-record`` with the summary in hand.
    """

    evidence = dict(evidence or {})
    task = store.get_task(task_id)
    if task is None:
        return _failed(
            "preflight",
            MutationResult(False, "NOT_FOUND", f"{task_id} does not exist"),
        )
    if str(task.get("review_required")).upper() != _RELEASE_CHECK_REVIEW:
        return _failed(
            "preflight",
            MutationResult(
                False,
                "RELEASE_CHECK_NOT_APPLICABLE",
                f"{task_id} review_required is {task.get('review_required')!r}, "
                f"not {_RELEASE_CHECK_REVIEW}",
                task,
            ),
        )

    review = _open_release_review(store.list_reviews(task_id))
    if review is None:
        return _failed(
            "preflight",
            MutationResult(
                False,
                "RELEASE_CHECK_NO_OPEN_REVIEW",
                f"{task_id} has no open {_RELEASE_CHECK_REVIEW} review "
                "(run maps flow review-start first)",
            ),
        )
    review_id = int(review["id"])

    subject = store.get_review_subject(review_id)
    requirement = store.review_subject_required(task_id)
    requires_subject = bool((requirement.task or {}).get("required"))
    if requires_subject and subject is None:
        return _failed(
            "subject_preflight",
            MutationResult(
                False,
                "RELEASE_CHECK_NO_BOUND_SUBJECT",
                f"{_RELEASE_CHECK_REVIEW} requires an immutable review subject; "
                "bind one via maps flow review-start before the release check",
            ),
        )
    subject_run_id = subject.get("run_id") if subject else None

    input_evidence_refs: list[str] = []

    # Step 2 — artifact identity
    acquisition = evidence.get("acquisition")
    if acquisition:
        manifest = acquisition.get("manifest")
        observations = acquisition.get("observations", [])
        try:
            acq_report = evaluate_acquisition_evidence(
                manifest, observations, label=f"{task_id}-release"
            )
        except AcquisitionEvidenceError as exc:
            return _failed(
                "artifact_identity",
                MutationResult(False, "INVALID_ACQUISITION_EVIDENCE", str(exc)),
            )
        artifact_identity_state = str(
            acq_report["benchmark_property_fragments"][
                "release.acquisition_paths_verified"
            ]["state"]
        )
        artifact_identity_report_ref = f"acquisition-report:{acq_report['report_id']}"
        input_evidence_refs.append(f"acquisition-manifest:{acq_report['manifest_sha256']}")
    else:
        artifact_identity_state = "NOT_APPLICABLE"
        artifact_identity_report_ref = None

    # Step 3 — release-path smoke
    benchmark = evidence.get("benchmark")
    if benchmark:
        protocol = benchmark.get("protocol")
        results = benchmark.get("results", [])
        try:
            smoke_report = evaluate_benchmark_results(
                protocol, results, label=f"{task_id}-release-smoke"
            )
        except BenchmarkResultError as exc:
            return _failed(
                "release_smoke",
                MutationResult(False, "INVALID_BENCHMARK_EVIDENCE", str(exc)),
            )
        release_smoke_state = str(smoke_report["benchmark_status"])
        release_smoke_report_ref = str(smoke_report["result_evidence_ref"])
        input_evidence_refs.append(release_smoke_report_ref)
    else:
        release_smoke_state = "NOT_APPLICABLE"
        release_smoke_report_ref = None

    composite_state = (
        "BLOCKED"
        if artifact_identity_state == "FAIL" or release_smoke_state == "FAIL"
        else "READY_FOR_OPERATOR_VERDICT"
    )

    summary: dict[str, Any] = {
        "release_check_version": 1,
        "task_id": task_id,
        "review_id": review_id,
        "subject_run_id": subject_run_id,
        "artifact_identity": {
            "state": artifact_identity_state,
            "report_ref": artifact_identity_report_ref,
        },
        "release_smoke": {
            "state": release_smoke_state,
            "report_ref": release_smoke_report_ref,
        },
        "composite": composite_state,
    }

    recorded = store.record_release_check(
        task_id,
        review_id,
        artifact_identity_state=artifact_identity_state,
        release_smoke_state=release_smoke_state,
        composite_state=composite_state,
        summary=summary,
        recorded_by=recorded_by,
        subject_run_id=subject_run_id,
        artifact_identity_report_ref=artifact_identity_report_ref,
        release_smoke_report_ref=release_smoke_report_ref,
        input_evidence_refs=input_evidence_refs,
        operator_ack_ref=operator_ack_ref,
    )
    if not recorded.ok:
        return _failed("record", recorded)

    stored = recorded.task or {}
    summary["recorded_at"] = stored.get("created_at")

    return {
        "ok": True,
        "code": "FLOW_RELEASE_CHECK_ASSEMBLED",
        "task_id": task_id,
        "review_id": review_id,
        "release_check_id": stored.get("id"),
        "summary": summary,
        "record": _mutation_payload(recorded),
        "next_step": {
            "state": "STOPPED_BEFORE_RELEASE_VERDICT",
            "reason": (
                "flow release-check assembles the artifact-identity + "
                "release-smoke evidence for the operator-visible review and "
                "records no verdict; the releasing party / reviewer / operator "
                "runs maps flow review-record with this summary in hand. "
                f"composite={composite_state} (BLOCKED is advisory this slice — "
                "it does not gate record_review)"
            ),
        },
    }
