# Review: TASK-001 first-run onboarding simulation

- Task: [TASK-001](../tasks/TASK-001-first-run-onboarding-simulation.md)
- Reviewer: Codex independent reviewer
- Verdict: `APPROVED`

## Acceptance criteria check

- `PASS` — The report starts from the Lean root, lists a coherent active-doc
  route, and does not rely on a legacy startup instruction.
- `PASS` — It records twelve files read in order with a reason for each.
- `PASS` — Its SQLite, LangGraph, RnS, hcom, and WezTerm descriptions match
  `README.md`, `playbook/INDEX.md`, and `playbook/CONTROL_PLANE.md`.
- `PASS` — It identifies four path-specific onboarding friction points and
  proposes bounded fixes.
- `PASS` — It recommends the Phase 0 runtime manifest and makes no out-of-scope
  implementation recommendation part of the task.
- `PASS` — The required handoff exists and links the report.

## Scope and evidence check

- `PASS` — Files created after the task record: only
  `work/reviews/TASK-001-onboarding-report.md` and
  `work/handoffs/TASK-001-onboarding-handoff.md` before this review artifact.
- `PASS` — The helper explicitly states it did not read or modify `legacy/` or
  runtime sources, consistent with the test's purpose.
- `PASS` — `git diff --check` passed according to the helper; reviewer file
  inspection found valid Markdown and working relative task/report links.

## Findings

- `RECOMMENDED` — `README.md`: add a direct first-run link to
  `playbook/CONTROL_PLANE.md` and explain that a newly assigned agent reads
  unrelated current state for constraints, not ownership.
- `RECOMMENDED` — `playbook/INDEX.md`: add a table row for understanding the
  retained control plane.
- `RECOMMENDED` — Phase 0 of DEC-001 should create an active-runtime manifest
  with hcom availability/status and safe-usage entrypoints.

None of these prevent a capable first-time agent from operating safely, so they
do not block approval. They are useful inputs to the next DEC-001 task.

