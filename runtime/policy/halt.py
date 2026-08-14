from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

VALID_STATES = {"clear", "halt_paid_dispatch", "halt_all_dispatch", "repair_only"}
VALID_SCOPES = {"global", "project", "task"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class HaltRecord:
    halt_id: str | None = None
    state: str = "clear"
    reason: str = "none"
    set_by: str | None = None
    set_at: str | None = None
    scope: str = "global"
    target: str | None = None
    clear_requires: str = "operator"
    cleared_by: str | None = None
    cleared_at: str | None = None
    clear_reason: str = ""

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "HaltRecord":
        record = cls(**{field: value.get(field) for field in cls.__dataclass_fields__})
        record.validate()
        return record

    def validate(self) -> None:
        if self.state not in VALID_STATES:
            raise ValueError(f"invalid halt state: {self.state}")
        if self.scope not in VALID_SCOPES:
            raise ValueError(f"invalid halt scope: {self.scope}")
        if self.state != "clear":
            if not self.halt_id or not self.reason or not self.set_by or not self.set_at:
                raise ValueError("active halt requires halt_id, reason, set_by, and set_at")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HaltStore:
    def __init__(self, path: str | Path = ".maps/state/halt.json"):
        self.path = Path(path)

    def load(self) -> HaltRecord:
        if not self.path.exists():
            return HaltRecord()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("halt record must be an object")
        return HaltRecord.from_mapping(data)

    def set(
        self,
        *,
        state: str,
        reason: str,
        actor: str,
        authority: str,
        scope: str = "global",
        target: str | None = None,
        clear_requires: str = "operator",
    ) -> HaltRecord:
        if state == "clear":
            raise ValueError("use clear()")
        if authority not in {"operator", "core", "system"}:
            raise PermissionError("unknown halt authority")
        if state in {"halt_all_dispatch", "repair_only"} and authority not in {"operator", "system"}:
            raise PermissionError(f"{state} requires operator/system authority")
        record = HaltRecord(
            halt_id=f"HALT-{uuid4().hex[:12]}",
            state=state,
            reason=reason.strip(),
            set_by=actor.strip(),
            set_at=utc_now(),
            scope=scope,
            target=target,
            clear_requires=clear_requires,
        )
        record.validate()
        self._write(record)
        return record

    def clear(self, *, actor: str, authority: str, reason: str) -> HaltRecord:
        current = self.load()
        if current.state == "clear":
            return current
        if authority != current.clear_requires and authority != "operator":
            raise PermissionError(f"clearing halt requires {current.clear_requires}")
        cleared = HaltRecord(
            halt_id=current.halt_id,
            state="clear",
            reason=current.reason,
            set_by=current.set_by,
            set_at=current.set_at,
            scope=current.scope,
            target=current.target,
            clear_requires=current.clear_requires,
            cleared_by=actor.strip(),
            cleared_at=utc_now(),
            clear_reason=reason.strip(),
        )
        self._write(cleared)
        return cleared

    def _write(self, record: HaltRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        temp.write_text(
            json.dumps(record.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temp.replace(self.path)


def task_lane(task: dict[str, Any]) -> str:
    task_type = str(task.get("task_type", "")).upper()
    if task_type == "REVIEW" or str(task.get("status", "")).upper() == "READY_FOR_REVIEW":
        return "review"
    if task_type == "REPAIR":
        return "repair"
    policy = task.get("policy", {})
    if isinstance(policy, dict) and policy.get("paid_execution") is False:
        return "local"
    return "paid"


def halt_block_reason(task: dict[str, Any], record: HaltRecord) -> str | None:
    if record.state == "clear":
        return None
    if record.scope == "task" and record.target and record.target != task.get("task_id"):
        return None
    if record.scope == "project" and record.target and record.target != task.get("project_id"):
        return None

    lane = task_lane(task)
    if record.state == "halt_paid_dispatch":
        return None if lane in {"review", "repair", "local"} else record.state
    if record.state == "halt_all_dispatch":
        return None if lane in {"review", "repair"} else record.state
    if record.state == "repair_only":
        return None if lane == "repair" else record.state
    return record.state
