# Task: execution lineage Wave 3 design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `ARCHITECTURE`
- Owner: `agent/execution-lineage-design-wave3`
- Risk: `MEDIUM`
- Goal: Produce an implementation-ready, planning-only design for explicit MAPS execution lineage without changing runtime behavior or creating duplicate task/session/review authority.

## Inputs and source of truth

- Inputs:
  - root `AGENTS.md`;
  - `templates/task.md` and `playbook/AGI_STANDARD.md`;
  - current `main` at `086e066f723d793273441dd52b500e62ac981deb`;
  - `runtime/state/schema.sql`;
  - `runtime/state/execution.py`;
  - `runtime/state/observability.py`;
  - `runtime/state/store.py`;
  - `runtime/communication/hcom_adapter.py` and `runtime/communication/README.md`;
  - `runtime/helpers/common.py`;
  - `runtime/recovery/store.py` and `runtime/recovery/supervisor.py`;
  - PR #24 head `3110457c78a1d30b4b6692d78108617d88c4d0ba` as the current prospective harness/security interface;
  - PR #33 head `3d618a4d74d8be4ba42e119cc5d659e204ccd9d5` as the current prospective portable Run Record interface;
  - PR #36 reconciliation planning as research/planning evidence only.
- Authoritative sources:
  - current merged `main` wins for accepted runtime behavior;
  - exact current PR heads may be inspected only as prospective interfaces and are not accepted authority until independently reviewed/merged;
  - root `AGENTS.md` wins on authority, uncertainty, and duplicate-truth constraints.
- Evidence labels:
  - `VERIFIED`: directly inspected current repository files/PR heads named above;
  - `PROSPECTIVE`: behavior present only on an open implementation PR;
  - `UNKNOWN`: external/provider facts not mechanically established by current source interfaces.
- Dependencies / preconditions:
  - Design may proceed now.
  - Runtime implementation must wait until the relevant harness/security and Run Record interfaces are accepted or their final reviewed shapes are known.

## Change boundary

- MAY CHANGE:
  - `work/tasks/execution-lineage-wave3.md`
  - `work/notes/2026-08-15-execution-lineage-design.md`
  - a planning-only branch and draft PR containing only those files.
- MUST NOT CHANGE:
  - any `runtime/` code;
  - any tests;
  - any migration/legacy source;
  - any master/reconciliation roadmap;
  - any existing PR #20-#37 branch, review, base, or status;
  - task/session/review/policy authority semantics.
- MAY CHANGE IF NECESSARY:
  - none during this design task; new output paths require a task amendment first.
- OPERATOR APPROVAL REQUIRED:
  - any runtime/schema implementation;
  - any change to accepted task, review, policy, provider, or release authority;
  - any modification of another agent's active PR branch.

## Decision authority

- Owner may decide:
  - evidence organization;
  - planning terminology;
  - the smallest proposed lineage relationships and staged implementation order;
  - explicit non-goals and acceptance tests consistent with current architecture.
- Owner must escalate:
  - any design that would require a second task/session/review/policy authority store;
  - any assumption that hcom/provider metadata proves more identity/readiness than the inspected interface actually exposes;
  - any proposal that would mutate immutable run manifests after creation;
  - any runtime implementation before reviewed upstream interfaces are known.

## Acceptance criteria

- [x] Current accepted identity/evidence sources are mapped by owner and authority role.
- [x] Current gaps are stated using explicit `VERIFIED`, `PROSPECTIVE`, and `UNKNOWN` evidence status.
- [x] The design preserves immutable run manifests and does not introduce a mutable `current_session_id` copy on tasks.
- [x] Late session attachment and session replacement have explicit, non-inferential semantics.
- [x] Cross-worker/context replacement creates a new run rather than rewriting the original run identity.
- [x] Helper, recovery, communication/request, and submission lineage have bounded proposed link shapes.
- [x] Provider/API readiness remains separate from process/session liveness.
- [x] Trace and Run Record projections preserve `MISSING`/`UNKNOWN` rather than claiming complete replay.
- [x] Backward compatibility for existing runs/helper/recovery/submission records is specified.
- [x] Concrete behavioral acceptance tests and a small PR sequence are specified.
- [x] No runtime code, tests, roadmaps, or existing PR branches are modified.

## Verification and evidence

- Verification:
  - inspect the exact source files/PR heads listed above;
  - re-fetch both generated planning files from the new branch;
  - verify the draft PR changed-file list contains only the two approved paths;
  - verify the PR remains planning-only and draft.
- Evidence to preserve:
  - branch head SHA;
  - draft PR number/head/base;
  - changed-file list;
  - exact current upstream heads treated as prospective inputs.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: GitHub repository `BigCatMellow/MAPS_Lean`; design is repository/planning-only.
- Ordered procedure:
  1. recover current `main` and operating contract;
  2. inspect accepted identity/evidence sources;
  3. inspect open harness/Run Record interfaces only as prospective inputs;
  4. design smallest lineage relations without duplicating authority;
  5. publish only the two planning artifacts on an isolated branch/draft PR;
  6. re-check exact changed-file scope.
- Failure branches:
  - IF an upstream draft head changes materially before implementation THEN re-read the accepted/final interface and amend the implementation task, not this historical evidence snapshot silently.
  - IF hcom/provider event identity or worker/session attribution cannot be proven THEN preserve `UNKNOWN` and require a bounded evidence probe before communication/session binding implementation.
  - IF a proposed relation duplicates an existing authoritative fact THEN derive/reference the existing source instead of storing a mutable copy.
- Rollback / recovery: close the draft PR/delete the isolated planning branch if the design is rejected; no runtime rollback is needed because runtime is unchanged.
- Security / privacy controls:
  - do not copy hcom message bodies, provider transcripts, secrets, raw task evidence, or helper raw output into lineage records;
  - store stable identifiers, bounded reason/status codes, timestamps, and evidence references only.
- External side effects: create one isolated GitHub branch and one draft planning PR; explicitly authorized by the operator's `go for it` instruction.
- Effort limit: stop after an implementation-ready design and verification; do not expand into implementation or broad archaeology.
- Approved reference: `work/roadmaps/legacy-recovery-reconciliation.md` NEXT A requirements, subordinate to root `AGENTS.md` and merged code.

## Stop / escalate

Stop rather than guess if:

- a provider/session identity cannot be tied to a run by an authoritative or explicitly approved evidence source;
- a worker change would require pretending an immutable run still has the same worker identity;
- communication correlation would require parsing arbitrary message prose;
- external event IDs/thread/addressee semantics are not exposed strongly enough by hcom to support an exact join;
- review of PR #20-#24 materially changes the binding/session contract before implementation;
- implementation would require modifying another active branch or widening this task beyond planning.

Escalate to: operator or a separately shaped research/implementation task, depending on the blocker.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- `run_manifests` remain the immutable initial task/run/worker binding; a new design must not mutate them to retrofit late sessions.
- hcom owns provider communication/session facts; MAPS may own only explicit cross-source correlation facts that hcom does not own.
- helper/recovery stores remain evidence sources; a lineage layer must not copy their mutable/result state into a new authority plane.
- a provider session existing or reporting `RUNNING` does not prove provider/API readiness, task ownership, progress, or authority.
- current hcom `send()`/`read_events()` expose thread/agent/intent surfaces but the inspected adapter does not validate a stable external event-ID/addressee schema; exact communication-event joining is therefore `UNKNOWN` until separately proven.

## Completion / handoff

- Completed: implementation-ready planning design and task contract prepared on an isolated branch.
- Not completed: runtime/schema/test implementation; intentionally deferred until upstream independent review settles relevant interfaces.
- Current blocker: none for design; implementation depends on accepted/final harness/security interfaces and exact communication-event evidence where required.
- Next action if not DONE: independent review of this design, then shape the first implementation tranche against accepted upstream heads.