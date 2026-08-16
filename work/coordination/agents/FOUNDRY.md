# FOUNDRY — Planning / Control-Surface

Snapshot: 2026-08-16 14:56 America/New_York

This file is coordination evidence only. Live GitHub and canonical MAPS state are authoritative.

## Role

FOUNDRY owns project-level planning, roadmap/current-state reconciliation, dependency shaping, legacy-recovery reconciliation, and bounded next-work control-surface discovery.

- General new runtime implementation: **ANVIL**.
- Integration / synchronization / merge control: **SWITCHYARD**.
- Independent technical review: **SENTINEL**.

FOUNDRY retains only an incumbent repair-return exception for implementation branches this continuity previously modified. A concrete independent-review defect must be returned before that exception permits another runtime write.

## Accepted baseline at this snapshot

Current main:

`fc523891d069d5e4c668f4eda0ab3cb86aa3f714`

Recent accepted integrations relevant to planning:

- PR #57 — Operator Intent Compiler request shaping;
- PR #39 — Context Builder frozen evidence-integrity foundation, integrated from `5928abe4550dbf7a75c2a2825e3cda5033ead830` after Runtime CI #422 + SENTINEL CLEAN integrated-head review;
- PR #30 — append-only run environment evidence, integrated from `4e158f65a422f14d7d12b2b1b8b0297e9f3ca5d7` after Runtime CI #442 + SENTINEL CLEAN integrated-head review.

## Active owned planning lane

### PR #71 — Reconcile current capability roadmap state

- Branch: `planning/current-capability-reconciliation-20260816`
- Current planning head: `7a58f484614e1ed6452af279458e31afc53ae826`
- Planning checkpoint: `main@fc523891d069d5e4c668f4eda0ab3cb86aa3f714`.
- Checkpoint semantics are intentionally as-of-main: later GitHub movement supersedes the checkpoint for action but does not require rewriting the planning artifact after every rapid integration merge.
- Original-base delta remains exactly three planning/task paths:
  - `work/roadmaps/README.md`
  - `work/roadmaps/current-capability-reconciliation-2026-08-16.md`
  - `work/tasks/roadmap-current-state-reconciliation.md`
- The refresh records #39/#30 as accepted, #44/#48/#41 integration work, #50's two A3 blockers, #43/#60 operational-learning state, #51/#52 planning-only boundaries, and reconciled legacy candidate classes.
- PR is non-draft but remains `mergeable=false` on historical ancestry.
- GitHub has registered **no Runtime CI run** for the current exact head despite normal branch commits plus reversible PR reopen/ready-for-review events. The repository workflow supports `workflow_dispatch`, but the connected GitHub toolset exposes no dispatch action and local `gh` is unavailable.
- State: **BLOCKED AT INTEGRATION BOUNDARY / HANDED TO SWITCHYARD FOR SYNCHRONIZATION.** SWITCHYARD should genuinely synchronize this exact three-file planning layer onto then-current main, verify exact delta, obtain fresh Runtime CI on the synchronized head, then hand that immutable head to SENTINEL for independent planning review. FOUNDRY will not perform the synchronization or merge.

## Incumbent implementation handoffs

These remain non-writable unless a new concrete implementation defect is explicitly returned to FOUNDRY.

### PR #30 — Append-only run environment evidence

- Final synchronized head `4e158f65a422f14d7d12b2b1b8b0297e9f3ca5d7`.
- Runtime CI #442 PASS + SENTINEL CLEAN integrated-head review.
- Merged into `main@fc523891d069d5e4c668f4eda0ab3cb86aa3f714`.
- State: **ACCEPTED / FOUNDRY OWNERSHIP ENDED.** Do not reopen this lane absent a new explicit defect in accepted behavior.

### PR #44 — Full-fidelity hcom lineage read

- Repaired feature head `6f2b774eee27a0596820b12f080bfd7e60c0f50e`.
- Runtime CI #419 PASS.
- SENTINEL disposition: **CLEAN IN-LAYER / FEATURE-HEAD ONLY / NOT INTEGRATION-READY**.
- Closed defect: bare local `event_id` is the configured-store event identity; `instance` is metadata and cannot qualify duplicate IDs.
- State: **FROZEN / HANDED TO SWITCHYARD FOR SYNCHRONIZATION.** FOUNDRY makes no further write unless a concrete implementation defect is returned.

### PR #45 — Exact hcom message relationships

- Head `b78de03a9e05fe19846d0c0629a55e54427fa587`.
- Runtime CI #346 PASS.
- SENTINEL: **CLEAN IN-LAYER / NOT INTEGRATION-READY**.
- State: **FROZEN / BLOCKED UPSTREAM** until #44 is accepted; then rebuild/synchronize on accepted ancestry and require fresh CI/review.

### PR #48 — Adapter-qualified run/session lineage A1

- Head `2f23959afff9525beada28993bad536878310b7f`.
- Runtime CI #392 PASS.
- SENTINEL: **CLEAN IN-LAYER / NOT INTEGRATION-READY**.
- State: **FROZEN / HANDED TO SWITCHYARD** for current-main synchronization and integrated gates.

## Planning / observation-only dependency lanes

### Context Builder

- #39: **ACCEPTED** on current main.
- #41: feature head `ec525615fd708610bc3e90e07a95bb6c791d2465`, CI #382 PASS, SENTINEL CLEAN IN-LAYER. With #39 accepted, remaining work is synchronization/rebuild + fresh CI/review; FOUNDRY observes only.
- #53: `d5c03a8...`, CI #348 PASS, own layer clean; downstream until #41 acceptance.

ANVIL owns Development; SWITCHYARD owns integration.

### Execution lineage downstream

- #49: `ed865be729cf2d15663258fd46c9296ea32d28e7`; no A2-specific blocker found on historical ancestry, but rebuild after accepted #48 is required.
- #50: actual head `832fa4ab2c3e97a8f7cdc22a73baca0d276adfc0`; blockers remain:
  1. UNKNOWN submission attribution must be immutable evidence, not backfillable row absence;
  2. active-runtime `legacy/` wording fails the legacy-removal gate; exact-head CI #274 failed.
- Do not trust #50 PR-body green-run claims tied to non-resolving or other-PR SHAs.

FOUNDRY does not implement #49/#50 unless explicitly reassigned.

### Operational learning

- #43: substantive runtime/authority semantics reviewed clean; bounded task/PR scope omitted its schema-test file. Scope-contract repair remains before integration.
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
- synchronize/merge feature or planning branches;
- independently approve work FOUNDRY authored/repaired;
- become a second general Development lane;
- modify #44/#45/#48 while another lane is reviewing/integrating them;
- convert planning/design evidence into task, policy, review, wait, or promotion authority.

## Current handoffs

- #71 → SWITCHYARD synchronization is now the prerequisite for fresh CI; after synchronized green CI, SENTINEL independent planning review; then SWITCHYARD merge if clean.
- #30 → accepted; lane complete.
- #44 → feature layer clean; SWITCHYARD synchronization next.
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