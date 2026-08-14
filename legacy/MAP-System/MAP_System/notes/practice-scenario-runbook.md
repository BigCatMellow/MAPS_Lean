# MAP Practice-Scenario Runbook

- status: CURRENT
- owner: codex-lab-kiri
- purpose: repeatable, operator-visible learning runs for MAP workflow tuning
- authority: planning and evidence only; normal task, decision, review, and release gates remain authoritative

## Retrieval capsule

- Purpose: Defines how MAP practice scenarios are admitted, bounded, measured, stopped, independently reviewed, and converted into evidence-backed tuning proposals without silently changing production policy.
- Proves: The required scenario packet, evidence destinations, operator decision points, scorecard, stop rules, ordinary fallback routing, independent review, and tuning loop.
- Applies to: Repeatable MAP coordination exercises that test one lifecycle question with visible core participants and named evidence paths.
- Does not provide: Permission to implement product changes, invent missing authority, approve a scenario automatically, replace normal task gates, or generalize policy from one run.
- Evidence type: procedure
- Status: current

## Objective

Run small, complete lifecycle exercises with an available core pair—normally
Codex as coordinator and Claude as independent contributor or reviewer—to test
whether MAP helps an operator reach a correct next action with less retrieval,
less coordination friction, and no hidden authority.

Each run answers one bounded question. It is not a standing agent role, a
background workflow, or permission to create policy from a single result.

## Admission checklist

Before starting, the coordinator records a scenario packet with all fields
below. If a field is unknown, stop and resolve it through the ordinary owner or
operator path rather than letting participants infer it.

```md
# Scenario packet — <ID>

- status: planned | running | complete | stopped
- coordinator: <core-agent>
- independent_role: <core-agent>
- operator_scope: <what the operator authorized>
- hypothesis: <one falsifiable claim>
- lifecycle_slice: intent | implementation | interruption | resume | review | release
- task_or_fixture: <one real low-risk task or isolated fixture>
- allowed_paths: <exact paths, or none>
- prohibited_actions: <writes, services, authority decisions, etc.>
- baseline_sources: <paths and commands>
- evidence_paths: packet=<path>; raw=<path(s)>; review=<path>; outcome=<path>
- operator_decision_points: scope_admission=<recorded decision or request>; during_run=<exact gates/blockers, or none>
- success_measure: <observable result>
- stop_conditions: <conditions that halt the run>
- review_owner: <different core agent>
```

Required boundaries:

- Use an existing task only with its owner’s consent or a recorded ownership
  transfer. Otherwise use a read-only fixture.
- No participant may claim, approve, release, deploy, or alter authority just
  because a scenario names that lifecycle stage.
- A model-backed helper may supply a bounded draft or contradiction pass only
  through the normal visible-helper rules; it never becomes a scenario owner.
- The Command Center remains the attention surface. A decision, conflict,
  blocker, or scope/privacy risk goes to the operator as an explicit request.

Evidence and decision routing are part of admission, not details to infer
later:

- `evidence_paths` names four destinations before the run: the packet itself,
  raw commands/results, independent review, and final outcome. A destination
  file need not exist yet, but its parent and intended owner must be known. If
  a destination is absent, ambiguous, inaccessible, or outside the authorized
  boundary, record `STOPPED` and return the packet to the coordinator through
  ordinary task/hcom routing. Do not improvise a storage location.
- `operator_decision_points` records the already-authorized scope admission
  and enumerates the only later scenario-specific gates or blockers expected
  to need an operator request. `during_run=none` is valid.
- An issue not listed in `operator_decision_points` does not gain operator
  priority merely because it occurred in a scenario. Pause or stop the run and
  classify it through normal MAP authority and hcom intent rules. Send a
  `request` only if the issue independently qualifies as a decision, approval,
  blocker, conflict, or scope/privacy risk; otherwise route it to the owner as
  ordinary work or record it as evidence.
- These fields expose existing authority and evidence routes. They create no
  new approval layer and do not let the scenario approve its own continuation.

## Standard run

1. **Freeze baseline.** Save the packet at its declared packet path, verify the
   remaining evidence destinations, record exact source paths, timestamps, and
   the expected first valid action before participant input.
2. **Assign two non-overlapping roles.** The coordinator owns integration;
   Claude (or another core agent) owns one independent bounded check such as
   contradiction, recovery, or review evidence. Announce the split over hcom.
3. **Execute one lifecycle slice.** Prefer a real low-risk transition or a
   controlled fixture. Record commands/results, not a reconstructed narrative.
4. **Handle interruptions explicitly.** If a terminal closes, a limit occurs,
   or an output is missing, record the event and stop or hand off. Do not count
   a claimed terminal action as delivery.
5. **Review independently.** A different core agent writes to the declared
   review path and checks the packet, evidence, authority boundary, and stated
   measure. Only BLOCKER/REQUIRED findings block the scenario verdict.
6. **Close the loop.** Record PASS, PARTIAL, FAIL, or STOPPED at the declared
   outcome path; state the next narrow experiment or why no change is
   justified.

## Scorecard

Record raw observations first, then interpret them. A lower number is not
automatically better if it skips a required safety read.

| Measure | Evidence | Good result |
|---|---|---|
| First-valid-action correctness | Scenario answer plus source citations | Correct action respects claim/review/authority state. |
| Retrieval cost | Count of required paths and commands | Only necessary governing sources were read. |
| Time and order | UTC timestamps and hcom/event IDs | Critical events are ordered and reproducible. |
| Handoff/fallback friction | Assignments, terminal state, output-path checks, cancellations | Failures are visible; duplicate/futile fallback work decreases. |
| Operator attention burden | Number/type of requests and time-to-decision | Requests are only genuine decisions or blockers. |
| Review/release outcome | Review record and task state | No self-approval; required findings are resolved. |
| Interruption/recovery | Handoff/snapshot and first action after resume | Recovery reaches a safe next action without chat archaeology. |
| Negative-result value | Failure reason and preserved baseline | A failed change is retained as evidence, not silently generalized. |

## Stop rules

Stop immediately and record `STOPPED` when any of these occurs:

- the next action would change agent authority, policy, deployment, or a task
  owned by another agent;
- the stated measure cannot be collected from durable evidence;
- a required source, reviewer, or visibility surface is unavailable;
- the run begins to require a new background process, state store, or broad
  implementation merely to continue;
- the operator withdraws scope or a privacy/security boundary appears.

Stopping is a valid result. Preserve the packet, evidence collected, and the
smallest missing prerequisite.

## Tuning loop

After review, classify the result:

- **PASS:** propose at most one follow-up task only if it names the lifecycle
  slice, measurable improvement, owned outputs, and review boundary.
- **PARTIAL:** repeat once with the smallest revised fixture or packet; do not
  claim system-wide benefit.
- **FAIL/STOPPED:** preserve the negative result in an experiment or test
  artifact. Create no task unless the blocker itself has a bounded owner and
  acceptance criteria.
- **Decision needed:** create an explicit command-center request. Do not encode
  the decision in a scenario conclusion.

Run one scenario at a time unless the operator explicitly approves independent
parallel lanes. Review the scorecard before selecting the next queue item.
