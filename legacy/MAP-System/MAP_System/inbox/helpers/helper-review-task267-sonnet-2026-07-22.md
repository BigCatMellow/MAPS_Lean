# Helper Assignment - TASK-267 independent alignment review

- status: awaiting_approval
- owner: codex-lab-lime
- provider: claude
- created_at: 2026-07-22
- scope: Independently verify TASK-267's project-vision, authority, model-routing, repository-path, active-queue, and SYN-0001 claims against primary state.
- requested_model_tier: sonnet
- approved_model_tier: sonnet
- approved_by: claude-lab-gabi
- tier_reason: Cross-file contradiction and evidence verification across canonical state requires Sonnet; Haiku was considered and skipped as too checklist-oriented, while Opus was unnecessary.
- permission_mode: read-only except the single review artifact below
- output_path: MAP_System/artifacts/reviews/task267-review-task267-sonnet.md
- stop_condition: Write one verdict/findings artifact, report it to codex-lab-lime through hcom, then stop.

## Inputs

- `MAP_System/tasks/TASK-267.json`
- `MAP_System/shared/project-brief.md`
- `MAP_System/shared/current-state.md`
- `MAP_System/shared/hpom.md`
- `MAP_System/shared/agent-capability-matrix.md`
- `MAP_System/shared/canonical-repo.md`
- `MAP_System/artifacts/planning/map-project-realignment-2026-07-22.md`
- `MAP_System/shared/decisions.md` (DEC-008, DEC-014, DEC-028 only)
- `MAP_System/map.db` (read-only verification)
- `MAP_System/graph/runner.py` (execute read-only route check)

## Review Requirement

Verify claims independently. Do not treat internal consistency or passing unit
tests as proof. Reproduce active task/claim facts from SQLite, runner facts from
the live runner, and repository-root facts with the Git wrapper. Check whether
any wording invents authority, overstates model capability, or contradicts the
operator's 2026-07-22 model-fit direction.

## Learned So Far

- Claude approved Sonnet through hcom #10521 after explicitly rejecting Haiku
  as too shallow and Opus as unjustified.
- TASK-186 is the reachability caution: synthetic terminal-state tests pass
  while the exporter removes the rows the watcher expects to read.
- The author/integrator is `codex-lab-lime`; the helper is review-only and must
  not edit the six canonical outputs.
- Launch was blocked before the helper started because sending the named
  repository/SQLite-derived state to the external Sonnet service requires
  explicit operator authorization. No review data was sent and no helper
  session was created.
