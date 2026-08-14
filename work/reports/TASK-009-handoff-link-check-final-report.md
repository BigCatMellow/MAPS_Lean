# Digital Fungus Report

## Purpose

A read-only knowledge-graph pass over MAP Lean. It models active notes as
the growth zone and treats `legacy/` / `archive/` as reachable but
high-resistance reference territory. Findings are proposals for human
review, not automatic link edits.

## Snapshot

- Notes scanned: 1503 (67 active)
- Resolved internal edges: 429
- Unresolved internal links: 139 (0 active)
- Unlinked file mentions: 731 (328 active)
- Active orphans: 7
- Active notes reachable from `docs/FIRST_RUN.md`: 38

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
- `work/handoffs/TASK-005-linked-route-selection-handoff.md` mentions `README.md`
- `work/handoffs/TASK-005-linked-route-selection-handoff.md` mentions `docs/FIRST_RUN.md`

### Active orphans

- `templates/retrospective.md`
- `work/reports/TASK-003-digital-fungus-report.md`
- `work/reports/TASK-004-digital-fungus-after-linking-report.md`
- `work/reports/TASK-007-post-repair-fungus-report.md`
- `work/reports/TASK-009-handoff-link-check-report.md`
- `work/tasks/TASK-003-digital-fungus-pilot.md`
- `work/tasks/TASK-004-link-the-active-navigation-spine.md`

### High-traffic active notes

| Note | Incoming | Outgoing | Kind |
| --- | ---: | ---: | --- |
| `playbook/INDEX.md` | 7 | 16 | method |
| `work/reviews/TASK-005-linked-route-selection-report.md` | 1 | 14 | review |
| `work/reviews/TASK-008-returning-agent-report.md` | 3 | 10 | review |
| `work/handoffs/2026-08-13-lean-navigation-and-simulation-tuning.md` | 1 | 11 | handoff |
| `AGENTS.md` | 6 | 5 | root |
| `state/CURRENT.md` | 8 | 2 | state |
| `docs/FIRST_RUN.md` | 6 | 4 | guide |
| `README.md` | 4 | 4 | root |
| `work/reviews/TASK-007-repair-record-link-report.md` | 2 | 6 | review |
| `playbook/SIMULATION_DESIGN.md` | 3 | 4 | method |
| `playbook/REPAIR_AND_LEARNING.md` | 5 | 1 | method |
| `playbook/PROJECT_BOOTSTRAP.md` | 2 | 4 | method |

### First-run resilience

- Removing `playbook/INDEX.md` makes 16 active note(s) unreachable from FIRST_RUN: `playbook/DECISIONS_AND_SAFETY.md`, `playbook/EMERGENCE.md`, `playbook/HPOM_ROUTING.md`, `playbook/INFORMATION_LIFECYCLE.md`, `playbook/PROJECT_BOOTSTRAP.md`, `playbook/REPAIR_AND_LEARNING.md`, `playbook/RESEARCH.md`, `playbook/RISK_AND_CHANGE.md`
- Removing `state/CURRENT.md` makes 9 active note(s) unreachable from FIRST_RUN: `README.md`, `work/decisions/DEC-001-target-operating-model-and-wezterm-decoupling.md`, `work/handoffs/2026-08-13-lean-navigation-and-simulation-tuning.md`, `work/handoffs/TASK-008-returning-agent-handoff.md`, `work/reports/TASK-008-post-simulation-fungus-report.md`, `work/reviews/TASK-008-independent-review.md`, `work/reviews/TASK-008-returning-agent-report.md`, `work/tasks/TASK-008-returning-agent-recovery-simulation.md`
- Removing `work/handoffs/2026-08-13-lean-navigation-and-simulation-tuning.md` makes 7 active note(s) unreachable from FIRST_RUN: `README.md`, `work/handoffs/TASK-008-returning-agent-handoff.md`, `work/reports/TASK-008-post-simulation-fungus-report.md`, `work/reviews/TASK-008-independent-review.md`, `work/reviews/TASK-008-returning-agent-report.md`, `work/tasks/TASK-008-returning-agent-recovery-simulation.md`, `work/tasks/TASK-008-simulated-prior-handoff.md`
- Removing `playbook/PROJECT_BOOTSTRAP.md` makes 2 active note(s) unreachable from FIRST_RUN: `templates/decision.md`, `templates/project-brief.md`
- Removing `work/reviews/TASK-008-independent-review.md` makes 1 active note(s) unreachable from FIRST_RUN: `work/handoffs/TASK-008-returning-agent-handoff.md`
- Removing `playbook/ROADMAP_AND_PROJECTUPDATER.md` makes 1 active note(s) unreachable from FIRST_RUN: `templates/roadmap.md`
- Removing `playbook/RESEARCH.md` makes 1 active note(s) unreachable from FIRST_RUN: `templates/research-brief.md`
- Removing `playbook/REPAIR_AND_LEARNING.md` makes 1 active note(s) unreachable from FIRST_RUN: `templates/repair-record.md`

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
