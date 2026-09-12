# Protocol Effectiveness Benchmark

Status: **DESIGN APPROVED — OWNER PRE-AUTHORING PACKAGE COMPLETE; BLOCKED ON INDEPENDENT CURATOR/CUSTODIAN; NOT EXECUTED**

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

## Owner-complete pre-authoring package

Current public/non-secret instantiation is under [`pre-corpus/`](pre-corpus/):

- `TREATMENT-SURFACE-MANIFEST.md` — tested ref `5f07b33...`, exact 45-file offline MAPS_L treatment inventory, bundle hash `7a944e3d...`, common bootstrap, B launcher, parity and context-cost accounting.
- `TREATMENT-BUNDLE-INVENTORY.tsv` — exact path/blob inventory used by the treatment hash.
- `GENERIC-CONTROL.md` — competent candidate Arm C text/hash; exact text still requires independent non-strawman approval.
- `SOURCE-POOL-DEFINITION.json` — fixed 16-repository external public source-pool definition, canonical hash `5101ed5b...`, 48-case quotas and objective eligibility filters.
- `TARGET-WORK-SAMPLING-MANIFEST.md` — sampling reference `OpenAI gpt-5.6-sol`, documented cutoff `2026-02-16`, plus secret-commit + future NIST-beacon HMAC selection so MAPS modifiers cannot reconstruct selected issue IDs.
- `CUSTODY-AND-EXPOSURE-PLAN.md` — access-based custody boundary covering selected content **and** secret/seed/ranking material.
- `PRE-AUTHORING-PACKAGE-MANIFEST.json` — package pin for the six owner-prepared pre-authoring inputs; candidate package hash `1cc69cd2...`.
- `INDEPENDENT-CURATOR-START-PROMPT.md` — standalone handoff for the genuinely independent curator/custodian.

Parent task: [`../../tasks/protocol-effectiveness-benchmark.md`](../../tasks/protocol-effectiveness-benchmark.md).
Corpus child task: [`../../tasks/protocol-effectiveness-corpus-construction.md`](../../tasks/protocol-effectiveness-corpus-construction.md).

## Important owner-found correction before handoff

A fully public deterministic seed would make selected public GitHub issue IDs reconstructable by a MAPS_L protocol modifier, violating the access-based exposure rule even if the selected IDs were never committed here.

The candidate sampling method therefore now requires:

1. curator-generated private 256-bit secret;
2. public SHA-256 commitment to that secret before a future qualifying NIST Randomness Beacon pulse;
3. HMAC-SHA256 seed derivation using the private secret + fixed public package inputs + that pulse;
4. public commitment to the derived seed while the secret/seed/rankings remain sealed;
5. reveal/recomputation only at the permitted look.

No issue enumeration/ranking has occurred in the MAPS_L owner context.

## Critical custody boundary

No selected `FROZEN_STANDARD` or `SEALED_HOLDOUT` identity/content, selection secret/seed, ranking table, selected URL, or holdout membership may be created in this repository or a user-visible MAPS_L-owner chat.

The current repository/user context therefore cannot serve as the independent corpus custodian. A genuinely separate curator/custodian with access-controlled storage is now the exact blocker.

A normal fresh review chat under the same user account is not sufficient custody. Use `INDEPENDENT-CURATOR-START-PROMPT.md` only with a separate eligible person/service/environment.

## What remains prohibited

Nothing has been executed. No A/B/C candidate runs, Smoke, Standard, benchmark evaluator/model/API calls, spending, MAPS_L runtime/protocol changes, promotion, or merge are authorized by the design approval or pre-authoring package.

## Exact next phase

1. eligible independent curator/custodian receives the exact `PRE-AUTHORING-PACKAGE-MANIFEST.json` package;
2. curator independently verifies treatment/Arm C/source pools/custody and either returns non-secret corrections or `PRE-AUTHORING PACKAGE ACCEPTED FOR SEALED SELECTION`;
3. only after acceptance, curator privately precommits the sampling secret, uses the frozen NIST-beacon rule, and performs deterministic selection/construction outside MAPS_L-owner access;
4. a distinct sealed-access reviewer audits overlays/corpus/freeze;
5. only hashes/counts/commitments/non-secret aggregate evidence return here;
6. fresh independent corpus/pre-freeze verdict opens the later pre-run gate.

Benchmark execution remains a later, separate gate.
