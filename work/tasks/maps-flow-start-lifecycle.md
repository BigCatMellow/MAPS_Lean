# Task: maps flow start lifecycle

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: add the first deterministic `maps flow` lifecycle operation: a
  guarded `flow start` CLI path that composes existing task claim, context
  planning, and run-manifest binding without launching or guessing an
  external provider session.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `playbook/PROGRAM_STEERING.md`,
  `work/roadmaps/CAPABILITY_CHECKLIST.md` item 6.21,
  `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` section 6.21,
  `work/roadmaps/prime-agent-capability-roadmap.md` Phase 4,
  `runtime/cli.py`, `runtime/state/execution.py`,
  `runtime/state/integrity.py`, and current CLI/state tests.
- Authoritative sources: roadmap 6.21 and Prime Phase 4 govern flow scope;
  existing `TaskStore` methods govern lifecycle mutation semantics.
- Evidence labels: `VERIFIED` for existing CLI/state APIs and roadmap text;
  `UNKNOWN` for provider session launch/attach, worker selection, and
  external harness routing.
- Dependencies / preconditions: task lifecycle, context builder, and run
  manifest APIs already exist.

## Change boundary

- MAY CHANGE: `runtime/cli.py`, `runtime/flow_start.py` or equivalent small
  composition module, tests for the new flow, this task file, and checklist
  status/evidence text for 6.21.
- MUST NOT CHANGE: database schema, existing `TaskStore` lifecycle semantics,
  harness adapter behavior, external provider/session launch behavior,
  unrelated roadmap items, and GitHub branch protection.
- MAY CHANGE IF NECESSARY: narrow CLI argument names for the first flow.
- OPERATOR APPROVAL REQUIRED: launching external sessions, adding a second
  workflow engine/state machine, broad lifecycle redesign, or destructive/
  external side effects.

## Decision authority

- Owner may decide: CLI shape, JSON result fields, sequencing, and tests for a
  minimal `flow start` that composes existing guarded operations.
- Owner must escalate: provider/session launch, worker auto-selection beyond
  an explicit `--worker-id`, new durable state types, or expansion to
  additional flows.

## Acceptance criteria

- [ ] `maps flow start <task_id> --worker-id <id>` exists and performs a
  deterministic sequence over existing APIs.
- [ ] The flow refuses to guess: caller must provide worker identity, repo
  root, and any context paths; provider/session launch is explicitly not
  performed.
- [ ] If claim/context/run binding fails, the command returns the failing step
  and does not continue to later steps.
- [ ] On success, output includes claim result, context-plan coverage, and
  exact run manifest/run id.
- [ ] Item 6.21 is updated from `NOT STARTED` to `IN PROGRESS` with evidence
  that this is the first flow only.

## Verification and evidence

- Verification: `git diff --check`; targeted unit tests for `flow start`;
  targeted CLI smoke for success and at least one fail-closed path.
- Evidence to preserve: this task, checklist row update, test output, and
  independent-review evidence.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: local MAPS_Lean worktree only.
- Ordered procedure: add composition code; expose CLI; test success and
  fail-closed behavior; update checklist.
- Failure branches: if an existing API cannot prove a step, return a
  structured failure and stop.
- Rollback / recovery: revert the implementation commit.
- Security / privacy controls: do not read arbitrary context outside declared
  scopes; do not launch, attach, send, or stop provider sessions.
- External side effects: GitHub PR publication only.
- Effort limit: one first flow; no general flow engine or other flow verbs.
- Approved reference: roadmap 6.21 and Prime Phase 4 `flow start` candidate.

## Stop / escalate

Stop rather than guess if:

- a flow step would require selecting a worker automatically;
- provider session launch/attach is needed to satisfy the design;
- database schema or lifecycle semantics need broad changes; or
- tests reveal existing guarded APIs do not support deterministic composition.

Escalate to: operator for scope/authority expansion; a separate task for
session launch/attach or additional flow verbs.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`
