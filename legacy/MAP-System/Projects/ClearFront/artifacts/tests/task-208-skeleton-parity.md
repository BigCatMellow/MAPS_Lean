<!-- hpom: file: artifacts/tests/task-208-skeleton-parity.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: helper-clearfront-skeleton-01 (owner: claude-lab-gome) -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-16 -->
<!-- hpom: verified_against: TASK-208 implementation, baseline/index.html (md5 5124cac23a9bd326bb8dfd00a110af92) -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# TASK-208 — Multi-File Skeleton Parity Report

## What was done

Split `baseline/index.html` (3797 lines, single inline `<style>` + single
inline IIFE `<script>`) into the first multi-file skeleton under `app/`,
per DEC-CF-002 (plain global `<script src>` files sharing a single
`window.CF` namespace — no ES modules, no build step, no server) and
DEC-CF-003 (module boundaries):

- `app/styles/clearfront.css` — baseline lines 11–1398 (the `<style>`
  block content), loaded via `<link rel="stylesheet">`.
- `app/js/data.js` — pure data, wrapped in an IIFE with `'use strict'`:
  baseline lines 1655–1659 (`MAX_BOARD`, `MAX_RELICS`, `HAND_LIMIT`,
  `STARTING_HAND`, `MAX_CARDS_PER_TURN`), 1661–1758 (`CARD_LIBRARY`),
  1760–1778 (decklist comment, `PLAYER_DECKLIST`, `AI_DECKLIST`,
  `DECKS`), 1797–1798 (`FACTION_POOLS` + its population loop), and 2914
  (`HERO_NAMES` — declared mid-engine in the baseline but listed as data
  by DEC-CF-003 and the TASK-208 acceptance criteria, so it moves here).
  All eleven values are published on the shared namespace via
  `window.CF = Object.assign(window.CF || {}, {...})` — no bare globals.
- `app/index.html` — head/meta (baseline 1–9, including the
  `window.__resources` map), the stylesheet `<link>`, body markup
  (baseline 1400–1650), `<script src="js/data.js">`, then the remaining
  inline IIFE (engine/render/input) unchanged except for the removed data
  section: one added line at the top of the IIFE destructures the eleven
  `window.CF` values into IIFE-local `const`s so every downstream
  reference is untouched. `HERO_NAMES`' original declaration line (2914)
  is removed to avoid a duplicate-`const` SyntaxError. Engine, render,
  and input code otherwise stays byte-identical inline (moves in
  TASK-209+).
- `app/assets/` — copy of `baseline/assets/` (6 portrait PNGs).
  `window.__resources` resolves portraits relative to the HTML file, so
  `app/` cannot render (or pass parity) without them. Originally outside
  TASK-208's declared `output_paths`; flagged to the task owner
  (claude-lab-gome), who registered `Projects/ClearFront/app/assets/` on
  the task record before submission. All 6 copies verified byte-identical
  to the baseline originals via `cmp`.

Load order in `app/index.html`: `__resources` head script → stylesheet →
markup → `data.js` (defines `window.CF`) → inline engine script
(consumes `window.CF`). Opens directly via `file://`; no server, no
build step, no `type="module"`.

## Acceptance criteria checks

1. **CSS byte-identical modulo `<style>` tags.** Extracted mechanically
   with `sed -n '11,1398p'`; verified:
   `diff <(sed -n '11,1398p' baseline/index.html) app/styles/clearfront.css`
   → empty (exit 0).
2. **data.js defines the eleven data values on a single `window.CF`, no
   bare new globals.** The data bodies are verbatim `sed` copies;
   verified byte-identical against the baseline source lines:
   `diff <(sed -n '1655,1659p;1661,1758p;1760,1778p;1797,1798p;2914p' baseline/index.html) <(sed -n '4,8p;10,107p;109,127p;129,130p;132p' app/js/data.js)`
   → empty (exit 0). The only additions are the IIFE wrapper and the
   `window.CF` `Object.assign` publish block. Runtime check (CDP,
   below): `Object.keys(window.CF)` = `AI_DECKLIST, CARD_LIBRARY, DECKS,
   FACTION_POOLS, HAND_LIMIT, HERO_NAMES, MAX_BOARD, MAX_CARDS_PER_TURN,
   MAX_RELICS, PLAYER_DECKLIST, STARTING_HAND` (all 11, nothing else).
   Both `app/js/data.js` and the app's inline script pass
   `node --check` (Node v22.23.1).
3. **Visual + functional parity via `file://`.** See the two sections
   below — screenshot byte-identical, smoke test clean.
4. **`baseline/` and `source/` untouched.** Every write in this task
   went under `app/` and `artifacts/tests/`; `baseline/` was only ever
   read (`sed -n`/`grep`/screenshot). Note `Projects/ClearFront/` is
   currently untracked in git, so `git status` cannot independently
   attest this — recorded here for the reviewer: baseline/index.html
   md5 after the task is `5124cac23a9bd326bb8dfd00a110af92`.
5. **Evidence recorded in this file, TASK-207 report format.** Yes.

## Visual parity (headless Chromium screenshot)

Rendered both pages headless with identical flags
(`chromium --headless=new --disable-gpu --window-size=1280,900
--hide-scrollbars --virtual-time-budget=5000`) at the initial
champion-select screen:

- `artifacts/tests/screenshots/task208-baseline-champion-select.png`
- `artifacts/tests/screenshots/task208-app-champion-select.png`

Both files are **byte-identical** — md5
`fd85d1db8e3b326a58f9678384c6b198` for both — pixel-for-pixel parity
including all 6 deck portraits loaded from the copied `app/assets/`.

## Functional parity (Chrome DevTools Protocol interaction)

Harness checked in at `artifacts/tests/task208-cdp-smoke.mjs` (plain
Node ≥21, no dependencies — talks CDP over the built-in WebSocket).
Run: `chromium --headless=new --remote-debugging-port=<port>
--user-data-dir=<tmp> about:blank &` then
`node task208-cdp-smoke.mjs <port> file://.../app/index.html <shot.png>`.

Per page it: navigates, waits for load, asserts the deck-select overlay
state, clicks the first deck option ("Emberwild") with real
`Input.dispatchMouseEvent` press/release (not `.click()`), waits, asserts
post-click DOM state, screenshots, and reports every
`Runtime.consoleAPICalled` / `Runtime.exceptionThrown` for the whole
session.

Results, app vs baseline reference run:

| check | app | baseline |
|---|---|---|
| deck-select overlay shown, 6 options, first = "Emberwild" | yes | yes |
| `window.CF` keys | all 11 | (none — expected) |
| overlay dismissed after click | yes | yes |
| player deck | Emberwild | Emberwild |
| enemy deck (game's own random rival pick) | Verdant Court | Gilded Vigil |
| hand cards at turn 1 | **3** | **3** |
| life | 20 / 20 | 20 / 20 |
| mana | 1/1 | 1/1 |
| phase title | "Your turn" | "Your turn" |
| hand label | "Your hand · cards played 0/2" | same |
| console messages (full session) | **0** | **0** |
| exceptions (full session) | **0** | **0** |

The only divergence is the enemy deck name, which `showDeckSelect`
assigns with `Math.random()` from the 5 non-chosen decks in both pages —
inherent game behavior, not a parity break.

Post-click screenshots (not expected to be comparable byte-wise because
of the random rival + hand draw):

- `artifacts/tests/screenshots/task208-app-after-champion-click.png`
- `artifacts/tests/screenshots/task208-baseline-after-champion-click.png`

## Notes for follow-on tasks (TASK-209+)

- The inline IIFE now begins with a single destructure of `window.CF`;
  when engine/render/input move to their own files, each will need the
  same pattern (or direct `CF.` access) — DEC-CF-002's namespace rule.
- `playerDeckChoice` / `enemyDeckChoice` (mutable, initialized from
  `DECKS`) and the `refs`/`$` DOM helpers deliberately stayed inline —
  they are state/DOM, not data.
- Two consecutive blank lines exist where the data section was lifted
  out (cosmetic only; kept to preserve every remaining baseline line
  byte-for-byte).

## Conclusion

TASK-208 acceptance criteria met: `app/` is a working multi-file
skeleton, visually and functionally identical to `baseline/index.html`
over plain `file://`, with CSS and all data extracted onto `window.CF`
and the engine untouched inline. Reported to claude-lab-gome for review
and MAP task-state transition (helper does not self-submit).
