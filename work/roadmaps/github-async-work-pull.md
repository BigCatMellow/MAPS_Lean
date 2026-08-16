# Roadmap: GitHub-native asynchronous work pull

- State: `WORKING`

## Goal

Make separate ChatGPT browser sessions cooperate asynchronously through GitHub so the operator can start role-bound sessions with minimal `continue` instructions instead of manually relaying detailed handoffs.

Core model:

> **Operator binds roles. TOWER prioritizes. Assigned agents pull. GitHub coordinates.**

## Current reality

- Browser sessions are separate and cannot wake/message each other directly.
- GitHub is available to all sessions and already carries task, PR, branch, CI, review, and coordination evidence.
- MAPS already separates planning, development, independent review, and integration authority.
- A real browser trial exposed a routing defect: an unbound fresh session self-selected SENTINEL because the protocol said to recover its role without requiring explicit role binding.
- Role choice cannot be inferred from workload. The operator must bind each browser session to exactly one existing role before consequential work.
- A second live operational gap was confirmed: a large open-PR backlog needs one persistent control owner so blocked/awaiting PRs do not become abandoned while agents focus on one item at a time.
- SWITCHYARD is therefore the standing PR-control lane for the entire live open-PR queue, while TOWER remains priority/planning authority and SENTINEL remains independent review.
- A third live throughput gap is now confirmed: several root PRs can reach fresh integrated-head review at the same time, causing development and integration lanes to wait behind one SENTINEL browser continuity.
- Live examples at this checkpoint include synchronized/in-review roots #44 and #48 plus synchronized #41 moving through fresh CI/review. This is enough evidence to scale reviewer capacity without weakening the review requirement.
- SENTINEL should therefore operate as one review role with multiple explicitly operator-bound browser continuities when review demand justifies it.
- A fourth integration-safety concern is explicit: backlog processing must never use PR age as merge order or let a historical branch overwrite newer accepted `main`. Integration order is dependency-first, and every candidate must be synchronized forward onto latest accepted `main` before merge.
- Current throughput pain comes from manual handoff/orchestration, serial discovery, deep dependency stacks, and serial independent review—not from a need to weaken safety gates.
- `work/coordination/README.md` already establishes GitHub/live MAPS state as stronger than coordination notes and prohibits cross-owner note rewriting.

## DONE

The operator can bind separate tabs as TOWER, ANVIL, FOUNDRY, one or more SENTINEL reviewer continuities, and SWITCHYARD, then later say roughly `continue`; each bound session independently recovers live state, pulls eligible work inside its role, executes or blocks, and leaves durable GitHub evidence for the next role.

An unbound new session must not choose a role for itself.

When review is the bottleneck, the operator can bind `SENTINEL-A`, `SENTINEL-B`, `SENTINEL-C`, etc. as distinct browser continuities sharing the same SENTINEL role. They claim different eligible exact-head reviews through GitHub, preserve continuity-specific independence, and do not duplicate review work while other eligible reviews are unclaimed.

While SWITCHYARD is active, every open PR has a current disposition, next legitimate gate, and discoverable owner/blocker, and SWITCHYARD continues advancing independent eligible PR-control work instead of idling behind one blocked PR.

Dependency stacks are integrated bottom-up: accepted roots first, then downstream layers synchronized onto the newly accepted main state. PR age/number is never the integration authority. Historical branches cannot silently replace or revert newer accepted behavior.

## Final proof

Run at least one real browser-only chain where:

1. each participating browser session is explicitly operator-bound to one role;
2. an unbound control session refuses to self-select a role;
3. development finishes and leaves a review handoff without synchronous reviewer contact;
4. at least two distinct operator-bound SENTINEL continuities recover the same live review queue and claim different eligible exact heads;
5. each SENTINEL continuity verifies it is independent of the work it claims and reviews without branch mutation;
6. a same-head claim race, if exercised, converges on one primary reviewer by GitHub claim ordering unless multiple reviews are explicitly required;
7. abandoned/stale review claims do not permanently block another eligible SENTINEL from taking over;
8. bound SWITCHYARD discovers clean candidates and performs integration gates;
9. SWITCHYARD derives integration order from dependency structure rather than PR age/number;
10. for a stacked chain, SWITCHYARD accepts the root first and synchronizes each dependent onto the newly accepted `main` before its own merge;
11. a deliberately stale historical candidate cannot silently revert or delete newer accepted behavior outside explicit current authority;
12. after each merge, remaining candidates are rechecked for ancestry/delta/CI/review freshness;
13. SWITCHYARD enumerates the full live open-PR backlog and gives every PR a current disposition / next gate / owner or blocker;
14. when one PR waits on another role, SWITCHYARD advances another independent eligible PR-control item rather than waiting;
15. TOWER observes resulting state transitions and releases downstream work from actual accepted evidence;
16. the operator does not need to relay detailed state between sessions.

## Boundaries

In scope:
- explicit browser-session role binding;
- multiple explicitly bound browser continuities sharing the SENTINEL role;
- lightweight exact-head review claims for duplicate-work avoidance;
- dependency-first integration ordering;
- current-main anti-regression synchronization gates;
- shared GitHub-native pull protocol;
- persistent SWITCHYARD PR backlog control;
- standard durable handoff headings/contents;
- role startup/pull loops;
- safe parallelism rules;
- lightweight empirical rollout.

Not doing in v1:
- dynamic/self-selected roles;
- new permanent roles for each reviewer tab;
- new service/daemon;
- new task, PR, or review database;
- automatic wakeups;
- automatic merge authority;
- mandatory per-agent inbox files;
- mandatory labels that become task truth.

## Phase 0 — protocol

- [x] Define shared protocol in `work/coordination/GITHUB_ASYNC_WORK_PULL.md`.
- [x] Require operator-bound browser roles; unbound sessions cannot pull consequential work.
- [x] Define role pull loops and eligibility checks.
- [x] Define developer -> review -> integration GitHub handoff pattern.
- [x] Define SWITCHYARD as persistent controller of the entire live open-PR backlog.
- [x] Define PR dispositions: `INTEGRATE`, `REVIEW NEEDED`, `REPAIR NEEDED`, `BLOCKED`, `SUPERSEDED / CLOSE CANDIDATE`, `PLANNING / COORDINATION`.
- [x] Define dependency-first / bottom-up integration; PR age/number is never merge order authority.
- [x] Require every historical candidate to synchronize forward onto latest accepted `main` before merge.
- [x] Require exact `current main -> synchronized head` anti-regression proof and preservation of newer accepted behavior by default.
- [x] Require all remaining integration candidates to be rechecked after `main` changes.
- [x] Define SENTINEL as a review role that may have multiple explicitly operator-bound browser continuities.
- [x] Define lightweight `MAPS REVIEW CLAIM` / release / takeover behavior so concurrent SENTINEL sessions preferentially select different exact heads.
- [x] Preserve reviewer independence as continuity-specific eligibility; a reviewer label alone never proves independence.
- [x] Preserve existing authority and low-contention rules.
- [ ] Fresh independent review of protocol, including role binding, reviewer-pool claims, dependency-first anti-regression integration, and PR-backlog-control changes.
- [ ] SWITCHYARD integration after clean review.

## Phase 1 — browser trial

After the protocol is accepted:

- [ ] Start one tab explicitly bound as TOWER; it maintains priorities only.
- [ ] Start one tab explicitly bound as ANVIL; it discovers development work only.
- [ ] Start one tab explicitly bound as FOUNDRY; it discovers development/repair work only.
- [ ] Start at least two tabs explicitly bound to the SENTINEL role with unique continuity labels such as `SENTINEL-A` and `SENTINEL-B`.
- [ ] Each SENTINEL tab recovers the whole live review-ready queue, claims a different eligible exact head, re-reads for claim races, performs independent review, and posts an exact disposition without changing the branch.
- [ ] Verify a SENTINEL continuity refuses work it implemented, repaired, synchronized, or materially authored even if its label is different.
- [ ] Verify duplicate claims normally collapse to one primary reviewer while another reviewer pulls a different eligible item.
- [ ] Verify a stale/abandoned claim cannot permanently block progress.
- [ ] Start one tab explicitly bound as SWITCHYARD; it owns the complete open-PR backlog as a standing control loop.
- [ ] SWITCHYARD enumerates all open PRs and assigns each one a live disposition, next gate, and owner/blocker from GitHub evidence.
- [ ] Verify a real dependency chain integrates root-first and downstream heads are synchronized only after the prerequisite is accepted.
- [ ] Verify an old branch overlapping newer accepted main preserves newer accepted content unless explicit current authority says to supersede it.
- [ ] Verify SWITCHYARD moves to another independent eligible PR when the current one waits on review, repair, CI, dependency, or operator action.
- [ ] Verify SWITCHYARD does not bypass gates merely to shrink the PR count.
- [ ] Start one generic/unbound control tab; verify it reports `UNBOUND — role assignment required` rather than choosing a lane.
- [ ] Record only concrete discovery/control failures; do not add machinery based on speculation.

Checkpoint outcome:
- `CONTINUE` if bound browser agents reliably discover role-appropriate work, multiple SENTINEL continuities distribute review work safely, dependency chains integrate bottom-up without regressing accepted main, unbound sessions refuse self-selection, and the full PR backlog remains classified/actionable;
- `CHANGE` if routing remains ambiguous, role drift occurs, reviewers duplicate work excessively, claims deadlock, historical branches can regress newer accepted state, or PRs remain ownerless/stale despite active role sessions;
- `CUT SCOPE` if extra coordination features create more maintenance than they remove.

## Phase 2 — only if evidence justifies it

Potential derived conveniences, not authorities:

- optional GitHub labels such as role/review/integration hints;
- generated role/PR/review inbox views;
- standardized query/search conventions;
- automation that prepares synchronization/CI/review packets while leaving consequential decisions with the existing role.

Add any of these only after Phase 1 demonstrates a repeated failure that the feature directly fixes.

## Design guardrails

- Operator binds each browser session to exactly one role.
- Multiple browser sessions may share SENTINEL only by explicit operator binding; they do not become new permanent roles.
- Reviewer continuity labels are coordination identity, not evidence of independence or authority.
- Agents never choose or switch permanent role merely because another queue has work.
- One fact / one authority.
- Coordination state is derived routing evidence, not canonical task truth.
- Review claims are advisory duplicate-work avoidance, not canonical review/task state.
- The PR backlog view is derived from live GitHub, not maintained as a second mutable PR database.
- Integration order follows dependency structure, not PR chronology.
- Latest accepted `main` is the integration baseline; historical branch state cannot silently win over it.
- A work item is pulled only after live eligibility verification.
- Agents do not race mutable outputs.
- Independent reviewers do not patch reviewed work.
- A SENTINEL continuity cannot review work it implemented/repaired/synchronized/materially authored.
- TOWER priority never grants execution/review/merge authority.
- SWITCHYARD owns backlog control but not feature/review authority.
- SWITCHYARD integration gates remain intact.
- Idle agents do not manufacture work or change lanes.

## Operator usage after acceptance

First bind a normal role tab, for example:

`Your role is ANVIL. Continue under work/coordination/GITHUB_ASYNC_WORK_PULL.md.`

For parallel reviewer tabs:

`Your role is SENTINEL. Your reviewer continuity label is SENTINEL-A. Recover the live review queue, claim a distinct eligible exact-head review under work/coordination/GITHUB_ASYNC_WORK_PULL.md, perform the independent review, record the disposition, and continue to another eligible unclaimed review when appropriate.`

`Your role is SENTINEL. Your reviewer continuity label is SENTINEL-B. Recover the live review queue, claim a distinct eligible exact-head review under work/coordination/GITHUB_ASYNC_WORK_PULL.md, perform the independent review, record the disposition, and continue to another eligible unclaimed review when appropriate.`

For the PR-control tab:

`Your role is SWITCHYARD. Own the full open-PR backlog under work/coordination/GITHUB_ASYNC_WORK_PULL.md; integrate dependency-first, synchronize every candidate onto latest accepted main, reject unauthorized regressions, classify every open PR, and continuously advance eligible PR-control/integration work.`

After a tab is bound, later prompts can be:

`Continue. Recover live GitHub state and pull the highest-priority eligible work for your bound role.`

For SENTINEL pool tabs, `continue` resumes the standing review queue and preferentially claims an unclaimed eligible exact head.

For SWITCHYARD, `continue` resumes the full backlog-control loop, derives order from dependencies rather than age, and carries every historical candidate forward onto latest accepted main before merge.