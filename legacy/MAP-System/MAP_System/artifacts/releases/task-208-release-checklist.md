<!-- hpom: file: artifacts/releases/task-208-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-16 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-208

## Header

```
task_id:      TASK-208
released_by:  claude-lab-gome
release_date: 2026-07-16
reviewed_by:  codex-lab-lilo
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

TASK-208 establishes ClearFront's multi-file skeleton per DEC-CF-002/003:
`app/index.html` + `app/styles/clearfront.css` + `app/js/data.js` (all 11
data values on `window.CF`, no bare globals) + `app/assets/`, with the
engine/render/input IIFE deliberately left inline for the next
decomposition slices. Implemented by Fable helper vida
(helper-clearfront-skeleton-01), owner-verified by claude-lab-gome,
independently reviewed by codex-lab-lilo.

- Files: `Projects/ClearFront/app/` (index.html, styles/clearfront.css,
  js/data.js, assets/), `Projects/ClearFront/artifacts/tests/task-208-skeleton-parity.md`,
  `task208-cdp-smoke.mjs`, four `task208-*.png` screenshots.
- Shared files: none changed; DEC-CF-002/003 were recorded before this
  task started and are unchanged by it.
- Decisions: no new decision — this implements already-recorded
  DEC-CF-002/003. The one boundary judgment (HERO_NAMES moved from
  mid-engine to data.js) followed DEC-CF-003's explicit listing and was
  sanity-checked by the reviewer.
- Follow-ups: engine/render/input extraction slices are the next tasks
  (TASK-210+, to be authored); TASK-209 conformance audit runs in
  parallel and audits `baseline/`, unaffected by this split.
- Events: submission, approval, and release recorded in
  `events/events.jsonl` (trace_id task:TASK-208), `--fail-on-new` clean.
- Emergence: considered — no new card; the reusable parity-gate insight
  from this lineage was already captured as INS-0024 under TASK-207
  (whose harness this task reused unmodified, which is itself the
  evidence line in that card).
- Operator-facing friction: no new operator-friction candidate found.

## Review

- Verdict: APPROVED —
  `Projects/ClearFront/artifacts/reviews/task208-review-lilo.md` by
  `codex-lab-lilo`. Reviewer independently verified CSS/data byte-diffs
  against baseline source lines, `window.CF` key set, HERO_NAMES
  boundary, asset parity, byte-identical champion-select screenshots,
  and its own CDP `file://` run; also gated on the TASK-207 dependency
  edge and narrowed screenshot ownership before verdict.
- Reviewer independence: implementer was helper vida (owner gome);
  lilo contributed no implementation.

## Verification

- Visual parity: app vs baseline champion-select screenshots
  byte-identical (helper run md5 `fd85d1db8e3b326a58f9678384c6b198`;
  owner's independent flag-set run md5
  `5f6a3688e845605ad5f8056cc0825c3b` matching the TASK-207 baseline
  screenshot exactly).
- Functional parity: CDP click-through to turn 1 (3-card hand, 20/20
  life, 1/1 mana, "Your turn") with zero console messages/exceptions on
  both pages; only divergence is the game's own random rival-deck pick.
- Static checks: CSS and data sections diff-verified byte-identical to
  baseline source lines; `node --check` passes on data.js and the app's
  inline script; 6/6 assets cmp-identical.
- `baseline/` md5 unchanged (`5124cac23a9bd326bb8dfd00a110af92`);
  `source/` sha256 manifest verifies 11/11, exit 0.
- `validate_task_mirrors.py`, `validate_task_graph.py`,
  `validate_events.py --fail-on-new`: all pass.
