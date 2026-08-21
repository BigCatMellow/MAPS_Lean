from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


ELIGIBLE_TASK_STATUSES = {"ACTIVE"}


@dataclass(frozen=True)
class ActivityObservation:
    activity_key: str
    progress_key: str


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _observations(items: Sequence[Mapping[str, Any]]) -> list[ActivityObservation]:
    observations: list[ActivityObservation] = []
    for item in items:
        activity_key = _text(item.get("activity_key"))
        progress_key = _text(item.get("progress_key"))
        if not activity_key or not progress_key:
            continue
        observations.append(
            ActivityObservation(activity_key=activity_key, progress_key=progress_key)
        )
    return observations


def no_progress_advisory(
    *,
    session_live: bool,
    task_status: str,
    observations: Sequence[Mapping[str, Any]],
    repeated_activity_threshold: int = 3,
    explicit_wait: bool = False,
    heartbeat_changed: bool = False,
    status_changed: bool = False,
    output_changed: bool = False,
) -> dict[str, Any]:
    """Project advisory no-progress from caller-supplied evidence.

    This function is deliberately read-only. It does not inspect providers,
    mutate task state, kill/reassign workers, or record incidents.
    """

    if (
        isinstance(repeated_activity_threshold, bool)
        or not isinstance(repeated_activity_threshold, int)
        or repeated_activity_threshold <= 1
    ):
        return {
            "state": "UNKNOWN",
            "advisory": None,
            "reason": "INVALID_THRESHOLD",
            "details": {"repeated_activity_threshold": repeated_activity_threshold},
        }
    if not session_live:
        return {"state": "CLEAR", "advisory": None, "reason": "SESSION_NOT_LIVE"}

    normalized_status = _text(task_status).upper()
    if normalized_status not in ELIGIBLE_TASK_STATUSES:
        return {
            "state": "CLEAR",
            "advisory": None,
            "reason": "TASK_NOT_ELIGIBLE",
            "details": {"task_status": normalized_status or "UNKNOWN"},
        }
    if explicit_wait:
        return {"state": "CLEAR", "advisory": None, "reason": "EXPLICIT_WAIT_ACTIVE"}

    progress_reasons = []
    if heartbeat_changed:
        progress_reasons.append("HEARTBEAT_CHANGED")
    if status_changed:
        progress_reasons.append("STATUS_CHANGED")
    if output_changed:
        progress_reasons.append("OUTPUT_CHANGED")
    if progress_reasons:
        return {
            "state": "CLEAR",
            "advisory": None,
            "reason": "PROGRESS_SIGNAL_CHANGED",
            "details": {"signals": progress_reasons},
        }

    usable = _observations(observations)
    if len(usable) < repeated_activity_threshold:
        return {
            "state": "CLEAR",
            "advisory": None,
            "reason": "OBSERVATION_THRESHOLD_NOT_MET",
            "details": {
                "usable_observations": len(usable),
                "repeated_activity_threshold": repeated_activity_threshold,
            },
        }

    window = usable[-repeated_activity_threshold:]
    activity_keys = {item.activity_key for item in window}
    progress_keys = {item.progress_key for item in window}
    if len(activity_keys) != 1:
        return {
            "state": "CLEAR",
            "advisory": None,
            "reason": "ACTIVITY_VARIED",
            "details": {"activity_keys": sorted(activity_keys)},
        }
    if len(progress_keys) != 1:
        return {
            "state": "CLEAR",
            "advisory": None,
            "reason": "PROGRESS_KEY_CHANGED",
            "details": {"progress_keys": sorted(progress_keys)},
        }

    return {
        "state": "NO_PROGRESS",
        "advisory": "HELPER_NO_PROGRESS",
        "reason": "REPEATED_EQUIVALENT_ACTIVITY_WITHOUT_PROGRESS",
        "details": {
            "activity_key": window[-1].activity_key,
            "progress_key": window[-1].progress_key,
            "observation_count": len(window),
            "repeated_activity_threshold": repeated_activity_threshold,
            "remediation": "ADVISORY_ONLY",
        },
    }
