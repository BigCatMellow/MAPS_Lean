<!-- hpom: file: artifacts/tests/task-214-combat-parity.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: helper-clearfront-skeleton-01 (owner: claude-lab-gome) -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: TASK-214 implementation vs pre-214 app/ (index.html md5 57db33f4faba0b776b3ae8bb5a4292d9, state.js md5 d2f3b03300e9963ce23cf3912ec6e5e4) -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# TASK-214 — combat.js Extraction Parity Report

## Retrieval capsule

- Purpose: Records the parity evidence for extracting ClearFront's combat, card-play, end-turn, and AI behavior from the monolithic page into `app/js/combat.js` while preserving direct file loading.
- Proves: The combat function inventory, shared mutable `ctx.state` contract, cross-file `window.CF` calls, deterministic replay, blocking and AI coverage, undo preservation, and source-integrity checks.
- Applies to: TASK-214's combat extraction compared with the recorded pre-214 application baseline and the verification artifacts named in this report.
- Does not provide: Proof for later render or input extractions, online multiplayer, behavior after subsequent unrecorded edits, or authority to reinterpret known ClearFront rules deviations.
- Evidence type: test_evidence
- Status: historical

Packet structured per codex-lab-lilo's review checklist: (1) function
inventory, (2) ctx contract, (3) deterministic replay artifacts,
(4) combat/block/AI/end-turn coverage, (5) TASK-213 undo preservation,
(6) source/baseline hashes.

## 1. Function inventory

**38 functions moved** into `app/js/combat.js` via
`CF.installCombatModule(ctx)` (DEC-CF-005 and the task say "37" but
enumerate 38 names; gome confirmed over hcom the explicit list is
authoritative — same 25/26 pattern as TASK-212):

`cardAttack`, `effectiveCost`, `isDamageCard`, `isDamageSpell`,
`damageHero`, `getCardCondition`, `canAttack`, `usesCompactLayout`,
`scrollZoneIntoView`, `scrollToTargets`, `handleHandCard`,
`getTargetInfo`, `isCardPlayable`, `handUnavailableReason`,
`handleUnitTarget`, `blockTargetReason`, `assignBlock`, `playCard`,
`resolveEffect`, `gainUnitHealth`, `buffUnit`, `dealDamage`,
`removeDeadUnits`, `beginPlayerAttack`, `aiChooseBlocks`,
`triggerCombatSurvival`, `resolveCombat`, `dealCombatDamage`,
`resolveEndTurnEffects`, `endPlayerTurn`, `endEnemyTurn`,
`scoreAiCardBase`, `scoreAiCard`, `aiMainPhase`, `chooseAiTarget`,
`aiDeclareAttackers`, `resolvePlayerBlocks`, `checkGameOver`.

In pre-214 `app/index.html` these formed exactly two contiguous blocks
(lines 312–1075 `cardAttack`…`dealCombatDamage`, lines 1297–1435
`resolveEndTurnEffects`…`checkGameOver`), separated by the
clash-animation cluster (lines 1077–1295: `clashTimers`/`clashSkip` +
`clashDelay`…`playClashSequence`) which **stays inline** per DEC-CF-005
point 2. `resolveCombat` hands off to it via one `playClashSequence`
call. The render cluster (`updateBoardScrollIndicator`…`escapeHtml`),
event listeners, and bootstrap also stay inline.

Load order: `data.js` → `state.js` → `combat.js` → inline script
(declares bindings, builds `ctx`, `installStateModule(ctx)` then
`installCombatModule(ctx)`, destructures both, bootstraps). Plain
`file://`, no modules, no build step.

## 2. ctx contract (final shape, runtime-verified)

`CF.ctx` keys after this task — exactly 10, confirmed via CDP
`Object.keys` on the live page:

| key | kind | notes |
|---|---|---|
| `state` | accessor (get+set) | the only mutable binding combat.js touches (80 sites) |
| `undoRecord` | accessor (get+set) | used by state.js only |
| `uidCounter` | accessor (get+set) | used by state.js only |
| `playerDeckChoice` | accessor (get+set) | used by state.js only |
| `enemyDeckChoice` | accessor (get+set) | used by state.js only |
| `$` | stable host binding | used by state.js only |
| `refs` | stable host binding | state.js + combat.js (9 sites) |
| `render` | forwarded host fn | kept per DEC-CF-005 (22 combat sites) |
| `playClashSequence` | forwarded host fn | **added** per DEC-CF-005 (1 site, `resolveCombat`) |
| `renderCombatReport` | forwarded host fn | **added — scoping gap found during implementation**: `resolveCombat`'s completion callback calls it (pre-214 line 1056); it lives in the inline render cluster and wasn't in DEC-CF-005's list. Forwarded identically to `render`; approved by claude-lab-gome over hcom and recorded in the updated DEC-CF-005. |

**Removed** per DEC-CF-005: `checkGameOver`, `removeDeadUnits`,
`damageHero`, `aiMainPhase` — these moved into combat.js and are
`window.CF`-published; all callers use `CF.checkGameOver(...)` form.

Cross-module calls go through `CF.*` (late-bound at call time), never
ctx: combat.js calls 12 state.js functions this way (`CF.addLog` ×48,
`CF.sideOf` ×23, `CF.otherSide` ×15, `CF.controllerLabel` ×8,
`CF.clearUndo` ×5, `CF.saveUndo` ×4, `CF.championDef` ×3,
`CF.refillHand` ×3, `CF.replaceCard` ×2, `CF.startTurn` ×2,
`CF.returnChampionToSlot` ×1, `CF.aiConsiderChampion` ×1).

**state.js was also edited** (disclosed — not in TASK-214
`output_paths`; needs registering like TASK-208's `app/assets`): its
ctx destructure dropped the four removed keys, and its 6 call sites to
them became `CF.*` (`CF.checkGameOver` ×3, `CF.removeDeadUnits` ×1,
`CF.damageHero` ×1, `window.setTimeout(CF.aiMainPhase, 550)` ×1), plus
its header comment updated. This is unavoidable given DEC-CF-005 point
3: leaving state.js on the old ctx keys would destructure `undefined`s
and crash at call time.

Runtime `window.CF` totals: 11 data values + 26 state fns + 38 combat
fns + `installStateModule` + `installCombatModule` + `ctx` (66
functions), nothing else.

## 3. Verbatim-move proof

Both blocks extracted mechanically (`sed -n '312,1075p;1297,1435p'`),
then transformed by exactly three guarded, word-boundary rewrite
classes: (a) `...state` spread → `...ctx.state` (4 sites — new hazard
class vs TASK-212, disclosed because the TASK-212 guard alone would
have missed spread positions), (b) `state` → `ctx.state` (all other
non-property positions), (c) the 12 state.js call targets `name(` →
`CF.name(`. **Stripping `CF.` and `ctx.` back out reproduces the
original 903-line block byte-for-byte — the strip-back diff is empty.**
Zero non-mechanical-prefix diffs to disclose (TASK-212 had one
shorthand expansion; TASK-214 has none). `render`, `playClashSequence`,
`renderCombatReport`, and `refs` references stay textually verbatim
(destructured from ctx inside `installCombatModule`).

`node --check` (Node v22.23.1) passes on `combat.js`, the edited
`state.js`, and the remaining inline script (extracted and checked
separately).

## 4. Visual + functional parity

**Champion-select screenshot** (same flags as TASK-207/208/212):
`task214-pre214-champion-select.png` vs `task214-app-champion-select.png`
— **byte-identical**, md5 `fd85d1db8e3b326a58f9678384c6b198` both (and
equal to the 208/212 screenshots, as expected).

**Deterministic seeded replay** (TASK-212 technique; harness
`artifacts/tests/task214-cdp-fullturn.mjs`, extended for blocking and
multi-card turns). Registered replay artifacts, checked in:

- `task214-run-app-seed42.log` / `task214-run-pre214-seed42.log`
- `task214-run-app-seed7.log` / `task214-run-pre214-seed7.log`

For **both seeds**, new app vs pre-214 step logs and final states are
**diff-identical line-for-line**, with **zero console messages and zero
exceptions** across every run (4/4 RESULT PASS).

Coverage demonstrated in the seed-42 trace (identical on both
versions): card play across multiple turns (Seedling, Bark Guard, Ash
Runner — `playCard`/`resolveEffect` path), attacker selection + confirm
(`beginPlayerAttack` → `aiChooseBlocks` → `resolveCombat` →
`playClashSequence` hand-off → "attack complete"), **blocking**: real
blocker selection and block assignment during the enemy attack
(`handleUnitTarget`/`assignBlock`, projection changed "Take 1 damage" →
"Resolve: 0 damage"), block resolution (`resolvePlayerBlocks` →
`resolveCombat` → combat report overlay), **full AI turns** (enemy
played units and declared attacks — `aiMainPhase`/`aiDeclareAttackers`/
`chooseAiTarget`), and end-turn both directions
(`endPlayerTurn`/`endEnemyTurn`/`resolveEndTurnEffects`). Seed 7
additionally passes the same goal set on a different game line.

## 5. Undo preservation (TASK-212 trio + TASK-213 fix)

`task212-undo-check.mjs` rerun unmodified (seed 42) on both versions —
now exercising undo across **three** files (`handleHandCard`/`playCard`
in combat.js → `CF.saveUndo`/`CF.clearUndo` in state.js → bindings in
the inline host): **10/10 PASS on both**, including ordinary play
creating a working one-step undo, undo restoring hand/board, and
replacement leaving undo unavailable (TASK-213/INS-0025 semantics
intact — lilo's two handler lines in `handleHandCard`/`resolvePlayerBlocks`
moved to combat.js with `clearUndo` → `CF.clearUndo` as their only
change, covered by the empty strip-back diff).

## 6. source/ and baseline/ hashes (reproduced, not asserted)

- `cd source && sha256sum -c SHA256SUMS.txt` → exit 0, all listed files
  `OK` (`Clearfront.html`, `clearfront_rules.md`,
  `Game-card-combat-effects.zip`, assets).
- `baseline/index.html` md5 `5124cac23a9bd326bb8dfd00a110af92` —
  unchanged from the TASK-208/212 reports.
- Pre-214 inputs: `app/index.html` md5
  `57db33f4faba0b776b3ae8bb5a4292d9`, `app/js/state.js` md5
  `d2f3b03300e9963ce23cf3912ec6e5e4`.
- Post-214 outputs: `app/index.html` md5
  `732bb851cf1da009c2319393f4a70b0f`, `app/js/state.js` md5
  `093607954e3b96ea02047e90016c645a`, `app/js/combat.js` md5
  `c673752f0cf9ac1bf283d5f92c888b75`.

## Conclusion

TASK-214 acceptance criteria met: the 38 combat-layer functions live in
`app/js/combat.js` behind the established install/ctx pattern with the
ctx contract updated exactly per DEC-CF-005 (plus the gome-approved
`renderCombatReport` forwarding), proven byte-level verbatim by an
empty strip-back diff, and proven behavior-identical by byte-identical
screenshots plus two-seed deterministic replay covering play, attack,
block, combat resolution, end turn, and AI turns, with undo semantics
(TASK-212 + TASK-213) intact. Reported to claude-lab-gome for review
and MAP transition (helper does not self-submit). Note for the task
record: `app/js/state.js` needs registering as a TASK-214 output path.
