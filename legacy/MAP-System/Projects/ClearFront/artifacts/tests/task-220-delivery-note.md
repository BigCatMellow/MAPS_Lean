# ClearFront Delivery Note — TASK-220

First real use of `templates/delivery-note-template.md` (TASK-219): one
combined evidence document replacing the legacy parity-report +
owner-verification + release-checklist trio. The independent reviewer's
record remains separate per the no-self-review boundary.

## Change summary

- Risk lane: MEDIUM (new test infrastructure; becomes a primary
  correctness oracle for future rules work; zero app-code changes)
- Snapshot or commit: working tree (repo snapshot decision pending with
  operator); all five `app/js/*.js` md5s recorded below are unchanged by
  this task
- What changed:
  - NEW `tests/engine/engine-host.mjs` — reusable headless host: loads the
    real, unmodified `data.js`+`state.js`+`combat.js` into a `node:vm`
    context (stubs: `window.CF`, `__resources` proxy, `setTimeout` →
    manual-drain queue, `matchMedia`, fake-element `refs` Proxy, injected
    `structuredClone` [host API absent from fresh vm contexts], seeded
    context-local `Math.random`, and a 3-function render stub whose
    `playClashSequence(report, onDone)` calls `onDone()` synchronously).
    Builds ctx accessors over harness-owned bindings — the harness *is*
    a host in the DEC-CF-004 sense (INS-0026).
  - NEW `tests/engine/rules.cases.mjs` — 34 table-driven cases /
    90 assertions: 7 keywords (Charge, Rush ×2, Guard, Flying, Shield ×2
    [effect + combat damage paths], Drain ×2 [blocked + unblocked],
    Stun), combat math (unblocked, blocked-simultaneous, simultaneous
    lethal, persistent damage, lethal-ends-game), champion lifecycle
    (mana gating, spend/count/enter, +2 return escalation, and ALL FOUR
    passives: orderPrevent, wildHealth, flameDamage, shadowDeath — each
    with its once-per-cycle consumption asserted), direct target
    legality (`getTargetInfo` switch: enemy-target, friendly-target,
    no-target default, and the finishWeak damaged-only filter),
    resources (fatigue incl. the hand-limit-guard nuance, board limit 6,
    relic limit 3, play limits incl. hand-membership, replace
    once-per-turn, 15/15 deck construction), and engine-level undo
    (roundtrip, clearUndo, play-arms/replace-disarms per TASK-213).
  - NEW `tests/engine/run-rules.mjs` — runner; per-case PASS/FAIL with
    precise expected/got diffs; nonzero exit on any failure; prints a
    distinct **deviation summary** (5 cases tagged with TASK-211 audit
    sections: Rush, Drain, Stun, fatigue, deck composition) — the
    flip-list for the pending rules-conformance disposition.
  - EDIT `scripts/test_all.mjs` — one added line: `engine rule matrix`
    as a check between extractor regressions and the browser section
    (needs no Chromium). Disclosed upfront in `output_paths` at task
    creation.
- What deliberately did not change: all `app/` code (md5s below match the
  TASK-215/216/217 released state), `source/`, `baseline/`, game rules or
  balance, the deviation behaviors themselves (asserted as-is pending the
  operator's disposition).
- Files delivered: `tests/engine/engine-host.mjs`,
  `tests/engine/rules.cases.mjs`, `tests/engine/run-rules.mjs`,
  `scripts/test_all.mjs` (1-line edit), this note.

## Verification

| Command | Result | Evidence or notes |
|---|---|---|
| `node tests/engine/run-rules.mjs` | PASS | 34/34 cases, 90/90 assertions, exit 0; deviation summary lists exactly 5 tagged cases |
| deliberately broken expectation (fatigue `-1` → `-99`), rerun, restore | PASS | exit 1 with precise diff (`expected -79, got 19`); after restore exit 0 — fail-loud criterion verified live |
| `node scripts/test_all.mjs` | PASS | 10/10 checks (engine matrix now the 7th), exit 0 |
| `cd source && sha256sum -c SHA256SUMS.txt` | PASS | exit 0, 11/11 |
| `md5sum baseline/index.html` | PASS | `5124cac23a9bd326bb8dfd00a110af92` — unchanged |
| `md5sum app/js/*.js` | PASS | combat `af2b8579…`, data `2d3e7923…`, input `47c98e69…`, render `f6f423dc…`, state `a45b71dc…` — all unchanged by this task |

Overall result: PASS

Known limitations or unresolved risks:

- The matrix asserts CURRENT behavior. The 5 deviation-tagged cases are
  correct-as-shipped, not spec-conformant; they intentionally encode the
  audit's P0 gap until the operator's disposition lands, at which point
  the tags are the implementation/spec-revision worklist.
- Coverage is the audit-requested core (keywords, combat, champion,
  limits, undo) — not yet every card `effect` id in `CARD_LIBRARY`
  (`resolveEffect`'s ~30 effect branches). That is the natural next
  matrix increment and now costs only new table rows, no new
  infrastructure.
- Two probe-stage test bugs (not engine bugs) were found and fixed during
  development: a naive fatigue test that didn't account for the
  hand-limit guard, and a `dealCombatDamage(null)` call violating the
  engine's source-unit contract. Both fixes are encoded as explicit
  assertions/contract notes in the shipped cases.

## Acceptance-criteria mapping

| Acceptance criterion | Evidence | Status |
|---|---|---|
| Full matrix runs headless, exit 0 iff all pass; broken expectation exits nonzero | rows 1–2 above, verified live both directions | MET |
| Coverage: 7 keywords, combat math incl. simultaneous lethal, persistent damage, champion lifecycle/passives, fatigue + nuance, board/relic limits, target legality, play limits, engine-level undo incl. TASK-213 | 34 cases enumerated in change summary. Rework round (per `task220-review-lilo.md`): added `champion-flame-damage-first-card`, `champion-shadow-death-first-friendly-death` (completing all four passive types), and two direct `getTargetInfo` cases (`target-enemy-friendly-and-default-shapes`, `target-filtered-damaged-only`) replacing the earlier proxy-coverage judgment call | MET |
| Deviation tags cite TASK-211 sections; runner prints deviation summary distinct from failures | 5 tagged cases; summary block in runner output | MET |
| `test_all.mjs` gains the matrix as one check; still exits 0 all-green | row 3 above | MET |
| Evidence via TASK-219 delivery-note template (first real use); `source/`/`baseline/` untouched | this document; rows 4–6 | MET |

Owner: claude-lab-gome
Verified at: 2026-07-17T22:30:00Z
