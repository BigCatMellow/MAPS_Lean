# Task: recovery UNKNOWN same-tick fallback

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: orchestration operator
- Risk: `MEDIUM`
- Goal: A returned failed harness resume with `RetryDisposition.UNKNOWN` cannot trigger a second direct resume in the same recovery tick; ambiguity evidence remains visible and the next tick re-observes session truth before another attempt.
- Parent roadmap: `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md` plus operator-approved reviewed-gap sequence (2026-09-09)
- Related records: `work/notes/2026-09-09-external-effect-idempotency-audit.md`; `work/decisions/2026-09-09-recovery-unknown-same-tick-fallback.md`; PR #327 characterization
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: `runtime/recovery/supervisor.py`, `runtime/harness/types.py`, `runtime/harness/service.py`, `runtime/harness/adapters/hcom.py`, `tests/test_recovery_supervisor.py`, `tests/test_recovery_external_effect_ambiguity.py`, predecessor audit/review evidence.
- Authoritative sources: `AGENTS.md` > operator-approved bounded objective > accepted decision above > current runtime/tests.
- Evidence labels: current same-tick fallback = VERIFIED by PR #327; `RetryDisposition.UNKNOWN` meaning = VERIFIED in `runtime/harness/types.py`; broader exactly-once/idempotency guarantees = NOT CLAIMED.
- Dependencies / preconditions: PR #327 merged; exact current `main` inspected; no active conflicting PR surface found.

## Change boundary

- MAY CHANGE: `runtime/recovery/supervisor.py`; `tests/test_recovery_external_effect_ambiguity.py`; this task record; the accepted bounded decision; PR metadata/review handoff.
- MUST NOT CHANGE: harness protocol signatures; adapter/provider behavior; SQLite schema; task authority; capability status; general operation ledger/idempotency architecture; E5 recovery-compatibility policy; unrelated recovery gates.
- MAY CHANGE IF NECESSARY: focused assertions in existing recovery tests only to preserve an explicitly intended compatibility behavior exposed by this change.
- HUMAN REAUTHORIZATION REQUIRED: any general idempotency architecture, schema/provider contract, new spending/credentials, destructive action, or expansion beyond recovery-resume same-tick fallback.

## Decision authority

- Inherited roadmap authority: operator instruction to use the recommended reviewed-gap order, starting with recovery ambiguity, plus Harness Mechanics' existing ambiguity/reconciliation direction.
- Owner may decide: the smallest recovery-resume policy that prevents UNKNOWN from being treated as implicitly retry-safe while preserving existing compatibility paths.
- Resolve internally first: exact pre-dispatch result classification, evidence fields, retry-budget/backoff interaction, test shape.
- Human escalation only if: fixing the seam requires general operation persistence/provider idempotency/schema changes or materially changes the approved objective.

## Acceptance criteria

- [x] failed returned harness result with `retry=UNKNOWN` does not call direct `hcom.resume()` in the same tick;
- [x] `operation_id`, `retry`, and `mutated` are surfaced in recovery action evidence for that ambiguous result;
- [x] incident stays on existing probing/backoff path and consumes one ordinary attempt;
- [x] a later tick re-observes a now-live session and resolves without a second resume;
- [x] production `HarnessService` + Hcom transport failure (`TRANSPORT_ERROR`, `retry=UNKNOWN`) is covered;
- [x] `CANONICAL_GUARD_REQUIRED` retains its established rollout compatibility fallback;
- [x] no ledger/schema/provider/capability/authority expansion;
- [ ] exact-head Runtime stack CI passes;
- [ ] independent review completed and evidence bound to exact code head.

## Verification and evidence

- Verification: targeted recovery ambiguity regression plus full repository Runtime stack CI.
- Evidence to preserve: PR diff, exact-head CI, independent review evidence.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: MAPS_L Python recovery runtime.
- Ordered procedure: apply bounded decision -> run targeted/full CI -> independent review -> reconcile findings -> merge only through repository merge-authority gate.
- Failure branches: IF existing compatibility regression fails THEN determine whether it is a known pre-dispatch outcome and preserve it rather than broadening UNKNOWN suppression blindly.
- Rollback / recovery: revert the bounded supervisor/test commit if it changes unrelated recovery semantics.
- Security / privacy controls: no new sensitive data; preserve only structured operation metadata already present in `OperationResult`.
- External side effects: none from implementation/tests.
- Effort limit: stop before general operation persistence/provider changes.
- Approved reference: `work/decisions/2026-09-09-recovery-unknown-same-tick-fallback.md`.
- Operational independence: `N/A — runtime behavior is automatically exercised by existing recovery operation; no separate operator procedure is introduced.`
- Reproduction package: test module is the executable reproduction; predecessor audit preserves source/provenance.

## Question-resolution ladder

Authoritative runtime/type evidence and PR #327 characterization were inspected. The previous policy implementation was treated as prior evidence only, then independently checked against current `main` before reuse. The decision stays bounded to the characterized seam.

## Stop / escalate

Stop this branch if the change requires a new durable operation record, adapter API, provider idempotency key, schema change, or a decision about later retries beyond the existing backoff behavior.

## AGI readiness

- Fresh-Agent Test: `PASS` — task states exact inputs, policy, tests, and boundary.
- No-Guess Test: `PASS` — current seam and retry semantics are executable/verified.
- Scope Test: `PASS` — one recovery decision seam plus focused tests.
- Authority Test: `PASS` — inside operator-approved reviewed-gap sequence; broader changes excluded.
- Completion Test: `PASS` — exact behavioral/CI/review gates stated.
- Failure Test: `PASS` — compatibility failure and rollback paths stated.
- Continuation Test: `PASS` — independent review then next reviewed gap.

## Notes / decisions

- `UNKNOWN` is not promoted to `SAFE`; same-tick duplicate attempt is suppressed.
- This does not decide whether a later backoff retry is always safe; that remains broader reconciliation work.
- Raw `HarnessService.resume()` exceptions are deliberately unchanged in this task.

## Completion / handoff

- Completed: bounded implementation shaped; policy decision recorded; implementation/test delta prepared for review.
- Not completed: CI and independent review.
- Triage capture: pending session friction capture before handoff.
- Reproduction package: `tests/test_recovery_external_effect_ambiguity.py` plus predecessor audit.
- Current blocker: none before CI/review.
- Next eligible roadmap task: reviewer execution lineage after this task completes.
- Human action required: none.
