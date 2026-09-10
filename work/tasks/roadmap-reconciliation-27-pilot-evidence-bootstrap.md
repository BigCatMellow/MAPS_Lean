# Task: Roadmap reconciliation #27 — Pilot evidence bootstrap

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `ChatGPT — operator-directed reconciliation lane`
- Risk: `MEDIUM`
- Goal: reconcile all 16 unfinished master capabilities against current MAPS_L evidence plus the Pilot borrow-before-build corpus, without changing capability status from research alone; preserve a bounded next sequence and a conditional prior-art check for future reusable-mechanism work.
- Parent roadmap: [`../roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md`](../roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md) + [`../../playbook/ROADMAP_TRAJECTORY_CHECK.md`](../../playbook/ROADMAP_TRAJECTORY_CHECK.md); operator-directed 2026-09-09
- Related records: [`../roadmaps/CAPABILITY_CHECKLIST.md`](../roadmaps/CAPABILITY_CHECKLIST.md), [`../../playbook/PROGRAM_STEERING.md`](../../playbook/PROGRAM_STEERING.md), Pilot research crosswalk `BigCatMellow/Pilot_Projects@research/competitive-architecture-borrow-before-build:complete-ai-work-system/research/MAPS_L-INTEGRATION-MAP.md`
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: current `main`; current capability checklist; master + six detailed capability roadmaps; current Development wiki snapshot as orientation only; live GitHub PR state; Pilot research integration map, production-accelerator test/fix-history corpus, and dated bootstrap assessment.
- Authoritative sources: `AGENTS.md` > approved roadmap/project envelope > this task > canonical runtime/task state > current merged code/tests/live GitHub. `CAPABILITY_CHECKLIST.md` is the canonical roadmap status overlay but remains evidence-backed rather than permission. Pilot research is supporting evidence only.
- Evidence labels: current `main`/merged code/roadmap state = `VERIFIED`; upstream/Pilot research = `REFERENCE` until locally applicable; untested design implications = `CANDIDATE`.
- Dependencies / preconditions: PR #319 is an independently owned active lane and is excluded from this task. Current `main` at task start: `18b064cdce00963b0417c8105c36e7fe624f3e4e`; the two commits after trajectory check #26 only add/update `docs/wiki/Development.md` and `_Sidebar.md`, with no capability implementation/status change.

## Change boundary

- MAY CHANGE: this task; one dated reconciliation note under `work/notes/`; a bounded clarification in `playbook/PROGRAM_STEERING.md` for conditional borrow-before-build evidence recovery.
- MUST NOT CHANGE: PR #319 or its branch/files; `playbook/EMERGENCE.md`; `playbook/INDEX.md` for #319's supersession proposal; `AGENTS.md`; runtime code; schemas; capability STATUS values; detailed roadmap status claims; wiki status; merge authority; Pilot repositories.
- MAY CHANGE IF NECESSARY: direct links/routing text needed to keep the reconciliation note discoverable, but only if a current owner cannot already route it.
- HUMAN REAUTHORIZATION REQUIRED: any capability status flip unsupported by current merged evidence; any replacement of SQLite/LangGraph/task authority; any new objective/authority expansion; any action on PR #319.

## Decision authority

- Inherited roadmap authority: current MAPS_L capability program may reconcile roadmap/evidence, shape bounded next work, and improve subordinate planning methods without inventing new scope.
- Owner may decide: KEEP/STRENGTHEN/DEFER/CHALLENGE classifications as advisory trajectory findings; the smallest discriminating test for a challenged assumption; concise process wording that only requires prior-art inspection when a reusable mechanism is actually being created or materially changed.
- Resolve internally first: whether Pilot research materially changes a current plan, whether an upstream mechanism is evidence-only versus locally relevant, and whether a conditional capability should stay gated.
- Human escalation only if: the recommendation crosses objective/scope/authority, spends money, changes credentials/permissions, performs destructive/external action, or attempts to disposition PR #319.

## Acceptance criteria

- [x] All 10 `IN PROGRESS` and 6 `NOT STARTED` master capabilities receive one explicit `KEEP | STRENGTHEN | DEFER | CHALLENGE` disposition with a short evidence-backed rationale and next proof/trigger.
- [x] No `DONE / IN PROGRESS / NOT STARTED` status changes are made from research alone.
- [x] PR #319 is named as a collision/exclusion boundary and is neither modified nor assumed merged.
- [x] The reconciliation distinguishes reuse/test evidence from adoption authority; DBOS/Restate/Temporal/DSH/LiteLLM/etc. do not become MAPS dependencies by citation.
- [x] A conditional borrow-before-build step is specified for reusable/general mechanism work and explicitly skipped for routine local fixes/application of accepted mechanisms.
- [x] The resulting next sequence prioritizes current production-evidence closure before broad new capability construction.
- [ ] Independent review verifies classification fidelity, no hidden status/authority change, and no collision with PR #319.

## Verification and evidence

- Verification: compare `25c7729..18b064c`; inspect current Development page, capability checklist/master/detail roadmaps, `PROGRAM_STEERING.md`, `ROADMAP_TRAJECTORY_CHECK.md`, current open PR state, and Pilot integration map; inspect final diff for boundary compliance.
- Evidence to preserve: dated reconciliation note + exact base commit + PR diff + independent review disposition.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: GitHub `BigCatMellow/MAPS_Lean`, docs/planning only.
- Ordered procedure: recover live state → exclude PR #319 → re-derive unfinished inventory → compare each item to current owner + Pilot evidence → classify → identify smallest proof/trigger → update only the existing steering method if a genuine process delta exists → independent review.
- Failure branches: IF live `main` gains capability-changing commits while this PR is open THEN revalidate affected rows before review; IF another PR starts touching the same files THEN rebase/re-scope rather than overwriting; IF evidence cannot distinguish KEEP/STRENGTHEN/DEFER/CHALLENGE THEN preserve `UNKNOWN` and do not create a roadmap delta.
- Rollback / recovery: docs-only branch; close/supersede PR if stale or duplicative.
- Security / privacy controls: no credentials/secrets; no external execution.
- External side effects: GitHub branch/PR only; no merge authority implied.
- Effort limit: one bounded reconciliation pass; do not reopen broad upstream research unless a concrete row cannot be decided from the existing corpus.
- Approved reference: current master/checklist + Pilot `MAPS_L-INTEGRATION-MAP.md`.
- Operational independence: `N/A — one-off roadmap reconciliation; the durable note and steering wording are the reproducible outputs.`
- Reproduction package: read this task, the dated reconciliation note, current `CAPABILITY_CHECKLIST.md`, and Pilot integration map; re-run the classification against current `main` before relying on it after material roadmap change.

## Question-resolution ladder

```text
authoritative evidence
→ safe inspection
→ focused existing Pilot/upstream research
→ independent challenge when consequential
→ orchestration operator decides inside inherited authority
→ human only if the decision would cross that authority
```

## Stop / escalate

- Stop any branch that would touch or depend on PR #319's unmerged authority proposal.
- Stop rather than flipping a capability status without local implementation/exercise evidence.
- Stop rather than replacing an existing MAPS owner/control plane from upstream research alone.
- Continue all independent reconciliation work that remains inside the approved capability program.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task is a research-backed roadmap reconciliation, not formal trajectory check #27's normal arc accounting/friction/emergence pass. It may inform the next canonical trajectory check; it must not counterfeit that cadence or its status authority.
- `CHALLENGE` here means “run a discriminating comparison/test against one current assumption,” not “supersede the mechanism.” Supersession authority is outside this task and PR #319 is reserved.

## Completion / handoff

- Completed: classification and bootstrap design authored; awaiting independent review.
- Not completed: independent review; any later capability implementation/exercises.
- Triage capture: `none — no §2 trigger fired during docs-only reconciliation.`
- Reproduction package: task + dated note + exact sources/links; automation `N/A — one-off evidence reconciliation`.
- Current blocker: none for review; no merge authority claimed.
- Next eligible roadmap task: current shipped Development sequence still starts with 6.4 and 6.22 first-exposure evidence unless newer merged evidence changes that.
- Human action required: none for this reconciliation; PR #319 remains separately owned.