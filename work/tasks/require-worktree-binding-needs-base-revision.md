# Task: `--require-worktree-binding` is inert without `--base-revision`

- Status: `READY`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: unassigned
- Risk: `LOW` (small, localized fix in one function + one CLI help string; no
  authority, no destructive path, no harness lifecycle change)
- Goal: make `maps flow start --require-worktree-binding` behave as its own
  `--help` text claims — it must either bind a Git worktree identity / fail run
  creation loudly when standalone, **or** its `--help` must state plainly that
  `--base-revision` is a required companion flag and run creation must fail
  loudly (not silently succeed with `worktree: null`) when it is passed alone.
- Parent roadmap: row 6.16 (Git worktree isolation) in
  `work/roadmaps/CAPABILITY_CHECKLIST.md` — this bug was surfaced *during* that
  row's closing exercise (PR #303) but is explicitly **not** part of what 6.16
  proves; it is a separate usability/correctness gap.
- Related records:
  - `work/notes/2026-09-05-dec003-row-6.16-worktree-binding-guard-exercise.md`
    — "Finding 0", where this was first diagnosed in source.
  - `work/reviews/pr-303-review-evidence.md` — reviewer `luna` independently
    confirmed Finding 0 against `runtime/state/integrity.py::create_run_manifest`
    and agreed it should be spun out, not fixed in PR #303.
  - `feedback_require_worktree_binding_needs_base_revision.md` (coordinator
    memory) — same finding, PR #303 "Finding 0".
  - PR #261 — its exercise run recorded `worktree: null`; this bug is the
    likely cause.
- Autonomous continuation: `YES`

## Inputs and source of truth

- `runtime/state/integrity.py::create_run_manifest` — authoritative. The whole
  worktree-identity-collection block (the `collect_git_worktree_identity`
  call **and** the `require_worktree_binding` → `WORKTREE_BINDING_REQUIRED`
  failure branch) is nested under `if base_revision is not None:`. When
  `base_revision is None`, `require_worktree_binding` is never consulted.
- `runtime/cli.py` — the `flow start` argument definitions: `--base-revision`
  is a bare arg with no help text; `--require-worktree-binding`'s help text
  ("fail run creation unless repo-root has readable Git worktree identity")
  overstates the standalone effect. Read these directly; do not guess line
  numbers — they drift.
- Evidence labels: the gating behavior above is VERIFIED (read in source by
  the PR #303 author and re-verified by reviewer `luna`). Any claim about how
  many existing callers pass `--require-worktree-binding` without
  `--base-revision` is ASSUMED until grepped.
- Dependencies / preconditions: none — PR #303 is independent; this fix does
  not depend on it merging.

## Change boundary

- MAY CHANGE:
  - `runtime/state/integrity.py` (`create_run_manifest` gating logic only)
  - `runtime/cli.py` (`flow start` help text for `--require-worktree-binding`
    and/or `--base-revision`; argument-validation wiring if the chosen fix
    rejects the flag combination at the CLI layer)
  - the relevant test module(s) for `create_run_manifest` /
    `flow start` argument handling
  - this task file
- MUST NOT CHANGE:
  - `CanonicalRunGuard` / `runtime/policy/harness_guard.py` or any harness
    lifecycle behavior
  - `verify_git_run()` payload keys or semantics
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` row 6.16 evidence text beyond, at
    most, a one-line pointer that this follow-up landed (row 6.16's status is
    already resolved and is not this task's concern)
  - worktree creation / cleanup / destructive Git behavior
  - task ownership, review independence, or merge authority
- MAY CHANGE IF NECESSARY: adjacent tests that assert the old silent-no-op
  behavior (update them to assert the new loud behavior).
- OPERATOR APPROVAL REQUIRED: only if the chosen fix would reject a flag
  combination that existing dispatched tasks/scripts already rely on (grep
  first; if there are such callers, escalate before changing behavior).

## Decision authority

- Owner may decide: which of the two acceptable end states to implement
  (make the flag work standalone by collecting worktree identity whenever
  `require_worktree_binding` is set, **or** fail loudly + fix the help text),
  the new failure code/message string, test fixture shape.
- Owner must escalate: any change that alters run-manifest schema for runs
  that today succeed; any change that would make a currently-passing dispatch
  flow start fail.
- Resolve internally first: exact CLI arg-parser mechanics — read
  `runtime/cli.py`.

## Acceptance criteria

- [ ] `maps flow start --require-worktree-binding` **without** `--base-revision`
      no longer silently returns `FLOW_STARTED` with `worktree: null`: it
      either (a) collects and binds a real worktree identity, or (b) fails run
      creation with an explicit, greppable code/message naming the missing
      `--base-revision` dependency.
- [ ] `maps flow start --require-worktree-binding --base-revision <sha>`
      behavior is unchanged (still binds `run_manifest.worktree`).
- [ ] `maps flow start` **without** `--require-worktree-binding` behavior is
      unchanged for both `base_revision` present and absent.
- [ ] The `--require-worktree-binding` (and, if relevant, `--base-revision`)
      `--help` text accurately describes the flag's real effect and any
      companion-flag requirement.
- [ ] Regression test covers: flag-standalone (new loud behavior),
      flag+base-revision (binds), no-flag (unchanged).
- [ ] No change to `CanonicalRunGuard`, `verify_git_run()` payloads, or any
      harness lifecycle outcome.

## Verification and evidence

- Verification:
  - `python3 -m py_compile runtime/state/integrity.py runtime/cli.py`
  - full suite as a blocking foreground call, output redirected to a file so
    the exit code is not masked by a pipe:
    `python3 -m unittest discover -s tests -v > /tmp/rwb-suite.log 2>&1; echo $?`
  - a manual `maps flow start --require-worktree-binding` (no `--base-revision`)
    against a throwaway clone, output captured, showing the new loud behavior.
- Evidence to preserve: passing suite output, the manual command transcript,
  and `work/reviews/pr-<N>-review-evidence.md`.
- Review required: `INDEPENDENT_REVIEW` (self-authored; owner not eligible).
  Reviewer must be independent of this task's implementer.

## Conditional execution rules

- Environment / target: fresh `git clone` to a UNIQUE `/tmp/<tag>-$$/` path,
  never the coordinator checkout or `.claude/worktrees/`. Standard git config
  (`user.name "BigCatMellow"` / matching noreply email).
- Ordered procedure: (1) grep the repo + recent dispatch docs for callers
  passing `--require-worktree-binding` without `--base-revision`; (2) pick the
  end state (escalate if step 1 found behavior-dependent callers); (3) change
  `create_run_manifest` gating and/or CLI validation; (4) fix help text;
  (5) tests; (6) run the full suite as a blocking foreground call.
- Failure branches: if the fix would break an existing passing dispatch flow,
  STOP and hand back to the coordinator with the caller list.
- Rollback / recovery: revert the branch; no persistent state, no destructive
  Git operation.
- Security / privacy controls: local absolute paths in worktree identity stay
  local runtime evidence only.
- External side effects: GitHub PR publication only; **do not merge** — merges
  are on a hold window; open the PR and let it queue for review.
- Effort limit: this one function's gating + the CLI help/validation and its
  tests. Do not expand into worktree-creation or guard work.

## Stop / escalate

Stop rather than guess if:

- existing dispatched tasks/scripts rely on the current silent behavior;
- the fix appears to need a run-manifest schema change;
- the two acceptable end states both look wrong for a case you find.

Escalate to: the coordinator (not the operator directly) for the retry-vs-
reshape decision; operator only if a behavior-dependent caller forces a
compatibility break.

## AGI readiness

- Fresh-Agent Test: `PASS` — the bug, its root cause (one `if` gate), the file,
  and the two acceptable end states are all named.
- No-Guess Test: `PASS` — source of truth is one function; line numbers
  explicitly deferred to a direct read.
- Scope Test: `PASS` — MAY/MUST NOT lists are concrete.
- Authority Test: `PASS` — escalation trigger (behavior-dependent callers) is
  named.
- Completion Test: `PASS` — acceptance criteria are checkable commands.
- Failure Test: `PASS` — failure branches and stop conditions listed.
- Continuation Test: `PASS` — autonomous continuation YES; hand-back target is
  the coordinator.

## Completion / handoff

- Not started. Created 2026-09-06 from PR #303's Finding 0 as a downstream
  spin-out; the PR #303 exercise itself did not fix this (change boundary).
- Next action: assign an implementer independent of the PR #303 author
  (`zara`) and reviewer (`luna`).
