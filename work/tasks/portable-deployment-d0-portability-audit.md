# Task: portable deployment D0 portability audit

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `RESEARCH`
- Owner: `/root`
- Risk: `LOW`
- Goal: produce a written audit of the `scripts/install_maps.sh` / `runtime.smoke` surface that classifies the runtime modules it touches for external-project portability.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `playbook/PROGRAM_STEERING.md`, `playbook/ROADMAP_TRAJECTORY_CHECK.md`, `work/roadmaps/CAPABILITY_CHECKLIST.md`, `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`, `scripts/install_maps.sh`, `runtime/smoke.py`, and directly imported runtime modules.
- Authoritative sources: current `main` code and merged roadmap/operator-decision notes win over handoff prose when they conflict.
- Evidence labels: `VERIFIED` for inspected code and commands in this task; `REPORTED` for handoff statements; `UNKNOWN` where a target external repository has not yet been inspected.
- Dependencies / preconditions: PRs #131 and #132 merged; operator decisions for portable deployment recorded in `work/notes/2026-08-19-portable-deployment-operator-decisions.md`.

## Change boundary

- MAY CHANGE: `work/tasks/portable-deployment-d0-portability-audit.md`, `work/notes/2026-08-20-portable-deployment-d0-portability-audit.md`, `work/notes/2026-08-20-roadmap-trajectory-check-4.md`, `work/roadmaps/CAPABILITY_CHECKLIST.md`, and D0 status text in `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`.
- MUST NOT CHANGE: runtime code, installer behavior, tests, external repositories, PR #132 history, and any Chain Shovel files.
- MAY CHANGE IF NECESSARY: none.
- OPERATOR APPROVAL REQUIRED: executing the Chain Shovel pilot or mutating any external project.

## Decision authority

- Owner may decide: audit wording, classification boundaries, and proportional verification for this docs-only research task.
- Owner must escalate: any change that implements installer behavior, changes target-project state conventions, or touches an external repository.

## Acceptance criteria

- [x] Audit identifies the installer shell surface and the mandatory/optional `runtime.smoke` runtime import surfaces.
- [x] Each touched runtime surface is classified as `Python-stdlib-portable`, `path-relative to MAPS_Lean only`, or `needs a real interface boundary before another repo could import it`.
- [x] Audit records concrete findings that should shape D1/D2a/D2b.
- [x] Checklist and roadmap D0 status are updated without marking D1/D2+ complete.

## Verification and evidence

- Verification: inspect source files, run import-surface checks, run docs-focused tests for smoke/install docs, and run the review-evidence checker after the PR number is known.
- Evidence to preserve: this task file, the audit note, trajectory note, PR diff, and independent review evidence.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: local MAPS_Lean repository only.
- Ordered procedure: inspect current main before editing; write audit; update status; obtain independent review before merge.
- Failure branches: if inspection finds D0 already done elsewhere, stop and update status only with evidence.
- Rollback / recovery: revert the docs-only PR.
- Security / privacy controls: do not inspect or mutate Chain Shovel or other external repositories.
- External side effects: GitHub PR publication only.
- Effort limit: one bounded audit; no implementation.
- Approved reference: Roadmap 06 D0 definition.

## Stop / escalate

Stop rather than guess if:

- a classification depends on running inside Chain Shovel or another external repo;
- the audit would require changing installer/runtime behavior;
- a target-project convention decision beyond the recorded operator decisions is needed.

Escalate to: operator for external-project access or new product/authority decisions.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task deliberately performs D0 only. D1 and D2a-D2c remain future design work.

## Completion / handoff

- Completed: portability audit written; D0 status updated.
- Not completed: independent review and merge.
- Current blocker: review/PR publication.
- Next action if not DONE: open PR and dispatch independent review.
