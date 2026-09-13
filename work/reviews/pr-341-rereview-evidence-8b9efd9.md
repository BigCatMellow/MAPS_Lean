# PR #341 — Protocol Effectiveness Benchmark — focused re-review (r6) evidence

reviewer: claude-opus-5-fresh-rereviewer-pr341-r6
head_sha: 8b9efd95f2cd48843f5eb38273a94eec55a49b58
independent: true
verdict: MINOR CORRECTIONS REQUIRED
review_state: CHANGES_REQUESTED
review_layer: FOCUSED DELTA RE-REVIEW (H1–H5 + semantic anchor safeguard + B/M/N/F/G regression); spec only; nothing executed

## Summary

Corpus gate stays closed. H1, H2, and H5 are resolved. H3 and H4 are partially resolved. The reviewer found no B/M/N/F/G regression and independently confirmed that the fifth-pass S4/verdict logic reproduces the accepted pre-regression semantics: comparator S4 excess cannot soften, rescue, or unlock the tested arm, and seeded stress cannot leave STRESS on cost/latency/burden-only paths.

Remaining bounded findings:

- **I1 — gate-holding:** the v2 anchor safeguard still misses semantic rewrites on the exact H1 surface, the SPEC copy of H2, H5 non-retroactivity, and the G3 run-visible list. Required fix: multi-anchor the concrete rule-bearing sentences/blocks, not headings/prefixes, and update the friction record for this third regression occurrence.
- **I2 — MINOR:** `TRADEOFF_RULE_V1` has an overlapping branch for `T_excl > 0 && T_excl <= K_excl && PRIMARY_BETTER && HARM_CROSSED`; make the branches mutually exclusive or explicitly ordered.
- **I3 — MINOR:** H5 BETTER is weaker than EQUIVALENT on tested-arm S4s and is not tied to the matching aggregate verdict. Require no S4 rule/registered harm in each stratum and require the matching aggregate verdict for `SUPPORTED_*`.
- **I4 — MINOR:** REPORT-TEMPLATE retains non-owner vocabulary: `NO CONFIRMATORY VERDICT`, `BLOCKED_AFTER_FORBIDDEN_EFFECT`, and omits `BLOCKED_WRONG_CLASS`.

## H1–H5 result

- H1 — RESOLVED.
- H2 — RESOLVED.
- H3 — PARTIALLY RESOLVED; safeguard catches deletion but not enough semantic rewrite cases.
- H4 — PARTIALLY RESOLVED; enumerated fifth-pass additions landed, but owner-vocabulary drift remains.
- H5 — RESOLVED.

## Regression result

B1–B3, M1–M12, N1–N10, F1–F9, and G1–G10: **STILL RESOLVED**. No fifth-pass regression was found.

## S4 verification

The reviewer exhaustively enumerated 256 tested/comparator S4/primary/harm/benefit combinations and found zero differences from the accepted semantics. The previously biased r5 cells were reverted. Comparator S4 cannot rescue a tested-arm primary loss, cannot convert tested-arm WORSE to TRADEOFF, and cannot restore BETTER/EQUIVALENT when the tested arm has its own S4 restriction.

## Mechanical safeguard result

- Expected/actual finding count: 49.
- Checker hard-codes B/M/N/F/G/H IDs and supports multiple anchors.
- Local checker passed.
- Mutation probes showed remaining false negatives on semantic rewrites, including S4 rule-2 classification, S4 no-soften wording, additive precedence rewrites, SPEC H2 wording, H5 non-retroactivity, and G3 run-visible-list weakening.
- Therefore invariant-13 protection remains incomplete until I1 is applied.

## Exact next gate

1. Apply I1–I4 as targeted edits only.
2. Extend semantic anchors to the edited rule bodies and update the friction carrier.
3. Fresh focused independent re-review at the new exact head must rerun the checker, mutation probes, S4 branch/enumeration test, I3/I4 verification, and bounded B/M/N/F/G/H regression check.
4. Only `APPROVED FOR CORPUS CONSTRUCTION` opens bounded corpus construction; benchmark execution remains prohibited.

No corpus/holdout authoring, threshold freeze, Smoke/Standard runs, model/evaluator calls, spending, runtime/protocol change, or merge was authorized by this review.