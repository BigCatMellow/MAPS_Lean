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
