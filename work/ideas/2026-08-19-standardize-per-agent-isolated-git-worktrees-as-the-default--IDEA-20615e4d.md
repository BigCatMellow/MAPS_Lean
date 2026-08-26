# IDEA-20615e4d: Standardize per-agent isolated git worktrees as the default for concurrent implementer sessions

- Kind: `idea`
- Date: `2026-08-19`
- ID: `IDEA-20615e4d`

## Observation

This session's own task instructions explicitly required working inside an isolated worktree (git worktree add /tmp/<name> -b <branch> origin/main) rather than the shared ~/Projects/MAPS_Lean checkout, with an explicit warning not to run git checkout/stash/clean/gh pr checkout there because other concurrent agent sessions are running in other worktrees against the same shared checkout right now. That instruction only makes sense as a mitigation for a real, recurring failure mode: two agents sharing one working tree can stomp each other's checked-out branch, staged changes, or in-progress git operations.

## Source / context

This task's own 'Process notes' section (2026-08-19), directing work into /tmp/emergence-script-worktree instead of the shared clone

## Potential value

If this collision pattern has actually caused lost work or corrupted state in a prior wave (not just been anticipated), that's worth a short durable note somewhere more permanent than one task's process notes -- e.g. a line in AGENTS.md or a coordination playbook -- so every future dispatched session defaults to git worktree add for its own branch instead of re-deriving the same mitigation ad hoc each time it happens to be spelled out in that session's brief.

## Smallest next test

Check whether any repair record or incident note in work/notes/ already documents an actual shared-checkout collision (not just this session's preventive instruction); if one exists, that's the concrete evidence to cite when proposing a standing 'always use an isolated worktree' convention. If none exists yet, the smallest next test is simply asking the operator whether this has bitten a session before, since the preventive instruction implies it has.

## Promotion

Not promoted at capture time. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.

## Current disposition — 2026-08-26

`PARTIALLY ADOPTED`

The original observation is now reflected in active project practice rather than
remaining only an unpromoted idea:

- [WORKTREE_ISOLATION.md](../../playbook/WORKTREE_ISOLATION.md) documents the
  isolated-worktree convention for dispatched writable work.
- [worktree run-binding design](../notes/2026-08-24-worktree-run-binding-design.md)
  extends the principle into run/verifier evidence.
- The capability checklist keeps E6 `IN PROGRESS`, correctly distinguishing the
  adopted isolation/evidence pieces from still-unbuilt automatic allocation and
  cleanup.

Do not interpret this disposition as authority to add automatic worktree
allocation/cleanup merely to complete the original idea. Revisit that only if
real coordination evidence shows manual isolation remains insufficient.
