# Task: portable-deployment roadmap design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `PLANNING`
- Owner: `design agent (FOUNDRY-style bootstrap task)`
- Risk: `LOW`
- Goal: produce a new, genuine roadmap document (following `templates/roadmap.md`'s
  shape) for a capability that does not exist in any of the five existing
  `work/roadmaps/agent-harness-capabilities/` sub-roadmaps: installing/targeting
  MAPS's control plane at an arbitrary external project's repository, not just
  MAPS_Lean itself, plus registering that new roadmap in the places other
  roadmaps are registered. This task produces documentation only — no runtime
  code.

## Inputs and source of truth

- Inputs: `docs/FRESH_INSTALL.md`, `scripts/install_maps.sh`,
  `playbook/CONTROL_PLANE.md`, `docs/CONTROL_PLANE_SETUP.md`,
  `docs/CHECKS_AND_BALANCES.md`, `scripts/check_review_evidence.py`,
  `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` §6, all five existing
  sub-roadmaps under `work/roadmaps/agent-harness-capabilities/`,
  `playbook/PROJECT_BOOTSTRAP.md`, `templates/roadmap.md`, `templates/task.md`.
- Authoritative sources: `playbook/PROJECT_BOOTSTRAP.md` for the bootstrap
  process this task follows; `templates/roadmap.md` for the document shape;
  the actual current state of `scripts/install_maps.sh` and the control-plane
  docs for what exists today (not assumptions about what exists).
- Evidence labels: facts about current `install_maps.sh`/control-plane
  behavior are `VERIFIED` (read directly from the scripts/docs); the claim
  that no existing sub-roadmap already covers this capability is `VERIFIED`
  by grepping `work/roadmaps/`, `docs/`, `playbook/` for
  `external project|other repo|another repo|target repo|target project|
  arbitrary project|foreign repo|non-MAPS|portable install` (zero hits) and
  by reading all 34 items of the master roadmap's §6 capability inventory and
  all five sub-roadmaps' phase lists directly.
- Dependencies / preconditions: none — this is a read/design task against the
  current repository state.

## Change boundary

- MAY CHANGE:
  - `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md` (new file)
  - `work/roadmaps/agent-harness-capabilities/README.md` (additive: new roadmap row)
  - `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` (additive: document map + new §6.35 entry)
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` (additive: new §6 for this roadmap's phases, renumbers the trailing master-inventory section from §6 to §7, adds one row for 6.35)
  - `playbook/INDEX.md` (additive: one new table row)
  - this task file
- MUST NOT CHANGE: any runtime code under `runtime/`; any existing roadmap's
  own content beyond additive references to the new roadmap; any active task,
  policy, or review state.
- MAY CHANGE IF NECESSARY: none.
- OPERATOR APPROVAL REQUIRED: none for this design task itself. The roadmap
  document this task produces explicitly records five open questions that
  **do** require operator decisions before any later implementation phase
  (`D2` onward) can start — see the roadmap's "Mission meeting → Operator
  decisions needed" section. This task does not resolve them.

## Decision authority

- Owner may decide: document structure/wording within `templates/roadmap.md`'s
  shape, phase numbering/letter-prefix choice (with stated reasoning),
  which files to touch for registration.
- Owner must escalate: any resolution of the five open design questions
  recorded in the roadmap (SQLite-vs-convention, distribution model,
  review-evidence portability, v1 language/stack scope, state location) —
  these are explicitly reserved for the operator, not this task.

## Acceptance criteria

- [x] A new roadmap document exists at
  `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`
  following `templates/roadmap.md`'s exact section shape (Current reality,
  Definition of DONE, Boundaries, Backward plan, Mission meeting, First wave,
  Phases, Checkpoints).
- [x] The roadmap's "Current reality" section is built from directly checked
  facts (with source paths cited), not assumptions.
- [x] The roadmap names a highest-risk unknown and records it as an open
  question requiring operator decision, rather than resolving it unilaterally.
- [x] A new, previously-unused phase-letter prefix is chosen with stated
  reasoning (`D`, confirmed unused by grepping existing phase IDs across all
  five sub-roadmaps and the checklist).
- [x] The roadmap is registered: a row in `playbook/INDEX.md`'s table, a
  reference in the master roadmap's document map and a new §6.35 capability
  inventory entry (both additive), and a new phase-status section in
  `work/roadmaps/CAPABILITY_CHECKLIST.md` with every phase marked NOT STARTED.
- [x] This task file itself exists documenting the design task.

## Verification and evidence

- Verification: manual read-through of the new roadmap against
  `templates/roadmap.md`'s section list (all present); manual diff review of
  the four registration edits confirming they are additive and do not alter
  existing roadmap content; re-grep of `work/roadmaps/`, `docs/`, `playbook/`
  for external-project-portability terms confirming no prior coverage existed
  before this PR.
- Evidence to preserve: the PR diff itself; the independent SENTINEL review's
  evidence file at `work/reviews/pr-<N>-review-evidence.md`.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: N/A (documentation only).
- Ordered procedure: N/A.
- Failure branches: N/A.
- Rollback / recovery: revert the PR if the independent reviewer finds the
  roadmap does not genuinely follow the template shape or silently resolves
  an open question it should have flagged instead.
- Security / privacy controls: N/A.
- External side effects: none — no runtime behavior changes.
- Effort limit: single bounded design task; if scope grows toward actually
  implementing any phase (`D0` onward), stop and shape a separate
  implementation task first.
- Approved reference: `templates/roadmap.md`, `playbook/PROJECT_BOOTSTRAP.md`.

## Stop / escalate

Stop rather than guess if:

- an existing sub-roadmap turns out to already cover this capability under
  different terminology (checked directly — not the case as of this task);
- the highest-risk unknown (SQLite-vs-convention for v1) seems to have an
  obviously correct answer — it does not; record it for the operator instead
  of resolving it.

Escalate to: operator, for the five recorded open questions.

## AGI readiness

- Fresh-Agent Test: `PASS` — the roadmap and this task file are self-contained
  with cited source paths; a fresh agent does not need this session's context.
- No-Guess Test: `PASS` — every "Current reality" claim cites a verified file/path.
- Scope Test: `PASS` — explicitly documentation-only; no runtime code touched.
- Authority Test: `PASS` — no policy/authority claim is made beyond documenting
  a planning artifact; open questions are explicitly deferred to the operator.
- Completion Test: `PASS` — acceptance criteria are concrete and checked above.
- Failure Test: `PASS` — stop/escalate conditions above are named.
- Continuation Test: `PASS` — the roadmap itself defines the next steps (D0/D1
  first wave) for any future agent picking this up.

## Notes / decisions

- Letter prefix `D` chosen for Deployment/Distribution after confirming
  `H`/`S`/`E`/`SEC`/`L` are the only phase-ID prefixes in active use (the
  apparent `F`/`T` hits found while grepping are metric labels — `F1` score,
  `T0`–`T3` trust tiers — not phase-ID prefixes).
- This roadmap deliberately does not resolve whether v1 needs a full SQLite
  port or a lighter file-convention-only discipline; that is recorded as the
  roadmap's highest-risk unknown and the first item under operator decisions
  needed.

## Completion / handoff

- Completed: roadmap document written and registered in all four required
  locations; this task file written.
- Not completed: none for this task's own scope. Implementation of any `D0`+
  phase is explicitly future work gated on operator decisions.
- Current blocker: none for this task. Future phases are blocked on the
  operator resolving the five recorded open questions.
- Next action if not DONE: N/A — task is complete pending independent review.
