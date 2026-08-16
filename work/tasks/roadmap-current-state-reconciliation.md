# Task: current capability roadmap reconciliation

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `FOUNDRY / Planning-Control-Surface`
- Risk: `MEDIUM`
- Goal: reconcile the master/Prime capability roadmaps and recovered legacy candidates with the accepted and open repository state as of 2026-08-16, without turning roadmap prose or open PRs into runtime authority.

## Inputs and source of truth

Authoritative / stronger evidence, in order:

1. root `AGENTS.md`;
2. live GitHub `main`, PR metadata/ancestry, merged code/tests, and exact review/CI evidence;
3. current multi-agent coordination notes under `work/coordination/agents/` for collision avoidance only;
4. accepted task/decision evidence;
5. existing planning roadmaps and migration audits/backlog as non-authoritative design/history evidence.

Planning inputs inspected:

- `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md`;
- `work/roadmaps/prime-agent-capability-roadmap.md`;
- `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md`;
- `work/roadmaps/agent-harness-capabilities/02-procedural-knowledge-and-skills.md`;
- `work/roadmaps/agent-harness-capabilities/03-environment-and-reproducibility.md`;
- `work/roadmaps/agent-harness-capabilities/04-agentic-security.md`;
- `work/roadmaps/agent-harness-capabilities/05-learning-and-evaluation.md`;
- `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`;
- `migration/FUTURE_IDEAS_BACKLOG.md`;
- live capability-relevant PR/merge state.

Snapshot base for this planning branch: `main@146f092a63af63b0fd750445e584a39e82ea1442`.

## Problem

The high-level design remains useful, but the master and Prime roadmaps still describe draft PR #19 as the current foundation and Phase 0 as awaiting stabilization. Live evidence shows PR #19 is merged and later tranches have already accepted substantial Harness, Skills, Environment, review-subject, evaluation, wait-projection, and coordination capabilities.

Without reconciliation, a fresh planning agent can:

- repeat already-merged work;
- treat open planning/design PRs as required runtime authority;
- miss real dependency stacks among still-open work;
- infer an obsolete integration sequence from historical roadmap prose;
- overlook legacy candidates that have already been partially or fully absorbed.

## Change boundary

May change only planning/task documentation:

- this task file;
- a dated current-capability reconciliation document under `work/roadmaps/`;
- the roadmap index to make that reconciliation discoverable;
- narrow stale-baseline annotations in the master and Prime roadmaps if needed to prevent the old PR #19/Phase 0 narrative from being mistaken for current state.

Must not change:

- runtime code;
- tests;
- SQLite/schema/state;
- provider behavior;
- active feature branches;
- another agent's coordination file;
- merge/integration state;
- review dispositions.

## Decision authority

FOUNDRY may:

- classify capability planning state from mechanically verified live evidence;
- identify obsolete roadmap assumptions;
- preserve dependency constraints and unresolved UNKNOWNs;
- shape bounded future implementation questions/tasks;
- distinguish accepted, open-review, blocked-upstream, planning-only, evidence-gated, and historical states.

FOUNDRY may not:

- declare an unmerged PR accepted;
- choose SWITCHYARD's live merge order;
- approve another lane's work;
- promote a legacy candidate into runtime merely because it appears valuable;
- assign implementation ownership contrary to current coordination;
- invent missing runtime architecture to make the roadmap look complete.

## Required invariants

- one fact / one authority;
- capability != authority;
- source evidence > summaries;
- derived planning status remains derived;
- open PR != accepted capability;
- planning/design PR != runtime dependency unless an accepted implementation actually depends on it;
- UNKNOWN remains UNKNOWN where review/integration evidence is incomplete;
- dependency ordering is preserved without turning it into speculative merge priority;
- no self-authorizing learning/promotion.

## Acceptance criteria

- [ ] roadmap reconciliation clearly states its exact snapshot base and that live GitHub supersedes it;
- [ ] merged PR #19 is recognized as accepted foundation, retiring the obsolete “draft PR #19 / pending Phase 0” baseline;
- [ ] accepted Harness Wave 1 (#20–#24) is distinguished from still-open durable lineage work;
- [ ] accepted Run Record / frozen regression / comparative evaluator foundation (#33–#35) is represented without claiming full replay/refinement;
- [ ] accepted Skills foundation/eval/static gate (#25–#27/#31) is separated from future production skill routing/promotion;
- [ ] accepted Environment E1/E2 (#28/#29) is separated from open E3 run evidence (#30) and later recovery/environment automation;
- [ ] accepted consequential review-subject binding (#32) is represented as closing the basic immutable reviewed-output identity gap;
- [ ] accepted structured wait projection (#59) is separated from future communication-response waits; #51/#52 remain planning/design evidence rather than runtime authority;
- [ ] open dependency stacks are explicit: #48→#49→#50, #44→#45, #39→#41→#53, #43→#60;
- [ ] repaired/unmerged heads remain `OPEN_REVIEW` / `BLOCKED_UPSTREAM` rather than `ACCEPTED`;
- [ ] Context Builder v1 from #19 is distinguished from evaluation-only v2 work;
- [ ] legacy recovered candidates are classified as already absorbed, partially represented/open, or still evidence-triggered rather than blindly copied into “next work”;
- [ ] the document identifies obsolete roadmap assumptions and bounded next planning questions without selecting runtime architecture prematurely;
- [ ] `work/roadmaps/README.md` links the reconciliation as the place to check current implementation state;
- [ ] no runtime/schema/test files are modified.

## Verification

Before handoff:

1. compare planning branch against its creation base and verify only declared planning/task files changed;
2. re-read live `main` and capability-relevant PR heads immediately before finalizing the snapshot;
3. update any state that moved materially or label the item UNKNOWN/stale rather than guessing;
4. require independent review because this planning document can affect future work selection/sequencing.

Review focus:

- factual status against live GitHub;
- no unmerged capability promoted to accepted;
- no stale branch SHA treated as authority;
- dependency constraints correctly separated from merge priority;
- no duplicate runtime authority introduced through planning prose;
- recovered legacy work correctly classified rather than revived wholesale.

Review required: `INDEPENDENT_REVIEW`.

## Stop / escalate

Stop rather than guess if:

- live main/PR movement invalidates a material status claim while this document is being finalized;
- two current agent notes claim the same runtime output path and ownership cannot be resolved from live state;
- a roadmap candidate would require a new authority store or widened policy semantics merely to make the plan internally tidy;
- an open planning PR conflicts with accepted runtime behavior and the intended future direction cannot be distinguished from historical design.

Escalate implementation questions to ANVIL after shaping. Escalate merge/integration order to SWITCHYARD. Send review of this planning change to SENTINEL or another eligible independent reviewer.
