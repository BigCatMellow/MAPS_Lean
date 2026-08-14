<!-- hpom: file: artifacts/releases/task-269-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-23 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-269

## Header

```
task_id:      TASK-269
released_by:  claude-lab-gabi
release_date: 2026-07-23
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Makes the helper model tier durable and checkable. `notes/helper-agent-guide.md`
has always required the **approved** model tier to be recorded (lines 148, 152),
but the helper-note metadata contract in `AGENTS.md` had no field to put it in.
Measured 2026-07-22: 6 of 82 helper notes carried any tier and 2 named a model
at all. A rule with nowhere to write its answer is not enforceable, which is why
the operator observed agents not being used at the right model level.

**What changed:**

- `AGENTS.md` helper-note contract gains `model:`, explicitly the **approved**
  tier rather than the requested one, with a note that `provider` names the
  system that ran the helper and therefore cannot answer whether the tier rubric
  was followed. When the approved tier is above the Haiku default, the approver
  and the skipped lower tier are recorded in the note.
- `graph/runner.py` reports active helper notes with no `model` line as
  `helpers_missing_model_tier`, in both the JSON output and an events line.
  Scoped to **active** notes deliberately: a finished note is historical
  evidence and is not reopened to backfill, so flagging it would be permanent
  unfixable noise. The reviewer challenged this scope and upheld it.
- `notes/helper-agent-guide.md` points at the contract field, so the requirement
  and its storage location are no longer in two disconnected documents.

**Implementation note worth carrying forward.** The first cut computed
`helpers_missing_model_tier` correctly and its unit tests passed, but the field
arrived **empty** in real runner output while the events line correctly named
one helper: `MapState` is a `TypedDict` and the graph drops keys it does not
declare. The unit tests could not see this because they call `scan_helper_notes`
directly. Caught only by running the real runner. A fifth test now asserts the
key is declared on `MapState`.

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_runner_helper_notes.py` —
  4 pass, covering a recorded tier, a missing tier, a blank tier counting as
  missing, a non-active note correctly NOT reported, and the `MapState`
  declaration.
- Live runner output confirms the mechanism works on real state: it currently
  reports `helper-local-map-advisor-4b-2026-07-18` as untiered.
- `bash MAP_System/scripts/run_tests.sh` — pass=72 fail=2 at time of release.
  The two failures are the pre-existing non-canonical `TASK_SUBMITTED` event at
  `events/events.jsonl:2145` and are unrelated.
- Independent review: `artifacts/reviews/task269-review-lime.md` — APPROVED
  after the reviewer verified live runner propagation, unchanged helper capacity
  accounting, focused behavior, the `MapState` declaration, and two mutation
  failures.

## Known non-blocking follow-up

The reviewer logged that metadata parsing detects a `model` field's presence but
does not validate tier vocabulary and does not restrict fields to the opening
block. Deliberately **not** hardened here: build it only if abuse is actually
observed, rather than pre-emptively.

## Related records

- Same SYN-0001 shape as the other findings in this batch: one piece of state
  (helper model tier) with two readers (the guide requires it, the contract had
  nowhere to store it) and no declared authority.
- Sibling instances: TASK-270 (`claim_review` identity), INS-0038
  (`claim_task` / mirror sync).
