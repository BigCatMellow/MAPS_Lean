# Task: protocol effectiveness benchmark

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: benchmark-spec owner
- Risk: `MEDIUM`
- Goal: Establish an independently reviewable, protocol-neutral specification for comparing MAPS_L with matched controls without MAPS-favoring grading, treatment contamination, benchmark leakage, or post-result analyst discretion.
- Parent roadmap: `none — PR #341 is the bounded specification work`
- Related records: [`../evals/protocol-effectiveness-benchmark/README.md`](../evals/protocol-effectiveness-benchmark/README.md); [`../reviews/pr-341-review-evidence.md`](../reviews/pr-341-review-evidence.md); [`../reviews/pr-341-rereview-evidence-56c43aa.md`](../reviews/pr-341-rereview-evidence-56c43aa.md); [`../reviews/pr-341-rereview-evidence-dcc064b.md`](../reviews/pr-341-rereview-evidence-dcc064b.md)
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: repository `AGENTS.md`; package owners; original review at `465d97300cf021840fb1fe0434656ff3772d1db4`; re-review at `56c43aa9c176a98b733c32cfb53b182b3c034b9f`; focused r3 review at `dcc064bbc70648bded8f3e944d4f00c46b198fa5`.
- Authoritative sources: `AGENTS.md` for repository rules; this task for bounded work; each package owner file for its concept; review records as immutable reviewer evidence.
- Evidence labels: review findings are VERIFIED as reviewer findings; F1–F9 correction completion is an OWNER CLAIM pending focused fresh independent verification; benchmark effectiveness remains UNKNOWN because nothing has run.
- Dependencies / preconditions: focused fresh independent re-review of F1–F9 at the current corrected head before any corpus or holdout authoring.

## Change boundary

- MAY CHANGE: `work/evals/protocol-effectiveness-benchmark/**`; this task; PR #341 metadata; review/handoff evidence for this benchmark.
- MUST NOT CHANGE: MAPS_L runtime/protocol behavior, existing frozen regression/end-to-end semantics, benchmark corpus/holdout contents, model/evaluator execution, spending, `main`.
- MAY CHANGE IF NECESSARY: documentation-only cross-links required to route this bounded work.
- HUMAN REAUTHORIZATION REQUIRED: benchmark/model/API spending; material scope expansion beyond specification/correction work; merge path remains governed by repository merge rules.

## Decision authority

- Inherited roadmap authority: user requested creation and correction of the benchmark information in MAPS_L.
- Owner may decide: bounded documentation corrections required to resolve independent review without changing runtime/protocol behavior.
- Resolve internally first: wording, ownership, and experimental definitions.
- Human escalation only if: execution/spend or material objective change is required.

## Acceptance criteria

- [x] Original independent review evidence preserved: `MAJOR CORRECTIONS REQUIRED`.
- [x] B1–B3 and M1–M12 correction pass preserved without removing the reviewer-designated architecture.
- [x] Fresh re-review at `56c43aa...` preserved separately: `MINOR CORRECTIONS REQUIRED`.
- [x] N1–N10 second correction pass preserved.
- [x] Focused r3 re-review at `dcc064b...` preserved separately: `MINOR CORRECTIONS REQUIRED`; F1/F2 MATERIAL, F3–F9 MINOR.
- [x] F1 external-answer/network leakage and canary timing/scope corrected in SPEC/RUN.
- [x] F2/M4 neutral human-response default restored as mandatory policy constraints.
- [x] F3 Smoke withholding window made access-based and material-change list owned only by SPEC.
- [x] F4 S4 arithmetic/alignment, guardrail wiring, crossing basis, one-sided harm, and H5 minimum-n made deterministic.
- [x] F5 COUNTERWEIGHT labels require independently checked tendency/harm-path evidence; operator-authored sampling constrained.
- [x] F6 truth-table gaps closed; accepted blocker classes frozen.
- [x] F7 harness/global auto-load and cross-run state reset defined.
- [x] F8 outcome-affecting responder misroute => paired INVALID/rerun; non-affecting => log only.
- [x] F9 blinding guess task/asymmetry threshold/timing frozen before semantic grades unmask.
- [x] Status remains not executed; no corpus or holdout authored.
- [ ] Focused fresh independent reviewer at the current head returns `APPROVED FOR CORPUS CONSTRUCTION`.

## Verification and evidence

- Verification: compare current owners against F1–F9 in `../reviews/pr-341-rereview-evidence-dcc064b.md`, plus regression check that prior B/M/N fixes remain intact.
- Evidence to preserve: PR/head/diff; all review generations; future approval evidence.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: GitHub documentation branch for PR #341.
- Ordered procedure: preserve r3 review → apply F1–F9 owner corrections → update PR/task status → focused independent re-review.
- Failure branches: if focused re-review finds remaining validity defect, correct only that defect and repeat review before corpus work.
- Rollback / recovery: branch/commit history.
- Security / privacy controls: no actual case secrets/holdout contents introduced; future storage/isolation rules only.
- External side effects: GitHub branch/PR metadata only.
- Effort limit: specification corrections only; no benchmark execution/corpus construction.
- Approved reference: r3 review at `dcc064b...` for F1–F9 scope.
- Operational independence: `N/A — one-off specification correction; future benchmark execution will have its own reproducible package`.
- Reproduction package: package owners + immutable PR/review history.

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
- Network is deny-all by default with answer-bearing upstream routes excluded from any per-case allowlist.
- Standard cases retire from later confirmatory inference after exposure to protocol modifiers.
- Smoke deltas remain hidden from anyone able to edit/freeze current or successor benchmark lines until Standard analysis is locked.
- Human-response content has a mandatory neutral default; responder implementation may not turn check-ins into stalls.
- S4/tradeoff/verdict/H5 decisions are deterministic from frozen inputs/crossing bases.
- COUNTERWEIGHT prevalence requires audited named harm paths, not labels alone.
- Experiment P remains outcome-scored; MAPS runtime/E2E criteria remain outside its primary scorer.

## Completion / handoff

- Completed: F1–F9 owner corrections prepared; all three review generations preserved.
- Not completed: focused fresh independent verification at current head; corpus construction.
- Triage capture: none — findings are represented by durable review evidence and this task.
- Reproduction package: package owner files + PR/review history.
- Current blocker: focused fresh independent re-review.
- Next eligible roadmap task: corpus construction only after `APPROVED FOR CORPUS CONSTRUCTION`.
- Human action required: none unless execution/spending is later requested.
