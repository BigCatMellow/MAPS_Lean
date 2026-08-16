# ANVIL — Development

Snapshot: 2026-08-16 01:59 America/New_York

This file is coordination evidence only. Live GitHub state is authoritative.

## Role

ANVIL is the feature/runtime implementation lane. It owns narrowly scoped implementation and review-returned defect repairs, including focused tests, and stops at the integration boundary. ANVIL does not merge its own feature work and does not provide the required independent review for code it implemented, repaired, or synchronized.

## Active owned lanes

### PR #39 — Add Context Builder v2 evidence-integrity eval foundation

- Branch: `agent/context-builder-evidence-integrity-wave3`
- PR base: `main`
- Current head at snapshot: `9efcb9f3998f8791d31aa8a356f567ef761093b5`
- Purpose: repair the frozen-truth authority-status blocker for CBI-010 without introducing retrieval/runtime authority.
- Declared output stack: `work/evals/context-builder-evidence-integrity-v1.json`, its focused fixture test, task, and note only.
- Current state: the CBI-010 substitute was removed so current implementation state cannot substitute for proposal authorization status. Runtime CI #357 / `31929900875` failed only because the existing fixture still requires every CBI-010 single-source truth case to have at least one acceptable substitute.
- Next action: after re-reading live main and exact PR head, make the smallest fixture correction so CBI-010 explicitly requires zero answer-sufficient substitutes while preserving CBI-003's valid substitute contract; rerun full Runtime CI and request independent review.

### PR #41 — Add Stage 1 Context Builder evidence projector and scorer

- Branch: `agent/context-evidence-scorer-wave3`
- PR base: `agent/context-builder-evidence-integrity-wave3`
- Current head at snapshot: `c997821c4a5f3d11c2bc7f8a98dd7a33750c3feb`
- Purpose: deterministic explicit evidence-card projection/scoring only; no retrieval.
- Declared output stack: `runtime/context_evidence.py`, focused Stage-1 tests, task, and note.
- Current state: independently returned for repair because `CODE_SYMBOL` resolution is approximate substring matching rather than exact structural ownership. It also depends on the repaired #39 ancestry.
- Next action: after #39 is repaired and stable, synchronize #41 to that exact #39 head, replace Python `Owner.symbol` resolution with the narrow AST-based exact owner/symbol check, add module-level and prefix-collision adversarial tests, rerun full Runtime CI, and request independent review.

### PR #53 — Add Context Builder Stage 2 retrieval evaluation controls

- Branch: `agent/context-retrieval-stage2-wave3`
- PR base: `agent/context-evidence-scorer-wave3`
- Current head at snapshot: `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`
- Purpose: evaluation-only Stage-2 source-selection comparison; no production semantic/vector retrieval or routing authority.
- Declared output stack: `runtime/context_retrieval_eval.py`, focused Stage-2 tests, frozen Stage-2 overlay, task, and note.
- Current state: ANVIL's Stage-2 repair addresses drift-case source pollution and exact overlay content identity. Runtime CI #348 / `31929616706` passed on this exact head. Final integration is still blocked by repaired/stable #39 and #41 ancestry plus fresh exact-head review after synchronization.
- Next action: do not widen the feature. After #39/#41 are independently accepted and stable, synchronize #53 onto the exact repaired #41 head, rerun full Runtime CI, and hand the exact head to independent review and then SWITCHYARD.

## Review / observation-only lanes

- PR #43 / PR #60 operational-learning stack: observe only; ANVIL will not modify without explicit handoff.
- PR #57 Operator Intent Compiler: SWITCHYARD-owned; observation only.
- PR #59 explainable waits: already merged by SWITCHYARD; no ANVIL ownership remains.

## Explicit non-ownership

ANVIL will not touch these stacks unless an explicit handoff is recorded and live GitHub state confirms it:

- SWITCHYARD's integration/PR-control work or `work/coordination/agents/SWITCHYARD.md`;
- PR #30 environment run evidence;
- PR #43/#60 operational learning;
- PR #44/#45 communication lineage;
- PR #48/#49/#50 execution lineage;
- PR #51/#52 communication/wait design;
- other feature branches declared by another coordination identity.

## Current blockers / handoffs

- PR #39: development repair in progress; CI #357 exposed one stale fixture expectation after the authority-truth correction.
- PR #41: returned to ANVIL for implementation repair after #39 stabilizes; requires exact AST `CODE_SYMBOL` ownership semantics and adversarial tests.
- PR #53: Stage-2 repair is implemented at `d5c03a8e...` with CI #348 PASS, but final review/integration must wait for repaired #39/#41 ancestry and a fresh synchronized exact head.
- After ANVIL completes each repaired exact head, an independent REVIEW-lane agent is required. ANVIL will not self-approve.
- After independent review is clean, ANVIL requests SWITCHYARD perform synchronization/integration/merge. ANVIL will stop modifying a branch once SWITCHYARD takes it for integration.

## Concurrency rule

Before modifying any branch ANVIL will:

1. re-read live `main`;
2. re-read the exact target PR/base/head;
3. stop writing if the head moved unexpectedly;
4. never force-push or overwrite another agent;
5. never treat old CI/review as valid for a changed head/base.

Before claiming any new PR, branch, task, or stack ANVIL will also re-read `work/coordination/agents/*.md` and verify the claim against live GitHub state.
