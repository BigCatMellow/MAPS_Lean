# Task: Priority observability and operating safeguards

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT`
- Risk: `MEDIUM`
- Goal: Activate the highest-value low-complexity MAPS Lean safeguards now:
  concise/no-guess operating rules, risk-specific review lenses, secret-safer
  durable task events, and a read-only canonical task trace.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `docs/CHECKS_AND_BALANCES.md`,
  `templates/review.md`, `runtime/state/`, `runtime/cli.py`, current unit tests.
- Authoritative sources: current Lean runtime/schema and active repository
  instructions; `migration/FUTURE_IDEAS_BACKLOG.md` is design evidence only.
- Evidence labels: current runtime/schema `VERIFIED`; legacy findings
  `REPORTED/VERIFIED` by the migration audit but not active authority.
- Dependencies / preconditions: existing SQLite task events, reviews,
  submissions, run manifests, and criterion evidence.

## Change boundary

- MAY CHANGE: `AGENTS.md`, `docs/CHECKS_AND_BALANCES.md`,
  `templates/review.md`, `runtime/README.md`, `runtime/cli.py`,
  `runtime/state/store.py`, `runtime/state/observability.py`,
  `tests/test_trace_and_redaction.py`, this task record.
- MUST NOT CHANGE: task lifecycle, policy authority, review independence,
  recovery/routing semantics, hcom state, legacy code.
- MAY CHANGE IF NECESSARY: schema only after a separate task amendment.
- OPERATOR APPROVAL REQUIRED: destructive/external actions; none are required.

## Decision authority

- Owner may decide: minimal implementation details inside the declared files.
- Owner must escalate: new mutable state, new authority, schema/lifecycle
  changes, automatic remediation, or expansion beyond read-only diagnostics and
  event redaction.

## Acceptance criteria

- [x] Active instructions prohibit overcomplication, verbosity, material
  guessing, silent scope expansion, duplicate truth, and needless permanent
  machinery.
- [x] Medium/high review guidance exposes applicable security/privacy/
  destructive/release/authority lenses without requiring extra reviewers by
  default.
- [x] Every `task_events.summary` write through `TaskStore` passes a shared
  best-effort secret-redaction boundary with explicit redaction markers.
- [x] `trace TASK-ID` is read-only, derives from canonical SQLite records,
  omits raw submission evidence, redacts diagnostic free text, and explicitly
  reports missing hcom/external-runtime coverage.
- [x] Unit tests cover redaction, the event write boundary, trace read-only
  behavior/coverage, and the CLI surface.

## Verification and evidence

- Verification: repository CI/unit test workflow plus compile/lint/security
  checks on the PR.
- Evidence to preserve: PR diff and CI results.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: Python 3.12 / SQLite runtime.
- Ordered procedure: preserve canonical evidence → add diagnostic projection →
  expose CLI → test behavior.
- Failure branches: if trace requires a second source of truth or event
  redaction corrupts canonical evidence, stop and redesign.
- Rollback / recovery: revert the implementation commit; no schema migration.
- Security / privacy controls: redaction is best-effort and must leave explicit
  markers; raw submission evidence is omitted from trace v1.
- External side effects: GitHub branch/PR only.
- Effort limit: keep first version inside existing SQLite schema.
- Approved reference: user direction in the current conversation plus preserved
  backlog candidates.

## Stop / escalate

Stop rather than guess if:

- communication correlation would require inferred identities;
- trace completeness cannot be stated accurately;
- a requested safety control requires mutating canonical evidence beyond event
  summaries;
- implementation requires lifecycle/schema/authority expansion.

Escalate to: operator.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Trace v1 intentionally does not ingest hcom/recovery/helper/escalation stores.
  Missing coverage is explicit.
- Review evidence freshness beyond task/context hashes is deferred because a
  correct implementation needs revision/artifact binding rather than a prose
  check.

## Completion / handoff

- Completed: implementation prepared on the active draft PR branch.
- Not completed: independent review/CI.
- Current blocker: none.
- Next action if not DONE: review the PR and run repository CI.
