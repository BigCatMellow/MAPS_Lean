<!-- hpom: file: artifacts/releases/task-216-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-216

## Header

```
task_id:      TASK-216
released_by:  claude-lab-gome
release_date: 2026-07-17
reviewed_by:  claude-lab-gome
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

TASK-216 is the final ClearFront decomposition slice: the self-contained
`initCardPeek` desktop-hover/touch-hold card-preview gesture layer moves
from `app/index.html`'s inline script into `app/js/input.js` behind
`CF.installInputModule()`, per DEC-CF-007. The installer takes no `ctx`
parameter — the only module in the decomposition with zero cross-module
dependencies, which is architecturally correct given the feature is
pure DOM-event/closure logic. Implemented by codex-lab-lilo per direct
operator assignment.

This completes the full engine/render/input decomposition (DEC-CF-002
through DEC-CF-007): `data.js` → `state.js` → `combat.js` → `render.js`
→ `input.js` → inline host, all seven implementation tasks in this
lineage (207, 208, 211, 212, 213, 214, 215) released, and this one
approved.

- Files: `Projects/ClearFront/app/index.html`,
  `Projects/ClearFront/app/js/input.js`, plus registered evidence
  (parity report, focused input-check harness, 2 champion-select
  screenshots), and `Projects/ClearFront/shared/decisions.md`
  (DEC-CF-007).
- Shared files: `shared/decisions.md` (DEC-CF-007, recorded by the
  implementer before starting — consistent with this project's
  established pattern of scoping the decision before touching code).
- Decisions: DEC-CF-007, ARCHITECTURE class, implemented as recorded.
- Follow-ups: none for the decomposition itself — it's complete. Next
  phase is game-improvement work gated on the Design Review Checklist
  (`clearfront_design_principles.md` §21), drawing from the 6
  prioritized follow-ups in the released rules-conformance audit
  (`artifacts/research/rules-conformance-audit.md`) and prioritizing
  INS-0025-adjacent findings already fixed (TASK-213) over the
  remaining scope-gap items (Equipment, Mind/Forge/Neutral, Rush/Stun).
- Events: creation, submission, approval, and this release are in
  `events/events.jsonl` (trace_id task:TASK-216), `--fail-on-new`
  clean.
- Emergence: considered — no new card. The `window.matchMedia`
  interception technique for testing hover-dependent behavior in
  headless Chromium (documented in the reviewer's independent
  verification) is a useful pattern but incremental to the
  already-established CDP-parity-gate insight (INS-0024), not a
  distinct new one.
- Operator-facing friction: no new operator-friction candidate found.

## Review

- Verdict: APPROVED —
  `Projects/ClearFront/artifacts/reviews/task216-review-gome.md` by
  `claude-lab-gome`. Reviewer executed the actual checked-in test
  harnesses directly (not just reading the parity report) —
  `task216-input-check.mjs` (8/8 PASS), the released `task215-undo-check.mjs`
  (6/6 PASS), and the released `task215-seeded-replay.mjs` against both
  `app/` and the pristine `baseline/` — and independently reproduced the
  screenshot hash. One apparent seeded-replay divergence (a transient
  UI string at an intermediate step) was investigated and confirmed to
  be fixed-delay snapshot timing jitter against async `setTimeout`-driven
  UI, not a regression, by reproducing the identical pattern running the
  same build against itself twice.
- Reviewer independence: implementer was codex-lab-lilo; claude-lab-gome
  contributed no part of the implementation.

## Verification

- `initCardPeek`'s move confirmed direct (78-line self-contained
  function body, zero `ctx` parameter — the correct minimal-surface
  design for a module with no cross-module dependencies).
- Invocation point confirmed at `app/index.html:381`, exactly matching
  DEC-CF-007's specified ordering (after scrollbar binding, before
  `showDeckSelect()`).
- Live `window.CF.ctx` key count confirmed unchanged at 7.
- `node --check` passes on all 5 app JS files and the remaining inline
  script.
- `source/` sha256 and `baseline/` md5 unchanged, reproduced
  independently.
- `validate_task_graph.py`, `validate_task_schema.py`,
  `validate_task_mirrors.py`, `validate_events.py --fail-on-new`: all
  pass.
