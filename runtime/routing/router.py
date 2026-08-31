from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any, Iterable, Mapping

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
    *,
    environment_reports: Mapping[str, CompatibilityReport] | None = None,
) -> RouteRecommendation:
    """Return a deterministic recommendation from supplied task evidence.

    Consequential task flags affect risk/review policy but do not create a
    routine human gate. ``requires_operator_approval`` now means the task has
    explicitly crossed its inherited permission envelope and needs human
    reauthorization.
    """
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

        # This is task evidence, not a worker-dependent capability result. It
        # must gate before worker selection so an unavailable or empty worker
        # pool cannot hide a proven incompatibility behind a generic wait.
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
            # The task's own environment contract can require a proven
            # environment before it routes. With no fresh report projected for
            # it, hold the task at the policy gate -- a hold, not a hard reject:
            # it clears the moment the task's next flow start records a fresh
            # report. This mirrors the ``environment_incompatible`` fallback
            # above and adds no new PolicyDecision outcome kind. A
            # ``required_for_routing`` that is unset/false is byte-identical to
            # today.
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
            selected = allowed[0]
            route = (
                "propose_helper"
                if selected.worker_class in {"helper", "mechanical"}
                else "claim_or_assign"
            )
            return RouteRecommendation(route, task_id, selected.worker_id)
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

    if blocked_fallbacks:
        return blocked_fallbacks[0]
    return RouteRecommendation("wait_or_reconcile", reasons=("no_routable_task",))
