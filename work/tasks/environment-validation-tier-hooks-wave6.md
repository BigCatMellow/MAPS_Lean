# Task: EnvironmentSpec validation-tier Hook wiring

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/environment-validation-tier-hooks-wave6`
- Risk: `MEDIUM`
- Goal: give `EnvironmentSpec.validation` (quick/normal/full command tiers,
  already schema'd since `environment-spec-wave2`) a real executor and a
  Hook-callback factory, so a declared validation tier can actually run and
  produce a structured pass/fail result, closing the gap identified by
  cross-referencing `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md`
  phase **H4 — Immediate validation hooks** and
  `03-environment-and-reproducibility.md` phase **E4 — Validation tiers**
  against current code: `ValidationTiers` was pure declared data with zero
  callers, and `HookEvent.BEFORE_WRITE`/`AFTER_WRITE` were declared enum
  values with zero registrations anywhere in the runtime.

## Inputs and source of truth

- `runtime/environment/spec.py` -- `ValidationTiers`/`EnvironmentSpec.validation`
  (unmodified by this task) already declare `quick`/`normal`/`full` command
  lists; this task adds the first code that reads them.
- `runtime/environment/fingerprint.py` -- `CommandResult`/`CommandRunner`
  pattern for shelling out and reporting `found`/`returncode`/`stdout` is the
  precedent this task's `CommandOutcome`/`CommandExecutor` follows for
  consistency; not reused directly because fingerprinting never runs
  validation commands (`inspect_local_environment` docstring: "Setup/validation
  commands are never executed here").
- `runtime/harness/hooks.py` -- `HookOutcome`/`HookDirective`/`HookRegistry`
  (unmodified) provide the Hook contract this task's callback factory targets.
- `runtime/state/observability.py::redact_sensitive_text` (unmodified) --
  reused for best-effort secret redaction of captured command output, same
  boundary already used by `EnvironmentSpec`'s own persisted-text fields.
- `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md` section 15
  (H4) and `03-environment-and-reproducibility.md` section 21 (E4) -- planning
  source; non-authoritative, evidence only.

## Change boundary

MAY CHANGE / ADD:
- `runtime/environment/validation.py` (new module)
- `runtime/environment/__init__.py` (additive exports only)
- `tests/test_environment_validation.py` (new)
- `runtime/README.md` (one line under the environment bullet)
- this task doc

MUST NOT CHANGE:
- `runtime/environment/spec.py`, `fingerprint.py`, `safety.py` (schema/inspection
  logic reused as-is)
- `runtime/harness/hooks.py`, `service.py`, `protocol.py`, `types.py`
- no production call site is wired to actually invoke the new hook at
  `BEFORE_WRITE`/`AFTER_WRITE` -- there is no existing generic "write" call
  site in `HarnessService` (it only has start/attach/send/inspect/heartbeat/
  resume/stop/collect against session-based adapters, not a file-write
  operation). Wiring a real caller is future work; this task only makes the
  validation-tier execution and Hook-callback pieces exist and be correct.

## Required semantics

1. `run_validation_tier(spec, tier, repo_root, executor=None)` executes
   `spec.validation.<tier>` commands in declared order via a swappable
   `CommandExecutor`, stopping at the first non-passing command
   (`found and returncode == 0`) and recording the remainder as `skipped`
   rather than silently running past a failure.
2. Commands are declared, operator-authored `EnvironmentSpec` content -- the
   same trust boundary `setup_commands`/`maintenance_commands` already rely
   on -- not caller-supplied input; no new injection surface is introduced.
3. Captured command output is redacted via `redact_sensitive_text` before
   being kept in the result, matching the existing secret-safety pattern in
   `spec.py`/`fingerprint.py`.
4. `ValidationTierResult.to_operation_result()` returns the shared
   `OperationResult` envelope (`VALIDATION_PASSED`/`VALIDATION_FAILED`), so a
   future caller gets the same normalized-result contract as harness
   operations (H1).
5. `make_validation_hook(spec, tier, repo_root, executor=None)` returns a
   `HookCallback` that runs the declared tier and maps pass -> `ALLOW`,
   fail -> `DENY` with a reason naming the failing command and full result
   as annotations -- narrowing/blocking only, never granting authority the
   registry didn't already have.
6. An unknown tier name raises `ValidationTierError` rather than silently
   validating nothing.

## Acceptance criteria

- [x] `run_validation_tier` reads the correct tier's command list and stops
      at the first failing command, recording `skipped` for the remainder.
- [x] Failing command output is redacted before being kept as evidence.
- [x] `to_operation_result()` reports `VALIDATION_PASSED`/`VALIDATION_FAILED`
      correctly for passing/failing runs.
- [x] `make_validation_hook` produces `ALLOW` on a passing tier and `DENY`
      (with the failing command named in the reason) on a failing tier, when
      registered into a real `HookRegistry` and run through
      `HookRegistry.run()`.
- [x] The hook factory demonstrably reads the *declared* tier's own commands
      (a `full`-tier failure is caught while `quick` still passes in the same
      spec), not an arbitrary or hard-coded tier.
- [x] An unknown tier name raises `ValidationTierError`.
- [x] `python3 -m unittest tests.test_environment_validation -v` and the full
      suite (`python3 -m unittest discover -s tests -v`) pass.
- [ ] Independent review remains required before completion.

## Verification

```text
python3 -m unittest tests.test_environment_validation -v
python3 -m unittest discover -s tests -v
```

Review required: `INDEPENDENT_REVIEW`. Self-authored; owner is not eligible
to supply that review (`work/reviews/pr-<N>-review-evidence.md` required
before merge per `scripts/check_review_evidence.py`).

## Stop / escalate

Stop rather than guess if:
- a design would wire this into a real production call site (`HarnessService`
  or an adapter) -- out of scope; no such write-operation call site exists
  yet for any adapter, and inventing one is a separate, larger decision;
- a design would let a validation-tier command's output or exit code grant
  task/session/policy authority beyond the existing Hook `ALLOW`/`DENY`
  narrowing contract.
