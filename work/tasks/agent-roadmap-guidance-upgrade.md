# Task: Agent roadmap guidance upgrade

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `MAINTENANCE`
- Owner: TOWER / roadmap-guidance documentation lane
- Risk: `MEDIUM`
- Goal: preserve the existing role-specific roadmap guidance and replace the unmerged ATLAS draft with **TOWER — Planning / Dispatch / Coordination**, the operator-facing fifth coordination role.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `playbook/REQUEST_COMPILATION.md`, `playbook/AGI_STANDARD.md`, `playbook/TASK_LIFECYCLE.md`, `playbook/HPOM_ROUTING.md`, `playbook/ROADMAP_AND_PROJECTUPDATER.md`, `templates/roadmap.md`, `templates/task.md`, current coordination notes, and live GitHub state.
- Authoritative sources: operator statements for intent and priority; canonical MAPS task/project state for task truth; live GitHub for repository/PR/branch/review state; named MAPS playbooks for method.
- Evidence labels: direct repository/live reads are `VERIFIED` at the inspected ref; coordination notes are derived evidence only and may become stale.
- Dependencies / preconditions: documentation-only change; preserve active branch ownership; preserve SENTINEL review independence and SWITCHYARD integration control.

## Change boundary

- MAY CHANGE: this task; `work/coordination/agents/TOWER.md`; remove the unmerged `work/coordination/agents/ATLAS.md`; the existing roadmap-guidance additions in ANVIL/FOUNDRY/SENTINEL/SWITCHYARD; and PR #70 title/body metadata.
- MUST NOT CHANGE: runtime code, tests, schemas, canonical project roadmaps, MAPS policies/playbooks, unrelated tasks, other agents' active branches, review dispositions, or merge state.
- MAY CHANGE IF NECESSARY: none; additional repository paths require task amendment first.
- OPERATOR APPROVAL REQUIRED: any further permanent role-authority change or consequential authority not stated by the operator.

## Decision authority

- Owner may decide: wording and organization needed to faithfully encode the operator-defined TOWER role using existing MAPS methods.
- Owner must escalate: any conflict requiring takeover of another agent's branch/artifact, merge action, review approval, or modification of canonical MAPS methods.

## Acceptance criteria

- [x] ANVIL/FOUNDRY/SENTINEL/SWITCHYARD retain the role-specific roadmap guidance already added.
- [x] `TOWER.md` replaces the unmerged ATLAS identity so the intended permanent structure has five roles rather than six.
- [x] TOWER accepts operator requests, uses MAPS request compilation/AGI rules to shape bounded prompts/tasks, and builds/maintains MAPS roadmaps.
- [x] TOWER reads live `main`, roadmaps, tasks, PRs, reviews, dependencies, and coordination notes before making dispatch decisions.
- [x] TOWER maintains only a **derived** priority/dispatch view; it does not create a second task authority.
- [x] TOWER identifies blocked stacks and safe parallel work and routes only legitimately eligible unclaimed work to suitable agents under existing MAPS task/routing rules.
- [x] TOWER keeps roadmap progress aligned with verified task/repository evidence and surfaces only material operator decisions.
- [x] TOWER explicitly cannot merge, independently approve substantive review, rewrite another agent's branch, invent operator permission, override SENTINEL findings, override SWITCHYARD gates, or manufacture task truth.
- [x] The contract explicitly distinguishes: **TOWER decides the next eligible work to dispatch; SWITCHYARD decides what is safe to integrate next.**
- [x] FOUNDRY remains a development/runtime lane in the intended permanent architecture; incumbent planning work may finish under its existing owner without becoming permanent dispatch authority.
- [x] PR #70 remains documentation-only and requires independent review before integration.

## Verification and evidence

- Verification: fetched TOWER/task files; confirmed branch coordination directory contains ANVIL, FOUNDRY, SENTINEL, SWITCHYARD, and TOWER with no ATLAS file; compared branch against original base and current `main`; inspected changed paths and current live PR role state.
- Evidence to preserve: original-base compare shows exactly the four existing coordination files, new `TOWER.md`, and this task record; current-main compare shows the documentation branch has diverged because `main` advanced after branch creation.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Ordered procedure: amend this task -> add TOWER -> remove ATLAS -> verify exact delta -> update PR #70 -> return task to `READY_FOR_REVIEW`.
- Failure branches: if a target moves unexpectedly, re-fetch before writing; if another agent owns the same mutable output, stop and reconcile ownership; if role reconciliation would require modifying another agent's branch, leave that branch untouched and surface the conflict.
- Rollback / recovery: documentation revert/removal only; no runtime state affected.
- External side effects: GitHub documentation commits and PR #70 metadata only.
- Effort limit: do not create a new priority database/service or redesign the control plane.

## Stop / escalate

Stop rather than guess if canonical task state and live ownership materially disagree or if a proposed TOWER action would require authority outside planning/dispatch.

Escalate to: operator for intent/priority/consequential decisions; SENTINEL for independent review; SWITCHYARD for integration/merge safety.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- The operator first requested an operator-facing roadmap agent. ATLAS was an unmerged draft name in PR #70.
- The operator refined that role to **TOWER — Planning / Dispatch / Coordination** with responsibility for current priorities, dependencies, blocked stacks, safe parallel dispatch, roadmap synchronization, and surfacing genuine operator decisions.
- TOWER therefore replaces ATLAS rather than adding a sixth permanent agent.
- The operator's intended permanent flow places ANVIL and FOUNDRY as development lanes, SENTINEL as independent review, and SWITCHYARD as integration/merge control.
- Live `main` is `7269ce2be25993fa19b172f65c95381328585a35`, advanced after PR #70's original base `146f092a63af63b0fd750445e584a39e82ea1442`; current-main comparison is diverged and final integration must re-resolve current-main state.
- Open PR #68 still proposes a permanent FOUNDRY Planning / Control-Surface transition. That is inconsistent with the newer operator-defined TOWER architecture; this branch reports the conflict but does not rewrite #68.
- PR #71 remains incumbent FOUNDRY-authored planning/reconciliation work and can finish under existing ownership without creating permanent dispatch authority.

## Completion / handoff

- Completed: four-agent roadmap guidance; TOWER planning/dispatch identity; ATLAS removal; exact documentation-scope verification.
- Not completed: PR #70 metadata refresh, independent review, current-main reconciliation, and integration.
- Current blocker: no documentation blocker; PR #70 is not currently integration-ready because `main` advanced and independent review is still required.
- Next action if not DONE: refresh PR #70 description/title with the TOWER architecture and hand the exact head to independent review/SWITCHYARD without self-approving or merging.
