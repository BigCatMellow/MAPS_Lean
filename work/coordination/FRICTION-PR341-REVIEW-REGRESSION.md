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
  regressed at r5 while headings survived; r6 showed the v2 anchor safeguard
  still missed exact H1/H2/G3/H5 rewrites; r7 showed v3 still missed the
  comparator no-shield mutation, report-vocabulary additions, weak anchors, and
  owner retargeting; r8 then showed v4 still allowed the same additive-exception
  class when contradictory semantics were moved outside the 13 pinned sections
  (including required cutoff probe 9 in SPEC §7.1 and duplicate-heading/sibling
  section variants). Prose, sentence anchors, and selected-section hashes were
  insufficient against relocation of a contradiction.
- countermeasure: AGENTS.md invariant-13 safeguard upgraded to v5.
  `RESOLVED-FINDING-ANCHORS.json` remains the human-reviewable 49-finding map.
  `check_protocol_effectiveness_benchmark_anchors.py` independently hard-codes
  the complete finding-ID -> owner-path map and now also pins normalized
  whole-document SHA-256 values for all five normative owners: SPEC, CASE, RUN,
  SCORING, and REPORT. The 13 section hashes remain for localized diagnostics,
  and each pinned heading must occur exactly once. An additive exception cannot
  pass merely by retaining the accepted sentence/section or moving the
  contradiction elsewhere in the same owner document; authorizing such a
  semantic change requires deliberately changing the checker itself and fresh
  independent review.
- verified: UNVERIFIED — require v5 safeguard CI plus a fresh independent review
  that recomputes whole-owner hashes from the accepted r7/r8 blobs, reruns r8
  probes including 9b and out-of-span/duplicate-heading variants, and confirms
  the five owner blobs remain unchanged. The r8 512-state S4 and B/M/N/F/G/H
  regression results may carry forward only if owner blobs are unchanged.
- follow-up: if a known semantic regression escapes whole-owner pinning, replace
  the checker architecture rather than adding another narrower prose/section
  preservation rule.
```
