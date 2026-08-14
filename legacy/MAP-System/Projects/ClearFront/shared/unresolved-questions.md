<!-- hpom: file: shared/unresolved-questions.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-16 -->
<!-- hpom: verified_against: bootstrap (hcom #311) -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Unresolved Questions — ClearFront

- Whether the game should keep the current artifact-bundler-style
  self-extracting HTML for distribution (e.g. re-bundle after editing
  modules) or move to a plain multi-file static site is undecided.
  Affects nothing until someone wants to ship a single-file build; the
  working format is the plain multi-file `app/` (DEC-CF-002).
- The design docs list open playtest questions of their own (see
  `clearfront_rules.md` section 16: max mana cap, Champion base/replay
  cost, Equipment expiry, first-player disadvantage, Guard blocking
  rule) — these are game-design questions, not implementation questions,
  and should stay in the design docs / a future playtest task rather
  than being answered here.
- How far to sub-split `engine.js` (state/combat/AI as separate files vs
  one engine file) — DEC-CF-003 flags the engine as the highest-risk
  slice and defers the sub-split decision to its own follow-on task.

## Resolved (kept for traceability)

- Module boundaries: resolved by DEC-CF-002/DEC-CF-003 (2026-07-16),
  validated by TASK-208's approved skeleton.
- Pi's lane: resolved — TASK-209 rules-conformance audit, lease held by
  pi-lab-puma, file-only workflow (no hcom required from Pi), accountable
  owner claude-lab-gome.
- Fable helper granularity: resolved in practice — one bounded helper
  per decomposition slice, spawned with a full context brief
  (helper-clearfront-skeleton-01/vida pattern), reassignable to the next
  slice while context is warm at the owner's discretion.
