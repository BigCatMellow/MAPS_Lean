from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any, Iterable, Mapping

from runtime.decision import (
    DecisionBroker,
    select_eligible_task,
    select_eligible_worker,
)
from runtime.policy.evaluator import (
    evaluate_assignment,
    evaluate_review,
    task_needs_human_reauthorization,
)
from runtime.policy.halt import HaltRecord, halt_block_reason
from runtime.policy.models import WorkerProfile

if TYPE_CHECKING:
    from runtime.environment.fingerprint import CompatibilityReport


@dataclass(frozen=True)
class RouteRecommendation:
    route: str
    task_id: str | None = None
    worker_id: str | None = None
    reasons: tuple[str, ...] = ()
    decision_evidence: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reasons"] = list(self.reasons)
        if self.decision_evidence is None:
            payload.pop("decision_evidence", None)
        return payload


def _sorted_workers(workers: Iterable[WorkerProfile]) -> list[WorkerProfile]:
    return sorted(workers, key=lambda item: (item.cost_rank, item.worker_id))


def _decision_evidence(*items: Mapping[str, Any] | None) -> Mapping[str, Any] | None:
    evidence = {
        str(item["decision_type"]): dict(item)
        for item in items
        if item is not None and item.get("decision_type")
    }
    return evidence or None


def recommend_route(
    tasks: Iterable[Mapping[str, Any]],
    workers: Iterable[WorkerProfile],
    halt: HaltRecord | None = None,
    *,
    environment_reports: Mapping[str, CompatibilityReport] | None = None,
    decision_broker: DecisionBroker | None = None,
) -> RouteRecommendation:
    """Return a recommendation from canonical gates plus optional judgment.

    Deterministic policy decides which tasks/workers are eligible. The optional
    decision broker may rank only those already-eligible choices and can never
    widen authority or bypass policy/environment/halt gates.
    """
    task_list = sorted(
        (dict(task) for task in tasks), key=lambda item: str(item.get("task_id", ""))
    )
    worker_list = _sorted_workers(workers)
    halt_record = halt or HaltRecord()
    blocked_fallbacks: list[RouteRecommendation] = []

    # Review work retains deterministic priority over implementation work.
    review_tasks = [
        task
        for task in task_list
        if str(task.get("status", "")).upper() == "READY_FOR_REVIEW"
    ]
    review_candidates: list[tuple[dict[str, Any], list[WorkerProfile]]] = []
    for task in review_tasks:
        task_id = str(task["task_id"])
        block = halt_block_reason(task, halt_record)
        if block:
            blocked_fallbacks.append(
                RouteRecommendation(
                    "policy_gate", task_id, reasons=(f"halt:{block}",)
                )
            )
            continue
        eligible = [
            worker for worker in worker_list if evaluate_review(task, worker).allowed
        ]
        if eligible:
            review_candidates.append((task, eligible))
            continue
        blocked_fallbacks.append(
            RouteRecommendation(
                "wait_for_agent",
                task_id,
                reasons=("no_eligible_independent_reviewer",),
            )
        )

    if review_candidates:
        task_selection = select_eligible_task(
            [task for task, _ in review_candidates],
            broker=decision_broker,
            decision_type="review_task_selection",
        )
        selected_task = dict(task_selection.task)
        task_id = str(selected_task["task_id"])
        eligible = next(
            reviewers
            for task, reviewers in review_candidates
            if str(task["task_id"]) == task_id
        )
        worker_selection = select_eligible_worker(
            selected_task,
            eligible,
            broker=decision_broker,
            decision_type="reviewer_selection",
        )
        return RouteRecommendation(
            "review",
            task_id,
            worker_selection.worker.worker_id,
            decision_evidence=_decision_evidence(
                task_selection.evidence,
                worker_selection.evidence,
            ),
        )

    executable = [
        task
        for task in task_list
        if str(task.get("status", "")).upper() in {"READY", "CHANGES_REQUESTED"}
    ]
    execution_candidates: list[tuple[dict[str, Any], list[WorkerProfile]]] = []

    for task in executable:
        task_id = str(task["task_id"])
        environment_report = (
            environment_reports.get(task_id) if environment_reports is not None else None
        )
        block = halt_block_reason(task, halt_record)
        if block:
            blocked_fallbacks.append(
                RouteRecommendation(
                    "policy_gate", task_id, reasons=(f"halt:{block}",)
                )
            )
            continue

        needs_reauthorization, reauthorization_reasons = task_needs_human_reauthorization(task)
        policy = task.get("policy", {})
        reauthorized = isinstance(policy, Mapping) and bool(
            policy.get("approved_by") and policy.get("approved_at")
        )
        if needs_reauthorization and not reauthorized:
            blocked_fallbacks.append(
                RouteRecommendation(
                    "policy_gate", task_id, reasons=reauthorization_reasons
                )
            )
            continue

        if environment_report is not None:
            from runtime.environment.fingerprint import CompatibilityState

            if environment_report.state == CompatibilityState.INCOMPATIBLE:
                blocked_fallbacks.append(
                    RouteRecommendation(
                        "policy_gate",
                        task_id,
                        reasons=("environment_incompatible",),
                    )
                )
                continue
        else:
            environment_contract = task.get("environment")
            if isinstance(environment_contract, Mapping) and environment_contract.get(
                "required_for_routing"
            ):
                blocked_fallbacks.append(
                    RouteRecommendation(
                        "policy_gate",
                        task_id,
                        reasons=("environment_report_required",),
                    )
                )
                continue

        allowed: list[WorkerProfile] = []
        reauthorization_required: set[str] = set()
        for worker in worker_list:
            decision = evaluate_assignment(
                task, worker, environment_report=environment_report
            )
            if decision.allowed:
                allowed.append(worker)
            elif decision.requires_approval:
                reauthorization_required.update(decision.reasons)

        if allowed:
            execution_candidates.append((task, allowed))
            continue
        if reauthorization_required:
            blocked_fallbacks.append(
                RouteRecommendation(
                    "policy_gate",
                    task_id,
                    reasons=tuple(sorted(reauthorization_required)),
                )
            )
            continue
        blocked_fallbacks.append(
            RouteRecommendation(
                "wait_for_agent",
                task_id,
                reasons=("no_competent_available_worker",),
            )
        )

    if execution_candidates:
        task_selection = select_eligible_task(
            [task for task, _ in execution_candidates],
            broker=decision_broker,
            decision_type="next_task_selection",
        )
        selected_task = dict(task_selection.task)
        task_id = str(selected_task["task_id"])
        allowed = next(
            workers_for_task
            for task, workers_for_task in execution_candidates
            if str(task["task_id"]) == task_id
        )
        worker_selection = select_eligible_worker(
            selected_task,
            allowed,
            broker=decision_broker,
            decision_type="worker_selection",
        )
        selected = worker_selection.worker
        route = (
            "propose_helper"
            if selected.worker_class in {"helper", "mechanical"}
            else "claim_or_assign"
        )
        return RouteRecommendation(
            route,
            task_id,
            selected.worker_id,
            decision_evidence=_decision_evidence(
                task_selection.evidence,
                worker_selection.evidence,
            ),
        )

    if blocked_fallbacks:
        return blocked_fallbacks[0]
    return RouteRecommendation("wait_or_reconcile", reasons=("no_routable_task",))
