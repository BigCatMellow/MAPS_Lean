# GitHub-native asynchronous work-pull protocol

Status: proposed shared coordination protocol for browser-only multi-agent operation.

## Why this exists

When MAPS agents are separate ChatGPT browser sessions, they cannot reliably message or wake one another directly. GitHub is the one durable shared surface available to every session.

The coordination model is therefore:

> **TOWER prioritizes. Agents pull. GitHub coordinates.**

```text
operator starts browser sessions
            |
          TOWER
  derived priority / dependencies
            |
          GitHub
   live repository + task/PR evidence
     /        |         |        \
  ANVIL    FOUNDRY   SENTINEL  SWITCHYARD
       each role pulls eligible work
```

This protocol is a coordination method only. It does **not** create a second task database, review authority, branch authority, or merge authority.

## Sources of truth

Use existing authority, in this order:

1. operator / policy authority;
2. canonical MAPS task state and task contract;
3. live GitHub repository, PR, branch, CI, and review evidence;
4. TOWER roadmaps / dispatch notes / coordination comments as derived routing evidence only.

If a coordination note conflicts with live or canonical state, the note loses.

## Browser-session startup rule

When the operator says **continue**, **go**, or otherwise starts an agent session, the agent should not wait for a bespoke handoff from another session.

The agent should:

1. recover current `main`;
2. read its role contract and this protocol;
3. inspect current GitHub task/PR/review/CI/coordination evidence relevant to its role;
4. find the highest-priority **eligible** work for that role;
5. verify ownership, dependencies, authority, exact head/base, and stop conditions;
6. execute until completion or a concrete blocker;
7. record the result on GitHub so the next role can discover it;
8. stop at its role boundary.

If no work is eligible, remain idle. Do not invent work to stay busy.

## Eligibility

A TOWER priority item is not automatically executable.

Before pulling work, verify the underlying contract. For consequential implementation this normally includes:

- task is legitimately `READY` / `AGI READY` as required;
- dependencies are accepted/stable;
- no conflicting owner or mutable-output claim exists;
- the role is allowed to perform the work;
- required authority exists;
- the current exact GitHub state still matches the handoff.

If any load-bearing fact is unknown, inspect or block rather than guess.

## Handoff model: agent -> GitHub state transition

Prefer durable GitHub evidence over direct agent-to-agent conversation.

### Development -> review

Developer finishes bounded work, then records on the owning PR/task:

- exact head/base;
- exact intended delta;
- verification / CI evidence;
- known limitations or blockers;
- explicit request for independent review;
- statement that the developer is freezing/stopping unless review returns a defect.

Suggested heading:

`MAPS HANDOFF — READY FOR INDEPENDENT REVIEW`

The developer does not need SENTINEL to be online.

### Review -> integration or repair

An eligible independent reviewer discovers review-ready work, reviews the exact state, and records one of:

- `CLEAN IN-LAYER` / equivalent clean disposition;
- `CHANGES REQUIRED` with concrete defect and required correction;
- `NOT READY` with exact freshness/CI/ancestry reason.

Suggested heading:

`MAPS REVIEW DISPOSITION — <result>`

If clean, the result becomes discoverable integration evidence. If defective, the implementation owner can discover and pull the repair later.

### Integration -> accepted main or blocker

SWITCHYARD discovers reviewed candidates and performs the normal integration gates:

- recover current main;
- genuine synchronization using real ancestry;
- exact delta verification;
- fresh exact-head CI;
- eligible integrated-head independent review where required;
- merge only under existing authority and expected-head protection.

Suggested heading:

`MAPS INTEGRATION HANDOFF — <result>`

Accepted main then becomes the dependency-release fact for downstream work.

## Role pull loops

### TOWER

Pull: current repository/project planning work.

Do:
- recover live state;
- maintain a **derived** priority/dependency view;
- identify eligible vs blocked work;
- update shared roadmap/dispatch evidence when material state changes;
- surface operator decisions only when evidence cannot resolve them.

Do not:
- create canonical task truth from the queue;
- approve independent review;
- merge;
- repair another role's branch without a valid handoff.

### ANVIL / FOUNDRY

Pull: highest-priority eligible development/repair task assigned or legitimately available to that development lane.

Do:
- implement the smallest task-authorized change;
- test it;
- publish exact evidence;
- freeze at review/integration boundary.

Do not:
- start downstream work on unaccepted ancestry just because the upstream looks likely to pass;
- self-approve;
- absorb another lane's work to avoid waiting.

### SENTINEL

Pull: highest-priority review-ready item for which reviewer independence is preserved.

Do:
- verify exact state and CI;
- evidence-test the task/implementation;
- record exact disposition;
- return defects to owner and freshness/integration blockers to SWITCHYARD.

Do not:
- patch work being independently reviewed;
- treat TOWER priority as proof of readiness.

### SWITCHYARD

Pull: highest-priority reviewed integration candidate whose prerequisites are satisfied.

Do:
- synchronize;
- verify exact ancestry/delta;
- require fresh evidence;
- merge only when existing integration gates and authority are satisfied.

Do not:
- merge merely because work is high priority;
- take over feature development unless a specific integration defect is legitimately returned.

## Parallelism rule

Browser sessions do not need to take turns if their work is genuinely independent.

Safe example:

```text
SENTINEL    reviews Context Builder
FOUNDRY     repairs unrelated communication work
SWITCHYARD  integrates environment evidence
TOWER       refreshes dependency/priority view
```

Unsafe parallelism includes:

- two agents editing the same branch/output;
- downstream implementation on unstable upstream ancestry;
- reviewer modifying the work they must independently approve;
- multiple agents independently synchronizing the same integration candidate.

## Operator workflow

The operator should be able to keep role-specific browser tabs and use a minimal instruction such as:

> `Continue. Recover live GitHub state and pull the highest-priority eligible work for your role under work/coordination/GITHUB_ASYNC_WORK_PULL.md.`

The operator still has to start/wake browser sessions. The protocol removes the need to manually relay detailed handoffs between sessions.

## What v1 intentionally does NOT add

Do not add these merely because they are possible:

- another task database;
- a daemon or scheduler;
- an agent-to-agent messaging service;
- mandatory GitHub labels as a second mutable truth;
- per-agent inbox files that must be kept synchronized with tasks/PRs;
- automatic merge authority.

If browser use later shows that discovery is still too costly, labels or generated inbox views may be added as **derived projections** from canonical/live state, never as authority.

## Success test

This protocol is working when the operator can open any role-specific browser session, say roughly **continue**, and that agent can independently discover:

- what it should do now;
- what it must not touch;
- what it is waiting for;
- what exact evidence proves the wait is over;
- where to record its result so another role can discover it.
