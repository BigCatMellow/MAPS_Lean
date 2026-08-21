# Task: portable deployment D2c first external pilot selection plan

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `/root/remove_chain_shovel_example`
- Risk: `MEDIUM`
- Goal: define a no-access plan for selecting and later running the first real
  external D3 pilot through the portable-v1 file convention, implementation,
  independent review, and merge, without treating any example target as
  selected.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `docs/CHECKS_AND_BALANCES.md`, Roadmap 06, the
  capability checklist, D0/D1/D2a/D2b artifacts, portable target templates,
  the 2026-08-19 portable-v1 architecture decisions, and the 2026-08-21
  operator correction that the previously named target was only an example.
- Authoritative sources: the 2026-08-21 operator correction governs target
  selection; Roadmap 06 governs the pilot proof; D1 governs the two-root
  boundary; D2a governs target `.maps/` files; D2b governs a future adapter
  boundary.
- Evidence labels: `VERIFIED` for the listed MAPS_Lean documents; `UNKNOWN`
  for the actual target repository, task, checkout, source paths,
  reproduction, test commands, Git hosting/CI, branch policy, and reviewer
  availability.
- Dependencies / preconditions: D0, D1, D2a, and D2b are complete as designs.
  D3 additionally requires explicit target/task selection, target-repository
  access, and an AGI-ready target task after its preflight gates pass.

## Change boundary

- MAY CHANGE: this task record, the D2c selection/preflight plan note, and
  D2c/D3 evidence text in Roadmap 06 and the capability checklist.
- MUST NOT CHANGE: runtime code, installer code, adapter code, templates,
  tests, any external repository, and D3 execution status.
- MAY CHANGE IF NECESSARY: none; target-local `.maps/` initialization,
  implementation, tests, review, PR creation, and merge require D3's separate
  task and target authority.
- OPERATOR APPROVAL REQUIRED: selecting a concrete pilot target/task, target
  access, target writes or command execution, PR publication/merge, target
  CI/configuration changes, and any change to portable-v1 decisions.

## Decision authority

- Owner may decide: plan structure, preflight ordering, generic target file
  classes, and documentation wording consistent with D1/D2a/D2b and the
  operator correction.
- Owner must escalate: target selection; target stack/test/CI assumptions;
  writes outside target `.maps/`; external side effects; reviewer/merge
  authority; and any adapter or installer implementation choice.

## Acceptance criteria

- [x] The plan states that no pilot target is selected and any prior named
  target was only an example.
- [x] The plan names generic target-local `.maps/` file classes,
  ownership/review roles, allowed/refused actions, verification evidence, and
  a later D3 sequence.
- [x] The plan confines D2c to MAPS_Lean documentation and leaves D3 not
  started and blocked on target/task selection, target access, and a shaped
  execution task.
- [x] Only D2c/D3 tracking text changes in the two canonical roadmaps.

## Verification and evidence

- Verification: inspect cited predecessor designs/templates; run
  `git diff --check`; run targeted status/path searches.
- Evidence to preserve: this task record, the D2c plan note, the roadmap and
  checklist diff, independent-review evidence, and the eventual D3 target PR
  and target-local review-evidence artifact.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: MAPS_Lean worktree only; no external target is
  accessed during D2c.
- Ordered procedure: preserve D1/D2a/D2b boundaries; write the D3 target/task
  selection and preflight plan; update only D2c/D3 tracking; verify the docs
  diff.
- Failure branches: if target facts would be needed, leave them `UNKNOWN` and
  stop D3 preflight for operator/target-owner input.
- Rollback / recovery: revert this docs-only commit.
- Security / privacy controls: no target inspection, credentials, network,
  external writes, or implicit root discovery.
- External side effects: publication of this MAPS_Lean documentation PR only.
- Effort limit: one plan note; no target task, adapter, installer, or pilot
  implementation.
- Approved reference: Roadmap 06, D0/D1/D2a/D2b, portable templates, and the
  2026-08-21 operator correction.

## Stop / escalate

Stop rather than guess if:

- target selection, target root, task reproduction, source scope, test
  command, hosting policy, or reviewer identity is unavailable;
- D3 would need an unlisted write, target dependency/CI change, arbitrary
  command, or MAPS runtime/SQLite/hcom state; or
- implementation would require selecting a replacement target in this task.

Escalate to: the operator or target owner for target/task selection,
access/authority/scope; a new D3 target task for execution; a separately
shaped implementation task for any installer or adapter code.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- D2c completes a plan only. It neither selects, verifies, nor modifies an
  external target.
- A D3 task cannot inherit target access or merge authority from this plan.

## Completion / handoff

- Completed: D2c selection/preflight plan and its canonical status updates.
- Not completed: target/task selection, target preflight, adapter/installer
  implementation, target initialization, target change, review, PR, merge, and
  final pilot proof.
- Current blocker: independent review of this documentation change; D3 remains
  blocked on target/task selection, target access, and a separately AGI-ready
  execution task.
- Next action: independently review this D2c documentation correction; then
  await explicit target/task selection and authority before shaping D3.
