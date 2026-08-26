# AGI Check: <artifact or task>

- Artifact: <path or task ID>
- Checked by: <agent/person>
- Date: <YYYY-MM-DD>
- Artifact type: `TASK | PROJECT | RESEARCH | REVIEW | HANDOFF | TOOL | DECISION`
- Related durable context: <task/project/decision/research/playbook links or `none`>

## Core task contract

For executable tasks, mark every applicable field `PASS | FAIL | N/A`.

- Outcome: <status> — <evidence/location>
- Accountable owner: <status> — <evidence/location>
- Source of truth / inputs: <status> — <evidence/location>
- Preconditions / dependencies: <status> — <evidence/location>
- Work boundary: <status> — <evidence/location>
- Decision authority: <status> — <evidence/location>
- Acceptance criteria: <status> — <evidence/location>
- Verification / expected evidence: <status> — <evidence/location>
- Review requirement: <status> — <evidence/location>
- Stop / escalation: <status> — <evidence/location>

## Conditional extensions

Mark applicable items `PASS | FAIL`; use `N/A` only when the condition truly
does not apply.

- Ordered procedure: <status> — <reason/evidence>
- Failure branches: <status> — <reason/evidence>
- Rollback / recovery: <status> — <reason/evidence>
- Environment: <status> — <reason/evidence>
- Security / privacy: <status> — <reason/evidence>
- External side effects: <status> — <reason/evidence>
- Effort limit: <status> — <reason/evidence>
- Approved reference: <status> — <reason/evidence>
- Handoff state: <status> — <reason/evidence>

## Seven tests

- Fresh-Agent Test: `PASS | FAIL | N/A` — <can the agent follow the important durable links without the original chat?>
- No-Guess Test: `PASS | FAIL | N/A` — <why>
- Scope Test: `PASS | FAIL | N/A` — <why>
- Authority Test: `PASS | FAIL | N/A` — <why>
- Completion Test: `PASS | FAIL | N/A` — <why>
- Failure Test: `PASS | FAIL | N/A` — <why>
- Continuation Test: `PASS | FAIL | N/A` — <why>

## Result

AGI status:

`AGI READY | AGI FAIL — NEEDS_SHAPING | AGI FAIL — NEEDS_RESEARCH | AGI FAIL — NEEDS_OPERATOR_DECISION | AGI FAIL — BLOCKED_ON_DEPENDENCY`

Blocking reasons:

- <smallest concrete reason preventing AGI READY, or `none`>

Required next action:

1. <single concrete action, or `none — AGI READY`>

Do not calculate a percentage score. Every applicable mandatory requirement
must pass before declaring `AGI READY`.
