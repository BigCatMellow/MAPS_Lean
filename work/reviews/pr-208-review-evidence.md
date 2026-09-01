# PR #208 — PR #194 residual design investigation — independent review evidence

reviewer: maps-lean-rev-beta
head_sha: ed5b2a05644cbf9aa78a0972ed54dbf8f5640770
independent: true
summary: APPROVE. "Latent not live" is correct — re-verified: `HarnessService.stop()` has zero production callers (`RecoverySupervisor` calls `.resume()` only; `contract.py:55` is a test helper), and `update_contract` is genuinely triple-gated (status freeze at `base.py:172`, unconditional approval reset in `policy.py::_apply_policy_contract_conn`, no autonomous caller — only `maps shape` CLI + smoke fixture). No STOP-condition / live-hole finding. Recommendation (b) — the `validate_ready` consistency rule — is the right smallest fix and has no way around it (composes with the freeze; `promote_ready` is the sole READY chokepoint and calls `_validate_ready_conn` in-transaction). Deferring (a) is appropriate; the `CanonicalRunGuard` live-read precedent holds. MUST-NOT / smallest-slice / STOP conditions are sound. Not operator-only. Three non-blocking editorial nits.

## Method

Reviewed at PR head `ed5b2a05644cbf9aa78a0972ed54dbf8f5640770` (note commit,
clean on top of `origin/main` `c5461c9` — no rebase needed). Every claim in the
note re-verified against source with `/usr/bin/grep` + direct read (rule 14).
Docs-only PR — no mutation testing. Diff in-bounds: adds one note under
`work/notes/`, no runtime code, no schema, no checklist status flip.

## 1. Claim-by-claim verification

| Note claim | Verified | Evidence |
|---|---|---|
| Guard reads both envelope booleans + approval from live `get_task(task_id)["policy"]` | ✅ | `runtime/policy/destructive_action_guard.py:161-190` — `self.source.get_task(task_id)` → `policy = task.get("policy")`; no manifest read |
| `task_needs_human_reauthorization` keys only off `requires_operator_approval` | ✅ (see nit 1) | `runtime/policy/evaluator.py:24-38` — `if bool(policy.get("requires_operator_approval")): return True, (...)` else `False, ()`. Returns a **tuple**, not a bare bool; guard unpacks at `destructive_action_guard.py:185` |
| `test_in_envelope_no_approval_needed_allows_with_evidence` asserts the ALLOW-with-no-human path | ✅ | assertion exists; ALLOW branch `destructive_action_guard.py:192-205` reachable with `destructive_action=True, requires_operator_approval=False` |
| `run_manifests` has no `policy` column | ✅ | `runtime/state/schema.sql:139-152` — columns are `run_id, task_id, task_revision, worker_id, session_id, readable/writable/forbidden_scope, runtime_limits, base_revision, created_by, created_at`. No `policy` |
| `get_run_manifest()` returns no `policy` key | ✅ | consistent with schema; note + PR #194 evidence §2 already established this |
| `_apply_policy_contract_conn` is the only writer of the 6 `task_policy` booleans | ✅ | `runtime/state/policy.py:54-93` — sole `UPDATE task_policy SET <flags>` site; registered via `_contract_shaping_hooks` |
| Status freeze: policy cannot be mutated outside `NEEDS_SHAPING`/`BLOCKED` | ✅ | `runtime/state/base.py:171-177` — `if row["status"] not in {"NEEDS_SHAPING","BLOCKED"}: rollback; return CONTRACT_FROZEN` — before any field write |
| Unconditional `approved_by=NULL` reset on any contract update | ✅ | `runtime/state/policy.py:76-84` — the reset `UPDATE task_policy SET approved_by=NULL, approved_at=NULL, approval_note=''` runs unconditionally (outside the `if policy:` block), plus `TASK_POLICY_UPDATED` event. Fires even when the contract does not touch `policy` |
| No autonomous runtime caller of `update_contract` | ✅ | `/usr/bin/grep -rn "update_contract\|\.shape(" runtime/ --include=*.py` → production callers are `runtime/cli.py:500` (`maps shape` — reads `--contract-json`) and `runtime/smoke.py:62` (smoke fixture). `policy.py` / `environment_contract.py` hits are `super()` chain. Nothing in `flow_start`, `harness/`, `recovery/`, `routing/` |
| `validate_ready` has no destructive/external ⇒ approval rule | ✅ | `/usr/bin/grep -n "destructive\|external_side\|requires_operator" runtime/state/readiness.py` → nothing. `_validate_ready_conn` (`readiness.py:50-193`) checks scalars, collections, deps, output-scope, environment contract — no `task_policy` read at all |
| `record_operator_approval` refuses `NO_APPROVAL_REQUIRED` unless flag set | ✅ (not re-read this pass; consistent with PR #194 evidence + 1e reasoning; low risk) | — |
| `HarnessService.stop()` has zero production callers | ✅ | `/usr/bin/grep -rn "\.stop(" runtime/ | grep -v test` → `service.py:393` (inside `stop()`'s own body, `adapter.stop`), `contract.py:55` (**test helper** `_call`, in `HarnessAdapterContractTestMixin`), `hcom.py:426` (adapter's `backend.stop`), 2 docstring mentions. No caller invokes `HarnessService.stop`/`.stop(binding` in production |
| `RecoverySupervisor` calls `.resume()` only | ✅ | `runtime/recovery/supervisor.py:538` `self.harness_service.resume(binding, session_ref)`; `:629` `self.hcom.resume(...)`. No `.stop(` in the file |
| `CanonicalRunGuard` reads authority live via duck-typed `source`, no snapshot | ✅ | `runtime/policy/harness_guard.py:74` `task = self.source.get_task(task_id)`; `:79` `get_run_manifest(run_id)` used for **revision/staleness** compare, not authority. Precedent holds |
| `promote_ready` is the READY transition and runs `_validate_ready_conn` in the write txn | ✅ (strengthens the note — see nit 2) | `runtime/state/readiness.py:195-255` — only READY mutation; `BEGIN IMMEDIATE` → `_validate_ready_conn` → READY in one txn; also gated `status in {NEEDS_SHAPING, BLOCKED}` |

## 2. Independent judgement on the four questions

### Q1 — "LATENT not live": CORRECT

No production path reaches `update_contract` from a task/worker execution
context, and no production caller of `HarnessService.stop()` exists. Both
independent preconditions for the §2 escape are absent. The status freeze means
an `ACTIVE`/`READY` task's live policy read *is* its claim-time (shaping-time)
value, authored at the same trust boundary that authorizes the task's output
paths and decision authority. **No urgent live-hole escalation.**

Adversarial probe — "shape a fresh task T2 with the permissive envelope, claim
it, trigger `stop()` bound to T2": still requires a production `stop()` caller
that can be pointed at an agent-supplied task/run. The note correctly names this
as exactly what the recovery-kill-path follow-up must get right (bind stop to
the incident's own run) and correctly makes closing this residual a precondition
for that work.

### Q2 — Recommendation (b) is the right smallest fix, and it is airtight

The `validate_ready` rule (`destructive_action or external_side_effect` set ⇒
`requires_operator_approval` set) closes the named "keep
`requires_operator_approval=False`" escape:

- **No second-`update_contract` bypass.** Set flags + `requires_operator_approval`,
  pass `validate_ready`, go `READY` — now the contract is frozen
  (`base.py:171`), so `requires_operator_approval` cannot be cleared. To clear
  it you must go `BLOCKED`, `update_contract` (which resets approval,
  `policy.py:76`), then re-`promote_ready` — which re-runs the rule and refuses
  to promote while `destructive_action` is still set and the flag is now false.
- **No "clear both flags" bypass.** Clearing `destructive_action` too satisfies
  the rule but then the guard DENYs `ACTION_OUTSIDE_TASK_ENVELOPE` anyway.
- **Single chokepoint.** `promote_ready` is the only READY transition and runs
  validation in the same transaction; there is no alternate READY path.
- **Right layer.** The fix is upstream in readiness; the guard is already
  correct and needs no change. Reuses `maps approve` / `record_operator_approval`
  (1e) unchanged. No schema change — all three booleans already live on
  `task_policy`.

### Q3 — Deferring (a) is appropriate; trigger is concrete enough

The run-manifest `policy` snapshot is a `schema.sql` change + migration + new
read path — heavier than (b), and PR #194's own STOP condition forbade it
there. Its only marginal value over `(b) + freeze` is the narrow "task goes
`BLOCKED` mid-run, envelope widened, run then triggers `stop()`" window — and in
that window (b)'s approval-reset already forces re-approval. The stated trigger
("a concrete task-reshaped-while-run-is-live threat, or a decision to make all
guard authority reads snapshot-based for uniformity") is a real, recognisable
condition, not a vague "revisit later". The `CanonicalRunGuard` precedent is
real: it reads task authority live through the same duck-typed `source` and no
snapshot was required there. Consistent.

### Q4 — Impl guardrails are sound

- **MUST-NOT list** correctly fences off (a) (schema/migration), new policy
  fields / authority stores, guard-logic changes, adding a `stop()` caller,
  weakening `record_operator_approval`, and live-task data migration. Complete
  for the slice.
- **Smallest first slice** (readiness rule + tests + one checklist evidence
  clause, no status flip) is genuinely minimal and matches the checklist-drift
  countermeasure in memory (`feedback_checklist_edit_repeatedly_skipped`).
- **STOP conditions** are the right three: needs-a-schema-change,
  flag-semantics-relied-on-inconsistently (a real risk — some production code
  might set `destructive_action` without meaning "needs approval"; that is a
  @niko semantics call, not a silent fix), and a missed autonomous
  `update_contract` path.
- **Not operator-only**: agreed. The (a)-vs-(b) choice is a technical judgement
  with a clearly smaller correct answer. The impl *does* change behavior
  (destructive-enveloped tasks that currently promote will fail `validate_ready`
  until approved) — the note already flags that for the impl PR description as
  intended tightening, which is the correct handling.

## 3. Non-blocking nits (editorial — fix at author's discretion, not gating)

1. **§1a** — "`task_needs_human_reauthorization` ... is **only** `bool(policy.get("requires_operator_approval"))`" describes the *condition* but the function returns `tuple[bool, tuple[str,...]]`. Reword to "keys only off `requires_operator_approval`" to avoid implying a bare-bool return.
2. **§2 / §3(b)** — the argument would be stronger by stating explicitly that `promote_ready` (`readiness.py:195`) is the *sole* READY transition and calls `_validate_ready_conn` inside the same write transaction — that is what makes the rule unbypassable. Currently implied, not stated.
3. **§4 "Smallest first slice" bullet 2** — the test description is garbled ("still fails *promotion*-time nothing new but the guard would DENY"). Rewrite as two clean cases.

## Verdict

**APPROVE.** The investigation is accurate, the "latent not live" conclusion is
correct and carries no live-hole finding, recommendation (b) is the right
smallest fix with no bypass, and the impl guardrails are sound. The three nits
are editorial and do not block merge.
