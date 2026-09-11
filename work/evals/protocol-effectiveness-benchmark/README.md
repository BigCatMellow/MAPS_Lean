# Protocol Effectiveness Benchmark

Status: **FIFTH CORRECTION PASS APPLIED — AWAITING FOCUSED H1–H5 RE-REVIEW; NOT EXECUTED**

Primary question:

> Given otherwise equivalent capable agents, does applying an operating protocol such as MAPS_L improve objectively correct autonomous task completion enough to justify its cost, complexity, and failure modes?

MAPS_L is a treatment configuration, not the grading definition. Protocol adherence is diagnostic only.

## Owner / current gate

Parent work: [`../../tasks/protocol-effectiveness-benchmark.md`](../../tasks/protocol-effectiveness-benchmark.md) on PR #341.

Review evidence:

- [`../../reviews/pr-341-review-evidence.md`](../../reviews/pr-341-review-evidence.md) — original review at `465d97300cf021840fb1fe0434656ff3772d1db4`: `MAJOR CORRECTIONS REQUIRED`.
- [`../../reviews/pr-341-rereview-evidence-56c43aa.md`](../../reviews/pr-341-rereview-evidence-56c43aa.md) — r2 at `56c43aa9c176a98b733c32cfb53b182b3c034b9f`: `MINOR CORRECTIONS REQUIRED`.
- [`../../reviews/pr-341-rereview-evidence-dcc064b.md`](../../reviews/pr-341-rereview-evidence-dcc064b.md) — r3 at `dcc064bbc70648bded8f3e944d4f00c46b198fa5`: `MINOR CORRECTIONS REQUIRED`.
- [`../../reviews/pr-341-rereview-evidence-7ec7e1d.md`](../../reviews/pr-341-rereview-evidence-7ec7e1d.md) — r4 at `7ec7e1d43e4252e3e6995cd83fc3ed6631a10e14`: `MINOR CORRECTIONS REQUIRED`; G1–G4 material, G5–G10 minor, with M2/N5/N7 fix-pass regressions.
- [`../../reviews/pr-341-rereview-evidence-0aee65b.md`](../../reviews/pr-341-rereview-evidence-0aee65b.md) — r5 at `0aee65b4b6ecc31cd3ac4042e1a47786d9490b06`: `MINOR CORRECTIONS REQUIRED`; H1/H2 material, H3–H5 minor, with M6/N4/F4 semantic regression.

H1–H5 are now owner-corrected on this branch. That is an **owner claim, not approval**.

Because correction passes repeatedly regressed previously resolved protections, AGENTS.md invariant 13 has a strengthened mechanical backstop:

- [`RESOLVED-FINDING-ANCHORS.json`](RESOLVED-FINDING-ANCHORS.json) maps every resolved B/M/N/F/G/H finding to its owner file and one or more rule-bearing semantic clauses;
- [`../../../scripts/check_protocol_effectiveness_benchmark_anchors.py`](../../../scripts/check_protocol_effectiveness_benchmark_anchors.py) hard-codes the complete B/M/N/F/G/H finding-ID set and fails if an ID, owner, or required semantic clause disappears;
- the existing `review-evidence` workflow runs that checker on every PR revision.

Corpus/holdout construction remains closed until a fresh independent reviewer at the current head returns:

`APPROVED FOR CORPUS CONSTRUCTION`

Nothing has been executed: no corpus/holdout authored or frozen, no scored candidate/evaluator/model calls, no benchmark spending, and no MAPS_L runtime/protocol behavior changes.

## Package ownership

One concept, one owner:

- [`BENCHMARK-SPEC.md`](BENCHMARK-SPEC.md) — arms, Treatment Surface Manifest, controls, target population/pools, exposure lifecycle, hidden-material/retrieval firewall, thresholds/guardrails, Smoke information firewall, version identity.
- [`CASE-DESIGN.md`](CASE-DESIGN.md) — corpus vs agent-visible schema, common task-facing contract/parser, hidden checks, families/overlay audit, terminal truth table, severity.
- [`RUN-PROTOCOL.md`](RUN-PROTOCOL.md) — execution, parity/isolation, full-environment/tool leakage checks, human-response delivery, normalization/blinding, invalidation/reruns.
- [`SCORING-AND-ANALYSIS.md`](SCORING-AND-ANALYSIS.md) — metrics, paired inference, S4/tradeoff/verdict/H5 rules, UNKNOWN sensitivity, subgroups, ablations, divergence analysis.
- [`REPORT-TEMPLATE.md`](REPORT-TEMPLATE.md) — reusable report schema.
- [`REFERENCES.md`](REFERENCES.md) — provenance/methodology only; non-normative.

This README is navigation/status only. Follow the owning file rather than treating summaries here as normative rules.

## Existing MAPS_L evaluation boundary

Experiment P does not inherit primary grading requirements from `SIMULATION_DESIGN.md`, `maps-end-to-end-benchmark-v1.json`, `runtime/evaluation/evaluator.py`, or `runtime/evaluation/regression_case.py`. Their MAPS-shaped process/runtime properties remain diagnostic, runtime-regression, or Experiment S material.

## Fifth-pass correction focus

The current owner corrections close the r5 findings by restoring the accepted conservative S4 semantics; preventing comparator S4s from rescuing a tested-arm loss; preventing seeded MAPS-favored stress from escaping the STRESS ceiling through efficiency-only counterweight labels; recording `seeded_stress_families[]`; strengthening the anchor safeguard from single/heading anchors to multiple rule-bearing semantic clauses through H1–H5; aligning the report schema; and pinning the sampling-reference model/provider/cutoff before case sampling with deterministic execution-model recomputation later.

## Current next step

**Focused fresh independent review of H1–H5 at the exact current PR head, plus the strengthened semantic-anchor check, explicit S4 branch verification, and a bounded B/M/N/F/G regression check.**

Only `APPROVED FOR CORPUS CONSTRUCTION` opens corpus construction. Approval opens **bounded corpus construction + independent corpus/freeze review**, not benchmark execution.
