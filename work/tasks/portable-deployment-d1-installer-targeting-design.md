# Task: portable deployment D1 installer targeting design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `/root/d1_installer_design`
- Risk: `LOW`
- Goal: define a Markdown-only, explicit `--target-repo <path>` contract for a successor or extension of `scripts/install_maps.sh` that separates MAPS_Lean setup from external target-repo state.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `docs/CHECKS_AND_BALANCES.md`, `playbook/PROGRAM_STEERING.md`, `work/roadmaps/CAPABILITY_CHECKLIST.md`, `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`, `scripts/install_maps.sh`, `work/notes/2026-08-20-portable-deployment-d0-portability-audit.md`, `work/notes/2026-08-20-portable-deployment-d2a-file-convention.md`, and `templates/portable-deployment/`.
- Authoritative sources: current roadmap and recorded operator decisions govern portable-v1 intent; D0's inspected installer findings govern current behavior; D2a governs target `.maps/` shape.
- Evidence labels: `VERIFIED` for directly inspected repository sources; `REPORTED` for the D0 audit's recorded source findings; `UNKNOWN` for any real external target repository, which this task does not inspect.
- Dependencies / preconditions: D0 is `DONE`; the 2026-08-19 operator decisions and D2a file-convention design are complete.

## Change boundary

- MAY CHANGE: this task record, `work/notes/2026-08-20-portable-deployment-d1-installer-targeting-design.md`, `work/roadmaps/CAPABILITY_CHECKLIST.md`, and D1 status text in `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`.
- MUST NOT CHANGE: `scripts/install_maps.sh`, runtime code, templates, tests, external repositories, or D2b/D2c/D3 status or design.
- MAY CHANGE IF NECESSARY: none; a new installer or adapter implementation requires a separate task.
- OPERATOR APPROVAL REQUIRED: mutating an external target repository, selecting a target-project pilot, changing the portable-v1 decisions, or implementing the described interface.

## Decision authority

- Owner may decide: the documentation structure, exact refusal/error contract, and proportional docs-only verification consistent with D0/D2a and the recorded decisions.
- Owner must escalate: new target state beyond `.maps/`, non-Git target support, package/distribution changes, installer implementation, and any external target-repo action.

## Acceptance criteria

- [x] A design note specifies `--target-repo <path>` parsing, canonical-root validation, and the separate MAPS and target roots.
- [x] The note specifies preview/apply behavior, allowed target writes, and required refusals that prevent writes to MAPS_Lean state when a target is supplied.
- [x] The note distinguishes MAPS-clone health checks from target-repository preparation and leaves hcom/LangGraph optional and MAPS-side.
- [x] The note consumes D0/D2a without defining D2b/D2c/D3 or changing runtime/installer code.
- [x] The capability checklist and Roadmap 06 mark D1 `DONE` only; D2b/D2c/D3 remain not started.

## Verification and evidence

- Verification: inspect the cited D0/D2a sources and current installer; run `git diff --check`; run targeted `rg` for D1 and `6.35` status/evidence references.
- Evidence to preserve: task record, design note, roadmap/checklist diff, and PR link.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: MAPS_Lean worktree only; no external target repository is accessed.
- Ordered procedure: read D0/D2a/current installer; write the design; update D1 tracking only; verify docs diff.
- Failure branches: if D0/D2a conflict materially, stop and escalate; if target behavior requires an unrecorded product decision, do not invent it.
- Rollback / recovery: revert the docs-only commit.
- Security / privacy controls: do not access target-repo contents or credentials; the design must reject unsafe root ambiguity.
- External side effects: publication of a GitHub pull request only.
- Effort limit: one bounded design note; no implementation or target pilot.
- Approved reference: Roadmap 06 D1 definition, D0 audit, D2a file convention, and 2026-08-19 operator decisions.

## Stop / escalate

Stop rather than guess if:

- a required action would change a target repository outside `.maps/`;
- a target must be supported without a Git worktree or beyond the recorded sibling-clone model;
- the design would require an installer/runtime/template edit or resolve D2b/D2c choices.

Escalate to: the operator for new portability scope or external-target authority; a separately shaped D2b task for adapter implementation details.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This closes a roadmap-traceable design gap; it does not document already-shipped targeting behavior. The current installer has no `--target-repo` support.
- D2a is an input because its target-owned `.maps/` shape constrains D1's allowed target writes. D2b/D2c/D3 remain separate, unstarted work.

## Completion / handoff

- Completed: D1 design and only its canonical roadmap/checklist status updates.
- Not completed: installer/adapter implementation, target-repo initialization, Chain Shovel planning, pilot, review, and merge.
- Current blocker: independent review before merge.
- Next action if not DONE: obtain independent review of this documentation-only PR.
