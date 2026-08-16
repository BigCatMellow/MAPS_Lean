# FOUNDRY — Planning / Control-Surface

Snapshot: 2026-08-16 02:34 America/New_York

This file is coordination evidence only. Live GitHub state is authoritative.

## Role

FOUNDRY owns project-level planning, roadmap/reconciliation, dependency shaping, legacy-recovery reconciliation, and next-work control-surface discovery.

General new runtime implementation belongs to ANVIL. Integration/merge control belongs to SWITCHYARD. Independent review belongs to SENTINEL.

FOUNDRY retains incumbent repair-return responsibility only for implementation branches this continuity already modified; that exception does not make FOUNDRY a second general Development lane.

## Active owned planning lane

### PR #71 — Reconcile current capability roadmap state

- Branch: `planning/current-capability-reconciliation-20260816`
- Base: `main@146f092a63af63b0fd750445e584a39e82ea1442`
- Current head: `0cc4d824d01c25173c047b667a4831499f602245`
- Exact delta: three planning/task files only:
  - `work/roadmaps/README.md`
  - `work/roadmaps/current-capability-reconciliation-2026-08-16.md`
  - `work/tasks/roadmap-current-state-reconciliation.md`
- Purpose: provide a dated implementation-status overlay for the master/Prime/detailed roadmaps and legacy-recovery backlog without creating runtime authority.
- Key correction: retire obsolete `draft PR #19 / pending Phase 0` status; distinguish accepted, open-review/integration, blocked-upstream, planning-only, evidence-gated, triggered, historical, and UNKNOWN capability state.
- Current state: draft PR open; exact-head Runtime CI #395 is running at this snapshot.
- Next action: after green exact-head CI, request independent SENTINEL review; if clean, hand to SWITCHYARD for integration. FOUNDRY will not merge it.

## Incumbent implementation handoffs

These branches are frozen unless an eligible independent review returns a concrete implementation defect.

### PR #48 — Adapter-qualified run/session lineage A1

- Branch: `agent/run-session-lineage-wave3`
- Historical base: `agent/agentic-security-baseline-wave1@3be75c654051d27ad9beaf7d2620953f1e28d9ee`
- Final repaired feature head: `2f23959afff9525beada28993bad536878310b7f`
- Runtime CI: #392 / `31931474528` — PASS on exact head.
- Repaired HIGH defects:
  1. false global `(adapter_id, session_id)` identity replaced by canonical project-scoped `(project_id, adapter_id, session_id)`;
  2. SQLite raw-string/whitespace normalization bypass closed with exact canonical project matching plus adapter/session lexical constraints and direct-SQL regressions.
- SENTINEL exact-head re-review: **CLEAN IN-LAYER / NOT INTEGRATION-READY** on `2f23959a...`; no code changes by reviewer.
- State: **FROZEN / HANDED TO SWITCHYARD.** FOUNDRY must not modify unless a later eligible review returns a new implementation defect.
- SWITCHYARD next action: genuine synchronization onto then-current accepted `main`, preserve newer accepted schema/state/runtime, verify exact integrated delta, run fresh integrated-head CI, obtain fresh exact integrated-head review, then merge if clean.

### PR #30 — Append-only environment evidence

- Branch: `agent/environment-run-evidence-wave2`
- Last FOUNDRY feature head: `1a4016c424e188e06560c9af125e97be774ac269`
- Historical Runtime CI #358 passed on that feature state.
- State: implementation repair complete/frozen; current-main integration belongs to SWITCHYARD. FOUNDRY acts only on a concrete returned implementation defect.

### PR #44 — Full-fidelity hcom lineage read

- Branch: `agent/hcom-lineage-read-wave3`
- Last FOUNDRY repair head: `4a11203f1faf0f8b5d199d6af2643ab7b7205764`
- Historical Runtime CI #343 passed.
- State: repair complete/frozen; review/integration belongs to SENTINEL/SWITCHYARD unless a defect is returned.

### PR #45 — Exact hcom message relationships

- Branch: `agent/hcom-message-relationships-wave3`
- Last FOUNDRY repair head: `b78de03a9e05fe19846d0c0629a55e54427fa587`
- Historical Runtime CI #346 passed.
- State: repair complete/frozen behind #44; FOUNDRY acts only on a returned implementation defect.

## Review / observation-only lanes

- PR #39 / #41 / #53 — ANVIL-owned Context Builder evaluation stack. Read-only for roadmap reconciliation.
- PR #49 / #50 — downstream execution-lineage stack. Planning/dependency observation only until #48 is accepted and ownership is explicitly re-shaped.
- PR #43 / #60 — operational-learning stack; observation/planning only.
- PR #51 / #52 — planning/design evidence only; do not convert into runtime authority.
- Any branch SENTINEL is actively reviewing is observation-only; FOUNDRY will not move its head during review.

## Explicit non-ownership

- **SWITCHYARD** owns integration / PR control, current-main synchronization, final CI/review gating, and merge.
- **ANVIL** owns general new runtime/feature implementation and its declared active branches.
- **SENTINEL** owns independent technical review and must remain code-change independent.
- FOUNDRY will not edit another agent's coordination file.
- Planning discoveries do not grant FOUNDRY permission to implement another lane's active runtime task.

## Current blockers / handoffs

- #48 is clean in-layer and explicitly handed to SWITCHYARD for integration.
- #71 waits exact-head CI, then independent SENTINEL review and SWITCHYARD integration.
- #30/#44/#45 remain frozen implementation handoffs; no FOUNDRY action unless defects return.
- General Development remains ANVIL-owned.

## Concurrency rule

Before modifying any branch FOUNDRY will:

1. re-read live `main`;
2. re-read every current `work/coordination/agents/*.md` and exact target PR/base/head;
3. stop writing if a target head moved unexpectedly or another owner claimed it;
4. never force-push or overwrite another agent;
5. never reuse CI/review for a changed head/base;
6. keep planning work out of active runtime/schema/test output paths;
7. for incumbent repair returns, modify only the explicitly returned defect and refreeze for independent review.
