# Protocol Effectiveness Benchmark

Status: **THIRD CORRECTION PASS APPLIED — AWAITING FOCUSED F1–F9 RE-REVIEW; NOT EXECUTED**

Primary question:

> Given otherwise equivalent capable agents, does applying an operating protocol such as MAPS_L improve objectively correct autonomous task completion enough to justify its cost, complexity, and failure modes?

MAPS_L is a treatment configuration, not the grading definition. Protocol adherence is diagnostic only.

## Owner / current gate

Parent work: [`../../tasks/protocol-effectiveness-benchmark.md`](../../tasks/protocol-effectiveness-benchmark.md) on PR #341.

Review evidence:

- [`../../reviews/pr-341-review-evidence.md`](../../reviews/pr-341-review-evidence.md) — original review at `465d97300cf021840fb1fe0434656ff3772d1db4`: `MAJOR CORRECTIONS REQUIRED`.
- [`../../reviews/pr-341-rereview-evidence-56c43aa.md`](../../reviews/pr-341-rereview-evidence-56c43aa.md) — re-review at `56c43aa9c176a98b733c32cfb53b182b3c034b9f`: `MINOR CORRECTIONS REQUIRED`.
- [`../../reviews/pr-341-rereview-evidence-dcc064b.md`](../../reviews/pr-341-rereview-evidence-dcc064b.md) — focused r3 review at `dcc064bbc70648bded8f3e944d4f00c46b198fa5`: `MINOR CORRECTIONS REQUIRED`; two material residuals (F1/F2) plus F3–F9 minor text gaps.

F1–F9 are now owner-corrected on this branch. That is an **owner claim, not approval**.

Corpus/holdout construction remains closed until a fresh independent reviewer at the current head returns:

`APPROVED FOR CORPUS CONSTRUCTION`

Nothing has been executed: no corpus/holdout authored or frozen, no scored candidate/evaluator/model calls, no benchmark spending, and no MAPS_L runtime/protocol behavior changes.

## Package ownership

One concept, one owner:

- [`BENCHMARK-SPEC.md`](BENCHMARK-SPEC.md) — arms, Treatment Surface Manifest, controls, target population/pools, exposure lifecycle, hidden-material/network firewall, thresholds/guardrails, Smoke information firewall, version identity.
- [`CASE-DESIGN.md`](CASE-DESIGN.md) — case schema, common task-facing contract/parser, hidden checks, families/counterweights, terminal truth table, severity.
- [`RUN-PROTOCOL.md`](RUN-PROTOCOL.md) — execution, parity/isolation, full-environment leakage checks, human-response delivery, normalization/blinding, invalidation/reruns.
- [`SCORING-AND-ANALYSIS.md`](SCORING-AND-ANALYSIS.md) — metrics, paired inference, S4/tradeoff/verdict/H5 rules, UNKNOWN sensitivity, subgroups, ablations, divergence analysis.
- [`REPORT-TEMPLATE.md`](REPORT-TEMPLATE.md) — reusable report schema.
- [`REFERENCES.md`](REFERENCES.md) — provenance/methodology only; non-normative.

This README is navigation/status only.

## Existing MAPS_L evaluation boundary

Experiment P does not inherit primary grading requirements from `SIMULATION_DESIGN.md`, `maps-end-to-end-benchmark-v1.json`, `runtime/evaluation/evaluator.py`, or `runtime/evaluation/regression_case.py`. Their MAPS-shaped process/runtime properties remain diagnostic, runtime-regression, or Experiment S material.

## Current next step

**Focused fresh independent review of F1–F9 at the current PR head.**

The reviewer should use `work/reviews/pr-341-rereview-evidence-dcc064b.md` as the finding source, verify those corrections in their owning files, and perform a bounded regression check that prior B/M/N fixes remain intact.

Only `APPROVED FOR CORPUS CONSTRUCTION` opens corpus construction. Approval opens **corpus construction + independent corpus review**, not benchmark execution.
