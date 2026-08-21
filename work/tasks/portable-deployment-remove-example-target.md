# Task: remove example target from portable deployment plan

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: correct the portable deployment plan so Chain Shovel is not treated as
  a selected pilot target; the first real external pilot target/task must be
  selected later by explicit operator decision.

## Inputs and source of truth

- Inputs: operator correction on 2026-08-21: "Remove Chain Shovel from the
  plan, it was an example"; current portable deployment roadmap/checklist;
  D1/D2a/D2b design boundaries; existing D2c plan artifacts.
- Authoritative source: the 2026-08-21 operator correction supersedes prior
  plan text that treated Chain Shovel as selected.
- Evidence labels: `VERIFIED` for current repository references found with
  `rg`; `SUPERSEDED` for earlier Chain Shovel-as-target planning text.
- Dependencies / preconditions: D0/D1/D2a/D2b remain valid; D2c must be
  reframed without naming a target.

## Change boundary

- MAY CHANGE: active portable deployment task/note/roadmap/checklist/handoff
  documents that treated Chain Shovel as the pilot target; this task record.
- MUST NOT CHANGE: runtime code, templates, tests, review-evidence provenance,
  external repositories, or the core D0/D1/D2a/D2b design decisions.
- MAY CHANGE IF NECESSARY: file names for the D2c task/note so active evidence
  no longer names the example target.
- OPERATOR APPROVAL REQUIRED: selecting any concrete pilot target/task or
  executing D3.

## Decision authority

- Owner may decide: wording and file names needed to remove the example target
  from active plan state.
- Owner must escalate: any new concrete target selection, external access, D3
  execution, or changes to the five portable-v1 architecture decisions.

## Acceptance criteria

- [x] Active roadmap/checklist state no longer says Chain Shovel is selected.
- [x] D2c is reframed as a generic target-selection and pilot-planning gate,
  not a concrete target plan.
- [x] D3 remains `NOT STARTED` and blocked on explicit target/task selection,
  target access/authority, and an AGI-ready execution task.
- [x] Historical review evidence may remain as provenance, but active plan
  references must not route future agents toward Chain Shovel.

## Verification and evidence

- Verification: `git diff --check`; targeted `rg` for active Chain Shovel
  references after the correction.
- Evidence to preserve: this task, corrected D2c note/task, roadmap/checklist
  diff, and handoff correction.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: MAPS_Lean docs only; no external target repository.
- Ordered procedure: identify active references; replace selected-target
  language with explicit later target-selection gates; verify no active plan
  target remains.
- Failure branches: if a path is historical review evidence, leave it as
  provenance rather than rewriting review history.
- Rollback / recovery: revert this docs-only correction commit.
- Security / privacy controls: no external repository inspection.
- External side effects: publication of a MAPS_Lean PR only.
- Effort limit: do not redesign portable deployment beyond removing the
  incorrect concrete example target.
- Approved reference: the 2026-08-21 operator correction.

## Stop / escalate

Stop rather than guess if correcting the plan requires selecting a replacement
target, target task, reviewer, hosting policy, or D3 execution authority.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Chain Shovel was an example, not an authorized pilot target.
- The first real external pilot remains required for 6.35 but is unselected.
