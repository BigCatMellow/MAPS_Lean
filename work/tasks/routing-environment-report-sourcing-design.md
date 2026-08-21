# Task: Routing environment-report sourcing design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `ARCHITECTURE`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: define how routing should source task-to-`EnvironmentSpec` evidence,
  compatibility reports, and freshness rules for roadmap 6.24 without
  implementing a cache, inspector, or new task-state schema.

## Inputs and source of truth

- Inputs:
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` row `6.24`.
  - `work/tasks/policy-environment-availability-wave20.md`.
  - `work/tasks/router-environment-report-routing.md`.
  - `runtime/policy/evaluator.py`.
  - `runtime/routing/router.py`, `runtime/routing/service.py`,
    `runtime/routing/cli.py`, `runtime/routing/langgraph_runtime.py`.
  - `runtime/environment/spec.py`, `runtime/environment/fingerprint.py`.
- Authoritative sources: current runtime code wins over older task prose.
- Evidence labels:
  - VERIFIED: `evaluate_assignment()` can reject supplied incompatible reports.
  - VERIFIED: router/service/CLI can forward caller-supplied reports by task ID.
  - VERIFIED: router does not select an `EnvironmentSpec`, compute a
    fingerprint, inspect environment, cache reports, or validate freshness.
  - UNKNOWN: whether any future task should require an `EnvironmentSpec`.
- Dependencies / preconditions: none for this docs/design task.

## Change boundary

- MAY CHANGE:
  - `work/notes/2026-08-21-routing-environment-report-sourcing-design.md`
  - this task file
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` row `6.24` evidence text only
- MUST NOT CHANGE:
  - `runtime/*.py`
  - `tests/*.py`
  - task-state schema or task contract template
  - compatibility semantics for `DRIFTED`, `UNKNOWN`, or missing reports
- MAY CHANGE IF NECESSARY: none.
- OPERATOR APPROVAL REQUIRED: none for design; any future schema migration,
  background inspector, or mandatory route-blocking rule requires its own task.

## Decision authority

- Owner may decide:
  - a proposed explicit evidence contract for future implementation;
  - freshness semantics for a future caller-supplied report envelope;
  - what remains deliberately out of scope.
- Owner must escalate:
  - changing routing behavior now;
  - making missing/unknown environment evidence block assignment;
  - choosing an implicit default `EnvironmentSpec` for all tasks;
  - adding persistent cache/state, migrations, or background inspection.

## Acceptance criteria

- [x] Design note states the current 6.24 gap using verified code paths.
- [x] Design note selects explicit task-contract evidence as the future source
      of task-to-`EnvironmentSpec` association, not repository-wide inference.
- [x] Design note defines report freshness rules for the future implementation.
- [x] Design note preserves current missing-report / `DRIFTED` / `UNKNOWN`
      routing behavior.
- [x] Design note leaves a bounded implementation follow-up with acceptance
      criteria.
- [x] No runtime or test file changes.

## Verification and evidence

- Verification:
  - `git diff --check`
  - direct read of changed docs
- Evidence to preserve: task doc, design note, and checklist evidence.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: repository docs only.
- Ordered procedure: inspect current code, write design, verify diff.
- Failure branches: if code already sources/freshness-validates reports, revise
  finding rather than preserving stale gap language.
- Rollback / recovery: revert docs-only commit.
- Security / privacy controls: do not introduce automatic environment
  inspection or secret probing.
- External side effects: GitHub PR publication/merge only after review.
- Effort limit: no code implementation in this task.
- Approved reference: current 6.24 checklist row.

## Stop / escalate

Stop rather than guess if:

- source/freshness choices require changing task schema or routing behavior now;
- an implementation would inspect local secrets or network availability;
- missing evidence would become a policy gate.

Escalate to: operator or a new implementation task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- The future implementation should add an explicit evidence envelope around
  caller-supplied reports; the router should remain a pure consumer.

## Completion / handoff

- Completed: design note and implementation-ready follow-up.
- Not completed: runtime implementation, cache, inspector, schema migration, or
  mandatory environment gating.
- Current blocker: independent review.
- Next action if not DONE: review this architecture task.
