# TASK-282 delivery note

Implemented criterion-level submission claims and independent verification
records: `MAP_System/scripts/submission_records.py`, additive schema
`MAP_System/migration/submission_record_schema.sql`, focused tests
`MAP_System/tests/test_submission_records.py` (9/9), and the documentation
template `MAP_System/workflow/templates/submission_record.json`.

## Delivered behavior

- Each acceptance criterion already carries a stable identifier —
  `task_acceptance_criteria.id`, an existing autoincrement primary key — so
  this task reuses it rather than inventing a second one.
- `record_claim()` links a claimed status (`complete`/`partial`/`blocked`)
  to that stable criterion id, the canonical submission author
  (`task_submission_authorship.author_id`, TASK-278), and optionally a
  TASK-281 `task_revision`/`run_id`.
- A `complete` claim requires at least one evidence reference and every
  referenced path must exist on disk at claim time; the insert is refused
  otherwise, with no partial row left behind.
- `record_verdict()` stores reviewer-verified status in a separate,
  append-only table (`submission_criterion_verdicts`) keyed by `claim_id`.
  Rejecting one criterion inserts a verdict row; it never mutates or deletes
  the implementer's original claim row. `record_verdict()` also rejects a
  reviewer verifying their own claim (`SELF_REVIEW`), mirroring TASK-278's
  no-self-review guard rather than trusting caller-supplied identity.
- Claims are tied to `(task_id, submission_count)`. Rework and resubmission
  advance `submission_count` (TASK-278) and produce new claim rows under the
  new count; prior rows for the earlier attempt are never overwritten,
  giving an auditable, append-only history across rejection/rework/
  resubmission.
- No competing task authority: this module never reads or writes
  `tasks.status`. It records structured evidence alongside the existing
  `db/claims.py` / `scripts/map_task.py` lifecycle; nothing here gates or
  drives a status transition.

## Migration and compatibility

`migration/submission_record_schema.sql` is additive and applied
idempotently by `submission_records.py` itself (`CREATE TABLE IF NOT
EXISTS`), kept separate from `migration/schema.sql` — same pattern as
TASK-281's `run_manifest_schema.sql`. No other task's `connect()` implicitly
depends on it, so it cannot break an unrelated flow. Tasks submitted before
this table existed simply have zero claim rows; `get_claims()` returns an
empty list rather than erroring, and nothing elsewhere requires a non-empty
result.

## Rollback

Drop the two new tables (`submission_criterion_claims`,
`submission_criterion_verdicts`) and delete
`migration/submission_record_schema.sql`; no other table or script
references them, and `tasks.status` lifecycle is completely unaffected by
their presence or absence.

## Residual risk

- This module is currently invoked only directly (CLI or import), not from
  any dispatch or review-gate code path — same "pilot, not production
  integration" posture as TASK-281. Wiring criterion claims into the actual
  `submit`/`approve` flow (e.g. requiring at least one `complete` claim per
  acceptance criterion before approval) is future work, not part of this
  task's registered scope, and would need its own independent review given
  it would then be load-bearing for approval decisions.
- `evidence_refs` existence-checking only confirms a file exists at claim
  time; it does not verify the file's *content* actually satisfies the
  criterion. That judgment remains a reviewer's job via `record_verdict()`.
