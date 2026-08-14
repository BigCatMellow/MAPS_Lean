# Task: First-run onboarding simulation

- Status: `DONE`
- Owner: `lean-onboarding-helper`
- Risk: `LOW`
- Type: `research / process evaluation`
- Goal: Test whether a capable agent given only this repository can orient,
  select the right active guidance, understand the retained control plane, and
  leave a useful durable report without relying on chat history or the legacy
  corpus as startup context.
- Allowed output paths:
  - `work/reviews/TASK-001-onboarding-report.md`
  - `work/reviews/TASK-001-independent-review.md`
  - `work/handoffs/TASK-001-onboarding-handoff.md`
- Do not change:
  - `legacy/`
  - runtime code, configuration, installers, databases, and launchers
  - `AGENTS.md`, `README.md`, `playbook/`, `docs/`, `templates/`, and
    `state/CURRENT.md`

## Acceptance criteria

- [x] The agent starts at the repository root and follows the active startup
  route without being directed to individual documents beyond this task.
- [x] The report identifies which active files it read, in order, and why each
  was selected.
- [x] The report explains the respective roles of SQLite, LangGraph, RnS,
  hcom, and WezTerm accurately enough for a future agent to act safely.
- [x] The report names at least three concrete onboarding ambiguities, missing
  links, or needless-friction points, each with a path and proposed fix.
- [x] The report recommends the smallest next action and does not make edits
  outside its allowed output paths.
- [x] A compact handoff records completion status and links the report.

## Verification

- Owner checks the output paths against this record.
- Independent reviewer checks accuracy against the active Lean docs and reports
  whether the onboarding path was sufficient.

## Notes

This is a deliberate usability exercise, not a request to implement the
recommendations. The helper may read `legacy/` only after completing the active
startup route and only to verify a specific control-plane claim.

## Completion

- Owner report: `work/reviews/TASK-001-onboarding-report.md`
- Handoff: `work/handoffs/TASK-001-onboarding-handoff.md`
- Independent review: `work/reviews/TASK-001-independent-review.md`
