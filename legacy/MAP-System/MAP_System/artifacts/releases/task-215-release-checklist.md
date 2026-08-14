<!-- hpom: file: artifacts/releases/task-215-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-215

## Header

```
task_id:      TASK-215
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

TASK-215 is the third and final large engine-decomposition slice: 28
render + clash-animation functions moved from `app/index.html`'s inline
script into `app/js/render.js` via `CF.installRenderModule(ctx)`, per
DEC-CF-006. `ctx` is now reduced to exactly its intended final shape —
the 5 mutable-reassignment accessors plus `$`/`refs` — with
`render`/`playClashSequence`/`renderCombatReport` moved out and
`window.CF`-published like every other extracted function.

Implemented directly by the task owner (claude-lab-gome), not by a
helper: Fable helper vida (implementer of TASK-212/214) ran out of
Fable-specific usage credits before starting this task (confirmed
distinct from a Sonnet session limit; operator directed doing the work
directly rather than waiting, after confirming vida was not running
headless). The helper was stopped
(`hcom kill helper-clearfront-skeleton-01-vida`); its accumulated
context is preserved in DEC-CF-004/005/006 and the released task
records, not lost.

Because this was the first ClearFront task without a second engineer's
pass before submission, 4 real bugs surfaced during the owner's own
implementation/verification loop — none caught by static checks
(`node --check` passed throughout), all caught only by driving the live
app via CDP and reading exception stack traces. All 4 are fully
disclosed with root cause in the parity report rather than smoothed
over, and the reviewer specifically scrutinized that disclosure.

- Files: `Projects/ClearFront/app/index.html`,
  `Projects/ClearFront/app/js/render.js`,
  `Projects/ClearFront/app/js/combat.js` (edit),
  `Projects/ClearFront/app/js/state.js` (edit), plus 12 evidence
  artifacts (parity report, 2 seeded-replay logs ×2 versions, 2 test
  harnesses, 2 champion-select screenshots) — all registered in
  `output_paths` before submission.
- Shared files: `Projects/ClearFront/shared/decisions.md` amended
  (DEC-CF-006's post-implementation note documenting all 4 bugs) and
  `shared/current-state.md` updated.
- Decisions: DEC-CF-006 (recorded before implementation) plus its
  post-implementation amendment.
- Follow-ups: `js/input.js` (small — the card-peek hover/touch IIFE) is
  the last decomposition slice, not yet a task record. Post-review
  advisory (non-blocking, applied before this release): the checked-in
  `task215-undo-check.mjs` harness now exits nonzero on any failed
  assertion or captured exception, so it fails loudly if reused in a
  future automated/maintenance context rather than requiring a human to
  read its JSON output. Re-verified live after the change: still 6/6
  PASS, exit 0.
- Events: creation, submission, approval, and this release are in
  `events/events.jsonl` (trace_id task:TASK-215), `--fail-on-new`
  clean.
- Emergence: considered — no new card. The four disclosed implementation
  bugs are process learning already captured directly in DEC-CF-006's
  post-implementation note (the more durable, load-bearing location for
  future decomposition tasks to read), not duplicated as a separate
  Emergence insight.
- Operator-facing friction: no new operator-friction candidate found
  (the Fable usage-credits blocker was a real friction point, but it
  was escalated and resolved through normal hcom/operator channels
  during the task, not left as an unaddressed friction signal).

## Review

- Verdict: APPROVED —
  `Projects/ClearFront/artifacts/reviews/task215-review-lilo.md` by
  `codex-lab-lilo`. Reviewer independently traced all four disclosed
  fix classes against the actual code, exhaustively re-scanned
  cross-module exports (not trusting the disclosed list), verified the
  28-function boundary and 7-key `ctx` shape, compared both seed pairs
  and both screenshot pairs byte-for-byte, reran the blocking/combat
  seeded replay and the undo harness independently, and confirmed zero
  errors throughout.
- Reviewer independence: owner-implemented (no helper); codex-lab-lilo
  is a fully independent core agent, same no-self-review routing as
  every prior ClearFront task.

## Verification

- All 28 functions confirmed present verbatim in `app/js/render.js`
  (empty strip-back diff per implementer; independently reconfirmed by
  reviewer).
- `ctx` final shape (7 keys: 5 mutable accessors + `$`/`refs`) and
  `window.CF` total (107 keys: 11 data + 26 state + 38 combat + 28
  render + 3 install fns + `ctx`) independently confirmed live via CDP
  by both owner and reviewer.
- `combat.js`'s 24 converted call sites and `state.js`'s 3 converted
  call sites confirmed clean, zero stray bare references remaining.
- Two-seed deterministic replay (seeds 42 and 7) byte-identical between
  `app/index.html` and the pristine, untouched `baseline/index.html`
  (the strongest available reference, since no pre-edit `app/` snapshot
  was saved before implementation began) — reproduced independently by
  the reviewer.
- Clash animation's `setTimeout`-based sequencing confirmed to actually
  execute (overlay observed genuinely open mid-combat, not just
  end-state correctness) by both owner and reviewer.
- Undo semantics (TASK-212/213 lineage) reconfirmed intact across the
  now-four-file boundary: 6/6 assertions, both independently rerun.
- `source/` sha256 and `baseline/` md5 unchanged, reproduced
  independently by implementer, owner, and reviewer throughout the
  multi-round implementation (not just once at the end).
- `node --check` passes on `render.js`, edited `combat.js`, edited
  `state.js`, and the remaining inline script.
- `validate_task_graph.py`, `validate_task_schema.py`,
  `validate_task_mirrors.py`, `validate_events.py --fail-on-new`: all
  pass.
