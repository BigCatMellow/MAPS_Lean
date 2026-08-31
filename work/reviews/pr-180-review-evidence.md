# Independent review evidence — PR #180

reviewer: independent-rebind-review-agent a7109cba25a2ee7f0 (did not author PR #180 or its prior review; isolated git worktree; original approval by a180f1a0f419bacb5 at 46785e8)
head_sha: 5591e220442d2c422dd1a0f2674e0cb2b7eaa0fd
independent: true
summary: APPROVE — head re-bound from 46785e8 to merge commit 5591e22 after two clean `origin/main` merges for branch protection. `git diff 46785e8 5591e22 -- runtime/` is empty; none of PR #180's 6 files differ (CAPABILITY_CHECKLIST.md untouched); every changed file between the two SHAs belongs to already-merged CI-green PRs #178/#179 (`docs/wiki/*`, `.claude/skills/pilot/*`, `AGENTS.md`, `playbook/*`, `templates/*`, `tools/digital_fungus.py`, `tests/test_documentation_sprawl.py`, `work/*`). CI `test` green on 5591e22 (run 33351456226, 58s). Local `python3 -m unittest tests.test_recovery_composition_root tests.test_recovery_production_trigger` → Ran 62 tests OK. Prior content review below stands unchanged. Original: APPROVE — the composition root matches the design note (§3b construction order, §3c CLI surface, §3d CanonicalRunGuard-only) and every §4 non-goal holds. Enforcement is default-off: `harness_service` stays `None` for every caller that does not pass `harness_project_id`, including the `maps claim` piggyback, so non-opted-in behavior is byte-identical. `--enforce-canonical-run` is a loud arg error without `--repo-root` (never infers cwd) and without `--harness-project-id`; `--repo-root` alone stays advisory-validation-only. Only 6 files touched — `runtime/recovery/supervisor.py`, `runtime/harness/`, and the policy guards are untouched. No CAPABILITY_CHECKLIST status label flipped to DONE. New tests prove opt-in routing through `HarnessService.resume()` with a full `ExecutionBinding` and default-off no-op; not vacuous. CI `test` is green on this head. Two non-blocking observations recorded below.

## Scope reviewed

`gh pr diff 180` at head `46785e8a5e1341925aeab5d84bdbfd91bb75f669` (`gh pr view 180 --json headRefOid`). Branch `impl/hook-harness-composition-root-20260830`, base `main`. Files touched (`gh pr view 180 --json files`), all inside the design/task change boundary:

- `runtime/cli.py` — two new `recovery-tick` flags + arg validation
- `runtime/recovery/production.py` — `build_canonical_harness_service` helper + one threaded keyword
- `tests/test_recovery_composition_root.py` (new)
- `tests/test_recovery_production_trigger.py` — source-guard update
- `work/roadmaps/CAPABILITY_CHECKLIST.md` — H5/E4/6.5/6.16 evidence text
- `work/tasks/hook-harness-composition-root.md` (new)

`runtime/recovery/supervisor.py`, `runtime/harness/` internals, `runtime/policy/harness_guard.py`, and `runtime/policy/destructive_action_guard.py` are **not** in the PR's file set — §4.3 and §4.4 hold mechanically.

Source of truth: `work/notes/2026-08-26-hook-enforcement-composition-root-design.md` (on main), §2c / §3b / §3c / §3d / §4.

## Verification against the design's non-goals (the checklist)

**1. `build_canonical_harness_service` location + construction order (§3b).**
It is a module-level helper in `runtime/recovery/production.py`, not a new module. Construction order matches §3b exactly:
`HcomHarnessAdapter(HcomAdapter(hcom_dir=…, executable=…, timeout_seconds=…), project_id=project_id, lineage_writer=task_reader)` → `HookRegistry()` → `register_canonical_run_guards(registry, CanonicalRunGuard(task_reader, repo_root=repo_root))` → `HarnessService([adapter], hooks=registry)`. `task_reader` is the caller's existing `TaskStore`, reused as `CanonicalRunSource` and as the adapter's `lineage_writer`. No second store is opened — `test_reuses_the_callers_store_as_the_canonical_run_source` also asserts `production.py` never names `TaskStore(`, which I confirmed by reading the file. The helper carries three extra optional `hcom_*` kwargs beyond the §3b signature sketch; these only thread the caller's existing hcom configuration through and introduce no new behavior — not a deviation of concern (non-blocking observation A).

**2. New keyword defaults `None` → byte-identical for non-opted-in callers (§3b).**
`run_recovery_tick` / `run_recovery_tick_isolated` gain one optional keyword `harness_project_id`, default `None`. When `None`, `harness_service` is `None` and `RecoverySupervisor(harness_service=None)` takes the pre-existing direct-`hcom.resume()` fallback. The `maps claim` piggyback at `runtime/cli.py` calls `run_recovery_tick_isolated(store, hcom_timeout_seconds=CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS)` — passes no new flags. `test_claim_piggyback_never_opts_into_enforcement` drives `maps claim` through the CLI and asserts the threaded `harness_project_id` is `None`. §4.7 holds.

**3. `--enforce-canonical-run` requires `--repo-root` and `--harness-project-id`; `--repo-root` alone stays advisory (§3c).**
`runtime/cli.py`'s `recovery-tick` branch: if `args.enforce_canonical_run` and not `args.repo_root` → `parser.error(...)` (exit 2, message names `--repo-root`, explicitly "never inferred from the current directory"). If enforce set and no `--harness-project-id` → `parser.error(...)`. `--repo-root` alone leaves `args.enforce_canonical_run` false, so `harness_project_id` stays `None` and only the advisory `RunBoundValidator` (PR #172) is constructed — PR #172's opt-in does not gain enforcement power. CLI tests `test_enforce_without_repo_root_exits_nonzero_with_a_clear_message`, `test_enforce_without_harness_project_id_exits_nonzero`, `test_repo_root_alone_stays_advisory_and_opts_into_no_enforcement`, `test_full_opt_in_threads_harness_project_id_through` all pin this. At the library level `run_recovery_tick(..., harness_project_id="proj-1")` with `validation_repo_root=None` raises `ValueError` (`test_harness_project_id_without_repo_root_is_a_loud_error`), and the isolated variant contains that error in its return payload rather than raising.

**4. Only `CanonicalRunGuard` registered — not `DestructiveExternalActionGuard` (§3d).**
`/usr/bin/grep -rn "DestructiveExternalActionGuard\|register_destructive\|DESTRUCTIVE_EXTERNAL_ACTION" runtime/` hits only `runtime/policy/destructive_action_guard.py` (definition + helper) and `runtime/policy/__init__.py` (re-export) — never `production.py`. The prior CI failure (a docstring naming that symbol) is fixed in `46785e8` as prose: `build_canonical_harness_service`'s docstring says "The destructive-external-action guard is intentionally not composed here" without naming the class as an identifier, and `tests/test_recovery_production_trigger.py`'s `HARNESS_COMPOSITION_SUBSTRINGS` guard would fail the build if it were re-introduced. `test_does_not_register_destructive_external_action_enforcement` asserts `has_enforcement(BEFORE_DESTRUCTIVE_ACTION/BEFORE_EXTERNAL_ACTION, DESTRUCTIVE_EXTERNAL_ACTION)` is `False` on the composed service.

**5. §4 non-goals hold.**
No daemon/scheduler/thread: `tests/test_recovery_production_trigger.py`'s `ALWAYS_FORBIDDEN_SUBSTRINGS` (`daemon`, `time . sleep`, `while true`) plus the import-pattern check still apply to both `production.py` and `cli.py`; `cli.py` additionally keeps the full `HARNESS_COMPOSITION_SUBSTRINGS` ban (it only parses flags, never constructs harness objects). No change to `tick()` decision logic / `_CANONICAL_DENIAL_CODES` / retry-backoff — `supervisor.py` is not in the diff at all; `production.py` supplies a non-`None` value to the `harness_service=` parameter that already existed. `CompositionRootSourceBoundaryTests.test_supervisor_source_untouched_by_the_composition_root` re-asserts the #160 source guard's forbidden substrings against `supervisor.py`. No `runtime/harness/` internal change. No new persistence (§4.5) — reuses `TaskStore`.

**6. Enforcement defaults OFF (§2c).**
`test_default_no_opt_in_constructs_no_harness_service_and_falls_back` captures the `RecoverySupervisor` kwargs, asserts `harness_service is None`, patches `build_canonical_harness_service` to raise if called, and confirms the direct-resume fallback actually executed (`backend.resumes` length 1, `action["harness_resume"]` is `None`). The design's rationale — `CanonicalRunGuard` never returns `ALLOW` and denies on absent evidence, so default-on would convert working resumes to `resume_denied`→`failed` — is why this matters; the guard file itself is unchanged by this PR (out of scope, already reviewed under PR #177).

**7. CAPABILITY_CHECKLIST.md H5/E4/6.5/6.16 (§4.8).**
All four rows keep their `IN PROGRESS` label. Evidence text is updated with a dated "Updated 2026-08-30" clause naming the new `build_canonical_harness_service` call site, stating default-off, and (H5) explicitly keeping the row open pending "the first real production exposure of an enforced pass" and design §5 Q4/Q5. No row flipped to DONE.

**8. New tests are not vacuous.**
`test_opt_in_routes_resume_through_harness_service_with_full_binding` builds a real bound run (task + contract + ready + claim + run manifest + adapter attach), schedules a due recovery, injects a `SpyHarnessService`, runs `run_recovery_tick(..., harness_project_id="proj-1", validation_repo_root=repo)`, and asserts the spy's `resume` was called exactly once with an `ExecutionBinding` whose `project_id` / `task_id` / `run_id` / `worker_id` / `task_revision` / `session_id` all match the bound lineage, plus `action["harness_resume"]["code"] == "SESSION_RESUMED"`. The default-off test (above) proves the no-op path. Both exercise `run_recovery_tick` end to end, not a mock of it.

## CI status

`gh pr checks 180`: `test` = **pass** (run 33349275410, ~1m20s) on head `46785e8`. `review-evidence` currently fails (no evidence file yet) — this commit is what makes it pass.

## Local targeted test runs

- `python3 -m unittest tests.test_recovery_composition_root` → `Ran 13 tests ... OK`.
- `python3 -m unittest tests.test_recovery_production_trigger` → `Ran 49 tests ... OK` (includes the updated `test_no_daemon_scheduler_or_hook_machinery_in_trigger_source` source guard).

(`pytest` is not installed in this environment; the repo uses `unittest`. The full suite was not re-run locally — CI already ran it green on this head, cited above.)

## Non-blocking observations

**A.** `build_canonical_harness_service` accepts `hcom_dir` / `hcom_executable` / `hcom_timeout_seconds` beyond the §3b signature sketch. These only forward the caller's existing hcom config and default to the module `DEFAULT_*` constants, so behavior is unchanged; worth noting only because the design's shape block does not show them.

**B.** `--harness-project-id` supplied *without* `--enforce-canonical-run` is silently ignored (the enforce flag gates the whole block, so `harness_project_id` stays `None`). This is safe — it preserves default-off — but a user who passes only `--harness-project-id` expecting it to take effect gets no warning. A future `parser.error` on that combination would be friendlier. Not blocking: the design's §5 Q2 explicitly leaves the per-flag vs per-mode split as "a taste call", and the safe direction was chosen.

## Verdict

**APPROVE.** The implementation is the minimum-viable composition root the design specifies, every non-goal is checkable and holds, enforcement is default-off with a loud multi-flag opt-in, and the supervisor / harness / guard internals are untouched. The two observations above are cosmetic and do not block merge.
