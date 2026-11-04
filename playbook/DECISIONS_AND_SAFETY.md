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

## THINK-informed decision restraint (selective adaptation)

Use this only when a decision is materially ambiguous or consequential; it is
not a mandatory reasoning stage for routine, already-clear work.

- **Execute directly** when the goal, permission, and next safe action are
  clear. Do not summon a panel of methods or generate alternatives to justify
  an obvious action.
- **Investigate** when plausible causes or interpretations would produce
  different actions. Separate observation, candidate explanation, and the
  smallest evidence that would distinguish them.
- **Critique** a consequential confident proposal with a real counterexample,
  failure mode, or alternative explanation. Do not treat repeated generic
  skepticism as additional evidence.
- **Reframe** only when material repeated failures point to a shared mistaken
  assumption; test that hypothesis before a broad redesign.
- **Decide or stop** when further reasoning is unlikely to change the next
  authorized action. Preserve `UNKNOWN` when the missing fact matters.

For a material choice, retain the chosen route, rejected *material*
alternative(s), assumptions/unknowns, decisive evidence, and a condition that
would reverse the choice. A short decision note is sufficient; do not create
an idea database or branching tree by default.

This is a **lightweight operational adaptation**, not an adoption of the Pilot
THINK research runtime. Pilot evidence supports efficient structured reasoning
but did **not** establish that dynamic method routing or shallow multi-branch
search merits default use. See the
[THINK scope](https://github.com/BigCatMellow/Pilot_Projects/blob/main/ai-creativity-and-ideation/THINK_PROJECT.md)
and [evaluated retrospective](https://github.com/BigCatMellow/Pilot_Projects/blob/main/autonomous-programs/project-evaluation/findings/PE-THINK-V1-full-retrospective.md).
Future mechanisms require explicit scoped evaluation before promotion.

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
