# Operational-learning Storage-0 implementation note

Date: 2026-08-17
Owner: `agent/operational-learning-storage0-wave4`
Status: implementation evidence

## Why

`work/notes/2026-08-17-operational-learning-authority-design.md` identified
that `runtime/operational_learning.py` (#43) and
`runtime/outcome_lesson_candidate.py` (#60) validate and construct lesson
records but never persist them -- everything is a pure function over
caller-supplied dicts, with no SQLite table, no store method, nothing
durable. The operator decided promotion/retirement stays operator-only
(a separate, not-yet-built mechanism) and approved landing `Storage-0` --
append-only `CANDIDATE`-only persistence -- as the first concrete step.

## What changed

`runtime/state/schema.sql`: new `operational_lessons` table, in the house
style of `run_helper_links`/`run_recovery_links` (append-only, explicit
`BEFORE UPDATE`/`BEFORE DELETE` triggers that `RAISE(ABORT, ...)`). Columns
cover the full validated lesson shape. `status` carries a `CHECK (status =
'CANDIDATE')` constraint -- the schema itself cannot represent a promoted or
retired lesson yet, which is the actual boundary this task is scoped to, not
just a documented convention. `promotion`/`retirement` columns exist
(nullable JSON) for future schema stability, but are always `NULL` today:
`validate_lesson_record()` itself rejects a `CANDIDATE` record carrying
promotion or retirement data, so there is no code path that could populate
them under the current constraint.

`runtime/state/operational_learning_storage.py` (new mixin,
`OperationalLessonStorageMixin`): `record_operational_lesson_candidate()`
validates via the existing `validate_lesson_record()` (not reimplemented),
rejects any non-`CANDIDATE` result before touching SQL, inserts inside
`BEGIN IMMEDIATE`, and returns a `MutationResult`. `get_operational_lesson()`
and `list_operational_lesson_candidates()` are read-only lookups.

`runtime/state/store.py`: wired the new mixin into `TaskStore`.

## Boundary proof, not just assertion

`test_direct_sql_status_active_violates_schema_check` bypasses
`record_operational_lesson_candidate()` entirely and hand-writes a raw SQL
`INSERT ... status = 'ACTIVE'` directly against the connection, asserting it
raises `sqlite3.IntegrityError`. This proves the constraint holds even if
some future code path skipped the Python validation layer -- the same
pattern this repo already uses elsewhere (e.g.
`test_sqlite_rejects_cross_task_and_reverse_chronology_recovery` in
`tests/test_helper_recovery_lineage.py`) to test invariants at the actual
enforcement boundary rather than only through the intended call path.

## Verification performed

- `python -m unittest tests.test_operational_learning_storage -v`: 8 tests,
  all pass (round-trip, ordering, Python-layer rejection, SQL-layer
  rejection, invalid-shape rejection, duplicate-id rejection, immutability,
  missing-actor rejection).
- `python -m unittest discover -s tests`: full suite, 555 tests, OK
  (skipped=6 -- the pre-existing optional `fastembed`-dependent Context
  Builder semantic-candidate tests, unrelated to this change).
- `python scripts/check_legacy_removal_readiness.py`: PASS.
- `git diff --stat main`: exactly `runtime/state/schema.sql`,
  `runtime/state/operational_learning_storage.py`,
  `runtime/state/store.py`, `tests/test_operational_learning_storage.py`,
  plus this task doc and note.

## Continuation

Per the design note's staged order: `Authority-1` (the operator-only
promotion/retirement mechanism) is the next bounded task, scoped and
reviewed separately. This task does not implement or partially implement
it -- the schema-level `CHECK (status = 'CANDIDATE')` constraint mechanically
prevents that until `Authority-1` explicitly changes it.
