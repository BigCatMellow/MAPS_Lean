# Roadmap: GitHub-native asynchronous work pull

- State: `WORKING`

## Goal

Make separate ChatGPT browser sessions cooperate asynchronously through GitHub with durable role contracts and minimal operator relay, while draining the inherited backlog without repeated status-snapshot or multi-candidate synchronization churn.

Core model:

> **Operator binds roles. TOWER prioritizes. Development lanes build/repair. SENTINEL reviews. SWITCHYARD integrates. GitHub carries live coordination.**

## Current reality

The browser trial established several durable findings:

- browser sessions cannot reliably wake/message one another directly;
- unbound sessions must not infer their permanent role from workload;
- live GitHub already contains the volatile facts needed for coordination;
- dated role/status snapshots become stale as `main` advances and can consume their own CI/review/integration cycles;
- parallel development/review is useful, but pre-synchronizing several final candidates to one `main` creates predictable invalidation when the first candidate merges;
- dependency chains should advance bottom-up, one accepted prerequisite at a time;
- feature-level independent review remains valuable while a branch waits, but it is not merge-authoritative integrated-head review;
- reviewer continuity labels help coordinate parallel SENTINEL sessions but never prove independence;
- a bounded ownerless repair can deadlock unless there is an explicit routing mechanism;
- accepted `main` must always win by default over stale historical content during reconciliation.

These findings justify simplifying coordination rather than adding another scheduler/database.

## Definition of DONE

The operating package is accepted when:

- every browser role has one durable role contract;
- `work/coordination/README.md` is the shared entry point;
- `GITHUB_ASYNC_WORK_PULL.md` defines browser binding, pull loops, handoffs, review layers, backlog control, dependency-first integration, and anti-regression rules;
- `BACKLOG_RECOVERY.md` defines temporary recovery flow and exit criteria;
- volatile status is read from GitHub rather than maintained in repository snapshots;
- SWITCHYARD uses one merge-authoritative product integration slot during recovery;
- development and feature review remain safely parallel before that slot;
- TOWER can make a narrowly scoped operator-authorized orphaned-development assignment without acquiring review/integration authority;
- a real recovery run demonstrates that ordinary merges no longer invalidate a large queue of synchronized integration reviews.

## Final proof

Run the browser pool under the accepted package and verify:

1. each session is explicitly operator-bound;
2. an unbound control session refuses consequential work;
3. each role starts from `work/coordination/README.md`, its role contract, and live GitHub;
4. no agent creates/refreshes a status-snapshot PR merely because GitHub state moved;
5. ANVIL/FOUNDRY can work distinct existing development/repair items in parallel;
6. downstream implementation waits for actual prerequisite acceptance unless a safe independent boundary is explicit;
7. stable feature/repair heads receive `CLEAN IN-LAYER` review and then freeze;
8. parallel SENTINEL continuities claim distinct exact-layer subjects and preserve continuity-specific independence;
9. SWITCHYARD maintains the full backlog but advances exactly one product candidate through final latest-main synchronization/CI/integrated review/merge;
10. accepted `main` is preserved against stale historical branch regressions;
11. after each merge SWITCHYARD rescans and chooses the next dependency-correct candidate;
12. superseded status/checkpoint PRs are closed only after the durable-value test;
13. an orphaned already-bounded repair can be explicitly assigned by TOWER without branch seizure or authority drift;
14. the backlog returns to a small steady-state queue and recovery mode can end without restoring status-snapshot maintenance.

## Boundaries

In scope:

- explicit role binding;
- durable role contracts for TOWER, ANVIL, FOUNDRY, SENTINEL, SWITCHYARD;
- GitHub-native live coordination;
- parallel SENTINEL reviewer continuities;
- exact-layer review claims;
- feature-review vs integrated-review distinction;
- persistent SWITCHYARD backlog control;
- one-slot recovery merge train;
- dependency-first / bottom-up integration;
- current-main anti-regression proof;
- bounded orphaned-development assignment during operator-declared recovery mode;
- durable-vs-live coordination boundary;
- recovery exit criteria.

Not doing:

- dynamic/self-selected roles;
- automatic task assignment without bounded authority;
- automatic merge authority;
- a second task/PR/review database;
- daemon/scheduler infrastructure;
- mandatory mutable inbox/status files;
- speculative capability work merely to occupy idle lanes.

## Phase 0 — durable coordination package

- [x] Make `work/coordination/README.md` the start-here entry point.
- [x] Convert ANVIL role file from dated status snapshot to durable contract.
- [x] Convert FOUNDRY role file from dated status snapshot to durable contract.
- [x] Convert SENTINEL role file from dated status snapshot to durable contract.
- [x] Convert SWITCHYARD role file from dated status snapshot to durable contract.
- [x] Add durable TOWER role file to the shared package.
- [x] Add `work/coordination/BACKLOG_RECOVERY.md`.
- [x] Consolidate the async protocol around durable state + live GitHub state.
- [x] Declare exactly one merge-authoritative product integration slot during recovery.
- [x] Define feature/repair review separately from integrated-head review.
- [x] Define exact-layer SENTINEL claims and continuity-specific independence.
- [x] Define bounded operator-authorized orphaned-development assignment.
- [x] Update task/change boundary for the expanded coordination package.
- [ ] Fresh exact-head verification/CI for the completed package.
- [ ] Fresh independent review of the completed package.
- [ ] SWITCHYARD integration if clean.

## Phase 1 — backlog recovery execution

After the package is accepted, operate in `BACKLOG_RECOVERY.md` mode:

- [ ] Stop creating new status-snapshot PRs.
- [ ] SWITCHYARD applies durable-value test to historical status/checkpoint PRs and closes genuine superseded work.
- [ ] Limit active development roots and dependency depth.
- [ ] Keep stable feature/repair heads frozen after appropriate review.
- [ ] Advance one final product integration candidate at a time.
- [ ] Rescan full backlog after every accepted merge.
- [ ] Preserve live ownership/claims/CI/blockers only on GitHub threads.
- [ ] Use bounded TOWER orphan assignment only when no active incumbent exists and scope is already authorized.
- [ ] Track recovery health from live GitHub without creating a repository status ledger.

Checkpoint:

- `CONTINUE` while dependency stacks are shrinking without repeated integration invalidation;
- `CHANGE` if the one-slot train creates an unexpected bottleneck or an authority gap appears;
- `CUT SCOPE` if durable coordination machinery itself becomes maintenance overhead;
- `STOP RECOVERY` when exit criteria are met.

## Phase 2 — steady-state operation

When recovery exits:

- retain durable role contracts and live-GitHub status boundary;
- preserve dependency-first integration and accepted-main anti-regression rules;
- decide whether one-slot integration remains the normal default or only a recovery-mode rule based on observed throughput;
- keep feature-review/integrated-review evidence classes distinct;
- remove or archive temporary recovery-only guidance only if doing so does not recreate the old churn;
- resume normal roadmap/capability development from the now-small backlog.

## Design guardrails

- one fact / one authority;
- capability != authority;
- preserve `UNKNOWN`;
- source/live evidence > summaries;
- no self-selected roles;
- no hidden ownership transfer;
- no reviewer mutation;
- no status-snapshot PR churn;
- no PR-age merge authority;
- no historical regression of accepted `main`;
- no speculative downstream work on unaccepted ancestry;
- no merge-count pressure overriding real gates;
- no second live queue database.

## Operator usage

Point every role-bound browser to:

1. `work/coordination/README.md`;
2. its own `work/coordination/agents/<ROLE>.md`;
3. `work/coordination/GITHUB_ASYNC_WORK_PULL.md`;
4. `work/coordination/BACKLOG_RECOVERY.md` while active;
5. live GitHub state.

After that, `Continue. Recover live GitHub state and pull the highest-priority eligible work for your bound role.` should normally be sufficient.
