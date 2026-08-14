<!-- hpom: file: artifacts/releases/task-213-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-213

## Header

```
task_id:      TASK-213
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

TASK-213 closes the hidden-information exploit found by TASK-211's
conformance audit and captured as INS-0025: card replacement previously
saved a fresh undo snapshot before drawing the replacement, letting a
player see the drawn card and then revert. Fix: `clearUndo()` (wiping
any undo capability, including an older snapshot) instead of
`saveUndo('card swap')`, in `app/index.html`'s replacement handler only.

- Files: `Projects/ClearFront/app/index.html`,
  `Projects/ClearFront/artifacts/tests/task213-replacement-undo-regression.md`.
- Shared files: none — this was a targeted app-only bugfix per the
  approved PROMO-0010 scope.
- Decisions: none new — implements the already-approved
  INS-0025 → IDEA-0021 → PROMO-0010 emergence lineage; no ARCHITECTURE/
  SCOPE/POLICY decision required.
- Follow-ups: none required beyond the audit's remaining prioritized
  candidates (Equipment/Mind/Forge/Neutral scope, Rush/Stun keyword
  gaps, undocumented fatigue) already tracked in the released
  rules-conformance-audit.md; TASK-212 (state.js extraction) unblocked
  by this release and resumes next.
- Events: creation, submission, approval, and this release are in
  `events/events.jsonl` (trace_id task:TASK-213), `--fail-on-new` clean.
- Emergence: considered — the originating insight/idea/promotion chain
  (INS-0025/IDEA-0021/PROMO-0010) already exists; no new card needed.
  `map_emergence.py validate` passed per the implementer's evidence.
- Operator-facing friction: no new operator-friction candidate found.

## Review

- Verdict: APPROVED —
  `Projects/ClearFront/artifacts/reviews/task213-review-gome.md` by
  `claude-lab-gome`. Reviewer independently reproduced both integrity
  hashes and read the actual diff site + `clearUndo`/`canUndo`/
  `replaceCard` source directly rather than trusting the submitted
  report's paraphrase.
- Reviewer independence: implementer was codex-lab-lilo; claude-lab-gome
  contributed no part of the fix.

## Verification

- Fix confirmed minimal and root-cause: `clearUndo()` (not merely
  declining to save) placed before `replaceCard(...)` in the one
  affected handler; no other functional change.
- `canUndo()`'s `!!undoRecord` gate confirmed to make the fix
  state-layer correct, not merely a UI-visibility change.
- `replaceCard` discard/draw/`swapUsed`/no-`cardsPlayed`-increment
  behavior confirmed unchanged from source.
- `source/` sha256 and `baseline/` sha256 both independently reproduced,
  exact match to the submitted evidence.
- 10/10 browser-trace assertions passed per implementer evidence (undo
  works for ordinary play, disabled and non-restoring after
  replacement, zero runtime exceptions); reviewer did not re-run the
  live browser trace but verified its logical basis is sound from the
  source code directly.
- `validate_task_graph.py`, `validate_task_schema.py`,
  `validate_task_mirrors.py`, `validate_events.py --fail-on-new`: all
  pass (the `app/index.html` output-path collision with paused TASK-212
  was resolved by setting TASK-212 to BLOCKED before this submission,
  per the TASK-209/RETIRED precedent).
