reviewer: /root/pr160_reviewer
head_sha: 988da5666cd5c3e8fc7a5b4a17db2c0b3eced082
independent: true
summary: APPROVED — PR #160 makes RecoverySupervisor.tick() the first real production caller of HarnessService.resume()/HcomHarnessAdapter.resume(), fail-open to the pre-existing direct hcom resume in every case except an explicit installed-and-denying CANONICAL_RUN Hook, with no task-truth mutation and no validation-tier or trigger-loop scope creep.

# Review: PR #160 RnS harness resume call site

- Task: `work/tasks/rns-harness-resume-callsite.md`
- Design: `work/notes/2026-08-21-rns-harness-validation-callsite-design.md`
- Reviewer: `/root/pr160_reviewer`
- Verdict: `APPROVED`

## Acceptance criteria check

- `PASS` — `RecoverySupervisor.tick()` routes resume through `HarnessService.resume()` when a binding can be constructed from existing lineage.
  - Evidence: `runtime/recovery/supervisor.py` diff (`ee7d14c..988da56`) shows `_resolve_harness_binding()` extracted (unchanged in substance) from the former shadow method, and `tick()`'s resume branch now calls `self.harness_service.resume(binding, session_ref)` when a binding resolves.
  - `tests.test_recovery_supervisor.RecoveryHarnessResumeCallSiteTests.test_successful_resume_routes_through_harness_adapter_not_direct_path` uses a *real* `HarnessService` + real `HcomHarnessAdapter` + real `CanonicalRunGuard` with a fake hcom backend wired only into the adapter, and a separate fake hcom wired as the direct-path double; asserts `harness_backend.resumes` got the call and `self.hcom.resumes == []`. This is a genuine distinguishing test, not tautological — see non-tautology check below.
- `PASS` — Explicit canonical-run denial (`HOOK_DENIED`/`APPROVAL_REQUIRED`) is observable in evidence without a fallback resume and without task-truth mutation.
  - Evidence: `_CANONICAL_DENIAL_CODES = {"HOOK_DENIED", "APPROVAL_REQUIRED"}`; on match, `action = "resume_denied"`, `resolved = True` (no direct-path fallback), `self.hcom.resumes == []` confirmed by `test_canonical_run_denial_surfaces_in_evidence_without_direct_fallback`. Only RnS's own incident-store bookkeeping (`attempt`, `state`, `next_attempt_at`, `last_error`) advances — grepped `runtime/recovery/supervisor.py` for `TaskStore`/`claim_task`/`submit_task`/`record_review`/`promote_ready`/`update_contract`/`INSERT INTO`/`UPDATE `/`sqlite`: zero hits.
- `PASS` — Missing/ambiguous binding preserves current direct-resume behavior unchanged.
  - Evidence: `_resolve_harness_binding()` returns `(None, None, reason)` for every lineage gap (no `run_id`, missing task, incomplete task binding, no lineage resolver, lineage not `EXPLICIT`, non-hcom adapter). `tick()` only sets `resolved = True` inside the `binding is not None` branch, so any of these reasons fall straight to the unchanged `self.hcom.resume(session_name, headless=True, go=True)` call. Confirmed by `test_missing_run_binding_falls_back_to_direct_resume` and `test_ambiguous_binding_falls_back_to_direct_resume`.
  - `CANONICAL_GUARD_REQUIRED` (harness attempted but no `CANONICAL_RUN` Hook installed) is also *not* in `_CANONICAL_DENIAL_CODES`, so it falls through to the same direct-resume fallback — confirmed by `test_missing_canonical_guard_falls_back_to_direct_resume` (`self.hcom.resumes` has 1 entry, action `"resume"`).
  - An exception raised by `harness_service.resume()` itself is caught (`except Exception ... HARNESS_CALL_ERROR`), also falls through to direct resume — confirmed by `test_harness_call_exception_falls_back_to_direct_resume`.
- `PASS` — No validation-tier wiring, no `EnvironmentSpec`, no report cache, no daemon/cron trigger loop, no new worker-loop entrypoint.
  - `git diff origin/main...HEAD | grep -inE "validation|run_validation_tier"` inside the real diff (merge-base `ee7d14c`, not the stale `origin/main` 2-commits-ahead comparison — see note below) has zero hits outside comment/task-doc prose referencing the design note's filename.
  - `tick()` is still only constructed/invoked by tests; unchanged, explicitly out of scope per both the design note and this task's own doc.
  - Source-level guard test `test_no_validation_tier_commands_or_task_mutation_in_source` grep-checks the actual `supervisor.py` source for `environmentspec`, `make_validation_hook`, `claim_task(`, `submit_task(`, `record_review(`, `promote_ready(`, `update_contract(` — none present.
- `PASS` — `HcomHarnessAdapter.resume()` / `HarnessService.resume()` signatures unmodified.
  - `git diff ee7d14c..988da56 -- runtime/harness/` is empty (0 lines) — confirmed directly.
- `PASS` — Full test suite passes.
  - `python3 -m unittest discover -s tests -v`: Ran 757 tests in 831.846s -- OK (skipped=6)

## Non-tautology check (design doc step 3 requirement)

Checked out parent commit `ee7d14c`'s `runtime/recovery/supervisor.py` in place (new test file kept) and re-ran the two most safety-critical new tests directly against old code:

- `test_successful_resume_routes_through_harness_adapter_not_direct_path` → **ERROR** (`KeyError: 'harness_resume'` — old code has no such evidence key at all, confirming the test exercises genuinely new behavior, not a restated assertion).
- `test_canonical_run_denial_surfaces_in_evidence_without_direct_fallback` → **FAIL** (`'resume' != 'resume_denied'` — old code silently resumed through the direct path on what the new code treats as an explicit denial).

Restored the PR's `supervisor.py` afterward; `git diff --stat` confirmed a clean working tree matching the PR head before running the full suite.

## Diff-scope note

`git diff origin/main -- runtime/harness/` is **not** a reliable proxy for this PR's actual change surface here: the PR branch (`988da56`) is 2 commits behind current `origin/main` (`efe2c8b`), so a straight diff against `origin/main` shows large unrelated deletions (`runtime/integrity/git_scope.py`, `runtime/run_record.py`, `work/reviews/pr-157/159-review-evidence.md`, worktree-binding task docs, etc.) that are purely a staleness artifact, not this PR's scope. Diffing against the actual merge-base (`ee7d14c`, `git merge-base origin/main HEAD`) gives the true 4-file change set: `runtime/recovery/supervisor.py`, `tests/test_recovery_supervisor.py`, `work/roadmaps/CAPABILITY_CHECKLIST.md`, `work/tasks/rns-harness-resume-callsite.md` — exactly the task doc's declared `MAY CHANGE` boundary, nothing more. No merge conflicts expected (touches none of the 2 commits main has since gained).

## Task doc Decisions section check

`work/tasks/rns-harness-resume-callsite.md`'s Decisions section gives explicit, non-vague answers to all 4 of the design note's open behavior questions:
1. CANONICAL_RUN denial handling — explicit code set, explicit action name, explicit no-mutation claim.
2. Missing/ambiguous binding — explicit "fail-open to existing behavior" with the specific `_resolve_harness_binding()` gap conditions enumerated.
3. Which lookup constructs the binding — explicit lineage chain (`incident["run_id"]` → `get_task()` → `compute_task_revision()` → `resolve_run_session(run_id)`), stated as unchanged extraction from the old shadow method.
4. Where results surface — explicit "recovery action evidence only... no Run Record coverage."

All four match what the code actually does (verified above), not just asserted.

## CAPABILITY_CHECKLIST.md honesty check

`git diff ee7d14c..988da56 -- work/roadmaps/CAPABILITY_CHECKLIST.md`: H4, H5, E4, 6.5 rows all remain `IN PROGRESS` (unchanged status), text updated only to note the new call site exists while explicitly stating validation-tier execution and a `tick()` production trigger loop remain separately-tracked, unstarted gaps. No row is marked `DONE` by this PR. No overclaiming found.

## Applicable review lenses

- `[x]` Functional / acceptance — traced every branch of the new `tick()` resume logic against the design note and task doc; ran targeted and full test suites; non-tautology check on 2 safety-critical tests against parent commit.
- `[x]` Security / trust boundary — confirmed `CANONICAL_RUN` denial is fail-closed (no fallback) and every other harness outcome is fail-open to pre-existing behavior, matching the design note's explicit "does not silently suppress a resume the direct path would have attempted unless the canonical-run guard has a concrete mismatch" contract.
- `[x]` Destructive / data-loss — confirmed no task-truth mutation surface touched (grep, zero hits); confirmed no daemon/cron/trigger-loop addition.
- `[x]` Authority / permission boundary — confirmed `HcomHarnessAdapter.resume()`/`HarnessService.resume()` themselves are byte-identical to `origin/main`/merge-base (empty diff under `runtime/harness/`).

## Findings

No blocking findings.

## Evidence checked

- Reviewed code head: `988da5666cd5c3e8fc7a5b4a17db2c0b3eced082`
- True merge-base: `ee7d14c5c10773f41c9dc8947804e258a619cab9` (2 commits behind current `origin/main` `efe2c8bb64ba736669d868e0fc7266c4aa302986` — see diff-scope note)
- `git diff ee7d14c..988da56 --stat` — 4 files, matches task doc's `MAY CHANGE` boundary exactly.
- `git diff ee7d14c..988da56 -- runtime/harness/` — empty.
- Non-tautology check: 2 new tests run against parent-commit `supervisor.py` (kept new test file), both fail as expected (see above); working tree restored and verified clean before full suite run.
- `python3 -m unittest tests.test_recovery_supervisor.RecoveryHarnessResumeCallSiteTests -v` — `OK`, 9 tests in 44.058s
- `python3 -m unittest discover -s tests -v` — Ran 757 tests in 831.846s -- OK (skipped=6)

## High-risk completion / release summary

Safety-critical recovery-path change (`RecoverySupervisor.tick()`, the automated resume path for RnS incidents). Verified: fail-closed only on an explicit, installed, actively-denying `CANONICAL_RUN` Hook; fail-open to unchanged legacy behavior for every other outcome including binding-construction failure, no-guard-installed, and harness-service exceptions. No task-truth mutation. No new trigger surface — `tick()` remains test-only invoked, same production-invocation gap as before, correctly left out of scope and correctly not claimed as closed anywhere in the PR (task doc, PR description, or checklist).

## Reviewer limits

- Missing context/evidence: none.
- New requirements discovered: none.
