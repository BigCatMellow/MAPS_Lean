# Protocol Effectiveness Benchmark

Status: **FOURTH CORRECTION PASS APPLIED — AWAITING FOCUSED G1–G10 RE-REVIEW; NOT EXECUTED**

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

G1–G10 are now owner-corrected on this branch. That is an **owner claim, not approval**.

Because correction passes repeatedly deleted previously resolved protections, AGENTS.md invariant 13 now has a mechanical backstop:

- [`RESOLVED-FINDING-ANCHORS.json`](RESOLVED-FINDING-ANCHORS.json) maps every resolved B/M/N/F/G finding to its owner file and required clause;
- [`../../../scripts/check_protocol_effectiveness_benchmark_anchors.py`](../../../scripts/check_protocol_effectiveness_benchmark_anchors.py) hard-codes the complete finding-ID set and fails if an anchor disappears;
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

## Fourth-pass correction focus

The current owner corrections close the r4 findings by restoring Arm C independence/competence/context-cost disclosure; independently auditing every NONE/STRESS/COUNTERWEIGHT label; extending answer-leakage controls to provider-hosted retrieval and run-visible metadata; defining COMPLETE/BLOCKED/INCOMPLETE task-facing semantics; restoring task-facing instruction precedence; removing residual S4/S3/UNSET verdict discretion; masking Smoke evidence before Standard lock; moving the operator-request cutoff to the benchmark package's first commit; covering environment/shell/global-VCS/runner state; and separating external cases by resolution-date/model-training-cutoff relation.

## Current next step

**Focused fresh independent review of G1–G10 at the exact current PR head, plus the resolved-finding anchor check and a bounded B/M/N/F regression check.**

Only `APPROVED FOR CORPUS CONSTRUCTION` opens corpus construction. Approval opens **bounded corpus construction + independent corpus/freeze review**, not benchmark execution.
