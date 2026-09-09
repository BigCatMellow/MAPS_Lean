# Task: competitor-derived external-effect idempotency audit

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `RESEARCH / DESIGN AUDIT`
- Owner: orchestration operator
- Risk: `MEDIUM`

## Goal

Audit whether MAPS_L's existing harness operation identity and retry semantics are sufficient to prevent duplicate or ambiguous consequential external effects after transport/provider uncertainty, using the pinned competitor/failure corpus as evidence rather than as design authority.

## Inputs / source of truth

- `AGENTS.md`
- `runtime/harness/types.py`
- `runtime/harness/protocol.py`
- `runtime/harness/service.py`
- `runtime/harness/adapters/hcom.py`
- `runtime/recovery/supervisor.py`
- `tests/test_harness_types.py`
- `work/roadmaps/CAPABILITY_CHECKLIST.md` items H1/H2, 6.3, 6.4
- predecessor process: PR #326 / `work/notes/2026-09-09-competitor-borrow-integration-log.md`
- deep upstream evidence: `BigCatMellow/Pilot_Projects@f6d584465e15b0fcf3cd09fea9e056bc23852e94`, especially durable-work/idempotency and event/reconciliation packets.

## Change boundary

MAY CHANGE:
- this task record;
- one bounded audit note under `work/notes/`;
- PR metadata describing findings.

MUST NOT CHANGE in this task:
- harness protocol signatures;
- runtime retry/fallback behavior;
- SQLite schema;
- task authority or capability status;
- active PR #319–#326 owned files;
- provider integration or paid execution.

A runtime/protocol fix is a separate task because it would define operation identity, persistence, retry, effect-receipt, and reconciliation semantics.

## Acceptance criteria

- [ ] Determine whether `operation_id` is intent identity established before dispatch or result/correlation identity established at/after result creation.
- [ ] Determine whether adapters receive/reuse a stable operation identity across retries.
- [ ] Determine whether `RetryDisposition` reaches the retry/recovery decision point.
- [ ] Identify any path where an ambiguous failed harness attempt can be followed by another side-effecting attempt without reconciliation.
- [ ] Distinguish current guarantees from candidate future invariants; do not overclaim exactly-once execution.
- [ ] Route a real gap to the existing harness/recovery owner rather than creating a parallel architecture.

## Verification / review

Evidence is source-level audit plus existing tests. No runtime behavior is changed. Independent review should challenge source interpretation and whether the proposed next proof is smaller than a protocol redesign.

## Stop / escalate

Stop before implementation if satisfying the stronger invariant requires any of:

- a durable operation ledger;
- adapter API changes;
- provider idempotency-key plumbing;
- new retry/fallback policy;
- external-effect reconciliation/receipt semantics;
- schema changes.

Those are design decisions, not research-note edits.
