# Task: RnS harness validation call-site design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `ARCHITECTURE`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: define the next production call-site boundary for H4/E4/6.5 validation
  tiers by deciding how the existing RecoverySupervisor hcom resume path should
  first move through `HarnessService`, without implementing runtime behavior.

## Inputs and source of truth

- Inputs:
  - `work/notes/2026-08-19-harness-production-wiring-gap.md`
  - `work/insights/2026-08-19-the-harness-layer-h4-h5-l6-sec4-waves-has-zero-production-ca-INSIGHT-75785aae.md`
  - `work/insights/2026-08-19-recoverysupervisor-tick-has-zero-production-invocation-anywh-INSIGHT-e0b448a6.md`
  - `runtime/recovery/supervisor.py`
  - `runtime/harness/service.py`, `runtime/harness/adapters/hcom.py`,
    `runtime/harness/hooks.py`, `runtime/harness/types.py`
  - `runtime/environment/validation.py`
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` rows H4/E4/6.5
- Authoritative sources: current runtime code and the 2026-08-19 production
  wiring gap note.
- Evidence labels:
  - VERIFIED: validation tiers and hook callback factory exist.
  - VERIFIED: no production call site currently invokes validation tiers.
  - VERIFIED: `RecoverySupervisor` remains the closest existing
    session-lifecycle-shaped caller but still uses direct hcom resume behavior.
  - VERIFIED: `HcomHarnessAdapter.resume()` is already implemented and maps to
    `backend.resume(..., headless=True, go=True)`.
- Dependencies / preconditions: PR #153 is merged; no Chain Shovel or external
  pilot authority is involved.

## Change boundary

- MAY CHANGE:
  - `work/notes/2026-08-21-rns-harness-validation-callsite-design.md`
  - this task file
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` H4/E4/6.5 evidence text only
- MUST NOT CHANGE:
  - `runtime/*.py`
  - `tests/*.py`
  - harness adapter behavior
  - recovery behavior
  - environment validation behavior
- MAY CHANGE IF NECESSARY: none.
- OPERATOR APPROVAL REQUIRED: none for this design; runtime recovery/harness
  behavior changes require their own implementation task and review.

## Decision authority

- Owner may decide:
  - the recommended first production call-site sequence;
  - which behavior questions must be answered before implementation;
  - where validation-tier wiring belongs relative to RnS harness resume wiring.
- Owner must escalate:
  - adding runtime code;
  - changing RnS resume behavior;
  - making validation tiers mandatory;
  - adding daemon/cron/always-on recovery invocation;
  - selecting any external project target.

## Acceptance criteria

- [x] Design note names the current H4/E4/6.5 blocker with direct source paths.
- [x] Design note preserves the prior Option B recommendation rather than
      inventing a new call-site.
- [x] Design note defines the base implementation boundary for RnS
      `HarnessService.resume()` wiring.
- [x] Design note does not ask future work to re-implement already-resolved
      hcom harness resume semantics.
- [x] Design note defines validation-tier fast-follow placement and non-goals.
- [x] Design note lists open behavior questions that must not be guessed.
- [x] No runtime or test files change.

## Verification and evidence

- Verification:
  - `git diff --check`
  - direct read of changed docs
- Evidence to preserve: design note, task doc, checklist update.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: repository docs only.
- Ordered procedure: inspect current notes/code, write design, verify.
- Failure branches: if runtime already has a production validation call-site,
  update the finding instead of preserving stale gap language.
- Rollback / recovery: revert docs-only commit.
- Security / privacy controls: do not introduce command execution, environment
  probing, credentials, or external project access.
- External side effects: GitHub PR publication/merge only after review.
- Effort limit: no implementation in this task.
- Approved reference:
  `work/notes/2026-08-19-harness-production-wiring-gap.md`.

## Stop / escalate

Stop rather than guess if:

- current hcom harness resume semantics appear to differ from the documented
  `headless=True, go=True` behavior;
- validation-tier failure policy would change recovery outcomes;
- a new always-on trigger loop would be required;
- implementation becomes necessary to prove the design.

Escalate to: operator or a new implementation task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task scopes the next H4/E4/6.5 path as RnS harness-resume wiring first,
  validation-tier hook-in second.

## Completion / handoff

- Completed: design note and bounded implementation follow-up.
- Not completed: runtime recovery/harness/validation wiring.
- Current blocker: independent review.
- Next action if not DONE: review this architecture task.
