# Review: TASK-220 deterministic rule-engine test matrix

task_id: TASK-220  
reviewer: codex-lab-lilo  
task_owner: claude-lab-gome

## Verdict

CHANGES_REQUESTED

## Acceptance Criteria Check

- PASS — The real unmodified modules load headlessly and the current matrix
  passes 30/30 cases and 71/71 assertions.
- PARTIAL — Required behavior domains are broadly present, but champion
  passives and target legality are incomplete as described below.
- PASS — Five known rules deviations carry TASK-211 section tags and print in
  a distinct non-failure summary.
- PASS — `scripts/test_all.mjs` includes the engine matrix as an additional
  fail-loud check.
- PASS — The combined TASK-219 delivery-note format is used; no legacy evidence
  trio was created.

## Files Reviewed

- `MAP_System/tasks/TASK-220.json`
- `Projects/ClearFront/tests/engine/engine-host.mjs`
- `Projects/ClearFront/tests/engine/rules.cases.mjs`
- `Projects/ClearFront/tests/engine/run-rules.mjs`
- `Projects/ClearFront/scripts/test_all.mjs`
- `Projects/ClearFront/artifacts/tests/task-220-delivery-note.md`
- `Projects/ClearFront/app/js/data.js`
- `Projects/ClearFront/app/js/state.js`
- `Projects/ClearFront/app/js/combat.js`

## Forbidden Changes Check

No app runtime, game-rule, balance, `source/`, or `baseline/` changes were found
in the registered TASK-220 output scope. The host loads the released modules
without modification.

## Findings

| Severity | File | Finding | Required action |
|---|---|---|---|
| REQUIRED | `Projects/ClearFront/tests/engine/rules.cases.mjs` | The task description and delivery note claim all four champion passive types, but only `orderPrevent` and `wildHealth` are tested. `flameDamage` and `shadowDeath` are unexercised primary behavior branches in `combat.js`. | Add deterministic cases for `flameDamage` (first damage card bonus and once-per-turn consumption) and `shadowDeath` (first friendly death trigger and once-per-cycle consumption), then correct counts in evidence. |
| REQUIRED | `Projects/ClearFront/tests/engine/rules.cases.mjs` | The acceptance criterion explicitly includes target legality. Hand membership tests whether a card may be played at all, and `blockTargetReason` tests blocker assignment; neither exercises card-effect target selection via `getTargetInfo`, where several effect-specific legality branches live. | Add focused direct `getTargetInfo` coverage demonstrating valid/invalid card-effect targets. At minimum cover enemy-only and friendly-only selection plus one filtered category such as damaged enemy. Update the delivery note instead of labeling the prior proxy coverage as complete. |

## Verification

- `node Projects/ClearFront/tests/engine/run-rules.mjs` — PASS, 30/30 cases,
  71/71 assertions, five deviation tags.
- Source inspection confirmed four passive keys in `data.js` and four distinct
  passive branches across `state.js`/`combat.js`; only two appear in the matrix.
- Source inspection confirmed the untested target-legality switch in
  `combat.js:getTargetInfo`.

## Risks

Approving the matrix with its current claims would make a new primary
correctness oracle look broader than it is. The required additions are bounded
test-only changes and do not require application edits.
