# Task: TOWER current dispatch — 2026-08-16

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `TOWER`
- Risk: `MEDIUM`
- Goal: Create a shared, evidence-backed multi-agent dispatch packet and working roadmap that tells each active MAPS lane what to do next, what to wait for, and what evidence must exist before downstream work resumes, without changing canonical task/review/merge authority.

## Inputs and source of truth

- Inputs:
  - live `main` and open PR state recovered on 2026-08-16;
  - `work/coordination/README.md`;
  - `work/coordination/agents/ANVIL.md`;
  - `work/coordination/agents/FOUNDRY.md`;
  - `work/coordination/agents/SENTINEL.md`;
  - `work/coordination/agents/SWITCHYARD.md`;
  - `playbook/ROADMAP_AND_PROJECTUPDATER.md`;
  - `templates/roadmap.md`;
  - `templates/task.md`;
  - live PR evidence for #30, #39, #44, #48, #68, and #70 plus their known downstream stacks.
- Authoritative sources: live GitHub state and accepted MAPS state win over this task, the roadmap, the dispatch note, coordination snapshots, and chat summaries.
- Evidence labels:
  - `VERIFIED` = directly re-read from current GitHub/repository evidence while shaping this packet;
  - `REPORTED` = stated in an owner/review/integration record but not independently reproduced by TOWER here;
  - `UNKNOWN` = not safely established and must be resolved by the assigned lane rather than guessed.
- Dependencies / preconditions: none for writing the planning packet. Execution of individual dispatch items remains subject to each existing task/PR's own dependencies and authority gates.

## Change boundary

- MAY CHANGE:
  - `work/tasks/tower-current-dispatch-2026-08-16.md`;
  - `work/roadmaps/tower-current-dispatch-2026-08-16.md`;
  - `work/coordination/agents/TOWER-DISPATCH-2026-08-16.md`;
  - top-level coordination comments on relevant existing PR threads that point owners/reviewers/integrators to this derived dispatch packet.
- MUST NOT CHANGE:
  - existing owner-controlled files `work/coordination/agents/ANVIL.md`, `FOUNDRY.md`, `SENTINEL.md`, or `SWITCHYARD.md`;
  - runtime, tests, schemas, policies, feature branches, existing task records, or existing roadmaps;
  - canonical task lifecycle, branch ownership, review disposition, merge order, or merge state;
  - SENTINEL findings or SWITCHYARD integration gates.
- MAY CHANGE IF NECESSARY: this task/roadmap/dispatch packet only, after re-reading live state. Any additional repository path requires task amendment first.
- OPERATOR APPROVAL REQUIRED: any material change to project priority, role architecture, scope, or consequential authority not already explicit in the operator request or accepted repository rules.

## Decision authority

- Owner may decide: derived `NOW / NEXT / BLOCKED / PARKED` ordering from verified dependencies; which existing lane should receive a coordination request; how to word stop/resume conditions; how to structure the roadmap and dispatch packet.
- Owner must escalate: conflicting canonical ownership, a requested priority change that materially changes operator intent, unresolved authority, or evidence showing the proposed role/dispatch architecture conflicts with accepted policy and cannot be reconciled without an operator decision.

## Acceptance criteria

- [x] A shared dated dispatch note exists beside the agent files and gives ANVIL, FOUNDRY, SENTINEL, SWITCHYARD, and TOWER explicit next actions, dependencies, hold conditions, resume conditions, required evidence, and handoff destinations.
- [x] A MAPS-format working roadmap records current reality, observable DONE, final proof, boundaries, backward plan, mission-meeting results, first wave, dependencies, checkpoints, and re-plan triggers.
- [x] The first wave prioritizes review/integration gates that unblock multiple downstream PRs rather than creating new speculative implementation work.
- [x] The packet never treats TOWER's queue as canonical task/review/merge truth and never grants TOWER merge or independent-review authority.
- [x] Existing owner-controlled agent notes are not modified.
- [x] Final `main -> branch` delta contains only the three new planning/coordination Markdown files listed above.

## Verification and evidence

- Verification:
  - live `main` re-read immediately before final verification and remained `7269ce2be25993fa19b172f65c95381328585a35`;
  - target root PRs were re-read while shaping: #30 `7bae6d5758619a391c7551ee4589ea2d80d0a5b8`, #44 `6f2b774eee27a0596820b12f080bfd7e60c0f50e`, #39 live `5928abe4550dbf7a75c2a2825e3cda5033ead830`, #48 `2f23959afff9525beada28993bad536878310b7f`;
  - `main -> coord/tower-dispatch-20260816` compare was ahead-only, merge base exactly current `main`, and contained exactly the three declared new Markdown files;
  - independent review is still required for factual freshness, dependency correctness, hidden authority, and unsafe parallelism before integration.
- Evidence to preserve: exact `main` SHA, exact branch head, changed-file list, PR links/heads cited in the roadmap, and review disposition.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: GitHub repository coordination/planning only.
- Ordered procedure:
  1. recover live state;
  2. build dependency graph;
  3. write shared dispatch packet;
  4. write working roadmap;
  5. verify exact delta;
  6. notify relevant PR threads without changing feature branches;
  7. hand packet to independent review.
- Failure branches:
  - IF `main` or a load-bearing target PR head moves during authoring THEN re-read the moved state and update affected dispatch facts before final verification;
  - IF a claimed dependency cannot be verified THEN mark it `UNKNOWN` and assign inspection rather than inventing order;
  - IF a dispatch action conflicts with a canonical task owner/status THEN canonical task state wins and TOWER updates the derived queue.
- Rollback / recovery: delete/revert only this branch's three planning files if the packet is rejected; no feature/runtime rollback is in scope.
- Security / privacy controls: do not copy secrets or private external content into coordination notes; preserve bounded repository evidence only.
- External side effects: GitHub branch, planning files, PR, and coordination comments only; no deployment, merge, release, or external send beyond repository coordination.
- Effort limit: if two or more first-wave target heads move before the packet is reviewed, refresh the first-wave evidence instead of continuing from stale facts.
- Approved reference: `playbook/ROADMAP_AND_PROJECTUPDATER.md`, `templates/roadmap.md`, `templates/task.md`, and `work/coordination/README.md`.

## Stop / escalate

Stop rather than guess if:

- live ownership conflicts with the dispatch target;
- exact review/CI state is materially ambiguous;
- an agent would need to modify another owner's branch/file without a valid handoff;
- execution would require TOWER to merge, independently approve, or suppress a review finding;
- operator intent changes the priority or role architecture materially.

Escalate to: operator for material intent/role/priority decisions; SENTINEL for independent review questions; SWITCHYARD for integration safety/merge gating.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- The operator explicitly requested TOWER to place messages beside the agent files telling each agent what to do next and to roadmap the work under MAPS protocols.
- The shared dispatch file is intentionally separate from each owner's status file to comply with `work/coordination/README.md`.
- This task does not depend on PR #70 being integrated; PR #70's TOWER-role/roadmap-guidance work remains a separate open coordination change with its own review findings.

## Completion / handoff

- Completed: shared dispatch note, MAPS working roadmap, task contract, live-state refresh, and exact three-file delta verification.
- Not completed: PR-thread notifications, independent review, and integration of this coordination packet.
- Current blocker: independent review is required before integration.
- Next action if not DONE: open the coordination PR, notify relevant PR threads with links to the dispatch packet, then hand the exact head to independent review.