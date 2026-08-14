from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from runtime.policy.evaluator import (
    evaluate_assignment,
    evaluate_review,
    task_needs_operator_approval,
)
from runtime.policy.halt import HaltRecord, halt_block_reason
from runtime.policy.models import WorkerProfile


@dataclass(frozen=True)
class RouteRecommendation:
    route: str
    task_id: str | None = None
    worker_id: str | None = None
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reasons"] = list(self.reasons)
        return payload


def _sorted_workers(workers: Iterable[WorkerProfile]) -> list[WorkerProfile]:
    return sorted(workers, key=lambda item: (item.cost_rank, item.worker_id))


def recommend_route(
    tasks: Iterable[Mapping[str, Any]],
    workers: Iterable[WorkerProfile],
    halt: HaltRecord | None = None,
) -> RouteRecommendation:
    task_list = sorted(
        (dict(task) for task in tasks), key=lambda item: str(item.get("task_id", ""))
    )
    worker_list = _sorted_workers(workers)
    halt_record = halt or HaltRecord()
    blocked_fallbacks: list[RouteRecommendation] = []

    # Review work has priority when it is actually routable. A review that is
    # waiting for an independent reviewer or blocked by policy must not freeze
    # unrelated tasks that can make progress.
    review_tasks = [
        task
        for task in task_list
        if str(task.get("status", "")).upper() == "READY_FOR_REVIEW"
    ]
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
            return RouteRecommendation("review", task_id, eligible[0].worker_id)
        blocked_fallbacks.append(
            RouteRecommendation(
                "wait_for_agent",
                task_id,
                reasons=("no_eligible_independent_reviewer",),
            )
        )

    executable = [
        task
        for task in task_list
        if str(task.get("status", "")).upper() in {"READY", "CHANGES_REQUESTED"}
    ]
    for task in executable:
        task_id = str(task["task_id"])
        block = halt_block_reason(task, halt_record)
        if block:
            blocked_fallbacks.append(
                RouteRecommendation(
                    "policy_gate", task_id, reasons=(f"halt:{block}",)
                )
            )
            continue

        needs_approval, approval_reasons = task_needs_operator_approval(task)
        policy = task.get("policy", {})
        approved = isinstance(policy, Mapping) and bool(
            policy.get("approved_by") and policy.get("approved_at")
        )
        if needs_approval and not approved:
            blocked_fallbacks.append(
                RouteRecommendation(
                    "policy_gate", task_id, reasons=approval_reasons
                )
            )
            continue

        allowed: list[WorkerProfile] = []
        approval_required: set[str] = set()
        for worker in worker_list:
            decision = evaluate_assignment(task, worker)
            if decision.allowed:
                allowed.append(worker)
            elif decision.requires_approval:
                approval_required.update(decision.reasons)

        if allowed:
            selected = allowed[0]
            route = (
                "propose_helper"
                if selected.worker_class in {"helper", "mechanical"}
                else "claim_or_assign"
            )
            return RouteRecommendation(route, task_id, selected.worker_id)
        if approval_required:
            blocked_fallbacks.append(
                RouteRecommendation(
                    "policy_gate",
                    task_id,
                    reasons=tuple(sorted(approval_required)),
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

    if blocked_fallbacks:
        return blocked_fallbacks[0]
    return RouteRecommendation("wait_or_reconcile", reasons=("no_routable_task",))
