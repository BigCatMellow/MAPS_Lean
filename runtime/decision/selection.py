from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from runtime.policy.models import WorkerProfile

from .provider import ChoiceDecision, DecisionProvider

DECISION_MODES = {"off", "shadow", "active"}


@dataclass(frozen=True)
class WorkerSelection:
    worker: WorkerProfile
    evidence: Mapping[str, Any] | None = None


def _task_state(task: Mapping[str, Any], workers: list[WorkerProfile]) -> dict[str, Any]:
    task_keys = (
        "task_id",
        "status",
        "agi_status",
        "task_type",
        "risk",
        "objective",
        "acceptance_criteria",
        "output_paths",
    )
    return {
        "task": {key: task[key] for key in task_keys if key in task},
        "eligible_workers": [worker.to_dict() for worker in workers],
    }


def _criteria(worker: WorkerProfile) -> str:
    task_types = ", ".join(worker.supported_task_types)
    return (
        f"class={worker.worker_class}; cost_rank={worker.cost_rank}; "
        f"max_risk={worker.max_risk}; task_types={task_types}; "
        f"can_mutate={worker.can_mutate}; can_review={worker.can_review}"
    )


def _valid_decision(decision: ChoiceDecision, eligible_ids: set[str]) -> bool:
    if decision.choice not in eligible_ids:
        return False
    try:
        confidence = float(decision.confidence)
        probability_items = list(decision.probabilities.items())
    except (AttributeError, TypeError, ValueError):
        return False
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        return False
    probability_keys = {str(key) for key, _ in probability_items}
    if not probability_keys.issubset(eligible_ids):
        return False
    for _, value in probability_items:
        try:
            probability = float(value)
        except (TypeError, ValueError):
            return False
        if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
            return False
    return True


def select_eligible_worker(
    task: Mapping[str, Any],
    eligible_workers: Iterable[WorkerProfile],
    *,
    provider: DecisionProvider | None = None,
    mode: str = "off",
) -> WorkerSelection:
    """Choose among workers already approved by deterministic MAPS policy.

    off preserves the existing cheapest-competent route.
    shadow asks the provider but never changes the selected worker.
    active may select the provider recommendation, but only when it names a
    worker already present in eligible_workers.

    Provider errors or invalid responses always degrade to the deterministic
    selection. This seam can influence preference, never eligibility/authority.
    """

    if mode not in DECISION_MODES:
        raise ValueError(f"unknown decision mode: {mode}")

    workers = list(eligible_workers)
    if not workers:
        raise ValueError("eligible_workers cannot be empty")

    deterministic = workers[0]
    if mode == "off" or provider is None or len(workers) == 1:
        return WorkerSelection(deterministic)

    choices = {worker.worker_id: _criteria(worker) for worker in workers}
    provider_name = str(getattr(provider, "provider_name", provider.__class__.__name__))

    try:
        decision = provider.choose(
            state=_task_state(task, workers),
            question=(
                "Which eligible worker is most appropriate for completing this task "
                "successfully while minimizing total execution, coordination, retry, "
                "and compute cost? All supplied choices already passed MAPS authority "
                "and capability gates; do not infer or widen permission."
            ),
            choices=choices,
        )
    except Exception as exc:
        return WorkerSelection(
            deterministic,
            {
                "mode": mode,
                "provider": provider_name,
                "status": "error",
                "error_type": type(exc).__name__,
                "selected_worker_id": deterministic.worker_id,
            },
        )

    eligible_ids = set(choices)
    if not _valid_decision(decision, eligible_ids):
        return WorkerSelection(
            deterministic,
            {
                "mode": mode,
                "provider": provider_name,
                "status": "invalid",
                "suggested_worker_id": decision.choice,
                "selected_worker_id": deterministic.worker_id,
            },
        )

    selected = deterministic
    if mode == "active":
        selected = next(worker for worker in workers if worker.worker_id == decision.choice)

    return WorkerSelection(
        selected,
        {
            "mode": mode,
            "provider": decision.provider or provider_name,
            "model": decision.model,
            "status": "ok",
            "suggested_worker_id": decision.choice,
            "selected_worker_id": selected.worker_id,
            "confidence": float(decision.confidence),
            "probabilities": {
                str(key): float(value) for key, value in decision.probabilities.items()
            },
        },
    )
