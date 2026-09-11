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
  still missed exact H1/H2/G3/H5 rewrites; r7 then showed v3 still missed the
  comparator no-shield mutation plus report-vocabulary additions and could be
  weakened by duplicate/trivial anchors or owner-path retargeting. Prose and
  sentence-presence checks alone were insufficient.
- countermeasure: AGENTS.md invariant-13 safeguard upgraded to v4.
  `RESOLVED-FINDING-ANCHORS.json` remains the human-reviewable 49-finding map,
  is now line-reviewable, restores the exact comparator no-shield anchor, and
  uses unique non-trivial anchors. `check_protocol_effectiveness_benchmark_anchors.py`
  independently hard-codes the complete finding-ID -> owner-path map, minimum
  unique-anchor counts, forbidden report vocabulary, exact five-verdict lines,
  and normalized hashes for 13 historically vulnerable whole rule sections:
  SCORING §4/§8/§9/§10; CASE §1/§2/§6.4; SPEC §4.2/§7.4/§9.1/§12; REPORT
  Verdicts and Terminal calibration. A coordinated manifest edit therefore
  cannot authorize an owner retarget or additive exception without changing the
  checker itself and triggering review.
- verified: UNVERIFIED — require the v4 checker to pass CI at the corrected head
  and a fresh independent review to rerun r7 probes 1-9 (including 2b and
  8a-8c), additive variants, the 512-state S4 enumeration, and bounded
  B/M/N/F/G/H regression verification.
- follow-up: if another known semantic regression escapes v4, replace or extend
  the affected structural pin rather than adding another prose preservation rule.
```
