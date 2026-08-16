# Task: Harness foundation Wave 1

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: establish the smallest provider-neutral harness contract needed for later adapters, hooks, lineage, and security work without creating new task authority or provider behavior.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md`, `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md`, existing runtime communication/helper/recovery code and tests.
- Authoritative sources: active repository instructions and current merged runtime behavior win; roadmaps provide planning intent only.
- Evidence labels: current `main` at merge commit `086e066f723d793273441dd52b500e62ac981deb` is VERIFIED baseline.
- Dependencies / preconditions: PR #19 merged to `main`; existing runtime CI available.

## Change boundary

- MAY CHANGE: `runtime/harness/**`, `tests/test_harness_types.py`, this task file, and narrowly necessary runtime documentation if implementation requires it.
- MUST NOT CHANGE: task-state schema/authority, hcom behavior, RnS behavior, helper behavior, routing behavior, policy semantics, review semantics, provider processes, deployment/external systems.
- MAY CHANGE IF NECESSARY: existing runtime modules only after explicit task amendment supported by a demonstrated integration requirement.
- OPERATOR APPROVAL REQUIRED: destructive/external behavior or material expansion beyond the typed contract.

## Decision authority

- Owner may decide: Python type shapes, validation details, serialization shape, module/package organization, and test implementation consistent with the approved roadmaps.
- Owner must escalate: any choice that creates new task authority, mutable canonical state, provider side effects, new dependencies, or changes existing runtime behavior.

## Acceptance criteria

- [x] `OperationResult` v1 explicitly distinguishes success/failure, mutation/read, complete/partial, evidence references, continuation, operation ID, and repeat-safety knowledge.
- [x] Provider-neutral session/binding/status types exist and preserve `UNKNOWN` rather than inferring missing state.
- [x] A narrow adapter protocol defines planned lifecycle operations without implementing provider behavior.
- [x] Harness contract does not depend on `TaskStore` or create a second authority store.
- [x] New unit tests pass and the repository Runtime stack CI remains green.
- [ ] Changes receive independent review before completion.

## Verification and evidence

- Verification: PR-triggered full Runtime stack CI run `31893719145` passed on code commit `5d408fc4c9fef165da3478e86bab3bd964470429`.
- Evidence to preserve: GitHub Actions run `31893719145`, PR #20 diff, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: existing MAPS Lean Python runtime.
- Ordered procedure: types/result envelope → protocol → unit tests → CI → independent review.
- Failure branches: IF the contract requires changing existing provider/task behavior THEN stop and re-shape rather than widening this tranche.
- Rollback / recovery: revert the isolated harness-package commit/PR; no schema/data migration is introduced.
- Security / privacy controls: no secrets, credentials, raw provider logs, or new external calls; types must not imply authority.
- External side effects: Git branch/PR publication only.
- Effort limit: one narrow Wave 1 foundation tranche; adapters and hooks are follow-up tasks.
- Approved reference: master roadmap + Harness Mechanics roadmap.

## Stop / escalate

Stop rather than guess if:

- an existing canonical source must be duplicated;
- lifecycle semantics require provider-specific assumptions;
- the adapter protocol cannot remain authority-neutral;
- CI exposes an incompatibility requiring changes outside the declared boundary.

Escalate to: operator / roadmap re-shaping as appropriate.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Keep scope/policy canonical: `ExecutionBinding` references task/run/revision/context/environment identity but does not copy writable scope or policy state.
- `UNKNOWN` is first-class for session/recovery uncertainty.
- This tranche deliberately does not implement hcom/helper adapters or Hooks yet.

## Completion / handoff

- Completed: typed harness foundation, focused unit coverage, full Runtime stack CI on the code commit.
- Not completed: independent review / merge.
- Current blocker: independent review required by the task contract.
- Next action if not DONE: independent review of PR #20; then resolve findings or merge if approved.
