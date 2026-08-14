# Roadmaps and ProjectUpdater Checklists

**Plan backward. Execute forward.**

A roadmap starts with the finished goal, not with a pile of tasks.

## Build the roadmap backward

1. Define **DONE** in observable terms.
2. Define the final proof: what test, review, build, release, or user-visible
   result proves DONE.
3. Ask what must be true immediately before that proof can pass.
4. Keep working backward until the chain reaches the project's current state.
5. Turn that chain around into forward execution phases.
6. Mark dependencies, integration points, and work that can safely happen in
   parallel.
7. Break phases into concrete tasks with clear owners and pass/fail results.

For a multi-agent or consequential project, review the draft roadmap in the
project **mission meeting** before implementation begins. Relevant agents should
look for missing work, bad assumptions, dependency mistakes, risks, weak tests,
and useful parallel work. The accountable owner integrates the findings; the
operator decides changes that materially affect scope, cost, risk, or
user-visible behavior.

The roadmap is the durable plan, not authority by itself. A checkbox never
authorizes spending, destructive action, external changes, or a scope change.

Write the approved roadmap as a trackable Markdown checklist from the start.
This makes it both the human-readable plan and the import source for
ProjectUpdater.

Start from [the roadmap template](../templates/roadmap.md).

```markdown
## Definition of DONE
- <observable finished result>
- Final proof: <how we know it works>

## Phase 0 — Foundation
- [x] Establish project brief
- [ ] Define acceptance tests

## Phase 1 — Delivery
- [ ] Build the feature
  - [ ] Implement the core behavior
  - [ ] Add verification

## Phase 2 — Integration and final proof
- [ ] Integrate completed work
- [ ] Independent review
- [ ] Run final acceptance test
```

## Rules

- Headings define phases or categories.
- A checkbox without children is a trackable leaf.
- A checkbox with indented checkbox children is a group; progress comes from
  the leaves, not the parent.
- Keep each leaf concrete, observable, and small enough to be meaningfully
  complete.
- Record dependencies when a task cannot safely start before another finishes.
- Name one integration owner when parallel work must be combined.
- Re-plan when evidence shows the roadmap is wrong; do not keep executing a bad
  plan merely because it was approved earlier.
- Update this source document first. Re-import it after changes; do not treat a
  browser UI's toggled state as the durable plan.

For the legacy ProjectUpdater app, import with its command tool:

```bash
python3 legacy/MAP-System/Projects/ProjectUpdater/scripts/project_updater_command.py \
  update "Project Name" --steps-file path/to/roadmap.md
```

The full parser conventions are preserved in
`legacy/MAP-System/Projects/ProjectUpdater/shared/steps-outline-guide.md`.
