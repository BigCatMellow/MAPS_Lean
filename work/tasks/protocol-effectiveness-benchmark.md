# Task: protocol effectiveness benchmark

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: benchmark-spec owner
- Risk: `MEDIUM`
- Goal: Establish an independently reviewable, protocol-neutral specification for comparing MAPS_L with matched controls without MAPS-favoring grading or treatment contamination.
- Parent roadmap: `none — PR #341 is the bounded specification work`
- Related records: [`../evals/protocol-effectiveness-benchmark/README.md`](../evals/protocol-effectiveness-benchmark/README.md); [`../reviews/pr-341-review-evidence.md`](../reviews/pr-341-review-evidence.md)
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: repository `AGENTS.md`; existing simulation/evaluation/runtime owners; PR #341 package; independent review at original head `465d97300cf021840fb1fe0434656ff3772d1db4`.
- Authoritative sources: `AGENTS.md` for repository rules; this task for bounded benchmark-spec work; each package owner file for its assigned benchmark concept.
- Evidence labels: review findings are VERIFIED as reviewer findings; benchmark effectiveness remains UNKNOWN because nothing has been run.
- Dependencies / preconditions: fresh independent re-review at corrected head before corpus construction.

## Change boundary

- MAY CHANGE: `work/evals/protocol-effectiveness-benchmark/**`; this task; PR #341 metadata; review/handoff evidence for this benchmark.
- MUST NOT CHANGE: MAPS_L runtime/protocol behavior, existing frozen regression/end-to-end benchmark semantics, benchmark corpus, model/evaluator execution, spending, `main`.
- MAY CHANGE IF NECESSARY: documentation-only cross-links required to route this bounded work.
- HUMAN REAUTHORIZATION REQUIRED: benchmark/model/API spending; material scope expansion beyond specification/correction work; merge path remains governed by repository merge rules.

## Decision authority

- Inherited roadmap authority: user requested creation and correction of the benchmark information in MAPS_L.
- Owner may decide: documentation structure and corrections required to resolve the independent review without changing runtime/protocol behavior.
- Resolve internally first: exact wording/ownership consolidation and protocol-neutral experimental definitions.
- Human escalation only if: execution/spend or material objective change is required.

## Acceptance criteria

- [x] Independent review evidence for original head is preserved durably.
- [x] B1–B3 corrections are represented in owning specification/case files.
- [x] M1–M12 corrections are represented without removing the reviewer-designated “keep intact” architecture.
- [x] Concept ownership is consolidated to prevent divergent normative copies.
- [x] Status remains not executed / no corpus constructed.
- [ ] Fresh independent reviewer at corrected head returns `APPROVED FOR CORPUS CONSTRUCTION`.

## Verification and evidence

- Verification: inspect corrected branch diff against the independent review findings; fresh independent re-review required.
- Evidence to preserve: PR diff/head; `work/reviews/pr-341-review-evidence.md`; fresh re-review evidence.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: GitHub documentation branch for PR #341.
- Ordered procedure: preserve review → apply docs corrections → update PR status → fresh independent re-review.
- Failure branches: if re-review finds remaining validity defect, correct only that defect and repeat review before corpus work.
- Rollback / recovery: branch/commit history.
- Security / privacy controls: no secrets/holdout contents introduced.
- External side effects: GitHub branch/PR metadata only.
- Effort limit: documentation corrections only; no benchmark execution.
- Approved reference: independent review for original head.
- Operational independence: `N/A — one-off specification correction; future benchmark execution will have its own reproducible run package`
- Reproduction package: package owner files + PR/review evidence are sufficient to reproduce the design state.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Primary endpoint excludes known MAPS regressions.
- Standard/Full requires independent generic structured Arm C before MAPS-specific claims.
- Holdout retirement is exposure-based.
- Runtime E2E/regression criteria are not Experiment P primary criteria.

## Completion / handoff

- Completed: design corrections prepared and original review evidence preserved.
- Not completed: fresh independent re-review at corrected head.
- Triage capture: none — review findings are represented by the review evidence and this correction task.
- Reproduction package: package owner files + immutable PR history.
- Current blocker: fresh independent review.
- Next eligible roadmap task: corpus construction only after `APPROVED FOR CORPUS CONSTRUCTION`.
- Human action required: none unless execution/spending is later requested.
