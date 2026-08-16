# GitHub-native asynchronous work-pull protocol

Status: proposed shared coordination protocol for browser-only multi-agent operation.

## Why this exists

When MAPS agents are separate ChatGPT browser sessions, they cannot reliably message or wake one another directly. GitHub is the one durable shared surface available to every session.

The coordination model is therefore:

> **Operator binds roles. TOWER prioritizes. Assigned agents pull. GitHub coordinates.**

```text
operator starts + binds browser sessions
                 |
               TOWER
       derived priority / dependencies
                 |
               GitHub
        live repository + task/PR evidence
          /        |         |        \
       ANVIL    FOUNDRY   SENTINEL  SWITCHYARD
            each bound role pulls eligible work
```

This protocol is a coordination method only. It does **not** create a second task database, review authority, branch authority, or merge authority.

## Mandatory role binding

A browser session **MUST NOT choose its own permanent role** from repository activity, workload, open PRs, apparent demand, or whichever lane looks most useful.

A new browser session begins `UNBOUND` unless its role is already explicit in that conversation. The operator binds the session to exactly one role:

- `TOWER` — planning / priority / dispatch;
- `ANVIL` — development;
- `FOUNDRY` — development / repair;
- `SENTINEL` — independent review;
- `SWITCHYARD` — integration / merge safety.

Examples of valid binding:

- `Your role is ANVIL. Continue under the GitHub async work-pull protocol.`
- `You are SENTINEL for this browser session. Recover live state and continue.`

An `UNBOUND` session may inspect public repository state to orient itself, but it must not claim consequential work, approve review, modify an owned feature branch, synchronize an integration candidate, or merge.

If a generic startup prompt omits the role, the session must report `UNBOUND — role assignment required`; it must **not infer or self-select** a role.

Role binding does not grant extra authority. It only tells the session which existing MAPS lane it is allowed to operate within. All task, ownership, review, and integration gates still apply.

## Sources of truth

Use existing authority, in this order:

1. operator / policy authority, including browser-session role binding;
2. canonical MAPS task state and task contract;
3. live GitHub repository, PR, branch, CI, and review evidence;
4. TOWER roadmaps / dispatch notes / coordination comments as derived routing evidence only.

If a coordination note conflicts with live or canonical state, the note loses.

## Browser-session startup rule

When the operator says **continue**, **go**, or otherwise starts a role-bound agent session, the agent should not wait for a bespoke handoff from another session.

The agent should:

1. confirm its operator-bound role; if none is explicit, remain `UNBOUND` and stop before consequential work;
2. recover current `main`;
3. read its role contract and this protocol;
4. inspect current GitHub task/PR/review/CI/coordination evidence relevant to its bound role;
5. find the highest-priority **eligible** work for that role;
6. verify ownership, dependencies, authority, exact head/base, and stop conditions;
7. execute until completion or a concrete blocker;
8. record the result on GitHub so the next role can discover it;
9. stop at its role boundary.

If no work is eligible, remain idle. Do not invent work or switch roles to stay busy.

## Eligibility

A TOWER priority item is not automatically executable.

Before pulling work, verify the underlying contract. For consequential implementation this normally includes:

- the browser session is explicitly bound to the required role;
- task is legitimately `READY` / `AGI READY` as required;
- dependencies are accepted/stable;
- no conflicting owner or mutable-output claim exists;
- the bound role is allowed to perform the work;
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

Pull: highest-priority eligible development/repair task assigned or legitimately available to that bound development lane.

Do:
- implement the smallest task-authorized change;
- test it;
- publish exact evidence;
- freeze at review/integration boundary.

Do not:
- start downstream work on unaccepted ancestry just because the upstream looks likely to pass;
- self-approve;
- absorb another lane's work to avoid waiting;
- switch to SENTINEL/SWITCHYARD because review/integration work is available.

### SENTINEL

Pull: highest-priority review-ready item for which reviewer independence is preserved.

Do:
- verify exact state and CI;
- evidence-test the task/implementation;
- record exact disposition;
- return defects to owner and freshness/integration blockers to SWITCHYARD.

Do not:
- patch work being independently reviewed;
- treat TOWER priority as proof of readiness;
- switch to implementation or integration because those queues are non-empty.

### SWITCHYARD

Pull: highest-priority reviewed integration candidate whose prerequisites are satisfied.

Do:
- synchronize;
- verify exact ancestry/delta;
- require fresh evidence;
- merge only when existing integration gates and authority are satisfied.

Do not:
- merge merely because work is high priority;
- take over feature development unless a specific integration defect is legitimately returned;
- switch to review/development because integration is temporarily idle.

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

- multiple unbound sessions independently deciding to become the same role;
- two agents editing the same branch/output;
- downstream implementation on unstable upstream ancestry;
- reviewer modifying the work they must independently approve;
- multiple agents independently synchronizing the same integration candidate.

## Operator workflow

Keep role-specific browser tabs. Bind each tab once and keep that role for the life of the session.

Suggested startup prompts:

- `Your role is TOWER. Continue under work/coordination/GITHUB_ASYNC_WORK_PULL.md.`
- `Your role is ANVIL. Continue under work/coordination/GITHUB_ASYNC_WORK_PULL.md.`
- `Your role is FOUNDRY. Continue under work/coordination/GITHUB_ASYNC_WORK_PULL.md.`
- `Your role is SENTINEL. Continue under work/coordination/GITHUB_ASYNC_WORK_PULL.md.`
- `Your role is SWITCHYARD. Continue under work/coordination/GITHUB_ASYNC_WORK_PULL.md.`

After binding, later prompts can usually be just:

> `Continue. Recover live GitHub state and pull the highest-priority eligible work for your bound role.`

The operator still has to start/wake browser sessions. The protocol removes the need to manually relay detailed handoffs between sessions.

## What v1 intentionally does NOT add

Do not add these merely because they are possible:

- dynamic self-selection of roles;
- another task database;
- a daemon or scheduler;
- an agent-to-agent messaging service;
- mandatory GitHub labels as a second mutable truth;
- per-agent inbox files that must be kept synchronized with tasks/PRs;
- automatic merge authority.

If browser use later shows that discovery is still too costly, labels or generated inbox views may be added as **derived projections** from canonical/live state, never as authority.

## Success test

This protocol is working when the operator can open role-specific browser sessions, bind each one once, and later say roughly **continue**; each agent can independently discover:

- what it should do now within its bound role;
- what it must not touch;
- what it is waiting for;
- what exact evidence proves the wait is over;
- where to record its result so another role can discover it.

It fails if a new unbound browser session can plausibly decide for itself that it is SENTINEL, ANVIL, FOUNDRY, SWITCHYARD, or TOWER.