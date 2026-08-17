# Task: GitHub-native asynchronous work pull and backlog recovery

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING / COORDINATION`
- Owner: `TOWER`
- Risk: `MEDIUM`

## Goal

Define one durable GitHub-native operating package for separate role-bound ChatGPT browser sessions, including the temporary backlog-recovery mode needed to drain inherited PR stacks without status-snapshot churn or repeated multi-candidate synchronization.

Core model:

> **Operator binds roles. TOWER prioritizes. Development lanes build/repair. SENTINEL reviews. SWITCHYARD integrates. GitHub carries live coordination.**

## Source evidence

Inputs include:

- root `AGENTS.md`;
- operator direction to recover the backlog and update all role files;
- live browser trial evidence that unbound sessions can self-select incorrectly unless roles are explicit;
- live evidence that status-snapshot PRs become stale and consume repeated CI/review capacity;
- live evidence that synchronizing several final candidates to one `main` causes most integrated review packets to become stale after the first merge;
- cross-role recovery feedback from ANVIL, FOUNDRY, SWITCHYARD, and SENTINEL-A/B/C on PR #73;
- successful bounded #43 repair flow as evidence for feature-review/final-integration separation.

Authority remains operator/policy -> canonical MAPS task state -> accepted `main` / live GitHub -> derived coordination guidance.

## Change boundary

MAY CHANGE on `coord/github-async-work-pull-20260816`:

- `work/coordination/README.md`
- `work/coordination/GITHUB_ASYNC_WORK_PULL.md`
- `work/coordination/BACKLOG_RECOVERY.md`
- `work/coordination/agents/TOWER.md`
- `work/coordination/agents/ANVIL.md`
- `work/coordination/agents/FOUNDRY.md`
- `work/coordination/agents/SENTINEL.md`
- `work/coordination/agents/SWITCHYARD.md`
- `work/roadmaps/github-async-work-pull.md`
- this task record
- PR #73 metadata/comments for the coordination change.

MUST NOT CHANGE:

- runtime code;
- schemas/tests/product behavior;
- feature branches;
- existing feature review dispositions;
- merge state;
- canonical task lifecycle facts unrelated to this coordination task.

The operator explicitly authorized this coordinated cross-role-file rewrite so the role files can become durable contracts instead of owner-specific status snapshots.

## Decision authority

- Operator binds every browser session to a role and retains intent/scope/consequential approval authority.
- Operator explicitly activates backlog-recovery mode and authorizes TOWER's bounded orphaned-development assignment mechanism described below.
- TOWER owns derived priority/dependency reasoning and may make bounded recovery-mode assignments, but not review/integration/merge authority.
- ANVIL/FOUNDRY own task-authorized development/repair steps assigned to them.
- SENTINEL retains independent review authority.
- SWITCHYARD owns persistent full-backlog PR control and final integration/merge safety.
- Accepted `main` is the forward integration baseline; historical branch content cannot silently regress it.

## Recovery-mode authority clarification

During backlog recovery, if an existing development/repair item has no active incumbent owner continuity and the required work is already task-authorized and bounded, TOWER may assign that bounded step to ANVIL or FOUNDRY after live ownership/dependency verification.

The GitHub handoff must identify exact target, bounded defect/step, dependency state, allowed scope, and state that no broader redesign or authority transfer is granted.

This does not transfer review, integration, merge, policy, or broader task authority and cannot be used to seize an actively owned branch or infer an unknown task boundary.

## Acceptance criteria

### Durable coordination model

- [x] `work/coordination/README.md` is the single coordination entry point and distinguishes durable repository rules from volatile GitHub status.
- [x] All five permanent role files exist as durable role contracts and contain no live PR queue snapshot.
- [x] Role files point agents to live GitHub for current heads, CI, blockers, review claims/dispositions, and handoffs.
- [x] A new `BACKLOG_RECOVERY.md` defines the temporary recovery operating mode and exit criteria.
- [x] Protocol explicitly forbids status-snapshot PR churn for facts expected to move with ordinary GitHub activity.

### Role binding and pull behavior

- [x] Fresh browser sessions are `UNBOUND` unless explicitly operator-bound.
- [x] Agents never self-select/switch permanent roles because another queue has work.
- [x] Startup/read order is durable and discoverable from README/protocol/role files.
- [x] If no eligible role work exists, the agent remains idle rather than inventing work.

### Development/recovery flow

- [x] ANVIL/FOUNDRY may rebuild against actually accepted dependency interfaces when correctness requires it.
- [x] Development heads freeze after the appropriate feature/repair review boundary instead of chasing unrelated `main` movement.
- [x] Only the next dependent implementation is released after prerequisite acceptance unless a task proves a safe independent output boundary.
- [x] Bounded orphaned-development assignment is explicit, operator-authorized, scoped, and non-transferable to review/integration authority.

### Review model

- [x] `FEATURE / REPAIR REVIEW — CLEAN IN-LAYER` and `INTEGRATED-HEAD REVIEW — CLEAN` are distinct evidence classes.
- [x] Feature-level CLEAN is explicitly not merge clearance.
- [x] Review claims are keyed to PR + exact base + exact head + review layer and are advisory only.
- [x] Reviewer independence is continuity-specific; continuity labels never prove it.
- [x] Prior read-only feature review does not automatically disqualify the same still-independent continuity from later integrated review.
- [x] A fresh exact integrated-head disposition remains required under current rules; earlier feature review may narrow later analysis only under explicit verified equivalence conditions.

### Integration/backlog model

- [x] SWITCHYARD persistently controls the full live open-PR backlog as a derived GitHub view.
- [x] During recovery exactly one product candidate occupies the merge-authoritative integration slot; no multi-candidate exception.
- [x] Non-slot stable/synchronized heads remain frozen and are not proactively refreshed.
- [x] Final synchronization occurs just in time on latest accepted `main`.
- [x] Integration is dependency-first / bottom-up, never by PR chronology.
- [x] Exact `current main -> candidate` anti-regression proof is required and accepted `main` wins by default over stale historical content.
- [x] After every merge SWITCHYARD rescans the full backlog before advancing the next candidate.
- [x] Superseded status/checkpoint PRs use the unique durable-value test and closure does not canonize their prose.

### Safety

- [x] No automatic merge authority, self-review, hidden queue authority, or second mutable task/PR/review database is introduced.
- [x] Verification remains task/risk/path proportional and existing task-specific requirements remain binding.
- [x] The backlog-count target is explicitly a health metric, not close/merge authority.

## Verification and review

- Verify PR #73 exact changed-file set is limited to the declared documentation/planning/coordination paths.
- Verify no runtime/schema/test/product files changed.
- Verify no role contract contains live queue facts that must be updated after every merge.
- Verify links/read order are internally consistent.
- Independent review required because this changes shared multi-agent operating behavior.
- Review should specifically test hidden authority, ownership transfer scope, status-vs-durable boundary, review-layer semantics, claim behavior, one-slot integration, dependency-first anti-regression behavior, and whether recovery rules can deadlock or permit unsafe takeover.
- Any prior #73 review is stale after this coordinated rewrite.

## Stop / escalation

Stop rather than guess if:

- a role must infer its identity;
- task/ownership scope is unknown;
- TOWER's bounded assignment would seize an active owner or broaden an unshaped task;
- review independence is uncertain;
- historical/current-main conflict requires an unresolved authority choice;
- reducing PR count would require weakening dependency/CI/review/ownership/merge gates.

## Completion / handoff

The durable role/protocol/recovery package is ready for fresh independent review once exact changed-file verification and fresh CI complete.

If clean, SWITCHYARD owns final current-main synchronization/integration under the one-slot recovery model.
