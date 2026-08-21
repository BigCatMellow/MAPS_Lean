# Task: Portable deployment D2a file-convention design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `agent/portable-deployment-d2a`
- Risk: `LOW`
- Goal: define the v1 file-convention shape for a target repository's `.maps/`
  directory, including task status vocabulary, directory layout, and
  best-effort review-evidence artifact shape.

## Inputs and source of truth

- VERIFIED: `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`
  D2a definition and Phase 1 boundaries.
- VERIFIED: `work/notes/2026-08-19-portable-deployment-operator-decisions.md`
  records v1 as file-convention-only, sibling-clone distribution,
  best-effort review discipline, stack-agnostic scope, and target-repo-owned
  `.maps/` state.
- VERIFIED: `templates/task.md`, `templates/review-evidence.md`, and
  `docs/CHECKS_AND_BALANCES.md` are the local MAPS patterns to adapt.
- UNKNOWN: the actual future target repository shape; D2a must not depend on
  access to it.

## Change boundary

- MAY CHANGE:
  - `work/notes/2026-08-20-roadmap-trajectory-check-5.md`
  - `work/notes/2026-08-20-portable-deployment-d2a-file-convention.md`
  - `templates/portable-deployment/target-task.md`
  - `templates/portable-deployment/target-review-evidence.md`
  - `templates/portable-deployment/target-roadmap.md`
  - `work/roadmaps/CAPABILITY_CHECKLIST.md`
  - `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`
  - this task doc
- MUST NOT CHANGE:
  - `runtime/`
  - `scripts/install_maps.sh`
  - any external repository
  - `.maps/state/`
- OPERATOR APPROVAL REQUIRED: actually running a pilot against an external
  repository, adding installer behavior, or changing the already-recorded v1
  operator decisions.

## Decision authority

- Owner may decide the Markdown convention details, template field names, and
  lightweight validation recommendations inside the file-convention-only v1
  boundary.
- Owner must escalate if D2a appears to require executable installer/adapter
  code, external repo access, CI enforcement, or a different v1 architecture.

## Acceptance criteria

- [x] A design note defines the target `.maps/` layout, status vocabulary,
      review-evidence shape, ownership rules, and non-goals.
- [x] Draft target task, review-evidence, and roadmap templates exist under
      `templates/portable-deployment/`.
- [x] The checklist and portable-deployment roadmap reflect D2a completion
      without marking D2b, D2c, D3, or 6.35 complete.
- [x] No runtime, installer, local `.maps/state/`, or external-repo files are
      changed.

## Verification and evidence

- Verification:
  - `git diff --stat`
  - `rg -n "D2a|6.35|target-task|target-review-evidence|target-roadmap" work/roadmaps work/notes templates/portable-deployment`
- Evidence to preserve: PR diff plus `work/reviews/pr-<N>-review-evidence.md`.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: MAPS_Lean planning repository only; target repos are
  represented by templates, not modified.
- Failure branches: if the convention cannot be defined without D2b adapter
  decisions, narrow D2a to the target-owned file layout and leave adapter calls
  out explicitly.
- External side effects: none.
- Approved reference: file-convention-only v1 decisions from
  `work/notes/2026-08-19-portable-deployment-operator-decisions.md`.

## Stop / escalate

Stop rather than guess if the work requires external target repository details,
an executable adapter, installer behavior, CI enforcement, or a change to the
operator's recorded v1 decisions.

Escalate to: operator for external-repo access or architecture decision changes;
research/design task for adapter behavior beyond D2a.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Completion / handoff

- Completed: D2a design note, draft templates, trajectory pass #5 note, and
  roadmap/checklist updates are ready for independent review.
- Not completed: updated independent review evidence and merge.
- Current blocker: PR #133 review requested explicit owner decision authority
  in the target task template and owner/owning-task tracking in the target
  roadmap template; both corrections have been applied.
- Next action if not DONE: obtain fresh independent review evidence at the
  corrected head.
