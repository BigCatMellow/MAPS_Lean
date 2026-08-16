# Task: TOWER current dispatch — 2026-08-16

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `TOWER`
- Risk: `MEDIUM`
- Goal: maintain a shared, evidence-backed multi-agent dispatch packet and working roadmap that tells each active MAPS lane what to do next, what to wait for, and what evidence releases downstream work, without changing canonical task/review/merge authority.

## Inputs and source of truth

- Inputs:
  - live `main` and relevant open PR/review/CI state;
  - `work/coordination/README.md`;
  - current agent coordination notes;
  - `playbook/ROADMAP_AND_PROJECTUPDATER.md`;
  - `templates/roadmap.md`;
  - `templates/task.md`;
  - live root-gate evidence for #30, #39, #44, #48 and coordination work #68/#70.
- Authoritative sources: live GitHub state and accepted MAPS state win over this task, roadmap, dispatch note, coordination snapshots, PR-body summaries, and chat history.
- Evidence labels:
  - `VERIFIED` = directly re-read from current repository/GitHub evidence during the checkpoint;
  - `REPORTED` = stated in a source but not mechanically reproduced by TOWER;
  - `UNKNOWN` = not safely established and assigned to the proper lane rather than guessed.
- Dependencies / preconditions: individual dispatch actions remain subject to existing task/PR authority, ownership, review independence, and integration gates.

## Change boundary

- MAY CHANGE:
  - `work/tasks/tower-current-dispatch-2026-08-16.md`;
  - `work/roadmaps/tower-current-dispatch-2026-08-16.md`;
  - `work/coordination/agents/TOWER-DISPATCH-2026-08-16.md`;
  - top-level coordination comments on relevant PR threads.
- MUST NOT CHANGE:
  - owner-controlled `ANVIL.md`, `FOUNDRY.md`, `SENTINEL.md`, `SWITCHYARD.md`;
  - runtime, tests, schemas, policies, feature branches, existing feature task records, or canonical project roadmaps;
  - canonical task lifecycle, ownership, review disposition, merge order, or merge state;
  - SENTINEL findings or SWITCHYARD integration gates.
- MAY CHANGE IF NECESSARY: only the three TOWER planning files above after live-state recovery. Any new repository path requires task amendment first.
- OPERATOR APPROVAL REQUIRED: material scope, priority, role, or consequential-authority change not already explicit in operator instructions/canonical rules.

## Decision authority

- Owner may decide: derived `NOW / NEXT / BLOCKED / PARKED` order from verified dependencies; which eligible lane should receive a coordination request; stop/resume wording; roadmap/checkpoint organization.
- Owner must escalate: conflicting canonical ownership, unresolved authority, material operator-intent ambiguity, or a priority/role decision that evidence cannot resolve.

## Acceptance criteria

- [x] A shared dated dispatch note gives ANVIL, FOUNDRY, SENTINEL, SWITCHYARD, and TOWER explicit next actions, dependencies, hold/resume conditions, required evidence, and handoffs.
- [x] A MAPS-format working roadmap records current reality, DONE/final proof, boundaries, backward plan, mission/checkpoint results, first wave, dependencies, phases, and re-plan triggers.
- [x] Queue changes are driven by live gate outcomes rather than the original dispatch order.
- [x] #30 is no longer incorrectly assigned to duplicate feature-head review after CLEAN IN-LAYER evidence appeared.
- [x] #39 is no longer incorrectly assigned to initial synchronization after SWITCHYARD produced exact synchronized-head evidence.
- [x] #44 remains at independent review until a repaired-head disposition exists.
- [x] #48 remains at current-main synchronization after verified CLEAN IN-LAYER feature review.
- [x] Downstream #41/#53, #45, and #49/#50 remain held behind accepted prerequisites.
- [x] TOWER's queue is explicitly derived and does not create task/review/merge authority.
- [x] Existing owner-controlled agent notes remain untouched by this branch.
- [x] PR #72 branch delta remains limited to the three TOWER planning/coordination Markdown files.

## Verification and evidence

- `main` re-read at checkpoint: `7269ce2be25993fa19b172f65c95381328585a35`.
- #30 re-read: head `7bae6d5758619a391c7551ee4589ea2d80d0a5b8`; CI #415 PASS; independent feature-head **CLEAN IN-LAYER** review found.
- #44 re-read: head `6f2b774eee27a0596820b12f080bfd7e60c0f50e`; CI #419 PASS; current owner review handoff found, no CLEAN repaired-head disposition found at checkpoint.
- #39 re-read: synchronized head `5928abe4550dbf7a75c2a2825e3cda5033ead830`; exact current main is reported merge base; CI #422 PASS; independent synchronized-head review remains next.
- #48 re-read: head `2f23959afff9525beada28993bad536878310b7f`; CI #392 PASS; SENTINEL **CLEAN IN-LAYER / NOT INTEGRATION-READY**.
- #70 repaired separately at `248aef12dff750ad53a1772942110c383202d738`, exact-head CI #435 PASS, independent re-review required.
- #68 received a TOWER coordination return because its permanent FOUNDRY planning-role proposal is superseded by newer operator intent; TOWER did not modify that branch.
- Review required for this packet: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Ordered procedure:
  1. recover live state;
  2. compare it to the current roadmap queue;
  3. record completed gates/checkpoint evidence;
  4. move only legitimately released work to NOW/NEXT;
  5. update the three TOWER files;
  6. verify exact branch delta;
  7. notify affected PR threads when dispatch materially changes;
  8. obtain independent review before integration of the TOWER packet.
- Failure branches:
  - IF `main` or a load-bearing root head moves THEN re-read and update affected facts before dispatch;
  - IF claimed review/CI cannot be bound to the exact head THEN mark the gate unproven rather than infer readiness;
  - IF a dispatch conflicts with canonical ownership/task state THEN canonical state wins and TOWER revises the queue;
  - IF an action would require TOWER to merge, independently approve, or rewrite another owner's branch THEN hand it to the proper role.
- Rollback / recovery: revert only this branch's TOWER planning files/comments; no feature/runtime rollback in scope.
- External side effects: repository coordination comments/files only; no deployment/release/merge by TOWER.
- Effort limit: refresh the queue if two current root heads move or a new interface-changing blocker invalidates multiple downstream assumptions.

## Stop / escalate

Stop rather than guess if live ownership conflicts, exact review/CI state is ambiguous, a new output path is required, or operator intent would materially change current priority/role architecture.

Escalate to: operator for material intent/priority/role choices; SENTINEL for independent review; SWITCHYARD for integration/merge safety; development owner for returned implementation defects.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Checkpoint decision: `CHANGE` — live evidence advanced two original first-wave gates, so the dispatch was revised instead of preserving stale assignments.
- #30: review complete -> SWITCHYARD integration.
- #39: synchronization complete -> independent synchronized-head review.
- #44: independent feature-head review still required.
- #48: SWITCHYARD current-main synchronization still required.
- Permanent coordination architecture remains TOWER planning/dispatch; ANVIL + FOUNDRY development; SENTINEL review; SWITCHYARD integration.
- PR #70 role/guidance repair and PR #68 owner reconciliation are tracked as coordination work and do not release downstream runtime branches by themselves.

## Completion / handoff

- Completed: initial dispatch, MAPS roadmap, root-gate checkpoint refresh, #70 delivery repair, #68 coordination return, and updated per-agent instructions.
- Not completed: current four root gates, independent review/integration of PR #72, #70 independent re-review/integration, #68 owner reconciliation.
- Current blocker for PR #72: independent review required before integration.
- Next action if not DONE: verify exact PR #72 delta/head after this checkpoint, update PR metadata/comments, then continue monitoring root gates from live evidence.