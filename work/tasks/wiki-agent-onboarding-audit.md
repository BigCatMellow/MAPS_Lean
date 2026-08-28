# Task: Wiki agent onboarding audit

- Status: `READY_FOR_REVIEW`
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
- Evidence labels: live wiki snapshot was VERIFIED through GitHub Actions; current repo files are VERIFIED from the active branch.
- Dependencies / preconditions: none remaining for implementation; independent review remains before merge.

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

- [x] Live wiki content is inventoried and compared against the current canonical repo contract.
- [x] Wiki has one obvious agent entry path that tells a fresh agent exactly what to read/do first.
- [x] Wiki explicitly states it is orientation/navigation, not a competing authority source; `AGENTS.md` is canonical for MAPS_Lean repository work.
- [x] Wiki explains the orchestration operator role, subordinate agent-slot relationship, autonomous continuation, and true human reauthorization boundary accurately.
- [x] Wiki gives a practical task flow from request → inspect → shape/AGI → route/delegate → execute → verify/review → reconcile → continue/complete.
- [x] Wiki distinguishes core MAPS_L concepts from optional/specialized mechanisms and avoids requiring broad chain-reading.
- [x] Stale or duplicate normative wiki material is consolidated, redirected, or removed.
- [x] Fresh-agent regression checks cover what MAPS_L is, authority, entry route, delegation/parent ownership, continuation, capability verification, and escalation.
- [ ] Repository-side canonical source/sync change receives required independent review and passes merge gates.

## Verification and evidence

- Live wiki snapshot workflow run: `33170349867` — SUCCESS.
- Final audited publish workflow run: `33171005727` — SUCCESS.
- Documentation guard result: 10/10 tests PASS before publication.
- Live wiki publication: wiki commit `79081be` (`68b640e..79081be`, 4 files changed, 534 insertions, 440 deletions).
- Temporary inspection/publish workflow removed after successful publication.
- Review required: `INDEPENDENT_REVIEW` before repository-side merge.

## Conditional execution rules

- Environment / target: public GitHub wiki for `BigCatMellow/MAPS_Lean` plus this repository.
- Ordered procedure: snapshot → audit → repair → smoke-test → publish → remove temporary machinery → independent review → merge canonical source/sync.
- Failure branches: direct wiki API access was unavailable; a bounded GitHub Actions snapshot/publish path was used successfully and then removed.
- Rollback / recovery: wiki content remains in wiki git history; repo-side changes remain isolated on `audit/wiki-agent-onboarding` pending review.
- Security / privacy controls: no secrets exposed; `GITHUB_TOKEN` used only inside Actions for wiki git access.
- External side effects: audited wiki documentation published; no product/runtime deployment.
- Effort limit: consolidated the existing four-page wiki rather than adding a larger parallel documentation system.
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

- The wiki is an onboarding projection, not normative authority.
- `docs/wiki/` is the reviewed source for the projection; `.github/workflows/sync-wiki.yml` publishes it after changes land on `main`.
- Capability status in the wiki points agents to live code/tests/checklist rather than freezing dated counts and audit snapshots.
- MAPS_L use is presented at three depths: method-only, orchestrated, runtime-backed. Agents should use the smallest depth that solves the coordination problem.

## Completion / handoff

- Completed: live wiki audit, rewrite, fresh-agent regression checks, live publication, durable repo-side source/sync implementation, temporary audit machinery cleanup.
- Not completed: independent review and merge of repository-side source/sync branch.
- Current blocker: required independent review for this MEDIUM-risk change.
- Next eligible roadmap task: independent review of `audit/wiki-agent-onboarding`, then merge if approved.
- Human action required: none unless a reviewer raises a true authority/scope question.
