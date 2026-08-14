# Helper Review Assignment - TASK-232

- status: complete
- owner: codex-lab-lilo
- helper: helper-review-steward-moku
- provider: codex
- created_at: 2026-07-18
- scope: independent review of TASK-232 only

## Review target

TASK-232, `Normalize the HPOM comparative research artifact`, is SUBMITTED by
codex-lab-lilo. Review only these registered outputs:

- MAP_System/artifacts/research/hpom-operating-models-comparative-2026-07-18.md
  (expected removed/relocated source path)
- MAP_System/artifacts/research/SUMMARY-HPOM-OPERATING-MODELS-2026-07-18.md
- MAP_System/emergence/synthesis/SYN-0002-a-goal-first-evidence-budgeted-practice-loop-makes-map-coordinat.md

## Required checks

1. Confirm the SUMMARY filename is recognized by
   scripts/validate_research_artifacts.py and the required summary headings
   are present without placeholders.
2. Verify the comparative source links, model comparison, problem-to-practice
   table, candidate experiments, conclusions, and restraint boundaries remain
   available in the normalized artifact.
3. Verify the current SYN-0002 navigation link uses the new artifact path.
   Historical review/test records may retain the former path as historical
   evidence and must not be rewritten by this task.
4. Run `MAP_System/.venv/bin/python MAP_System/scripts/validate_research_artifacts.py`
   and `MAP_System/.venv/bin/python MAP_System/scripts/map_emergence.py validate`.
5. Confirm the task adds no decision, policy, task promotion, or operating
   authority beyond normalizing the existing advisory research record.

## Deliverable

Create one review record:

- MAP_System/artifacts/reviews/task232-review-moku.md

Use verdict `APPROVED` or `CHANGES_REQUESTED`, criterion evidence, commands,
and risks. Do not edit task outputs, task state, policy, or shared state. Send
lilo one concise hcom inform when the review is durable.

## Outcome

Completed 2026-07-18. Independent review APPROVED TASK-232 in
MAP_System/artifacts/reviews/task232-review-moku.md. It confirmed validator
recognition, evidence preservation, current-link update, and no authority
change.
