# IDEA-bc6cd243: A stale-worktree prune + report step in coordination housekeeping

- Kind: `idea`
- Date: `2026-09-03`
- ID: `IDEA-bc6cd243`

## Observation

git worktree list shows 6 live .claude/worktrees/ entries plus ~30 registrations under dead /tmp/claude-* session scratch dirs. Nothing prunes them; git worktree prune is never run; git worktree remove is autoMode-blocked so it needs operator action. The dead /tmp ones are always safe to prune automatically; the .claude/worktrees/ ones need an age-annotated list for operator review.

## Source / context

git worktree list output 2026-09-03; memory feedback_worktree_removal_automode_blocked; memory project_zombie_session8_orchestrator (holds 4 worktree locks)

## Potential value

Stale worktrees pollute every repo-wide scan (see the Spiderweb idea), consume disk, and hide real state (the zombie session-8 locks). A bounded housekeeping step - prune dead registrations, list the rest by last-commit-age - keeps the checkout legible without a daemon.

## Smallest next test

Add to scripts/coordination_housekeeping.py (or a new scripts/worktree_housekeeping.py): run 'git worktree prune -v', then print remaining worktrees with last-commit date + branch merged-status; SAFE-to-remove list goes to the operator.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.
