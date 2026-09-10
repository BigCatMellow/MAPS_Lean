# Task: Freeze symlink escape rejection in run scopes

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `MAINTENANCE`
- Owner: `competitor-borrow integration lane`
- Risk: `LOW`
- Goal: Preserve a deterministic regression proving that an apparently in-repo writable path cannot escape the repository through a filesystem symlink.
- Parent roadmap: `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md` + `04-agentic-security.md`
- Related records: `work/notes/2026-09-09-competitor-borrow-integration-log.md`; Pilot DSH sandbox/path-enforcement packet at `BigCatMellow/Pilot_Projects@f6d584465e15b0fcf3cd09fea9e056bc23852e94`
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: `runtime/state/integrity.py::_repo_relative`, existing run-manifest scope tests, DSH/Pilot sandbox containment evidence.
- Authoritative sources: current MAPS_L run-scope semantics; external material is evidence only.
- Evidence labels: realpath-based containment implementation `VERIFIED`; absence of a symlink-escape regression in the inspected execution-integrity suite `VERIFIED`.
- Dependencies / preconditions: current platform must support filesystem symlinks in CI; no runtime behavior change allowed in this slice.

## Change boundary

- MAY CHANGE: one focused test file; this task record; rolling competitor-borrow process note.
- MUST NOT CHANGE: runtime/security implementation, schemas, capability status, active PR #319–#325 files, sandbox architecture.
- MAY CHANGE IF NECESSARY: test arrangement only.
- HUMAN REAUTHORIZATION REQUIRED: any proposal to introduce or change sandbox/containment authority rather than preserve current resolved-path behavior.

## Decision authority

- Inherited roadmap authority: test existing scope-containment behavior.
- Owner may decide: fixture shape and public-surface assertions.
- Resolve internally first: whether to exercise private helper or public run-manifest path; prefer public behavior.
- Human escalation only if: current behavior permits the symlink escape and fixing it requires a semantic/authority change.

## Acceptance criteria

- [x] Public run-manifest path is used rather than testing a private helper in isolation.
- [x] Test creates an in-repo symlink whose resolved target is outside the repo.
- [x] `create_run_manifest()` rejects the writable scope as `INVALID_SCOPE`.
- [x] Failure explains that the path escapes the repository root.
- [x] No run record is created on the failed scope request.
- [x] No runtime/schema/status change.
- [ ] Exact-head CI passes.
- [ ] Independent review confirms this tests existing containment and does not overclaim sandbox isolation.

## Verification and evidence

- Verification: `python -m unittest tests.test_scope_symlink_containment`; repository Runtime stack tests.
- Evidence to preserve: test diff, CI, independent review, process-log disposition.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: Linux GitHub CI / normal MAPS Python runtime; test uses a local temporary symlink.
- Ordered procedure: inspect current path normalization → confirm missing regression → add public-path test → CI → independent review.
- Failure branches: IF current behavior allows escape THEN stop this test-hardening slice and route the runtime gap through Harness/Security owners.
- Rollback / recovery: remove test if unsupported platform behavior makes it invalid; do not weaken containment to satisfy the test.
- Security / privacy controls: no secrets/network/external data.
- External side effects: none beyond GitHub branch/CI.
- Effort limit: one path-containment regression; no sandbox subsystem.
- Approved reference: DSH/Pilot `P0-SANDBOX-PATH-ENFORCEMENT.md` semantics.
- Operational independence: `REQUIRED`
- Reproduction package: repository + `python -m unittest tests.test_scope_symlink_containment`.

## Stop / escalate

Stop if this requires runtime edits, platform-specific production behavior, or changes the meaning of current scope authority.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This borrows only the invariant “authorize the resolved filesystem target, not lexical path text.” It does not import DSH's sandbox backend or claim that MAPS has process/network/credential isolation.

## Completion / handoff

- Completed: current implementation audit; focused regression added.
- Not completed: exact-head CI and independent review.
- Triage capture: `none — no §2 trigger fired`
- Reproduction package: run the focused unittest and inspect that `trace_task(task_id)["runs"]` remains empty after rejection.
- Current blocker: review/CI only.
- Next eligible roadmap task: continue competitor-derived test audit outside active PR surfaces.
- Human action required: `none`
