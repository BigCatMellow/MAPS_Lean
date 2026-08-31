# Design: canonical-enforcement first-exposure behaviour — retry budget and expired-lease workflow

**Status: DESIGN ONLY.** This note changes no runtime code, no test, and no
checklist row. It answers the two open questions that
`work/notes/2026-08-26-hook-enforcement-composition-root-design.md` §5 left as
gates in front of enabling `maps recovery-tick --enforce-canonical-run` on a real
project and closing **E4 / H5 / 6.5 / 6.16**:

- **Q4** — retry-budget interaction: does a `HOOK_DENIED` canonical denial
  correctly terminate as `failed` / `retry_budget_exhausted`, or should it be
  distinguished from a transient failure?
- **Q5** — `LEASE_EXPIRED` dominates first exposure. What is the operator
  workflow, and where is it documented?

Source of truth re-checked at this branch head (`origin/main` `84cc3f7`):
`runtime/recovery/supervisor.py` `tick()`, `runtime/policy/harness_guard.py`,
`runtime/state/execution.py` (`claim_task` / `heartbeat`),
`runtime/state/run_lineage.py`. The composition-root note's §2b trace was
reproduced against current code, not trusted from prose (rule 14).

---

## 1. What `tick()` actually does with a canonical denial today — re-derived

`supervisor.py` `_CANONICAL_DENIAL_CODES = {"HOOK_DENIED", "APPROVAL_REQUIRED"}`
(line 24). Inside `tick()`, when `harness_service` is composed and
`_resolve_harness_binding` returns a binding, `self.harness_service.resume(...)`
is called and its result routed:

- `result.ok` → `action = "resume"`, `resolved = True`.
- `str(result.code) in _CANONICAL_DENIAL_CODES` → `error = str(result.summary)`,
  `action = "resume_denied"`, `resolved = True`. **No fallback to direct
  `hcom.resume()`.**
- any other code → fall through to the pre-existing direct resume.

Then — and this is the load-bearing detail — control reaches the **unconditional**
tail of the loop body (`supervisor.py:478-502`) regardless of which branch set
`resolved`:

```
attempt += 1
incident["attempt"] = attempt
incident["state"] = "probing"
incident["last_attempt_at"] = _time_z(now)
incident["last_error"] = error
incident["next_attempt_at"] = _time_z(now + timedelta(seconds=self.backoff_seconds[min(attempt - 1, len - 1)]))
```

So a canonical denial **consumes a retry attempt**, sets the incident back to
`probing`, and schedules the next pass on the ordinary escalating backoff
(`DEFAULT_BACKOFF_SECONDS = (300, 900, 1800, 3600, 7200)`). On a later pass, once
`attempt >= len(self.backoff_seconds)` (line 384), the incident becomes
`state = "failed"`, `last_error = "retry_budget_exhausted"`, `action = "fail"`.

`resume_denied` is therefore **not** a terminal state. It is a normal probing
attempt that happens to have been blocked, and five of them across ~3.5 h of
backoff collapse into a single generic `retry_budget_exhausted` terminal.

`harness_resume` on every affected action dict does carry `{"attempted": true,
"ok": false, "code": "HOOK_DENIED", "summary": "<deny code + message>"}`, so the
real cause is present in the action log — but it is **not** reflected in the
incident's own `state` / `last_error`, which is what an operator scanning the
`RecoveryStore` sees first.

---

## 2. Q4 — retry-budget interaction

### 2a. The problem with the current behaviour

A canonical denial is **deterministic with respect to a re-run of the identical
pass**. `CanonicalRunGuard` performs reads only; given unchanged task truth and
unchanged run manifest, `LEASE_EXPIRED`, `NOT_CLAIM_OWNER`, `RUN_WORKER_MISMATCH`,
`RUN_REVISION_MISMATCH`, `RUN_STALE` and the `SESSION_*` lineage denials all
return the same outcome on attempt 2 as on attempt 1. Nothing `tick()` itself
does between passes changes any input to the guard.

Two consequences, both bad:

1. **Misattributed terminal cause.** The incident ends as
   `retry_budget_exhausted` — a code that means "we tried and the transient
   condition never cleared". The actual cause (`HOOK_DENIED` /
   `RUN_WORKER_MISMATCH`, say) is only in the last action dict's `harness_resume`
   field, not the incident state. An operator triaging a wall of `failed`
   incidents cannot tell canonical denials from genuine transient exhaustion
   without opening each action log.

2. **Delayed and budget-coupled signal.** The operator does not get a clear
   "this run is not canonically resumable, do something" signal until the full
   backoff ladder is spent. Worse, the coupling runs the other way too: if an
   incident had *already* burned 3 of 5 attempts on genuine transient failures
   before enforcement denied it, it has only 2 canonical-denial passes left
   before `retry_budget_exhausted` — the denial budget is whatever is left over,
   which is arbitrary.

The one countervailing fact: a denial is **not** deterministic across an
*operator remediation* between passes. If the operator renews/re-establishes the
lease (see §3), the next pass's guard call genuinely can flip to
`CANONICAL_RUN_VERIFIED`. So "canonical denial → immediate hard terminal" would
be wrong too: it would slam the door on the exact recovery the operator is in the
middle of performing.

### 2b. Recommendation

**A canonical denial should not consume a transient retry attempt, and should be
surfaced as its own incident state rather than laundered through
`retry_budget_exhausted`.** Concretely, the intended behaviour is:

- On `str(result.code) in _CANONICAL_DENIAL_CODES`: set
  `incident["state"] = "denied"` (a new, non-terminal-but-distinct state),
  `incident["last_error"] = "<deny code>"`, record the denial on the action dict
  as today, **do not** increment `attempt`, and reschedule on a **flat**
  interval (reuse `silent_stop_probe_delay_seconds`, or the first backoff rung)
  rather than the escalating ladder.
- Keep a **separate, small ceiling** on consecutive canonical denials — e.g. a
  `denied` incident that has been denied N times in a row (N≈3) with no
  intervening state change goes to `state = "failed"`,
  `last_error = "canonical_denial_persistent"` — so a genuinely
  un-remediable run does not probe forever. This ceiling is independent of the
  transient `backoff_seconds` budget.

This gives the operator (a) an immediate, correctly-labelled signal
(`state = "denied"`, `last_error = "LEASE_EXPIRED"`), (b) a bounded window to
remediate during which the incident stays resumable, and (c) a distinct terminal
code when remediation never happens, so `retry_budget_exhausted` keeps meaning
only what it says.

### 2c. The single exact decision point this would touch

`runtime/recovery/supervisor.py`, the

```python
elif str(result.code) in _CANONICAL_DENIAL_CODES:
    error = str(result.summary)
    action = "resume_denied"
    resolved = True
```

branch inside `tick()` (currently ~line 447), **plus** the unconditional loop
tail at ~line 478 that must be made conditional (a canonical denial would
`continue` past the `attempt += 1` block after writing its own state, the way the
`retry_budget_exhausted` and `resolve` branches already `continue`). The
consecutive-denial ceiling adds one counter read/write alongside
`incident["attempt"]`.

**Nothing else.** No guard change (`harness_guard.py` is untouched), no
`HarnessService` change, no new event, no `HookRegistry` change.

### 2d. Explicitly OUT of scope for the composition-root implementation PR

The composition-root note's §4 non-goal 3 ("no change to `tick()`'s internal
decision logic") stands. **Everything in §2b is a separate slice.** The
composition-root PR ships with the *current* behaviour: a canonical denial
consumes an attempt and, on repeat, terminates as `retry_budget_exhausted`. That
is acceptable for a **default-off, operator-opted-in** first exposure — the
operator running the first enforced pass is doing so deliberately and watching
the output — but it is **not** acceptable as the steady state once enforcement is
recommended for routine use. The §2b slice is the gate between "first exposure"
and "routine use", and it must land before E4 / H5 / 6.5 / 6.16 are argued to
DONE on the basis of routine enforceability.

---

## 3. Q5 — the expired-lease operator workflow

### 3a. `maps heartbeat` does NOT work once the lease has expired

The obvious answer — "renew the lease with `maps heartbeat`, then re-run the
pass" — **fails on the dominant case.** `runtime/state/execution.py` `heartbeat`
(lines 103-156) itself refuses an already-expired lease:

```python
lease = parse_time(row["lease_expires_at"])
if lease is not None and lease <= current:
    return MutationResult(False, "LEASE_EXPIRED", "claim lease has expired", dict(row))
```

It also requires `row["claimed_by"] == worker_id` (`NOT_CLAIM_OWNER` otherwise).
So `heartbeat` only helps a session whose lease is *still live* — which is
precisely **not** the RnS recovery case. §2b of the composition-root note is
explicit that a silently-stopped session is a strong candidate for a lease that
has *already* lapsed. `heartbeat` is the wrong tool here.

### 3b. The workflow that does work: recover the claim in place

`claim_task` (`execution.py:25-100`) has a `recover` path for an **expired**
`ACTIVE` claim:

```python
elif row["status"] == "ACTIVE":
    lease = parse_time(row["lease_expires_at"])
    ...
    if lease is None or lease > current:      # still live -> LEASE_ACTIVE, refuse
        ...
    if row["attempt"] >= row["max_attempts"]: # -> ATTEMPT_LIMIT, refuse
        ...
    recover = True                            # expired -> recover
```

Recovery sets `status = 'ACTIVE'`, a fresh `lease_expires_at`, `claimed_by = ?`,
and **`attempt = attempt + 1`**.

The operator workflow is therefore:

```
maps claim <task-id> --worker-id <ORIGINAL worker id> --lease-seconds <N>
maps recovery-tick --enforce-canonical-run --harness-project-id <PROJ> --repo-root <PATH>
```

**Critical constraint — the `--worker-id` must be the run manifest's recorded
worker.** `CanonicalRunGuard._require_live_claim` checks `task.claimed_by ==
worker_id` from the binding (`NOT_CLAIM_OWNER`), and the run-lineage checks in
`run_lineage.py` compare the session's recorded worker against the current
claimant (`RUN_WORKER_MISMATCH` / `RUN_NOT_OWNED`). Recovering the claim under a
*different* worker id clears `LEASE_EXPIRED` only to trip a worker-mismatch
denial on the same pass. Recovering under the original worker id clears the lease
without introducing a mismatch.

**Second constraint — `claim_task`'s `attempt + 1` is task-truth, distinct from
the recovery incident's retry `attempt`.** It counts against `max_attempts`; an
incident whose task is already at `attempt >= max_attempts` gets `ATTEMPT_LIMIT`
and cannot be recovered this way at all — that incident is genuinely done and
should be closed, not resumed.

### 3c. Known gap (UNKNOWN, not guessed)

Whether recovering the claim in place also requires the run manifest's
`task_revision` to still match `compute_task_revision()` after the
`attempt`-bump — i.e. whether `claim_task`'s recovery mutates anything that feeds
`compute_task_revision()` and would then trip `RUN_REVISION_MISMATCH` /
`TASK_REVISION_STALE` on the subsequent enforced pass — was **not** verified for
this note. `compute_task_revision()`'s input set is in
`runtime/state/integrity.py`; the implementer must confirm at their head whether
a claim-recovery bumps it. If it does, the workflow in §3b is incomplete and the
only canonical-resume path for a revision-drifted run is "start a fresh run", not
"recover + re-tick". **This is the one open risk in the Q5 answer.**

### 3d. Recommendation on where this is documented

**Not this note** (a design note is ephemeral working material). **Not a new
`work/playbooks/` tree** (rule 8/13 — no new machinery for one runbook).

Document it in **two** places:

1. **The composition-root implementation PR description and its checklist-row
   edits** — E4 / H5 / 6.5 / 6.16 evidence text should state that first exposure
   is expected to produce `LEASE_EXPIRED` denials and that the remediation is
   claim-recovery under the original worker id, not `heartbeat`.
2. **`docs/CONTROL_PLANE_SETUP.md`** — it already documents `claim`, `heartbeat`,
   leases and attempts (lines ~128, ~182). Add a short "Canonical enforcement:
   remediating a denied resume" subsection there, next to the existing recovery
   material. That is the canonical operator-facing home and adding a subsection
   to it is the smallest change.

### 3e. The single exact decision point (if any code change followed)

**None in `tick()` or the guard.** The `maps claim` recovery path and
`maps heartbeat` already exist and already behave correctly; Q5 is answered by
*documentation* plus the §2b state-labelling change (which makes the
`LEASE_EXPIRED` denial visible as `state = "denied"` / `last_error =
"LEASE_EXPIRED"` so the operator knows to run claim-recovery). The only code
decision point Q5 shares is the same `_CANONICAL_DENIAL_CODES` branch named in
§2c — surfacing the deny code on the incident is what turns "some opaque failure"
into "run claim-recovery under the original worker id".

---

## 4. What stays OUT of scope

- **Any `tick()` decision-logic change** — the §2b recommendation
  (non-attempt-consuming `denied` state + consecutive-denial ceiling) is a
  **separate implementation slice**, gated behind this note, not part of the
  composition-root PR. The composition-root PR ships current behaviour.
- **Any guard change** (`harness_guard.py`), any `HarnessService` /
  `HookRegistry` / `HookEnforcement` change, any new event or enforcement role.
- **Any change to `maps claim` or `maps heartbeat`.** §3's workflow uses them
  exactly as they are.
- **`work/roadmaps/CAPABILITY_CHECKLIST.md`** — untouched by this note; the
  E4 / H5 / 6.5 / 6.16 edits belong in the implementation PR (composition-root
  note §6, pass #8 §2 process finding).
- **The §3c revision-drift question** — flagged UNKNOWN, to be resolved by the
  implementer against current `integrity.py`, not answered here.

---

## 5. Summary answer

| Q | Answer | Exact decision point if implemented |
|---|---|---|
| **Q4** | `retry_budget_exhausted` is the **wrong** terminal state for a canonical denial. A denial should not consume a transient attempt; it should set a distinct `state = "denied"` with the deny code as `last_error`, reschedule on a flat interval, and have its own small consecutive-denial ceiling before a distinct `failed` code. Separate slice; composition-root PR ships current behaviour, acceptable only for default-off first exposure. | `supervisor.py` `tick()` `elif str(result.code) in _CANONICAL_DENIAL_CODES:` branch (~L447) + making the unconditional `attempt += 1` loop tail (~L478) conditional. |
| **Q5** | Workflow is **not** `maps heartbeat` (it refuses an already-expired lease). It is `maps claim <task> --worker-id <ORIGINAL worker> --lease-seconds N` (claim-recovery of the expired ACTIVE claim under the manifest's recorded worker) then re-run the enforced pass. Document in the impl PR description + a subsection of `docs/CONTROL_PLANE_SETUP.md`. One UNKNOWN: whether claim-recovery's `attempt+1` bumps `compute_task_revision()` and trips `RUN_REVISION_MISMATCH` — implementer to verify. | No `tick()`/guard change of its own; shares the §2c branch only to surface the deny code on the incident state. |

---

## Resume prompt

Implement the §2b `tick()` slice that this note gates. In
`runtime/recovery/supervisor.py` `tick()`, change the
`_CANONICAL_DENIAL_CODES` branch so a canonical denial does **not** consume a
transient retry `attempt`: set `incident["state"] = "denied"` and
`incident["last_error"]` to the deny code, record the denial on the action dict
as today, `continue` past the unconditional `attempt += 1` loop tail (make that
tail conditional, mirroring how the `resolve` and `retry_budget_exhausted`
branches already `continue`), and reschedule on a flat interval (reuse
`silent_stop_probe_delay_seconds` or `backoff_seconds[0]`). Add a separate
consecutive-canonical-denial counter with a small ceiling (N≈3) that promotes a
persistently-`denied` incident to `state = "failed"`,
`last_error = "canonical_denial_persistent"` — independent of the transient
`backoff_seconds` budget. Do NOT touch `runtime/policy/harness_guard.py`,
`HarnessService`, `HookRegistry`, or any hook event. Update the affected tests in
`tests/test_recovery_supervisor.py`. Then verify §3c: check at your HEAD whether
`runtime/state/execution.py` `claim_task`'s recovery path (`attempt = attempt +
1`) changes any input to `runtime/state/integrity.py` `compute_task_revision()`;
if it does, the expired-lease operator workflow in
`work/notes/2026-08-31-canonical-enforcement-first-exposure-design.md` §3b is
incomplete and needs a "start a fresh run" branch — say so in the PR. Add the
operator remediation subsection to `docs/CONTROL_PLANE_SETUP.md` (next to the
existing claim/heartbeat/lease material): denied resume → `maps claim <task>
--worker-id <ORIGINAL worker> --lease-seconds N` → re-run the enforced pass; note
that `maps heartbeat` cannot renew an already-expired lease. Edit
`work/roadmaps/CAPABILITY_CHECKLIST.md` E4 / H5 / 6.5 / 6.16 in this same PR.
Run `python3 -m unittest tests.test_recovery_supervisor` as one blocking
foreground call. Get an independent reviewer; do not self-certify.
