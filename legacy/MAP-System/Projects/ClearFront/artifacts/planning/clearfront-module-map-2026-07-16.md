<!-- hpom: file: artifacts/planning/clearfront-module-map-2026-07-16.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: claude-lab-gome -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-16 -->
<!-- hpom: verified_against: baseline/index.html (post-TASK-207 extraction) -->
<!-- hpom: confidence: MEDIUM -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# ClearFront Module Map — baseline/index.html (3797 lines)

Line-by-line inventory used to derive DEC-CF-003's module boundaries.
Line numbers are against `baseline/index.html` as of TASK-207.

## Structure

| Lines | Content |
|---|---|
| 1-9 | `<!DOCTYPE>`, `<head>` open, meta tags, title |
| 10-1399 | `<style>` — all CSS |
| 1400-1406 | head close |
| 1407-1650 | `<body>` markup (deck-select modal, board, hand, sidebar, log, game-over modal) |
| 1651-1799 | JS: constants + data (`CARD_LIBRARY`, decklists, `DECKS`, `FACTION_POOLS`, `HERO_NAMES`) |
| 1800-2148 | JS: setup (deck build, side creation, `resetGame`, champion deploy, undo) |
| 2148-2916 | JS: turn/hand/combat rules engine (play card, resolve effects, damage, combat resolution) |
| 2916-3300 | JS: combat clash animation + end-turn + AI |
| 3272-3668 | JS: rendering (`render*` functions, overlaps combat-report rendering) |
| 3653-3721 | JS: log rendering, `escapeHtml` |
| 3721-3797 | JS: input (hover/touch card-peek), final bootstrap call |

Rendering and engine ranges overlap slightly (`3272-3300` AI vs render
functions interleave) — treat the DEC-CF-003 function list as authoritative
over the raw line ranges.

## Full function inventory (declaration order)

Setup: `buildDecklist`, `applyDeckIdentity`, `showDeckSelect`, `makeCard`,
`shuffle`, `createSide`, `resetGame`, `sideOf`, `otherSide`,
`controllerLabel`, `championDef`, `resetChampionTurnFlags`,
`championDeployReason`, `deployChampion`, `returnChampionToSlot`,
`saveUndo`, `clearUndo`, `canUndo`, `undoLastAction`, `aiConsiderChampion`,
`addLog`, `dealStartingHand`, `drawCard`, `refillHand`, `replaceCard`,
`startTurn`.

Engine/rules: `cardAttack`, `effectiveCost`, `isDamageCard`,
`isDamageSpell`, `damageHero`, `getCardCondition`, `canAttack`,
`usesCompactLayout`, `scrollZoneIntoView`, `scrollToTargets`,
`handleHandCard`, `getTargetInfo`, `isCardPlayable`,
`handUnavailableReason`, `handleUnitTarget`, `blockTargetReason`,
`assignBlock`, `playCard`, `resolveEffect`, `gainUnitHealth`, `buffUnit`,
`dealDamage`, `removeDeadUnits`, `beginPlayerAttack`, `aiChooseBlocks`,
`triggerCombatSurvival`, `resolveCombat`, `dealCombatDamage`.

Combat clash FX (candidate: keep with render, it's purely visual):
`clashDelay`, `buildClashCard`, `buildClashFx`, `spawnClashNumber`,
`showClashHit`, `flagClashCard`, `stageImpact`, `runBlockedClash`,
`runHeroClash`, `playClashSequence`.

End of turn / AI: `resolveEndTurnEffects`, `endPlayerTurn`, `endEnemyTurn`,
`scoreAiCardBase`, `scoreAiCard`, `aiMainPhase`, `chooseAiTarget`,
`aiDeclareAttackers`, `resolvePlayerBlocks`, `checkGameOver`.

Render: `updateBoardScrollIndicator`, `updateBoardScrollbars`,
`bindBoardScrollbar`, `render`, `renderEnemyHand`, `renderRelics`,
`renderChampionSlot`, `renderBoard`, `renderHand`, `createCardElement`,
`renderCardCatalog`, `getBlockingSnapshot`, `predictCombat`,
`renderBlockReview`, `renderCombatReport`, `renderPhase`, `renderLog`,
`escapeHtml`.

Input: `initCardPeek` (IIFE: `removePeek`, `removeTouchPeek`, plus
pointer/touch event wiring).

## Notes for implementers

- Everything currently lives inside one top-level `(() => { 'use strict';
  ... })()`. Splitting into separate `<script>` files means every
  variable currently closed over (`state`, `undoRecord`, `clashTimers`,
  etc.) needs a shared home — DEC-CF-002 says a single namespace object
  (e.g. `window.CF`), not bare globals, not ES modules.
- `handleHandCard`/`handleUnitTarget`/`assignBlock` are DOM-event
  entry points but call straight into engine logic — DEC-CF-003 keeps
  them in `engine.js`, not `input.js`. `input.js` should stay limited to
  the hover/touch card-peek gesture handling, which is genuinely
  self-contained (already its own IIFE at line 3721).
- The clash-animation functions (`buildClashCard` etc.) are visual-only
  and read combat data already computed by `resolveCombat` — good
  candidates for `render.js`, not `engine.js`, to keep game-rules logic
  free of DOM/animation concerns (supports the design principle "the
  interface must explain the current game state" without conflating
  state computation and presentation).
- TASK-208 (data.js extraction) is the recommended first slice: pure
  data, no function bodies, easiest to verify byte-for-byte equivalence
  of the extracted constants against the original.
