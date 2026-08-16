# Parallel development handoff — 2026-08-16

Status: **HANDOFF / ACTIVE DEVELOPMENT**

This note records the current state of the parallel-development lane for a fresh agent/window. It is descriptive continuity evidence only. It does not grant task, policy, review, merge, promotion, provider, or external-action authority.

## Start here

At note creation, accepted `main` was:

```text
37edf4581d0db5f4a9ef7c35e1bd7d865c2a600d
```

The current-main commit merged PR #29 (local environment fingerprint compatibility). **Do not trust this SHA as current when resuming.** Re-fetch `main`, PR heads/bases, CI, reviews, and branch ownership before changing anything.

Read root `AGENTS.md` first. Preserve its core invariants, especially:

- smallest coherent change;
- one fact / one authority;
- capability is not authority;
- preserve `UNKNOWN` instead of guessing;
- source evidence outranks summaries;
- one owner + independent reviewer;
- task/policy/operator authority wins;
- no hidden authority through derived read models;
- avoid speculative architecture while interfaces are moving.

## Completed in this lane

### PR #56 — acquisition-path evidence validation — MERGED

Final synchronized feature head:

```text
5837192f9a1fab0432d003662f40017abd614f22
```

Reviewed base:

```text
main@2cfb4bb8eef5526c074942421e7567f6a7c52159
```

Runtime CI:

```text
#314 / 31927614005 — PASS
```

Final independent exact-head review:

```text
review 4945430422
TECHNICALLY CLEAN / INTEGRATION-READY
```

PR #56 merged at:

```text
58a9aec6fb61b2d92f996a2eb9b8eaf4a693571d
```

The repaired invariant is important and must not regress:

```text
operator-visible + allowed NOT_APPLICABLE
+ no separate withdrawal/non-visibility proof

release.acquisition_paths_verified = PASS   # N/A may satisfy coverage
release.no_stale_visible_artifact = UNKNOWN # N/A decision alone proves no removal
```

Do not infer visible-surface removal from an N/A decision ref, manifest permission, labels, prose, or lack of observation.

Other retained #56 properties:

- exact immutable-ref comparison;
- stale-but-usable stays content/stale FAIL while usability may PASS;
- missing/unreachable evidence preserves UNKNOWN where appropriate;
- report identity is normalized and label/order-independent;
- validator performs no acquisition/network/install/publish action;
- validator grants no task/review/policy/publication authority and does not prove real-world provenance.

Unless a regression appears, **#56 is complete; do not reopen it as active feature work.**

## Open work owned by this parallel-development lane

### PR #59 — structured explainable-waits projection

Last observed state:

```text
open draft
head 127dd5d4fe24ba589e7b9f87cce883af0806b847
Runtime CI #301 / 31926888094 — PASS
```

Changed paths:

- `runtime/wait_projection.py`
- `tests/test_wait_projection.py`
- `work/tasks/explainable-waits-core-wave3.md`
- `work/notes/2026-08-15-explainable-waits-core.md`

Current semantics:

- exact dependency wait;
- review-unclaimed / review-in-progress wait;
- operator-approval wait using existing policy logic;
- generic `BLOCKED` without typed causal evidence remains `UNKNOWN`;
- `NO_VERIFIED_WAIT` never means runnable;
- read-only projection only;
- no communication/helper/recovery wait inference.

Important: #59 was created from an older `main`. Re-fetch current review state and compare it against live `main` before synchronizing or modifying it. Do not self-review it.

### PR #60 — canonical outcome -> lesson CANDIDATE builder

Last observed state:

```text
open draft
head cfd758aace44970e7400c005c337be040d367918
base agent/operational-learning-projection-wave3
Runtime CI #307 / 31927126075 — PASS
```

Core behavior:

- exact canonical outcome/task/revision/run evidence;
- source task must be `DONE`;
- candidate creation cannot predate source outcome;
- superseded outcomes are rejected;
- outcome `notes` / `source` prose never become lesson instructions;
- semantic candidate IDs use full SHA-256;
- output is always `CANDIDATE`;
- no lesson persistence, promotion, startup injection, or automatic activation;
- PR #43 projection withholds candidates as `CANDIDATE_NOT_PROMOTED`.

Dependency: PR #43 (`agent/operational-learning-projection-wave3`). Re-fetch #43 before changing #60. Do not invent lesson-promotion authority to move this stack forward.

### PR #53 — Context Builder Stage-2 retrieval evaluation

Last observed state:

```text
open draft
head 16fa7931b576b3aa9743049cd4cf0ca5e41dd726
base agent/context-evidence-scorer-wave3
Runtime CI #284 / 31926153229 — PASS
```

Evaluation-only controls:

1. explicit-only baseline;
2. exact same-path drift supplementation;
3. lexical overlap negative control.

Safety gates include:

- perfect hard-negative abstention;
- zero forbidden temporal-source cases;
- complete drift-pair recall;
- vocabulary-shift recall;
- perfect evidence-source recall;
- perfect evidence-source precision;
- explicit-prefix preservation.

The lexical method is intentionally never a promotion candidate. Do not turn this PR into production semantic/vector retrieval. Re-fetch #39/#41 state before synchronizing.

### PR #51 — A4c exact task/run <-> hcom event correlation design

Planning-only head last observed:

```text
e68dc4cd19a362f35de71cd10f3038e64e377b82
```

Critical finding:

- upstream hcom creates an exact provider event ID inside `send_message()`;
- the current CLI/MAPS send boundary does not return that ID;
- therefore MAPS cannot prove which exact provider event a send created.

Do **not** correlate using session/name, sender/recipient coincidence, timestamp proximity, latest-event lookup, thread/intent, or message text/hash.

Smallest prerequisite remains a provider-issued structured send receipt containing the exact event ID (conceptually `{"event_id":123,"delivered_to":[...]}`). If the event is created but the receipt/root link is lost, attribution remains `UNKNOWN`; there is no heuristic repair.

### PR #52 — A4d explainable-waits design

Planning-only head last observed:

```text
9b8f25fce9d72f1f330fd8e4add15a0145779e91
```

Core rule:

```text
structured prerequisite
+ proof it gates progress
+ proof it remains unresolved
= verified wait
```

A future communication wait requires both exact A4c event correlation **and** an explicit response-required/progress-blocking contract. `request + no reply in bounded input` is not waiting.

PR #59 implements only the already-supported structured dependency/review/approval tranche; communication waits remain deferred.

## Active work owned by other agents — do not edit

At handoff, these were active parallel lanes:

- **#48** — A1 adapter-qualified run/session lineage;
- **#49** — A2 helper/recovery lineage;
- **#50** — A3 exact submission-attempt/run lineage;
- **#57** — Operator Intent Compiler / Request Compiler playbook + roadmap.

The user explicitly has other agents working these areas. Do not modify their branches, silently retarget them, duplicate their implementations, or review/approve work you authored. Re-check live ownership because assignments may change after this note.

Older communication prerequisites #44/#45 also remain open drafts. Treat their interfaces as prospective until independently reviewed/accepted; do not casually synchronize them into another agent's moving lineage stack.

## Recommended continuation order

On a fresh window:

1. Read root `AGENTS.md`.
2. Read this note.
3. Fetch live `main` and current PR states before trusting any hash here.
4. Check comments/reviews on **#59, #60, and #53** for concrete independent-review findings.
5. Address a concrete blocker first, if one exists, without widening scope.
6. If no blocker exists, choose the most integration-ready lane whose dependency/base is stable:
   - #59 if its current-main interface is still compatible;
   - #60 only after #43 is stable enough to bind against;
   - #53 only after #39/#41 truth/scorer interfaces are stable enough to bind against.
7. When synchronizing an old branch, genuinely incorporate current accepted upstream state; do not merely retarget the PR base. Verify final base -> head changed-file scope and rerun full Runtime CI on the exact synchronized head.
8. Obtain fresh independent exact-head review before integration. CI green is not review approval.
9. Do not merge consequential work unless the operator/canonical task authority permits it and the exact head has required review clearance.
10. Leave a new handoff/checkpoint if another context switch happens.

## Stop / do-not-build list

Do not add these merely to keep busy:

- automatic lesson promotion or a self-authorizing lesson database;
- production semantic/vector retrieval before the frozen evaluator supports a reviewed candidate decision;
- mutable task-level `current_session_id` or equivalent duplicated lineage truth;
- generic mutable lineage graph / blackboard;
- hcom body mirroring;
- timestamp/name/prose-based communication joins;
- `no reply observed = waiting` semantics;
- provider/session liveness as task authority or causal wait proof;
- broad automatic self-modification;
- a new supervisor/watcher/sentinel architecture;
- acquisition/network/install/publishing machinery unless a separately authorized real benchmark demonstrates the pure evidence split is insufficient.

## Short state map

```text
MERGED / accepted path
  #40 benchmark protocol
  #42 benchmark evidence repair
  #56 acquisition evidence repair

parallel-development open work
  #59 structured waits
  #60 outcome -> lesson candidate
  #53 Context Builder Stage 2 evaluation
  #51 A4c communication join design
  #52 A4d wait design

other-agent occupied implementation lanes
  #48 -> #49 -> #50 execution lineage
  #57 operator request compilation

A4 communication runtime
  #44 full-fidelity read
    -> #45 exact provider relationships
    -> #51 exact MAPS root-correlation design
    -> BLOCKED on provider-issued exact send event receipt
```

## Handoff principle

The next agent should continue useful work, but **not by creating overlap**. Prefer concrete review findings, stable integration boundaries, and exact evidence over starting another subsystem because one branch is temporarily waiting.