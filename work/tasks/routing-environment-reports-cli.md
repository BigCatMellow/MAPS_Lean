# Task: routing environment reports CLI input

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: add a routing CLI input path for caller-supplied task environment
  compatibility reports so the existing 6.24 environment gate can be exercised
  through normal routing commands.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `work/roadmaps/CAPABILITY_CHECKLIST.md` item 6.24,
  `runtime/routing/cli.py`, `runtime/routing/service.py`,
  `runtime/routing/langgraph_runtime.py`, `runtime/routing/router.py`,
  `runtime/environment/fingerprint.py`, and routing tests.
- Authoritative sources: existing `CompatibilityReport` schema and router
  environment-report behavior govern semantics; 6.24 checklist row governs
  remaining limitations.
- Evidence labels: `VERIFIED` for current router/service support for
  caller-supplied reports; `UNKNOWN` for report freshness, task-to-spec
  association, and production report source.
- Dependencies / preconditions: PR #140 already wired environment report
  gating through router/service/checkpointed routing.

## Change boundary

- MAY CHANGE: `runtime/routing/cli.py`, routing CLI tests, this task file, and
  checklist 6.24 evidence text.
- MUST NOT CHANGE: compatibility evaluation semantics, environment inspection,
  report freshness rules, task-to-EnvironmentSpec association, router
  scheduling priority, database schema, and unrelated roadmap items.
- MAY CHANGE IF NECESSARY: small parsing helper in routing CLI.
- OPERATOR APPROVAL REQUIRED: automatic environment inspection, report cache,
  freshness enforcement, task/spec binding model, or lifecycle mutation.

## Decision authority

- Owner may decide: JSON file shape accepted by the CLI and validation error
  wording.
- Owner must escalate: deriving reports automatically, changing
  `INCOMPATIBLE`/`DRIFTED`/`UNKNOWN` semantics, or broad routing changes.

## Acceptance criteria

- [ ] `runtime.routing.cli route` accepts caller-supplied environment reports
  from JSON.
- [ ] An explicit `INCOMPATIBLE` report supplied through the CLI produces the
  existing `policy_gate/environment_incompatible` route.
- [ ] Malformed reports fail closed with a nonzero CLI exit.
- [ ] The checklist states 6.24 still lacks production source/freshness/cache/
  task-spec association even though CLI input now exists.

## Verification and evidence

- Verification: `git diff --check`; targeted routing CLI tests; routing policy
  and LangGraph routing tests.
- Evidence to preserve: task file, checklist row, test output, and independent
  review evidence.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: local MAPS_Lean worktree only.
- Ordered procedure: add JSON parser; wire CLI arg into `route_project`; test
  success and malformed input; update checklist.
- Failure branches: if JSON cannot be validated into `CompatibilityReport`,
  fail the CLI command rather than ignoring the report.
- Rollback / recovery: revert implementation commit.
- Security / privacy controls: read only explicit JSON file path; do not scan
  environment or infer reports.
- External side effects: GitHub PR publication only.
- Effort limit: CLI input path only.
- Approved reference: existing `CompatibilityReport` and router behavior.

## Stop / escalate

Stop rather than guess if:

- a report source/freshness/task-spec binding must be invented;
- route semantics need to change; or
- environment inspection is required.

Escalate to: operator or separate architecture task for report source,
freshness, cache, or task/spec association.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`
