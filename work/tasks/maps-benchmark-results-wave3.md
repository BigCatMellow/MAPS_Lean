# Task: MAPS benchmark result validation Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `maps-benchmark-results-wave3`
- Risk: `MEDIUM`
- Goal: validate and score externally produced Layer 2/Layer 3 benchmark evidence against the frozen PR #40 protocol without executing agents, production sampling, or external actions.

## Inputs and source of truth

- Inputs:
  - root `AGENTS.md`
  - `work/evals/maps-end-to-end-benchmark-v1.json`
  - `work/notes/2026-08-15-maps-end-to-end-benchmark.md`
  - PR #40 exact stacking head `85ca58db52c81dd250b89316ecbc54785aeb9e18`
- Authoritative sources: repository operating contract and the frozen benchmark protocol for this experiment.
- Evidence labels: PR #40 is an experimental dependency, not merged production authority.
- Dependencies / preconditions: frozen protocol exists and mechanically validates.

## Change boundary

- MAY CHANGE:
  - `runtime/benchmark_results.py`
  - `tests/test_benchmark_results.py`
  - this task file
  - `work/notes/2026-08-15-maps-benchmark-results.md`
- MUST NOT CHANGE:
  - runtime task/state/policy/harness behavior
  - benchmark protocol truth in PR #40
  - external systems or operator/user-visible artifacts
  - production sampling policy
  - PR #20-#40 branches
- MAY CHANGE IF NECESSARY: result/scoring contract only through explicit task amendment and tests.
- OPERATOR APPROVAL REQUIRED: actual consequential external benchmark execution or any production change based on benchmark results.

## Decision authority

- Owner may decide: bounded result schema, provenance-state contract, deterministic scoring/report shape, focused tests.
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
- [x] Report is deterministic and explicitly non-authorizing.

## Verification and evidence

- Verification:
  - `python -m unittest tests.test_benchmark_results -v`
  - full PR Runtime stack CI
- Evidence to preserve: exact branch head, CI run, changed-file list, review packet.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: repository Python runtime.
- Ordered procedure: validate frozen protocol → validate externally produced result schema → evaluate provenance eligibility → score required properties → aggregate without weighted score.
- Failure branches: malformed result fails closed; unknown/missing evidence remains incomplete; synthetic Layer 3 fails.
- Rollback / recovery: revert isolated stacked PR; no migration or external mutation exists.
- Security / privacy controls: only evidence references/counts are retained in reports; no private chain-of-thought or raw private prompt/file content is required.
- External side effects: none.
- Effort limit: result adapter/scorer only; no scenario runner or production sampler.
- Approved reference: PR #40 frozen protocol.

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

- `VERIFIED` provenance is a scorer input contract; later adapters must earn that state from canonical/accepted evidence rather than setting it from prose.
- The scorer does not treat good cost/runtime/activity measurements as success evidence.
- Completion of the benchmark is evidence only and still cannot self-authorize a production change.

## Completion / handoff

- Completed: result validator/scorer and adversarial tests implemented on isolated stack.
- Not completed: actual Layer 2 execution, Layer 3 production sampling, independent review.
- Current blocker: none for implementation; review/execution intentionally deferred.
- Next action if not DONE: open stacked draft PR, run full CI, preserve exact-state handoff.
