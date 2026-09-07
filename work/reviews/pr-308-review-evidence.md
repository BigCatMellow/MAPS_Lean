# PR #308 review evidence

reviewer: reval-neso
head_sha: cc90de7c4bd58fbc393e202b0a87d1565376594b
independent: true
summary: Zero-diff revalidation after rebase onto main 17a6679. PR #308 touches runtime/cli.py which merged PR #306 also touched, so a naive OLD..NEW diff on cli.py is non-empty by design. Verified instead: (1) #308's own patch content lines are byte-identical pre/post rebase for runtime/cli.py, runtime/state/integrity.py, tests/test_execution_integrity.py (cli.py hunk-header line numbers shifted only from #306's earlier additions above the hunk; no +/- content line changed); (2) file end-state at rebased head is byte-identical to approved state 728ab26eca1080f8d2c88d2225f844e083654b5f for integrity.py, the test file, and work/tasks/require-worktree-binding-needs-base-revision.md; cli.py end-state legitimately carries #306's merged lines plus #308's own unchanged hunk. Task-doc conflict with #304 (new-file vs existing) resolved by taking #308's reviewed content, which matches byte-for-byte. Original APPROVE by maps-lean-vima stands.

## Non-involvement

I (maps-lean-vima) had no prior involvement with this work — not implementer,
not task author, not a participant in PR #303/#304 or Finding 0. First contact
with this change was this review.

## Method

Fresh clone to /tmp/rev308-*, git config BigCatMellow / noreply email, fetched
refs/pull/308/head (728ab26) and refs/pull/304/head. Verified every claim
against source, not the PR narrative.

## 1. Change boundary — CLEAN

`git diff c958cf6..728ab26 --name-only`:
- runtime/cli.py
- runtime/state/integrity.py
- tests/test_execution_integrity.py
- work/tasks/require-worktree-binding-needs-base-revision.md

No change to CanonicalRunGuard / runtime/policy/harness_guard.py / harness
lifecycle. No change to verify_git_run() payload keys or semantics. No
CAPABILITY_CHECKLIST.md change at all (task allowed at most a one-line pointer;
none added — acceptable).

## 2. The fix — CORRECT

`runtime/state/integrity.py::create_run_manifest`: new guard added BEFORE the
`if base_revision is not None:` block and BEFORE any DB connection / `BEGIN
IMMEDIATE`:

    if require_worktree_binding and base_revision is None:
        return MutationResult(False, "WORKTREE_BINDING_REQUIRES_BASE_REVISION",
            "require_worktree_binding needs base_revision (pass --base-revision) ...")

- No run manifest / state written on that path (early return precedes the
  transaction; new test asserts trace_task()[...] runs == []).
- Failure code `WORKTREE_BINDING_REQUIRES_BASE_REVISION` is greppable and the
  message names the `--base-revision` dependency explicitly.
- Pre-existing `WORKTREE_BINDING_REQUIRED` path (base_revision present but
  identity unreadable) is untouched.

## 3. Acceptance criteria — ALL MET

- flag standalone: now fails loud (was silent FLOW_STARTED + worktree:null).
  Covered by test_require_worktree_binding_without_base_revision_fails_loud (pass).
- flag + --base-revision <sha>: UNCHANGED. Still binds run_manifest.worktree.
  Existing test_required_worktree_binding_accepts_git_repo unchanged and passes;
  test_cli_flow_start_require_worktree_binding_exits_nonzero unchanged and passes.
- no flag, base_revision present AND absent: UNCHANGED. Covered by new
  test_no_worktree_flag_without_base_revision_still_succeeds_unbound (pass) plus
  existing coverage.
- --help text: `flow start` help for both --base-revision and
  --require-worktree-binding rewritten to state the companion requirement and
  name the failure code accurately.
- regression tests: all three cases covered (standalone loud / flag+base binds /
  no-flag unchanged).

## 4. Full suite — GREEN

python3 -m unittest discover -s tests -v > /tmp/rev308-suite.log 2>&1; echo $?
  => exit 0
  => Ran 1292 tests in 2523.477s / OK (skipped=6)
CI `test` job: pass (run 34018694699).
CI `review-evidence` job: was failing pre-this-commit (evidence file absent) —
this commit adds it.

## 5. No missed behavior-dependent caller

/usr/bin/grep -rn 'require.worktree.binding|require_worktree_binding' over repo +
work/: only test modules, review-evidence docs, task docs, and
runtime/integrity/README.md line 183 (which uses `--base-revision HEAD
--require-worktree-binding` together). No caller passes the flag standalone.

## 6. Non-blocking observations (NOT defects, no fix required)

- a) `runtime/integrity/cli.py` `run-create` subcommand also exposes
  `--require-worktree-binding` (+ a bare `--base-revision`); its help string
  ("fail run creation unless --repo has readable Git worktree identity") is now
  as stale/overstated as the one this PR fixed in `runtime/cli.py`. The
  *behavior* is fixed there too (same create_run_manifest code path — a
  standalone flag now returns WORKTREE_BINDING_REQUIRES_BASE_REVISION). Only the
  help text lags. The task's change boundary explicitly scoped MAY-CHANGE to
  `runtime/cli.py` and framed the goal around `maps flow start`, so leaving
  integrity/cli.py's help alone is within scope. Worth a one-line follow-up.
- b) The task doc work/tasks/require-worktree-binding-needs-base-revision.md is
  duplicated onto this branch (also present on PR #304's branch). Identical
  content; will resolve as a no-op / fast-forward at merge. Not blocking.

## Verdict

APPROVE. DO NOT MERGE (operator 3-day merge hold in force).
