from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any


_METRICS = (
    ("max_attempts", "actual_attempts", "attempts"),
    ("max_tool_failures", "actual_tool_failures", "tool_failures"),
    ("runtime_seconds", "actual_runtime_seconds", "runtime_seconds"),
)


def _nonnegative_int(value: int | None, label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer")
    return value


def _safe_filename_part(value: object, fallback: str) -> str:
    text = str(value or fallback)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("._-")
    return safe or fallback


def check_run_budget(
    store: Any,
    run_id: str,
    *,
    actual_attempts: int | None = None,
    actual_tool_failures: int | None = None,
    actual_runtime_seconds: int | None = None,
) -> dict[str, Any]:
    """Compare measured run use with the immutable manifest limits.

    This is a deterministic gate/evidence check. It does not mutate task truth,
    dispatch another attempt, or halt the system by itself.
    """
    actual = {
        "actual_attempts": _nonnegative_int(actual_attempts, "actual_attempts"),
        "actual_tool_failures": _nonnegative_int(
            actual_tool_failures, "actual_tool_failures"
        ),
        "actual_runtime_seconds": _nonnegative_int(
            actual_runtime_seconds, "actual_runtime_seconds"
        ),
    }
    manifest = store.get_run_manifest(run_id)
    if manifest is None:
        return {
            "ok": False,
            "run_id": run_id,
            "reason": "run_not_found",
            "runtime_limits": {},
            "actual": actual,
            "exceeded": [],
        }

    limits = dict(manifest.get("runtime_limits") or {})
    exceeded: list[dict[str, Any]] = []
    for limit_key, actual_key, label in _METRICS:
        limit = limits.get(limit_key)
        measured = actual[actual_key]
        if limit is None or measured is None:
            continue
        if measured >= int(limit):
            exceeded.append(
                {
                    "metric": limit_key,
                    "label": label,
                    "limit": int(limit),
                    "actual": measured,
                }
            )

    return {
        "ok": not exceeded,
        "run_id": run_id,
        "task_id": manifest["task_id"],
        "reason": "within_budget" if not exceeded else "budget_exhausted",
        "runtime_limits": limits,
        "actual": actual,
        "exceeded": exceeded,
    }


def write_budget_escalation(
    record: dict[str, Any],
    *,
    out_dir: str | Path = ".maps/state/escalations",
) -> Path:
    """Persist budget exhaustion as evidence; grant no authority or task state."""
    if record.get("ok") is not False or record.get("reason") != "budget_exhausted":
        raise ValueError("only an exhausted budget record can be escalated")
    run_id = _safe_filename_part(record.get("run_id"), "unknown-run")
    task_id = _safe_filename_part(record.get("task_id"), "unknown-task")
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = directory / f"BUDGET-{task_id}-{run_id}-{stamp}.json"
    payload = {
        **record,
        "created_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
    }
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return path
