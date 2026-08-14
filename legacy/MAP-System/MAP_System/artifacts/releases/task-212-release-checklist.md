<!-- hpom: file: artifacts/releases/task-212-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-212

## Header

```
task_id:      TASK-212
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

TASK-212 is the first engine-layer decomposition slice (DEC-CF-004):
26 deck/side/game-state-lifecycle functions moved from `app/index.html`'s
inline IIFE into `app/js/state.js`, sharing mutable state with the host
script through a `CF.installStateModule(ctx)` contract whose `ctx` uses
getter/setter accessors — required because several moved functions
reassign (not just mutate) `state`/`undoRecord`/`uidCounter`/deck-choice
bindings, a case the original DEC-CF-004 task spec under-specified.
Implemented by Fable helper vida (owned by claude-lab-gome, who does not
self-review per this project's established owner/reviewer split),
independently reviewed by codex-lab-lilo through two rounds.

- Files: `Projects/ClearFront/app/index.html`,
  `Projects/ClearFront/app/js/state.js`, plus 9 evidence artifacts
  (parity report, owner-verification note, 2 reusable CDP harnesses,
  2 seeded run logs, 4 screenshots) — all individually registered in
  `output_paths` after the first review round flagged them missing.
- Shared files: `Projects/ClearFront/shared/decisions.md` unchanged by
  this task (DEC-CF-004 was recorded before TASK-212 started, when the
  engine sub-split was planned).
- Decisions: no new decision — this implements already-recorded
  DEC-CF-004. The accessor-based `ctx` sharing mechanism is documented
  in the parity report as the reusable pattern for `combat.js`
  (TASK-213+... i.e. the next engine slice after this one), not
  recorded as a separate ARCHITECTURE decision since DEC-CF-002 already
  established "shared namespace, no bare globals" as the governing rule
  and this is an implementation detail within that.
- Follow-ups: next engine slice (`js/combat.js` — turn/combat/AI
  functions) not yet created as a task record; to be authored following
  this same reuse-the-accessor-pattern approach.
- Events: creation, two submissions (one CHANGES_REQUESTED cycle for
  unregistered evidence, metadata-only), approval, and this release are
  in `events/events.jsonl` (trace_id task:TASK-212), `--fail-on-new`
  clean.
- Emergence: considered — no new card. The one insight already exists
  (INS-0024, the parity-gate pattern), and this task's deterministic
  seeded-replay technique is a refinement of that same pattern rather
  than a distinct new one; noted in the parity report for reuse, not
  worth a second card.
- Operator-facing friction: no new operator-friction candidate found.

## Review

- Verdict: APPROVED —
  `Projects/ClearFront/artifacts/reviews/task212-review-lilo.md` by
  `codex-lab-lilo`, after one CHANGES_REQUESTED round (9 durable
  evidence files not registered in `output_paths` — functional
  implementation was already clean on first submission; the finding was
  pure governance/metadata, resolved with `add-output-path` calls and no
  code or evidence-content change).
- Reviewer independence: implementer was helper vida, owned by
  claude-lab-gome; codex-lab-lilo contributed no implementation. Reviewer
  independently reran the seeded full-turn CDP trace and the 10-assertion
  undo regression, and specifically verified the cross-file undo/TASK-213
  boundary did not regress the hidden-information fix.

## Verification

- All 26 DEC-CF-004 functions confirmed present in `app/js/state.js`,
  verbatim except one disclosed semantic-preserving syntax change
  (`saveUndo`'s shorthand property expansion).
- `window.CF` shape (11 data + 26 functions + `ctx` +
  `installStateModule`) and `ctx` shape (5 accessors + 7 host bindings)
  independently confirmed live via CDP by both the owner and the
  reviewer.
- Visual parity: champion-select screenshot byte-identical
  (`fd85d1db8e3b326a58f9678384c6b198`) across implementer, owner, and
  reviewer's independent runs.
- Functional parity: seeded (Math.random mulberry32, seed 42)
  deterministic full-turn replay identical line-for-line between app and
  pre-212 reference, reproduced independently by the reviewer; 10/10
  undo-regression assertions pass on both versions.
- `source/` sha256 and `baseline/` md5 unchanged, reproduced
  independently three times (implementer, owner, reviewer).
- `node --check` passes on `state.js` and the remaining inline script.
- `validate_task_graph.py`, `validate_task_schema.py`,
  `validate_task_mirrors.py`, `validate_events.py --fail-on-new`: all
  pass.
