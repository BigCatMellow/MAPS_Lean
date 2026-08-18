# Multi-agent coordination — START HERE

This directory is the durable coordination entry point for MAPS_Lean browser agents.

It contains **stable operating rules and role contracts**. It must not become a second live-status database.

Live GitHub state and accepted MAPS state remain authoritative for current PR heads, CI, reviews, blockers, ownership evidence, merge position, and other facts that can change when repository activity changes.

## Required read order

Every explicitly role-bound browser session should recover live GitHub state and read, in order:

1. root `AGENTS.md`;
2. this file;
3. `work/coordination/GITHUB_ASYNC_WORK_PULL.md`;
4. `work/coordination/BACKLOG_RECOVERY.md` while recovery mode is active;
5. its own durable role contract under `work/coordination/agents/`;
6. the current task/PR/roadmap evidence relevant to the work it may act on.

Do not trust PR numbers, heads, CI results, review dispositions, blockers, queue order, or ownership snapshots merely because they appear in old prose. Recover them live.

## Permanent roles

- `work/coordination/agents/TOWER.md` — planning / dependency reasoning / dispatch.
- `work/coordination/agents/ANVIL.md` — development / runtime implementation.
- `work/coordination/agents/FOUNDRY.md` — development / runtime implementation and repair.
- `work/coordination/agents/SENTINEL.md` — independent review; may have multiple explicitly operator-bound browser continuities.
- `work/coordination/agents/SWITCHYARD.md` — full PR-backlog control, final synchronization, integration, and merge safety.

A browser session does not choose its own role. The operator binds the role explicitly. `SENTINEL-A`, `SENTINEL-B`, etc. are continuity labels only, not new roles.

## Durable vs live state

### Durable repository coordination

Repository coordination files may contain:

- role definitions and authority boundaries;
- stable coordination protocols;
- safety and anti-regression rules;
- durable task/roadmap reasoning;
- recovery-mode operating rules and exit criteria.

### Live GitHub coordination

Use the relevant PR/task/issue thread for:

- current owner/worker or bounded handoff;
- exact branch head/base;
- latest CI;
- latest review disposition or review claim;
- current blocker/dependency;
- merge-train position;
- current `NOW / NEXT / BLOCKED` routing facts;
- repair/rebuild handoffs.

**Anti-churn rule:** a fact expected to change merely because another PR merges is normally live coordination state and must not require its own merge to remain current.

Do not create or refresh a status-snapshot PR simply to restate changing GitHub facts.

## Role-file rule

Role files are now **durable contracts**, not per-session status ledgers.

Agents should not rewrite their role file merely because their current PR, CI run, reviewer claim, blocker, or next action changed. Record those facts on GitHub instead.

A cross-role edit to the durable role contracts requires explicit operator authority or an accepted coordination-protocol change. The operator explicitly authorized the coordinated recovery update that converted all role files from dated snapshots to durable contracts.

## Backlog recovery mode

While `work/coordination/BACKLOG_RECOVERY.md` says recovery mode is active:

- do not invent new speculative capability work;
- preserve safe parallel implementation and feature review;
- cap active dependency depth;
- freeze stable feature/repair heads while they wait;
- SWITCHYARD advances exactly one merge-authoritative product integration candidate at a time;
- final current-main synchronization happens just in time at the integration slot;
- evaluate status/checkpoint PRs by whether unique durable content actually belongs in future `main`.

The open-PR count is a health metric, not authority to close or merge work.

## Shared handoff headings

Prefer discoverable GitHub-thread evidence:

- `MAPS HANDOFF — READY FOR INDEPENDENT REVIEW`
- `MAPS REVIEW CLAIM — SENTINEL-<label>`
- `MAPS REVIEW DISPOSITION — <result>`
- `MAPS INTEGRATION HANDOFF — <result>`
- `TOWER ROUTING — <bounded assignment or dependency decision>`

Each handoff should identify the exact subject, evidence, boundary, and next legitimate role. A handoff does not silently create task, review, or merge authority beyond the accepted MAPS/operator rules.

## Stalled-work triage

A dispatched worker (a background agent, a CI run, a scheduled job) can go
silent far longer than its task should plausibly take, even after the
underlying work actually finished — a completion signal not reliably
reaching whatever was waiting on it is a real, observed failure mode here,
not a hypothetical one.

If a dispatched worker has not reported back and elapsed time is far beyond
what the task should plausibly take:

1. **Do not keep waiting indefinitely.** Check the live GitHub evidence the
   worker should have produced by now (a PR, a commit, an issue comment) —
   this repo's own durable-vs-live model already says GitHub is the
   authoritative check, not an assumption about internal state.
2. If nothing appropriate exists yet, **proactively resume/re-contact the
   worker** rather than continuing to wait — do not silently give up on it
   either.
3. Once resolved, **record the incident**, not just the fix: what stalled,
   for how long, and why, somewhere durable (a note in the task's own
   PR/handoff at minimum; a coordination-protocol addition here if the
   pattern is likely to recur for other roles/workers, not just this one
   instance). Silently fixing a stall without recording it wastes the
   chance to notice a repeating pattern across sessions.

This applies to any dispatched worker under any role (TOWER dispatching
FOUNDRY/SENTINEL/etc., or an operator-level agent dispatching sub-agents),
not just one specific tool or continuity.

## Core operating model

> **Operator binds roles. TOWER prioritizes. Development lanes build/repair. SENTINEL reviews. SWITCHYARD integrates. GitHub carries live coordination.**

If no eligible work exists for a role, remain idle rather than changing roles or manufacturing work.
