# Worktree run binding design

Date: 2026-08-24
Owner: `/root`
Status: design complete; no runtime behavior changed

## Finding

E6 / roadmap 6.16 is still convention-bound, not run-evidence-bound.

VERIFIED current state:

- `playbook/WORKTREE_ISOLATION.md` documents the operational rule: writable
  dispatched agents must use isolated Git worktrees and must not mutate the
  shared checkout branch state.
- `runtime/state/integrity.py::create_run_manifest()` records immutable task
  revision, worker/session, readable/writable/forbidden scopes, runtime limits,
  context refs, and optional `base_revision`.
- `runtime/integrity/git_scope.py::verify_git_run()` compares the current Git
  worktree's changed paths against a run manifest's base revision and scope.
- No run-manifest field currently records which Git worktree/root identity was
  assigned to the run.
- `verify_git_run()` accepts a caller-supplied `repo_root` and verifies it is a
  Git top level, but it cannot report "this is not the worktree originally
  bound to the run" because no such binding exists.

This leaves a real attribution gap for concurrent agents. A run can have a base
revision and scope, but the later verifier cannot prove the caller supplied the
same isolated worktree where the run was supposed to execute.

## Decision: additive immutable run worktree identity

Future implementation should bind worktree identity to each run manifest without
creating or deleting worktrees.

Recommended storage shape:

```sql
CREATE TABLE IF NOT EXISTS run_worktree_bindings (
    run_id TEXT PRIMARY KEY REFERENCES run_manifests(run_id) ON DELETE CASCADE,
    repo_root TEXT NOT NULL,
    git_common_dir TEXT NOT NULL,
    git_dir TEXT NOT NULL,
    worktree_private_dir TEXT NOT NULL DEFAULT '',
    head_revision TEXT NOT NULL,
    bound_at TEXT NOT NULL
);
```

Field meaning:

- `repo_root`: resolved Git top-level path supplied to run creation.
- `git_common_dir`: resolved `git rev-parse --git-common-dir`; distinguishes
  independent clones from worktrees sharing one common object/control store.
- `git_dir`: resolved `git rev-parse --git-dir`; distinguishes each linked
  worktree's own Git administrative directory.
- `worktree_private_dir`: resolved `git rev-parse --git-path .` if useful, or
  empty when the Git implementation does not expose a separate per-worktree
  private directory. The implementation should select the exact Git command
  after proving it on normal clones and linked worktrees.
- `head_revision`: exact `HEAD` commit when the run is created.
- `bound_at`: UTC timestamp.

The existing `run_manifests.base_revision` remains the diff base for scope
verification. `head_revision` is an observed worktree fact; it must not replace
`base_revision` because callers may intentionally set a different review/diff
base.

Do not store branch name as authority. Branch names move. They may be useful as
diagnostic metadata later, but they are not a stable binding for this slice.

## Create/read behavior

Recommended implementation behavior:

1. `create_run_manifest(..., repo_root=...)` resolves and validates Git
   identity using read-only `git rev-parse` calls before the SQLite insert.
2. The run manifest and its worktree binding are inserted in the same
   transaction.
3. The binding is immutable. It should be protected by triggers like
   `run_manifests` and `run_context_refs`.
4. `get_run_manifest()` includes:

   ```python
   manifest["worktree"] = {
       "repo_root": str,
       "git_common_dir": str,
       "git_dir": str,
       "worktree_private_dir": str,
       "head_revision": str,
       "bound_at": str,
   } | None
   ```

5. Existing callers that create run manifests from non-Git fixture directories
   should either receive `worktree: None` through an explicit optional flag, or
   tests should initialize Git repos where they are exercising Git-backed run
   integrity. The implementation task must choose one behavior explicitly.

Preferred first slice: require Git identity only when `base_revision` is
provided or when the caller opts into worktree binding. This preserves older
non-Git unit fixtures while letting real Git-scoped runs bind worktree identity.

## Verification behavior

`verify_git_run(store, run_id, repo_root=...)` should compare the caller's
current Git identity with the stored binding before interpreting changed paths.

Recommended failure payload additions:

```python
{
    "ok": False,
    "reason": "worktree_mismatch",
    "worktree_mismatch": {
        "expected_repo_root": "...",
        "actual_repo_root": "...",
        "expected_git_dir": "...",
        "actual_git_dir": "...",
        "expected_git_common_dir": "...",
        "actual_git_common_dir": "...",
    },
}
```

If the run has no worktree binding, verification should preserve current
behavior and include `"worktree_binding": "missing"` or equivalent coverage
metadata. Missing binding is a coverage gap, not automatic task failure.

If Git identity cannot be read from the supplied `repo_root`, verification
should fail closed for Git-scoped runs and return an explicit
`worktree_unavailable` reason. It must not fall back to the process current
directory or a guessed repository root.

## Non-goals

Do not add these in the first implementation:

- worktree creation;
- worktree cleanup;
- `git reset`, `git clean`, or deletion of dirty directories;
- merge/integration authority;
- global worktree registry;
- daemon or session supervisor;
- branch-name-based authority;
- changes to review approval rules.

The run/worktree binding is evidence. It does not authorize a worker, reviewer,
or integrator. Existing task ownership, review independence, run-scope
verification, and GitHub merge controls remain authoritative.

## Bounded follow-up implementation

Recommended next task: `Run worktree binding`.

Allowed implementation scope:

- Add `run_worktree_bindings` schema and immutability triggers.
- Add a small read-only Git identity helper next to `runtime/integrity/git_scope.py`.
- Bind worktree identity during run-manifest creation for Git-scoped runs.
- Project binding from `get_run_manifest()`.
- Make `verify_git_run()` report worktree mismatch before changed-path scope
  evaluation.
- Add tests for:
  - normal Git repo run stores immutable worktree identity;
  - linked worktrees sharing `git_common_dir` still have distinct `git_dir`;
  - verifier accepts the original worktree;
  - verifier rejects a different worktree/clone with `worktree_mismatch`;
  - no-Git or unbound legacy fixtures preserve current behavior according to
    the implementation task's explicit choice;
  - binding is immutable under raw SQL update/delete attempts;
  - existing scope, forbidden-path, and run-manifest tests still pass.

Must not do in that follow-up:

- create worktrees;
- remove worktrees;
- clean dirty worktrees;
- merge branches;
- change task/review authority.

## Roadmap impact

This design does not complete E6/6.16. It defines the next runtime evidence
surface needed to prove that a run's Git changes are being verified against the
same isolated worktree identity the run was assigned.
