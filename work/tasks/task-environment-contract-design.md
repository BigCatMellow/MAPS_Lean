# Task: Task environment contract design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `ARCHITECTURE`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: design the additive task-contract storage surface for explicit
  `EnvironmentSpec` routing requirements so future 6.24 work can associate a
  task with environment evidence without guessing or changing routing behavior.

## Inputs and source of truth

- Inputs:
  - `work/notes/2026-08-21-routing-environment-report-sourcing-design.md`.
  - `work/tasks/routing-environment-report-envelope.md`.
  - `runtime/state/base.py`, `runtime/state/policy.py`,
    `runtime/state/integrity.py`, `runtime/state/readiness.py`,
    `runtime/state/schema.sql`.
  - `runtime/routing/environment_reports.py`.
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` row `6.24`.
- Authoritative sources: current state-store code and merged 6.24 design.
- Evidence labels:
  - VERIFIED: task contracts are normalized across task/list/policy tables.
  - VERIFIED: task revision currently includes scalar/list contract fields and
    policy flags, but no environment contract.
  - VERIFIED: BaseStore currently calls one optional shaping hook used by
    `PolicyStateMixin`; adding another contract domain needs an explicit
    extension pattern.
- Dependencies / preconditions: PR #151 is merged.

## Change boundary

- MAY CHANGE:
  - `work/notes/2026-08-21-task-environment-contract-design.md`
  - this task file
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` row `6.24` evidence text only
- MUST NOT CHANGE:
  - `runtime/*.py`
  - `tests/*.py`
  - SQLite schema
  - routing behavior
- MAY CHANGE IF NECESSARY: none.
- OPERATOR APPROVAL REQUIRED: none for this design; future schema/runtime work
  requires its own implementation task and independent review.

## Decision authority

- Owner may decide:
  - the proposed task environment contract fields;
  - where they should be stored;
  - how they should participate in task revision and readiness.
- Owner must escalate:
  - adding schema/runtime code in this task;
  - making environment evidence mandatory by default;
  - adding live inspection, cache, or external environment probing.

## Acceptance criteria

- [x] Design note states the current state-store constraint with source paths.
- [x] Design note proposes explicit task environment contract fields.
- [x] Design note defines storage/read/write/task-revision/readiness behavior.
- [x] Design note preserves current routing behavior and no-default-block rule.
- [x] Design note leaves a bounded implementation follow-up with acceptance
      criteria.
- [x] No runtime or test files change.

## Verification and evidence

- Verification:
  - `git diff --check`
  - direct read of changed docs
- Evidence to preserve: design note, task doc, checklist update.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: repository docs only.
- Ordered procedure: inspect state-store extension points, write design, verify.
- Failure branches: if code already has an environment contract store, update
  finding instead of preserving stale gap language.
- Rollback / recovery: revert docs-only commit.
- Security / privacy controls: do not introduce secret probing or environment
  inspection.
- External side effects: GitHub PR publication/merge only after review.
- Effort limit: no implementation in this task.
- Approved reference:
  `work/notes/2026-08-21-routing-environment-report-sourcing-design.md`.

## Stop / escalate

Stop rather than guess if:

- task environment fields would require changing routing behavior now;
- schema migration strategy is unclear;
- environment reports would become required by default.

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

- This is a design-only bridge from explicit report envelopes to task-contract
  environment requirements.

## Completion / handoff

- Completed: design note and implementation-ready follow-up.
- Not completed: schema/runtime implementation.
- Current blocker: independent review.
- Next action if not DONE: review this architecture task.
