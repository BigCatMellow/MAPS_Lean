<!-- hpom: file: artifacts/reviews/task213-review-gome.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: claude-lab-gome -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: TASK-213 independent review -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Review Record: TASK-213

## Header

```text
task_id:      TASK-213
reviewer:     claude-lab-gome
review_date:  2026-07-17
task_owner:   codex-lab-lilo
```

Reviewer (`claude-lab-gome`) != task owner (`codex-lab-lilo`). Independence passes.

## Verdict

```text
APPROVED
```

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Undo unavailable/non-restoring after a replacement reveal | PASS | `app/index.html:749-756` calls `clearUndo()` before `replaceCard(...)`; `clearUndo` sets `undoRecord = null` (line 490); `canUndo()` returns `!!undoRecord && ...` (line 492), so it is `false` immediately after any replacement, independent of whether an older snapshot existed. |
| 2 | Ordinary one-step undo still works | PASS | `saveUndo`/`undoLastAction` (lines 485-500) untouched; harness step 3 confirms hand/mana restore after an ordinary play+undo. |
| 3 | Replacement mechanics unchanged | PASS | `replaceCard` (lines 561-573) unchanged: discards to graveyard, draws once via `drawCard(who, false)`, sets `swapUsed`, never touches `cardsPlayed`. |
| 4 | Source/baseline integrity + `file://` compatibility | PASS | Independently reproduced both hashes (see below) — exact match. |
| 5 | Scope limited to `app/index.html` + task evidence | PASS | `output_paths` in `MAP_System/tasks/TASK-213.json` lists only those two files; no other file under `Projects/ClearFront/` shows a newer mtime than the evidence file. |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Edit `source/` | NOT BROKEN — sha256 `57e67f19...` matches independently. |
| Edit `baseline/` | NOT BROKEN — sha256 `fa4dea9c...` matches independently. |
| Mix in a decomposition/refactor change | NOT BROKEN — the only functional diff is the one `handleHandCard` branch (`saveUndo('card swap')` → `clearUndo()`); everything else in the surrounding function and `replaceCard` is untouched. |
| Mix in a rules/balance change | NOT BROKEN — no numeric/keyword/card-data change. |

## Independent Verification

- Reproduced both integrity hashes myself (not copied from the report):
  `source/game-card-combat-effects/Clearfront.html` sha256
  `57e67f190b5a7f05418af1ad1884f8f99602ed6cc9731e02a9975086c0744fa6`;
  `baseline/index.html` sha256
  `fa4dea9c0c5987b6c5e50f6e6707a36942f432edfb7951851367a70c5e4cfe9a`.
  Both match the report exactly.
- Read the actual diff site directly (`app/index.html:749-756`) rather
  than trusting the report's line numbers: confirmed `clearUndo()`
  replaces the prior `saveUndo('card swap')` call, placed before
  `replaceCard(...)` — the fix is the minimal, root-cause change (clear,
  not merely skip-save), which is what INS-0025 required: an *older*
  snapshot must not survive a later hidden-information reveal, and
  "decline to save a new one" alone would not have achieved that.
- Confirmed `canUndo()`'s gate is `!!undoRecord`, so this fix's
  correctness does not depend on any other UI-layer disabling logic —
  the control is disabled at the state layer, not just visually.
- Confirmed `replaceCard`'s discard/draw/`swapUsed`/no-`cardsPlayed`
  behavior directly from source, matching criterion 3 without relying on
  the report's paraphrase.

## Assessment

Correctly scoped, minimal, root-cause fix. Distinguishes "declining to
create a new undo snapshot" (insufficient — an older snapshot could
still be exploited) from "clearing any undo capability on a
hidden-information reveal" (correct, and what was implemented). No
notes beyond approval.

## Files Reviewed

- `Projects/ClearFront/app/index.html` (diff site + `clearUndo`/`canUndo`/`replaceCard`)
- `Projects/ClearFront/artifacts/tests/task213-replacement-undo-regression.md`
- `Projects/ClearFront/source/game-card-combat-effects/Clearfront.html` (hash only)
- `Projects/ClearFront/baseline/index.html` (hash only)
- `MAP_System/tasks/TASK-213.json`

## Findings

No `BLOCKER` or `REQUIRED` findings.
