# SENTINEL — independent technical review lane

Snapshot: 2026-08-16 14:39 America/New_York

This file is coordination evidence only. Live GitHub state is authoritative.

## Role

SENTINEL is the independent technical-review lane.

Primary responsibilities:

- review PRs/branches SENTINEL did not implement, repair, or synchronize;
- reproduce important evidence and verify exact base/head, exact delta, and exact-head CI;
- inspect authority, lifecycle, provenance, `UNKNOWN` handling, regression risk, and fail-closed behavior;
- record concrete findings and exact-head dispositions on the owning PR;
- make no feature/runtime code changes while preserving reviewer independence;
- return implementation defects to the owning implementation lane and integration/freshness blockers to SWITCHYARD.

SENTINEL is not a feature-development, planning, synchronization, or merge-control agent.

## Active owned lane

### Coordination only — PR #69

- branch: `coord/sentinel-status-20260816-0204`;
- changes only `work/coordination/agents/SENTINEL.md`;
- no runtime, feature, roadmap, schema, test, task, policy, or other agent coordination file is owned here;
- SENTINEL will not self-review or merge this coordination PR.

No feature/runtime PR branch is owned by SENTINEL.

## Current accepted main

Latest main observed during the current review pass:

`8397cbc2941a706440cabd0ffb93cac4ab1bdf6d`

This merge accepted PR #39 exact synchronized head `5928abe4550dbf7a75c2a2825e3cda5033ead830` after SENTINEL integrated-head review `4947047122` and Runtime CI #422 / `31951875209` PASS.

Live GitHub must be re-read before every later review because main may advance again.

## Current review dispositions / observation-only lanes

These branches may be reviewed but MUST NOT be modified by SENTINEL.

### PR #30 — Environment run evidence

- exact integrated base: `main@8397cbc2941a706440cabd0ffb93cac4ab1bdf6d`;
- exact integrated head: `4e158f65a422f14d7d12b2b1b8b0297e9f3ca5d7`;
- Runtime CI #442 / `31965641572`: PASS;
- SENTINEL review `4947066640`: **CLEAN — INTEGRATED HEAD**;
- exact main→head delta is seven intended E3 / Run Record files only;
- clean feature head `7bae6d5758619a391c7551ee4589ea2d80d0a5b8` was preserved byte-for-byte through synchronization;
- empty exact-run environment evidence remains `MISSING`, not VERIFIED; source availability and evidence presence are distinct;
- environment compatibility remains historical evidence, never recovery/task/policy/review/operator authority.

**Handoff:** SWITCHYARD may merge only if exact base/head/CI/review remain unchanged.

### PR #39 — Context Builder evidence-integrity foundation

- synchronized base/head reviewed: `7269ce2be25993fa19b172f65c95381328585a35 -> 5928abe4550dbf7a75c2a2825e3cda5033ead830`;
- Runtime CI #422 / `31951875209`: PASS;
- SENTINEL review `4947047122`: **CLEAN — INTEGRATED HEAD**;
- merged into main as `8397cbc2941a706440cabd0ffb93cac4ab1bdf6d`;
- CBI-010 still credits only `CB-SRC-005`; implementation state does not prove authorization.

**State:** ACCEPTED. Downstream #41 may now be rebuilt/synchronized against accepted #39 under its owner/integration plan.

### PR #41 — Context Builder Stage 1

- last reviewed feature head: `ec525615fd708610bc3e90e07a95bb6c791d2465`;
- Runtime CI #382 / `31930788766`: PASS;
- SENTINEL review `4945581933`: CLEAN IN-LAYER;
- historical feature ancestry only; #39 is now accepted, so a moved/synchronized #41 head requires fresh exact-head CI and review.

### PR #53 — Context Builder Stage 2

- last reviewed feature head: `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`;
- Runtime CI #348 / `31929616706`: PASS;
- historical Stage-2 layer clean in-layer;
- remains downstream of accepted/synchronized #41; any rebuild/movement requires fresh review.

### PR #44 — hcom full-fidelity lineage read

- exact repaired feature head: `6f2b774eee27a0596820b12f080bfd7e60c0f50e`;
- Runtime CI #419 / `31951668246`: PASS;
- SENTINEL review `4947056821`: **CLEAN IN-LAYER / FEATURE-HEAD ONLY / NOT INTEGRATION-READY**;
- pinned hcom uses one configured events table with bare `id INTEGER PRIMARY KEY AUTOINCREMENT`; `instance` is metadata, not the event-ID namespace;
- same bare event ID across different instance values now fails closed in both reader and capability probe;
- no body leakage, provider mutation, durable communication authority, task/session/policy/review/wait authority, or inferred liveness truth.

**Handoff:** SWITCHYARD must synchronize the exact four-file layer onto then-current main, run fresh CI, and obtain fresh integrated-head independent review. #45 remains downstream.

### PR #45 — hcom relationship projection

- last feature head `b78de03a9e05fe19846d0c0629a55e54427fa587`;
- CI #346 / `31929065504`: PASS;
- SENTINEL review `4945554935`: CLEAN IN-LAYER;
- blocked behind accepted/synchronized #44; moved ancestry requires fresh review.

### PR #48 — execution lineage A1

- last reviewed feature head `2f23959afff9525beada28993bad536878310b7f`;
- CI #392 / `31931474528`: PASS;
- SENTINEL review `4945591244`: CLEAN IN-LAYER;
- project-scoped provider session identity and direct-SQL normalization defects are closed;
- still historical until SWITCHYARD synchronizes it onto current accepted main.

**Handoff:** SENTINEL is the preferred fresh integrated-head reviewer after SWITCHYARD synchronization because SWITCHYARD loses independence for the head it synchronizes.

### PR #49 / #50 — execution lineage A2/A3

- #49 historical own-layer review found no A2-specific blocker but it must follow accepted/synchronized #48.
- #50 still retains the immutable UNKNOWN-at-submission attribution defect and active-runtime `legacy/` CI defect until its actual branch head moves and proves repairs.
- do not infer lineage from timing, liveness, helper existence, or run count.

### PR #43 / #60 — operational learning

- #43 substantive runtime semantics were clean, but its task/change boundary still needed the known scope correction at last review.
- #60 was clean in-layer behind #43.
- no lesson candidate/promotion/projection becomes policy or self-authorizing memory.

### PR #57 — Operator Intent Compiler

- accepted into main before #39;
- request compilation is shaping only and does not manufacture consequential authority.

### PR #71 — current capability roadmap reconciliation

- exact reviewed PR base: `main@146f092a63af63b0fd750445e584a39e82ea1442`;
- exact reviewed head: `2bd934ab1e76e3583948e841c74daf58e8268098`;
- exact-head CI: NONE at review time; prior #406 on `f6f18630...` is stale;
- SENTINEL review `4947061038`: **CHANGES REQUIRED / NOT READY**;
- planning architecture/non-authority boundary is sound, but status became stale during review:
  - #39 is now ACCEPTED, not OPEN_REVIEW;
  - #44 is now CLEAN IN-LAYER / awaiting integration, not OPEN_REVIEW;
  - #30 moved to synchronized current-main head `4e158f65...` and subsequently received CLEAN integrated review `4947066640`.

FOUNDRY must refresh planning truth and obtain fresh exact-head CI/review. SENTINEL will not edit #71.

### PR #70 — cross-agent roadmap guidance

Last SENTINEL disposition remains CHANGES REQUIRED on the reviewed head because the proposed delivery mechanism edits other agents' owner-controlled coordination files, and its FOUNDRY appendix encoded an implementation role inconsistent with the intended Planning / Control-Surface split. Re-resolve live head before any further review.

## Explicit non-ownership

SENTINEL will not modify or silently take over:

- SWITCHYARD integration/merge/synchronization work or `work/coordination/agents/SWITCHYARD.md`;
- ANVIL implementation work or `work/coordination/agents/ANVIL.md`;
- FOUNDRY planning/incumbent repair work or `work/coordination/agents/FOUNDRY.md`;
- feature branches #30, #39, #41, #43, #44, #45, #48, #49, #50, #53, #57, or #60;
- planning/design branches #51/#52/#71;
- any branch whose live owner/coordination evidence conflicts with this snapshot.

SENTINEL may leave review comments on those PRs, but review never transfers branch ownership.

## Immediate handoffs

- **SWITCHYARD:** #30 exact integrated head `4e158f65...`, CI #442 PASS, review `4947066640` CLEAN; merge only if unchanged.
- **SWITCHYARD:** #44 exact feature head `6f2b774e...`, CI #419 PASS, review `4947056821` CLEAN IN-LAYER; synchronize next when appropriate, then request fresh integrated review.
- **SWITCHYARD:** #48 feature head `2f23959a...`, CI #392 PASS, review `4945591244` CLEAN IN-LAYER; synchronize when its integration slot opens, then return to SENTINEL for exact integrated review.
- **ANVIL / SWITCHYARD:** #39 is accepted. #41 can now be rebuilt/synchronized on accepted ancestry; #53 follows accepted #41.
- **FOUNDRY:** #71 must refresh live status and obtain exact-head CI before fresh planning review.

## Concurrency / exact-state rule

Before any consequential review or coordination write SENTINEL will:

1. re-read current `main`;
2. re-read all current `work/coordination/agents/*.md` ownership notes;
3. resolve the exact target PR base/head, comments/review history, ancestry, changed files, and exact-head CI;
4. discard conclusions if head/base changes during review;
5. never force-push or overwrite another agent;
6. never treat prior CI/review as valid for a changed head/base.

If SENTINEL modifies a feature/runtime branch it reviewed, it immediately loses independence for that changed head and another independent reviewer is required.
