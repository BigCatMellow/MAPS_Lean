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
- `SWITCHYARD` — integration / PR-control / merge safety.

Examples of valid binding:

- `Your role is ANVIL. Continue under the GitHub async work-pull protocol.`
- `You are SENTINEL for this browser session. Recover live state and continue.`

The operator may explicitly bind **more than one browser session to the same role** when that role has safely parallelizable work. This does not create new roles or duplicate authority. For parallel SENTINEL work, each session should also receive a unique operator-provided continuity label such as `SENTINEL-A`, `SENTINEL-B`, or `SENTINEL-C` so GitHub handoffs can distinguish independent browser continuities sharing the same review role.

An `UNBOUND` session may inspect public repository state to orient itself, but it must not claim consequential work, approve review, modify an owned feature branch, synchronize an integration candidate, or merge.

If a generic startup prompt omits the role, the session must report `UNBOUND — role assignment required`; it must **not infer or self-select** a role.

Role binding does not grant extra authority. A continuity label is coordination identity only. All task, ownership, reviewer-independence, review, and integration gates still apply.

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
9. continue with another independent eligible item when the role has a standing queue responsibility; otherwise stop at the role boundary.

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

For independent review, also verify that the specific browser continuity did not implement, repair, synchronize, or materially author the exact work it would review. A `SENTINEL-*` label does not manufacture independence.

If any load-bearing fact is unknown, inspect or block rather than guess.

## Integration order and anti-regression rule

**PR age, PR number, creation time, and recency do not determine integration order.** MAPS integrates **dependency-first / bottom-up**:

1. accepted prerequisites and root foundations first;
2. then direct dependents rebuilt or synchronized against those accepted prerequisites;
3. then later dependents, repeating until the stack is exhausted.

For unrelated eligible roots, TOWER priority and SWITCHYARD integration safety may choose order. Regardless of order, every candidate must integrate **forward onto the latest accepted `main`**.

An older branch is never allowed to make the repository travel backward merely because it was created first. Before merge, SWITCHYARD must:

- recover the latest accepted `main`;
- genuinely synchronize the reviewed feature layer onto that exact `main` using real Git ancestry;
- treat accepted `main` as the baseline that must be preserved;
- compare exact `current main -> synchronized head` rather than trusting the branch's historical base;
- verify that the synchronized delta contains only the task-authorized intended change plus explicit, reviewed conflict reconciliation;
- fail/return the candidate if it silently deletes, reverts, replaces, or reintroduces stale versions of newer accepted behavior outside its authorized change.

When a historical branch overlaps newer accepted work, **newer accepted `main` wins by default**. A task may intentionally supersede accepted behavior only when that replacement is explicitly within current task/operator authority and receives fresh exact-head review; an old branch may never overwrite newer accepted behavior implicitly.

After any merge changes `main`, every remaining integration candidate must be treated as potentially stale. Re-check ancestry, dependencies, exact delta, CI, and review freshness before the next merge.

Therefore the safe model is not `newest -> oldest` or `oldest -> newest` by date. It is:

```text
dependency root
      ↓ accept into current main
next dependent synchronized onto new main
      ↓ accept
next dependent synchronized onto newer main
      ↓
...
```

This rule prevents historical PRs from overwriting accepted newer work while still allowing old but valid feature layers to be carried forward safely.

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
- apply the dependency-first / anti-regression rule above;
- genuine synchronization using real ancestry;
- exact delta verification against current accepted main;
- fresh exact-head CI;
- eligible integrated-head independent review where required;
- merge only under existing authority and expected-head protection.

Suggested heading:

`MAPS INTEGRATION HANDOFF — <result>`

Accepted main then becomes the dependency-release fact for downstream work.

## Parallel SENTINEL reviewer pool

SENTINEL is an **independent-review role**, not a singleton browser session. When review throughput is the bottleneck, the operator may explicitly bind multiple independent browser continuities to the SENTINEL role.

Example:

```text
SENTINEL-A -> review PR X exact head
SENTINEL-B -> review PR Y exact head
SENTINEL-C -> review PR Z exact head
```

These are three browser continuities sharing one role. They are not three new permanent MAPS roles and do not gain different review authority.

### Review claim protocol

Before beginning a substantive review, a SENTINEL session should recover the live review queue and post a lightweight claim on the target PR:

`MAPS REVIEW CLAIM — SENTINEL-<label>`

The claim should include:

- reviewer continuity label;
- exact PR base/head being claimed;
- review layer, such as feature-head or integrated-head;
- statement that reviewer independence was checked;
- statement that the claim is coordination only, not a review disposition.

Then immediately re-read the PR before doing the full review.

If another SENTINEL continuity already claimed the **same exact base/head** for the same review layer, the later claimant should normally release/withdraw its duplicate claim and pull another eligible review. If simultaneous claims race, GitHub comment ordering is the tie-break for duplication avoidance unless the operator or task explicitly requires multiple independent reviews.

Suggested release heading:

`MAPS REVIEW CLAIM RELEASED — SENTINEL-<label>`

A claim:

- does **not** make work review-ready;
- does **not** approve or reject anything;
- does **not** grant merge authority;
- does **not** change canonical task state;
- becomes irrelevant when base/head moves or an exact-head review disposition is posted;
- must never deadlock the queue merely because a browser tab disappeared.

If an older claim appears abandoned, other eligible reviews should be taken first. If no other eligible review exists, another independent SENTINEL may take over after re-checking live state and leaving `MAPS REVIEW CLAIM TAKEOVER — SENTINEL-<label>` with the displaced claim, exact base/head, and reason. Duplicate review is preferable to an indefinitely blocked acceptance gate when independence is preserved.

### Reviewer-pool pull loop

Each SENTINEL continuity should:

1. recover all review-ready PRs, not only the last remembered PR;
2. remove items it is not independent or otherwise eligible to review;
3. prefer the highest-priority eligible exact head not already claimed by another active SENTINEL continuity;
4. post the claim and re-read for a race;
5. review without modifying the branch;
6. post the exact review disposition;
7. if another independent eligible review remains, continue the review queue rather than waiting on SWITCHYARD or a developer.

Multiple SENTINEL sessions may therefore review different PRs concurrently while preserving the same independent-review standard.

## Role pull loops

### TOWER

Pull: current repository/project planning work.

Do:
- recover live state;
- maintain a **derived** priority/dependency view;
- identify eligible vs blocked work;
- prioritize dependency roots before downstream dependents when acceptance of the root gates the stack;
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

Pull: the review-ready queue, distributed across explicitly operator-bound SENTINEL continuities using the review-claim protocol above.

Do:
- verify exact state and CI;
- verify continuity-specific reviewer independence;
- claim a distinct eligible exact head before substantive review;
- evidence-test the task/implementation;
- for integrated-head review, verify current-main synchronization did not regress newer accepted behavior;
- record exact disposition;
- return defects to owner and freshness/integration blockers to SWITCHYARD;
- continue to another independent eligible unclaimed review instead of waiting behind one blocked item.

Do not:
- patch work being independently reviewed;
- treat TOWER priority as proof of readiness;
- treat a claim as review authority or canonical state;
- duplicate another active SENTINEL claim when a different eligible review exists;
- switch to implementation or integration because those queues are non-empty.

### SWITCHYARD

Pull: the **entire live open-PR backlog** as a standing repository-control queue, with integration candidates advanced whenever eligible.

SWITCHYARD is the persistent PR-control lane. TOWER decides product/work priority; SWITCHYARD ensures no open PR becomes ownerless, stale, ambiguous, or able to regress accepted `main`.

For every open PR, recover live state and maintain one current disposition derived from GitHub evidence:

- `INTEGRATE` — reviewed/eligible; advance dependency-first synchronization, exact-delta, fresh CI, integrated review, and merge gates;
- `REVIEW NEEDED` — leave a durable exact-head handoff for SENTINEL or another eligible independent reviewer;
- `REPAIR NEEDED` — return the concrete defect to the owning development lane;
- `BLOCKED` — record the exact prerequisite and avoid branch churn;
- `SUPERSEDED / CLOSE CANDIDATE` — identify obsolete/duplicate work; close only when authority and evidence are clear, otherwise surface the decision;
- `PLANNING / COORDINATION` — move through the appropriate review/integration path without treating prose as feature authority.

Do:
- enumerate and periodically re-scan all open PRs;
- derive integration order from dependency structure and current authority, never PR age/number;
- ensure every open PR has a current disposition, next legitimate gate, and discoverable owner/blocker;
- work the highest-priority eligible SWITCHYARD action;
- when one PR is waiting on SENTINEL, ANVIL, FOUNDRY, TOWER, CI, or another prerequisite, leave the handoff and continue scanning for another independent eligible PR;
- re-scan after merges or material `main` changes because ancestry/readiness may have changed;
- synchronize legitimately handed-off integration branches onto the latest accepted `main`;
- preserve accepted `main` by default during conflicts and fail closed on unauthorized regression;
- verify exact ancestry/delta against current main and require fresh evidence;
- merge only when existing integration gates and authority are satisfied.

Do not:
- integrate newest-to-oldest or oldest-to-newest merely from PR chronology;
- let historical branch content silently overwrite/revert newer accepted behavior;
- reduce the PR count by bypassing dependency, review, CI, ownership, or exact-head gates;
- merge merely because work is high priority;
- take over feature development unless a specific integration defect is legitimately returned;
- self-approve work requiring independent review;
- create a second mutable PR database; the queue is derived from live GitHub;
- stop merely because the highest-priority PR is waiting while other independent PR-control work is eligible.

## Parallelism rule

Browser sessions do not need to take turns if their work is genuinely independent.

Safe example:

```text
SENTINEL-A  reviews integrated Context Builder
SENTINEL-B  reviews integrated communication lineage
SENTINEL-C  reviews another eligible exact head
FOUNDRY     repairs unrelated development work
SWITCHYARD  integrates one PR while triaging the rest of the backlog
TOWER       refreshes dependency/priority view
```

Unsafe parallelism includes:

- unbound sessions independently deciding to become SENTINEL or any other role;
- two agents editing the same branch/output;
- downstream implementation on unstable upstream ancestry;
- reviewer modifying the work they must independently approve;
- one SENTINEL continuity reviewing work it implemented/repaired/synchronized/materially authored;
- multiple SENTINEL continuities knowingly duplicating the same exact-head review while other eligible reviews are unclaimed;
- multiple agents independently synchronizing the same integration candidate.

## Operator workflow

Keep role-specific browser tabs. Bind each tab once and keep that role for the life of the session.

Suggested startup prompts:

- `Your role is TOWER. Continue under work/coordination/GITHUB_ASYNC_WORK_PULL.md.`
- `Your role is ANVIL. Continue under work/coordination/GITHUB_ASYNC_WORK_PULL.md.`
- `Your role is FOUNDRY. Continue under work/coordination/GITHUB_ASYNC_WORK_PULL.md.`
- `Your role is SENTINEL. Your reviewer continuity label is SENTINEL-A. Continue under work/coordination/GITHUB_ASYNC_WORK_PULL.md and claim a distinct eligible review before reviewing.`
- `Your role is SENTINEL. Your reviewer continuity label is SENTINEL-B. Continue under work/coordination/GITHUB_ASYNC_WORK_PULL.md and claim a distinct eligible review before reviewing.`
- `Your role is SWITCHYARD. Own the full open-PR backlog under work/coordination/GITHUB_ASYNC_WORK_PULL.md; integrate dependency-first, synchronize every candidate onto latest accepted main, reject regressions of accepted behavior, and continuously advance eligible PR-control/integration work.`

Additional SENTINEL sessions may be bound with additional unique labels when review demand justifies them. They remain the same SENTINEL role.

After binding, later prompts can usually be just:

> `Continue. Recover live GitHub state and pull the highest-priority eligible work for your bound role.`

For a SENTINEL pool tab, `continue` means recover the live review queue, claim a distinct eligible exact head, review it, record the disposition, and continue to another eligible unclaimed review when appropriate.

For SWITCHYARD, `continue` means resume the standing full-backlog control loop, derive integration order from dependencies rather than PR age, and never merge a historical branch without synchronizing it onto latest accepted `main` and proving no unauthorized regression.

The operator still has to start/wake browser sessions. The protocol removes the need to manually relay detailed handoffs between sessions.

## What v1 intentionally does NOT add

Do not add these merely because they are possible:

- dynamic self-selection of roles;
- new permanent reviewer roles for each SENTINEL browser tab;
- another task database or PR database;
- a daemon or scheduler;
- an agent-to-agent messaging service;
- mandatory GitHub labels as a second mutable truth;
- per-agent inbox files that must be kept synchronized with tasks/PRs;
- automatic merge authority.

Review claims are lightweight coordination comments only; they are deliberately not another task/review database.

If browser use later shows that discovery is still too costly, labels or generated inbox views may be added as **derived projections** from canonical/live state, never as authority.

## Success test

This protocol is working when the operator can open role-specific browser sessions, bind each one once, and later say roughly **continue**; each agent can independently discover:

- what it should do now within its bound role;
- what it must not touch;
- what it is waiting for;
- what exact evidence proves the wait is over;
- where to record its result so another role can discover it.

Additionally:

- dependency stacks are integrated root-first, never by PR age alone;
- every historical candidate is synchronized onto latest accepted `main` before merge;
- exact current-main deltas prove older branches do not silently revert newer accepted behavior;
- after each merge, remaining candidates are rechecked for staleness;
- multiple operator-bound SENTINEL continuities can concurrently claim and review different eligible exact heads without weakening reviewer independence;
- a same-head claim race converges on one primary reviewer unless multiple reviews are explicitly required;
- an abandoned claim cannot permanently block review progress;
- SWITCHYARD can recover the complete live open-PR backlog and ensure every open PR has a current disposition, next legitimate gate, and discoverable owner/blocker while continuing other eligible PR-control work when one item is waiting.

It fails if a new unbound browser session can plausibly decide for itself that it is SENTINEL, ANVIL, FOUNDRY, SWITCHYARD, or TOWER; if an older PR can silently overwrite or revert newer accepted behavior; if parallel SENTINEL tabs manufacture reviewer independence from labels alone; or if open PRs can remain indefinitely unclassified/ownerless while SWITCHYARD is active.