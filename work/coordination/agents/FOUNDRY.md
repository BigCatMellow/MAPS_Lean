# FOUNDRY — Development / Runtime Implementation

Snapshot: 2026-08-16 01:55 America/New_York

This file is coordination evidence only. Live GitHub state is authoritative.

## Role

FOUNDRY owns narrowly scoped feature/runtime implementation and implementation-defect repair. It owns its declared feature branches/output paths, writes focused tests, and stops at the integration boundary. FOUNDRY does not routinely merge its own feature work and cannot provide the required independent review for work it implemented, repaired, or synchronized.

## Active owned lanes

### PR #30 — Bind append-only environment evidence to runs

- Branch: `agent/environment-run-evidence-wave2`
- Current feature head at snapshot: `1a4016c424e188e06560c9af125e97be774ac269`
- Purpose: append-only EnvironmentSpec/fingerprint/compatibility evidence bound to immutable runs without creating execution/recovery authority.
- Modified feature/integration paths: `runtime/state/environment.py`, `runtime/state/schema.sql`, `runtime/state/store.py`, `tests/test_run_environment_evidence.py`, `tests/test_run_record.py`, `work/tasks/environment-run-evidence-wave2.md`.
- State: implementation/repair complete. Runtime CI #358 / `31929911245` passed on exact head `1a4016c4...`. Current `main` subsequently advanced to `cf05e2549120f7607271c98b6fab039bb35443ed` through coordination-only PR #63, so the prior synchronized head is no longer final integration evidence.
- Next action: freeze this feature branch unless an independent review returns a concrete implementation blocker. SWITCHYARD should perform any required current-main synchronization, exact-delta verification, fresh exact-head CI/review gating, and merge.

### PR #44 — Add full-fidelity hcom lineage read path

- Branch: `agent/hcom-lineage-read-wave3`
- Current head at snapshot: `4a11203f1faf0f8b5d199d6af2643ab7b7205764`
- Purpose: body-free, bounded full-message hcom lineage evidence with mechanically checked provider-local `(instance, event_id)` uniqueness.
- Modified paths: `runtime/communication/hcom_lineage.py`, `tests/test_hcom_lineage.py`, `work/tasks/hcom-lineage-read-wave3.md`, `work/notes/2026-08-15-hcom-lineage-read.md`.
- State: implementation repair complete; Runtime CI #343 / `31928993044` passed on the repaired historical head. Branch is intentionally not treated as integrated with current main.
- Next action: freeze implementation. Hand to SWITCHYARD for genuine synchronization to then-current main, fresh exact-head CI, independent review, and integration.

### PR #45 — Add exact hcom message relationship projection

- Branch: `agent/hcom-message-relationships-wave3`
- Current head at snapshot: `b78de03a9e05fe19846d0c0629a55e54427fa587`
- Purpose: derive exact body-free delivery/reply/thread/request/ack relationships while respecting PR #44 `field_presence` evidence and preserving bounded UNKNOWN semantics.
- Modified paths: `runtime/communication/message_lineage.py`, `tests/test_message_lineage.py`, `work/tasks/hcom-message-relationships-wave3.md`, `work/notes/2026-08-15-hcom-message-relationships.md`.
- State: implementation repair complete; Runtime CI #346 / `31929065504` passed. It remains stacked on historical pre-repair #44 ancestry and must not merge before #44 is accepted.
- Next action: freeze implementation. After #44 is accepted, SWITCHYARD should rebuild/synchronize #45 on accepted #44/main, then require fresh CI and independent exact-head review.

## Review / observation-only lanes

- PR #39 — Context Builder v2 evidence-integrity eval foundation: observation only. Known blocker remains that `CBI-010` incorrectly credits `CB-SRC-007` as an answer-sufficient acceptable substitute for authorization status. FOUNDRY has not modified this branch and will not claim it without re-reading all coordination files and live ownership.
- PR #41 / #53 — downstream Context Builder evaluation stack: observation only; do not modify while ownership is unresolved.
- PR #48 / #49 / #50 — execution-lineage stack: observation only; do not modify without explicit handoff and live ownership check.

## Explicit non-ownership

- SWITCHYARD owns integration / PR control. FOUNDRY will not edit `work/coordination/agents/SWITCHYARD.md`, take over PR #57 integration, merge its own feature heads, or invalidate SWITCHYARD's exact-head integration work.
- PR #43 / #60 operational-learning stack is not owned here.
- PR #51 / #52 planning/design lanes are not owned here.
- Any branch claimed in another agent's coordination file after this snapshot is non-owned until an explicit handoff is verified against live GitHub.

## Current blockers / handoffs

- PR #30 implementation is complete and exact-head CI #358 passed, but `main` moved afterward. **FOUNDRY requests SWITCHYARD perform the final current-main integration synchronization and gating.** FOUNDRY must not modify #30 while SWITCHYARD is synchronizing it.
- PR #44 repair is complete and ready for SWITCHYARD integration sequencing when appropriate. It still needs current-main synchronization, fresh exact-head CI, and independent review.
- PR #45 repair is complete but waits for accepted #44 before integration.
- FOUNDRY is not eligible to provide the required independent review for #30, #44, or #45 because this continuity implemented/repaired them. Those reviews belong to the independent REVIEW lane.

## Concurrency rule

Before modifying any branch FOUNDRY will:

1. re-read live `main`;
2. re-read `work/coordination/agents/*.md` and the exact target PR/base/head;
3. stop writing if the target head moved unexpectedly or another owner has claimed it;
4. never force-push or overwrite another agent;
5. never treat old CI/review as valid for a changed head/base;
6. stop at the integration boundary and hand completed implementation to SWITCHYARD.
