# Roadmap: GitHub-native asynchronous work pull

- State: `WORKING`

## Goal

Make separate ChatGPT browser sessions cooperate asynchronously through GitHub so the operator can start a role-bound session with a minimal `continue` instruction instead of manually relaying detailed handoffs.

Core model:

> **Operator binds roles. TOWER prioritizes. Assigned agents pull. GitHub coordinates.**

## Current reality

- Browser sessions are separate and cannot wake/message each other directly.
- GitHub is available to all sessions and already carries task, PR, branch, CI, review, and coordination evidence.
- MAPS already separates planning, development, independent review, and integration authority.
- A real browser trial exposed a routing defect: an unbound fresh session self-selected SENTINEL because the protocol said to recover its role without requiring explicit role binding.
- Role choice cannot be inferred from workload. The operator must bind each browser session to exactly one existing role before consequential work.
- Current throughput pain comes partly from manual handoff/orchestration and serial discovery, not from a need to weaken safety gates.
- `work/coordination/README.md` already establishes GitHub/live MAPS state as stronger than coordination notes and prohibits cross-owner note rewriting.

## DONE

The operator can bind separate tabs as TOWER, ANVIL, FOUNDRY, SENTINEL, and SWITCHYARD, then later say roughly `continue`; each bound session independently recovers live state, pulls the highest-priority eligible work inside its role, executes or blocks, and leaves durable GitHub evidence for the next role.

An unbound new session must not choose a role for itself.

## Final proof

Run at least one real browser-only chain where:

1. each participating browser session is explicitly operator-bound to one role;
2. an unbound control session refuses to self-select a role;
3. development finishes and leaves a review handoff without synchronous reviewer contact;
4. an independently bound reviewer later discovers and reviews it from GitHub;
5. bound SWITCHYARD later discovers the clean candidate and performs integration gates;
6. TOWER observes the resulting state transition and releases downstream work from actual accepted evidence;
7. the operator does not need to relay the detailed state between sessions.

## Boundaries

In scope:
- explicit browser-session role binding;
- shared GitHub-native pull protocol;
- standard durable handoff headings/contents;
- role startup/pull loops;
- safe parallelism rules;
- lightweight empirical rollout.

Not doing in v1:
- dynamic/self-selected roles;
- new service/daemon;
- new task database;
- automatic wakeups;
- automatic merge authority;
- mandatory per-agent inbox files;
- mandatory labels that become task truth.

## Phase 0 — protocol

- [x] Define shared protocol in `work/coordination/GITHUB_ASYNC_WORK_PULL.md`.
- [x] Require operator-bound browser roles; unbound sessions cannot pull consequential work.
- [x] Define role pull loops and eligibility checks.
- [x] Define developer -> review -> integration GitHub handoff pattern.
- [x] Preserve existing authority and low-contention rules.
- [ ] Independent review of protocol, including the role-self-selection repair.
- [ ] SWITCHYARD integration after clean review.

## Phase 1 — browser trial

After the protocol is accepted:

- [ ] Start one tab explicitly bound as TOWER; it maintains priorities only.
- [ ] Start one tab explicitly bound as ANVIL; it discovers development work only.
- [ ] Start one tab explicitly bound as FOUNDRY; it discovers development/repair work only.
- [ ] Start one tab explicitly bound as SENTINEL; it discovers independent review work only.
- [ ] Start one tab explicitly bound as SWITCHYARD; it discovers integration work only.
- [ ] Start one generic/unbound control tab; verify it reports `UNBOUND — role assignment required` rather than choosing a lane.
- [ ] Record only concrete discovery failures/friction; do not add machinery based on speculation.

Checkpoint outcome:
- `CONTINUE` if bound browser agents reliably discover role-appropriate work and unbound sessions refuse self-selection;
- `CHANGE` if routing remains ambiguous or role drift occurs;
- `CUT SCOPE` if extra coordination features create more maintenance than they remove.

## Phase 2 — only if evidence justifies it

Potential derived conveniences, not authorities:

- optional GitHub labels such as role/review/integration hints;
- generated role inbox views;
- standardized query/search conventions;
- automation that prepares synchronization/CI/review packets while leaving consequential decisions with the existing role.

Add any of these only after Phase 1 demonstrates a repeated failure that the feature directly fixes.

## Design guardrails

- Operator binds each browser session to exactly one role.
- Agents never choose or switch permanent role merely because another queue has work.
- One fact / one authority.
- Coordination state is derived routing evidence, not canonical task truth.
- A work item is pulled only after live eligibility verification.
- Agents do not race mutable outputs.
- Independent reviewers do not patch reviewed work.
- TOWER priority never grants execution/review/merge authority.
- SWITCHYARD integration gates remain intact.
- Idle agents do not manufacture work or change lanes.

## Operator usage after acceptance

First bind a tab, for example:

`Your role is ANVIL. Continue under work/coordination/GITHUB_ASYNC_WORK_PULL.md.`

After that tab is bound, later prompts can be:

`Continue. Recover live GitHub state and pull the highest-priority eligible work for your bound role. Record your result on GitHub and stop at your role boundary.`
