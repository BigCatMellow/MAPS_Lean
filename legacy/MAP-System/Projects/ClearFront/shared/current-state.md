<!-- hpom: file: shared/current-state.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: claude-lab-gome -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: TASK-207-217 RELEASED (TASK-209 RETIRED), independent process audit 2026-07-17 -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Current State — ClearFront

Last updated: 2026-07-17 (claude-lab-gome)

**Independent process audit landed** (operator-commissioned, Codex agent
`nipa`): `artifacts/reviews/clearfront-independent-delivery-audit-2026-07-17.md`.
Verdict: decomposition/refactor quality and independent reviews are
credible (caught real defects: TASK-207 path traversal, TASK-213 undo
exploit, TASK-214 missing binding, TASK-215's 4 live-only bugs), but the
same full review/release ceremony was applied to every slice regardless
of risk, generating 89 MAP events and 60 artifacts for 8 released tasks.
Adopted the audit's risk-tiered review model going forward — see
DEC-CF-008 in `shared/decisions.md`. Two findings routed to bigboss
directly (not decided here): the P0 rules-conformance disposition
(implement-to-spec vs. revise-spec) and the P1 no-git-snapshot finding
(touches 57 files across other agents' unrelated work, not a unilateral
call). RISK-CF-0001/0002 closed as MITIGATED (parity gate proven across
7 tasks; extractor's asset enumeration confirmed complete).

**Process-improvement batch (TASK-218/219) RELEASED**, implementing
DEC-CF-008's two halves: `MAP_System/notes/review-guide.md` gained a
Risk-Tiered Review section (reusable MAP-wide); ClearFront gained
`scripts/test_all.mjs` (one-command test runner, self-managed Chromium
lifecycle, live-verified including its forced-failure cleanup path) and
`templates/delivery-note-template.md` (replaces the parity-report +
owner-verification + release-checklist trio for future low/medium-risk
work, not retrofitted onto TASK-207–217). Both reviewed at the tier they
themselves define — light read for TASK-218, one live-verification pass
for TASK-219 — closing the loop on the audit's own central finding.
Lilo separately reviewed the operator-provided
`MAP_AGENT_COORDINATION_DESIGN_PHILOSOPHY.md`/
`optimal-agent-communication-guide.md`; durable review at
`MAP_System/artifacts/reviews/agent-coordination-documents-review-2026-07-17.md`
(adopt state-change-only events, bounded delegation, event-triggered
deliberation now; do not mandate a new MAP/1 DSL without a piloted
safety case first).

Note: pi-lab-puma (local model) is not a reliable delegate for ClearFront
work as of this update — 15+ turns without completing a bounded task,
plus operator confirmation Pi is unavailable. Route Pi-shaped lanes to
codex-lab-lilo or a Fable helper instead.

## Directory truth

| Path | Role | Editable? |
|---|---|---|
| `source/` | Untouched original (bundle, docs, assets, zip) + `SHA256SUMS.txt` | NO — re-copy + re-hash if the original ever changes |
| `baseline/` | Extraction-parity reference, regenerable via `scripts/extract_bundle.py` | NO — regenerate, never hand-edit |
| `app/` | The living, editable game (multi-file) | YES — through MAP tasks |
| `scripts/` | Extractor + its regression tests | YES — through MAP tasks |

## Task lineage

- TASK-207 — bundle → editable baseline. **RELEASED** 2026-07-16.
  Two review rounds (lilo) caught path traversal, stale-output,
  checksum-self-hash, silent-incomplete, failed-rerun atomicity; all
  fixed, 5 regression tests. Captured INS-0024 (parity-gate pattern).
- TASK-208 — multi-file skeleton (`app/`: CSS + 11 data values on
  `window.CF`; engine/render/input still inline). **RELEASED**
  2026-07-17. Implemented by Fable helper vida, reviewed by lilo
  (no findings).
- TASK-209 — rules-conformance audit. **SUPERSEDED, do not claim.**
  Misclassified role=reviewer (trips the self-review claim gate for
  any owner); original delegate pi-lab-puma (local model) could not
  complete it in 15+ turns and is now confirmed unavailable. See
  `events/events.jsonl` BLOCKED entry.
- TASK-211 — replaces TASK-209, same scope, correctly classified
  role=implementer. **RELEASED** 2026-07-17. Implemented by
  codex-lab-lilo, independently reviewed by claude-lab-gome (7 claims
  re-derived from source, zero inaccuracies found). Key findings:
  Equipment/Mind/Forge/Neutral are scope gaps (future-decision
  candidates); Rush and Stun keywords are incomplete/unimplemented; an
  undo hidden-information leak in card replacement is a real exploit
  (captured as **INS-0025**, prioritize before other findings);
  undocumented fatigue damage on empty-deck draw. Full findings + 6
  prioritized follow-ups: `artifacts/research/rules-conformance-audit.md`.
- TASK-210 — unrelated MAP infra repair (`limit_watcher.py` hyphenated
  hcom sender name broke reset-nudge delivery), **READY**, unclaimed,
  open to any core agent — filed from a real incident during this
  project's session-reset handling, not itself ClearFront work.
- TASK-213 — closes INS-0025 (undo hidden-info exploit) in `app/`
  only. **RELEASED** 2026-07-17. `handleHandCard`'s replacement branch
  now calls `clearUndo()` (wipes any snapshot, including an older one)
  instead of `saveUndo('card swap')`. Implemented by lilo, independently
  reviewed by gome.
- TASK-212 — first engine-layer decomposition slice (DEC-CF-004):
  26 deck/side/game-state functions moved to `app/js/state.js` behind a
  `CF.installStateModule(ctx)` contract. **RELEASED** 2026-07-17.
  `ctx` uses getter/setter accessors (not a plain reference) because
  several functions *reassign* `state`/`undoRecord`/`uidCounter`/deck
  choices wholesale, not just mutate contents — this is the pattern
  `js/combat.js` (next slice) must reuse. Implemented by Fable helper
  vida, owned by gome, reviewed by lilo (one CHANGES_REQUESTED round:
  9 evidence files not registered in output_paths — metadata only, no
  code/evidence-content change).
- TASK-214 — second, highest-risk engine slice (DEC-CF-005, RISK-CF-0001):
  38 card-play/combat/end-turn/AI functions moved to `app/js/combat.js`.
  **RELEASED** 2026-07-17. Implemented by vida; found and disclosed a
  real DEC-CF-005 gap mid-implementation (`resolveCombat` calls
  `renderCombatReport()`, a not-yet-extracted render function, missing
  from the original ctx list) — approved and recorded as a DEC-CF-005
  amendment before submission. Final `ctx` (10 keys): 5 mutable
  accessors + `$`/`refs` + 3 forwarded render-layer functions (`render`,
  `playClashSequence`, `renderCombatReport`) — `checkGameOver`/
  `removeDeadUnits`/`damageHero`/`aiMainPhase` moved into `combat.js`
  and became `window.CF`-published like everything else. `state.js`
  needed a small disclosed edit (6 call sites → `CF.*`) to match. All 9
  evidence outputs registered *before* submission this time (learned
  from TASK-212). Two-seed deterministic replay + undo regression both
  clean, reviewed by lilo with zero findings beyond a cosmetic
  37-vs-38 prose note (same authoring-miscount class as TASK-212's
  25/26; explicit lists were always authoritative).

- TASK-215 — `js/render.js` (28 functions incl. the clash-animation
  cluster, finally resolving its home). **RELEASED** 2026-07-17,
  implemented directly by claude-lab-gome — Fable helper vida ran out
  of usage credits before starting (operator confirmed no session
  limit, directed doing it directly; helper stopped, its context
  preserved in DEC-CF-004/005/006). Found and fixed 4 real bugs during
  implementation (all disclosed in the parity report, none caught by
  static review — only by driving the live app and reading exception
  stack traces): 3 more missed cross-module functions beyond
  DEC-CF-006's original 12, a missing data.js constant destructure, a
  missed `undoRecord` bare-identifier rewrite, and a recurrence of
  TASK-214's disclosed spread-position regex hazard. `ctx` now at its
  final intended shape (7 keys: 5 mutable accessors + `$`/`refs`).
  Reviewed by lilo (independently re-verified every disclosed fix,
  reran both seeds/screenshots/undo checks; one advisory — the undo
  harness now exits nonzero on failure, applied before release).
- TASK-216 — `js/input.js` (the card-peek hover/touch gesture IIFE),
  per DEC-CF-007. **RELEASED** 2026-07-17. Implemented by codex-lab-lilo
  per direct operator assignment. `installInputModule()` takes zero
  parameters — the only decomposition module with no `ctx`/cross-module
  dependency, correctly reflecting that the feature is pure DOM-event/
  closure logic. Reviewed by gome: ran the actual checked-in harnesses
  directly (8/8 input assertions, 6/6 undo, seeded combat/blocking) —
  one apparent seeded-replay divergence (a transient UI string at an
  intermediate step) investigated and confirmed to be fixed-delay
  snapshot timing jitter, not a regression. **This completes the full
  engine/render/input decomposition** (DEC-CF-002 through DEC-CF-007,
  7 implementation tasks released: 207/208/211/212/213/214/215/216 —
  8 counting the audit).
- TASK-217 — category art card faces (Unit/Spell/Relic bitmaps), per
  operator request. **RELEASED** 2026-07-17. Implemented by lilo: three
  original 512×512 text-free PNGs (generated, then resized/stripped
  6.1 MiB → 1.1 MiB), integrated via a static `<img>` in
  `createCardElement` keyed off `card.type` — no new state. Details
  visibility is CSS-only (`.card-details`/`.card-peek` rules). Reviewed
  by gome: viewed all 3 assets and the actual code diff directly, ran
  all 3 checked-in harnesses myself. One `OPTIONAL` note (non-blocking):
  the details-hiding rule is desktop-width-scoped only; mobile compact
  cards show full text directly rather than requiring touch-hold — a
  reasonable reading of the criteria, not a gap.
- Independent ClearFront process audit — operator-requested, in
  progress. Fresh Codex auditor `nipa` assessing code quality plus
  task/review/coordination overhead; writing a durable report; no
  app-code edits authorized.

## Next planned work (not yet task records)

1. Game-improvement tasks gated on the Design Review Checklist
   (`clearfront_design_principles.md` §21), drawing from the 6
   prioritized follow-ups in `artifacts/research/rules-conformance-audit.md`
   (Equipment/Mind/Forge/Neutral scope, Rush/Stun keyword gaps,
   undocumented fatigue) — decomposition is done, this is the next
   major track alongside TASK-217's art work.

## Standing constraints

- No build step, no server, no ES modules — `app/index.html` must open
  via plain `file://` (DEC-CF-002).
- Refactor tasks and rules/balance changes never share a task
  (`shared/requirements.md`).
- Parity gate for every engine-touching task: byte-identical screenshot
  + CDP interaction run (INS-0024; harness at
  `artifacts/tests/task208-cdp-smoke.mjs`).

## Key artifacts

- Decisions: `shared/decisions.md` (DEC-CF-001..003)
- Module map: `artifacts/planning/clearfront-module-map-2026-07-16.md`
- Parity evidence: `artifacts/tests/task-extraction-parity.md`,
  `artifacts/tests/task-208-skeleton-parity.md`
- Reviews: `artifacts/reviews/task207-*.md`, `task208-review-lilo.md`
- Risks: `risks/RISK_REGISTER.md` (RISK-CF-0001 mitigated by parity
  gate; RISK-CF-0002 mitigated by extractor enumeration + fail-closed)
