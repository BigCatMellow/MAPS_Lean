reviewer: vivo
head_sha: 6a8dc8953a388b0c86170c8953a7493f7fe54b23
independent: true
summary: Independent review of PR #335 (fail-closed on UNKNOWN recovery resume before direct fallback). Verified the clone at the exact head SHA; the diff touches only the 4 authorized files (runtime/recovery/supervisor.py, tests/test_recovery_external_effect_ambiguity.py, work/decisions/2026-09-09-recovery-unknown-same-tick-fallback.md, work/tasks/recovery-unknown-same-tick-fallback.md), and the code change matches what the decision doc authorizes within the operator-approved 2026-09-09 reviewed-gap objective. All 7 review-ask checks hold: (1) ambiguous_external_outcome fires only when not result.ok and result.retry == UNKNOWN and code not in _PRE_DISPATCH_RESULT_CODES; every production pre-dispatch code (HOOK_DENIED, APPROVAL_REQUIRED, CANONICAL_GUARD_REQUIRED, adapter/service guard codes) is emitted with retry=UNSAFE, so the disposition check alone excludes them and the code-name set is defensive belt-and-suspenders against a default-UNKNOWN fake caller; (2) canonical-denial handling is unchanged and test_recovery_supervisor is green; (3) the ambiguous branch sets resolved=True/action="resume_failed" but NOT canonically_denied, so it skips the direct hcom.resume fallback, then falls through to attempt += 1, state="probing", next_attempt_at=backoff -- no permanent suppression, and the next tick re-runs session_is_live(...) before any retry (verified in tick() control flow, not just the test); (4) mutated/operation_id/retry are added to harness_resume additively and only in the ambiguous case, and the decision doc explicitly disclaims durable logical-operation identity; (5) test_real_hcom_transport_failure_unknown_suppresses_direct_fallback exercises the real HcomHarnessAdapter + HarnessService + registered CanonicalRunGuard, with _FakeHcom only at the hcom subprocess/provider boundary, and asserts backend.resumes==1 before the HcomError is normalized to TRANSPORT_ERROR/retry=UNKNOWN; (6) no scope creep -- no ledger, schema, adapter/provider API, authority, new recovery state, or E5 policy change; (7) no sibling guard-isolation / non-goal / slice-boundary test breaks (script_paths NonGoal asserts live only in unrelated modules). Test evidence: targeted pytest tests/test_recovery_external_effect_ambiguity.py tests/test_recovery_supervisor.py = 79 passed, exit 0; broad pytest tests/ -k "recovery or harness or supervisor" = 269 passed / 1084 deselected, exit 0. Verdict: APPROVE. Non-blocking observation: other pre-dispatch guard codes (ADAPTER_NOT_FOUND, *_MISMATCH, SESSION_REQUIRED, DESTRUCTIVE_GUARD_REQUIRED) are not enumerated in _PRE_DISPATCH_RESULT_CODES, harmless today because all are UNSAFE in production, but a future code returning one with retry=UNKNOWN would be misclassified as an ambiguous external effect -- worth a one-line note in the decision doc's residual-questions section if a follow-up touches this area.

## Verdict: APPROVE

### Checks performed

- Clone: git clone + git fetch origin pull/335/head + checkout; git rev-parse HEAD == 6a8dc8953a388b0c86170c8953a7493f7fe54b23 confirmed.
- Diff scope: git diff --name-only origin/main...pr335 = exactly the 4 authorized files. Branch is 7dfcbd0 (current main) + 3 commits, clean.
- _PRE_DISPATCH_RESULT_CODES = _CANONICAL_DENIAL_CODES | {"CANONICAL_GUARD_REQUIRED"} -- covers the 3 codes named in the review ask. Cross-checked producers in runtime/harness/service.py and runtime/harness/adapters/hcom.py (_provider_failure -> TRANSPORT_ERROR|PROTOCOL_ERROR|COMMAND_FAILED / UNKNOWN). Post-dispatch provider ambiguity is exactly the UNKNOWN set the suppression targets.
- tick() flow: ambiguous_external_outcome branch -> action="resume_failed", resolved=True, canonically_denied stays False -> direct self.hcom.resume skipped -> attempt += 1, state="probing", next_attempt_at = backoff. Next tick: session_is_live(...) check resolves the incident if the session came up; otherwise waits for due_at. Retry budget still bounded by backoff_seconds -> eventual retry_budget_exhausted. No permanent suppression.
- Real-path test: HcomHarnessAdapter + HookRegistry + register_canonical_run_guards + HarnessService([adapter], hooks=hooks); _FakeHcom is the provider backend only; harness_backend.fail = True raises HcomError after recording the resume dispatch; test asserts harness_backend.resumes == 1 and harness_resume["code"] == "TRANSPORT_ERROR" / retry == "UNKNOWN".
- Non-goal/slice-boundary: /usr/bin/grep -rn "script_paths" tests/ -> only test_memory_trust_gate.py, test_skills_format.py (unrelated). Broad -k run green.

### Test output tails

```
# pytest tests/test_recovery_external_effect_ambiguity.py tests/test_recovery_supervisor.py -q
79 passed, 3 subtests passed in 158.41s
EXIT=0

# pytest tests/ -q -k "recovery or harness or supervisor"
269 passed, 1084 deselected, 13 subtests passed in 465.14s
BROAD_EXIT=0
```

(python3 -m unittest cross-check of the 3 new ambiguity tests also green: Ran 3 tests ... OK.)

---

reviewer: ChatGPT GPT-5.6 Sol / SENTINEL-FRESH-PR335
head_sha: 6a8dc8953a388b0c86170c8953a7493f7fe54b23
independent: true
summary: APPROVE — fresh independent review bound to exact code head 6a8dc8953a388b0c86170c8953a7493f7fe54b23. Verified the bounded supervisor predicate suppresses same-tick direct fallback only for returned non-success retry=UNKNOWN results outside the explicit pre-dispatch compatibility set; CANONICAL_GUARD_REQUIRED continues to fall through to direct resume, canonical denials retain their dedicated no-fallback/separate-budget path, unresolved harness binding and raw HarnessService.resume exceptions retain direct-fallback behavior, and the ambiguous result still consumes one ordinary attempt and returns to probing/backoff. Verified the next tick checks session liveness before due/retry and resolves a now-live session without a second resume. Recovery evidence preserves mutated, operation_id, and retry only for the ambiguous case; OperationResult defines operation_id as an opaque correlation identifier and the task/decision/audit explicitly do not claim durable logical intent/idempotency identity. The production regression composes real HarnessService + registered CanonicalRunGuard + HcomHarnessAdapter and makes the fake backend record the resume dispatch before raising HcomError, which HcomHarnessAdapter normalizes to TRANSPORT_ERROR with retry=UNKNOWN. Exact base-to-code-head diff changes only supervisor.py, the focused ambiguity test, task, and decision; no ledger, schema, provider/idempotency protocol, capability, E5 policy, authority, new recovery state, or broader retry architecture is introduced. GitHub Actions Runtime stack tests run 1641 / job 102711106769 is completed success at exact head_sha 6a8dc8953a388b0c86170c8953a7493f7fe54b23, including compile, lint, security analysis, dependency consistency, active tests, smoke, and installer validation. No blocking defect found.

## Fresh independent verification details

- UNKNOWN suppression: `ambiguous_external_outcome = (not result.ok and result.retry == RetryDisposition.UNKNOWN and code not in _PRE_DISPATCH_RESULT_CODES)`; that branch sets `action="resume_failed"`, `resolved=True`, skips `self.hcom.resume(...)`, then executes ordinary `attempt += 1`, `state="probing"`, and backoff scheduling.
- Compatibility isolation: `_PRE_DISPATCH_RESULT_CODES` includes `HOOK_DENIED`, `APPROVAL_REQUIRED`, and `CANONICAL_GUARD_REQUIRED`; the first two are handled before the ambiguous branch and the last is allowed to fall through. Other production pre-dispatch service/binding errors are emitted with `retry=UNSAFE`, so they do not satisfy the UNKNOWN predicate.
- Canonical-denial / binding / exception preservation: the production delta does not alter `_resolve_harness_binding`, the canonical-denial accounting branch, or the `except Exception` path; exact-head recovery-supervisor tests covering missing canonical guard direct fallback and harness-call exception direct fallback are part of the successful Runtime stack run.
- Ambiguity evidence: `mutated`, `operation_id`, and `retry` are projected only when the UNKNOWN/non-pre-dispatch predicate is true. `runtime/harness/types.py::new_operation_id` calls it an opaque operation correlation identifier; the predecessor audit explicitly states it is not durable logical intent identity.
- Re-observation: `tick()` reads the current session list once at tick start and checks `session_is_live(...)` before due-at evaluation or any resume. The focused regression changes the next tick's observed session to active/process-bound and proves resolution with exactly one harness resume total and zero direct resumes.
- Real transport path: the focused test uses production `HarnessService`, `HookRegistry`, `CanonicalRunGuard`, and `HcomHarnessAdapter`. `_FakeHcom.resume` appends the call and then raises `HcomError`; adapter `_provider_failure` maps it to `TRANSPORT_ERROR` and `RetryDisposition.UNKNOWN`, which reaches the supervisor predicate.
- Exact-head CI: Runtime stack tests workflow run 1641 / run id 34425953377 / job 102711106769 reports `head_sha=6a8dc8953a388b0c86170c8953a7493f7fe54b23` and `conclusion=success`.

Verdict: APPROVED.

---

reviewer: bila (main-sync rebind only; both reviews above stand unchanged, see below)
head_sha: 633cfc850ff38fa48b91af7eef8605e3f859f58c
independent: true
summary: Mechanical main-sync rebind, not a new substantive review. Merged origin/main (5f07b33, automated "Refresh Development status" docs-only commit) into PR #335 with `git merge --no-edit`; the merge touched only docs/wiki/Development.md and has zero overlap with #335's reviewed files (runtime/recovery/supervisor.py, tests/test_recovery_external_effect_ambiguity.py, work/decisions/2026-09-09-recovery-unknown-same-tick-fallback.md, work/tasks/recovery-unknown-same-tick-fallback.md). The reviewed code itself is byte-identical to what both independent reviewers above (vivo and the lineage's SENTINEL reviewer) already approved at code head 6a8dc8953a388b0c86170c8953a7493f7fe54b23; re-ran the targeted regression suite post-merge to confirm nothing regressed: `pytest tests/test_recovery_external_effect_ambiguity.py tests/test_recovery_supervisor.py` = 79 passed, exit 0. Both prior independent verdicts stand unchanged; this commit exists only to rebind their evidence to the new merge-commit head required by `check_review_evidence.py`'s merge-commit walk-back rule (a merge commit is never walked past, so a main-sync always needs a fresh evidence commit even when the reviewed code itself is unchanged).
