# Roadmap: TOWER current multi-agent dispatch — 2026-08-16

- State: `WORKING`

## Current reality

### Checked facts

- `VERIFIED` — accepted `main` remained `7269ce2be25993fa19b172f65c95381328585a35` at this checkpoint.
- `VERIFIED` — coordination notes and this roadmap are derived coordination evidence; live GitHub + accepted MAPS state remain authoritative.
- `VERIFIED` — #30 exact feature head `7bae6d5758619a391c7551ee4589ea2d80d0a5b8` has Runtime CI #415 PASS and independent feature-head disposition **CLEAN IN-LAYER**; current-main integration is now the next gate.
- `VERIFIED` — #44 exact repaired feature head remains `6f2b774eee27a0596820b12f080bfd7e60c0f50e`, Runtime CI #419 PASS; a fresh owner handoff requests independent review of the bare-local-`event_id` identity repair. No CLEAN repaired-head disposition was found at this checkpoint.
- `VERIFIED` — #39 exact synchronized head is `5928abe4550dbf7a75c2a2825e3cda5033ead830` on exact current `main`; SWITCHYARD reports accepted main as exact merge base, intended four-file evaluation delta, and Runtime CI #422 PASS. It now requires independent synchronized-head review before final merge gating.
- `VERIFIED` — #48 exact feature head `2f23959afff9525beada28993bad536878310b7f` has Runtime CI #392 PASS and SENTINEL **CLEAN IN-LAYER / NOT INTEGRATION-READY**; SWITCHYARD must genuinely synchronize it to current main.
- `VERIFIED` — #41/#53 remain downstream of #39/#41; #45 remains downstream of #44; #49/#50 remain downstream of #48/#49.
- `VERIFIED` — #70 is repaired at `248aef12dff750ad53a1772942110c383202d738`: no other agent's owner-controlled file remains in its original-base delta; shared guidance moved to `work/coordination/ROADMAP_PARTICIPATION.md`; Runtime CI #435 PASS; independent re-review remains required.
- `VERIFIED` — #68 still proposes permanent FOUNDRY Planning / Control-Surface, but TOWER returned that proposal to its owner because newer operator intent establishes TOWER as permanent planning/dispatch and FOUNDRY as development/runtime implementation and repair.

### Evidence/source paths

- `work/coordination/README.md`
- `work/coordination/agents/TOWER-DISPATCH-2026-08-16.md`
- `playbook/ROADMAP_AND_PROJECTUPDATER.md`
- `templates/roadmap.md`
- `templates/task.md`
- live PR/review/CI evidence for #30, #39, #44, #48, #68, #70, #72 and downstream stacks

### Important assumptions / unknowns

- `UNKNOWN` — whether #44's repaired exact head will pass independent review; do not release #45 until accepted.
- `UNKNOWN` — whether synchronizing #48/#30 to then-current main will expose integration-specific defects; SWITCHYARD must prove the resulting exact heads.
- `UNKNOWN` — whether #39 synchronized head will receive a CLEAN independent disposition; #41 remains held until actual acceptance.

## Definition of DONE

- Finished result:
  - each active lane has one current evidence-backed action or wait condition;
  - root review/integration gates are resolved or converted into explicit blockers;
  - downstream work starts only from accepted upstream ancestry;
  - TOWER refreshes the queue after material evidence changes rather than preserving stale instructions.
- Final proof:
  1. #39 has an exact synchronized-head independent disposition and final integration outcome;
  2. #44 has an exact repaired feature-head disposition and, if clean, an integration outcome;
  3. #48 and #30 have exact current-main synchronization/CI/independent-review outcomes;
  4. downstream #41/#45/#49 are released only after their upstream is accepted;
  5. TOWER's source roadmap/dispatch reflects those outcomes.
- Who can perform/inspect final proof:
  - SENTINEL or another eligible reviewer for independent review;
  - SWITCHYARD for integration/merge safety;
  - TOWER for queue/roadmap reconciliation;
  - operator for material scope/priority/role decisions.

## Boundaries

- In scope: priority/dependency coordination, review/integration dispatch, holds/resume conditions, TOWER coordination cleanup, and evidence-based re-planning.
- Not doing: feature implementation by TOWER, merge by TOWER, independent approval by TOWER, edits to other agents' owner-controlled notes/branches, speculative new architecture, or busy work.
- Effort limit: refresh rather than continue if accepted main materially changes a load-bearing assumption or two current root heads move before their gates finish.
- Highest-risk unknown: integration effects when #48/#30 are rebuilt onto current accepted state/schema/runtime ancestry.

## Backward plan

1. Immediately before DONE: root gates have exact proof; downstream lanes are either released from accepted prerequisites or explicitly held; queue reflects actual outcomes.
2. Before that: independent reviews resolve #39/#44 and SWITCHYARD synchronizes #48/#30 with fresh integrated evidence.
3. Before that: exact feature/synchronized heads and clean-in-layer evidence are preserved without downstream churn.
4. Current state: coding is not the principal bottleneck; review and integration proof are.

## Mission meeting / checkpoint result

- Required: `YES` — completed as a TOWER evidence refresh.
- Assumptions accepted/rejected:
  - `ACCEPTED` — #30's feature-head review gate is complete; repeating it would waste independent-review bandwidth.
  - `ACCEPTED` — #39's synchronization gate is complete; it now needs independent integrated-head review rather than further SWITCHYARD branch work.
  - `ACCEPTED` — #44 still needs feature-head review.
  - `ACCEPTED` — #48 still needs genuine current-main synchronization.
  - `REJECTED` — the original first-wave queue remains correct after gate movement.
  - `REJECTED` — downstream agents should start early merely because root implementation looks stable.
- Operator decisions needed: none for this checkpoint.
- Roadmap change: move #30 from SENTINEL review to SWITCHYARD integration; move #39 from SWITCHYARD synchronization to SENTINEL integrated-head review; retain #44 review and #48 synchronization.

## First wave — current

- [ ] `TOWER-R1 / PR #39 synchronized review` — independently verify exact `main@7269ce2... -> 5928abe...`, CI #422, intended four-file delta, preserved CBI-010 authority boundary, and issue exact-head disposition without modifying branch — Owner: `SENTINEL`
- [ ] `TOWER-R2 / PR #44 feature review` — independently verify exact `6f2b774e...`, CI #419, bare local event-ID uniqueness, body-free/UNKNOWN/authority boundaries, and issue exact-head disposition — Owner: `SENTINEL`
- [ ] `TOWER-I1 / PR #48 synchronization` — genuinely synchronize independently reviewed A1 feature layer `2f23959...` onto current main, preserve accepted state/schema behavior, run fresh CI, and request integrated-head independent review — Owner: `SWITCHYARD`
- [ ] `TOWER-I2 / PR #30 synchronization` — genuinely synchronize CLEAN feature layer `7bae6d...` onto current main, preserve accepted state/schema/Run Record behavior, run fresh CI, and request integrated-head independent review — Owner: `SWITCHYARD`
- [ ] `TOWER-Q1 / queue watch` — update source roadmap/dispatch immediately after any gate resolves and release downstream work only after actual acceptance — Owner: `TOWER`

## Phase 0 — Root gates

- [x] #30 feature-head blocker repair + exact-head CI + independent CLEAN IN-LAYER review.
- [ ] #30 current-main synchronization + integrated CI/review + final integration.
- [ ] #44 exact repaired feature-head independent review.
- [ ] #44 current-main synchronization/integrated review after CLEAN feature review.
- [x] #39 current-main synchronization + exact synchronized-head CI.
- [ ] #39 independent synchronized-head review + final merge gate.
- [x] #48 exact repaired feature-head independent CLEAN IN-LAYER review.
- [ ] #48 current-main synchronization + integrated CI/review + final integration.

## Phase 1 — Downstream usable slices

### Context Builder

- [ ] After accepted #39, ANVIL rebuilds/synchronizes #41 on exact accepted ancestry.
  - [ ] preserve exact AST `Owner.symbol` semantics and adversarial ownership/prefix tests;
  - [ ] fresh Runtime CI;
  - [ ] independent exact-head review;
  - [ ] SWITCHYARD integration.
- [ ] After accepted #41, ANVIL rebuilds #53.
  - [ ] preserve strict drift-case source precision and exact `overlay_sha256` identity;
  - [ ] fresh CI/review/integration.

### Communication lineage

- [ ] After accepted #44, rebuild #45 on exact accepted #44/current-main ancestry.
  - [ ] preserve `field_presence`, body-free lineage, and exact relationship semantics;
  - [ ] fresh CI/review/integration.

### Execution lineage

- [ ] After accepted #48, explicitly resolve owner and rebuild #49 on exact accepted A1/current main.
  - [ ] preserve A1 project-scoped session identity and SQLite normalization;
  - [ ] add only A2 helper/recovery relationships;
  - [ ] fresh CI/review/integration.
- [ ] After accepted #49, repair/rebuild #50.
  - [ ] mechanically seal omitted/UNKNOWN submission attribution against retroactive explicit attachment;
  - [ ] preserve valid active-legacy gate semantics while removing the invalid runtime token that caused the historical failure;
  - [ ] fresh CI/review/integration.

## Phase 2 — Coordination architecture

- [x] Repair #70 delivery so shared roadmap guidance no longer modifies ANVIL/FOUNDRY/SENTINEL/SWITCHYARD owner-controlled notes.
- [x] Move role-specific roadmap guidance into shared `work/coordination/ROADMAP_PARTICIPATION.md` on #70.
- [x] Return #68's superseded permanent FOUNDRY planning-role proposal to its owner without modifying that branch.
- [ ] Independently re-review exact repaired #70 head; if clean, SWITCHYARD performs current-main reconciliation/integration.
- [ ] Owner of #68 revises/replaces it to preserve FOUNDRY development role while retaining useful incumbent handoff facts.
- [ ] Allow incumbent FOUNDRY planning work such as #71 to finish or hand off without creating permanent dispatch authority.

## Explicit holds

- `ANVIL`: #41 held until #39 accepted; #53 held until #41 accepted.
- `FOUNDRY`: #44 held during review; #30/#48 held unless integrated review returns an implementation defect; #45 held until #44 accepted.
- `SENTINEL`: never patch branches being independently reviewed; return defects to owner.
- `SWITCHYARD`: roadmap priority is not merge authority; exact ancestry/delta/CI/review/ownership remain required.
- `TOWER`: no feature branches, no other agents' owner files, no merge/review authority.

## Checkpoints

### Checkpoint A — #39 disposition

- Evidence: exact synchronized base/head, CI #422, independent review.
- Decision: `CONTINUE | CHANGE | STOP`.
- If CLEAN and merged: release #41.
- If defect: route exact defect and keep #41/#53 held.

### Checkpoint B — #44 disposition

- Evidence: exact repaired feature head, CI #419, bare-ID review.
- Decision: `CONTINUE | CHANGE | STOP`.
- If CLEAN: release SWITCHYARD synchronization, not #45 yet.
- If defect: return to FOUNDRY and keep #45 held.

### Checkpoint C — #48 integrated result

- Evidence: synchronized exact delta, state/schema compatibility, CI, independent review, merge result.
- Decision: `CONTINUE | CHANGE | STOP`.
- If accepted: resolve owner and release #49.
- If blocked: keep #49/#50 held.

### Checkpoint D — #30 integrated result

- Evidence: synchronized exact delta, Run Record/environment semantics, CI, independent review, merge result.
- Decision: `CONTINUE | CHANGE | STOP`.
- No downstream branch is released directly, but accepted environment evidence becomes foundation for later work.

### Checkpoint E — coordination role integration

- Evidence: #70 independent review; #68 owner reconciliation; exact current role files/branches.
- Decision: `CONTINUE | CHANGE | STOP`.
- Requirement: one permanent planning/dispatch owner (TOWER), one independent review role (SENTINEL), one integration role (SWITCHYARD), development lanes ANVIL/FOUNDRY, no duplicate authority.

## Re-plan immediately if

- current `main` changes a load-bearing dependency;
- any root head moves unexpectedly;
- review exposes an interface-changing defect;
- ownership changes;
- canonical task state contradicts this plan;
- the operator changes priority, scope, or role architecture.

## Core rule

**TOWER decides what is worth attempting next. SENTINEL decides whether reviewed evidence survives independent testing. SWITCHYARD decides what is safe to integrate.**