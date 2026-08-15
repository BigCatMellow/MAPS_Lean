# Task: Status surface v1

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT`
- Risk: `LOW`
- Goal: Provide one compact read-only operator view of canonical task counts,
  active claims, concrete attention items, and recent lifecycle events without
  creating another control plane or mutable status store.

## Inputs and source of truth

- Inputs: canonical SQLite tasks/events/outcomes.
- Authoritative sources: `.maps/state/maps.db`; status output is disposable.
- Evidence labels: canonical DB facts `VERIFIED`; omitted hcom/recovery/helper
  coverage is explicit.
- Dependencies / preconditions: task database can be opened.

## Change boundary

- MAY CHANGE: `runtime/status.py`, `runtime/cli.py`, `runtime/README.md`,
  `tests/test_status.py`, review packet, this task.
- MUST NOT CHANGE: task state, leases, review, outcomes, routing, hcom, recovery.
- MAY CHANGE IF NECESSARY: none without task amendment.
- OPERATOR APPROVAL REQUIRED: none.

## Decision authority

- Owner may decide: compact read-model fields and attention classifications.
- Owner must escalate: any status action that mutates, reassigns, retries, kills,
  approves, or otherwise changes authority.

## Acceptance criteria

- [ ] Status is read-only and derived from canonical SQLite state.
- [ ] Counts by task status are shown.
- [ ] Active claims show claimant/lease/heartbeat/attempt information.
- [ ] Attention includes `READY_FOR_REVIEW`, `BLOCKED`, expired/missing ACTIVE
  leases, and recorded post-completion `FAILURE` outcomes.
- [ ] Recent events expose event type/actor/time without duplicating free-text
  summaries into another display surface.
- [ ] Coverage explicitly says hcom/recovery/helper evidence is not joined in v1.
- [ ] CLI/tests cover counts, stale leases, review attention, failure outcomes,
  limit handling, and no mutation.

## Verification and evidence

- Verification: pull-request CI plus focused tests.
- Evidence to preserve: CI result and PR diff.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: Python 3.12 / SQLite.
- Ordered procedure: canonical query → derive attention → compact JSON.
- Failure branches: invalid limits rejected; absent optional sources reported as
  coverage gaps rather than inferred.
- Rollback / recovery: revert implementation; no schema/state migration.
- Security / privacy controls: recent events omit free-text summaries.
- External side effects: GitHub branch/PR only.
- Effort limit: no UI, daemon, polling loop, auto-remediation, or hcom join.
- Approved reference: preserved small Mission Control / `maps status` candidate.

## Stop / escalate

Stop if usefulness would require status to become authority or to guess state
from unstructured communication.

Escalate to: operator.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Completion / handoff

- Completed: task shaped.
- Not completed: implementation/review.
- Current blocker: none.
- Next action if not DONE: implement derived status view and tests.
