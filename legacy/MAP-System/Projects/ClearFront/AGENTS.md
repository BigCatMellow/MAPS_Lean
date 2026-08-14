# Agent Instructions — ClearFront

Follow the root `AGENTS.md` and `MAP_System/AGENTS.md` as the canonical
collaboration protocol. This file adds project-specific notes only.

## Scope

ClearFront is a browser-based trading card game prototype. It currently
exists as a single self-extracting HTML bundle (`source/` — untouched
original, do not edit) plus governing design docs. The operator directive
(hcom #311, 2026-07-16) asked MAP to take over improving it: preserve the
original, extract a reproducible/editable baseline, split it into modules
instead of one large HTML file, and improve the game following its own
design principles and rules.

Governing design inputs (treat as binding constraints, not background
reading):

- `source/game-card-combat-effects/clearfront_design_principles.md` —
  "simple cards, complex situations," no purple mechanics, one job per
  system. Read this before proposing any new mechanic or card.
- `source/game-card-combat-effects/clearfront_rules.md` — current
  playtest ruleset (20 life, 3-card hand, 2-card turn limit, Champions,
  6 factions). Treat as the spec the implementation must match, and as
  something the team may propose changes to only via the design
  principles' checklist (Design Review Checklist, section 21).

## Decision paths

- Routine implementation, refactor-only decomposition, bug fixes, and UI
  adjustments that keep current rules intact: core agent decides and
  records directly (ARCHITECTURE/OWNERSHIP class per
  `MAP_System/DECISION_CLASSES.md`).
- Any change to game balance/rules (numbers, keywords, card text, win
  condition) beyond what `clearfront_rules.md` already states: record as
  a decision in `shared/decisions.md` and treat as SCOPE-class — flag to
  command-center before shipping if it is not obviously implied by the
  existing rules doc.
- Adding a server/network dependency, or anything that changes what the
  game is allowed to depend on: escalate to command-center first (SCOPE
  class).

## Orchestration note

Claude leads this project per operator instruction (hcom #311), including
coordinating Fable-model helpers for implementation/decomposition work and
Pi for its own bounded lane. Codex (lilo) did the initial read-only source
inventory (`MAP_System/handoffs/HANDOFF-CLEARFRONT-intake-codex-lab-lilo-to-claude-lab-gome.md`)
and made no source or destination edits — normal MAP task ownership rules
apply from here on (one accountable owner per active task, no self-review
on gated deliverables).

## Source handling

- `source/` holds the untouched original copy (bundle, docs, assets,
  archive zip) plus `source/SHA256SUMS.txt` for provenance. Never edit
  files under `source/` — if the original changes, re-copy and re-hash.
- The extracted, editable baseline and its modular decomposition live
  outside `source/` (see the extraction task for the target layout).
