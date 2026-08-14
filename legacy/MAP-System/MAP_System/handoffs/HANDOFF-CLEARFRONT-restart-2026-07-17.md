<!-- hpom: file: handoffs/HANDOFF-CLEARFRONT-restart-2026-07-17.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: codex-lab-lilo -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: Projects/ClearFront/shared/current-state.md; TASK-207/208/211/212/213 RELEASED; TASK-214 IN_PROGRESS; hcom #1246 -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: HANDOFF-CLEARFRONT-intake-codex-lab-lilo-to-claude-lab-gome.md -->
<!-- hpom: superseded_by: NONE -->

# ClearFront Restart Handoff — 2026-07-17

Use this note to resume the ClearFront work after restarting the Command Center
Lab. Durable task/database state remains authoritative if anything below has
advanced since `last_verified`.

## Fast restart

From `/home/mellow/Projects/MultiAgentProject/Source`:

```bash
sed -n '1,260p' MAP_System/handoffs/HANDOFF-CLEARFRONT-restart-2026-07-17.md
sed -n '1,260p' Projects/ClearFront/shared/current-state.md
cat MAP_System/agents/status.json
MAP_System/.venv/bin/python MAP_System/graph/runner.py
hcom list --json --name <your-hcom-name>
```

If the restarted agent is listed as `standby/awaiting_work`, run:

```bash
python3 MAP_System/scripts/declare_standby.py <agent-name> --back
```

Then inspect the live task and recent coordination:

```bash
cat MAP_System/tasks/TASK-214.json
hcom transcript claude-lab-gome --last 30 --name <your-hcom-name>
hcom transcript helper-clearfront-skeleton-01-vida --last 30 --name <your-hcom-name>
```

Send bigboss exactly one startup status message as required by the lab startup
protocol. Routine ClearFront progress belongs in `--intent inform`; reserve
`--intent request` for decisions, approvals, blockers, conflicts, risks, or
questions.

## Project ownership and agents

- Project lead/owner: `claude-lab-gome`.
- Independent review lane: `codex-lab-lilo`.
- Visible Fable implementation helper: `helper-clearfront-skeleton-01-vida`.
- Pi is not a reliable ClearFront delegate in this session: 15+ turns failed
  to complete its bounded audit, and the operator confirmed Pi unavailable.
  Route that work to a core agent or visible Fable helper instead.
- Do not run helpers headlessly. Any newly spawned helper must use
  `--terminal wezterm-tab` and have a bounded purpose plus a durable report.

## Directory truth

| Path | Purpose | Rule |
|---|---|---|
| `Projects/ClearFront/source/` | Preserved original bundle, rules, principles, assets | Never edit; verify with `SHA256SUMS.txt` |
| `Projects/ClearFront/baseline/` | Reproducible extraction/parity reference | Never hand-edit |
| `Projects/ClearFront/app/` | Living editable game | Edit only through claimed MAP tasks |
| `Projects/ClearFront/artifacts/` | Durable plans, tests, research, reviews | Register task-owned outputs |

The app must continue opening directly through `file://`: no server, build
step, bundler, or ES modules. Never mix structural refactoring with rules or
balance changes.

## Released work

| Task | Result |
|---|---|
| TASK-207 | Reproducible bundle extraction; path traversal, stale output, checksum, completeness, and failed-rerun atomicity issues fixed; 5 regression tests. |
| TASK-208 | Multi-file skeleton: CSS, assets, and static data extracted; visual/browser parity proven. |
| TASK-211 | Rules-to-implementation audit released; audit claims independently re-derived with zero inaccuracies. |
| TASK-213 | Fixed the replacement undo hidden-information exploit by clearing all snapshots before the hidden draw; browser regression passed. |
| TASK-212 | Extracted 26 lifecycle/state functions to `app/js/state.js` through `CF.installStateModule(ctx)` with accessor-backed shared bindings; seeded parity and cross-file undo verified. |

TASK-209 is retired/superseded and must not be claimed. TASK-210 is an
unrelated READY MAP infrastructure repair for the limit-watcher's invalid
hyphenated hcom sender; it is not ClearFront product work.

## Live work: TASK-214

At handoff time, `TASK-214` is `IN_PROGRESS`, owned by
`claude-lab-gome`, dependent on released TASK-212.

Vida reported implementation complete in hcom #1246:

- 38 explicitly listed card-play/combat/end-turn/AI functions moved into
  `app/js/combat.js` through `CF.installCombatModule(ctx)`.
- The task text reportedly miscounts 37, but the explicit 38-name list is the
  authoritative scope (same class of authoring count error as TASK-212).
- Mechanical prefix stripping reportedly reproduces the original 903-line
  block byte-for-byte.
- Two deterministic seeds (42 and 7) reportedly match pre-TASK-214 step logs
  exactly and exercise real blocking, combat in both directions, AI turns,
  and end-turn flow with zero console errors/exceptions.
- The existing undo harness reportedly still passes 10/10 across the now
  three-file path, preserving TASK-213 semantics.
- `renderCombatReport` was correctly added as a stable `ctx` binding after
  vida found `resolveCombat` calls the not-yet-extracted render function;
  Claude approved and recorded this in DEC-CF-005.

### Immediate TASK-214 actions

1. Claude must independently inspect vida's implementation and evidence.
2. Before submission, register every durable output. The current task mirror
   only lists:
   - `Projects/ClearFront/app/index.html`
   - `Projects/ClearFront/app/js/combat.js`
   - `Projects/ClearFront/artifacts/tests/task-214-combat-parity.md`
3. Vida explicitly flagged that `Projects/ClearFront/app/js/state.js` was
   necessarily edited (four obsolete `ctx` keys removed and six calls changed
   to late-bound `CF.*`) but is not yet registered. Add it.
4. Register the TASK-214 harness, four replay logs, screenshots, and any owner
   verification note individually, following the TASK-212 correction pattern.
5. Export mirrors and require graph/schema/mirror validators to pass.
6. Submit TASK-214 to `codex-lab-lilo` for independent review.

### Required independent review focus

- Exact 38-function inventory; no render/input functions accidentally moved.
- Mechanical/verbatim proof against the pre-TASK-214 snapshot.
- Correct accessor use for reassigned mutable bindings; do not destructure
  mutable accessor values.
- Validate the `state.js` edits and all late-bound `CF.*` calls.
- Fresh seeded browser runs covering card play, blocks, both combat
  directions, AI, end turn, game-over-sensitive paths where practical, and
  zero console errors/exceptions.
- Re-run the unmodified TASK-212 undo harness to protect TASK-213.
- Byte-identical champion-select screenshot and preserved source/baseline
  hashes.
- Confirm every durable evidence artifact is registered before approval.

## Work after TASK-214

Continue decomposition in separate parity-gated tasks:

1. Extract `js/render.js` from the remaining inline render/clash/UI rendering
   cluster.
2. Extract `js/input.js` for gesture/event wiring and final bootstrap.
3. Only after decomposition is stable, create separate game-improvement tasks
   gated by `clearfront_design_principles.md` section 21.

Rules-audit follow-ups, in priority order:

1. The undo exploit is already fixed by TASK-213.
2. Decide whether Equipment, Mind, Forge, and Neutral are committed scope or
   explicitly future rules.
3. Resolve Rush's contract (direct enemy-unit attack versus current normal
   attack with zero hero damage on the entry turn).
4. Implement a complete Stun lifecycle before adding Stun cards.
5. Document or remove fatigue damage.
6. Generalize Drain if it should apply outside combat, or narrow its written
   definition.

Do not combine any of those behavior/rules decisions with module extraction.

## Durable references

- Current state: `Projects/ClearFront/shared/current-state.md`
- Decisions: `Projects/ClearFront/shared/decisions.md` (DEC-CF-001 onward)
- Requirements: `Projects/ClearFront/shared/requirements.md`
- Risks: `Projects/ClearFront/risks/RISK_REGISTER.md`
- Module plan: `Projects/ClearFront/artifacts/planning/clearfront-module-map-2026-07-16.md`
- Rules audit: `Projects/ClearFront/artifacts/research/rules-conformance-audit.md`
- TASK-212 review: `Projects/ClearFront/artifacts/reviews/task212-review-lilo.md`
- TASK-213 regression: `Projects/ClearFront/artifacts/tests/task213-replacement-undo-regression.md`

## Validation commands

```bash
(cd Projects/ClearFront/source && sha256sum -c SHA256SUMS.txt)
MAP_System/.venv/bin/python MAP_System/scripts/validate_task_graph.py
MAP_System/.venv/bin/python MAP_System/scripts/validate_task_schema.py
MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py
python3 MAP_System/scripts/map_emergence.py validate
```

Expected preserved baseline md5 at this handoff:
`5124cac23a9bd326bb8dfd00a110af92` for
`Projects/ClearFront/baseline/index.html`.
