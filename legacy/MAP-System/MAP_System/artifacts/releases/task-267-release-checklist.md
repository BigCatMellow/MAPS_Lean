<!-- hpom: file: artifacts/releases/task-267-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-22 -->
<!-- hpom: verified_against: TASK-267 independent approval and HPOM release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-267

## Header

```text
task_id: TASK-267
released_by: codex-lab-kula
release_date: 2026-07-22
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Release Summary

TASK-267 establishes one verified current operating picture for MAP: software
delivery is the proving workflow; Codex and Claude retain core accountability;
Pi, helpers, and local models remain bounded support; SQLite claim state is
distinguished from durable ownership and decision authority; and the recovery
queue is ordered without treating model fit as ownership.

The release includes two independent rejection/rework cycles. Kiri's review
required a current TASK-186 state, explicit owner/claimant columns, DEC-014 path
reconciliation, and removal of volatile roster names. Bima's review then caught
TASK-266 being described as RELEASED without a release record. The final state
correctly records TASK-186 as RELEASED, TASK-266 as APPROVED/pending release,
and TASK-268 as dependency-satisfied through the runner's accepted dependency
statuses.

No project-direction decision was created or changed. No additional follow-up
task is created by this release: INS-0039 and INS-0040 already preserve the two
new systemic findings about claimant-aware review separation and mechanically
checking task-state assertions in canonical prose. Emergence capture was
therefore considered and is satisfied by those existing records.

This is internal planning/shared-state documentation, so the user-acquisition
release-path smoke checklist is not applicable.

## Verification

- Independent approval: `artifacts/reviews/task267-rereview2-bima.md`.
- `validate_shared_state.py`: PASS, 23/23 with zero warnings.
- `validate_task_mirrors.py`: PASS.
- `validate_task_graph.py`: PASS.
- `validate_decisions.py`: PASS, 28/28 with zero conflicts.
- `validate_canonical_repo_paths.py`: PASS.
- Scoped `map-git diff --check` over the six registered outputs: PASS.
