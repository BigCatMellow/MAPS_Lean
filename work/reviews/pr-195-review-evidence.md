# PR #195 — canonical-denied tick() state — independent review evidence

reviewer: maps-lean-hemo
head_sha: 778148e778fde9ec85514f5a634e71ac8839a9d0
independent: true
summary: APPROVE. The §2b slice matches the PR #189 design note exactly — a canonical denial no longer consumes a transient retry attempt and parks the incident in a distinct non-terminal `denied` state; genuine budget exhaustion still terminates as `retry_budget_exhausted`. The `_MAX_CONSECUTIVE_CANONICAL_DENIALS` ceiling is IN the note's design (§2b bullet 2 + Resume prompt), not scope creep. NO schema change — `canonical_denials` rides the existing JSON blob. §3c UNKNOWN resolved correctly against `integrity.py`. All 5 mutations against the denied-branch logic are caught. Diff in-bounds; no MUST-NOT violated.

## Method

Independent review in own worktree. Original review was performed at PR head
`53771d56a06fc686ff69e425989635b9b79a2f4b`; this evidence is re-bound to the
rebased code commit `a5f719cdea8d86af6f62ecde5e1616cb71e8f0a3` (branch
`canonical-denied-tick-state` rebased onto `origin/main` `5b76458` after #193 /
#194 / #196 merged — a mechanical rebase; the only conflict was
`CAPABILITY_CHECKLIST.md` rows H4/H5/E4/6.4/6.5, resolved by keeping #194's 6.4
row + #196's "Design note pending" clauses AND appending this branch's
"Updated 2026-08-31 … §2b" clauses, per coordinator instruction). The
supervisor/store code delta is byte-identical to the reviewed state.
Post-rebase re-run: `runtime.smoke` exit 0, `tests.test_recovery_supervisor` 47
passed. Every callsite claim re-verified at HEAD (rule 14). Source of truth:
`work/notes/2026-08-31-canonical-enforcement-first-exposure-design.md` §2b + §3c.

## 1. Denied branch — CONFIRMED (item 2)

`runtime/recovery/supervisor.py` `tick()`, new block after the
`_CANONICAL_DENIAL_CODES` routing (`canonically_denied` flag set at the
`resume_denied` branch):

- **`attempt` NOT incremented on canonical denial.** The new block ends with
  `continue`, which skips the unconditional loop tail (`attempt += 1;
  incident["attempt"] = attempt; …`). Verified by reading — the tail is only
  reached by the non-denied path. Mutation M1 (adding `incident["attempt"] =
  attempt + 1` into the denied block) is caught (3 failures).
- **Distinct terminal-ish state.** `incident["state"] = "denied"` with
  `incident["last_error"] = error` (the deny code / summary). `"denied"` was
  added to the processable set (`{"scheduled", "probing", "denied"}`) so the
  incident stays resumable on a flat interval
  (`silent_stop_probe_delay_seconds`, matching the note's "reuse
  `silent_stop_probe_delay_seconds` or `backoff_seconds[0]`"). Mutation M5
  (removing the `incident["state"] = "denied"` assignment) is caught (2
  failures). Mutation M2 (making the denied path set `state="failed"` /
  `last_error="retry_budget_exhausted"`) is caught (2 failures + 1 error).
- **`retry_budget_exhausted` STILL fires for genuine exhaustion.** The
  pre-existing budget-exhaustion branch (`attempt >= len(self.backoff_seconds)`)
  is untouched by this PR; the non-denied path still flows through
  `attempt += 1` and can reach it. The only addition to that tail is
  `incident["canonical_denials"] = 0` (streak reset). Mutation M4 (removing that
  reset) is caught (1 failure).

## 2. Scope scrutiny — `_MAX_CONSECUTIVE_CANONICAL_DENIALS` — JUDGMENT: IN the design, NOT scope creep (item 3)

The note's §2b bullet 2 reads verbatim: *"Keep a separate, small ceiling on
consecutive canonical denials — e.g. a `denied` incident that has been denied N
times in a row (N≈3) … goes to `state = "failed"`,
`last_error = "canonical_denial_persistent"` … This ceiling is independent of the
transient `backoff_seconds` budget."* The note's Resume prompt repeats it.

The impl matches exactly: `_MAX_CONSECUTIVE_CANONICAL_DENIALS = 3`;
`canonical_denials` counter on `RecoveryIncident`; `>= 3` →
`state = "failed"`, `last_error = "canonical_denial_persistent"`, `action =
"fail"`; reset to 0 on any non-denied outcome. Mutation M3 (`>=` → `>`) is
caught (1 failure). **This is the design, not creep.**

## 3. NO schema change — STOP condition NOT triggered (item 4)

`canonical_denials` is a new `@dataclass` field on
`runtime/recovery/store.py::RecoveryIncident` (`int = 0`, default). `RecoveryStore`
persists state via `asdict()` + `json.dumps()` to `.maps/state/recovery.json`
(`store.py:53,57-80`) — a JSON blob, **no SQL**. `git diff` touches no
`runtime/state/schema.sql`. In `tick()` the field is read defensively as
`int(incident.get("canonical_denials", 0))`, so pre-existing incident JSON
without the key deserialises cleanly. **STOP condition not triggered.**

## 4. §3c UNKNOWN resolution — CONFIRMED correct (item 5)

Verified against `runtime/state/integrity.py` at HEAD:

- `_task_definition_conn` (the input set for `compute_task_revision`) SELECTs
  from `tasks`: `task_id, project_id, title, outcome, task_type, owner, risk,
  decision_authority, verification, evidence_expected, review_required,
  escalation, max_attempts` + 7 child tables + `task_policy` + environment.
- `runtime/state/execution.py::claim_task` recovery path UPDATE mutates exactly:
  `status, claimed_by, lease_expires_at, heartbeat_at, attempt, updated_at`.
- **Intersection is empty.** None of the recovery-mutated columns feed
  `compute_task_revision`. (`max_attempts` is in the revision set but recovery
  bumps `attempt`, not `max_attempts`.)

So claim-recovery does **not** bump `task_revision`, and the PR's
`docs/CONTROL_PLANE_SETUP.md` statement ("Claim-recovery does **not** change the
run manifest's `task_revision` … `recover + re-tick` is a complete workflow; no
'start a fresh run' step is required") is accurate.

## 5. docs §5 workflow — CONFIRMED matches note (item 6)

`docs/CONTROL_PLANE_SETUP.md` §5 new subsection "Canonical enforcement:
remediating a denied resume": the `denied` state description, `LEASE_EXPIRED` as
the dominant first-exposure denial, `maps heartbeat` cannot renew an expired
lease, `maps claim <task-id> --worker-id <ORIGINAL worker id> --lease-seconds N`
then re-run, the worker-id-must-match-manifest constraint, and the
`ATTEMPT_LIMIT` / `max_attempts` edge — all match note §3a/§3b/§3d.

## 6. Checklist — CONFIRMED, no status flip (item 7)

E4, H5, 6.5, 6.16 each gain an "Updated 2026-08-31 (impl of §2b)" paragraph
describing the distinct `denied` state and (H5/6.16) the docs workflow. Post-rebase
the E4 / 6.5 rows also retain #196's "Design note pending:
`work/notes/2026-08-31-resume-validation-gate-design.md`" clause (both clauses
present, #196's first). **All four rows stay `IN PROGRESS`** — no status-token
change on any row.

## 7. MUST-NOT checks — ALL CLEAR (item 8)

| Prohibition | Result |
|---|---|
| Guard / `HarnessService` / `HookRegistry` change | NONE. Code delta = `store.py`, `supervisor.py` only (+ tests, docs, checklist). `harness_guard.py`, `harness/service.py`, `harness/hooks.py` untouched. |
| Non-canonical retry-semantics change | NONE. The non-denied loop tail gains only `incident["canonical_denials"] = 0`; `attempt`, `state`, `last_error`, backoff scheduling for the transient path are byte-unchanged. |
| `--enforce-canonical-run` enabled by default | NO. `runtime/recovery/production.py` is not in the diff. |

## 8. Mutation testing — 5/5 CAUGHT

Module: `tests.test_recovery_supervisor` (47 tests). Each mutation applied to
`runtime/recovery/supervisor.py`, suite run, then file restored.

| # | Mutation | Result |
|---|---|---|
| M1 | Denied path consumes an attempt: insert `incident["attempt"] = attempt + 1` into the `canonically_denied` block | **CAUGHT** — FAILED (failures=3) |
| M2 | Denied terminates as budget exhaustion: `incident["state"] = "denied"` → `state="failed"` + `last_error="retry_budget_exhausted"` | **CAUGHT** — FAILED (failures=2, errors=1) |
| M3 | Ceiling comparison loosened: `denials >= _MAX_CONSECUTIVE_CANONICAL_DENIALS` → `denials >` | **CAUGHT** — FAILED (failures=1) |
| M4 | Streak never resets: delete `incident["canonical_denials"] = 0` from the non-denied loop tail | **CAUGHT** — FAILED (failures=1) |
| M5 | Distinct-state assignment removed: drop `incident["state"] = "denied"` | **CAUGHT** — FAILED (failures=2) |

## 9. Suite + smoke

- `python3 -m runtime.smoke` → exit 0 (at `53771d5` and re-run at `a5f719c`).
- `python3 -m unittest`:
  - `tests.test_recovery_supervisor` — 47 passed (both SHAs)
  - `tests.test_recovery_composition_root` — 13 passed
  - `tests.test_recovery_production_trigger` — 49 passed

## 10. Diff-in-bounds

5 files: `docs/CONTROL_PLANE_SETUP.md` (+44), `runtime/recovery/store.py` (+7),
`runtime/recovery/supervisor.py` (+64/-2), `tests/test_recovery_supervisor.py`
(+105/-1), `work/roadmaps/CAPABILITY_CHECKLIST.md` (evidence text only). No
`schema.sql`, no guard/harness code, no `main` touch, no `production.py`.

## Verdict

APPROVE. No CHANGES REQUESTED. Distinct non-attempt-consuming `denied` state
confirmed; genuine exhaustion still routed to `retry_budget_exhausted`; the
consecutive-denial ceiling is note-specified design; no schema change (STOP
condition not triggered); §3c resolved correctly; 5/5 mutations caught; diff
in-bounds.
