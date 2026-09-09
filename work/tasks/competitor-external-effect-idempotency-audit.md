# Task: competitor-derived external-effect idempotency audit

- Status: `READY_FOR_REVIEW`
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
- `tests/test_recovery_supervisor.py`
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

- [x] Determine whether `operation_id` is intent identity established before dispatch or result/correlation identity established at/after result creation.
- [x] Determine whether adapters receive/reuse a stable operation identity across retries.
- [x] Determine whether `RetryDisposition` reaches the retry/recovery decision point.
- [x] Identify any path where an ambiguous failed harness attempt can be followed by another side-effecting attempt without reconciliation.
- [x] Distinguish current guarantees from candidate future invariants; do not overclaim exactly-once execution.
- [x] Route a real gap to the existing harness/recovery owner rather than creating a parallel architecture.

## Result

`DESIGN GAP IDENTIFIED`.

`OperationResult` already provides useful correlation/retry-uncertainty vocabulary, but the current adapter/service protocol does not establish a stable logical operation identity before dispatch, and recovery does not retain `operation_id` / `RetryDisposition` when deciding whether to fall back. Existing recovery tests already characterize that non-canonical harness failures/exceptions can immediately fall through to the legacy direct resume path.

Detailed evidence and bounded next proof: `work/notes/2026-09-09-external-effect-idempotency-audit.md`.

## Verification / review

Source evidence inspected directly. Existing tests confirm result-ID behavior and the non-canonical direct-fallback behavior; no duplicate characterization test was added. No runtime behavior changed.

Independent review should challenge source interpretation, especially whether `operation_id` is being under-read elsewhere and whether an existing persistence owner can carry the stronger fact without a new operation ledger.

## Stop / escalate

Implementation remains stopped because satisfying the stronger invariant may require one or more of:

- a durable operation record;
- adapter API changes;
- provider idempotency-key plumbing;
- new retry/fallback policy;
- external-effect reconciliation/receipt semantics;
- schema changes.

Those are design decisions, not research-note edits.
