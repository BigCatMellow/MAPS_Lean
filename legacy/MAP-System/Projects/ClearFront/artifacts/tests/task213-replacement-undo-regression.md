<!-- hpom: file: artifacts/tests/task213-replacement-undo-regression.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: codex-lab-lilo -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: TASK-213; PROMO-0010; INS-0025; app/index.html -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# TASK-213 Replacement Undo Regression Evidence

## Scope and change

TASK-213 closes the hidden-information exploit confirmed by TASK-211 and
INS-0025. In `app/index.html:749-758`, the player replacement handler now
calls `clearUndo()` before `replaceCard(...)` instead of saving a `card swap`
snapshot. Clearing, rather than merely declining to save, is necessary: an
older reversible snapshot must not survive a later action that reveals a
random card.

No replacement mechanics were otherwise changed. `replaceCard` still moves
the selected card to the graveyard, draws once when possible, marks
`swapUsed`, and does not increment `cardsPlayed` (`app/index.html:561-573`).

## Headless Chromium interaction regression

Executed the editable app directly over `file://` in Chromium using Chrome
DevTools Protocol (`Runtime.evaluate`) and captured all runtime exceptions.
The trace performed these actions in one game:

1. Select Emberwild and wait for the player's action window.
2. Play the guaranteed one-cost starting card.
3. Confirm Undo becomes enabled, invoke it, and verify the original hand and
   mana return.
4. Play the one-cost card again, creating a live older undo snapshot.
5. Replace a remaining hand card and inspect the resulting UI state.
6. Attempt to click the now-disabled Undo control and confirm state does not
   change.

Observed trace:

| Check | Before/action | Result |
|---|---|---|
| Ordinary play creates undo | Play `Ember Runner`; hand 3→2, mana 1/1→0/1 | Undo enabled |
| Ordinary undo works | Click Undo | Original three-card hand and 1/1 mana restored |
| Replacement preserves play count | Before and after replacement | `cards played 1/2` unchanged |
| Replacement preserves hand count | Replace from a two-card hand | Two cards remain |
| Replacement draws hidden card | Replace `Moss Titan` | Hand becomes `Fire Drake`, `Ash Hunter` |
| Once-per-turn marker | After replacement | Control reads `Swap used` |
| Hidden-info action clears undo | An earlier play snapshot existed | Undo disabled after replacement |
| Disabled undo cannot restore | Attempted click after replacement | Hand, mana, label, log, and controls unchanged |
| Runtime health | Entire browser trace | 0 exceptions |

All 10 harness assertions passed.

## Static and integrity checks

- Inline application JavaScript passed `node --check` after extraction from
  the HTML script block.
- `python3 MAP_System/scripts/map_emergence.py validate` passed for the
  INS-0025 → IDEA-0021 → PROMO-0010 lineage.
- `Projects/ClearFront/source/SHA256SUMS.txt` verified all 11 preserved source
  payloads.
- Preserved hashes at final verification:
  - source `Clearfront.html`:
    `57e67f190b5a7f05418af1ad1884f8f99602ed6cc9731e02a9975086c0744fa6`
  - `baseline/index.html`:
    `fa4dea9c0c5987b6c5e50f6e6707a36942f432edfb7951851367a70c5e4cfe9a`
- The app continues to load and execute through `file://`; the browser trace
  used no server and reported zero runtime exceptions.

## Acceptance criteria result

1. Replacement cannot be undone after revealing a card: **PASS**.
2. Ordinary one-step undo remains functional: **PASS**.
3. Hand count, play count, draw, and once-per-turn replacement behavior remain
   intact: **PASS**.
4. Source/baseline integrity and `file://` compatibility: **PASS**.
5. Implementation scope is limited to `app/index.html`; this file is the
   task-specific evidence artifact: **PASS**.

Emergence capture considered: the originating issue is already captured and
promoted through INS-0025, IDEA-0021, and PROMO-0010; no additional insight
was created.
