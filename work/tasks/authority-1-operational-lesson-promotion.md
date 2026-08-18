# Authority-1 — operator-only operational-lesson promotion/retirement

Owner: FOUNDRY implementation task
Status: authorized (see `work/notes/2026-08-17-operational-learning-authority-design.md`, operator decision #1: "Option A — operator-only, every promotion and every retirement")

## Ground truth (already verified, do not re-derive)

- `runtime/operational_learning.py`'s `validate_lesson_record()` **already fully supports** ACTIVE and RETIRED status, including complete promotion/retirement contract validation (`_promotion()`, `_retirement()`) and cross-field timing rules (review_at > starts_at, expires_at > starts_at, retirement can't precede promotion start, etc). `project_applicable_lessons()` **already fully consumes** ACTIVE lessons (NOT_STARTED/EXPIRED/REVIEW_DUE/applicability matching). None of this needs to change. This task is purely about making promoted/retired rows reach storage.
- `runtime/state/schema.sql` (`operational_lessons` table, ~line 619) hard-locks `lesson_version = 1` and `status = 'CANDIDATE'` as SQLite `CHECK` constraints, and `lesson_id` is currently the sole `PRIMARY KEY`. `trg_operational_lessons_no_update` / `trg_operational_lessons_no_delete` make every row immutable (INSERT-only) — keep these; the design below relies on them.
- `runtime/state/operational_learning_storage.py`'s `OperationalLessonStorageMixin` currently has `record_operational_lesson_candidate()` (CANDIDATE-only, by design — do not remove this restriction from it), `get_operational_lesson()`, and `list_operational_lesson_candidates()`.
- Precedent for "operator-only" authority elsewhere in this codebase: `runtime/state/policy.py`'s `record_operator_approval(task_id, *, approved_by, note)` — identity is a **required, non-empty free-text string recorded as an audit trail**, not cryptographically verified. MAPS's established pattern is recorded-assertion-based operator authority, not identity authentication. Match this shape; do not invent a stronger identity-verification mechanism than the rest of the codebase uses.

## Required change: versioned, append-only lesson rows

Promotion/retirement must never mutate or delete the original row (immutability triggers already enforce this). Each promotion/retirement appends a **new row** for the same `lesson_id` at `lesson_version + 1`, carrying the unchanged content fields (`claim`, `source_kind`, `source_refs`, `applicability`, `created_by`, `created_at`) copied verbatim from the row being promoted/retired — promotion must never re-author lesson content, only add promotion/retirement authority data. This mirrors how `validate_lesson_record()` already expects `promotion`/`retirement` to be populated on otherwise-identical-content rows.

### 1. Schema (`runtime/state/schema.sql`)

- `PRIMARY KEY` on `operational_lessons` must become composite `(lesson_id, lesson_version)` — `lesson_id` alone is no longer unique once multiple versions exist.
- `lesson_version INTEGER NOT NULL CHECK (lesson_version = 1)` → `CHECK (lesson_version >= 1)`.
- `status TEXT NOT NULL CHECK (status = 'CANDIDATE')` → `CHECK (status IN ('CANDIDATE','ACTIVE','RETIRED'))`.
- `superseded_by TEXT REFERENCES operational_lessons(lesson_id)`: this FK required `lesson_id` to be unique, which no longer holds under a composite PK. SQLite will reject/misbehave with a dangling FK target. Either (a) drop the SQL-level FK and validate `superseded_by` existence at the Python storage layer instead (documented inline why), or (b) find a schema-valid way to keep it (e.g. a separate `UNIQUE` index expressing "at least one row exists for this lesson_id" isn't expressible as a FK target directly in SQLite without a dedicated one-row-per-lesson_id lookup table). Prefer (a) — simpler, and this codebase already validates plenty at the Python layer (see `_declared_availability` etc. elsewhere) rather than pushing everything into SQL. Document the tradeoff in a comment where the FK used to be.
- Update the existing comment block above the table (currently says promotion/retirement/superseded_by "are always NULL while this constraint holds" — no longer true).

### 2. Storage layer (`runtime/state/operational_learning_storage.py`)

Add two new methods, following `record_operational_lesson_candidate`'s existing transaction/validation/error-shape pattern (`BEGIN IMMEDIATE`, `MutationResult` on every path, `sqlite3.IntegrityError` → `MutationResult(False, ...)`):

```python
def promote_operational_lesson(
    self, lesson_id: str, *, promoted_by: str,
    decision_ref: str, starts_at: str, review_at: str,
    expires_at: str | None = None,
) -> MutationResult:
```
- Look up the **latest** row for `lesson_id` (`ORDER BY lesson_version DESC LIMIT 1`, inside the same transaction).
- Fail (`MutationResult(False, "LESSON_NOT_FOUND", ...)`) if no row exists.
- Fail (`MutationResult(False, "LESSON_NOT_CANDIDATE", ...)`) if the latest row's status isn't `CANDIDATE` — this is the actual "operator-only, deliberate, one-way" gate: you can only promote the current candidate tip, never re-promote an already-ACTIVE or already-RETIRED lesson.
- Construct the new record dict: same `lesson_id`/`claim`/`source_kind`/`source_refs`/`applicability`/`created_by`/`created_at`/`superseded_by` as the latest row, `lesson_version = latest + 1`, `status = "ACTIVE"`, `promotion = {"decision_ref": ..., "promoted_by": promoted_by, "starts_at": starts_at, "review_at": review_at, "expires_at": expires_at}`, `retirement = None`.
- Validate via `validate_lesson_record()` before inserting (reuse it exactly as `record_operational_lesson_candidate` does) — do not hand-roll a second validation path.
- Insert; return `MutationResult(True, "LESSON_PROMOTED", ...)` with the new row.

```python
def retire_operational_lesson(
    self, lesson_id: str, *, retired_by: str,
    decision_ref: str, retired_at: str,
) -> MutationResult:
```
- Same shape: latest row must exist and have status `ACTIVE` (fail `LESSON_NOT_ACTIVE` otherwise); new row copies content fields + the **existing promotion object unchanged** (retirement doesn't erase promotion history — `validate_lesson_record` requires `promotion is None` for RETIRED only when `promotion_raw is None`; check the actual code path in `operational_learning.py`'s `validate_lesson_record` — the `else` branch for RETIRED currently reads `promotion = _promotion(promotion_raw, lesson_id) if promotion_raw is not None else None`, i.e. RETIRED **may** carry the promotion record. Carry it forward from the ACTIVE row being retired), sets `status = "RETIRED"`, `retirement = {"decision_ref": ..., "retired_by": retired_by, "retired_at": retired_at}`.

**Critical fix required in the same task** (found during design review, not optional): `get_operational_lesson()` and `list_operational_lesson_candidates()` currently query with no per-`lesson_id` version disambiguation. That was harmless when only one row per `lesson_id` could ever exist. Once promotion appends a second (higher-version) row for the same `lesson_id`, the **original CANDIDATE row still exists forever** (immutability triggers forbid deleting it), so:
- `get_operational_lesson(lesson_id)` must return the **latest version** row, not an arbitrary/first-matching one.
- `list_operational_lesson_candidates()` must only return `lesson_id`s whose **latest** version has `status = 'CANDIDATE'` — not any row that happens to have `status = 'CANDIDATE'`, which after this change would incorrectly include stale pre-promotion snapshots forever.

Use a `lesson_version = (SELECT MAX(lesson_version) FROM operational_lessons WHERE lesson_id = operational_lessons.lesson_id)` correlated-subquery filter (or equivalent) for both.

### 3. Tests

Extend `tests/test_operational_learning_storage.py` (existing `lesson_record()` helper takes `status=` already — reuse it, add a `promotion=`/`retirement=` override if needed for constructing expected-row assertions). Required coverage, minimum:
- Promote a CANDIDATE lesson → new row at version 2, status ACTIVE, content fields byte-identical to version 1, promotion fields match input.
- Promoting a nonexistent `lesson_id` fails `LESSON_NOT_FOUND`.
- Promoting an already-ACTIVE lesson fails `LESSON_NOT_CANDIDATE` (no double-promotion).
- Promoting an already-RETIRED lesson fails `LESSON_NOT_CANDIDATE`.
- Retire an ACTIVE lesson → new row at version 3, status RETIRED, promotion carried forward unchanged, retirement fields match input.
- Retiring a CANDIDATE (never-promoted) lesson fails `LESSON_NOT_ACTIVE`.
- Retiring an already-RETIRED lesson fails `LESSON_NOT_ACTIVE`.
- **`get_operational_lesson()` after promotion returns the ACTIVE (latest) row, not the original CANDIDATE row.**
- **`list_operational_lesson_candidates()` after promoting one of two candidates returns only the still-unpromoted one** — this is the regression test for the critical fix above; without it this bug would ship silently.
- Original CANDIDATE row is still readable via direct SQL query (proving immutability/append-only held, nothing was deleted/mutated) — one assertion querying `sqlite3` directly for `COUNT(*) WHERE lesson_id = ? ` returning 2 (or 3 after retirement) is enough.
- Trigger still fires: attempting a raw `UPDATE`/`DELETE` on `operational_lessons` still raises (this proves the schema change didn't accidentally weaken the existing immutability triggers).

Also check `tests/test_operational_learning_schema.py` for anything asserting the old single-row-per-lesson_id / `lesson_version = 1` constraint — update expectations there if present, since that CHECK is intentionally being relaxed.

### 4. Explicit non-goals (do not implement)

- No Context Builder integration (`Injection-0`/`Injection-1` are separate, later, operator-decision-gated tasks).
- No conflict/precedence auto-resolution (`Conflict-0` surfaces multiple applicable matches as evidence only — already handled by `project_applicable_lessons`'s existing multi-record output; nothing new needed here).
- No CLI/API surface beyond the two storage methods, unless one already exists for `record_operational_lesson_candidate` that these should mirror — check `runtime/integrity/cli.py` and mirror only if a parallel CLI entry point already exists for the candidate path; do not invent a new CLI surface if none exists yet for lessons.
- Do not touch `promoted_by`/`retired_by` identity verification beyond the free-text-recorded-assertion pattern already established by `record_operator_approval` — this task does not add authentication.

## Verification required before handoff

1. Full test suite passes (`python -m unittest discover -s tests -v`) — run in background, it takes 7-11 minutes.
2. `python -m compileall -q runtime tests`.
3. New tests specifically listed above all present and passing, not just "tests pass overall."
4. Confirm via direct SQL query in a throwaway script (not just unit tests) that after promotion, both the CANDIDATE and ACTIVE rows exist in the table simultaneously with the same `lesson_id` — this is the core invariant the whole design depends on; verify it isn't just asserted by a test that could itself have a bug.

## Delivery

Implement on a fresh branch off current `main`, commit, push, open a PR (do not merge). Title should reference "Authority-1". PR body must state the schema change explicitly (composite PK change, CHECK relaxation, FK drop) since this is the kind of change reviewers should not have to discover by reading a diff. Do not merge — a second, independent SENTINEL-style review pass happens after you're done, then a human/operator merges.
