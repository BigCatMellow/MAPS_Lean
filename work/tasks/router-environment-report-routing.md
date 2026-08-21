# Task: route only explicitly supplied environment compatibility reports

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/router-environment-report-routing`
- Risk: `MEDIUM`
- Goal: deterministic routing can use a caller-supplied compatibility report
  for each task and gate only reports proven `INCOMPATIBLE`, without probing or
  deciding how live environment evidence is sourced.

## Inputs and source of truth

- Inputs: `runtime/policy/evaluator.py`, `runtime/routing/router.py`,
  `runtime/routing/langgraph_runtime.py`, `runtime/routing/service.py`,
  `runtime/environment/fingerprint.py`, `tests/test_routing_policy.py`, and
  `work/roadmaps/CAPABILITY_CHECKLIST.md`.
- Authoritative sources: the routing and evaluator behavior in those files;
  `playbook/AGI_STANDARD.md`; repository `AGENTS.md`.
- Evidence labels: `VERIFIED` — `evaluate_assignment` rejects only a supplied
  `CompatibilityState.INCOMPATIBLE`; `UNKNOWN` — no approved live source,
  freshness rule, or task-to-`EnvironmentSpec` mapping exists.
- Dependencies / preconditions: wave20 evaluator support is present; callers
  supply reports deliberately, keyed by task ID.

## Change boundary

- MAY CHANGE: this task file; `runtime/routing/router.py`;
  `runtime/routing/langgraph_runtime.py`; `runtime/routing/service.py`;
  `tests/test_routing_policy.py`; narrowly related LangGraph routing tests if
  serialization is added; `work/roadmaps/CAPABILITY_CHECKLIST.md`.
- MUST NOT CHANGE: `runtime/environment/` fingerprint or `EnvironmentSpec`
  semantics; environment probing; task-state writes; LangGraph checkpoint
  identity/storage semantics; CLI evidence sourcing; treatment of
  `DRIFTED`/`UNKNOWN` as rejection; any live report cache/freshness policy.
- MAY CHANGE IF NECESSARY: public routing function signatures only to accept
  an explicit report mapping; any additional path requires task amendment.
- OPERATOR APPROVAL REQUIRED: selecting a live evidence source, persisting or
  probing reports, changing compatibility semantics, or making task state
  mutations.

## Decision authority

- Owner may decide: the smallest typed representation and deterministic
  serialization/deserialization needed to carry an explicit per-task report
  through routing; whether the absence of a report preserves existing behavior.
- Owner must escalate: source/freshness/fingerprinting policy, a new
  `EnvironmentSpec` association model, any change to environment safety or
  routing/state semantics outside this boundary.

## Acceptance criteria

- [x] `recommend_route` accepts an optional, explicit task-ID-to-report mapping
  and passes only the matching report to `evaluate_assignment`.
- [x] A proven incompatible report prevents assignment for that task and
  exposes an environment gate; a compatible report routes normally; no report,
  `DRIFTED`, and `UNKNOWN` preserve prior assignment behavior.
- [x] The checkpointed route path carries only serializable
  caller-supplied values and neither probes nor writes task truth. Otherwise,
  that path is explicitly deferred and documented.
- [x] The 6.24 checklist remains `IN PROGRESS` and accurately distinguishes
  explicit-router wiring from missing report sourcing and remaining scope proof.

## Verification and evidence

- Verification: `git diff --check`; `python3 -m unittest tests.test_routing_policy -v`;
  focused LangGraph routing tests if that module is changed.
- Evidence to preserve: commit SHA and passing command output in the PR/review.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: no local environment inspection or external side effects.
- Ordered procedure: write this contract; implement deterministic data plumbing;
  add focused regression tests; run verification; commit only after pass.
- Failure branches: if a safe serializable representation cannot be bounded,
  leave checkpointed/service plumbing unchanged and record that residual gap.
- Rollback / recovery: revert this task's single commit; no durable state is
  created or mutated.
- Security / privacy controls: do not serialize secrets, environment snapshots,
  or probe output; reports are only caller-supplied compatibility metadata.
- External side effects: none; do not push or publish.
- Effort limit: stop and escalate rather than adding sourcing, cache, or spec
  association infrastructure.
- Approved reference: `runtime/policy/evaluator.py` wave20 behavior.

## Stop / escalate

Stop rather than guess if report identity, task-to-spec association, freshness,
or persistence is required to meet the acceptance criteria; these are outside
the explicit-input contract. Escalate to the operator or a separately shaped
environment-evidence task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- The mapping is an evidence injection boundary, not a source-of-truth or a
  compatibility evaluator. Missing entries deliberately preserve legacy routing.
- Explicit `INCOMPATIBLE` evidence gates after existing halt and operator
  approval checks but before worker selection, so an empty or unavailable-only
  worker pool cannot conceal a proven incompatibility.

## Completion / handoff

- Completed: focused implementation and owner verification; independent review remains.
- Not completed: a production source, task-to-`EnvironmentSpec` association,
  freshness rule/cache, and CLI input remain explicitly out of scope.
- Current blocker: none.
- Next action if not DONE: independent review of the bounded routing change.
