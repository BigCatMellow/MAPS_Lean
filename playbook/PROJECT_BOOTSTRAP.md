# Project Bootstrap

Use for a project expected to span sessions, accumulate multiple tasks, or use
more than one agent. Skip it for a throwaway experiment or small local fix.

## Project flow

**Look at reality. Define the destination. Plan backward. Challenge the plan. Execute forward. Adapt as you learn.**

1. **Look at reality first.** Inspect the current product, code, users, data,
   constraints, prior attempts, or other direct evidence that matters. Record
   what was actually checked and separate verified facts from assumptions. Do
   not build a roadmap mainly from assumptions when the facts can be checked.
2. Define the goal and a concrete definition of **DONE**: what must exist, work,
   or be proven when the project is complete, especially from the user or
   operator's point of view. DONE must be testable or otherwise observable.
3. Set boundaries before designing the solution:
   - what is in scope;
   - what is explicitly not being done;
   - how much time, effort, or cost the project is worth before reconsidering;
   - important unknowns that may require research or a small prototype first.
4. Make a **draft backward plan**. Ask what must be true immediately before
   DONE, then what must be true before that. Continue until the chain reaches
   the current state. If a required condition is unknown, record the unknown;
   do not invent certainty.
5. Turn that chain into a **draft forward roadmap**. Name likely phases,
   dependencies, integration points, final verification, and work that may run
   in parallel. Do not over-plan distant work yet.
6. Record quality standards, assumptions, unanswered research questions,
   risks, and decision boundaries. Convert dangerous unknowns into research,
   inspection, or prototype work before betting the project on them.
7. For a multi-agent or consequential project, hold a short **mission meeting**
   before implementation. The accountable owner presents the goal and draft
   roadmap; relevant agents challenge missing steps, bad assumptions,
   dependencies, risks, verification, scope, and useful parallel work. The
   operator resolves decisions that affect scope, cost, risk, or user-visible
   behavior.
8. The mission meeting must produce concrete outputs, not just discussion:
   - accepted or changed assumptions;
   - roadmap changes;
   - unresolved questions and who owns resolving them;
   - the first wave of work;
   - any operator decision still required.
9. Revise the draft into the **working roadmap**. Record the first wave of
   assignments, not every future assignment. The meeting does not grant
   authority by itself; approved project/task records remain authoritative.
10. Before a first-wave implementation task starts, its task record must state
    owner, allowed outputs, dependencies, acceptance criteria, verification,
    and required review. If those cannot be stated without guessing, shape or
    research the task first.
11. Create locations for tasks, decisions, evidence, handoffs, and useful
    discoveries.
12. Start execution when the first-wave tasks are clear enough to own, verify,
    and finish.
13. Revisit the roadmap when evidence changes assumptions, dependencies, risk,
    scope, or the route to DONE. Refine later phases as they get closer instead
    of pretending the original plan is certain.
14. Require an explicit checkpoint at least:
    - after each major phase or usable end-to-end result;
    - when a key assumption fails;
    - when a named risk becomes real;
    - when the effort limit is reached or likely to be exceeded; or
    - before a consequential or hard-to-reverse change.
15. At a checkpoint choose and record one result: **CONTINUE, CHANGE, CUT SCOPE,
    RESEARCH, or STOP**. State why and what happens next. Do not keep spending
    effort on a route that no longer makes sense.
16. Finish only when the final proof for DONE passes. If the final proof cannot
    be performed, the project is not DONE; record the blocker instead.

The mission meeting is a planning check, not ceremony. Do not summon extra
agents for a simple task or invent roles merely to have a meeting.

## Planning horizon

Plan the whole project, but not at equal detail:

- **Destination:** precise definition of DONE and final proof.
- **Current phase:** detailed enough to expose dependencies and integration.
- **First-wave tasks:** very detailed, owned, and testable.
- **Later phases:** broad enough to preserve direction; refine them when closer.

This keeps the roadmap useful without turning guesses about the distant future
into fake certainty.

## Agent clarity rule

For work that is ready to execute, an agent should not have to guess the basic
contract. Make these explicit:

- **Input:** what facts, files, systems, or prior work to use.
- **Output:** what must be produced or changed.
- **Owner:** who is accountable for the work.
- **Boundaries:** what may and may not be changed.
- **Pass/fail:** how success will be judged.
- **Verification:** what evidence must be produced.
- **Stop/escalate:** when to stop, research, ask, or route a decision upward.

If one of these is materially unknown, do not silently invent it.

## Minimum project brain

A new agent should be able to answer:

- What are we making, and for whom?
- What facts about the current situation have actually been checked?
- What exactly counts as DONE?
- What are we deliberately not doing?
- How much effort is this worth before we reconsider?
- What is the current working roadmap from here to DONE?
- What is the next wave of work?
- What is unknown or risky?
- Who decides what?
- What can happen in parallel?
- How will the final result be verified?
- What evidence would cause the roadmap to change or stop?
- Where do tasks, decisions, handoffs, evidence, and useful new ideas go?

Use [the project brief template](../templates/project-brief.md),
[the roadmap template](../templates/roadmap.md),
[the task template](../templates/task.md),
[the decision template](../templates/decision.md), and
[the risk-register template](../templates/risk-register.md) as the initial kit.
Add folders only when the work calls for them.
