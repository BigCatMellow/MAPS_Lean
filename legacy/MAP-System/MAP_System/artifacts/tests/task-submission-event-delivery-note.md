# MAP Delivery Note — TASK-274 Durable Submission Authorship

- task: `TASK-274`
- implementer: `codex-lab-hana`
- source chain: INS-0039 → IDEA-0026 (parked) → EXP-0008 → IDEA-0027 → EXP-0009 → PROMO-0013
- approval evidence: SQLite event `1716` (`DECISION_RECORDED`, `bigboss`)
- registered outputs: `db/claims.py`, `scripts/map_task.py`,
  `scripts/run_tests.sh`, `tests/test_submission_event.py`, and this note

## Delivered Behavior

- `db.claims.submit_task()` preserves its Boolean return contract while owning
  the guarded `IN_PROGRESS` → `SUBMITTED` transition and the canonical
  `SUBMISSION` event.
- Event emission happens only after the status transaction commits. A failed or
  racing guarded update returns `False` and emits nothing. An event-log failure
  after commit leaves visible reconciliation debt rather than a false-positive
  submission record.
- The event names the submitting agent as `sender` and `actor`, includes the
  task ID and `trace_id`, and records registered task output paths.
- `map_task.py submit` passes its selected `--event-log` into the low-level API,
  removes its former duplicate append, and still exports task/graph mirrors.
- When an isolated caller omits `event_log`, a noncanonical database derives a
  sibling `events.jsonl`; scratch tests therefore never append to the
  production `MAP_System/events/events.jsonl`.

## Evidence and Safety Interpretation

EXP-0008 established that submission authorship could not be recovered
reliably: a meaningful share of approvals lacked a durable submission event.
EXP-0009 proved the post-commit event mechanism and unchanged Boolean contract
on a scratch database. This implementation also closes EXP-0009's P1
integration finding by making the event-log destination explicit and
scratch-safe.

Absence of a `SUBMISSION` event means **UNKNOWN AUTHOR**. It is never evidence that no self-review occurred. Any future authorship-based review guard must fail
closed or request additional evidence when the event is absent; it must not
infer innocence from missing history.

## Focused Verification

`MAP_System/tests/test_submission_event.py` covers:

- correct actor/task/trace fields in SQLite and JSONL;
- unchanged submitted task-row shape and Boolean return;
- repeat submission with no duplicate;
- wrong-claimant failure with no mutation or event;
- simulated lost-race refusal with no event;
- scratch-default event-log isolation from production;
- event-log failure occurring only after the committed transition;
- the `UNKNOWN AUTHOR` interpretation above.

The test is registered in `MAP_System/scripts/run_tests.sh`. The independent
reviewer must be neither `codex-lab-hana` nor `claude-lab-bima`.

Focused verification passed on 2026-07-26:

- 7/7 TASK-274 submission-event regressions;
- 3/3 TASK-268 lifecycle compatibility regressions;
- 5/5 owner-reassignment regressions;
- task graph, task schema, and task mirror validators.

The full test runner completed with 74 passes and 4 failures, all caused by
pre-existing canonical-state debt outside TASK-274's registered outputs:
the malformed `SUMMARY-herdr-comparison-2026-07-22.md`, the expected
`current-state.md` drift while TASK-274 is actively claimed, and two event
checks that surface the historical noncanonical `TASK_SUBMITTED` event at
`events.jsonl` line 2145. TASK-274's new event uses canonical `SUBMISSION` and
adds no warning; its acceptance criterion explicitly identifies line 2145 as
pre-existing.

## Deliberate Non-Goals

- No review guard changes.
- No historical submission-event backfill.
- No change to `tasks.owner` semantics.
- No inference about self-review from missing events.
