# Task: protocol effectiveness benchmark

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: benchmark-spec owner
- Risk: `MEDIUM`
- Goal: Establish an independently reviewable, protocol-neutral specification for comparing MAPS_L with matched controls without MAPS-favoring grading, treatment contamination, benchmark leakage, or post-result analyst discretion.
- Parent roadmap: `none — PR #341 is the bounded specification work`
- Related records: [`../evals/protocol-effectiveness-benchmark/README.md`](../evals/protocol-effectiveness-benchmark/README.md); [`../reviews/pr-341-review-evidence.md`](../reviews/pr-341-review-evidence.md); [`../reviews/pr-341-rereview-evidence-56c43aa.md`](../reviews/pr-341-rereview-evidence-56c43aa.md)
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: repository `AGENTS.md`; existing simulation/evaluation/runtime owners; PR #341 package; original review at `465d97300cf021840fb1fe0434656ff3772d1db4`; fresh re-review at `56c43aa9c176a98b733c32cfb53b182b3c034b9f`.
- Authoritative sources: `AGENTS.md` for repository rules; this task for bounded benchmark-spec work; each package owner file for its assigned benchmark concept; review records as evidence of reviewer findings.
- Evidence labels: original and re-review findings are VERIFIED as reviewer findings; N1–N10 correction completion is an OWNER CLAIM pending focused fresh independent verification; benchmark effectiveness remains UNKNOWN because nothing has been run.
- Dependencies / preconditions: focused fresh independent re-review of the N1–N10 correction delta at the new head before corpus construction.

## Change boundary

- MAY CHANGE: `work/evals/protocol-effectiveness-benchmark/**`; this task; PR #341 metadata; review/handoff evidence for this benchmark.
- MUST NOT CHANGE: MAPS_L runtime/protocol behavior, existing frozen regression/end-to-end benchmark semantics, benchmark corpus/holdout contents, model/evaluator execution, spending, `main`.
- MAY CHANGE IF NECESSARY: documentation-only cross-links required to route this bounded work.
- HUMAN REAUTHORIZATION REQUIRED: benchmark/model/API spending; material scope expansion beyond specification/correction work; merge path remains governed by repository merge rules.

## Decision authority

- Inherited roadmap authority: user requested creation and correction of the benchmark information in MAPS_L.
- Owner may decide: bounded documentation structure/corrections required to resolve independent review without changing runtime/protocol behavior.
- Resolve internally first: exact wording/ownership consolidation and protocol-neutral experimental definitions.
- Human escalation only if: execution/spend or material objective change is required.

## Acceptance criteria

- [x] Original independent review evidence is preserved.
- [x] First-pass B1–B3 and M1–M12 corrections were applied without removing the reviewer-designated architecture.
- [x] Fresh independent re-review at `56c43aa...` is preserved separately; verdict `MINOR CORRECTIONS REQUIRED`, no blocking defect.
- [x] N1 snapshot/history/hidden-secret leakage rules are corrected in owning files.
- [x] N2 treatment/holdout/standard exposure lifecycle is corrected.
- [x] N3 Smoke→Standard re-freeze path is closed for a benchmark line.
- [x] N4 S4/tradeoff/verdict/H5 logic is made deterministic through frozen rule IDs.
- [x] N5 target population and stress/counterweight prevalence bounds are explicit.
- [x] N6–N9 terminal parsing, treatment-surface edges, human-response routing, and blinding-power rules are corrected.
- [x] N10 report schema and duplicated normative summaries are corrected.
- [x] Status remains not executed / no corpus or holdout authored.
- [ ] Focused fresh independent reviewer at the new corrected head returns `APPROVED FOR CORPUS CONSTRUCTION`.

## Verification and evidence

- Verification: compare current package against N1–N10 in `../reviews/pr-341-rereview-evidence-56c43aa.md`; inspect PR changed paths; focused independent re-review required.
- Evidence to preserve: PR/head/diff; both independent review records; future focused re-review evidence.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: GitHub documentation branch for PR #341.
- Ordered procedure: preserve re-review → apply N1–N10 docs corrections → update PR/task status → focused independent re-review.
- Failure branches: if focused re-review finds a remaining validity defect, correct only that defect and repeat review before corpus work.
- Rollback / recovery: branch/commit history.
- Security / privacy controls: no secrets or actual holdout contents introduced; future secret storage is specified but not created here.
- External side effects: GitHub branch/PR metadata only.
- Effort limit: documentation corrections only; no benchmark execution or corpus construction.
- Approved reference: fresh re-review at `56c43aa...` for N1–N10 correction scope.
- Operational independence: `N/A — one-off specification correction; future benchmark execution will have its own reproducible package`
- Reproduction package: package owner files + immutable PR/review history.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Primary inference uses only unexposed Standard + sealed holdout work for the protocol version under test.
- Treatment bundle is frozen before case authoring; MAPS_HOME run snapshots are history-free/sanitized with secret-canary verification.
- Standard cases retire from later confirmatory inference after exposure to protocol modifiers.
- A benchmark line carries one Arm-C text and one Threshold Manifest from Smoke through Standard/Full.
- S4/tradeoff/verdict/H5 rules are referenced by frozen deterministic rule IDs.
- Primary overlay prevalence is bounded: no-trap floor, stress ceiling, counterweight floor.
- Experiment P remains outcome-scored; MAPS runtime/E2E criteria remain outside its primary scorer.

## Completion / handoff

- Completed: N1–N10 owner corrections prepared; both review generations preserved.
- Not completed: focused fresh independent verification at the new head; corpus construction.
- Triage capture: none — reviewer findings are represented by review evidence and this correction task.
- Reproduction package: package owner files + PR/review history.
- Current blocker: focused fresh independent re-review.
- Next eligible roadmap task: corpus construction only after `APPROVED FOR CORPUS CONSTRUCTION`.
- Human action required: none unless execution/spending is later requested.
