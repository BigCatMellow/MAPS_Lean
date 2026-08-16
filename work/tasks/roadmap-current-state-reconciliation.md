# Task: current capability roadmap reconciliation

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `FOUNDRY / Planning-Control-Surface`
- Risk: `MEDIUM`
- Goal: reconcile the master/Prime capability roadmaps and recovered legacy candidates with accepted and open repository state as of 2026-08-16, without turning roadmap prose or open PRs into runtime authority.

## Inputs and source of truth

Evidence order:

1. root `AGENTS.md`;
2. live GitHub `main`, exact PR/base/head/review/CI state, merged code/tests, and canonical MAPS state;
3. current `work/coordination/agents/*.md` for collision avoidance only;
4. accepted task/decision evidence;
5. long-form roadmaps and migration audits/backlog as non-authoritative design/history evidence.

Planning inputs include the master roadmap, Prime roadmap, all five detailed agent-harness roadmaps, migration legacy audit/backlog, and live capability-relevant PR state.

Current snapshot base: `main@7269ce2be25993fa19b172f65c95381328585a35`.

## Problem

The architecture remains useful, but historical baseline/status prose changes more slowly than live integration. A fresh agent could repeat accepted work, mistake planning PRs for authority, follow obsolete sequencing, trust stale CI/review metadata, or revive legacy subsystems unnecessarily.

## Change boundary

Changed only:

- this task file;
- `work/roadmaps/current-capability-reconciliation-2026-08-16.md`;
- `work/roadmaps/README.md` remains the existing index link from this PR.

No runtime, tests, schema/state, provider behavior, feature branches, other agent coordination files, merge state, or review dispositions are changed. The master/Prime architecture is preserved rather than rewritten wholesale.

## Decision authority

FOUNDRY may classify derived planning status from verified live evidence, identify obsolete assumptions, preserve dependency/UNKNOWN boundaries, and shape bounded future questions.

FOUNDRY may not declare unmerged work accepted, choose integration order, approve another lane's work, promote legacy candidates, take another lane's runtime branch, or invent missing architecture for roadmap completeness.

## Required invariants

- one fact / one authority;
- capability != authority;
- source evidence > summaries;
- planning status remains derived;
- green CI does not override a semantic blocker;
- clean feature review != merged capability;
- synchronized head without fresh review != merge-ready;
- planning/design PR != runtime authority;
- UNKNOWN remains UNKNOWN where evidence is incomplete;
- dependency ordering != merge priority;
- no self-authorizing learning/promotion.

## Acceptance criteria

- [x] exact snapshot base is stated and live GitHub explicitly supersedes it;
- [x] merged PR #19 is recognized as accepted and obsolete “draft PR #19 / pending Phase 0” status is retired;
- [x] accepted Harness #20–#24 is separated from open lineage work;
- [x] accepted Run Record/evaluation #33–#35 is represented without claiming complete replay/refinement;
- [x] accepted Skills #25–#27/#31 is separated from future production routing/promotion;
- [x] accepted Environment #28/#29 is separated from #30 and later recovery/environment automation;
- [x] accepted review-subject #32, wait subset #59, and Operator Intent Compiler #57 are represented without authority expansion;
- [x] dependency stacks are explicit: #48→#49→#50, #44→#45, #39→#41→#53, #43→#60;
- [x] unmerged work is classified as `OPEN_REPAIR`, `OPEN_REVIEW`, `OPEN_INTEGRATION`, or `BLOCKED_UPSTREAM`, never `ACCEPTED`;
- [x] #51/#52 remain planning-only and communication-response waits remain unimplemented;
- [x] legacy candidates are classified as absorbed, partial/open, or evidence-triggered;
- [x] bounded next questions/non-goals are identified without speculative implementation;
- [x] roadmap index links the dated reconciliation;
- [x] no runtime/schema/test files are modified.

## Live verification — 2026-08-16 refresh

Current accepted main was re-read as:

`7269ce2be25993fa19b172f65c95381328585a35`

This main includes merged PR #57 Operator Intent Compiler request shaping.

Live status corrections applied to the roadmap overlay:

1. **PR #30 — `OPEN_INTEGRATION`**
   - head `7bae6d5758619a391c7551ee4589ea2d80d0a5b8`;
   - Runtime CI #415 / `31932277332` PASS;
   - SWITCHYARD independent feature-head review `CLEAN IN-LAYER`;
   - the prior empty-environment-evidence VERIFIED defect is closed;
   - current-main synchronization + fresh integrated-head CI/review remain.

2. **PR #44 — `OPEN_REVIEW`**
   - repaired head `6f2b774eee27a0596820b12f080bfd7e60c0f50e`;
   - Runtime CI #419 / `31951668246` PASS;
   - bare local `event_id` now defines the configured-store source identity while `instance` remains metadata;
   - no fresh independent disposition exists yet on this repaired head, so it is not integration-ready.

3. **PR #45 — `BLOCKED_UPSTREAM`, clean in-layer**
   - head `b78de03a9e05fe19846d0c0629a55e54427fa587`;
   - Runtime CI #346 PASS;
   - SENTINEL `CLEAN IN-LAYER / NOT INTEGRATION-READY`;
   - must be rebuilt on accepted #44.

4. **PR #48 — `OPEN_INTEGRATION`**
   - head `2f23959afff9525beada28993bad536878310b7f`;
   - Runtime CI #392 PASS;
   - SENTINEL `CLEAN IN-LAYER / NOT INTEGRATION-READY`;
   - current-main synchronization remains.

5. **PR #49/#50 execution-lineage downstream**
   - #49 head `ed865be729cf2d15663258fd46c9296ea32d28e7`; independent review found no A2-specific blocker on historical ancestry, but it must be rebuilt on accepted #48;
   - #50 actual head `832fa4ab2c3e97a8f7cdc22a73baca0d276adfc0`; exact-head CI #274 failed and two A3 defects remain: immutable UNKNOWN-at-submission must be recorded rather than backfillable absence, and active-runtime `legacy/` wording trips the legacy-removal gate;
   - later green-run claims in #50 PR prose are not accepted as evidence because the cited SHAs do not resolve to #50 and the run numbers belong to other PRs.

6. **PR #39 — `OPEN_REVIEW` on synchronized current-main ancestry**
   - synchronized head `5928abe4550dbf7a75c2a2825e3cda5033ead830`;
   - base `main@7269ce2be25993fa19b172f65c95381328585a35`;
   - Runtime CI #422 / `31951875209` PASS;
   - historical feature head was SENTINEL CLEAN IN-LAYER, but synchronized head still needs fresh independent review.

7. **PR #41/#53 — clean in-layer, `BLOCKED_UPSTREAM`**
   - #41 `ec525615fd708610bc3e90e07a95bb6c791d2465`, CI #382 PASS, SENTINEL CLEAN IN-LAYER; rebuild after accepted #39;
   - #53 `d5c03a8e09bc5c49b884bc452d3c487a04ce5974`, CI #348 PASS, independent remediation review clean; rebuild after accepted #39/#41.

8. **PR #57 — `ACCEPTED`**
   - merged into current snapshot main;
   - no longer represented as OPEN_INTEGRATION.

9. **Operational-learning stack**
   - #43 head `aeecf1b5775db1d5ac2484819620f476752f3654`: runtime/authority semantics reviewed clean, but task/PR scope omitted the existing schema-test path; classify `OPEN_REPAIR` for the bounded scope-contract correction and later current-main integration;
   - #60 head `cfd758aace44970e7400c005c337be040d367918`, CI #307 PASS, independent review CLEAN IN-LAYER; classify `BLOCKED_UPSTREAM` behind #43.

10. **PR #51/#52 — `PLANNING_ONLY`**
    - #51 exact-provider-receipt / task-run↔hcom-event join design remains design evidence only;
    - #52 evidence-backed wait design remains design evidence only; accepted #59 covers only the safe canonical subset.

## Legacy reconciliation verification

Re-read:

- `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`;
- `migration/FUTURE_IDEAS_BACKLOG.md`.

The current reconciliation preserves their governing rule rather than reviving old machinery: preserve observed problems, invariants, evidence, experiments, and useful techniques; classify candidates as absorbed, partially represented/open, or evidence-triggered; do not promote a subsystem merely because legacy MAP implemented or proposed it.

## Independent review focus

Fresh independent review is required after this factual refresh. Reviewer should verify:

- exact snapshot/main and live classifications;
- #57 is accepted/merged;
- #30 is clean in-layer and integration-pending, not still repair-blocked;
- #44 is repaired/CI-green but remains review-pending;
- #39 is synchronized and CI-green but still needs integrated-head review;
- #41/#53 remain upstream-blocked despite clean own-layer reviews;
- #48 remains unaccepted/integration-pending;
- #49/#50 downstream distinctions and #50 bad-CI-metadata warning are accurate;
- #43/#60 scope/upstream states are accurate;
- no unmerged capability is promoted to accepted;
- dependency constraints are not presented as SWITCHYARD merge priority;
- no duplicate runtime authority is created through roadmap prose;
- legacy candidates are classified rather than revived wholesale.

Review required: `INDEPENDENT_REVIEW`.
FOUNDRY authored the planning change and cannot provide the disposition.

## Stop / escalate

Stop rather than guess if live state invalidates a material claim, ownership conflicts cannot be resolved, a planning candidate requires new authority merely for roadmap neatness, or accepted runtime contradicts an open design in a way that cannot be safely classified.

Route general runtime repair to ANVIL, incumbent FOUNDRY repair returns only to FOUNDRY when explicitly returned, integration order to SWITCHYARD, and independent review to SENTINEL or another eligible reviewer.
