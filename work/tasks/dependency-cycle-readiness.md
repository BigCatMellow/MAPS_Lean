# Task: dependency-cycle readiness rejection

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: orchestration operator
- Risk: `MEDIUM`

## Goal

Strengthen the existing MAPS_L dependency-readiness owner so a task cannot remain indefinitely dependency-blocked by a reachable dependency cycle that the system could have diagnosed deterministically at shaping/readiness time.

## Inputs / source of truth

- `AGENTS.md`
- `runtime/state/readiness.py`
- `runtime/state/schema.sql` (`task_dependencies`)
- current readiness/state tests
- borrow-integration process: PR #326 / `work/notes/2026-09-09-competitor-borrow-integration-log.md`
- upstream lesson: Noriq rejects dependency cycles before claimability; use the invariant, not its schema.

## Existing behavior

MAPS_L already:

- rejects direct self-dependency;
- blocks missing dependencies;
- blocks dependencies that are not `DONE`;
- treats a `DONE` dependency as satisfied.

It does not explicitly detect a multi-task reachable cycle. For example `A -> B -> A` leaves both tasks dependency-blocked rather than identifying an unresolvable graph error.

## Change boundary

MAY CHANGE:
- `runtime/state/readiness.py` only for deterministic dependency-cycle validation;
- a new focused test module;
- this task file / PR metadata.

MUST NOT CHANGE:
- dependency schema;
- task lifecycle states;
- claim/lease logic;
- routing or scheduler architecture;
- capability/checklist status;
- active PR #319–#327 files.

## Required semantics

1. Detect a cycle reachable from the task being validated through dependencies that are not already `DONE`.
2. Report the cycle deterministically in task-id order traversal.
3. A reachable cycle is a shaping error (`AGI FAIL — NEEDS_SHAPING`), not an ordinary temporary dependency wait.
4. Preserve existing direct-self wording (`task cannot depend on itself`).
5. Preserve existing behavior for:
   - missing dependency -> dependency blocker;
   - acyclic unfinished dependency -> `AGI FAIL — BLOCKED_ON_DEPENDENCY` when no other shaping error exists;
   - `DONE` dependency -> satisfied; do not traverse its historical dependency graph.
6. No task state mutation beyond the existing `promote_ready()` rejection path.

## Acceptance criteria

- [ ] `A -> B -> A` is rejected with one deterministic cycle reason.
- [ ] `A -> B -> C -> B` is rejected for A with the reachable `B -> C -> B` cycle.
- [ ] acyclic unfinished dependency remains `BLOCKED_ON_DEPENDENCY`, not `NEEDS_SHAPING`.
- [ ] direct self-dependency keeps its existing reason and is not duplicated by cycle output.
- [ ] no schema/authority/lifecycle expansion.
- [ ] relevant CI passes and independent review is requested.

## Verification

Focused dependency-cycle readiness tests plus repository CI.

## Stop / escalate

Stop if cycle handling requires changing dependency persistence, auto-breaking cycles, mutating other tasks, or introducing a scheduler/backlog subsystem. This task only diagnoses the existing graph during readiness validation.
