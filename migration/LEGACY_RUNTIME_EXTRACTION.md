# Legacy Runtime Extraction Plan

Status: `IN_PROGRESS`
Source commit: `77723d16f77efc5e1fe03a74adab920dc7534f16`
Source root: `legacy/MAP-System/MAP_System/`
Staging root: `migration/legacy-runtime-source/`

## Goal

Preserve the minimum proven implementation and tests needed to rebuild the MAPS Lean control plane before `legacy/` is removed.

This is not an attempt to keep the old command center. The target remains provider-neutral Lean runtime with SQLite task truth, bounded routing, hcom transport, RnS recovery, AGI readiness gates, and optional local helpers.

## Classification

| Area | Preserved source | Lean target | Action |
| --- | --- | --- | --- |
| SQLite task lifecycle | `db/`, `migration/schema.sql` | `runtime/state/` | **PROMOTED IN TASK-009** |
| Task allocator/transitions | `scripts/map_task.py`, `promote_task.py`, `release_task.py` | `runtime/state/` + CLI | **PARTIALLY PROMOTED: STATE/AGI/REVIEW** |
| Review separation | claims/review authorship + tests | state/review API | **PROMOTED IN TASK-009** |
| Scope/write boundary | `verify_run_scope.py`, graph validator | AGI/task boundary validator | OUTPUT-PATH RESERVATION ACTIVE; FILESYSTEM RUN-SCOPE ENFORCEMENT PENDING |
| Pre-dispatch policy | `pre_dispatch_policy.py` | `runtime/policy/` | SIMPLIFY, KEEP HARD GATES |
| Halt state | `halt_state.py` | `runtime/policy/halt.py` | ADAPT |
| LangGraph routing | `graph/runner.py`, policy/role config | `runtime/routing/` | ADAPT |
| LangGraph checkpoints | `db/checkpointer.py` | separate checkpoint DB | REIMPLEMENT WITH OFFICIAL SAVER |
| Agent reconciliation | `reconcile_agents.py` | runtime identity adapter | REDESIGN AROUND ONE DURABLE ID MODEL |
| RnS / limits | `limit_watcher.py` | `runtime/recovery/` | PRESERVE DETECTION/BACKOFF; REMOVE WEZTERM |
| Liveness | `liveness_reaper.py` | `runtime/recovery/` | ADAPT |
| Durable execution | `durable_execution.py` | `runtime/recovery/` | ADAPT |
| Resilience / DLQ | resilience + dead-letter scripts | `runtime/recovery/` | PORT IF STILL NEEDED |
| Ollama helper | `local_runner.py` + health | `runtime/helpers/ollama.py` | ADAPT TO HPOM PROFILES |
| Aider helper | `aider_wrapper.py` | `runtime/helpers/aider.py` | ADAPT TO MARKDOWN TASK CONTRACT |
| Events/redaction | `event_trace.py`, `redaction.py` | shared runtime utilities | PORT |
| Installer | old installer + fresh-install guide | Lean installer | REWRITE; KEEP SAFETY PATTERN |

## P0 invariants to preserve

These are more important than file-for-file compatibility:

1. **One claim winner.** Concurrent attempts cannot both acquire the same READY task.
2. **Lease recovery.** Stale claims can recover without stealing live work.
3. **No self-review.** Submission authorship is distinct from durable ownership and cannot be rewritten by reassignment.
4. **Explicit promotion gate.** A task cannot become executable just because an agent wants to start it; Lean adds AGI readiness to this gate.
5. **Write boundary.** A worker cannot silently expand output paths/scope.
6. **Policy before dispatch.** Destructive, authority-changing, broad, or unsupported work cannot be routed merely because a model can technically perform it.
7. **Halt is durable and inspectable.** Blocking state must survive agent/session failure and have explicit set/clear authority.
8. **Routing is not authority.** LangGraph may recommend a route; guarded MAPS operations change task truth.
9. **Communication is not task truth.** hcom owns transport/session state; MAPS owns project/task authority.
10. **Recovery does not invent work.** RnS may resume/nudge known sessions and reconcile stale state but must not silently claim/reassign/create tasks.
11. **Local models are bounded helpers.** Ollama/Aider work must have narrow input/output scope and no final approval authority.
12. **Installer is reversible.** Dry-run first, user-local writes, backup before overwrite, credentials left to the user.

## P0 tests preserved

The staging snapshot includes focused tests for:

- no-self-review;
- atomic/independent review claims;
- pre-dispatch policy;
- task promotion;
- release gating;
- runner policy gates;
- task schema validation;
- shared-output graph conflicts;
- task ID allocation and rework;
- halt state;
- limit watcher and liveness reaper;
- durable execution/resilience;
- local Ollama runner;
- Aider wrapper;
- multi-project isolation.

Historical task records, UI screenshots, release checklists, command-center prototypes, and fixed-roster artifacts are deliberately not extracted.

## Active state promotion — TASK-009

The first active runtime slice now lives in `runtime/state/` and `runtime/cli.py`.
It ports the state-layer invariants instead of importing migration code:

- SQLite foreign keys, WAL, and busy timeout;
- unique task allocation under concurrency;
- structural AGI validation and READY mutation in one write transaction;
- active output-path reservation conflicts;
- atomic task claims and lease recovery;
- durable owner vs current claimant separation;
- durable submission evidence/authorship;
- no-self-review for independent review;
- `CHANGES_REQUESTED` rework without ownership mutation.

Owner-side active tests currently cover these behaviors with 15 passing cases.
This is an active equivalent for the **state subset** of P0 tests, not a claim
that routing, policy, recovery, helper, or install P0 coverage is complete.

## Known legacy problems not to reproduce

The legacy migration audit already identified several real drift problems:

- SQLite agent rows, `agents/status.json`, and hcom session state were not one synchronized identity source.
- SQLite, per-task JSON, and a monolithic `task_graph.json` created multiple mutable task representations.
- UI was a separate consumer and could drift from runtime state.
- all projects shared infrastructure while some policies lacked explicit project dimensions.

Lean should solve these at the boundary rather than preserving the duplication.

## Removal gate for `legacy/`

`legacy/` can be removed from the active repository once all of the following are true:

- [x] critical runtime source snapshot exists outside `legacy/`;
- [x] critical tests exist outside `legacy/`;
- [x] migration/install references exist outside `legacy/`;
- [x] active SQLite/state implementation exists under `runtime/`;
- [x] AGI readiness is enforced by the READY transition;
- [ ] LangGraph router uses the active task store and separate checkpoint DB;
- [ ] hcom adapter exists and has no authority side effects;
- [ ] RnS works without mandatory WezTerm;
- [ ] local helper wrappers are adapted to Lean task records/HPOM;
- [ ] preserved P0 tests have active equivalents and pass;
- [ ] fresh-clone installer/smoke path works without reading `legacy/`.

Removing `legacy/` before the unchecked items are complete is allowed only if the staging snapshot remains until those migrations finish.
