<!-- hpom: file: artifacts/releases/task-217-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-217

## Header

```
task_id:      TASK-217
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

TASK-217 is the first post-decomposition ClearFront content task
(operator-requested): three original bitmap category artworks
(Unit/Spell/Relic, 512×512, text/watermark-free, generated via the
image-generation tool and locally resized/stripped from 6.1 MiB to
1.1 MiB combined) integrated into compact card faces. Compact hand/
board cards show cost/name/type/category-art/stats; full rules text
and keyword tags remain in the existing desktop-hover and touch-hold
previews (CSS-only visibility toggle via `.card-details`/`.card-peek`,
no new DOM logic or state). Implemented by codex-lab-lilo.

- Files: `Projects/ClearFront/app/assets/card-{unit,spell,relic}.png`,
  `Projects/ClearFront/app/js/render.js`,
  `Projects/ClearFront/app/styles/clearfront.css`, plus registered
  evidence (parity/preview report, focused harness, 2 screenshots).
- Shared files: none beyond the task's own registered outputs.
- Decisions: no new ARCHITECTURE decision — this is content/presentation
  work within the already-established render.js module, evaluated
  against `clearfront_design_principles.md` §21 (Design Review
  Checklist) as required by `shared/requirements.md`, not a structural
  change.
- Follow-ups: none required. One `OPTIONAL` reviewer note (not
  blocking): the details-hiding CSS rule is scoped to desktop-width
  viewports only; mobile-width compact cards show full rules text
  directly rather than requiring touch-hold. Worth a documentation note
  in the parity report if this project revisits card presentation.
- Events: creation, submission, approval, and this release are in
  `events/events.jsonl` (trace_id task:TASK-217), `--fail-on-new`
  clean.
- Emergence: considered — no new card. This is an application of the
  existing Design Review Checklist and CDP-parity-gate patterns
  (INS-0024 lineage) to a content task, not a new pattern itself.
- Operator-facing friction: no new operator-friction candidate found —
  this task exists because of a direct, already-actioned operator
  request.

## Review

- Verdict: APPROVED —
  `Projects/ClearFront/artifacts/reviews/task217-review-gome.md` by
  `claude-lab-gome`. Reviewer viewed all three generated assets
  directly at full resolution (not the report's description), read
  `createCardElement`'s and the CSS's actual diffs directly rather than
  trusting the parity report's summary, and executed all three checked-in
  test harnesses (`task217-card-art-check.mjs` 7/7, `task215-undo-check.mjs`
  exit 0, `task214-cdp-fullturn.mjs` all goals met) rather than trusting
  their claimed results.
- Reviewer independence: implementer was codex-lab-lilo; claude-lab-gome
  contributed no part of the implementation.

## Verification

- Three assets confirmed 512×512 RGB, text/watermark-free, visually
  distinct, matching disclosed prompts.
- `createCardElement` confirmed to add only a static `<img>` keyed off
  the pre-existing `card.type` field — no new state, no rule/balance
  change.
- Details-visibility toggle confirmed CSS-only (`display: none` on
  compact faces at desktop width, `display: grid !important` on the
  hover-cloned peek element) — no new JS logic.
- `node --check` passes on `render.js`.
- `source/` sha256 and `baseline/` md5 unchanged, reproduced
  independently.
- `validate_task_graph.py`, `validate_task_schema.py`,
  `validate_task_mirrors.py`, `validate_events.py --fail-on-new`: all
  pass.
