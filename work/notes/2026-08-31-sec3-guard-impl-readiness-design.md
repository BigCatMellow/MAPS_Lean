# SEC3 / 6.4 — `DestructiveExternalActionGuard` implementation-readiness (design addendum)

Date: 2026-08-31
Status: design-only. No runtime code, no test, no schema, no checklist change.
Parent: `work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md`
(answers the six "Behavior questions the implementation task must answer",
§ near line 143).

This addendum exists because the parent note's behavior questions were written
against `origin/main@4431b3a` and several of their premises are now **stale**.
Re-verified at this branch head (`origin/main` `03bb8a4`, PR #190 merged):

## What already exists (re-derived at HEAD, rule 14)

- **`HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION`** — a real enum member,
  `runtime/harness/hooks.py:52`, next to `CANONICAL_RUN`.
- **`runtime/policy/destructive_action_guard.py`** — `DestructiveExternalActionGuard`
  (read-only, fail-closed) **and** `register_destructive_external_action_guards()`
  (registers on both `BEFORE_DESTRUCTIVE_ACTION` and `BEFORE_EXTERNAL_ACTION` via
  `registry._register_enforcement(..., HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION)`).
  Re-exported from `runtime/policy/__init__.py`. Tested in
  `tests/test_destructive_external_action_guard.py`.
- The guard's **current** decision table: classification key missing → DENY
  `CLASSIFICATION_REQUIRED`; key present but not `bool` → DENY
  `CLASSIFICATION_INVALID`; `destructive or external` True → **unconditional**
  DENY `ACTION_AUTHORITY_ABSENT`; both explicitly `False` → ALLOW
  `ACTION_NOT_CONSEQUENTIAL`.
- **A task policy model exists** — `runtime/state/policy.py::PolicyStateMixin`.
  `get_task(task_id)["policy"]` carries booleans `destructive_action`,
  `external_side_effect`, `requires_operator_approval`, `security_sensitive`,
  `broad_architecture`, `paid_execution`, plus `approved_by` / `approved_at` /
  `approval_note`. Backed by the `task_policy` table. The six booleans are also
  folded into the task-revision hash input (`runtime/state/integrity.py`
  `_task_definition_conn`, `definition["policy"]`) — but **NOTE (impl
  correction):** that is the revision-hash input, not a column persisted on the
  run manifest. `get_run_manifest()` carries no `policy` key at HEAD, and
  `approved_by`/`approved_at` are live task state only. See the "Implementation
  correction" section below.
- **An operator-approval mechanism exists** —
  `PolicyStateMixin.record_operator_approval(task_id, *, approved_by, note)`
  (event `HUMAN_REAUTHORIZATION_RECORDED`), reachable from the CLI as
  `maps ... approve <task_id> --approved-by … --note …` — the task id is
  **positional** (`runtime/routing/cli.py`, `approve.add_argument("task_id")`).
  `clear_operator_approval` is its inverse.
- **A policy-decision helper exists** — `runtime/policy/evaluator.py`:
  `task_needs_human_reauthorization(task)` returns
  `(bool(policy["requires_operator_approval"]), …)`; `_approved(task)` returns
  `bool(policy["approved_by"] and policy["approved_at"])`.
- **`CanonicalRunGuard`** (`runtime/policy/harness_guard.py`) is the pattern:
  `__init__(source: CanonicalRunSource, *, repo_root)`, reads
  `context["binding"]` via `_extract_binding`, calls `source.get_task(task_id)`
  / `source.get_run_manifest(run_id)`. Success → `HookOutcome(ANNOTATE, …,
  annotations={"guard_code": "CANONICAL_RUN_VERIFIED"}, evidence_refs=(f"task:{id}",
  f"run:{id}"))`. Denials → `_deny(code, reason)` =
  `HookOutcome(DENY, reason, annotations={"guard_code": code})`, **no
  `evidence_refs`**.
- **`build_canonical_harness_service`** (`runtime/recovery/production.py`, PR #180)
  composes the one production `HarnessService`; its docstring **explicitly
  declines** to register the destructive guard ("the two Hook events it would
  subscribe to are fired by nothing in `runtime/`").
- **`HarnessService` fires exactly five events** (`service.py`): `RUN_STARTING`,
  `RUN_STARTED`, `BEFORE_SEND`, `BEFORE_RESUME`, `SESSION_STOPPING`. Each is
  preceded by `_require_canonical_enforcement(event, op)` →
  `CANONICAL_GUARD_REQUIRED` when no guard installed. **Nothing fires
  `BEFORE_DESTRUCTIVE_ACTION` or `BEFORE_EXTERNAL_ACTION`.**

So SEC3's remaining gap is **not** "build the guard / add the enum member" —
that is done. It is: (a) the guard's `ACTION_AUTHORITY_ABSENT` unconditional
deny is now wrong (a policy source *does* exist); (b) no production operation
fires either event or gates on the second enforcement; (c) the guard is not
composed anywhere. The six answers below close exactly that.

---

## Q1 — Exact source of "task policy" the guard consults

**Decision: `task["policy"]` from `PolicyStateMixin.get_task()` (envelope
booleans equivalently readable from the run-manifest snapshot; approval state
from the live task only). No new field, not `ExecutionBinding`.**

`ExecutionBinding`'s own docstring: "Scope and policy are intentionally not
copied here … callers must re-check them." So the guard gains a `source`
dependency exactly like `CanonicalRunGuard` — the caller's existing `TaskStore`,
duck-typed — and reads policy through it.

Replace the guard's unconditional `ACTION_AUTHORITY_ABSENT` branch with:

| Condition (when `destructive` or `external` is declared `True`) | Outcome |
|---|---|
| declared `destructive` and `policy["destructive_action"]` is `False` | DENY `ACTION_OUTSIDE_TASK_ENVELOPE` |
| declared `external` and `policy["external_side_effect"]` is `False` | DENY `ACTION_OUTSIDE_TASK_ENVELOPE` |
| matching envelope flag(s) set, `policy["requires_operator_approval"]` and not `_approved(task)` | DENY `OPERATOR_REAUTHORIZATION_ABSENT` (see Q6) |
| matching envelope flag(s) set, approval satisfied or not required | ALLOW `ACTION_WITHIN_TASK_ENVELOPE` (+ `evidence_refs`, see Q5) |

Read the **envelope booleans from the run manifest snapshot**
(`source.get_run_manifest(run_id)["policy"]`) — it is the tamper-evident copy
bound to the run — and the **approval state from the live task**
(`source.get_task(task_id)["policy"]`), because the manifest snapshot omits
`approved_by`/`approved_at`. Reuse `runtime.policy.evaluator._approved` and
`task_needs_human_reauthorization` rather than re-deriving them.

`context["binding"]` supplies `task_id` and `run_id` (mirror
`CanonicalRunGuard._extract_binding`; add a `BINDING_REQUIRED`-equivalent
`CLASSIFICATION_BINDING_REQUIRED` deny when a declared consequential action
arrives with no binding).

**File/callsite for the impl PR:** `runtime/policy/destructive_action_guard.py`
— `DestructiveExternalActionGuard.__init__` (add `source`), `__call__` (extract
binding, look up policy, apply the table above). No schema change, no new
authority store — the authority model already exists.

---

## Q2 — First concrete production operation + who sets the classification

**Decision: `HarnessService.stop()` fires `BEFORE_DESTRUCTIVE_ACTION` before
`adapter.stop(...)`, and `HarnessService.stop` itself sets
`context["destructive"] = True, context["external"] = False` as a fixed
literal.**

`stop` is *definitionally* a destructive operation (irreversible termination of
in-flight session state) — hard-coding the two booleans in the `stop` code path
is declaration-at-the-operation, not inference (no argument sniffing, no
regex). This is consistent with the parent note's "the code about to perform a
consequential operation already knows what it is about to do".

Mirror the canonical-enforcement gate exactly:

- Add `_require_destructive_enforcement(event, operation)` next to
  `_require_canonical_enforcement` (`service.py:64`): returns
  `OperationResult.failure("DESTRUCTIVE_GUARD_REQUIRED", …, retry=UNSAFE)` when
  `not self.hooks.has_enforcement(event, HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION)`.
- In `stop()` (`service.py:327-344`): call it for
  `HookEvent.BEFORE_DESTRUCTIVE_ACTION` **before** the existing
  `_require_canonical_enforcement(SESSION_STOPPING, "stop")`, then
  `self.hooks.run(BEFORE_DESTRUCTIVE_ACTION, self._context("stop", …,
  destructive=True, external=False))` and `_hook_block("stop", before)` on
  `not before.permitted` — reusing the existing `_hook_block` /
  `_context` machinery (extend `_context` to accept the two booleans for this
  event).
- Register the guard in `build_canonical_harness_service`
  (`runtime/recovery/production.py`) via
  `register_destructive_external_action_guards(registry,
  DestructiveExternalActionGuard(task_reader))`, and update that function's
  docstring — the "fired by nothing in `runtime/`" statement is retired for the
  destructive event by this PR.

`BEFORE_EXTERNAL_ACTION` gets **no** firing call site in this slice: no
production operation crosses the process/host boundary through a registry-fired
hook today. The enum member and the both-events registration already exist and
stay; only the destructive event becomes live.

**File/callsite for the impl PR:** `runtime/harness/service.py` (`stop()` +
`_require_destructive_enforcement`); `runtime/recovery/production.py`
(composition + docstring).

**UNKNOWN / judgment call for `gobi`:** `HarnessService.stop()` has **no
production caller today** (production only calls `.resume()` via the recovery
supervisor). Wiring the gate into `stop()` is real, composed, tested code with
no live caller — exactly the state `.resume()` was in before PR #160/#180. The
alternative is to ship only Q1+Q5 (the guard's policy wiring) + the composition
registration in this PR and make the `stop()` firing call site its own
follow-up. **Recommendation: include `stop()` now** — it is the smallest honest
firing site and keeps the guard from being dead code, and the parent note's
own two-step precedent (guard PR, then call-site PR) is about the *real
external caller*, which here is "something that calls `HarnessService.stop()` in
production" (a `maps recovery-tick` kill path) — still a separate follow-up.

---

## Q3 — One combined guard vs. two split `HookEnforcement` members

**Decision: keep the one combined `HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION`
(already in code). No split.**

The Q1 table branches per-flag: a declared `destructive` action is checked
against `policy["destructive_action"]`, a declared `external` one against
`policy["external_side_effect"]`. One guard object evaluating two independent
booleans against two independent policy flags does **not** conflate them — the
conflation the parent note worried about would only arise if the *policy source*
forced a single verdict, and it does not.

Revisit only if a future requirement needs genuinely independent *enforcement
lifecycles* (e.g. "external actions are always denied regardless of whether a
guard is installed" — a different `has_enforcement` default per event). Nothing
today needs that. **No impl change.**

---

## Q4 — Missing-key behavior

**Decision: DENY, code `CLASSIFICATION_REQUIRED` (already in code, already
tested). Fail-closed, matching `CanonicalRunGuard`'s `BINDING_REQUIRED`.**

`tests/test_destructive_external_action_guard.py` already covers the guard-unit
case (missing key, non-bool value). The impl PR adds a **service-path** test:
a composed `HarnessService.stop()` call must always produce a context carrying
both booleans (the service hard-codes them per Q2), so on that path the keys are
never absent — the test asserts the service supplies them and that a guard
receiving a hand-built context with a missing key still denies
`CLASSIFICATION_REQUIRED` (`HOOK_DENIED` at the service boundary).

**File/callsite for the impl PR:** no guard change; new test in
`tests/test_harness_service.py` (or the composition-root test).

---

## Q5 — Where the guard decision is recorded as evidence

**Decision: mirror `CanonicalRunGuard` exactly. On ALLOW,
`evidence_refs=(f"task:{task_id}", f"run:{run_id}",
f"action_classes:{','.join(classes)}")`. On DENY, keep
`annotations={"guard_code": …, "action_classes": …}` and no `evidence_refs`
(consistent with every `CanonicalRunGuard` denial). No new evidence stream.**

Downstream propagation already exists and needs no change: `_hook_block` copies
`result.evidence_refs` into the `OperationResult`
(`service.py:137`); `HookRunResult.evidence_refs` aggregates across invocations
(`hooks.py:162`); `runtime/run_record.py:92-98` already captures
`destructive_action` / `external_side_effect` / `approved_by_present` into the
Run Record. A future recovery *kill* path that calls `stop()` should record a
`harness_stop` action-dict field analogous to the supervisor's existing
`harness_resume` — but that belongs to the call-site follow-up, not this PR.

**File/callsite for the impl PR:**
`runtime/policy/destructive_action_guard.py` — add `evidence_refs` to the ALLOW
return only.

---

## Q6 — `REQUIRE_APPROVAL`: attach to an existing mechanism, or DENY-only?

**Decision: DENY-only for the first call site. Code `OPERATOR_REAUTHORIZATION_ABSENT`.
Do NOT return `HookDirective.REQUIRE_APPROVAL`.**

An operator-approval *record* mechanism exists (`record_operator_approval` +
`maps … approve`), so this is **not** an operator-authority decision that has to
be escalated — the authority model is settled. What is missing is a
**control-flow bridge**: `HookDirective.REQUIRE_APPROVAL` →
`_hook_block` → `OperationResult.failure("APPROVAL_REQUIRED", …)`, and **nothing
catches `APPROVAL_REQUIRED` and turns it into an operator prompt that later
resumes the operation**. In the recovery supervisor `APPROVAL_REQUIRED` is in
`_CANONICAL_DENIAL_CODES` and is treated identically to a hard denial (no
fallback, consumes a retry attempt). So `REQUIRE_APPROVAL` today is a
worse-labelled `DENY` with an implied escape hatch that does not exist.

**Operator workflow with DENY-only:** operation denied
`OPERATOR_REAUTHORIZATION_ABSENT` → operator runs
`maps … approve <T> --approved-by <id> --note <why>` (task id positional) → re-run the
operation → guard re-reads `policy["approved_by"]` via `_approved(task)` → ALLOW.
Deterministic, uses only existing surfaces. Document this in the impl PR
description and in the guard's module docstring.

**X that must exist before `REQUIRE_APPROVAL` is meaningful:** a
hook-outcome → operator-prompt → resume bridge at the call site — a component
that receives `APPROVAL_REQUIRED` from `HarnessService.stop()` (or a recovery
kill path), surfaces it to an operator, and re-invokes the operation once
`record_operator_approval` lands. **Naming it here; not designing it.** It is a
separate roadmap item (call it SEC3 Half 3 / "async approval bridge").

**File/callsite for the impl PR:** `runtime/policy/destructive_action_guard.py`
— the `OPERATOR_REAUTHORIZATION_ABSENT` branch in `__call__` (Q1 table row 3).

---

## SEC3 first-guard impl: in scope / out of scope

### In scope — ONE guard, ONE enum member (both already exist), ONE firing event

| Change | File | Q |
|---|---|---|
| `DestructiveExternalActionGuard.__init__(source)` + `context["binding"]` extraction | `runtime/policy/destructive_action_guard.py` | Q1 |
| Replace unconditional `ACTION_AUTHORITY_ABSENT` with the envelope/approval table (`ACTION_OUTSIDE_TASK_ENVELOPE`, `OPERATOR_REAUTHORIZATION_ABSENT`, `ACTION_WITHIN_TASK_ENVELOPE`); reuse `runtime.policy.evaluator._approved` / `task_needs_human_reauthorization` | `runtime/policy/destructive_action_guard.py` | Q1, Q6 |
| `evidence_refs` on the ALLOW outcome only | `runtime/policy/destructive_action_guard.py` | Q5 |
| `_require_destructive_enforcement(event, op)` + `DESTRUCTIVE_GUARD_REQUIRED` | `runtime/harness/service.py` | Q2 |
| `stop()` fires `BEFORE_DESTRUCTIVE_ACTION` with `{destructive: True, external: False}` before `adapter.stop()` | `runtime/harness/service.py` | Q2, Q4 |
| Register the guard in `build_canonical_harness_service`; update its docstring | `runtime/recovery/production.py` | Q2 |
| Tests: guard table via temp-file `TaskStore`; composed-service `stop()` deny/allow; missing-key service-path assertion | `tests/test_destructive_external_action_guard.py`, `tests/test_harness_service.py`, `tests/test_recovery_composition_root.py` | Q1, Q4, Q5 |
| 6.4 / SEC3 evidence text (no status flip — capability-declaration-manifest half still NOT STARTED) | `work/roadmaps/CAPABILITY_CHECKLIST.md` (impl PR only) | — |

### Out of scope

- **A `BEFORE_EXTERNAL_ACTION` firing call site** — no production boundary-crossing
  operation runs through a registry-fired hook today. Enum member + both-events
  registration stay; the external event stays dormant.
- **A real production caller of `HarnessService.stop()`** (a `maps recovery-tick`
  kill path) — separate follow-up, mirrors the RnS design/call-site split.
- **The async approval bridge** (Q6 "X") — `REQUIRE_APPROVAL` stays unused until
  it exists.
- **Splitting the enforcement member** (Q3 = no).
- **Any new policy field, new authority store, operator-identity registry** — the
  `task_policy` model + `record_operator_approval` already cover it.
- **Inferred / static-analysis / model-judged classification** (parent note
  non-goal).
- **Any daemon, scheduler, or background scan.**
- **`runtime/state/schema.sql`** — unchanged; `task_policy` is sufficient.

---

## Implementation correction (PR #<impl>, rule 14 re-verify at HEAD `ee342c5`)

Q1 proposed reading the envelope booleans from a run-manifest policy snapshot
(`source.get_run_manifest(run_id)["policy"]`) for tamper-evidence, and approval
state from the live task. Re-verified at the implementing HEAD:
**`get_run_manifest()` returns no `policy` key** — `runtime/state/integrity.py`
`_task_definition_conn` builds a `definition["policy"]` only as an input to the
task-revision hash; it is never written as a `run_manifests` column. That
snapshot does not exist.

Resolution, no schema change (STOP condition not hit — `task_policy` suffices):
the guard reads **both** the envelope booleans and the approval state from the
live task via `source.get_task(task_id)["policy"]`. `run_id` from the binding is
still used, but only in `evidence_refs`. This is strictly within the "no new
policy field / authority store / schema change" boundary; adding a manifest
policy snapshot would be the schema change the note forbids.

## Roadmap impact

Does not complete 6.4 / SEC3. Makes `DestructiveExternalActionGuard`
implementation-ready by binding it to the existing `task_policy` authority model
and wiring `HarnessService.stop()` as the first `BEFORE_DESTRUCTIVE_ACTION`
firing site. SEC3's capability-declaration-manifest half stays NOT STARTED.
`work/roadmaps/CAPABILITY_CHECKLIST.md` is unchanged by this note.

---

## Resume prompt

You are implementing the SEC3 / roadmap 6.4 first destructive-action guard wiring
for MAPS_Lean. Work in your own git worktree off `origin/main`;
`cd ~/Projects/MAPS_Lean` first and `git fetch origin main`.

Source of truth: `work/notes/2026-08-31-sec3-guard-impl-readiness-design.md`
(this note) and its parent `work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md`.
Re-verify every callsite/grep claim at your own HEAD (rule 14) before relying on
it — this note already found the parent note's premises stale once.

Implement exactly the "In scope" table:

1. `runtime/policy/destructive_action_guard.py`: add a `source` parameter to
   `DestructiveExternalActionGuard.__init__` (the caller's `TaskStore`,
   duck-typed like `CanonicalRunSource`). In `__call__`, extract
   `context["binding"]` (mirror `CanonicalRunGuard._extract_binding`; deny
   `CLASSIFICATION_BINDING_REQUIRED` if absent when a consequential action is
   declared). Replace the unconditional `ACTION_AUTHORITY_ABSENT` deny with:
   read envelope booleans from `source.get_run_manifest(run_id)["policy"]` and
   approval state from `source.get_task(task_id)["policy"]`; DENY
   `ACTION_OUTSIDE_TASK_ENVELOPE` when the matching flag
   (`destructive_action` / `external_side_effect`) is False; DENY
   `OPERATOR_REAUTHORIZATION_ABSENT` when `requires_operator_approval` and not
   `runtime.policy.evaluator._approved(task)`; else ALLOW
   `ACTION_WITHIN_TASK_ENVELOPE` with
   `evidence_refs=(f"task:{task_id}", f"run:{run_id}", f"action_classes:{classes}")`.
   Keep `CLASSIFICATION_REQUIRED` / `CLASSIFICATION_INVALID` exactly as they are.
   Do NOT return `HookDirective.REQUIRE_APPROVAL`.
2. `runtime/harness/service.py`: add `_require_destructive_enforcement(event,
   operation)` returning `DESTRUCTIVE_GUARD_REQUIRED` when
   `not self.hooks.has_enforcement(event, HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION)`.
   In `stop()`, call it for `HookEvent.BEFORE_DESTRUCTIVE_ACTION` before the
   existing canonical check, then `self.hooks.run(BEFORE_DESTRUCTIVE_ACTION,
   self._context("stop", …, destructive=True, external=False))` and
   `_hook_block("stop", before)` on `not before.permitted`. Extend `_context` to
   carry the two booleans.
3. `runtime/recovery/production.py`: in `build_canonical_harness_service`,
   `register_destructive_external_action_guards(registry,
   DestructiveExternalActionGuard(task_reader))`. Update the docstring — the
   "fired by nothing in runtime/" claim is now false for the destructive event.

MUST NOT: add a `BEFORE_EXTERNAL_ACTION` firing site; add a real production
caller of `HarnessService.stop()`; design an async approval bridge; split
`HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION`; add any policy field / authority
store / operator-identity registry; touch `runtime/state/schema.sql`; use
inferred classification.

Tests (one blocking foreground call — no Monitor, no background):
`python3 -m unittest tests.test_destructive_external_action_guard
tests.test_harness_service tests.test_harness_hooks
tests.test_recovery_composition_root tests.test_recovery_supervisor`.
Round-trip policy + approval through a real temp-file `TaskStore`; assert
`ACTION_OUTSIDE_TASK_ENVELOPE`, `OPERATOR_REAUTHORIZATION_ABSENT` (before
`maps approve`) → `ACTION_WITHIN_TASK_ENVELOPE` (after), and that a composed
`HarnessService.stop()` denies with `HOOK_DENIED` when the guard denies and with
`DESTRUCTIVE_GUARD_REQUIRED` when no guard is registered. `python3 -m
runtime.smoke` must exit 0. Push before any full-suite run; rely on CI.

Update the 6.4 / SEC3 evidence text in `work/roadmaps/CAPABILITY_CHECKLIST.md`
in the same PR (no status flip — the capability-declaration-manifest half is
still NOT STARTED). Document the DENY-only operator workflow (`maps … approve
<task_id> --approved-by … --note …` then re-run — task id positional) in the PR
description and the guard module docstring.

Then: PR into `main` (never push to main). Request independent review per
`reference_committee_review` and add a bound
`work/reviews/pr-<N>-review-evidence.md`. Do NOT self-merge. Report the PR
number to `gobi` via hcom when open and green.

Stop conditions: if wiring the policy lookup forces a schema change or a new
authority field, STOP and flag `gobi` — the `task_policy` model should be
sufficient. If the PR starts building the async approval bridge or a real
`stop()` caller, STOP — both are separate follow-ups.
