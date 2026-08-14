# Writing project outlines for ProjectUpdater

How to write a plan so it imports directly into ProjectUpdater as a
tracked checklist, instead of writing prose and converting it later.

## Format

Standard GitHub-flavored Markdown task list, one level of nesting:

```markdown
## Phase or category label
- [ ] Top-level step
  - [ ] Sub-goal (2-space indent)
  - [x] Completed sub-goal
- [x] A step with no sub-goals is itself a leaf, done
- [ ] Another top-level step with no sub-goals
```

Rules:

- `## Heading` lines set the "phase" label shown above each group of
  steps. Any heading level 1-6 works; only the text is used.
- A step is a `- [ ]` or `- [x]` (or `[X]`) line. `x`/`X` = done.
- A sub-goal is the same syntax indented by leading whitespace (2 spaces
  is the convention; any consistent indent works — the parser only
  checks whether the line has leading whitespace before the `-`).
- A step **with** sub-goals becomes a group header: its own checkbox
  isn't independently toggled in the app — it shows an `x/y` fraction
  instead, derived from its sub-goals.
- A step **without** sub-goals is a normal, directly-toggleable
  checkbox, and counts as its own leaf.
- Blank lines separate items but aren't required between every line.
- **Wrapped/continuation lines**: a plain text line immediately after a
  step or sub-goal (not itself starting with `- [ ]`, and not blank) is
  appended to that item's text. Use this for long sub-goal descriptions
  instead of one unreadable 200-character line:

  ```markdown
  - [ ] P0.2: Durable validation debt (TASK-323, READY)
    - [ ] events.jsonl NUL corruption repaired on Smalls (REPAIR-0013
      follow-up, applied directly on Smalls; verified byte-identical
      clean line 18785 on both hosts, validate_events.py errors=0)
  ```

  A blank line ends the continuation — don't leave one in the middle of
  a multi-line item.

## Progress calculation

Progress is `done leaves / total leaves`, where a **leaf** is either a
childless top-level step or a sub-goal. Group-header parents are never
counted themselves — only their children are — so adding sub-goals to a
step doesn't silently inflate or deflate the percentage in a surprising
way.

## Letter labels (a., b., c., ...)

The app automatically prefixes each sub-goal with a letter label
(`a.`, `b.`, `c.`, ... `z.`, `aa.`, `ab.`, ...) based on its position
under its parent step. This is purely a **display** feature — it is
derived at render time from array order, not stored in the source
markdown. Don't write letters into the outline yourself; just write
plain sub-goal text and the app labels them for you. This is what makes
"P0.2.a" a stable, speakable reference to a specific sub-goal in
conversation.

## Applying an outline

Three ways, all round-trip through the same parser:

1. **CLI** (bulk import/replace — this is the normal way to publish a
   plan):
   ```bash
   python3 Projects/ProjectUpdater/scripts/project_updater_command.py \
     update "Project Name" --steps-file path/to/outline.md
   ```
   For a new project, use `new` instead of `update` (see `--help` for
   the full set of flags: `--area`, `--goal`, `--next-action`,
   `--priority`, `--status`, `--progress`, `--due-date`, etc.). Omit
   `--progress` to let it auto-compute from the outline's checkboxes.

2. **In-app**: the Add/Edit project form has a "Steps outline" textarea
   that accepts the exact same markdown.

3. **Click-to-toggle**: once imported, clicking a checkbox in the app
   flips that leaf's done state and recomputes progress — this does
   *not* write back to your source `.md` file, so treat the file as the
   durable source of truth and re-import after editing it, not the
   other way around.

## Convention: write plans in this format from the start

When starting or re-planning any project, write the phases/work
packages directly in this format in the plan document itself — not as
prose to be manually converted into a checklist later. That plan
document is then both the readable spec and the ProjectUpdater-ready
import source in one file; re-run the `update --steps-file` command
whenever the plan changes to keep the two in sync.

Worked example: `MAP_System/artifacts/planning/map-bedrock-phase-checklist-2026-08-10.md`
next to its imported form (the "MAP Bedrock" project in ProjectUpdater).
That file also shows the optional HPOM header convention for
durable/agent-readable planning docs:

```markdown
<!-- hpom: file: artifacts/planning/your-file-name.md -->
<!-- hpom: project: YOUR-PROJECT-ID -->
<!-- hpom: state_owner: your-agent-name -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: YYYY-MM-DD -->
<!-- hpom: confidence: HIGH -->
```

## Minimal full example

```markdown
<!-- hpom: file: artifacts/planning/example-plan.md -->
<!-- hpom: status: CURRENT -->

## Phase 0 — Setup
- [x] Repo scaffolding created
- [ ] CI pipeline configured
  - [x] Lint job
  - [ ] Test job
  - [ ] Deploy job

## Phase 1 — Core feature
- [ ] Design the data model
- [ ] Implement the API
  - [ ] Endpoint: create
  - [ ] Endpoint: read
- [ ] Write tests
```

This imports as: Phase 0 (2 top-level items, one a 1/3 group), Phase 1
(3 top-level items, one a 0/2 group) — 3 done / 8 total leaves = 37%.
