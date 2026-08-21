from __future__ import annotations

from enum import Enum
import hashlib
import json
from typing import Any, Mapping, Protocol


class CoverageState(str, Enum):
    VERIFIED = "VERIFIED"
    SOURCE_LOCAL = "SOURCE_LOCAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class RunRecordError(ValueError):
    pass


class TraceSource(Protocol):
    def trace_task(self, task_id: str) -> dict[str, Any] | None: ...


_FREE_TEXT_REASON = (
    "free text is omitted from portable Run Record v1 by default; "
    "use canonical source evidence or a separately reviewed sanitized fixture"
)


def _text_stub(value: object, *, reason: str = _FREE_TEXT_REASON) -> dict[str, object]:
    text = value if isinstance(value, str) else ""
    return {
        "included": False,
        "present": bool(text),
        "characters": len(text),
        "reason": reason,
    }


def _canonical_hash(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _count_list(mapping: Mapping[str, Any], key: str) -> int:
    value = mapping.get(key)
    return len(value) if isinstance(value, list) else 0


def _task_projection(trace: Mapping[str, Any]) -> dict[str, object]:
    task = trace.get("task")
    if not isinstance(task, Mapping):
        raise RunRecordError("trace is missing canonical task projection")
    policy = trace.get("policy")
    policy_map = policy if isinstance(policy, Mapping) else {}

    return {
        "task_id": trace.get("task_id"),
        "project_id": task.get("project_id"),
        "task_revision": trace.get("task_revision"),
        "task_type": task.get("task_type"),
        "risk": task.get("risk"),
        "status": task.get("status"),
        "agi_status": task.get("agi_status"),
        "owner": task.get("owner"),
        "attempt": task.get("attempt"),
        "max_attempts": task.get("max_attempts"),
        "review_required": task.get("review_required"),
        "text": {
            "title": _text_stub(task.get("title")),
            "outcome": _text_stub(task.get("outcome")),
            "decision_authority": _text_stub(task.get("decision_authority")),
            "verification": _text_stub(task.get("verification")),
            "evidence_expected": _text_stub(task.get("evidence_expected")),
            "escalation": _text_stub(task.get("escalation")),
        },
        "contract_counts": {
            "inputs": _count_list(task, "inputs"),
            "sources": _count_list(task, "sources"),
            "dependencies": _count_list(task, "dependencies"),
            "output_paths": _count_list(task, "output_paths"),
            "non_goals": _count_list(task, "non_goals"),
            "acceptance_criteria": _count_list(task, "acceptance_criteria"),
            "stop_conditions": _count_list(task, "stop_conditions"),
        },
        "policy": {
            "requires_operator_approval": bool(policy_map.get("requires_operator_approval", False)),
            "destructive_action": bool(policy_map.get("destructive_action", False)),
            "external_side_effect": bool(policy_map.get("external_side_effect", False)),
            "security_sensitive": bool(policy_map.get("security_sensitive", False)),
            "broad_architecture": bool(policy_map.get("broad_architecture", False)),
            "paid_execution": bool(policy_map.get("paid_execution", True)),
            "approved_by_present": bool(policy_map.get("approved_by")),
            "approved_at": policy_map.get("approved_at"),
        },
    }


def _submission_projection(trace: Mapping[str, Any]) -> dict[str, object] | None:
    submission = trace.get("submission")
    if not isinstance(submission, Mapping):
        return None
    evidence = submission.get("evidence")
    evidence_meta = evidence if isinstance(evidence, Mapping) else _text_stub("")
    return {
        "author_id": submission.get("author_id"),
        "submission_count": submission.get("submission_count"),
        "first_submitted_at": submission.get("first_submitted_at"),
        "submitted_at": submission.get("submitted_at"),
        "evidence": dict(evidence_meta),
    }


def _review_projection(review: Mapping[str, Any]) -> dict[str, object]:
    result: dict[str, object] = {
        "id": review.get("id"),
        "reviewer_id": review.get("reviewer_id"),
        "verdict": review.get("verdict"),
        "created_at": review.get("created_at"),
        "completed_at": review.get("completed_at"),
        "summary": _text_stub(review.get("summary")),
    }
    if "subject" in review:
        result["subject"] = review.get("subject")
    return result


def _criterion_claim_projection(claim: Mapping[str, Any]) -> dict[str, object]:
    return {
        "id": claim.get("id"),
        "task_id": claim.get("task_id"),
        "submission_count": claim.get("submission_count"),
        "criterion_id": claim.get("criterion_id"),
        "claimed_status": claim.get("claimed_status"),
        "evidence_refs": claim.get("evidence_refs", []),
        "task_revision": claim.get("task_revision"),
        "run_id": claim.get("run_id"),
        "author_id": claim.get("author_id"),
        "created_at": claim.get("created_at"),
    }


def _criterion_verdict_projection(verdict: Mapping[str, Any]) -> dict[str, object]:
    return {
        "id": verdict.get("id"),
        "claim_id": verdict.get("claim_id"),
        "verified_status": verdict.get("verified_status"),
        "reviewer_id": verdict.get("reviewer_id"),
        "created_at": verdict.get("created_at"),
        "notes": _text_stub(verdict.get("notes")),
    }


def _outcome_projection(outcome: Mapping[str, Any]) -> dict[str, object]:
    return {
        "id": outcome.get("id"),
        "run_id": outcome.get("run_id"),
        "outcome_status": outcome.get("outcome_status"),
        "failure_class": outcome.get("failure_class"),
        "incident_class": outcome.get("incident_class", "UNKNOWN"),
        "escaped_defect": bool(outcome.get("escaped_defect", False)),
        "rework_count": outcome.get("rework_count"),
        "operator_intervention_count": outcome.get("operator_intervention_count"),
        "actor_id": outcome.get("actor_id"),
        "actor_class": outcome.get("actor_class"),
        "task_revision": outcome.get("task_revision"),
        "supersedes_outcome_id": outcome.get("supersedes_outcome_id"),
        "created_at": outcome.get("created_at"),
        "source": _text_stub(outcome.get("source")),
        "notes": _text_stub(outcome.get("notes")),
    }


def _event_projection(event: Mapping[str, Any]) -> dict[str, object]:
    return {
        "id": event.get("id"),
        "event_type": event.get("event_type"),
        "actor": event.get("actor"),
        "created_at": event.get("created_at"),
        "summary": _text_stub(event.get("summary")),
    }


def _review_subject_binds_run(review: Mapping[str, Any], run_id: str) -> bool:
    subject = review.get("subject")
    return isinstance(subject, Mapping) and subject.get("run_id") == run_id


def _coverage(
    trace: Mapping[str, Any],
    *,
    run_id: str,
    environment_source_available: bool,
    environment_evidence_present: bool,
    harness_config_hash_available: bool,
    reviews: list[dict[str, object]],
) -> dict[str, object]:
    canonical = trace.get("coverage")
    canonical_map = canonical if isinstance(canonical, Mapping) else {}
    db_coverage = canonical_map.get("canonical_task_db")
    db_map = db_coverage if isinstance(db_coverage, Mapping) else {}

    review_subjects_observed = bool(db_map.get("review_subjects_included")) or any(
        "subject" in review for review in reviews
    )
    review_subject_bound = any(
        _review_subject_binds_run(review, run_id) for review in reviews
    )
    if review_subject_bound:
        review_subject_state = CoverageState.VERIFIED.value
        review_subject_reason = "an immutable review subject explicitly binds the selected run"
    elif review_subjects_observed:
        review_subject_state = CoverageState.UNKNOWN.value
        review_subject_reason = (
            "review subjects are exposed by the source trace, but none proves a binding to the selected run"
        )
    else:
        review_subject_state = CoverageState.MISSING.value
        review_subject_reason = "current accepted trace does not expose immutable review-subject bindings"

    if environment_evidence_present:
        environment_state = CoverageState.VERIFIED.value
        environment_reason = "one or more exact-run environment evidence observations are included"
    elif environment_source_available:
        environment_state = CoverageState.MISSING.value
        environment_reason = (
            "the source trace exposes run environment evidence, but the selected run has no recorded observations"
        )
    else:
        environment_state = CoverageState.MISSING.value
        environment_reason = "current accepted trace does not expose run environment evidence"

    if harness_config_hash_available:
        harness_configuration_state = CoverageState.VERIFIED.value
        harness_configuration_included = True
        harness_configuration_reason = (
            "an exact-run harness/hook configuration identity is included"
        )
    else:
        harness_configuration_state = CoverageState.MISSING.value
        harness_configuration_included = False
        harness_configuration_reason = (
            "current run manifest does not bind harness/hook configuration identity"
        )

    return {
        "canonical_task_db": {
            "state": CoverageState.VERIFIED.value,
            "included": True,
            "sources": ["SQLite task state"],
        },
        "context_refs": {
            "state": CoverageState.VERIFIED.value,
            "included": True,
            "reason": "immutable run context path/hash references are included",
        },
        "communication": {
            "state": CoverageState.UNKNOWN.value,
            "included": False,
            "sources": ["hcom"],
            "reason": "current canonical trace cannot safely join hcom communication to this run",
        },
        "session_helper_recovery_lineage": {
            "state": CoverageState.UNKNOWN.value,
            "included": False,
            "sources": ["hcom", "helper subsystem", "recovery state"],
            "reason": "durable cross-source lineage is not yet complete",
        },
        "harness_operation_trajectory": {
            "state": CoverageState.MISSING.value,
            "included": False,
            "reason": "Run Record v1 has no canonical operation/result trajectory source",
        },
        "skills": {
            "state": CoverageState.MISSING.value,
            "included": False,
            "reason": "current run manifest does not bind selected Skill identities/hashes",
        },
        "harness_configuration": {
            "state": harness_configuration_state,
            "included": harness_configuration_included,
            "reason": harness_configuration_reason,
        },
        "environment": {
            "state": environment_state,
            "source_available": environment_source_available,
            "included": environment_evidence_present,
            "reason": environment_reason,
        },
        "review_subject": {
            "state": review_subject_state,
            "included": review_subjects_observed,
            "reason": review_subject_reason,
        },
    }


def build_run_record(
    source: TraceSource,
    task_id: str,
    run_id: str,
) -> dict[str, object]:
    """Build one sanitized, deterministic portable record for an exact run.

    The record is a read model over `trace_task()`. It never writes canonical
    state and explicitly reports sources that cannot currently be joined.
    """

    task_id = task_id.strip()
    run_id = run_id.strip()
    if not task_id or not run_id:
        raise RunRecordError("task_id and run_id are required")

    trace = source.trace_task(task_id)
    if trace is None:
        raise RunRecordError(f"task not found: {task_id}")
    runs = trace.get("runs")
    if not isinstance(runs, list):
        raise RunRecordError("trace is missing run list")
    matches = [run for run in runs if isinstance(run, Mapping) and run.get("run_id") == run_id]
    if not matches:
        raise RunRecordError(f"run {run_id} is not bound to task {task_id}")
    if len(matches) != 1:
        raise RunRecordError(f"run identity is ambiguous in trace: {run_id}")
    run = dict(matches[0])

    context_refs = run.pop("context_refs", [])
    environment_source_available = "environment_evidence" in run
    environment = run.pop("environment_evidence", None)
    if not isinstance(context_refs, list):
        raise RunRecordError("run context_refs must be a list")
    if environment_source_available and not isinstance(environment, list):
        raise RunRecordError("run environment_evidence must be a list when exposed")
    environment_list = environment if isinstance(environment, list) else []
    environment_evidence_present = bool(environment_list)
    harness_config_hash_available = "harness_config_hash" in run

    raw_reviews = trace.get("reviews")
    reviews = (
        [_review_projection(review) for review in raw_reviews if isinstance(review, Mapping)]
        if isinstance(raw_reviews, list)
        else []
    )

    criterion = trace.get("criterion_evidence")
    criterion_map = criterion if isinstance(criterion, Mapping) else {}
    claims = criterion_map.get("claims")
    verdicts = criterion_map.get("verdicts")
    raw_claims = (
        [item for item in claims if isinstance(item, Mapping)]
        if isinstance(claims, list)
        else []
    )
    raw_verdicts = (
        [item for item in verdicts if isinstance(item, Mapping)]
        if isinstance(verdicts, list)
        else []
    )
    run_claims = [item for item in raw_claims if item.get("run_id") == run_id]
    run_claim_ids = {
        item.get("id") for item in run_claims if item.get("id") is not None
    }
    claims_list = [_criterion_claim_projection(item) for item in run_claims]
    verdicts_list = [
        _criterion_verdict_projection(item)
        for item in raw_verdicts
        if item.get("claim_id") in run_claim_ids
    ]
    unbound_claim_count = sum(
        not isinstance(item.get("run_id"), str) or not str(item.get("run_id")).strip()
        for item in raw_claims
    )
    other_run_claim_count = len(raw_claims) - len(run_claims) - unbound_claim_count

    raw_outcomes = trace.get("outcomes")
    all_outcomes = (
        [_outcome_projection(outcome) for outcome in raw_outcomes if isinstance(outcome, Mapping)]
        if isinstance(raw_outcomes, list)
        else []
    )
    run_outcomes = [item for item in all_outcomes if item.get("run_id") == run_id]
    task_unbound_outcomes = [item for item in all_outcomes if item.get("run_id") is None]

    raw_timeline = trace.get("timeline")
    timeline = (
        [_event_projection(event) for event in raw_timeline if isinstance(event, Mapping)]
        if isinstance(raw_timeline, list)
        else []
    )

    payload: dict[str, object] = {
        "record_version": 1,
        "record_kind": "MAPS_PORTABLE_RUN_RECORD",
        "task": _task_projection(trace),
        "run": run,
        "context": {
            "refs": context_refs,
            "content_included": False,
            "reason": "Run Record preserves path/hash references, not file contents",
        },
        "environment": environment_list,
        "completion": {
            "submission": _submission_projection(trace),
            "reviews": {
                "items": reviews,
                "join_state": CoverageState.UNKNOWN.value,
                "reason": (
                    "reviews are task-level unless an immutable review subject explicitly binds them to a run"
                ),
            },
            "criterion_evidence": {
                "claims": claims_list,
                "verdicts": verdicts_list,
                "join_state": CoverageState.VERIFIED.value,
                "reason": (
                    "only criterion claims explicitly bound to the selected run and verdicts for those claims are included"
                ),
                "omitted_task_unbound_claims": unbound_claim_count,
                "omitted_other_run_claims": other_run_claim_count,
            },
        },
        "outcomes": {
            "run_bound": run_outcomes,
            "task_unbound": task_unbound_outcomes,
        },
        "timeline": {
            "events": timeline,
            "join_state": CoverageState.UNKNOWN.value,
            "reason": "task_events are task-level and not all events carry run_id",
        },
        "coverage": _coverage(
            trace,
            run_id=run_id,
            environment_source_available=environment_source_available,
            environment_evidence_present=environment_evidence_present,
            harness_config_hash_available=harness_config_hash_available,
            reviews=reviews,
        ),
        "replay": {
            "complete": False,
            "reason": (
                "Run Record v1 preserves observable canonical evidence but lacks "
                "complete provider/session/helper/recovery and operation trajectory sources"
            ),
        },
    }
    digest = _canonical_hash(payload)
    return {
        "record_id": f"RR-{digest}",
        "content_sha256": digest,
        **payload,
    }


def dumps_run_record(record: Mapping[str, object]) -> str:
    return json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False)
