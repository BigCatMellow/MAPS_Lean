<!-- hpom: file: shared/project-brief.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-16 -->
<!-- hpom: verified_against: bootstrap (hcom #311) -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Project Brief — ClearFront

## Objective

Take over improvement of the ClearFront trading card game prototype
(operator directive, hcom #311, 2026-07-16), sourced from
`/home/mellow/Documents/Projects/ClearFront`. The operator's stated goals:

- Preserve the good parts of the existing prototype.
- Use the MAP system (task/review/release gates, durable state) to
  improve it going forward instead of ad hoc single-session edits.
- Follow the game's own governing design principles and current rules —
  simplicity is a stated core value, not just an aesthetic preference.
- Copy the project into this workspace and work on the copy, not the
  original.
- Break the game out of one large HTML file into a maintainable modular
  structure.
- Claude leads and orchestrates, including Fable-model helpers; Pi
  ("Pi agent") also participates with its own bounded lane.

## Completion condition

There is no single "done" state yet — this is an ongoing improvement
project, not a one-shot build. A completion condition for the *first*
phase (source-preservation + modularization, tracked as TASK-207+):

- Original prototype preserved byte-for-byte under `source/` with a
  hash manifest (done — see `source/SHA256SUMS.txt`).
- A reproducibly-extracted, runnable baseline exists outside `source/`
  that is provably equivalent to the original bundle (parity smoke-test
  passing) before any behavior changes are made.
- The baseline is split into separate files by concern (at minimum:
  structure/markup, styles, card/deck data, rules/state-engine, AI
  behavior, rendering, input/event wiring) rather than one monolithic
  HTML file, with no loss of functionality versus the baseline.
- Design-principle and rules-conformance audit exists comparing the
  implementation against `clearfront_design_principles.md` and
  `clearfront_rules.md`, so game-improvement work after this phase has a
  known-accurate starting point.

Later phases (game balance/content improvements, new cards/mechanics)
are out of scope for this brief and should get their own task(s) once
the modular baseline exists, evaluated against the Design Review
Checklist in `clearfront_design_principles.md` section 21.

## Non-goals (for this phase)

- No rules/balance changes bundled into the extraction/decomposition
  work — those are separate, reviewable changes so regressions stay
  attributable (per Lilo's intake handoff risk notes).
- No framework/build-tooling rewrite (e.g. React+bundler pipeline)
  unless a later decision explicitly adopts one; "modular" here means
  separated files, not a mandated new stack.
- No server/backend dependency (SCOPE-class change, needs command-center
  approval per `AGENTS.md` decision paths).
