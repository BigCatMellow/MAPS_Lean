# Release Checklist: TASK-268

## Header

```
task_id:      TASK-268
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

Adds one sanctioned synchronized submission verb (`map_task.py submit`,
wrapping `db/claims.py submit_task()`) that verifies the current claimant,
transitions SQLite to `SUBMITTED`, appends a canonical `SUBMISSION` event, and
syncs task/graph mirrors — plus an explicit review-claim identity contract so
an unregistered reviewer gets a diagnosable failure instead of a false
"already claimed."

**Checklist evidence:**

- **Shared-file updates complete:** `MAP_System/AGENTS.md`'s "Task Claiming
  (SQLite)" section, read directly, documents exactly this verb today:
  `MAP_System/.venv/bin/python MAP_System/scripts/map_task.py submit TASK-NNN
  --actor your-agent-id` — "This synchronized command verifies the current
  claimant, transitions SQLite to SUBMITTED, appends the canonical SUBMISSION
  event, and exports the task and graph mirrors." This is the task's own
  registered output path and matches its acceptance criteria verbatim.
- **Decisions recorded:** no decision_class is set on this task and no
  DEC-NNN/DECISION_RECORDED event exists for it. Not needed: this is a
  bounded, within-scope lifecycle-verb fix (a missing synchronized wrapper
  around an existing primitive), not a project-direction call.
- **Follow-up tasks created:** none created directly by this task. Not
  needed: its own acceptance criteria are self-contained (add the verb, fix
  the review-claim identity contract, prove both live); the broader
  submission-authorship gap it exposed was already tracked independently as
  TASK-274 (created earlier, 2026-07-23, from IDEA-0027) and is being
  released alongside it in this same batch.
- **Event log entry prepared:** `events.jsonl` carries the full lifecycle —
  creation (2026-07-22T18:33:13Z), output-path registration, `SUBMISSION`
  (2026-07-26T18:43:21Z), `APPROVED` (2026-07-26T19:05:04Z, `codex-lab-lilo`).
  This release appends the canonical `RELEASED` event.
- **Emergence capture considered:** yes — IDEA-0026, IDEA-0027,
  INS-0040, PROMO-0013, and EXP-0009 all name TASK-268 directly in
  `MAP_System/emergence/`, capturing the durable-authorship gap this task
  helped close (jointly with TASK-274).

## Verification

- All 5 output paths confirmed to exist: `MAP_System/AGENTS.md`,
  `artifacts/planning/task268-lifecycle-authority-contract.md`,
  `repairs/REPAIR-0008-task278-map-task-output-defer.md`,
  `scripts/map_task.py`, `tests/test_task268_lifecycle.py`.
- `MAP_System/.venv/bin/python MAP_System/tests/test_task268_lifecycle.py`
  passes as part of the full `run_tests.sh` run (73/79 pass; the 6 failures
  are pre-existing and unrelated — `validate_research_artifacts`,
  `validate_shared_state_tasks` (TASK-263/254/289 drift), `validate_events_
  no_new_warnings`, `validate_layer1_test`, `local_ollama_lane_test`).
- Independent review: `APPROVED` by `codex-lab-lilo`, 2026-07-26T19:05:04Z.
