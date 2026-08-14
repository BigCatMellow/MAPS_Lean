# Task: Promote SQLite + AGI state runtime

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: ChatGPT
- Risk: `HIGH`
- Goal: MAPS Lean has an active SQLite task-state implementation outside `legacy/` and `migration/`; `READY` is reachable only through an enforced structural AGI gate.

## Inputs and source of truth

- Inputs: `playbook/AGI_STANDARD.md`, `playbook/TASK_LIFECYCLE.md`, `docs/CONTROL_PLANE_SETUP.md`, `migration/LEGACY_RUNTIME_EXTRACTION.md`, preserved SQLite schema/claim/review source and focused tests.
- Authoritative sources: active root `AGENTS.md` and active Lean playbooks; migration source is behavioral evidence only.
- Evidence labels: legacy collision/review findings are `VERIFIED` by preserved tests/audits; the Lean implementation is verified by the test suite listed below.
- Dependencies / preconditions: legacy archaeology and runtime extraction snapshots completed in PRs #7 and #8.

## Change boundary

- MAY CHANGE: `runtime/**`, `tests/test_state_store.py`, `templates/task-contract.example.json`, `README.md`, `docs/CONTROL_PLANE_SETUP.md`, `migration/LEGACY_RUNTIME_EXTRACTION.md`, `migration/LEGACY_REMOVAL_CHECKLIST.md`, `state/CURRENT.md`, this task record.
- MUST NOT CHANGE: LangGraph routing, hcom adapter, RnS/recovery, local-helper adapters, `legacy/`, migration snapshot source.
- MAY CHANGE IF NECESSARY: additional state-only tests/docs that expose a defect in this slice.
- OPERATOR APPROVAL REQUIRED: expanding this PR into autonomous dispatch, external writes, or deletion of legacy source.

## Decision authority

- Owner may decide: internal Python/SQLite structure needed to preserve the named state invariants.
- Owner must escalate: changes to product intent, provider routing, external side effects, destructive cleanup, or the target operating model beyond this state slice.

## Acceptance criteria

- [x] Active `runtime/state/` exists and imports nothing from `legacy/` or `migration/`.
- [x] SQLite enables foreign keys, WAL, and a 5-second busy timeout.
- [x] Incomplete AGI contracts cannot transition to `READY`.
- [x] AGI validation and `READY` mutation share one write transaction.
- [x] Concurrent claim attempts have exactly one winner.
- [x] Expired leases can recover without changing accountable owner; live leases cannot be stolen.
- [x] Active output-path conflicts block `READY` promotion.
- [x] Submission evidence/authorship are durable and independent-review self-review is rejected.
- [x] `CHANGES_REQUESTED` work can be reclaimed without changing owner.
- [x] A small JSON CLI exposes semantic state operations with typed failure codes.
- [ ] Independent review confirms the implementation and test evidence.

## Verification and evidence

- Verification: `PYTHONWARNINGS=error::ResourceWarning python -m unittest discover -s tests -v`
- Evidence to preserve: 15 passing unit tests plus CLI init smoke output showing `foreign_keys=1`, `journal_mode=wal`, `busy_timeout=5000`.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: Python 3.10+ with stdlib `sqlite3`; local filesystem for WAL-backed state.
- Ordered procedure: inspect preserved invariants → implement state-only slice → race-test promotion/claims → update active docs → independent review.
- Failure branches: test failure blocks merge; a new cross-subsystem dependency is split into a later task.
- Rollback / recovery: revert this PR; mutable `.maps/state/maps.db` is local/ignored and not migration source.
- Security / privacy controls: no secrets, network calls, or external service writes.
- External side effects: GitHub branch/PR only.
- Effort limit: do not add LangGraph/hcom/RnS to this slice.
- Approved reference: `migration/LEGACY_RUNTIME_EXTRACTION.md` P0 invariants and active AGI standard.

## Stop / escalate

Stop rather than guess if the state slice would require changing operator authority, external behavior, routing policy, or deleting preserved legacy material.

Escalate to: operator for architectural expansion; separate task for later runtime layers.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Structural AGI validation deliberately checks presence/types/dependencies/path conflicts; it does not pretend to judge prose quality.
- Owner and current claimant are separate fields.
- This task remains `READY_FOR_REVIEW` until independent review; local tests are owner verification, not independent approval.

## Completion / handoff

- Completed: implementation and owner-side verification.
- Not completed: independent review and merge.
- Current blocker: required independent review.
- Next action if not DONE: review PR against this task and the P0 invariants, then merge or request changes.
