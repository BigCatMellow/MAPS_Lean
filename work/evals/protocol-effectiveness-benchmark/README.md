# Protocol Effectiveness Benchmark

Status: **DRAFT SPECIFICATION — NOT EXECUTED**

This folder defines a reusable controlled benchmark for answering a narrow causal question:

> Given otherwise equivalent capable agents, does applying an operating protocol such as MAPS_L improve successful autonomous completion of consequential work enough to justify its cost and complexity?

The benchmark is intentionally **protocol-neutral**. MAPS_L is one treatment configuration, not part of the grading definition. Protocol adherence is diagnostic evidence; it is not itself a success metric.

## Why this exists

MAPS_L claims value beyond final-answer quality: task truth, bounded authority, orchestration, evidence use, verification, recovery, review independence, continuation, and durable operability. A final-artifact-only comparison would miss much of that value. Conversely, a MAPS-specific compliance test could reward ceremony without proving better outcomes.

This benchmark therefore separates four questions:

1. **Effectiveness** — does the protocol complete more work correctly?
2. **Safety/reliability** — does it reduce serious mistakes, false success, unauthorized action, or unrecovered failure?
3. **Efficiency** — what does any improvement cost in tokens, money, latency, tool calls, files read, retries, and human intervention?
4. **Diagnosis** — which mechanisms help or hurt, on which kinds of work, and why?

## Package

- [`BENCHMARK-SPEC.md`](BENCHMARK-SPEC.md) — hypotheses, comparison arms, controls, corpus architecture, portability, validity, and benchmark lifecycle.
- [`CASE-DESIGN.md`](CASE-DESIGN.md) — case families, neutral/regression/holdout mix, hidden contracts, traps, severity, and case-construction rules.
- [`RUN-PROTOCOL.md`](RUN-PROTOCOL.md) — exact execution, randomization, blinding, repetitions, observable trajectory capture, and evaluator procedure.
- [`SCORING-AND-ANALYSIS.md`](SCORING-AND-ANALYSIS.md) — metrics, paired analysis, uncertainty, equivalence, tradeoff rules, ablations, and interpretation.
- [`REPORT-TEMPLATE.md`](REPORT-TEMPLATE.md) — standard result report and failure-analysis format.
- [`REFERENCES.md`](REFERENCES.md) — internal MAPS_L owners and external evaluation references.

## Relationship to existing MAPS_L evaluation

This package does **not** supersede the existing evaluation owners.

- [`../../../playbook/SIMULATION_DESIGN.md`](../../../playbook/SIMULATION_DESIGN.md) remains the reusable method for controlled agent simulations.
- [`../maps-end-to-end-benchmark-v1.json`](../maps-end-to-end-benchmark-v1.json) remains the existing frozen MAPS end-to-end scenario protocol.
- [`../../../runtime/evaluation/evaluator.py`](../../../runtime/evaluation/evaluator.py) remains the deterministic frozen-case evaluator/comparator.
- [`../../../runtime/evaluation/regression_case.py`](../../../runtime/evaluation/regression_case.py) remains the frozen regression-case representation.
- [`../../../playbook/REPAIR_AND_LEARNING.md`](../../../playbook/REPAIR_AND_LEARNING.md) remains the owner for converting real failures into repairs and regression protection.

The protocol-effectiveness benchmark sits **above** those mechanisms. It defines how to compare a protocol-enabled agent to a matched control, while reusing existing MAPS_L evidence and evaluation machinery where appropriate.

## Core experimental shape

Primary comparison:

```text
A — VANILLA
same model + tools + environment + task + limits
without MAPS_L operating protocol

B — PROTOCOL
same model + tools + environment + task + limits
with MAPS_L operating protocol
```

Later validation may add:

```text
C — GENERIC STRUCTURED AGENT
same capabilities plus a competent generic
understand → inspect → plan → execute → test → review → report checklist
without MAPS_L-specific mechanisms
```

The benchmark should first isolate **protocol effects**. A separate system-level experiment may later compare a vanilla agent environment against the complete MAPS_L runtime/harness. Mixing those questions initially would make causal attribution weak.

## Anti-bias rules

1. Freeze task fixtures, hidden acceptance contracts, metrics, evaluator prompts, stopping rules, and analysis rules **before** observing comparative outcomes.
2. Do not build the corpus only from MAPS_L's known historical failures.
3. Use a mix of ordinary neutral work, known regression cases, and sealed novel holdouts.
4. Include unrelated external projects so MAPS_L is tested outside repositories designed around MAPS terminology.
5. Keep the evaluator blind to treatment identity where feasible.
6. Prefer mechanical/objective checks over subjective judgment.
7. Do not require private chain-of-thought; use observable actions, artifacts, state transitions, and bounded decision explanations.
8. Preserve `UNKNOWN` / `NOT_RUN`; never force ambiguous evidence into PASS or FAIL.
9. Report effectiveness, serious failure, and efficiency separately. Do not hide tradeoffs in one weighted score.
10. Never change a frozen benchmark in place to make a candidate look better. Version it.

## Development firewall

Maintain three evidence pools:

```text
DEV / REGRESSION SET
known to developers; used continuously; may guide fixes

FROZEN STANDARD SET
versioned; supports historical score comparisons

SEALED HOLDOUT SET
not inspected during development; opened only at designated evaluation points
```

Once a holdout case has been inspected in detail and a protocol change is made specifically in response to it, the case is no longer a valid holdout. Promote it to regression coverage and replenish the sealed pool.

## Intended result states

A benchmark run may conclude:

- `BETTER`
- `WORSE`
- `EQUIVALENT`
- `INCONCLUSIVE`
- `TRADEOFF`

These meanings are defined before execution in [`SCORING-AND-ANALYSIS.md`](SCORING-AND-ANALYSIS.md). `TRADEOFF` is deliberate: a protocol can improve success while becoming unacceptably slower, more expensive, or more dangerous in another dimension.

## Current gate

This folder is specification only. No benchmark execution, model/API spending, corpus freeze, threshold freeze, MAPS_L protocol modification, or promotion decision is implied by adding it.

Before the first comparative run:

1. independently review this specification for MAPS-favoring assumptions;
2. build and review the initial neutral case corpus;
3. freeze evaluator/model/version/settings and run limits;
4. freeze scoring and practical-equivalence thresholds;
5. seal the holdout subset;
6. then run the smallest smoke comparison.
