# Protocol Effectiveness Benchmark

Status: **CORRECTIONS APPLIED — AWAITING FRESH INDEPENDENT RE-REVIEW; NOT EXECUTED**

Primary question:

> Given otherwise equivalent capable agents, does applying an operating protocol such as MAPS_L improve objectively correct autonomous task completion enough to justify its cost, complexity, and failure modes?

This package is protocol-neutral at the grading boundary. MAPS_L is a treatment configuration. Protocol adherence is diagnostic only.

## Owner / current gate

Parent work: PR #341 and the benchmark specification task/review evidence for this branch.

Latest independent review at the original head `465d97300cf021840fb1fe0434656ff3772d1db4` returned **MAJOR CORRECTIONS REQUIRED**. Its corrections are applied on this branch. No corpus may be constructed until a **fresh independent reviewer at the new head** returns:

`APPROVED FOR CORPUS CONSTRUCTION`

No scored benchmark, model/evaluator spending, threshold freeze based on outcomes, runtime change, or protocol promotion has occurred.

## Package ownership

One concept, one owner:

- [`BENCHMARK-SPEC.md`](BENCHMARK-SPEC.md) — arms, Treatment Surface Manifest, controls, target population/pools, holdout lifecycle, thresholds/guardrails, version identity.
- [`CASE-DESIGN.md`](CASE-DESIGN.md) — case schema, neutral output contract, hidden checks, families/counterweights, terminal truth table, severity.
- [`RUN-PROTOCOL.md`](RUN-PROTOCOL.md) — execution, parity/isolation, human responses, logging, normalization/blinding, invalidation, reruns.
- [`SCORING-AND-ANALYSIS.md`](SCORING-AND-ANALYSIS.md) — metrics, paired inference, exact verdict rules, subgroups, ablations, failure divergence.
- [`REPORT-TEMPLATE.md`](REPORT-TEMPLATE.md) — reusable report shape.
- [`REFERENCES.md`](REFERENCES.md) — provenance/methodology only; not runtime authority.
- [`../../tasks/protocol-effectiveness-benchmark.md`](../../tasks/protocol-effectiveness-benchmark.md) — bounded owning task/current gate.
- [`../../reviews/pr-341-review-evidence.md`](../../reviews/pr-341-review-evidence.md) — independent review evidence for the original PR head.

Do not restate normative rules in this README; follow the owning file above.

## Relationship to existing MAPS_L evaluation

This package does **not** supersede existing owners, but Experiment P has a strict boundary:

- [`../../../playbook/SIMULATION_DESIGN.md`](../../../playbook/SIMULATION_DESIGN.md) remains a MAPS_L simulation method. Its required live updates, route/document reporting, and observability failure classes are **not** Experiment P primary-outcome requirements.
- [`../maps-end-to-end-benchmark-v1.json`](../maps-end-to-end-benchmark-v1.json) remains a frozen MAPS end-to-end/runtime evidence protocol. Its MAPS-shaped properties are **diagnostic or Experiment S material**, not Experiment P primary criteria.
- [`../../../runtime/evaluation/evaluator.py`](../../../runtime/evaluation/evaluator.py) and [`../../../runtime/evaluation/regression_case.py`](../../../runtime/evaluation/regression_case.py) remain runtime regression machinery. They are **not the Experiment P scorer** and must not force P into portable MAPS Run Record or one-result-per-case semantics.
- [`../../../playbook/REPAIR_AND_LEARNING.md`](../../../playbook/REPAIR_AND_LEARNING.md) remains the owner for turning real failures into repairs/regression protection after results exist.

Any machine schema needed for Experiment P must be defined once by this package rather than silently extending the runtime evaluator format.

## Experimental shape

- **A — Vanilla:** matched substrate, no tested protocol.
- **B — Protocol:** same substrate plus one frozen offline MAPS_L treatment bundle.
- **C — Generic structured control:** mandatory for Standard/Full before any MAPS-specific contribution claim.
- **Experiment P:** isolates protocol effect.
- **Experiment S:** separately measures the complete MAPS_L system.

Known MAPS regression cases are separate diagnostics, not part of the primary H1/H5 endpoint.

## Anti-bias commitments

The benchmark must be able to show MAPS_L is better, worse, equivalent, inconclusive, or a tradeoff.

In particular:

- hidden contracts contain checks, not unstated process requirements;
- primary population weights are defined from target work characteristics, not MAPS invariants;
- true blockers have resolvable counterweights;
- cases include asking-is-correct, over-continuation, ceremony, context-pressure, foreign-repo artifact-write, instruction-conflict, and review/helper-harm cases;
- external projects are at least half of the primary population;
- evaluator evidence is normalized to reduce treatment-identifying process vocabulary;
- holdouts retire on exposure and have a frozen look count;
- Smoke cannot issue a directional verdict;
- threshold/guardrail values must be frozen before the first scored run;
- arm-exclusive adjudicated S4 failures prevent a clean BETTER label;
- no result is erased by post-hoc benchmark edits.

## Current next step

**Fresh independent re-review at the corrected PR head.**

That reviewer must verify B1–B3 and M1–M12 from the recorded review are actually resolved and that the corrections did not introduce a new MAPS-favoring path. Only then may corpus construction begin.
