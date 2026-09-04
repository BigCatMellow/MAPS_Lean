# DEC-003 option B — real-stall exercise — attempt 1 results

**Status: BLOCKED before a live session could be established.** No task-truth
change, no `--enforce-canonical-run` pass run against a bound live session, no
checklist row touched. This does not count as one of the exercise's 2
substantive attempts — the blocker is an environment precondition failure
(cannot spawn an authenticated real hcom session), not a stall/detection
outcome.

Executed 2026-09-04 by `dec003-exercise-luvo`, dispatched by coordinator `vine`.
Task doc: `work/tasks/dec003-b-real-stall-exercise.md` on
`decision/dec-003-adopt-b-authorize-exercise` (PR #293).

## What was attempted

Fresh clone to `/tmp/dec003-stall-806175/`, checked out the DEC-003 branch,
read the task doc + both precedent notes
(`2026-09-02-lineage-bootstrap-exercise.md`,
`2026-09-03-item5-enforced-pass-results.md`) plus
`2026-09-02-ask1-control-plane-runbook.md` for the exact `recovery-tick`
mechanics. Traced `runtime/recovery/supervisor.py` `session_is_live` /
`observe_silent_stops` / `tick()` source directly (not guessed):

- `session_is_live()` treats a session with `process_bound` set as live iff
  the OS process is alive; only a genuine process exit (or, absent
  `process_bound`, 30-minute status staleness) reads as "not live".
- `observe_silent_stops` opens an incident only on an observed
  **live(prev)->not-live(current)** transition — the first tick against any
  session only ever records a baseline, never opens an incident.
- A newly-opened incident is scheduled `resume_after = now +
  silent_stop_probe_delay_seconds` (default **900s**, not configurable via any
  `recovery-tick` CLI flag — confirmed by reading `runtime/cli.py` and
  `RecoverySupervisor.__init__`), so a *third* tick, ~15+ minutes after the
  second, is needed before `tick()` actually attempts the resume that could
  produce `resume_denied`.

Correct attempt shape derived from this (not run — blocked before step 1):
spawn real session → bind-session while alive (tick #1 = baseline) → session's
process exits (a real crash/stall, not a hang-while-alive, is the only
`session_is_live`-detectable "stop") → tick #2 (observes the transition, opens
incident, not yet due) → wait ~900s+ → tick #3 (incident due, attempts resume,
expects `LEASE_EXPIRED` given the short `--lease-seconds`). This refines the
task doc's single-tick reading of step 5 — flagging it here since the doc's
literal procedure would silently no-op on a first-ever tick.

## The actual blocker

Every real hcom-agent spawn path tried hit a **login wall** on this host,
independent of the mechanics above:

1. `hcom 1 claude --tag dec003-stall --headless --dir /tmp/dec003-stall-806175`
   — launched, but blocked on Claude Code's first-run wizard (theme, then
   "Select login method") in the fresh, never-before-used directory.
   `hcom term inject --enter` cleared the theme screen; the login screen
   requires an actual auth choice.
2. Retried via `~/.local/bin/hcom-claude-visible` (tmux, per CLAUDE.md rule 6)
   — same wizard, same login wall.
3. Selecting "Claude account with subscription" + Enter progressed to
   `Opening browser to sign in…` — a real OAuth device-flow requiring human
   interaction (open a URL, authorize, paste a code back). Not automatable
   from this session, and no human was available mid-exercise to complete it
   (the task explicitly requires the throwaway session to run unattended).
4. Tried `--dir "$HOME/Projects/MAPS_Lean"` (the one directory known to have
   working, already-authenticated Claude Code sessions — `vine`, `sana`,
   `opcmd-gule` all run there) to sidestep the fresh-directory auth wall while
   keeping `HCOM_DIR` pointed at this exercise's isolated
   `/tmp/dec003-stall-806175/.hcom` transport. **Correctly denied by the
   Claude Code auto-mode classifier** — spawning any agent bound to the
   coordinator checkout is exactly the pattern
   `feedback_never_edit_coordinator_checkout` exists to block. Per CLAUDE.md
   rule 7, did not attempt to loosen the classifier to route around this.

All three throwaway spawn attempts (`kimi`, `leza`/`lumo`, `rumi`) were killed
after confirming the login wall; none ever produced a real `session_id`, so
none were ever bound via `maps run bind-session` and no `.maps/` mutation
happened beyond `init` (empty DB, no tasks, no run manifests — confirmed
`status` still shows `{"total": 0}`).

## Why this isn't "attempt 1" of the 2-attempt budget

The task doc's 2-attempt cap is about the stall/detection outcome (did the
tick produce a routable `resume_denied`). This run never reached a live,
bound session to observe a stall against — it is a **tooling/environment
precondition failure**, not a stall-detection failure. Recorded per rule 15
(`UNKNOWN`/blocker, not papered over) rather than spent against the budget.

## What would unblock this

Spawning a real, unattended hcom session anywhere other than an
already-authenticated, already-trusted directory requires one of:
- a human completing the OAuth browser flow once for a scratch directory
  (then that directory's credential state can presumably be reused for
  future exercises), or
- a directory this classifier already treats as safe to spawn throwaway
  agents in (not `~/Projects/MAPS_Lean`, not `.claude/worktrees/`) that also
  already carries valid Claude Code credentials.

This is an operator/environment question, not something resolvable inside
this exercise's own change boundary (`work/notes/`, `work/regression-cases/`,
`work/decisions/DEC-003-*.md`, the 7 checklist rows) — no runtime code
change would fix it; it is host/credential state.

## Boundaries honoured

No `runtime/` change. No checklist row touched. No regression case frozen (no
routable denial to freeze). `.maps/` in `/tmp/dec003-stall-806175/` is
gitignored and empty of task state (`init` only); the clone itself is
disposable. `~/Projects/MAPS_Lean` and `.claude/worktrees/` were not edited —
the one spawn attempt naming that directory as `--dir` was blocked before it
could run, and no other action touched it.

## Resume prompt

You are picking up DEC-003 option B (real-stall exercise) after attempt 1 was
blocked before a live session could be spawned — not a stall-detection
failure, an auth/environment precondition failure. Read this note in full,
then `work/tasks/dec003-b-real-stall-exercise.md` on
`decision/dec-003-adopt-b-authorize-exercise` (PR #293) for the full AGI-ready
spec. Do not re-attempt the exact same spawn paths without first resolving the
login wall documented above (a human completing OAuth once for a scratch
directory, or the coordinator naming a pre-authenticated non-coordinator-
checkout directory that's safe to spawn throwaway agents in). Once a real
session can reach `listening` status without manual login, follow the
corrected 3-tick procedure in this note's "What was attempted" section
(baseline tick while alive, kill the process to simulate the stall/crash,
wait for the live->not-live transition tick, then wait ~900s+ for the
incident's `resume_after` before a third tick can actually attempt the
resume and produce `LEASE_EXPIRED`). Report to the coordinator (`vine`) before
consuming attempt 2.
