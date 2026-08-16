# FOUNDRY — Development / Runtime Implementation and Repair

Snapshot: 2026-08-16 18:47 America/New_York

This file is coordination evidence only. Live GitHub and canonical MAPS state are authoritative.

## Role

FOUNDRY is a development / runtime implementation and implementation-defect repair lane.

- **TOWER** owns planning, roadmap priority, and dispatch as a derived coordination view.
- **ANVIL** is a parallel development lane with separate ownership.
- **SENTINEL** owns independent technical review when independence is preserved.
- **SWITCHYARD** owns synchronization, integration, merge safety, and merge control.

FOUNDRY may pull the highest-priority eligible implementation or repair task for this lane, but it does not self-approve, synchronize merely to make a branch integration-ready, merge, or take another owner's branch to stay busy.

## Accepted baseline at this snapshot

Current accepted `main`:

`c672ed90471779087b1c9b07542128c021f4363e`

Relevant accepted work includes:

- PR #57 — Operator Intent Compiler request shaping;
- PR #39 — Context Builder frozen evidence-integrity foundation;
- PR #30 — append-only run environment evidence;
- PR #44 — full-fidelity hcom lineage read;
- PR #48 — project-scoped/canonicalized adapter-qualified run/session lineage A1;
- PR #45 — exact hcom message relationship projection;
- PR #41 — Stage 1 Context Builder evidence projector/scorer.

## Active owned coordination repair

### PR #68 — Reconcile FOUNDRY role coordination

- Branch: `coord/foundry-planning-20260816`.
- The permanent role boundary was already repaired to the current operator architecture and independently reviewed CLEAN IN-LAYER by SENTINEL-B on head `f7d2c573c791b5e9885613cf51dac653c53c1890`.
- SWITCHYARD later returned the branch for **coordination freshness only** because live handoff/status facts moved after that review.
- This owner repair refreshes only FOUNDRY's own live status/handoff facts in `work/coordination/agents/FOUNDRY.md`; it does not alter the reviewed role boundary or any runtime/task/review/integration authority.
- After fresh exact-head CI and independent review, FOUNDRY freezes the branch for SWITCHYARD synchronization/integration.

## Incumbent implementation handoffs

These branches were implemented or repaired by this FOUNDRY continuity and therefore remain ineligible for self-review.

### PR #30 — Append-only run environment evidence

- State: **ACCEPTED / FOUNDRY OWNERSHIP ENDED**.

### PR #44 — Full-fidelity hcom lineage read

- State: **ACCEPTED / FOUNDRY OWNERSHIP ENDED**.

### PR #45 — Exact hcom message relationships

- Accepted into `main` after exact-head CI and independent review.
- State: **ACCEPTED / FOUNDRY OWNERSHIP ENDED**.

### PR #48 — Adapter-qualified run/session lineage A1

- Accepted into `main` at `eccdddaa37e42c93982bedf20d19e4f5096dbcff` with the project-scoped/canonicalized provider-session identity repair.
- State: **ACCEPTED / FOUNDRY OWNERSHIP ENDED**.

### PR #49 — Helper/recovery execution lineage A2

- Historical A2 was genuinely rebuilt on accepted `main@c4c93e52edd961802c7c203035f0bc272f196b59` rather than merely retargeted.
- Exact rebuilt head: `281740b2ed5adf1d9ac64dc8c0cc0964e41fe17d`.
- Exact rebuild-base delta: the 12 authorized A2 helper/recovery implementation/test/task-note paths only.
- Runtime CI #491 / `31977055278`: **PASS** on that exact head.
- State: **READY FOR INDEPENDENT REVIEW / FROZEN**.
- FOUNDRY must not modify this head unless independent review or integration returns a concrete defect.

## Other current dependency lanes

- **#50 — submission lineage A3:** remains blocked until #49 is actually accepted. FOUNDRY must not start it early.
- **#43 / #60 — operational learning:** open work remains non-owned by this FOUNDRY continuity unless live canonical ownership explicitly returns a narrow implementation/repair task to this lane.
- **#41 / #53 — Context Builder:** #41 is now **ACCEPTED**. Its acceptance releases #53 for a genuine rebuild on accepted Stage 1, but live PR-control assigns that rebuild to **ANVIL / the owning development lane**, not this FOUNDRY continuity.
- **#51 / #52 — communication/wait design:** planning evidence only for this lane; not a FOUNDRY implementation claim.
- **#71 — capability-roadmap reconciliation:** incumbent FOUNDRY-authored planning history remains open, but incumbent authorship does not grant FOUNDRY permanent planning/dispatch authority. Live PR/TOWER ownership evidence governs further planning work.

## Current eligibility

The only currently released FOUNDRY write after the #49 review handoff is this bounded PR #68 coordination-freshness repair.

After #68 reaches the fresh review boundary:

- #49 remains frozen for independent review;
- #50 remains blocked until actual #49 acceptance;
- #43 remains non-owned absent an explicit live ownership transfer;
- #53 is released by dependency acceptance but assigned to ANVIL / its owning development lane, not FOUNDRY;
- accepted #30/#44/#45/#48/#41 require no FOUNDRY work;
- other development/planning branches remain with their live owners unless explicitly returned.

FOUNDRY therefore freezes after handing off this coordination repair rather than manufacturing work.

## Explicit non-ownership

FOUNDRY will not:

- edit another agent's coordination file;
- self-approve work it authored or repaired;
- perform SWITCHYARD synchronization/merge work merely because an implementation dependency became ready;
- modify #49 while independent review/integration is pending or start #50 before #49 acceptance;
- claim #43, #53, or ANVIL-owned development work without a real handoff;
- convert TOWER priority/roadmap evidence into task, policy, review, or merge authority.

## Concurrency rule

Before every consequential FOUNDRY write:

1. re-read live `main`;
2. re-read current coordination evidence and the exact target PR/base/head;
3. verify the task is legitimately eligible for FOUNDRY and dependencies are accepted/stable;
4. stop if the target moved unexpectedly or another owner claimed it;
5. never force-push or overwrite another agent;
6. never reuse CI/review across a changed head/base;
7. make only the smallest task-authorized implementation or repair;
8. freeze at the review/integration boundary and leave an exact GitHub handoff.
