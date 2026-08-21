# Task: Routing environment-report evidence envelope

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: add a bounded caller-supplied environment-report envelope for routing
  so stale or mismatched reports are omitted before the pure router sees them,
  without adding live inspection, cache/state, schema migration, or mandatory
  missing-report gating.

## Inputs and source of truth

- Inputs:
  - `work/notes/2026-08-21-routing-environment-report-sourcing-design.md`.
  - `runtime/routing/router.py`, `runtime/routing/cli.py`,
    `runtime/routing/langgraph_runtime.py`.
  - `runtime/environment/spec.py`, `runtime/environment/fingerprint.py`.
  - `runtime/state/store.py`.
  - `tests/test_routing_cli.py`, `tests/test_routing_policy.py`,
    `tests/test_langgraph_routing.py`.
- Authoritative sources: current runtime code and the merged 6.24 sourcing
  design.
- Evidence labels:
  - VERIFIED: router already consumes task-keyed `CompatibilityReport` values.
  - VERIFIED: existing direct report mapping behavior is preserved.
  - VERIFIED: task revisions are hashes, so freshness uses exact revision match.
- Dependencies / preconditions: PR #150 design is merged.

## Change boundary

- MAY CHANGE:
  - `runtime/routing/environment_reports.py`
  - `runtime/routing/cli.py`
  - `tests/test_routing_environment_reports.py`
  - `tests/test_routing_cli.py`
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` row `6.24` evidence text only
  - this task file
- MUST NOT CHANGE:
  - `runtime/routing/router.py`
  - `runtime/policy/evaluator.py`
  - `runtime/environment/fingerprint.py`
  - task-state schema or task contract template
  - missing-report / `DRIFTED` / `UNKNOWN` routing behavior
- MAY CHANGE IF NECESSARY: none.
- OPERATOR APPROVAL REQUIRED: none for this bounded explicit-JSON parsing
  implementation.

## Decision authority

- Owner may decide:
  - envelope parser helper names;
  - per-entry diagnostic reason strings;
  - exact revision-match freshness semantics.
- Owner must escalate:
  - live environment inspection;
  - durable report cache/state;
  - schema migration;
  - making missing reports blocking by default;
  - choosing a universal default `EnvironmentSpec`.

## Acceptance criteria

- [x] Fresh explicit envelopes produce task-keyed `CompatibilityReport` values
      for existing router input.
- [x] Spec-hash mismatch, stale age, task-revision mismatch, task/project
      mismatch, and malformed envelopes are omitted rather than converted into
      `INCOMPATIBLE`.
- [x] CLI accepts the new `environment_report_envelopes` wrapper while
      preserving existing direct `environment_reports` / direct mapping support.
- [x] Router remains pure and unchanged.
- [x] No live environment fingerprint is computed by routing.
- [x] Missing/stale/invalid envelope evidence preserves current routing behavior.
- [x] 6.24 remains `IN PROGRESS`.

## Verification and evidence

- Verification:
  - `git diff --check`
  - `python3 -m unittest tests.test_routing_environment_reports tests.test_routing_cli tests.test_routing_policy tests.test_langgraph_routing -v`
- Evidence to preserve: test output and review evidence.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: Python unittest; optional LangGraph dependency may skip
  one integration test.
- Ordered procedure: implement parser/filter, wire CLI read boundary, run
  focused tests, request independent review.
- Failure branches: if a change requires router inspection or task-state schema,
  stop and reshape.
- Rollback / recovery: revert PR.
- Security / privacy controls: no secret probing, no network probing, no live
  environment inspection.
- External side effects: GitHub PR publication/merge only after review.
- Effort limit: no broader 6.24 enforcement in this task.
- Approved reference:
  `work/notes/2026-08-21-routing-environment-report-sourcing-design.md`.

## Stop / escalate

Stop rather than guess if:

- report freshness requires timestamp semantics unavailable from current task
  revisions;
- a missing report would need to become a blocker;
- the implementation would inspect environments or persist report cache state.

Escalate to: operator or a new architecture task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Task revision freshness is an exact hash match.
- Invalid envelope entries produce diagnostics and are omitted from router
  input. Diagnostics are not yet surfaced in CLI output.

## Completion / handoff

- Completed: implementation and focused tests.
- Not completed: task-contract schema, durable cache, live inspector,
  required-for-routing behavior, or broader scope-dimension proof.
- Current blocker: independent review.
- Next action if not DONE: review this implementation.
