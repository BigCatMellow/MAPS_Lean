from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

VALID_TASK_TYPES = {
    "IMPLEMENTATION", "REVIEW", "ARCHITECTURE", "PLANNING",
    "RESEARCH", "MAINTENANCE", "REPAIR",
}
VALID_RISKS = {"LOW", "MEDIUM", "HIGH"}
VALID_REVIEW = {"OWNER_CHECK", "INDEPENDENT_REVIEW", "OPERATOR_VISIBLE_RELEASE_CHECK"}
ACTIVE_SCOPE_STATUSES = {"READY", "ACTIVE", "READY_FOR_REVIEW", "CHANGES_REQUESTED"}

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def iso_z(value: datetime) -> str:
    value = value.astimezone(timezone.utc).replace(microsecond=0)
    return value.isoformat().replace("+00:00", "Z")

def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    agi_status: str
    reasons: tuple[str, ...] = ()

@dataclass(frozen=True)
class MutationResult:
    ok: bool
    code: str
    message: str
    task: dict | None = None
