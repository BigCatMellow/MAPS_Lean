# Roadmaps and ProjectUpdater Checklists

Write a roadmap as a trackable Markdown checklist from the start. This makes it
both the human-readable plan and the import source for ProjectUpdater.

Start from [the roadmap template](../templates/roadmap.md). A draft roadmap can
explore approved options, but its checkboxes never authorize implementation,
spending, or an external change by themselves.

```markdown
## Phase 0 — Foundation
- [x] Establish project brief
- [ ] Define acceptance tests

## Phase 1 — Delivery
- [ ] Build the feature
  - [ ] Implement the core behavior
  - [ ] Add verification
- [ ] Independent review
```

## Rules

- Headings define phases or categories.
- A checkbox without children is a trackable leaf.
- A checkbox with indented checkbox children is a group; progress comes from
  the leaves, not the parent.
- Keep each leaf concrete, observable, and small enough to be meaningfully
  complete.
- Update this source document first. Re-import it after changes; do not treat a
  browser UI’s toggled state as the durable plan.

For the legacy ProjectUpdater app, import with its command tool:

```bash
python3 legacy/MAP-System/Projects/ProjectUpdater/scripts/project_updater_command.py \
  update "Project Name" --steps-file path/to/roadmap.md
```

The full parser conventions are preserved in
`legacy/MAP-System/Projects/ProjectUpdater/shared/steps-outline-guide.md`.
