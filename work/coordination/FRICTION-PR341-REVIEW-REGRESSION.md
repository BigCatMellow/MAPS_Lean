# PR #341 repeated correction-pass regression friction

Status: **PENDING CANONICAL FRICTION_LOG APPEND**

Date: 2026-09-11
Class: process-gap

This record exists only because the current GitHub connector exposes whole-file replacement but no safe append operation for the large append-only `work/coordination/FRICTION_LOG.md`. It is not a competing friction log. The same entry must be appended verbatim to `FRICTION_LOG.md` when an append-capable path is available; then this temporary carrier can be removed under normal review.

## Entry to append

```text
## 2026-09-11 — PR #341 fix passes repeatedly regressed resolved benchmark protections
- class: process-gap
- opened: 2026-09-11
- signal: independent r3/r4/r5 review caught repeated correction-pass regressions:
  M4 regressed at r3; M2/N5/N7 regressed at r4 after owner-file rewrites; and
  M6/N4/F4 regressed at r5 when an S4 determinism edit preserved the section
  headings but changed accepted verdict semantics in favor of the tested arm.
  Prose-only preservation instructions did not hold, and the first mechanical
  anchor version still missed semantic rewrites because several anchors were
  headings or single weak substrings.
- countermeasure: mechanical safeguard required by AGENTS.md invariant 13 —
  `work/evals/protocol-effectiveness-benchmark/RESOLVED-FINDING-ANCHORS.json`
  now pins every resolved B/M/N/F/G/H finding ID to one or more rule-bearing
  semantic clauses; `scripts/check_protocol_effectiveness_benchmark_anchors.py`
  hard-codes the complete expected finding-ID set and fails when an ID, owner,
  or required semantic clause disappears; the existing
  `.github/workflows/review-evidence.yml` runs the check on every PR revision.
  The S4 rule body, harm->WORSE path, seeded-stress primary-harm requirement,
  full instruction-precedence sentence, report labels, and cutoff-reference
  rules are explicitly pinned rather than relying on headings.
- verified: UNVERIFIED — the deletion-oriented v1 safeguard passed CI but did
  not catch the r5 semantic rewrite. Verify the strengthened v2 safeguard by a
  passing anchor-check CI step on the corrected head and a fresh independent
  re-review that confirms H1-H5 plus the bounded B/M/N/F/G regression set.
- follow-up: close after the strengthened anchor check passes and the fresh
  reviewer approves the correction gate. Any future repeat regression extends
  the semantic anchors/check or adds a more structural check; do not add another
  preservation instruction in place of machinery.
```
