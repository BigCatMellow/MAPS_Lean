# Roadmaps and ProjectUpdater Checklists

**Look at reality. Define the destination. Plan backward. Challenge the plan. Execute forward. Adapt as you learn.**

A roadmap starts with the finished goal, not with a pile of tasks.

## Before the roadmap

1. Inspect the current reality: product, code, users, data, constraints, prior
   attempts, or other direct evidence that matters. Record what was actually
   checked and separate facts from assumptions.
2. Define **DONE** in observable terms, especially from the user or operator's
   point of view.
3. Define the final proof: what test, review, build, release, or user-visible
   result proves DONE. The proof must be something an agent or operator can
   actually perform or inspect.
4. Set boundaries:
   - what is in scope;
   - what is explicitly not being done;
   - how much time, effort, or cost the project is worth before reconsidering;
   - which unknowns must be researched or prototyped before commitment.

## Build the draft roadmap backward

1. Ask what must be true immediately before the final proof can pass.
2. Keep working backward until the chain reaches the project's current state.
3. If a required condition is unknown, record the unknown and create research,
   inspection, or prototype work for it. Do not fill gaps with invented facts.
4. Turn the backward chain around into forward execution phases.
5. Mark dependencies, integration points, and work that can safely happen in
   parallel.
6. Keep distant phases broad. Make the current phase and first-wave tasks much
   more detailed.
7. Convert dangerous unknowns into explicit research, inspection, or prototype
   steps instead of hiding them inside implementation tasks.

For a multi-agent or consequential project, review this **draft** roadmap in the
project **mission meeting** before implementation begins. Relevant agents should
look for missing work, bad assumptions, dependency mistakes, risks, weak tests,
unnecessary scope, and useful parallel work. The accountable owner integrates
the findings; the operator decides changes that materially affect scope, cost,
risk, or user-visible behavior.

The mission meeting must leave a durable result containing:

- assumptions accepted, rejected, or still unknown;
- roadmap changes;
- unresolved questions and their owners;
- operator decisions still needed;
- the first wave of work ready to shape or assign.

After the meeting, revise the draft into the **working roadmap** and assign the
first wave of work. Do not pretend every future task is knowable in advance.
Some tasks will only become clear after real work produces new evidence.

Before an implementation task starts, its task record—not the roadmap checkbox
alone—must define its owner, inputs, allowed outputs, dependencies, pass/fail
criteria, verification, and required review.

The roadmap is the durable plan, not authority by itself. A checkbox never
authorizes spending, destructive action, external changes, or a scope change.

Write the working roadmap as a trackable Markdown checklist. This makes it both
the human-readable plan and the import source for ProjectUpdater.

Start from [the roadmap template](../templates/roadmap.md).

```markdown
## Definition of DONE
- <observable finished result>
- Final proof: <how we know it works>

## Boundaries
- In scope: <...>
- Not doing: <...>
- Effort limit: <when to reconsider>

## Phase 0 — Foundation
- [x] Establish project brief
- [ ] Resolve the highest-risk unknown

## Phase 1 — Delivery
- [ ] Build the first usable slice
  - [ ] Implement the core behavior
  - [ ] Verify it works

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
- Once assigned, link or name the task record and owner rather than relying on
  an unlabeled checkbox to communicate responsibility.
- Record dependencies when a task cannot safely start before another finishes.
- Name one integration owner when parallel work must be combined.
- Prefer a usable end-to-end slice over many disconnected partial pieces when
  that gives earlier proof the plan works.
- Require a checkpoint after major phases or usable results, on failed key
  assumptions, when named risks become real, when the effort limit is reached,
  and before consequential hard-to-reverse changes.
- At each checkpoint choose and record: **CONTINUE, CHANGE, CUT SCOPE, RESEARCH,
  or STOP**, plus the reason and next action.
- Re-plan when evidence shows the roadmap is wrong; do not keep executing a bad
  plan merely because it was approved earlier.
- Refine later phases as they approach instead of filling them with guessed
  detail too early.
- Update this source document first. Re-import it after changes; do not treat a
  browser UI's toggled state as the durable plan.

## Why these rules exist

MAPS borrows useful ideas, not whole corporate systems:

- **Amazon:** start from the desired customer result and force hard questions
  before building.
- **Toyota:** inspect the real situation, use evidence, then improve the plan as
  reality teaches you more.
- **Google:** make goals, roles, and expected results clear enough that a team
  can coordinate and challenge the plan.
- **Basecamp:** shape work before committing it; set boundaries, expose risky
  unknowns, and do not confuse imagined future tasks with work discovered while
  building.
- **GV / Google Ventures:** when a major assumption is uncertain, learn or test
  it cheaply before spending heavily on implementation.

Use the principle that solves the problem. Do not copy company-specific ritual
when a simpler MAPS rule does the same job.

For the legacy ProjectUpdater app, import with its command tool:

```bash
python3 legacy/MAP-System/Projects/ProjectUpdater/scripts/project_updater_command.py \
  update "Project Name" --steps-file path/to/roadmap.md
```

The full parser conventions are preserved in
`legacy/MAP-System/Projects/ProjectUpdater/shared/steps-outline-guide.md`.
