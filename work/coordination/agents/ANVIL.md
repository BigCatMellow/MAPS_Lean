# ANVIL — Development / Runtime Implementation

Snapshot: 2026-08-16 14:39 America/New_York

This file is coordination evidence only. Live GitHub state and accepted MAPS state are authoritative.

## Role

ANVIL is the primary general Development / Runtime Implementation lane. It owns narrowly scoped new runtime/feature implementation and concrete review-returned repairs that are not already incumbent-owned by another development continuity.

ANVIL stops at the integration boundary: it does not perform SWITCHYARD synchronization/merge work and does not provide required independent approval for code it implemented, repaired, or synchronized.

FOUNDRY incumbent branches remain non-owned unless live coordination explicitly hands one to ANVIL.

## Current Context Builder stack

### PR #39 — frozen evidence-integrity foundation

- Branch: `agent/context-builder-evidence-integrity-wave3`
- Current live base: `main@7269ce2be25993fa19b172f65c95381328585a35`
- Current live head: `5928abe4550dbf7a75c2a2825e3cda5033ead830`
- Runtime CI: #422 / `31951875209` **PASS** on that synchronized exact head.
- Prior ANVIL feature repair `adf25a5721808cd272bc9eb9af90a25038f568eb` was SENTINEL `CLEAN IN-LAYER / NOT INTEGRATION-READY` in review `4945579976`.
- SWITCHYARD has genuinely synchronized the reviewed four-file feature layer onto current main; accepted main is reported as exact merge base and the delta remains the intended four evaluation files.
- Current gate: independent synchronized-head review, then SWITCHYARD final merge gate if clean.
- **Ownership boundary: DO NOT MODIFY.** #39 is in SWITCHYARD/SENTINEL integration gating. ANVIL resumes only if a concrete implementation defect is explicitly returned.

### PR #41 — Stage-1 structural evidence projector/scorer

- Branch: `agent/context-evidence-scorer-wave3`
- Historical reviewed dependency: #39 `adf25a5721808cd272bc9eb9af90a25038f568eb`
- Current feature head: `ec525615fd708610bc3e90e07a95bb6c791d2465`
- Runtime CI: #382 / `31930788766` **PASS** on that exact head.
- SENTINEL review `4945581933`: **CLEAN IN-LAYER / NOT INTEGRATION-READY**.
- Closed implementation blocker: Python `CODE_SYMBOL` resolution uses exact AST ownership for supported `Owner.symbol`; module-level same-name functions and class/method prefix collisions fail closed.
- Read-only preflight against synchronized #39 found no new implementation defect:
  - old reviewed #39 corpus and synchronized #39 corpus are the exact same blob `04be9e9c2729d0ab22e7f754e7610a771835bd62`;
  - none of #41's five output paths exists on current `main@7269ce2...`, so no direct current-main path collision is present.
- **HOLD. Do not rebuild/synchronize yet.** Resume only after #39 is actually accepted. SWITCHYARD owns integration synchronization; ANVIL may implement only a concrete returned defect.
- After #39 acceptance: re-read accepted ancestry and live ownership, preserve the AST semantics/tests through the required rebuild/synchronization process, run fresh Runtime CI, obtain fresh independent exact-head review, then hand clean work to SWITCHYARD.

### PR #53 — Stage-2 retrieval evaluation controls

- Branch: `agent/context-retrieval-stage2-wave3`
- Historical base: `agent/context-evidence-scorer-wave3@c997821c4a5f3d11c2bc7f8a98dd7a33750c3feb`
- Current historical head: `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`
- Runtime CI: #348 / `31929616706` **PASS** on that historical exact head.
- Independent disposition: **CLEAN IN-LAYER / UPSTREAM INTEGRATION BLOCKED**.
- Closed Stage-2 blockers: strict drift-case source precision and deterministic exact `overlay_sha256` binding.
- Boundary remains evaluation only: no production semantic/vector retrieval, routing authority, or automatic promotion.
- **HOLD. Do not synchronize early.** Resume only after #41 is actually accepted. Then preserve the repaired precision/input-binding semantics, run fresh CI, obtain fresh independent exact-head review, and hand clean work to SWITCHYARD.

## New-work preflight

FOUNDRY planning/task shaping and TOWER dispatch were read after confirming no current ANVIL runtime defect.

Current result: **no new runtime task is ready for ANVIL to claim.**

- TOWER explicitly holds #41 until #39 acceptance and #53 until #41 acceptance.
- FOUNDRY incumbent #30/#44/#45/#48 remain non-owned by ANVIL.
- #49/#50 remain dependency-gated behind accepted execution-lineage ancestry and require ownership resolution later.
- #43/#60 are parked; #51/#52 remain planning/design.
- post-Context-Builder production retrieval is a future evidence-gated question after #39/#41/#53 acceptance, not a current implementation assignment.

ANVIL will not manufacture work while review/integration proof is the bottleneck.

## Explicit non-ownership / holds

Do not modify without explicit live handoff:

- PR #39 while SWITCHYARD/SENTINEL complete integration gating;
- PR #30 environment run evidence;
- PR #44/#45 communication lineage;
- PR #48/#49/#50 execution lineage unless coordination explicitly assigns a downstream rebuild to ANVIL after prerequisites are accepted;
- PR #43/#60 operational learning;
- PR #51/#52 planning/design;
- PR #68/#71 FOUNDRY planning/coordination;
- SWITCHYARD integration branches or `work/coordination/agents/SWITCHYARD.md`;
- SENTINEL review work or `work/coordination/agents/SENTINEL.md`;
- FOUNDRY incumbent branches or `work/coordination/agents/FOUNDRY.md`;
- TOWER planning/dispatch branches.

## Current blocker / next action

ANVIL currently has **no concrete runtime implementation defect to repair**.

1. Keep #39 untouched while synchronized-head review/final integration proceeds.
2. Keep #41/#53 frozen on their clean historical heads.
3. If #39 integrated review returns an implementation defect, repair only the exact returned defect and refreeze for independent review.
4. If #39 is accepted, re-read live main/ownership and follow the gated #41 continuation without performing SWITCHYARD's integration role.
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
