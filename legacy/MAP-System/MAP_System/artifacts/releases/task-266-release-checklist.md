<!-- hpom: file: artifacts/releases/task-266-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-23 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-266

## Header

```
task_id:      TASK-266
released_by:  codex-lab-lori
release_date: 2026-07-23
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Adds the sanctioned recovery path for an `IN_PROGRESS` task whose claimant is
missing and whose lease is absent or expired. The recovery verb is deliberately
narrow: it requires an attributable actor and written reason, refuses a live
claimant or live lease, records the prior owner, writes an auditable event, and
exports SQLite state to the task and graph mirrors.

The task closed the concrete TASK-186 stall without hand-editing SQLite. Two
review cycles corrected actor validation, output registration, synchronized
submission evidence, and normalization of the actor identity across command
output, the agent table, SQLite/JSONL events, and summaries.

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_recover_orphan.py` —
  10/10 pass on 2026-07-23.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_review.py
  --review-record MAP_System/artifacts/reviews/task266-final-review-lime.md
  --task-id TASK-266` — pass.
- Independent final review:
  `MAP_System/artifacts/reviews/task266-final-review-lime.md` — APPROVED with
  no remaining `BLOCKER` or `REQUIRED` finding.
- The reviewer independently verified the focused suite, a mutation restoring
  the actor-normalization defect, task mirrors, task graph, and security
  boundaries.
- Final global task-mirror, task-graph, and event validation are required
  immediately before the release command.

## Follow-Up Boundary

- TASK-268 owns the synchronized submission verb and consumes `claims.py`,
  `map_task.py`, and `run_tests.sh` only after this release.
- TASK-270 already released the separate review-claim identity fix.
- INS-0039's owner-versus-submitter self-review gap is outside TASK-266 and was
  not changed during release.
