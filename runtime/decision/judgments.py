from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from runtime.incident_taxonomy import IncidentClass, classify_failure_text

from .broker import DecisionBroker


@dataclass(frozen=True)
class AdvisoryJudgment:
    selected: str
    evidence: Mapping[str, Any] | None = None


_INCIDENT_DESCRIPTIONS = {
    IncidentClass.TOOL_FAILURE.value: "A tool, API, parser, or command invocation failed.",
    IncidentClass.CONTEXT_OMISSION.value: "Required context or source information was missing.",
    IncidentClass.CONTEXT_POISONING.value: "Untrusted, stale, or misleading context influenced execution.",
    IncidentClass.ROUTING_ERROR.value: "The task or worker was routed incorrectly.",
    IncidentClass.SKILL_ROUTING_ERROR.value: "A reusable Skill was selected or omitted incorrectly.",
    IncidentClass.HELPER_FAILURE.value: "A delegated helper failed to complete its bounded job.",
    IncidentClass.HELPER_NO_PROGRESS.value: "A helper remained active but made no useful progress.",
    IncidentClass.RECOVERY_FAILURE.value: "Recovery/resume handling failed.",
    IncidentClass.DUPLICATE_EXECUTION.value: "The same work or side effect was executed more than once.",
    IncidentClass.ENVIRONMENT_DRIFT.value: "The execution environment no longer matches required state.",
    IncidentClass.REVIEW_MISS.value: "Review failed to catch a material defect.",
    IncidentClass.STALE_REVIEW_EVIDENCE.value: "Review evidence no longer matches the reviewed state.",
    IncidentClass.VALIDATOR_FALSE_POSITIVE.value: "A validator incorrectly reported a problem.",
    IncidentClass.VALIDATOR_FALSE_NEGATIVE.value: "A validator incorrectly passed defective work.",
    IncidentClass.AUTHORITY_VIOLATION_ATTEMPT.value: "An action attempted to exceed the authority envelope.",
    IncidentClass.ACI_AMBIGUITY.value: "The agent-computer interface left material action/state ambiguous.",
    IncidentClass.SUPPLY_CHAIN_DEFECT.value: "A dependency, package, artifact, or upstream input was defective.",
    IncidentClass.OPERATOR_FRICTION_INTERVENTION.value: "Human intervention was required because of workflow friction.",
    IncidentClass.UNKNOWN.value: "Evidence is insufficient to classify the failure confidently.",
}


def diagnose_failure(
    reason: str,
    *,
    broker: DecisionBroker | None,
    state: Mapping[str, Any] | None = None,
) -> AdvisoryJudgment:
    """Classify a failure without overriding exact deterministic evidence."""

    exact = classify_failure_text(reason)
    if exact is not IncidentClass.UNKNOWN:
        return AdvisoryJudgment(
            exact.value,
            {
                "decision_type": "failure_diagnosis",
                "status": "deterministic_exact",
                "selected": exact.value,
                "applied": True,
                "escalation_recommended": False,
            },
        )

    if broker is None:
        return AdvisoryJudgment(IncidentClass.UNKNOWN.value)

    decision = broker.choose(
        decision_type="failure_diagnosis",
        state={"failure_reason": reason, **dict(state or {})},
        question=(
            "Which MAPS incident class best describes this observed failure? "
            "Preserve UNKNOWN when the evidence is genuinely insufficient."
        ),
        choices=_INCIDENT_DESCRIPTIONS,
        deterministic_choice=IncidentClass.UNKNOWN.value,
    )
    return AdvisoryJudgment(decision.selected, decision.evidence)


_RECOVERY_PATHS = {
    "retry_or_resume": "Retry or resume the same bounded execution when its deterministic gates permit.",
    "inspect_environment_or_validation": "Inspect environment/validation evidence before another attempt.",
    "reassign_worker": "Return the work to orchestration for assignment to another eligible worker.",
    "reasoning_investigation": "Escalate the diagnosis to a capable reasoning worker before acting.",
    "human_authority_check": "Escalate only because the next necessary action may cross human authority.",
}


def recovery_path_advisory(
    action: Mapping[str, Any],
    *,
    task: Mapping[str, Any] | None,
    broker: DecisionBroker | None,
) -> Mapping[str, Any] | None:
    """Recommend a recovery path; never execute it or grant authority."""

    if broker is None:
        return None
    action_name = str(action.get("action", ""))
    if action_name not in {
        "fail",
        "resume_failed",
        "resume_denied",
        "resume_blocked_validation",
    }:
        return None

    reason = str(action.get("reason") or action.get("error") or action_name)
    diagnosis = diagnose_failure(
        reason,
        broker=broker,
        state={
            "action": action_name,
            "task": {
                key: task.get(key)
                for key in ("task_id", "status", "task_type", "risk", "claimed_by")
                if isinstance(task, Mapping) and key in task
            },
        },
    )
    decision = broker.choose(
        decision_type="recovery_path_selection",
        state={
            "recovery_action": action_name,
            "reason": reason,
            "failure_diagnosis": diagnosis.selected,
            "task": {
                key: task.get(key)
                for key in ("task_id", "status", "task_type", "risk", "claimed_by")
                if isinstance(task, Mapping) and key in task
            },
        },
        question=(
            "Which recovery path should the MAPS operator investigate next? "
            "This is advisory only; deterministic authority and recovery gates "
            "still decide what may actually execute."
        ),
        choices=_RECOVERY_PATHS,
        deterministic_choice="reasoning_investigation",
    )
    return {
        "advisory_only": True,
        "failure_diagnosis": {
            "selected": diagnosis.selected,
            "evidence": diagnosis.evidence,
        },
        "recovery_path": {
            "selected": decision.selected,
            "evidence": decision.evidence,
        },
    }


def annotate_recovery_actions(
    actions: Sequence[Mapping[str, Any]],
    task_reader: Any,
    *,
    broker: DecisionBroker | None,
) -> list[dict[str, Any]]:
    """Attach advisory recovery judgments only when a provider is enabled."""

    if broker is None or broker.provider is None or broker.config.mode == "off":
        return [dict(action) for action in actions]

    output: list[dict[str, Any]] = []
    for action in actions:
        item = dict(action)
        task_id = str(item.get("task_id") or "")
        if not task_id:
            # Recovery action payloads use incident_id rather than task_id today;
            # no guessing across that missing link here.
            task = None
        else:
            task = task_reader.get_task(task_id)
        advisory = recovery_path_advisory(item, task=task, broker=broker)
        if advisory is not None:
            item["decision_advisory"] = advisory
        output.append(item)
    return output


def review_evidence_preflight(
    store: Any,
    task_id: str,
    *,
    broker: DecisionBroker | None,
) -> Mapping[str, Any] | None:
    """Advisory preflight before review; never substitutes for reviewer proof."""

    if broker is None or broker.provider is None or broker.config.mode == "off":
        return None

    task = store.get_task(task_id)
    submission = store.get_submission(task_id)
    if not isinstance(task, Mapping) or not isinstance(submission, Mapping):
        return None

    claims = (
        store.get_criterion_claims(task_id)
        if hasattr(store, "get_criterion_claims")
        else []
    )
    evidence_text = str(submission.get("evidence") or "")
    state: dict[str, Any] = {
        "task": {
            "task_id": task_id,
            "risk": task.get("risk"),
            "verification": task.get("verification"),
            "evidence_expected": task.get("evidence_expected"),
            "acceptance_criteria": task.get("acceptance_criteria", []),
            "review_required": task.get("review_required"),
        },
        "submission": {
            "author_id": submission.get("author_id"),
            "submission_count": submission.get("submission_count"),
            "evidence_text_present": bool(evidence_text.strip()),
            "evidence_text_chars": len(evidence_text),
        },
        "criterion_claims": [
            {
                "criterion_id": claim.get("criterion_id"),
                "claimed_status": claim.get("claimed_status"),
                "evidence_ref_count": len(claim.get("evidence_refs") or []),
                "verdict_count": len(claim.get("verdicts") or []),
            }
            for claim in claims
            if isinstance(claim, Mapping)
        ],
    }
    if broker.config.allow_content:
        state["submission"]["evidence_text"] = evidence_text[:8000]

    decision = broker.choose(
        decision_type="evidence_preflight",
        state=state,
        question=(
            "Does the submitted evidence appear ready for an independent review? "
            "This is only a preflight; choose needs_reasoning when evidence cannot "
            "be judged from the supplied state."
        ),
        choices={
            "appears_sufficient": "Evidence appears materially aligned with the stated acceptance/verification expectations.",
            "appears_incomplete": "Evidence appears to omit a material expected proof or acceptance criterion.",
            "needs_reasoning": "The supplied metadata/evidence is insufficient for a cheap bounded judgment.",
        },
        deterministic_choice="needs_reasoning",
    )
    return {
        "advisory_only": True,
        "selected": decision.selected,
        "content_included": broker.config.allow_content,
        "evidence": decision.evidence,
    }
