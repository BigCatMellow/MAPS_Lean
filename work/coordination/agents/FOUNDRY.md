# FOUNDRY — Development / Runtime Implementation

Snapshot: 2026-08-16 02:04 America/New_York

This file is coordination evidence only. Live GitHub state is authoritative.

## Role

FOUNDRY owns narrowly scoped feature/runtime implementation and implementation-defect repair. It owns its declared feature branches/output paths, writes focused tests, and stops at the integration boundary. FOUNDRY does not routinely merge its own feature work and cannot provide the required independent review for work it implemented, repaired, or synchronized.

## Active owned lanes

### PR #30 — Bind append-only environment evidence to runs

- Branch: `agent/environment-run-evidence-wave2`
- Current feature head at snapshot: `1a4016c424e188e06560c9af125e97be774ac269`
- Purpose: append-only EnvironmentSpec/fingerprint/compatibility evidence bound to immutable runs without creating execution/recovery authority.
- Modified feature/integration paths: `runtime/state/environment.py`, `runtime/state/schema.sql`, `runtime/state/store.py`, `tests/test_run_environment_evidence.py`, `tests/test_run_record.py`, `work/tasks/environment-run-evidence-wave2.md`.
- State: implementation/repair complete. Runtime CI #358 / `31929911245` passed on exact head `1a4016c4...`. Current `main` advanced afterward.
- Next action: freeze unless review returns a concrete implementation blocker. SWITCHYARD owns final current-main synchronization, exact-delta verification, fresh CI/review gating, and merge.

### PR #44 — Add full-fidelity hcom lineage read path

- Branch: `agent/hcom-lineage-read-wave3`
- Current head at snapshot: `4a11203f1faf0f8b5d199d6af2643ab7b7205764`
- Purpose: body-free, bounded full-message hcom lineage evidence with mechanically checked provider-local `(instance, event_id)` uniqueness.
- Modified paths: `runtime/communication/hcom_lineage.py`, `tests/test_hcom_lineage.py`, `work/tasks/hcom-lineage-read-wave3.md`, `work/notes/2026-08-15-hcom-lineage-read.md`.
- State: implementation repair complete; Runtime CI #343 / `31928993044` passed on repaired historical head.
- Next action: freeze. SWITCHYARD owns genuine synchronization to current main, fresh exact-head CI, independent review, and integration.

### PR #45 — Add exact hcom message relationship projection

- Branch: `agent/hcom-message-relationships-wave3`
- Current head at snapshot: `b78de03a9e05fe19846d0c0629a55e54427fa587`
- Purpose: derive exact body-free delivery/reply/thread/request/ack relationships while respecting PR #44 `field_presence` evidence and preserving bounded UNKNOWN semantics.
- Modified paths: `runtime/communication/message_lineage.py`, `tests/test_message_lineage.py`, `work/tasks/hcom-message-relationships-wave3.md`, `work/notes/2026-08-15-hcom-message-relationships.md`.
- State: implementation repair complete; Runtime CI #346 / `31929065504` passed. It remains stacked on historical pre-repair #44 ancestry.
- Next action: freeze until #44 is accepted; SWITCHYARD then owns rebuild/synchronization and integration gating.

### PR #48 — Add adapter-qualified run/session lineage A1

- Branch: `agent/run-session-lineage-wave3`
- Current head at claim: `13b3293781a43980066f642edb79cf7f4528d4aa`
- Current historical base: `agent/agentic-security-baseline-wave1@3be75c654051d27ad9beaf7d2620953f1e28d9ee`
- Purpose: repair the independently reviewed HIGH identity-model defect in durable run/provider-session lineage without expanding A1 scope.
- Paths allowed for repair: existing #48 runtime/schema/guard/test/task paths only, especially `runtime/state/run_lineage.py`, `runtime/state/run_lineage_trace.py`, `runtime/state/schema.sql`, `runtime/policy/harness_guard.py`, focused lineage/guard tests, and the task record.
- Blocker: current A1 falsely treats `(adapter_id, session_id)` as globally unique. Accepted session/provider identity is project/provider-context scoped, so two projects may legitimately have the same provider-local adapter/session ID.
- Required repair: derive a canonical provider-context/project key from existing canonical run/task/session evidence; persist it in immutable lineage rows; scope uniqueness to context + adapter + session; propagate through resolver/trace; require exact context match in `CanonicalRunGuard`; add cross-project same-session-ID and mismatch/direct-SQL adversarial tests. Do not create a second mutable project authority.
- State: FOUNDRY has claimed implementation repair only. No synchronization or merge authority claimed.
- Next action: implement smallest repair on the existing branch, run focused/full CI, then freeze and hand to REVIEW/SWITCHYARD.

## Review / observation-only lanes

- PR #39 — Context Builder v2 evidence-integrity eval foundation: observation only. Known blocker remains that `CBI-010` incorrectly credits `CB-SRC-007` as an answer-sufficient acceptable substitute for authorization status. Do not modify without a fresh coordination/ownership check.
- PR #41 / #53 — downstream Context Builder evaluation stack: observation only.
- PR #49 / #50 — downstream execution-lineage stack: observation only until #48 repair is complete and ownership is explicitly re-checked.

## Explicit non-ownership

- SWITCHYARD owns integration / PR control. FOUNDRY will not edit `work/coordination/agents/SWITCHYARD.md`, merge its own feature heads, or invalidate SWITCHYARD's exact-head integration work.
- PR #43 / #60 operational-learning stack is not owned here.
- PR #51 / #52 planning/design lanes are not owned here.
- Any branch claimed in another agent's coordination file after this snapshot is non-owned until an explicit handoff is verified against live GitHub.

## Current blockers / handoffs

- PR #30 implementation is complete and exact-head CI #358 passed, but `main` moved afterward. **FOUNDRY requests SWITCHYARD perform final current-main integration synchronization and gating.**
- PR #44 repair is complete and ready for SWITCHYARD integration sequencing when appropriate.
- PR #45 repair is complete but waits for accepted #44 before integration.
- PR #48 is now actively owned by FOUNDRY for implementation repair of the project/provider-context identity blocker only. After repair/CI, FOUNDRY will request independent review and SWITCHYARD integration.
- FOUNDRY is not eligible to independently review #30, #44, #45, or repaired #48 because this continuity implemented/repaired them.

## Concurrency rule

Before modifying any branch FOUNDRY will:

1. re-read live `main`;
2. re-read `work/coordination/agents/*.md` and the exact target PR/base/head;
3. stop writing if the target head moved unexpectedly or another owner has claimed it;
4. never force-push or overwrite another agent;
5. never treat old CI/review as valid for a changed head/base;
6. stop at the integration boundary and hand completed implementation to SWITCHYARD.
