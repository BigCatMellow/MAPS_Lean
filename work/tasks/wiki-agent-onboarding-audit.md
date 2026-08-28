# Task: Wiki agent onboarding audit

- Status: `READY`
- AGI status: `AGI READY`
- Type: `REPAIR`
- Owner: orchestration operator
- Risk: `MEDIUM`
- Goal: A fresh capable agent pointed only to the MAPS_L GitHub wiki can reliably discover the canonical repository contract, understand its orchestration role, select the right MAPS_L workflow, use the active runtime/control plane appropriately, and continue work without treating wiki prose as competing authority.
- Parent roadmap: user-authorized MAPS_L documentation/operability repair in this conversation
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: live GitHub wiki, `AGENTS.md`, `docs/FIRST_RUN.md`, `README.md`, `playbook/INDEX.md`, active runtime/control-plane documentation, current tests/CI.
- Authoritative sources: `AGENTS.md` first, then approved scope/task, canonical runtime state, then subordinate playbook/docs. Wiki is onboarding/navigation only.
- Evidence labels: wiki content must be inspected from the live wiki repository; current repo files are VERIFIED from the active branch.
- Dependencies / preconditions: obtain a readable snapshot of the separate GitHub wiki repository.

## Change boundary

- MAY CHANGE: wiki onboarding/navigation pages; repo-side wiki synchronization/audit support if needed; this task record; tests that prevent wiki/onboarding drift; directly related README/FIRST_RUN/index links if a contradiction is found.
- MUST NOT CHANGE: runtime behavior, unrelated playbooks, application architecture, unrelated roadmap scope.
- MAY CHANGE IF NECESSARY: a small repo-side canonical wiki source or synchronization mechanism if that is the least-complex durable way to prevent wiki drift.
- HUMAN REAUTHORIZATION REQUIRED: none for bounded documentation/onboarding repair; any unrelated product/runtime expansion.

## Decision authority

- Inherited roadmap authority: audit and repair MAPS_L wiki/onboarding so agents can use the system effectively.
- Owner may decide: page structure, navigation, consolidation, cross-links, derived-vs-authoritative wording, drift guards, and the smallest durable synchronization mechanism.
- Resolve internally first: stale wiki text, duplicated rules, unclear agent entry sequence, terminology collisions, runtime-vs-method distinctions.
- Human escalation only if: the repair would materially redefine MAPS_L objectives or authority rather than document current approved behavior.

## Acceptance criteria

- [ ] Live wiki content is inventoried and compared against the current canonical repo contract.
- [ ] Wiki has one obvious agent entry path that tells a fresh agent exactly what to read/do first.
- [ ] Wiki explicitly states it is orientation/navigation, not a competing authority source; `AGENTS.md` is canonical.
- [ ] Wiki explains the orchestration operator role, subordinate agent-slot relationship, autonomous continuation, and true human reauthorization boundary accurately.
- [ ] Wiki gives a practical task flow from request → inspect → shape/AGI → route/delegate → execute → verify/review → reconcile → continue/complete.
- [ ] Wiki distinguishes core MAPS_L concepts from optional/specialized mechanisms and avoids requiring broad chain-reading.
- [ ] Stale or duplicate normative wiki material is consolidated, redirected, or removed.
- [ ] A fresh-agent smoke check can answer: what MAPS_L is, what authority applies, what to read, how to start, how to delegate, how to know DONE, and what to do next.
- [ ] Changes pass relevant repo CI/review requirements.

## Verification and evidence

- Verification: snapshot live wiki; compare page-by-page against canonical files; run documentation regression tests; inspect final rendered/wiki source structure; independent review of agent-onboarding usability.
- Evidence to preserve: wiki inventory/audit findings, diff, test results, review evidence.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: public GitHub wiki for `BigCatMellow/MAPS_Lean` plus this repository.
- Ordered procedure: snapshot → audit → repair → smoke-test → independent review → publish/sync → verify.
- Failure branches: if direct wiki access is unavailable to the current connector, use a bounded GitHub Actions snapshot/publish path and remove temporary inspection-only machinery afterward.
- Rollback / recovery: wiki content remains in git history; repo-side changes via branch/PR.
- Security / privacy controls: no secrets; use `GITHUB_TOKEN` only inside Actions if wiki git access is required.
- External side effects: publishing wiki documentation; no external product deployment.
- Effort limit: consolidate rather than proliferate pages; do not create a parallel wiki constitution.
- Approved reference: current `AGENTS.md` and canonical first-run/playbook docs.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- The wiki should teach agents how to enter and use MAPS_L, while linking to canonical repo sources for normative detail.

## Completion / handoff

- Completed: none yet
- Not completed: live wiki snapshot, audit, repair, review, publication
- Current blocker: none; live wiki can be inspected through a bounded Actions snapshot if direct API access is unavailable
- Next eligible roadmap task: live wiki inventory
- Human action required: none
