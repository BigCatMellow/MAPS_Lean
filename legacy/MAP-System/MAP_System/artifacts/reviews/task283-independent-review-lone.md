# Review: TASK-283 Independent Review

- task_id: TASK-283
- reviewer: helper-review-task-283-lone
- task_owner: command-center
- submitter: claude-lab-venu
- reviewed_at: 2026-07-27
- review_claim: `claim_review("TASK-283", "helper-review-task-283-lone")`
- tier escalation: sonnet, per `MAP_System/inbox/helpers/helper-review-task-283.md` (codex-lab-diro flagged the live-dispatch-path stakes; approved under operator delegation, reported to bigboss)

## Verdict

APPROVED

The delivery is honest, tested, and safe. The one part of this change that is
actually load-bearing today -- the `pre_dispatch_policy.py` preflight
integration -- is correct, additive, and independently confirmed to leave
every task without a `scope_contract` field byte-for-byte unaffected. The
`run_manifests` schema migration is safe against pre-existing rows (verified
by direct reproduction, not just by reading the shipped test). The
`runtime_policy.yaml` addition is confirmed inert to all four other named
consumers by reading each consumer's actual parsing code, not by trusting the
delivery note's claim. Two acceptance criteria (3 and 4) are PARTIAL rather
than PASS: the post-run-diff and budget-exhaustion primitives are correct and
tested but are not yet called from any live submission or retry path. This
gap is explicitly disclosed in the delivery note's "Residual risk" section
and matches the precedent already accepted for TASK-281/TASK-282 in this same
roadmap, so it is a scope note, not a defect -- documented below as a
RECOMMENDED follow-up, not a blocker.

## Acceptance Criteria Check

| # | Result | Evidence |
|---|--------|----------|
| 1 | PASS | `run_manifest.py`'s `create_manifest()` now threads `readable_scope`/`writable_scope`/`forbidden_scope` plus `max_attempts`/`max_tool_failures`/`runtime_seconds` (as `runtime_limits`) into every manifest row. Verified live: `test_manifest_records_readable_writable_and_forbidden_scope`, `test_manifest_scope_defaults_when_not_supplied` both pass. |
| 2 | PASS | `evaluate_pre_dispatch()` calls `scope_contract_issues()` immediately after the tier-0 early return, before any tier-specific branch (`pre_dispatch_policy.py:357-363`), and rejects for every tier above 0 (`test_task_with_invalid_scope_contract_is_rejected_regardless_of_tier` exercises tiers 1/2/3; `test_command_center_tier_bypasses_scope_contract_check` confirms tier 0 is exempt by design, consistent with every other check in the file). `validate_scope_contract()` independently confirmed to reject overlap, escape, and readable/writable mismatch cases (see "Independent verification" below). |
| 3 | PARTIAL | `verify_post_run_diff()` correctly *detects* out-of-scope and forbidden writes given a caller-supplied changed-paths list (confirmed by direct testing, see below). It does **not** currently block submission: `grep -rn "verify_post_run_diff" MAP_System --include="*.py"` outside `verify_run_scope.py`/`test_run_scope.py` returns zero hits -- nothing in `db/claims.py`, `scripts/map_task.py`, or `graph/runner.py` calls it. The delivery note discloses this explicitly under "Residual risk." The literal AC wording ("blocks submission until...") is not yet true of the running system. |
| 4 | PARTIAL | `check_budget()`/`write_escalation_artifact()` correctly detect budget exhaustion and write a durable JSON record (confirmed by direct testing). Same gap as AC3: zero live callers found outside the new module and its own test file -- `agent_loop.py`'s retry cycle does not invoke `check_budget()`. An actual unbounded retry loop is still possible today; only the capability to stop one exists. Disclosed in the delivery note, consistent with TASK-281/282 precedent. |
| 5 | PASS | The three-tier distinction (prompt guidance / preflight+post-run detection / genuine harness containment) is stated identically and consistently across the module docstring, the delivery note, and `runtime_policy.yaml`'s inline comment. `containment_level: preflight_reject_and_post_run_diff_detection` is explicitly not `harness_enforced`, and `test_load_scope_policy_reads_the_real_runtime_policy_yaml` asserts `containment_level != "harness_enforced"` as a regression guard. `grep`ed the whole repo for `containment_level`/`scope_contract` outside this task's own files -- only `MAP_System/inbox/helpers/helper-review-task-283.md` (this review's own intake note) references them, so there is no other surface where a careless reader could pick up an inflated claim. |

## Reproduce, Don't Trust -- Independent Verification

- **`evaluate_pre_dispatch()` before/after identity for tasks without `scope_contract`:** read the actual insertion point in `pre_dispatch_policy.py` (lines 357-363) -- `scope_contract_issues(task)` returns `[]` when `task.get("scope_contract")` is absent (line 316: `if not contract or not isinstance(contract, dict): return []`), so `contract_issues` is always `[]` and `if contract_issues:` never fires. No other line in the function was touched (confirmed by reading the full file, not just the diff hunk). Behavior for the ~277 real tasks in `map.db` is provably unchanged, not merely asserted.
- **`runtime_policy.yaml` consumer inertness**, read each consumer directly rather than trusting the claim:
  - `graph/runner.py:191` -- `runtime_policy = policy.get("runtime_policy", {})` (top-level key only; `scope_budget_contracts` is a sibling key, never read).
  - `scripts/halt_state.py:111-112` -- `runtime_policy = data.get("runtime_policy", data)` (same top-level-key-only pattern).
  - `scripts/multigate_regression_test.py` -- only passes the file *path* string into `app.invoke()`; parsing is delegated to `graph/runner.py`'s `load_runtime_policy`, already confirmed inert above.
  - `scripts/task_fingerprint_holdout.py:64` -- classifies by filename only (`name == "runtime_policy.yaml"`), never parses YAML content.
  - All four confirmed inert by reading their code, not by re-running the submitter's claim.
- **`run_manifests` ALTER TABLE migration safety:** built a standalone SQLite DB with the *original* TASK-281 schema (no `readable_scope`/`forbidden_scope` columns) and inserted a live-shaped row, then called `run_manifest.py`'s `connect()` directly. Result: both columns added via `ALTER TABLE ... ADD COLUMN ... DEFAULT '[]'`, pre-existing row fully intact with sane defaults for the new columns, no data loss. This reproduces (not just trusts) `test_pre_existing_run_manifests_table_migrates_additive_columns`.
- **`verify_post_run_diff()` / `check_budget()` correctness:** read the implementation and ran the shipped unit tests, which cover overlap-both-directions, path-escape, empty-path, and readable/writable-mismatch cases for the contract validator; out-of-scope, forbidden, and clean-diff cases for the post-run check; within-limit, exceeded, and undeclared-limit cases for the budget check. All match the module's own stated scope.

## Test Run (Independent Execution)

```
MAP_System/.venv/bin/python MAP_System/tests/test_run_scope.py            -> 25/25 PASS
MAP_System/.venv/bin/python MAP_System/tests/test_run_manifest.py         -> 10/10 PASS
MAP_System/.venv/bin/python MAP_System/tests/test_pre_dispatch_policy.py  -> 10/10 PASS, no FAIL
MAP_System/.venv/bin/python MAP_System/tests/test_pre_dispatch_gate_inputs.py -> 15/15 PASS
MAP_System/.venv/bin/python MAP_System/tests/test_capability_whitelist.py -> 10/10 PASS, no FAIL
```

No behavior change detected in any pre-existing test in the last three suites.

## Files Reviewed

- `MAP_System/artifacts/tests/task283-scope-budget-delivery-note.md` (full read)
- `MAP_System/scripts/pre_dispatch_policy.py` (full read, insertion point traced line-by-line)
- `MAP_System/scripts/verify_run_scope.py` (full read, new file)
- `MAP_System/tests/test_run_scope.py` (full read, all 25 tests)
- `MAP_System/workflow/runtime_policy.yaml` (full read, additive section)
- `MAP_System/scripts/run_manifest.py` (full read, `connect()`/`create_manifest()` traced)
- `MAP_System/migration/run_manifest_schema.sql` (full read)
- `MAP_System/graph/runner.py`, `MAP_System/scripts/halt_state.py`, `MAP_System/scripts/multigate_regression_test.py`, `MAP_System/scripts/task_fingerprint_holdout.py` (read the relevant `runtime_policy` parsing sections of each)
- `MAP_System/tasks/TASK-283.json` (acceptance criteria, output_paths)

## Forbidden Changes Check

Used output_paths + mtime comparison, not `git diff` (this repo has unrelated
uncommitted work since 2026-07-15/23 that makes `git diff` misleading, per
this helper packet's process note).

- Compared TASK-283's registered `output_paths` (7 files) against the exact
  files touched in the 2026-07-27 14:38-14:46 mtime window:
  `run_manifest_schema.sql`, `verify_run_scope.py`, `run_manifest.py`,
  `runtime_policy.yaml`, `pre_dispatch_policy.py`, `test_run_scope.py`,
  `task283-scope-budget-delivery-note.md` -- exact 1:1 match, no extra files.
- Other files with mtimes in the same broad window (`task286-*`,
  `context_rotation.py`, `test_context_rotation.py`,
  `workstream_digest_pilot.py`, `task285-*`, `emergence_sentinel.py`) belong
  to other tasks (TASK-285/286 and unrelated work) and are outside TASK-283's
  window and output_paths -- not a TASK-283 forbidden change.
  `__pycache__/*.pyc` entries are test-run byproducts (both the submitter's
  and this review's), not source changes.
  `workflow/task_graph.json`'s 14:46 mtime is this review's own
  `claim_review()` call updating the mirror, not a submitter change.
- PASS: no forbidden or out-of-scope changes found.

## RECOMMENDED Follow-up (non-blocking)

Open a follow-on task to wire `verify_post_run_diff()` into the actual
submission gate (`db/claims.py`/`scripts/map_task.py`) and `check_budget()`
into `graph/runner.py`'s dispatch loop or `scripts/agent_loop.py`'s retry
cycle, so AC3/AC4 become true of the live system rather than true only of
callable primitives. This is the same residual gap TASK-281 and TASK-282 left
open; it is reasonable for TASK-283 to leave it open too, but the roadmap
should not let it go open indefinitely across three consecutive tasks
without a tracked follow-up.
