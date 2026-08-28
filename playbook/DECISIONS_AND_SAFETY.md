# Decisions, Permissions, and Safety

Capability, assignment, ownership, authority, and approval are different.
Permission comes from repository rules plus the approved roadmap/task envelope.

## Standing authorization

Human approval should normally happen at the scope/roadmap level, not before
every child task or implementation decision.

Once a roadmap is approved for autonomous execution, that approval authorizes
all reasonably necessary actions inside its stated permission envelope,
including task shaping, helper dispatch, implementation choices, testing,
review routing, routine commits/PRs, reconciliation, and progression to the next
eligible roadmap item.

Do not ask for fresh human approval merely because a new child task starts, a
checkpoint is reached, review completes, or another in-scope implementation
choice appears.

## Decision ladder

For a material decision:

1. inspect authoritative evidence;
2. perform safe inspection/reproduction;
3. use focused research/helper agents;
4. use an independent challenger when consequential uncertainty remains;
5. let the orchestration operator decide if the choice stays inside the approved
   permission envelope;
6. escalate to the human only if the decision would cross that envelope or
   requires human-only authority/preference.

Record a durable decision when it materially changes architecture, security,
data handling, external behavior, a standing rule, or future work. The record is
for continuity, not a human approval ceremony.

## Human reauthorization boundary

Fresh human authorization is required when the proposed action would materially
leave the approved envelope, for example:

- changing the approved objective or materially expanding scope;
- acting against an explicit roadmap exclusion;
- new spending, credential/permission grants, legal consent, or publication not
  already authorized;
- an irreversible/destructive action not specifically preauthorized; or
- an irreducibly subjective preference that materially changes the intended
  result and cannot be resolved from the approved specification/evidence.

If only one branch crosses the boundary, block that branch and continue
independent authorized work when safe.

## Destructive and irreversible actions

A destructive/irreversible action may proceed without another human prompt only
when the approved roadmap/task explicitly preauthorizes it with enough precision
to know what was authorized:

1. bounded target or target class;
2. expected impact/limits;
3. safer reversible alternative considered when practical;
4. rollback/recovery path when possible; and
5. verification/evidence required afterward.

If those conditions are not present, obtain fresh human authorization for the
actual resolved action before executing it.

Never treat a broad goal as permission for an irreversible action whose target
or impact has not been resolved.

## Security, privacy, and external boundaries

- Keep credentials/secrets out of chat, logs, commits, screenshots, and helper
  prompts where possible.
- Treat publication, permission changes, sensitive data movement, spending, and
  material external side effects as explicit permission-envelope fields.
- Apply least privilege to agents/helpers.
- Security/privacy-sensitive work gets verification and independent review
  proportional to risk.
- Security/privacy uncertainty inside an already approved bounded policy should
  be researched/reviewed internally first; escalate only when the proposed
  resolution would change the approved posture or cross authority.

## Core rule

**Approved roadmap = standing authority to execute inside its envelope.**
Visibility, checkpoints, reviews, and status reports do not revoke that authority
or create new human approval gates.
