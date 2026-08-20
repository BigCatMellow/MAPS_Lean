# Task: portable deployment D2c Chain Shovel pilot plan

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `/root/d2c_chain_shovel_plan`
- Risk: `MEDIUM`
- Goal: define a target-specific, no-access plan for a later D3 pilot that
  moves the recorded Chain Shovel ES-module-split + logger bug through the
  portable-v1 file convention, implementation, independent review, and merge.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `docs/CHECKS_AND_BALANCES.md`, Roadmap 06, the
  capability checklist, D0/D1/D2a/D2b artifacts, portable target templates,
  and the 2026-08-19 operator decision record.
- Authoritative sources: the recorded portable-v1 decisions and Roadmap 06
  govern the pilot intent; D1 governs the two-root boundary; D2a governs
  target `.maps/` files; D2b governs a future adapter boundary.
- Evidence labels: `VERIFIED` for the listed MAPS_Lean documents; `REPORTED`
  for the pilot target and its bounded bug as recorded by the operator;
  `UNKNOWN` for Chain Shovel's checkout, source paths, reproduction, test
  commands, Git hosting/CI, branch policy, and reviewer availability.
- Dependencies / preconditions: D0, D1, D2a, and D2b are complete as designs.
  D3 additionally requires target-repository access and an AGI-ready target
  task after its preflight gates pass.

## Change boundary

- MAY CHANGE: this task record, the D2c plan note, and D2c/D3 evidence text in
  Roadmap 06 and the capability checklist.
- MUST NOT CHANGE: runtime code, installer code, adapter code, templates,
  tests, Chain Shovel, any external repository, and D3 execution status.
- MAY CHANGE IF NECESSARY: none; target-local `.maps/` initialization,
  implementation, tests, review, PR creation, and merge require D3's separate
  task and target authority.
- OPERATOR APPROVAL REQUIRED: target access, Chain Shovel writes or command
  execution, PR publication/merge, target CI/configuration changes, and any
  change to portable-v1 decisions.

## Decision authority

- Owner may decide: plan structure, preflight ordering, target file names, and
  documentation wording consistent with D1/D2a/D2b.
- Owner must escalate: target bug scope beyond the recorded ES-module-split +
  logger issue; target stack/test/CI assumptions; writes outside target
  `.maps/`; external side effects; reviewer/merge authority; and any adapter
  or installer implementation choice.

## Acceptance criteria

- [x] The plan preserves the recorded real pilot task while labeling unverified
  Chain Shovel details as preflight gates.
- [x] The plan names target-local `.maps/` files, ownership/review roles,
  allowed/refused actions, verification evidence, and a later D3 sequence.
- [x] The plan confines D2c to MAPS_Lean documentation and leaves D3 not
  started and blocked on target access plus a shaped execution task.
- [x] Only D2c/D3 tracking text changes in the two canonical roadmaps.

## Verification and evidence

- Verification: inspect cited predecessor designs/templates; run
  `git diff --check origin/main...HEAD`; run targeted status/path searches.
- Evidence to preserve: this task record, the D2c plan note, the roadmap and
  checklist diff, independent-review evidence, and the eventual D3 target PR
  and target-local review-evidence artifact.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: MAPS_Lean worktree only; no external target is
  accessed during D2c.
- Ordered procedure: preserve D1/D2a/D2b boundaries; write the D3 preflight
  plan; update only D2c/D3 tracking; verify the docs diff.
- Failure branches: if target facts would change bug scope or required action,
  leave them `UNKNOWN` and stop D3 preflight for operator/target-owner input.
- Rollback / recovery: revert this docs-only commit.
- Security / privacy controls: no target inspection, credentials, network,
  external writes, or implicit root discovery.
- External side effects: publication of this MAPS_Lean documentation PR only.
- Effort limit: one plan note; no target task, adapter, installer, or pilot
  implementation.
- Approved reference: Roadmap 06, D0/D1/D2a/D2b, portable templates, and the
  2026-08-19 operator decisions.

## Stop / escalate

Stop rather than guess if:

- Chain Shovel access, target root, bug reproduction, source scope, test
  command, hosting policy, or reviewer identity is unavailable or conflicts
  with this plan;
- D3 would need an unlisted write, target dependency/CI change, arbitrary
  command, or MAPS runtime/SQLite/hcom state; or
- implementation reveals the reported bug is not bounded as described.

Escalate to: the operator or target owner for access/authority/scope; a new
D3 target task for execution; a separately shaped implementation task for any
installer or adapter code.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- D2c completes a plan only. It neither verifies nor modifies Chain Shovel.
- A D3 task cannot inherit target access or merge authority from this plan.

## Completion / handoff

- Completed: D2c plan and its canonical status updates.
- Not completed: target preflight, adapter/installer implementation, target
  initialization, bug fix, review, PR, merge, and final pilot proof.
- Current blocker: independent review of this documentation change; D3 remains
  blocked on target access and a separately AGI-ready execution task.
- Next action: independently review this D2c documentation change; then await
  target access/authority before shaping D3.
