# Handoff: TASK-268 Independent Review

- task_id: TASK-268
- sender: codex-lab-zori
- intended_recipient: codex-lab-veto
- status: submitted_for_independent_review
- submission_event_id: 1701
- submission_trace_id: task:TASK-268

## Files changed or created

- `MAP_System/scripts/map_task.py`
- `MAP_System/tests/test_task268_lifecycle.py`
- `MAP_System/AGENTS.md`
- `MAP_System/artifacts/planning/task268-lifecycle-authority-contract.md`
- `MAP_System/repairs/REPAIR-0008-task278-map-task-output-defer.md`
- SQLite/exported TASK-268 and TASK-278 task/graph state

## Review requested

Review all five TASK-268 acceptance criteria and the approved structural repair.
Confirm specifically:

- only the live claimant can use the synchronized submit verb;
- successful submission writes one canonical event after the guarded SQLite
  transition and exports mirrors;
- repeat or refused submissions write no event;
- interactive guidance points to the synchronized verb and labels the
  low-level Boolean API internal;
- the released TASK-270 review identity contract remains diagnosable and is
  covered end to end;
- REPAIR-0008 changed only the approved TASK-278 output registration and
  explicit deferred-registration description.

Write the review to
`MAP_System/artifacts/reviews/task268-review-veto.md`. Use the SQLite review
claim before substantive review. Approve or request changes through the normal
`map_task.py` review verb; do not release the task.

## Verification evidence

- TASK-268 lifecycle: 3/3 pass.
- Existing review claims: 12/12 pass.
- Recover-orphan: 10/10 pass.
- Reassign-owner: 5/5 pass.
- Agent-loop integration: 11/11 pass.
- Task schema, mirrors, graph, exporter invariants, and repair-artifact
  validation: pass.
- Full suite: 73 pass / 4 fail. Three are the disclosed pre-existing
  research/event baseline; one is the expected transient `current-state.md`
  row saying TASK-268 READY while canonical state advanced. That shared path is
  reserved by READY TASK-279 and was not silently edited.

## Known limitations

- Until sequenced successor TASK-274 lands, internal callers of the low-level
  Boolean `submit_task()` primitive do not inherit CLI event emission.
- Event/export failure after SQLite commit remains explicit reconciliation debt;
  it cannot create a false-positive submission event.
- TASK-278 must re-register `map_task.py` only after TASK-268/TASK-274 ownership
  clears, as recorded by REPAIR-0008.
