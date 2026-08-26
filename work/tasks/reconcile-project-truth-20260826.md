# Task: Reconcile project truth and durable information links

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `MAINTENANCE`
- Owner: `operator-delegated reconciliation session`
- Risk: `MEDIUM`
- Goal: Make the active repository describe its current information/steering behavior more accurately and make forward-relevant durable records easier to follow across sessions, without adding runtime capabilities or changing authority.
- Related durable records:
  - [Current state](../../state/CURRENT.md)
  - [Audit index](../audits/README.md)
  - [Proof Phase Audit & External Test Plan](../audits/2026-08-26-maps-proof-phase-audit-and-test-plan.md)
  - [Deep Project Archaeology Audit](../audits/2026-08-26-deep-project-archaeology-audit.md)
  - [Roadmap index](../roadmaps/README.md)
  - [Information lifecycle](../../playbook/INFORMATION_LIFECYCLE.md)
  - [Tenth-Seat review](../../playbook/TENTH_SEAT_REVIEW.md)
  - [E/I](../../playbook/EMERGENCE.md)
  - [Current reconciliation handoff](../handoffs/2026-08-26-project-reconciliation-and-proof-phase.md)

## Inputs and source of truth

- Inputs: current `main` at task start (`d22036bcebca3d7eb729c2b9dd70e82c229ac60a`), active playbooks/templates, current GitHub PR/branch state, PR #172 review findings, current ideas/insights, repository archaeology findings, and the operator-requested durable Proof Phase/audit records.
- Authoritative sources: current merged runtime/code and active repository instructions; live GitHub state for PR/CI facts; current task/decision authority where applicable.
- Evidence labels: direct repository/GitHub inspection is `VERIFIED`; unresolved historical interpretation remains `UNKNOWN`/historical until reconciled.
- Dependencies / preconditions: user/operator explicitly requested the small reconciliation fixes and preservation/linking of the conversation-derived audits; no runtime implementation dependency.

## Change boundary

- MAY CHANGE: `AGENTS.md`; active information/review playbooks; task/decision/AGI/handoff templates; `state/CURRENT.md`; root/runtime README wording; forward-relevant current ideas/insights/decision annotations; reconciliation handoff/follow-up notes; `work/audits/` evidence/navigation; roadmap-index links that do not change capability status; this task record.
- MUST NOT CHANGE: runtime behavior, schemas, tests, capability status rows, Skill authority wiring, destructive-action enforcement, external systems, branch protection, `legacy/` contents/deletion, PR #171 implementation.
- MAY CHANGE IF NECESSARY: capability checklist wording only after a complete current view and explicit evidence; not included in this maintenance branch.
- OPERATOR APPROVAL REQUIRED: deletion, capability/status promotion, authority expansion, external/destructive action, or new subsystem.

## Decision authority

- Owner may decide: concise wording, relative link placement, non-authoritative disposition labels for already-observed ideas/review findings, correction of demonstrably stale README/orientation statements, and navigation links that place the audits on the existing roadmap/handoff path without making them authority.
- Owner must escalate: any change that promotes a capability/decision, changes runtime behavior, creates a new authority surface, deletes historical material, or expands scope beyond reconciliation/evidence preservation.

## Acceptance criteria

- [x] Tenth-Seat trigger ownership is reciprocally linked from the trajectory-check procedure.
- [x] Active instructions explicitly require forward-relevant durable information to remain connected and prefer links over copied rationale.
- [x] Information lifecycle distinguishes capture, review, disposition, and later reconciliation without introducing a second task/memory database.
- [x] Core durable templates provide small relationship/context fields rather than large new forms.
- [x] Selected stale idea/insight records preserve their original observation and add a current forward disposition.
- [x] PR #172 non-blocking findings F3-F8 have explicit dispositions/revisit triggers outside PR prose without becoming automatic tasks.
- [x] `state/CURRENT.md` and clear root/runtime README drift are refreshed against current evidence.
- [x] The Proof Phase and deep archaeology Markdown reports are preserved under `work/audits/`, link to current task/handoff/roadmap context, and are linked back from the roadmap/handoff so neither is an island.
- [x] The roadmap index explicitly preserves the audits as Proof Phase/D3 inputs without turning audit findings into automatic work.
- [x] No runtime code, schema, tests, capability status rows, or external/destructive behavior changed.
- [ ] Independent review confirms the reconciliation is accurate, proportionate, and does not create duplicate truth.

## Verification and evidence

- Verification: compare `main...maintenance/reconcile-project-truth-20260826`; inspect changed-file list for docs/state-only scope; inspect links/claims against current code/PR evidence; confirm the audit files have both incoming and outgoing durable links; required repository CI after PR opens.
- Evidence to preserve: PR diff, independent review evidence, required CI results, final merge/rejection outcome, and the two linked audit records.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: GitHub repository `BigCatMellow/MAPS_Lean`.
- Ordered procedure: inspect current evidence → make bounded reconciliation edits → preserve/link audit evidence → compare branch to `main` → independent review → merge only through existing gates.
- Failure branches: if a current claim cannot be verified from complete evidence, leave it unchanged and record it as a follow-up/revisit rather than guessing.
- Rollback / recovery: close/reject the maintenance PR; no runtime/database migration exists.
- Security / privacy controls: no secrets or private data; use public repo evidence only.
- External side effects: GitHub branch/PR writes only; no release/deploy/runtime side effects.
- Effort limit: do not turn this into a full historical backlink retrofit, second audit authority, or capability redesign.
- Approved reference: current repository operating contract and playbooks.

## Stop / escalate

Stop rather than guess if:

- a proposed correction would change capability or decision authority;
- a large current-status file cannot be read completely enough to edit safely;
- a historical record's present disposition cannot be established from current evidence;
- an audit finding would need runtime/capability work before being shaped into its own authorized task;
- a change would add another mutable source of truth rather than reconcile an existing one.

Escalate to: operator or a separately shaped research/maintenance task as appropriate.

## AGI readiness

- Fresh-Agent Test: `PASS` — task links the active context, audits, roadmap path, and exact maintenance boundary.
- No-Guess Test: `PASS` — uncertain status/capability changes are explicitly excluded.
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS` — current handoff and audit index preserve remaining work/non-goals.

## Notes / decisions

- Do not create `work/LOOSE_ENDS.md` or another graph/database in this pass; first use/reconcile the existing lifecycle surfaces.
- Use wiki-like connectivity through standard relative Markdown links; derive backlinks later only if evidence justifies tooling.
- The full `CAPABILITY_CHECKLIST.md` reconciliation remains separate because this connector view was truncated and the scoreboard must not be rewritten from a partial read.
- The deep archaeology audit is later than the initial Proof Phase plan and supersedes any conflicting specific diagnosis about whether historical work remains unfinished.
- Audit findings are evidence/planning inputs, not executable tasks. Reconcile each finding against current `main` when the roadmap reaches it.

## Completion / handoff

- Completed: implementation of the bounded documentation/information-lifecycle reconciliation on `maintenance/reconcile-project-truth-20260826`, including durable preservation and roadmap-linking of the two conversation-derived audit reports.
- Not completed: independent review/CI/merge; full capability-checklist reconciliation; external Proof Phase.
- Current blocker: independent review and normal PR gates.
- Next action if not DONE: obtain independent review, then use the linked audits as inputs to the external Proof Phase/D3 pilot.
- Resulting/superseding records: [current reconciliation handoff](../handoffs/2026-08-26-project-reconciliation-and-proof-phase.md), [audit index](../audits/README.md).
