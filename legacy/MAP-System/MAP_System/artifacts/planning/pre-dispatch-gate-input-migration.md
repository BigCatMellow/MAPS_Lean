# Pre-Dispatch Gate Input Migration Plan

Owner: claude-review-soba (plan author; not the fix owner)
Date: 2026-07-21
Related: `MAP_System/artifacts/research/SUMMARY-external-blueprint-gap-review-2026-07-21.md`
(gap 4, "Four of six core-agent approval gates are unreachable"),
`MAP_System/tests/test_pre_dispatch_gate_inputs.py` (originally a known-failing
regression test pinning the gap this plan closes; now rewritten to assert the
fixed behavior and wired into `run_tests.sh` — see Status above),
`MAP_System/DECISION_CLASSES.md`,
`MAP_System/RISK_SYSTEM.md`, `MAP_System/artifacts/planning/map-task-tiering-spec.md`.

Status: PHASE 1 LANDED 2026-07-21 (implemented by claude-lab-rose, independently
re-verified by claude-review-soba against this plan's intent). Schema, both
loaders (`pre_dispatch_policy.load_task_from_db` and `graph/runner.py`'s own
`load_tasks_from_sqlite` — this plan named only the former; rose found and
fixed the latter, which this plan should have named), `map_task.py create`
flags, and the mirror/export path (`migration/export_to_files.py`,
`validate_task_mirrors.py` `SCALAR_FIELDS`) all match Section 1-4 below
exactly. 0/253 existing tasks were backfilled, matching Section 2's
recommendation. `test_pre_dispatch_gate_inputs.py` was rewritten by rose to
assert the fixed (not the gap) behavior and is now wired into `run_tests.sh`;
full suite pass=69 fail=2, same 2 pre-existing failures, unrelated to this
change. Phase 2 (below) has now also landed (see update below). This document
originally described a fix before any of it existed; it now also serves as
the record of what landed and how it was checked.

## Retrieval capsule

- Purpose: Defines the schema/loader/create-path/mirror changes needed so
  `pre_dispatch_policy.py`'s five schema-dependent approval gates
  (`decision_class`, `risk_class`, `risk_severity`, `task_tier`,
  `requires_operator_approval`) can actually fire, instead of being
  permanently unreachable because `tasks` has no columns for them.
- Proves: nothing yet — this is a plan, not a decision or a change.
- Applies to: whoever the operator assigns as fix owner for gap 4.
- Does not provide: authorization to run any ALTER TABLE, backfill, or edit
  to `pre_dispatch_policy.py`. Explicitly out of scope for this document's
  author.
- Evidence type: plan
- Status: current

## Problem recap (verified independently, not just cited)

- `tasks` columns today: `task_id, project_id, title, description, task_type,
  role, status, priority, required_agent, owner, claimed_by, lease_expires_at,
  heartbeat_at, attempt, max_attempts, created_at, updated_at` — confirmed via
  `PRAGMA table_info(tasks)`. None of the five gate-input fields exist.
- 253 tasks in `map.db` today; a task loaded via `load_task_from_db()` never
  carries any of the five keys, because the `SELECT` in that function
  (`pre_dispatch_policy.py:420-428`) does not name them and the columns do
  not exist to select from.
- `map_task.py create_task()` (`map_task.py:161-220`) never accepts or
  inserts any of the five fields — there is no CLI flag for any of them.
- The five fields have **no text-heuristic fallback** in
  `evaluate_pre_dispatch()`, unlike the eight predicate-backed fields
  (`destructive_action`, `final_review`, `final_decision`,
  `broad_architecture`, `broad_rewrite`, `canonical_map_mutation`,
  `shell_required`, `trust_boundary_crossing`), each of which degrades to a
  working text heuristic (`is_destructive()`, `is_final_review()`, etc.) when
  the field is absent. The five in scope here degrade to nothing.

## Phase 1 — the five schema-blocked gate inputs (this migration)

### 1. Exact schema change

```sql
ALTER TABLE tasks ADD COLUMN decision_class TEXT;
ALTER TABLE tasks ADD COLUMN risk_class TEXT;
ALTER TABLE tasks ADD COLUMN risk_severity TEXT;
ALTER TABLE tasks ADD COLUMN task_tier TEXT;
ALTER TABLE tasks ADD COLUMN requires_operator_approval INTEGER NOT NULL DEFAULT 0;
```

Notes:

- All five are additive, nullable (or defaulted false for the boolean) —
  matches the existing schema's style (no `CHECK` constraints on `status`,
  `task_type`, etc. either; validity is enforced by the application layer,
  not SQLite). Consistent with `map-runtime-migration-inventory.md`'s stated
  rule: "any new column ... is an ALTER TABLE against this live file with
  existing rows — must be additive/nullable, never a rewrite-in-place."
- `requires_operator_approval` is `INTEGER NOT NULL DEFAULT 0` rather than
  nullable TEXT because `pre_dispatch_policy.as_bool()` already treats
  missing/falsy values as `False` — defaulting to `0` (not required) is the
  correct *safe* default for existing rows, not an arbitrary choice. The
  other four default to `NULL` (unclassified), which `upper_value()`/
  `normalize()` already coerce to `""`, matching current behavior exactly
  for any row that isn't explicitly classified.
- No `CHECK` constraint tying `decision_class` to the `DECISION_CLASSES.md`
  vocabulary (`ARCHITECTURE`, `OWNERSHIP`, `SCOPE`, `AUTHORITY`, `POLICY`) or
  `risk_class`/`risk_severity` to `RISK_SYSTEM.md`'s vocabulary (`SECURITY`,
  `DATA`, `PROCESS`, `AVAILABILITY`, `KNOWLEDGE` / `COSMETIC`, `DRIFT`,
  `BLOCKING`, `STRUCTURAL`) or `task_tier` to
  `map-task-tiering-spec.md`'s (`mechanical`, `bounded`, `architecture`,
  `policy`, `operator`). SQLite `CHECK` on an `ALTER TABLE ADD COLUMN` is
  awkward and the existing schema doesn't use them elsewhere; validate at
  the `map_task.py create` CLI layer instead (see Section 3), same place
  `task_type`/`role` already get validated today if at all.

### 2. Backfilling existing 253 tasks

**Recommendation: do not backfill existing tasks.** Reasons:

- The whole point of these fields is a human or agent *classifying* the
  task's risk/decision/tier at creation time using judgment
  (`DECISION_CLASSES.md`'s "How to classify" is a decision tree, not a
  derivable function of existing columns). Auto-backfilling 253 historical
  tasks from `title`/`description` text would just be re-implementing the
  same text-heuristic fallback the schema fix exists to move away from, and
  would risk *wrong* classifications being recorded as if they were
  deliberate, which is worse than leaving them unclassified.
- Almost all 253 tasks are already terminal (`APPROVED`, `DONE`, `RELEASED`,
  etc. — dispatch policy is only evaluated pre-claim, on non-terminal
  tasks). Backfilling gate inputs on tasks that will never be re-evaluated
  by `evaluate_pre_dispatch` again has no safety benefit.
- For any task still active (non-terminal) at migration time, the fix owner
  should hand-classify only that small subset using `DECISION_CLASSES.md`/
  `RISK_SYSTEM.md`'s own criteria, not a bulk script. Query:
  `SELECT task_id, title FROM tasks WHERE status NOT IN ('APPROVED','DONE','RELEASED','REJECTED','ARCHIVED')`.
- `requires_operator_approval` defaults to `0` for all existing rows, which
  is safe by construction (Section 1) and needs no backfill decision at all.

### 3. `map_task.py create` population

Add four new optional CLI flags plus the boolean flag to `create_task`'s
`argparse` block (`map_task.py:486-499`, alongside the existing
`--task-type`, `--role`, `--priority`):

```text
create.add_argument("--decision-class", choices=["ARCHITECTURE", "OWNERSHIP", "SCOPE", "AUTHORITY", "POLICY"])
create.add_argument("--risk-class", choices=["SECURITY", "DATA", "PROCESS", "AVAILABILITY", "KNOWLEDGE"])
create.add_argument("--risk-severity", choices=["COSMETIC", "DRIFT", "BLOCKING", "STRUCTURAL"])
create.add_argument("--task-tier", choices=["mechanical", "bounded", "architecture", "policy", "operator"])
create.add_argument("--requires-operator-approval", action="store_true")
```

Using `choices=` here is where the vocabulary enforcement from Section 1
actually lands — at the one place tasks are created, not as a DB constraint.
All five stay optional (no `required=True`) so routine tasks that don't need
classification aren't forced to guess one; `evaluate_pre_dispatch` already
treats absence as "unclassified," which remains a valid, common case.

The `INSERT INTO tasks` in `create_task()` (`map_task.py:182-199`) needs the
five new columns and bound parameters added. This is the only code change
inside "create a task" — no change to the claim/dispatch path itself.

**Explicitly not in scope for this plan:** deciding whether task creation
should *require* one of these five for certain `task_type`/`role`
combinations (e.g. every `task_type: architecture` task must set
`decision_class`). That's a policy decision for the fix owner + operator,
not a schema/plumbing detail — flagging it as an open question, not
answering it here.

### 4. Mirror / export path

Two additional surfaces silently drop these fields today even after the
schema fix, unless updated in the same change:

- `MAP_System/migration/export_to_files.py:63` — the `load_tasks()` SELECT
  (`SELECT task_id, title, task_type, role, status, owner, description`) and
  `task_file_payload()` (`export_to_files.py:127`) both need the five new
  fields added, or `MAP_System/tasks/TASK-*.json` and
  `MAP_System/workflow/task_graph.json` will keep omitting them from the
  durable file mirrors even once `map.db` carries real values — reproducing
  the exact "value exists but isn't visible where agents actually read it"
  failure this migration is meant to fix, just one layer further out.
- `MAP_System/scripts/validate_task_mirrors.py:25` — `SCALAR_FIELDS =
  ("title", "task_type", "role", "status", "owner")` doesn't include the new
  fields, so DB-vs-mirror drift on them wouldn't be caught. Recommend adding
  the five (well, four — `requires_operator_approval` is a bool store, not a
  drift-prone scalar text field, but worth including too) to `SCALAR_FIELDS`
  in the same change, so the existing drift gate covers them from day one
  instead of needing a follow-up ticket to notice they were never covered.

### 5. Rollback

- Schema: `ALTER TABLE ... ADD COLUMN` has no clean `DROP COLUMN` in the
  SQLite version constraints this repo otherwise assumes (the migration
  inventory notes existing columns were never dropped either) — rollback is
  "stop reading/writing the column," not "remove it." If a genuine revert is
  ever needed: rebuild `tasks` via SQLite's copy-and-swap pattern
  (`CREATE TABLE tasks_new AS SELECT <old columns> FROM tasks; DROP TABLE
  tasks; ALTER TABLE tasks_new RENAME TO tasks;`), same pattern any future
  column removal in this file would need — this migration doesn't need to
  invent that mechanism, just note it's available.
- Code: revert the `map_task.py create` flags, the `load_task_from_db`
  SELECT addition (Phase 1 also needs this — see below), and the
  `export_to_files.py`/`validate_task_mirrors.py` field lists in one commit;
  none of these three files reference each other in a way that requires a
  staged rollback order.
- No data loss risk either direction: existing rows get `NULL`/`0` on
  forward migration (Section 1), and a rollback simply stops reading columns
  that still physically exist in the file until/unless the table is
  rebuilt.

### 6. One piece not yet named above: `load_task_from_db`'s SELECT

`pre_dispatch_policy.py:420-428`'s `SELECT` must add the five new column
names, or the schema change alone accomplishes nothing — this is the exact
mechanism `test_pre_dispatch_gate_inputs.py` pins as currently absent. This
plan lists it explicitly because it is easy to do the ALTER TABLE and the
CLI flags and forget the read path, which would leave the gates just as
unreachable as today with a schema that looks fixed.

## Phase 2 — the eight predicate-backed fields (lower priority, separate change)

`destructive_action`, `final_review`, `final_decision`, `broad_architecture`,
`broad_rewrite`, `canonical_map_mutation`, `shell_required`,
`trust_boundary_crossing` have the identical schema gap (no columns, not
selected by `load_task_from_db`) but each already degrades to a working text
heuristic when absent (`is_destructive()`, `is_final_review()`, etc. — all
verified honoured when explicitly set, per the SUMMARY's "HONOURED" table).
Explicit declaration is strictly better than text inference (removes
phrasing-dependent risk), but the current state is a working approximation,
not a silent no-op. Recommend the same treatment — eight more nullable
`BOOLEAN`/`INTEGER` columns, eight more `map_task.py create` flags, the same
`load_task_from_db` SELECT and mirror/export additions — as a follow-on
change once Phase 1 lands and the drift-gate pattern (Section 4) is proven
out on a smaller field set first. Do not bundle Phase 1 and Phase 2 into one
change: Phase 1 fixes gates that are *completely* dead; Phase 2 hardens
gates that already work by another route, which is a materially lower-risk,
lower-urgency change and shouldn't block or be blocked by Phase 1.

### Phase 2 landed 2026-07-21 (implemented by claude-lab-rose, independently re-verified by claude-review-soba)

All eight fields added as nullable `INTEGER` columns (not `NOT NULL DEFAULT
0`) — a deliberate, correct deviation from Phase 1's `requires_operator_approval`
default. `as_bool()` treats `None` and `0` identically, and every predicate
function (`is_destructive()`, `is_final_review()`, etc.) checks the explicit
field before falling through to its text heuristic, so an unset task behaves
exactly as it did pre-migration — confirmed by reading `as_bool()` and by the
fact that all 255 tasks in `map.db` today have all eight fields `NULL` and
still evaluate identically to before. A `NOT NULL DEFAULT 0` here would have
asserted "confirmed not destructive" for a task nobody has classified — the
same wrong-but-recorded failure mode this plan's Section 2 already warned
against for backfilling. `map_task.py create`'s new `--destructive-action`
etc. flags (all `action="store_true"`, which argparse itself defaults to
`False`) correctly insert `None` when unset (`1 if args.destructive_action
else None`, not a raw bool cast) — verified in the diff, this is not an
incidental detail, it's the mechanism that makes the nullable-column choice
actually hold at the create path.

Both loaders (`pre_dispatch_policy.load_task_from_db`,
`graph/runner.py:load_tasks_from_sqlite`) and the mirror/export path
(`export_to_files.py`, `validate_task_mirrors.py` `SCALAR_FIELDS`, both via a
new `GATE_PREDICATE_FIELDS`/`nullable_bool()` helper that preserves
`None` distinctly from `False` through the JSON round-trip) were updated
identically to Phase 1's pattern. 8 new tests in
`test_pre_dispatch_gate_inputs.py`, one per field, each asserting a neutral-
text baseline returns `allow` (tier 1 for the two that gate core agents,
tier 2 for the six that only gate helpers) before flipping the field and
asserting the correct `require_approval`/`reject` outcome — independently
re-verified: read every baseline's task text against the literal
`contains_any`/heuristic phrase lists in `pre_dispatch_policy.py` (not just
skimmed for plausibility) and confirmed none trip a heuristic; also
independently tested all eight fields at `worker_tier=1` directly against
`evaluate_pre_dispatch()` and confirmed only `destructive_action` and
`trust_boundary_crossing` produce `require_approval` there — the other six
return `allow` at tier 1 and only `reject` at tier 2+, which is pre-existing
`evaluate_pre_dispatch()` branching (the `if tier >= 2:` block), unchanged by
either migration phase per `git diff` — not an artifact of this work. Full
suite: pass=69 fail=2, same 2 known pre-existing failures. Core agents
(tier 1) remain deliberately ungated on broad rewrites, canonical MAP
mutation, and final review/decision authority by this migration — that is
existing, unchanged trust-model behavior, not something Phase 2 was scoped
to close, and should not be read as "core agents are now fully gated."

## Explicitly out of scope for this document

- Whether `pre_dispatch_policy.py` itself needs any logic change. It
  doesn't — `test_pre_dispatch_policy.py` and
  `test_pre_dispatch_gate_inputs.py` both confirm `evaluate_pre_dispatch()`
  already does the right thing with every field once it's present on the
  dict. This is a pure plumbing gap.
- Assigning a fix owner. The operator has not done so as of this writing
  (see the parent hcom thread); this plan is input to that decision, not a
  claim on the work.
- Running any part of this plan. No `ALTER TABLE`, no backfill script, no
  `pre_dispatch_policy.py` edit was executed while producing this document,
  per the assigning agent's explicit boundary.
