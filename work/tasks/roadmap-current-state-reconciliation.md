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
- live capability-relevant PR/merge/review/CI state.

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

Changed only planning/task documentation:

- this task file;
- `work/roadmaps/current-capability-reconciliation-2026-08-16.md`;
- `work/roadmaps/README.md`.

Deliberately not changed:

- runtime code;
- tests;
- SQLite/schema/state;
- provider behavior;
- active feature branches;
- another agent's coordination file;
- merge/integration state;
- review dispositions;
- the long-form master/Prime roadmap architecture itself.

The dated reconciliation is used as a current-state overlay rather than rewriting historical architecture prose wholesale.

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
- planning/design PR != runtime dependency unless accepted implementation actually depends on it;
- UNKNOWN remains UNKNOWN where review/integration evidence is incomplete;
- dependency ordering is preserved without turning it into speculative merge priority;
- no self-authorizing learning/promotion.

## Acceptance criteria

- [x] roadmap reconciliation clearly states exact snapshot base and that live GitHub supersedes it;
- [x] merged PR #19 is recognized as accepted foundation, retiring obsolete “draft PR #19 / pending Phase 0” baseline;
- [x] accepted Harness Wave 1 (#20–#24) is distinguished from still-open durable lineage work;
- [x] accepted Run Record / frozen regression / comparative evaluator foundation (#33–#35) is represented without claiming full replay/refinement;
- [x] accepted Skills foundation/eval/static gate (#25–#27/#31) is separated from future production skill routing/promotion;
- [x] accepted Environment E1/E2 (#28/#29) is separated from open E3 run evidence (#30) and later recovery/environment automation;
- [x] accepted consequential review-subject binding (#32) is represented as closing the basic immutable reviewed-output identity gap;
- [x] accepted structured wait projection (#59) is separated from future communication-response waits; #51/#52 remain planning/design evidence rather than runtime authority;
- [x] open dependency stacks are explicit: #48→#49→#50, #44→#45, #39→#41→#53, #43→#60;
- [x] repaired/unmerged heads remain `OPEN_REVIEW` / `OPEN_INTEGRATION` / `BLOCKED_UPSTREAM` rather than `ACCEPTED`;
- [x] Context Builder v1 from #19 is distinguished from evaluation-only v2 work;
- [x] legacy recovered candidates are classified as already absorbed, partially represented/open, or evidence-triggered rather than blindly copied into next work;
- [x] obsolete roadmap assumptions and bounded next planning questions are identified without choosing runtime architecture prematurely;
- [x] `work/roadmaps/README.md` links the reconciliation as the dated implementation-status overlay;
- [x] no runtime/schema/test files are modified.

## Verification and exact-state evidence

Immediately before final handoff:

- accepted `main` was re-read and remained `146f092a63af63b0fd750445e584a39e82ea1442`;
- live ownership lanes were re-read from coordination files;
- PR #48 moved materially during planning because independent review returned a second HIGH SQLite-normalization defect; the reconciliation was updated rather than preserving the stale earlier head;
- final #48 repair head is `2f23959afff9525beada28993bad536878310b7f`, Runtime CI #392 / `31931474528` PASS, and remains `OPEN_REVIEW`, not accepted;
- #39/#41/#53, #43/#60, #30, #51/#52 and their authority/dependency boundaries were rechecked against live PR metadata;
- planning branch compare must remain limited to the three declared planning/task files.

No implementation status is inferred solely from this task or reconciliation; exact live state must be rechecked at use time.

## Independent review focus

Because this planning artifact can influence future work selection/sequencing, independent review is required. Reviewer should verify:

- factual status against live GitHub;
- no unmerged capability is promoted to accepted;
- no stale branch SHA is treated as authority;
- dependency constraints are separated from merge priority;
- no duplicate runtime authority is introduced through planning prose;
- recovered legacy work is classified rather than revived wholesale;
- #48 is represented as repaired/CI-green but still pending independent review/integration.

Review required: `INDEPENDENT_REVIEW`.
FOUNDRY authored this planning change and is not eligible to supply the independent disposition.

## Stop / escalate

Stop rather than guess if:

- live main/PR movement invalidates a material status claim while this document is being finalized;
- two current agent notes claim the same runtime output path and ownership cannot be resolved from live state;
- a roadmap candidate would require a new authority store or widened policy semantics merely to make the plan internally tidy;
- an open planning PR conflicts with accepted runtime behavior and the intended future direction cannot be distinguished from historical design.

Escalate implementation questions to ANVIL after shaping. Escalate merge/integration order to SWITCHYARD. Send review of this planning change to SENTINEL or another eligible independent reviewer.
