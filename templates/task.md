# Task: <short name>

- Status: `NEEDS_SHAPING | READY | ACTIVE | READY_FOR_REVIEW | CHANGES_REQUESTED | DONE | BLOCKED`
- AGI status: `UNCHECKED | AGI READY | AGI FAIL — NEEDS_SHAPING | AGI FAIL — NEEDS_RESEARCH | AGI FAIL — NEEDS_OPERATOR_DECISION | AGI FAIL — BLOCKED_ON_DEPENDENCY`
- Type: `IMPLEMENTATION | REVIEW | ARCHITECTURE | PLANNING | RESEARCH | MAINTENANCE | REPAIR`
- Owner: <agent or person>
- Risk: `LOW | MEDIUM | HIGH`
- Goal: <observable outcome>

## Inputs and source of truth

- Inputs: <files, systems, evidence, or prior work to inspect/use>
- Authoritative sources: <what wins if context conflicts>
- Evidence labels: <VERIFIED / REPORTED / ASSUMED / UNKNOWN where relevant>
- Dependencies / preconditions: <none or named tasks/conditions>

## Change boundary

- MAY CHANGE: <every path/action this task may edit/create/perform>
- MUST NOT CHANGE: <paths, behavior, scope, or decisions outside this task>
- MAY CHANGE IF NECESSARY: <none or items that require task amendment first>
- OPERATOR APPROVAL REQUIRED: <none or named consequential choices>

## Decision authority

- Owner may decide: <bounded implementation choices>
- Owner must escalate: <scope, product intent, security, privacy, cost, external behavior, destructive/irreversible choices, or named project-specific decisions>

## Acceptance criteria

- [ ] <observable pass/fail result>
- [ ] <observable pass/fail result>

## Verification and evidence

- Verification: <test, command, screenshot, inspection, benchmark, or reproduction step>
- Evidence to preserve: <command result, screenshot, log, diff, link, or artifact>
- Review required: `OWNER_CHECK | INDEPENDENT_REVIEW | OPERATOR_VISIBLE_RELEASE_CHECK`

## Conditional execution rules

Include only what materially applies; use `N/A` explicitly when useful.

- Environment / target: <runtime, OS, hardware, viewport, deployment target, or N/A>
- Ordered procedure: <required sequence or N/A>
- Failure branches: <IF condition THEN action, or N/A>
- Rollback / recovery: <reversal path or N/A>
- Security / privacy controls: <requirements or N/A>
- External side effects: <publication/deployment/API/data mutation or N/A>
- Effort limit: <time/cost/attempt threshold or N/A>
- Approved reference: <mockup/spec/schema/behavior reference or N/A>

## Stop / escalate

Stop rather than guess if:

- <important unknown, changed dependency, new output path, failed assumption, authority boundary, safety issue, or verification conflict>

Escalate to: <owner/operator/research task as appropriate>

## AGI readiness

Before setting `Status: READY`, validate against
[the AGI standard](../playbook/AGI_STANDARD.md).
Use [the AGI check template](agi-check.md) when a durable check is useful.

- Fresh-Agent Test: `PASS | FAIL | N/A`
- No-Guess Test: `PASS | FAIL | N/A`
- Scope Test: `PASS | FAIL | N/A`
- Authority Test: `PASS | FAIL | N/A`
- Completion Test: `PASS | FAIL | N/A`
- Failure Test: `PASS | FAIL | N/A`
- Continuation Test: `PASS | FAIL | N/A`

A consequential task MUST NOT be marked `READY` unless every applicable
mandatory AGI requirement passes.

## Notes / decisions

- <only forward-relevant information>

## Completion / handoff

- Completed: <what is verified true now>
- Not completed: <remaining work or `none`>
- Current blocker: <none or exact blocker>
- Next action if not DONE: <single concrete action>
