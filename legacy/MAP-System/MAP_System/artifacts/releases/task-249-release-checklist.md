# TASK-249 Release Checklist

task_id: TASK-249
released_by: claude-lab-lure
review_record: MAP_System/artifacts/reviews/task249-review-kiri.md
release_date: 2026-07-19

## Release checks

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Evidence

- Independent review APPROVED (kiri, `artifacts/reviews/task249-review-kiri.md`);
  `validate_review` PASS; 10 pre_dispatch_policy + 3 runner_policy_gate tests
  PASS; mirror validation passed on the APPROVED transition.
- Change: `is_destructive()` now uses clause-scoped negation
  (`contains_unnegated`) so a hard-stop phrase named only inside a prohibition
  no longer trips REQUIRE_CORE_DESTRUCTIVE_APPROVAL, while an imperative after a
  clause boundary and any unnegated hard-stop phrase still do. Safety is not
  weakened; the `destructive_action` flag and all other gates are untouched.
- POLICY / AUTHORITY note: this modifies a dispatch **safety** classifier.
  Command-center (operator) release authorization is required; running the
  release constitutes that authorization.
- Follow-up captured (not a blocker): generalizing the same clause-scoped
  negation to the other gate predicates (`requires_shell_or_network`,
  `mutates_canonical_map`, `crosses_trust_boundary`) is deferred as reviewed
  future work, not applied here.
- Emergence capture considered: the fix plus regression tests convert the
  prohibition-clause false-positive lesson into a mechanical guard.
- Normal release writes the durable lifecycle event.
