# Release Checklist: TASK-321

## Header

```
task_id:      TASK-321
released_by:  rotation-replacement-dune-nizu
release_date: 2026-08-10
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered — mechanism: sentinel scan; evidence/reason: `emergence_sentinel.py list` found no pending candidate; this remediation applies the existing fail-closed authority and security-review lessons rather than introducing a new reusable pattern.

## Evidence

- Smalls remains the sole writable lifecycle authority; Biggie remains a
  read-only mirror.
- Functional review: `MAP_System/artifacts/reviews/task321_review.md`, approved
  after the current-UID cgroup-root fail-closed remediation.
- Original security findings:
  `MAP_System/artifacts/reviews/task321_security_review.md`.
- Final independent security rereview:
  `MAP_System/artifacts/reviews/task321_security_rereview.md`.
- Focused tests: 59 passed.
- `py_compile`, task-mirror validation, and shared-state validation passed.
- Live `map-authority status` and sanctioned `map-authority route` reported
  `FRESH`, `topology_valid: true`, no active local writers, and
  `writer_service_probe_source: cgroup_v2_fallback`.

## Completion Notes

- Shared-file updates: no new durable policy or project-truth decision was
  required; the implementation conforms to the existing single-writer and
  fail-closed authority rules.
- Decisions: no new decision was introduced. The approved MAP 2 implementation
  program and TASK-321 acceptance criteria remain authoritative.
- Follow-up tasks: no defect follow-up is required for this Phase 0 slice.
  Later MAP 2 phases remain governed by the existing implementation program.
- Event log: the sanctioned Smalls approval/release commands append the
  canonical lifecycle events and export task mirrors.

## Summary

TASK-321 restores truthful Biggie/Smalls authority probing inside the Codex
sandbox without weakening collision detection. Missing or malformed cgroup
evidence fails closed, the current-UID service root is required, and status
output identifies whether writer safety came from `systemctl` or the cgroup-v2
fallback.
