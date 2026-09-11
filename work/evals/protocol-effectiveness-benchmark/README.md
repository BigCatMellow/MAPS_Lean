# Protocol Effectiveness Benchmark

Status: **SEVENTH CORRECTION PASS APPLIED — AWAITING FOCUSED J1 RE-REVIEW; NOT EXECUTED**

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
- [`../../reviews/pr-341-rereview-evidence-8b9efd9.md`](../../reviews/pr-341-rereview-evidence-8b9efd9.md) — r6: `MINOR CORRECTIONS REQUIRED`.
- [`../../reviews/pr-341-rereview-evidence-5f1ef8e.md`](../../reviews/pr-341-rereview-evidence-5f1ef8e.md) — r7 at `5f1ef8e090b62c8393113ddb211399646d381c84`: `MINOR CORRECTIONS REQUIRED`; I2–I4 resolved, no B/M/N/F/G/H owner-document regression, J1 is the only gate-holding residual; J2 is optional/NIT.

J1 is now owner-corrected on this branch. That is an **owner claim, not approval**. J2 was deliberately left unchanged because it is optional and another semantic edit would add risk without opening the gate.

The invariant-13 backstop is now v4:

- [`RESOLVED-FINDING-ANCHORS.json`](RESOLVED-FINDING-ANCHORS.json) is a line-reviewable 49-finding map with the exact comparator no-shield protection restored;
- [`../../../scripts/check_protocol_effectiveness_benchmark_anchors.py`](../../../scripts/check_protocol_effectiveness_benchmark_anchors.py) independently hard-codes the complete finding-ID → owner-path map, rejects duplicate/trivial anchors, enforces minimum unique-anchor counts, pins 13 historically vulnerable whole rule sections by normalized content hash, and directly checks canonical report vocabulary;
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

## Seventh-pass correction focus

J1 only: the v3 sentence-presence safeguard was insufficient against additive semantic exceptions, manifest-coordinated owner retargeting, duplicate/trivial anchors, and report-vocabulary additions. v4 adds script-owned structural pins around the independently accepted owner sections without changing those owner semantics.

I2–I4 remain independently resolved from r7. J2 remains optional and was not changed.

## Current next step

**Fresh focused independent re-review of J1 at the exact current PR head.** It must rerun the v4 safeguard, r7 mutation probes 1–9 including 2b and 8a–8c plus additive variants, rerun the 512-state S4 enumeration, and perform a bounded B/M/N/F/G/H regression check.

Only `APPROVED FOR CORPUS CONSTRUCTION` opens bounded corpus construction followed by independent corpus/freeze review. Benchmark execution remains prohibited.
