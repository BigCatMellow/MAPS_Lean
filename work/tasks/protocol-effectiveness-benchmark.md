# Task: protocol effectiveness benchmark

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `PLANNING / EVALUATION`
- Owner: benchmark orchestration owner
- Risk: `MEDIUM`
- Goal: Carry the independently approved protocol-effectiveness design through a contamination-resistant primary-corpus/holdout freeze, then stop before benchmark execution.
- Parent roadmap: `none — PR #341 is the bounded benchmark work`
- Autonomous continuation: `YES`

## Current verified state

- Pre-corpus design gate: **APPROVED FOR CORPUS CONSTRUCTION** at reviewed head `369bccaf68b258c70eb6efec0c9f70115c8014cb`.
- Current independent approval: [`../reviews/pr-341-rereview-evidence-369bcca.md`](../reviews/pr-341-rereview-evidence-369bcca.md).
- Canonical exact-head evidence was rebound to the approved design head before corpus-phase edits.
- J3/v5 safeguard resolved; I2–I4 and all B/M/N/F/G/H owner findings remain resolved; 512-state S4 result carried forward with zero ambiguity/mismatch.
- Benchmark effectiveness remains `UNKNOWN`: no candidate agents, benchmark evaluators/models/APIs, Smoke, Standard, or spend have occurred.

## Current phase

Pre-authoring freeze package is being instantiated under:

- [`../evals/protocol-effectiveness-benchmark/pre-corpus/TREATMENT-SURFACE-MANIFEST.md`](../evals/protocol-effectiveness-benchmark/pre-corpus/TREATMENT-SURFACE-MANIFEST.md)
- [`../evals/protocol-effectiveness-benchmark/pre-corpus/GENERIC-CONTROL.md`](../evals/protocol-effectiveness-benchmark/pre-corpus/GENERIC-CONTROL.md)
- [`../evals/protocol-effectiveness-benchmark/pre-corpus/TARGET-WORK-SAMPLING-MANIFEST.md`](../evals/protocol-effectiveness-benchmark/pre-corpus/TARGET-WORK-SAMPLING-MANIFEST.md)
- [`../evals/protocol-effectiveness-benchmark/pre-corpus/CUSTODY-AND-EXPOSURE-PLAN.md`](../evals/protocol-effectiveness-benchmark/pre-corpus/CUSTODY-AND-EXPOSURE-PLAN.md)

Child task: [`protocol-effectiveness-corpus-construction.md`](protocol-effectiveness-corpus-construction.md).

## Source of truth

- `AGENTS.md` — authority/invariants.
- Approved five normative owner documents under `work/evals/protocol-effectiveness-benchmark/` — benchmark rules; v5 whole-document pins mean deliberate edits require checker update + fresh review.
- This task — parent phase/state only.
- Child corpus task — exact construction/custody contract.

## Change boundary

- MAY CHANGE: non-normative pre-corpus manifests, corpus-phase task/review/handoff records, benchmark-specific tooling needed to package/hash/freeze those artifacts, PR #341 metadata.
- MUST NOT CHANGE without a new design review: the five accepted normative owner documents or their experimental semantics.
- MUST NOT: expose selected primary/holdout case content to MAPS_L protocol modifiers; execute benchmark arms; call benchmark evaluator/model APIs; spend money; change MAPS_L runtime/protocol behavior; merge PR #341.
- HUMAN REAUTHORIZATION REQUIRED: spending/paid execution, new credentials or storage accounts, merge, or material objective expansion.

## Acceptance criteria for corpus phase

- [x] Design approval preserved durably and bound to reviewed SHA.
- [ ] Treatment Surface Manifest has exact bundle inventory/hash, frozen launcher/bootstrap, measured A/B/C instruction/context costs, and independently approved Arm C.
- [ ] Independent curator freezes concrete source pools, reference model/cutoff, deterministic selection inputs, and primary Standard/holdout allocation before selecting cases.
- [ ] Eligible access-controlled custodian exists before any selected primary case content is created.
- [ ] Initial primary corpus and sealed holdout are constructed under the approved sampling/custody rules without exposure to protocol modifiers.
- [ ] Independent overlay/corpus reviewer verifies strata, leakage boundaries, hidden-check neutrality, case truth, custody, hashes, and freeze package.
- [ ] Fresh independent corpus/pre-freeze review returns the required approval for the next pre-run gate.
- [ ] No benchmark execution occurs in this task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Current blocker / continuation

Public pre-authoring shaping may continue in this repository. **Selected primary case content may not be created here yet.** The approved exposure rules are access-based, and the current repository/user context can influence MAPS_L; therefore an eligible independent curator/custodian with storage inaccessible to protocol modifiers is a real dependency, not a preference.

Next eligible action: finish the non-secret pre-authoring freeze package, then dispatch it to an independent curator/custodian for freeze review and case construction. Benchmark execution remains a later gate.
