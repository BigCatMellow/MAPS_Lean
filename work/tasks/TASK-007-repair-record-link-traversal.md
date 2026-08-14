# Task: Repair-record link traversal

- Status: `DONE`
- Owner: `lean-repair-route-helper`
- Risk: `LOW`
- Type: `research / process evaluation`
- Goal: Verify that a first-time agent can reach and correctly apply the active
  repair-record template from the incident-triage route without a directory
  search or legacy access.
- Allowed output paths:
  - `work/reviews/TASK-007-repair-record-link-report.md`
  - `work/reviews/TASK-007-independent-review.md`
  - `work/handoffs/TASK-007-repair-record-link-handoff.md`
- Do not change:
  - `legacy/`, runtime state, databases, active guidance, or Obsidian settings

## Scenario

An active task's canonical record is verified as `IN_PROGRESS` with an expired
lease, while a stale export still says the prior owner is active. The recovery
is mechanical: no ownership, policy, schema, review-separation, or approved
behavior will change. The coordinator needs the correct durable repair record
before using the authorized lifecycle recovery path.

## Acceptance criteria

- [x] Starting from Lean root, the helper follows active Markdown links to
  Repair and Learning and reaches the repair-record template without search.
- [x] The report names the correct repair severity, evidence, permitted action,
  verification, rollback, and prevention fields for this scenario.
- [x] The report explains why this is mechanical and where the boundary would
  become structural.
- [x] The helper sends at most four live `question/assumption → next step`
  updates, creates only the allowed report/handoff, and uses no legacy/runtime
  access.

## Verification

- Coordinator monitors the route and output scope.
- Independent reviewer confirms the template is reached through links and the
  authority boundary is correct.

## Review result

The focused traversal passed after the active Repair and Learning page gained
its direct template link. The review also found a simulation-instrumentation
gap: “at most four” updates permits zero. Future simulation tasks that need
observability should require a bounded minimum (for example, two to four).
