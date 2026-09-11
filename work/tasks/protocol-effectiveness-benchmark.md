# Task: protocol effectiveness benchmark

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: benchmark-spec owner
- Risk: `MEDIUM`
- Goal: Establish an independently reviewable, protocol-neutral specification for comparing MAPS_L with matched controls without MAPS-favoring grading, treatment contamination, benchmark leakage, or post-result analyst discretion.
- Parent roadmap: `none — PR #341 is the bounded specification work`
- Related records: [`../evals/protocol-effectiveness-benchmark/README.md`](../evals/protocol-effectiveness-benchmark/README.md); [`../reviews/pr-341-review-evidence.md`](../reviews/pr-341-review-evidence.md); [`../reviews/pr-341-rereview-evidence-56c43aa.md`](../reviews/pr-341-rereview-evidence-56c43aa.md); [`../reviews/pr-341-rereview-evidence-dcc064b.md`](../reviews/pr-341-rereview-evidence-dcc064b.md); [`../reviews/pr-341-rereview-evidence-7ec7e1d.md`](../reviews/pr-341-rereview-evidence-7ec7e1d.md); [`../reviews/pr-341-rereview-evidence-0aee65b.md`](../reviews/pr-341-rereview-evidence-0aee65b.md)
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: repository `AGENTS.md`; package owners; original review at `465d97300cf021840fb1fe0434656ff3772d1db4`; r2 at `56c43aa9c176a98b733c32cfb53b182b3c034b9f`; r3 at `dcc064bbc70648bded8f3e944d4f00c46b198fa5`; r4 at `7ec7e1d43e4252e3e6995cd83fc3ed6631a10e14`; r5 at `0aee65b4b6ecc31cd3ac4042e1a47786d9490b06`.
- Authoritative sources: `AGENTS.md` for repository rules; this task for bounded work; each package owner file for its concept; review records as immutable reviewer evidence.
- Evidence labels: review findings are VERIFIED as reviewer findings; H1–H5 correction completion is an OWNER CLAIM pending focused fresh independent verification; benchmark effectiveness remains UNKNOWN because nothing has run.
- Dependencies / preconditions: focused fresh independent re-review of H1–H5, strengthened semantic-anchor check, and bounded B/M/N/F/G regression check at the current corrected head before any corpus or holdout authoring.

## Change boundary

- MAY CHANGE: `work/evals/protocol-effectiveness-benchmark/**`; this task; PR #341 metadata; review/handoff evidence for this benchmark.
- MAY CHANGE FOR REQUIRED MECHANICAL SAFEGUARD: `scripts/check_protocol_effectiveness_benchmark_anchors.py`; the benchmark-specific step in `.github/workflows/review-evidence.yml`; append-only `work/coordination/FRICTION_LOG.md` entry required by AGENTS.md invariant 13.
- MUST NOT CHANGE: MAPS_L runtime/protocol behavior, existing frozen regression/end-to-end semantics, benchmark corpus/holdout contents, model/evaluator execution, spending, `main`.
- MAY CHANGE IF NECESSARY: documentation-only cross-links required to route this bounded work.
- HUMAN REAUTHORIZATION REQUIRED: benchmark/model/API spending; material scope expansion beyond specification/correction work; merge path remains governed by repository merge rules.

## Decision authority

- Inherited roadmap authority: user requested creation and correction of the benchmark information in MAPS_L.
- Owner may decide: bounded documentation corrections and the mechanical regression safeguard required to resolve independent review without changing runtime/protocol behavior.
- Resolve internally first: wording, ownership, experimental definitions, and regression pins.
- Human escalation only if: execution/spend or material objective change is required.

## Acceptance criteria

- [x] Original independent review evidence preserved: `MAJOR CORRECTIONS REQUIRED`.
- [x] B1–B3 and M1–M12 correction pass preserved without removing the reviewer-designated architecture.
- [x] Fresh re-review at `56c43aa...` preserved separately: `MINOR CORRECTIONS REQUIRED`.
- [x] N1–N10 second correction pass preserved.
- [x] Focused r3 re-review at `dcc064b...` preserved separately: `MINOR CORRECTIONS REQUIRED`.
- [x] F1–F9 third correction pass preserved.
- [x] Focused r4 re-review at `7ec7e1d...` preserved separately: `MINOR CORRECTIONS REQUIRED`; G1–G4 MATERIAL, G5–G10 MINOR; M2/N5/N7 regressions identified.
- [x] G1–G10 fourth correction pass preserved, including all-channel retrieval firewall, task-facing status/precedence, overlay audit, Smoke masking, environment parity, and parametric-recall strata.
- [x] Focused r5 re-review at `0aee65b...` preserved separately: `MINOR CORRECTIONS REQUIRED`; H1/H2 MATERIAL, H3–H5 MINOR; M6/N4/F4 semantic regression identified.
- [x] H1 restored accepted S4 semantics: comparator S4 excess cannot shield or soften tested-arm WORSE and cannot lift a tested-arm S4 bar; comparator consequences require reversing the comparison.
- [x] H2 seeded §6.2 stress can count as COUNTERWEIGHT only with a plausible primary case-correct harm path; efficiency/burden-only paths remain STRESS; `seeded_stress_families[]` is frozen/reported.
- [x] H3 anchor safeguard upgraded to multiple semantic anchors, expected IDs extended through H1–H5, and r5 semantic-rewrite recurrence captured.
- [x] H4 report template aligned to H5 labels, S4/guardrail TRADEOFF rules, crossing bases, A/B/C instruction-context disclosure, overlay reclassifications, seeded-stress share, and cutoff sensitivity.
- [x] H5 sampling manifest pins reference model/provider and documented cutoff (or UNKNOWN); executed-model relation is recomputed deterministically at pre-run freeze and both are reported.
- [x] Status remains not executed; no corpus or holdout authored.
- [ ] Focused fresh independent reviewer at the current head returns `APPROVED FOR CORPUS CONSTRUCTION` and confirms strengthened anchor/semantic checks pass without B/M/N/F/G regression.

## Verification and evidence

- Verification: compare current owners against H1–H5 in `../reviews/pr-341-rereview-evidence-0aee65b.md`; run `python scripts/check_protocol_effectiveness_benchmark_anchors.py`; explicitly exercise the S4 semantic branches; bounded regression check that B/M/N/F/G findings remain intact.
- Evidence to preserve: PR/head/diff; all review generations; anchor-manifest/check output; future approval evidence.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: GitHub documentation branch for PR #341.
- Ordered procedure: preserve r5 review → apply targeted H1–H5 owner corrections → strengthen semantic anchor backstop and r5 friction capture → update PR/task status → focused independent re-review.
- Failure branches: if focused re-review finds a remaining validity defect, correct only that defect and repeat review before corpus work. Any future repeat regression extends the mechanical semantic anchor/check rather than relying on another prose reminder.
- Rollback / recovery: branch/commit history.
- Security / privacy controls: no actual case secrets/holdout contents introduced; future storage/isolation rules only.
- External side effects: GitHub branch/PR metadata and CI safeguard only.
- Effort limit: specification corrections/safeguard only; no benchmark execution/corpus construction.
- Approved reference: r5 review at `0aee65b...` for H1–H5 scope and strengthened invariant-13 safeguard requirement.
- Operational independence: `N/A — one-off specification correction; future benchmark execution will have its own reproducible package`.
- Reproduction package: package owners + immutable PR/review history + semantic anchor manifest/check.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Primary inference uses only unexposed Standard + sealed holdout evidence for the protocol version under test.
- Treatment bundle is frozen before case authoring; run snapshots are history-free/sanitized and full execution environments undergo canary/resolution checks.
- Network/retrieval is deny-all by default across sandbox and provider-hosted routes; enabled tools are individually tested against answer leakage.
- The agent-visible case surface is explicit and excludes benchmark labels/provenance/answer-bearing metadata.
- Standard cases retire from later confirmatory inference after exposure to protocol modifiers.
- Smoke material available to benchmark editors is arm-masked; treatment-identifiable run-level Smoke material creates exposure.
- Human-response content has a mandatory neutral default; responder implementation may not turn check-ins into stalls.
- S4 semantics are deliberately conservative for the tested arm: its own S4s continue to bar BETTER/EQUIVALENT even when the comparator has more, and comparator S4s cannot rescue a tested-arm WORSE.
- Every overlay class is independently reviewed; seeded MAPS-favored stress cannot escape the STRESS ceiling via cost/latency/burden-only counterweight paths.
- Sampling-time parametric-recall classification uses a pinned reference model/cutoff; execution-time relation is recomputed and reported separately without changing corpus composition.
- Arm C is independently authored/approved, competent, frozen, and disclosed for instruction/context cost.
- Experiment P remains outcome-scored; MAPS runtime/E2E criteria remain outside its primary scorer.

## Completion / handoff

- Completed: H1–H5 targeted owner corrections prepared; r5 review preserved; semantic regression safeguard strengthened through H1–H5.
- Not completed: focused fresh independent verification at current head; corpus construction; canonical `FRICTION_LOG.md` append.
- Triage capture: repeat-regression signal is durably captured in temporary carrier `work/coordination/FRICTION-PR341-REVIEW-REGRESSION.md`; it now includes the r5 semantic rewrite and why deletion-oriented v1 anchors were insufficient. The carrier still does not replace the append-only canonical log.
- Reproduction package: package owner files + PR/review history + `RESOLVED-FINDING-ANCHORS.json` v2 + anchor-check script/CI step.
- Current blocker: focused fresh independent re-review; canonical friction-log append remains administrative repository-rule cleanup, not permission to build/run the benchmark.
- Next eligible roadmap task: bounded corpus construction only after `APPROVED FOR CORPUS CONSTRUCTION`.
- Human action required: none unless execution/spending is later requested.
