<!-- hpom: file: artifacts/reviews/task215-review-lilo.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: codex-lab-lilo -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: TASK-215 independent review -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Review Record: TASK-215

## Header

```text
task_id:      TASK-215
reviewer:     codex-lab-lilo
review_date:  2026-07-17
task_owner:   claude-lab-gome
```

Reviewer (`codex-lab-lilo`) differs from owner/implementer
(`claude-lab-gome`).

## Verdict

```text
APPROVED
```

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Move all 28 render/clash functions without logic changes; keep clash timers private | PASS | `render.js` defines exactly the 28 names in TASK-215/DEC-CF-006. `clashTimers` and `clashSkip` are module-private; the sole overlay listener that accesses `clashSkip` moved into the same install closure. Mechanical identifier rewrites and all four disclosed correction classes were inspected; no bare cross-module calls or mutable bindings remain. |
| 2 | Reduce `ctx` and update sibling callers | PASS | `app/index.html:296-303` contains exactly five mutable accessors plus `$` and `refs`. `state.js` has three `CF.render()` calls; `combat.js` has 22 `CF.render()`, one `CF.playClashSequence()`, and one `CF.renderCombatReport()` call, with no old destructured render dependencies. |
| 3 | Preserve visual and functional behavior over `file://` | PASS | Registered champion-select screenshots are byte-identical. Both registered seed-42 and seed-7 app/baseline JSON pairs compare byte-for-byte. Reviewer reran the stronger TASK-214 seed-42 browser harness against the current app through play, attack, a real blocker assignment, combat resolution/report, end turns, and AI turns: all goals PASS, zero console messages/exceptions. |
| 4 | Preserve undo and TASK-213 hidden-information protection | PASS | Reviewer ran `task215-undo-check.mjs` in a fresh browser and independently inspected every reported boolean: 6/6 true, zero console messages/exceptions. Ordinary play/restore and replacement-clears-undo semantics remain intact across four files. |
| 5 | Syntax checks | PASS | `node --check` passes on `render.js`, `combat.js`, `state.js`, and the correctly extracted remaining inline script. |
| 6 | Preserve source and baseline | PASS | `source/SHA256SUMS.txt` independently verifies all 11 payloads; baseline md5 remains `5124cac23a9bd326bb8dfd00a110af92`. |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Edit preserved source or baseline | NOT BROKEN — integrity checks reproduced. |
| Move input/gesture wiring | NOT BROKEN — `initCardPeek` and general input listeners remain inline; only the clash-overlay listener moved because it closes over render-private `clashSkip`. |
| Leave render functions forwarded through `ctx` | NOT BROKEN — final context is exactly seven keys. |
| Introduce build/server/module requirements | NOT BROKEN — ordered classic scripts load directly through `file://`. |
| Leave unresolved cross-module identifiers | NOT BROKEN — exhaustive export-name scan found no suspicious bare cross-module calls; runtime traces report zero exceptions. |
| Regress TASK-213 | NOT BROKEN — replacement leaves undo unavailable in the independent run. |
| Hide durable outputs | NOT BROKEN — implementation files, harnesses, JSON traces, and screenshots are registered. |

## Independent Verification

- Read the complete disclosed bug/fix section and traced each final repair in
  `render.js`, `combat.js`, and `state.js`.
- Mechanically enumerated 26 state, 38 combat, and 28 render functions.
- Scanned every module export name for bare calls from sibling modules; none
  remain. Confirmed the added `CF.championDeployReason`, `CF.deployChampion`,
  and eight `CF.cardAttack` sites.
- Confirmed `MAX_CARDS_PER_TURN`, `CARD_LIBRARY`, and `HERO_NAMES` are the
  complete render-layer data destructure.
- Confirmed all live render-layer `undoRecord` reads use `ctx.undoRecord` and
  all three spread-position state uses are `...ctx.state...`.
- Compared registered screenshot and seeded-output pairs byte-for-byte.
- Reran current-app combat/blocking and undo sessions in fresh Chromium.
- Reproduced syntax, source, baseline, task graph, schema, and mirror checks.

## Risks

- The parity comparison uses the pristine baseline because no pre-TASK-215 app
  snapshot was preserved. This is strong for the exercised render/combat paths,
  but baseline predates the intentional TASK-213 undo change; the separate
  current-app undo test correctly covers that known divergence.
- TASK-215's undo harness prints booleans but does not aggregate failures into a
  nonzero exit code. A future harness-maintenance task should make failed
  assertions fail the process so CI cannot mistake a printed false value for a
  passing run.
- Four runtime-only defects were found during implementation. Their common
  lesson is to generate cross-module symbol checks from complete export sets,
  not hand-maintained lists or negative-lookbehind rewrites. Final exhaustive
  scanning and live tests found no residue.

## Files Reviewed

- `MAP_System/tasks/TASK-215.json`
- `Projects/ClearFront/shared/decisions.md` (DEC-CF-006)
- `Projects/ClearFront/app/index.html`
- `Projects/ClearFront/app/js/state.js`
- `Projects/ClearFront/app/js/combat.js`
- `Projects/ClearFront/app/js/render.js`
- `Projects/ClearFront/artifacts/tests/task-215-render-parity.md`
- `Projects/ClearFront/artifacts/tests/task215-seeded-replay.mjs`
- `Projects/ClearFront/artifacts/tests/task215-undo-check.mjs`
- Four registered seeded JSON traces and two registered screenshots
- `Projects/ClearFront/artifacts/tests/task214-cdp-fullturn.mjs`
- Preserved source checksum manifest and baseline index

## Findings

No `BLOCKER` or `REQUIRED` findings.

Advisory: update `task215-undo-check.mjs` in a future registered maintenance
scope so any false assertion or runtime/console error exits nonzero.
