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

This module is also the composition root for the *advisory* resume-path
validation tier, per
`work/notes/2026-08-25-rns-validation-tier-hookin-design.md`. `RunBoundValidator`
below is the only place in the recovery package that knows about declared
environment specs or validation tiers; `runtime/recovery/supervisor.py` receives
it as an opaque duck-typed `resume_validator` and never imports (or even names)
those types, so the #160 source guard
`tests/test_recovery_supervisor.py::test_no_validation_tier_commands_or_task_mutation_in_source`
keeps passing unmodified.

Authority note (why executing DB-sourced commands here is in-bounds). The tier
commands are read from a `run_environment_evidence.spec_snapshot` row, not from
an operator-authored file on disk, and they are executed unattended. That is a
deliberate, bounded widening of the trust boundary
`runtime/environment/validation.py` already relies on for
`EnvironmentSpec.setup_commands`, and it holds because:

- rows can only be created by `record_run_environment_evidence`, which requires
  an already-existing `run_manifests.run_id` and stamps a `recorded_by` actor,
  so a row is authored inside the same task DB this recovery pass already trusts
  for task truth, claims and lineage -- an attacker who can insert rows there can
  already redirect the pass in worse ways;
- the snapshot is the operator-authored spec verbatim, rows are insert-only
  (an `UPDATE` is refused by a database trigger: "run environment evidence is
  immutable"), and the snapshot's `sha256` is re-derived and compared against the
  row's `environment_spec_hash` column before anything runs -- so a snapshot that
  disagrees with its own recorded hash is rejected as `spec_hash_mismatch` rather
  than executed;
- only the `quick` tier is ever reachable from here (`normal`/`full` are
  review-time tiers and are not wired);
- the blast radius is bounded by composition: no validator is constructed on the
  `claim`-piggyback path at all, so this only ever runs inside an explicitly
  invoked `maps recovery-tick --repo-root ...`, i.e. with a human or CI
  deliberately naming the checkout the commands may run in.

Executing a row's `validation.quick` is therefore treated as exactly the same
authority as executing that spec's `setup_commands`, and nothing more.
"""

from __future__ import annotations

from pathlib import Path
from time import monotonic
from typing import Any, Callable, Mapping

from runtime.communication import HcomAdapter

# Import order below is load-bearing, not alphabetical: `runtime.state` must be
# fully imported before `runtime.environment`. Those two packages are mutually
# dependent at module level (`runtime/state/environment.py` imports
# `runtime.environment`, and `runtime/environment/spec.py` imports
# `runtime.state.observability`), and only the state-first order resolves --
# importing `runtime.environment` first raises ImportError on a partially
# initialized module. That is a pre-existing property of those two packages,
# unchanged and unfixable from here.
from runtime.state.observability import redact_sensitive_text
from runtime.environment import parse_environment_spec, run_validation_tier

# Deliberate reuse of the canonical command executor rather than a second copy
# of it here. Re-implementing it would duplicate the one place that owns the
# command-execution trust boundary, and it is not even possible in this module:
# `tests/test_recovery_production_trigger.py`'s source guard forbids this file
# from importing `subprocess` at all (a #165 boundary that must keep holding).
from runtime.environment.validation import _default_executor
from runtime.recovery.store import RecoveryStore
from runtime.recovery.supervisor import RecoverySupervisor

# Match HcomAdapter's own constructor defaults rather than inventing new ones.
DEFAULT_HCOM_DIR = ".hcom"
DEFAULT_HCOM_EXECUTABLE = "hcom"
# Match RecoveryStore's own constructor default.
DEFAULT_RECOVERY_STATE_PATH = ".maps/state/recovery.json"
# HcomAdapter's own default, used by the standalone `recovery-tick` subcommand,
# which is a deliberate, explicitly-invoked diagnostic pass.
DEFAULT_HCOM_TIMEOUT_SECONDS = 30.0
# Deliberately much shorter for the `claim`-piggybacked pass. That pass is
# best-effort and opportunistic, never a requirement for the claim to be
# correct, so it must not stall a previously pure-local, fast operation behind
# an unresponsive hcom. One pass makes two `hcom list` calls
# (observe_silent_stops, then tick), so this bounds the added worst-case
# latency on a successful `claim` at roughly 2x this value, after which the
# pass fails, is contained by run_recovery_tick_isolated, and the claim
# result is emitted unchanged.
CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS = 3.0

# Only the immediate tier is reachable from a recovery pass. `normal`/`full`
# are review-time tiers and have no business inside a bounded resume pass.
VALIDATION_TIER = "quick"
# Wall-clock budget for one incident's whole tier, not per command: once this
# much time has elapsed inside a single `run_validation_tier` call, no further
# command in that tier is started.
DEFAULT_VALIDATION_TIER_BUDGET_SECONDS = 60.0
# Wall-clock budget for all validation across one tick, summed across
# incidents. Once exhausted, further incidents report `budget_exceeded` and run
# nothing.
DEFAULT_VALIDATION_TICK_BUDGET_SECONDS = 120.0
# Hard count cap on validations per tick, so N due incidents sharing one spec
# cannot run the tier N times unbounded (no result is cached or reused -- this
# is a counter that skips and records a reason, not a cache).
DEFAULT_MAX_VALIDATIONS_PER_TICK = 4

# Closed vocabulary for `resume_validation["reason"]`. A consumer can never
# confuse "nothing ran" with "passed": whenever `attempted` is False the
# `passed` key is *absent*, not False.
VALIDATION_SKIP_REASONS = (
    "no_run_id_bound",
    "no_repo_root",
    "no_spec_bound",
    "spec_ambiguous",
    "spec_unparseable",
    "spec_hash_mismatch",
    "budget_exceeded",
    "validation_error",
)


class _ValidationBudgetExceeded(Exception):
    """Raised by the bounded executor to abort a tier before its next command."""


class RunBoundValidator:
    """Advisory `quick`-tier validation against a run's own declared spec.

    Duck-types the `resume_validator` input of `RecoverySupervisor`
    (`validate_for_run(run_id) -> dict`). Every return value is one of:

    - `{"attempted": False, "reason": <VALIDATION_SKIP_REASONS>, ...}` -- nothing
      executed; `passed` is deliberately absent.
    - `{"attempted": True, "passed": bool, "tier": ..., "environment_spec_hash":
      ..., "result": <ValidationTierResult.to_dict()>}` -- the tier ran. Command
      output inside `result` has already been secret-redacted by
      `run_validation_tier`.

    The spec is sourced from exactly one place: `run_environment_evidence` rows
    bound to this incident's own `run_id`. There is no fallback, no conventional
    path, no bundled or remembered spec, and no synthesis from a fingerprint --
    when no row exists the honest answer is `no_spec_bound`. Since
    `record_run_environment_evidence` currently has zero production writers, that
    is the answer every real incident gets today; this wiring is deliberately
    inert until a production writer of run-bound environment evidence exists.

    Double-read note. `tick()` separately calls
    `_advisory_environment_evidence(run_id)`, which reads the same table. In the
    production composition below that reader is left `None` (unchanged from
    #165) while this validator does its own read, so production performs exactly
    one read per incident and the two observations cannot disagree. A deployment
    that configures both gets two reads in sequence; because
    `run_environment_evidence` is append-only (insert-only, never updated or
    deleted) and row selection here is deterministic, the only possible
    divergence is a row appended between them, and both values are advisory and
    feed no decision either way.
    """

    def __init__(
        self,
        *,
        environment_reader: Any,
        repo_root: str | Path,
        tier: str = VALIDATION_TIER,
        tier_budget_seconds: float = DEFAULT_VALIDATION_TIER_BUDGET_SECONDS,
        tick_budget_seconds: float = DEFAULT_VALIDATION_TICK_BUDGET_SECONDS,
        max_validations: int = DEFAULT_MAX_VALIDATIONS_PER_TICK,
        executor: Callable[..., Any] | None = None,
        clock: Callable[[], float] = monotonic,
    ):
        self.environment_reader = environment_reader
        self.repo_root = repo_root
        self.tier = tier
        self.tier_budget_seconds = tier_budget_seconds
        self.tick_budget_seconds = tick_budget_seconds
        self.max_validations = max_validations
        self.executor = executor
        self.clock = clock
        self.validations_run = 0
        self.seconds_used = 0.0

    @staticmethod
    def _skip(reason: str, detail: str = "") -> dict[str, Any]:
        result: dict[str, Any] = {"attempted": False, "reason": reason}
        if detail:
            result["detail"] = detail
        return result

    def _error(self, exc: BaseException) -> dict[str, Any]:
        # Exception text is not covered by `_redact_outcome`, which only sees
        # CommandOutcome.output, so redaction is applied explicitly here.
        return self._skip(
            "validation_error",
            f"{type(exc).__name__}: {redact_sensitive_text(str(exc))}",
        )

    def _bounded_executor(self, started: float) -> Callable[..., Any]:
        run_command = self.executor or _default_executor
        remaining_tick = max(0.0, self.tick_budget_seconds - self.seconds_used)
        deadline = started + min(self.tier_budget_seconds, remaining_tick)

        def _bounded(command: str, root: Path) -> Any:
            if self.clock() >= deadline:
                raise _ValidationBudgetExceeded(
                    "validation budget exhausted before the next tier command started"
                )
            return run_command(command, root)

        return _bounded

    def validate_for_run(self, run_id: Any) -> dict[str, Any]:
        if not run_id:
            return self._skip("no_run_id_bound")
        root = Path(self.repo_root)
        if not root.is_dir():
            return self._skip("no_repo_root", f"{root} is not a directory")
        if self.validations_run >= self.max_validations:
            return self._skip(
                "budget_exceeded",
                f"per-tick validation cap of {self.max_validations} reached",
            )
        if self.seconds_used >= self.tick_budget_seconds:
            return self._skip(
                "budget_exceeded",
                f"per-tick wall-clock budget of {self.tick_budget_seconds}s exhausted",
            )

        try:
            rows = self.environment_reader.list_run_environment_evidence(str(run_id))
        except Exception as exc:  # noqa: BLE001 - contained, reported, never raised
            return self._error(exc)
        if not rows:
            return self._skip("no_spec_bound")

        hashes = {str(row.get("environment_spec_hash") or "") for row in rows}
        if len(hashes) > 1:
            return self._skip(
                "spec_ambiguous",
                f"{len(hashes)} distinct declared specs bound to this run",
            )
        row = rows[-1]
        snapshot = row.get("spec_snapshot")
        if not isinstance(snapshot, Mapping):
            return self._skip("spec_unparseable", "spec_snapshot is not an object")
        try:
            spec = parse_environment_spec(dict(snapshot))
        except Exception as exc:  # noqa: BLE001 - contained, reported, never raised
            return self._skip(
                "spec_unparseable",
                f"{type(exc).__name__}: {redact_sensitive_text(str(exc))}",
            )
        stored_hash = str(row.get("environment_spec_hash") or "")
        if stored_hash and spec.sha256 != stored_hash:
            return self._skip(
                "spec_hash_mismatch",
                "recomputed spec hash does not match the recorded one",
            )

        self.validations_run += 1
        started = self.clock()
        try:
            result = run_validation_tier(
                spec,
                self.tier,
                repo_root=root,
                executor=self._bounded_executor(started),
            )
        except _ValidationBudgetExceeded as exc:
            self.seconds_used += self.clock() - started
            return self._skip("budget_exceeded", str(exc))
        except Exception as exc:  # noqa: BLE001 - contained, reported, never raised
            self.seconds_used += self.clock() - started
            return self._error(exc)
        self.seconds_used += self.clock() - started
        return {
            "attempted": True,
            "passed": bool(result.passed),
            "tier": result.tier,
            "environment_spec_hash": result.environment_spec_hash,
            "result": result.to_dict(),
        }


def run_recovery_tick(
    task_reader: Any,
    *,
    bindings: Mapping[str, str] | None = None,
    hcom_dir: str | Path = DEFAULT_HCOM_DIR,
    hcom_executable: str | Path = DEFAULT_HCOM_EXECUTABLE,
    hcom_timeout_seconds: float = DEFAULT_HCOM_TIMEOUT_SECONDS,
    recovery_state_path: str | Path = DEFAULT_RECOVERY_STATE_PATH,
    validation_repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Run exactly one bounded RnS pass and return an audit-friendly summary.

    `task_reader` is the caller's existing `TaskStore`; it is reused as-is and
    never re-opened here. `bindings` is the explicit `worker_id ->
    session_name` mapping `observe_silent_stops()` requires. No production
    source of that mapping exists yet (the design note flags deriving one as
    needing its own design pass), so callers that do not know it pass nothing
    and get an empty mapping -- which detects no silent stops rather than
    guessing at a binding.

    `hcom_timeout_seconds` bounds each individual hcom subprocess call. A pass
    makes two of them (one per `hcom list`), so worst-case added latency is
    about twice this value.

    `validation_repo_root` opts this pass in to advisory `quick`-tier validation
    (`RunBoundValidator`) against each about-to-be-resumed incident's own
    run-bound declared spec. It has **no default**: when it is None -- which is
    every caller that does not deliberately pass one, including the
    `claim`-piggyback path -- no validator is constructed, `resume_validation` is
    None on every action dict, and this pass runs exactly the commands it ran
    before, which is none.

    That is a deliberate cost decision, not an oversight. `claim` was a
    pure-local operation before #165 and is already bounded there at roughly
    2 x CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS; running arbitrary declared shell
    commands inside it could add minutes and would reintroduce exactly the stall
    #165 was written to avoid. Validation is therefore available only where a
    caller explicitly names a checkout to run in -- in practice
    `maps recovery-tick --repo-root ...`, a deliberate, explicitly-invoked pass.
    When it is enabled, the added wall time is bounded by
    DEFAULT_VALIDATION_TICK_BUDGET_SECONDS across the whole tick plus at most one
    in-flight command's own timeout (600s, owned by
    `runtime/environment/validation.py:_default_executor`; tightening that per
    command ceiling is a change to that module and out of scope here), and by
    DEFAULT_MAX_VALIDATIONS_PER_TICK executions.

    Raises whatever the underlying supervisor/hcom calls raise. Callers that
    must not fail on a recovery problem should use `run_recovery_tick_isolated`.
    """
    resume_validator = (
        RunBoundValidator(
            # The caller's existing TaskStore already exposes
            # list_run_environment_evidence; no second store is opened, and
            # RecoverySupervisor.environment_reader stays None (unchanged from
            # #165), so the table is read at most once per incident.
            environment_reader=task_reader,
            repo_root=validation_repo_root,
        )
        if validation_repo_root is not None
        else None
    )
    supervisor = RecoverySupervisor(
        task_reader=task_reader,
        hcom=HcomAdapter(
            hcom_dir=hcom_dir,
            executable=hcom_executable,
            timeout_seconds=hcom_timeout_seconds,
        ),
        recovery_store=RecoveryStore(recovery_state_path),
        resume_validator=resume_validator,
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
    hcom_timeout_seconds: float = DEFAULT_HCOM_TIMEOUT_SECONDS,
    recovery_state_path: str | Path = DEFAULT_RECOVERY_STATE_PATH,
    validation_repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """`run_recovery_tick` with every failure contained in the return value.

    Used by call sites (notably the `claim` CLI branch) whose own contract must
    never regress because a piggybacked recovery pass failed -- an unreachable
    hcom, a corrupt recovery-state file, or any other supervisor error becomes
    `{"ok": False, "error": ...}` instead of an exception. An hcom that hangs is
    contained the same way, via `hcom_timeout_seconds`.
    """
    try:
        return run_recovery_tick(
            task_reader,
            bindings=bindings,
            hcom_dir=hcom_dir,
            hcom_executable=hcom_executable,
            hcom_timeout_seconds=hcom_timeout_seconds,
            recovery_state_path=recovery_state_path,
            validation_repo_root=validation_repo_root,
        )
    except Exception as exc:  # noqa: BLE001 - deliberate isolation boundary
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "opened_incidents": [],
            "actions": [],
        }
