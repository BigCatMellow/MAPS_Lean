# ClearFront UI Redesign — Kickoff & Locked Direction (2026-07-19)

- status: DIRECTION LOCKED by operator (bigboss), 2026-07-19
- lead: claude-lab-lure (per project brief: "Claude leads and orchestrates")
- art support: codex (kiri) — type glyphs
- context: This is the G1 "prove-it" milestone from
  `MAP_System/artifacts/planning/map-project-improvement-kickoff-2026-07-19.md` —
  real product work driven through MAP, UI-first.

## Problem (operator's words + verified causes)

"If a game doesn't have a clean UI, the rules don't matter." The UI must feel
clean and usable, ideally **one screen with no scrolling**, without feeling
tight (constricting) or wasteful (dead negative space).

Verified root causes in the current `app/`:

1. `.app { min-height: 100vh }` lets the page grow past the viewport → it
   scrolls. Never locked to one screen.
2. A fixed 310px column holds always-on reference text (How to play / Champions
   / Keywords / Log) that **duplicates the Rules and Cards modals** — the single
   biggest wasted-space offender.
3. Board is **mirror-symmetric**: enemy and player get identical footprints,
   though the enemy side is mostly hidden/non-interactive info.
4. ~10 stacked zones with large min-heights (board 150–180px, relics 80px ×2)
   overflow vertically — board scrollbars already exist, proving space pressure.
5. Card type is shown as full decorative `.card-art` PNG + text label; there is
   **no compact type glyph** for a dense/collapsed state.
   (`app/assets/card-{unit,spell,relic}.png` exist but are full-art, wired at
   `render.js:446` — not solving collapse.)

## Locked decisions

### D1 — Layout: SIDE RAILS + CENTER
- Left/right vertical **rails** hold all chrome: player + enemy status
  (portrait, life, mana), relics, champion slots, mana.
- **Center column is pure play**: enemy board (top) → phase divider → your board
  (bottom) → your hand + action buttons. Boards get full height.
- Reference sidebar (310px) is **removed**; its content stays reachable through
  the existing Rules / Cards / Log modals.
- Whole game **locks to one viewport (100dvh), zero page scroll** on desktop.

### D2 — Card density: COLLAPSED GLYPH TILES, EXPAND ON HOVER/TAP
- Board + hand cards default to a compact tile: **type glyph + cost +
  attack/health** only.
- Hover (desktop) / tap (touch) reveals the full card (existing full render with
  text + keywords). No information is lost, only deferred.
- Type glyphs: **⚔ Unit · ✦ Spell · ◆ Relic** — the primary at-a-glance ID.

## Ownership split (no file overlap — anti-collision by design)

- **codex (kiri):** generate the 3 type-glyph images ONLY.
  Output paths: `app/assets/glyph-unit.png`, `app/assets/glyph-spell.png`,
  `app/assets/glyph-relic.png`.
- **claude (lure):** layout + density implementation.
  Output paths: `app/index.html`, `app/styles/clearfront.css`,
  `app/js/render.js`. Wires the glyphs once delivered.

## Milestone acceptance (observable)

1. On a desktop viewport the full game fits in 100dvh with **no page scroll**;
   both boards visible without scrolling the page.
2. Board + hand cards render as collapsed glyph tiles by default; hover/tap
   reveals full card text; **no information lost** vs. current.
3. The three type glyphs are visually distinct and present on every relevant
   card.
4. `scripts/test_all.mjs` passes — game logic parity, no rules/state regression
   (this milestone is presentation-only).
5. On a narrow (mobile portrait) viewport there is **no horizontal scroll**; the
   rails reflow to compact top/bottom bars. (Implementation detail owned by the
   layout lead; the side-rails choice is the desktop target.)

## Status update — 2026-07-19 (operator)

- Layout direction (side-rails + glyph tiles + champion faces/art + themed
  boards + relics-to-the-side + bigger card/champion text) is **APPROVED** via
  iterative mockup (v6). Champion slots use the clean-alpha edited art
  (`lionedited.png` / `badgeredited.png`) zoomed to fill.
- Clash-animation screen (horizontal face-off + gold rune divider) was
  prototyped and **TABLED** by operator — revisit after a working prototype.
- **Current priority: port the approved layout into the real app so the game
  actually plays** (`app/index.html`, `app/styles/clearfront.css`,
  `app/js/render.js`), keeping game logic byte-identical and `test_all.mjs`
  green. This is the G1 "working prototype" milestone.

## Stage 1 COMPLETE — 2026-07-19 (claude-lab-lure)

Ported the approved side-rails design into the real app; game is playable with
the new look. **`scripts/test_all.mjs` → 10/10 checks pass** (game logic
unchanged; verified via headless chromium screenshot too).

- `app/index.html`: restructured `.layout` → `.board-grid` (lrail / arena /
  rrail); all element IDs preserved. Emptied `playerDeckName`/`enemyDeckName`
  static placeholders (they collided with the undo test's deck-select finder).
- `app/styles/clearfront.css`: appended side-rails CSS block (overrides reused
  `.app`/`.arena`); boards themed, relics in a side slot, actions in phase bar,
  log in left rail.
- `app/js/render.js`: `createCardElement` uses `assets/champ-<deck>.png` for
  commander cards.
- `app/js/` (inline in index.html): procedural themed board-bg canvas painter.
- `app/assets/champ-{lion,badger,stag,raven,owl,fox}.png`: clean champion
  cutouts (edited lion/badger have real alpha; others flood-filled from the
  checkerboard originals).

## Stage 2 COMPLETE — 2026-07-19 (claude-lab-lure)

In-play cards now render as the mockup's compact glyph tiles; the game matches
the approved design and stays playable. **`scripts/test_all.mjs` → 10/10.**

- `app/js/render.js`: `createCardElement` flattened; card art switched to
  `assets/glyph-{unit,spell,relic}.png` (champions still use `champ-<deck>.png`).
- `app/styles/clearfront.css`: flat base card; compact tiles scoped to
  `.board .card` / `.tray .card` (type+text hidden in tile, shown in the
  existing hover-peek / Cards catalog which reveal the full card); champion slot
  shows the animal art prominent with name/keyword/status/stats below.
- Verified via headless-chromium screenshots: champion lion/fox art visible,
  glyph hand+board tiles, themed boards, relics to the side, actions in phase bar.

## Stage 3 — fidelity fixes at the operator viewport — 2026-07-19 (claude-lab-lure)

Operator caught that the build did NOT match the mockup at their window width
(~963px) even though it looked right at 1440px — the exact failure now recorded
as [[INS-0031]] / promoted rule (PROMO-0012). Fixes:

- **Root-cause bug:** the side-rails were `aside` elements and the legacy
  stylesheet's `aside { grid-template-columns:1fr 1fr }` / `aside { display:none }`
  rules hijacked them, collapsing champions to 2 tiny columns and crushing the
  log — only at narrow widths. Fix: rails changed from `aside` to `div`.
- Champions now cover-fill their boxes (badger/stag/lion etc.), stacked.
- CLEARFRONT gradient wordmark; phase-bar wraps cleanly (actions to a 2nd row)
  instead of forcing a tall vertical wrap at narrow widths.
- **Verified with screenshots at 963px (operator target) AND 1280px**; matches
  the mockup at both. `test_all.mjs` → 10/10.

Deferred (non-blocking): tabled clash animation.

## Notes / open implementation calls (lead-owned, not operator gates)

- Glyph spec for Codex: small, clean, transparent-background marks that read at
  ~24–32px on a dark faction palette; one each for Unit/Spell/Relic; distinct
  silhouettes (not color-only, for accessibility).
- Mobile reflow: rails → thin top (enemy) / bottom (you) status bars; center
  boards stay stacked. Chosen over re-asking the operator.
- Parity discipline: no change to `data.js` / `state.js` / `combat.js`; this is
  a presentation refactor.
