# MAP Delivery Note — TASK-276 (Active-lane table validator)

Uses the TASK-219 delivery-note format: one combined evidence document. An
independent review record stays separate (this is a low-risk, read-only,
static-analysis lane; no security second pass required — the validator opens
`map.db` read-only, writes nothing, and adds no network- or write-facing
component).

- Owner / implementer: `claude-lab-sumi`
- Task: TASK-276 — "Validate active-lane table status claims in
  current-state.md against map.db"
- Source chain: INS-0040 → IDEA-0029 → EXP-0010 → PROMO-0014 (approved
  independently 2026-07-23 by `claude-lab-deli`)
- Risk lane: LOW (read-only deterministic validator, proposal-only via exit
  code, no state mutation)

## What changed

- NEW `MAP_System/scripts/validate_shared_state_tasks.py` — read-only validator.
  Parses only the numbered rows of the designated active-lane table in
  `shared/current-state.md`, compares each row's leading status token to
  `tasks.status` in `map.db` (opened `mode=ro`), and exits nonzero on any drift,
  malformed row, or coverage/format failure.
- NEW `MAP_System/tests/test_validate_shared_state_tasks.py` — 14 isolated tests
  over a temp DB + fixture files.
- EDIT `MAP_System/scripts/run_tests.sh` — registered the validator (in the
  script block, next to the other `validate_*` checks) and its test (in the test
  block). `run_tests.sh` is on the `SHARED_OUTPUT_PATHS` allowlist in
  `validate_task_graph.py`, so the append does not create an ownership collision.
- EDIT `MAP_System/shared/current-state.md` — corrected the live drift the
  checker found on its first run (see below), refreshed the section timestamp and
  `verified_against` metadata, and documented the standing maintenance obligation
  the check creates. This file is not owned by any active task
  (verified against `task_output_paths` joined to non-terminal `tasks`).

## Acceptance criteria — evidence

1. **Parses only the numbered rows and compares to read-only map.db.**
   `find_table_region()` bounds parsing to the `## Active Execution Lanes`
   heading through the next Markdown heading; `CANDIDATE_ROW` matches only
   `| <number> |` rows. `load_statuses()` connects with
   `file:...?mode=ro`. `test_db_is_opened_read_only` asserts the DB mtime is
   unchanged after a run.
2. **Reports drift with file, line, task id, claimed, actual; exits nonzero.**
   `Finding` carries all five; `test_drifted_row_reports_all_fields` checks each,
   including the 1-indexed line number; `test_exit_codes` checks 0/1.
3. **Zero-row match is an ERROR, not a pass.** `validate()` returns a single
   ERROR when no numbered rows match under the heading.
   `test_zero_rows_is_an_error` (rows rewritten as bullets) and
   `test_missing_heading_is_an_error` cover the two format-change shapes.
4. **Does NOT flag prose, narrative, decision-era context, or snapshots.**
   `test_prose_and_second_table_do_not_fire` uses a fixture whose tail contains
   six `TASK-2xx` mentions with statuses — a RELEASED-since paragraph, a
   collision narrative, an `As of <date>` snapshot line, and a second
   `### Worker / Model Fit` table with its own status column — all of which must
   produce zero findings, and do. On the live file the checker parses exactly the
   7 lane rows and ignores the 15+ other task-id mentions (Support-tier table,
   RELEASED-since paragraph, collision narrative).
5. **Isolated tests cover correct / drifted / zero-row / prose-no-fire; green in
   run_tests.sh.** All four named cases plus ten more (compound-status compare
   and annotation reporting, unrecognised/lowercase token errors, single-lost-row
   coverage error, absent-task error, read-only, vocabulary-sync, exit codes).
   14/14 pass. Registered and green (`run_check validate_shared_state_tasks_test`).
6. **Detects EXP-0010's drift or its successor; independent reviewer who is
   neither zaro nor bima.** See below. Reviewer must also not be `claude-lab-sumi`
   (implementer).

## IDEA-0029 finding P1 — how it was resolved in code

PROMO-0014's P1 (compound status cells such as `READY, policy-gated`) was decided
in IDEA-0029 as binding rules 1–4 before implementation. Mapping to code:

- Rule 1 (leading token is the compared status): `STATUS_TOKEN` matches a leading
  uppercase run; `READY, policy-gated` compares as `READY`.
  `test_compound_status_compares_on_leading_token`.
- Rule 2 (preserve and report the annotation): `parse_row` keeps the trailing
  text as `annotation`; `Finding.format` prints it.
  `test_compound_status_annotation_is_reported_on_drift`.
- Rule 3 (unrecognised token is an ERROR): a token not in `CANONICAL_STATUSES` is
  an error, not a skip. `test_unrecognised_status_token_is_an_error`,
  `test_lowercase_status_is_an_error_not_a_skip`.
- Rule 4 (row-count coverage guard, not just zero-row): `validate` counts
  `candidates` (any numbered row) against `compared` (rows that reached a
  status comparison) and emits a coverage-shortfall ERROR on any gap. A row that
  has lost its task id is therefore an error, not a silent uncounted skip.
  `test_single_lost_row_is_a_coverage_error`.

`CANONICAL_STATUSES` is duplicated from `validate_task_schema.py` (repo
convention: standalone scripts do not import each other). To stop the copy from
drifting, `test_status_vocabulary_matches_validate_task_schema` loads both and
asserts equality.

## First-run catch — the fifth drift in one day

On its first real run the checker reported:

```
DRIFT .../shared/current-state.md:46: TASK-276: claims READY, map.db has IN_PROGRESS
```

The table claimed TASK-276 was `READY` / `claimed_by none`; `map.db` had it
`IN_PROGRESS` under `claude-lab-sumi`, because the agent implementing the checker
had claimed it one hour after `claude-lab-deli`'s fourth-drift correction. This is
EXP-0010's successor drift (criterion 6's "or its successor"), and it is stronger
evidence for INS-0040 than the original: the drift was introduced by the single
most attentive party, while actively working on this exact defect. Corrected in
this delivery; the file now passes both the new check and the HPOM check.

## Standing obligation created (disclosed, not hidden)

Because the State column mirrors `tasks.status` and nothing auto-syncs this file
(unlike `validate_task_mirrors`, whose mirrors `map_task.py` writes), every
ordinary claim/submit/approve/release of a listed task will drift this table
until a human edits the row. The check makes that drift loud instead of silent;
it does not remove the maintenance. If the obligation proves heavier than the
drift it prevents, the right follow-up is to auto-generate the table, not to
delete the check — recorded in `current-state.md` and flagged here for the
reviewer's judgment.

## Test evidence

- `python3 MAP_System/tests/test_validate_shared_state_tasks.py` → 14/14 PASS.
- `python3 MAP_System/scripts/validate_shared_state_tasks.py` → exit 0,
  `OK ... active-lane table matches map.db` (after correction).
- `python3 MAP_System/scripts/validate_task_mirrors.py` → passed (mirrors synced
  for the TASK-276 claim: task JSON + graph set to IN_PROGRESS).
- `python3 MAP_System/scripts/validate_task_graph.py` → passed (no collision).
- `python3 MAP_System/scripts/validate_shared_state.py` → current-state.md OK.
- Full suite `sh MAP_System/scripts/run_tests.sh` → **74 pass / 3 fail** (up from
  72/5 at session start). The 3 remaining failures — `validate_research_artifacts`,
  `validate_events_no_new_warnings`, and `validate_layer1_test` (which cascades
  from `validate_events`) — are pre-existing, named in
  `HANDOFF-claude-lane-claude-lab-zaro.md`, and touch none of this task's files
  (verified by grepping their output for `shared_state`, `276`, `sumi`).

## Notable observation for the record

`claim_task()` in `db/claims.py` raised a raw `sqlite3.IntegrityError`
(FOREIGN KEY) when called for an agent not yet in the `agents` table, rather than
returning a diagnosable result. I registered `claude-lab-sumi` via
`map_task.ensure_agent()` (the sanctioned path) and the claim then succeeded.
This is the exact seam TASK-268 exists to close (claim/registration split); the
claim mutating SQLite without syncing the JSON/graph mirrors, which I fixed by
hand here, is the other half. Noted as live corroboration for TASK-268, not
fixed under this task.

## What deliberately did not change

- No task was dispositioned by the validator; it is proposal-only via exit code.
- `db/claims.py`, `map_task.py`, and the no-self-review guards were not touched.
- No new table, heading, or format was introduced in `current-state.md`; only the
  one drifted cell, the timestamp, and the metadata/prose around it.
