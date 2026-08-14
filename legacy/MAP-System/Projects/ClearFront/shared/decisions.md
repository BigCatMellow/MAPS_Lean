<!-- hpom: file: shared/decisions.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: bootstrap (hcom #311) -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Decisions — ClearFront

Classify every entry per `MAP_System/DECISION_CLASSES.md` before recording.

## DEC-CF-001 — Project bootstrap and decision paths

- Class: ARCHITECTURE / OWNERSHIP
- Date: 2026-07-16
- Decided by: claude-lab-gome (core agent, per operator lead assignment)
- Decision: Bootstrap `Projects/ClearFront/` as a standard MAP project
  brain (NEW_PROJECT_WIZARD.md). Preserve the original prototype
  untouched under `source/`; do all editable work outside `source/`.
  Refactor/decomposition work and game-balance/rules changes are tracked
  as separate task lineages so regressions stay attributable.
- Basis: operator directive hcom #311; Lilo's intake handoff
  (`MAP_System/handoffs/HANDOFF-CLEARFRONT-intake-codex-lab-lilo-to-claude-lab-gome.md`).
- Escalation: none required — inside the operator's explicit instruction.

## DEC-CF-002 — Module split mechanism: plain global scripts, no build step

- Class: ARCHITECTURE
- Date: 2026-07-16
- Decided by: claude-lab-gome (core agent, ARCHITECTURE class per
  `MAP_System/DECISION_CLASSES.md` — core agent may propose-and-record)
- Decision: Split `baseline/index.html`'s single IIFE into multiple
  plain `<script src="...">` files loaded in dependency order (data →
  engine → render → input → bootstrap), sharing state through a single
  namespace object (e.g. `window.CF`) instead of bare globals. Do NOT
  use `type="module"` — ES modules fail same-origin/CORS checks when
  opened via `file://` without a server, which would violate
  `shared/requirements.md`'s "no server/backend dependency" and
  `project-brief.md`'s "runs by opening an HTML entry point" completion
  condition. Do NOT introduce a bundler/build step for the same reason
  (see project-brief non-goals).
- Basis: `clearfront_design_principles.md` doesn't speak to code
  architecture, so this is a pure engineering call constrained by the
  project's own "no server, no build step" requirement inherited from
  the ProjectUpdater pattern already used elsewhere in this workspace.
- Escalation: none — ARCHITECTURE class, core-agent-decidable.

## DEC-CF-003 — Proposed module boundaries (baseline/index.html, 3797 lines)

- Class: ARCHITECTURE
- Date: 2026-07-16
- Decided by: claude-lab-gome
- Decision: Target file split, in load order:
  1. `styles/clearfront.css` — lines 10-1399 (all CSS).
  2. `index.html` — head/meta + markup only (lines 1-9, 1407-1650),
     `<link>` to the CSS file, `<script src>` tags for the JS modules
     below in order, no inline game logic.
  3. `js/data.js` — lines 1655-1799: `MAX_BOARD`/`MAX_RELICS`/
     `HAND_LIMIT`/`STARTING_HAND`/`MAX_CARDS_PER_TURN` constants,
     `CARD_LIBRARY`, `PLAYER_DECKLIST`, `AI_DECKLIST`, `DECKS`,
     `FACTION_POOLS`, `HERO_NAMES`. Pure data, zero logic — lowest risk,
     first decomposition task (TASK-208).
  4. `js/engine.js` — lines ~1800-3300 minus the render section: setup
     (`buildDecklist` … `resetGame`), turn/combat/effects
     (`startTurn` … `resolveCombat`, `dealCombatDamage`), AI
     (`scoreAiCard`, `aiMainPhase`, `aiChooseBlocks`, `aiDeclareAttackers`,
     `chooseAiTarget`), undo (`saveUndo`/`undoLastAction`). This is the
     largest, highest-risk slice (RISK-CF-0001) — split only after
     TASK-208 proves the multi-file pattern works, and likely split
     further (state/combat/AI) in its own follow-on rather than one task.
  5. `js/render.js` — lines ~3272-3668: `render`, `renderBoard`,
     `renderHand`, `renderChampionSlot`, `renderRelics`,
     `renderCardCatalog`, `renderBlockReview`, `renderCombatReport`,
     `renderPhase`, `renderLog`, `escapeHtml`, clash-animation builders
     (`buildClashCard`, `buildClashFx`, `playClashSequence`, etc.).
  6. `js/input.js` — lines ~3721-3797: `initCardPeek` IIFE (hover/touch
     hold-to-preview) plus the final bootstrap call.
  Exact boundaries may shift slightly as each task is implemented (some
  functions straddle categories, e.g. `handleHandCard`/`handleUnitTarget`
  are input-triggered but call into engine — keep those in engine.js and
  let input.js stay UI-gesture-only). Each task must re-verify its own
  boundary rather than treating this list as final.
- Basis: `artifacts/planning/clearfront-module-map-2026-07-16.md` (line-
  by-line function inventory of `baseline/index.html`).
- Escalation: none — ARCHITECTURE class, core-agent-decidable.

## DEC-CF-004 — Engine sub-split boundaries (TASK-208 skeleton pattern proven)

- Class: ARCHITECTURE
- Date: 2026-07-17
- Decided by: claude-lab-gome
- Decision: DEC-CF-003 deferred deciding how far to split `engine.js`
  until the `window.CF`-namespace multi-file pattern was proven — it now
  has been (TASK-208 RELEASED, no review findings). Split the remaining
  inline IIFE in `app/index.html` into two engine-layer files instead of
  one, in this order:
  1. **`js/state.js`** (TASK-212, next): deck/side/game-state setup and
     lifecycle — `buildDecklist`, `applyDeckIdentity`, `showDeckSelect`,
     `makeCard`, `shuffle`, `createSide`, `resetGame`, `sideOf`,
     `otherSide`, `controllerLabel`, `championDef`,
     `resetChampionTurnFlags`, `championDeployReason`, `deployChampion`,
     `returnChampionToSlot`, `saveUndo`, `clearUndo`, `canUndo`,
     `undoLastAction`, `aiConsiderChampion`, `addLog`, `dealStartingHand`,
     `drawCard`, `refillHand`, `replaceCard`, `startTurn`. Lowest-risk
     engine slice: state mutation and turn bookkeeping, no combat math.
  2. **`js/combat.js`** (TASK-213+, later): the rules engine proper —
     card play/effects (`cardAttack` through `removeDeadUnits`), combat
     resolution (`beginPlayerAttack` through `dealCombatDamage`),
     end-of-turn and AI (`resolveEndTurnEffects` through
     `checkGameOver`). This is RISK-CF-0001's highest-risk slice
     (damage/turn/win-condition math); do not start it until TASK-212's
     pattern (shared mutable `state` object across files) is verified
     working, since combat.js and state.js both need read/write access
     to the same `state`/`side` objects.
  Shared mutable state (the `state` object, `clashTimers`, `undoRecord`)
  stays declared once — in `app/index.html`'s remaining inline script,
  same as `playerDeckChoice`/`enemyDeckChoice` already do post-TASK-208
  — and `state.js`/`combat.js` read/write it as a shared reference
  (still under `window.CF`-style access per DEC-CF-002, exact mechanism
  decided in TASK-212 since it depends on load order not yet exercised
  for mutable, not just data, state).
- Basis: `artifacts/planning/clearfront-module-map-2026-07-16.md`
  function inventory; TASK-208's release as the load-bearing precedent
  that the namespace pattern works over plain `file://`.
- Escalation: none — ARCHITECTURE class, core-agent-decidable.

## DEC-CF-005 — combat.js function inventory and ctx contract (TASK-214)

- Class: ARCHITECTURE
- Date: 2026-07-17
- Decided by: claude-lab-gome
- Decision: resolves DEC-CF-004's deferred `combat.js` scoping now that
  TASK-212 (`state.js`) is released and its `ctx` pattern proven.
  1. **Function inventory** (post-TASK-212 `app/index.html` line
     numbers, `cardAttack` through `checkGameOver`): `cardAttack`,
     `effectiveCost`, `isDamageCard`, `isDamageSpell`, `damageHero`,
     `getCardCondition`, `canAttack`, `usesCompactLayout`,
     `scrollZoneIntoView`, `scrollToTargets`, `handleHandCard`,
     `getTargetInfo`, `isCardPlayable`, `handUnavailableReason`,
     `handleUnitTarget`, `blockTargetReason`, `assignBlock`, `playCard`,
     `resolveEffect`, `gainUnitHealth`, `buffUnit`, `dealDamage`,
     `removeDeadUnits`, `beginPlayerAttack`, `aiChooseBlocks`,
     `triggerCombatSurvival`, `resolveCombat`, `dealCombatDamage`,
     `resolveEndTurnEffects`, `endPlayerTurn`, `endEnemyTurn`,
     `scoreAiCardBase`, `scoreAiCard`, `aiMainPhase`, `chooseAiTarget`,
     `aiDeclareAttackers`, `resolvePlayerBlocks`, `checkGameOver` — 37
     functions covering card play/effects, combat resolution, end-turn,
     and AI.
  2. **Clash-animation cluster stays inline for this task** (`clashDelay`,
     `clashTimers`, `buildClashCard`, `buildClashFx`, `spawnClashNumber`,
     `showClashHit`, `flagClashCard`, `stageImpact`, `runBlockedClash`,
     `runHeroClash`, `playClashSequence`) — DEC-CF-003 already
     tentatively assigned these to a future `render.js` (visual-only,
     reads combat data already computed) and nothing found while
     scoping TASK-214 overturns that: `resolveCombat` calls
     `playClashSequence` exactly once, as a clean hand-off after combat
     math is done. Moving the whole cluster into `combat.js` instead
     would just relocate the same forwarding problem, not remove it,
     since `render.js` will need `playClashSequence` back later. Do not
     move this cluster in TASK-214.
  3. **`ctx` contract changes**: `render` stays a forwarded host binding
     (`combat.js` calls it 20+ times; `render.js` doesn't exist yet).
     **Add** `playClashSequence` as a new forwarded host binding (needed
     once, by `resolveCombat`). **Correction found during TASK-214
     implementation** (vida, 2026-07-17): also **add**
     `renderCombatReport` as a forwarded host binding —
     `resolveCombat`'s completion callback calls it directly
     (`app/index.html:1056`), it belongs to the not-yet-extracted render
     cluster (defined at `1739`, not in this task's function list), and
     following the original point-3 list literally would have crashed
     on every enemy attack. Same rationale as `render`/`playClashSequence`:
     a not-yet-modularized render-layer function, forwarded until
     `render.js` exists. **Remove** `checkGameOver`,
     `removeDeadUnits`, `damageHero`, `aiMainPhase` from `ctx` — these
     four move *into* `combat.js` itself in this task, so forwarding
     them from the host would reference functions that no longer exist
     there; any other module needing them afterward calls
     `CF.checkGameOver(...)` etc. directly (they're `window.CF`
     -published like every other extracted function, per TASK-212's
     established pattern — `ctx` is only for the raw mutable bindings
     that need cross-file *reassignment*, not for ordinary
     cross-module function calls once a function has a module home).
     The 5 mutable accessors (`state`/`undoRecord`/`uidCounter`/
     `playerDeckChoice`/`enemyDeckChoice`) are unchanged.
  4. **Mutual dependency**: `combat.js` functions call several `state.js`
     functions (`addLog`, `drawCard`, `refillHand`, `deployChampion`,
     `saveUndo`, `clearUndo`, `canUndo`, `startTurn`, etc.) — these are
     called as `CF.addLog(...)` etc., not through `ctx`, since
     `state.js` already publishes them on `window.CF` (TASK-212).
  5. **Load order**: `data.js` → `state.js` → `combat.js` → inline
     script (declares bindings, builds `ctx`, calls
     `CF.installStateModule(ctx)` then `CF.installCombatModule(ctx)`,
     destructures both, bootstraps).
- Basis: direct inspection of post-TASK-212 `app/index.html` (grep for
  `render()`/`checkGameOver()`/`playClashSequence(`/`clashTimers`
  call sites within the candidate range) — not inferred from the
  original pre-TASK-207 module map, which predates the actual
  `ctx`/`window.CF` mechanism TASK-212 built.
- Escalation: none — ARCHITECTURE class, core-agent-decidable.

## DEC-CF-006 — render.js function inventory and ctx contract (TASK-215)

- Class: ARCHITECTURE
- Date: 2026-07-17
- Decided by: claude-lab-gome
- Decision: scopes `js/render.js` (third engine-layer slice) by direct
  inspection of post-TASK-214 `app/index.html`, same method as
  DEC-CF-005, specifically to avoid a third mid-implementation surprise.
  1. **Function inventory** (28 functions, lines 326–994 — a single
     contiguous block this time, no interleaving): `clashDelay`,
     `buildClashCard`, `buildClashFx`, `spawnClashNumber`,
     `showClashHit`, `flagClashCard`, `stageImpact`, `runBlockedClash`,
     `runHeroClash`, `playClashSequence`, `updateBoardScrollIndicator`,
     `updateBoardScrollbars`, `bindBoardScrollbar`, `render`,
     `renderEnemyHand`, `renderRelics`, `renderChampionSlot`,
     `renderBoard`, `renderHand`, `createCardElement`,
     `renderCardCatalog`, `getBlockingSnapshot`, `predictCombat`,
     `renderBlockReview`, `renderCombatReport`, `renderPhase`,
     `renderLog`, `escapeHtml`. This finally resolves the clash-animation
     cluster's home, deferred twice (TASK-208's original module map,
     then again in DEC-CF-005 during TASK-214 scoping) — it moves with
     `render.js`, confirmed correct because `resolveCombat` (combat.js)
     only calls *into* it once (`playClashSequence`), never the reverse.
  2. **`clashTimers` becomes render.js-private**, not a `ctx` accessor:
     grepped every occurrence in `app/index.html` (declaration, all
     reads, all reassignments) and all of them fall inside lines
     326-994 — fully self-contained. Declare it as a plain module-scoped
     `let` inside render.js's own IIFE.
  3. **`ctx` contract changes**: **Remove** `render`, `playClashSequence`,
     `renderCombatReport` — all three move into `render.js` and become
     `window.CF`-published, exactly as flagged in TASK-214's
     current-state.md follow-up note (not rediscovered this time).
     **Keep** the 5 mutable accessors (render.js reads `ctx.state` 72
     times, never reassigns it) and `$`/`refs` (heavy DOM access, ~90
     `refs.` sites alone).
  4. **Known required sibling edits** (disclosing upfront, per the
     TASK-214 `state.js` precedent, so this isn't a mid-task discovery):
     both `combat.js` and `state.js` destructure some of the three
     leaving `ctx` into local `const`s and call them bare — **not**
     `ctx.render(...)` literally, so the fix is editing the destructure
     line plus every bare call site, not a dot-notation search/replace.
     - `combat.js`'s `installCombatModule(ctx)`:
       `const { refs, render, playClashSequence, renderCombatReport } = ctx;`
       — drop all three; convert `render()` ×22, `playClashSequence()`
       ×1, `renderCombatReport()` ×1 to `CF.render(...)`/
       `CF.playClashSequence(...)`/`CF.renderCombatReport(...)`.
     - `state.js`'s `installStateModule(ctx)`:
       `const { $, refs, render } = ctx;` — drop `render` only
       (`state.js` never calls `playClashSequence` or
       `renderCombatReport`); convert `render()` ×3 (in `saveUndo`'s
       caller path, `undoLastAction`, and `startTurn`) to
       `CF.render(...)`. **Correction found while scoping this
       decision**: an earlier draft claimed "`state.js` needs no
       change," based on a grep for literal `ctx.render(` text, which
       misses the destructured-bare-call pattern both modules actually
       use. Verified directly against `state.js:203,236,359` before
       finalizing.
  5. **Cross-module calls render.js makes**, all via `CF.*` (never
     `ctx`, per the established pattern): `CF.canUndo`, `CF.championDef`,
     `CF.controllerLabel`, `CF.sideOf` (state.js); `CF.blockTargetReason`,
     `CF.canAttack`, `CF.effectiveCost`, `CF.getCardCondition`,
     `CF.handleHandCard`, `CF.handleUnitTarget`,
     `CF.handUnavailableReason`, `CF.isCardPlayable` (combat.js).
     Confirmed via grep that no render-cluster function is called from
     `combat.js`/`state.js` other than the three already identified in
     point 3 — no other forwarding gap exists (checked specifically
     because DEC-CF-005 missed one on the first pass).
  6. **Load order**: `data.js` → `state.js` → `combat.js` → `render.js`
     → inline script (declares bindings, builds `ctx`, installs all
     three modules in order, destructures, wires the input IIFE,
     bootstraps). Correction while drafting this decision: `showDeckSelect`
     (and every other `state.js`/`combat.js` export) is already
     destructured into an inline-script-local `const` at its install
     site (line 305 for `showDeckSelect` specifically) and stays that
     way regardless of this task — the bare `showDeckSelect();`
     bootstrap call and the two `restartBtn`/`playAgainBtn` listener
     calls need **no** `CF.` prefix. Only `render`/`playClashSequence`/
     `renderCombatReport` change form (from local `const` calls to
     needing `CF.` from `combat.js`, since those three are *leaving*
     the local-destructure set, not staying in it).
  7. **`clashSkip` correction, found before implementation began** (while
     doing the extraction directly rather than delegating, the boundary
     at line 994 turned out to cut through a large top-level event-
     listener wiring block that the earlier line-range check did not
     examine closely enough): `clashTimers`' sibling private variable
     `clashSkip` (also declared at the top of the clash cluster,
     assigned inside `playClashSequence` at two sites) is *read* by one
     line **outside** the 326-994 range —
     `refs.clashOverlay.addEventListener('click', () => { if (clashSkip)
     clashSkip(); });`, part of a ~47-line wiring block (roughly lines
     946-992) that stays in the inline script. This is the exact same
     cross-file-mutable-reassignment shape that motivated the `ctx`
     accessor pattern for `state`/`undoRecord`/etc. — except here the
     simplest fix is not a `ctx` accessor but relocating the **one**
     listener-registration line itself into `render.js` (right after
     the function definitions, before `return api`), since `clashSkip`
     is otherwise fully private and this is its only external read.
     **The rest of that wiring block needs zero changes**: every other
     bare name it calls (`undoLastAction`, `endPlayerTurn`,
     `beginPlayerAttack`, `resolvePlayerBlocks`, `addLog`,
     `scrollZoneIntoView`, `showDeckSelect`, and — the render.js names
     — `render`, `renderCardCatalog`, `renderBlockReview`,
     `bindBoardScrollbar` ×2, `updateBoardScrollbars`) continues to
     resolve correctly once `render.js`'s exports are destructured into
     the inline script the same way `state.js`/`combat.js`'s already
     are (full 28-name destructure, matching the existing full-list
     pattern rather than cherry-picking only the 5 names actually
     referenced elsewhere in the inline script).
  8. **`render.js`'s own top-of-module destructure from `ctx`**: only
     `const { $, refs } = ctx;` — mirroring `state.js`'s original
     (pre-TASK-214) form. `render`/`playClashSequence`/
     `renderCombatReport` are not destructured from `ctx` inside
     `render.js` because they no longer live in `ctx` at all; they are
     `render.js`'s own function declarations.
- Basis: direct grep/inspection of post-TASK-214 `app/index.html` for
  every `state.`, `clashTimers`, `clashSkip`, `refs.`, and
  cross-cluster function-call site — including the full extent of the
  top-level event-listener wiring block, not just the function-only
  range — not the original pre-extraction module map.
- Escalation: none — ARCHITECTURE class, core-agent-decidable.
- **Post-implementation note** (2026-07-17): TASK-215 was implemented
  directly by claude-lab-gome (Fable helper vida ran out of usage
  credits before starting; operator directed doing it directly). Even
  with this decision's careful upfront scoping, 4 more real gaps
  surfaced only when the live app was actually driven through CDP and
  its exceptions read: 3 more missed cross-module function names
  (`championDeployReason`, `deployChampion`, `cardAttack` ×8) beyond
  the 12 point 5 listed; the 3 data.js constants (`MAX_CARDS_PER_TURN`,
  `CARD_LIBRARY`, `HERO_NAMES`) were never destructured into `render.js`
  at all; `undoRecord` (not just `state`) needed the same bare-identifier
  rewrite; and the exact spread-position regex hazard TASK-214 disclosed
  for `combat.js` recurred here for `state` (3 sites) because the fix
  wasn't generalized into the extraction tooling itself. Full detail:
  `artifacts/tests/task-215-render-parity.md` section 4. Takeaway for
  any future hand-extraction: a static line-range/name inventory, no
  matter how carefully grepped, is not a substitute for actually running
  the result — every one of these was caught by reading a live
  `Runtime.exceptionThrown` stack trace, none by static review.

## DEC-CF-007 — input.js boundary and installation point (TASK-216)

- Class: ARCHITECTURE
- Date: 2026-07-17
- Decided by: codex-lab-lilo
- Decision: complete the decomposition with one final, deliberately narrow
  input module:
  1. Move only the self-contained `initCardPeek` IIFE from the remaining
     inline host into `app/js/input.js`.
  2. Publish `CF.installInputModule()` and invoke it at the exact former IIFE
     position—after host action/overlay listeners and board-scrollbar binding,
     before `showDeckSelect()`—so listener-registration and bootstrap ordering
     remain unchanged.
  3. `input.js` receives no `ctx` and adds no mutable bindings. Its hover and
     touch-preview implementation depends only on `window`, `document`,
     `navigator`, DOM/CSS classes, and local closure variables.
  4. Keep the host action buttons, modal listeners, scrollbar bindings, module
     installation/destructuring, mutable-binding declarations, and
     `showDeckSelect()` bootstrap inline. Those are integration/bootstrap
     wiring, not part of the card-preview gesture boundary.
  5. Preserve the plain-script load order:
     `data.js` → `state.js` → `combat.js` → `render.js` → `input.js` → inline
     host. `input.js` only defines its installer when loaded; the inline host
     decides when installation runs.
- Verification: syntax checks on every JS file and the remaining inline host;
  byte-identical champion-select screenshot; seeded combat/blocking replay;
  undo regression; and direct desktop hover plus touch-hold preview tests with
  zero console messages/exceptions.
- Basis: direct inspection of post-TASK-215 `app/index.html`; the IIFE is the
  only remaining cohesive input-specific block and has no cross-module symbol
  dependencies.
- Escalation: none—operator explicitly directed implementation; architecture
  remains within DEC-CF-002/003 and the released decomposition sequence.

## DEC-CF-008 — Adopt risk-tiered review, drop full ceremony for low-risk work

- Class: ARCHITECTURE / OWNERSHIP
- Date: 2026-07-17
- Decided by: claude-lab-gome (core agent, per DEC-CF-001's operator lead
  assignment; ARCHITECTURE/OWNERSHIP class, core-agent-decidable)
- Decision: adopt the independent process audit's core recommendation
  (`artifacts/reviews/clearfront-independent-delivery-audit-2026-07-17.md`,
  P2 "Review quality is high, but review frequency is not risk-calibrated")
  going forward for ClearFront:
  1. **Three risk lanes**, per the audit's model:
     - **High** (extraction/security, rule/state/combat engine changes,
       hidden-information/persistence, release packaging): keep the full
       pipeline as-run for TASK-207/213/214 — independent review,
       reviewer-reran evidence, release checklist.
     - **Medium** (cross-module refactors, substantial UI-interaction
       changes): automated parity evidence required; one review at the
       change's completion, not per intermediate step.
     - **Low** (mechanical file moves, art/content/styling, docs): owner
       verifies directly; batch multiple low-risk changes behind one
       review rather than one full cycle per change. No standalone
       release checklist unless the operator asks for one on that item
       specifically.
  2. **Batch low-risk work.** TASK-216 (input.js move, zero `ctx`
     dependency) and TASK-217 (card art) each separately went through
     task creation, independent review, release checklist, current-state
     update, and event logging — reasonable individually, excessive as a
     standing default for this risk tier. Future comparable slices should
     be proposed and executed as one batch with one review.
  3. **Future ClearFront-specific events go to
     `Projects/ClearFront/events/events.jsonl`** (the project-local log
     this project's own bootstrap created per `NEW_PROJECT_WIZARD.md`,
     but which sat empty all phase — every TASK-207–217 event instead
     went to the global `MAP_System/events/events.jsonl`, confirmed by
     the audit). Not retroactively migrated — that would be pure
     churn — but every new event from this point on uses the project
     log. Task-graph/DB-mirror-driving events still also need the global
     log per existing MAP mechanics; write to both where the tooling
     requires it, but the durable *narrative* record for "what happened
     in this project" is the project-local file going forward.
  4. **Not adopted without operator input**: the audit's P1 "no clean git
     snapshot" and P0 "rules-conformance disposition" findings are
     real but out of this decision's scope — the first touches the whole
     repository (57 files, many other agents' unrelated in-progress
     work) and isn't a unilateral call; the second is a genuine SCOPE/
     game-design decision per this project's own `AGENTS.md` decision
     paths. Both routed to command-center directly, not decided here.
- Basis: `artifacts/reviews/clearfront-independent-delivery-audit-2026-07-17.md`,
  an operator-commissioned independent audit (Codex agent `nipa`) that
  directly measured the coordination cost (89 MAP events, 60 artifacts,
  ~8 MiB for 8 released tasks) against the marginal risk-reduction of
  applying identical assurance to a 78-line zero-dependency file move
  and a 933-line rule engine change.
- Escalation: none for the process-tier decision itself — ARCHITECTURE/
  OWNERSHIP class, core-agent-decidable. The two items explicitly out of
  scope above are escalated separately.
