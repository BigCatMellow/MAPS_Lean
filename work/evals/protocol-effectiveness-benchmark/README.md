# Protocol Effectiveness Benchmark

Status: **SECOND CORRECTION PASS APPLIED — AWAITING FOCUSED FRESH RE-REVIEW; NOT EXECUTED**

Primary question:

> Given otherwise equivalent capable agents, does applying an operating protocol such as MAPS_L improve objectively correct autonomous task completion enough to justify its cost, complexity, and failure modes?

MAPS_L is a treatment configuration, not the grading definition. Protocol adherence is diagnostic only.

## Owner / current gate

Parent work: [`../../tasks/protocol-effectiveness-benchmark.md`](../../tasks/protocol-effectiveness-benchmark.md) on PR #341.

Review evidence:

- [`../../reviews/pr-341-review-evidence.md`](../../reviews/pr-341-review-evidence.md) — original review at `465d97300cf021840fb1fe0434656ff3772d1db4`: `MAJOR CORRECTIONS REQUIRED`.
- [`../../reviews/pr-341-rereview-evidence-56c43aa.md`](../../reviews/pr-341-rereview-evidence-56c43aa.md) — fresh re-review at `56c43aa9c176a98b733c32cfb53b182b3c034b9f`: `MINOR CORRECTIONS REQUIRED`; no blocking defect remained; N1–N10 required bounded text corrections.

N1–N10 are now owner-applied on this branch. That is **not approval**.

Corpus construction remains closed until a focused fresh independent reviewer at the current corrected head returns:

`APPROVED FOR CORPUS CONSTRUCTION`

Nothing has been executed: no corpus/holdout has been authored or frozen, no scored model/evaluator run or spending occurred, and no MAPS_L runtime/protocol behavior changed.

## Package ownership

One concept, one owner:

- [`BENCHMARK-SPEC.md`](BENCHMARK-SPEC.md) — arms, Treatment Surface Manifest, controls, target population/pools, exposure lifecycle, thresholds/guardrails, version identity.
- [`CASE-DESIGN.md`](CASE-DESIGN.md) — case schema, common task-facing contract, hidden checks, families/counterweights, terminal truth table/parser, severity.
- [`RUN-PROTOCOL.md`](RUN-PROTOCOL.md) — execution, snapshot isolation/canaries, human-response delivery, logging, normalization/blinding, invalidation/reruns.
- [`SCORING-AND-ANALYSIS.md`](SCORING-AND-ANALYSIS.md) — metrics, paired inference, exact S4/tradeoff/verdict/H5 rules, subgroups, ablations, divergence analysis.
- [`REPORT-TEMPLATE.md`](REPORT-TEMPLATE.md) — frozen report schema.
- [`REFERENCES.md`](REFERENCES.md) — provenance/methodology only; not runtime authority.

This README is navigation/status only. Follow the owning file rather than treating summaries here as normative rules.

## Relationship to existing MAPS_L evaluation

Experiment P does **not** replace or inherit primary grading requirements from existing MAPS_L evaluation owners:

- [`../../../playbook/SIMULATION_DESIGN.md`](../../../playbook/SIMULATION_DESIGN.md) remains a MAPS_L simulation method; its live-update/observability procedure is not Experiment P primary scoring.
- [`../maps-end-to-end-benchmark-v1.json`](../maps-end-to-end-benchmark-v1.json) remains a MAPS end-to-end/runtime evidence protocol; its MAPS-shaped properties are diagnostic/Experiment S material.
- [`../../../runtime/evaluation/evaluator.py`](../../../runtime/evaluation/evaluator.py) and [`../../../runtime/evaluation/regression_case.py`](../../../runtime/evaluation/regression_case.py) remain runtime regression machinery, not the Experiment P scorer.
- [`../../../playbook/REPAIR_AND_LEARNING.md`](../../../playbook/REPAIR_AND_LEARNING.md) remains the repair/regression owner after evidence exists.

Any Experiment P machine schema is defined once by this package.

## Current next step

**Focused fresh independent re-review of the N1–N10 correction delta at the current PR head.**

The reviewer should use `work/reviews/pr-341-rereview-evidence-56c43aa.md` as the finding source and verify current owner files rather than re-opening already resolved B/M findings unless the delta regressed them.

Only an `APPROVED FOR CORPUS CONSTRUCTION` verdict opens corpus construction.
