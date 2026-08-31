# Task: Worktree binding guard enforcement

- Status: `IN REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: unassigned
- Risk: `MEDIUM`
- Goal: make an existing production dispatch guard fail closed when a run bound
  to a specific Git worktree is continued from a different worktree, without
  adding worktree creation, cleanup, changed-path enforcement, or merge
  authority.

## Inputs and source of truth

- Inputs:
  - `work/notes/2026-08-26-worktree-binding-enforcement-seam-design.md`
  - `work/notes/2026-08-24-worktree-run-binding-design.md`
  - `runtime/integrity/git_scope.py`
  - `runtime/integrity/__init__.py`
  - `runtime/policy/harness_guard.py`
  - `runtime/state/integrity.py`
  - `tests/test_runtime_review_hardening.py`
- Authoritative sources: the merged E6 design notes and current runtime code at
  `origin/main`.
- Evidence labels:
  - VERIFIED: `verify_git_run()`'s only non-test caller at `origin/main`
    `44ab61f` is `runtime/integrity/cli.py`'s `run-verify-git` subcommand.
  - VERIFIED: `CanonicalRunGuard` is registered under
    `HookEnforcement.CANONICAL_RUN` at `RUN_STARTING`, `BEFORE_SEND`,
    `BEFORE_RESUME`, and `SESSION_STOPPING`, and already fails closed on
    `check_run_stale()` with guard code `RUN_STALE`.
  - VERIFIED: `register_canonical_run_guards()` and `HarnessService(...)` have
    NO non-test callers; every registration/composition is in `tests/`. The
    CANONICAL_RUN layer is mandatory-when-composed but library-only today.
    Completing this task therefore closes the GUARD-LAYER gap only. It does
    NOT close E6's "enforcement in a real dispatch flow" gap, and no roadmap
    row may be marked `DONE` on that basis.
  - VERIFIED: `create_run_manifest()` leaves non-Git and
    placeholder-`base_revision` runs unbound; regression coverage is
    `test_non_git_placeholder_base_revision_remains_unbound`.
- Dependencies / preconditions: the design note above merged to `origin/main`.

## Change boundary

- MAY CHANGE:
  - `runtime/integrity/git_scope.py`
  - `runtime/integrity/__init__.py`
  - `runtime/policy/harness_guard.py`
  - `runtime/integrity/README.md`
  - `tests/test_runtime_review_hardening.py`
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` rows E6 and 6.16
  - this task file
- MUST NOT CHANGE:
  - `verify_git_run()`'s public payload keys or semantics
  - worktree creation, removal, or cleanup behavior
  - destructive Git commands
  - changed-path scope enforcement at harness lifecycle points
  - task ownership, review independence, or merge authority
  - RnS/recovery, Chain Shovel, or external target behavior
  - `SESSION_STOPPING` outcomes for this new check
- MAY CHANGE IF NECESSARY: adjacent guard tests documenting the same outcomes.
- OPERATOR APPROVAL REQUIRED: denying unbound runs, any automatic worktree
  mutation, or any authority change.

## Decision authority

- Owner may decide: helper and guard-code names, injection signature, test
  fixture shape, ordering among existing guard checks.
- Owner must escalate: any behavior that denies an unbound run; extending
  enforcement to changed-path scope; extending enforcement to
  `SESSION_STOPPING`.

## Acceptance criteria

- [ ] `compare_worktree_identity()` (or equivalent) exists in
      `runtime/integrity/git_scope.py` and is the single definition of worktree
      sameness.
- [ ] `verify_git_run()` uses it and its emitted payloads are unchanged.
- [ ] `CanonicalRunGuard` accepts an injectable worktree-identity source.
- [ ] Continuing operations (`start`/`send`/`resume`) on a bound run deny with
      `RUN_WORKTREE_MISMATCH` from a different worktree and
      `RUN_WORKTREE_UNAVAILABLE` when identity cannot be read.
- [ ] Unbound runs are still allowed.
- [ ] `SESSION_STOPPING` is not denied by this check.
- [ ] No worktree creation, cleanup, destructive Git repair, changed-path
      enforcement, or authority behavior is added.
- [ ] The roadmap update states that the composition-root gap remains open and
      does not mark E6 or 6.16 `DONE`.

## Verification and evidence

- Verification:
  - `git diff --check origin/main...HEAD`
  - `python3 -m py_compile runtime/integrity/git_scope.py runtime/integrity/__init__.py runtime/policy/harness_guard.py`
  - full suite as a blocking foreground call with output redirected to a file,
    not piped to `tail`, so the exit code is not masked:
    `python3 -m unittest discover -s tests -v > /tmp/worktree-guard-suite.log 2>&1; echo $?`
- Evidence to preserve: passing command output and review evidence.
- Review required: `INDEPENDENT_REVIEW` with mutation testing.

## Conditional execution rules

- Environment / target: local Git repositories and SQLite task DB.
- Ordered procedure: extract helper, refactor `verify_git_run()`, add guard
  injection, add `_require_bound_worktree()`, tests, README, roadmap.
- Failure branches: if worktree identity cannot be read for a bound run, deny;
  never fall back to the process current directory.
- Rollback / recovery: revert the branch; no destructive Git operation is used.
- Security / privacy controls: local absolute paths remain local runtime
  evidence only.
- External side effects: GitHub PR publication/merge only after review.
- Effort limit: this guard seam only.
- Approved reference:
  `work/notes/2026-08-26-worktree-binding-enforcement-seam-design.md`.

## Stop / escalate

Stop rather than guess if:

- the change would deny unbound or legacy runs;
- enforcement would require Git mutation;
- guard semantics would change task/review/merge authority.

Escalate to: operator or a follow-up design task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Completion / handoff

- Completed (branch `impl/worktree-binding-guard-20260831`, pending independent
  review with mutation testing):
  - `compare_worktree_identity()` + `WORKTREE_IDENTITY_FIELDS` added to
    `runtime/integrity/git_scope.py` as the single definition of worktree
    sameness; exported from `runtime/integrity/__init__.py`.
  - `verify_git_run()` refactored to call it; emitted payload keys
    (`reason`, `worktree_binding`, `worktree_mismatch.{expected,actual}_*`)
    unchanged — regression-tested in `tests/test_runtime_review_hardening.py`
    and `tests/test_execution_integrity.py`.
  - `CanonicalRunGuard.__init__` gained an injectable
    `worktree_identity` source (default `collect_git_worktree_identity`).
  - `_require_bound_worktree()` runs only on continuing operations
    (`start`/`send`/`resume`), after `_require_current_run()`: allows unbound
    runs, denies `RUN_WORKTREE_UNAVAILABLE` on unreadable identity, denies
    `RUN_WORKTREE_MISMATCH` on differing identity fields. `SESSION_STOPPING`
    is never gated by this check.
  - Coverage in `tests/test_harness_canonical_guard.py`
    (`WorktreeBindingGuardTests`): verified/mismatch/unavailable/unbound/stop.
  - `runtime/integrity/README.md` and `work/roadmaps/CAPABILITY_CHECKLIST.md`
    rows E6 + 6.16 updated; both state the composition-root gap remains open
    and neither row is marked `DONE`.
- Not completed: composition-root / real-dispatch-flow enforcement (E6(b)) —
  out of scope for this task by design.
- Current blocker: none; awaiting `INDEPENDENT_REVIEW` with mutation testing.
- Next action if not DONE: address independent-review findings.
