# Release Checklist: TASK-237

## Header

```
task_id:      TASK-237
released_by:  mapfinish-guru
release_date: 2026-07-28
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

AIM-style operator attention popup queue for CommandCenterUI (unanswered
requests/approval gates/terminal prompts, explicit operator actions only, no
automatic approve/send). Touches
`templates/install/command-center-ui/...`, classifies `full` tier.

**Deliverable verified today** (independent check):

- All 8 output paths exist on disk, including both the live
  (`../../CommandCenterUI/src/chat.*`) and template copies.
- `grep -c attention-popup` on the **live** `chat.html`/`chat.js` returns
  14/11 real hits — the feature is deployed in the app the operator actually
  runs, not only present in the installer template.
- `MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_command_center_attention_popup -v`:
  **4/4 pass**, covering exactly this task's three acceptance criteria:
  `test_popup_queues_all_existing_attention_types` (queuing without
  duplicating a seen item), `test_popup_has_explicit_operator_actions` +
  `test_popup_never_approves_or_sends_automatically` (no automatic action),
  and `test_popup_is_visually_distinct`.
- Single clean submission/approval cycle: submitted by codex-lab-kiri
  2026-07-18T19:29:34Z citing "Node syntax checks and 4 focused tests
  passed," approved same day by claude-lab-lure with no rework round.

**Shared-file updates complete**: `MAP_System/artifacts/tests/task237-attention-popup.md`
is the task's own durable verification record; no MAP canonical doc required
a change for this task's scope.

**Decisions recorded**: none required — a bounded UI feature with an
explicit no-automatic-action constraint enforced by its own tests, not a
policy/authority question. `decision_class=null`,
`requires_operator_approval=false`, unchallenged since creation.

**Follow-up tasks created**: none needed — `task_dependencies` shows nothing
depends on TASK-237, and its review history is a single clean pass with no
open follow-up implied.

**Event log entry prepared**: appended automatically by `map_task.py
release`.

**Emergence capture considered**: considered, none warranted — this is a
routine, cleanly-approved UI feature with no novel pattern beyond what
`AGENTS.md`'s existing "no automatic action" conventions already cover.
