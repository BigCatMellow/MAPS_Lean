# Ask #1 — control-plane setup + first `--enforce-canonical-run` pass — runbook

**READ-ONLY INVESTIGATION. No `maps` mutation was run; `.maps/` was not
created; no `--enforce-*` command was run.** All behaviour below is traced from
source at `origin/main` `1b9fe1d` (rule 14). The coordinator executes; this note
removes the guesswork.

Ask #1 (first enforced `--enforce-canonical-run` pass) is **AUTHORIZED** by the
operator (#243). Blocker: `~/Projects/MAPS_Lean/.maps/` does not exist — no
control-plane DB. This note is the step-by-step to establish it and run the
first pass.

> **Headline finding (see §3, §5, §6).** With a freshly created `.maps/` and the
> current (empty) incident set, the first `--enforce-canonical-run` pass is a
> **near no-op**: it *instantiates* the production guard composition (the "first
> production exposure of the composition root" the checklist rows want) but the
> guard's decision logic is **never invoked**, because no run has the durable
> `EXPLICIT` hcom session lineage the RnS supervisor requires before it will
> route a resume through the guarded `HarnessService`, and **no production code
> path writes that first session link.** So the pass produces **zero**
> `resume_denied`. That is safe, but it also means Ask #1 as literally scoped
> ("first pass that converts working resumes into `resume_denied`") is not
> reachable without a code change — flagged to @soda in §8.

---

## 1. What `docs/CONTROL_PLANE_SETUP.md` requires

`docs/CONTROL_PLANE_SETUP.md` is a **rebuild-from-legacy implementation guide**,
not a "run these 3 commands" runbook — it has no explicit `maps init` sequence.
The relevant sections:

- **§1 Prerequisites** — from the repo root:
  ```bash
  mkdir -p .maps/state
  python3 -m venv .venv && source .venv/bin/activate
  python -m pip install --upgrade pip
  ```
  (`mkdir -p .maps/state` is belt-and-braces — see §2, the runtime creates it.)
- **§2 SQLite → "Connection defaults"** — every task-ledger connection must use
  `PRAGMA foreign_keys = ON; journal_mode = WAL; busy_timeout = 5000`. **The
  runtime already does this** in `runtime/state/base.py::BaseStore._connect`
  (verified) — no manual step.
- **§2 → "Do not start from the old minimal schema"** / **§10 "Local-state
  ignore rules"** — `.venv/`, `.maps/state/`, `.hcom/` stay out of Git; "Tracked
  Markdown remains the durable human-readable project record."
- **§5 "Canonical enforcement: remediating a denied resume"** — the remediation
  workflow (reproduced in §4 below).
- **§11 Troubleshooting → SQLite** — post-hoc inspection:
  ```bash
  sqlite3 .maps/state/maps.db '.tables'
  sqlite3 .maps/state/maps.db 'PRAGMA integrity_check;'
  ```

### (a) Create the control-plane DB

There is a **`maps init`** subcommand (`runtime/cli.py:78`,
`init = sub.add_parser('init', help='create/open the task database')`). But the
DB is created as a side effect of constructing `TaskStore(db_path)` —
`BaseStore.__init__` runs `self.db_path.parent.mkdir(parents=True,
exist_ok=True)` then `conn.executescript(schema.sql)` (all `CREATE TABLE IF NOT
EXISTS`). So:

```bash
cd ~/Projects/MAPS_Lean
python3 -m runtime.cli --db .maps/state/maps.db init
```

`--db` defaults to `.maps/state/maps.db` (`runtime/cli.py:26 DEFAULT_DB`), so
`python3 -m runtime.cli init` from the repo root is equivalent. Output:
`{"ok": true, "db": ".maps/state/maps.db", "settings": {foreign_keys, journal_mode, busy_timeout}}`.

**Consequence to know:** *any* `maps` subcommand — `maps status`, `maps show`,
`maps recovery-tick` — constructs `TaskStore` and therefore **creates and
schema-initialises `.maps/state/maps.db` on first run.** There is no
"read-only, no side effect" `maps` invocation. The coordinator's very first
`maps` command *is* the DB-creation step, whatever it is. (This is why this
note did not run `maps status`.)

### (b) Register `--harness-project-id`

**Not a registration step.** `--harness-project-id P` is a *pass-time argument*
to `maps recovery-tick`, not persisted anywhere. It binds the one
`HcomHarnessAdapter` the enforced pass constructs
(`build_canonical_harness_service(..., project_id=P)`), and
`CanonicalRunGuard` then requires `binding.project_id == task.project_id ==
manifest`-implied project == `session_ref.project_id == P` on every guarded
operation (`_base_evidence` → `PROJECT_MISMATCH`; `_require_durable_session` →
`SESSION_PROJECT_MISMATCH`).

`P` **must equal the `project_id` string carried by the tasks / run manifests
you want guarded.** It is never inferred (`runtime/cli.py:722` — "never
inferred from an incident"; a tick can span several projects and the adapter is
single-project). Pick `P` = whatever `project_id` your real MAPS_Lean tasks use
(e.g. `maps-lean`). No table, no `maps` verb registers it.

### (c) Get real run manifests into it

`create_run_manifest` has exactly two production callers
(`runtime/state/schema.sql:139 run_manifests`; grep-verified):

1. **`runtime/flow_start.py:145`** — `maps flow start <task_id> --worker-id W
   --repo-root PATH [--require-canonical-run]`. Claims the task, builds the
   context plan, binds an **immutable** run manifest (append-only —
   `trg_run_manifests_no_update` / `_no_delete`, schema.sql:172/178). It
   **stops before a provider session** (`next_step.state ==
   STOPPED_BEFORE_PROVIDER_SESSION`) — so it writes **no** `run_session_links`
   row (see §3).
2. `runtime/integrity/cli.py` `run-verify-git` — diagnostic, not a dispatch
   flow.

`--require-canonical-run` (`runtime/cli.py:320`) makes manifest creation *fail*
unless the repo root has a readable Git worktree identity — it records the
`worktree` mapping the guard's `_require_bound_worktree` later checks.

---

## 2. What state gets created, and is any of it in Git

| Path | Created by | Contents | Git |
|---|---|---|---|
| `.maps/state/maps.db` (+ `-wal`, `-shm`) | first `TaskStore(...)` construction | the full `runtime/state/schema.sql` — ~60 tables: `tasks`, `task_*` child tables, `task_events`, `run_manifests`, `run_worktree_bindings`, `run_context_refs`, `run_session_links`, `task_submissions`, `reviews`, `review_subjects`, `release_checks`, `skill_lifecycle_*`, `authorized_operators`, `run_environment_evidence`, `run_recovery_links`, `continuity_links`, … | **gitignored** — `.gitignore:10` `/.maps/state/` |
| `.maps/state/recovery.json` | first `RecoveryStore.save()` inside the first `maps recovery-tick` / `maps claim` piggyback | a single JSON snapshot: `{incidents: {...}, ...}` — RnS incident state. **Mutable** (atomic `tmp.write_text(...)` + rename, `runtime/recovery/store.py:84`), not append-only | gitignored (same rule) |
| `.maps/state/langgraph-checkpoints.db` | only if you run the §3 LangGraph smoke in the setup doc | LangGraph checkpoints — **not needed** for the enforced pass | gitignored |
| `.hcom/` | hcom, if `HCOM_DIR=$PWD/.hcom` is set | hcom transport/session state | gitignored `.gitignore` `/.hcom/` |
| `.venv/` | `python3 -m venv .venv` | Python env | gitignored `/.venv/` |

**Nothing under `.maps/` is or ever becomes tracked.** `CONTROL_PLANE_SETUP.md`
§10 is explicit: tracked Markdown is the durable record; local state is
disposable. This is the basis of the reversibility answer (§5).

Precision on the ignore rule: `.gitignore:10` is `/.maps/state/`, **not**
`/.maps/`. Everything the runtime writes lives under `.maps/state/` (verified —
`DEFAULT_DB`, `DEFAULT_RECOVERY_STATE_PATH`, the LangGraph checkpoint path all
have the `state/` segment), so all of it is ignored. But a hypothetical future
file placed directly at `.maps/<x>` (not under `state/`) would **not** be
auto-ignored — no current code creates one; if the setup ever adds a
`.maps/`-level file, widen the rule to `/.maps/` at that point.

Immutability inside `maps.db`: `run_manifests`, `run_environment_evidence`,
`skill_lifecycle_*`, `release_checks`, `run_recovery_links` all carry
`BEFORE UPDATE`/`BEFORE DELETE` `RAISE(ABORT)` triggers. `tasks` rows are
mutable (status/claim/lease/attempt) via guarded store methods only.

---

## 3. What the first enforced pass actually does — traced

Command (per `runtime/cli.py:709-745`):

```bash
python3 -m runtime.cli --db .maps/state/maps.db recovery-tick \
  --enforce-canonical-run \
  --harness-project-id <P> \
  --repo-root ~/Projects/MAPS_Lean \
  [--binding <WORKER_ID>=<SESSION_NAME> ...]
```

`--enforce-canonical-run` **requires** both `--repo-root` and
`--harness-project-id` (CLI `parser.error` otherwise). It composes with, and
runs *after*, `--enforce-validation` if that is also passed (they are separate
flags; this note is canonical-run only).

### Trace

`run_recovery_tick_isolated(store, harness_project_id=P,
validation_repo_root=repo_root, ...)`
→ `run_recovery_tick` → because `harness_project_id` is set:
`harness_service = build_canonical_harness_service(store, project_id=P,
repo_root=repo_root)` which constructs, **for the first time in production**:

1. `HcomHarnessAdapter(HcomAdapter(hcom_dir=.hcom, executable=hcom, timeout=30s),
   project_id=P, lineage_writer=store)`
2. `HookRegistry()`
3. `register_canonical_run_guards(registry, CanonicalRunGuard(store,
   repo_root=repo_root))` — subscribes the guard READ_ONLY at
   `RUN_STARTING`, `BEFORE_SEND`, `BEFORE_RESUME`, `SESSION_STOPPING`
4. `register_destructive_external_action_guards(registry,
   DestructiveExternalActionGuard(store))`
5. `register_memory_provenance_guards(registry, MemoryProvenanceGuard())`
6. `HarnessService([adapter], hooks=registry)`

Then `RecoverySupervisor(task_reader=store, hcom=HcomAdapter(...),
recovery_store=RecoveryStore(".maps/state/recovery.json"),
harness_service=<the above>, ...)`.

- `supervisor.observe_silent_stops(bindings)` — opens a silent-stop incident
  **only** for a `worker_id` present in the explicit `--binding` map that has
  **exactly one** `ACTIVE` task and a detected stop. **No `--binding` → no
  incident opened, ever** (`runtime/cli.py:711` `_parse_bindings`; supervisor
  `observe_silent_stops` iterates only `bindings.items()`).
- `supervisor.tick()` — for each reprocessable incident
  (`_REPROCESSABLE_STATES = {scheduled, probing, blocked_validation, denied}`),
  attempts a resume.

### The guard is only reached for a *routable* incident

`tick()` calls `_resolve_harness_binding(incident, session_name)` (supervisor
:208). That returns a usable `(ExecutionBinding, SessionRef)` **only if**:

- `incident["run_id"]` is set, and
- `store.compute_task_revision(task_id)` and `task.project_id` are non-empty, and
- **`store.resolve_run_session(run_id)["state"] == "EXPLICIT"`** and
  `current.adapter_id == "hcom"` and `current.session_id` is non-empty
  (supervisor :240-248).

If any of those fail → `(None, None, reason)` → `harness_resume = {"attempted":
False, "reason": reason}` → **the code falls through to the pre-existing direct
`self.hcom.resume(...)` call** (supervisor :570 comment: "harness attempt
failed for a non-canonical reason … fall through … preserve current
direct-resume behavior"). **No guard call, no denial, byte-identical to a
non-enforced pass.**

### Why no run has `EXPLICIT` session lineage on a fresh `.maps/`

`run_session_links` (schema.sql:258, `UNIQUE(project_id, adapter_id,
session_id)`) is written by exactly one production path:
`HcomHarnessAdapter.record_run_session_link(...)` inside
`HcomHarnessAdapter.start()` / `.resume()` (`runtime/harness/adapters/hcom.py:218`),
which is only ever called by `HarnessService`, which is only ever constructed
by `build_canonical_harness_service` (this pass), and is only ever *invoked* by
`RecoverySupervisor.tick()` — **which pre-checks `state == "EXPLICIT"` before
calling it.** No `maps` CLI records a session link (grep: no `session-link` /
`record_run_session_link` in `cli.py`). `flow start` explicitly stops before a
session.

**Net: on the first pass there is no `EXPLICIT` lineage, so no incident is
routable, so `CanonicalRunGuard.__call__` never runs, so there are zero
`resume_denied` outcomes.** The pass's observable effect is limited to: (1) the
composition is constructed (the instantiation itself), (2) `recovery.json` is
written/updated, (3) every incident (if any were opened via `--binding`) is
resumed exactly as an un-enforced pass would resume it.

### What the guard *would* decide (once a routable binding exists — future state)

For `operation == "resume"` (`continuing = True`, `session_bound = True`),
`CanonicalRunGuard.__call__` denies in this order (`runtime/policy/harness_guard.py`):

`BINDING_REQUIRED` → `BINDING_INCOMPLETE` → `TASK_NOT_FOUND` →
`PROJECT_MISMATCH` → `RUN_NOT_FOUND` → `RUN_TASK_MISMATCH` →
`RUN_WORKER_MISMATCH` → `RUN_REVISION_MISMATCH` → `TASK_REVISION_STALE`
(current `compute_task_revision` ≠ manifest) → `TASK_NOT_ACTIVE` →
`NOT_CLAIM_OWNER` → **`LEASE_EXPIRED`** → `RUN_STALE`
(`check_run_stale`: task revision changed *or* a recorded context-ref file's
sha256 changed *or* is missing — `runtime/state/integrity.py:402`) →
`RUN_WORKTREE_UNAVAILABLE` / `RUN_WORKTREE_MISMATCH` (only for
`worktree`-bound manifests) → `SESSION_REF_REQUIRED` / `SESSION_REF_INCOMPLETE`
/ `SESSION_PROJECT_MISMATCH` / `SESSION_ADAPTER_MISMATCH` /
`SESSION_NOT_DURABLY_BOUND` / `SESSION_ADAPTER_UNPROVEN` /
`SESSION_LINEAGE_INVALID` / `SESSION_LINEAGE_UNPROVEN` / `SESSION_BINDING_MISMATCH`.

Only a `HarnessService.resume()` result code in `_CANONICAL_DENIAL_CODES =
{"HOOK_DENIED", "APPROVAL_REQUIRED"}` (supervisor :24) becomes
`action = "resume_denied"` + incident `state = "denied"`. Any other guard
outcome that isn't an outright service failure falls through to direct resume.

`denied` state (supervisor :580+): `last_error` = deny reason;
`canonical_denials` counter += 1; transient `attempt` retry budget **untouched**;
flat-interval reschedule; at `canonical_denials >=
_MAX_CONSECUTIVE_CANONICAL_DENIALS (3)` → `state = "failed"`, `last_error =
"canonical_denial_persistent"`. A single non-denied outcome resets the streak.

**The design notes' "converts currently-working resumes into `resume_denied`,
most likely via `LEASE_EXPIRED`" warning describes this future state, not the
first pass on a fresh DB.**

---

## 4. The remediation workflow (`docs/CONTROL_PLANE_SETUP.md` §5)

For an incident parked `denied` via `LEASE_EXPIRED` (the "dominant
first-exposure denial" per the doc — a silently-stopped session's claim lease
has lapsed):

```bash
# 1. claim-recover the expired ACTIVE claim under the manifest's ORIGINAL worker
python3 -m runtime.cli --db .maps/state/maps.db claim <task-id> \
  --worker-id <ORIGINAL manifest worker_id> --lease-seconds <N>

# 2. re-run the enforced pass
python3 -m runtime.cli --db .maps/state/maps.db recovery-tick \
  --enforce-canonical-run --harness-project-id <P> --repo-root <PATH>
```

Rules (from the doc, source-verified):

- `--worker-id` **must** be the run manifest's recorded `worker_id`.
  `CanonicalRunGuard._base_evidence` checks `manifest.worker_id == binding
  worker` (`RUN_WORKER_MISMATCH`) and `_require_live_claim` checks
  `task.claimed_by == worker` (`NOT_CLAIM_OWNER`); recovering under a different
  worker clears `LEASE_EXPIRED` only to trip one of those on the same pass.
- `claim_task`'s recovery path bumps the task-truth **`attempt`** (counted
  against `max_attempts`), *distinct* from the recovery incident's retry
  counter. A task already at `attempt >= max_attempts` returns **`ATTEMPT_LIMIT`**
  — that incident is genuinely done; **close it, do not resume**.
- Claim-recovery does **not** change `task_revision`
  (`compute_task_revision`'s inputs — `runtime/state/integrity.py`
  `_task_definition_conn` — are the task definition columns + child tables +
  policy + environment; **not** `status` / `claimed_by` / `lease_expires_at` /
  `heartbeat_at` / `attempt` / `updated_at`). So `recover + re-tick` is
  complete — no "start a fresh run" step for a revision-stable task.
- **`maps heartbeat` does NOT work here** — it refuses an already-expired lease
  (`LEASE_EXPIRED`) and requires the caller to still be the live claimant;
  neither holds in the recovery case.

For a `RUN_STALE` denial: a recorded context-ref file changed on disk since the
run was bound. Remediation is a **new run** (`maps flow start`), not
claim-recovery — the old run's context evidence is genuinely stale.

For `RUN_WORKTREE_MISMATCH`: the resume is being attempted from a different Git
worktree than the manifest recorded. Continue from the correct worktree, or
start a new run.

---

## 5. Reversibility

**Fully reversible.** `rm -rf .maps/` resets the entire control plane —
everything under `.maps/state/` is gitignored (`.gitignore:10`), nothing is
committed, ever, and `maps init` (or any `maps` command) rebuilds the schema
from scratch (`CREATE TABLE IF NOT EXISTS` — idempotent).

What the enforced pass writes:

- **Task truth (`maps.db` `tasks` + children): nothing.** `CanonicalRunGuard`
  is `HookSideEffect.READ_ONLY`; the `resume_denied` branch comment is explicit
  — "no task truth is touched". `run_manifests` is append-only regardless
  (UPDATE/DELETE triggers).
- **`.maps/state/recovery.json`**: the only mutable artifact the pass writes —
  a single JSON snapshot of incident state, rewritten atomically each tick.
  Freely editable or deletable; deleting it drops all incident history and the
  next pass starts clean.
- **Guard decisions are not separately persisted** — a denial lives only in the
  returned action dict (stdout JSON) and the `denied` incident's `last_error` /
  `canonical_denials` fields in `recovery.json`.

What the **remediation** (`maps claim --worker-id ORIGINAL`) writes: bumps
`tasks.attempt` and re-sets `claimed_by` / `lease_expires_at` / status. The
`attempt` bump is the one semi-durable effect — it is bounded by
`max_attempts` and only reversible by recreating the task. Nothing else the
runbook does touches durable task truth.

Reset recipes:
- **Undo one bad pass, keep the DB:** `rm .maps/state/recovery.json`.
- **Full reset:** `rm -rf .maps/` then `maps init`.
- **Inspect before deciding:** `sqlite3 .maps/state/maps.db '.tables'`;
  `python3 -m runtime.cli --db .maps/state/maps.db status`;
  `cat .maps/state/recovery.json`.

---

## 6. The 7-row verification — what each row needs, and what the pass does / does not give it

The pass is a **prerequisite/enabler** for these rows, **not** a completion
event. Each row today says some variant of "no first real production exposure
of an enforced pass"; each *also* has further unmet conditions. **Do not flip
any row** — this is what #18 / a future gate step checks.

| Row | "Still missing before a status flip" (from the row) | What the first pass gives it | Does the pass alone flip it? |
|---|---|---|---|
| **6.4** Deterministic Hooks | write/credential guards + capability-declaration manifest not built; needs the `CANONICAL_RUN` + `DESTRUCTIVE_EXTERNAL_ACTION` composition exercised | the composition is **instantiated** in production for the first time (`build_canonical_harness_service` constructs both guards + registry) | **No** — write/credential guards still absent |
| **6.5** Immediate deterministic validation | executed validation is advisory-only; no path consults the result to allow/deny; needs *enforcement* of the validation-tier *outcome* | **Nothing** — canonical-run enforcement guards run *identity*, not validation-tier outcome. That is `--enforce-validation` (a separate flag/gate) | **No** — wrong enforcement layer |
| **6.22** Memory trust classes (`MemoryProvenanceGuard` first exposure) | `HarnessService.send()` has no production caller and no assembler emits `memory_provenance`; needs "a real `send()` caller denied on a `WITHHOLD` item" | the guard is **instantiated** in the composition (§3 step 5, `register_memory_provenance_guards`) — but `RecoverySupervisor` only ever calls `.resume()`, never `.send()`, so the guard's `BEFORE_SEND` callback is never fired by this pass | **No** — instantiation-only, same pattern as the H5 row; the real exit (a denied `send()` on a `WITHHOLD` item) is unreachable from `recovery-tick` |
| **6.16 / E6(b)** Git worktree isolation | composition root default-off, exercised only on `recovery-tick`, **no first real production exposure** | the composition is instantiated; a *routable* `RUN_WORKTREE_MISMATCH` denial would be the exposure evidence — but see §3, no routable binding on a fresh DB | **No** — needs a routable binding to actually exercise the worktree seam |
| **H5** Remaining adapters + contract suite | "closes only after the first real production exposure of an enforced pass (which converts currently-working resumes into `resume_denied`)" | the pass instantiates `HarnessService` + `HookRegistry` with a non-test caller (already true since #175's composition landed); a real `resume_denied` is **not reachable** (§3) | **No** — the stated exit criterion is currently unreachable; see §8 |
| **E4** Validation tiers | execution is opt-in, `quick`-only, advisory; `make_validation_hook` attached to no production registry | **Nothing** — canonical pass carries the `CanonicalRunGuard` only, not a validation callback | **No** — same as 6.5 |
| **L6** Harness configuration identity | no production call site sets/persists the harness-config hash onto a real run manifest; `create_run_manifest` callers have no `HarnessService` in scope; the enforced-resume path creates no manifests | **Nothing** — the pass creates no manifest and the manifest-writer (`flow_start`) has no `HarnessService`. This is a **wiring gap**, not an exposure gap (`work/notes/2026-09-01-traj12-next3-scoping.md` / PR #216 confirms L6 is *blocked on* Ask #1 as a sequencing prerequisite, then needs its own wiring PR) | **No** — needs a wiring change after the pass |

**Summary for the gate step:** a successful first pass lets each row's evidence
text advance from "composition default-off, never exposed" to "composition
instantiated in a real enforced pass on <date>; behaviour observed: <N
incidents, 0 routable, 0 denials>" (or, if a routable denial is later
engineered, "denial <CODE> observed and remediated per §4"). **None of the 7
reach DONE from the pass alone** — 6.4 needs write/credential guards, 6.5/E4
need the validation-outcome gate, L6 needs manifest wiring, H5 and 6.22 need a
reachable denial (a `resume_denied` / a denied `send()` respectively — §8),
6.16 needs the worktree seam actually exercised. Three of the seven (6.16, H5,
6.22) share the same "guard instantiated in the composition but its callback
never fired for lack of a reachable operation" shape.

---

## 7. Risks / operator-visible consequences

- **First pass, current state (no `.maps/`, no incidents, no `--binding`): zero
  operator-visible consequence.** `observe_silent_stops({})` opens nothing;
  `tick()` has nothing to process; the composition is built and discarded.
- **First pass *with* a `--binding` map naming a real stalled worker:** an
  incident is opened and resumed **exactly as an un-enforced pass would** (§3 —
  no routable guard binding → direct `hcom.resume()` fallback). No `denied`
  state, no task-truth change.
- **Future state (once `EXPLICIT` session lineage exists for a run):** an
  enforced pass can park a *working* incident as `denied` — flat-interval
  reprobe, `attempt` budget untouched, own 3-strike ceiling → `failed` /
  `canonical_denial_persistent`. Most likely `LEASE_EXPIRED` (silently-stopped
  session's lease lapsed). Remediation per §4. **No task truth is mutated by
  the denial itself.**
- **Real incidents that a pass would touch *right now*: none.** `.maps/` does
  not exist, so there are no run manifests, no incidents, no session lineage.
  `git log` / `git grep` show no tracked incident records (incidents live only
  in the gitignored `recovery.json`). `maps status` cannot be consulted without
  first creating the DB (§1b) — and it would report an empty store.
- **`.hcom` isolation:** run every hcom-touching command with
  `HCOM_DIR=$PWD/.hcom` (`CONTROL_PLANE_SETUP.md` §4) so the pass's `hcom list`
  calls read this clone's transport state, not a global one. The enforced pass
  makes two `hcom list` subprocess calls (bounded at
  `DEFAULT_HCOM_TIMEOUT_SECONDS = 30s` each).

---

## 8. Is there an operator/coordinator decision beyond "go / timing"? — YES, one

**The lineage-bootstrap gap.** Ask #1 is scoped as "the first enforced pass
that converts currently-working resumes into `resume_denied`" (the H5 / design
§2c framing). Per §3, that outcome is **not reachable with the current code**:
no production path writes the `EXPLICIT` hcom session lineage the supervisor
requires before it will route a resume through the guarded `HarnessService`,
and the supervisor pre-checks that lineage before it would let the adapter
bootstrap it. So the guard's decision logic cannot fire on a real incident.

**This is an operator decision, not a coordinator one.** The operator's #243
"go" on Ask #1 was for a specific pictured outcome — currently-working resumes
becoming `resume_denied`, exposing the enforcement layer for real. That outcome
is now known to be **unreachable** without a code change (§3). So the operator
authorised something that cannot happen as they pictured it, and must at
minimum be told: *the pass you authorised will produce 0 denials against the
current code; option (B) is the code change needed for the outcome you meant.*
Whether to (A) run the 0-denial pass now for the instantiation evidence, or (B)
do the lineage-bootstrap wiring first, is then the operator's call:

- **(A) Accept a narrower "exposure"** — the first pass *instantiates* the
  composition in production and is documented to have processed the real
  incident set with 0 routable bindings / 0 denials. Update the 7 rows'
  evidence text to that effect; treat "a real `resume_denied`" as a later
  milestone gated on the lineage work. Lowest risk, available now.
- **(B) Require the lineage-bootstrap wiring first** — a small reviewed change
  so that a production path (e.g. `maps flow start`, or a new
  `maps run attach-session`) records the first `run_session_links` row, making
  runs routable and the guard actually exercisable. Then the enforced pass can
  produce (and §4 can remediate) a real denial. This is a scoped follow-up, not
  part of Ask #1's authorization.

Recommendation to put to the operator: **(A) + (B) sequenced** — run the
documented 0-denial pass now for the instantiation evidence (it is within the
granted scope: a pass, not a code change), *and* open a separate scoping note
for the lineage-bootstrap wiring (B) as the real path to H5 / 6.16 / 6.22 DONE.
(A) alone does not deliver what #243 authorised; (B) alone leaves the
instantiation evidence ungathered.

Everything else in this runbook is "go / timing" only.

---

## 9. The runbook — condensed command sequence (for the coordinator)

```bash
cd ~/Projects/MAPS_Lean
export HCOM_DIR="$PWD/.hcom"

# 0. (optional) venv per CONTROL_PLANE_SETUP.md §1
python3 -m venv .venv && source .venv/bin/activate && python -m pip install -U pip

# 1. create the control-plane DB  (== the "establish .maps/" step)
python3 -m runtime.cli --db .maps/state/maps.db init
# expect: {"ok": true, "db": ".maps/state/maps.db", "settings": {...WAL, FK on...}}

# 2. sanity — empty store
python3 -m runtime.cli --db .maps/state/maps.db status
sqlite3 .maps/state/maps.db '.tables'
sqlite3 .maps/state/maps.db 'PRAGMA integrity_check;'   # expect: ok

# 3. (only if exercising the guard for real — decision (B) territory, NOT Ask #1)
#    create a real run manifest:
# python3 -m runtime.cli --db .maps/state/maps.db flow start <TASK> \
#   --worker-id <W> --repo-root "$PWD" --require-canonical-run

# 4. THE FIRST ENFORCED PASS
python3 -m runtime.cli --db .maps/state/maps.db recovery-tick \
  --enforce-canonical-run \
  --harness-project-id <P> \
  --repo-root "$PWD"
#   add --binding <W>=<SESSION_NAME> only if you have a real stalled worker to recover
#   expect (fresh DB, no bindings): {"ok": true, "opened_incidents": [], "actions": []}

# 5. inspect
cat .maps/state/recovery.json 2>/dev/null || echo "(no incidents -> no recovery.json)"

# --- remediation, only if an incident parks as "denied" (see §4) ---
# python3 -m runtime.cli --db .maps/state/maps.db claim <TASK> \
#   --worker-id <ORIGINAL manifest worker> --lease-seconds 1800
# python3 -m runtime.cli --db .maps/state/maps.db recovery-tick \
#   --enforce-canonical-run --harness-project-id <P> --repo-root "$PWD"

# --- reset ---
# rm .maps/state/recovery.json      # undo incident state, keep DB
# rm -rf .maps/                     # full reset (all gitignored)
```

`<P>` = the `project_id` your real tasks carry. Never pass `--enforce-validation`
unless you also intend the resume-validation gate (separate feature, not this
ask). Never run any `--enforce-*` flag against a checkout other than the one
named by `--repo-root`.

---

## 10. Boundaries honoured

Read-only investigation. No `maps` command run. `.maps/` not created. No
`--enforce-*` run. `runtime/` untouched. No checklist status changed.
`python3 -m runtime.smoke` → exit 0 (design-only PR sanity — run in the PR).

Re-verify at execution time (rule 14): `runtime/cli.py` `recovery-tick`
argument wiring; `build_canonical_harness_service`; `CanonicalRunGuard`
deny-code order; `RecoverySupervisor._resolve_harness_binding`'s
`state == "EXPLICIT"` pre-check; whether any new CLI verb now writes
`run_session_links` (that would change §3 and §8).
