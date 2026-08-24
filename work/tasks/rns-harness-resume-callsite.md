# Task: RnS harness resume production call site

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: make `RecoverySupervisor.tick()`'s resume attempt the first real
  production caller of `HarnessService.resume()` / `HcomHarnessAdapter.resume()`,
  replacing the direct `self.hcom.resume(session_name, headless=True, go=True)`
  call whenever the incident's existing session/run lineage lets a real
  `ExecutionBinding`/`SessionRef` be constructed, while preserving today's
  direct-resume behavior for every other outcome.

## Inputs and source of truth

- Inputs:
  - `work/notes/2026-08-21-rns-harness-validation-callsite-design.md` (design;
    source of truth for scope and the open behavior questions this task
    answers)
  - `runtime/recovery/supervisor.py`
  - `runtime/harness/service.py`
  - `runtime/harness/adapters/hcom.py` (unchanged)
  - `runtime/harness/types.py`
  - `runtime/policy/harness_guard.py` (`CanonicalRunGuard`, unchanged)
  - `tests/test_recovery_supervisor.py`
- Authoritative sources: the design note above; `HarnessService.resume()`'s
  actual control flow (read directly, not assumed).
- Evidence labels:
  - VERIFIED: prior to this task, `harness_service` on `RecoverySupervisor`
    was wired but only ever used for a shadow, non-gating observation
    (`_advisory_harness_resume_shadow`) that ran unconditionally for every
    incident on every tick and was never a production call site (no code
    outside tests ever constructed a `RecoverySupervisor` with a real
    `harness_service`).
  - VERIFIED: `HarnessService.resume()` denies with `CANONICAL_GUARD_REQUIRED`
    whenever no `CANONICAL_RUN` Hook enforcement is registered for
    `BEFORE_RESUME` at all -- this fires before the adapter is ever called,
    regardless of whether a real mismatch exists.
  - VERIFIED: `HcomHarnessAdapter.resume()` is unmodified; it still calls
    `backend.resume(name, headless=True, go=True)`.

## Change boundary

- MAY CHANGE:
  - `runtime/recovery/supervisor.py`
  - `tests/test_recovery_supervisor.py`
  - this task file
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` (harness production-wiring
    evidence text only)
- MUST NOT CHANGE:
  - `runtime/harness/adapters/hcom.py`
  - `runtime/harness/service.py` (signatures)
  - `runtime/environment/validation.py` or any `EnvironmentSpec` wiring
  - task-truth mutation surfaces (`claim_task`, `submit_task`,
    `record_review`, `promote_ready`, `update_contract`)
  - any daemon/cron/always-on invocation of `tick()`
- MAY CHANGE IF NECESSARY: none.
- OPERATOR APPROVAL REQUIRED: none -- bounded follow-up already scoped by the
  merged design note.

## Decisions (answers to the design note's open behavior questions)

1. **What does RnS record when `HarnessService.resume()` denies because of
   `CANONICAL_RUN`?**
   Only an *installed, actively denying* `CANONICAL_RUN` Hook (`HOOK_DENIED`
   or `APPROVAL_REQUIRED`) counts as an explicit canonical-run denial. In that
   case `tick()` returns action `"resume_denied"`, with `error` set to the
   Hook's summary and `harness_resume` carrying `{"attempted": true, "ok":
   false, "code": ..., "summary": ...}`. No fallback direct resume is
   attempted, and no task-truth mutation occurs -- only the incident's own
   RnS-owned recovery-store bookkeeping (`attempt`, `state`,
   `next_attempt_at`) advances, same as any other attempted-and-failed
   resume.
   `CANONICAL_GUARD_REQUIRED` (no `CANONICAL_RUN` Hook installed at all) is
   deliberately *not* treated as a denial -- it is a configuration gap, not a
   concrete mismatch, and per the design note's own framing ("does not
   silently suppress a resume the direct path would have attempted unless
   the canonical-run guard has a concrete mismatch") it falls back to the
   pre-existing direct resume call instead.

2. **Missing/ambiguous run binding: skip harness and preserve direct
   behavior, or fail closed?**
   Fail-open to existing behavior. When `_resolve_harness_binding()` cannot
   build a binding (no `run_id` bound, task missing, incomplete task
   binding, no lineage resolver, or lineage not `EXPLICIT`/not an `hcom`
   session), `tick()` falls straight through to the original
   `self.hcom.resume(session_name, headless=True, go=True)` call, unchanged.
   `harness_resume` records `{"attempted": false, "reason": ...}` for
   observability. This is the safety-conservative choice for the first
   production call site: harness routing can only ever narrow behavior via
   an explicit, attempted, denying call -- never via an inability to
   construct one.

3. **Which existing lookup constructs `ExecutionBinding`/`SessionRef`?**
   The same lineage relationship `_advisory_environment_evidence` already
   relies on: `incident["run_id"]` -> `task_reader.get_task()` for
   `project_id` -> `task_reader.compute_task_revision()` for the current
   revision -> `task_reader.resolve_run_session(run_id)` for the durable
   `hcom` session lineage. No new lineage-resolution machinery was added;
   this logic was extracted, unchanged in substance, from the former
   `_advisory_harness_resume_shadow` into `_resolve_harness_binding()`.

4. **Where is the eventual result persisted/surfaced?**
   Recovery action evidence only -- the `harness_resume` key in the
   `list[dict[str, Any]]` `tick()` already returns and persists nothing new
   beyond RnS's existing incident-store bookkeeping. No Run Record coverage
   and no new persistence machinery were added (out of scope; not needed for
   this call site).

## Behavior change summary

- Renamed the `harness_resume_shadow` evidence key to `harness_resume` and
  removed the unconditional-every-tick shadow call: a harness attempt now
  only happens on an actually-due resume attempt, and its result is real
  (not shadow-only).
- `tick()`'s resume attempt now routes through `HarnessService.resume()`
  whenever a binding is constructible; a successful harness resume reaches
  hcom through `HcomHarnessAdapter.resume()` (`backend.resume(name,
  headless=True, go=True)`), not the direct call.
- The only outcome this changes versus the pre-existing direct-resume
  behavior is an explicit, installed, actively-denying `CANONICAL_RUN` Hook
  (`HOOK_DENIED`/`APPROVAL_REQUIRED`) -> new action `"resume_denied"`.
  Every other harness outcome (success, `CANONICAL_GUARD_REQUIRED`, adapter
  failure, an exception from `harness_service.resume()` itself, or an
  unconstructible binding) preserves the current direct-resume
  success/failure semantics.
- `_advisory_environment_evidence` is untouched.

## Acceptance criteria

- [x] `RecoverySupervisor.tick()` routes resume through `HarnessService.resume()`
      when a binding can be constructed from existing lineage.
- [x] Explicit canonical-run denial is observable in returned evidence
      without a fallback resume and without task-truth mutation.
- [x] Missing/ambiguous binding preserves current direct-resume behavior.
- [x] No validation-tier wiring, no `EnvironmentSpec`, no report cache, no
      daemon/cron trigger loop, no new worker-loop entrypoint.
- [x] `HcomHarnessAdapter.resume()` / `HarnessService.resume()` signatures
      unmodified.
- [x] Full test suite passes.

## Verification and evidence

- Verification: `python3 -m unittest discover -s tests -v` (full suite).
- Evidence to preserve: this task doc, `tests/test_recovery_supervisor.py`'s
  `RecoveryHarnessResumeCallSiteTests` class, PR diff.
- Review required: `INDEPENDENT_REVIEW`.

## Tests added

All in `tests/test_recovery_supervisor.py::RecoveryHarnessResumeCallSiteTests`:

- `test_no_harness_service_configured_direct_resume_unchanged`
- `test_missing_run_binding_falls_back_to_direct_resume`
- `test_ambiguous_binding_falls_back_to_direct_resume`
- `test_successful_resume_routes_through_harness_adapter_not_direct_path`
  (real `HarnessService` + real `HcomHarnessAdapter` + real
  `CanonicalRunGuard`, proving the resume reaches a separate fake hcom
  backend through the harness adapter and never touches the direct-path
  hcom double)
- `test_canonical_run_denial_surfaces_in_evidence_without_direct_fallback`
- `test_missing_canonical_guard_falls_back_to_direct_resume`
- `test_harness_call_exception_falls_back_to_direct_resume`
- `test_environment_evidence_unaffected_by_harness_routing`
- `test_no_validation_tier_commands_or_task_mutation_in_source`

## Explicitly still out of scope

- Validation-tier wiring (`EnvironmentSpec.validation`, `make_validation_hook`)
  -- H4/E4/6.5 remain `IN PROGRESS`; this is a separate fast-follow task per
  the design note.
- A production trigger loop that actually calls `RecoverySupervisor.tick()`
  -- no code outside tests constructs a `RecoverySupervisor` at all today;
  that gap is tracked separately and is not this task's problem.
- Any daemon/cron/always-on process.
- Wrapping other helpers (Ollama/Aider) as harness adapters.
- A production report cache.

## Conditional execution rules

- Environment / target: this repository, isolated worktree.
- Ordered procedure: read design note and source files; extract lineage
  binding logic; route resume through the harness with the fail-open
  fallback rules above; rewrite tests; run full suite; update checklist;
  open PR.
- Failure branches: if `HarnessService.resume()`'s real behavior diverged
  from the design note's assumptions, stop and report rather than invent a
  workaround (did not occur).
- Rollback / recovery: revert the PR commit.
- Security / privacy controls: none beyond existing RnS/harness invariants.
- External side effects: GitHub PR only.
- Effort limit: this call site only; no validation tiers, no trigger loop.
- Approved reference: `work/notes/2026-08-21-rns-harness-validation-callsite-design.md`.

## Stop / escalate

Stop rather than guess if:

- `HarnessService.resume()`'s signature changes incompatibly with
  `ExecutionBinding`/`SessionRef` as currently defined;
- the incident/session/run lineage used by `_advisory_environment_evidence`
  turns out insufficient for most/all real incidents (would require new
  lineage-resolution machinery, out of scope).

Neither condition was hit during this task.

Escalate to: operator or a separate implementation task (validation-tier
fast-follow, or a production trigger-loop task).

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Completion / handoff

- Completed: base RnS harness resume production call site, with fail-open
  fallback and explicit canonical-run denial handling, fully tested.
- Not completed: validation-tier wiring (H4/E4/6.5 fast-follow); a production
  trigger loop for `tick()`.
- Current blocker: independent review.
- Next action if not DONE: review this PR; if approved, the validation-tier
  fast-follow and the `tick()` trigger-loop gap remain as the next two
  separately-scoped harness-production-wiring tasks.
