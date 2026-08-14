# TASK-295 Delivery Note: Sanctioned `map_task.py retire` Verb

## What was built

- `MAP_System/db/claims.py`: `retire_task(task_id, actor_id, reason, *,
  db_path=DEFAULT_DB)` — the guarded, atomic primitive. Refuses a task
  already in `TERMINAL_TASK_STATUSES` (`DONE`/`RELEASED`/`RETIRED`, the same
  constant `reassign_task_owner` uses), refuses a blank actor or reason, and
  otherwise moves the task to `RETIRED`, clearing `claimed_by`/
  `lease_expires_at`/`heartbeat_at`. Deliberately allows retiring from **any**
  other nonterminal status, including `APPROVED` (TASK-053's own shape) and
  `CHANGES_REQUESTED` (TASK-241–248's shape under TASK-254) — retirement is a
  closure of abandoned/superseded work, not a review verdict, so it does not
  reuse `extend_task_attempts`'s narrower `TERMINAL_ATTEMPT_STATUSES` (which
  also excludes `APPROVED`).
- `MAP_System/scripts/map_task.py`: `retire` subcommand (`task_id --actor
  --reason`), matching `extend-attempts`/`reassign-owner`'s CLI shape --
  calls the claims primitive, raises a clean `UsageError` with the refusal
  reason on `None`, appends a `PROGRESS` event naming actor/prior-status/
  reason, and re-exports mirrors.
- `MAP_System/tests/test_map_task_retire.py`: 8 focused tests -- successful
  retirement from `APPROVED` (TASK-053's shape) and from
  `READY`/`IN_PROGRESS`/`SUBMITTED`/`CHANGES_REQUESTED`/`BLOCKED`/`CONFLICT`;
  refusal on each terminal status with no state change; refusal on blank
  reason/actor; unknown task returns `None`; and two CLI end-to-end tests
  (event + mirror sync on success, nonzero exit + unchanged DB row on a
  terminal-status refusal). Wired into `run_tests.sh` immediately after
  `map_task_extend_attempts_test`.

All 8 new tests pass standalone; the full `run_tests.sh` run shows
pass=77/fail=4/total=81, and the 4 failures
(`validate_research_artifacts`, `validate_shared_state_tasks`,
`validate_events_no_new_warnings`, `validate_layer1_test`) are the
pre-existing, already-documented failures from the 2026-07-28 release-backlog
triage (`artifacts/planning/release-backlog-triage-2026-07-28.md`, "Patterns
found" #4) -- unrelated to this task's files and unchanged by it.

## Criterion 4: full lifecycle-transition enumeration

Canonical status vocabulary (`validate_task_schema.py`/
`validate_shared_state_tasks.py`): `NEEDS_SHAPING` (create-only, not in the
enum but produced by `create_task`), `READY`, `IN_PROGRESS`, `SUBMITTED`,
`REVIEW`, `CHANGES_REQUESTED`, `BLOCKED`, `CONFLICT`, `APPROVED`, `RELEASED`,
`DONE`, `RETIRED`.

**Now has a sanctioned verb, after TASK-293 and this task:**

| Transition | Verb |
|---|---|
| (none) → `READY`/`NEEDS_SHAPING` | `map_task.py create` |
| `READY`/expired `IN_PROGRESS` → `IN_PROGRESS` | `db.claims.claim_task` (no CLI wrapper; used directly per `AGENTS.md`) |
| `IN_PROGRESS` → `SUBMITTED` | `map_task.py submit` |
| `SUBMITTED` → `APPROVED` | `map_task.py approve` |
| `SUBMITTED` → `CHANGES_REQUESTED` | `map_task.py reject` |
| `CHANGES_REQUESTED` → `READY` | `map_task.py rework` |
| `APPROVED` → `RELEASED` | `map_task.py release` |
| orphaned `IN_PROGRESS` (no claimant, no live lease) → `READY` | `map_task.py recover-orphan` |
| expired-lease `IN_PROGRESS` → `READY` (automatic reconciliation, not a manual verb) | `db.claims.expire_leases` |
| nonterminal → `CONFLICT` | `scripts/flag_conflict.py` (HPOM-008; a dedicated script, not a `map_task.py` subcommand, but gated/evented) |
| owner change (any nonterminal status, no status change) | `map_task.py reassign-owner` |
| `max_attempts` change (nonterminal minus `APPROVED`/`RELEASED`/`RETIRED`/`DONE`) | `map_task.py extend-attempts` (TASK-293) |
| additional `output_paths` entry (editable states only) | `map_task.py add-output-path` |
| any nonterminal → `RETIRED` | `map_task.py retire` (**this task**) |

**Still verb-less after both land -- named explicitly, not rediscovered a
fourth time:**

1. **Amending an existing task's `description`/`acceptance_criteria`/`title`
   after creation.** This is not hypothetical: it is the exact gap
   `mapfinish-kino`'s TASK-254 review (`artifacts/reviews/task254-review-kino.md`)
   found blocking right now -- TASK-254's acceptance criterion 4 needs a real,
   authorized edit to the task record (kino's required action (a)), and no
   `map_task.py` verb can do that; the only route left is either a raw-SQL
   `UPDATE tasks SET description=...` (now blocked by the harness permission
   classifier for canonical task state, same class of block this task
   responds to) or a companion planning-doc addendum, which kino correctly
   rejected as reinterpretation-not-amendment. This is the single highest-
   priority next gap: a task actively stuck in the release queue needs it.
2. **Removing or editing an existing `output_paths` row.** `add-output-path`
   is additive-only (REPAIR-0009's original finding); there is still no
   sanctioned way to retract a path that turns out to be wrong or to belong
   to a different task, only to add more.
3. **Resolving a `CONFLICT` back to a working status with a recorded
   resolution.** `flag_conflict.py` enters `CONFLICT`; `promote_task.py`
   explicitly refuses to touch a `CONFLICT` task ("resolve the conflict
   before promoting to READY"). No script performs the paired exit
   transition -- whatever currently resolves a conflict record does so
   without a verb of its own.
4. **Editing `decision_class`/`risk_class`/`risk_severity`/`task_tier`/
   `requires_operator_approval` after creation.** If a task's risk
   classification is found wrong post-creation (e.g. a security-relevant
   output path was added later via `add-output-path` and the task was never
   re-classified), nothing updates these fields short of raw SQL.

**Not a live gap, flagged only so it is not mistaken for one:** `DONE` and
`REVIEW` are in the canonical vocabulary but no current script assigns
either -- `cost_yield.py` maps `DONE` to `"legacy_done"` (a status prior
tooling produced, not current tooling), and `REVIEW` does not appear as a
write target anywhere in `db/claims.py` or `scripts/*.py`. No verb is needed
for a transition nothing currently produces; if either becomes live again,
the gap should be re-evaluated then, not pre-built speculatively.

## Precedent this does not disturb

Per the assignment, the 16 tasks already `RETIRED` via raw SQL (TASK-241–248
under TASK-254, plus TASK-053 and others) are **not** retroactively rewritten
through this verb. They remain historical, as-is.
