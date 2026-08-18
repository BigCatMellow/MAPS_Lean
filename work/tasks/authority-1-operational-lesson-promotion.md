# Task: operational-learning promotion/retirement authority, Authority-1

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/operational-learning-authority1-wave4`
- Risk: `MEDIUM`
- Goal: Implement `Authority-1` from
  `work/notes/2026-08-17-operational-learning-authority-design.md` -- the
  operator-only `CANDIDATE -> ACTIVE` promotion and `CANDIDATE|ACTIVE ->
  RETIRED` retirement mechanism, per the recorded operator decision (Option A:
  operator-only, every promotion and every retirement, no automatic path).

## Note on this task file's provenance

This task file did not exist before this branch. The design note
(`2026-08-17-operational-learning-authority-design.md`, merged PR #79) names
`Authority-1` as the authorized next bounded task and records the operator's
decision, but no task doc was written for it before `Storage-0` (PR #81)
landed. This file is that missing task doc, written from the design note's
"Operator decisions (recorded 2026-08-17)" section and the actual `Storage-0`
implementation on `main`, following the `Storage-0` task doc
(`work/tasks/operational-learning-storage0-wave4.md`) as its structural model.

## Inputs and source of truth

- `work/notes/2026-08-17-operational-learning-authority-design.md` (merged
  PR #79), specifically "2. Promotion / retirement authority" and "Operator
  decisions (recorded 2026-08-17)": Option A is decided -- operator-only,
  every transition, no bounded-automatic or hybrid-queue path.
- `runtime/operational_learning.py` at current `main` (merged PR #43,
  unmodified by this task) -- `validate_lesson_record()`'s `_promotion()` /
  `_retirement()` sub-schemas (`_PROMOTION_KEYS`, `_RETIREMENT_KEYS`) are
  reused as-is and are the authoritative shape for what a promotion/
  retirement decision must carry.
- `runtime/state/schema.sql` `operational_lessons` table and
  `runtime/state/operational_learning_storage.py` (merged PR #81, `Storage-0`)
  -- read in full. Two facts from the actual implementation, not the design
  note's illustrative sketch, drive this task's schema shape:
  1. `operational_lessons.lesson_id` is the table's `PRIMARY KEY` (one row
     per lesson, not a multi-snapshot append log keyed by a separate
     `lesson_row_id` as the design note's sketch showed).
  2. `operational_lessons.status` has a literal `CHECK (status = 'CANDIDATE')`
     -- the table cannot hold a row with any other status at all, by design
     (`Storage-0`'s own "Boundary enforcement" section: this restriction is
     intentional, not an oversight).
  Consequence: promotion/retirement **cannot** be modeled as a second row in
  `operational_lessons` (the design note's original sketch), because the
  table's own schema now forbids both a second row for the same `lesson_id`
  (`PRIMARY KEY`) and any non-`CANDIDATE` status. This task instead adds a
  **new, separate append-only decisions table** referencing
  `operational_lessons.lesson_id`, which is the same "new row referencing the
  old row, never an UPDATE" house pattern the design note asked for, adapted
  to the schema `Storage-0` actually shipped. This is the one place this task
  had to make a judgment call the design note did not fully pin down, because
  the note's schema sketch and `Storage-0`'s actual shipped schema disagree
  on primary-key shape; the decision favors what is actually on `main`.
- `runtime/state/schema.sql` `run_recovery_links` /
  `run_helper_links` -- house style for a linking/decision table: append-only,
  `INTEGER PRIMARY KEY AUTOINCREMENT`, `CHECK`-validated actor/ref text,
  explicit `BEFORE UPDATE`/`BEFORE DELETE` triggers that `RAISE(ABORT, ...)`,
  and `BEFORE INSERT` triggers enforcing relationship invariants (e.g.
  chronological order, no cycles) at the SQL layer, not just in Python.

## Change boundary

MAY CHANGE / ADD:
- `runtime/state/schema.sql` (additive only: new
  `operational_lesson_decisions` table, index, immutability + invariant
  triggers; no change to the existing `operational_lessons` table or any
  other existing table)
- `runtime/state/operational_learning_storage.py` (extend the existing
  mixin: `promote_operational_lesson()`, `retire_operational_lesson()`,
  `list_operational_lesson_decisions()`; update `get_operational_lesson()`
  to compose the effective lesson view from the base row plus its decisions,
  and `list_operational_lesson_candidates()` to exclude lessons that already
  have a decision)
- `tests/test_operational_learning_storage.py` (extend with promotion/
  retirement coverage)
- this task doc

MUST NOT CHANGE:
- `runtime/operational_learning.py`
- `runtime/outcome_lesson_candidate.py`
- `runtime/context_builder.py` or any Context Builder integration
- the existing `operational_lessons` table definition or its triggers
- any other runtime file
- any other agent's branch

## Boundary enforcement (the actual point of this task)

- `status` transitions are never a SQL `UPDATE`. `operational_lessons` stays
  exactly as `Storage-0` shipped it (append-only `CANDIDATE` rows, `status`
  `CHECK`-locked to `'CANDIDATE'`, immutable). A lesson's *effective* status
  (`CANDIDATE` / `ACTIVE` / `RETIRED`) is derived by composing the base row
  with the latest rows in the new `operational_lesson_decisions` table --
  never stored as a mutable column anywhere.
- Every promotion and every retirement requires an explicit, non-empty
  `decision_ref` and actor (`promoted_by` / `retired_by`) -- there is no
  automatic/evidence-gated path (Option B/C from the design note are not
  implemented; Option A only, matching the recorded operator decision).
- `promote_operational_lesson()` and `retire_operational_lesson()` both
  reconstruct the full candidate lesson snapshot (base fields + the proposed
  `status`/`promotion`/`retirement`) and pass it through the existing,
  unmodified `validate_lesson_record()` before writing anything -- the same
  defense-in-depth pattern `Storage-0` used, not a reimplementation of shape
  validation.
- A lesson already carrying a `PROMOTE` decision cannot be promoted again
  (`ALREADY_PROMOTED`); a lesson already carrying a `RETIRE` decision cannot
  be promoted or retired again (`LESSON_RETIRED` -- retirement is terminal).
  A `CANDIDATE` lesson can be retired directly without ever being promoted
  (rejecting a candidate outright). Both invariants are enforced in the
  Python layer and independently backstopped by `BEFORE INSERT` triggers on
  `operational_lesson_decisions` that `RAISE(ABORT, ...)`, so a hand-written
  SQL insert cannot bypass them either -- tested directly, not just asserted.
- `operational_lesson_decisions` rows are immutable (`BEFORE
  UPDATE`/`BEFORE DELETE` triggers), matching every other evidence/decision
  table in `schema.sql`.

## Acceptance criteria

- [x] New `operational_lesson_decisions` table: append-only, references
      `operational_lessons(lesson_id)`, `decision_kind` restricted by `CHECK`
      to `'PROMOTE'`/`'RETIRE'`, decision payload `CHECK (json_valid(...))`,
      non-empty actor/ref `CHECK`s, immutable (`UPDATE`/`DELETE` both
      rejected by trigger, tested with direct SQL).
- [x] `BEFORE INSERT` trigger rejects a second `PROMOTE` decision for the
      same `lesson_id` (tested with direct SQL, bypassing Python).
- [x] `BEFORE INSERT` trigger rejects any decision (`PROMOTE` or `RETIRE`)
      for a `lesson_id` that already has a `RETIRE` decision (tested with
      direct SQL, bypassing Python).
- [x] `promote_operational_lesson()`: rejects an unknown `lesson_id`, rejects
      re-promotion, rejects promoting a retired lesson, requires
      `decision_ref`/`promoted_by`/`starts_at`/`review_at` (matching
      `_PROMOTION_KEYS`), validates the composed `ACTIVE` record through
      `validate_lesson_record()` before writing, writes exactly one
      `operational_lesson_decisions` row on success.
- [x] `retire_operational_lesson()`: rejects an unknown `lesson_id`, rejects
      double retirement, allows retiring a still-`CANDIDATE` lesson directly,
      allows retiring an already-`ACTIVE` lesson (composed record carries
      both `promotion` and `retirement`), validates the composed `RETIRED`
      record through `validate_lesson_record()` before writing.
- [x] `get_operational_lesson()` returns the effective composed view
      (`CANDIDATE`/`ACTIVE`/`RETIRED` with the correct `promotion`/
      `retirement` sub-dicts) and the composed record itself passes
      `validate_lesson_record()` (tested).
- [x] `list_operational_lesson_candidates()` excludes any lesson that has
      since acquired a decision (still queries only truly-undecided rows).
- [x] `list_operational_lesson_decisions(lesson_id)` returns the immutable
      decision history for one lesson in `created_at` order, for audit/
      traceability.
- [x] No automatic/evidence-gated promotion path exists anywhere in this
      change (Option A only).
- [x] `python scripts/check_legacy_removal_readiness.py` passes.
- [x] Full suite passes with 0 failures (baseline was 555 tests / 6 skipped
      before this change; net new tests only add to that count).
- [x] `git diff --stat main` shows only the four files in the change
      boundary.

## Verification

```text
python -m unittest tests.test_operational_learning_storage -v
python -m unittest discover -s tests -v
python scripts/check_legacy_removal_readiness.py
```

Verification required (direct-SQL invariant check, not just unit tests):
manually open the resulting `maps.db` (or an equivalent scratch DB built the
same way `TaskStore` builds one) and, with hand-written SQL outside the
Python layer, confirm: (a) inserting a second `PROMOTE` decision for the same
`lesson_id` raises; (b) inserting any decision for a `lesson_id` that already
has a `RETIRE` decision raises; (c) `UPDATE`/`DELETE` against
`operational_lesson_decisions` both raise; (d) the existing `operational_lessons`
`CHECK (status = 'CANDIDATE')` constraint from `Storage-0` is untouched and
still holds.

Review required: `INDEPENDENT_REVIEW`.

## Stop / escalation

Stop rather than extend scope if:
- any bounded-automatic or evidence-gated promotion path is requested (that
  is Option B/C, explicitly not what the operator decided);
- any Context Builder wiring or worker-context injection is requested (that
  is `Injection-0/1`, a separate, not-yet-implemented, not-yet-operator-
  authorized-for-build task);
- applicability-conflict auto-resolution is requested (the operator decided
  conflicts are surfaced, never auto-resolved -- that is `Conflict-0/1`, a
  separate task touching `project_applicable_lessons()`, which this task
  does not modify);
- the `operational_lessons` table's existing `Storage-0` shape or triggers
  are found to need changing for this task's own purposes -- that would mean
  this task is silently expanding into a `Storage-0` schema revision instead
  of an additive `Authority-1` extension.

## Continuation

Per the design note's staged order, after this task: `Lifecycle-1`
(renewal/supersession using this same operator-only decision mechanism),
`Conflict-0` (multi-match detection/surfacing in `project_applicable_lessons()`
output), then `Injection-0`/`Injection-1` (attributed `GUIDANCE_ONLY` Context
Builder evidence item) remain separate, not-yet-scoped future tasks. This
task does not imply or partially implement any of them.
