# Design note — a production call site for `HarnessService.stop()` (6.4)

**Status:** design only. No runtime code changed by this note. No
`CAPABILITY_CHECKLIST.md` edit. Not self-reviewed. Merge is on the 3-day
operator hold; `review-evidence` CI is expected red until a coordinator
dispatches an independent reviewer.

**Source of truth**

- `work/roadmaps/CAPABILITY_CHECKLIST.md` row 6.4 ("Deterministic
  Hooks/Interceptors", IN PROGRESS).
- `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md` §7.2.
- `runtime/harness/service.py::HarnessService.stop()` (defn at L335).
- `runtime/policy/destructive_action_guard.py` (guard built + composed).
- `runtime/recovery/production.py::build_canonical_harness_service` (composition
  root; registers `DestructiveExternalActionGuard`).
- `runtime/recovery/supervisor.py::RecoverySupervisor` (only production consumer
  of a `HarnessService`; today calls `.resume()` only).
- Predecessor context: `/home/home/MAPS_Lean_Handoff_2026-09-06-session33.md`
  priority #4; `work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md`;
  `work/notes/2026-09-05-dec003-b-attempt2-real-run-results.md` (case
  `CASE-378fb326…`, the first real routable `resume_denied`).
- Local memory: `project_6_4_6_22_need_production_callsite.md`.

---

## 1. Fresh grep — zero production callers; what exists vs. not

All commands run in a fresh clone at `origin/main` =
`c958cf6ba099edf2363e0d66b40f10c2c1174425` (`#298`).

### 1a. No `.stop(` on a `HarnessService` anywhere under `runtime/recovery/`

```
$ /usr/bin/grep -rn "\.stop(" runtime/recovery/ --include=*.py | grep -v test
runtime/recovery/production.py:384:    registered. `HarnessService.stop()` fires `BEFORE_DESTRUCTIVE_ACTION`
```

The single hit is prose inside the `build_canonical_harness_service` docstring,
not a call.

### 1b. Every `.stop(` under `runtime/` (non-test)

```
$ /usr/bin/grep -rn "\.stop(" runtime/ --include=*.py | grep -v test
runtime/harness/adapters/hcom.py:426:            self.backend.stop(str(record["name"]))
runtime/harness/service.py:393:        return adapter.stop(binding, reason)
runtime/harness/contract.py:55:            return self.adapter.stop(self.binding, self.stop_reason)
runtime/policy/destructive_action_guard.py:219:    `HarnessService.stop()` is the first operation that fires
runtime/recovery/production.py:384:    registered. `HarnessService.stop()` fires `BEFORE_DESTRUCTIVE_ACTION`
```

- `service.py:393` — the *tail* of `HarnessService.stop()` itself (delegates to
  the adapter after the hook chain). Not a caller of `HarnessService.stop`.
- `adapters/hcom.py:426` — `HcomHarnessAdapter.stop()` calling its hcom
  *backend*; reached only *from* `HarnessService.stop()` at L393. Not an
  independent caller.
- `contract.py:55` — `StopIntent.execute()` (a value-object convenience
  wrapper); grep for its constructor shows no production instantiation.
- The remaining two are docstring prose.

### 1c. `HarnessService.stop` / `service.stop` symbol search

```
$ /usr/bin/grep -rn "harness_service\.stop\|harness\.stop\|service\.stop\|\.stop(binding" --include=*.py runtime/ cli/ 2>/dev/null | grep -v test
(no matches)
```

### 1d. Only production `HarnessService` consumer routes resume only

```
$ /usr/bin/grep -n "self.harness_service" runtime/recovery/supervisor.py
120:        self.harness_service = harness_service
532:            if self.harness_service is not None:
538:                        result = self.harness_service.resume(binding, session_ref)
```

`supervisor.py:538` is the sole production invocation of any `HarnessService`
method, and it is `.resume(...)`.

**Conclusion:** `HarnessService.stop()` has **zero production callers** on
current `origin/main`. Stop condition ("a caller already exists → STOP") does
not fire.

### 1e. What already exists vs. not

| Piece | State | Location |
|---|---|---|
| `HookEvent.BEFORE_DESTRUCTIVE_ACTION` enum member | **exists** | `runtime/harness/hooks.py:19` |
| `HookEvent.SESSION_STOPPING` enum member | **exists** | `runtime/harness/hooks.py:25` |
| `HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION` | **exists** | `runtime/harness/hooks.py` |
| `HarnessService.stop()` — fires `BEFORE_DESTRUCTIVE_ACTION` (fixed literal `destructive=True, external=False`), then `SESSION_STOPPING`, then `adapter.stop()` | **exists**, fully built | `runtime/harness/service.py:335-393` |
| `_require_destructive_enforcement()` gate (returns `DESTRUCTIVE_GUARD_REQUIRED` if no guard registered for the event) | **exists** | `runtime/harness/service.py:78-92`, called at `:354` |
| `DestructiveExternalActionGuard` + `register_destructive_external_action_guards` | **exists**, subscribes to `BEFORE_DESTRUCTIVE_ACTION` **and** `BEFORE_EXTERNAL_ACTION` | `runtime/policy/destructive_action_guard.py` |
| Guard **composed into the one production `HarnessService`** | **exists** | `runtime/recovery/production.py:414-417` (`build_canonical_harness_service`) |
| `HcomHarnessAdapter.stop()` → hcom backend `stop(name)` | **exists** | `runtime/harness/adapters/hcom.py:426` |
| `_resolve_harness_binding(incident, session_name)` → `(ExecutionBinding, SessionRef, reason)` | **exists**, already used by the resume path | `runtime/recovery/supervisor.py:208-300` |
| A **production code path that calls `HarnessService.stop()`** | **does NOT exist** | — (this note) |
| Default-off CLI flag that would arm such a call | **does NOT exist** | — (this note) |
| `BEFORE_EXTERNAL_ACTION` firing site | **does NOT exist** (guard subscribes; nothing fires it) | — |

The destructive-action guard callback has therefore **never executed in a real
pass**: `build_canonical_harness_service` was instantiated in a live enforced
pass twice (2026-09-03 resume-only; 2026-09-05 DEC-003 option B, `CASE-378fb326…`),
but both exercised only `HarnessService.resume()` → `BEFORE_RESUME` /
`CANONICAL_RUN`. `BEFORE_DESTRUCTIVE_ACTION` has fired zero times outside unit
tests.

---

## 2. Smallest legitimate production call site in `RecoverySupervisor`

### 2a. Existing incident terminal / parked states (cross-check for duplication)

From `runtime/recovery/supervisor.py::tick()`:

| State | `last_error` values | Meaning | Touches the bound session? |
|---|---|---|---|
| `suppressed` | `terminal_session`, `task_missing`, `task_not_active`, `claim_changed` | recovery no longer applies; incident abandoned | **no** — recovery *recognises* an already-gone/irrelevant session; it performs no termination |
| `resolved` | `""` | session came back (live, or a successful resume) | no |
| `blocked_validation` (parked) | `quick validation tier failed` | quick tier failed; re-tried on flat interval | no |
| `denied` (parked) | canonical deny summary | one `HOOK_DENIED`/`APPROVAL_REQUIRED`; re-tried on flat interval, `attempt` untouched | no |
| `failed` | `retry_budget_exhausted` | ran out of `backoff_seconds` attempts | no |
| `failed` | `validation_block_persistent` | `_MAX_CONSECUTIVE_VALIDATION_BLOCKS` consecutive quick-tier blocks | no |
| `failed` | `canonical_denial_persistent` | `_MAX_CONSECUTIVE_CANONICAL_DENIALS` (3) consecutive canonical denials with no intervening non-denied outcome | **no** |

**Nothing in `supervisor.py` terminates a session today.** `terminal_session`
suppression is the supervisor *reading* `state["terminal_sessions"]` (populated
elsewhere when a session is externally/operator-terminated) and standing down —
it is the opposite of performing a termination. So any `HarnessService.stop()`
call added here is genuinely new behaviour and duplicates nothing.

### 2b. The one condition that legitimately means "terminate, don't park"

The `canonical_denial_persistent` promotion (`supervisor.py:593-608`) is the
only terminal state whose *cause* is an **active, repeated, deterministic guard
verdict that this session must not continue**: an installed `CANONICAL_RUN` Hook
(`CanonicalRunGuard`, `guard_code="LEASE_EXPIRED"` in the #276/`CASE-378fb326…`
trace) denied the resume 3 consecutive times. That is exactly the roadmap's
"lease permanently unrecoverable" / "denial-ceiling reached" case. At that point
the recovery system has definitively concluded the bound session is operating
outside canonical run state and cannot be brought back — yet today it simply
stops probing and leaves the session in whatever state it is in (for a
`canonical_denial` the session can still be *alive*: `session_is_live()` was
false at tick time, but "not listed as live in the hcom snapshot" is not "process
gone", and a session running against non-canonical lineage is precisely what the
guard is objecting to).

The other two `failed` reasons are **not** good call sites:

- `retry_budget_exhausted` — cause is "we could not get a resume to land", which
  in practice means the session is already dead; `stop()` would almost always
  be a redundant no-op or an error, and it is a *transient*-budget outcome, not a
  guard verdict. Out of scope for this call site.
- `validation_block_persistent` — the quick tier is explicitly advisory-adjacent
  and "never implies environment incompatibility"; escalating it to a
  destructive termination would over-reach its stated authority.

**Smallest legitimate call site:** a single bounded `HarnessService.stop()` call
inside the existing `denials >= _MAX_CONSECUTIVE_CANONICAL_DENIALS` branch at
`runtime/recovery/supervisor.py:593`, immediately before (or after) the
`incident["state"] = "failed"` assignment, gated default-off. No new state, no
new loop, no new scheduler branch, no new persistence — the incident still ends
`failed` / `canonical_denial_persistent` exactly as now; the only addition is
"and route a stop for the binding we already resolved this tick".

### 2c. Larger-than-expected check (stop condition #2)

This is a bounded call in an existing terminal-state branch plus a default-off
boolean threaded through the same three layers `--enforce-canonical-run` already
uses (`cli.py` → `run_recovery_tick_isolated` → `RecoverySupervisor.__init__`).
It requires **no new infrastructure**: the `HarnessService`, the destructive
guard, the guard composition, the binding resolver, and the enforcement gate all
already exist. The stop condition ("requires non-trivial new infrastructure →
STOP and flag") **does not fire**. Proceeding to a full design (not
implementing).

---

## 3. Call construction, gating, fail-closed behaviour

### 3a. Binding / SessionRef / reason

Reuse the resume path's own resolution verbatim. Within the same `tick()`
iteration the canonical-denial branch already has `binding`, `session_ref`,
`binding_reason` in scope from the `_resolve_harness_binding(incident,
session_name)` call at `supervisor.py:533` — the denial branch is only reachable
when that call returned a non-`None` `binding`/`session_ref` (the resume was
actually attempted). So **no second `_resolve_harness_binding` call is needed**;
the existing pair is reused.

- `binding` — the `ExecutionBinding` already built at `supervisor.py:263-270`
  (`task_id`, `run_id`, `worker_id`, `task_revision`, `project_id`,
  `session_id=adapter_session_id`).
- `session_ref` — the `SessionRef` already built at `supervisor.py:271-277`
  (`session_id`, `worker_id`, `adapter="hcom"`, `project_id`,
  `remote_ref=session_name`).
- `reason` — a fixed, closed-vocabulary string constructed at this code path,
  never inferred: `reason = "recovery:canonical_denial_persistent"` (optionally
  suffixed with the deny code already in `error`, e.g.
  `f"recovery:canonical_denial_persistent:{guard_code}"` if the annotation is
  cheaply available — but a bare constant is sufficient and preferable for
  determinism). This mirrors how `HarnessService.stop()` documents `reason` as
  free-form provenance text passed straight to `adapter.stop(binding, reason)`.

The call:

```python
stop_result = self.harness_service.stop(binding, session_ref, reason)
```

wrapped in `try/except Exception` with the same `# noqa: BLE001 - service
failure must not crash the tick` contract as the resume call at
`supervisor.py:537`. The outcome is recorded on the action dict under a new
`harness_stop` key (shape mirrors `harness_resume`:
`{"attempted": bool, "ok": bool, "code": str, "summary": str}` or
`{"attempted": False, "reason": <binding_reason>}`), read by nothing —
audit-only, same discipline as `harness_resume` / `resume_validation`.

### 3b. Default-off gating (mirror `--enforce-canonical-run`)

New, separate opt-in — **not** folded into `--enforce-canonical-run`, because
arming a *destructive* action is a strictly larger authority grant than arming a
*resume-denial*, and the roadmap's own §2c "opt-in / default-off" discipline
applies per-consequence:

1. `RecoverySupervisor.__init__` gains
   `terminate_on_canonical_denial: bool = False` (stored as
   `self._terminate_on_canonical_denial = bool(...)`), documented with the same
   "byte-identical when False" contract as `validation_blocks_resume`.
2. `runtime/recovery/production.py::run_recovery_tick` /
   `run_recovery_tick_isolated` gain
   `terminate_denied_sessions: bool = False`, passed through to the supervisor.
   It is only meaningful when `harness_service is not None` (you cannot call
   `.stop()` without the service) — so, mirroring the existing
   `harness_project_id requires validation_repo_root` guard, raise
   `ValueError("terminate_denied_sessions requires harness_project_id: there is
   no HarnessService to route a stop through otherwise")` when set without
   `harness_project_id`.
3. `runtime/cli.py` `recovery-tick` gains `--terminate-denied-sessions`
   (`action='store_true'`), with `parser.error(...)` if set without
   `--enforce-canonical-run` (same shape as the existing
   `--enforce-validation requires --repo-root` check at `cli.py:807`).

Result: today's every existing invocation — including
`--enforce-canonical-run` alone — is byte-identical. The stop call fires only
under `maps recovery-tick --enforce-canonical-run --harness-project-id …
--repo-root … --binding … --terminate-denied-sessions`.

### 3c. Fail-closed behaviour

"Fail-closed" here means **never terminate a session that cannot be positively
and canonically identified, and never let an inability-to-stop change the
incident outcome**:

- If `binding is None` / `session_ref is None` (cannot happen on this branch
  today, but assert defensively): **do not** call `.stop()`, **do not** invent
  any direct `hcom stop` path (none exists and this note does not add one),
  record `harness_stop={"attempted": False, "reason": binding_reason}`. The
  incident still ends `failed`/`canonical_denial_persistent` — i.e. exactly the
  pre-existing behaviour. The session is left as-is; that is the safe default
  because force-killing an unidentified session is worse than leaving a
  known-denied one parked.
- If `self.harness_service is None` (flag can't be armed without it, but guard
  anyway): skip silently, behaviour unchanged.
- If `HarnessService.stop()` returns a non-ok `OperationResult` — including
  `DESTRUCTIVE_GUARD_REQUIRED` (guard not registered),
  `SESSION_MISMATCH`/`PROJECT_MISMATCH`/`WORKER_MISMATCH` (binding integrity
  failure), or a `_hook_block` from the destructive guard's own veto (operator
  approval required / caller lacks task authority per §7.2): record it on
  `harness_stop`, **do not** retry within the tick, **do not** alter the
  incident state. A guard veto of the *stop* is itself a fail-closed outcome —
  the session is not terminated, matching today's "left parked" behaviour.
- If `HarnessService.stop()` raises: caught, recorded as
  `{"attempted": True, "ok": False, "code": "HARNESS_CALL_ERROR", …}`, tick
  continues.

In every failure mode the observable incident outcome is identical to today.
The *only* new observable effect is the success path: a genuinely
un-recoverable, guard-denied, still-alive session is deterministically
terminated (firing `BEFORE_DESTRUCTIVE_ACTION` → `DestructiveExternalActionGuard`
→ `SESSION_STOPPING` → `HcomHarnessAdapter.stop()`) instead of drifting.

---

## 4. What a later 6.4 exercise would look like (analogous to PR #303 for 6.16)

**Not done here.** Sketch only, for whoever picks up the implementation +
exercise:

1. Implement §3 (separate PR): the bounded `.stop()` call + the
   `--terminate-denied-sessions` opt-in + unit coverage
   (`tests/test_recovery_supervisor.py`: flag off = byte-identical action dicts;
   flag on + fake `HarnessService` = one `stop(binding, session_ref, reason)`
   call on the 3rd consecutive denial, `harness_stop` recorded, incident still
   `failed`; binding-unresolvable and stop-vetoed paths leave state unchanged).
2. Real enforced pass, extending the DEC-003 option B rig
   (`work/notes/2026-09-05-dec003-b-attempt2-real-run-results.md`): bind a live
   hcom session via `maps run bind-session`, kill it, let its lease + the
   silent-stop incident's `resume_after` lapse, then run **three** consecutive
   `maps recovery-tick --enforce-canonical-run --harness-project-id maps-lean
   --repo-root <checkout> --binding <w>=<sess> --terminate-denied-sessions`
   passes. Passes 1-2 produce `resume_denied` (as `CASE-378fb326…` already did);
   pass 3 promotes to `failed`/`canonical_denial_persistent` **and** fires the
   stop.
3. Capture, as the #303-analogous evidence: the pass-3 action dict showing
   `harness_stop: {attempted: true, ok: …, code: …}`, the
   `BEFORE_DESTRUCTIVE_ACTION` hook-chain evidence from
   `DestructiveExternalActionGuard` (task-policy lookup, approve/deny), the
   `SESSION_STOPPING` evidence, and confirmation the hcom session is actually
   gone afterward. Freeze as a regression case per
   `playbook/REPAIR_AND_LEARNING.md`.
4. Only then does 6.4's stated "destructive-action guard callback has never
   fired in a real pass" gap close. Update `CAPABILITY_CHECKLIST.md` row 6.4 at
   that point (not before, and not in the implementation PR unless the exercise
   is in the same PR).

Remaining 6.4 gaps after that exercise (still open, still `IN PROGRESS`): the
write/credential guards and the capability-declaration manifest.

---

## 5. Explicitly OUT OF SCOPE

- **The write / credential / scope guards** (§7.1 scope guard — filesystem
  mutation, writable/forbidden scope). Not touched.
- **The capability-declaration manifest.** Not touched.
- **6.22's `send()` production caller** (`MemoryProvenanceGuard` on
  `BEFORE_SEND`). Separate gap; not touched.
- **Any exercise of `MemoryProvenanceGuard` or `BEFORE_EXTERNAL_ACTION`.**
- **`retry_budget_exhausted` and `validation_block_persistent` as stop call
  sites** — considered and rejected in §2b; not to be added.
- **Any actual runtime code change.** This note changes no file under
  `runtime/`, no test, no `work/roadmaps/CAPABILITY_CHECKLIST.md`, no other
  note, no PR wiring. `git status` after this note shows exactly one new
  untracked file.
- **Flipping 6.4 to DONE / editing the checklist row.** A prior branch already
  overclaimed this once (corrected 2026-09-05); the row stays `IN PROGRESS`
  until §4's exercise runs.

---

## Reproducing section 1's grep claims

```
$ git rev-parse origin/main
c958cf6ba099edf2363e0d66b40f10c2c1174425

$ /usr/bin/grep -rn "\.stop(" runtime/recovery/ --include=*.py | grep -v test
runtime/recovery/production.py:384:    registered. `HarnessService.stop()` fires `BEFORE_DESTRUCTIVE_ACTION`

$ /usr/bin/grep -rn "\.stop(" runtime/ --include=*.py | grep -v test
runtime/harness/adapters/hcom.py:426:            self.backend.stop(str(record["name"]))
runtime/harness/service.py:393:        return adapter.stop(binding, reason)
runtime/harness/contract.py:55:            return self.adapter.stop(self.binding, self.stop_reason)
runtime/policy/destructive_action_guard.py:219:    `HarnessService.stop()` is the first operation that fires
runtime/recovery/production.py:384:    registered. `HarnessService.stop()` fires `BEFORE_DESTRUCTIVE_ACTION`

$ /usr/bin/grep -n "self.harness_service" runtime/recovery/supervisor.py
120:        self.harness_service = harness_service
532:            if self.harness_service is not None:
538:                        result = self.harness_service.resume(binding, session_ref)

$ /usr/bin/grep -n "BEFORE_DESTRUCTIVE_ACTION\|SESSION_STOPPING" runtime/harness/hooks.py
19:    BEFORE_DESTRUCTIVE_ACTION = "before_destructive_action"
25:    SESSION_STOPPING = "session_stopping"
```

---

## Resume prompt

You are picking up after the 6.4 "harness-stop call site" design note
(`work/notes/2026-09-06-harness-stop-callsite-design.md`, branch
`design/6.4-harness-stop-callsite`). The note is design-only and awaits an
independent review under the 3-day operator merge hold. Do **not** merge it and
do **not** edit `CAPABILITY_CHECKLIST.md`. Next action once it is reviewed +
merged: dispatch the implementation PR described in the note's §3 — a single
bounded `HarnessService.stop(binding, session_ref, reason)` call in the
`denials >= _MAX_CONSECUTIVE_CANONICAL_DENIALS` branch of
`runtime/recovery/supervisor.py::tick()` (~L593), gated behind a new default-off
`--terminate-denied-sessions` CLI flag threaded exactly like
`--enforce-canonical-run` (cli.py → production.py → RecoverySupervisor.__init__),
fail-closed per §3c, audit-only `harness_stop` key on the action dict. Then the
§4 real enforced-pass exercise (extend the DEC-003 option B rig, three
consecutive `recovery-tick` passes, capture the `BEFORE_DESTRUCTIVE_ACTION`
firing evidence, freeze as a regression case). Only after that exercise does
6.4's "guard callback never fired in a real pass" gap close.
