<!-- hpom: file: shared/requirements.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-16 -->
<!-- hpom: verified_against: bootstrap (hcom #311) -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Requirements — ClearFront

## Functional

- The extracted/decomposed implementation must remain playable end to
  end (deck select, mana, hand of 3, 2-card turn limit, Champion deploy,
  combat with blocking, persistent damage, keywords, win at 0 life) with
  no regression versus the original bundle, unless a change is an
  explicitly recorded rules decision.
- Runs by opening an HTML entry point in a browser; no server/backend
  dependency (see project-brief non-goals).

## Design conformance

Every new card, mechanic, or system change must be checked against
`source/game-card-combat-effects/clearfront_design_principles.md`
section 21 (Design Review Checklist: Clarity, Depth, Necessity, Identity,
Tracking) before it is proposed as a task. Reject or simplify anything
that reads as a "purple mechanic" per section 3.

## Non-functional

- Single logical entry point remains easy to open and run, even though
  the implementation is split across multiple files (module loading must
  not require a build step unless a later ARCHITECTURE decision adopts
  one).
- No silent loss of embedded assets or third-party resources during
  extraction — provenance-preserving (hash before/after).
- Refactoring (decomposition) and behavior/balance changes are kept in
  separate tasks so regressions are attributable to one or the other.

## Quality bar

- Any task that touches the state engine or combat resolution needs a
  parity check against the previous behavior (smoke test or manual
  playtest trace) before submission, not just "it compiles/loads."
- Any task proposing a rules or balance change records it in
  `shared/decisions.md` and cites which design-principle question(s)
  motivated it.
