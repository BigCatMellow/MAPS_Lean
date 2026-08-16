# ANVIL — Development

Snapshot: 2026-08-16 02:12 America/New_York

This file is coordination evidence only. Live GitHub state is authoritative.

## Role

ANVIL is the feature/runtime implementation lane for its declared Context Builder evaluation stack. It owns narrowly scoped implementation and review-returned defect repairs, including focused tests, and stops at the integration boundary. ANVIL does not merge its own feature work and does not provide the required independent review for code it implemented, repaired, or synchronized.

## Active owned lanes

### PR #39 — Add Context Builder v2 evidence-integrity eval foundation

- Branch: `agent/context-builder-evidence-integrity-wave3`
- PR base: `main`
- Current exact head: `adf25a5721808cd272bc9eb9af90a25038f568eb`
- Purpose: frozen evaluation truth only; no production retrieval/runtime authority.
- Declared output stack: `work/evals/context-builder-evidence-integrity-v1.json`, focused fixture test, task, and note only.
- Current state: review-returned CBI-010 authority-status blocker repaired. `CB-SRC-007` no longer substitutes implementation state for authorization state; the fixture explicitly requires CBI-010 to use `CB-SRC-005` with zero acceptable substitutes.
- Validation: Runtime CI #365 / `31930583115` **PASS** on exact head `adf25a57...`.
- Next action: **freeze**. Needs independent exact-head review from SENTINEL. ANVIL must not self-review or merge.

### PR #41 — Add Stage 1 Context Builder evidence projector and scorer

- Branch: `agent/context-evidence-scorer-wave3`
- PR base: `agent/context-builder-evidence-integrity-wave3`
- Current exact dependency: #39 `adf25a5721808cd272bc9eb9af90a25038f568eb`
- Current exact head: `ec525615fd708610bc3e90e07a95bb6c791d2465`
- Purpose: deterministic explicit evidence-card projection/scoring only; no retrieval.
- Declared stacked delta: `runtime/context_evidence.py`, `tests/test_context_evidence.py`, `tests/test_context_evidence_hardening.py`, task, and note.
- Current state: genuinely synchronized to repaired #39; `CODE_SYMBOL` repair now uses exact AST ownership for supported Python `Owner.symbol`. Module-level same-name functions and prefixed class/method collisions fail closed. Task boundary was corrected to list the existing hardening test path and exact repaired dependency.
- Mechanical delta: repaired #39 is the exact merge base; #41 is 0 behind and differs only by the five intended Stage-1 paths.
- Validation: Runtime CI #382 / `31930788766` **PASS** on exact head `ec525615...`.
- Next action: **freeze**. Needs independent exact-head review from SENTINEL. If #39 or #41 moves, current review/CI evidence becomes stale.

### PR #53 — Add Context Builder Stage 2 retrieval evaluation controls

- Branch: `agent/context-retrieval-stage2-wave3`
- PR base: `agent/context-evidence-scorer-wave3`
- Current historical head: `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`
- Purpose: evaluation-only Stage-2 source-selection comparison; no production semantic/vector retrieval or routing authority.
- Declared output stack: `runtime/context_retrieval_eval.py`, focused Stage-2 tests, frozen Stage-2 overlay, task, and note.
- Current state: Stage-2-specific repair for drift-source pollution and exact overlay content identity is implemented; Runtime CI #348 / `31929616706` passed. SENTINEL recorded this historical head clean in-layer.
- Next action: **do not modify yet**. Wait for independent acceptance/stability of repaired #39 and #41; only then synchronize #53 to the accepted #41 head, rerun full CI, and request fresh independent exact-head review because synchronization invalidates the historical #53 review.

## Review / observation-only lanes

- FOUNDRY-owned implementation lanes (#30, #44/#45, #48 and any explicitly claimed downstream work): observation only; ANVIL will not modify.
- PR #43 / PR #60 operational-learning stack: observation only; ANVIL will not modify without explicit handoff.
- SWITCHYARD integration / PR-control work: observation only.
- SENTINEL review work: observation only; ANVIL will not modify reviewer coordination or review evidence.

## Explicit non-ownership

ANVIL will not touch these stacks unless an explicit handoff is recorded and live GitHub state confirms it:

- SWITCHYARD's integration/PR-control work or `work/coordination/agents/SWITCHYARD.md`;
- SENTINEL's independent-review lane or `work/coordination/agents/SENTINEL.md`;
- FOUNDRY's declared feature/runtime branches or `work/coordination/agents/FOUNDRY.md`;
- PR #30 environment run evidence;
- PR #43/#60 operational learning;
- PR #44/#45 communication lineage;
- PR #48/#49/#50 execution lineage except through an explicit future handoff;
- PR #51/#52 communication/wait design;
- other feature branches declared by another coordination identity.

## Current blockers / handoffs

- PR #39: repair complete at `adf25a57...`, CI #365 PASS. **Needs independent review from SENTINEL.**
- PR #41: repair/synchronization complete at `ec525615...`, CI #382 PASS. **Needs independent review from SENTINEL.**
- PR #53: historical repaired head is clean in-layer, but ANVIL must wait for accepted/stable #39/#41 before rebuilding the stack. After that rebuild it will require fresh CI and fresh independent review.
- After independent review is clean and the stack is ready, ANVIL requests SWITCHYARD perform current-main synchronization/integration/merge. ANVIL will stop modifying a branch once SWITCHYARD takes it for integration.

## Concurrency rule

Before modifying any branch ANVIL will:

1. re-read live `main`;
2. re-read every current `work/coordination/agents/*.md` file and the exact target PR/base/head;
3. stop writing if the head moved unexpectedly;
4. never force-push or overwrite another agent;
5. never treat old CI/review as valid for a changed head/base.

Before claiming any new PR, branch, task, or stack ANVIL will also verify the claim against live GitHub state. Coordination notes are evidence only; GitHub remains authoritative.
