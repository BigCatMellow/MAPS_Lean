# ClearFront Independent Product and Delivery Audit

Date: 2026-07-17  
Auditor: clearfront-audit-nipa (independent Codex helper)  
Scope: final `Projects/ClearFront/app/`, governing rules/design documents, TASK-207–217 records, reviews, test evidence, release checklists, MAP events, recent hcom activity, and repository status/history. No application code was modified.

## Executive verdict

ClearFront's preservation and decomposition phase was built carefully and is credible as a behavior-preserving refactor. The team found and corrected real defects: unsafe extraction paths and non-atomic replacement in TASK-207, a hidden-information undo exploit in TASK-213, a missed render binding in TASK-214, and four live-only extraction bugs during TASK-215. Independent browser replays, source hashes, screenshots, and no-self-review gates materially reduced risk.

However, “released” currently means “matches the original prototype,” not “matches the published game rules” or “is comprehensively correct.” The released audit already documents missing Equipment, Mind, Forge, Neutral and Stun, narrower Rush/Drain behavior, a non-spec fatigue rule, and deck-composition deviation. The test suite is mostly scripted end-to-end parity over a few seeded paths; it does not provide systematic rule-engine coverage. The code is modular by file, but not yet modular by dependency: a 933-line `combat.js`, a host-owned mutable `ctx`, `window.CF`, and cross-module calls leave a tightly coupled global application.

The workflow is slower than a capable single agent chiefly because the phase applied high-assurance release ceremony to nearly every mechanical slice. The process generated at least 60 ClearFront artifacts (about 8 MiB) and 89 MAP events for TASK-207–217, including 53 `PROGRESS` events. Several tasks repeat the same hash, syntax, screenshot, seeded replay, review, release-checklist, shared-state, and event updates. That cost was justified for the extractor and combat/state boundaries, but not for every small presentation or input extraction.

Recommended model: one accountable implementer for a coherent vertical batch, automated continuous checks, and a second-agent review only at risk boundaries. Preserve provenance, behavioral tests, and independent review for extraction, combat/rules, persistence/security, and player-visible rule changes. Collapse routine mechanical refactors and low-risk UI changes into one batch with one review and one release record.

## Prioritized findings

### P0 — The game is not conformant with its own current rules

This is a known scope gap, not a newly introduced regression, but it is the largest correctness risk if the application is represented as implementing `clearfront_rules.md`.

The released TASK-211 audit records:

- Decks use a 15/15 two-faction construction instead of the documented 17 primary / 7 allied / 6 neutral distribution.
- Empty-deck refill applies undocumented fatigue damage.
- Equipment is unimplemented.
- Mind, Forge, and Neutral are absent.
- Stun is unimplemented; Rush and Drain are narrower than the rules text.
- Several interface requirements cannot be fulfilled while those systems are absent.

These gaps should be converted into an explicit product decision before further content work: either (1) change the implementation to match the current rules, or (2) revise the working rules through the required SCOPE/design-review path. “Parity with baseline” must not be used as evidence that these behaviors are correct.

### P0 — Rule-engine regression evidence is too narrow for future gameplay changes

Current evidence is strong for refactor parity but weak for semantic completeness. The seeded CDP harnesses exercise representative card play, combat, blocking, AI turns, and undo, usually at seeds 42 and 7. They do not form a rule matrix across all keywords, card effects, board limits, simultaneous lethal cases, Champion return/replay, full-zone failures, target legality, persistent damage, and first-player variants.

The browser scripts also depend on fixed delays around asynchronous UI transitions. TASK-216's review explicitly observed transient snapshot jitter and had to distinguish it by rerunning the same build against itself. This is acceptable as supporting evidence but unsuitable as the primary oracle for a growing rules engine.

Before balance or mechanic work, extract or expose a deterministic engine test seam and add table-driven cases for every rule and effect. Keep one browser smoke test for integration and presentation; move most combinatorial correctness checks below the DOM.

### P1 — There is no clean, durable release snapshot in Git

`map-git status --short` shows the entire `Projects/ClearFront/` tree and TASK-207–217 records/artifacts as untracked, alongside many unrelated MAP modifications. The relevant Git history contains only the earlier repository-organization commit. Therefore reviews compare working-tree files and saved artifacts, not immutable commits.

This creates provenance and rollback risk: a later edit can change a “released” file without a commit boundary, and the repository cannot reproduce the exact state approved for each release. Hashing `source/` and `baseline/` protects the original, but not the evolving `app/` release.

Quick fix: create one intentional phase-completion commit after reconciling the dirty tree, then require a commit SHA (or equivalent immutable snapshot ID) in future high-risk review packets. Do not create a commit per tiny task unless that is useful; one coherent batch commit is enough.

### P1 — File decomposition improved navigation, but dependency architecture remains global and coupled

The 3,797-line baseline became HTML/CSS plus `data.js`, `state.js`, `combat.js`, `render.js`, and `input.js`, which is a real maintainability improvement. Yet `combat.js` is still 933 lines and owns card play, effects, combat, AI, scrolling helpers, and game-over logic. The host retains mutable bindings exposed through getter/setter `ctx`; modules publish broad APIs on `window.CF` and call one another cyclically.

This architecture is reasonable for direct `file://` compatibility and a no-build-step phase, but it is an intermediate endpoint. It makes isolated unit testing and contract enforcement difficult, and a missing forwarded function already caused a real TASK-214 scoping defect.

Next refactor should be driven by testability rather than file count: separate pure rule calculations/effect resolution from DOM/rendering and AI policy, pass explicit state/ports, and reduce the public `CF` surface. Do not introduce a framework merely to rename the coupling.

### P1 — The checked-in test artifacts are not a coherent one-command suite

Independent validation found:

- All five application JS files pass `node --check`.
- Running `python3 Projects/ClearFront/scripts/test_extract_bundle.py` passes all five extractor regression checks.
- Running the same file through standard `python -m unittest` reports zero tests because the script uses free functions/assertions rather than a discoverable test framework.
- Browser harnesses fail without externally starting Chromium and supplying positional port/URL/output arguments. Invoking `task217-card-art-check.mjs` or `task215-undo-check.mjs` directly produces CDP/undefined-URL errors.

The parity reports document launch commands, so evidence is reproducible by a careful reviewer, but maintenance is unnecessarily manual. Add one project test runner that starts/stops Chromium safely, allocates a port, runs syntax/extractor/engine/browser checks, and returns a single nonzero exit code on failure. Convert fixed sleeps to state/event polling where possible.

### P1 — MAP records are split across the wrong scopes and contain avoidable churn

`Projects/ClearFront/events/events.jsonl` is empty even though project instructions call for durable project activity records. The relevant history instead lives in the global `MAP_System/events/events.jsonl`. TASK-207–217 account for 89 global events: 53 `PROGRESS`, 11 `APPROVED`, 9 `RELEASED`, 8 `SUBMISSION`, 5 `CHANGES_REQUESTED`, 2 `BLOCKED`, and 1 decision event.

Examples of avoidable process cost:

- TASK-212 required a changes-requested/resubmission cycle solely to register nine already-existing evidence files in `output_paths`; implementation had passed.
- TASK-209 was created with the wrong role, blocked, then retired and replaced by TASK-211.
- Function-count metadata drifted (“37” vs an explicit list of 38) in TASK-214.
- Each slice repeatedly updates task JSON, graph mirrors, DB state, decisions/current-state, evidence, review, release checklist, and events.

These controls are useful when they change behavior or preserve accountability. They become ceremony when mirror registration or narrative duplication triggers the same rejection path as a product defect. Choose one canonical event scope and generate mirrors/checklists mechanically. Treat metadata-only corrections as an amend-without-resubmission path when ownership and tested outputs are unchanged.

### P2 — Review quality is high, but review frequency is not risk-calibrated

Independent review paid for itself on TASK-207 and high-risk engine slices. It caught path traversal, stale/partial output behavior, atomicity, a missing binding, evidence usability, and an undo exploit. Those gates should remain.

The same full workflow is excessive for bounded mechanical moves and low-risk presentation work. TASK-216 moved a self-contained 78-line gesture IIFE with no `ctx` keys; TASK-217 added category art and CSS/markup presentation. They received task creation/claim, comprehensive regressions, independent review, release checklist, current-state update, and event records. The assurance is good, but the marginal benefit per coordination step is low.

Batch low-risk changes behind a single review. Use second-agent review for changes that alter rules/state, security/provenance, shared contracts, or large cross-module boundaries. For small UI/content work, require automated checks plus sampled visual review at batch end.

### P2 — Evidence volume obscures the decision signal

ClearFront has 60 artifact files totaling roughly 8 MiB after one day, with repeated screenshots, logs, parity reports, owner-verification notes, reviews, and release summaries. Much of this proves the same facts several times. Durable evidence is valuable, but the primary question becomes harder to answer: which release is current, what commands define the gate, and what risks remain?

Retain compact machine-readable test output and only the screenshots that prove a visible acceptance criterion. One release manifest should link test results, reviewer verdict, source commit, and unresolved risks. Avoid repeating the full implementation narrative in parity report, review, release checklist, decision log, current state, hcom, and event log.

### P2 — Mobile card-detail behavior should be resolved explicitly

TASK-217's reviewer found that detail-hiding CSS is desktop-width-scoped, so mobile-width compact cards display full rules text rather than requiring touch-hold. This is not a gameplay correctness failure, but it conflicts with the stated compact/detail-on-preview concept and may reduce mobile readability. Decide whether mobile should remain always-expanded or use the touch-hold preview, then encode that behavior in a focused viewport test.

### P3 — Risk and state documents are already drifting

`RISK-CF-0001` and `RISK-CF-0002` remain open with last-review dates from 2026-07-16 even though the extraction/decomposition phase is released and the mitigations were exercised repeatedly. `current-state.md`, release checklists, decisions, tasks, and the conformance audit overlap substantially.

Close or reclassify mitigated risks at phase end and make `current-state.md` a short index to canonical records, not another narrative ledger.

## What the team did well

- Preserved the original source byte-for-byte and added reproducible extraction with security regression tests.
- Correctly avoided ES modules/build tooling because direct `file://` execution is a stated constraint.
- Separated refactoring from behavior changes, enabling credible baseline parity checks.
- Used independent review where it uncovered substantive defects; reviewers reran tests rather than only reading claims.
- Recorded known rules deviations candidly instead of calling baseline behavior specification-conformant.
- Fixed the hidden-information undo exploit promptly and tested that ordinary undo still works.
- Disclosed implementation defects discovered during TASK-215 rather than smoothing them out of the record.

## Why this felt slower than one agent

A strong single agent could have performed the mechanical split in one coherent pass, run a single regression suite, and reviewed its own diff in hours. The present system serializes work through creation, claim, ownership boundaries, helper briefing, output-path registration, submission, reviewer availability, changes-requested handling, approval, release, graph/DB reconciliation, checklist writing, shared-state updates, event logging, and hcom reporting. Because many slices touch `app/index.html`, parallelism is limited by shared-file ownership; TASK-212 was explicitly blocked while TASK-213 used the same path. Multi-agent capacity therefore adds coordination latency without much parallel throughput.

The comparison is not “multi-agent bad.” The extractor and combat work benefited from adversarial review, and a single agent plausibly would have missed some defects. The mismatch is applying the same assurance pipeline to high-risk logic, mechanical relocation, and cosmetic work. The current workflow optimizes for auditability per task; the operator is feeling the cost in end-to-end product cadence.

## Recommended streamlined operating model

### 1. Work in coherent batches

Use one owner for a vertical objective such as “complete modular baseline” or “implement and test Stun,” not one task per file/function cluster. Allow the owner to make necessary sibling edits within a declared batch boundary.

### 2. Establish three risk lanes

- High risk: extraction/security, rule/state/combat changes, persistence/network dependencies, hidden information, release packaging. Require explicit acceptance criteria, immutable snapshot, independent review, and focused adversarial tests.
- Medium risk: cross-module refactors and substantial UI interaction changes. Require automated parity plus one review at batch end.
- Low risk: mechanical moves, copy, art, styling, documentation. Owner verifies; include in a batch review or sample review. No standalone release ceremony unless operator-visible urgency warrants it.

### 3. Make automation the gate

Add `Projects/ClearFront/scripts/test_all` (or equivalent) that runs extractor regressions, JS syntax, deterministic rule tests, and browser smoke checks with managed Chromium lifecycle. Task/release records should cite one command and stored summary rather than reproduce manual recipes.

### 4. Keep one canonical record per concern

- Task record: objective, owner, risk lane, outputs, acceptance.
- Test result: command, commit/snapshot, pass/fail, concise failures.
- Review: findings and verdict only.
- Current state: latest release pointer and open risks only.
- Event stream: transitions only, not every output registration.

Generate task-graph/DB mirrors and release boilerplate automatically. Do not make a product-passing task re-enter full review solely for evidence-path metadata.

### 5. Use agents where independence or parallelism is real

- Primary agent owns implementation and integration.
- Reviewer agent works only at risk boundaries and reviews an immutable diff.
- Helper agents receive independently mergeable scopes (test matrix, rules audit, asset research), not adjacent edits to the same host file.
- For small changes, a lighter hybrid is preferable: single owner + automated checks + periodic independent batch review.

### 6. Define phase exits

At the end of a phase, create one clean commit/snapshot, run the full gate, update/close risks, archive superseded evidence, and publish one release manifest. Then begin the next product phase. This prevents an indefinitely dirty working tree from becoming the de facto release store.

## Immediate quick wins

1. Commit or otherwise snapshot the released decomposition phase after reconciling unrelated dirty-tree changes.
2. Add a one-command test runner and make browser harness arguments/lifecycle self-contained.
3. Create a rule/effect test matrix before implementing new mechanics or balance changes.
4. Decide implementation-versus-spec disposition for fatigue, deck composition, Equipment, missing factions, Rush/Drain, and Stun.
5. Batch the next low-risk UI/content changes; require one review at the end rather than one release per small task.
6. Stop emitting `PROGRESS` events for individual output-path registrations; generate registered outputs from the final manifest.
7. Resolve the mobile card-details behavior and add one mobile viewport assertion.
8. Close or update the extraction/decomposition risks and point `current-state.md` to a single phase release manifest.

## Evidence limitations

This audit did not perform a complete manual playthrough of every deck/card combination. It independently ran the extractor regression script (5/5 pass) and JS syntax checks (all five app modules pass). Direct invocation of browser harnesses without their externally managed Chromium/arguments failed, which supports the test-usability finding rather than a product-failure conclusion. Existing reviewers independently ran the browser harnesses successfully, including TASK-217's 7/7 focused check, undo checks, and combat/blocking replay.
