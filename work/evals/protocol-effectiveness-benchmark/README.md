# Protocol Effectiveness Benchmark

Status: **DESIGN APPROVED — REVISION-3 PRE-AUTHORING PACKAGE COMPLETE; FRESH INDEPENDENT REVIEW + ARM C GATE 1 REQUIRED; NOT EXECUTED**

Primary question:

> Given otherwise equivalent capable agents, does applying an operating protocol such as MAPS_L improve objectively correct autonomous task completion enough to justify its cost, complexity, and failure modes?

MAPS_L is a treatment configuration, not the grading definition. Protocol adherence is diagnostic only.

## Approved design

The pre-corpus design gate was independently approved at exact head `369bccaf68b258c70eb6efec0c9f70115c8014cb`:

- [`../../reviews/pr-341-rereview-evidence-369bcca.md`](../../reviews/pr-341-rereview-evidence-369bcca.md) — r9: `APPROVED FOR CORPUS CONSTRUCTION`.
- J3/v5 safeguard resolved; I2–I4 and all B/M/N/F/G/H owner findings remain resolved.
- 512-state S4 verification carried forward: 0 ambiguous, 0 unhandled, 0 semantic mismatches.

The five normative owner documents remain frozen by the v5 whole-document safeguard:

- [`BENCHMARK-SPEC.md`](BENCHMARK-SPEC.md)
- [`CASE-DESIGN.md`](CASE-DESIGN.md)
- [`RUN-PROTOCOL.md`](RUN-PROTOCOL.md)
- [`SCORING-AND-ANALYSIS.md`](SCORING-AND-ANALYSIS.md)
- [`REPORT-TEMPLATE.md`](REPORT-TEMPLATE.md)

This README is navigation/status only. It does not redefine those owners.

## Current pre-authoring package

Current public/non-secret instantiation is under [`pre-corpus/`](pre-corpus/):

- `TREATMENT-SURFACE-MANIFEST.md` / `TREATMENT-BUNDLE-INVENTORY.tsv` — frozen offline treatment surface.
- `GENERIC-CONTROL.md` — exact candidate Arm C control; still requires independent competent/non-strawman Gate 1 approval.
- `SOURCE-POOL-DEFINITION.json` — frozen external public source-pool definition and eligibility rules.
- `TARGET-WORK-SAMPLING-MANIFEST.md` — revision 3 public beacon selection with a complete eligible-candidate ledger frozen and hashed before the qualifying pulse.
- `CUSTODY-AND-EXPOSURE-PLAN.md` — selection custody retired; Gate 4/5 case-construction/hidden-material custody remains separate.
- `PRE-AUTHORING-PACKAGE-MANIFEST.json` — exact six-input package pin.
- `INDEPENDENT-CURATOR-START-PROMPT.md` — operational public-selection procedure; the historical filename does not imply a private selection custodian.

Current package hash:

`32295d7152542b3d6aa2ec0f903c03c8fae2cd82056b4e0e72295d4f278a8e2f`

The package is owner-recomputed and not yet independently verified at this revision. No selected case content exists.

## Revision 3 selection integrity

Before the qualifying pulse exists, the operator must enumerate/adjudicate the complete eligible population, assign domain/complexity, commit the canonical public eligible-candidate ledger, compute `candidate_set_sha256`, and commit `selection/SELECTION-FREEZE.json` binding that set to the package/source-pool hashes, formulas, operator, freeze timestamp, and pulse rule.

The first valid NIST Randomness Beacon 2.0 pulse at least 600 seconds after the candidate-ledger freeze is then applied arithmetically to that frozen set. The ranking formulas include `candidate_set_sha256`.

Ordinary post-pulse eligibility adjudication is prohibited. A frozen row can be removed only under the documented objective-defect/source-availability exception with published evidence and independent confirmation.

## Gate 1 — Arm C remains separate

Before candidate enumeration/selection, an independent reviewer without a MAPS_L development stake must explicitly judge the exact `GENERIC-CONTROL.md` text competent/non-strawman or return corrections.

PR #371 clarifies that same-owner adversarial critique may be supporting evidence but does not satisfy this independence requirement. One eligible fresh reviewer may review #371 and the exact Arm C control in the same pass.

## Gate 4/5 remains separate

Publishing candidate/selected identities, ranks, and holdout membership does not publish case answers. Hidden fixtures/contracts/oracles/checks, canaries, answer-bearing provenance, and sealed case-construction material remain governed separately by `BENCHMARK-SPEC.md` §9 and `CUSTODY-AND-EXPOSURE-PLAN.md`.

That later construction-custody boundary remains unresolved.

## Current sequence

1. Fresh independent review of revision-3 pre-authoring package.
2. Independent Gate 1 approval of exact Arm C control.
3. Freeze and commit the complete eligible-candidate ledger before a future qualifying pulse.
4. Apply the future pulse deterministically and publish selection/ranking/holdout results.
5. Resolve Gate 4/5 case-construction custody before hidden case content is created.
6. Construct/audit/freeze corpus.
7. Fresh independent pre-run review.
8. Separate execution authorization before benchmark execution.

## What remains prohibited

Nothing has been executed. No A/B/C candidate runs, Smoke, Standard, benchmark evaluator/model/API calls, spending, MAPS_L runtime/protocol changes, promotion, or merge are authorized by the design approval or pre-authoring package.

## Exact next phase

1. eligible independent curator/custodian receives package `c0927f437e7a4d07d1a825eace7e3d061ad0bb9c6a8b8775c28b2e4bfd07e963` through `INDEPENDENT-CURATOR-START-PROMPT.md`;
2. curator independently verifies treatment/Arm C/source pools/custody and either returns non-secret corrections or `PRE-AUTHORING PACKAGE ACCEPTED FOR SEALED SELECTION`;
3. only after acceptance, curator privately precommits the sampling secret, uses the frozen NIST-beacon rule, and performs deterministic selection/construction outside MAPS_L-owner access;
4. a distinct sealed-access reviewer audits overlays/corpus/freeze;
5. only hashes/counts/commitments/non-secret aggregate evidence return here;
6. fresh independent corpus/pre-freeze verdict opens the later pre-run gate.

Benchmark execution remains a later, separate gate.
