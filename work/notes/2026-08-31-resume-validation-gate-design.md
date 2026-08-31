# Resume-validation gate — design note (6.5 / H4 / E4)

Date: 2026-08-31
Status: design-only. No runtime code change, no schema change, no checklist
status flip. Design review only (docs-only note).

Turns the advisory `resume_validation` observation into an opt-in gate on the
RnS resume path. Continues `work/notes/2026-08-25-rns-validation-tier-hookin-design.md`
(which built the advisory tier and deferred the gate to "a later, explicit
policy task") and is horizon item §5a.4 of
`work/notes/2026-08-31-roadmap-trajectory-check-10.md`.

All callsite claims re-verified at `origin/main` `fbe88bc` (rule 14).

---

## Q1 — Where `resume_validation` is produced, and who consumes it

**Produced:** `runtime/recovery/supervisor.py::RecoverySupervisor.tick()`. When
`self.resume_validator is not None`, `tick()` calls
`self.resume_validator.validate_for_run(incident["run_id"])` exactly once per
incident that has passed every earlier `continue` (not suppressed / resolved /
not-due / retry-budget-exhausted), *before* the resume attempt, and stores the
dict on the incident's action dict under `resume_validation` (line ~407–419,
emitted at ~500). Shape: `{"attempted": False, "reason": <closed vocab>}` or
`{"attempted": True, "passed": bool, "tier": "quick", ...}`.

The only concrete validator is `runtime/recovery/production.py::RunBoundValidator`,
constructed only when `run_recovery_tick(validation_repo_root=...)` is set — in
practice `maps recovery-tick --repo-root <checkout>`. It reads the incident's
own `run_environment_evidence` rows, parses the spec, and runs
`run_validation_tier(spec, "quick", ...)` under a per-tick wall-clock + count
budget. Never constructed on the `maps claim` piggyback path.

**Consumed by:** nothing. Verified at `fbe88bc`:
`grep -rn resume_validation runtime/` → only the producer in `supervisor.py`
and docstrings in `production.py`. No branch in `tick()` reads it;
`run_recovery_tick` returns `actions` verbatim; `runtime/cli.py` emits them as
JSON. **The trajectory note's "consulted by nothing" claim holds exactly.**
This is deliberate — the hookin note's non-goal 6 and Q1 forced "proceed, and
flag" for that task.

---

## Q2 — What it means for a failed `quick` tier to BLOCK a resume

A blocking gate converts a would-be resume into a distinct non-resume outcome
when `resume_validation == {"attempted": True, "passed": False}` — nothing else
(see Q6: `attempted: False` must never block).

### Placement: in `tick()`, immediately after the `validate_for_run` call

Add the check between the existing `validate_for_run` call (~line 419) and the
`if self.harness_service is not None:` resume block (~line 422):

```
if self._validation_blocks and _blocked(resume_validation):
    action = "resume_blocked_validation"          # new, distinct label
    incident["state"] = "blocked_validation"      # new, re-processable state
    incident["last_error"] = "quick validation tier failed"
    # attempt NOT incremented; reschedule on the flat probe interval
    incident["next_attempt_at"] = _time_z(now + probe_delay)
    ... append action dict ... ; continue
```

`_blocked(v)` = `isinstance(v, Mapping) and v.get("attempted") is True and
v.get("passed") is False`.

### Which component enforces it

`RecoverySupervisor` itself, via one new optional constructor flag
(`validation_blocks_resume: bool = False`), composed in
`runtime/recovery/production.py` from a new `maps recovery-tick
--enforce-validation` CLI flag (Q3/Q5). **Not** a Hook.

### Why not register `make_validation_hook()` at `BEFORE_RESUME`

Rejected for the same three reasons the hookin note §2.1 gives, all still true
at HEAD:

1. `make_validation_hook` returns `HookOutcome(DENY, …)`;
   `HarnessService.resume()` turns any `BEFORE_RESUME` DENY into
   `_hook_block("resume", …)` → `code = "HOOK_DENIED"`.
2. `supervisor.py` `_CANONICAL_DENIAL_CODES = {"HOOK_DENIED", "APPROVAL_REQUIRED"}`
   — a validation DENY would land in the `action = "resume_denied"` branch,
   **mislabelling a broken environment as a canonical-run mismatch** and
   destroying the attribution PR #160 / #195 preserve.
3. It only runs when a production `HarnessService` *and* an installed
   `CANONICAL_RUN` hook exist — i.e. only when `--enforce-canonical-run` is on.
   The `tick()` placement runs regardless (Q4).

### Interaction with the canonical-run guard and PR #195's `denied` state

The gate runs **before** the harness resume call, so it is independent of
whether `--enforce-canonical-run` is on. Deliberate ordering: if the
environment is broken there is no value in attempting a canonical-guarded
resume, and the validation signal is the cheaper, more specific one.

`blocked_validation` (this note) and `denied` (PR #195, canonical denial) are
**disjoint states**, both:

- do **not** consume the transient `attempt` retry budget — a failed `quick`
  tier is deterministic w.r.t. an identical re-run, exactly like a canonical
  denial;
- reschedule on the flat `silent_stop_probe_delay_seconds`, not the escalating
  backoff ladder;
- get their **own** consecutive-occurrence ceiling
  (`_MAX_CONSECUTIVE_VALIDATION_BLOCKS`, mirroring PR #195's
  `_MAX_CONSECUTIVE_CANONICAL_DENIALS = 3`) → promote a persistently-blocked
  incident to `failed` / `validation_block_persistent`;
- reset their streak counter on any non-matching outcome.

With both flags on, an incident flows: due → **validation gate** (block →
`blocked_validation`, stop) → harness resume → **canonical guard** (deny →
`denied`, stop) → resume / fallback. The two counters
(`canonical_denials`, `validation_blocks`) are separate dataclass fields on
`RecoveryIncident` (JSON store, no schema change — same pattern as #195).

Unchanged: only the `quick` tier runs on the resume path; the per-tick
wall-clock and count budgets in `RunBoundValidator` are untouched; a
budget-skipped incident yields `attempted: False` and therefore never blocks.

---

## Q3 — WHO decides "block" vs "warn" — the real open question

### Options considered

| Model | Verdict |
|---|---|
| **Per-tier default** (quick=warn, normal/full=block) | Rejected. `quick` is the only tier that runs on the resume path, so "quick = warn" means the gate never fires. |
| **`task_policy` flag** (e.g. `policy["validation_blocks_resume"]`) | Rejected. RnS deliberately never reads task policy to make a recovery decision (`supervisor.py` docstrings; hookin non-goal 9). "May a broken environment block a resume" is a run/environment property, not a task-authority one. Coupling it to `task_policy` also means a new `POLICY_FLAGS` entry (schema change). |
| **Per-spec `EnvironmentSpec.validation.enforcement: "advisory" \| "blocking"`** (or `task_environment.validation_blocks_resume`) | Right long-term home — the spec is operator-authored, run-bound, and tamper-evident via `environment_spec_hash`, analogous to the existing `task_environment.required_for_routing`. But it is a spec-schema / `parse_environment_spec` change and needs its own authorised task. |
| **Operator opt-in at invocation** — `maps recovery-tick --enforce-validation` | **Recommended for the first slice.** |

### Recommendation

**Two levels, first level only in the first slice:**

1. **Now:** the operator decides per-pass, via `maps recovery-tick
   --enforce-validation` (requires `--repo-root`, since no validator is built
   without it). This is an exact parallel of the `--enforce-canonical-run`
   enablement model: a deliberate operator choice at an explicitly-invoked
   pass, default-off, no schema change, no new authority store, no `task_policy`
   coupling. The authority to say "a failed tier blocks" is the operator
   running the pass — the same authority that already decides to run validation
   at all (`--repo-root`) and to enforce canonical-run identity
   (`--enforce-canonical-run`).

2. **Later (separate authorised task):** a per-spec
   `EnvironmentSpec.validation.enforcement` field for finer control — some runs
   advisory, some blocking — layered under the CLI flag (flag off ⇒ always
   advisory; flag on ⇒ per-spec, defaulting to blocking). This is the
   `task_policy`-style granularity the dispatch asks about, deferred because it
   is a spec-schema change.

Never on the `claim` piggyback path (no validator there; keep #165's bound).

---

## Q4 — Relationship to §5a item 1 (enforced `--enforce-canonical-run`)

**Independent, not a slice of it.** The trajectory note's "enforced
canonical-run is the natural place to also consult validation outcome" is only
true under the rejected Option A (validation hook at `BEFORE_RESUME`), which
requires the harness path and the `CANONICAL_RUN` hook to be live.

With the recommended `tick()` placement the gate needs no `HarnessService` and
no hook — it reads a dict `tick()` already computes. So:

- it can ship and be enabled **without** `--enforce-canonical-run`;
- it does not block, and is not blocked by, the canonical-run enablement work;
- the two share a **design pattern** (an `--enforce-X` opt-in; a distinct,
  non-attempt-consuming parked state; a separate ceiling) but **no code**;
- `--enforce-validation` and `--enforce-canonical-run` **compose** cleanly
  (validation gate first, then the canonical guard on the harness path).

Decoupling them is the recommendation: neither should be a prerequisite for the
other.

---

## Q5 — Smallest first slice (rule 8)

Makes one tier (`quick`) gate one resume path (RnS `tick()`), deferring the
per-spec policy field.

**`runtime/recovery/supervisor.py`**
- One new optional constructor kwarg `validation_blocks_resume: bool = False`
  (stored as `self._validation_blocks`).
- In `tick()`, one new check immediately after the existing `validate_for_run`
  call: if `self._validation_blocks` and `_blocked(resume_validation)` →
  `action = "resume_blocked_validation"`, `state = "blocked_validation"`,
  `last_error`, reschedule on `silent_stop_probe_delay_seconds`, **do not**
  increment `attempt`, append the standard action dict, `continue`.
- Add `"blocked_validation"` to the re-processable state set (`{"scheduled",
  "probing"}` → add it).
- **No** `EnvironmentSpec` / validation-type import or name anywhere in the file
  (keep `test_no_validation_tier_commands_or_task_mutation_in_source` green).
- v1 may or may not include the persistent-block ceiling — recommended to
  include it (mirrors #195, small) but acceptable to defer to a fast-follow if
  it risks scope; the minimal slice just parks + reschedules.

**`runtime/recovery/store.py`** (only if the ceiling is in v1)
- `RecoveryIncident.validation_blocks: int = 0` dataclass field. JSON store, no
  schema change (identical to #195's `canonical_denials`).

**`runtime/recovery/production.py` + `runtime/cli.py`**
- Thread a `--enforce-validation` flag on `recovery-tick` →
  `run_recovery_tick(..., validation_blocks_resume=True)` →
  `RecoverySupervisor(validation_blocks_resume=...)`. Argparse-require
  `--repo-root` when it is set (no validator otherwise).

**Deferred:** the per-spec `validation.enforcement` field; `normal`/`full`
tiers on the resume path; any `compatibility_state` / `EnvironmentCompatibilityReport`
derived from a tier result; persisting the block onto the recovery-state
incident beyond the counter.

**Tests (one blocking foreground `python3 -m unittest tests.test_recovery_supervisor`):**
- failing `quick` tier + flag on → `action == "resume_blocked_validation"`,
  `attempt` unchanged, `hcom.resume` / `harness_service.resume` never called,
  incident `state == "blocked_validation"`, rescheduled on the flat interval;
- flag **off** → byte-identical to today (advisory `resume_validation` recorded,
  resume proceeds);
- `{"attempted": False, ...}` (missing / ambiguous / unparseable spec,
  `budget_exceeded`) → **never** blocks, regardless of the flag;
- a subsequent passing tier resets the streak / clears `blocked_validation`;
- (if ceiling in v1) N consecutive blocks → `failed` /
  `validation_block_persistent`, independent of the transient retry budget.

---

## Q6 — STOP conditions / MUST-NOTs for the eventual impl

**MUST NOT:**

1. Register `make_validation_hook()` at `BEFORE_RESUME`, add a `HookEnforcement`
   member for validation, or change `_CANONICAL_DENIAL_CODES` /
   `HarnessService._hook_block` semantics — mislabels a broken environment as a
   canonical-run denial (Q2, hookin §2.1).
2. Read `task_policy` in `supervisor.py`, or make any recovery decision from
   task truth. No `claim_task` / `submit_task` / `record_review` /
   `promote_ready` / `update_contract` / task-DB write (RnS contract; hookin
   non-goal 9).
3. Import or name `EnvironmentSpec` / validation-tier types in
   `runtime/recovery/supervisor.py` — the #160 source guard is a lowercased
   substring scan over the whole file.
4. Let `{"attempted": False}` block a resume — only a real
   `{"attempted": True, "passed": False}`. Missing / ambiguous / unparseable /
   budget-skipped validation evidence must not block and must not imply
   environment incompatibility (hookin Q4/Q9).
5. Change default behavior: `validation_blocks_resume` defaults `False`;
   without `--enforce-validation` the pass is byte-identical to today, including
   the advisory `resume_validation` recording.
6. Consume the transient `attempt` retry budget on a validation block, or route
   it onto the escalating backoff ladder — it is deterministic w.r.t. re-run,
   like a canonical denial (PR #195 parity).
7. Enable validation (advisory or blocking) on the `maps claim` piggyback path
   — no validator is constructed there; keep #165's ~6s bound.
8. Add a schema change, a new `POLICY_FLAGS` entry, an authority store, or an
   operator-identity registry in the first slice — the per-spec
   `validation.enforcement` field is a separate authorised task.
9. Flip 6.5 / H4 / E4 (or 6.16 / H5) status. A first real production exposure
   (a `maps recovery-tick --repo-root --enforce-validation` pass on a real
   project with a run-bound spec, and the recorded outcome) is still required
   before any status moves.
10. Weaken `tests/test_recovery_supervisor.py::test_no_validation_tier_commands_or_task_mutation_in_source`.

**STOP and escalate to `miga` if:**

- wiring the gate forces a `HarnessService` dependency or an installed
  `CANONICAL_RUN` hook (it must not — the gate sits before the harness call);
- the "who decides block vs warn" question cannot be resolved to the
  operator-invocation model (`--enforce-validation`) without a schema / spec
  change in the first slice;
- the first slice starts to require the per-spec `validation.enforcement` field,
  a `task_policy` flag, or any coupling between recovery decisions and task
  truth.

---

## Roadmap impact

Does not complete 6.5 / H4 / E4. Makes the advisory `resume_validation`
observation gate-ready by specifying the enforcing component (`RecoverySupervisor`
+ a `--enforce-validation` opt-in), the enforcement point (in `tick()`, before
the harness call), the disjoint `blocked_validation` incident state (PR #195
parity), and the "who decides" model (operator per-pass now, per-spec field
later). `work/roadmaps/CAPABILITY_CHECKLIST.md` is unchanged by this note (an
optional one-line "design note pending" annotation on 6.5 / H4 / E4 is within
the output boundary if the reviewer prefers it).

---

## Resume prompt

You are implementing the **first slice** of the resume-validation gate for
MAPS_Lean (roadmap 6.5 / H4 / E4). Work in your own git worktree off
`origin/main`; `cd ~/Projects/MAPS_Lean` and `git fetch origin main` first.
Re-verify every callsite at your HEAD (rule 14).

Source of truth: this note (`work/notes/2026-08-31-resume-validation-gate-design.md`),
its parent `work/notes/2026-08-25-rns-validation-tier-hookin-design.md`, and
PR #195's `blocked`-state / non-attempt-consuming pattern
(`work/notes/2026-08-31-canonical-enforcement-first-exposure-design.md` §2b).

Implement exactly the **Q5 "Smallest first slice"** list:

1. `runtime/recovery/supervisor.py`: one optional constructor kwarg
   `validation_blocks_resume: bool = False`; in `tick()`, immediately after the
   existing `self.resume_validator.validate_for_run(...)` call, if the flag is
   set and `resume_validation` is `{"attempted": True, "passed": False}` →
   `action = "resume_blocked_validation"`, `incident["state"] =
   "blocked_validation"`, `last_error = "quick validation tier failed"`,
   reschedule on `silent_stop_probe_delay_seconds`, **do not** increment
   `attempt`, append the standard action dict, `continue`. Add
   `"blocked_validation"` to the re-processable state set. No `EnvironmentSpec`
   / validation-type name anywhere in the file.
2. `runtime/recovery/store.py` (only if you include the ceiling now):
   `RecoveryIncident.validation_blocks: int = 0`; a
   `_MAX_CONSECUTIVE_VALIDATION_BLOCKS = 3` ceiling in `tick()` →
   `failed` / `validation_block_persistent`; reset on any non-block outcome.
3. `runtime/recovery/production.py` + `runtime/cli.py`: a `--enforce-validation`
   flag on `recovery-tick`, argparse-requiring `--repo-root`, threaded through
   `run_recovery_tick` → `RecoverySupervisor`.

MUST NOT: register `make_validation_hook()` at `BEFORE_RESUME`; add a
`HookEnforcement` member or touch `_CANONICAL_DENIAL_CODES`; read `task_policy`
or mutate task truth in `supervisor.py`; let `{"attempted": False}` block;
change default (flag-off) behavior; consume the retry budget on a block; enable
on the `claim` piggyback path; add a schema / `POLICY_FLAGS` change; flip
6.5 / H4 / E4 / 6.16 / H5 status; weaken the #160 source guard.

Tests (one blocking foreground `python3 -m unittest tests.test_recovery_supervisor`,
no Monitor, no background): failing tier + flag on → blocked, `attempt`
unchanged, no resume call; flag off → byte-identical to today;
`{"attempted": False}` never blocks; passing tier clears the block;
(if ceiling) N blocks → `failed`. `python3 -m runtime.smoke` exits 0. Push
before any full-suite run; rely on CI.

Update the 6.5 / H4 / E4 evidence text in
`work/roadmaps/CAPABILITY_CHECKLIST.md` in the same PR — **no status flip**.

Then: PR into `main` (never push to main). Request independent review with
mutation testing (min 5) per `reference_committee_review`; add a bound
`work/reviews/pr-<N>-review-evidence.md` (the reviewer's, not yours — see
`feedback_implementer_cannot_commit_review_evidence`). Do NOT self-merge.
Report the PR number to `miga`.

Stop conditions: if the gate forces a `HarnessService` / `CANONICAL_RUN` hook
dependency, or the first slice starts needing the per-spec
`validation.enforcement` field / a `task_policy` flag, STOP and flag `miga`.
