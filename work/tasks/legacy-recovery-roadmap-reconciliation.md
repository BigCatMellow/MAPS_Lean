# Task: Legacy recovery roadmap reconciliation

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: primary agent continuity
- Risk: `MEDIUM`
- Goal: reconcile the preserved legacy MAPS discoveries with merged Lean behavior and current open PRs so future implementation has one explicit status/order map without reviving obsolete legacy architecture.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`, `migration/FUTURE_IDEAS_BACKLOG.md`, `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md`, detailed capability roadmaps, merged PR #19, current open PRs #20-#37, and the bounded parallel archaeology report on PR #37.
- Authoritative sources: current `main`, current PR heads/metadata, active `AGENTS.md`, merged code/tests, canonical task/policy/review state, and explicit operator decisions. Legacy/audit/roadmap/research prose is planning evidence only.
- Evidence labels: current GitHub state is `VERIFIED`; legacy evidence is preserved at its recorded status; unresolved `SYN-0004` and `EXP-0007` remain `UNKNOWN` rather than guessed.
- Dependencies / preconditions: current `main` and open PR state must be checked before assigning implementation status.

## Change boundary

- MAY CHANGE: `work/roadmaps/legacy-recovery-reconciliation.md`, `work/roadmaps/README.md`, this task record, and a compact checkpoint/integration note if needed.
- MUST NOT CHANGE: runtime behavior, canonical state, existing open PR implementation branches, `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`, `migration/FUTURE_IDEAS_BACKLOG.md`, or the existing master roadmap's subsystem design during this task.
- MAY CHANGE IF NECESSARY: the master roadmap only in a later follow-up after reconciliation evidence is independently reviewed.
- OPERATOR APPROVAL REQUIRED: destructive legacy deletion or any consequential architecture/policy change; neither is in scope here.

## Decision authority

- Owner may decide: planning taxonomy, status labels, dependency ordering, and where recovered items map to already-merged/current PR work when evidence is explicit.
- Owner must escalate: any proposed new authority store, policy semantics, destructive legacy action, or material conflict between current code and preserved design intent.

## Acceptance criteria

- [x] Every major legacy-derived candidate already preserved in the audit/backlog is mapped to `MERGED`, `IN OPEN PR`, `NEXT`, `TRIGGERED/LATER`, `DO NOT REVIVE`, or `AUDIT REMAINS`.
- [x] Current PR #20-#35 work is mapped to the recovered legacy capabilities it already satisfies or partially satisfies.
- [x] The next implementation sequence is explicit and avoids building on unresolved authority/evidence prerequisites.
- [x] The map explicitly preserves known rejected legacy directions, including the failed lexical claim-card retriever and duplicate control-plane architecture.
- [x] The roadmap index points to the reconciliation map without making it active authority.
- [x] Current stacked PR integration/review ordering is explicit, including how base changes invalidate stale final review/CI evidence.
- [x] Independent bounded archaeology findings from PR #37 are reconciled without copying its historical subsystem forms into Lean.
- [x] Broad legacy archaeology has an explicit stop condition; residual unsupported records remain `UNKNOWN` rather than becoming blockers or assumptions.

## Verification and evidence

- Verification: inspected current `main`, current open PR #20-#37 metadata/state, existing review submissions, source audit/backlog, master roadmap and roadmap index; inspected changed-file inventories for implementation PR deltas; inspected #30/#32 shared state-layer patches and MRO composition; verified #33 passes through optional environment/review-subject trace enrichments without claiming complete lineage; read and reconciled the PR #37 bounded archaeology report against the existing roadmap rather than accepting recommendations wholesale.
- Evidence to preserve: PR #36, PR #37, `work/roadmaps/legacy-recovery-reconciliation.md`, `work/notes/2026-08-15-open-pr-integration-sequence.md`, current `main` SHA `086e066f723d793273441dd52b500e62ac981deb` at shaping time, current PR ranges/status, and Runtime CI results on the planning branch.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: documentation/planning only.
- Ordered procedure: recover current state -> reconcile existing work -> classify remaining items -> order next waves -> publish draft PR -> verify integration topology/review sequence -> consume bounded independent archaeology -> fold only genuinely new evidence.
- Failure branches: if a legacy item cannot be mapped confidently, mark `AUDIT REMAINS/UNKNOWN`; do not invent a disposition.
- Rollback / recovery: planning branch can be abandoned without runtime effect.
- Security / privacy controls: do not copy raw sensitive legacy content; reference IDs/paths and summarized evidence only.
- External side effects: GitHub branch/draft PR only.
- Effort limit: stop broad archaeology once major candidate-bearing collections are classified and remaining unsupported chains are explicitly `UNKNOWN`; do not implement feature work in this task.
- Approved reference: existing master roadmap, migration audit/backlog, and PR #37 as research evidence only.

## Stop / escalate

Stop rather than guess if a recovered candidate appears to require a new source of authority, if current PR behavior materially conflicts with the preserved invariant, or if an unresolved legacy chain changes the critical path.

Escalate to: operator for architecture/authority decisions; targeted research only when an `UNKNOWN` legacy chain materially affects a concrete decision.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task creates a reconciliation layer under the existing master roadmap; it does not create a competing master roadmap.
- The parallel archaeology branch remained non-conflicting and produced PR #37 as research/planning evidence only.
- PR #37 found one genuinely new candidate: risk-triggered user-visible acquisition-path verification. It is preserved as `TRIGGERED/LATER`, not inserted into the lineage/evaluation critical path and not expanded into a general artifact registry.
- PR #37 otherwise sharpened existing NEXT A/B/C/D/E candidates and reinforced existing do-not-revive decisions; `SYN-0004` and `EXP-0007` remain explicit `UNKNOWN`.
- Broad active archaeology can now pause; future legacy retrieval should be targeted to a concrete decision rather than restarted as a general project.
- The next recommended implementation path is truth/evidence first: accept/reshape current draft stacks -> explicit lineage/communication coverage -> explainable waits/full evidence views -> Context Builder v2 evidence integrity -> complete Layer 2/3 evaluation -> controlled operational learning.
- Root PRs #20, #25, #28, #32, #33 and #36 are path-disjoint at the recorded checkpoint; downstream #30 and #32 both compose `runtime/state/schema.sql` and `runtime/state/store.py`. Patch/MRO inspection found them structurally cooperative, but whichever lands second still needs real synchronization, fresh CI and final review on the integrated delta.
- #33 already projects optional environment evidence and immutable review subjects from enriched traces while keeping missing communication/session/helper/recovery lineage explicit.

## Completion / handoff

- Completed: current state recovery, reconciliation map, roadmap-index link, owner verification, stacked-review/integration sequence, cross-stack overlap preflight, Run Record enrichment compatibility check, and reconciliation of PR #37's independent archaeology findings.
- Not completed: independent review of PR #36; independent integration reviews/merges for implementation PRs.
- Current blocker: independent review only for this planning task.
- Next action if not DONE: independently review/integrate PR #20 first; independently review PR #36; preserve PR #37 as research evidence and avoid restarting broad archaeology unless a concrete unresolved claim materially affects a decision.
