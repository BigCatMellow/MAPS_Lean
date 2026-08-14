# Release Checklist: TASK-298

## Header

```
task_id:      TASK-298
released_by:  helper-releases-batch1-mive
release_date: 2026-08-10
```

## Checklist

- [x] Shared-file updates complete
  Sole output path `artifacts/operations/cross-pc-convergence-2026-07-28.md`
  confirmed present on disk.
- [x] Decisions recorded
  None new; operational convergence action, not a policy change. Evidence
  doc explicitly states this does not make the two independently-writable
  SQLite copies safe — that remains a separate, later architectural step
  (subsequently addressed by TASK-299).
- [x] Follow-up tasks created
  TASK-299 (centralize cross-PC MAP SQLite authority on RUKI) already exists
  and is released alongside this task in the same batch.
- [x] Event log entry prepared
  This checklist's release event.
- [x] Emergence capture considered — mechanism: neither; evidence/reason: routine backlog release of already fully-reviewed work.

## Re-verification (2026-08-10, helper-releases-batch1-mive)

`destructive_action: true`, `task_tier: operator` — high blast radius, only
one cited output artifact for a large operation (SSH key setup, atomic tree
swap, rollback). Read the full evidence doc and its independent review
(`artifacts/reviews/task298-independent-review-mimi.md`) rather than
spot-checking existence, per the disposition report's caveat.

Confirmed all 6 acceptance criteria are substantively covered, not just
existence-checked:
1. RUKI pre-convergence state archived — 4 checksummed artifacts,
   `sha256sum -c` verified before activation.
2. KUDU→staging transfer with equivalence manifest — file-count
   reconciliation (2,146→2,148) and checksum dry-run with documented
   host-local exclusions.
3. Atomic swap with quiescent agents, preserved backup, recorded rollback —
   two same-filesystem renames; backup path independently re-confirmed
   intact and untouched by the reviewer's live second pass (`veni`) two days
   later.
4. Installer regeneration + health checks — 9 named checks passing at
   convergence time.
5. SSH hardening — independently re-verified live against the actual
   `sshd_config.d` override file (not the commented-out base defaults), by
   the reviewer's live pass, not just the evidence doc's claim.
6. Separate functional + security review before backup eligible for
   removal — `task298-independent-review-mimi.md` explicitly covers both
   lenses (dedicated "Functional Assessment" and "Security Assessment"
   sections) in one review record, single reviewer (claude-lab-mimi ≠
   task owner codex-live, independence holds), APPROVED, no BLOCKER/REQUIRED
   findings.

Note: the review explicitly recommends leaving the preserved backup path in
place until the operator or recovery coordinator makes a separate, deliberate
removal decision — criterion 6 makes it merely *eligible*, not mandatory to
remove. This release does not instruct or perform that removal.

One open item carried forward, not blocking this release: the evidence doc
discloses a credential-exposure incident (sudo password visible in an
hcom-visible command during setup) with password rotation still outstanding.
Already tracked as a known, operator-deferred item outside this task's
acceptance criteria.

## Summary

Converged RUKI onto the same MAP System/Command Center program tree as KUDU
via checksummed archive, verified transfer, atomic swap with preserved
rollback, and hardened SSH. Independent review re-verified the live system
two days post-convergence (not just the evidence doc) and confirmed all 6
acceptance criteria, including the required dual functional+security review.
No gaps found beyond an already-tracked, operator-deferred password rotation
item. Ready to RELEASE.
