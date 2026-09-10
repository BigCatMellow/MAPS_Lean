# Task: enforce canonical task/history retention

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `orchestration-operator`
- Risk: `HIGH`
- Goal: Enforce the independently approved task/history retention contract with the smallest SQLite guards and focused regressions.
- Parent design: PR #338 / [`task-history-retention-design.md`](task-history-retention-design.md).
- Review evidence for parent design: [`../reviews/pr-338-review-evidence.md`](../reviews/pr-338-review-evidence.md), bound to `3a3d46d0da6f8a8c4b98b6da6bc97ef5f5d86484`.
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: independently approved PR #338 design, accepted `runtime/state/schema.sql`, `runtime/state/base.py`, PR #330 task/event atomicity regression.
- Authoritative sources: `AGENTS.md` > approved operator sequence > independently approved PR #338 design > this implementation task > accepted runtime/schema.
- Required invariant:

```text
create canonical task
→ TASK_CREATED commits atomically
→ committed task_events cannot UPDATE/DELETE
→ canonical task cannot hard-delete
→ ordinary lifecycle writes continue by appending later events
```

## Change boundary

- MAY CHANGE:
  - `runtime/state/schema.sql` — add exactly the three approved retention/immutability triggers;
  - `tests/test_task_history_retention.py` — focused direct-SQL and normal-lifecycle regressions;
  - this task record;
  - mandatory friction capture if this session produces a qualifying friction signal;
  - PR metadata and later independent review evidence.
- MUST NOT CHANGE:
  - task lifecycle vocabulary;
  - `BaseStore` event-writing semantics;
  - existing foreign-key `ON DELETE CASCADE` clauses;
  - archive/tombstone/redaction/purge behavior;
  - privacy/legal retention policy or retention duration;
  - provider/harness/recovery behavior;
  - capability status or task/review authority.
- HUMAN REAUTHORIZATION REQUIRED: any implementation that deletes/migrates existing persisted state or introduces a legal/privacy retention choice.

## Implementation

Add only:

1. `BEFORE UPDATE ON task_events` → abort with `task events are immutable`;
2. `BEFORE DELETE ON task_events` → abort with `task events are immutable`;
3. `BEFORE DELETE ON tasks` → abort with `canonical tasks cannot be hard-deleted`.

The explicit parent-task trigger owns the normal retention rule. Event triggers own event-row integrity. Existing cascade FKs stay unchanged and latent behind the parent guard.

## Acceptance criteria

- [x] A freshly created canonical task has `TASK_CREATED` history.
- [x] Direct SQL UPDATE of a committed task event is rejected.
- [x] Direct SQL DELETE of a committed task event is rejected.
- [x] Direct SQL DELETE of the canonical task is rejected by the task-level guard.
- [x] Failed direct mutations leave canonical task/history unchanged.
- [x] Normal contract shaping, READY promotion, and claim still append new semantic events.
- [x] No archive/tombstone/purge/redaction framework is added.
- [x] No existing FK cascade declarations are rewritten.

## Verification

- Focused: `python -m unittest tests.test_task_history_retention -v`.
- Full: repository `Runtime stack tests` on the exact implementation head.
- Independent review: required because this changes database-enforced retention/immutability behavior.
- Reviewer must inspect the exact implementation delta and verify the parent task trigger—not incidental child cascade failure—causes direct task-delete rejection.

## Stop / escalate

Stop if the guards break an accepted normal runtime lifecycle path, reveal a real supported canonical-task hard-delete path, or require migration/deletion of existing persisted state. Do not widen into archival, privacy, legal erasure, or storage-retention design.

## Completion / handoff

- Implementation: bounded three-trigger enforcement plus focused regressions.
- Merge authority: not granted by this task.
- Next gate: exact-head Runtime CI + fresh independent implementation review.
