reviewer: /root/pr156_reviewer
head_sha: c86d376507b399009136e39b5410edb2600d0e40
independent: true
summary: APPROVED. Re-reviewed PR #156 after rebase at exact code/design head c86d376507b399009136e39b5410edb2600d0e40 against current origin/main c3129f12d673e38f6204ef83854eba65542b8e08 in isolated clone /tmp/maps-pr156-rereview.cgBn25. The PR remains docs-only: `git diff --name-status origin/main...HEAD` shows only `work/notes/2026-08-24-worktree-run-binding-design.md` added, `work/tasks/worktree-run-binding-design.md` added, and `work/roadmaps/CAPABILITY_CHECKLIST.md` modified. `git diff --name-only origin/main...HEAD -- runtime tests runtime/state/schema.sql` returned no paths, so no runtime, test, or SQLite schema behavior changed. `git diff --check origin/main...HEAD` passed. Direct source checks against current main plus the PR confirmed the material design premises remain true: `playbook/WORKTREE_ISOLATION.md` is convention-only and explicitly not an authority layer; `runtime/state/integrity.py::create_run_manifest()` records task revision, worker/session, readable/writable/forbidden scopes, runtime limits, context refs, and optional `base_revision`; `runtime/state/schema.sql` has immutable `run_manifests` and `run_context_refs` but no `run_worktree_bindings`/worktree identity storage; `runtime/integrity/git_scope.py::verify_git_run()` accepts caller-supplied `repo_root`, validates top-level through `collect_git_changes()`, and verifies changed paths against manifest scope/base revision without comparing a stored worktree identity. The task is AGI-ready enough for this medium docs/design task: owner, sources, scope boundaries, acceptance criteria, verification, required independent review, and stop/escalation conditions are explicit. Non-goals correctly exclude worktree creation, cleanup, reset/clean/deletion, merge/integration authority, branch-name authority, global registry/daemon, RnS/recovery/harness behavior, external target work, and review-rule changes. The design is internally coherent and additive, with immutable binding fields, create/read/verify behavior, explicit mismatch/missing/unavailable semantics, and bounded implementation-test follow-up. The roadmap update is accurate and proportional: E6 and 6.16 remain `IN PROGRESS` and describe the design as a next evidence surface, not completed enforcement. No blocking findings.

# Review: Worktree run binding design

- Task: `work/tasks/worktree-run-binding-design.md`
- Reviewer: `/root/pr156_reviewer`
- Verdict: `APPROVED`

## Acceptance criteria check

- `PASS` — Design note names the current E6 gap with direct source paths.
  - Evidence: `work/notes/2026-08-24-worktree-run-binding-design.md` names the convention-only gap and cites `playbook/WORKTREE_ISOLATION.md`, `runtime/state/integrity.py::create_run_manifest()`, and `runtime/integrity/git_scope.py::verify_git_run()`.
- `PASS` — Design note proposes additive immutable run/worktree binding fields.
  - Evidence: The note proposes `run_worktree_bindings` with `run_id`, `repo_root`, `git_common_dir`, `git_dir`, `worktree_private_dir`, `head_revision`, and `bound_at`, while preserving existing `run_manifests.base_revision`.
- `PASS` — Design note defines create/read/verify behavior and failure semantics.
  - Evidence: The note specifies same-transaction creation, immutability, `get_run_manifest()` projection, `worktree_mismatch`, missing-binding coverage metadata, and fail-closed `worktree_unavailable` behavior for Git-scoped runs.
- `PASS` — Design note excludes worktree creation, cleanup, merge authority, and broad registries.
  - Evidence: The note's non-goals exclude worktree creation/cleanup, reset/clean/deletion, merge/integration authority, global registry, daemon/session supervisor, branch-name authority, and review-rule changes.
- `PASS` — Design note leaves a bounded implementation follow-up with tests.
  - Evidence: The follow-up scope is limited to schema/helper/binding/projection/verifier changes and targeted tests; forbidden follow-up work still excludes creation/removal/cleanup/merge/authority changes.
- `PASS` — No runtime or test files change.
  - Evidence: `git diff --name-status origin/main...HEAD` changes only the two `work/` docs and `work/roadmaps/CAPABILITY_CHECKLIST.md`; `git diff --name-only origin/main...HEAD -- runtime tests runtime/state/schema.sql` returned no paths.

## Applicable review lenses

- `[x]` Functional / acceptance
- `[x]` Authority / permission boundary
- `[x]` Destructive / data-loss

Functional / acceptance evidence: reviewed all changed files and compared their claims to the current source paths named by the task/design. The PR satisfies its docs-only architecture acceptance criteria.

Authority / permission boundary evidence: the task and design state that run/worktree binding is evidence only and does not authorize workers, reviewers, integrators, task-state changes, GitHub merge, RnS behavior, or external target work.

Destructive / data-loss evidence: the design excludes worktree cleanup, `git reset`, `git clean`, deletion of dirty directories, automatic removal, and merge authority.

## Findings

No blocking findings.

## Evidence checked

- `git ls-remote origin refs/heads/main refs/pull/156/head`
- `git rev-parse HEAD origin/main`
- `git merge-base HEAD origin/main`
- `git diff --name-status origin/main...HEAD`
- `git diff --stat origin/main...HEAD`
- `git diff --check origin/main...HEAD`
- `git diff --name-only origin/main...HEAD -- runtime tests runtime/state/schema.sql`
- `rg -n "E6 — Worktree isolation|6\\.16 \\| Git worktree isolation" work/roadmaps/CAPABILITY_CHECKLIST.md`
- Direct read:
  - `work/tasks/worktree-run-binding-design.md`
  - `work/notes/2026-08-24-worktree-run-binding-design.md`
  - `work/roadmaps/CAPABILITY_CHECKLIST.md`
  - `playbook/WORKTREE_ISOLATION.md`
  - `runtime/state/integrity.py`
  - `runtime/state/schema.sql`
  - `runtime/integrity/git_scope.py`
  - `work/roadmaps/prime-agent-capability-roadmap.md` section 10 / HW-03

## High-risk completion / release summary

N/A.

## Reviewer limits

- Missing context/evidence: none.
- New requirements discovered: none.
