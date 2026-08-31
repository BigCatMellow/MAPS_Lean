# Task: <short name>

- Status: `NEEDS_SHAPING | READY | ACTIVE | READY_FOR_REVIEW | CHANGES_REQUESTED | DONE | BLOCKED`
- AGI status: `UNCHECKED | AGI READY | AGI FAIL — NEEDS_SHAPING | AGI FAIL — NEEDS_RESEARCH | AGI FAIL — NEEDS_AUTHORITY_DECISION | AGI FAIL — BLOCKED_ON_DEPENDENCY`
- Type: `IMPLEMENTATION | REVIEW | ARCHITECTURE | PLANNING | RESEARCH | MAINTENANCE | REPAIR`
- Owner: <agent or person>
- Risk: `LOW | MEDIUM | HIGH`
- Goal: <observable outcome>
- Parent roadmap: <direct path/link + authorization revision, or `none`>
- Related records: <only directly useful decision/evidence/handoff/review links, or `none`>
- Autonomous continuation: `YES | NO`

## Inputs and source of truth

- Inputs: <files, systems, evidence, or prior work to inspect/use>
- Authoritative sources: <what wins if context conflicts>
- Evidence labels: <VERIFIED / REPORTED / ASSUMED / UNKNOWN where relevant>
- Dependencies / preconditions: <none or named tasks/conditions>

## Change boundary

- MAY CHANGE: <every path/action this task may edit/create/perform>
- MUST NOT CHANGE: <paths, behavior, scope, or decisions outside this task>
- MAY CHANGE IF NECESSARY: <in-scope additions allowed after task amendment>
- HUMAN REAUTHORIZATION REQUIRED: <only actions that would cross inherited roadmap authority, or `none`>

## Decision authority

- Inherited roadmap authority: <permission envelope this task inherits>
- Owner may decide: <bounded implementation/task-shaping choices inside that envelope>
- Resolve internally first: <evidence/research/helper/tenth-seat questions that do not need human input>
- Human escalation only if: <true permission-envelope crossing or human-only authority/preference>

A child task does not require separate human approval merely because it is the
next roadmap item. If its work is inside the approved roadmap envelope, the
orchestration operator may shape, assign, execute, review, and close it.

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
- Operational independence: `REQUIRED | N/A — <reason>` (whole-gate `N/A` only for genuinely non-repeatable/one-off work per `OIG-NA-WHOLE`; repeatable work stays `REQUIRED`)
- Reproduction package: <first-time-user/manual reproduction instructions + source inputs/provenance + verification, plus automation (code/script/formulas/query/config/template) unless that component is `N/A — <reason>` per `OIG-NA-AUTO`>

For repeatable operational work, follow the
[Operational independence gate](../playbook/TASK_LIFECYCLE.md#operational-independence-gate).
Solve/discover the real process first when needed, then codify the successful
path so future operation does not depend on the original AI/session.

## Question-resolution ladder

For material uncertainty:

```text
authoritative evidence
→ safe inspection
→ focused helper/research
→ independent challenge when consequential
→ orchestration operator decides inside inherited authority
→ human only if the decision would cross that authority
```

A status update, review result, or completed child task is not a request for
permission to continue.

## Stop / escalate

Stop only the affected branch rather than guessing if a material authority,
safety, verification, or dependency boundary is reached.

- If the issue is inside inherited roadmap authority: research, consult helpers,
  amend/re-shape the task, re-run AGI, and continue.
- If it would leave inherited authority: record the exact proposed boundary
  crossing and seek human reauthorization.
- Continue independent in-scope work when safe rather than idling the whole
  roadmap.

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

- <only forward-relevant information; link detailed owner records instead of copying them>

## Completion / handoff

- Completed: <what is verified true now>
- Not completed: <remaining work or `none`>
- Reproduction package: <manual instructions + source inputs + verification path, plus automation unless `automation N/A — reason`; whole-gate `N/A — reason` only for genuinely one-off work>
- Current blocker: <none or exact blocker>
- Next eligible roadmap task: <task ID/path or `roadmap complete`>
- Human action required: <none or exact boundary decision>
