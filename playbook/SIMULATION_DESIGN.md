# Simulation Design

Use simulations as controlled usability tests of the active project brain—not
as a proxy for whether an agent can produce a plausible answer.

## Design a useful scenario

1. Name one role and one bounded outcome: implementer, reviewer, coordinator,
   researcher, incident responder, or returning agent.
2. Provide only the realistic starting materials that role would receive.
3. Include one controlled trap: tempting but irrelevant guidance, conflicting
   secondary state, a missing link, stale context, or an unclear authority
   boundary.
4. State the safe expected conclusion. It may be `BLOCKED`; do not force an
   agent to invent a repair or proceed without authority.
5. Assign an independent reviewer and exact output paths before starting.

## Required observable behavior

For a question-led simulation, require **two to four** concise live updates in
the form `question or assumption → next step`. They must reveal route choice
and uncertainty without pausing for a non-blocking reply.

The task should also require the helper to report:

- the active links or documents actually followed;
- relevant methods considered and why they were selected or rejected;
- documents deliberately not read and why;
- searches, runtime access, and writes attempted (normally none except the
  declared outputs); and
- the authority, evidence, and escalation boundary.

## Score failures precisely

Classify each finding before changing guidance:

| Class | Meaning | Typical repair |
| --- | --- | --- |
| Navigation | The right document/template could not be reached | Add or repair an active link. |
| Comprehension | It was reached but applied incorrectly | Clarify the method or template. |
| Governance | It recommended an unauthorized action | Strengthen authority/evidence gates. |
| Observability | It acted correctly but did not expose its reasoning | Require bounded live updates or an explicit route record. |
| Scope | It read or changed irrelevant material | Tighten task boundaries and route selection. |

## Review and learning loop

An independent reviewer checks acceptance criteria, output scope, link targets,
and whether the result stays inside its authority. Record the scenario, route,
result, friction, repair, and regression test in its task/review record.

When a repair is made, run the smallest focused regression scenario that can
falsify it. Run durable workflows in two modes where useful:

1. **Cold start:** an agent begins from Lean root.
2. **Returning agent:** a session has restarted and the agent has only the
   task, current state, and a compact prior handoff.

Use [Task Lifecycle](TASK_LIFECYCLE.md), [Helpers and Communication](HELPERS_AND_COMMUNICATION.md),
[Context](../docs/CONTEXT.md), and [the review template](../templates/review.md)
to shape and evaluate the simulation.
