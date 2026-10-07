# PR #341 — Protocol Effectiveness Benchmark — focused correction re-review (r7) evidence

reviewer: claude-opus-5-fresh-rereviewer-pr341-r7
head_sha: 5f1ef8e090b62c8393113ddb211399646d381c84
prior_head: 8b9efd95f2cd48843f5eb38273a94eec55a49b58
independent: true
verdict: MINOR CORRECTIONS REQUIRED
review_state: CHANGES_REQUESTED
review_layer: FOCUSED CORRECTION RE-REVIEW (I1–I4 + safeguard + bounded B/M/N/F/G/H regression); spec only; nothing executed

## Summary

Corpus gate stays closed. Owner documents at this head are sound: I2, I3, I4 resolved; no B/M/N/F/G/H document regression. I1 (gate-holding) is only partially resolved: two required mutation-probe classes are not caught, and the v3 manifest dropped a v2 anchor on the exact H1 comparator-shielding surface.

Head check: `refs/pull/341/head` = `5f1ef8e…` (match). Delta `8b9efd9..5f1ef8e`: SCORING (I2/I3 lines only), REPORT-TEMPLATE (I4 only), manifest, checker, README, task, friction carrier, r6 evidence. BENCHMARK-SPEC, CASE-DESIGN, RUN-PROTOCOL byte-unchanged.

## I1–I4

- I1 — PARTIALLY RESOLVED (gate-holding). Checker passes; direct rewrites of pinned clauses caught; probes 2b and 8a–8c missed; v3 lost coverage v2 had.
- I2 — RESOLVED. §8 S4 branches mutually exclusive; matches r4 accepted semantics.
- I3 — RESOLVED. `SUPPORTED_*` requires matching aggregate verdict; BETTER cond 4 bars rule 1/rule 2/registered harm per stratum.
- I4 — RESOLVED at head. Five verdicts; `confirmatory: yes|no` separate; forbidden-effect BLOCKED is a FALSE_SUCCESS subset row; `BLOCKED_WRONG_CLASS` present.

## Mechanical safeguard

- Checker: PASS. Expected IDs 49 (hard-coded); actual 49. Anchors 106 listed / 71 unique.
- Required probes caught: 1a–1d, 2a, 2c, 2d, 3, 4a, 4b, 5a, 5b, 6 (each of 6 fields removed; field added), 7a, 7b, 8d, 8e, 9a–9c.
- Required probes MISSED:
  - 2b: `§9 step 4` rewritten so comparator-exclusive S4s turn tested-arm `PRIMARY_WORSE` into `TRADEOFF`. v2 caught this via `comparator-exclusive S4s never shield T from this determination.` (N4/F4/H1); v3 removed that anchor from all three.
  - 8a/8c: `| NO CONFIRMATORY VERDICT` or `| PROMISING` appended to a template verdict line.
  - 8b: `BLOCKED_AFTER_FORBIDDEN_EFFECT` terminal row re-added.
- Adversarial false negatives (not required, recorded): additive §8 exception lifting S4 rule 2; additive CASE §6.4 cost-path exception; additive precedence line after `INSTRUCTION_PRECEDENCE`; SPEC §4.2 bootstrap precedence copy; SPEC §9.1 run-visible copy; SPEC §12 Smoke withholding audience; I3 aggregate-match and stratum-S4 clauses; v2 H4 anchors (A/B/C instruction length, overlay reclassification) dropped.
- Manifest-coordinated bypasses: min-count satisfied by duplicate trivial anchors; `owner_file` retargetable to a decoy file (only abs/`..` rejected). Manifest is one 18 KB physical line, so manifest diffs are not line-reviewable.

## S4/verdict

- Enumerated T_excl 0..3 × K_excl 0..3 × PRIMARY B/E/I/W × HARM × BENEFIT × integrity = 512 states against r4-era accepted semantics (`7ec7e1d`).
- Mismatches: 0. Tested-arm S4 regains BETTER/EQUIVALENT: 0. Comparator S4 rescue outside the accepted rule-1/rule-2 net-excess boundary: 0. §9-step-3 S4 bullets matched ≠ 1: 0.
- Literal residuals (NIT; no divergent verdict under §9 order and §4 rule-2 ineligibility): §4 rule-2 clause read unordered double-matches `PRIMARY_BETTER + HARM_CROSSED` (12 states); §8 `PRIMARY_EQUIVALENT + BENEFIT_CROSSED` bullet lacks the "no S4 branch deciding" qualifier (6 states).

## Regression

B1–B3, M1–M12, N1–N10, F1–F9, G1–G10, H1–H5: owner documents STILL RESOLVED. Safeguard coverage for N4/F4/H1 regressed relative to v2 (tracked under I1).

## New findings

- J1 — MINOR, gate-holding (I1 residual, fourth safeguard-gap occurrence). Fix below.
- J2 — NIT: §4 rule-2 clause ordering; §8 last two bullets qualifier; template Smoke mapping (`INCONCLUSIVE`, `confirmatory: no`); template H5 block lacks aggregate verdict / stratum intervals / Nmin / stratum harm; template cutoff line omits overlay class. Optional; must not change the 512-state result.

## Exact next gate

1. J1 only (J2 optional): restore no-shield anchor; pin whole rule blocks structurally in the script (section hashes or contiguous full-block anchors) for SCORING §4/§8/§9/§10, CASE §1/§2/§6.4, SPEC §4.2/§7.4/§9.1/§12, REPORT Verdicts + Terminal calibration; add script-level forbidden-vocabulary and exact-verdict-line checks; script-pin ID→owner path; require unique non-trivial anchors; pretty-print manifest; pin I2–I4 surfaces; record the occurrence and correct task/friction overclaims.
2. Fresh focused re-review at the new exact head reruns checker, probes 1–9 incl. 2b/8a–8c and additive variants, the 512-state enumeration, and bounded regression check.

No corpus/holdout authoring, threshold freeze, Smoke/Standard runs, model/evaluator calls, spending, runtime/protocol change, or merge was authorized by this review.
