<!-- hpom: file: artifacts/tests/task-212-state-parity.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: helper-clearfront-skeleton-01 (owner: claude-lab-gome) -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: TASK-212 implementation vs pre-212 app/index.html (md5 fd7629350ec18e4c97ff9578b32b18ff, includes TASK-213 undo fix) -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# TASK-212 — state.js Extraction Parity Report

## What was done

Extracted the 26 deck/side/game-state functions listed in DEC-CF-004
(the task record's acceptance criterion says "25", but the task
description and DEC-CF-004 both enumerate 26 names — all 26 were moved:
`buildDecklist` … `startTurn`) from `app/index.html`'s inline IIFE into
`app/js/state.js`, loaded via `<script src="js/state.js">` between
`data.js` and the inline script. No ES modules, no build step; still
opens via plain `file://`.

The extraction baseline was the post-TASK-213 `app/index.html`
(md5 `fd7629350ec18e4c97ff9578b32b18ff`). Timeline note: lilo's TASK-213
undo fix was written to the file at 08:52 on 2026-07-17, *before* this
task's first snapshot, so the "re-snapshot after lilo submits" step
found zero byte drift — the fix was already in both. Verified present:
`handleHandCard`'s swap branch calls `clearUndo()` before
`replaceCard(...)` (one added call vs baseline). Both TASK-213 handler
lines live in code that stays inline — the extraction did not touch
them.

## The mutable-state sharing mechanism (binding for combat.js, TASK-213+)

DEC-CF-004 requires the shared mutable bindings — `state`, `undoRecord`,
`uidCounter`, plus `playerDeckChoice`/`enemyDeckChoice` — to stay
**declared once in `app/index.html`'s inline script**. But the moved
functions don't just mutate `state`'s contents, they **reassign the
bindings themselves** (`resetGame`/`undoLastAction` replace `state`
wholesale; `saveUndo`/`clearUndo` replace `undoRecord`; `makeCard`/
`deployChampion` increment `uidCounter`; `showDeckSelect` reassigns both
deck choices). A plain reference or one-time destructure cannot cross a
file boundary for reassignment, so the mechanism is a **shared accessor
context**:

1. The inline script (sole owner of the `let` declarations) builds a
   `ctx` object whose `state`/`undoRecord`/`uidCounter`/
   `playerDeckChoice`/`enemyDeckChoice` properties are **getter/setter
   pairs over its own closure bindings** — `ctx.state = v` writes the
   host's `state` binding; `ctx.state` always reads the current one.
   `ctx` also carries the stable host bindings the moved functions call:
   `$`, `refs`, `render`, `checkGameOver`, `removeDeadUnits`,
   `damageHero`, `aiMainPhase` (function declarations, hoisted, so the
   references are valid at wiring time).
2. `state.js` defines `CF.installStateModule(ctx)`. Calling it creates
   the 26 functions (which access all shared mutables exclusively as
   `ctx.<name>`), publishes them on `window.CF` (`Object.assign`),
   stores the contract as `CF.ctx`, and returns the function map.
3. The inline script calls it exactly where the functions used to be
   declared and destructures the return into IIFE-local `const`s — so
   every one of the ~170 existing call sites in the remaining inline
   code (`addLog` ×50, `sideOf` ×26, …) is textually untouched.

Load order: `data.js` (defines `CF` data) → `state.js` (defines
`CF.installStateModule`; nothing runs) → inline script (declares the
bindings, builds `ctx`, installs, then bootstraps `showDeckSelect()`).

**For TASK-213+ (combat.js):** consume the same contract. Either read
`CF.ctx` at call time or follow the same `installX(ctx)` pattern; access
every shared mutable as `ctx.<name>` (never destructure them — a
destructured copy goes stale on reassignment); stable host functions may
be destructured freely. New shared mutables must be added as accessor
pairs in the inline script's `ctx` literal.

## Verbatim-move proof

The 26 function bodies were extracted mechanically (`sed -n '288,634p'`)
and transformed only by a guarded, word-boundary rewrite of the five
shared identifiers to `ctx.<name>` (guards exclude property positions
like `undoRecord.state`). Stripping `ctx.` back out of the transformed
block and diffing against the original shows exactly **one** non-prefix
change: `saveUndo`'s object shorthand `{ …, uidCounter }` became
`{ …, uidCounter: ctx.uidCounter }`, which strips back to
`uidCounter: uidCounter` — semantically identical. No other logic
change of any kind.

## Acceptance criteria checks

1. **All listed functions moved verbatim.** All 26 (see verbatim-move
   proof above). Runtime check: `window.CF` exposes exactly the 11 data
   values + 26 state functions + `installStateModule` + `ctx`;
   `CF.ctx` exposes exactly the 5 accessors + 7 host bindings.
2. **Sharing mechanism explicit and documented.** Section above.
3. **Visual + functional parity via `file://`.** Sections below.
4. **`node --check` passes** on `app/js/state.js` and on the remaining
   inline script (extracted and checked separately). Node v22.23.1.
5. **`source/` and `baseline/` untouched.** All writes went to
   `app/index.html`, `app/js/state.js`, and `artifacts/tests/`.
   `baseline/index.html` md5 unchanged:
   `5124cac23a9bd326bb8dfd00a110af92`.

## Visual parity (headless Chromium screenshot)

Identical flags as prior reports (`--headless=new --disable-gpu
--window-size=1280,900 --hide-scrollbars --virtual-time-budget=5000`),
champion-select screen, new app vs pre-212 snapshot:

- `artifacts/tests/screenshots/task212-pre212-champion-select.png`
- `artifacts/tests/screenshots/task212-app-champion-select.png`

**Byte-identical** — md5 `fd85d1db8e3b326a58f9678384c6b198` for both
(also equal to the TASK-208 screenshots' md5, as expected: no visual
surface changed since).

## Functional parity (CDP, deterministic seeded games)

Harness: `artifacts/tests/task212-cdp-fullturn.mjs` (plain Node, CDP
over built-in WebSocket, real `Input.dispatchMouseEvent` clicks with
hit-test-verified coordinates). It adaptively drives: deck select →
play a card → select attacker → confirm attack → end turn, while
resolving enemy blocking phases, clash animations, and report overlays.

**Key method upgrade over TASK-207/208:** the harness injects a seeded
`Math.random` (mulberry32) via `Page.addScriptToEvaluateOnNewDocument`
before any page script runs, so both page versions play the **same
game** — removing deck/hand/AI randomness from the comparison entirely.

Seed 42, new app vs pre-212 (logs checked in:
`task212-run-app-seed42.log` / `task212-run-pre212-seed42.log`):

- Step sequences **identical line-for-line** (`diff` empty): play
  "Seedling" (turn 1), end turn, attack with it (turn 2), attack
  resolves, end turn, enemy attacks for 1, resolve, stop at player main
  turn 3.
- Final DOM state **identical**: life 19/20, mana 3/3, hand 3 (2
  clickable), board 1, same phase text.
- **Zero console messages, zero exceptions** on both, full session.
- Both runs: RESULT PASS (played + attacked + ended turn after attack).

Supplementary unseeded runs: pre-212 PASS (play/attack/end turn); a new
-app unseeded run earlier in the session ran a complete game to the
game-over screen (7 turns, multiple enemy combats) with zero console
messages and zero exceptions. One unseeded new-app run drew a hand whose
only playable card was a target-mode spell — verified to be game
behavior, not a regression, by the seeded identical-game comparison; the
harness now skips such cards instead of retrying.

## Undo regression (cross-file `saveUndo`/`canUndo`/`undoLastAction` + TASK-213)

The undo trio moved to `state.js` while its callers and the TASK-213
fix stayed inline, so the undo path now crosses the file boundary in
both directions. Dedicated check
(`artifacts/tests/task212-undo-check.mjs`, seed 42, both versions):

| check | new app | pre-212 |
|---|---|---|
| undo disabled before any action | PASS | PASS |
| ordinary play enables undo | PASS | PASS |
| undo restores hand/board, then disables | PASS | PASS |
| re-play re-arms undo snapshot | PASS | PASS |
| swap-replacement consumes swap, hand changed | PASS | PASS |
| **undo UNAVAILABLE after replacement (TASK-213/INS-0025)** | PASS | PASS |
| zero console / zero exceptions | PASS | PASS |

10/10 assertions on both versions.

## Conclusion

TASK-212 acceptance criteria met: the 26 state-layer functions live in
`app/js/state.js` behind an explicit, documented shared-mutable-state
contract (`CF.installStateModule(ctx)` with accessor-backed bindings
declared once in the host), and the app is pixel- and
behavior-identical to its pre-212 self under deterministic seeded
replay, including the TASK-213 undo semantics. Reported to
claude-lab-gome for review and MAP transition (helper does not
self-submit).
