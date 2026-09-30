from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from runtime.policy.models import WorkerProfile

from .broker import DecisionBroker


@dataclass(frozen=True)
class WorkerSelection:
    worker: WorkerProfile
    evidence: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class TaskSelection:
    task: Mapping[str, Any]
    evidence: Mapping[str, Any] | None = None


def _task_projection(task: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "task_id",
        "title",
        "status",
        "agi_status",
        "task_type",
        "risk",
        "objective",
        "acceptance_criteria",
        "output_paths",
    )
    return {key: task[key] for key in keys if key in task}


def _task_description(task: Mapping[str, Any]) -> str:
    parts = [
        f"status={task.get('status', '')}",
        f"type={task.get('task_type', '')}",
        f"risk={task.get('risk', '')}",
    ]
    title = str(task.get("title", "")).strip()
    objective = str(task.get("objective", "")).strip()
    if title:
        parts.append(f"title={title}")
    if objective:
        parts.append(f"objective={objective[:500]}")
    return "; ".join(parts)


def select_eligible_task(
    tasks: Iterable[Mapping[str, Any]],
    *,
    broker: DecisionBroker | None = None,
    decision_type: str = "next_task_selection",
) -> TaskSelection:
    candidates = list(tasks)
    if not candidates:
        raise ValueError("tasks cannot be empty")

    deterministic = candidates[0]
    if broker is None or len(candidates) == 1:
        return TaskSelection(deterministic)

    choices = {
        str(task["task_id"]): _task_description(task)
        for task in candidates
    }
    decision = broker.choose(
        decision_type=decision_type,
        state={"candidate_tasks": [_task_projection(task) for task in candidates]},
        question=(
            "Which already-routable task is the highest-value next action toward "
            "the parent outcome? Prefer useful progress, dependency unblocking, "
            "risk reduction, and avoiding unnecessary coordination. All choices "
            "have already passed deterministic MAPS authority and routing gates."
        ),
        choices=choices,
        deterministic_choice=str(deterministic["task_id"]),
    )
    selected = next(
        task for task in candidates if str(task["task_id"]) == decision.selected
    )
    return TaskSelection(selected, decision.evidence)


def _worker_criteria(worker: WorkerProfile) -> str:
    task_types = ", ".join(worker.supported_task_types)
    return (
        f"class={worker.worker_class}; cost_rank={worker.cost_rank}; "
        f"max_risk={worker.max_risk}; task_types={task_types}; "
        f"can_mutate={worker.can_mutate}; can_review={worker.can_review}"
    )


def select_eligible_worker(
    task: Mapping[str, Any],
    eligible_workers: Iterable[WorkerProfile],
    *,
    broker: DecisionBroker | None = None,
    decision_type: str = "worker_selection",
) -> WorkerSelection:
    """Choose among workers already approved by deterministic MAPS policy."""

    workers = list(eligible_workers)
    if not workers:
        raise ValueError("eligible_workers cannot be empty")

    deterministic = workers[0]
    if broker is None or len(workers) == 1:
        return WorkerSelection(deterministic)

    choices = {worker.worker_id: _worker_criteria(worker) for worker in workers}
    decision = broker.choose(
        decision_type=decision_type,
        state={
            "task": _task_projection(task),
            "eligible_workers": [worker.to_dict() for worker in workers],
        },
        question=(
            "Which eligible worker is most appropriate for completing this task "
            "successfully while minimizing total execution, coordination, retry, "
            "and compute cost? All choices already passed MAPS authority and "
            "capability gates; do not infer or widen permission."
        ),
        choices=choices,
        deterministic_choice=deterministic.worker_id,
    )
    selected = next(worker for worker in workers if worker.worker_id == decision.selected)
    return WorkerSelection(selected, decision.evidence)
