# Open PR integration sequence

Status: `INTEGRATION / REVIEW GUIDANCE — NOT ACTIVE AUTHORITY`

Date: `2026-08-15`

Purpose: define the safest practical way to independently review and integrate the current MAPS Lean draft PR stacks without allowing stacked-base changes to invalidate review or CI evidence.

This note does not approve any PR and does not replace `AGENTS.md`, canonical review requirements, or the exact current GitHub state. Re-check every head/base/check before acting.

## Current stack topology

At this checkpoint the open implementation stacks are:

```text
HARNESS / SECURITY
#20 ecfc27269e096db5d83bfa376878c33089a4e106  base main
 ↓
#21 5d31410fd80e9dd4f751621cd9dd65d10bfe0bde  base #20
 ↓
#22 9020476c9e98837ef8bfa121f45d6dbf6a17e4d7  base #21
 ↓
#23 9456d324e8cc72c620125759111a5076b6f91efb  base #22
 ↓
#24 3110457c78a1d30b4b6692d78108617d88c4d0ba  base #23

SKILLS
#25 f2985f3dd510ee1679f19df45120afc316c15b6d  base main
 ↓
#26 564498285be1519b10183247eab5f73a42f5cc6c  base #25
 ↓
#27 f6d6685b4396829cc71e67144a3ca0951f1d8b52  base #26
 ↓
#31 ace6131845c729937dee1c6fcfedc8914c4024cb  base #27

ENVIRONMENT
#28 6128ef94334b1868677430d65724628d19bb8b70  base main
 ↓
#29 93e63fb49fb5bbcebb3002ff17cada6fc02fdbc3  base #28
 ↓
#30 b7599bc71e7e0f55118ad4708a2a21ac0c6ae1b0  base #29

REVIEW FRESHNESS
#32 489a2524b513d6d9ab5eb186874cbc04e6e4ba4a  base main

RUN RECORD / EVALUATION
#33 3d618a4d74d8be4ba42e119cc5d659e204ccd9d5  base main
 ↓
#34 aca786cf1af71a38c453f9aa2d69998b492ea4bc  base #33
 ↓
#35 5fac110b4af70eaec92bb3ec91eeb5c52ee7a149  base #34

ROADMAP RECONCILIATION
#36 current head on agent/legacy-recovery-roadmap-reconciliation  base main
```

These SHA values are checkpoints only. If any head moves, use the new exact head.

## Review fact at this checkpoint

The existing review submissions on the implementation PRs are continuity-linked `COMMENTED` reviews from the primary implementation/review continuity. They are useful findings/remediation history but **do not satisfy independent review**.

PR #36 has no submitted independent review at this checkpoint.

## Safe integration rule

A stacked PR should not receive its final completion approval solely against an upstream feature branch that will later disappear from its diff.

Use this sequence for each stack:

```text
1. independently review the current root PR against its exact current base/head
2. resolve findings
3. verify full Runtime CI on the exact approved head
4. merge root into main
5. retarget the next PR from the now-merged feature branch to main
6. update/synchronize that branch with current main using normal Git integration if main advanced
7. rerun full Runtime CI against the resulting current base/head
8. independently review the exact resulting delta
9. repeat
```

Do not fabricate a merge commit by merely giving a commit two parents while retaining an unmerged tree. If synchronization is needed, perform a real Git merge/rebase/update and resolve the resulting tree normally.

Changing only a PR base may not produce fresh CI evidence depending on workflow trigger configuration. If the base or integration context changed materially, ensure the branch is genuinely synchronized so a fresh check runs before final approval/merge.

## Recommended priority

The shortest path to the next roadmap capability is:

```text
FIRST: harness/security stack
#20 → #21 → #22 → #23 → #24

THEN: portable execution evidence root
#33

THEN, when useful for evaluation work
#34 → #35
```

Why: explicit execution/session/helper/recovery lineage depends most directly on stable harness semantics and benefits from the portable Run Record surface. It does not require completing every independent Wave 2 track first.

The other independent tracks can follow without blocking that critical path:

```text
#32 review-subject freshness
#28 → #29 → #30 environment evidence
#25 → #26 → #27 → #31 Skills
#36 roadmap reconciliation
```

If a fresh independent reviewer is available for several roots, early non-final review of independent roots can happen in parallel to surface defects. Final completion approval should still bind to the exact base/head/integration state that will be merged.

## Cross-stack file overlap

The current **root** PRs are path-disjoint:

- #20 — `runtime/harness/*`
- #25 — `runtime/skills/*`
- #28 — `runtime/environment/*`
- #32 — review/state binding files
- #33 — `runtime/run_record.py` + CLI
- #36 — planning/docs only

That makes early root review reasonably parallelizable.

One known downstream integration hotspot exists:

```text
#30 environment run evidence
  touches runtime/state/schema.sql
          runtime/state/store.py

#32 review-subject freshness
  touches runtime/state/schema.sql
          runtime/state/store.py
```

Therefore #30 and #32 must not be treated as permanently independent merely because their roots were independent. Whichever lands second must be synchronized with current `main`, resolve the shared state-layer tree normally, run fresh Runtime CI, and receive final review on that integrated delta.

No other current cross-stack file overlap was found in the changed-file inventory for #20-#36 at this checkpoint. Re-check after any head moves.

## Per-stack reviewer focus

### #20 → #24 Harness/security

Check especially:

- provider-neutral types do not become authority;
- Hook context remains recursively immutable across hooks;
- Hooks only narrow/block/annotate and never grant authority;
- HarnessService correlation is explicit;
- canonical guard checks current task/run/worker/session evidence rather than liveness inference;
- stale resume/lease/identity adversarial cases fail closed;
- no duplicate session/task authority store is introduced.

### #25 → #27 → #31 Skills

Check especially:

- discovery is separate from activation;
- provenance/hash drift remains exact;
- catalog trust remains descriptive, not approval;
- frozen Skill-selection evaluation includes paraphrase/hard-negative/no-Skill/ambiguity cases;
- full frontmatter/custom metadata is covered by the security gate;
- `CLEAR` never means approved/trusted;
- scripts/resources are not executed by the static gate.

### #28 → #30 Environment

Check especially:

- EnvironmentSpec remains descriptive;
- secret requirements are capability names, not values;
- dependency paths cannot read/hash outside repo through symlinks;
- fingerprint/compatibility preserve UNKNOWN rather than guessing;
- compatibility is evidence, not recovery authority;
- run environment evidence is append-only and does not mutate run/task truth.

Before final #30 review, account explicitly for #32 if #32 has already landed because both modify the state schema/store composition.

### #32 Review freshness

Check especially:

- exact immutable subject binding;
- freshness validation occurs inside the existing review transaction;
- consequential approval rejects changed revision/submission/run evidence;
- re-derived evidence must match exact immutable refs;
- the feature does not create a second review lifecycle.

Before final #32 review, account explicitly for #30 if #30 has already landed because both modify the state schema/store composition.

### #33 → #35 Run Record/evaluation

Check especially:

- Run Record is a read model, not a new authority store;
- missing external coverage remains `MISSING`/`UNKNOWN`;
- replay stays explicitly incomplete;
- frozen cases preserve exact sanitized evidence and complete incident taxonomy;
- comparative evaluation consumes frozen cases/results deterministically;
- better scores cannot self-authorize production promotion.

### #36 Roadmap reconciliation

Check especially:

- it remains subordinate planning, not active authority;
- `MERGED`, `IN OPEN PR`, `NEXT`, `TRIGGERED/LATER`, `DO NOT REVIVE`, and `AUDIT REMAINS` are supported by evidence;
- it does not claim legacy archaeology is exhaustive;
- it does not revive the failed lexical claim-card retriever or duplicate control-plane architecture;
- next ordering matches actual accepted dependencies after the implementation stacks settle.

## Stop conditions

Do not merge a PR when any of these are true:

- current head differs from the reviewed head;
- current base/diff materially differs from the reviewed integration state;
- required Runtime CI is missing or failing for that integration state;
- unresolved blocking review finding exists;
- independent-review requirement is not actually met;
- a change would silently add a second authority store or widen operator/policy authority.

## What not to do

- Do not mark all drafts ready merely because previous CI was green.
- Do not merge top-of-stack PRs into their feature-branch bases and call the capability integrated into `main`.
- Do not treat the primary continuity's earlier comments as independent approval.
- Do not re-review unchanged upstream code repeatedly when reviewing a clean retargeted delta; verify integration behavior and focus on the exact remaining delta.
- Do not start the durable-lineage implementation until the relevant harness contract is accepted or its final interface is otherwise known.

## Next integration action

Obtain a genuinely independent review of **PR #20** at its exact current head/base. Once accepted and merged, retarget/synchronize #21 to current `main`, obtain fresh CI, and review that exact delta. In parallel, a separate bounded legacy-archaeology agent may continue evidence recovery because it does not edit these implementation branches.
