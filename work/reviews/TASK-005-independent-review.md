# Review: TASK-005 linked route-selection simulation

- Task: [TASK-005](../tasks/TASK-005-linked-route-selection-simulation.md)
- Reviewer: Codex independent reviewer
- Verdict: `APPROVED_AFTER_FIXES`

## Acceptance criteria check

- `PASS` — The helper followed the active Markdown route from README through
  FIRST_RUN and the playbook index, without a directory-wide discovery search.
- `PASS` — It considered Research, Project Bootstrap, Risk and Change Control,
  Roadmaps/ProjectUpdater, and Task Lifecycle; its minimum selected set is
  appropriately bounded.
- `PARTIAL` — The report identifies the needed project records, but it cannot
  identify the exact existing project-brief, research-brief, risk-register, and
  roadmap templates through the linked route. It explicitly reports those
  templates as not linked.
- `PASS` — Research, proposed decision, operator approval, roadmap, and
  implementation authority are separated correctly. A proposed roadmap may be
  drafted for discussion, but it must not imply budget/design approval or
  authorize implementation.
- `PASS` — Coordinator received six bounded live updates, within the cap; the
  report and handoff are the only helper-created paths.

## Required correction

Link these existing templates from the relevant active methods:

- `templates/project-brief.md` from `playbook/PROJECT_BOOTSTRAP.md`
- `templates/research-brief.md` from `playbook/RESEARCH.md`
- `templates/risk-register.md` from `playbook/RISK_AND_CHANGE.md` and/or
  `playbook/PROJECT_BOOTSTRAP.md`
- `templates/roadmap.md` from `playbook/ROADMAP_AND_PROJECTUPDATER.md`

Completed: the four template links now exist at the corresponding method
decision points. A focused link traversal verifies all targets resolve. This is
a documentation/graph correction only; it does not authorize any API,
ProjectUpdater, architecture, budget, or implementation work.

## Evidence checked

- Helper report and handoff.
- `README.md`, `docs/FIRST_RUN.md`, `playbook/INDEX.md`,
  `playbook/RESEARCH.md`, `playbook/PROJECT_BOOTSTRAP.md`,
  `playbook/RISK_AND_CHANGE.md`, `playbook/ROADMAP_AND_PROJECTUPDATER.md`.
- Existing but unlinked templates listed above.
