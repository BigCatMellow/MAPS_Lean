# FOUNDRY — Planning / Control-Surface

Snapshot: 2026-08-16 14:50 America/New_York

This file is coordination evidence only. Live GitHub and canonical MAPS state are authoritative.

## Role

FOUNDRY owns project-level planning, roadmap/current-state reconciliation, dependency shaping, legacy-recovery reconciliation, and bounded next-work control-surface discovery.

- General new runtime implementation: **ANVIL**.
- Integration / synchronization / merge control: **SWITCHYARD**.
- Independent technical review: **SENTINEL**.

FOUNDRY retains only an incumbent repair-return exception for implementation branches this continuity previously modified. A concrete independent-review defect must be returned before that exception permits another runtime write.

## Current accepted baseline relevant to this lane

Current main at snapshot:

`8397cbc2941a706440cabd0ffb93cac4ab1bdf6d`

This includes:
- PR #57 Operator Intent Compiler request shaping;
- PR #39 Context Builder frozen evidence-integrity foundation, merged after synchronized head `5928abe4550dbf7a75c2a2825e3cda5033ead830`, Runtime CI #422 PASS, and SENTINEL CLEAN integrated-head review.

## Active owned planning lane

### PR #71 — Reconcile current capability roadmap state

- Branch: `planning/current-capability-reconciliation-20260816`
- Current planning head: `2ae42c6f74d493aafecb3b0073e13d44a7794e10`
- Original branch ancestry remains historical from `main@146f092a...`; SWITCHYARD owns later current-main synchronization.
- Exact original-base delta remains only:
  - `work/roadmaps/README.md`
  - `work/roadmaps/current-capability-reconciliation-2026-08-16.md`
  - `work/tasks/roadmap-current-state-reconciliation.md`
- Latest factual refresh records:
  - #39 `ACCEPTED`;
  - #30 synchronized/CI-green and fresh-review pending;
  - #44 clean feature-layer / integration pending;
  - #41 clean feature-layer / integration pending after accepted #39;
  - #48 integration pending;
  - #49 historical A2 layer without its own blocker;
  - #50 immutable-UNKNOWN + active-runtime legacy-token blockers;
  - #43 bounded scope-contract repair and #60 clean downstream layer;
  - #51/#52 planning-only;
  - legacy candidates classified rather than revived wholesale.
- State: **AWAITING FRESH EXACT-HEAD RUNTIME CI.** All earlier #71 CI/review packets are stale. After green CI, hand exact head to SENTINEL and freeze. FOUNDRY will not synchronize or merge it.

## Incumbent implementation handoffs

These remain non-writable unless a new concrete implementation defect is returned to FOUNDRY.

### PR #30 — Append-only run environment evidence

- Feature repair head `7bae6d5758619a391c7551ee4589ea2d80d0a5b8` was CLEAN IN-LAYER after Runtime CI #415.
- SWITCHYARD has now synchronized it to accepted main:
  - base `main@8397cbc2941a706440cabd0ffb93cac4ab1bdf6d`;
  - current head `4e158f65a422f14d7d12b2b1b8b0297e9f3ca5d7`;
  - Runtime CI #442 / `31965641572` PASS.
- State: **SWITCHYARD INTEGRATION LANE / FRESH INDEPENDENT REVIEW PENDING.** FOUNDRY must not modify this synchronized head unless a reviewer returns a concrete implementation defect.

### PR #44 — Full-fidelity hcom lineage read

- Repaired feature head `6f2b774eee27a0596820b12f080bfd7e60c0f50e`.
- Runtime CI #419 / `31951668246` PASS.
- SENTINEL disposition: **CLEAN IN-LAYER / FEATURE-HEAD ONLY / NOT INTEGRATION-READY**.
- Closed defect: bare local `event_id` is the configured-store event identity; `instance` is metadata and cannot qualify duplicate IDs.
- State: **FROZEN / HANDED TO SWITCHYARD FOR SYNCHRONIZATION.** FOUNDRY makes no further write unless a concrete implementation defect is returned.

### PR #45 — Exact hcom message relationships

- Head `b78de03a9e05fe19846d0c0629a55e54427fa587`.
- Runtime CI #346 PASS.
- SENTINEL: **CLEAN IN-LAYER / NOT INTEGRATION-READY**.
- State: **FROZEN / BLOCKED UPSTREAM** until #44 is accepted; then SWITCHYARD must rebuild/synchronize #45 on accepted ancestry and require fresh CI/review.

### PR #48 — Adapter-qualified run/session lineage A1

- Head `2f23959afff9525beada28993bad536878310b7f`.
- Runtime CI #392 PASS.
- SENTINEL: **CLEAN IN-LAYER / NOT INTEGRATION-READY**.
- State: **FROZEN / HANDED TO SWITCHYARD** for current-main synchronization and integrated gates.

## Planning / observation-only dependency lanes

### Context Builder

- #39: **ACCEPTED** on current main.
- #41: feature head `ec525615fd708610bc3e90e07a95bb6c791d2465`, CI #382 PASS, SENTINEL CLEAN IN-LAYER. With #39 accepted, remaining work is integration/rebuild; FOUNDRY observes only.
- #53: `d5c03a8e...`, CI #348 PASS, own layer clean; still downstream of accepted/integrated #41.

ANVIL owns Development; SWITCHYARD owns integration.

### Execution lineage downstream

- #49: current historical A2 head `ed865be729cf2d15663258fd46c9296ea32d28e7`; independent review found no A2-specific blocker, but it must be rebuilt after accepted #48.
- #50: actual head `832fa4ab2c3e97a8f7cdc22a73baca0d276adfc0`; two blockers remain:
  1. UNKNOWN submission attribution must be immutable evidence, not backfillable row absence;
  2. active-runtime `legacy/` wording fails the legacy-removal gate; exact-head CI #274 failed.
- Do not trust #50 PR-body green-run claims tied to non-resolving or other-PR SHAs.

FOUNDRY does not implement #49/#50 unless explicitly reassigned under coordination.

### Operational learning

- #43: substantive runtime/authority semantics reviewed clean; bounded task/PR scope omitted its schema-test file. Planning state: repair required for scope contract before integration.
- #60: own layer CLEAN IN-LAYER, downstream of corrected/accepted #43.

### Communication/wait design

- #51/#52 remain planning-only evidence.
- No exact provider-event receipt => no heuristic task/run communication join.
- Request + bounded silence != WAITING.

## Legacy reconciliation

The legacy audit/backlog are options/evidence, not an implementation queue. Preserve problems, invariants, experiments, and useful techniques; classify them as absorbed, partially represented/open, or evidence-triggered. Do not revive legacy subsystems wholesale.

## Explicit non-ownership

FOUNDRY will not:
- edit another agent's coordination file;
- synchronize/merge feature branches;
- independently approve work FOUNDRY authored/repaired;
- become a second general Development lane;
- modify #30/#44/#45/#48 while another lane is reviewing/integrating them;
- convert planning/design evidence into task, policy, review, wait, or promotion authority.

## Current handoffs

- #71 → fresh CI, then SENTINEL exact-head planning review, then SWITCHYARD integration if clean.
- #30 → SWITCHYARD synchronized head, fresh independent review pending.
- #44 → feature layer clean, SWITCHYARD synchronization next.
- #45 → waits accepted #44.
- #48 → SWITCHYARD integration.
- #41 → integration/rebuild after accepted #39; not a FOUNDRY implementation lane.

## Concurrency rule

Before any FOUNDRY write:

1. re-read live `main`;
2. re-read all current coordination files and exact target PR/base/head;
3. stop if a target moved unexpectedly or another owner claimed it;
4. never force-push/overwrite;
5. never reuse CI/review across a changed head/base;
6. keep planning work out of runtime/schema/test paths;
7. for incumbent repair returns, modify only the explicitly returned defect and refreeze for independent review.