# GitHub-native asynchronous work-pull protocol

Status: proposed shared coordination protocol for browser-only multi-agent operation.

## Core model

> **Operator binds roles. TOWER prioritizes. Development lanes build/repair. SENTINEL reviews. SWITCHYARD integrates. GitHub carries live coordination.**

Separate browser sessions cannot reliably message or wake one another directly. GitHub is therefore the durable shared surface for current work evidence.

This protocol is coordination only. It does not create a second task database, review authority, branch authority, or merge authority.

## Start here

Every role-bound browser session reads:

1. root `AGENTS.md`;
2. `work/coordination/README.md`;
3. this protocol;
4. `work/coordination/BACKLOG_RECOVERY.md` while recovery mode is active;
5. its own role contract under `work/coordination/agents/`;
6. current live task/PR/branch/CI/review evidence.

Volatile status is recovered from GitHub, not from role files.

## Mandatory role binding

A new browser session is `UNBOUND` unless its role is already explicit in that conversation.

The operator binds each session to one permanent role:

- `TOWER` — planning / dependency reasoning / dispatch;
- `ANVIL` — development / runtime implementation;
- `FOUNDRY` — development / runtime implementation and repair;
- `SENTINEL` — independent review;
- `SWITCHYARD` — integration / PR-control / merge safety.

The operator may bind multiple browser continuities to SENTINEL, such as `SENTINEL-A`, `SENTINEL-B`, and `SENTINEL-C`. These labels are coordination identities only, not new roles or evidence of independence.

An unbound session may orient itself but must not claim consequential work, modify an owned branch, approve review, synchronize an integration candidate, or merge. It reports:

`UNBOUND — role assignment required`

A session never self-selects or switches permanent role merely because another queue has work.

## Sources of truth

Use authority in this order:

1. operator / policy authority;
2. canonical MAPS task state and task contract;
3. accepted `main` and live GitHub PR/branch/CI/review evidence;
4. TOWER routing/roadmap/coordination prose as derived guidance.

If a coordination note conflicts with stronger live/canonical state, the note loses.

Preserve `UNKNOWN` rather than inventing a missing ownership, dependency, readiness, reviewer-independence, or authority fact.

## Durable state vs live state

Repository coordination files contain stable rules, role boundaries, architecture, task contracts, and durable planning reasoning.

Live GitHub contains current heads, owners/workers, CI, reviewer claims/dispositions, blockers, queue position, and handoffs.

> **A fact expected to change merely because another PR merges is normally live coordination state and must not require its own merge to remain current.**

Do not create or refresh status-snapshot PRs merely to mirror GitHub activity.

## Browser pull loop

When the operator says `continue`, a role-bound session should:

1. recover accepted `main`;
2. read the durable coordination files above;
3. inspect live GitHub evidence relevant to its role;
4. identify the highest-priority eligible work for that role;
5. verify ownership/assignment, dependency readiness, authority, exact subject, and stop conditions;
6. execute until completion or a concrete blocker;
7. record the result on GitHub;
8. continue another independent eligible item only when the role has a standing queue responsibility.

If no eligible work exists, remain idle. Do not invent work or change roles.

## TOWER routing

TOWER maintains dependency/priority reasoning but does not maintain a second live queue file.

TOWER uses relevant PR/task threads for bounded routing decisions and dependency holds.

During operator-declared backlog recovery, TOWER may make the bounded orphaned-development assignment defined in `BACKLOG_RECOVERY.md`: an existing already-task-authorized ownerless development/repair step may be assigned to ANVIL or FOUNDRY after verifying no active incumbent owner and recording the exact bounded handoff.

That mechanism does not transfer review, integration, merge, policy, or broader task authority.

## Development flow

ANVIL/FOUNDRY pull only legitimately owned/assigned work whose dependencies and task boundary permit action.

A development owner may rebuild against an actually accepted dependency interface when correctness requires it.

When a stable feature/repair head is ready:

- run task-appropriate verification;
- post `MAPS HANDOFF — READY FOR INDEPENDENT REVIEW` with exact subject/evidence;
- freeze the feature head after the required feature/repair review boundary;
- do not chase unrelated `main` movement merely for freshness.

Final latest-main synchronization belongs to SWITCHYARD.

## Review layers

### Feature / repair review

`MAPS REVIEW DISPOSITION — CLEAN IN-LAYER / FEATURE-HEAD ONLY`

This proves the exact bounded feature/repair head survived independent review.

It does not mean current-main compatible, dependency-accepted, integration-ready, or merge-authorized.

### Integrated-head review

`MAPS REVIEW DISPOSITION — CLEAN INTEGRATED-HEAD`

This binds the exact accepted base + synchronized head + exact delta + fresh required exact-head verification.

It returns the candidate to SWITCHYARD; it does not itself merge.

A prior clean feature review may be reused as evidence. A fresh exact integrated-head disposition remains required under current accepted rules. When the strict equivalence conditions in `BACKLOG_RECOVERY.md` are all verified, that integrated review may focus on ancestry-only equivalence and anti-regression instead of re-litigating unchanged feature semantics.

## Parallel SENTINEL pool

SENTINEL is one logical review role that may have multiple explicitly operator-bound browser continuities.

Reviewer independence is continuity-specific. A reviewer must not have materially implemented, repaired, synchronized, merged, or authored the work being independently reviewed. A label never proves independence.

Prior read-only review of an earlier layer does not by itself destroy later independence unless a stronger task/operator rule requires distinct reviewers.

### Review claim

Before substantive review post:

`MAPS REVIEW CLAIM — SENTINEL-<label>`

The claim subject is:

`PR + exact base + exact head + review layer`

Then re-read GitHub for races or subject movement.

A claim is an advisory duplicate-work lease only. It does not choose priority, reserve an integration slot, approve/reject work, alter task state, survive base/head/layer movement, or block takeover indefinitely.

Parallel SENTINEL continuities should prefer distinct useful review subjects. During backlog recovery, one eligible reviewer should remain available for the active final integration candidate while other reviewers may process stable feature/repair heads.

Reviewers never patch the work they must independently review.

## SWITCHYARD backlog control

SWITCHYARD continuously derives the full live open-PR queue from GitHub and classifies each PR as one of:

- `INTEGRATE`;
- `REVIEW NEEDED`;
- `REPAIR NEEDED`;
- `BLOCKED`;
- `SUPERSEDED / CLOSE CANDIDATE`;
- `PLANNING / COORDINATION`.

Every open PR should have a discoverable next legitimate gate and owner/blocker from live evidence.

The backlog view is not stored as a second mutable repository database.

When one PR waits on another role/CI/dependency, SWITCHYARD continues other eligible PR-control work rather than idling.

## Dependency-first integration

PR age, PR number, creation time, and recency do not determine merge order.

MAPS integrates dependency-first / bottom-up:

```text
accepted root
   ↓
next direct dependent
   ↓
next dependent
   ↓
...
```

A downstream layer is not released by green CI or a clean feature review. Its prerequisite must actually be accepted.

## Accepted-main anti-regression rule

Every final integration candidate moves **forward onto latest accepted `main`**.

Accepted `main` is the baseline that must be preserved. Historical branch content has no authority to silently delete, revert, replace, or reintroduce stale versions of newer accepted behavior.

Before merge SWITCHYARD must:

1. recover latest accepted `main`;
2. genuinely synchronize the active candidate using real ancestry;
3. prove exact `current main -> synchronized head` delta;
4. verify only task-authorized changes plus explicit reviewed reconciliation remain;
5. preserve newer accepted behavior by default;
6. require fresh task-appropriate exact-head verification;
7. require the eligible integrated-head review required by current rules;
8. expected-head merge only if all gates remain valid.

If historical content conflicts with accepted behavior, accepted `main` wins by default unless an explicitly authorized current task intentionally supersedes it and receives appropriate fresh review.

If reconciliation requires an unresolved authority choice, stop that candidate rather than guess.

## Backlog recovery mode

When `work/coordination/BACKLOG_RECOVERY.md` is active, its stricter flow controls apply.

Most importantly:

- no new speculative capability work;
- cap active dependency depth;
- preserve safe parallel development and feature review;
- freeze stable non-slot heads;
- exactly **one merge-authoritative product integration candidate at a time**;
- synchronize that candidate just in time;
- after each merge, rescan the full backlog before selecting the next candidate;
- evaluate status/checkpoint PRs by unique durable future-main value rather than freshness.

Recovery-mode WIP limits are flow guidance, not task authority.

## Superseded coordination/status PRs

For a status/checkpoint PR ask:

> Why must this content exist in future accepted `main` rather than remain preserved in GitHub history?

If no unique durable value remains, SWITCHYARD may classify it `SUPERSEDED / CLOSE CANDIDATE` and close under existing authority after checking no durable information needs preservation.

Closing it is not acceptance of its prose.

## Standard handoffs

### Development -> review

`MAPS HANDOFF — READY FOR INDEPENDENT REVIEW`

Include exact base/head, intended delta, verification/CI, dependencies, relevant limitations/UNKNOWNs, and freeze statement.

### Review -> repair/integration

`MAPS REVIEW DISPOSITION — <result>`

Bind the exact review layer and subject.

### Integration

`MAPS INTEGRATION HANDOFF — <result>`

Include accepted base, synchronized head, exact delta/anti-regression proof, fresh verification, review result, and next gate.

### TOWER routing

`TOWER ROUTING — <bounded assignment / dependency decision>`

Routing is derived coordination evidence. It does not silently grant broader task/review/merge authority.

## Unsafe behavior

Do not:

- self-select or switch roles;
- race another agent on the same mutable branch/output;
- build deep downstream work on unaccepted ancestry;
- review work a continuity materially authored/modified;
- treat feature review as merge authority;
- treat review claims as locks/priority/merge authority;
- pre-synchronize several merge-authoritative candidates during backlog recovery;
- integrate by PR chronology;
- let historical content regress accepted `main`;
- bypass dependency, ownership, CI, review, or operator gates to reduce the PR count;
- create a second status/PR/review database in Markdown.

## Operator usage

A normal role tab can be started with:

`Your role is ANVIL. Read work/coordination/README.md, your role file, the async protocol, and active backlog-recovery rules. Recover live GitHub state and continue.`

A reviewer tab:

`Your role is SENTINEL. Your reviewer continuity label is SENTINEL-A. Read work/coordination/README.md, SENTINEL.md, the async protocol, and active backlog-recovery rules. Recover live GitHub state and pull an eligible review.`

SWITCHYARD:

`Your role is SWITCHYARD. Read work/coordination/README.md, SWITCHYARD.md, the async protocol, and active backlog-recovery rules. Recover the full live PR backlog and continue the one-slot dependency-first merge train.`

After the session is bound, later instructions can simply be:

`Continue. Recover live GitHub state and pull the highest-priority eligible work for your bound role.`
