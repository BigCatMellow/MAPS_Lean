# Task: portable deployment D2b sibling-clone adapter design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `/root/d2b_adapter_design`
- Risk: `MEDIUM`
- Goal: define the Markdown-only contract for a thin, target-local adapter that makes the D2a file convention usable with an explicit sibling MAPS_Lean clone without crossing either repository's authority boundary.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `docs/CHECKS_AND_BALANCES.md`, `work/roadmaps/CAPABILITY_CHECKLIST.md`, `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`, `scripts/install_maps.sh`, the D0 audit, D1 installer-targeting design, D2a file-convention note, and `templates/portable-deployment/`.
- Authoritative sources: the recorded portable-v1 operator decisions and Roadmap 06 govern product intent; D1 governs the two-root installer boundary; D2a governs the target `.maps/` convention.
- Evidence labels: `VERIFIED` for inspected repository files; `REPORTED` for D0 findings not re-run here; `UNKNOWN` for any real target repository.
- Dependencies / preconditions: D0, D1, and D2a are complete; the five 2026-08-19 operator decisions are recorded.

## Change boundary

- MAY CHANGE: this task record, `work/notes/2026-08-20-portable-deployment-d2b-sibling-adapter-design.md`, and D2b evidence/status text in the portable-deployment roadmap and capability checklist.
- MUST NOT CHANGE: runtime code, `scripts/install_maps.sh`, portable templates, tests, external repositories, or D2c/D3 status/design.
- MAY CHANGE IF NECESSARY: none; any adapter implementation or target initialization requires a separately shaped task.
- OPERATOR APPROVAL REQUIRED: external target writes, target command/test execution, target selection, changing portable-v1 decisions, package/distribution changes, or adapter implementation.

## Decision authority

- Owner may decide: documentation structure and a narrow adapter contract consistent with D1/D2a.
- Owner must escalate: an adapter operation that writes outside target `.maps/`, invokes arbitrary commands, adds a target dependency/CI hook, shares MAPS runtime state, changes review authority, or requires external target access.

## Acceptance criteria

- [x] The design names explicit canonical `MAPS_CLONE_ROOT` and `TARGET_REPO_ROOT` inputs and preserves D1's MAPS/target root separation.
- [x] The design bounds target-local adapter operations, output paths, and optional checks to the D2a file convention.
- [x] The design states refusal conditions for ambiguous paths, cross-store writes, implicit control-plane state, arbitrary command execution, target test/readiness claims, and review/merge authority.
- [x] The design leaves implementation and target-selection/pilot execution to separate D2c/D3 work.
- [x] Only D2b tracking is updated; D2c and D3 remain `NOT STARTED`.

## Verification and evidence

- Verification: inspect D0/D1/D2a/current installer and target templates; run `git diff --check origin/main...HEAD`; run targeted `rg` for D2b and D2c/D3 status.
- Evidence to preserve: task record, design note, roadmap/checklist diff, and PR link.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: MAPS_Lean worktree only; no target repository is accessed.
- Ordered procedure: inspect predecessor designs; write the bounded contract; update D2b tracking only; verify documentation diff.
- Failure branches: if D1/D2a conflict materially, stop and escalate; if an adapter behavior needs unrecorded product intent, do not invent it.
- Rollback / recovery: revert the docs-only commit.
- Security / privacy controls: do not access target contents or credentials; reject ambiguous roots and authority-crossing operations in the design.
- External side effects: publication of a GitHub pull request only.
- Effort limit: one bounded design note; no adapter, installer, or pilot implementation.
- Approved reference: Roadmap 06, the D0/D1/D2a artifacts, and 2026-08-19 portable-deployment decisions.

## Stop / escalate

Stop rather than guess if:

- a required adapter action would mutate a target outside `.maps/` or MAPS_Lean state on behalf of a target;
- target support requires a non-Git root, implicit target discovery, or a runtime/SQLite/hcom state model not decided for v1;
- the work would require target tests, readiness claims, review approval, auto-merge, or external repository access.

Escalate to: the operator for scope/authority changes; D2c for target/task selection planning; a separately shaped implementation task for any adapter code.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This is an interface contract, not an executable adapter. It neither proves a target is prepared nor changes the current installer.
- D2a owns the target file shape. D2b only defines how a future target-local adapter may use that shape while consulting a sibling clone.

## Completion / handoff

- Completed: D2b design note and its canonical tracking updates.
- Not completed: adapter implementation, target initialization, target/task selection, pilot execution, independent review, and merge.
- Current blocker: independent review before merge.
- Next action if not DONE: obtain independent review of this documentation-only change.
