# Task: Hook/Harness production composition root

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: make the already-built, already-tested CANONICAL_RUN Hook enforcement
  layer reachable in production by adding the minimum-viable composition root
  designed in `work/notes/2026-08-26-hook-enforcement-composition-root-design.md`
  (merged, PR #177). After this, production RnS resume can route through
  `HarnessService.resume()` with a fail-closed `CanonicalRunGuard` installed —
  but only when a caller explicitly opts in, and default-off otherwise.

## Inputs and source of truth

- `work/notes/2026-08-26-hook-enforcement-composition-root-design.md` — whole
  note; especially §2c (default-off), §3b (construction order), §3c (CLI
  surface), §3d (CanonicalRunGuard only), §4 (non-goals), "Resume prompt".
- `tests/test_recovery_supervisor.py:758-769` — the only existing correct
  composition of `HcomHarnessAdapter`/`HookRegistry`/`HarnessService`; mirrored.
- `runtime/recovery/production.py`, `runtime/recovery/supervisor.py`,
  `runtime/harness/service.py`, `runtime/harness/adapters/hcom.py`,
  `runtime/policy/harness_guard.py`, `runtime/cli.py`.

## Change boundary

- MAY CHANGE:
  - `runtime/recovery/production.py` (new module-level helper + one threaded kw)
  - `runtime/cli.py` (two new `recovery-tick` flags + arg validation)
  - `tests/test_recovery_composition_root.py` (new), `tests/test_recovery_production_trigger.py`
    (source-guard: `production.py` is now the sanctioned harness composition site)
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` (H5/E4/6.5/6.16 evidence text only)
  - this task file
- MUST NOT CHANGE: `runtime/recovery/supervisor.py` (the `harness_service is not
  None` branch already exists — no change needed), `runtime/harness/` internals,
  `runtime/policy/harness_guard.py`, `runtime/policy/destructive_action_guard.py`,
  `playbook/`, any other roadmap doc. No new module/package/daemon/thread.

## What changed

1. `runtime/recovery/production.py::build_canonical_harness_service(task_reader,
   *, project_id, repo_root, ...)` — constructs
   `HcomHarnessAdapter(HcomAdapter(...), project_id=..., lineage_writer=task_reader)`
   → `HookRegistry()` → `register_canonical_run_guards(registry,
   CanonicalRunGuard(task_reader, repo_root=repo_root))` →
   `HarnessService([adapter], hooks=registry)`. Reuses the caller's `TaskStore`
   as `CanonicalRunSource`; opens no second store. `CanonicalRunGuard` only.
2. `run_recovery_tick` / `run_recovery_tick_isolated` gain one optional keyword
   `harness_project_id` (default `None` ⇒ nothing constructed ⇒ byte-identical
   to today). When set, `validation_repo_root` is required (reused as the guard's
   `repo_root`) — a `ValueError` otherwise.
3. `maps recovery-tick` only: `--enforce-canonical-run` and
   `--harness-project-id`. `--enforce-canonical-run` requires both `--repo-root`
   and `--harness-project-id` (loud `parser.error`, exit 2, never inferred).
   `--repo-root` alone stays advisory-validation-only. `maps claim` piggyback
   passes neither.

## Acceptance criteria

- Full `pytest tests/` green; `python3 -m runtime.smoke` clean.
- `grep -rn "HarnessService(\|HookRegistry(\|register_canonical_run_guards(" --include=*.py runtime/ | grep -v '/tests/'`
  now shows the new call site in `runtime/recovery/production.py`.
- Default-off proven by test (`test_default_no_opt_in_constructs_no_harness_service_and_falls_back`).
- Opt-in routing proven by test (`test_opt_in_routes_resume_through_harness_service_with_full_binding`).
- CLI arg-error tests for `--enforce-canonical-run` without `--repo-root` /
  without `--harness-project-id`.
- `test_no_validation_tier_commands_or_task_mutation_in_source` passes unmodified
  (supervisor.py untouched).
- CAPABILITY_CHECKLIST.md H5/E4/6.5/6.16 evidence text updated; no status label
  flipped to DONE.

## Verification

- `python -m pytest tests/ -q`
- `python3 -m runtime.smoke`

## Stop conditions

- Threading the keyword needs a real change to `tick()` decision logic /
  `_CANONICAL_DENIAL_CODES` / retry-backoff → STOP (design §4.3 forbids it).
- An existing test fails for a reason that is not a legitimate update for the
  new optional param → STOP and report verbatim.

## Open questions carried forward (design §5)

- Q4: retry-budget interaction — repeated canonical denials drive an incident to
  `failed`/`retry_budget_exhausted`. Must be decided before enforcement is
  recommended for routine use.
- Q5: expired-lease operator workflow (renew lease, re-run pass?) is undocumented
  and would dominate first-exposure experience.
- These, plus the first real production exposure, are why H5/E4/6.5/6.16 stay
  IN PROGRESS.

## Resume prompt

The composition root is implemented on branch
`impl/hook-harness-composition-root-20260830` and under review. If review
requests changes, address them in `runtime/recovery/production.py` /
`runtime/cli.py` / `tests/test_recovery_composition_root.py` only, keep
enforcement default-off, keep `runtime/recovery/supervisor.py` untouched, re-run
`python -m pytest tests/ -q` and `python3 -m runtime.smoke`, and do not flip any
CAPABILITY_CHECKLIST status label. Do not self-merge — an independent reviewer
owns the verdict.
