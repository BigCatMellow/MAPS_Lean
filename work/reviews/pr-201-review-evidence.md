# PR #201 — 6.24 environment-report production source & cache design note — independent review evidence

reviewer: maps-lean-vara
head_sha: 244765a90fe3d25a506e225d2e3005d099b5f632
independent: true
verdict: PASS (APPROVE)
summary: All 6 dispatch questions are answered. Every load-bearing existence claim verified by direct read at `fae8251` — the E3 recorder and its table exist with zero production writers, E2 `inspect_local_environment` exists as a pure containment-checked function, and all three `task_environment` columns + the `run_manifests.task_id` join path exist, so the cache and HOLD rule need no schema change as claimed. The "source = a flow_start step wiring two existing pure functions" judgment is sound — not a new subsystem. Deferred items (task-scoped evidence table, strict-DRIFTED flag) are correctly walled off as their own authorised schema-change steps. Diff in-bounds: note + one 6.24 evidence annotation, no status flip. 4 non-blocking observations for the impl PR. Not the author (muzi).

## Method

Reviewer's own detached worktree at PR #201 head `244765a`, on `fae8251` (= `origin/main`). `git fetch origin main` first; every callsite / column claim re-derived with `/usr/bin/grep` + `sed` (rule 14). Sources of truth: `work/notes/2026-08-21-routing-environment-report-sourcing-design.md` (prior boundary), `runtime/routing/environment_reports.py`, `runtime/routing/router.py`, `runtime/policy/evaluator.py`, `runtime/flow_start.py`, `runtime/state/environment.py`, `runtime/environment/safety.py`, `runtime/state/schema.sql`, checklist rows 6.24 / E1–E3. Design review only, no mutation testing (docs-only note).

## 1. Diff in bounds

`git diff fae8251...244765a --stat` — 2 files:

| File | Content |
|---|---|
| `work/notes/2026-08-31-environment-report-production-source-cache-design.md` (+377) | the design note |
| `work/roadmaps/CAPABILITY_CHECKLIST.md` (+1/-1) | 6.24 row — appends "Production source/cache design pending: …" to the evidence text; **`| IN PROGRESS |` unchanged** |

No `runtime/`, no `schema.sql`, no tests, no other checklist row. `git diff --check` clean.

## 2. Six questions — all answered

| Q | Answer in note | Verdict |
|---|---|---|
| Q1 production source | a **step 4 in `flow_start()`** (only when `task["environment"]` is set): `load_environment_spec` → `inspect_local_environment` → `record_run_environment_evidence(run_id, …)` | sound — see §3 |
| Q2 cache | rides the existing tables — `run_environment_evidence` (run-scoped, insert-only) + `task_environment.max_age_seconds` TTL + `run_manifests.task_id` join; a **read-side projection**, no new table, no in-memory cache (rule 12) | verified — see §4 |
| Q3 default required-for-routing rule | the **existing `required_for_routing` column**, per-task, operator-authored, **default-off**; `=1` → routing **holds** (`environment_report_required`) when no fresh report; a hold, not a hard reject — clears on the task's next flow-start | sound — see §6 |
| Q4 DRIFTED / UNKNOWN | unchanged — only `INCOMPATIBLE` gates; a fresh `DRIFTED`/`UNKNOWN` report **satisfies** the required-for-routing bar ("a fresh report exists"); making `DRIFTED` itself gate is a deferred `strict_environment` column | sound; orthogonality (missing-report rule vs content rule) stated plainly |
| Q5 second scope dimension | **environment compatibility**, production-sourced; concrete 3-step proof artifact (held → routes on COMPATIBLE → rejected on INCOMPATIBLE) exercising identity ∩ environment | sound — the axis already exists in `evaluate_assignment`/`router`, slice 1 makes it real in production |
| Q6 smallest slice + STOP + MUST-NOT | 5-item slice (flow-start step 4; `select_recorded_environment_reports`; `maps route --environment-reports-from-recorded` default-off; the hold; checklist text) + 8 MUST-NOTs + 3 STOP conditions | complete; STOP conditions appropriately conservative |

## 3. "Not a new subsystem" — JUDGMENT: SOUND

The production source is `flow_start` composing two functions that **already exist and are already pure**:

- **`runtime/environment/safety.py:139` `inspect_local_environment(spec, *, repo_root, …) -> EnvironmentFingerprint`** — docstring "Collect a local fingerprint **without following dependency inputs outside the repo**"; it calls `_validate_dependency_containment` first, and the underlying inspector's docstring says "**Setup/validation commands are never executed here**". So the three things the dispatch STOP condition names (network calls, following deps outside the repo, executing spec commands) are **structurally prevented** by the function the note picks. Wiring it adds no probing capability.
- **`runtime/state/environment.py:44` `record_run_environment_evidence(run_id, *, spec, fingerprint, spec_ref, recorded_by, reference=None)`** — already computes a `CompatibilityReport`, persists `compatibility_state` + full `compatibility_snapshot`, and owns the immutability trigger + the `environment_spec_hash` / sensitive-text fail-close.

`flow_start()` already produces a `run_id` (`create_run_manifest`) and holds `repo_root`. The `task_environment` row is the opt-in — a task with no contract records nothing and routes exactly as today. The standalone `maps environment-probe` alternative is considered and rejected with correct reasoning (`run_environment_evidence` is `run_id`-keyed; a task being routed may have no run yet; flow-start already makes the run). **This is composition of existing pure primitives, not a new subsystem — STOP condition not triggered.**

Minor (non-blocking obs. 1): a **second** `inspect_local_environment` exists at `runtime/environment/fingerprint.py:251` with the same signature. The note names the `safety.py` one (the stricter, containment-checked wrapper) — the correct choice — but the impl PR should be explicit it wires `safety.py`'s, not `fingerprint.py`'s.

## 4. Cache claims — ALL VERIFIED (no schema change needed)

`runtime/state/schema.sql`:

- **`task_environment`** (line 129): `spec_ref TEXT NOT NULL`, `max_age_seconds INTEGER NOT NULL CHECK (max_age_seconds > 0)`, `required_for_routing INTEGER NOT NULL DEFAULT 0 CHECK (required_for_routing IN (0,1))`, `allow_older_task_revision INTEGER NOT NULL DEFAULT 0`. **All four columns the note relies on exist.**
- **`run_environment_evidence`** (line 480): keyed `run_id TEXT NOT NULL REFERENCES run_manifests(run_id)`; columns `environment_spec_hash`, `compatibility_state` (CHECK IN COMPATIBLE/…/INCOMPATIBLE/UNKNOWN), `compatibility_snapshot TEXT NOT NULL`, `created_at`; `trg_run_environment_evidence_no_update` / `_no_delete` triggers (lines 501/507) → insert-only/immutable as claimed.
- **`run_manifests.task_id`** FK (line 141) + **`idx_run_manifests_task ON run_manifests(task_id, created_at)`** — the task↔run join path exists and is indexed.
- **`runtime/state/observability.py:158`** — the note quotes `SELECT * FROM run_manifests WHERE task_id = ? ORDER BY created_at, run_id`; verified **verbatim**.
- **`select_fresh_environment_reports`** (`environment_reports.py:85`) + **`RoutingEnvironmentReportSelection`** (line 15) exist; the freshness predicates the note wants to mirror are all present (`spec_hash_mismatch`, `task_revision_mismatch`, `report_stale` via `age > max_age_seconds`, `project_mismatch`).

**Zero production writers of the recorder** confirmed: `/usr/bin/grep -rn record_run_environment_evidence runtime/` → the definition (`environment.py:44`) + two docstring mentions in `runtime/recovery/production.py` (which say so explicitly). Only `RunBoundValidator` *reads* the table.

Minor (non-blocking obs. 2): Q6 item 2 says the new `select_recorded_environment_reports` "reuses the freshness predicates already in this module" — it re-applies the same checks to SQLite rows rather than calling `select_fresh_environment_reports`. The note is honest it's a new function; "reuses" is loose. The impl should factor the shared predicates into one helper rather than keep a second copy (rule 12).

## 5. Recorder / column / axis — E3, E2, evaluate_assignment

- `record_run_environment_evidence` + `run_environment_evidence` — **exist, zero production writers** (§4).
- `inspect_local_environment` (E2) — **exists**, pure, containment-checked (§3).
- `load_environment_spec` — exists at `runtime/environment/spec.py:317`.
- `evaluate_assignment(task, worker, *, environment_report=…)` — carries the axis; `router.py:122-133` gates `CompatibilityState.INCOMPATIBLE` → `RouteRecommendation("policy_gate", task_id, reasons=("environment_incompatible",))` **before** worker selection. The note's Q4/Q5 posture matches the code exactly.

## 6. HOLD-not-reject — SOUND; "HOLD" is a real router state

`router.py` already emits **soft `RouteRecommendation("policy_gate", task_id, reasons=(…))` fallbacks** for `halt:*` (line 101), reauthorization (line 114), and `environment_incompatible` (line 128) — each `continue`s and is re-evaluated on the next routing pass, clearing when the condition clears. `environment_report_required` is **one more of these**, placed alongside the `INCOMPATIBLE` check at 122-133. **No new `PolicyDecision` outcome kind is needed** — the router does this gating directly, not via `evaluate_assignment`'s return value. The note's parity claim with `--enforce-canonical-run` / `--enforce-validation` (deliberate, default-off) holds, at contract granularity the column already provides.

Minor (non-blocking obs. 3): the note leaves open (STOP condition 3) whether the hold "cannot be expressed without a new `PolicyDecision` outcome kind". It can — as a router `policy_gate` fallback mirroring `environment_incompatible`. The impl PR should state this concretely rather than carry it as an open risk; the STOP condition is over-cautious but harmless.

Minor (non-blocking obs. 4): Q1d (temporal model) is correct — first-ever routing of a task has no report → non-rejecting, or held if `required_for_routing=1`. The impl should test that a `required_for_routing=1` task whose first `flow_start` has not run yet **holds** (not errors) — the note implies this but doesn't call out the test.

## 7. Deferred items correctly walled off

- **Task-scoped evidence table** (Q2): "a new `task_environment_evidence` table with its own immutability trigger and its own authority question (who may write a task-scoped environment claim) … must be designed and reviewed separately. Slice 1 stays entirely on the run-scoped store." ✓ MUST-NOT #1 restates it.
- **Strict-DRIFTED** (Q4): "a `task_environment` column = schema change = deferred. Slice 1 must not add it." ✓ MUST-NOT #5.
- **`maps route --enforce-environment-routing` fleet flag** (Q3): named as a fast-follow, "not designed here beyond naming it." ✓

None are designed into slice 1. MUST-NOT #7 correctly forbids a 6.24/E1/E2/E3 status flip pending first production exposure.

## Verdict

**PASS / APPROVE.** All six questions answered; every load-bearing existence claim (E3 recorder + table + zero writers, E2 `inspect_local_environment`, all three `task_environment` columns, the `run_manifests.task_id` join, the observability query) verified by direct read at `fae8251`. The production source is genuinely composition of two existing pure functions into an existing composition point — not a new subsystem — and the `safety.py` inspector structurally prevents the probing growth the STOP condition guards against. The HOLD is expressible as an existing-pattern router `policy_gate` fallback with no new `PolicyDecision` kind and no schema change. Deferred schema steps are correctly separated. Four non-blocking observations recorded for the impl PR. `miga` owns rebase / merge-prep.
