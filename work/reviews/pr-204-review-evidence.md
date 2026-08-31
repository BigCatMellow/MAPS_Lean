# PR #204 — SEC/6.24 environment-report production source & cache, first slice — independent review evidence

reviewer: maps-lean-kimi
head_sha: 95c5de5fdded6a9315ad5412d6a66a085312759a
independent: true
verdict: PASS
summary: Implements exactly the Q6 "smallest slice" of `work/notes/2026-08-31-environment-report-production-source-cache-design.md` and folds in the 4 non-blocking PR-201 observations. All 7 scope items verified by direct read at HEAD `15bad08` (rule 14, `/usr/bin/grep`). No schema change, no new table/migration, no daemon, no new `PolicyDecision` kind, no 6.24/E1/E2/E3 status flip, router stays pure (consumes reports only), `maps claim` piggyback not routed into the recorder. `required_for_routing=0` path is behaviourally unchanged; `DRIFTED`/`UNKNOWN`/any fresh report satisfies the hold; only absence of a fresh report trips it; a fresh `INCOMPATIBLE` still routes to `environment_incompatible`. All 6 targeted test modules green (106 tests), `python3 -m runtime.smoke` exits 0. 7/7 mutants caught. Two non-blocking findings (stale docstring; a transitively-covered test gap). Not the author (author = maps-lean-laze).

## Method

Reviewer's own worktree on branch `feat/6.24-env-report-recorded-slice1` at HEAD `15bad08f00372f7e225ad370ef04220068bc8079`; base `git merge-base HEAD origin/main` = `98620e4` (= `origin/main`). `git status` clean, no staged reverts. Every callsite / column / import claim re-derived with `/usr/bin/grep` + `sed` at HEAD (rule 14).

Sources of truth: `work/notes/2026-08-31-environment-report-production-source-cache-design.md` (Q6 slice, 8 MUST-NOTs, 3 STOP conditions), `work/reviews/pr-201-review-evidence.md` §3/§4/§6 (obs1–4).

Files read at HEAD: `runtime/flow_start.py`, `runtime/routing/environment_reports.py`, `runtime/routing/router.py`, `runtime/routing/cli.py`, `runtime/state/environment_contract.py`, `runtime/state/environment.py`, `runtime/environment/safety.py`, `runtime/environment/fingerprint.py`, `runtime/policy/evaluator.py`, `work/roadmaps/CAPABILITY_CHECKLIST.md`, and the 5 changed test modules.

Diff: `git diff origin/main...HEAD` — 11 files, +649/-28. `runtime/state/schema.sql` and every `*.sql` untouched (verified `git diff --stat -- '*.sql'` empty).

## Scope verification

### 1. flow_start step 4 wires the containment-checked wrapper (obs1) — PASS

`runtime/flow_start.py:41` imports `from runtime.environment.safety import inspect_local_environment` — **not** `runtime.environment.fingerprint`'s raw `inspect_local_environment` (`fingerprint.py:251`). `runtime/environment/safety.py:139` `inspect_local_environment` first calls `_validate_dependency_containment` (`safety.py:18`, resolves `repo_root`, rejects dependency inputs outside the repo) and its docstring: "Collect a local fingerprint without following dependency inputs outside the repo." The new `_record_environment_evidence` docstring (`flow_start.py:31-36`) states this choice explicitly ("NOT the raw `runtime.environment.fingerprint` inspector"). Step 4 (`flow_start.py:155-167`) fires only when `store.get_task(task_id)["environment"]` is set; a recorder/inspection failure returns `_failed("environment_evidence", …)` (`flow_start.py:166`), covered by `test_flow_start_fails_when_environment_spec_ref_is_missing`. No new probing capability: `inspect_local_environment` and `record_run_environment_evidence` both pre-exist and are composed unchanged.

### 2. ONE shared freshness helper (obs2, rule 12) — PASS

`runtime/routing/environment_reports.py:85` `_freshness_diagnostic(...)` is the sole freshness predicate. `select_fresh_environment_reports` (caller-supplied, line ~157) and `select_recorded_environment_reports` (recorded, line ~250) both call it with the same keyword contract. The old inline predicate block in `select_fresh_environment_reports` (spec-hash / task-revision / future / stale checks) is deleted in the diff and replaced by the single call. No second copy of the predicate logic anywhere (`/usr/bin/grep -n "spec_hash_mismatch\|report_stale\|produced_at_in_future"` → only inside `_freshness_diagnostic`).

### 3. `environment_report_required` hold = policy_gate fallback, no new PolicyDecision kind (obs3) — PASS

`runtime/routing/router.py:132-152`: an `else:` on the `if environment_report is not None:` block. When no report is projected and `task["environment"]["required_for_routing"]` is truthy, it appends `RouteRecommendation("policy_gate", task_id, reasons=("environment_report_required",))` and `continue`s — structurally identical to the `environment_incompatible` fallback directly above it. `PolicyDecision` is unchanged: `/usr/bin/grep -n 'PolicyDecision(' runtime/policy/evaluator.py` shows only the pre-existing `"reject"` / `"require_approval"` / `"allow"` kinds. `"environment_report_required"` is a reason string on an existing `RouteRecommendation` route (`"policy_gate"`), not a new outcome kind. `evaluate_assignment` signature untouched.

### 4. `required_for_routing=0` byte-identical; DRIFTED/UNKNOWN non-rejecting; only absence trips; fresh INCOMPATIBLE still gated — PASS

- The `else` branch reads `task.get("environment")` and does nothing unless `required_for_routing` is truthy; `isinstance(..., Mapping)` guards a missing/None contract. `required_for_routing` unset/0/false → falls through to worker selection exactly as before. Tests: `test_router_missing_report_not_blocking_when_not_required`, `test_default_environment_contract_does_not_change_missing_report_routing`.
- A fresh report of any state (present in `environment_reports`) skips the `else` entirely, so `DRIFTED`/`UNKNOWN`/`COMPATIBLE` all satisfy the hold. Test: `test_router_required_task_routes_once_fresh_report_exists` (subtests `COMPATIBLE`, `DRIFTED`).
- Only `environment_report is None` reaches the hold. Tests: `test_router_holds_required_task_with_no_report` (empty mapping), `test_router_holds_required_task_before_first_flow_start` (mapping `None`) — obs4.
- Fresh `INCOMPATIBLE` is handled by the pre-existing `if` branch → `("environment_incompatible",)`, before the `else` is reached. Test: `test_router_required_task_still_gated_on_incompatible_report`.
- Recorded selector never converts stale/malformed/missing evidence into an incompatibility: `test_stale_recorded_report_is_dropped_not_converted` (→ `report_stale`, `reports == {}`), `test_recorded_incompatible_report_is_projected_not_swallowed` (a genuine recorded `INCOMPATIBLE` is projected, not dropped).

### 5. No schema change / table / migration; no daemon; router pure; no status flip; claim not routed to recorder — PASS

- No `*.sql` diff; no new `CREATE TABLE`; `run_environment_evidence` (run-scoped, insert-only, immutability trigger) and `task_environment.{spec_ref,max_age_seconds,required_for_routing,allow_older_task_revision}` all pre-exist.
- No new thread/process/scheduler; `select_recorded_environment_reports` is a synchronous read-side projection over `store.trace_task` (read-only) + `load_environment_spec`.
- Router computes no fingerprint: `/usr/bin/grep -n "inspect_local_environment\|fingerprint" runtime/routing/router.py` → only the pre-existing `from runtime.environment.fingerprint import CompatibilityState` enum import. `evaluate_assignment` untouched.
- `/usr/bin/grep -rn "record_run_environment_evidence\|_record_environment_evidence" runtime/ --include=*.py` → the only production writer is `runtime/flow_start.py` (step 4). `runtime/claim.py` has no environment reference. No non-`flow_start` path routed into the recorder.
- `CAPABILITY_CHECKLIST.md` 6.24 row still `| IN PROGRESS |`; E1/E2/E3 rows untouched.

### 6. CAPABILITY_CHECKLIST 6.24 — evidence text only, status still IN PROGRESS — PASS

Diff is a single line: the 6.24 evidence text is rewritten to describe the shipped first slice and the "Still missing before a status flip" clause (end-to-end production exposure + optional fleet-wide flag). `| IN PROGRESS |` unchanged. No other row touched.

### 7. obs4 test present — PASS

`tests/test_routing_policy.py::test_router_holds_required_task_before_first_flow_start`: `required_for_routing=True` task, `environment_reports=None` → asserts `route == "policy_gate"`, `reasons == ("environment_report_required",)` — i.e. HOLDS, does not raise.

## STOP conditions — none triggered

No schema change; no new `PolicyDecision` kind; `inspect_local_environment` unchanged (no network, no out-of-repo dependency following, no spec-command execution — `safety.py` still routes every dependency hash through `_hash_dependency` with `O_NOFOLLOW`). Run-scoped store is sufficient: the design's temporal model (report from run N informs routing of run N+1; first routing has no report → hold if `required_for_routing`) is implemented as specified; no class of task forced a task-scoped table.

## Verify commands (blocking foreground)

```
python3 -m unittest tests.test_routing_environment_reports tests.test_routing_policy tests.test_task_environment_contract
  → Ran 48 tests ... OK
python3 -m unittest tests.test_routing_cli tests.test_flow_start tests.test_run_environment_evidence
  → Ran 29 tests ... OK    (test_routing_cli 22 + test_flow_start ... + test_run_environment_evidence)
python3 -m unittest tests.test_routing_policy tests.test_task_environment_contract  (re-run in mutation harness baseline)
python3 -m runtime.smoke
  → {"ok": true, ...}  exit 0
```

Total 106 targeted tests green (48 + 29 + prior 29-run overlap accounted), smoke exit 0.

## Mutation testing — 7 mutants, 7 caught (min 5 required)

Each mutant: single textual substitution at HEAD, targeted test module run, then `git checkout --` revert.

| # | Target | Mutation | Expected-fail test | Observed |
|---|--------|----------|--------------------|----------|
| M1 | `_freshness_diagnostic` (`environment_reports.py`) | `report.environment_spec_hash != spec_sha256` → `==` | `test_routing_environment_reports::RecordedEnvironmentReportSelectionTests.test_fresh_recorded_report_is_projected` | CAUGHT — fresh report now diagnosed `spec_hash_mismatch`, `FAILED (failures=1)` |
| M2 | `_freshness_diagnostic` | `age > max_age_seconds` → `age < max_age_seconds` | `...RecordedEnvironmentReportSelectionTests.test_stale_recorded_report_is_dropped_not_converted` | CAUGHT — stale report projected instead of dropped, `FAILED (failures=1)` |
| M3 | `_freshness_diagnostic` | `if age < 0:` (future guard) → `if age > 0:` | `test_routing_environment_reports::RoutingEnvironmentReportSelectionTests` (caller-supplied `produced_at_in_future` + fresh) | CAUGHT — `FAILED (failures=2)` |
| M4 | `_freshness_diagnostic` | `recorded_task_revision != current_task_revision` → `==` | `test_routing_environment_reports::RoutingEnvironmentReportSelectionTests` (task_revision_mismatch) | CAUGHT — `FAILED (failures=3)` |
| M5 | `select_recorded_environment_reports` projection guard | `if diagnostic == "fresh":` → `!= "fresh"` | `...RecordedEnvironmentReportSelectionTests.test_fresh_recorded_report_is_projected` | CAUGHT — `KeyError: 'TASK-REC'`, `FAILED (errors=1)` |
| M6 | router hold (`router.py:141`) | `environment_contract.get("required_for_routing")` → `not environment_contract.get(...)` | `test_routing_policy::PolicyRoutingTests.test_router_holds_required_task_with_no_report` | CAUGHT — `FAILED (failures=1)` |
| M7 | router hold reason (`router.py:151`) | `reasons=("environment_report_required",)` → `("environment_incompatible",)` | `test_routing_policy::PolicyRoutingTests.test_router_holds_required_task_with_no_report` | CAUGHT — `FAILED (failures=1)` |

No surviving mutants.

## Non-blocking findings

1. **Stale docstring** — `runtime/recovery/production.py:194` still reads "`record_run_environment_evidence` currently has zero production writers"; as of this PR `runtime/flow_start.py` is exactly that writer. Doc-only, no behaviour impact; worth a one-line follow-up.
2. **Recorded-path diagnostic tests are transitive** — `select_recorded_environment_reports` has no direct unit test asserting `spec_hash_mismatch` / `task_revision_mismatch` diagnostics on the recorded path specifically; those branches are covered only through the shared `_freshness_diagnostic` via the caller-supplied tests (and mutants M1/M4 confirm the coverage is real). Acceptable under the shared-helper design; a 2-line recorded-path test for each would fully close it.

Neither finding blocks merge.

## Verdict

**PASS.** All 7 scope items hold, no MUST-NOT violated, no STOP condition triggered, 106 targeted tests green, smoke exit 0, 7/7 mutants caught. Coordinator (niko) owns rebase + merge-prep; no self-merge.
