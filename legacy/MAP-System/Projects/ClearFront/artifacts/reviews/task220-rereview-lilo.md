# Review: TASK-220 deterministic rule-engine test matrix — re-review

task_id: TASK-220  
reviewer: codex-lab-lilo  
task_owner: claude-lab-gome  
prior_review: `Projects/ClearFront/artifacts/reviews/task220-review-lilo.md`

## Verdict

APPROVED

## Acceptance Criteria Check

- PASS — `node tests/engine/run-rules.mjs` loads the real, unmodified engine
  modules in Node and passes 34/34 cases and 90/90 assertions. An isolated
  one-assertion mutation produces exit 1 with the expected precise diff, so
  the runner is fail-loud.
- PASS — The revised matrix covers the required keywords, combat states,
  persistent damage, champion deployment/return/cost escalation, all four
  champion passives with their per-cycle consumption, fatigue/hand-limit
  nuance, board/relic limits, direct effect-target legality, play limits, and
  engine-level undo including replacement clearing.
- PASS — Five current-behavior deviations are tagged to their exact TASK-211
  audit sections and appear in a separate runner summary.
- PASS — `scripts/test_all.mjs` invokes the engine matrix and succeeds without
  caller-managed Chromium setup (the full command exited 0 in this review).
- PASS — The TASK-219 combined delivery note captures change, verification,
  acceptance mapping, and untouched `source/`/`baseline/` evidence.

## Files Reviewed

- `MAP_System/tasks/TASK-220.json`
- `Projects/ClearFront/tests/engine/engine-host.mjs`
- `Projects/ClearFront/tests/engine/rules.cases.mjs`
- `Projects/ClearFront/tests/engine/run-rules.mjs`
- `Projects/ClearFront/scripts/test_all.mjs`
- `Projects/ClearFront/artifacts/tests/task-220-delivery-note.md`
- `Projects/ClearFront/artifacts/reviews/task220-review-lilo.md`

## Forbidden Changes Check

No application runtime, game-rule, balance, `source/`, or `baseline/` change
appears in the registered TASK-220 output scope. The headless host supplies
test-only browser shims and loads the released modules unchanged; the source
checksum verification independently confirms frozen-source provenance.

## Rework Resolution

The two REQUIRED findings in the prior review are resolved:

| Prior finding | Evidence of resolution |
|---|---|
| `flameDamage` and `shadowDeath` passives were untested | `champion-flame-damage-first-card` proves the first damage-card bonus and its one-per-cycle consumption; `champion-shadow-death-first-friendly-death` proves the first friendly-death trigger and its one-per-cycle consumption. Alongside the existing Order and Wild cases, all four defined passive branches are exercised. |
| Card-effect target legality was only proxied | `target-enemy-friendly-and-default-shapes` calls `getTargetInfo` directly for enemy, friendly, and no-target card shapes; `target-filtered-damaged-only` directly covers the filtered damaged-enemy branch. |

## Findings

No BLOCKER or REQUIRED findings remain.

| Severity | File | Finding | Required Action |
|---|---|---|
| RECOMMENDED | `tests/engine/rules.cases.mjs` | The matrix intentionally covers the audit's core behavior, not every `resolveEffect` branch in the card library. | Treat additional effect coverage as a later, separately scoped matrix expansion; do not enlarge this completed task. |

## Verification

- `node Projects/ClearFront/tests/engine/run-rules.mjs` — PASS: 34/34 cases,
  90/90 assertions; five deviations printed separately.
- Isolated temporary copy with the flame-damage expectation changed by one —
  PASS: 33/34 cases, 89/90 assertions, exit 1, and a precise expected/got
  failure; repository files were not changed.
- `node Projects/ClearFront/scripts/test_all.mjs` — PASS: exit 0, including
  the engine rule-matrix and browser checks.
- `cd Projects/ClearFront/source && sha256sum -c SHA256SUMS.txt` — PASS:
  source provenance remains intact.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_graph.py` and
  `validate_task_mirrors.py` — PASS before approval.

## Notes

This is a test-only medium-risk delivery. No game-rule, balance, app-runtime,
`source/`, or `baseline/` modification is included in the registered
TASK-220 scope. The current-rule deviation cases remain deliberately visible
decision support, not a silent claim of rules conformance.
