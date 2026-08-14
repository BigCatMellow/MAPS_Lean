# ClearFront UI Redesign Continuity and QA Packet

- Date: 2026-07-19
- Task: TASK-253
- Prepared by: codex-lab-kiri
- Production implementation owner: claude-lab-lure
- Status: continuity packet ready; production integration has not started
- Governing kickoff: `Projects/ClearFront/notes/ui-redesign-kickoff-2026-07-19.md`
- Preserved prototype: `Projects/ClearFront/prototypes/clearfront-side-rails-2026-07-19.html`

## 1. Purpose and boundary

This packet preserves the latest visual prototype and turns the operator's
successive UI comments into an implementation and verification handoff. It is
not authorization to change game rules, card data, or the governing source
documents.

The production ownership boundary remains intact:

- Claude owns `app/index.html`, `app/styles/clearfront.css`, and
  `app/js/render.js` for this redesign.
- Kiri's production contribution remains the three glyph PNGs already submitted
  under TASK-252.
- TASK-253 adds only this packet and a preserved prototype. It does not modify
  production HTML, CSS, JavaScript, game mechanics, or source provenance.

This matters because the prototype is a design reference, not production code.
It contains static demonstration state, embedded base64 images, and mock values
that must not replace the real renderer or game data.

## 2. Current verified state

At the time of this packet:

- The production `app/index.html`, `app/styles/clearfront.css`, and
  `app/js/render.js` still have their July 17 modification times. Claude's UI
  redesign has not yet been ported into them.
- The three generated glyphs are present at
  `app/assets/glyph-{unit,spell,relic}.png`.
- Claude's latest layout exists as a standalone static prototype, now preserved
  durably outside `/tmp`.
- The current production baseline passes every check in `scripts/test_all.mjs`.

### Pre-integration automated baseline

Command run from `Projects/ClearFront/` on 2026-07-19:

```text
node scripts/test_all.mjs
```

Result: **PASS, 9 of 9 checks**.

| Check | Baseline |
|---|---|
| Syntax: `combat.js` | PASS |
| Syntax: `data.js` | PASS |
| Syntax: `input.js` | PASS |
| Syntax: `render.js` | PASS |
| Syntax: `state.js` | PASS |
| Extractor regressions | PASS |
| Engine rule matrix | PASS |
| Browser input preview | PASS |
| Browser undo | PASS |

This is the comparison point for the eventual presentation-only integration.

## 3. Prototype preservation record

The prototype was copied byte-for-byte from Claude's session scratchpad before
the reset window.

| Field | Value |
|---|---|
| Source | `/tmp/claude-1000/-home-mellow-Projects-MultiAgentProject-Source/50955350-d702-4849-bdd6-4834bdfd6a28/scratchpad/clearfront-side-rails.html` |
| Durable copy | `Projects/ClearFront/prototypes/clearfront-side-rails-2026-07-19.html` |
| Source modified | 2026-07-19 10:43:50.130809079 EDT |
| Size | 132,739 bytes |
| Lines | 396 |
| SHA-256, source | `d98427f3772ca8f6215cef852ed9baffc1715e9e59e43904ce28beb862cfbde7` |
| SHA-256, copy | `d98427f3772ca8f6215cef852ed9baffc1715e9e59e43904ce28beb862cfbde7` |
| Preservation result | PASS: sizes and hashes match |

The copy intentionally retains the prototype's embedded images and static
sample data. Editing the preserved file would erase its value as a recovery
point; further mockup iterations should use a new versioned file.

## 4. Direction ledger

### 4.1 Locked foundation

These decisions remain the redesign foundation:

1. Desktop uses side rails around a center play area.
2. The full game fits within one desktop viewport without document scrolling.
3. Board and hand cards use a compact state with distinct Unit, Spell, and
   Relic glyphs.
4. Full card information remains available through hover on pointer devices and
   tap on touch devices.
5. The reference-text sidebar is removed. Rules and card reference material
   remains available through modals.
6. The work is presentation-only. Game state, mechanics, card definitions, and
   rule behavior do not change.

### 4.2 Changes already represented in prototype v3

The preserved prototype already demonstrates the following operator-driven
iterations:

- Hover details render in a viewport-clamped floating layer instead of inside
  the board's clipped overflow region.
- The left rail uses enemy status, a live battle log, and player status, filling
  the previously empty middle space. This is the latest direction and replaces
  the earlier idea that all log information would live only in a modal.
- The right rail contains both Champion panels and faces.
- Real Unit, Spell, and Relic glyphs replace text placeholders.
- Three hand cards spread across the full tray width.
- Undo, Swap, and Attack controls sit in the phase strip between the boards.
- Unit rows are centered rather than left-aligned.
- Emberwild and Iron Covenant receive distinct procedural Canvas atmospheres.
- Board card art has a fixed height, tiles are taller, and stats are pinned to
  the bottom so keywords cannot cover names.
- Relics occupy a visually divided field slot rather than appearing in the unit
  line, and duplicate rail relic pills are removed.

### 4.3 Latest operator correction not yet applied

The final feedback arrived after Claude reached the monthly spend limit. It is
therefore **outstanding**, not implemented:

1. Card tiles still have too much negative space. Increase the useful text size
   to occupy the available area more comfortably.
2. Champion panels have the same problem. Increase Champion name, ability, and
   supporting text size so the rail reads as intentional rather than sparse.
3. Use the new lion artwork for Ember Warden and badger artwork for Iron Warden
   as larger Champion-card/background treatments, rather than relying only on
   small portrait squares. The goal is to fill the Champion panel while keeping
   text readable.

The preserved prototype shows why this remains open: its board-card name is
`.6rem`, keyword text `.5rem`, effect text `.56rem`, Champion ability text
`.63rem`, and Champion name `.8rem`. These values are a starting point, not an
accepted final typography scale.

## 5. User-supplied asset inventory

The operator added nine files to `Projects/ClearFront/assets/`. A visual contact
sheet and channel inspection were performed without changing the files.

| Asset | Dimensions / channels | Known relationship | Readiness |
|---|---|---|---|
| `lion.png` | 1254x1254 RGB | Explicitly selected for Ember Warden / Emberwild | **Needs cleanup:** the visible checkerboard is baked into RGB pixels; it is not transparent |
| `badger.png` | 1024x1536 RGBA | Explicitly selected for Iron Warden / Iron Covenant | True alpha is present; portrait composition needs a Champion-panel crop/contain test |
| `crow.png` | 1254x1254 RGB | Likely related to code deck id `raven`, but the name differs | Not operator-confirmed; baked checkerboard must be removed before use |
| `fox.png` | 1254x1254 RGB | Matches the existing fox deck identity | Not selected for this two-side pass; baked checkerboard |
| `owl.png` | 1254x1254 RGB | Matches the existing owl deck identity | Not selected for this two-side pass; baked checkerboard |
| `stag.png` | 1254x1254 RGB | Matches the existing stag deck identity | Not selected for this two-side pass; baked checkerboard |
| `unit.png` | 1254x1254 RGB | Alternate full Unit illustration | Not needed for the compact glyph lane; baked checkerboard |
| `spell.png` | 1254x1254 RGB | Alternate full Spell illustration | Not needed for the compact glyph lane; baked checkerboard |
| `relic.png` | 1254x1254 RGB | Alternate full Relic illustration | Not needed for the compact glyph lane; baked checkerboard |

Only the lion-to-Ember-Warden and badger-to-Iron-Warden assignments are locked
for this pass. Other apparent mappings must not be silently treated as product
decisions.

Before production use, the lion needs real background removal and an edge check
against both faction panels. The badger should be tested at the actual rail
aspect ratio. Both should be normalized to an appropriate delivery size after
the layout establishes their rendered dimensions; shipping the full source
resolution is unnecessary.

## 6. Prototype hazards that must not leak into production

1. **Static values are not canonical game data.** The prototype displays Ember
   Warden as `4 / 5` and Iron Warden as `3 / 6`, while current `data.js` defines
   them as `4 / 6` and `3 / 9`. Production must continue to render from real
   state and definitions.
2. **Sample cards are illustrative.** Names, text, stats, and relic effects in
   the mockup are not a new card set.
3. **Pointer behavior is incomplete.** The prototype listens to `mouseenter`
   and `mouseleave`; it does not yet demonstrate keyboard focus or the locked
   touch/tap detail behavior.
4. **Mobile is not proven.** A media query exists, but no captured mobile result
   proves the full controls, rails, boards, and hand fit without horizontal
   overflow or inaccessible content.
5. **Canvas backgrounds are atmosphere, not state.** They may be reused as a
   visual technique, but must not obscure cards, consume input events, or become
   required for game information.
6. **Embedded base64 is prototype-only.** Production should use normal asset
   paths and existing resource mapping rather than copying the embedded payloads.

## 7. Integration acceptance matrix

The redesign is ready for review only when the following are observed in the
real app, not merely in the static prototype.

### 7.1 Desktop layout

Test at minimum at 1366x768, 1440x900, and 1920x1080.

| Check | Pass condition |
|---|---|
| Document fit | `document.documentElement.scrollHeight <= window.innerHeight` and no document-level vertical scrollbar |
| Horizontal fit | `scrollWidth <= innerWidth`; no rail, popup, or hand card extends past the viewport |
| Information hierarchy | Status left, play center, Champions right; boards remain the dominant visual region |
| Board composition | Partial unit rows are centered; relics remain visually separate from combat units |
| Hand composition | At three cards, the hand uses the tray width without looking clumped or leaving the action controls in its row |
| Controls | Undo, Swap, and Attack remain visible, readable, and reachable in the phase/action strip |
| Left rail | Live log fills the middle area without crowding status; its own scrolling does not scroll the page |
| Right rail | Champion art uses the panel meaningfully, and names, abilities, and stats remain readable over it |

### 7.2 Card readability and detail behavior

| Check | Pass condition |
|---|---|
| Compact identity | Unit, Spell, and Relic remain distinguishable by silhouette at normal rendered size |
| Name safety | No glyph, cost, keyword, or stat overlaps or hides the card name |
| Useful typography | Card and Champion text is visibly larger than prototype v3 where the extra space allows it; no essential text is clipped |
| Full information | Hover, keyboard focus, and touch/tap can expose every name, rule text, keyword, cost, and relevant stat available before the redesign |
| Popup bounds | The detail surface stays completely inside the viewport at all four edges and above board clipping contexts |
| Dismissal | Pointer exit, Escape/focus movement, and a second tap or outside tap dismiss detail without triggering an unintended game action |
| Selection clarity | Ready, selected, targetable, unavailable, owner, and Champion states remain visually distinct after compaction |

### 7.3 Champion and art checks

| Check | Pass condition |
|---|---|
| Correct mapping | Lion appears only with Ember Warden/Emberwild; badger appears only with Iron Warden/Iron Covenant in this pass |
| No fake transparency | No grey/white checkerboard or chroma fringe is visible in the real UI |
| Contrast | Champion text and controls meet readable contrast over both illustrations at each tested viewport |
| Focal safety | Faces and defining silhouettes are not cropped by responsive panel changes |
| Performance | Art is delivered at a reasonable size and does not introduce visible layout delay or repeated decoding work |

### 7.4 Mobile and alternate input

Test at minimum at 390x844 portrait and 844x390 landscape.

| Check | Pass condition |
|---|---|
| Reflow | Rails become compact status areas without covering the boards or hand |
| Width | No horizontal document scroll |
| Touch detail | A card can be inspected and then acted on without hover and without accidental play/attack |
| Controls | Primary actions remain reachable without precision tapping or hidden overflow |
| Text | Increased typography does not reintroduce overlap at narrow widths; an explicit compact breakpoint may reduce it where necessary |

### 7.5 Regression gate

1. Run `node scripts/test_all.mjs`; all nine baseline checks must remain green.
2. Confirm no edits to `app/js/data.js`, `app/js/state.js`, or
   `app/js/combat.js` unless a separately authorized gameplay task owns them.
3. Exercise: new game/deck selection, play unit/spell/relic, deploy Champion,
   select attackers/blockers, Undo, Swap, end/advance turn, and open/close the
   Rules, Cards, and Log surfaces.
4. Verify real state values are used everywhere; compare Champion stats against
   `data.js`, not the prototype.

## 8. Required evidence destinations for integration

The future integration task should register these or equivalent durable paths
before producing evidence:

- `Projects/ClearFront/artifacts/ui-redesign/g1-desktop-1366x768.png`
- `Projects/ClearFront/artifacts/ui-redesign/g1-desktop-1440x900.png`
- `Projects/ClearFront/artifacts/ui-redesign/g1-mobile-390x844.png`
- `Projects/ClearFront/artifacts/ui-redesign/g1-card-detail-bounds.png`
- `Projects/ClearFront/artifacts/ui-redesign/g1-qa-results.md`

The QA report should record viewport, browser/runtime, test commands and results,
known limitations, and direct links to the captures. `/tmp` screenshots and a
Claude artifact URL are useful working material but are not durable completion
evidence.

## 9. Resume plan for Claude

1. Read this packet and the locked kickoff note.
2. Use the preserved v3 prototype as the recovery baseline; do not depend on the
   original scratchpad or external artifact link.
3. Apply the outstanding typography and Champion-art correction in a new
   versioned mockup or directly during the controlled port.
4. Route lion background removal/normalization back to Kiri as a separate asset
   output if needed; do not ship its baked checkerboard.
5. Port layout structure and interaction behavior into the three Claude-owned
   production files while continuing to read all state from the existing game
   engine.
6. Add keyboard and touch behavior that the prototype does not yet prove.
7. Run the acceptance matrix and `scripts/test_all.mjs`, capture the registered
   durable evidence, then request independent review.

## 10. Handoff summary

Nothing needed for Claude's return has to be reconstructed from chat memory:
the latest prototype is preserved, every applied and outstanding direction is
separated, asset readiness is explicit, the clean baseline is recorded, and the
post-integration proof requirements are concrete. Production ownership remains
collision-free.
