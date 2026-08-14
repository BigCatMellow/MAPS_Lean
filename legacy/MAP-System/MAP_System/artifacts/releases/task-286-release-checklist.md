# Release Checklist: TASK-286

## Header

```
task_id:      TASK-286
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

Implements the operator-directed lifecycle correction found during the
roles-roadmap run: default CCL startup now opens only the operator surfaces
and one core Codex orchestrator; Claude, scout/helper, Pi, and Librarian
lanes remain available on demand but no longer auto-start, with routing
driven from SQLite/the runner rather than terminal presence.

**Checklist evidence:**

- **Shared-file updates complete:** `MAP_System/templates/install/wezterm/
  ai-command-center-lab.lua`, read directly, carries the change live:
  "TASK-286: default topology is minimal and orchestrator-driven... Claude,
  Pi, Librarian, and scout/helper lanes stay... but do not auto-start."
  `MAP_System/templates/install/bin/ai-command-center-lab-codex`, read
  directly, carries the full orchestrator routing contract as the launch
  prompt itself. `MAP_System/notes/command-center-orchestrator-lifecycle.md`
  is the durable contract doc these two reference.
- **Decisions recorded:** yes — `DECISION_RECORDED`, 2026-07-26T19:45:38Z,
  `bigboss`, directly on this task's own creation: "Operator directed MAP
  to keep working until complete and to handle orchestration more
  effectively; this authorizes TASK-286 registered structural CCL startup
  and lifecycle scope." The task itself was operator-created
  (`bigboss`, not a core agent), so authorization is at the point of
  origin, not retrofitted.
- **Follow-up tasks created:** none created directly. Not needed: scope is
  self-contained per its own acceptance criteria (minimal startup, on-demand
  lane launch, no headless/approval/privacy/review-separation/continuity
  regression).
- **Event log entry prepared:** clean single-pass lifecycle in
  `events.jsonl` — creation (2026-07-26T19:45:15Z), operator authorization,
  `SUBMISSION` (2026-07-27T17:53:27Z), one disclosed review-conflict note,
  then `APPROVED` (18:02:45Z) by a freshly spawned helper reviewer
  (`helper-review-task-286-gina`). This release appends the canonical
  `RELEASED` event.
- **Emergence capture considered:** considered; no `emergence/` record
  names TASK-286 directly, and none is warranted — cleanly approved after
  direct operator authorization, no rework, no new systemic finding beyond
  what its own review covered.

## Verification

- All 4 output paths confirmed to exist.
- `test_command_center_orchestrator_startup.py` passes as part of the full
  `run_tests.sh` run (73/79; unrelated pre-existing failures noted in
  TASK-268's checklist).
- Independent review: `APPROVED` by helper reviewer
  `helper-review-task-286-gina`, 2026-07-27T18:02:45Z, spawned per the
  documented conflict-routing convention.
- Read the live launcher templates directly (not just the task's claim):
  both the wezterm startup hook and the Codex orchestrator prompt carry
  the minimal-topology behavior today, confirming the mechanism ships.

## Batch Note

This is the twelfth and final release in this batch (TASK-268, 271, 272,
274, 277, 278, 279, 280, 281, 282, 283, 286 — the coherent architecture
build-out identified in the 2026-07-28 backlog triage,
`MAP_System/artifacts/planning/release-backlog-triage-2026-07-28.md`, as
stemming from TASK-277's roadmap review). All 12 released in dependency
order (277 first as the root roadmap; 268/271/272/274 next as the
process-fix prerequisites; then 278/279/280/281/282/283/286 as the P0
implementation slices, each releasing only after its stated output-path
dependencies had already released).
