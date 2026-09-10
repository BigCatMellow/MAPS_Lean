# Task: task/event atomicity regression

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `TEST HARDENING`
- Owner: orchestration operator
- Risk: `MEDIUM`

## Goal

Freeze the existing SQLite invariant that a canonical task mutation and its critical semantic `task_events` record commit or roll back together.

Borrowed prior-art lesson: mature durable systems separate semantic history from telemetry and require critical state/history facts to share an atomic commit boundary. Use that invariant only; MAPS `task_events` are not being relabeled as a distributed transactional outbox.

## Existing MAPS behavior

`runtime/state/execution.py::claim_task()` performs, inside one `BEGIN IMMEDIATE` transaction:

1. canonical `tasks` update;
2. `_append_event(... TASK_CLAIMED/TASK_CLAIM_RECOVERED ...)`;
3. one `commit()`.

The code appears correct, but the regression suite did not explicitly prove rollback if event persistence fails after the task update.

## Change boundary

MAY CHANGE:
- one new focused test module;
- this task record / PR metadata.

MUST NOT CHANGE:
- `runtime/`;
- schema;
- event vocabulary;
- task lifecycle semantics;
- external event delivery/outbox architecture;
- capability status.

## Acceptance criteria

- [x] inject failure at `_append_event` during `claim_task()` after the SQL task update has executed;
- [x] exception is observable rather than converted into false success;
- [x] canonical task remains `READY`, unclaimed, attempt `0` after connection rollback;
- [x] task-event row count is unchanged;
- [x] no runtime change.
- [ ] repository CI passes.
- [ ] independent review completed.

## Limitation

This proves same-SQLite-transaction atomicity for canonical task state + `task_events`. It does not prove atomic delivery to GitHub/providers/filesystems/queues; those require the separate external-effect/outbox/reconciliation work identified by the competitor audit.
