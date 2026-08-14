# Release Checklist: TASK-301

## Header

```
task_id:      TASK-301
released_by:  claude-lab-sumi
release_date: 2026-08-10
review_record: task299-security-review-todo (APPROVED)
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered — mechanism: neither; evidence/reason: routine release-checklist authoring for already-approved infra work (batch2 pass, 2026-08-10); no new pattern surfaced during verification.

## Evidence

- History: created → SUBMISSION → APPROVED (task299-security-review-todo).
- All 5 cited output paths independently confirmed present on disk:
  `MAP_System/artifacts/operations/opensnitch-cross-pc-2026-07-28.md`,
  `MAP_System/scripts/install_opensnitch_rules.py`,
  `MAP_System/templates/install/opensnitch/map-kudu-hcom-relay.json`,
  `MAP_System/templates/install/opensnitch/map-kudu-ruki-ssh.json`,
  `MAP_System/tests/test_install_opensnitch_rules.py`.
- No gaps found in the p03-lifecycle-backlog-disposition-2026-08-10.md pass;
  no gaps found in this independent re-check.

## Rollback

Uninstall reverses to prior OpenSnitch rule set; installer is idempotent and
preserves unrelated user rules, so removal/re-run carries no other-rule risk.
