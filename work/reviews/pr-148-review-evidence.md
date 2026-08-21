reviewer: SENTINEL-pr148
head_sha: 94f87768aec07cd18ea94b78799142e0e831e150
independent: true
summary: >-
  Approved docs-only architecture design after amendment. The design selects
  one bounded Context Builder seam, covers all 11 trust classes, preserves
  canonical authority boundaries, and now explicitly defines fail-closed
  handling for missing, malformed, unknown, mapping-failure, expired,
  review-due, and future stale Skill metadata. Source claims remain aligned
  with current runtime behavior; no runtime or test files changed.
