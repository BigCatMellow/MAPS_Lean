# Digital Fungus Report

## Purpose

A read-only knowledge-graph pass over MAP Lean. It models active notes as
the growth zone and treats `legacy/` / `archive/` as reachable but
high-resistance reference territory. Findings are proposals for human
review, not automatic link edits.

## Snapshot

- Notes scanned: 1478 (42 active)
- Resolved internal edges: 311
- Unresolved internal links: 139 (0 active)
- Unlinked file mentions: 550 (147 active)
- Active orphans: 32
- Active notes reachable from `docs/FIRST_RUN.md`: 1

## Findings

### Unresolved internal links

None found in active Lean material by this parser.

Legacy/reference material has 139 unresolved candidate links; treat these as historical cleanup evidence, not an onboarding defect.

### Unlinked navigational references

These code-styled paths are readable to an agent but invisible as graph edges in Obsidian. Review them as candidates for real links:

- `AGENTS.md` mentions `docs/CHECKS_AND_BALANCES.md`
- `AGENTS.md` mentions `playbook/INDEX.md`
- `AGENTS.md` mentions `state/CURRENT.md`
- `AGENTS.md` mentions `templates/handoff.md`
- `AGENTS.md` mentions `templates/task.md`
- `README.md` mentions `AGENTS.md`
- `README.md` mentions `state/CURRENT.md`
- `README.md` mentions `templates/task.md`
- `docs/CHECKS_AND_BALANCES.md` mentions `templates/review.md`
- `docs/FIRST_RUN.md` mentions `AGENTS.md`
- `docs/FIRST_RUN.md` mentions `playbook/CONTROL_PLANE.md`
- `docs/FIRST_RUN.md` mentions `playbook/INDEX.md`
- `docs/FIRST_RUN.md` mentions `state/CURRENT.md`
- `docs/WORKFLOW.md` mentions `state/CURRENT.md`
- `playbook/INDEX.md` mentions `docs/CONTEXT.md`
- `playbook/INDEX.md` mentions `legacy/MAP-System/MAP_System/shared/hpom.md`
- `playbook/INDEX.md` mentions `legacy/MAP-System/Projects/ProjectUpdater/shared/steps-outline-guide.md`
- `playbook/INDEX.md` mentions `playbook/CONTROL_PLANE.md`
- `playbook/INDEX.md` mentions `playbook/DECISIONS_AND_SAFETY.md`
- `playbook/INDEX.md` mentions `playbook/EMERGENCE.md`
- `playbook/INDEX.md` mentions `playbook/HELPERS_AND_COMMUNICATION.md`
- `playbook/INDEX.md` mentions `playbook/HPOM_ROUTING.md`
- `playbook/INDEX.md` mentions `playbook/INFORMATION_LIFECYCLE.md`
- `playbook/INDEX.md` mentions `playbook/PROJECT_BOOTSTRAP.md`
- `playbook/INDEX.md` mentions `playbook/REPAIR_AND_LEARNING.md`
- `playbook/INDEX.md` mentions `playbook/RESEARCH.md`
- `playbook/INDEX.md` mentions `playbook/RISK_AND_CHANGE.md`
- `playbook/INDEX.md` mentions `playbook/ROADMAP_AND_PROJECTUPDATER.md`
- `playbook/INDEX.md` mentions `playbook/SOURCE_CATALOG.md`
- `playbook/INDEX.md` mentions `playbook/TASK_LIFECYCLE.md`

### Active orphans

- `AGENTS.md`
- `docs/CHECKS_AND_BALANCES.md`
- `docs/CONTEXT.md`
- `docs/WORKFLOW.md`
- `playbook/CONTROL_PLANE.md`
- `playbook/DECISIONS_AND_SAFETY.md`
- `playbook/EMERGENCE.md`
- `playbook/HELPERS_AND_COMMUNICATION.md`
- `playbook/HPOM_ROUTING.md`
- `playbook/INDEX.md`
- `playbook/INFORMATION_LIFECYCLE.md`
- `playbook/PROJECT_BOOTSTRAP.md`
- `playbook/REPAIR_AND_LEARNING.md`
- `playbook/RESEARCH.md`
- `playbook/RISK_AND_CHANGE.md`
- `playbook/ROADMAP_AND_PROJECTUPDATER.md`
- `playbook/SOURCE_CATALOG.md`
- `playbook/TASK_LIFECYCLE.md`
- `state/CURRENT.md`
- `templates/decision.md`
- `templates/handoff.md`
- `templates/project-brief.md`
- `templates/repair-record.md`
- `templates/research-brief.md`
- `templates/retrospective.md`
- `templates/review.md`
- `templates/risk-register.md`
- `templates/roadmap.md`
- `templates/task.md`
- `work/decisions/DEC-001-target-operating-model-and-wezterm-decoupling.md`
- `work/reports/TASK-003-digital-fungus-report.md`
- `work/tasks/TASK-003-digital-fungus-pilot.md`

### High-traffic active notes

| Note | Incoming | Outgoing | Kind |
| --- | ---: | ---: | --- |
| `work/tasks/TASK-002-question-led-onboarding-simulation.md` | 3 | 0 | task |
| `work/tasks/TASK-001-first-run-onboarding-simulation.md` | 3 | 0 | task |
| `work/reviews/TASK-001-onboarding-report.md` | 1 | 1 | review |
| `work/handoffs/TASK-001-onboarding-handoff.md` | 0 | 2 | handoff |
| `docs/FIRST_RUN.md` | 1 | 0 | guide |
| `work/reviews/TASK-002-question-led-onboarding-report.md` | 0 | 1 | review |
| `work/reviews/TASK-002-independent-review.md` | 0 | 1 | review |
| `work/reviews/TASK-001-independent-review.md` | 0 | 1 | review |
| `work/handoffs/TASK-002-question-led-onboarding-handoff.md` | 0 | 1 | handoff |
| `README.md` | 0 | 1 | root |
| `work/tasks/TASK-003-digital-fungus-pilot.md` | 0 | 0 | task |
| `work/reports/TASK-003-digital-fungus-report.md` | 0 | 0 | root |

### First-run resilience

No single intermediate active note disconnected another active note from FIRST_RUN in this directed-link pass.

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
