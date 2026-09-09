# Task: dependency-cycle readiness rejection

- Status: `READY_FOR_REVIEW`
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

It did not explicitly detect a multi-task reachable cycle. For example `A -> B -> A` left both tasks dependency-blocked rather than identifying an unresolvable graph error.

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

## Implemented semantics

1. Readiness now detects one deterministic cycle reachable from the task through dependencies that are not already `DONE`.
2. Dependency traversal is ordered by task id so the returned cycle is stable for the same graph.
3. A reachable cycle is a shaping error (`AGI FAIL — NEEDS_SHAPING`), not an ordinary temporary dependency wait.
4. Existing direct-self wording remains `task cannot depend on itself`; the generic cycle detector is skipped for that case so the reason is not duplicated.
5. Existing behavior is preserved for:
   - missing dependency -> dependency blocker;
   - acyclic unfinished dependency -> `AGI FAIL — BLOCKED_ON_DEPENDENCY` when no other shaping error exists;
   - `DONE` dependency -> satisfied; traversal terminates there and ignores its historical downstream graph.
6. No task state mutation was added beyond the existing `promote_ready()` rejection path.

## Acceptance criteria

- [x] `A -> B -> A` is rejected with one deterministic cycle reason.
- [x] `A -> B -> C -> B` is rejected for A with the reachable `B -> C -> B` cycle.
- [x] acyclic unfinished dependency remains `BLOCKED_ON_DEPENDENCY`, not `NEEDS_SHAPING`.
- [x] direct self-dependency keeps its existing reason and is not duplicated by cycle output.
- [x] missing dependency behavior is unchanged.
- [x] `DONE` dependency terminates traversal and remains satisfied.
- [x] no schema/authority/lifecycle expansion.
- [ ] repository CI passes.
- [ ] independent review completed.

## Verification

Focused tests added in `tests/test_dependency_cycle_readiness.py`; repository CI will run on the PR head.

## Stop / escalate

No stop boundary was crossed. The change diagnoses the existing dependency graph only; it does not auto-break cycles, mutate other tasks, or introduce scheduler/backlog infrastructure.
