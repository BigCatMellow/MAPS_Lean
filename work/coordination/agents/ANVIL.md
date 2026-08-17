# ANVIL — Development / Runtime Implementation

Snapshot: 2026-08-16 14:44 America/New_York

This file is coordination evidence only. Live GitHub state and accepted MAPS state are authoritative.

## Role

ANVIL is the primary general Development / Runtime Implementation lane. It owns narrowly scoped new runtime/feature implementation and concrete review-returned repairs that are not already incumbent-owned by another development continuity.

ANVIL stops at the integration boundary: it does not perform SWITCHYARD current-main synchronization/merge work and does not provide required independent approval for code it implemented or repaired.

FOUNDRY incumbent branches remain non-owned unless live coordination explicitly hands one to ANVIL.

## Current Context Builder stack

### PR #39 — frozen evidence-integrity foundation — ACCEPTED

- PR #39 is merged.
- Accepted merge commit / current main at this checkpoint: `8397cbc2941a706440cabd0ffb93cac4ab1bdf6d`.
- Integrated feature head: `5928abe4550dbf7a75c2a2825e3cda5033ead830` on prior accepted base `7269ce2be25993fa19b172f65c95381328585a35`.
- Runtime CI #422 / `31951875209`: **PASS** on the exact integrated head.
- SENTINEL integrated-head review `4947047122`: **CLEAN — INTEGRATED HEAD**.
- The accepted four-file layer preserves the repaired CBI-010 authority rule: implementation/current-state evidence cannot substitute for proposal-authorization proof.
- **ANVIL ownership ended at merge. Do not modify #39.**

### PR #41 — Stage-1 structural evidence projector/scorer

- Branch: `agent/context-evidence-scorer-wave3`.
- Current live feature head remains `ec525615fd708610bc3e90e07a95bb6c791d2465`; no concurrent branch movement was found after #39 acceptance.
- Historical reviewed dependency: repaired #39 `adf25a5721808cd272bc9eb9af90a25038f568eb`.
- Runtime CI #382 / `31930788766`: **PASS** on that historical exact head.
- SENTINEL review `4945581933`: **CLEAN IN-LAYER / NOT INTEGRATION-READY**.
- Closed implementation blocker: Python `CODE_SYMBOL` resolution uses exact AST ownership for supported `Owner.symbol`; module-level same-name functions and class/method prefix collisions fail closed.
- Read-only preflight before #39 merge found no implementation conflict:
  - historical reviewed #39 corpus and synchronized/accepted #39 corpus share exact blob `04be9e9c2729d0ab22e7f754e7610a771835bd62`;
  - none of #41's five output paths existed on then-current accepted main, so no direct path collision was present.
- **Dependency status: READY.** #39 is now accepted.
- **Development status: NO DEFECT RETURNED.** No ANVIL code repair is currently justified.
- **Integration boundary: SWITCHYARD owns current-main synchronization.** The operator explicitly forbids ANVIL from performing SWITCHYARD's integration work, so ANVIL will not rebase/merge/reconstruct #41 merely because its upstream is now accepted.
- If SWITCHYARD synchronization or integrated review exposes a concrete implementation conflict, return that exact defect to ANVIL; ANVIL will repair the smallest coherent defect, run fresh exact-head Runtime CI, freeze, and hand it to SENTINEL.

### PR #53 — Stage-2 retrieval evaluation controls

- Branch: `agent/context-retrieval-stage2-wave3`.
- Current historical head: `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`.
- Historical base: `agent/context-evidence-scorer-wave3@c997821c4a5f3d11c2bc7f8a98dd7a33750c3feb`.
- Runtime CI #348 / `31929616706`: **PASS** on that historical exact head.
- Independent disposition: **CLEAN IN-LAYER / UPSTREAM INTEGRATION BLOCKED**.
- Closed Stage-2 blockers: strict drift-case source precision and deterministic exact `overlay_sha256` binding.
- Boundary remains evaluation only: no production semantic/vector retrieval, routing authority, or automatic promotion.
- **HOLD.** #53 remains blocked until #41 is actually accepted. Do not synchronize early and do not widen the feature.

## New-work preflight

FOUNDRY planning/task shaping and TOWER dispatch were read after confirming no current ANVIL runtime defect.

Current result: **no unrelated runtime task is ready for ANVIL to claim.**

- FOUNDRY incumbent #30/#44/#45/#48 remain non-owned by ANVIL.
- #49/#50 remain dependency/ownership gated; no reassignment to ANVIL is accepted here.
- #43/#60 are parked; #51/#52 remain planning/design.
- post-Context-Builder production retrieval remains an evidence-gated future question after #39/#41/#53 acceptance, not a current implementation assignment.
- TOWER's derived dispatch anticipated an ANVIL rebuild after #39 acceptance, but the operator's current explicit boundary assigns integration synchronization to SWITCHYARD. Operator authority wins; ANVIL does not silently take that integration work.

ANVIL will not manufacture work while integration proof is the actual bottleneck.

## Explicit non-ownership / holds

Do not modify without explicit live handoff:

- merged PR #39;
- PR #30 environment run evidence;
- PR #44/#45 communication lineage;
- PR #48/#49/#50 execution lineage unless coordination explicitly assigns a downstream Development repair after prerequisites are accepted;
- PR #43/#60 operational learning;
- PR #51/#52 planning/design;
- PR #68/#71 FOUNDRY planning/coordination;
- SWITCHYARD integration branches or `work/coordination/agents/SWITCHYARD.md`;
- SENTINEL review work or `work/coordination/agents/SENTINEL.md`;
- FOUNDRY incumbent branches or `work/coordination/agents/FOUNDRY.md`;
- TOWER planning/dispatch branches.

## Current blocker / next action

ANVIL currently has **no concrete runtime implementation defect to repair**.

1. #39 is accepted; no further ANVIL action exists there.
2. Keep #41's clean feature head unchanged while SWITCHYARD owns accepted-ancestry synchronization/integration.
3. Keep #53 frozen until #41 is actually accepted.
4. If #41 integration returns a concrete implementation defect, repair only that defect and refreeze for independent review.
5. Do not claim unrelated work merely to keep the Development lane busy.

## Concurrency rule

Before any write ANVIL will:

1. re-read live `main`;
2. re-read `work/coordination/README.md` and every live `work/coordination/agents/*.md` on accepted main;
3. re-read exact target PR/base/head, latest review/handoff evidence, and task boundary;
4. stop if another agent moved the branch into integration or otherwise owns the target;
5. never force-push or overwrite another agent;
6. never reuse CI/review evidence after a material head/base change;
7. prefer no write when no concrete Development work is authorized or ready.
