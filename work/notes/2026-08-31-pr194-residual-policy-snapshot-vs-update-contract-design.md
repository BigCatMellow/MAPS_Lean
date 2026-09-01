# PR #194 residual — run-manifest policy snapshot vs. `update_contract` gating (design investigation)

Date: 2026-08-31
Status: design-only. No runtime code, no test, no schema change, no checklist
status flip. Design review only.

Resolves the residual `work/reviews/pr-194-review-evidence.md` §2 recorded as a
follow-up: before `HarnessService.stop()` gains a production caller (the
"recovery kill path"), decide whether the `DestructiveExternalActionGuard`'s
live-task policy read needs a run-manifest `policy` snapshot **(a)**, or whether
`update_contract` is already gated enough that a task cannot self-authorize a
destructive `stop()` **(b)** — and what the smallest form of the answer is.

All facts re-verified at `origin/main` `c5461c9` (rule 14).

---

## 1. Re-verified facts

### 1a. What the guard reads

`runtime/policy/destructive_action_guard.py::DestructiveExternalActionGuard.__call__`
reads **both** the envelope booleans and the approval state from the **live**
task: `task = self.source.get_task(task_id)` → `policy = task["policy"]` →

- `destructive and not policy["destructive_action"]` → DENY `ACTION_OUTSIDE_TASK_ENVELOPE`
- `external and not policy["external_side_effect"]` → DENY `ACTION_OUTSIDE_TASK_ENVELOPE`
- `task_needs_human_reauthorization(task) and not _approved(task)` → DENY `OPERATOR_REAUTHORIZATION_ABSENT`
- else → ALLOW `ACTION_WITHIN_TASK_ENVELOPE`

`task_needs_human_reauthorization` (`runtime/policy/evaluator.py`) is **only**
`bool(policy.get("requires_operator_approval"))`. So a task with
`destructive_action = True` and `requires_operator_approval = False` takes the
ALLOW path with **no human in the loop** — and this is a currently-asserted
test expectation
(`tests/test_destructive_external_action_guard.py::test_in_envelope_no_approval_needed_allows_with_evidence`,
line 138).

### 1b. The run-manifest `policy` snapshot does not exist

`runtime/state/schema.sql` `run_manifests` columns: `run_id, task_id,
task_revision, worker_id, session_id, readable_scope, writable_scope,
forbidden_scope, runtime_limits, base_revision, created_by, created_at`. No
`policy` column. `runtime/state/integrity.py::get_run_manifest()` returns
`dict(row)` + decoded scopes + `context_refs` + `worktree` — **no `policy`
key**. `_task_definition_conn` builds `definition["policy"]` from `task_policy`
**only** as an input to the task-revision hash (`_task_revision_conn`); it is
never persisted on the manifest. (Matches the #194 note's "Implementation
correction" and this review's §2.)

### 1c. `update_contract` — every path that can set `task_policy` booleans

`runtime/state/policy.py::PolicyStateMixin._apply_policy_contract_conn` is the
only writer of the six `task_policy` booleans. It runs as a
`_contract_shaping_hook` of `update_contract`. Three independent gates apply:

1. **Status freeze.** `runtime/state/base.py::update_contract` line 172: if
   `row["status"] not in {"NEEDS_SHAPING", "BLOCKED"}` → `CONTRACT_FROZEN`,
   transaction rolled back. A `READY`, `ACTIVE`, `READY_FOR_REVIEW`,
   `CHANGES_REQUESTED`, or `DONE` task's policy **cannot be mutated at all**.
2. **Approval reset on every policy update.** `_apply_policy_contract_conn`
   unconditionally runs `UPDATE task_policy SET approved_by = NULL, approved_at
   = NULL, approval_note = ''` and appends `TASK_POLICY_UPDATED`, on *any*
   contract update (even one that does not touch `policy`). So a task can never
   simultaneously (i) widen its envelope booleans and (ii) retain a recorded
   `maps approve`. Any self-mutation of the contract drops approval.
3. **No autonomous runtime caller.** `grep -rn "update_contract\|\.shape(" runtime/
   --include=*.py` → the only production callers are `runtime/cli.py:500`
   (`maps shape <task_id> --contract-json …`) and `runtime/smoke.py` (smoke
   fixture). **No** path in `flow_start`, `harness/`, `recovery/`, `routing/`,
   or any execution flow calls `update_contract`. A worker executing a task has
   no code path that mutates any task's policy envelope.

### 1d. There is no readiness consistency rule linking the flags

`runtime/state/readiness.py` `validate_ready` checks collections, dependencies,
output-scope conflicts, and the *environment* contract — but has **no** rule
that `destructive_action` / `external_side_effect` implies
`requires_operator_approval`. `grep -n "destructive\|external_side\|requires_operator"
runtime/state/readiness.py` → nothing. A task can be promoted `READY` with
`destructive_action = True, requires_operator_approval = False`.

### 1e. `record_operator_approval` gate

`PolicyStateMixin.record_operator_approval` refuses (`NO_APPROVAL_REQUIRED`)
unless `requires_operator_approval` is set. So today an operator *cannot* even
pre-approve a destructive task that lacks the reauthorization flag — there is
nothing to approve.

---

## 2. Is the residual live or latent?

**Latent.** Two independent future conditions must both hold before any escape
is reachable:

- **`HarnessService.stop()` has zero production callers.** It is the guard's
  only firing site. The one production consumer of a `HarnessService` is
  `RecoverySupervisor` (`harness_service=` param, wired only by
  `build_canonical_harness_service`), and it calls **`self.harness_service.resume(...)`
  only** (`runtime/recovery/supervisor.py:538`) — never `.stop(...)`. So the
  guard is composed but never fires in production. The recovery-kill-path
  follow-up is what adds a `.stop()` caller.
- **The freeze blocks self-service escalation on an in-flight task.** To make a
  destructive `stop()` bound to task T succeed, T's live policy must carry
  `destructive_action = True`. Once T is `READY`/`ACTIVE` its contract is frozen
  (1c-1), so the permissive envelope must have been authored at **shaping**
  time, by whoever ran `maps shape` — the same trust boundary that authorizes
  T's output paths, risk, and decision authority. The executing worker does not
  re-shape its own task.

The theoretical escape ("an autonomous agent shapes a fresh task T2 with
`destructive_action = True, requires_operator_approval = False`, promotes and
claims it, then triggers a `stop()` bound to T2") requires a production `stop()`
caller that can be pointed at an agent-chosen task/run. The recovery-kill-path
caller will bind the stop to *the incident's own run*, not an arbitrary
agent-supplied one — but that binding discipline is exactly what the impl of
that follow-up must get right, and is why this residual must be closed first.

**No STOP-condition finding: `update_contract` is not exploitable from a task
context today.** The status freeze + approval-reset + absence of any autonomous
caller mean there is no live self-escalation path.

---

## 3. (a) vs (b)

### (b) — "`update_contract` is operator-gated": **mostly already true, one real gap**

Of the residual the review names ("a task that can freely call `update_contract`
to set `destructive_action = True` while keeping `requires_operator_approval =
False`"): the "freely call `update_contract`" half is already closed — status
freeze (1c-1) + no autonomous caller (1c-3) + approval reset (1c-2). What
remains open is **1d**: nothing forces a destructive/external envelope to also
carry the reauthorization flag, so a task *shaped that way from the start*
reaches the guard's ALLOW path with no `maps approve` ever required.

Closing 1d is a **readiness consistency rule** — no schema change, no new
authority field, no new store:

> In `validate_ready`: if `task_policy.destructive_action` or
> `task_policy.external_side_effect` is set, then
> `task_policy.requires_operator_approval` must also be set — otherwise the task
> is `AGI FAIL — NEEDS_SHAPING` with reason
> `destructive/external envelope requires operator reauthorization`.

Effect: every task whose envelope permits a destructive/external action must go
through `maps approve <task_id>` before it can be `READY` (and 1e already allows
that once the flag is set). The guard's `OPERATOR_REAUTHORIZATION_ABSENT` branch
then becomes reachable for exactly the class of tasks it was written for, and
the "keep `requires_operator_approval = False`" escape the review describes is
structurally impossible.

This also composes with the freeze: an approved destructive task that goes
`BLOCKED` mid-run and is re-shaped drops its approval (1c-2) and must re-pass
`validate_ready` (which now re-checks the rule) and be re-approved.

### (a) — run-manifest `policy` snapshot: **defer, gate on a concrete scenario**

A `run_manifests.policy_snapshot` column populated at `create_run_manifest` and
read by the guard instead of the live task would make the envelope
**tamper-evident** across the claim→stop window. But:

- It is a `schema.sql` change + migration + a new read path — the #194 note's
  own STOP condition explicitly forbade doing it in that PR, and it is heavier
  than (b).
- Its marginal value over `(b) + the existing freeze` is small: for any
  `ACTIVE` task the live read *is* the claim-time value (frozen). The only
  window (a) closes that (b) does not is "task goes `BLOCKED` during a live run,
  someone widens the envelope, the run then triggers `stop()`" — and in that
  window (b)'s approval-reset already forces re-approval, and `CanonicalRunGuard`
  (the sibling guard, same live-read pattern) would also need the same treatment
  for consistency.
- `CanonicalRunGuard` sets the precedent: it reads authority live via the same
  duck-typed `source`, and no snapshot was deemed necessary there.

Record (a) as a follow-up **gated on a concrete "task reshaped while its run is
live" threat** (or on a decision to make all guard authority reads
snapshot-based for uniformity). Not slice 1.

### Recommendation

**(b), as the `validate_ready` consistency rule in §3(b).** Smallest change that
closes the named residual; no schema change; reuses `maps approve` / `1e`
unchanged. (a) deferred with an explicit trigger.

---

## 4. For the eventual implementation

### Smallest first slice

1. **`runtime/state/readiness.py`** — add the 1d consistency rule to
   `validate_ready`: `destructive_action or external_side_effect` set ⇒
   `requires_operator_approval` must be set; else a `NEEDS_SHAPING` reason.
   Read from the `task_policy` row already available in that method's scope.
2. **Tests** — `tests/test_readiness*.py` (or `tests/test_task_policy*.py`): a
   task with `destructive_action = True, requires_operator_approval = False`
   fails `validate_ready` with the new reason; the same task with
   `requires_operator_approval = True` (and no `maps approve` yet) still fails
   *promotion*-time nothing new but the guard would DENY
   `OPERATOR_REAUTHORIZATION_ABSENT`; after `maps approve` it is `READY` and the
   guard ALLOWs. A non-consequential task (both flags false) is unaffected.
3. **`work/roadmaps/CAPABILITY_CHECKLIST.md`** — one clause on 6.4 / SEC3
   evidence text noting the readiness rule now backs the guard's envelope read;
   **no status flip**.

### MUST NOT

- Add a `run_manifests` column / migration / any `schema.sql` change (that is
  option (a), deferred).
- Add a new policy field, authority store, or operator-identity registry.
- Change `DestructiveExternalActionGuard` decision logic or any of its guard
  codes — the fix is upstream in readiness, the guard is already correct.
- Add a production caller of `HarnessService.stop()` or the recovery kill path
  — separate follow-up.
- Make `record_operator_approval` auto-fire, or weaken its `NO_APPROVAL_REQUIRED`
  gate (1e).
- Retro-invalidate existing `READY` tasks beyond what `validate_ready`
  naturally does on next validation (no data migration of live tasks).

### STOP conditions (flag @niko)

- The readiness rule turns out to need a schema change or a new column to
  express (it should not — `task_policy` has all three booleans).
- Adding the rule breaks existing non-consequential-task fixtures in a way that
  reveals the flag semantics are already relied on inconsistently elsewhere
  (i.e. some production code sets `destructive_action` without meaning "needs
  approval") — that is a semantics question for @niko, not a silent fix.
- Investigation during impl finds a real autonomous path to `update_contract`
  on an in-flight task that this note missed — urgent, not a readiness rule.

### Not an operator-only decision

The (a)-vs-(b) choice is a technical judgment with a clear smaller answer
((b), §3). No OPERATOR DECISION callout. The *impl* does change behavior
(destructive-enveloped tasks that currently promote will fail `validate_ready`
until approved) — flag that in the impl PR description, but it is the intended
tightening, not an authority question.

---

## 5. Checklist annotation (optional, in-bounds)

6.4 row, appendable to the evidence text, no status change:

> PR #194 residual (`pr-194-review-evidence.md` §2 — destructive envelope
> integrity resting on `update_contract` authorization) scoped in
> `work/notes/2026-08-31-pr194-residual-policy-snapshot-vs-update-contract-design.md`:
> latent not live (freeze + approval-reset + no autonomous caller); fix is a
> `validate_ready` rule (`destructive_action`/`external_side_effect` ⇒
> `requires_operator_approval`), no schema change; a run-manifest policy
> snapshot is deferred.

---

## Resume prompt

You are implementing the PR #194 residual fix for MAPS_Lean (roadmap 6.4 /
SEC3). Work in your own git worktree off `origin/main`; `git fetch origin main`
first. Re-verify every callsite at your HEAD (rule 14).

Source of truth: this note
(`work/notes/2026-08-31-pr194-residual-policy-snapshot-vs-update-contract-design.md`),
`work/reviews/pr-194-review-evidence.md` §2, and the files it cites:
`runtime/state/readiness.py::validate_ready`, `runtime/state/policy.py`,
`runtime/policy/destructive_action_guard.py`,
`runtime/policy/evaluator.py::task_needs_human_reauthorization`,
`runtime/state/schema.sql` (`task_policy`).

Implement exactly the §4 "Smallest first slice": add to `validate_ready` the
rule that `task_policy.destructive_action` or `task_policy.external_side_effect`
being set requires `task_policy.requires_operator_approval` to be set, else an
`AGI FAIL — NEEDS_SHAPING` reason; tests; one checklist evidence clause, no
status flip.

MUST NOT: touch `schema.sql` / add a `run_manifests` column (that is the
deferred option (a)); add a policy field / authority store / operator-identity
registry; change `DestructiveExternalActionGuard` logic or guard codes; add a
production `HarnessService.stop()` caller or the recovery kill path; weaken
`record_operator_approval`'s `NO_APPROVAL_REQUIRED` gate.

Tests (one blocking foreground `python3 -m unittest` — no Monitor, no
background): `tests.test_readiness*` (or the readiness test module) +
`tests.test_task_environment_contract tests.test_destructive_external_action_guard
tests.test_routing_policy`. `python3 -m runtime.smoke` exits 0. Push before any
full-suite run; rely on CI.

Then: PR into `main` (never push to main). Do NOT spawn your own reviewer —
ping @niko, niko dispatches. Independent review per `reference_committee_review`
(no mutation required — small readiness rule, but a targeted mutation set
against the new predicate is welcome); reviewer commits
`work/reviews/pr-<N>-review-evidence.md`. Do NOT self-merge. Report the PR
number to @niko.

STOP conditions: if the rule needs a schema change to express, or if adding it
reveals production code that sets `destructive_action` without meaning "needs
approval", or if you find a real autonomous `update_contract` path on an
in-flight task — STOP and flag @niko.
