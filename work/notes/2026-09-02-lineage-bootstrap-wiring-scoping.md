# Lineage-bootstrap wiring — scoping (the #255 §8 B code change)

**DESIGN ONLY. No impl, no `runtime/` change, no checklist change.** Scopes the
smallest wiring that lets a first `maps recovery-tick --enforce-canonical-run`
pass actually invoke `CanonicalRunGuard` — the true bottleneck for 6.16 / H5
(and, partially, 6.22), per trajectory check #18 (#256) and the #255 runbook
(`work/notes/2026-09-02-ask1-control-plane-runbook.md` §8).

Sources verified at `origin/main` `d8568a3` (rule 14).

Verdict: **SCOPE-FOR-IMPL.** Recommended write-site: **a new explicit
`maps run bind-session` verb** (candidate (b) below), a thin wrapper over the
already-guarded `store.record_run_session_link`. **No operator decision** —
recording a session binding is a claimant-scoped write, strictly narrower than
manifest creation (§4).

---

## The deadlock (restated, verified)

1. `CanonicalRunGuard.__call__` fires only as a `BEFORE_RESUME` (etc.) hook
   inside `HarnessService.resume()` (`runtime/policy/harness_guard.py`,
   `register_canonical_run_guards`).
2. `RecoverySupervisor.tick()` routes a resume through `HarnessService` only if
   `_resolve_harness_binding` returns a binding, which requires
   `resolve_run_session(run_id)["state"] == "EXPLICIT"` **and**
   `current.adapter_id == "hcom"` (`runtime/recovery/supervisor.py:240-248`).
3. `state == "EXPLICIT"` requires ≥1 `run_session_links` row forming a valid
   linear ATTACH(→REPLACE*) chain (`run_lineage.py::_resolve_run_session_conn`,
   the terminal `return {... "state": "EXPLICIT" ...}`).
4. The **incident's `run_id` itself** is resolved by
   `RecoverySupervisor._resolve_run_id` → `resolve_session_run(project_id,
   "hcom", session_id)` — a reverse lookup **on `run_session_links`**
   (`supervisor.py:162`). No row ⇒ no `run_id` on the incident ⇒
   `_resolve_harness_binding` returns `no_run_id_bound` immediately.
5. The sole non-test writer of `run_session_links` is
   `HcomHarnessAdapter._record_attach` /`.resume()` path
   (`runtime/harness/adapters/hcom.py:218`), reachable only *inside*
   `HarnessService.start()/.resume()` — i.e. only after step 2 already
   succeeded. `flow_start` writes the manifest and **stops before any session**
   (`flow_start.py` docstring: "It intentionally stops before choosing or
   launching a provider session").

**One `run_session_links` ATTACH row breaks the whole cycle** — it satisfies
both step 4 (incident gets a `run_id`) and step 3 (lineage becomes `EXPLICIT`).
The wiring is: *give a legitimate non-adapter caller a way to write that row.*

---

## 1. Where should the first `run_session_links` row be written?

### (a) `maps flow start`, after the manifest, when the caller supplies a session ref

- **Fit:** partial. `flow_start` already claims the task (→ ACTIVE, live lease,
  `claimed_by = worker`) and writes the manifest — exactly the preconditions
  `record_run_session_link` needs (§2). Adding `--session-id S --adapter hcom`
  and recording the link when both are supplied is mechanically trivial.
- **Invariant risk:** **real.** `flow_start`'s stated contract is "stops before
  choosing or launching a provider session" and returns
  `next_step.state == "STOPPED_BEFORE_PROVIDER_SESSION"`. Recording a binding to
  an *already-existing* session the caller names is not *launching* one — but it
  does move the session identity into `flow_start`'s surface, which several
  tests and the roadmap treat as a bright line. A reviewer would reasonably
  push back.
- **Authority:** none added (same `--worker-id` / `--created-by` as today).
- **Verdict:** workable but blurs a deliberate boundary; not recommended as the
  primary site.

### (b) A new explicit `maps run bind-session TASK RUN --session S --adapter hcom --worker W` verb — **RECOMMENDED**

- **Fit:** exact. It is a single-purpose, thin wrapper over
  `store.record_run_session_link(run_id, worker_id, adapter_id=..., session_id=...,
  evidence_ref=..., created_by=...)` — the same shape as `maps operator add`
  over `record_authorized_operator`, or `maps skill approve` over
  `record_skill_lifecycle_transition`. The store method is **fully standalone**
  (§2) — no `HarnessService`, no adapter, no launch.
- **Invariant risk:** **none.** `flow_start`'s contract is untouched. The new
  verb is explicitly "I already have session S running for run R; record the
  durable binding" — it is evidence recording, not orchestration.
- **Authority:** none added (§4).
- **Matches the lineage model's intent** precisely: `RunSessionLineageMixin`'s
  own docstring — "records identify provider sessions for an immutable run;
  they do not grant task authority and do not represent provider
  liveness/readiness." A standalone verb *is* that: an identity record.
- **Verdict:** **recommended.** Smallest surface, breaks nothing, one new
  thin CLI verb + dispatch.

### (c) `maps claim` when a session is known

- **Fit:** poor. `claim` has no session parameter and is *also* the recovery /
  claim-recovery path (§5, `docs/CONTROL_PLANE_SETUP.md` §5). Threading a
  session through it conflates a durable-identity write with the
  ownership/lease mutation and with recovery. `claim`'s recovery path
  additionally runs under the *original* worker with a possibly-expired lease —
  the wrong context for `record_run_session_link`'s `RUN_NOT_OWNED` / live-lease
  preconditions.
- **Verdict:** rejected.

---

## 2. What `record_run_session_link` requires (verified)

`runtime/state/run_lineage.py::RunSessionLineageMixin.record_run_session_link(
run_id, worker_id, *, adapter_id, session_id, evidence_ref, created_by,
replaces_link_id=None, now=None) -> MutationResult`.

**Standalone — a direct guarded store write. It does not import, construct, or
call `HarnessService` or any adapter.** It is a `TaskStore` mixin method like
every other lineage writer.

Validation / preconditions for the **first (ATTACH)** link, in order:

| Check | Failure code |
|---|---|
| `run_id` / `adapter_id` / `session_id` match `_ID_RE` (`^[A-Za-z0-9][\w.:@-]{0,127}$`); `evidence_ref` matches `_REF_RE`; `created_by` non-empty ≤128, no control chars; `worker_id` non-empty | `INVALID_SESSION_LINK` |
| `run_manifests` row for `run_id` exists | `RUN_NOT_FOUND` |
| `manifest.worker_id == worker_id` (the **immutable** run worker) | `RUN_WORKER_MISMATCH` |
| run's task exists; `task.project_id` non-empty | `TASK_NOT_FOUND` / `PROJECT_CONTEXT_UNAVAILABLE` |
| `task.status == "ACTIVE"` **and** `task.claimed_by == worker_id` | `RUN_NOT_OWNED` |
| `task.lease_expires_at` is in the future | `LEASE_EXPIRED` |
| `compute_task_revision(task) == manifest.task_revision` (not stale) | `RUN_STALE` |
| existing lineage not already `INVALID` | `SESSION_LINEAGE_INVALID` |
| `(project_id, adapter_id, session_id)` not already bound to **any** run (schema `UNIQUE`) | `SESSION_ALREADY_BOUND` |
| first link: `replaces_link_id` must be `None` | `UNEXPECTED_REPLACEMENT_LINK` |
| first link: if `manifest.session_id` (legacy) is set it must equal `session_id` | `MANIFEST_SESSION_CONFLICT` |

On success → inserts `relation='ATTACH', replaces_link_id=NULL`. Table is
append-only (schema: no delete/update path; a later session change is a
`relation='REPLACE'` row naming the current link via `replaces_link_id`).

**Key point:** every precondition is state the run's own live claimant already
holds right after `maps flow start` (manifest bound, task ACTIVE, claimed by
`W`, lease live, revision current). So the new verb needs the caller to supply
only: `run_id`, `worker_id` (= manifest worker), `session_id`, `adapter_id`
(`hcom`), and an `evidence_ref` + `created_by`. Nothing adapter-derived.

The chain-validity rules in `_resolve_run_session_conn` (`root_count`, `branch`,
`cycle`, `disconnected_links`, `predecessor_outside_run`,
`project_context_mismatch`) only bite on **subsequent** links; the first ATTACH
row cannot trip them.

---

## 3. The minimal change

**New file:** none required (a `_dispatch_run` helper can live in `cli.py`
alongside `_dispatch_skill` / `_dispatch_operator`).

**`runtime/cli.py`** (the only file):
- add `run = sub.add_parser('run', ...)` with a `bind-session` subcommand:
  `maps run bind-session <run_id> --worker-id W --session-id S
  [--adapter hcom] --evidence-ref R [--created-by C]`.
  - `--adapter` defaults to `hcom` (the only adapter; the guard also hard-codes
    `adapter_id == "hcom"` in `_resolve_harness_binding`).
  - `--evidence-ref` required (the store requires a non-empty ref; e.g.
    `hcom:attach:<session>` mirroring `HcomHarnessAdapter`'s own
    `f"harness:attach:{...}"`).
  - `--created-by` defaults to something like `maps-run-bind-session`.
- dispatch: `_emit(store.record_run_session_link(args.run_id, args.worker_id,
  adapter_id=args.adapter, session_id=args.session_id,
  evidence_ref=args.evidence_ref, created_by=args.created_by))`.

**Does it touch `HarnessService` / the adapter?** **No.** Direct
`store.record_run_session_link(...)` — same pattern as `maps operator` /
`maps skill`. `HarnessService` and `HcomHarnessAdapter` are untouched.

**What the caller must supply:** the `run_id` from the `maps flow start` output
(`run_manifest.run_id`), the same `--worker-id` used for `flow start`, and the
provider session's **`session_id`** — note this is hcom's own `session_id`
field, *not* the display `name` used in `--binding W=S` for `recovery-tick`
(`supervisor._resolve_run_id` docstring is explicit about the distinction). The
impl should document that clearly and the `recovery-tick --binding` value must
still be the display name; the two identifiers must both point at the same
session.

**Optional convenience (evaluate in impl, not required):** `maps flow start`
could gain an optional `--session-id`/`--adapter` pair that, *when both are
supplied*, calls `record_run_session_link` after the manifest — candidate (a).
Recommend deferring this to keep `flow_start`'s contract clean; the standalone
verb is the load-bearing piece.

### Tests (impl slice)
- `tests/test_cli_run.py` (new) or extend an existing CLI test module:
  bind-session round-trip → `resolve_run_session(run_id)["state"] == "EXPLICIT"`;
  each store failure code surfaced (`RUN_NOT_FOUND`, `RUN_WORKER_MISMATCH`,
  `RUN_NOT_OWNED`, `LEASE_EXPIRED`, `SESSION_ALREADY_BOUND`,
  `MANIFEST_SESSION_CONFLICT`); `--adapter` non-hcom accepted by the store but
  flagged as non-routable by the guard (document, don't block).
- An integration-style test: `flow start` → `run bind-session` →
  `resolve_run_session` EXPLICIT → a constructed `_resolve_harness_binding`
  returns a binding (mirrors `tests/test_recovery_supervisor.py` composition).
- ≥5 mutations on the dispatch + arg wiring.

---

## 4. Does this expand any authority surface? — NO

`record_run_session_link` **self-gates to the run's live ACTIVE claimant**:
`RUN_NOT_OWNED` unless `task.status == "ACTIVE" and task.claimed_by ==
worker_id`, plus a live-lease check. So the only party who can write the first
link is the worker currently running the task — acting on *their own* run. This
is the **same authority level as `maps heartbeat` / `maps submit`** (the
claimant operating on their own claim) and **strictly narrower than
`maps flow start` / `create_run_manifest`**, which take an arbitrary
`--worker-id` + `--created-by` with no claimant check at all.

The lineage records "do not grant task authority" (mixin docstring) — they are
identity evidence. Recording one is not operator-gated, is not a scope change,
and does not touch review/approval/destructive-action authority.

**No operator decision.** (Contrast: the #255 §8 decision — *whether* to do
this wiring at all vs. accept a 0-denial pass — is the operator's call, per
#255. *This* note assumes that call is "do the wiring" and scopes only the how.)

---

## 5. After the wiring — what the first enforced pass actually does (traced)

Setup the coordinator performs:
```
maps flow start T --worker-id W --repo-root PATH [--require-canonical-run]
  → manifest M created, task T ACTIVE, claimed_by=W, lease live
maps run bind-session <M.run_id> --worker-id W --session-id S --adapter hcom \
  --evidence-ref hcom:attach:S
  → run_session_links ATTACH row; resolve_run_session(M.run_id).state == EXPLICIT
[ session S then silently stops ]
maps recovery-tick --enforce-canonical-run --harness-project-id P \
  --repo-root PATH --binding W=<session display name>
```

Trace:
- `observe_silent_stops({W: name})` → detects W has one ACTIVE task + a stopped
  session → opens an incident. `_resolve_run_id(task, session)` →
  `resolve_session_run(P, "hcom", S)` → **finds M.run_id** (the ATTACH row).
  Incident now carries `run_id = M.run_id`.
- `tick()` → `_resolve_harness_binding(incident, name)`:
  `run_id` set ✓; `compute_task_revision(T)` + `task.project_id == P` non-empty
  ✓; `resolve_run_session(M.run_id).state == "EXPLICIT"` ✓;
  `current.adapter_id == "hcom"`, `current.session_id == S` ✓ →
  **returns `(ExecutionBinding, SessionRef)`.** ROUTABLE.
- `harness_service.resume(binding, session_ref)` → `HarnessService` fires
  `BEFORE_RESUME` → `CanonicalRunGuard.__call__({operation:"resume",
  binding:{task_id,run_id,worker_id,task_revision,project_id},
  session_ref:{session_id,adapter,project_id}, adapter_id:"hcom"})`.
- Guard evaluates (order per `harness_guard.py`): binding complete ✓; task
  exists, `project_id == P` ✓; manifest exists, task/worker/revision match ✓;
  `require_current_revision` (continuing): `compute_task_revision == binding
  revision` ✓ (fresh); then **`_require_live_claim`**:
  - `task.status == "ACTIVE"`? — a silently-stopped session's **lease has
    typically lapsed**, and the recovery loop has not re-claimed → the task may
    still read ACTIVE but the **lease is expired** → **`LEASE_EXPIRED` DENY.**
  - (If the lease somehow still lives: `_require_current_run` →
    `check_run_stale` (context-ref sha / revision) → possible `RUN_STALE`;
    `_require_bound_worktree` → if M is worktree-bound and recovery runs from a
    different worktree → **`RUN_WORKTREE_MISMATCH` DENY**; else
    `_require_durable_session` against the lineage just written → passes → guard
    returns `ANNOTATE` / `CANONICAL_RUN_VERIFIED` and the resume proceeds.)
- A `DENY` → `HarnessService.resume()` returns code `HOOK_DENIED` → supervisor
  (`_CANONICAL_DENIAL_CODES`): `action = "resume_denied"`, incident
  `state = "denied"`, `last_error = "Continuing execution requires a live task
  lease."`, `canonical_denials = 1`, **transient `attempt` untouched**, flat
  reschedule. Third consecutive denial → `failed` /
  `canonical_denial_persistent`.

**This is the Ask #1 outcome the operator meant.** Remediation (unchanged, §255
§4 / `CONTROL_PLANE_SETUP.md` §5): `maps claim T --worker-id W
--lease-seconds N` (re-acquire under the **original** worker) → re-tick → now
`_require_live_claim` passes → guard proceeds → `ANNOTATE` → resume succeeds
(or a further, real, denial like `RUN_WORKTREE_MISMATCH` surfaces and is
remediated in turn).

Denials reachable on the first exercised pass: **`LEASE_EXPIRED`** (dominant),
`RUN_WORKTREE_MISMATCH` (if `--require-canonical-run` bound a worktree and
recovery runs elsewhere), `RUN_STALE` (a recorded context-ref file changed),
`TASK_REVISION_STALE` (task definition edited after the run).

---

## 6. Which of 6.16 / H5 / 6.22 does wiring + a pass let flip, and what remains

| Row | Exit criterion (from the checklist row) | Wiring + an exercised pass delivers | Flip? | What still remains |
|---|---|---|---|---|
| **H5** | "closes only after the first real production exposure of an enforced pass (which converts currently-working resumes into `resume_denied`)"; design §5 Q4/Q5 must be settled (they are — `denied` state + `CONTROL_PLANE_SETUP.md` §5) | a real `resume_denied` (`LEASE_EXPIRED`) on a routed incident, remediated per §5 — **the exposure happens** | **YES** — with a documented pass + remediation. The "remaining adapters" half (ollama/aider) is already recorded as deliberately out of scope in the row. | nothing blocking, once the pass is run and documented |
| **6.16 / E6(b)** | "first real production exposure of the enforced composition on the RnS `recovery-tick` path"; the worktree-binding seam (`_require_bound_worktree`) exercised | `CanonicalRunGuard.__call__` runs on a routed incident; if the exercised run is **worktree-bound** (`flow start --require-canonical-run`) the pass exercises `_require_bound_worktree` (pass-through or `RUN_WORKTREE_MISMATCH`) | **YES** — provided the documented exercise uses a `--require-canonical-run` run so the worktree branch actually executes | nothing blocking; the exercise must include a worktree-bound run |
| **6.22** | "a real `send()` caller denied on a `WITHHOLD` item" — `MemoryProvenanceGuard` on `BEFORE_SEND` | **nothing** — the RnS recovery path calls only `HarnessService.resume()`, **never `.send()`** (verified: `supervisor.py:538` is the only `harness_service.` call; grep for `HarnessService.send` production callers → none). `MemoryProvenanceGuard` is instantiated in the composition but its `BEFORE_SEND` callback is never fired by any pass. | **NO** | 6.22 needs a **separate** wiring: a production `HarnessService.send()` caller (an orchestrator dispatch that emits a `memory_provenance`-annotated payload). The checklist row already says this ("`HarnessService.send()` has no production caller … no real payload assembler emits `memory_provenance` yet"). This lineage wiring does not touch it. |

**Net:** the wiring + one documented exercised pass **flips H5 and 6.16/E6(b)**
(each also needs the pass actually run — a separate execution step, not this
scoping note). It **does not** advance 6.22, which is a distinct `send()`-path
wiring problem.

---

## 7. STOP-check (trajectory playbook)

- **Is the increment blocked on a retrieval mechanism / larger design?** No.
  `record_run_session_link` already exists, is fully guarded, and is a direct
  store write. The change is one thin CLI verb.
- **Does it need an operator decision?** No (§4) — a claimant-scoped identity
  write, narrower than manifest creation. (The prior decision — *whether* to do
  this wiring vs. accept a 0-denial pass — is the operator's, per #255 §8, and
  is assumed answered "do it" here.)
- **Does it break an invariant?** No, with candidate (b). Candidate (a)
  (folding it into `flow start`) would brush the "stops before provider
  session" line — which is why (b) is recommended.
- **Is there hidden scope?** One: the `session_id` (hcom identifier) vs
  `session_name` (display) distinction between `run bind-session` and
  `recovery-tick --binding` — an impl caution, not a blocker (§3).
- **Conclusion:** **SCOPE-FOR-IMPL**, no PARK, no operator gate.

---

## The impl slice — MAY / MUST-NOT / acceptance

### MAY touch
- `runtime/cli.py` — new `run` subparser + `bind-session` subcommand + a
  `_dispatch_run` helper; dispatch calls `store.record_run_session_link(...)`
  directly.
- `tests/test_cli_run.py` (new) — round-trip + each failure code + an
  integration test through `resolve_run_session` / a constructed
  `_resolve_harness_binding`.
- `work/roadmaps/CAPABILITY_CHECKLIST.md` — H5 / 6.16 evidence text **only if**
  the impl PR also runs and documents the first exercised pass; otherwise leave
  the rows for the follow-up execution step. **No STATUS flip in the wiring PR
  itself** (the flip is the reviewer gate step after the pass is run).

### MUST NOT
- Touch `runtime/harness/` (`HarnessService`, `HcomHarnessAdapter`) or
  `runtime/recovery/`.
- Add a parameter to `record_run_session_link` or change its guard logic.
- Fold session recording into `maps flow start` as the *primary* mechanism
  (optional `--session-id` convenience only, and only if the reviewer agrees it
  doesn't breach the stop-before-session contract).
- Add any authority gate, `--enforce-*` flag, or operator check to the new verb.
- Run any `--enforce-canonical-run` pass as part of the wiring PR (that is the
  separate execution + gate step).
- Flip any checklist STATUS.

### Acceptance
1. `maps run bind-session <run_id> --worker-id W --session-id S --evidence-ref R`
   after `maps flow start` makes `resolve_run_session(run_id)["state"] ==
   "EXPLICIT"`.
2. Every `record_run_session_link` failure code is surfaced with a non-zero
   exit and the store's message.
3. `python3 -m unittest tests.test_cli_run tests.test_run_lineage
   tests.test_recovery_supervisor` foreground green; `python3 -m runtime.smoke`
   exit 0. Full `tests/` → CI.
4. ≥5 mutations on the dispatch + arg wiring.
5. Independent review; PR into `main`; coordinator merge-prep; no self-merge.

---

## Resume prompt

You are implementing the **lineage-bootstrap wiring** for MAPS_Lean. Source:
this note + `work/notes/2026-09-02-ask1-control-plane-runbook.md` §8 +
trajectory check #18 (#256). The operator has decided the wiring should be done
(#255 §8 decision); no further operator input is needed.

Add a **`maps run bind-session <run_id> --worker-id W --session-id S
[--adapter hcom] --evidence-ref R [--created-by C]`** CLI verb in
`runtime/cli.py` (new `run` subparser + `_dispatch_run` helper, mirroring
`_dispatch_operator` / `_dispatch_skill`). Dispatch calls
`store.record_run_session_link(run_id, worker_id, adapter_id=adapter,
session_id=session_id, evidence_ref=evidence_ref, created_by=created_by)`
**directly** — do not touch `runtime/harness/` or `runtime/recovery/`, do not
change the store method. `--adapter` defaults to `hcom`; `--evidence-ref` is
required (store rejects an empty ref); `--created-by` defaults to
`maps-run-bind-session`.

The store method self-gates to the run's live ACTIVE claimant, so no authority
gate is added. Document in `--help` / the note that `--session-id` is hcom's
own `session_id` (not the display name used by `recovery-tick --binding`).

Tests: `tests/test_cli_run.py` — round-trip → `resolve_run_session` EXPLICIT;
each failure code (`RUN_NOT_FOUND` / `RUN_WORKER_MISMATCH` / `RUN_NOT_OWNED` /
`LEASE_EXPIRED` / `SESSION_ALREADY_BOUND` / `MANIFEST_SESSION_CONFLICT`); an
integration test `flow start` → `run bind-session` → a constructed
`_resolve_harness_binding` returns a binding (mirror
`tests/test_recovery_supervisor.py` composition). ≥5 mutations.

**No `--enforce-canonical-run` pass in this PR** — that is the separate
execution + reviewer gate step that then flips H5 and 6.16/E6(b). **No STATUS
flip.** Verify targeted modules foreground + `python3 -m runtime.smoke` (exit
0); full suite to CI. New worktree off `origin/main`; PR into `main`;
independent reviewer; ping the coordinator; no self-merge.
