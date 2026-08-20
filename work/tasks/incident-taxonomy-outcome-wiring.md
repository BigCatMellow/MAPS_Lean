# Task: incident taxonomy outcome wiring

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `incident_taxonomy_owner`
- Risk: `MEDIUM`
- Goal: Outcome records retain their existing free-text `failure_class` and expose a deterministic `incident_class` projection derived with `IncidentClass` / `classify_failure_text`.

## Inputs and source of truth

- Inputs: `AGENTS.md`; `playbook/AGI_STANDARD.md`; `runtime/incident_taxonomy.py`; `runtime/state/outcomes.py`; `runtime/run_record.py`; `runtime/status.py`; affected tests.
- Authoritative sources: `work/roadmaps/CAPABILITY_CHECKLIST.md` row 6.27; existing runtime behavior and tests where compatibility is not contradicted by that row.
- Evidence labels: row 6.27 and the inspected implementation are `VERIFIED`; no new database field or lifecycle change is assumed.
- Dependencies / preconditions: `IncidentClass` and `classify_failure_text` already exist and focused tests are runnable.

## Change boundary

- MAY CHANGE: `work/tasks/incident-taxonomy-outcome-wiring.md`, `runtime/incident_taxonomy.py` documentation only, `runtime/state/outcomes.py`, `runtime/state/observability.py`, `runtime/run_record.py`, `runtime/status.py`, `runtime/cli.py` only if output plumbing needs it, `tests/test_outcomes.py`, `tests/test_incident_taxonomy.py`, `tests/test_run_record.py`, affected status tests, and `work/roadmaps/CAPABILITY_CHECKLIST.md`.
- MUST NOT CHANGE: SQLite schema, outcome append-only semantics, task lifecycle/status mutation, review/authority semantics, CLI command syntax, or free-text storage/acceptance of legacy `failure_class` values.
- MAY CHANGE IF NECESSARY: none; expand this task before adding a migration, a new public command, or unrelated output paths.
- OPERATOR APPROVAL REQUIRED: schema migration, lifecycle or policy gating, compatibility break, external publication, or scope beyond this projection.

## Decision authority

- Owner may decide: the smallest in-memory/output projection location and focused test coverage that meets the stated compatibility boundary.
- Owner must escalate: any need to reject, rewrite, or migrate legacy failure text; any authority/lifecycle change; or a conflict between existing behavior and the stated acceptance criteria.

## Acceptance criteria

- [x] Canonical enum-valued `failure_class` records retain their stored text and expose the same canonical `incident_class` value.
- [x] A noncanonical legacy string is retained as supplied after existing trimming behavior and projects `incident_class: "UNKNOWN"` without rejection.
- [x] A `FAILURE` with blank `failure_class` retains existing `"UNKNOWN"` storage behavior and projects `incident_class: "UNKNOWN"`.
- [x] `get_outcome`, `list_outcomes`, task trace, run record, and existing CLI JSON output remain compatible and include the projection where they expose outcomes.
- [x] No task status, authority, review, or append-only behavior changes.

## Verification and evidence

- Verification: `git diff --check`; `python3 -m unittest tests.test_incident_taxonomy tests.test_outcomes tests.test_run_record -v`; affected status tests if `runtime/status.py` changes.
- Evidence to preserve: committed task contract, focused test output, and commit SHA.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: local Python runtime and temporary SQLite databases used by the named unit tests.
- Ordered procedure: create this AGI-ready task contract; add projection without changing persistence; add assertions; run focused tests; commit only after they pass.
- Failure branches: IF a projection requires a schema change, command-syntax change, or lifecycle behavior change, THEN stop and escalate rather than widen scope.
- Rollback / recovery: revert the single implementation commit; existing database rows remain valid because no schema or stored values change.
- Security / privacy controls: retain existing redaction and do not add free-text content to outputs beyond current fields.
- External side effects: none; do not push or publish.
- Effort limit: stop after one bounded implementation/test pass if an unplanned dependency is required.
- Approved reference: 6.27 explicitly requires consuming the enum while preserving the free-text `failure_class` surface.

## Stop / escalate

Stop rather than guess if:

- the canonical projection cannot be added without changing stored rows, accepting/rejecting legacy values, or changing task lifecycle/authority semantics;
- an exposed output contract needs a non-backward-compatible shape; or
- named focused tests reveal an incompatible expectation outside the boundary.

Escalate to: root task owner/operator.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- `incident_class` is a derived projection, not canonical persisted state. Existing `failure_class` remains the source text.

## Completion / handoff

- Completed: read-only `incident_class` projections added to outcome reads, trace, status attention, and portable Run Records; focused verification passed.
- Not completed: independent review.
- Current blocker: none.
- Next action if not DONE: independent reviewer validates the bounded diff and focused evidence.
