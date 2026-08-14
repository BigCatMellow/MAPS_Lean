# Release Checklist: TASK-225

## Header

```
task_id:      TASK-225
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

Visible local MAP Steward attention assistant (advisory-only, read-only
packet + optional qwen3.5:4b summarization). Touches
`templates/install/command-center-ui/...`, classifies `full` tier.

**Deliverable verified today** (independent check):

- All 8 output paths exist on disk.
- `MAP_System/templates/install/command-center-ui/app/server.py:73-74`
  defines `STEWARD_STATE_PATH`/`STEWARD_SCRIPT`, wiring the steward into the
  server. `grep -c steward` on both live (`/home/mellow/Projects/
  CommandCenterUI/{app/server.py,src/chat.js,src/chat.html}`) and template
  copies both show real hit counts (18/23/14 live; matching template) —
  confirms this is deployed in the live app the operator actually runs, not
  only present in the installer template.
- `MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_map_steward -v`:
  **6/6 pass**, including `test_writes_only_explicit_state_path` (privacy/
  source-bounds guarantee), `test_model_failure_falls_back_without_actions`
  and `test_model_parser_rejects_prose_and_oversized_output` (Ollama-
  unavailable and malformed-output handling), and
  `test_stop_persists_until_explicit_resume` — this last one is the exact
  fix for the one rejection this task took (see below), confirmed passing
  now, not just claimed fixed at review time.

**Shared-file updates complete**: `MAP_System/artifacts/command-center-ui/map-steward.md`
documents the steward for operators; no MAP canonical doc required a change
for this task's own scope.

**Decisions recorded**: none required beyond the task's own description,
which records the operating boundary directly ("The steward is advisory: it
cannot edit code/policy, approve/promote, claim tasks, message the operator
autonomously, or spawn agents... every model-backed interactive/curation
session remains visible in wezterm-tab") — this constraint is enforced in
code (`test_writes_only_explicit_state_path`, no task/policy-mutation calls
in `map_steward.py`), not merely asserted. `decision_class=null` /
`requires_operator_approval=false` on the task record, unchallenged. No
`REQUIRE_*` pre-dispatch policy gate applies.

**Follow-up tasks created**: none needed — TASK-225 is a terminal leaf in
`task_dependencies` (nothing currently depends on it) and its own review
history shows exactly one rejection/rework cycle, fully closed:
`helper-review-steward-moku` rejected once (2026-07-18) for "Command Center
does not visibly render steward inputs and Stop is ineffective," codex-lab-lilo
reworked, moku approved the same day. Not stuck, not silently patched.

**Event log entry prepared**: appended automatically by `map_task.py
release`.

**Emergence capture considered**: considered, none warranted — the
advisory/no-mutation boundary this task establishes is already the pattern
`notes/helper-agent-guide.md`/`AGENTS.md`'s Elastic Helper Agents section
codifies generally; nothing steward-specific rises to a new insight.
