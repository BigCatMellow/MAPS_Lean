# PR #199 — opt-in resume-validation gate (SEC/6.5, first slice of #196) — independent review evidence

reviewer: maps-lean-lola
head_sha: b592bcc75f32dea8f16f512561137056089d5462
independent: true
summary: APPROVE. The slice matches design note #196 §Q5 exactly — one supervisor constructor kwarg, one `tick()` gate block placed BEFORE any harness/hcom resume call, one module ceiling const, and a `--enforce-validation` CLI flag (requires `--repo-root`) threaded through `production.py` with exact parity to `--enforce-canonical-run`. Q2 respected: the gate is in `tick()`, NOT a `make_validation_hook()` registration at `BEFORE_RESUME` — grep confirms no `BEFORE_RESUME` hook / `make_validation_hook` call was added. Fully disjoint from the merged #195 (`d5c99ed`): distinct state `blocked_validation`, counter `validation_blocks`, ceiling `_MAX_CONSECUTIVE_VALIDATION_BLOCKS`, label `validation_block_persistent`, action `resume_blocked_validation` — zero symbol overlap, and the gate `continue`s before `attempt` is ever touched. 5/5 mutations against the gate decision + ceiling are caught. No schema change (`validation_blocks` rides the JSON blob). E4/H4/6.5 evidence text updated, no status flip. `python3 -m runtime.smoke` exit 0.

## Method

Own detached worktree at PR #199 head `bcb8ff7` (branch `impl/resume-validation-gate`,
base `24e0139` — which is #197). `git fetch origin` first. Reviewed content as-is
per dispatch; coordinator rebased the merge-order conflicts against `d5c99ed`
(the merged #195) to the code commit bound above (`b592bcc`) — supervisor.py
module-const block keeps both `_MAX_CONSECUTIVE_CANONICAL_DENIALS` and
`_MAX_CONSECUTIVE_VALIDATION_BLOCKS` + the `_REPROCESSABLE_STATES` union, the
`tick()` guard uses `_REPROCESSABLE_STATES`, docs keeps both new subsections, and
the E4/6.5 checklist rows carry both the #199 gate text and the disjoint #195
§2b canonical-denial sentence. Every callsite re-verified by `/usr/bin/grep` /
file read at HEAD (rule 14). Disjointness checked against
`git show origin/main:runtime/recovery/supervisor.py` (the merged #195).

## 1. Slice matches note §Q5 — CONFIRMED

| §Q5 item | Impl | Verdict |
|---|---|---|
| One constructor kwarg `validation_blocks_resume: bool = False` | `supervisor.py` `RecoverySupervisor.__init__` — added, stored `self._validation_blocks_resume` (note said `self._validation_blocks`; immaterial naming) | ✓ |
| One `tick()` gate immediately after the `validate_for_run` call | `supervisor.py` — new block right after the advisory `resume_validation` assignment, `if self._validation_blocks_resume and _quick_validation_failed(resume_validation):` | ✓ |
| `action="resume_blocked_validation"`, `state="blocked_validation"`, `last_error`, reschedule on `silent_stop_probe_delay_seconds`, do NOT increment `attempt`, append action dict, `continue` | all present, exactly | ✓ |
| Add `"blocked_validation"` to the re-processable state set | `_REPROCESSABLE_STATES = {"scheduled", "probing", "blocked_validation", "denied"}` const, applied at both the `tick()` loop guard and `_open_incident_for` | ✓ (also folds in #195's `"denied"` — clean union) |
| No `EnvironmentSpec` / validation-type import or name in the file | `git show` diff adds no such import; `_quick_validation_failed` uses only `Mapping`/`Any`. `test_supervisor_source_never_names_the_declared_environment_spec_type` still passes. | ✓ |
| Persistent-block ceiling (recommended) | `_MAX_CONSECUTIVE_VALIDATION_BLOCKS = 3`; `blocks >= ceiling` → `state="failed"`, `last_error="validation_block_persistent"`, `action="fail"` | ✓ |
| `RecoveryIncident.validation_blocks: int = 0` dataclass field, JSON store | `store.py` — added, comment explicitly notes "no schema change (the SQL task DB is untouched by RnS state)" | ✓ |
| `--enforce-validation` flag → `run_recovery_tick(..., validation_blocks_resume=True)` → supervisor; argparse-require `--repo-root` | `cli.py`: `store_true` flag + `parser.error` if set without `--repo-root`; `production.py`: `enforce_validation` kwarg on both `run_recovery_tick` and `run_recovery_tick_isolated`, plus a defense-in-depth `ValueError` if `enforce_validation and validation_repo_root is None`. Exact parity with the `--enforce-canonical-run` / `harness_project_id` plumbing. | ✓ |

`_quick_validation_failed` correctly returns `True` only for
`{"attempted": True, "passed": False}` — verified against
`production.py::RunBoundValidator.validate_for_run`, which returns
`{"attempted": True, "passed": bool, ...}` or `{"attempted": False, "reason": ...}`
with `passed` **absent**. `{"attempted": False}`, `None` (no validator), and
`{"attempted": False, "reason": "validation_error"}` (the tick() exception
branch) all fall through → never block. Matches note Q6.4.

## 2. Q2 compliance — gate in `tick()`, not `BEFORE_RESUME` — CONFIRMED

`git show HEAD | grep "BEFORE_RESUME\|make_validation_hook\|HookRegistry\|register.*hook"`
→ the only hits are in commit-message / checklist **prose**. **No hook
registration, no `HookRegistry` construction, no `make_validation_hook` call is
added to any runtime file.** The gate is a plain conditional in `tick()`, placed
strictly before the `resolved = False` / `self.harness_service` block and
therefore before any `HarnessService.resume()` or `self.hcom.resume()` call.
This is exactly the note's Q2 rejection of the `BEFORE_RESUME` hook.

## 3. Disjointness from #195 (`d5c99ed`) — CONFIRMED

| Concern | #195 (merged) | #199 | Collision? |
|---|---|---|---|
| Parked state | `"denied"` | `"blocked_validation"` | none |
| Counter field | `canonical_denials` | `validation_blocks` | none |
| Ceiling const | `_MAX_CONSECUTIVE_CANONICAL_DENIALS` | `_MAX_CONSECUTIVE_VALIDATION_BLOCKS` | none |
| Terminal label | `canonical_denial_persistent` | `validation_block_persistent` | none |
| Non-terminal action | `resume_denied` | `resume_blocked_validation` | none |
| Trigger point | post-harness | pre-harness (before `resolved = False`) | #199 is strictly upstream |
| `attempt` handling | `continue` before `attempt += 1` | `continue` before `attempt += 1` | both non-attempt-consuming, independent |

The only shared touch point is the re-processable-state set — resolved in the
rebase to a single `_REPROCESSABLE_STATES` constant containing the union
(`scheduled`, `probing`, `blocked_validation`, `denied`). **No logic overlap, no
behavioral interaction.** Ordering at merged HEAD: advisory validation → #199
gate (continue if blocked) → #199 streak reset → harness block → #195 branch
(continue if denied) → `if not resolved` → tail.

## 4. Behavior assertions — muzi's tests cover all; mutations confirm

`tests/test_recovery_supervisor.py::ResumeValidationGateTests` (new, 7 tests) +
`ResumeValidationAdvisoryTests` (existing, unmodified):

- flag OFF + failing tier → `action == "resume"`, `state == "probing"`, `validation_blocks == 0`.
- flag ON + `quick` failure → `action == "resume_blocked_validation"`, no resume call, `state == "blocked_validation"`, `attempt == 0` unchanged, rescheduled at `now + silent_stop_probe_delay_seconds`.
- flag ON + passing tier → `action == "resume"`, `attempt == 1`.
- flag ON + `{"attempted": False}` (`no_spec_bound` / `budget_exceeded` / `validation_error`) → never blocks.
- blocked incident re-processed next pass, passing tier resets the streak.
- 3 consecutive blocks → `action == "fail"`, `reason == "validation_block_persistent"`, `state == "failed"`, `attempt == 0` throughout; ceiling independent of the transient retry budget.

### Mutation testing — 5/5 CAUGHT

| # | Mutation | Result |
|---|---|---|
| M(a) | Gate ignores the flag: `if self._validation_blocks_resume and ...` → `if True and ...` | **CAUGHT** — FAILED (failures=2, errors=1) |
| M(b) | Gate consumes a transient attempt: add `incident["attempt"] = int(incident.get("attempt",0))+1` into the block branch | **CAUGHT** — FAILED (failures=4) |
| M(c) | Block on validation PASS instead of failure: `result.get("passed") is False` → `... is True` | **CAUGHT** — FAILED (failures=5) |
| M(d) | Ceiling loosened: `blocks >= _MAX_CONSECUTIVE_VALIDATION_BLOCKS` → `blocks >` | **CAUGHT** — FAILED (failures=5) |
| M(e) | Distinct-state assignment collides with #195: `incident["state"] = "blocked_validation"` → `... = "denied"` | **CAUGHT** — FAILED (failures=2) |

Baseline (post-rebase, at `b592bcc`): `tests.test_recovery_supervisor` 73 passed
(combined with `tests.test_recovery_composition_root`); `python3 -m runtime.smoke`
→ exit 0.

## 5. Checklist + no-schema-change — CONFIRMED

`git show HEAD -- work/roadmaps/CAPABILITY_CHECKLIST.md`: E4, H4, and 6.5 each
carry the #199 "first slice implemented" text; the rebase additionally preserved
the disjoint #195 §2b canonical-denial sentence on E4 and 6.5. `| … | IN PROGRESS |`
unchanged on all rows — **no status flip**. `git show --stat` touches no
`runtime/state/schema.sql`; `validation_blocks` is a `@dataclass` default on
`RecoveryIncident`, persisted via `asdict()` + `json.dumps()` and read
defensively as `int(incident.get("validation_blocks", 0))`.

## 6. MUST-NOT checks — ALL CLEAR

| Prohibition | Result |
|---|---|
| `EnvironmentSpec.validation.enforcement` field | NONE — not in diff; named as deferred in the checklist text. |
| `BEFORE_RESUME` hook / `make_validation_hook` registration | NONE (§2). |
| Default-on flag | NO — `validation_blocks_resume: bool = False`; CLI `store_true` off by default; `production.py` raises if `enforce_validation` without a repo root. |
| Non-validation retry-semantics change | NONE — the transient `attempt` / backoff path is byte-unchanged; the gate `continue`s before it. |
| Capability STATUS flip | NONE (§5). |

## 7. Minor observations — non-blocking

1. `incident["last_error"] = "quick validation tier failed"` is a prose string
   where #195 used the deny-code convention. Cosmetic — machine-readable outcome
   is in `action` / `reason`. Not a defect.
2. If an incident has BOTH a pending validation failure and a pending canonical
   denial, #199's gate wins (parks in `blocked_validation`, never reaches the
   harness call where #195 would fire). Correct by design — do not resume into a
   broken environment. Worth a one-line note mention; not a code change.

## Verdict

**APPROVE.** No CHANGES REQUESTED. Slice matches note §Q5; Q2 respected; fully
disjoint from the merged #195; 5/5 mutations caught; no schema change; no status
flip; `attempt` counter never consumed by the gate. Merge-order conflicts
against `main` resolved by the coordinator during merge-prep (keep-both, bound
to `b592bcc`).
