# Roadmap: GitHub-native asynchronous work pull

- State: `WORKING`

## Goal

Make separate ChatGPT browser sessions cooperate asynchronously through GitHub so the operator can start a role session with a minimal `continue` instruction instead of manually relaying detailed handoffs.

Core model:

> **TOWER prioritizes. Agents pull. GitHub coordinates.**

## Current reality

- Browser sessions are separate and cannot wake/message each other directly.
- GitHub is available to all sessions and already carries task, PR, branch, CI, review, and coordination evidence.
- MAPS already separates planning, development, independent review, and integration authority.
- Current throughput pain comes partly from manual handoff/orchestration and serial discovery, not from a need to weaken safety gates.
- `work/coordination/README.md` already establishes GitHub/live MAPS state as stronger than coordination notes and prohibits cross-owner note rewriting.

## DONE

The operator can start ANVIL, FOUNDRY, SENTINEL, SWITCHYARD, or TOWER in separate browser tabs and say roughly `continue`; each session can independently recover live state, pull the highest-priority eligible role-appropriate work, execute or block, and leave durable GitHub evidence for the next role.

## Final proof

Run at least one real browser-only chain where:

1. development finishes and leaves a review handoff without synchronous reviewer contact;
2. an independent reviewer later discovers and reviews it from GitHub;
3. SWITCHYARD later discovers the clean candidate and performs integration gates;
4. TOWER observes the resulting state transition and releases downstream work from actual accepted evidence;
5. the operator does not need to relay the detailed state between sessions.

## Boundaries

In scope:
- shared GitHub-native pull protocol;
- standard durable handoff headings/contents;
- role startup/pull loops;
- safe parallelism rules;
- lightweight empirical rollout.

Not doing in v1:
- new service/daemon;
- new task database;
- automatic wakeups;
- automatic merge authority;
- mandatory per-agent inbox files;
- mandatory labels that become task truth.

## Phase 0 — protocol

- [x] Define shared protocol in `work/coordination/GITHUB_ASYNC_WORK_PULL.md`.
- [x] Define role pull loops and eligibility checks.
- [x] Define developer -> review -> integration GitHub handoff pattern.
- [x] Preserve existing authority and low-contention rules.
- [ ] Independent review of protocol.
- [ ] SWITCHYARD integration after clean review.

## Phase 1 — browser trial

After the protocol is accepted:

- [ ] TOWER uses it when producing/refreshing priorities.
- [ ] ANVIL browser session is started with a minimal `continue` instruction and must discover its own eligible work.
- [ ] FOUNDRY does the same for its lane.
- [ ] SENTINEL discovers review-ready work without operator-provided PR details.
- [ ] SWITCHYARD discovers integration-ready work without operator-provided PR details.
- [ ] Record only concrete discovery failures/friction; do not add machinery based on speculation.

Checkpoint outcome:
- `CONTINUE` if browser agents reliably discover work from GitHub;
- `CHANGE` if routing is repeatedly ambiguous;
- `CUT SCOPE` if extra coordination features create more maintenance than they remove.

## Phase 2 — only if evidence justifies it

Potential derived conveniences, not authorities:

- optional GitHub labels such as role/review/integration hints;
- generated role inbox views;
- standardized query/search conventions;
- automation that prepares synchronization/CI/review packets while leaving consequential decisions with the existing role.

Add any of these only after Phase 1 demonstrates a repeated failure that the feature directly fixes.

## Design guardrails

- One fact / one authority.
- Coordination state is derived routing evidence, not canonical task truth.
- A work item is pulled only after live eligibility verification.
- Agents do not race mutable outputs.
- Independent reviewers do not patch reviewed work.
- TOWER priority never grants execution/review/merge authority.
- SWITCHYARD integration gates remain intact.
- Idle agents do not manufacture work.

## Operator usage after acceptance

Suggested browser prompt:

`Continue. Recover live GitHub state and pull the highest-priority eligible work for your role under work/coordination/GITHUB_ASYNC_WORK_PULL.md. Record your result on GitHub and stop at your role boundary.`
