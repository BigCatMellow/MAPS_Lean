# RnS production trigger loop design

Date: 2026-08-24
Owner: `/root`
Status: design complete; no runtime behavior changed

## Finding

`RecoverySupervisor.tick()` (and `observe_silent_stops()`, and
`RecoverySupervisor(...)` construction itself) have zero production
invocation anywhere in this codebase. Per
`work/insights/2026-08-19-recoverysupervisor-tick-has-zero-production-invocation-anywh-INSIGHT-e0b448a6.md`
(confirmed by direct grep, not inferred): `grep -rln 'RecoverySupervisor('
runtime/` and a search of `runtime/cli.py`/`scripts/*.py` for `.tick(` both
return only `tests/test_recovery_supervisor.py`. Re-verified in this session
against `origin/main` @ `4431b3a` (post-#160): still true. `#160` gave
`tick()` a real `HarnessService.resume()` call path *inside* the method, but
nothing outside tests ever calls `tick()` in the first place, so that path
still can't accumulate real evidence. This design note proposes the missing
call site. Per the insight's own "smallest next test," this is exactly the
deferred decision it flagged for a future trajectory pass.

## Constraint

`work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` §7.1 rejects a large
persistent `mapd` supervisor daemon by default; §7.9 rejects continuous
discovery/process-police agents by default, preferring "bounded audits and
deterministic checks." Any trigger mechanism proposed here must be a bounded,
one-shot invocation tied to a concrete already-occurring event -- not a new
scheduler, cron, or long-running process.

## Survey of existing lifecycle events / entrypoints

Before proposing anything new, the following were checked for a reusable
trigger surface:

- `runtime/harness/hooks.py::HookRegistry` -- a real Hook system
  (`HookEvent.BEFORE_RESUME`, `SESSION_STOPPING`, etc.), but its hooks only
  run *inside* `HarnessService.resume()`/`stop()` (see
  `runtime/harness/service.py:295,301,328,334`). They gate a resume/stop
  attempt that is already happening; they are not a mechanism for triggering
  a resume attempt in the first place. Using them to fire `tick()` would be
  circular -- `tick()` is what decides to *call* `HarnessService.resume()`.
- `runtime/cli.py` subcommands: `init`, `create`, `shape`, `check`,
  `promote`, `show`, `trace`, `run-record`, `freeze-case`, `context`,
  `status`, `claim`, `heartbeat`, `submit`, `review-claim`, `review-record`,
  `outcome-record`, `outcomes`, `events`, `reviews`, `flow ...`. No
  `recovery`/`rns`/`supervisor`-shaped subcommand exists today (grep is
  empty).
- `status` (`runtime/status.py::build_status`) is explicitly documented and
  implemented as a **read-only** DB summary (`_connect()` + `SELECT`s only,
  no hcom calls). Attaching a mutating `tick()` call here would silently
  break that contract -- ruled out.
- `claim` (`runtime/cli.py` -> `store.claim_task(...)`, backed by
  `runtime/state/execution.py::claim_task`) is the CLI moment a worker begins
  new active work. It already mutates task truth and already runs at a real,
  bounded, per-event cadence set entirely by existing worker/orchestration
  behavior -- not by anything this design adds.
- `runtime/communication/` (hcom adapter) has no hook/event system of its
  own; it is a narrow CLI-shelling adapter (see its README) with no lifecycle
  callback points to attach to.
- `scripts/coordination_housekeeping.py` is the closest existing precedent
  for the *shape* of trigger this design wants: a bounded, standalone script
  invoked by a human or CI, explicitly because (per its own docstring) "no
  session is live" to do the mechanical work interactively. It performs
  reversible, mechanically-safe actions and exits. It is not itself a
  reusable call site for `tick()` (it only touches GitHub PR state via `gh`),
  but it establishes that this kind of bounded, externally-invoked script is
  an accepted pattern in this codebase, separate from a daemon.

No existing mechanism does "fire tick() periodically" today. The two
reusable candidates are (a) a brand-new bounded CLI subcommand, invoked
by a human/CI, and (b) piggybacking on the existing `claim` mutation.

## Decision: `claim` as the trigger, exposed as its own bounded CLI step

Recommend a **new `runtime/cli.py recovery-tick` subcommand**, whose sole job
is to construct the RnS components and call
`RecoverySupervisor.observe_silent_stops()` then `.tick()` once and exit --
plus wiring `main()`'s existing `claim` branch to invoke that same one-shot
path immediately after a successful `store.claim_task(...)` call.

Justification:

- **Bounded, not a daemon.** The subcommand is a single process invocation
  that runs one `observe_silent_stops()` + one `tick()` pass over already-due
  incidents and returns. It holds no long-lived state, opens no listener,
  and does not reschedule itself. Nothing about it resembles §7.1's
  "large persistent supervisor" or §7.9's "continuous discovery agent" --
  it is exactly the "bounded audits and deterministic checks" §7.9
  prescribes as the preferred alternative.
- **Fires often enough to matter, without a new schedule.** `claim` already
  fires every time any worker (existing today, driven by existing
  orchestration, not a new loop this design adds) picks up new READY/
  CHANGES_REQUESTED work. That is precisely the moment new active-task
  bindings are established -- the same moment RnS's own
  `observe_silent_stops()` needs current `worker_id -> session_name`
  bindings to detect a *different* worker's silent stop, and the natural
  moment to reconcile stale incidents before more coordination proceeds on
  top of them. Piggybacking here means the trigger cadence tracks real
  system activity for free: more concurrent work in flight means more
  `claim` calls means more recovery reconciliation passes, with zero
  incremental infrastructure.
- **Independently invocable.** Because it is also a standalone
  `recovery-tick` subcommand (not *only* a `claim` side effect), a human,
  CI job, or the `coordination_housekeeping.py`-style "nobody is currently
  live" script can run it directly, e.g. after a long idle period where no
  worker has claimed anything to naturally trigger it. This keeps the
  mechanism usable even in the gap `claim`-piggybacking alone would miss
  (all workers silent, nobody claiming anything).
- **No new Hook type, no new event.** This reuses an existing, already-firing
  CLI mutation (`claim`) and adds one new, ordinary (non-Hook,
  non-enforcement) CLI subcommand of the same kind `runtime/cli.py` already
  has 20 of. It does not touch `runtime/harness/hooks.py` at all.

## Call-site boundary

What `RecoverySupervisor.tick()` needs constructed, and where:

- `task_reader`: the existing `TaskStore` instance. `runtime/cli.py::main()`
  already constructs `store = TaskStore(args.db)` at the top of `main()` --
  reuse that same object directly. (Confirmed duck-type compatible:
  `tests/test_recovery_supervisor.py` already constructs
  `RecoverySupervisor(task_reader=self.task_store, ...)` against a real
  `TaskStore` in its harness-routed test class.)
- `hcom`: a `runtime.communication.HcomAdapter` instance, constructed the
  same way any other production hcom call site would (project-local
  `HCOM_DIR`, default `executable="hcom"`). No existing production
  construction site exists yet for this either (same insight-file gap) --
  this call site would be the first.
- `recovery_store`: `runtime.recovery.store.RecoveryStore()` (accepts its own
  defaults; no external wiring beyond the recovery-state file it manages).
- `environment_reader` (optional/advisory-only per `supervisor.py`'s own
  contract): omit for the first implementation unless a concrete production
  `list_run_environment_evidence(run_id)` source is already wired elsewhere
  by the time this lands; never fabricate one just to fill the parameter.
- `harness_service` (optional; enables the `HarnessService.resume()` path
  landed in #160): construct only if a production `HarnessService` +
  `HcomHarnessAdapter` wiring already exists at the time of implementation.
  Per the insight file, this also has zero production construction today --
  if that gap is still open when this lands, pass `harness_service=None` and
  let `tick()` use its existing, unchanged direct-`hcom.resume()` fallback
  path. Do not build harness_service wiring as a side effect of this task;
  that is the separate, already-landed #160 gap and any further harness
  wiring is out of scope here.
- Construction site: a new small helper (e.g.
  `runtime/recovery/production.py::run_recovery_tick(store, ...)`, exact name
  left to the implementation task) called from two places in
  `runtime/cli.py`: (1) the new `recovery-tick` subcommand branch, and (2)
  the existing `if args.command == 'claim':` branch, immediately after the
  existing `store.claim_task(...)` result is obtained. Reuse one function for
  both call sites rather than duplicating construction logic.

## Non-goals for the implementation follow-up

- No change to `tick()`'s internal decision logic, backoff schedule, or
  evidence shape (`runtime/recovery/supervisor.py`'s existing behavior from
  #160 is untouched).
- No new `HookEvent`, no new `HookRegistry` usage, no enforcement role.
- No daemon, no cron, no scheduled/background process of any kind.
- No change to `claim`'s existing return value, exit code, or output schema
  on success -- `recovery-tick`'s outcome must not change what `claim`
  reports to its caller (surfaced as separate, additive output at most; see
  open question below).
- No new production `HarnessService`/`HcomHarnessAdapter` wiring as part of
  this task if it does not already exist by then -- `harness_service=None`
  is an acceptable, already-supported input.
- No mandatory blocking: `claim` must still succeed even if the
  `recovery-tick` pass fails or hcom is unreachable (see open question
  below on failure isolation).
- Does not mark any roadmap/checklist row `DONE`.

## Behavior questions the implementation task must answer

Do not guess these inside a broad implementation:

- Should a `recovery-tick` failure (hcom unreachable, recovery-store
  corruption, etc.) ever fail the `claim` call itself, or must `claim`'s
  existing success/failure contract be fully preserved regardless of
  recovery-tick outcome? (Recommendation to validate, not assume: `claim`'s
  own result must never regress because of a piggybacked recovery pass --
  isolate failures and surface them separately.)
- Should `observe_silent_stops()` also run at this call site, or does this
  task scope to `tick()` alone and leave `observe_silent_stops()`'s own
  zero-invocation gap for a follow-up? (This note assumes both run together
  since `tick()` has nothing to process without `observe_silent_stops()`
  ever having opened incidents in production -- but the implementation task
  must state this explicitly rather than silently split or silently
  combine them.)
- What bindings (`worker_id -> session_name`) does `observe_silent_stops()`
  receive at the `claim`/`recovery-tick` call site in production? `tick()`
  itself needs none, but `observe_silent_stops()` does, and today nothing
  constructs that mapping outside tests. This may itself need its own
  narrower design pass before implementation, not an on-the-spot guess.
- Should `recovery-tick` output be silent-by-default (matching `claim`'s
  existing terse machine-readable contract) or always emit its own action
  list? Should output differ between the standalone subcommand and the
  `claim`-piggybacked path?
- Should the standalone `recovery-tick` subcommand require the same
  `--db` argument plumbing as other subcommands, and should it accept an
  explicit `--hcom-dir`/`--hcom-executable` override, or default exactly the
  way `HcomAdapter`'s own constructor defaults do?
- If `harness_service` construction is still unavailable at implementation
  time (per the insight file's parallel gap), should the task explicitly
  re-confirm that gap via grep before proceeding (as this note did), rather
  than assuming #160's landing already closed it?

## Bounded follow-up implementation

Recommended next task: `RnS production trigger loop call site`.

Allowed implementation scope:

- Add `runtime/cli.py recovery-tick` subcommand.
- Wire the existing `claim` branch to also invoke the same one-shot
  construction-and-tick helper, with failure isolation per the open question
  above.
- Add the small construction helper (task_reader/hcom/recovery_store
  wiring), reusing existing classes as-is.
- Add tests for: `recovery-tick` subcommand runs one bounded pass and exits;
  `claim` still succeeds when recovery-tick fails; `claim`'s existing
  success-path output is unchanged when recovery-tick has nothing to do;
  no `HookEvent`/daemon/schedule code is introduced (source-level grep
  guard, mirroring #160's own `test_no_validation_tier_commands_or_task_mutation_in_source`-style guard).

Must not do in that follow-up:

- Modify `tick()`'s internals.
- Add a scheduler, cron entry, or background thread/process.
- Build new `HarnessService`/`HcomHarnessAdapter` production wiring if it
  does not already exist.
- Add validation-tier execution (separate, already-tracked H4/E4/6.5
  fast-follow per `work/notes/2026-08-21-rns-harness-validation-callsite-design.md`).
- Mark any roadmap/checklist row `DONE`.

## Roadmap impact

This design does not close the insight file's finding. It identifies the
prerequisite trigger call site (`claim` + a standalone `recovery-tick`
subcommand) and leaves implementation, including the open behavior
questions above, to a separate task.
