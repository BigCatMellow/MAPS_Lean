# Release Checklist: TASK-293

## Header

```
task_id:      TASK-293
released_by:  mapfinish2-dove
release_date: 2026-07-28
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Adds a sanctioned `map_task.py extend-attempts` verb so attempt-budget
repairs are auditable, gated, and mirror-synchronized instead of raw SQL —
the second occurrence of this repair class in two days (REPAIR-0010,
raw SQL; REPAIR-0012, this verb). Includes a calibration judgment: default
`max_attempts=3` is left as-is, on the reasoning that both prior exhaustions
were evidence of thorough review converging slowly, not of a systematically
too-tight default.

**Checklist evidence:**

- **Shared-file updates complete:** not applicable in the shared/-folder
  sense — outputs are `db/claims.py`, `scripts/map_task.py`,
  `scripts/run_tests.sh`, and a test file. No shared/canonical doc required
  updating; the calibration judgment itself is recorded in the task's own
  description (appended 2026-07-28T16:49:34Z per acceptance criterion 5),
  which is the durable record this task's scope calls for.
- **Decisions recorded:** this task's `decision_class` is blank but
  `task_tier=policy` and `risk_severity=STRUCTURAL`. No standalone DEC-NNN
  or DECISION_RECORDED event names TASK-293 directly, but the authority
  chain for applying it is durably recorded: `REPAIR-0012` cites bigboss's
  standing batch authorization ("You have my permission to approve whatever
  needs to be done," 2026-07-28) as the STRUCTURAL approval basis, and a
  separate DEC entry (`shared/decisions.md` line ~1040, in the Sonnet/auto-
  mode-default decision) independently corroborates the same event: "the
  classifier still blocks unmediated mutations of canonical state, as it did
  to a raw-SQL `max_attempts` update on 2026-07-28 (REPAIR-0012), which is
  what prompted building the sanctioned verb in TASK-293 instead." Two
  independent durable records agree on the same authorization chain.
- **Follow-up tasks created:** yes, indirectly — the same missing-verb
  pattern this task fixes for attempt-budgets is explicitly named as
  precedent in TASK-295 (retire verb) and TASK-297 (criterion-amendment
  verb), both of which cite "REPAIR-0010/0012 (attempt budgets, fixed by
  TASK-293)" as the completed instance their own scope is modeled on.
- **Event log entry prepared:** clean single-pass lifecycle in
  `events.jsonl` — creation (2026-07-28T12:31:26Z), output-path
  registration, description amendment for the calibration judgment,
  `SUBMISSION` (16:49:48Z), `APPROVED` (16:54:48Z, `lili-replacement-nisa`,
  who "verified all four guard rails by direct exercise against a scratch
  database rather than trusting the test suite"), no rework needed. Beyond
  its own lifecycle, the verb's real-world use is independently evented:
  TASK-263's rework event (2026-07-28T16:56:48Z) states "Attempt budget
  extended to 4 via the sanctioned extend-attempts verb (REPAIR-0012),"
  and `REPAIR-0012`'s own record shows the actual CLI invocation and
  output (`prior_max_attempts: 3, new_max_attempts: 4, attempt: 3`) plus
  confirms the same verb also unblocked TASK-254. This release appends
  the canonical `RELEASED` event.
- **Emergence capture considered:** considered; no `emergence/` record
  names TASK-293 directly. None additional warranted — `REPAIR-0012`'s own
  "Notes" section already captures the systemic finding (attempt budgets
  count submissions, not defects; tier-scaling should be considered before
  any future global bump), which is a durable, cross-referenced repair
  record rather than a gap.

## Verification

- All 4 output paths confirmed to exist.
- `test_map_task_extend_attempts.py`: 9/9 PASS, independently re-run
  directly (not taken from the submission report): successful extension,
  refuses terminal statuses, refuses lowering below current attempt,
  requires a reason/actor/positive target, unknown-task returns `None`,
  CLI records an auditable event and syncs mirrors, CLI refuses
  simultaneous/absent `--max-attempts`/`--add`.
- Independent review: `artifacts/reviews/task293-review-lili-replacement-
  nisa.md` — APPROVED, reviewer explicitly exercised the guard rails
  directly against a scratch database rather than relying on the test
  suite alone.
- **Live production verification, not just test coverage:** confirmed via
  `sqlite3` against the real `map.db` that `TASK-263.max_attempts=4` and
  `TASK-254.max_attempts=4` today, both above the 3 default, both
  attributable to this verb per the events and repair record cited above —
  the two real invocations the requester asked me to confirm both check
  out.
- Follow-up-pattern precedent confirmed live: `MAP_System/tasks/TASK-295.
  json` and `TASK-297.json`, read directly, both name TASK-293 as the
  completed precedent for the next two verb-gap fixes.
