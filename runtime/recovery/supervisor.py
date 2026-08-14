from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from runtime.communication import HcomAdapter, HcomError
from .store import RecoveryStore, parse_time

LIVE_STATUSES = {"active", "listening", "waiting", "blocked"}
DEFAULT_BACKOFF_SECONDS = (300, 900, 1800, 3600, 7200)


def session_is_live(session: Mapping[str, Any], *, stale_after_seconds: int = 1800) -> bool:
    if str(session.get("status", "")).lower() not in LIVE_STATUSES:
        return False
    process_bound = session.get("process_bound")
    if process_bound is not None:
        return bool(process_bound)
    age = session.get("status_age_seconds")
    if isinstance(age, (int, float)) and age > stale_after_seconds:
        return False
    return True


def _time_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class RecoverySupervisor:
    """Resume known sessions for already-active work; never mutate task truth."""

    def __init__(
        self,
        *,
        task_reader: Any,
        hcom: HcomAdapter,
        recovery_store: RecoveryStore | None = None,
        backoff_seconds: tuple[int, ...] = DEFAULT_BACKOFF_SECONDS,
        silent_stop_probe_delay_seconds: int = 900,
    ):
        self.task_reader = task_reader
        self.hcom = hcom
        self.store = recovery_store or RecoveryStore()
        self.backoff_seconds = backoff_seconds
        self.silent_stop_probe_delay_seconds = silent_stop_probe_delay_seconds
        if not backoff_seconds or any(value <= 0 for value in backoff_seconds):
            raise ValueError("backoff_seconds must contain positive values")

    @staticmethod
    def _open_incident_for(state: dict[str, Any], task_id: str, session_name: str) -> bool:
        return any(
            item.get("task_id") == task_id
            and item.get("session_name") == session_name
            and item.get("state") in {"scheduled", "probing"}
            for item in state.get("incidents", {}).values()
        )

    def observe_silent_stops(
        self,
        bindings: Mapping[str, str],
        *,
        now: datetime | None = None,
    ) -> list[str]:
        """Open incidents only for prior-live sessions tied to current ACTIVE claims.

        A worker with multiple ACTIVE tasks is ambiguous because the binding is
        worker -> session, not task -> session. RnS records that ambiguity and
        refuses to guess which task the stopped session represented.
        """
        now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        sessions = {
            item.get("name"): item
            for item in self.hcom.list_sessions(include_stopped=True)
        }
        state = self.store.load()
        detected: list[tuple[str, str, str]] = []

        tasks_by_worker: dict[str, list[dict[str, Any]]] = {}
        for task in self.task_reader.list_tasks(statuses=("ACTIVE",)):
            worker_id = str(task.get("claimed_by") or "").strip()
            if worker_id:
                tasks_by_worker.setdefault(worker_id, []).append(task)

        state["ambiguous_workers"] = {
            worker_id: sorted(str(task["task_id"]) for task in tasks)
            for worker_id, tasks in tasks_by_worker.items()
            if len(tasks) != 1
        }
        active_by_worker = {
            worker_id: tasks[0]
            for worker_id, tasks in tasks_by_worker.items()
            if len(tasks) == 1
        }

        for worker_id, session_name in sorted(bindings.items()):
            task = active_by_worker.get(worker_id)
            if not task:
                continue
            if session_name in state["terminal_sessions"]:
                continue
            current = session_is_live(sessions.get(session_name, {}))
            previous = bool(state["last_live"].get(session_name, False))
            state["last_live"][session_name] = current
            if previous and not current and not self._open_incident_for(
                state, str(task["task_id"]), session_name
            ):
                detected.append((str(task["task_id"]), worker_id, session_name))

        self.store.save(state)
        opened: list[str] = []
        for task_id, worker_id, session_name in detected:
            incident = self.store.schedule(
                task_id=task_id,
                worker_id=worker_id,
                session_name=session_name,
                reason="silent_stop",
                resume_after=_time_z(
                    now + timedelta(seconds=self.silent_stop_probe_delay_seconds)
                ),
            )
            opened.append(incident.incident_id)
        return opened

    def tick(self, *, now: datetime | None = None) -> list[dict[str, Any]]:
        """Process due incidents and return an audit-friendly action list."""
        now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        sessions = {
            item.get("name"): item
            for item in self.hcom.list_sessions(include_stopped=True)
        }
        state = self.store.load()
        actions: list[dict[str, Any]] = []

        for incident_id, incident in sorted(state["incidents"].items()):
            if incident.get("state") not in {"scheduled", "probing"}:
                continue
            session_name = str(incident["session_name"])
            task_id = str(incident["task_id"])
            worker_id = str(incident["worker_id"])

            if session_name in state["terminal_sessions"]:
                incident["state"] = "suppressed"
                incident["last_error"] = "terminal_session"
                incident["updated_at"] = _time_z(now)
                actions.append(
                    {
                        "incident_id": incident_id,
                        "action": "suppress",
                        "reason": "terminal_session",
                    }
                )
                continue

            task = self.task_reader.get_task(task_id)
            if task is None:
                reason = "task_missing"
            elif str(task.get("status", "")).upper() != "ACTIVE":
                reason = "task_not_active"
            elif task.get("claimed_by") != worker_id:
                reason = "claim_changed"
            else:
                reason = ""
            if reason:
                incident["state"] = "suppressed"
                incident["last_error"] = reason
                incident["updated_at"] = _time_z(now)
                actions.append(
                    {"incident_id": incident_id, "action": "suppress", "reason": reason}
                )
                continue

            if session_is_live(sessions.get(session_name, {})):
                incident["state"] = "resolved"
                incident["last_error"] = ""
                incident["updated_at"] = _time_z(now)
                actions.append(
                    {
                        "incident_id": incident_id,
                        "action": "resolve",
                        "reason": "session_live",
                    }
                )
                continue

            due_at = parse_time(str(incident["resume_after"]))
            if incident.get("next_attempt_at"):
                due_at = max(due_at, parse_time(str(incident["next_attempt_at"])))
            if now < due_at:
                continue

            attempt = int(incident.get("attempt", 0))
            if attempt >= len(self.backoff_seconds):
                incident["state"] = "failed"
                incident["last_error"] = "retry_budget_exhausted"
                incident["updated_at"] = _time_z(now)
                actions.append(
                    {
                        "incident_id": incident_id,
                        "action": "fail",
                        "reason": "retry_budget_exhausted",
                    }
                )
                continue

            try:
                self.hcom.resume(session_name, headless=True, go=True)
                error = ""
                action = "resume"
            except HcomError as exc:
                error = str(exc)
                action = "resume_failed"

            attempt += 1
            incident["attempt"] = attempt
            incident["state"] = "probing"
            incident["last_attempt_at"] = _time_z(now)
            incident["last_error"] = error
            incident["next_attempt_at"] = _time_z(
                now
                + timedelta(
                    seconds=self.backoff_seconds[
                        min(attempt - 1, len(self.backoff_seconds) - 1)
                    ]
                )
            )
            incident["updated_at"] = _time_z(now)
            actions.append(
                {
                    "incident_id": incident_id,
                    "action": action,
                    "attempt": attempt,
                    "error": error,
                }
            )

        self.store.save(state)
        return actions
