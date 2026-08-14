from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

RISK_RANK = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
WORKER_CLASSES = {"core", "bounded", "helper", "mechanical"}


@dataclass(frozen=True)
class WorkerProfile:
    worker_id: str
    worker_class: str
    available: bool = True
    supported_task_types: tuple[str, ...] = ("*",)
    max_risk: str = "HIGH"
    can_mutate: bool = True
    can_review: bool = False
    cost_rank: int = 100

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "WorkerProfile":
        for field in ("available", "can_mutate", "can_review"):
            if field in value and not isinstance(value[field], bool):
                raise ValueError(f"{field} must be boolean")
        worker_id = str(value.get("worker_id", "")).strip()
        worker_class = str(value.get("worker_class", "")).strip().lower()
        supported = value.get("supported_task_types", ("*",))
        if isinstance(supported, str):
            supported = (supported,)
        if not isinstance(supported, (list, tuple)):
            raise ValueError("supported_task_types must be a list/tuple or string")
        profile = cls(
            worker_id=worker_id,
            worker_class=worker_class,
            available=value.get("available", True),
            supported_task_types=tuple(
                str(item).upper() for item in supported if str(item).strip()
            ),
            max_risk=str(value.get("max_risk", "HIGH")).strip().upper(),
            can_mutate=value.get("can_mutate", True),
            can_review=value.get("can_review", False),
            cost_rank=int(value.get("cost_rank", 100)),
        )
        profile.validate()
        return profile

    def validate(self) -> None:
        if not self.worker_id:
            raise ValueError("worker_id is required")
        if self.worker_class not in WORKER_CLASSES:
            raise ValueError(f"unknown worker_class: {self.worker_class}")
        if self.max_risk not in RISK_RANK:
            raise ValueError(f"unknown max_risk: {self.max_risk}")
        if not self.supported_task_types:
            raise ValueError("supported_task_types cannot be empty")
        if self.cost_rank < 0:
            raise ValueError("cost_rank must be >= 0")

    def supports_task_type(self, task_type: str) -> bool:
        normalized = str(task_type or "").upper()
        return "*" in self.supported_task_types or normalized in self.supported_task_types

    def supports_risk(self, risk: str) -> bool:
        return RISK_RANK.get(str(risk or "").upper(), 999) <= RISK_RANK[self.max_risk]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["supported_task_types"] = list(self.supported_task_types)
        return payload


@dataclass(frozen=True)
class PolicyDecision:
    decision: str  # allow | reject | require_approval
    reasons: tuple[str, ...] = ()

    @property
    def allowed(self) -> bool:
        return self.decision == "allow"

    @property
    def requires_approval(self) -> bool:
        return self.decision == "require_approval"

    def to_dict(self) -> dict[str, Any]:
        return {"decision": self.decision, "reasons": list(self.reasons)}
