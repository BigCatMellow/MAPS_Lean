# Roadmap: TOWER current multi-agent dispatch — 2026-08-16

- State: `WORKING`

## Current reality

### Checked facts

- `VERIFIED` — accepted `main` was re-read at `7269ce2be25993fa19b172f65c95381328585a35` while shaping this roadmap.
- `VERIFIED` — `work/coordination/README.md` says coordination notes are not canonical task/review/policy/repository state, live GitHub and accepted MAPS state win, and agents should normally edit only their own status file.
- `VERIFIED` — current `main` contains four owner-controlled coordination notes: ANVIL, FOUNDRY, SENTINEL, SWITCHYARD. Those snapshots contain stale historical details and therefore are inputs, not final authority.
- `VERIFIED` — PR #30 is open at `7bae6d5758619a391c7551ee4589ea2d80d0a5b8`; its returned Run Record empty-evidence coverage blocker is described as repaired, and its PR body requires an independent exact-head review before SWITCHYARD current-main integration.
- `REPORTED` — FOUNDRY coordination PR #68 reports Runtime CI #415 PASS on exact #30 head `7bae6d57...`; the independent reviewer must verify that exact-head CI evidence rather than trusting this roadmap.
- `VERIFIED` — PR #44 is open at `6f2b774eee27a0596820b12f080bfd7e60c0f50e`; its bare provider-local `event_id` uniqueness repair is present, exact-head Runtime CI #419 is reported PASS in the PR body, and the PR explicitly requires independent re-review before integration.
- `VERIFIED` — PR #39 is open against current `main`, but its live head is `5928abe4550dbf7a75c2a2825e3cda5033ead830` while the PR body still names `adf25a5721808cd272bc9eb9af90a25038f568eb` as the validated head. Therefore the old CI/review packet cannot be treated as exact-head evidence for the live head.
- `VERIFIED` — PR #48 is open at `2f23959afff9525beada28993bad536878310b7f`; exact-head Runtime CI #392 is reported PASS in its PR body, and the branch remains historical relative to current `main`, requiring genuine synchronization before merge.
- `REPORTED` — FOUNDRY coordination PR #68 reports #48 is SENTINEL `CLEAN IN-LAYER` and handed to SWITCHYARD. SWITCHYARD must verify the exact review evidence and eligibility before acting.
- `VERIFIED` — #45 remains downstream of #44; #41/#53 remain downstream of #39; #49/#50 remain downstream of #48. Their own PR descriptions/review records require rebuild/synchronization after accepted upstream ancestry rather than blind retargeting.
- `VERIFIED` — PR #68 proposes permanent FOUNDRY Planning / Control-Surface ownership. This conflicts with the operator's newer TOWER architecture, under which TOWER owns planning/dispatch while FOUNDRY remains a development/runtime lane. PR #68 must not be treated as silently authoritative over the newer operator direction.
- `VERIFIED` — PR #70 is open and introduces TOWER but still modifies all four owner-controlled agent notes. Existing SENTINEL review found that delivery mechanism violates the low-contention ownership rule. This dispatch roadmap does not depend on #70 being integration-ready.

### Evidence/source paths

- `work/coordination/README.md`
- `work/coordination/agents/ANVIL.md`
- `work/coordination/agents/FOUNDRY.md`
- `work/coordination/agents/SENTINEL.md`
- `work/coordination/agents/SWITCHYARD.md`
- `playbook/ROADMAP_AND_PROJECTUPDATER.md`
- `templates/roadmap.md`
- `templates/task.md`
- live GitHub PR state for #30, #39, #44, #48, #68, #70 and their referenced downstream PRs

### Important assumptions / unknowns

- `UNKNOWN` — why PR #39 moved from its previously reviewed/validated head to live head `5928abe...`; SWITCHYARD must inspect exact ancestry/delta rather than infer that the movement was safe synchronization.
- `UNKNOWN` — whether every review/CI gate reported in coordination prose still binds the exact current head at execution time; each assigned lane must re-read exact live state immediately before acting.
- `ASSUMED` — the operator wants maximum safe forward progress rather than preserving agent utilization for its own sake. This is consistent with the explicit request to identify who is waiting on what and tell agents what to do next.

## Definition of DONE

- Finished result:
  - every active agent can read one shared TOWER dispatch packet and know its immediate action, what not to touch, what prerequisite it is waiting on, the exact condition that resumes work, and who receives the handoff next;
  - the current high-leverage review/integration gates are resolved or converted into explicit evidence-backed blockers;
  - downstream development resumes only after its accepted upstream dependency is stable;
  - the roadmap is refreshed when live evidence invalidates the current queue.
- Final proof:
  1. SENTINEL has posted exact-head dispositions for the first-wave review targets (#30 and #44), or explicitly records why either is not review-ready;
  2. SWITCHYARD has produced exact-state integration decisions for #39 and #48, including live ancestry/delta, exact-head CI/review status, and merge/hold outcome under its own authority;
  3. no downstream owner has modified #41/#53, #45, or #49/#50 ahead of its required accepted upstream condition unless a new canonical handoff explicitly reshapes that work;
  4. TOWER updates this roadmap/dispatch from the resulting evidence rather than treating the original queue as permanent truth.
- Who can perform/inspect final proof:
  - SENTINEL for independent review dispositions;
  - SWITCHYARD for integration safety and merge decisions;
  - TOWER for derived queue/roadmap reconciliation;
  - operator for material priority/scope/role decisions.

## Boundaries

- In scope:
  - current multi-agent priority/dependency view;
  - specific review/integration dispatch for #30, #44, #39, #48;
  - hold/resume conditions for #41/#53, #45, #49/#50;
  - TOWER's own coordination cleanup around #68/#70;
  - evidence-driven checkpoints and re-planning.
- Not doing:
  - no feature/runtime implementation;
  - no merge by TOWER;
  - no independent review by TOWER where reviewer independence is required;
  - no edits to other agents' owner-controlled coordination notes;
  - no canonical task lifecycle or review-state changes merely from this roadmap;
  - no speculative new architecture or busy work to keep an agent occupied.
- Effort limit: if `main` changes materially or two or more first-wave target heads move before the first-wave gates are acted on, pause and refresh this roadmap instead of continuing from stale state.
- Highest-risk unknown: exact current integration/review freshness of live #39 and the exact review eligibility/status that SWITCHYARD must verify for #48.

## Backward plan

Work backward from a clean, stable queue rather than from whichever branch looks easiest to modify.

1. Immediately before DONE:
   - first-wave gates have exact current evidence;
   - downstream stacks have either resumed from accepted prerequisites or remain explicitly held;
   - TOWER has reconciled the queue to those outcomes.
2. Before that:
   - SENTINEL independently resolves the repaired root review gates #30 and #44;
   - SWITCHYARD independently resolves current-main integration gates for #39 and #48;
   - no downstream stack is rebuilt before its required root is accepted.
3. Before that:
   - live heads, base ancestry, existing review/CI evidence, ownership, and downstream dependencies are re-read;
   - any stale or contradictory coordination prose is treated as non-authoritative.
4. Current state:
   - several implementation repairs are complete;
   - multiple downstream stacks are waiting on upstream acceptance;
   - the bottleneck is primarily review/integration evidence rather than missing code;
   - TOWER is shaping a shared dispatch packet without modifying owner-controlled notes.

## Mission meeting

- Required: `YES`
- Questions to settle:
  - Which work unblocks the most downstream work?
  - Which branches genuinely need coding versus review/integration only?
  - Which parallel work is safe without creating rebuild churn?
  - Which current claims are exact evidence versus stale coordination prose?
  - Where must TOWER stop because authority belongs to SENTINEL, SWITCHYARD, an existing owner, or the operator?
- Assumptions accepted/rejected:
  - `ACCEPTED` — review/integration gates are the present bottleneck; creating more downstream code would often increase churn.
  - `ACCEPTED` — #30 and #44 are appropriate immediate SENTINEL review targets because their owner repairs are complete and their downstream/integration paths depend on clean review.
  - `ACCEPTED` — #39 and #48 are appropriate immediate SWITCHYARD integration targets because each is a root for a larger downstream stack.
  - `REJECTED` — every open PR should be actively modified.
  - `REJECTED` — idle agent time justifies inventing new work.
  - `REJECTED` — a roadmap/priority label can override canonical ownership, review findings, or integration gates.
  - `REJECTED` — FOUNDRY's open #68 planning-role proposal should silently override the operator's newer TOWER role architecture.
- Unresolved questions + owner:
  - exact reason/delta for live #39 head movement → `SWITCHYARD`;
  - exact current independent-review evidence eligible for #48 integration → `SWITCHYARD` to verify, with `SENTINEL` only where a fresh independent disposition is required;
  - any new implementation defect found in #30/#44 review → return to `FOUNDRY`;
  - any new implementation defect exposed while synchronizing #39 → return to `ANVIL`;
  - any new implementation defect exposed while synchronizing #48 → return to `FOUNDRY` unless a canonical handoff changes ownership.
- Operator decisions needed: none for the first wave. A decision is required only if evidence forces a material reprioritization or role/scope change.
- Roadmap changes: queue is organized around root-gate leverage rather than PR age or agent occupancy.
- First wave selected: #30 review, #44 review, #39 integration gate, #48 integration gate.

## First wave

These are coordination dispatches against existing work. They do not replace the underlying task/PR contracts.

- [ ] `TOWER-R1 / PR #30 review gate` — independently verify exact current #30 head, exact-head CI, returned blocker closure, and issue CLEAN/NOT READY/CHANGES REQUIRED evidence without modifying the branch — Owner: `SENTINEL`
- [ ] `TOWER-R2 / PR #44 review gate` — independently review exact `6f2b774e...`, verify CI #419 and bare-local-event-ID uniqueness repair, then post the exact-head disposition without modifying the branch — Owner: `SENTINEL`
- [ ] `TOWER-I1 / PR #39 integration gate` — inspect live `5928abe...` movement, exact current-main ancestry/delta, exact-head CI/review freshness, and either integrate under normal SWITCHYARD gates or record the exact blocker/return path — Owner: `SWITCHYARD`
- [ ] `TOWER-I2 / PR #48 integration gate` — verify reported clean-in-layer review on `2f23959...`, genuinely synchronize the feature layer onto current accepted `main`, preserve newer state/schema changes, run fresh exact-head CI/review, and merge only if SWITCHYARD's gates are clean — Owner: `SWITCHYARD`
- [ ] `TOWER-Q1 / queue watch` — re-read first-wave heads after each completed gate and update the derived queue; do not allow stale roadmap state to dispatch downstream work — Owner: `TOWER`

## Phase 0 — Foundation / root gates

- [ ] Complete first-wave independent review of #30.
- [ ] Complete first-wave independent review of #44.
- [ ] Resolve #39's live-head/current-main integration state.
- [ ] Resolve #48's historical-stack/current-main integration state.
- [ ] Checkpoint: update queue from actual dispositions before authorizing any downstream resume.

## Phase 1 — Downstream usable slices

### Context Builder stack

- [ ] After #39 is accepted, ANVIL re-reads accepted #39/current main and rebuilds/synchronizes #41 on that exact ancestry.
  - [ ] Preserve #41's already-repaired exact AST `Owner.symbol` behavior and focused tests.
  - [ ] Run fresh full Runtime CI.
  - [ ] Obtain independent exact-head review.
  - [ ] Hand clean head to SWITCHYARD.
- [ ] After #41 is accepted, ANVIL rebuilds/synchronizes #53 onto accepted #41.
  - [ ] Preserve #53's repaired drift-case source precision and exact `overlay_sha256` binding.
  - [ ] Run fresh Runtime CI and independent review before SWITCHYARD integration.

### Communication lineage stack

- [ ] After #44 is independently clean and accepted by SWITCHYARD, rebuild/synchronize #45 on exact accepted #44/current main.
  - [ ] Preserve `field_presence` and exact body-free relationship semantics.
  - [ ] Run fresh Runtime CI and independent exact-head review.
  - [ ] Hand clean head to SWITCHYARD.

### Execution lineage stack

- [ ] After #48 is accepted, rebuild/synchronize #49 on exact accepted #48/current main.
  - [ ] Preserve A1 project-scoped session identity and SQLite normalization while adding only A2 helper/recovery relationships.
  - [ ] Run fresh Runtime CI and independent exact-head review.
- [ ] After #49 is accepted, repair/rebuild #50.
  - [ ] Mechanically seal omitted/UNKNOWN submission attribution against retroactive later attachment.
  - [ ] remove the invalid active-legacy runtime token that caused the historical exact-head CI failure without weakening semantics.
  - [ ] run fresh CI and independent exact-head review before SWITCHYARD integration.

## Phase 2 — Coordination cleanup and final proof

- [ ] TOWER repairs the delivery structure of PR #70 so shared roadmap guidance is not implemented through cross-owner writes to ANVIL/FOUNDRY/SENTINEL/SWITCHYARD notes.
- [ ] Reconcile PR #68 against the operator's newer permanent role split: TOWER planning/dispatch, ANVIL + FOUNDRY development, SENTINEL review, SWITCHYARD integration.
- [ ] Allow incumbent FOUNDRY-authored planning work such as #71 to finish under existing ownership without turning that incumbent work into permanent dispatch authority.
- [ ] Refresh the shared TOWER dispatch packet from accepted repository progress.
- [ ] Independently review the resulting coordination/roadmap changes.
- [ ] Perform final proof of this coordination cycle: all active lanes have a current next action or evidence-backed wait, root gates are no longer described from stale heads, and no duplicate authority has been created.

## Explicit holds / do-not-start rules

- `ANVIL` — do not rebuild #41 until #39 is accepted; do not rebuild #53 until #41 is accepted.
- `FOUNDRY` — do not modify #30/#44/#48 unless review/integration returns a concrete defect under existing ownership; do not rebuild #45 until #44 is accepted.
- `SENTINEL` — do not patch reviewed feature branches; return defects to owners and integration/freshness blockers to SWITCHYARD.
- `SWITCHYARD` — do not treat roadmap priority as merge authority; exact ancestry, CI, eligible independent review, ownership, and expected-head protection still decide integration safety.
- `TOWER` — do not modify other agents' owner-controlled notes or feature branches; update the derived queue from evidence and surface operator decisions only when evidence cannot resolve them.

## Checkpoints

### Checkpoint A — after either #30 or #44 review returns a new blocker

- Evidence reviewed: exact-head review disposition, CI, changed delta, owner/task boundary.
- Decision: `CHANGE` if a real implementation blocker returns; otherwise `CONTINUE`.
- Reason: a root review defect must return to the owner before integration work can safely continue.
- Next action: send the concrete finding to FOUNDRY and keep downstream dependent work held.
- Re-plan if: the repair materially changes downstream interface/ancestry assumptions.

### Checkpoint B — after #39 integration decision

- Evidence reviewed: live #39 head/base, exact `main -> head` delta, CI, eligible review, merge/hold result.
- Decision: `CONTINUE | CHANGE | STOP`.
- Reason: #41/#53 scheduling depends on accepted #39 ancestry.
- Next action: if accepted, release ANVIL to rebuild #41; if blocked, keep #41/#53 held and route the exact blocker.
- Re-plan if: #39's moved head contains unexpected scope or an implementation defect.

### Checkpoint C — after #48 integration decision

- Evidence reviewed: exact synchronized A1 delta, state/schema overlap, CI, eligible review, merge/hold result.
- Decision: `CONTINUE | CHANGE | STOP`.
- Reason: #49/#50 must inherit the accepted A1 identity boundary exactly.
- Next action: if accepted, release the correct development owner to rebuild #49; if blocked, keep #49/#50 held.
- Re-plan if: synchronization changes the A1 interface or ownership.

### Checkpoint D — before coordination-role integration (#68/#70)

- Evidence reviewed: operator role intent, current `work/coordination/README.md`, #68/#70 exact deltas, independent review findings, current agent ownership.
- Decision: `CHANGE` unless the resulting integration has one coherent role model and no cross-owner note writes.
- Reason: planning/dispatch and integration safety must remain separate, and coordination files must retain low-contention ownership.
- Next action: reshape the coordination changes, then obtain independent review.
- Re-plan if: operator changes the permanent role architecture.

### Global re-plan trigger

At any point choose `RESEARCH` or `CHANGE` rather than guessing if live GitHub evidence contradicts this roadmap, a target head moves unexpectedly, or a dependency/authority claim cannot be proven.