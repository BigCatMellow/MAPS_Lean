# Task: Legacy recovery roadmap reconciliation

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: primary agent continuity
- Risk: `MEDIUM`
- Goal: reconcile the preserved legacy MAPS discoveries with merged Lean behavior and current open PRs so future implementation has one explicit status/order map without reviving obsolete legacy architecture.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`, `migration/FUTURE_IDEAS_BACKLOG.md`, `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md`, detailed capability roadmaps, merged PR #19, current open PRs #20-#35, and the parallel archaeology report when it becomes available.
- Authoritative sources: current `main`, current PR heads/metadata, active `AGENTS.md`, merged code/tests, canonical task/policy/review state, and explicit operator decisions. Legacy/audit/roadmap prose is planning evidence only.
- Evidence labels: current GitHub state is `VERIFIED`; legacy audit classifications are preserved as reported evidence until reconciled; unresolved archaeology remains `UNKNOWN`.
- Dependencies / preconditions: current `main` and open PR state must be checked before assigning implementation status.

## Change boundary

- MAY CHANGE: `work/roadmaps/legacy-recovery-reconciliation.md`, `work/roadmaps/README.md`, this task record, and a compact checkpoint note if needed.
- MUST NOT CHANGE: runtime behavior, canonical state, existing open PR implementation branches, `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`, `migration/FUTURE_IDEAS_BACKLOG.md`, or the existing master roadmap's subsystem design during this task.
- MAY CHANGE IF NECESSARY: the master roadmap only in a later follow-up after reconciliation evidence is independently reviewed.
- OPERATOR APPROVAL REQUIRED: destructive legacy deletion or any consequential architecture/policy change; neither is in scope here.

## Decision authority

- Owner may decide: planning taxonomy, status labels, dependency ordering, and where recovered items map to already-merged/current PR work when evidence is explicit.
- Owner must escalate: any proposed new authority store, policy semantics, destructive legacy action, or material conflict between current code and preserved design intent.

## Acceptance criteria

- [ ] Every major legacy-derived candidate already preserved in the audit/backlog is mapped to `MERGED`, `IN OPEN PR`, `NEXT`, `TRIGGERED/LATER`, `DO NOT REVIVE`, or `AUDIT REMAINS`.
- [ ] Current PR #20-#35 work is mapped to the recovered legacy capabilities it already satisfies or partially satisfies.
- [ ] The next implementation sequence is explicit and avoids building on unresolved authority/evidence prerequisites.
- [ ] The map explicitly preserves known rejected legacy directions, including the failed lexical claim-card retriever and duplicate control-plane architecture.
- [ ] The roadmap index points to the reconciliation map without making it active authority.

## Verification and evidence

- Verification: inspect current `main`, current open PR metadata/heads, source audit/backlog, and roadmap index; then re-fetch changed files from the branch and run PR CI if GitHub triggers it.
- Evidence to preserve: branch/PR link, current `main` SHA, current PR ranges/status, and the reconciliation matrix.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: documentation/planning only.
- Ordered procedure: recover current state -> reconcile existing work -> classify remaining items -> order next waves -> publish draft PR.
- Failure branches: if a legacy item cannot be mapped confidently, mark `AUDIT REMAINS/UNKNOWN`; do not invent a disposition.
- Rollback / recovery: planning branch can be abandoned without runtime effect.
- Security / privacy controls: do not copy raw sensitive legacy content; reference IDs/paths and summarized evidence only.
- External side effects: GitHub branch/draft PR only.
- Effort limit: stop once the reconciliation map and index are complete; do not implement feature work in this task.
- Approved reference: existing master roadmap and migration audit/backlog.

## Stop / escalate

Stop rather than guess if a recovered candidate appears to require a new source of authority, if current PR behavior materially conflicts with the preserved invariant, or if an unresolved legacy chain changes the critical path.

Escalate to: operator for architecture/authority decisions; parallel archaeology task for unresolved historical evidence.

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
- A second agent may independently mine unresolved legacy evidence but must not edit this roadmap during the parallel pass.

## Completion / handoff

- Completed: current state recovery and task shaping.
- Not completed: reconciliation map/index publication and independent review.
- Current blocker: none.
- Next action if not DONE: create the reconciliation map from verified current state and preserved legacy candidates.
