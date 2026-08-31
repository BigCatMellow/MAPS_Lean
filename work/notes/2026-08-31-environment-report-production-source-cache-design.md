# Routing environment report — production source & cache (roadmap 6.24)

Date: 2026-08-31
Status: design-only. No runtime code, no schema change, no checklist status
flip. Design review only.

Scopes the **production source and cache** for routing environment reports,
plus the default required-for-routing rule and a concrete second
scope-dimension. Continues:

- `work/notes/2026-08-21-routing-environment-report-sourcing-design.md` — the
  source/freshness boundary decision (explicit task-contract association, a
  caller-supplied envelope before the pure router, `INCOMPATIBLE`-only
  rejection preserved);
- horizon item `work/notes/2026-08-31-roadmap-trajectory-check-10.md` §5b.1;
- 6.24's checklist "Still missing" clause: *production source/cache, a
  default required-for-routing rule, and scope-dimension proof beyond
  canonical run identity*.

All callsite claims re-verified at `origin/main` `fae8251` (rule 14).

---

## Q1 — Where does a production environment report come from?

### 1a. Today: only caller-supplied

`runtime/routing/environment_reports.py::select_fresh_environment_reports()`
filters a `Mapping[str, envelope-dict]` handed in by the caller (in practice
`maps route --environment-reports-json <file>`, `runtime/routing/cli.py:71`).
It never inspects an environment, computes a fingerprint, or reads recorded
state. That is the correct pure-router boundary and stays.

### 1b. There is already a recorder — with zero production writers

`runtime/state/environment.py::EnvironmentEvidenceMixin.record_run_environment_evidence(run_id, *, spec, fingerprint, spec_ref, recorded_by, reference=None)`
(E3, PR shipped) already:

- calls `evaluate_environment_compatibility(spec, fingerprint, reference=...)`
  → a real `CompatibilityReport` (line ~84);
- persists `compatibility_state` **and** the full `compatibility_snapshot`
  (`report.to_dict()`) into `run_environment_evidence`, **insert-only /
  immutable** (an `UPDATE` is refused by a DB trigger), keyed by `run_id`;
- fail-closes on `environment_spec_hash` ≠ `spec.sha256` and on
  sensitive-text in any snapshot.

`grep -rn record_run_environment_evidence runtime/` → **no production
writer** (only `RunBoundValidator` *reads* `run_environment_evidence`
rows). `runtime/recovery/production.py`'s own docstring says so verbatim:
"`record_run_environment_evidence` currently has zero production writers".

So the **report format, the compute step, and the durable store already
exist**. The missing piece is (a) something that computes a `fingerprint`
and calls the recorder in production, and (b) a read-side projection from
that store into the router's task-ID-keyed input.

### 1c. The production writer: `maps flow start`, not a new subsystem

`runtime/flow_start.py::flow_start()` already composes claim → context plan →
**`create_run_manifest`** (so a `run_id` exists) and has `repo_root` in hand.
`EnvironmentSpec` inspection is `runtime/environment/safety.py::inspect_local_environment(spec, *, repo_root=...)`
— a **one-shot pure function** (E2), not a daemon or prober.

Proposed production write point: a **step 4 in `flow_start()`**, executed
only when the task carries an environment contract
(`task["environment"] is not None`, i.e. a `task_environment` row exists):

1. `load_environment_spec(repo_root / task["environment"]["spec_ref"])`;
2. `fingerprint = inspect_local_environment(spec, repo_root=repo_root)`;
3. `store.record_run_environment_evidence(run_id, spec=spec,
   fingerprint=fingerprint, spec_ref=..., recorded_by="maps-flow-start")`.

This is wiring two existing E2/E3 functions into an existing composition — it
adds **no new capability**: `inspect_local_environment` already does exactly
this probing today (it is what E2 shipped), and `record_run_environment_evidence`
already owns the trust boundary and the immutability trigger. The
`task_environment` row is itself the opt-in — a task with no environment
contract records nothing and routes exactly as today.

**This does not trigger the dispatch STOP condition.** No live environment
prober is introduced; `inspect_local_environment` is a synchronous
repo-scoped inspection that already exists and is already the E2 exit
artifact.

Deferred alternative considered — a standalone `maps environment-probe
<task> --repo-root` command (operator/CI-invoked, mirroring `maps
recovery-tick --repo-root`): rejected as slice 1 because
`run_environment_evidence` is `run_id`-keyed and a task being routed may have
no run yet, so the probe would need either a task-scoped store (schema
change, deferred — Q2) or to attach to "the latest run manifest", which is
exactly what flow-start already produces. Flow-start is the smaller change.

### 1d. Temporal model (important, not a defect)

Routing runs **before** `flow_start`. So a report recorded at flow-start of
run N informs routing decisions for run N+1 and for later tasks. The
first-ever routing of a task has **no** report → non-rejecting (or a hold
if `required_for_routing`, Q3). This matches the prior note's "missing
report preserves current routing behavior" rule and needs no live inspection
on the routing path.

---

## Q2 — The cache

**It rides the tables that already exist. No new table, no schema change.**

| Concern | Where it already lives |
|---|---|
| Durable report store | `run_environment_evidence` (insert-only, immutable, `compatibility_snapshot` = `report.to_dict()`), keyed by `run_id` |
| Task → spec association | `task_environment.spec_ref` |
| Freshness TTL | `task_environment.max_age_seconds` (`CHECK (max_age_seconds > 0)`) |
| Produced-at | `run_environment_evidence.created_at` |
| Task ↔ run join | `run_manifests.task_id` + `run_manifests.task_revision` (lookup `SELECT * FROM run_manifests WHERE task_id = ? ORDER BY created_at, run_id` already exists in `runtime/state/observability.py:158`) |
| Older-revision tolerance | `task_environment.allow_older_task_revision` |

The "cache" is therefore a **read-side projection**, not a new storage
layer: for a task, take the latest `run_manifests` row → its
`run_environment_evidence` row → apply the same freshness checks
`select_fresh_environment_reports()` already implements
(`environment_spec_hash == spec.sha256`, age ≤ `max_age_seconds`,
task-revision match unless `allow_older_task_revision`, project boundary) →
yield a `CompatibilityReport` or a non-blocking diagnostic. Same
`RoutingEnvironmentReportSelection` shape, sourced from SQLite instead of a
JSON file.

**Schema change = its own authorised step, not slice 1.** If a *task-scoped*
(rather than run-scoped) evidence row is ever wanted — so a report can exist
before the first run — that is a new `task_environment_evidence` table with
its own immutability trigger and its own authority question (who may write a
task-scoped environment claim), and it must be designed and reviewed
separately. Slice 1 stays entirely on the run-scoped store.

No in-memory cache: routing is a short-lived CLI/LangGraph pass; a
per-process cache would be a second mutable copy of `run_environment_evidence`
(rule 12) for no measurable benefit.

---

## Q3 — The default required-for-routing rule

### The column already exists

`task_environment.required_for_routing INTEGER NOT NULL DEFAULT 0` — a
per-task, operator-authored flag set through
`store.update_contract(task_id, {"environment": {..., "required_for_routing":
true}})` (`runtime/state/environment_contract.py`). Its own docstring today:
"intentionally does not source reports or influence routing."

### Recommendation

**Per-task, operator-authored, default-off — no global default, no
enabled-by-default rejection.**

- `required_for_routing = 0` (the default): unchanged — a missing/stale
  report is non-rejecting, exactly as today.
- `required_for_routing = 1`: routing **holds** the task (a policy-gate
  reason `environment_report_required`, routed to
  `policy_gate/environment_report_required`) when no *fresh* report can be
  projected for it. A **hold**, not a hard reject: it clears itself the
  moment a fresh report lands (i.e. after the task's next `flow_start`),
  parallel to how an unapproved gated task clears when approval is recorded.

The authority to say "this task must not route without a proven environment"
is the operator who authors the task contract — the same authority that
already sets `spec_ref` and `max_age_seconds`. This mirrors the
`--enforce-canonical-run` / `--enforce-validation` model (a deliberate,
default-off opt-in) but at the **contract** granularity the column already
provides, rather than a CLI flag.

Optionally, a *second* layer — a `maps route --enforce-environment-routing`
operator flag that promotes **every** task with an environment contract to
required-for-routing regardless of its column — is a natural fast-follow for
"the whole fleet must prove environment now", but slice 1 needs only the
column. Not designed here beyond naming it.

**MUST NOT (dispatch boundary):** no rule that makes a missing report
blocking for a task whose `required_for_routing` is 0; no global default
flipping that column's meaning.

---

## Q4 — `DRIFTED` / `UNKNOWN`

Prior note preserved: `UNKNOWN` and `DRIFTED` do not reject on environment;
only `INCOMPATIBLE` routes to `policy_gate/environment_incompatible`. **Keep
that in slice 1**, including under `required_for_routing = 1`:

- A fresh report in state `DRIFTED` / `UNKNOWN` / `COMPATIBLE` /
  `COMPATIBLE_WITH_WARNINGS` **satisfies** the required-for-routing rule —
  "a fresh report exists" is the bar, and the report's *content* gate stays
  `INCOMPATIBLE`-only.
- Only the **absence** of a fresh report trips the
  `environment_report_required` hold.

Interaction, stated plainly: the missing-report rule (Q3) and the
report-content rule (INCOMPATIBLE) are **orthogonal**. A `required_for_routing`
task with a fresh `DRIFTED` report routes; the same task with **no** report
holds; any task (required or not) with a fresh `INCOMPATIBLE` report is
gated.

Making `DRIFTED` itself gate is a strictness increase that belongs behind an
explicit future per-task `strict_environment` flag (a `task_environment`
column = schema change = deferred). Slice 1 must not add it.

---

## Q5 — The second scope dimension

Dimension 1 (shipped): **canonical run identity** — `CanonicalRunGuard`
intersects worker / task / policy on the one enforced resume path.

Smallest concrete dimension 2: **environment compatibility**, now driven by a
**production-sourced** report rather than only a caller-supplied JSON file.
`evaluate_assignment(task, worker, *, environment_report=...)` already
carries the axis (`environment_incompatible` reason); slice 1 makes that axis
*real in production* by feeding it from `run_environment_evidence` instead of
requiring an operator to hand-assemble `--environment-reports-json`.

The two-axis demonstration artifact (the "proof"):

1. Task T with an environment contract (`spec_ref`, `required_for_routing =
   1`). Route T → **held** (`environment_report_required`): no report yet.
2. `maps flow start T` in a checkout whose environment *matches* the spec →
   records a `COMPATIBLE` report. Re-route T → **routes** (worker ∩ task ∩
   policy ∩ **environment** all satisfied).
3. `maps flow start T` in a checkout that *violates* the spec → records an
   `INCOMPATIBLE` report. Re-route T → **rejected**
   (`environment_incompatible`), independent of worker capability.

That exercises least-privilege intersection on two independent axes
(identity + environment), which is exactly what the checklist clause asks
for.

---

## Q6 — Smallest first slice, STOP conditions, MUST-NOTs

### Smallest slice

1. **`runtime/flow_start.py`** — step 4: when `task["environment"]` is set,
   `load_environment_spec` → `inspect_local_environment(spec,
   repo_root=repo_root)` → `store.record_run_environment_evidence(run_id,
   ...)`. A recorder failure is a `_failed("environment_evidence", ...)`
   step result — the flow already fails-with-payload on any earlier step, so
   this is consistent; it does **not** get swallowed. (Open impl question:
   whether a recorder failure should hard-fail the flow or be a non-fatal
   warning — decide in impl, default to hard-fail for slice 1 since the task
   explicitly opted in via its contract.)
2. **`runtime/routing/environment_reports.py`** — a new pure function
   `select_recorded_environment_reports(store, task_ids, *, repo_root, now)`
   returning the existing `RoutingEnvironmentReportSelection`. Reuses the
   freshness predicates already in this module; sources rows from
   `run_manifests` + `run_environment_evidence` + `task_environment`.
3. **`runtime/routing/router.py` / `service.py` / `cli.py`** — `maps route
   --environment-reports-from-recorded` (default-off) selects the DB-sourced
   mapping; when both it and `--environment-reports-json` are given, the JSON
   envelope wins (explicit caller override) and that is surfaced in
   diagnostics.
4. **`evaluate_assignment` / `router.recommend_route`** — the
   `environment_report_required` hold when
   `task["environment"]["required_for_routing"]` and the selection yields no
   fresh report for that task. `required_for_routing = 0` path byte-identical
   to today.
5. **`work/roadmaps/CAPABILITY_CHECKLIST.md`** — narrow 6.24's "Still
   missing" clause; **no status flip**.

Tests: flow-start records a report for a contracted task and records nothing
for an uncontracted one; the DB selector yields fresh reports, drops stale /
spec-mismatched / revision-mismatched ones into diagnostics, and never
emits an incompatibility; `required_for_routing=1` + no report → held;
`required_for_routing=1` + fresh COMPATIBLE/DRIFTED → routes; fresh
INCOMPATIBLE → gated; `required_for_routing=0` unchanged; JSON envelope still
overrides.

### MUST NOT

1. Add a schema change / migration / new table in slice 1 — the run-scoped
   store, `task_environment.spec_ref` / `max_age_seconds` /
   `required_for_routing` / `allow_older_task_revision`, and
   `run_manifests.task_id` all already exist. (A task-scoped evidence table
   is a separate authorised step — Q2.)
2. Add a background inspector, daemon, scheduler, or any always-on process.
3. Compute a live fingerprint **inside the router** or
   `evaluate_assignment` — the router stays pure and consumes reports only.
4. Make a missing report blocking for a task whose `required_for_routing`
   is 0, or add a global default that changes that column's meaning.
5. Make `DRIFTED` / `UNKNOWN` reject, or convert stale / malformed / missing
   evidence into `INCOMPATIBLE`.
6. Pick a universal default `EnvironmentSpec` or infer `spec_ref` from a
   path heuristic — association stays explicit task-contract evidence
   (prior note).
7. Flip 6.24 (or E1/E2/E3) status. First real production exposure — a
   `maps flow start` that records a report and a subsequent `maps route`
   that consumes it — is still required before the row moves.
8. Route the `maps claim` piggyback or any non-`flow_start` path into the
   recorder in slice 1.

### STOP and escalate to `miga` if

- wiring the flow-start recorder forces `inspect_local_environment` to grow
  new probing capability (network calls, following dependency inputs outside
  the repo, executing spec commands) — it must not; if it does, the
  production source is a new subsystem and gets its own roadmap item;
- the run-scoped store turns out to be unusable for routing (e.g. routing
  genuinely needs a report before any run can exist for a class of tasks),
  forcing the task-scoped table into slice 1;
- the `environment_report_required` hold cannot be expressed without a new
  `PolicyDecision` outcome kind or a schema change.

---

## Roadmap impact

Does not complete 6.24. Specifies the production source (a `flow_start` step
wiring existing E2 `inspect_local_environment` + E3
`record_run_environment_evidence`, gated by the task's own environment
contract), the cache (the existing immutable run-scoped
`run_environment_evidence` store + `task_environment` TTL — no schema
change), the default required-for-routing rule (the existing
`required_for_routing` column, per-task, default-off, a hold not a hard
reject), the `DRIFTED`/`UNKNOWN` posture (unchanged), and the second
scope dimension (environment compatibility, production-sourced). After the
follow-up impl, 6.24's "production source/cache" and "scope-dimension proof
beyond canonical run identity" clauses close; "missing reports plus
DRIFTED/UNKNOWN remain non-rejecting" narrows to "non-rejecting **unless the
task's contract sets `required_for_routing`**". An optional one-line
"production source/cache design pending" annotation on 6.24 is within the
output boundary.

---

## Resume prompt

You are implementing the **first slice** of the routing environment-report
production source & cache for MAPS_Lean (roadmap 6.24). Work in your own git
worktree off `origin/main`; `git fetch origin main` first. Re-verify every
callsite at your HEAD (rule 14).

Source of truth: this note
(`work/notes/2026-08-31-environment-report-production-source-cache-design.md`),
its parent `work/notes/2026-08-21-routing-environment-report-sourcing-design.md`,
and the existing pieces it names:
`runtime/state/environment.py::record_run_environment_evidence`,
`runtime/environment/safety.py::inspect_local_environment`,
`runtime/flow_start.py`, `runtime/routing/environment_reports.py`,
`runtime/policy/evaluator.py::evaluate_assignment`,
`runtime/routing/router.py` / `service.py` / `cli.py`, and the
`task_environment` DDL in `runtime/state/schema.sql`.

Implement exactly the **Q6 "Smallest slice"** list (flow-start step 4;
`select_recorded_environment_reports`; `maps route
--environment-reports-from-recorded` default-off; the
`environment_report_required` hold on `required_for_routing = 1`; checklist
evidence text, no status flip).

MUST NOT: add a schema change / migration / new table; add a daemon or
background inspector; compute a live fingerprint in the router; make a
missing report blocking when `required_for_routing = 0`; make `DRIFTED` /
`UNKNOWN` reject; pick a universal default `EnvironmentSpec`; flip
6.24/E1/E2/E3 status; route the `maps claim` piggyback into the recorder.

Tests (one blocking foreground `python3 -m unittest` over the routing +
flow-start + environment-evidence modules, no Monitor/background): see the
note's test list. `python3 -m runtime.smoke` exits 0. Push before any
full-suite run; rely on CI.

Then: PR into `main` (never push to main). Request independent review with
mutation testing (min 5) against the freshness/selection + hold logic per
`reference_committee_review`; add a bound
`work/reviews/pr-<N>-review-evidence.md` (reviewer commits — see
`feedback_implementer_cannot_commit_review_evidence`). Do NOT self-merge.
Report the PR number to `miga`.

Stop conditions: if the flow-start recorder forces `inspect_local_environment`
to grow new probing capability, or routing genuinely needs a task-scoped
evidence row before any run exists, STOP and flag `miga`.
