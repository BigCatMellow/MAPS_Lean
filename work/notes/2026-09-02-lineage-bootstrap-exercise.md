# Lineage-bootstrap exercise — `maps run bind-session` on a fresh `.maps/`

**Executed 2026-09-02 by `maps-lean-nava`** at `~/Projects/MAPS_Lean`, `origin/main`
`3a4b3a4` (post #258/#259/#260). Dispatched by coordinator `mika` (hcom #82729).

**Scope actually run:** `maps init` → `maps create/shape/promote` → `maps flow start`
→ **`maps run bind-session`** → read-only verification → `runtime.smoke`.
**NOT run:** any `--enforce-canonical-run` / `--enforce-*` pass (operator-gated,
decision batch item 5, UNANSWERED). No `runtime/` change. No `CAPABILITY_CHECKLIST.md`
status change.

**Result: PASS.** `maps run bind-session` wrote the first `run_session_links`
`ATTACH` row on a freshly created `.maps/`; both the reverse lookup
(`resolve_session_run`) and the forward lineage state (`resolve_run_session` →
`EXPLICIT`) resolve. This is the concrete confirmation that the lineage-bootstrap
deadlock the #257 scoping note traced is now broken by a real production CLI path.

---

## 1. Exact commands + output

All commands run from `~/Projects/MAPS_Lean` with `export HCOM_DIR="$PWD/.hcom"`.
`--db .maps/state/maps.db` is the default; shown explicitly for the record.

### 1.1 Establish the control plane

```
$ python3 -m runtime.cli --db .maps/state/maps.db init
{"ok": true, "db": ".maps/state/maps.db",
 "settings": {"busy_timeout": 5000, "foreign_keys": 1, "journal_mode": "wal"}}
```

`CONTROL_PLANE_SETUP.md` §2 "Connection defaults" (`foreign_keys=ON`,
`journal_mode=WAL`, `busy_timeout=5000`) are applied by the runtime
(`BaseStore._connect`) — confirmed in the `settings` payload, no manual `PRAGMA`
step. `.maps/state/` is created by the runtime; `.gitignore:10` `/.maps/state/`
keeps all of it out of Git.

```
$ python3 -m runtime.cli --db .maps/state/maps.db status
{"tasks": {"total": 0, "by_status": {"ACTIVE": 0, ...}}, "active": [], "recent": [],
 "coverage": {"canonical_task_db": true, "recovery_state": false,
              "communication_hcom": false, "helper_run_state": false}}
```

Empty store, as expected on a fresh DB. `PRAGMA integrity_check` was requested via
the `sqlite3` CLI, which is **not installed on this host**; substituted with a
Python check — see §2. (Runbook §1 lists `sqlite3` as "useful but not required by
the Python runtime.")

### 1.2 Seed a run to bind (a real run manifest is a `bind-session` precondition)

`maps run bind-session`'s store method (`record_run_session_link`, verified in the
#258 review) requires an existing `run_manifests` row whose `worker_id` matches,
whose task is `ACTIVE` and claimed by that worker, with a live lease and a
current revision. `maps flow start` is the production path that produces exactly
that state (it claims the task + writes the immutable manifest, then stops).

```
$ python3 -m runtime.cli --db .maps/state/maps.db create \
    --task-id LBW-EXERCISE-1 --project-id maps-lean --title "Lineage-bootstrap exercise"
{"ok": true, "code": "CREATED", "task": {"status": "NEEDS_SHAPING", ...}}

$ python3 -m runtime.cli --db .maps/state/maps.db shape LBW-EXERCISE-1 \
    --contract-json <contract.json>          # full AGI-ready contract, output_paths=["work/notes"]
{"ok": true, "code": "UPDATED", ...}

$ python3 -m runtime.cli --db .maps/state/maps.db promote LBW-EXERCISE-1 --actor maps-lean-nava
{"ok": true, "code": "READY", "task": {"status": "READY", "agi_status": "AGI READY", ...}}

$ python3 -m runtime.cli --db .maps/state/maps.db flow start LBW-EXERCISE-1 \
    --worker-id nava-worker-1 --repo-root "$PWD"
{"ok": true,
 "claim": {"code": "CLAIMED", "task": {"status": "ACTIVE", "claimed_by": "nava-worker-1",
           "attempt": 1, "lease_expires_at": "2026-09-02T15:36:48Z"}},
 "run_manifest": {"run_id": "RUN-6d536476052a4633af0d5679af0eb22d",
                  "worker_id": "nava-worker-1", "task_revision": "9b6e2467fdaeba55...",
                  "session_id": null, "worktree": null,
                  "writable_scope": ["work/notes"], "readable_scope": ["."]},
 "next_step": {"state": "STOPPED_BEFORE_PROVIDER_SESSION",
               "reason": "flow start does not select workers, launch providers, attach sessions, or send messages"}}
```

Note `run_manifest.session_id: null` and `next_step.state ==
STOPPED_BEFORE_PROVIDER_SESSION` — `flow start` writes **no** `run_session_links`
row. This is precisely the deadlock premise from #257 §3: the only pre-#258
writer of that table sat inside `HarnessService`, reachable only *after* the
supervisor's `EXPLICIT` pre-check already passed.

### 1.3 The exercise — `maps run bind-session`

```
$ python3 -m runtime.cli --db .maps/state/maps.db run bind-session \
    RUN-6d536476052a4633af0d5679af0eb22d \
    --worker-id nava-worker-1 \
    --session-id hcom-sess-nava-lbw-1 \
    --adapter hcom \
    --evidence-ref hcom:attach:hcom-sess-nava-lbw-1
{"ok": true, "code": "SESSION_ATTACHED", "message": "recorded run/session lineage link 1",
 "task": {"state": "EXPLICIT", "chain_complete": true, "project_id": "maps-lean",
          "run_id": "RUN-6d536476052a4633af0d5679af0eb22d",
          "legacy_manifest_session_id": null,
          "current": {"link_id": 1, "relation": "ATTACH", "replaces_link_id": null,
                      "adapter_id": "hcom", "session_id": "hcom-sess-nava-lbw-1",
                      "project_id": "maps-lean", "created_by": "maps-run-bind-session",
                      "evidence_ref": "hcom:attach:hcom-sess-nava-lbw-1",
                      "created_at": "2026-09-02T15:21:57Z"},
          "history": [ <the same single ATTACH link> ]}}
```

Exit code `0`. No `--session-id` vs `--session-name` confusion: `--session-id` is
the adapter identifier (here a synthetic `hcom-sess-nava-lbw-1`); the
`recovery-tick --binding W=<name>` display name is a separate identifier and was
not needed for this step.

---

## 2. Verification (PASS/FAIL: is the ATTACH row written and do both lookups resolve?)

`sqlite3` CLI is absent on this host; all inspection via the Python store /
`sqlite3` module (same DB file).

### 2.1 The `run_session_links` row exists

```
$ python3 -c "import sqlite3,json; c=sqlite3.connect('.maps/state/maps.db'); \
    c.row_factory=sqlite3.Row; \
    print(json.dumps([dict(r) for r in c.execute('SELECT * FROM run_session_links')], indent=2))"
[
  {"id": 1, "run_id": "RUN-6d536476052a4633af0d5679af0eb22d", "relation": "ATTACH",
   "project_id": "maps-lean", "adapter_id": "hcom", "session_id": "hcom-sess-nava-lbw-1",
   "replaces_link_id": null, "evidence_ref": "hcom:attach:hcom-sess-nava-lbw-1",
   "created_by": "maps-run-bind-session", "created_at": "2026-09-02T15:21:57Z"}
]
```

One row. `relation = ATTACH`, `replaces_link_id = NULL` — the first link in the
chain.

### 2.2 Both lineage-resolution paths resolve

```
$ python3 -c "from runtime.state import TaskStore; s=TaskStore('.maps/state/maps.db'); \
    run='RUN-6d536476052a4633af0d5679af0eb22d'; \
    rs=s.resolve_run_session(run); \
    print('resolve_run_session.state =', rs['state']); \
    print('reverse:', s.resolve_session_run('maps-lean','hcom','hcom-sess-nava-lbw-1')); \
    print('unknown session:', s.resolve_session_run('maps-lean','hcom','no-such'))"
resolve_run_session.state = EXPLICIT
reverse: RUN-6d536476052a4633af0d5679af0eb22d
unknown session: None
```

- **Forward** (`resolve_run_session(run_id)`): `state == "EXPLICIT"`,
  `current.adapter_id == "hcom"`, `current.session_id == "hcom-sess-nava-lbw-1"`.
- **Reverse** (`resolve_session_run(project, adapter, session_id)`): returns the
  exact `run_id`; an unknown session returns `None` (non-heuristic, per the
  method's docstring — it never guesses among candidates).

### 2.3 Every `_resolve_harness_binding` precondition is now satisfied

`RecoverySupervisor._resolve_harness_binding` (supervisor.py:208, the gate that
decides whether a resume is routed through the guarded `HarnessService`) checks,
for a given incident:

| Precondition | Value after this exercise |
|---|---|
| `incident["run_id"]` resolvable via `resolve_session_run` | `RUN-6d53…` (§2.2 reverse lookup) |
| `compute_task_revision(task_id)` non-empty | `9b6e2467fdaeba55…` |
| `task.project_id` non-empty | `maps-lean` |
| `resolve_run_session(run_id)["state"] == "EXPLICIT"` | **True** |
| `current.adapter_id == "hcom"` | **True** |
| `current.session_id` non-empty | `hcom-sess-nava-lbw-1` |

Before `bind-session` (immediately after `flow start`) the `EXPLICIT` check would
have failed (`state` would be `UNBOUND` — a manifest with no session links), so
`_resolve_harness_binding` would return `(None, None, "session_not_durably_bound")`
and any enforced pass would fall through to a direct resume with **no guard call**
— the deadlock. After `bind-session`, a routable binding is constructible.

**This was verified by reading the resolved state, not by running the supervisor
or any `--enforce-*` pass.**

### 2.4 `runtime.smoke`

```
$ python3 -m runtime.smoke
... "ok": true    (exit 0)
```

### 2.5 Nothing tracked changed; state is fully local

```
$ ls .maps/state/
maps.db                       # only file — no recovery.json (no tick ran), no langgraph db

$ git status --porcelain      # (at repo root, before the note worktree)
                              # empty — .maps/ is gitignored
```

Reversible per runbook §5: `rm -rf .maps/` is a full reset.

---

## 3. Which of H5 / 6.16(E6b) / 6.22 does this exercise advance?

**It advances the shared *precondition* for H5, 6.16/E6(b), and 6.22 — a
production path can now write the first `run_session_links` row, so a run can
reach `EXPLICIT` lineage and become routable. It flips NONE of them**, because
every one of those rows' exit criteria requires the `--enforce-canonical-run`
pass to actually be *run* (operator-gated, batch item 5 unanswered), and this
exercise deliberately did not run it.

Verified against each row's unmet conditions (runbook §6 + `CAPABILITY_CHECKLIST.md`
at `3a4b3a4`):

| Row | Exit criterion | State after this exercise | Still unmet |
|---|---|---|---|
| **H5** — Remaining adapters + contract suite | "closes only after the first real production exposure of an enforced pass (which converts currently-working resumes into `resume_denied`)" | A routable binding is now *constructible* (§2.3), so a subsequent enforced pass **could** reach `CanonicalRunGuard.__call__` and — against this run, whose lease expires 15:36:48Z — produce a real `LEASE_EXPIRED` → `resume_denied`. The pass itself has not been run. | (1) the enforced pass run + documented; (2) the "remaining adapters" half (ollama/aider contract conformance) is separately recorded as out of scope in the row. |
| **6.16 / E6(b)** — Git worktree isolation | "first real production exposure of the enforced composition on the RnS `recovery-tick` path"; the `_require_bound_worktree` seam exercised | Composition still not instantiated in an enforced pass. This run's manifest was created **without** `--require-canonical-run`, so `worktree: null` — even a future pass on *this* run would not exercise `_require_bound_worktree`. | (1) the enforced pass run; (2) a `--require-canonical-run` (worktree-bound) run so the worktree branch actually executes. |
| **6.22** — Memory trust classes (`MemoryProvenanceGuard` first exposure) | "a real `send()` caller denied on a `WITHHOLD` item" | **No change.** The RnS recovery path calls `HarnessService.resume()` only, never `.send()`; `bind-session` touches neither. `MemoryProvenanceGuard`'s `BEFORE_SEND` callback is unreachable from `recovery-tick`. | A distinct wiring problem: a production `HarnessService.send()` caller emitting a `memory_provenance`-annotated payload. This exercise is orthogonal. |

**Net:** the deadlock #257 identified is broken. The path to H5 and 6.16/E6(b)
is now: operator answers batch item 5 → run the documented `--enforce-canonical-run`
pass (for 6.16, with a `--require-canonical-run` run) → the reviewer gate step
re-runs and *then* decides any status flip. 6.22 is not on this path.

---

## 4. Boundaries honoured

- No `--enforce-canonical-run` / `--enforce-validation` / any `--enforce-*` run.
- No `runtime/` change. No schema change (`maps init` is `CREATE TABLE IF NOT
  EXISTS` only).
- No `CAPABILITY_CHECKLIST.md` status flip (this note carries no checklist edit;
  a separate follow-up PR adds evidence prose only).
- `.maps/` is gitignored, local, disposable (`rm -rf .maps/` resets it).
- `bind-session` behaved exactly as #257 §2 predicted on a fresh DB — no
  surprise, no `#258` patch needed.

---

## 5. STOP conditions — none hit

- `bind-session` did **not** error on the fresh DB in any way #257 did not
  predict — `SESSION_ATTACHED` on the first call, `EXPLICIT` lineage, clean chain.
- The exercise did **not** need an `--enforce-*` pass to demonstrate value: the
  ATTACH row + both resolution paths + the `_resolve_harness_binding`
  precondition table (§2.3) are the deliverable, and none of that requires the
  enforced pass. (The enforced pass remains the operator-gated next step for the
  H5 / 6.16 status question.)

---

## Resume prompt

You are picking up after the lineage-bootstrap exercise (this note). The
`.maps/` control plane exists at `~/Projects/MAPS_Lean` with one bound run
(`RUN-6d536476052a4633af0d5679af0eb22d`, task `LBW-EXERCISE-1`, session
`hcom-sess-nava-lbw-1`, lineage `EXPLICIT`). `maps run bind-session` (#258) is
proven working.

Next, **only if the operator has answered decision-batch item 5** (Ask #1
`--enforce-canonical-run` go + timing): run the documented enforced pass per
`work/notes/2026-09-02-ask1-control-plane-runbook.md` §9, against a
`--require-canonical-run` run so the 6.16 worktree seam is exercised, capture the
`resume_denied` (expect `LEASE_EXPIRED`) + remediate per runbook §4, then hand
the result to a reviewer gate step for the H5 / 6.16 status decision. Do **not**
run the enforced pass without that operator answer. Do not flip any checklist
status yourself.

Also pending: a separate PR adding evidence-prose (no status flip) to the H5 /
6.16 / 6.22 rows citing this exercise.
