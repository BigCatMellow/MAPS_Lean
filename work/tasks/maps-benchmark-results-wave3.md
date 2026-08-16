# Task: MAPS benchmark result validation Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `maps-benchmark-results-wave3`
- Risk: `MEDIUM`
- Goal: validate and score externally produced Layer 2/Layer 3 benchmark evidence against the exact frozen benchmark protocol without executing agents, production sampling, or external actions.

## Inputs and source of truth

- Inputs:
  - root `AGENTS.md`
  - `work/evals/maps-end-to-end-benchmark-v1.json`
  - `work/notes/2026-08-15-maps-end-to-end-benchmark.md`
  - accepted frozen protocol blob `1de87962caa9f66319dbb9f6f192254569ab0cd3`
- Authoritative sources: repository operating contract plus the frozen benchmark protocol for this evaluation.
- Current integration fact: the former PR #42 head `beeef987e25509136ff3de5b79263c984cc501da` was incorporated into `main` by PR #55 before its two independent-review evidence-identity blockers were cleared. This task therefore also carries the narrow repair for those defects; it does not treat that merge as review acceptance.
- Dependencies / preconditions: frozen protocol exists and its exact content identity can be proven before scoring.

## Change boundary

- MAY CHANGE:
  - `runtime/benchmark_results.py`
  - `tests/test_benchmark_results.py`
  - `tests/test_benchmark_result_measurements.py`
  - `tests/test_benchmark_result_evidence_binding.py`
  - this task file
  - `work/notes/2026-08-15-maps-benchmark-results.md`
- MUST NOT CHANGE:
  - runtime task/state/policy/harness behavior
  - frozen benchmark protocol truth
  - external systems or operator/user-visible artifacts
  - production sampling policy
  - unrelated PR branches
- MAY CHANGE IF NECESSARY: result/scoring contract only through explicit task amendment and tests.
- OPERATOR APPROVAL REQUIRED: actual consequential external benchmark execution or any production change based on benchmark results.

## Decision authority

- Owner may decide: bounded result schema, provenance-state contract, deterministic scoring/report shape, exact protocol/evidence identity binding, focused tests.
- Owner must escalate: execution policy, external side effects, production sampling, truth-label changes, automatic promotion, or authority semantics beyond protocol requirements.

## Acceptance criteria

- [x] Every asserted property `PASS`/`FAIL` requires at least one observable evidence reference.
- [x] Required `UNKNOWN`/`NOT_RUN` properties remain `INCOMPLETE`.
- [x] Any required `FAIL`, including QUALITY failures, fails its scenario.
- [x] Failed BLOCKER properties are explicitly reported and prevent candidate advancement.
- [x] Layer 3 rejects controlled/synthetic fixture kinds mechanically.
- [x] Layer 3 requires VERIFIED task, run, and outcome provenance.
- [x] `E2E-L3-001` additionally requires VERIFIED operator-visible result and external-authority provenance.
- [x] Counted operator intervention requires VERIFIED intervention provenance where the protocol requires it.
- [x] Activity/cost measurements do not influence pass/fail status.
- [x] Missing scenario/property evidence remains incomplete rather than guessed.
- [x] Unknown scenarios/properties/result fields fail closed.
- [x] Count-like measurements reject fractional values.
- [x] Scoring is mechanically bound to the exact frozen protocol content; a same-version changed protocol fails closed.
- [x] Reports retain the exact validated property evidence refs and provenance states/refs needed to identify what was scored.
- [x] Normalized supplied result evidence has a deterministic immutable SHA-256 reference; changing evidence/provenance changes that identity.
- [x] Report output is deterministic and explicitly non-authorizing.

## Verification and evidence

- Verification:
  - `python -m unittest tests.test_benchmark_results tests.test_benchmark_result_measurements tests.test_benchmark_result_evidence_binding -v`
  - full PR Runtime stack CI
- Evidence to preserve: exact branch head, frozen protocol identity, result-evidence identity, CI run, changed-file list, review packet.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: repository Python runtime.
- Ordered procedure: verify exact frozen protocol identity → validate externally produced result schema → retain/bind exact evidence/provenance identity → evaluate provenance eligibility → score required properties → aggregate without weighted score.
- Failure branches: unavailable or changed frozen protocol fails closed; malformed result fails closed; unknown/missing evidence remains incomplete; synthetic Layer 3 fails.
- Rollback / recovery: revert isolated repair commits; no migration or external mutation exists.
- Security / privacy controls: reports retain bounded evidence/provenance references needed for reproducibility, not private chain-of-thought or raw private prompt/file content.
- External side effects: none.
- Effort limit: result adapter/scorer only; no scenario runner, canonical-source resolver, or production sampler.
- Approved reference: exact frozen benchmark protocol content.

## Stop / escalate

Stop rather than guess if:

- a benchmark scenario must actually perform an external action;
- protocol truth/eligibility needs to change;
- a provenance reference cannot be categorized without another accepted interface;
- result scoring would need to infer human/operator intent from arbitrary messages.

Escalate to: operator / separately shaped execution or integration task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- `VERIFIED` provenance remains a scorer input contract; later adapters must earn that state from canonical/accepted evidence rather than setting it from prose.
- Exact evidence/provenance refs are preserved for reviewability but do not become authority merely by appearing in an evaluation report.
- The scorer does not treat good cost/runtime/activity measurements as success evidence.
- Completion of the benchmark is evidence only and still cannot self-authorize a production change.
- The implementation owner who made the evidence-identity repair cannot provide the independent review for that repaired head.

## Completion / handoff

- Completed: bounded result validator/scorer, count hardening, exact frozen-protocol binding, exact evidence/provenance preservation, deterministic evidence identity, adversarial tests.
- Not completed: synchronization onto then-current `main`, independent exact-head review, actual Layer 2 execution, or Layer 3 production sampling.
- Current blocker: integration must synchronize this repaired branch with current `main` rather than merely retargeting its base, then obtain fresh full Runtime CI and independent exact-head review.
- Next action if not DONE: synchronize against current accepted `main`, verify the resulting tree/delta, run full CI, and hand the immutable base/head packet to an independent reviewer.
