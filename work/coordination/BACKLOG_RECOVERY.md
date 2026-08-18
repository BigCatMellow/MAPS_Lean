# MAPS backlog recovery mode

Status: **ENDED by operator direction, 2026-08-17.** All six exit criteria below were materially true (0 open PRs, no dependency stacks, no status-snapshot loops, nothing outrunning integration capacity) and the operator confirmed exit. This file is preserved for its durable lessons (see "Durable state vs live state" and "Exit criteria"); the recovery-mode flow limits (1 merge-authoritative candidate at a time, etc.) are no longer an active operating constraint.

This file is a durable temporary operating contract. It defines how the existing roles should reduce the inherited backlog without weakening MAPS safety. It does **not** contain a live PR queue; recover that from GitHub.

## Goal

Return MAPS to a small, steady-state backlog where:

- status-snapshot refresh loops are gone;
- historical dependency stacks are accepted, rejected, superseded, or explicitly parked;
- every open product PR has a clear owner or bounded assignment, prerequisite, review position, and integration position;
- safe development and feature review continue in parallel;
- only one product candidate consumes merge-authoritative current-main synchronization/review capacity at a time;
- ordinary `main` movement no longer invalidates a large synchronized review queue;
- speculative work no longer outruns integration capacity.

A backlog around five open PRs is a useful health signal, **not** authority to close, discard, or merge work.

## Recovery priority

During recovery, prioritize existing work in this order unless stronger operator/task/dependency evidence says otherwise:

1. bounded repairs that unblock an existing dependency chain;
2. already-started feature/rebuild work whose prerequisite is accepted;
3. independent review of stable feature/repair heads;
4. the single active final integration candidate;
5. durable operating/protocol changes that directly remove systemic churn;
6. planning/design work already in flight when it has unique durable value.

Do not start new speculative capability work merely because a lane is idle.

## Durable state vs live state

Repository files hold stable rules, task contracts, architecture, and durable roadmap reasoning.

GitHub holds volatile facts: current heads, CI, review claims/dispositions, blockers, worker/owner evidence, queue position, and handoffs.

> **A fact expected to change merely because another PR merges is live coordination state and must not require its own merge to remain current.**

For a coordination/status PR, ask:

> Why must this content exist in future accepted `main` rather than remain preserved in GitHub history?

If there is no durable answer, SWITCHYARD should classify it `SUPERSEDED / CLOSE CANDIDATE` and close it only after confirming no unique durable information needs preservation.

Closing a superseded status PR does not accept its prose into canonical MAPS state.

## Work-in-progress limits

Recovery-mode flow guidance:

- active development roots: about **3 maximum** across the system;
- active independent feature/repair reviews: about **3 distinct useful targets**;
- active merge-authoritative product integration candidates: **exactly 1**;
- active durable process/coordination change: about **1** where practical.

These are flow-control heuristics, not lifecycle or task authority.

Idle capacity is preferable to creating unstable downstream work.

## Dependency depth rule

Release only the next dependent implementation after its prerequisite is actually accepted unless the task explicitly proves an independent safe output boundary.

Do not build an entire descendant stack because an upstream PR looks likely to pass.

A clean feature review, green CI, or synchronization is not prerequisite acceptance. Accepted `main` is the dependency-release fact.

## Owner rebuild vs final synchronization

Development owners may rebuild or repair against an **actually accepted dependency interface** when that interface materially affects feature correctness.

Once the feature/repair is coherent and appropriately verified/reviewed:

1. freeze the feature head;
2. do not chase unrelated `main` movement merely for freshness;
3. wait until SWITCHYARD places the candidate in the final integration slot.

Final latest-main synchronization is SWITCHYARD work.

## Final merge train

During backlog recovery there is **exactly one merge-authoritative product integration slot**. There is no multi-candidate exception.

The normal train is:

```text
stable feature / repair head
        ↓
independent FEATURE / REPAIR REVIEW — CLEAN IN-LAYER
        ↓
FROZEN while waiting
        ↓
SWITCHYARD integration slot
        ↓
synchronize onto latest accepted main
        ↓
exact current-main -> candidate delta + anti-regression proof
        ↓
fresh required exact-head CI
        ↓
independent INTEGRATED-HEAD REVIEW — CLEAN
        ↓
expected-head merge
        ↓
retarget any PR whose base was just orphaned by this merge
        ↓
full backlog rescan
        ↓
next dependency-correct candidate
```

Do not proactively synchronize the rest of the queue to current `main`.

Already-synchronized candidates may remain frozen. If `main` moves, they are refreshed only when they later enter the active slot.

A squash merge does not delete the merged branch (`delete-branch=false`), so GitHub does not auto-retarget any PR stacked on it. That PR keeps comparing against dead ancestry and reads CLEAN/MERGEABLE while its delta is meaningless. Retargeting orphaned bases to the branch the merge itself landed on (normally `main`) is not optional cleanup — it is part of "full backlog rescan," not a separate later step. `scripts/coordination_housekeeping.py` does this mechanically on a schedule as a floor between sessions, but SWITCHYARD's own rescan must check it directly rather than assume the automation already ran.

## Accepted-main anti-regression rule

Integration is dependency-first / bottom-up, never newest-first or oldest-first by PR age.

Accepted `main` is the forward baseline. Historical branch content may not silently delete, revert, or replace newer accepted behavior.

Before merge SWITCHYARD must prove the exact `current main -> synchronized head` delta is the authorized change plus any explicit reviewed reconciliation. If accepted behavior and historical content conflict, accepted `main` wins by default unless a current authorized task explicitly intends to supersede it.

## Review layers

### FEATURE / REPAIR REVIEW — CLEAN IN-LAYER

Binds an exact stable feature/repair head and proves the bounded implementation survived independent review.

It is **not** current-main compatibility, dependency acceptance, integration clearance, or merge authority.

### INTEGRATED-HEAD REVIEW — CLEAN

Binds the exact accepted base + exact synchronized head + exact delta + fresh required exact-head verification.

It is the final independent review evidence required by the current accepted task/policy rules and returns the candidate to SWITCHYARD. It does not itself merge.

### Evidence carry-forward

A prior clean feature review remains useful evidence after ancestry-only synchronization, but never silently becomes merge approval.

The integrated review may be narrower when it can prove unchanged feature semantics, but a fresh exact integrated-head disposition remains required unless a stronger accepted task/policy explicitly says otherwise.

A narrower integrated revalidation is permitted only when all of these are VERIFIED:

1. prior clean feature/repair review is identified by exact head;
2. reviewed changed-file blobs/authorized patch are byte-identical;
3. no conflict reconciliation or unreviewed feature modification occurred;
4. intervening `main` changes no overlapping path, declared dependency, schema/interface, authority boundary, or other load-bearing assumption;
5. exact `current-main -> candidate` delta remains task-authorized;
6. fresh required exact-head CI passes;
7. the independent reviewer verifies equivalence and anti-regression preservation;
8. no load-bearing fact is `UNKNOWN`.

If any condition fails or is unknown, perform normal full integrated-head review.

## SENTINEL claims and independence

A review claim is keyed to:

`PR + exact base + exact head + review layer`

It is an advisory duplicate-work lease only. It does not choose priority, reserve the integration slot, survive subject movement, create review authority, or block takeover indefinitely.

`SENTINEL-A/B/C` labels are coordination identities only.

Reviewer independence is continuity-specific: the reviewer must not have materially implemented, repaired, synchronized, merged, or authored the work under review. Prior read-only review of an earlier layer does not by itself destroy independence for a later integrated-head review unless a task/operator rule requires distinct reviewers.

## Bounded orphaned-development assignment

The operator authorizes the following recovery-mode mechanism to prevent ownerless bounded repairs from deadlocking:

1. recover current task/PR/branch ownership and recent owner activity;
2. if an active incumbent owner exists, do not take the branch;
3. if an existing development/repair item has no active owner continuity **and the required work is already task-authorized and bounded**, TOWER may assign that bounded step to ANVIL or FOUNDRY;
4. the assignment must be recorded on the relevant PR/task thread as `TOWER ROUTING — <lane> BOUNDED ASSIGNMENT` and identify:
   - target PR/branch;
   - exact returned defect or bounded implementation step;
   - dependency state;
   - allowed task/path boundary where material;
   - explicit statement that no broader redesign or authority transfer is granted;
5. the receiving lane owns only that bounded development/repair step;
6. review authority remains SENTINEL and integration/merge authority remains SWITCHYARD.

This mechanism must not be used to seize an actively owned branch, broaden an unshaped task, or infer permission when the task boundary itself is unknown.

## Verification proportionality

Do not weaken required verification.

- runtime/schema/security-sensitive work receives its normal required tests/CI/review;
- durable protocol/authority changes receive serious independent review;
- transient status artifacts should not consume production-runtime verification simply to remain current and should normally leave the merge pipeline when they have no durable value.

Existing task-specific verification requirements remain binding until explicitly amended through the proper authority.

## Role behavior during recovery

### TOWER

Route existing eligible work, resolve dependency order, make bounded orphan assignments when allowed above, and keep durable roadmap reasoning aligned with actual accepted conditions. Do not maintain another live queue document.

### ANVIL / FOUNDRY

Work only on existing assigned/owned implementation, returned repair, accepted-dependency rebuild, or explicit bounded TOWER assignment. Freeze at the review/integration boundary, and clear draft status before or with the handoff post — a frozen draft cannot be merged and stalls the backlog exactly like an unowned PR.

### SENTINEL

Keep one eligible reviewer available for the active integration slot while other independent continuities review distinct stable feature/repair heads. Reviewers never patch the reviewed work.

### SWITCHYARD

Own the full open-PR backlog as a control queue, but actively advance exactly one product integration candidate through the final train. Close genuinely superseded status artifacts only after the durable-value check. Treat a stuck-draft PR with posted handoff evidence and green CI, and a PR whose base was orphaned by an upstream squash merge, as backlog-control work in their own right — both silently stall a PR that otherwise reads as ready, independent of the one-slot merge train.

## Exit criteria

Recovery mode ends when the operator ends it or the following condition is materially true:

- historical dependency stacks are resolved or explicitly parked;
- status-snapshot refresh loops are gone;
- one ordinary merge no longer invalidates a queue of merge-authoritative reviews;
- every open product PR has a clear owner/bounded assignment, prerequisite, review position, and integration position;
- speculative work is no longer outrunning integration capacity;
- the backlog is a small steady-state queue.

On exit, preserve the durable lessons that reduced churn; do not revive status-snapshot maintenance.
