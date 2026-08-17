from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


def now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("recovery times must include a timezone")
    return parsed.astimezone(timezone.utc)


@dataclass
class RecoveryIncident:
    incident_id: str
    task_id: str
    worker_id: str
    session_name: str
    reason: str
    resume_after: str
    state: str = "scheduled"
    attempt: int = 0
    next_attempt_at: str | None = None
    last_attempt_at: str | None = None
    last_error: str = ""
    created_at: str = ""
    updated_at: str = ""
    # Optional binding to the immutable MAPS run this incident concerns. Never
    # inferred/guessed here -- absent (None/UNKNOWN) unless a caller that
    # already knows the exact run explicitly supplies it via schedule(). This
    # is the Stage 1 prerequisite for advisory environment-evidence surfacing
    # (see RecoverySupervisor.tick()); it grants no recovery authority by
    # itself and does not change any existing recovery decision.
    run_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RecoveryStore:
    def __init__(self, path: str | Path = ".maps/state/recovery.json"):
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {
                "incidents": {},
                "terminal_sessions": {},
                "last_live": {},
                "ambiguous_workers": {},
            }
        value = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("recovery state must be an object")
        value.setdefault("incidents", {})
        value.setdefault("terminal_sessions", {})
        value.setdefault("last_live", {})
        value.setdefault("ambiguous_workers", {})
        return value

    def save(self, value: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self.path)

    def schedule(
        self,
        *,
        task_id: str,
        worker_id: str,
        session_name: str,
        reason: str,
        resume_after: str,
        run_id: str | None = None,
    ) -> RecoveryIncident:
        parse_time(resume_after)
        state = self.load()
        now = now_z()
        incident = RecoveryIncident(
            incident_id=f"RNS-{uuid4().hex[:12]}",
            task_id=task_id,
            worker_id=worker_id,
            session_name=session_name,
            reason=reason,
            resume_after=resume_after,
            run_id=run_id,
            created_at=now,
            updated_at=now,
        )
        state["incidents"][incident.incident_id] = incident.to_dict()
        self.save(state)
        return incident

    def mark_terminal(self, session_name: str, reason: str) -> None:
        if reason not in {"session_superseded", "disposable_session_ended"}:
            raise ValueError("unsupported terminal-session reason")
        state = self.load()
        state["terminal_sessions"][session_name] = {
            "reason": reason,
            "recorded_at": now_z(),
        }
        self.save(state)
