# Protocol Effectiveness Benchmark

Status: **SIXTH CORRECTION PASS APPLIED — AWAITING FOCUSED I1–I4 RE-REVIEW; NOT EXECUTED**

Primary question:

> Given otherwise equivalent capable agents, does applying an operating protocol such as MAPS_L improve objectively correct autonomous task completion enough to justify its cost, complexity, and failure modes?

MAPS_L is a treatment configuration, not the grading definition. Protocol adherence is diagnostic only.

## Owner / current gate

Parent work: [`../../tasks/protocol-effectiveness-benchmark.md`](../../tasks/protocol-effectiveness-benchmark.md) on PR #341.

Review evidence:

- [`../../reviews/pr-341-review-evidence.md`](../../reviews/pr-341-review-evidence.md) — original: `MAJOR CORRECTIONS REQUIRED`.
- [`../../reviews/pr-341-rereview-evidence-56c43aa.md`](../../reviews/pr-341-rereview-evidence-56c43aa.md) — r2: `MINOR CORRECTIONS REQUIRED`.
- [`../../reviews/pr-341-rereview-evidence-dcc064b.md`](../../reviews/pr-341-rereview-evidence-dcc064b.md) — r3: `MINOR CORRECTIONS REQUIRED`.
- [`../../reviews/pr-341-rereview-evidence-7ec7e1d.md`](../../reviews/pr-341-rereview-evidence-7ec7e1d.md) — r4: `MINOR CORRECTIONS REQUIRED`.
- [`../../reviews/pr-341-rereview-evidence-0aee65b.md`](../../reviews/pr-341-rereview-evidence-0aee65b.md) — r5: `MINOR CORRECTIONS REQUIRED`.
- [`../../reviews/pr-341-rereview-evidence-8b9efd9.md`](../../reviews/pr-341-rereview-evidence-8b9efd9.md) — r6 at `8b9efd95f2cd48843f5eb38273a94eec55a49b58`: `MINOR CORRECTIONS REQUIRED`; H1/H2/H5 resolved, no B/M/N/F/G regression, I1–I4 remaining.

I1–I4 are now owner-corrected on this branch. That is an **owner claim, not approval**.

The invariant-13 backstop is now v3:

- [`RESOLVED-FINDING-ANCHORS.json`](RESOLVED-FINDING-ANCHORS.json) pins all 49 resolved B/M/N/F/G/H findings to rule-bearing semantic clauses, including complete multi-line surfaces where needed;
- [`../../../scripts/check_protocol_effectiveness_benchmark_anchors.py`](../../../scripts/check_protocol_effectiveness_benchmark_anchors.py) independently hard-codes the 49-ID set and minimum anchor counts for historically vulnerable findings;
- the `review-evidence` workflow runs the checker on each PR revision.

Nothing has been executed: no corpus/holdout authored or frozen, no scored candidate/evaluator/model calls, no benchmark spending, and no MAPS_L runtime/protocol behavior changes.

## Package ownership

One concept, one owner:

- [`BENCHMARK-SPEC.md`](BENCHMARK-SPEC.md) — arms, treatment surface, controls, target population/pools, exposure lifecycle, hidden-material/retrieval firewall, thresholds/guardrails, Smoke firewall, version identity.
- [`CASE-DESIGN.md`](CASE-DESIGN.md) — case schema/run-visible boundary, task-facing contract/parser, hidden checks, overlay/counterweight semantics, terminal truth table, severity.
- [`RUN-PROTOCOL.md`](RUN-PROTOCOL.md) — execution, parity/isolation, environment/tool leakage checks, human-response delivery, normalization/blinding, invalidation/reruns.
- [`SCORING-AND-ANALYSIS.md`](SCORING-AND-ANALYSIS.md) — metrics, paired inference, S4/tradeoff/verdict/H5 rules, sensitivity and divergence analysis.
- [`REPORT-TEMPLATE.md`](REPORT-TEMPLATE.md) — reusable report schema only.
- [`REFERENCES.md`](REFERENCES.md) — provenance/methodology only; non-normative.

This README is navigation/status only. Follow the owning file rather than treating summaries here as normative rules.

## Sixth-pass correction focus

- I1: exact known semantic surfaces are pinned rather than headings/prefixes; the checker also enforces minimum anchor counts on vulnerable findings.
- I2: S4 `PRIMARY_BETTER` and harm no longer double-match competing TRADEOFF/WORSE bullets.
- I3: H5 support must match the aggregate verdict and H5 BETTER excludes tested-arm S4 rule firings or registered harm in either supporting stratum.
- I4: report vocabulary now uses only owner-defined verdict/terminal classes, with confirmatory status and forbidden-effect subsets reported separately.

## Current next step

**Fresh focused independent re-review of I1–I4 at the exact current PR head.** It must rerun the semantic-anchor checker and mutation probes, rerun the S4 branch/enumeration test, verify H5/report alignment, and perform a bounded B/M/N/F/G/H regression check.

Only `APPROVED FOR CORPUS CONSTRUCTION` opens bounded corpus construction followed by independent corpus/freeze review. Benchmark execution remains prohibited.
