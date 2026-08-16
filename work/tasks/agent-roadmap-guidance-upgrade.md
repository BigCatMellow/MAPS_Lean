# Task: Agent roadmap guidance upgrade

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `MAINTENANCE`
- Owner: `TOWER / roadmap-guidance documentation lane`
- Risk: `MEDIUM`
- Goal: establish **TOWER — Planning / Dispatch / Coordination** as the operator-facing fifth coordination role and preserve role-specific roadmap participation guidance through a shared coordination document without modifying another agent's owner-controlled status file.

## Inputs and source of truth

- Inputs:
  - `AGENTS.md`;
  - `work/coordination/README.md`;
  - `playbook/REQUEST_COMPILATION.md`;
  - `playbook/AGI_STANDARD.md`;
  - `playbook/TASK_LIFECYCLE.md`;
  - `playbook/HPOM_ROUTING.md`;
  - `playbook/ROADMAP_AND_PROJECTUPDATER.md`;
  - `templates/roadmap.md`;
  - `templates/task.md`;
  - current coordination notes and live GitHub state;
  - SENTINEL review findings on PR #70.
- Authoritative sources: operator statements for intent/role architecture; live GitHub for repository/PR/branch/review state; canonical MAPS task/project state for task truth; named MAPS playbooks for method.
- Evidence labels: direct repository/live reads are `VERIFIED` at the inspected ref; coordination notes and PR bodies are derived evidence that may become stale.
- Dependencies / preconditions: documentation-only repair; preserve per-agent coordination-file ownership, SENTINEL independence, and SWITCHYARD integration control.

## Change boundary

- MAY CHANGE:
  - `work/coordination/agents/TOWER.md`;
  - `work/coordination/ROADMAP_PARTICIPATION.md`;
  - `work/tasks/agent-roadmap-guidance-upgrade.md`;
  - PR #70 title/body metadata and coordination comments.
- MUST NOT CHANGE:
  - `work/coordination/agents/ANVIL.md` relative to PR #70's branch base;
  - `work/coordination/agents/FOUNDRY.md` relative to PR #70's branch base;
  - `work/coordination/agents/SENTINEL.md` relative to PR #70's branch base;
  - `work/coordination/agents/SWITCHYARD.md` relative to PR #70's branch base;
  - runtime code, tests, schemas, policies, canonical project roadmaps, unrelated tasks, other agents' branches, review dispositions, or merge state.
- MAY CHANGE IF NECESSARY: none; additional repository paths require task amendment first.
- OPERATOR APPROVAL REQUIRED: any further permanent role-authority change or consequential authority not stated by the operator.

## Decision authority

- Owner may decide: wording and organization needed to encode the operator-defined TOWER role and project shared roadmap-participation guidance without creating a parallel authority system.
- Owner must escalate: any conflict requiring takeover of another agent's branch/artifact, merge action, independent review approval, or modification of canonical MAPS methods.

## Acceptance criteria

- [x] `TOWER.md` defines TOWER as Planning / Dispatch / Coordination and preserves the separation: **TOWER decides the next eligible work to dispatch; SWITCHYARD decides what is safe to integrate next.**
- [x] TOWER accepts operator requests, shapes bounded MAPS prompts/tasks, builds/maintains roadmaps, reasons about dependencies/priority, dispatches only eligible work, and surfaces material operator decisions.
- [x] TOWER explicitly cannot merge, independently approve work requiring independent review, rewrite another agent's branch without a valid handoff, invent operator permission, override SENTINEL, override SWITCHYARD, or manufacture canonical task truth.
- [x] Shared role-specific roadmap guidance exists in `work/coordination/ROADMAP_PARTICIPATION.md` and links back to the canonical MAPS roadmap method/template.
- [x] Shared guidance explicitly defines evidence-testing as looking for source evidence that could show a claim is wrong, incomplete, or unsupported, and explicitly prohibits altering/inventing/suppressing/manufacturing evidence.
- [x] Shared guidance records the permanent operator-defined role split: TOWER planning/dispatch; ANVIL + FOUNDRY development; SENTINEL independent review; SWITCHYARD integration/merge.
- [x] Incumbent FOUNDRY-authored planning work may finish or hand off without creating permanent FOUNDRY dispatch authority.
- [x] PR #70 no longer has a diff in ANVIL/FOUNDRY/SENTINEL/SWITCHYARD owner-controlled status files relative to its branch base.
- [x] PR #70 remains documentation-only and requires independent review before integration.

## Verification and evidence

- Verification:
  - recovered live `main` before repair;
  - re-read PR #68, #70, and #72 state;
  - re-read SENTINEL's two PR #70 review dispositions;
  - restored the four owner-controlled coordination files to the exact blobs present at PR #70's branch base;
  - moved the useful role-specific guidance into a shared coordination document;
  - preserved TOWER as the fifth role and kept ATLAS absent;
  - exact compare must show only `TOWER.md`, `ROADMAP_PARTICIPATION.md`, and this task record relative to the original PR base.
- Evidence to preserve: original base SHA, repaired head SHA, exact changed-file list, independent re-review disposition, and later SWITCHYARD current-main integration evidence.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Ordered procedure:
  1. recover live state/review findings;
  2. restore owner-controlled files to branch-base content;
  3. add shared roadmap-participation guidance;
  4. update this task and PR metadata;
  5. verify exact branch delta;
  6. request independent re-review;
  7. if clean, hand to SWITCHYARD for current-main reconciliation/integration.
- Failure branches:
  - IF PR #70 head moves unexpectedly before a write THEN stop and re-resolve ownership;
  - IF final compare still contains another agent's owner-controlled status file THEN repair the branch before review;
  - IF newer operator intent conflicts with this role split THEN stop and update the task rather than guessing;
  - IF synchronization to current main would require integration work THEN hand to SWITCHYARD rather than performing it from TOWER.
- Rollback / recovery: documentation revert/removal only; no runtime state is affected.
- External side effects: GitHub documentation commits, PR metadata, and coordination comments only.
- Effort limit: do not create a new priority database/service or redesign the control plane.

## Stop / escalate

Stop rather than guess if canonical task state/live ownership materially disagree or if a proposed TOWER action requires authority outside planning/dispatch.

Escalate to: operator for intent/priority/consequential decisions; SENTINEL for independent review; SWITCHYARD for current-main synchronization/integration/merge safety.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- The initial roadmap-guidance delivery edited all four other agents' owner-controlled coordination notes. SENTINEL correctly returned that as a HIGH coordination-authority/concurrency defect.
- The repair keeps the useful guidance but relocates it to a shared coordination document, so each agent's status note remains owned by that agent.
- The operator's newer architecture supersedes the earlier proposal to make FOUNDRY the permanent planning/control-surface lane. Permanent planning/dispatch now belongs to TOWER; FOUNDRY remains a development/runtime lane. Existing FOUNDRY planning work such as PR #71 may finish under incumbent ownership.
- Open PR #68 still contains the older permanent FOUNDRY planning transition and must be reconciled by its owner before integration; TOWER will not rewrite that branch.
- PR #72 is a separate dated TOWER dispatch/roadmap packet and does not replace this durable role/guidance change.

## Completion / handoff

- Completed: TOWER identity; shared roadmap-participation guidance; removal of cross-owner status-file changes from the intended final delta; task/authority repair.
- Not completed: exact repaired-head independent re-review, current-main reconciliation, and integration.
- Current blocker: independent review required on the repaired exact head; after that SWITCHYARD must synchronize/reconcile against then-current `main`.
- Next action if not DONE: verify the exact repaired delta, update PR #70 metadata, notify #68 of the superseding role decision, then hand PR #70 to independent re-review.
