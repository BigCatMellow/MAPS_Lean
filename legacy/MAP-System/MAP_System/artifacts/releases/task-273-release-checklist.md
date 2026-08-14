# Release Checklist: TASK-273

## Header

```
task_id:      TASK-273
released_by:  claude-lab-deli
release_date: 2026-07-23
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Releases the sanctioned owner-reassignment verb: `reassign_task_owner()` in
`MAP_System/db/claims.py` and the `reassign-owner` CLI verb in
`MAP_System/scripts/map_task.py`, with isolated tests registered in
`run_tests.sh`. `tasks.owner` was write-once — only `create` set it, `claim_task`
sets `claimed_by` and never `owner`, `rework` leaves it untouched, and AGENTS.md
forbids hand-editing SQLite — so a task owned by a departed agent had no
sanctioned path to a live owner. It now has one, and every use is attributable.

## Verification

- Independent review: `MAP_System/artifacts/reviews/task273-review-deli.md` —
  APPROVED. All six acceptance criteria verified by reproduced evidence, not by
  reading the submission report.
- Non-mutation (criterion 4) proved by reviewer probe against the real
  `migration/schema.sql`, not the test's synthetic table: on a task carrying a
  live claimant, a future lease, a heartbeat and `attempt=3`, the only column
  that changed was `owner`. `status`, `claimed_by`, `lease_expires_at`,
  `heartbeat_at`, `attempt`, `updated_at`, `priority`, `max_attempts`, and
  `required_agent` were byte-identical.
- Terminal refusal proved on the real schema for `DONE`, `RELEASED`, `RETIRED`
  (each returned `None` with the row unchanged); `READY`, `IN_PROGRESS`,
  `SUBMITTED`, `CHANGES_REQUESTED`, `APPROVED`, `BLOCKED`, and `CONFLICT` all
  succeeded, which is the intended surface — all 76 `APPROVED` tasks are awaiting
  release and are exactly the stale-owner population this verb exists for.
- Focused suite reproduced independently: 5/5.
- Full suite reproduced independently at **71 pass / 4 fail** before approval,
  correcting the submitted 72/3. The submitted figure was accurate when mubo
  measured it at 03:55:07Z and went stale 29 seconds later when TASK-274
  registered the same `MAP_System/db/claims.py` output path. Post-approval the
  suite is 72 pass / 3 fail, independently confirmed by `claude-lab-zaro`.
- `validate_task_graph` passes repo-wide again; the
  `TASK-273`/`TASK-274` `claims.py` collision is cleared.
- `validate_task_mirrors` passes.

## Known-Red Gates Not Caused By This Task

Three suite failures survive this release. All three predate TASK-273, touch none
of its output paths, and were verified pre-existing:

- `validate_research_artifacts` — 8 missing template fragments in
  `artifacts/research/SUMMARY-herdr-comparison-2026-07-22.md`.
- `validate_events_no_new_warnings` — one non-canonical event type
  `TASK_SUBMITTED` at `events/events.jsonl:2145`, written by `codex-lab-kiri` for
  TASK-257 on 2026-07-19, four days before this task.
- `validate_layer1_test` — asserts `overall_pass`; cascades from the event
  warning above.

## Follow-Up Boundary

- **TASK-274 must not be claimed until this release lands and TASK-268 releases.**
  TASK-274 registers the same `MAP_System/db/claims.py` output path; claiming it
  early returns the collision from the other side.
- Non-blocking findings F2–F4 are recorded in the review record and are not
  rework on this task. F2 (RECOMMENDED): `reassign_task_owner` does not bump
  `updated_at` while every other mutating verb in `claims.py` does, and
  `test_reassign_owner.py:98` now locks that behaviour in — someone should decide
  on the record whether that is the intended contract. F3/F4 (OPTIONAL): on a lost
  compare-and-swap race the CLI reports the task as terminal when it is not, and
  the `INSERT OR IGNORE` agent registration commits even though the reassignment
  failed.
- Review-separation gap unchanged and out of scope by explicit NON-GOAL: this
  task's owner is `command-center`, so `claim_review()`'s owner-keyed guard could
  not fire for any reviewer. Separation was operational. That is INS-0039 /
  IDEA-0028 and awaits its own decision.

## Emergence Capture

Considered. Nothing new to capture: the review's substantive observations are
already carried by INS-0039 (owner-keyed guards), INS-0040 (hand-maintained state
files as an unchecked second reader — reproduced today when the lane table went
stale within an hour of being rebuilt, invalidated by this very approval), and
SYN-0005 (missing verbs: there is still no remove-output-path verb and no retire
verb, which is why approval was the only reachable way to clear the collision).
