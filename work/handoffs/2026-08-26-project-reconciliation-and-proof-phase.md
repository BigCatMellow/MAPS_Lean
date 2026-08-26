# Handoff: project reconciliation and Proof Phase

- From: repository archaeology / reconciliation pass
- To: next MAPS_Lean worker
- Task: [reconcile-project-truth-20260826](../tasks/reconcile-project-truth-20260826.md)
- Status: `ACTIVE — reconciliation maintenance; architecture expansion frozen pending proof`
- Related durable records:
  - [Current state](../../state/CURRENT.md)
  - [Audit index](../audits/README.md)
  - [Proof Phase Audit & External Test Plan](../audits/2026-08-26-maps-proof-phase-audit-and-test-plan.md)
  - [Deep Project Archaeology Audit](../audits/2026-08-26-deep-project-archaeology-audit.md)
  - [Tenth-Seat review](../../playbook/TENTH_SEAT_REVIEW.md)
  - [Roadmap trajectory check](../../playbook/ROADMAP_TRAJECTORY_CHECK.md)
  - [Information lifecycle](../../playbook/INFORMATION_LIFECYCLE.md)
  - [Future Ideas Backlog](../../migration/FUTURE_IDEAS_BACKLOG.md)
  - [Capability checklist](../roadmaps/CAPABILITY_CHECKLIST.md)
  - [Portable deployment roadmap](../roadmaps/agent-harness-capabilities/06-portable-deployment.md)

## What is true now

- VERIFIED: the original audit/reconciliation baseline was
  `main@d22036bcebca3d7eb729c2b9dd70e82c229ac60a`, merging PR #172.
- VERIFIED: live `main` later advanced to
  `6c87d18d1d9980acac1b987cdee9e3aabc854260` through PR #175.
- VERIFIED: PR #171 is now merged. It landed Skill-lifecycle durable storage
  Half 1 only; Half 2 authority wiring remains separate and is not authorized by
  that merge.
- VERIFIED: PR #175 is now merged. Its independent review corrected material
  enforcement overstatement before merge; E6/6.16 remain `IN PROGRESS` and no
  runtime worktree enforcement was added.
- VERIFIED: PR #172 made resume-path validation production-invokable but
  deliberately advisory/inert for ordinary real runs because no production
  writer currently supplies run-bound environment evidence.
- VERIFIED: PR #173 is the open reconciliation/maintenance PR. Runtime-stack
  tests passed at its prior head; `review-evidence` failed because no
  `work/reviews/pr-173-review-evidence.md` exists yet. Independent review is the
  outstanding gate, not a runtime-test failure.
- VERIFIED: PR #174 is the bounded Spiderweb Audit stacked on #173. It remains a
  separate follow-up and should be retargeted/synchronized after #173 lands.
- VERIFIED: the Tenth-Seat protocol is an active playbook method. Trajectory
  checks #6 and #7 each found substantive issues, so a future clean check #8
  must evaluate Trigger 2 before treating the result as settled.
- VERIFIED: repository archaeology found substantial information/status drift:
  old notes can look unfinished after later implementation, and accepted review
  findings can survive only inside review/PR prose unless dispositioned.
- VERIFIED: the conversation-derived Proof Phase and archaeology findings are
  preserved under `work/audits/`, linked from this handoff and the roadmap
  index, and explicitly non-authoritative until shaped into work.
- ASSUMED / UNKNOWN: no claim is made here that every historical artifact has
  been fully reconciled. Live code, current checklist evidence, and GitHub state
  still win over historical prose.

## Work completed

- Added a repo-wide rule that forward-relevant durable information must connect
  to its source/parent/successor/evidence and should link instead of duplicate.
- Extended the existing information-lifecycle playbook with explicit
  capture→review→disposition→reconciliation guidance rather than creating a new
  memory/loose-ends subsystem.
- Connected `ROADMAP_TRAJECTORY_CHECK.md` back to the Tenth-Seat triggers.
- Tightened E/I guidance so promoted/rejected/superseded ideas preserve their
  later disposition through links.
- Updated core task, decision, AGI-check, and handoff templates with small
  relationship fields.
- Reconciled the current disposition of two ideas and two historical
  zero-production-caller insights without rewriting their original observations.
- Preserved PR #172 F3-F8 as explicit `TEST`/`WATCH`/`DEFERRED` dispositions
  with revisit triggers rather than silently converting them into tasks.
- Refreshed `state/CURRENT.md` and corrected clearly stale root/runtime README
  claims, including operational-learning, branch-protection, and RnS validation
  descriptions.
- Reconciled DEC-001 with current implementation while deliberately leaving its
  formal `PROPOSED` authority status unchanged.
- Preserved the Proof Phase and deep archaeology reports as linked durable audit
  records and added them to the roadmap planning path so their unresolved
  findings are revisited during Proof Phase/D3 rather than floating outside the
  program.
- Refreshed this handoff/current-state pair after PRs #171 and #175 merged so the
  reconciliation branch does not preserve already-stale live-state claims.

## Work not completed

- Independent review/review evidence for PR #173 has not been produced.
- External Proof Phase / D3 real-project pilot has not been run.
- Skill lifecycle Half 2 is not authorized by this handoff.
- Legacy deletion remains separately operator-gated.
- A full historical backlink retrofit is intentionally not being attempted.
- The capability checklist still needs a deliberate whole-file re-verification
  against current `main`; its header remains dated 2026-08-18 and some prose
  lags later merged work.
- Branch cleanup and hcom fork-pin removal require their own evidence checks;
  neither should be inferred from this handoff.
- The audit records are not a task queue: individual findings still require
  explicit shaping/disposition before implementation.

## Decisions and constraints

- Freeze new major capability families until external comparative evidence
  demonstrates a concrete need.
- Preserve history; reconcile current meaning. Do not rewrite old observations
  to pretend later outcomes were known at capture time.
- Prefer standard relative Markdown links over copied rationale. Backlinks may
  be derived; do not create a second mutable graph/authority store.
- Tenth-Seat review remains rare and trigger-based, not a CI gate or permanent
  contrarian role.
- Use the existing D3 external-pilot concept as the first real proof vehicle
  rather than inventing a duplicate pilot framework.
- The audit files are evidence/roadmap inputs. When an audit finding is reached,
  verify it against current `main` and shape only the smallest authorized work
  that evidence still supports.

## Current blocker / risk

- PR #173 needs a genuinely independent reviewer. The author/reconciliation
  session must not self-certify this substantive information-integrity change.
- Main is moving quickly; before the review is bound/finalized, synchronize the
  branch to current `main` and re-check any current-state claims rather than
  repeatedly rebinding evidence after every unrelated merge.
- External proof remains blocked until a real target repository/task and the
  necessary operator authority/access are explicitly selected.

## Working state

- Reconciliation branch: `maintenance/reconcile-project-truth-20260826`
- Original audit baseline: `d22036bcebca3d7eb729c2b9dd70e82c229ac60a`
- Live main at this refresh: `6c87d18d1d9980acac1b987cdee9e3aabc854260`
- Latest merged PR at this refresh: #175
- Open reconciliation PR: #173
- Stacked Spiderweb follow-up: #174

## Next action

1. Synchronize PR #173 with current `main` at the point its independent review
   begins, then obtain independent review/review evidence and normal checks.
2. After #173 lands, synchronize/retarget #174 and run its normal review/checks.
3. Run the first bounded Spiderweb scan and fresh-agent traversal test.
4. Reconcile the capability checklist from a complete current view.
5. Use the linked Proof Phase audit + archaeology audit as inputs to the
   external Proof Phase/D3 pilot rather than opening another broad internal
   capability wave.

## Do not redo / do not assume

- Do not recreate an additional loose-ends database: MAPS already has future
  ideas, E/I, decisions, trajectory checks, handoffs, audits, and the capability
  checklist. Reconcile these before adding another layer.
- Do not assume a dated `future task` note is still unfinished until checked
  against current code/checklist/merged PRs.
- Do not interpret `IN PROGRESS` as one homogeneous maturity state; distinguish
  design, implementation, tests, production reachability, real evidence input,
  and external proof when that distinction matters.
- Do not wire Skill Half 2, destructive-action enforcement, automatic recovery
  remediation, or other authority expansion merely to complete a roadmap shape.
- Do not remove the hcom fork pin merely because `HcomAdapter.send()` currently
  does not use `--json`; first prove no other live caller/contract still depends
  on the fork-specific behavior.

## Evidence / paths

- [Reconciliation maintenance task](../tasks/reconcile-project-truth-20260826.md)
- [Audit index](../audits/README.md)
- [Proof Phase Audit & External Test Plan](../audits/2026-08-26-maps-proof-phase-audit-and-test-plan.md)
- [Deep Project Archaeology Audit](../audits/2026-08-26-deep-project-archaeology-audit.md)
- [Agent operating contract](../../AGENTS.md)
- [Active playbook index](../../playbook/INDEX.md)
- [Information lifecycle](../../playbook/INFORMATION_LIFECYCLE.md)
- [Tenth-Seat protocol](../../playbook/TENTH_SEAT_REVIEW.md)
- [Roadmap trajectory check](../../playbook/ROADMAP_TRAJECTORY_CHECK.md)
- [E/I](../../playbook/EMERGENCE.md)
- [Current state](../../state/CURRENT.md)
- [Roadmap index](../roadmaps/README.md)
- [Capability checklist](../roadmaps/CAPABILITY_CHECKLIST.md)
- [PR #172 follow-up dispositions](../notes/2026-08-26-pr172-followup-dispositions.md)
- [Future Ideas Backlog](../../migration/FUTURE_IDEAS_BACKLOG.md)

## Continuation link

- Superseded by / next handoff: `none yet`

This handoff reports durable orientation only. Recover live PR/CI/task state via
`work/coordination/README.md` before acting.
