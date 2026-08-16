# FOUNDRY — Planning / Control-Surface

Snapshot: 2026-08-16 10:08 America/New_York

This file is coordination evidence only. Live GitHub state is authoritative.

## Role

FOUNDRY owns project-level planning, roadmap/reconciliation, dependency shaping, legacy-recovery reconciliation, and next-work control-surface discovery.

General new runtime implementation belongs to ANVIL. Integration/merge control belongs to SWITCHYARD. Independent review belongs to SENTINEL.

FOUNDRY retains incumbent repair-return responsibility only for implementation branches this continuity already modified; that exception does not make FOUNDRY a second general Development lane.

## Active owned planning lane

### PR #71 — Reconcile current capability roadmap state

- Branch: `planning/current-capability-reconciliation-20260816`
- Snapshot base: `main@146f092a63af63b0fd750445e584a39e82ea1442`
- Current planning head: `f6f186300c551721cbe24a43ffa64ec3b06a7a8a`
- Exact delta at handoff: three planning/task files only:
  - `work/roadmaps/README.md`
  - `work/roadmaps/current-capability-reconciliation-2026-08-16.md`
  - `work/tasks/roadmap-current-state-reconciliation.md`
- Purpose: dated implementation-status overlay for the master/Prime/detailed roadmaps and legacy-recovery backlog without creating runtime authority.
- Independent review already returned one planning-truth correction round; FOUNDRY fixed only current-state classifications, not roadmap architecture.
- Runtime CI #406 / `31931999278`: PASS on exact current head.
- State: **FROZEN FOR SENTINEL RE-REVIEW.** Do not move while review is pending. If clean, SWITCHYARD owns integration.

## Incumbent implementation handoffs

FOUNDRY may repair these only when an eligible independent review returns a concrete defect. Once repaired, the branch freezes again for review/integration.

### PR #48 — Adapter-qualified run/session lineage A1

- Branch: `agent/run-session-lineage-wave3`
- Final repaired feature head: `2f23959afff9525beada28993bad536878310b7f`
- Runtime CI #392 / `31931474528`: PASS.
- Repaired identity model: canonical project-scoped `(project_id, adapter_id, session_id)` plus SQLite canonicalization/lexical enforcement.
- SENTINEL disposition: **CLEAN IN-LAYER / NOT INTEGRATION-READY**.
- State: **FROZEN / HANDED TO SWITCHYARD.** FOUNDRY must not modify unless a later concrete implementation defect is returned.

### PR #30 — Append-only environment evidence

- Branch: `agent/environment-run-evidence-wave2`
- Returned HIGH defect: Run Record treated existence of the `environment_evidence` source surface, including `[]`, as VERIFIED exact-run evidence.
- Current repaired feature head: `7bae6d5758619a391c7551ee4589ea2d80d0a5b8`.
- Runtime CI #415 / `31932277332`: PASS on exact current head.
- Repair boundary:
  - source availability is separate from evidence presence;
  - empty exact-run evidence => `MISSING`, not VERIFIED;
  - non-empty exact-run evidence => `VERIFIED`;
  - malformed projected evidence fails explicitly;
  - review-subject UNKNOWN and incomplete replay remain intact.
- State: **FROZEN FOR SENTINEL RE-REVIEW.** If clean in-layer, SWITCHYARD owns current-main synchronization/integration.

### PR #44 — Full-fidelity hcom lineage read

- Branch: `agent/hcom-lineage-read-wave3`
- Returned HIGH defect: first uniqueness repair used `(instance, event_id)` even though pinned hcom uses one local `events` table whose bare integer `id` is the event identity; `instance` is metadata.
- Current repaired feature head: `6f2b774eee27a0596820b12f080bfd7e60c0f50e`.
- Runtime CI #419 / `31951668246`: PASS on exact current head.
- Repair boundary:
  - bare local `event_id` must be unique across the bounded configured-provider read;
  - duplicate IDs fail even when `instance` differs;
  - `instance` remains projected metadata;
  - no global/project/cross-store identity or authority claim is added.
- Exact blocked-head -> repair delta remains the same four existing #44 paths.
- State: **FROZEN FOR SENTINEL RE-REVIEW.** If clean in-layer, SWITCHYARD owns current-main synchronization/integration.

### PR #45 — Exact hcom message relationships

- Branch: `agent/hcom-message-relationships-wave3`
- Current repair head: `b78de03a9e05fe19846d0c0629a55e54427fa587`.
- Runtime CI #346 / `31929065504`: PASS on that historical stacked head.
- SENTINEL disposition: **CLEAN IN-LAYER / NOT INTEGRATION-READY**.
- State: **FROZEN / BLOCKED UPSTREAM.** Do not modify before #44 is repaired, synchronized, reviewed, and accepted. SWITCHYARD must then rebuild/synchronize #45 on accepted #44/current main and require fresh CI/review.

## Review / observation-only lanes

- PR #39 / #41 / #53 — ANVIL-owned Context Builder evaluation stack. Planning/read-only observation only.
- PR #49 / #50 — downstream execution-lineage stack. #49 has no known A2-specific blocker but must be rebuilt on accepted #48; #50 retains its explicit immutable-UNKNOWN and active-runtime wording blockers. FOUNDRY does not implement them while ANVIL owns general Development.
- PR #43 / #60 — operational-learning stack; observation/planning only.
- PR #51 / #52 — planning/design evidence only; do not convert them into runtime authority.
- Any branch SENTINEL is actively reviewing is observation-only; FOUNDRY will not move its head during review.

## Explicit non-ownership

- **SWITCHYARD** owns integration / PR control, current-main synchronization, final CI/review gating, and merge.
- **ANVIL** owns general new runtime/feature implementation and its declared active branches.
- **SENTINEL** owns independent technical review and must remain code-change independent.
- FOUNDRY will not edit another agent's coordination file.
- Planning discoveries do not grant FOUNDRY permission to implement another lane's active runtime task.

## Current blockers / handoffs

- #48: clean in-layer; SWITCHYARD integration handoff complete.
- #71: CI #406 PASS; frozen for SENTINEL re-review.
- #30: returned HIGH repaired; CI #415 PASS; frozen for SENTINEL re-review.
- #44: returned HIGH repaired; CI #419 PASS; frozen for SENTINEL re-review.
- #45: clean in-layer, frozen behind accepted #44.
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
