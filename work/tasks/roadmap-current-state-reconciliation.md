# Task: current capability roadmap reconciliation

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `FOUNDRY / Planning-Control-Surface`
- Risk: `MEDIUM`
- Goal: reconcile the master/Prime capability roadmaps and recovered legacy candidates with accepted and open repository state as of 2026-08-16, without turning roadmap prose or open PRs into runtime authority.

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

Without reconciliation, a fresh planning agent can repeat already-merged work, treat planning-only PRs as runtime authority, miss real dependency stacks, infer obsolete sequencing, or revive legacy subsystems unnecessarily.

## Change boundary

Changed only:

- this task file;
- `work/roadmaps/current-capability-reconciliation-2026-08-16.md`;
- `work/roadmaps/README.md`.

Deliberately not changed:

- runtime code or tests;
- SQLite/schema/state;
- provider behavior;
- feature branches;
- another agent's coordination file;
- merge/integration state;
- review dispositions;
- the long-form master/Prime architecture itself.

The dated reconciliation is a current-state overlay rather than a wholesale rewrite of historical design documents.

## Decision authority

FOUNDRY may classify planning state from verified live evidence, identify obsolete roadmap assumptions, preserve dependencies/UNKNOWNs, and shape bounded future questions.

FOUNDRY may not declare unmerged work accepted, choose SWITCHYARD's merge order, approve another lane's work, promote legacy candidates into runtime, assign implementation contrary to coordination, or invent missing runtime architecture.

## Required invariants

- one fact / one authority;
- capability != authority;
- source evidence > summaries;
- derived planning status remains derived;
- open PR != accepted capability;
- planning/design PR != runtime dependency by citation alone;
- UNKNOWN remains UNKNOWN where evidence is incomplete;
- dependency ordering is not merge priority;
- no self-authorizing learning/promotion.

## Acceptance criteria

- [x] exact snapshot base is stated and live GitHub explicitly supersedes it;
- [x] merged PR #19 is recognized as accepted foundation; obsolete “draft PR #19 / pending Phase 0” status is retired;
- [x] accepted Harness #20–#24 is separated from open durable lineage work;
- [x] accepted Run Record/frozen regression/comparative evaluator #33–#35 is represented without claiming complete replay/refinement;
- [x] accepted Skills #25–#27/#31 is separated from future production routing/promotion;
- [x] accepted Environment #28/#29 is separated from open #30 and later recovery/environment automation;
- [x] accepted review-subject #32 is represented as closing the basic immutable reviewed-output identity gap;
- [x] accepted wait subset #59 is separated from future communication-response waits; #51/#52 remain planning-only;
- [x] dependency stacks are explicit: #48→#49→#50, #44→#45, #39→#41→#53, #43→#60;
- [x] repaired/unmerged heads remain `OPEN_REVIEW`, `OPEN_INTEGRATION`, or `BLOCKED_UPSTREAM`, never `ACCEPTED`;
- [x] Context Builder v1 from #19 is separated from v2 evaluation work;
- [x] legacy candidates are classified as absorbed, partial/open, or evidence-triggered rather than blindly copied into next work;
- [x] bounded next questions are identified without prematurely choosing runtime architecture;
- [x] roadmap index links the reconciliation as a dated implementation-status overlay;
- [x] no runtime/schema/test files are modified.

## Verification and exact-state evidence

Immediately before final handoff:

- accepted `main` was re-read and remained `146f092a63af63b0fd750445e584a39e82ea1442`;
- live coordination/ownership lanes were re-read;
- PR #48 moved materially twice during planning, so the reconciliation was refreshed rather than preserving stale status;
- final #48 feature head is `2f23959afff9525beada28993bad536878310b7f`, Runtime CI #392 / `31931474528` PASS;
- SENTINEL independently reviewed that exact #48 head and returned `CLEAN IN-LAYER / NOT INTEGRATION-READY`; therefore #48 is represented as `OPEN_INTEGRATION`, not accepted;
- #39/#41/#53, #43/#60, #30, and #51/#52 authority/dependency boundaries were rechecked against live PR metadata;
- final branch compare must remain limited to the three declared planning/task files.

No implementation status is inferred solely from this task/reconciliation; exact live state must be rechecked at use time.

## Independent review focus

This planning artifact can affect future work selection/sequencing, so independent review is required. Reviewer should verify:

- factual status against live GitHub;
- no unmerged capability is promoted to accepted;
- no stale branch SHA is treated as authority;
- dependency constraints are separated from merge priority;
- no duplicate runtime authority is introduced through planning prose;
- recovered legacy work is classified rather than revived wholesale;
- #48 is represented as clean in-layer but still pending SWITCHYARD synchronization/integrated-head gates.

Review required: `INDEPENDENT_REVIEW`.
FOUNDRY authored this planning change and is not eligible to provide the independent disposition.

## Stop / escalate

Stop rather than guess if live main/PR movement invalidates a material status claim, ownership conflicts cannot be resolved from live evidence, a planning candidate would require a new authority store merely for roadmap neatness, or accepted runtime behavior conflicts with an open design in a way that cannot be safely classified.

Escalate implementation questions to ANVIL, merge/integration order to SWITCHYARD, and independent review to SENTINEL or another eligible reviewer.
