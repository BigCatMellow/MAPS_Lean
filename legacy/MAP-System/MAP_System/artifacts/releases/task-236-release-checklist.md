<!-- hpom: file: artifacts/releases/task-236-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-23 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-236

## Header

```
task_id:      TASK-236
released_by:  codex-lab-mubo
release_date: 2026-07-23
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Releases the deterministic, read-only advisory monitor and its evidence. The
monitor reports proposal-only coordination findings, leaves deployment
authority with command-center, and specifies candidate-only recurrence/Emergence
handling without placing a model in the control path.

The final owner-liveness increment treats `available` and `busy` as live,
describes `standby` as parked rather than departed, and explicitly documents
that roster-backed results are a floor rather than a census of actual process
liveness. The liveness reaper remains the single computation authority.

## Verification

- Independent review:
  `MAP_System/artifacts/reviews/task236-rereview-mubo.md` — APPROVED.
- Focused advisory-monitor tests: 25/25 pass.
- Task mirrors and task graph: pass.
- Full suite: 71 pass, 3 fail, 74 total; the three disclosed baseline failures
  are the research-summary shape issue, the pre-existing noncanonical event
  warning, and its layer-1 cascade.
- Read-only input hashes were unchanged across execution.
- The post-approval documentation correction removed a volatile expired-lease
  task ID and retained the stable finding-kind distribution. The independent
  reviewer inspected it and updated the review hash before release.
- `run_tests.sh` changed after review only because active TASK-273 registered
  its separate `reassign_owner_test`; TASK-236's `advisory_monitor_test`
  registration is unchanged and still passes. The registry is intentionally a
  shared generated/registration surface under the task-graph collision rules.

## Follow-Up Boundary

- Standing trigger, surface, ownership, grouping, and repeat suppression remain
  command-center decisions; this release starts no service.
- Roster freshness remains a liveness-reaper/roster-maintenance concern, not a
  second authority inside the monitor.
- TASK-273 and TASK-268 own the overlapping lifecycle files. INS-0039 remains
  sequenced behind both.
