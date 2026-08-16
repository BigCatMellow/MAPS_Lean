# FOUNDRY — Development / Runtime Implementation and Repair

Snapshot: 2026-08-16 15:25 America/New_York

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

`fc523891d069d5e4c668f4eda0ab3cb86aa3f714`

Relevant accepted work includes:

- PR #57 — Operator Intent Compiler request shaping;
- PR #39 — Context Builder frozen evidence-integrity foundation;
- PR #30 — append-only run environment evidence.

## Active owned coordination repair

### PR #68 — Reconcile FOUNDRY role coordination

- Branch: `coord/foundry-planning-20260816`.
- TOWER returned the prior permanent Planning / Control-Surface transition because the newer operator architecture assigns permanent planning/dispatch to TOWER and keeps FOUNDRY as a development/repair lane.
- This repair changes only `work/coordination/agents/FOUNDRY.md` and preserves useful incumbent handoff facts without creating planning, review, integration, or merge authority.
- After this exact-head repair is verified, FOUNDRY freezes the branch for independent review and SWITCHYARD integration.

## Incumbent implementation handoffs

These branches were implemented or repaired by this FOUNDRY continuity and therefore remain ineligible for self-review.

### PR #30 — Append-only run environment evidence

- Final synchronized head `4e158f65a422f14d7d12b2b1b8b0297e9f3ca5d7`.
- Runtime CI #442 PASS plus SENTINEL CLEAN integrated-head review.
- State: **ACCEPTED / FOUNDRY OWNERSHIP ENDED**.

### PR #44 — Full-fidelity hcom lineage read

- Repaired feature head `6f2b774eee27a0596820b12f080bfd7e60c0f50e`.
- Runtime CI #419 PASS.
- SENTINEL: **CLEAN IN-LAYER / FEATURE-HEAD ONLY / NOT INTEGRATION-READY**.
- State: **FROZEN / HANDED TO SWITCHYARD FOR CURRENT-MAIN SYNCHRONIZATION**.
- FOUNDRY must not modify this head unless review/integration returns a concrete implementation defect.

### PR #45 — Exact hcom message relationships

- Head `b78de03a9e05fe19846d0c0629a55e54427fa587`.
- Runtime CI #346 PASS.
- SENTINEL: **CLEAN IN-LAYER / NOT INTEGRATION-READY**.
- State: **FROZEN / BLOCKED UPSTREAM** until #44 is accepted; then the stack must be rebuilt/synchronized and re-verified by the appropriate owner/integration lane.

### PR #48 — Adapter-qualified run/session lineage A1

- Repaired feature head `2f23959afff9525beada28993bad536878310b7f`.
- Runtime CI #392 PASS.
- SENTINEL: **CLEAN IN-LAYER / FEATURE-HEAD ONLY / NOT INTEGRATION-READY**.
- State: **FROZEN / HANDED TO SWITCHYARD FOR CURRENT-MAIN SYNCHRONIZATION**.
- Acceptance of #48 is the release condition for downstream #49 rebuild work; CLEAN IN-LAYER alone does not release it.

## Other current dependency lanes

- **#41 / #53 — Context Builder:** #39 is accepted. #41 remains a clean feature layer requiring integration/rebuild gates; #53 remains downstream until #41 acceptance. FOUNDRY has no ownership claim.
- **#49 / #50 — execution lineage downstream:** #49 waits for accepted #48. #50 remains downstream and retains its known A3 repair requirements. FOUNDRY does not claim these branches without an explicit eligible handoff.
- **#43 / #60 — operational learning:** observation only for this lane unless a concrete implementation task is returned and ownership is re-checked.
- **#51 / #52 — communication/wait design:** planning-only evidence; not a FOUNDRY implementation claim.
- **#71 — capability-roadmap reconciliation:** incumbent FOUNDRY-authored planning work is frozen at `7a58f484614e1ed6452af279458e31afc53ae826` and handed to SWITCHYARD for synchronization. Incumbent authorship does not give FOUNDRY permanent planning/dispatch authority.

## Current eligibility

After the PR #68 coordination repair, there is no separate feature/runtime implementation task currently released to FOUNDRY by the live dependency state recovered for this session:

- #44 and #48 are already clean feature layers at the integration boundary;
- #45 remains blocked on accepted #44;
- #49 remains blocked on accepted #48;
- #30 is accepted;
- other active development stacks are owned elsewhere or have not been explicitly released to FOUNDRY.

FOUNDRY therefore remains idle after handing off this coordination repair unless live GitHub evidence returns a concrete implementation defect or releases a new eligible task.

## Explicit non-ownership

FOUNDRY will not:

- edit another agent's coordination file;
- self-approve work it authored or repaired;
- perform SWITCHYARD synchronization/merge work merely because an implementation dependency became ready;
- modify #44/#45/#48 while another lane is reviewing or integrating them;
- claim ANVIL-owned development work without a real handoff;
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
