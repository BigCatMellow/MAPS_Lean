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

Snapshot base: `main@146f092a63af63b0fd750445e584a39e82ea1442`.

## Problem

The architecture remains useful, but historical baseline prose still describes draft PR #19 / pending Phase 0 after #19 and many later capability foundations have already merged. A fresh agent could repeat accepted work, mistake planning PRs for authority, follow obsolete sequencing, or revive legacy subsystems unnecessarily.

## Change boundary

Changed only:

- this task file;
- `work/roadmaps/current-capability-reconciliation-2026-08-16.md`;
- `work/roadmaps/README.md`.

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
- [x] accepted review-subject #32 and wait subset #59 are represented without authority expansion;
- [x] dependency stacks are explicit: #48→#49→#50, #44→#45, #39→#41→#53, #43→#60;
- [x] unmerged work is classified as `OPEN_REPAIR`, `OPEN_REVIEW`, `OPEN_INTEGRATION`, or `BLOCKED_UPSTREAM`, never `ACCEPTED`;
- [x] #51/#52 remain planning-only and communication-response waits remain unimplemented;
- [x] legacy candidates are classified as absorbed, partial/open, or evidence-triggered;
- [x] bounded next questions/non-goals are identified without speculative implementation;
- [x] roadmap index links the dated reconciliation;
- [x] no runtime/schema/test files are modified.

## Verification and review-returned corrections

Accepted `main` was re-read and remained `146f092a63af63b0fd750445e584a39e82ea1442` during this revision.

The first independent review of PR #71 correctly found four planning-truth errors. Each was rechecked against live exact PR/review evidence and corrected:

1. **PR #30** — exact head `1a4016c424e188e06560c9af125e97be774ac269`, CI #358 PASS, but SENTINEL `CHANGES REQUIRED`: Run Record marks environment coverage VERIFIED on key presence even when the exact run has zero observations. Reclassified `OPEN_REPAIR`.
2. **PR #44** — exact head `4a11203f1faf0f8b5d199d6af2643ab7b7205764`, CI #343 PASS, but SENTINEL `CHANGES REQUIRED`: pinned hcom local storage uses bare event ID identity, so `(instance,event_id)` uniqueness is the wrong boundary. Reclassified `OPEN_REPAIR`.
3. **PR #39/#41** — #39 `adf25a57...` CI #365 and #41 `ec525615...` CI #382 both have SENTINEL `CLEAN IN-LAYER / NOT INTEGRATION-READY`; #39 is `OPEN_INTEGRATION`, while #41 remains `BLOCKED_UPSTREAM` despite clean in-layer review because accepted #39/current-main synchronization must come first.
4. **PR #57** — exact current base `main@146f092a...`, head `854226531acd740ed8c282e58654bc8da74bde47`, CI #379 PASS, SENTINEL CLEAN / technically ready for SWITCHYARD integration. Reclassified `OPEN_INTEGRATION`.

PR #48 remains correctly represented as exact feature head `2f23959afff9525beada28993bad536878310b7f`, CI #392 PASS, SENTINEL `CLEAN IN-LAYER / NOT INTEGRATION-READY`, therefore `OPEN_INTEGRATION` rather than accepted.

Final branch compare must remain limited to the three declared planning/task files.

## Independent review focus

Fresh independent review is required after these status corrections. Reviewer should verify:

- factual live classifications;
- no unmerged capability promoted to accepted;
- blockers not hidden by green CI;
- dependency constraints separated from merge priority;
- no duplicate runtime authority through roadmap prose;
- legacy candidates classified rather than revived wholesale;
- exact #30/#44 repair blockers and #39/#41/#48/#57 integration statuses are represented accurately.

Review required: `INDEPENDENT_REVIEW`.
FOUNDRY authored the planning change and cannot provide the disposition.

## Stop / escalate

Stop rather than guess if live state invalidates a material claim, ownership conflicts cannot be resolved, a planning candidate requires new authority merely for roadmap neatness, or accepted runtime contradicts an open design in a way that cannot be safely classified.

Route runtime repair to the owning Development lane, integration order to SWITCHYARD, and independent review to SENTINEL or another eligible reviewer.
