# Task: operational-learning candidate storage, Storage-0 Wave 4

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/operational-learning-storage0-wave4`
- Risk: `LOW`
- Goal: Implement `Storage-0` from `work/notes/2026-08-17-operational-learning-authority-design.md`
  -- append-only persistence of `CANDIDATE`-status operational lesson
  snapshots, with no promotion/retirement mechanism -- per the operator
  decisions recorded there.

## Inputs and source of truth

- `work/tasks/operational-learning-authority-design-wave4.md` and
  `work/notes/2026-08-17-operational-learning-authority-design.md` (merged
  PR #79) -- this task implements exactly `Storage-0` from its "Unblocked
  next step" section. `Authority-1` (the operator-only promotion mechanism)
  and `Injection-0/1` (context surfacing) are explicitly separate, not-yet-
  implemented future tasks; this task does not build them.
- `runtime/operational_learning.py` at current `main` (merged PR #43,
  unmodified by this task) -- `validate_lesson_record()` is reused as-is for
  all shape validation.
- `runtime/state/schema.sql`, `runtime/state/helper_recovery_lineage.py` --
  house style for append-only, immutable-by-default relationship/evidence
  tables (explicit `BEFORE UPDATE`/`BEFORE DELETE` triggers, `MutationResult`
  return shape, `BEGIN IMMEDIATE` transactions).

## Change boundary

MAY CHANGE / ADD:
- `runtime/state/schema.sql` (additive only: new `operational_lessons`
  table, index, immutability triggers; no changes to any existing table)
- `runtime/state/operational_learning_storage.py` (new)
- `runtime/state/store.py` (additive: wire the new mixin into `TaskStore`)
- `tests/test_operational_learning_storage.py` (new)
- this task doc and its note

MUST NOT CHANGE:
- `runtime/operational_learning.py`
- `runtime/outcome_lesson_candidate.py`
- `runtime/context_builder.py` or any Context Builder integration
- any other runtime file
- any other agent's branch

## Boundary enforcement (the actual point of this task)

`status` is restricted to the literal value `'CANDIDATE'` by a SQLite `CHECK`
constraint on the `operational_lessons` table -- not merely a Python-level
convention. `record_operational_lesson_candidate()` also independently
rejects any non-`CANDIDATE` validated record before it reaches SQL, as
defense in depth. Both layers are tested directly, including a test that
bypasses the Python layer entirely with hand-written SQL to prove the schema
constraint itself holds.

## Acceptance criteria

- [x] New `operational_lessons` table matches the full validated shape from
  `validate_lesson_record()` (all `_LESSON_KEYS`).
- [x] `status` cannot be anything other than `'CANDIDATE'`, enforced at the
  SQL schema level via `CHECK`.
- [x] Rows are immutable (`UPDATE`/`DELETE` both rejected by trigger).
- [x] `record_operational_lesson_candidate()` reuses `validate_lesson_record()`
  without reimplementing validation logic.
- [x] A non-`CANDIDATE` record is rejected by the Python layer before any row
  is written.
- [x] A direct-SQL attempt to insert `status='ACTIVE'` is rejected by the
  schema `CHECK` constraint (tested, not just asserted).
- [x] Duplicate `lesson_id` is rejected.
- [x] An invalid record shape (e.g. missing a required key) is rejected
  before any row is written.
- [x] `get_operational_lesson()` and `list_operational_lesson_candidates()`
  round-trip correctly, including full JSON-encoded `source_refs` and
  `applicability` fields.
- [x] `python scripts/check_legacy_removal_readiness.py` passes.
- [x] Full suite passes: 555 tests, 6 skipped (unrelated pre-existing
  optional-dependency skips), 0 failures.
- [x] `git diff --stat main` shows only the four files in the change
  boundary.

## Verification

```text
python -m unittest tests.test_operational_learning_storage -v
python -m unittest discover -s tests
python scripts/check_legacy_removal_readiness.py
```

Review required: `INDEPENDENT_REVIEW`.

## Stop / escalation

Stop rather than extend scope if:
- any promotion/retirement/status-transition capability is requested (that
  is `Authority-1`, a separate task requiring its own operator-decision-
  matching implementation);
- any Context Builder wiring is requested (that is `Injection-0/1`, gated on
  `Authority-1` landing first per the design note);
- the schema-level `status` restriction is found to need relaxing for this
  task's own purposes -- that would mean scope has silently grown beyond
  Storage-0.

## Continuation

Per the design note's staged order: `Authority-1` (implementing the
operator-only promotion/retirement mechanism decided in
`2026-08-17-operational-learning-authority-design.md`) is the next bounded
task, once explicitly scoped and independently reviewed on its own. It is
not implied or partially done by this task.
