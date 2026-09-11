# PR #341 repeated correction-pass regression friction

Status: **PENDING CANONICAL FRICTION_LOG APPEND**

Date: 2026-09-11
Class: process-gap

This record exists because the current GitHub connector does not provide a safe append operation for the large append-only `work/coordination/FRICTION_LOG.md`. It is a temporary carrier, not a competing friction log. The canonical entry still needs to be appended when an append-capable path is available.

## Entry to append

```text
## 2026-09-11 — PR #341 correction passes repeatedly regressed resolved benchmark protections
- class: process-gap
- opened: 2026-09-11
- signal: independent reviews repeatedly found correction-pass regressions or
  safeguard gaps. M4 regressed at r3; M2/N5/N7 regressed at r4; M6/N4/F4
  regressed at r5 when S4 semantics changed while headings remained; r6 then
  showed the v2 semantic-anchor safeguard still had false negatives on the
  exact H1 S4 surface, the SPEC copy of H2, H5 non-retroactivity, and the G3
  run-visible-field block. Prose preservation and broad/heading anchors were
  insufficient.
- countermeasure: AGENTS.md invariant-13 mechanical safeguard upgraded again.
  `work/evals/protocol-effectiveness-benchmark/RESOLVED-FINDING-ANCHORS.json`
  v3 pins the complete 49-finding B/M/N/F/G/H set to 100+ rule-bearing clauses,
  including complete multi-line surfaces where necessary.
  `scripts/check_protocol_effectiveness_benchmark_anchors.py` independently
  hard-codes the 49 finding IDs and minimum anchor counts for historically
  vulnerable findings, so a future edit cannot silently weaken a critical
  finding back to one heading/prefix while keeping CI green.
  The pinned surfaces include full S4 rule-2/rule-3 classification, all relevant
  TRADEOFF/preference branches, comparator no-rescue clauses, SPEC+CASE seeded
  stress primary-outcome conditions, the exact G3 run-visible block, report
  vocabulary, instruction precedence, and cutoff non-retroactivity.
- verified: UNVERIFIED — require a passing v3 anchor-check CI step plus a fresh
  independent re-review that repeats the r6 mutation probes/S4 enumeration and
  confirms I1-I4 plus bounded B/M/N/F/G/H regression status.
- follow-up: if another known semantic regression escapes this machinery, add
  structural validation for that rule surface rather than another prose-only
  preservation instruction.
```
