# PR #185 review evidence

reviewer: independent-reviewer-ace9b0d0
head_sha: 57382a01f0a6a78ac9ef07276dc782ff9a4d06df
independent: true
summary: APPROVE - scope clean, verify_git_run payloads unchanged and regression-tested, all 5 required mutations caught (5/5), composition-root gap correctly left open and no row marked DONE.

## Method

- `git diff origin/main...HEAD --stat`: 9 files, all within the task doc MAY CHANGE
  list (`tests/test_harness_canonical_guard.py` covered by "MAY CHANGE IF NECESSARY:
  adjacent guard tests" and named in the design note). No worktree
  creation/removal/cleanup, no destructive Git, no changed-path scope enforcement,
  no authority/ownership/review/merge change.
- `git diff --check` clean; `py_compile` clean.
- Baseline: `tests.test_harness_canonical_guard tests.test_runtime_review_hardening
  tests.test_execution_integrity` -> 53 tests OK.
- Payload stability: `verify_git_run()` mismatch path now delegates dict
  construction to `compare_worktree_identity()`; keys (`reason`,
  `worktree_binding`, `worktree_mismatch.{expected,actual}_<field>`) and values
  byte-for-byte identical. Regression test
  `test_verify_git_run_worktree_mismatch_payload_is_stable_after_refactor` asserts
  exact key set AND values; `test_git_scope_verifier_rejects_different_clone_before_scope_check`
  also covers it. Not weak.
- Design fidelity: `_require_bound_worktree()` is called from `__call__` under the
  same `continuing` predicate, immediately after `_require_current_run()`, as the
  seam design specifies. Guard codes `RUN_WORKTREE_MISMATCH` /
  `RUN_WORKTREE_UNAVAILABLE` match the design. `collect_git_worktree_identity`
  raises only `RuntimeError` (via `_git`), so the `except RuntimeError` is
  comprehensive for git-command failure.

## Mutation testing: 5/5 caught

Each mutation applied in the review worktree, one blocking foreground unittest
run, exit code recorded, reverted before the next.

1. invert comparison in `compare_worktree_identity()` (`if any` -> `if not any`)
   -> FAILED (failures=7), exit=1. CAUGHT.
2. `_require_bound_worktree()` returns allow on unreadable identity for a bound
   run (`except RuntimeError: return None`) -> FAILED (failures=1,
   `test_unreadable_worktree_identity_is_denied`), exit=1. CAUGHT.
3. also fire the check on `SESSION_STOPPING` (call added under `session_bound`)
   -> FAILED (failures=1, `test_session_stopping_is_not_denied_by_worktree_check`),
   exit=1. CAUGHT.
4. deny unbound runs (`if not isinstance(expected, Mapping): return self._deny(...)`)
   -> FAILED (failures=9), exit=1. CAUGHT.
5. remove the `_require_bound_worktree()` call from the guard entirely
   -> FAILED (failures=3), exit=1. CAUGHT.

Post-revert `git status` clean.

## Verdict

APPROVE. Non-blocking notes only (see PR comment): mismatch is tested on
`start`/`resume` but not `send`, and `RUN_WORKTREE_UNAVAILABLE` only on `send`;
the guard treats all three continuing ops via one predicate so coverage is
adequate. `FileNotFoundError` (git binary absent) is not caught by
`except RuntimeError` and would propagate rather than deny cleanly.

The composition-root / real-dispatch-flow gap (E6(b)) remains OPEN; the roadmap
rows E6 and 6.16 were updated in this PR, state the gap explicitly, and neither
is marked `DONE`.

<!-- review re-verified; CI retrigger -->
