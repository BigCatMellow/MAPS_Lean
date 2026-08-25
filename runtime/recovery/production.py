"""One-shot production construction and invocation of the RnS supervisor.

Per `work/notes/2026-08-24-rns-production-trigger-loop-design.md`. This module
is the single production construction site for `RecoverySupervisor`; it exists
because `RecoverySupervisor(...)`, `observe_silent_stops()` and `tick()`
previously had zero production invocation anywhere in the codebase (see
`work/insights/2026-08-19-recoverysupervisor-tick-has-zero-production-invocation-anywh-INSIGHT-e0b448a6.md`).

Bounded by construction, per master roadmap §7.1/§7.9: `run_recovery_tick`
constructs the supervisor, performs exactly one `observe_silent_stops()` pass
and exactly one `tick()` pass, and returns. It holds no long-lived state, opens
no listener, starts no thread or subprocess of its own, and never reschedules
itself. There is deliberately no scheduler, cron entry, daemon, or background
worker here -- the trigger cadence comes entirely from already-occurring
external events (a `maps claim` call, or a human/CI running `maps
recovery-tick`).

`harness_service` and `environment_reader` are intentionally left `None`. Both
are already-supported optional inputs to `RecoverySupervisor`; re-confirmed by
grep at implementation time that no production `HarnessService` /
`HcomHarnessAdapter` construction exists anywhere outside tests, so `tick()`
uses its existing, unchanged direct-`hcom.resume()` fallback. Building that
wiring is explicitly out of scope for this call site.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from runtime.communication import HcomAdapter
from runtime.recovery.store import RecoveryStore
from runtime.recovery.supervisor import RecoverySupervisor

# Match HcomAdapter's own constructor defaults rather than inventing new ones.
DEFAULT_HCOM_DIR = ".hcom"
DEFAULT_HCOM_EXECUTABLE = "hcom"
# Match RecoveryStore's own constructor default.
DEFAULT_RECOVERY_STATE_PATH = ".maps/state/recovery.json"


def run_recovery_tick(
    task_reader: Any,
    *,
    bindings: Mapping[str, str] | None = None,
    hcom_dir: str | Path = DEFAULT_HCOM_DIR,
    hcom_executable: str | Path = DEFAULT_HCOM_EXECUTABLE,
    recovery_state_path: str | Path = DEFAULT_RECOVERY_STATE_PATH,
) -> dict[str, Any]:
    """Run exactly one bounded RnS pass and return an audit-friendly summary.

    `task_reader` is the caller's existing `TaskStore`; it is reused as-is and
    never re-opened here. `bindings` is the explicit `worker_id ->
    session_name` mapping `observe_silent_stops()` requires. No production
    source of that mapping exists yet (the design note flags deriving one as
    needing its own design pass), so callers that do not know it pass nothing
    and get an empty mapping -- which detects no silent stops rather than
    guessing at a binding.

    Raises whatever the underlying supervisor/hcom calls raise. Callers that
    must not fail on a recovery problem should use `run_recovery_tick_isolated`.
    """
    supervisor = RecoverySupervisor(
        task_reader=task_reader,
        hcom=HcomAdapter(hcom_dir=hcom_dir, executable=hcom_executable),
        recovery_store=RecoveryStore(recovery_state_path),
        # environment_reader/harness_service deliberately omitted -- see module docstring.
    )
    opened = supervisor.observe_silent_stops(dict(bindings or {}))
    actions = supervisor.tick()
    return {
        "ok": True,
        "error": "",
        "opened_incidents": list(opened),
        "actions": list(actions),
    }


def run_recovery_tick_isolated(
    task_reader: Any,
    *,
    bindings: Mapping[str, str] | None = None,
    hcom_dir: str | Path = DEFAULT_HCOM_DIR,
    hcom_executable: str | Path = DEFAULT_HCOM_EXECUTABLE,
    recovery_state_path: str | Path = DEFAULT_RECOVERY_STATE_PATH,
) -> dict[str, Any]:
    """`run_recovery_tick` with every failure contained in the return value.

    Used by call sites (notably the `claim` CLI branch) whose own contract must
    never regress because a piggybacked recovery pass failed -- an unreachable
    hcom, a corrupt recovery-state file, or any other supervisor error becomes
    `{"ok": False, "error": ...}` instead of an exception.
    """
    try:
        return run_recovery_tick(
            task_reader,
            bindings=bindings,
            hcom_dir=hcom_dir,
            hcom_executable=hcom_executable,
            recovery_state_path=recovery_state_path,
        )
    except Exception as exc:  # noqa: BLE001 - deliberate isolation boundary
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "opened_incidents": [],
            "actions": [],
        }
