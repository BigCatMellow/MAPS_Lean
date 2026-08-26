# Worktree binding enforcement seam design

Date: 2026-08-26
Owner: `/root`
Status: design complete; no runtime behavior changed

## Why this note exists

`work/notes/2026-08-24-roadmap-trajectory-check-7.md` §5b item 4 recorded an
open question against roadmap 6.16 / E6:

> #157 merged this arc — `verify_git_run()`'s mismatch path exists and is
> tested but still not proven wired into a real production dispatch flow.
> Re-verify a real call site invokes it before calling E6 closer to done.

This note answers that question with evidence, and defines the enforcement seam
that would close it. It does not change runtime behavior.

## Finding: pass #7's conservative read was correct

VERIFIED at `origin/main` `44ab61f`:

- `runtime/integrity/git_scope.py::verify_git_run()` is exported from
  `runtime/integrity/__init__.py`.
- Its only non-test importers are:
  - `runtime/integrity/cli.py`, which calls it from the `run-verify-git`
    subcommand (`return emit(verify_git_run(store, args.run_id,
    repo_root=args.repo))`), documented at `runtime/integrity/README.md:173`;
  - nothing else.
- Its only other callers are tests: `tests/test_execution_integrity.py`
  (including `test_git_scope_verifier_rejects_different_clone_before_scope_check`,
  which covers the mismatch path) and `tests/test_runtime_review_hardening.py`.

So the `worktree_mismatch` / `worktree_unavailable` payloads added by PR #157
are reachable in production only when a human or agent explicitly runs
`python -m runtime.integrity.cli run-verify-git`. They are not consulted by any
lifecycle flow, guard, or dispatch path.

This is not dead code — the CLI is a real production entry point — but it is
advisory-on-request, not enforced. The distinction matters for E6, whose gap is
precisely that a *concurrent* agent working in the wrong worktree is not
detected unless someone remembers to ask.

### Contrast: the sibling verifier reaches a guard; neither reaches a composed dispatch flow

The comparable staleness verifier gets one layer further than worktree identity:

- `runtime/state/integrity.py::TaskStore.check_run_stale()` is consumed by
  `runtime/policy/harness_guard.py::CanonicalRunGuard._require_current_run()`,
  which returns a `DENY` with `guard_code` `RUN_STALE`. `__call__` gates that
  check behind `continuing`, so it applies to `start` / `send` / `resume` only,
  not to `stop`.
- `register_canonical_run_guards()` registers `CanonicalRunGuard` under
  `HookEnforcement.CANONICAL_RUN` at `HookEvent.RUN_STARTING`, `BEFORE_SEND`,
  `BEFORE_RESUME`, and `SESSION_STOPPING`, and
  `runtime/harness/service.py::_require_canonical_enforcement()` makes the
  layer mandatory once a `HarnessService` is composed with it.

VERIFIED, and important to state plainly so this note does not repeat the
overstatement it exists to correct: `register_canonical_run_guards()` and
`HarnessService(...)` have **no non-test callers** in the repo. Every
registration and composition is in `tests/`. The CANONICAL_RUN layer is
therefore library-only — mandatory-when-composed, but nothing in-repo composes
it into a running dispatch flow.

So E6's enforcement gap is two-layered, and this note addresses only the first:

1. **Guard layer.** `check_run_stale()` is consulted by a fail-closed guard;
   worktree identity is not consulted by anything but an on-request CLI. This
   asymmetry is real and is what the follow-up task closes.
2. **Composition-root layer.** No production code constructs a `HarnessService`
   with these guards, so no lifecycle enforcement of *any* canonical run
   evidence is live today. The follow-up task does **not** close this, and must
   not claim to.

Worktree identity is the one piece of run evidence PR #157 added that never
reached the guard layer. Closing that is a real, bounded step; it is not the
same as proving enforcement in a running dispatch flow.

## Why this was not wired directly in this pass

Wiring is one function call, but it crosses two boundaries the merged E6 task
document explicitly reserves for escalation
(`work/tasks/run-worktree-binding.md`, "Decision authority" and
"Stop / escalate"):

- "failure semantics that would block legacy/unbound runs automatically" must be
  escalated by the owner;
- stop rather than guess if "verifier semantics would change task/review
  authority".

A new `DENY` inside a mandatory `HookEnforcement.CANONICAL_RUN` guard is exactly
such a failure semantic: it can block a real dispatch. Three specific hazards
make the naive wiring wrong:

1. **`verify_git_run()` is too broad for this seam.** Beyond comparing worktree
   identity it calls `collect_git_changes()` (a `git diff` plus
   `git ls-files --others`) and then `store.verify_run_changes()`. Calling it
   from `BEFORE_SEND` would run two Git subprocesses on every message and would
   also deny on *out-of-scope changed paths* — a much larger authority
   expansion than worktree binding, and one E6's checklist row explicitly
   disclaims.
2. **Unbound runs must not be denied.** `create_run_manifest()` deliberately
   leaves non-Git and placeholder-`base_revision` runs unbound (regression test
   `test_non_git_placeholder_base_revision_remains_unbound`). A guard that
   treats "no binding" as failure would break every legacy fixture and any
   non-Git run.
3. **`CanonicalRunSource` has no Git capability.** The guard's `Protocol` today
   exposes only store reads. Reading worktree identity means the guard performs
   Git I/O, which needs an explicit, injectable, failure-tolerant seam rather
   than an inline subprocess call.

None of these is hard, but together they make the call site consequential rather
than obvious, which is what a design note is for.

## Decision: a narrow identity-only guard check

Recommended shape for the follow-up implementation.

### 1. Factor the comparison, do not duplicate it

Extract the identity comparison already inlined in `verify_git_run()` into a
shared read-only helper in `runtime/integrity/git_scope.py`, e.g.:

```python
WORKTREE_IDENTITY_FIELDS = (
    "repo_root", "git_common_dir", "git_dir", "worktree_private_dir",
)

def compare_worktree_identity(expected, actual) -> dict:
    """Return {"status": "match"|"mismatch", "worktree_mismatch": {...}}."""
```

`verify_git_run()` must be refactored to call it so there is exactly one
definition of "same worktree". Do not write a second comparison in the guard.

### 2. Add an explicit, optional Git-identity source to the guard

Give `CanonicalRunGuard` an injected callable rather than importing Git I/O
directly, so tests and non-Git deployments stay simple:

```python
def __init__(self, source, *, repo_root, now=utc_now,
             worktree_identity=collect_git_worktree_identity): ...
```

### 3. Fail closed only for bound runs

New `_require_bound_worktree(manifest)`, called from `__call__` only when
`continuing` is true (`start` / `send` / `resume`) — the same predicate that
already gates `_require_current_run()`:

- `manifest.get("worktree")` is not a mapping → return `None` (allow).
  Unbound is a coverage gap, not a failure. This preserves every existing
  fixture and non-Git run.
- identity read raises `RuntimeError` → `DENY` with guard code
  `RUN_WORKTREE_UNAVAILABLE`.
- fields differ → `DENY` with guard code `RUN_WORKTREE_MISMATCH`.
- fields match → `None`.

Ordering: place it after `_require_current_run()`. Cheapest checks first, and a
stale run should still report `RUN_STALE`.

### 4. Do not touch `SESSION_STOPPING`

Denying a stop because the worktree moved would strand sessions. Enforcement
belongs on the continuing operations only.

### 5. Cost

`collect_git_worktree_identity()` spawns five `git rev-parse` invocations
(`--show-toplevel`, `--git-common-dir`, `--git-dir`, `--git-path .`, and
`--verify HEAD^{commit}`). That is not free, but it is still materially cheaper
than `verify_git_run()`, which adds `collect_git_changes()`'s `git diff` and
`git ls-files --others` on top of those same five plus scope evaluation. The
comparative argument for calling the helper rather than the full verifier holds;
the absolute cost is higher than a naive reading suggests, so the implementer
should not treat the guard check as free.

## Non-goals

Unchanged from `work/notes/2026-08-24-worktree-run-binding-design.md`, and
restated because they bound the follow-up:

- worktree creation;
- worktree cleanup or removal;
- `git reset`, `git clean`, or deletion of dirty directories;
- merge/integration authority;
- global worktree registry, daemon, or session supervisor;
- branch-name-based authority;
- changes to review approval rules;
- changed-path scope enforcement at harness lifecycle points (that remains
  `verify_git_run()`'s job, on request).

The binding remains evidence. It gains an enforcement point; it does not gain
authority over who may work or who may merge.

## Bounded follow-up implementation

Recommended next task: `Worktree binding guard enforcement`. Tracked at
`work/tasks/worktree-binding-guard-enforcement.md`.

Allowed scope:

- `runtime/integrity/git_scope.py` — extract `compare_worktree_identity()`;
  `verify_git_run()` uses it with no payload change.
- `runtime/integrity/__init__.py` — export the helper.
- `runtime/policy/harness_guard.py` — injected identity source and
  `_require_bound_worktree()`.
- `tests/test_runtime_review_hardening.py` (or the guard's existing test module)
  — new coverage.
- `work/roadmaps/CAPABILITY_CHECKLIST.md` rows E6 and 6.16.

Required tests:

- bound run in the bound worktree → guard annotates `CANONICAL_RUN_VERIFIED`;
- bound run in a different worktree/clone → `DENY` `RUN_WORKTREE_MISMATCH`;
- bound run whose identity read raises → `DENY` `RUN_WORKTREE_UNAVAILABLE`;
- unbound (non-Git / placeholder-`base_revision`) run → still allowed, proving
  legacy compatibility;
- `SESSION_STOPPING` on a mismatched worktree → not denied by this check;
- `verify_git_run()`'s existing mismatch/unavailable payloads unchanged after
  the refactor.

## Roadmap impact

This note does not complete E6/6.16, and no row may be marked `DONE` on it.
It corrects the record: worktree verification exists and is enforced only on
explicit CLI request, and it names the single seam that would make the binding
consequential. E6 and 6.16 remain `IN PROGRESS`.
