# PR #341 benchmark friction carrier

Status: **PENDING CANONICAL FRICTION_LOG APPEND**

Date: 2026-09-11
Class: process-gap / evaluation-integrity

This record exists because the current GitHub connector does not provide a safe append operation for the large append-only `work/coordination/FRICTION_LOG.md`. It is a temporary carrier, not a competing friction log. Both entries still need canonical append when an append-capable path is available.

## Entry 1 to append

```text
## 2026-09-11 — PR #341 correction passes repeatedly regressed resolved benchmark protections
- class: process-gap
- opened: 2026-09-11
- signal: independent reviews repeatedly found correction-pass regressions or
  safeguard gaps. M4 regressed at r3; M2/N5/N7 regressed at r4; M6/N4/F4
  regressed at r5 while headings survived; r6 showed the v2 anchor safeguard
  still missed exact H1/H2/G3/H5 rewrites; r7 showed v3 still missed the
  comparator no-shield mutation, report-vocabulary additions, weak anchors, and
  owner retargeting; r8 then showed v4 still allowed the same additive-exception
  class when contradictory semantics were moved outside the 13 pinned sections.
- countermeasure: invariant-13 safeguard upgraded to v5. The checker independently
  pins all five complete normative owner documents in addition to the 49 finding
  map, owner mappings, anchor checks, 13 localized section hashes, unique-heading
  checks, and report-vocabulary invariants.
- verified: VERIFIED at r9 reviewed head
  369bccaf68b258c70eb6efec0c9f70115c8014cb. Fresh reviewer recomputed all five
  owner hashes, demonstrated previously escaping additive/out-of-span mutations
  fail under v5, carried forward the 512-state S4 result with zero ambiguity /
  unhandled / semantic mismatch, and returned APPROVED FOR CORPUS CONSTRUCTION.
- follow-up: deliberate normative owner edits require checker rebaseline + fresh
  review; do not restart safeguard hardening absent a demonstrated escaping
  semantic regression or actual benchmark-validity defect.
```

## Entry 2 to append

```text
## 2026-09-11 — public deterministic corpus seed would expose selected public issues
- class: evaluation-integrity
- opened: 2026-09-11
- signal: during post-approval pre-authoring instantiation, the owner noticed that
  deriving the selection seed only from public design/source-pool hashes makes
  selected GitHub issue IDs reproducible by any MAPS_L protocol modifier. Under
  the approved access-based exposure rule, withholding the IDs from git/chat is
  insufficient if the owner can reconstruct them from public inputs.
- consequence: a public deterministic seed would contaminate FROZEN_STANDARD and
  SEALED_HOLDOUT selection before construction and make the public-source holdout
  unsuitable as pristine evidence.
- countermeasure: TARGET-WORK-SAMPLING-MANIFEST now requires an eligible curator
  to generate a private 256-bit secret, publish only SHA256(secret) before a
  predetermined future NIST Randomness Beacon 2.0 pulse, derive the selection
  seed via HMAC-SHA256(secret, fixed package inputs + pulse), publish only
  SHA256(seed), and retain secret/seed/ranks/selected IDs/holdout membership in
  sealed custody until the permitted reveal. Public source pools remain auditable
  without making the sample reconstructable.
- verified: OWNER-SHAPED / NOT YET INDEPENDENTLY FROZEN. No issue IDs were
  enumerated, ranked, or selected in the MAPS_L owner context. Require the
  independent curator/custodian to validate the package before generating the
  secret, then later reveal/recompute commitments and no-reroll selection during
  the permitted audit.
- follow-up: if independent review rejects the beacon/commit construction, stop
  before enumeration and revise only the public selection/custody method; never
  expose a candidate sample while correcting it.
```
