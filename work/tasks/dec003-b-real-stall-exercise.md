# Task: DEC-003 option B — controlled real-stall exercise

- Status: `READY`
- AGI status: `AGI READY`
- Type: `RESEARCH`
- Owner: dispatched agent (throwaway session)
- Risk: `MEDIUM` (deliberately runs unbabysat; bounded blast radius per mitigation below)
- Goal: capture a real, routable `resume_denied` from
  `recovery-tick --enforce-canonical-run` against a genuinely-live hcom session
  that stalls unattended past its lease, closing DEC-003's strong-evidence path
  for the 7-row harness-enforcement cluster (6.4 / 6.5 / 6.16 / 6.22 / H5 / E4 / L6).
- Parent roadmap: `work/decisions/DEC-003-harness-enforcement-cluster-exit-criterion.md`
  (Status: `ADOPTED`, operator GO 2026-09-04 session 31)
- Related records: `work/notes/2026-09-02-lineage-bootstrap-exercise.md` (synthetic
  precedent, `bind-session` mechanics), `work/notes/2026-09-03-item5-enforced-pass-results.md`
  (option-A enforced-pass recipe, exact `recovery-tick` invocation), `work/notes/2026-09-02-ask1-control-plane-runbook.md`
  §8 (option-B path design)
- Autonomous continuation: `YES`

## Inputs and source of truth

- `runtime/cli.py` — `flow start` / `run bind-session` / `recovery-tick` argument
  lists are authoritative; do not guess flags, read them.
- `work/notes/2026-09-02-lineage-bootstrap-exercise.md` §1 — exact command
  sequence for `flow start` → `run bind-session` (reuse verbatim except: use a
  REAL hcom session id from a REAL spawned agent, not a synthetic one; and pass
  a short `--lease-seconds`).
- `work/notes/2026-09-03-item5-enforced-pass-results.md` — exact
  `recovery-tick --enforce-canonical-run --harness-project-id maps-lean
  --repo-root "$PWD"` invocation and what a routable vs non-routable incident
  looks like in the result.
- Evidence labels: the command outputs you capture are VERIFIED; anything you
  infer about *why* a denial did/didn't fire is ASSUMED unless traced in code.
- Dependencies/preconditions: none outstanding — option-B wiring (`bind-session`
  verb, #258/#261/#263) is merged and exercised already.

## Change boundary

- MAY CHANGE: `work/notes/` (new exercise-results note), `work/regression-cases/`
  (the frozen case, per `playbook/REPAIR_AND_LEARNING.md`'s freeze-case workflow),
  `work/decisions/DEC-003-*.md` (append a "Result" section — do not alter the
  already-recorded authorization), `work/roadmaps/CAPABILITY_CHECKLIST.md` (the
  7 named rows only, and ONLY on a genuine routable `resume_denied` capture —
  a failed/inconclusive attempt does not flip any row).
- MUST NOT CHANGE: any `runtime/` source file, any test file, any other
  checklist row, `AGENTS.md`, any other open PR's branch.
- MAY CHANGE IF NECESSARY: none — if you find yourself needing a runtime code
  change to make the exercise work, STOP and escalate (that's a real gap, not
  an exercise-scope decision).
- HUMAN REAUTHORIZATION REQUIRED: a 3rd attempt after 2 failures (DEC-003's
  explicit fallback is (A)-with-caveat at that point, not another try).

## Decision authority

- Inherited roadmap authority: DEC-003's operator GO covers exactly this
  exercise as scoped in DEC-003's Recommendation section (dedicated throwaway
  tagged session, unbabysat, shortened lease TTL, single bounded window).
- Owner may decide: exact lease-seconds value, task-id/worker-id naming,
  how long to wait past lease expiry before running the tick (a few multiples
  of the lease window is reasonable), IncidentCategory for the frozen case.
- Resolve internally first: any command syntax question — read `runtime/cli.py`
  directly rather than guess.
- Human escalation only if: 2 attempts both fail to produce a routable denial
  (invoke the DEC-003 fallback instead of trying a 3rd time), or you hit a
  genuine runtime bug that needs a code fix.

## Acceptance criteria

- [ ] A real hcom session was spawned, bound via `maps run bind-session` to a
      real run manifest (not a synthetic session id), with a short
      `--lease-seconds` (e.g. 60-180s).
- [ ] That session was left genuinely unattended (no coordinator/watcher
      interaction) until its lease expired.
- [ ] `recovery-tick --enforce-canonical-run` was run after expiry and its
      output is captured verbatim in the exercise-results note.
- [ ] EITHER: the tick produced a routable `resume_denied` (SUCCESS — freeze it
      as a regression case per `playbook/REPAIR_AND_LEARNING.md`, then flip the
      7 checklist rows citing this note + the frozen case id) OR: it did not
      (record why in as much traced detail as possible; do not flip any row;
      hand back to the coordinator for a 2nd attempt or, after 2 failures, the
      DEC-003 fallback).

## Verification and evidence

- Verification: the `recovery-tick` JSON output itself — look for a
  `resume_denied`-shaped result tied to the bound run/session, not a generic
  no-op ("nothing to do") result.
- Evidence to preserve: full command transcript (all steps, verbatim stdout),
  the frozen regression case JSON (if SUCCESS) at
  `work/regression-cases/<case_id>.json`, the exercise-results note at
  `work/notes/2026-09-04-dec003-b-real-stall-exercise-results.md`.
- Review required: `INDEPENDENT_REVIEW` (self-authored; owner is not eligible).

## Conditional execution rules

- Environment / target: `~/Projects/MAPS_Lean` clone pattern — fresh clone to a
  UNIQUE `/tmp/<tag>-$$/` path, never `~/Projects/MAPS_Lean` or
  `.claude/worktrees/`. `export HCOM_DIR="$PWD/.hcom"` per the precedent note.
- Ordered procedure:
  1. Spawn a dedicated throwaway real hcom session (a second, separate agent —
     NOT this task's own owner session) tagged distinctly (e.g. `dec003-stall`).
     This is the session that will stall. **Nobody messages it, watches it, or
     nudges it once spawned** — the coordinator is explicitly told to exclude
     it from routine `hcom list -v` babysitting for the duration.
  2. `maps init` (fresh `.maps/` under this task's own clone) → `create` →
     `shape` → `promote` → `flow start --worker-id <id> --lease-seconds <short>`
     to get a real `run_manifest` (reuse the exact contract shape from the
     precedent note, `output_paths` scoped to `work/notes`).
  3. `maps run bind-session <run_id> --worker-id <id> --session-id
     <the throwaway session's REAL hcom session id> --adapter hcom
     --evidence-ref hcom:attach:<session_id>`.
  4. Wait past lease expiry (several multiples of `--lease-seconds`) doing
     nothing to that session.
  5. `recovery-tick --enforce-canonical-run --harness-project-id maps-lean
     --repo-root "$PWD"`. Capture output verbatim.
  6. Kill the throwaway stalled session once the tick has run (it has served
     its purpose).
  7. Write the results note; on SUCCESS, freeze the case and flip the checklist
     rows in the same PR.
- Failure branches: IF the tick returns a non-routable/no-op result THEN this
  is attempt N — do not flip anything; hand back with full detail for a 2nd
  attempt (or invoke the DEC-003 fallback if this was already attempt 2).
- Rollback / recovery: none needed — this task creates no persistent runtime
  state outside its own throwaway `.maps/` (git-ignored) and its own hcom
  session (killed at the end).
- Security / privacy controls: N/A.
- External side effects: spawns one real (billed) agent session that sits idle
  for the wait window — bounded by design (short lease, single window).
- Effort limit: 2 attempts total per DEC-003's explicit fallback; do not exceed.
- Approved reference: DEC-003 Recommendation section + the two precedent notes
  cited above.
- Operational independence: `REQUIRED`.
- Reproduction package: the exercise-results note itself, plus the frozen
  case (if produced), constitute the reproduction package for a future
  trajectory pass to re-verify without re-running the exercise.

## Question-resolution ladder

authoritative evidence (`runtime/cli.py`, the two precedent notes) → safe
inspection → focused research if a command's exact behavior is unclear →
independent challenge (the reviewer) on the SUCCESS/FAILURE call → coordinator
decides retry vs fallback inside DEC-003's 2-attempt envelope → human only if
DEC-003's fallback itself needs to be invoked or a genuine runtime bug appears.

## Stop / escalate

Stop and hand back to the coordinator (not the operator directly) if: 2
attempts both fail; a runtime code change looks necessary; or the spawned
throwaway session's lease/lifecycle behaves in a way this note's assumptions
don't cover. The coordinator escalates to the operator only for the DEC-003
fallback decision itself.
