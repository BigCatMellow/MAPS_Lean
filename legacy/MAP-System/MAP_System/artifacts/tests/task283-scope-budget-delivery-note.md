# TASK-283 delivery note

Implemented deterministic run-path scope contracts and retry/runtime
budgets, per the final TASK-277 P2 slice: `scripts/verify_run_scope.py`
(new), `workflow/runtime_policy.yaml`'s new `scope_budget_contracts`
section (additive), `scripts/pre_dispatch_policy.py`'s dispatch-preflight
integration, and `scripts/run_manifest.py`'s extended `readable_scope`/
`forbidden_scope` fields (registered as additional TASK-283 outputs now
that TASK-281, their prior owner, is terminal — same re-registration
pattern TASK-280 used for `map_task.py`). 35 new focused tests across
`tests/test_run_scope.py` (25) and extended `tests/test_run_manifest.py`
coverage (unchanged 10, all still passing).

## The three-tier containment distinction (acceptance criterion 5)

This is the most important thing to get right in this delivery, so it is
stated plainly rather than left implicit:

1. **Prompt-level guidance.** Every core-agent and helper launcher prompt in
   `templates/install/bin/` already tells the agent what it may and may not
   touch, in prose. This was true before TASK-283 and is unchanged by it.
   Prompt guidance is advisory only — nothing prevents a model from
   ignoring it.
2. **Post-run/preflight detection (what TASK-283 actually adds).**
   - `verify_run_scope.validate_scope_contract()` is a **preflight**
     self-consistency check: given a declared readable/writable/forbidden
     contract, it can prove the contract doesn't escape the repo and that
     writable and forbidden don't overlap, *before* work starts. It cannot
     prove a worker will honor the contract once dispatched.
   - `verify_run_scope.verify_post_run_diff()` is a **post-run** check: given
     a list of paths a run actually changed (supplied by the caller — this
     function does no git/filesystem inspection itself), it can *detect*
     an out-of-scope or forbidden write after the fact. Detection is not
     prevention.
   - `verify_run_scope.check_budget()` / `write_escalation_artifact()`
     detect retry/runtime budget exhaustion and record a durable JSON
     escalation artifact under `artifacts/escalations/` instead of allowing
     silent unbounded retries.
   - `pre_dispatch_policy.py`'s `evaluate_pre_dispatch()` now rejects a task
     with an invalid `scope_contract` field, for every tier above 0
     (command-center), before any other tier-specific check runs. This is
     wired into the same function every dispatch decision already goes
     through, so it is real dispatch-preflight enforcement — but only for
     tasks that *declare* a `scope_contract`. A task with no such field is
     completely unaffected (verified by
     `test_task_without_scope_contract_is_unaffected`), which is why this
     did not regress any of the 25 existing pre-dispatch/capability tests
     (all still pass unchanged).
3. **Genuine harness containment. This workspace has none, and TASK-283
   does not claim otherwise.** There is no OS-level sandbox, filesystem
   permission boundary, or process-level enforcement anywhere in this
   repository that would stop a worker from writing outside its declared
   scope, exceeding its declared retry budget, or ignoring
   `verify_post_run_diff()`'s findings. `workflow/runtime_policy.yaml`'s new
   `scope_budget_contracts.containment_level` is explicitly set to
   `preflight_reject_and_post_run_diff_detection`, not `harness_enforced`,
   specifically so no downstream reader can mistake this for a security
   boundary. This matches `REPAIR-0009`'s and this codebase's repeated
   caution: "Do not claim path containment until the runtime enforces it."

`tests/test_run_scope.py` exercises each of the second tier's three
functions directly and separately (contract validation, diff detection,
budget checking) so a reader can see exactly what is proven and what is
not, without needing to trust this note's prose.

## What changed, file by file

- **`scripts/verify_run_scope.py`** (new): `validate_scope_contract()`,
  `verify_post_run_diff()`, `check_budget()`, `write_escalation_artifact()`,
  `load_scope_policy()`. Fully standalone — no dependency on
  `run_manifest.py` or `pre_dispatch_policy.py`; both of those import *from*
  this module, not the reverse.
- **`workflow/runtime_policy.yaml`** (additive edit to an existing,
  actively-used file — confirmed via `grep` that `graph/runner.py`,
  `scripts/halt_state.py`, `scripts/multigate_regression_test.py`, and
  `scripts/task_fingerprint_holdout.py` all read this file; each only reads
  the top-level `runtime_policy` key or does path-name classification, so
  the new sibling `scope_budget_contracts` top-level key is inert to all of
  them — verified live: `graph/runner.py --pretty` still evaluates all 277
  tasks cleanly after this edit). Declares default readable/forbidden paths
  and per-tier retry budgets, consumed by `verify_run_scope.load_scope_policy()`.
- **`scripts/pre_dispatch_policy.py`** (edit): new `scope_contract_issues()`
  helper and its call site inside `evaluate_pre_dispatch()`, immediately
  after the tier-0 early return. No other function in this file was
  touched. `contains_unnegated`/`is_final_review`/etc. (already present
  from TASK-280's prior work) are unchanged.
- **`scripts/run_manifest.py`** (edit, output path re-registered from
  TASK-281 now that it's terminal): `readable_scope`/`forbidden_scope`
  columns, threaded through `create_manifest()`/`get_manifest()`/the CLI,
  and validated via `validate_scope_contract()` at creation time — an
  invalid contract refuses to bind a manifest at all, with no partial row
  (`test_manifest_creation_rejects_invalid_scope_contract`).
- **`migration/run_manifest_schema.sql`** (edit, output path re-registered):
  the two new columns are in the `CREATE TABLE` for fresh databases; for
  databases created before TASK-283 (including any that already ran
  TASK-281's `create_manifest()`), `run_manifest.py`'s `connect()` runs a
  guarded `ALTER TABLE ... ADD COLUMN` migration (`PRAGMA table_info` check
  first, since SQLite has no `ADD COLUMN IF NOT EXISTS`). Verified against a
  hand-built pre-TASK-283 table with an existing row:
  `test_pre_existing_run_manifests_table_migrates_additive_columns`.
- **`tests/test_run_scope.py`** (new, 25 tests) and `tests/test_run_manifest.py`
  (unchanged 10, still pass — confirms the schema/API extension is backward
  compatible).

## Compatibility

- The real canonical `MAP_System/map.db` never had a `run_manifests` table
  before this task (TASK-281's own pilot measurement was run against an
  isolated scratch database, not the canonical one) — so the ALTER TABLE
  path is exercised for the first time by any future real invocation, not
  retroactively on live data. The migration test proves it is safe when
  that does happen.
- `readable_paths`/`forbidden_paths` are optional `create_manifest()`
  parameters; omitting them defaults to `readable=["."]`,
  `forbidden=[]` — every existing caller and test from TASK-281 continues
  to work unchanged (`test_manifest_scope_defaults_when_not_supplied`).
- `scope_contract` on a task is an entirely optional, additive field.
  `pre_dispatch_policy.py`'s existing behavior for all ~277 real tasks
  currently in `map.db` (none of which declare `scope_contract`) is
  unchanged, confirmed by the full existing pre-dispatch/capability suites
  passing unmodified (25/25 + 10/10).

## Rollback

Revert the four edited files (`verify_run_scope.py` can simply be deleted
since nothing outside this task's own new code imports it) and drop the
two additive `run_manifests` columns (or leave them — `readable_scope`/
`forbidden_scope` default to `'[]'` and are inert if unread by reverted
callers). `runtime_policy.yaml`'s `scope_budget_contracts` section can be
deleted independently of everything else in that file.

## Residual risk

- `verify_post_run_diff()` and `check_budget()` are standalone, callable
  primitives — like TASK-281 and TASK-282 before them, this task does not
  wire them into the live `submit_task()`/review gate (that would require
  editing `db/claims.py`/`scripts/map_task.py`, which are not TASK-283
  output paths) or into `graph/runner.py`'s dispatch loop (also not a
  TASK-283 output path). Actually blocking submission on an out-of-scope
  write, or halting a runner loop on budget exhaustion, is future work
  requiring its own task and independent review — consistent with every
  prior pilot task in this roadmap.
- The `pre_dispatch_policy.py` integration is the one part of this delivery
  that *is* live and load-bearing today, but only for tasks that opt in by
  declaring a `scope_contract` field — no currently-real task does.
