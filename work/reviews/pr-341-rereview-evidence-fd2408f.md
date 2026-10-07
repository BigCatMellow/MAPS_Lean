# PR #341 — focused J1/v4 safeguard re-review (r8)

reviewer: claude-opus-5-fresh-rereviewer-pr341-r8
head_sha: fd2408fda31d574554bf345cde6319fe8313bd90
prior_head: 5f1ef8e090b62c8393113ddb211399646d381c84
independent: true
verdict: MINOR CORRECTIONS REQUIRED
review_state: CHANGES_REQUESTED
review_layer: focused J1/v4 safeguard re-review; spec only; nothing executed

## Summary

Corpus gate remains closed. The benchmark-owner semantics are unchanged and sound: SPEC, CASE, RUN, SCORING, REPORT, and REFERENCES were byte-identical to r7; the 512-state S4 enumeration returned 0 ambiguous, 0 unhandled, and 0 semantic mismatches; I2–I4 and all 49 B/M/N/F/G/H findings remain resolved.

v4 materially improved the invariant-13 safeguard: it independently enforces the 49-ID set, ID→owner mapping, anchor-quality/minimum-count rules, 13 section hashes, and report vocabulary. All requested r7 mutations inside pinned sections were caught, including comparator additive exceptions and report-vocabulary probes.

J1 is only partially resolved because additive contradictory semantics can still be placed outside the 13 pinned spans while preserving all old anchors. Required probe 9 escaped when a cutoff exception was added in SPEC §7.1. Additional adversarial escapes included sibling/unpinned sections, duplicate pinned headings, CASE terminal sections, and RUN.

## Verified results

- Baseline safeguard: PASS — 49 findings, 107 semantic anchors, 13 structurally pinned sections.
- CI at `fd2408f`: safeguard step passed; exact-head review-evidence step failed as expected before approving review evidence; Runtime stack tests passed.
- S4 enumeration: 512 states; 0 ambiguous; 0 unhandled; 0 mismatches.
- I2: STILL RESOLVED.
- I3: STILL RESOLVED.
- I4: STILL RESOLVED.
- B1–B3, M1–M12, N1–N10, F1–F9, G1–G10, H1–H5: STILL RESOLVED.

## J3 — MINOR, gate-holding

The structural checker hashes only the first occurrence of 13 selected heading spans. The repeated additive-exception class can therefore be relocated elsewhere in the same normative owner document and remain green. This is the same regression pattern rather than a new benchmark-design defect.

### Smallest sufficient correction

1. Add normalized whole-document SHA-256 pins for the five normative owners, computed from the independently reviewed r7/r8 blobs:
   - BENCHMARK-SPEC.md: `86909cba3552121fcf17320d270fac45f7ba1b1e312ce723b8eb9c288d40cac6`
   - CASE-DESIGN.md: `363c5a0ffaaecbb1ce8cdfd141d80e5a5a41cb773d5c969ac8cc1f2bc28c0bfa`
   - RUN-PROTOCOL.md: `d5cf4fe8549e066bb153288c447a148928e4cdfd269bf03b55239157c0436939`
   - SCORING-AND-ANALYSIS.md: `f40d462542b6607eece154ffb6c8c105e6fad64675ecf50465cc0dad92eeaf66`
   - REPORT-TEMPLATE.md: `558cecc5f5582ff3b1467eb67b8f6dd49cfaea360559d6e244118905e35c14ae`
2. Retain the 13 section pins for localized diagnostics.
3. Fail unless each pinned heading occurs exactly once.
4. Correct overclaims in task/friction status: additive semantic exceptions cannot pass merely by retaining old sentences only after the whole-owner pins are installed.
5. Record this repeated safeguard-gap occurrence under AGENTS.md invariant 13.

A throwaway reviewer prototype of this change rejected all 73 probe states, including probe 9b and every adversarial escape, while baseline and whitespace/CRLF-only edits remained green.

## J4 — OPTIONAL

The anchor-quality floor is length-only, so a generic 20+ character anchor could replace a semantic phrase. Whole-owner hashes close this risk for normative owner documents; no separate gate-holding change is required.

## Exact next gate

Owner applies J3 only. J2/J4 remain optional. No normative owner-document edits.

Then a fresh focused independent review at the new exact head must:

- rerun the safeguard;
- independently recompute the whole-owner hashes from the accepted r7 blobs;
- rerun probes 1–9 including probe 9b and out-of-span/duplicate-heading additive variants;
- confirm the five normative owner blobs are unchanged.

If owner blobs remain unchanged, the r8 512-state S4 and bounded B/M/N/F/G/H regression results may carry forward.

No corpus/holdout authoring, threshold freeze, Smoke/Standard execution, model/evaluator calls, spending, runtime/protocol change, or merge is authorized by this review.
