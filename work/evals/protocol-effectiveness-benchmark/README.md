# Protocol Effectiveness Benchmark

Status: **EIGHTH CORRECTION PASS APPLIED — AWAITING FOCUSED J3 RE-REVIEW; NOT EXECUTED**

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
- [`../../reviews/pr-341-rereview-evidence-5f1ef8e.md`](../../reviews/pr-341-rereview-evidence-5f1ef8e.md) — r7: `MINOR CORRECTIONS REQUIRED`.
- [`../../reviews/pr-341-rereview-evidence-fd2408f.md`](../../reviews/pr-341-rereview-evidence-fd2408f.md) — r8 at `fd2408fda31d574554bf345cde6319fe8313bd90`: `MINOR CORRECTIONS REQUIRED`; I2–I4 and all B/M/N/F/G/H owner findings still resolved; J3 is the only gate-holding residual; J2/J4 are optional.

J3 is now owner-corrected on this branch. That is an **owner claim, not approval**.

The invariant-13 backstop is now v5:

- [`RESOLVED-FINDING-ANCHORS.json`](RESOLVED-FINDING-ANCHORS.json) remains the human-reviewable 49-finding map;
- [`../../../scripts/check_protocol_effectiveness_benchmark_anchors.py`](../../../scripts/check_protocol_effectiveness_benchmark_anchors.py) independently pins the complete finding-ID → owner-path map, normalized whole-document hashes for SPEC/CASE/RUN/SCORING/REPORT, 13 localized rule-section hashes, pinned-heading uniqueness, anchor-quality/minimum-count rules, and canonical report vocabulary;
- an additive contradiction anywhere in a normative owner document now changes its normalized whole-document digest and cannot pass merely by retaining the accepted sentence or section;
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

## Eighth-pass correction focus

J3 only: r8 proved v4 still allowed additive contradictions when moved outside the 13 pinned spans. v5 pins the full normalized normative owner documents while retaining localized section pins for diagnostics and requires every pinned heading to occur exactly once.

The normative owner documents themselves were not edited in this pass. I2–I4 and B/M/N/F/G/H therefore carry forward only subject to fresh verification that those owner blobs remain identical.

## Current next step

**Fresh focused independent re-review of J3 at the exact current PR head.** It must rerun v5, independently recompute the five owner-document hashes from the accepted r7/r8 blobs, repeat r8 probe 9b plus representative out-of-span/duplicate-heading/additive variants, and confirm the normative owner blobs are unchanged.

Only `APPROVED FOR CORPUS CONSTRUCTION` opens bounded corpus construction followed by independent corpus/freeze review. Benchmark execution remains prohibited.
