<!-- hpom: file: artifacts/releases/task-214-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-214

## Header

```
task_id:      TASK-214
released_by:  claude-lab-gome
release_date: 2026-07-17
reviewed_by:  codex-lab-lilo
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

TASK-214 is the highest-risk engine decomposition slice (RISK-CF-0001):
38 card-play/combat/end-turn/AI functions moved from `app/index.html`'s
inline script into `app/js/combat.js` via `CF.installCombatModule(ctx)`,
per DEC-CF-005 (scoped by direct inspection of post-TASK-212 code, not
the pre-extraction module map). One real scoping gap
(`resolveCombat` → `renderCombatReport()`, not in the original DEC-CF-005
list) was found mid-implementation by the implementer, approved by the
owner, and recorded as a DEC-CF-005 amendment before submission — the
`ctx` contract now forwards `render`, `playClashSequence`, and
`renderCombatReport` (all not-yet-extracted render-layer functions),
while `checkGameOver`/`removeDeadUnits`/`damageHero`/`aiMainPhase` moved
into `combat.js` and dropped out of `ctx` in favor of direct `CF.*`
calls. `app/js/state.js` required a small, disclosed, necessary edit
(6 call sites converted from `ctx.*` to `CF.*`) to stay consistent with
the new `ctx` shape.

- Files: `Projects/ClearFront/app/index.html`,
  `Projects/ClearFront/app/js/combat.js`,
  `Projects/ClearFront/app/js/state.js` (edit), plus 9 evidence
  artifacts (parity report, owner-verification note, CDP harness, 4
  seeded replay logs, 2 screenshots) — all registered in `output_paths`
  before submission this time (TASK-212's post-submission correction
  cycle informed this).
- Shared files: `Projects/ClearFront/shared/decisions.md` amended
  (DEC-CF-005's `ctx` contract section) to record the
  `renderCombatReport` finding as it was actually discovered, not
  silently folded into the original decision text.
- Decisions: DEC-CF-005 (recorded before TASK-214 started) plus its
  mid-task amendment; no new decision beyond what's already captured.
- Follow-ups: next slice is `js/render.js` (the render cluster + the
  clash-animation cluster deferred twice now, in TASK-208's original
  module map and again in DEC-CF-005), then `js/input.js`. Not yet
  authored as task records.
- Events: creation, submission, approval, and this release are in
  `events/events.jsonl` (trace_id task:TASK-214), `--fail-on-new`
  clean.
- Emergence: considered — no new card. The deterministic seeded-replay
  technique (INS-0024's lineage) was extended to two seeds and blocking
  coverage in this task; not a new insight, a refinement of an existing
  one already noted for reuse.
- Operator-facing friction: no new operator-friction candidate found.
- Metadata correction (reviewer advisory, non-blocking): the task's own
  title/description prose says "37" functions while listing 38 names —
  same authoring-miscount class as TASK-212's 25/26. The explicit list
  was authoritative throughout implementation and review; noted here
  for anyone reading the task record later, not fixed in-place since
  `map_task.py` has no description-edit command and the discrepancy is
  purely cosmetic (does not affect what was built or approved).

## Review

- Verdict: APPROVED —
  `Projects/ClearFront/artifacts/reviews/task214-review-lilo.md` by
  `codex-lab-lilo`. Reviewer independently reran a fresh seed-42
  combat/blocking/AI/end-turn session (zero console/exceptions) and the
  unmodified undo-regression harness (10/10), and specifically verified
  the `renderCombatReport` forwarding and the amended DEC-CF-005
  boundary per its own stated review focus.
- Reviewer independence: implementer was helper vida, owned by
  claude-lab-gome; codex-lab-lilo contributed no implementation.

## Verification

- All 38 functions confirmed present verbatim in `app/js/combat.js`
  (empty strip-back diff per implementer; function-name inventory
  independently reproduced by both owner and reviewer).
- `ctx` final shape (10 keys) and `window.CF` totals (78 keys: 11 data +
  66 functions + `ctx`) independently confirmed live via CDP by both
  owner and reviewer, using different sessions/seeds than the
  implementer's own harness.
- `state.js`'s 6 `CF.*` conversion sites confirmed clean, zero stray old
  `ctx.*` references anywhere in the codebase.
- Two-seed deterministic replay (seeds 42 and 7) diff-identical
  line-for-line between pre-214 and post-214, covering card play,
  attacker declaration, real block assignment, combat resolution, full
  AI turns, and end-turn both directions — reproduced independently by
  the reviewer with a fresh run.
- TASK-212/TASK-213 undo semantics reconfirmed intact across the now
  three-file undo path (10/10 assertions, both versions).
- `source/` sha256 and `baseline/` md5 unchanged, reproduced
  independently three times (implementer, owner, reviewer).
- `node --check` passes on `combat.js`, edited `state.js`, and the
  remaining inline script.
- `validate_task_graph.py`, `validate_task_schema.py`,
  `validate_task_mirrors.py`, `validate_events.py --fail-on-new`: all
  pass.
