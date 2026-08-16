# Task: MAPS end-to-end Layer 2 / Layer 3 benchmark protocol

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `RESEARCH`
- Owner: `agent/maps-end-to-end-benchmark-wave3`
- Risk: `MEDIUM`
- Goal: Freeze a provider-neutral benchmark protocol that defines how MAPS will measure controlled agent-quality regressions and real production/outcome behavior without pretending synthetic evidence is production proof.

## Inputs and source of truth

- Inputs:
  - `AGENTS.md`
  - `work/roadmaps/prime-agent-capability-roadmap.md`
  - `work/roadmaps/agent-harness-capabilities/05-learning-and-evaluation.md`
  - merged task/context/trace/outcome behavior on `main`
  - PR #36 reconciliation only as planning evidence
  - PRs #33-#35 only as prospective Run Record/frozen-case/comparative-evaluator interfaces
  - PR #39 only as a parallel example of frozen evaluation discipline, not as a dependency
- Authoritative sources: merged `main` and root `AGENTS.md`; draft PR APIs may inform compatibility planning but are not accepted authority.
- Evidence labels:
  - `VERIFIED`: merged MAPS separates task completion from append-only outcome observations.
  - `VERIFIED`: current roadmaps require separate Layer 1, Layer 2, and Layer 3 evaluation and reject activity metrics as outcome proof.
  - `PLANNING`: future Run Record/frozen-case/comparative evaluator APIs are still draft until independently accepted.
- Dependencies / preconditions: none for freezing this protocol. Executing it against real runs depends on accepted supporting interfaces and real eligible work.

## Change boundary

- MAY CHANGE:
  - `work/tasks/maps-end-to-end-benchmark-wave3.md`
  - `work/notes/2026-08-15-maps-end-to-end-benchmark.md`
  - `work/evals/maps-end-to-end-benchmark-v1.json`
  - `tests/test_maps_end_to_end_benchmark_fixture.py`
- MUST NOT CHANGE:
  - `runtime/**`
  - canonical state/policy/review schemas
  - existing roadmaps/backlogs/audits
  - PR #20-#39 branches
  - provider/model routing or production evaluation policy
  - any real release/deployment/external system
- MAY CHANGE IF NECESSARY: none without task amendment.
- OPERATOR APPROVAL REQUIRED: any actual consequential external/release benchmark execution, production policy change, or automatic promotion behavior.

## Decision authority

- Owner may decide: benchmark scenario structure, observable property IDs, evidence-class rules, synthetic fixture content, and fixture-validation checks.
- Owner must escalate: production sampling policy, external execution targets, cost-bearing model/provider runs, destructive actions, release/deployment behavior, or changes to review/policy authority.

## Acceptance criteria

- [x] Protocol defines Layer 2 and Layer 3 as distinct evidence classes.
- [x] Layer 2 permits frozen/synthetic representative fixtures but requires observable agent behavior when actually executed.
- [x] Layer 3 requires real run/outcome provenance and explicitly rejects synthetic fixtures as production evidence.
- [x] At least one required Layer 3 scenario is genuinely external/operator-visible and includes acquisition/use verification, not only an internal lifecycle round trip.
- [x] Result states include `PASS`, `FAIL`, `UNKNOWN`, and `NOT_RUN`; missing evidence cannot be coerced into PASS.
- [x] Security/authority/review-integrity blocker properties remain visible separately from quality/cost metrics.
- [x] Benchmark does not require private chain-of-thought; scoring uses observable actions, artifacts, structured evidence, review, and outcomes.
- [x] Protocol does not depend on a particular model/provider or draft PR API.
- [x] Benchmark results cannot automatically promote harness/routing/policy/context changes.
- [x] Fixture test validates layer rules, scenario IDs/properties, blocker semantics, external-evidence requirements, and non-automatic promotion.
- [x] Independent review is required before this protocol is treated as frozen experimental authority.

## Verification and evidence

- Verification:
  - `python -m json.tool work/evals/maps-end-to-end-benchmark-v1.json >/dev/null`
  - `python -m unittest tests.test_maps_end_to_end_benchmark_fixture -v`
  - full PR Runtime CI.
- Evidence to preserve: exact base/head, final changed-file list, CI result, and independent review.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: protocol/fixture validation only; no real provider or external target in this task.
- Ordered procedure:
  1. freeze benchmark layers, scenarios, and property truth;
  2. mechanically validate protocol invariants;
  3. independently review the protocol;
  4. after supporting interfaces are accepted, build a separate result adapter/runner;
  5. execute Layer 2 controlled cases;
  6. collect Layer 3 only from eligible real runs/outcomes;
  7. compare candidates only on like-for-like frozen scenarios/evidence classes.
- Failure branches:
  - IF a Layer 3 result lacks real run/outcome provenance THEN mark it invalid/NOT_RUN, never synthetic PASS.
  - IF a required fact is unavailable THEN use `UNKNOWN` rather than infer it from prose/activity.
  - IF a benchmark requires hidden model reasoning THEN reshape it to observable behavior/evidence.
- Rollback / recovery: reject/delete the draft protocol; no runtime state is changed.
- Security / privacy controls: synthetic Layer 2 fixtures only; Layer 3 protocol requires sanitized projections/references rather than raw private prompts/content by default.
- External side effects: Git branch/draft PR only.
- Effort limit: four declared paths; no runner/scorer implementation.
- Approved reference: roadmap Layer 2/Layer 3 evaluation requirements and end-to-end benchmark sequence.

## Stop / escalate

Stop rather than guess if:

- supporting merged behavior materially changes the meaning of a benchmark property;
- a scenario would require actual production/external execution in this task;
- a new durable authority/store would be needed;
- an overlapping benchmark implementation branch appears.

Escalate to: operator for consequential execution; independent reviewer for protocol truth.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task freezes a benchmark **protocol**, not benchmark results.
- Layer 3 is deliberately impossible to complete from this branch because real production/operator-visible evidence must come later from actual eligible work.
- Draft PR #33-#35 formats may later be adapters into this protocol, but the protocol does not freeze their current draft spelling.

## Completion / handoff

- Completed: benchmark protocol, scenario fixture, validation test, and design note prepared on isolated branch.
- Not completed: benchmark execution, result adapter/scorer, Layer 2 model runs, Layer 3 production sampling.
- Current blocker: independent review before treating this as the frozen benchmark protocol.
- Next action if not DONE: independently review scenario sufficiency, blocker properties, and the synthetic-vs-real evidence boundary.
