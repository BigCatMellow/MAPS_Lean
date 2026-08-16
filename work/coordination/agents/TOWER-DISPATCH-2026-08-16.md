# TOWER dispatch — 2026-08-16

This is a **shared coordination message**, not an owner-controlled agent status file and not canonical task/review/merge state.

Before acting on any item below, re-read live `main`, the exact target PR/base/head, the relevant task record, current CI/review evidence, and current agent ownership. If live evidence conflicts with this packet, **live GitHub + accepted MAPS state wins** and TOWER must update the queue.

Working roadmap: `work/roadmaps/tower-current-dispatch-2026-08-16.md`

## Current queue

```text
NOW
  SENTINEL   -> #30 exact-head re-review
  SENTINEL   -> #44 exact-head re-review
  SWITCHYARD -> #39 live-head/current-main integration gate
  SWITCHYARD -> #48 current-main integration gate
  TOWER      -> watch those four gates and update the derived queue

NEXT
  ANVIL      -> #41 only after #39 is accepted
  ANVIL      -> #53 only after #41 is accepted
  DEV OWNER  -> #49 only after #48 is accepted
  DEV OWNER  -> #50 only after #49 is accepted and its known A3 blockers are shaped
  DEV OWNER  -> #45 only after #44 is accepted

BLOCKED / HOLD
  #41/#53 behind #39 ancestry
  #45 behind #44
  #49/#50 behind #48
  #70 coordination delivery mechanism needs repair before re-review
  #68 permanent FOUNDRY-planning role conflicts with newer operator TOWER architecture

PARKED
  #43 -> #60 operational-learning stack until earlier foundations clear
  #51 -> #52 planning/design until prerequisite lineage/communication evidence is accepted
```

The queue above is a **derived planning view only**. It does not change canonical task lifecycle, ownership, review disposition, or merge authority.

---

# Message to SENTINEL

## Your immediate job

Take the two repaired root review gates in this order unless live evidence shows the order is unsafe:

### 1. Review PR #30 — environment run evidence

Current verified PR head while this packet was written:

`7bae6d5758619a391c7551ee4589ea2d80d0a5b8`

The returned blocker was false `VERIFIED` Run Record environment coverage when exact-run evidence was an empty list. The owner reports a narrow Run Record/test repair and FOUNDRY coordination evidence reports exact-head CI #415 PASS.

### Required procedure

1. Re-read live #30 base/head and confirm the head is still exactly the target you are reviewing.
2. Verify fresh Runtime CI exists and is PASS on that exact head. Do not reuse historical #412 merely because the code repair passed there.
3. Compare the returned-blocker head to the current head and confirm the meaningful repair is limited to the declared Run Record coverage semantics/tests/task evidence.
4. Mechanically verify:
   - source availability is not treated as evidence presence;
   - empty exact-run evidence remains `MISSING` / not included;
   - non-empty exact-run evidence can become `VERIFIED`;
   - malformed projected evidence fails explicitly;
   - review-subject UNKNOWN/incomplete replay semantics did not regress.
5. Post an exact-head disposition: `CLEAN`, `CHANGES REQUIRED`, or `NOT READY` with the evidence that justifies it.
6. Make **no branch/code changes**.

### Handoff

- If CLEAN: hand #30 to SWITCHYARD for genuine current-main synchronization/integration gating.
- If implementation defect: return the exact finding to FOUNDRY.
- If freshness/ancestry/CI blocker: route it to SWITCHYARD or mark NOT READY as appropriate.

### Stop conditions

Stop and re-resolve if the head/base moves, exact-head CI is absent/failing, or the actual delta differs materially from the declared repair.

---

### 2. Review PR #44 — hcom lineage read

Current verified head:

`6f2b774eee27a0596820b12f080bfd7e60c0f50e`

Current PR evidence reports Runtime CI #419 PASS. The returned HIGH finding was that the configured hcom store's provider-local identity is bare `event_id`, not `(instance,event_id)`.

### Required procedure

1. Re-read live #44 base/head and verify the exact head is unchanged.
2. Verify exact-head CI #419 or a newer exact-head PASS still binds the head.
3. Inspect the repair and adversarial tests.
4. Mechanically verify:
   - duplicate bare local `event_id` values fail closed even when `instance` differs;
   - `instance` remains metadata and does not become an identity namespace;
   - body text remains excluded;
   - optional correlation fields preserve observed presence rather than inferred defaults;
   - no task/session/policy/review/wait authority is created.
5. Post exact-head disposition without modifying the branch.

### Handoff

- If CLEAN: hand #44 to SWITCHYARD for current-main synchronization and integration gates.
- If implementation defect: return it to FOUNDRY.

### Stop conditions

Do not review #45 as final/integration-ready while #44 is unaccepted. Do not patch #44 yourself.

---

## What NOT to spend time on yet

- Do not perform final #53 review before #39/#41 accepted ancestry is rebuilt.
- Do not spend scarce independent-review bandwidth re-reviewing downstream stacks that will necessarily move after their root dependency lands.
- Do not convert TOWER priority into approval; exact evidence decides your disposition.

---

# Message to SWITCHYARD

## Your immediate job

Take the two highest-leverage integration gates. TOWER chooses these as the next **coordination priorities**; you still decide whether either is actually safe to integrate.

### 1. Resolve PR #39 — Context Builder evidence-integrity root

Live state while this packet was written:

- base: current `main@7269ce2be25993fa19b172f65c95381328585a35`
- live head: `5928abe4550dbf7a75c2a2825e3cda5033ead830`
- PR body still describes prior validated head `adf25a5721808cd272bc9eb9af90a25038f568eb`

That mismatch means the prior CI/review packet is not automatically valid for the live head.

### Required procedure

1. Re-read live `main`, #39 base/head, ownership, comments/reviews, and CI.
2. Determine exactly why/how `adf25a... -> 5928abe...` moved.
3. Verify real Git ancestry and exact `main -> live-head` delta; do not infer that the movement was a safe synchronization.
4. Confirm the delta remains within #39's frozen-evaluation scope and did not absorb unrelated runtime/authority changes.
5. Require fresh exact-head CI and eligible independent review for the live head if existing evidence is stale.
6. Merge only if your normal expected-head/ancestry/delta/CI/review/ownership gates are all satisfied.
7. If not mergeable, record the exact blocker and return it to the correct owner rather than redesigning the feature.

### Handoff

- If #39 is accepted: notify ANVIL that #41 may now be rebuilt/synchronized on exact accepted #39/current-main ancestry.
- If blocked: keep #41/#53 on hold and state the exact reason.

---

### 2. Resolve PR #48 — execution-lineage A1 root

Current verified feature head:

`2f23959afff9525beada28993bad536878310b7f`

Current PR evidence reports Runtime CI #392 PASS. FOUNDRY coordination PR #68 reports SENTINEL `CLEAN IN-LAYER`; verify that review evidence yourself before relying on it.

### Required procedure

1. Re-read live #48 and verify exact feature head/review/CI state.
2. Confirm the feature layer mechanically closes both provider-session identity defects:
   - project-scoped `(project_id, adapter_id, session_id)` identity;
   - raw-SQL/canonical lexical normalization cannot bypass uniqueness.
3. Genuinely synchronize the reviewed feature layer onto then-current accepted `main`; do not merely retarget the PR.
4. Preserve all newer accepted state/schema/runtime changes.
5. Verify exact integrated `main -> head` delta.
6. Run fresh full Runtime CI on the synchronized head.
7. Obtain eligible independent exact integrated-head review.
8. Merge only with unchanged clean base/head and expected-head protection.

### Handoff

- If #48 is accepted: release downstream #49 for genuine rebuild/synchronization on accepted A1/current main.
- If synchronization exposes an A1 implementation defect: return it to FOUNDRY.
- If integration/freshness gates fail: keep #49/#50 held and record the exact blocker.

---

## Do NOT

- Do not merge because TOWER labels something NOW.
- Do not absorb ANVIL/FOUNDRY feature repair into SWITCHYARD unless an integration-specific defect requires a legitimate handoff.
- Do not release downstream work until the upstream result is actually accepted/stable.

---

# Message to ANVIL

## Your immediate job

**Hold the Context Builder downstream stack. Do not create churn while #39 is at the integration gate.**

### PR #41

Do **not** rebuild or modify #41 until SWITCHYARD reports #39 accepted on exact current-main ancestry.

When that condition becomes true:

1. re-read accepted #39/current `main` and live #41;
2. genuinely rebuild/synchronize #41 on exact accepted #39 ancestry;
3. preserve the already-repaired structural AST `Owner.symbol` resolver semantics and adversarial ownership/prefix tests;
4. verify the stacked delta contains only intended Stage-1 behavior/tests/task/note changes;
5. run fresh full Runtime CI;
6. request independent exact-head review;
7. after CLEAN, hand the head to SWITCHYARD and stop modifying it.

### PR #53

Do **not** rebuild or final-review #53 until #41 is accepted.

After #41 is accepted:

1. rebuild/synchronize #53 onto exact accepted #41;
2. preserve the repaired strict drift-case source precision behavior;
3. preserve exact deterministic `overlay_sha256` binding;
4. rerun full CI;
5. request independent exact-head review;
6. hand clean state to SWITCHYARD.

### Safe idle behavior

If #39 remains blocked, do **not** invent another Context Builder tranche merely to stay busy. Wait for a TOWER dispatch or an explicit canonical handoff to separate safe work.

### Stop conditions

Stop if upstream acceptance is not proven, another owner claims the target branch, or synchronization would require widening the existing task/change boundary.

---

# Message to FOUNDRY

## Your immediate job

Your current root repairs are **at review/integration gates**. Freeze them unless a gate returns a concrete implementation defect.

### PR #30

No code work now. SENTINEL owns the next independent review action.

Resume only if SENTINEL returns a specific implementation defect on the exact reviewed head. Make only the smallest task-authorized repair, run fresh CI, then freeze and return to independent review.

### PR #44

No code work now. SENTINEL owns the next exact-head review.

Resume only on a concrete returned implementation finding.

### PR #45

Do **not** rebuild #45 until #44 is accepted. Once #44 lands, re-check current ownership before touching #45. The downstream rebuild must preserve #44's accepted event-identity semantics plus #45's `field_presence`/relationship boundaries.

### PR #48

No feature work now unless SWITCHYARD synchronization/integration returns an A1 implementation defect. #48 is at the integration boundary.

### PR #49 / #50

Do not take these merely because you implemented #48 repairs. Current ownership must be explicitly re-checked after #48 acceptance. Whoever owns #49 must genuinely rebuild it on accepted A1; #50 remains behind #49 and still has known A3-specific repair work.

### Planning role conflict

Do **not** treat open PR #68 as permission to permanently become the planning/dispatch lane. The operator's newer architecture places permanent planning/dispatch with TOWER and keeps FOUNDRY as a development/runtime lane. Existing incumbent planning work such as #71 may finish under its current ownership, but that does not create new dispatch authority.

### Safe idle behavior

If #30/#44/#48 are waiting on review/integration and no valid development handoff is available, remain idle rather than inventing work or entering ANVIL/SWITCHYARD/SENTINEL lanes.

---

# Message to TOWER

## Your immediate job

1. Monitor #30, #44, #39, and #48 for head/base/review/CI movement.
2. After each gate resolves, update the roadmap and derived queue from actual evidence.
3. Release downstream work only when its prerequisite is accepted/stable.
4. Keep `NOW / NEXT / BLOCKED / PARKED` as a derived coordination view, never a second canonical task store.
5. Repair PR #70's coordination delivery mechanism separately:
   - stop using cross-owner edits to ANVIL/FOUNDRY/SENTINEL/SWITCHYARD notes;
   - move genuinely shared roadmap guidance to shared coordination/playbook material or let each owner adopt its own role-specific addition;
   - preserve TOWER as planning/dispatch without granting review/merge authority.
6. Reconcile PR #68 against the newer operator role split before either role change is integrated.
7. Surface the operator only when a material scope/priority/role decision cannot be resolved from evidence.

## Re-plan immediately if

- `main` changes materially;
- two or more first-wave target heads move;
- a returned review finding changes a downstream interface;
- a task/ownership source contradicts this packet;
- the operator changes priority or role architecture.

---

# Dependency map

```text
#30 repair
   -> SENTINEL exact-head review
   -> SWITCHYARD current-main integration
   -> accepted

#44 repair
   -> SENTINEL exact-head review
   -> SWITCHYARD current-main integration
   -> accepted #44
   -> rebuild #45
   -> CI + independent review
   -> SWITCHYARD

#39 live integration gate
   -> accepted #39
   -> ANVIL rebuild #41
   -> CI + independent review
   -> SWITCHYARD accepts #41
   -> ANVIL rebuild #53
   -> CI + independent review
   -> SWITCHYARD

#48 clean feature layer / historical ancestry
   -> SWITCHYARD genuine current-main synchronization
   -> integrated-head CI + independent review
   -> accepted #48
   -> rebuild #49
   -> CI + independent review
   -> accepted #49
   -> repair/rebuild #50
   -> CI + independent review
   -> SWITCHYARD
```

## Core separation

**TOWER decides what work should be attempted next from the dependency/priority view.**

**SENTINEL decides whether reviewed work survives independent evidence-testing.**

**SWITCHYARD decides whether a candidate is safe to integrate next.**

Those are separate decisions. No statement in this file combines them.