# Task: Freeze stale-owner rejection after lease takeover

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `MAINTENANCE`
- Owner: `competitor-borrow integration lane`
- Risk: `LOW`
- Goal: Preserve a deterministic regression proving that a superseded claimant cannot heartbeat or submit after another worker recovers an expired lease.
- Parent roadmap: `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` §6.1 task truth/ownership + `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md`
- Related records: `work/notes/2026-09-09-competitor-borrow-integration-log.md`; `work/research/agent-harness/2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md` when PR #323 lands; Pilot deep evidence `BigCatMellow/Pilot_Projects@f6d584465e15b0fcf3cd09fea9e056bc23852e94`
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: `runtime/state/execution.py`, `tests/test_state_store.py`, Noriq/Restate ownership-fencing evidence from the pinned Pilot corpus.
- Authoritative sources: current MAPS_L `runtime/state/execution.py` and existing SQLite task-state semantics win over external research; competitor material is evidence only.
- Evidence labels: current MAPS behavior `VERIFIED`; missing explicit post-takeover stale-owner regression `VERIFIED`; universal external-effect fencing `NOT CLAIMED`.
- Dependencies / preconditions: none; must remain non-overlapping with active PRs #319–#323.

## Change boundary

- MAY CHANGE: `tests/test_state_store.py`; this task record; `work/notes/2026-09-09-competitor-borrow-integration-log.md` for process/result evidence.
- MUST NOT CHANGE: `runtime/`; schemas; `CAPABILITY_CHECKLIST.md`; roadmaps; `AGENTS.md`; `playbook/EMERGENCE.md`; `playbook/PROGRAM_STEERING.md`; `docs/wiki/`; PR #319–#323 owned files.
- MAY CHANGE IF NECESSARY: test-only supporting assertions in the same existing state-store test module after review findings.
- HUMAN REAUTHORIZATION REQUIRED: any runtime/schema/authority change or attempt to generalize this test into arbitrary external-effect fencing.

## Decision authority

- Inherited roadmap authority: strengthen existing task-truth/lease behavior with regression evidence; no behavior/status change.
- Owner may decide: exact deterministic test arrangement and assertions inside existing semantics.
- Resolve internally first: test duplication, assertion shape, fixture reuse, naming.
- Human escalation only if: the existing implementation fails the borrowed invariant and repair would change task ownership/lease authority semantics.

## Acceptance criteria

- [x] Existing coverage was audited before adding a test.
- [x] New regression models A claim → expiry → B recovery → A stale mutation attempts.
- [x] Old claimant heartbeat is rejected as `NOT_CLAIM_OWNER`.
- [x] Old claimant submission is rejected as `NOT_CLAIM_OWNER`.
- [x] Replacement claimant remains canonical and can heartbeat/submit.
- [x] No runtime/schema/checklist/status change.
- [ ] Targeted/full CI passes on the exact PR head.
- [ ] Independent review verifies the test is discriminating and the external-effect limitation is stated honestly.

## Verification and evidence

- Verification: `python -m unittest tests.test_state_store`; repository CI/runtime stack tests; independent PR review.
- Evidence to preserve: exact test diff; CI result; reviewer result; process-log disposition.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: normal MAPS_L Python test environment.
- Ordered procedure: audit current code/tests → state borrowed invariant → add missing regression only → CI → independent review.
- Failure branches: IF existing runtime fails the test THEN do not silently repair runtime in this slice; record the gap and reshape under the owning roadmap/authority.
- Rollback / recovery: remove the test-only commit if review finds the test redundant or semantically invalid.
- Security / privacy controls: N/A — no secrets/user data.
- External side effects: GitHub branch/PR/test evidence only; no product/provider side effects.
- Effort limit: one focused regression; do not expand into fencing-token or external-effect implementation.
- Approved reference: pinned Pilot Noriq/Restate claim/fencing research.
- Operational independence: `REQUIRED`
- Reproduction package: current repository + `python -m unittest tests.test_state_store`; no external service required.

## Question-resolution ladder

```text
current MAPS code/tests
→ pinned upstream evidence
→ focused test
→ independent review
→ owning roadmap if behavior change is actually needed
```

## Stop / escalate

Stop this slice if the test requires runtime/schema changes or conflicts with an active PR. Do not infer that claimant/lease rejection provides exactly-once or external-effect fencing.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Borrowed invariant was translated into current MAPS semantics rather than copying Noriq/Restate schema or runtime.
- Existing code already appears to satisfy the invariant; this task intentionally adds only missing regression coverage.

## Completion / handoff

- Completed: current coverage audit; process note; focused stale-owner regression.
- Not completed: exact-head CI and independent review.
- Triage capture: `none — no §2 trigger fired`
- Reproduction package: run `python -m unittest tests.test_state_store` on the branch and inspect the single added takeover test.
- Current blocker: independent review / CI only.
- Next eligible roadmap task: after review, inspect 6.20 no-progress semantics against `process alive != useful progress != valid ownership`.
- Human action required: `none`
