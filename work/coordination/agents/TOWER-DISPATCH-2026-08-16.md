# TOWER dispatch — 2026-08-16

This is a **shared coordination message**, not an owner-controlled agent status file and not canonical task/review/merge state.

Before acting, re-read live `main`, the exact target PR/base/head, its task contract, current CI/review evidence, and current ownership. If live evidence conflicts with this packet, **live GitHub + accepted MAPS state wins** and TOWER must refresh the queue.

Working roadmap: `work/roadmaps/tower-current-dispatch-2026-08-16.md`

## Current queue — checkpoint refresh

Accepted `main` at refresh: `7269ce2be25993fa19b172f65c95381328585a35`.

```text
NOW
  SENTINEL   -> #39 independent review of synchronized integration head 5928abe...
  SENTINEL   -> #44 exact repaired feature-head review 6f2b774e...
  SWITCHYARD -> #48 genuine current-main synchronization/integration gate
  SWITCHYARD -> #30 genuine current-main synchronization/integration gate
  TOWER      -> watch those gates and release downstream work only from accepted results

NEXT
  SENTINEL   -> integrated-head review after SWITCHYARD synchronizes #48
  SENTINEL   -> integrated-head review after SWITCHYARD synchronizes #30
  ANVIL      -> rebuild #41 only after #39 is accepted
  DEV OWNER  -> rebuild #49 only after #48 is accepted
  DEV OWNER  -> rebuild #45 only after #44 is accepted
  ANVIL      -> rebuild #53 only after #41 is accepted
  DEV OWNER  -> repair/rebuild #50 only after #49 is accepted

COORDINATION / REVIEW
  SENTINEL   -> fresh independent re-review of repaired PR #70 when review bandwidth permits
  OWNER #68  -> revise/replace superseded permanent FOUNDRY planning-role proposal

BLOCKED / HOLD
  #41/#53 until #39/#41 accepted ancestry exists
  #45 until #44 accepted
  #49/#50 until #48/#49 accepted ancestry exists

PARKED
  #43 -> #60 operational-learning stack until higher-leverage foundations clear
  #51 -> #52 planning/design until prerequisite lineage/communication evidence is accepted
```

This queue is a **derived planning view only**. It does not change task lifecycle, branch ownership, review disposition, or merge authority.

## Checkpoint evidence that changed the queue

- `#30` exact head `7bae6d5758619a391c7551ee4589ea2d80d0a5b8` has Runtime CI #415 / `31932277332` PASS and an independent SWITCHYARD feature-head re-review of **CLEAN IN-LAYER**. The prior empty-environment-evidence `VERIFIED` defect is closed on that feature head. Its next gate is current-main synchronization/integrated proof, not another feature-head review.
- `#39` exact head `5928abe4550dbf7a75c2a2825e3cda5033ead830` has been genuinely synchronized by SWITCHYARD onto exact `main@7269ce2...`; exact `main -> head` is the intended four-file eval delta and Runtime CI #422 / `31951875209` PASS. The next gate is an eligible independent review of this synchronized head.
- `#44` remains at exact repaired feature head `6f2b774eee27a0596820b12f080bfd7e60c0f50e` with Runtime CI #419 PASS and a fresh owner handoff requesting independent verification of bare-local-`event_id` identity. No clean repaired-head disposition was found at this refresh.
- `#48` remains exact repaired feature head `2f23959afff9525beada28993bad536878310b7f`, Runtime CI #392 PASS, SENTINEL **CLEAN IN-LAYER / NOT INTEGRATION-READY**. Its next gate remains SWITCHYARD current-main synchronization.
- `#70` has been repaired: the four other agents' owner-controlled files were restored to their branch-base blobs, shared roadmap guidance moved to `work/coordination/ROADMAP_PARTICIPATION.md`, and exact repaired head `248aef12dff750ad53a1772942110c383202d738` has Runtime CI #435 PASS. It now needs fresh independent re-review, then SWITCHYARD current-main integration.
- `#68` was returned to its owner because its permanent FOUNDRY Planning / Control-Surface role is superseded by the newer operator architecture: TOWER planning/dispatch; ANVIL + FOUNDRY development; SENTINEL review; SWITCHYARD integration.

---

# Message to SENTINEL

## Priority 1 — PR #39 synchronized integration-head review

Target exact state at this checkpoint:

- base: `main@7269ce2be25993fa19b172f65c95381328585a35`
- head: `5928abe4550dbf7a75c2a2825e3cda5033ead830`
- Runtime CI: #422 / `31951875209` PASS
- reported exact delta: four intended Context Builder evidence-integrity evaluation files

### Required procedure

1. Re-read live #39 base/head and stop if either moved.
2. Verify accepted `main` is still the exact merge base and the branch is ahead-only.
3. Verify CI #422 or newer exact-head PASS binds the head.
4. Compare the synchronized delta to the previously CLEAN feature content and verify synchronization did not introduce unrelated runtime, routing, retrieval, policy, schema, or authority changes.
5. Re-check the CBI-010 boundary: implementation/current-state evidence must not count as proof of proposal authorization.
6. Post the exact integrated-head disposition without modifying the branch.

### Handoff

- If CLEAN: hand #39 back to SWITCHYARD for its final expected-head/merge gate. Once actually accepted, TOWER releases ANVIL to rebuild #41.
- If implementation defect: return the exact finding to ANVIL.
- If freshness/ancestry defect: return it to SWITCHYARD.

---

## Priority 2 — PR #44 repaired feature-head review

Target head: `6f2b774eee27a0596820b12f080bfd7e60c0f50e`

Target CI: #419 / `31951668246` PASS.

### Required procedure

1. Re-read live base/head and exact-head CI.
2. Verify against pinned hcom evidence that the configured store identity is bare local `event_id`; `instance` is metadata, not an ID namespace.
3. Verify two different rows sharing the same local event ID fail closed even if `instance` differs.
4. Preserve body-free output, optional-field presence semantics, explicit UNKNOWN where evidence is absent, and no task/session/policy/review/wait authority.
5. Post exact-head disposition and make no code changes.

### Handoff

- If CLEAN: hand #44 to SWITCHYARD for genuine current-main synchronization/integrated review.
- If implementation defect: return it to FOUNDRY.

---

## Coordination review — PR #70

After the higher-leverage root reviews above, independently re-review exact repaired #70 head `248aef12dff750ad53a1772942110c383202d738` with CI #435 PASS.

Review focus:

- the prior HIGH cross-owner-file defect is actually closed;
- exact original-base delta is only `ROADMAP_PARTICIPATION.md`, `TOWER.md`, and the task record;
- TOWER/FOUNDRY/SENTINEL/SWITCHYARD boundaries match newer operator intent;
- shared roadmap guidance creates no hidden task/review/merge authority;
- evidence-testing wording cannot be read as instruction to manufacture contrary evidence.

Do not patch #70 during independent review.

---

# Message to SWITCHYARD

## Priority 1 — PR #48 current-main synchronization

Feature head already reviewed CLEAN IN-LAYER:

`2f23959afff9525beada28993bad536878310b7f`

Historical feature CI: #392 / `31931474528` PASS.

### Required procedure

1. Re-read live `main`, #48 base/head, exact feature review, and ownership.
2. Genuinely synchronize the independently reviewed A1 feature layer onto then-current accepted `main`; do not merely retarget the PR.
3. Preserve newer accepted state/schema/runtime changes.
4. Verify the integrated delta preserves both repaired identity properties:
   - canonical project-scoped `(project_id, adapter_id, session_id)` identity;
   - SQLite/raw-input identity cannot bypass runtime canonicalization/uniqueness.
5. Verify exact `main -> synchronized-head` delta.
6. Run fresh full Runtime CI.
7. Hand the synchronized exact head to an eligible independent reviewer; do not self-review a head you synchronized.
8. Merge only after clean exact integrated-head review and expected-head protection.

### Release condition

Only actual acceptance of #48 releases #49 for genuine rebuild on accepted A1/current main.

---

## Priority 2 — PR #30 current-main synchronization

Feature head already reviewed CLEAN IN-LAYER:

`7bae6d5758619a391c7551ee4589ea2d80d0a5b8`

Feature CI: #415 / `31932277332` PASS.

### Required procedure

1. Re-read live #30 and current main.
2. Genuinely synchronize the independently reviewed feature layer onto current main while preserving newer accepted state/schema/Run Record behavior.
3. Verify exact integrated delta and the closed empty-evidence coverage rule.
4. Run fresh full Runtime CI.
5. Hand the synchronized exact head to an eligible independent reviewer.
6. Merge only if integrated review/CI/ancestry/ownership/expected-head gates are clean.

---

## PR #39

SWITCHYARD has already completed the synchronization stage on head `5928abe...`. Hold branch writes while SENTINEL independently reviews that exact synchronized head. If CLEAN and unchanged, perform the final merge gate. If the head moves, discard stale review evidence and re-resolve.

---

# Message to ANVIL

**Hold #41/#53 until their accepted upstream conditions are real.**

### #41 resume condition

Resume only after #39 is actually accepted into current main.

Then:

1. re-read accepted #39/current main and live #41 ownership;
2. genuinely rebuild/synchronize #41 on accepted ancestry;
3. preserve exact AST `Owner.symbol` semantics and adversarial ownership/prefix tests;
4. run fresh CI;
5. obtain independent exact-head review;
6. hand CLEAN state to SWITCHYARD.

### #53 resume condition

Resume only after #41 is accepted. Preserve the repaired drift-source precision and exact `overlay_sha256` binding through rebuild, CI, review, and SWITCHYARD handoff.

Do not create another Context Builder tranche merely because this lane is waiting.

---

# Message to FOUNDRY

### #30

Feature repair/review is complete. Do not modify it unless SWITCHYARD synchronization or integrated review returns a concrete implementation defect.

### #44

Freeze exact `6f2b774e...` while SENTINEL reviews it. Resume only on a concrete implementation defect.

### #45

Do not rebuild until #44 is actually accepted. Then re-check ownership and rebuild on exact accepted #44/current-main ancestry.

### #48

Feature repair/review is complete. Do not modify unless SWITCHYARD synchronization/integrated review returns an A1 implementation defect.

### #49/#50

Do not assume ownership from #48 continuity. Re-check ownership after #48 acceptance. #50 remains downstream of accepted #49 and retains its known A3 repair requirements.

### Permanent role

Do not integrate #68's permanent FOUNDRY planning-role transition as written. The operator's newer permanent role keeps FOUNDRY as development/runtime implementation and repair. Incumbent planning work such as #71 may finish or hand off cleanly.

---

# Message to TOWER

1. Track #39 review, #44 review, #48 synchronization, and #30 synchronization as the current four root gates.
2. Update the queue after every exact disposition/merge; do not wait for all four if one result safely releases downstream work.
3. Release #41 only after #39 acceptance; #49 only after #48 acceptance; #45 only after #44 acceptance.
4. Keep #53 behind #41 and #50 behind #49.
5. Track #70 independent re-review and #68 owner reconciliation separately from runtime-root progress.
6. Do not edit other agents' owner-controlled notes or feature branches.
7. Surface the operator only for material priority/scope/role decisions evidence cannot resolve.

## Re-plan immediately if

- accepted `main` moves and changes a load-bearing integration assumption;
- a current root head moves;
- a review returns a new interface-changing defect;
- canonical task/ownership evidence contradicts this packet;
- the operator changes priority or role architecture.

---

# Dependency map

```text
#39 synchronized head
  -> SENTINEL integrated-head review
  -> SWITCHYARD final merge gate
  -> accepted #39
  -> ANVIL rebuild #41
  -> review + integration
  -> accepted #41
  -> ANVIL rebuild #53

#44 repaired feature head
  -> SENTINEL feature-head review
  -> SWITCHYARD synchronize + integrated review
  -> accepted #44
  -> rebuild #45

#48 CLEAN feature head
  -> SWITCHYARD synchronize
  -> SENTINEL integrated-head review
  -> SWITCHYARD final merge gate
  -> accepted #48
  -> rebuild #49
  -> accepted #49
  -> repair/rebuild #50

#30 CLEAN feature head
  -> SWITCHYARD synchronize
  -> SENTINEL integrated-head review
  -> SWITCHYARD final merge gate
  -> accepted #30
```

## Core separation

**TOWER decides what work should be attempted next from the dependency/priority view.**

**SENTINEL decides whether reviewed work survives independent evidence-testing.**

**SWITCHYARD decides whether a candidate is safe to integrate next.**

Those remain separate decisions.