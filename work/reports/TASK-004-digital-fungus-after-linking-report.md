# Digital Fungus Report

## Purpose

A read-only knowledge-graph pass over MAP Lean. It models active notes as
the growth zone and treats `legacy/` / `archive/` as reachable but
high-resistance reference territory. Findings are proposals for human
review, not automatic link edits.

## Snapshot

- Notes scanned: 1480 (44 active)
- Resolved internal edges: 345
- Unresolved internal links: 139 (0 active)
- Unlinked file mentions: 522 (119 active)
- Active orphans: 9
- Active notes reachable from `docs/FIRST_RUN.md`: 24

## Findings

### Unresolved internal links

None found in active Lean material by this parser.

Legacy/reference material has 139 unresolved candidate links; treat these as historical cleanup evidence, not an onboarding defect.

### Unlinked navigational references

These code-styled paths are readable to an agent but invisible as graph edges in Obsidian. Review them as candidates for real links:

- `playbook/INDEX.md` mentions `legacy/MAP-System/MAP_System/shared/hpom.md`
- `playbook/INDEX.md` mentions `legacy/MAP-System/Projects/ProjectUpdater/shared/steps-outline-guide.md`
- `playbook/ROADMAP_AND_PROJECTUPDATER.md` mentions `legacy/MAP-System/Projects/ProjectUpdater/shared/steps-outline-guide.md`
- `playbook/SOURCE_CATALOG.md` mentions `docs/CHECKS_AND_BALANCES.md`
- `playbook/SOURCE_CATALOG.md` mentions `docs/CONTEXT.md`
- `playbook/SOURCE_CATALOG.md` mentions `playbook/DECISIONS_AND_SAFETY.md`
- `playbook/SOURCE_CATALOG.md` mentions `playbook/EMERGENCE.md`
- `playbook/SOURCE_CATALOG.md` mentions `playbook/HELPERS_AND_COMMUNICATION.md`
- `playbook/SOURCE_CATALOG.md` mentions `playbook/HPOM_ROUTING.md`
- `playbook/SOURCE_CATALOG.md` mentions `playbook/INFORMATION_LIFECYCLE.md`
- `playbook/SOURCE_CATALOG.md` mentions `playbook/PROJECT_BOOTSTRAP.md`
- `playbook/SOURCE_CATALOG.md` mentions `playbook/REPAIR_AND_LEARNING.md`
- `playbook/SOURCE_CATALOG.md` mentions `playbook/RESEARCH.md`
- `playbook/SOURCE_CATALOG.md` mentions `playbook/RISK_AND_CHANGE.md`
- `playbook/SOURCE_CATALOG.md` mentions `playbook/ROADMAP_AND_PROJECTUPDATER.md`
- `playbook/SOURCE_CATALOG.md` mentions `playbook/TASK_LIFECYCLE.md`
- `playbook/SOURCE_CATALOG.md` mentions `templates/decision.md`
- `playbook/SOURCE_CATALOG.md` mentions `templates/review.md`
- `playbook/SOURCE_CATALOG.md` mentions `templates/task.md`
- `work/handoffs/TASK-001-onboarding-handoff.md` mentions `AGENTS.md`
- `work/handoffs/TASK-001-onboarding-handoff.md` mentions `README.md`
- `work/handoffs/TASK-001-onboarding-handoff.md` mentions `playbook/CONTROL_PLANE.md`
- `work/handoffs/TASK-002-question-led-onboarding-handoff.md` mentions `AGENTS.md`
- `work/handoffs/TASK-002-question-led-onboarding-handoff.md` mentions `docs/FIRST_RUN.md`
- `work/handoffs/TASK-002-question-led-onboarding-handoff.md` mentions `playbook/CONTROL_PLANE.md`
- `work/handoffs/TASK-002-question-led-onboarding-handoff.md` mentions `playbook/INDEX.md`
- `work/handoffs/TASK-002-question-led-onboarding-handoff.md` mentions `state/CURRENT.md`
- `work/handoffs/TASK-002-question-led-onboarding-handoff.md` mentions `work/reviews/TASK-002-question-led-onboarding-report.md`
- `work/reports/TASK-003-digital-fungus-report.md` mentions `AGENTS.md`
- `work/reports/TASK-003-digital-fungus-report.md` mentions `README.md`

### Active orphans

- `templates/project-brief.md`
- `templates/repair-record.md`
- `templates/research-brief.md`
- `templates/retrospective.md`
- `templates/risk-register.md`
- `templates/roadmap.md`
- `work/reports/TASK-003-digital-fungus-report.md`
- `work/tasks/TASK-003-digital-fungus-pilot.md`
- `work/tasks/TASK-004-link-the-active-navigation-spine.md`

### High-traffic active notes

| Note | Incoming | Outgoing | Kind |
| --- | ---: | ---: | --- |
| `playbook/INDEX.md` | 3 | 15 | method |
| `AGENTS.md` | 2 | 5 | root |
| `docs/FIRST_RUN.md` | 2 | 4 | guide |
| `state/CURRENT.md` | 4 | 1 | state |
| `README.md` | 0 | 4 | root |
| `work/tasks/TASK-002-question-led-onboarding-simulation.md` | 3 | 0 | task |
| `work/tasks/TASK-001-first-run-onboarding-simulation.md` | 3 | 0 | task |
| `templates/task.md` | 3 | 0 | template |
| `playbook/PROJECT_BOOTSTRAP.md` | 1 | 2 | method |
| `templates/handoff.md` | 2 | 0 | template |
| `playbook/CONTROL_PLANE.md` | 2 | 0 | method |
| `work/reviews/TASK-001-onboarding-report.md` | 1 | 1 | review |

### First-run resilience

- Removing `playbook/INDEX.md` makes 14 active note(s) unreachable from FIRST_RUN: `docs/CONTEXT.md`, `playbook/DECISIONS_AND_SAFETY.md`, `playbook/EMERGENCE.md`, `playbook/HELPERS_AND_COMMUNICATION.md`, `playbook/HPOM_ROUTING.md`, `playbook/INFORMATION_LIFECYCLE.md`, `playbook/PROJECT_BOOTSTRAP.md`, `playbook/REPAIR_AND_LEARNING.md`
- Removing `AGENTS.md` makes 2 active note(s) unreachable from FIRST_RUN: `docs/CHECKS_AND_BALANCES.md`, `templates/review.md`
- Removing `state/CURRENT.md` makes 1 active note(s) unreachable from FIRST_RUN: `work/decisions/DEC-001-target-operating-model-and-wezterm-decoupling.md`
- Removing `playbook/PROJECT_BOOTSTRAP.md` makes 1 active note(s) unreachable from FIRST_RUN: `templates/decision.md`
- Removing `docs/CHECKS_AND_BALANCES.md` makes 1 active note(s) unreachable from FIRST_RUN: `templates/review.md`

## Interpretation

- A link is a navigational claim, not proof that a note is current or authoritative.
- Prioritize fixing broken links and onboarding-path gaps before adding visual density.
- Review orphan notes before linking them: some should remain intentionally isolated templates or records.
- Use Obsidian Graph/Local Graph to inspect the same link topology visually; standard Markdown links and wikilinks are both parsed.

## Limitations

- Link topology is not semantic relevance or truth.
- Bare wikilinks resolve only when the filename is unique.
- External URLs are ignored as graph edges.
- No proposed link is applied automatically.
