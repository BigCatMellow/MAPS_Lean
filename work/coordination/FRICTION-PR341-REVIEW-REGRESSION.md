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
- signal: independent r3/r4 review caught repeat correction-pass regressions:
  M4 regressed at r3; M2/N5/N7 regressed at r4 after owner-file rewrites.
  Prose-only preservation instructions did not hold.
- countermeasure: mechanical safeguard required by AGENTS.md invariant 13 —
  `work/evals/protocol-effectiveness-benchmark/RESOLVED-FINDING-ANCHORS.json`
  pins every resolved B/M/N/F/G finding ID to an owner file + required clause;
  `scripts/check_protocol_effectiveness_benchmark_anchors.py` hard-codes the
  complete expected finding-ID set and fails when an anchor disappears; the
  existing `.github/workflows/review-evidence.yml` runs the check on every PR.
- verified: UNVERIFIED — safeguard is committed on PR #341; verify live by a
  passing anchor-check CI step on the corrected head and a fresh independent
  re-review confirming no B/M/N/F/G regression.
- follow-up: close after the anchor check passes and the fresh reviewer approves
  the correction gate. Any future repeat regression extends the mechanical
  anchors/check instead of adding another preservation instruction.
```
