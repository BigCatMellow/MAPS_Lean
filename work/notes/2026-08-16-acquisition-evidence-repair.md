# Acquisition evidence repair checkpoint — 2026-08-16

Scope: PR #56 narrow semantic repair only.

Blocking defect fixed in the feature branch before synchronization:

- an allowed `NOT_APPLICABLE` observation may still satisfy acquisition-path coverage;
- an operator-visible N/A decision alone cannot prove `release.no_stale_visible_artifact`;
- therefore operator-visible N/A preserves stale-visible `UNKNOWN` unless separate structured evidence proves the surface is gone/non-visible/non-applicable.

No withdrawal/removal evidence field was added; this is intentionally the smaller fail-closed correction requested by independent review.

After this repair, the branch must be genuinely synchronized with accepted `main@2cfb4bb8eef5526c074942421e7567f6a7c52159`, retargeted to `main`, verified to contain only acquisition-evidence delta, rerun through full Runtime CI, and independently re-reviewed before merge.
