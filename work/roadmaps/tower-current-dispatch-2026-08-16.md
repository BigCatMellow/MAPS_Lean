# Roadmap: TOWER current multi-agent dispatch — 2026-08-16

- State: `WORKING`

## Current reality

### Checked facts

- `VERIFIED` — accepted `main` is now `c4c93e52edd961802c7c203035f0bc272f196b59` after PR #45 merged.
- `VERIFIED` — accepted foundations now include #30, #39, #44, #45, and #48.
- `VERIFIED` — #41 remains open at `6359e9246ef487d40fff60c2fb31b78067728fcb`; prior CI #480 passed on `main@eccdddaa...`, but SENTINEL-A returned `NOT READY — RESYNCHRONIZATION REQUIRED` because #45 moved accepted main during review. #53 stays blocked until actual #41 acceptance.
- `VERIFIED` — #49 remains historical at `ed865be729cf2d15663258fd46c9296ea32d28e7`; SWITCHYARD released the rebuild to FOUNDRY on accepted #48/A1. Current rebuild must also preserve newer accepted main, now including #45. #50 stays blocked until #49 acceptance.
- `VERIFIED` — #73 remains at `7434b08e9343750f5d860070fa4005bcbf2da1e3`; SENTINEL-C's CLEAN review on old base `eccdddaa...` is explicitly stale after #45 acceptance. SWITCHYARD must resynchronize before fresh merge-authoritative review.
- `VERIFIED` — #70 remains at `90c2d08ae3f45e176b914487401686f09021ab4f` and #71 at `cc8917b83c800863f8e3d8b6e0f34901f74b4d1b`; both old integration packets are based on `eccdddaa...` and must be re-evaluated/resynchronized against current main before a current merge-authoritative review.
- `VERIFIED` — #43 has a narrow scope-contract repair only; runtime semantics were independently clean. ANVIL explicitly declined ownership because no handoff binds it. #60 remains blocked until #43 acceptance.
- `VERIFIED` — #67/#68/#69 remain owner-controlled coordination freshness work.
- `VERIFIED` — #51/#52 remain planning/design only and create no runtime wait authority.

### Sources of truth

- root `AGENTS.md`;
- `work/coordination/README.md`;
- proposed PR #73 protocol until accepted;
- live GitHub PR/base/head/review/CI/comments;
- accepted MAPS state.

This roadmap is derived only and loses to those sources.

### Unknowns / decisions

- `UNKNOWN` — results of future current-main #41/#70/#71/#73 synchronized heads and reviews.
- `UNKNOWN` — whether #49 rebuild exposes integration defects.
- `UNKNOWN / OPERATOR BOUNDARY` — legitimate development continuity for #43 repair.

## Definition of DONE

This dispatch cycle is complete when:

1. #41 is synchronized on the latest accepted main and has exact CI/review/integration outcome;
2. #49 is genuinely rebuilt on accepted A1/latest main and has exact CI/review/integration evidence or a concrete blocker;
3. #70/#71/#73 have been re-grounded on current accepted main and moved through fresh review/integration gates;
4. downstream #53/#50 release only after actual upstream acceptance;
5. #43 is either explicitly assigned by legitimate authority or remains visibly blocked without invented ownership;
6. coordination owner-note work stays with its owners;
7. TOWER refreshes immediately on further material main movement.

## Boundaries

### In scope

- derived NOW/NEXT/BLOCKED/PARKED planning;
- dependency release conditions;
- role routing under existing authority;
- explicit unknown/ownership blockers;
- TOWER-owned planning files/comments.

### Out of scope

- feature/runtime implementation by TOWER;
- independent review by TOWER;
- synchronization/merge by TOWER;
- other agents' owner-controlled notes;
- assigning #43 without operator/canonical authority;
- speculative coordination machinery.

## Backward plan

1. Immediately before DONE, current dependency heads have exact proof and downstream releases reflect actual acceptance.
2. Before that, SWITCHYARD refreshes stale integration heads after each accepted main movement; SENTINEL reviews only immutable current packets; FOUNDRY rebuilds #49.
3. Before that, #45 acceptance advances main and invalidates old `eccdddaa...` packets.
4. Current state: integration refresh + #49 development are executable bottlenecks; #43 is an ownership bottleneck.

## Mission/checkpoint result

- Required: `YES` — TOWER re-read live state after #45 moved main.
- `ACCEPTED` — #45 is no longer an active review item; it is accepted foundation.
- `ACCEPTED` — #41 must return to SWITCHYARD resynchronization before fresh review.
- `ACCEPTED` — #73 prior CLEAN review is stale and grants no current merge authority.
- `ACCEPTED` — #70/#71 old integration packets must be refreshed against the new main before current merge-authoritative review.
- `ACCEPTED` — #49 remains valid parallel development work for FOUNDRY.
- `REJECTED` — reusing clean review/CI evidence across a changed accepted-main baseline as final merge authority.
- `REJECTED` — assigning #43 from idle capacity.

## First wave — current

- [ ] `TOWER-I1 / #41` — genuinely synchronize Stage-1 onto `main@c4c93e52...` or newer accepted main, prove exact delta, fresh Runtime CI, fresh independent review — Owner: `SWITCHYARD`
- [ ] `TOWER-D1 / #49` — genuinely rebuild A2 on accepted #48/A1 and latest accepted main, preserve newer accepted behavior, fresh CI/review/handoff — Owner: `FOUNDRY`
- [ ] `TOWER-I2 / #73` — resynchronize protocol layer after stale old-base CLEAN review, fresh CI/review — Owner: `SWITCHYARD`
- [ ] `TOWER-I3 / #70/#71` — re-ground stale old-base planning/coordination packets on latest accepted main before fresh review — Owner: `SWITCHYARD`
- [ ] `TOWER-I4 / whole backlog` — continuously consume clean returns and invalidate stale packets after merges — Owner: `SWITCHYARD`
- [ ] `TOWER-Q1 / queue watch` — refresh after material movement and release only from acceptance — Owner: `TOWER`

## Phase 0 — accepted foundations

- [x] #30 accepted.
- [x] #39 accepted.
- [x] #44 accepted.
- [x] #45 accepted.
- [x] #48 accepted.

## Phase 1 — product frontier

### Context Builder

- [ ] #41 current-main resynchronization.
- [ ] fresh exact-head CI + independent review.
- [ ] SWITCHYARD merge gate.
- [ ] Only after accepted #41: rebuild #53; preserve Stage-2 evaluation-only scope, strict source precision, exact `overlay_sha256`; fresh CI/review/integration.

### Execution lineage

- [ ] #49 FOUNDRY rebuild on accepted A1/latest main.
  - preserve accepted project-scoped run/session identity;
  - preserve helper/recovery authorities;
  - relationship evidence only;
  - exact delta + fresh CI + independent review + SWITCHYARD integration.
- [ ] Only after accepted #49: repair/rebuild #50 on accepted ancestry.

### Operational learning

- [ ] Resolve #43 development ownership from operator/canonical evidence.
- [ ] Owner performs bounded change-contract repair unless new evidence returns substantive defect.
- [ ] Fresh CI/review/integration.
- [ ] Only after accepted #43: rebuild/review/integrate #60.

## Phase 2 — coordination/protocol

- [ ] #73 resynchronize after #45 main movement; fresh CI and independent review; SWITCHYARD integration.
- [ ] #70 current-main re-grounding; fresh CI/review/integration.
- [ ] #71 current-main re-grounding; fresh CI/review/integration.
- [ ] #67 ANVIL owner-note freshness repair.
- [ ] #68 FOUNDRY owner-note freshness repair preserving FOUNDRY development role.
- [ ] #69 SENTINEL owner-note refresh.

## PARKED / design-only

- [ ] #51 exact task/run ↔ hcom event correlation design.
- [ ] #52 evidence-backed wait design stacked on #51.

No runtime communication-response wait inference from provider silence, timestamps, identity coincidence, text, or same-thread traffic.

## Checkpoints

### A — #41

- Current disposition: stale old-base packet / resynchronization required.
- Next proof: new exact head on latest main, exact delta, fresh CI, independent review.
- CLEAN + accepted -> release #53.

### B — #49

- Next proof: rebuilt exact head on accepted A1/latest main, intended A2 delta, fresh CI, independent review.
- CLEAN + accepted -> release #50.

### C — #73/#70/#71

- Current issue: prior integration baseline `eccdddaa...` is no longer current.
- Next proof: genuine latest-main synchronization, fresh exact-head evidence and independent review.

### D — #43 ownership

- Required evidence: explicit operator/canonical ownership handoff.
- No binding -> remain blocked; idle capacity is not permission.

## Re-plan immediately if

- `main` moves;
- #41/#49/#70/#71/#73 heads move;
- new exact review dispositions land;
- #43 ownership becomes explicit;
- an interface-changing defect appears;
- canonical state contradicts the plan.

## Core rule

**TOWER decides what is worth attempting next from the derived dependency view. SENTINEL decides whether reviewed evidence survives independent testing. SWITCHYARD decides what is safe to integrate. The operator resolves authority evidence cannot.**
