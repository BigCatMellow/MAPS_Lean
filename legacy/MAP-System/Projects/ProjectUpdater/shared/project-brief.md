<!-- hpom: file: shared/project-brief.md -->
<!-- hpom: project: ProjectUpdater -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-03 -->
<!-- hpom: verified_against: bootstrap -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Project Brief — ProjectUpdater

## Objective

Build a working implementation of the "Project Updater" design (a
personal project/task tracker) sourced from a Claude Design project:
`https://claude.ai/design/p/9e3f5e32-b481-4f33-8091-67f8b3456daf?file=Project+Updater.dc.html`.

The app should let a single user:

- see a dashboard of active/stale/due-soon projects and recent notes;
- browse and filter all projects (open, stale, due soon, finished,
  archived);
- capture a quick note against a project (resets its idle clock, can
  update status/progress);
- add a new project with a goal, next action, priority, reminder window,
  and optional due date.

## Completion condition

- All four views (Dashboard, Projects, Quick Note, Add Project) are
  implemented and functional against real, persisted data (not sample
  data).
- Stale detection (`daysIdle >= reminderDays`) and due-soon detection
  (due within 7 days) work correctly against real dates, not hardcoded
  sample values.
- Data survives a page reload (persisted in `localStorage`).
- Visual design matches the dark theme from `Project Updater.dc.html`
  (colors, layout, typography) reasonably closely — this is a personal
  tool, not a pixel-perfect handoff.
- No server/backend dependency; runs by opening the HTML file directly.

## Non-goals

- No multi-user support, accounts, or sync.
- No mobile-native app; a responsive web page is sufficient.
- Not replicating the Google-Apps-Script-specific backend from the
  earlier prototype — its data model and UI logic are reused, its
  `google.script.run` calls are not.

## Steps outline format (added 2026-08-10)

Each project may carry a `steps` checklist, independent of the freeform
`goals` list, driving an auto-computed progress percent. Format (standard
GFM nested task list, one level of nesting):

```markdown
## Phase or category label
- [ ] Top-level step
  - [ ] Sub-goal (2-space indent)
  - [x] Completed sub-goal
- [x] A step with no sub-goals is itself a leaf
```

A step with sub-goals becomes a group header (its own checkbox is not
independently toggled — shown as an `x/y` fraction instead); a step with
none is a normal checkbox. Progress is `done leaves / total leaves`, where
a leaf is either a childless step or a sub-goal — parent group headers are
never double-counted.

Apply via `scripts/project_updater_command.py new|update --steps-file
<path>` (replaces the whole checklist), or edit directly in the Add/Edit
form's "Steps outline" textarea, or click checkboxes in the app.

**Convention this enables**: when starting or re-planning any project (MAP
work or otherwise), write the plan's phases/work-packages directly in this
format from the outset — not as prose to be manually converted later. A
plan authored this way is import-ready into ProjectUpdater immediately,
and stays the single source of truth for both the written plan and the
tracked checklist. See
`MAP_System/artifacts/planning/map-2-research-adoption-implementation-program-2026-08-09.md`
next to its ProjectUpdater-imported form (project "MAP Bedrock") for a
worked example of the same phases in both representations.
