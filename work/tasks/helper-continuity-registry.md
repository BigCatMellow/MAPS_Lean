# Task: helper continuity registry

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: add the first task-scoped helper-continuity primitive: a durable
  metadata registry that can decide whether a prior helper session reference is
  reusable for the same task/project/helper purpose/context within TTL, without
  granting task authority or auto-resuming the helper.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `work/roadmaps/CAPABILITY_CHECKLIST.md` item 6.19,
  `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` section 6.19,
  `runtime/helpers/README.md`, `runtime/helpers/common.py`,
  `runtime/helpers/ollama.py`, `runtime/helpers/aider.py`, and
  `tests/test_bounded_helpers.py`.
- Authoritative sources: roadmap 6.19 governs reuse conditions; helper README
  governs authority limits; existing helper wrappers remain bounded helper
  lanes, not owners/reviewers/approvers.
- Evidence labels: `VERIFIED` for current one-shot helper wrappers and helper
  result store; `UNKNOWN` for provider-specific session health checks and real
  external helper session attachment.
- Dependencies / preconditions: bounded helper result records already exist.

## Change boundary

- MAY CHANGE: `runtime/helpers/common.py`, `runtime/helpers/README.md`,
  helper tests, this task file, and checklist 6.19 status/evidence text.
- MUST NOT CHANGE: task lifecycle authority, review/approval state, helper
  process launch semantics, Aider/Ollama command arguments, database schema,
  external provider sessions, and unrelated roadmap items.
- MAY CHANGE IF NECESSARY: `runtime/helpers/__init__.py` exports for the new
  registry types.
- OPERATOR APPROVAL REQUIRED: actual automatic helper resume/reuse, provider
  liveness integration, schema migration, or changes to helper write scope.

## Decision authority

- Owner may decide: JSON registry shape, deterministic reuse checks, TTL and
  context-key validation, and test coverage.
- Owner must escalate: auto-resuming helpers, treating continuity as task
  authority, provider-specific health checks, or broad helper workflow changes.

## Acceptance criteria

- [ ] A helper-continuity record can be registered for a task/project/helper
  purpose/session reference/context key with an expiry.
- [ ] Reuse is returned only for exact task, project, helper kind, purpose,
  context key, and unexpired TTL.
- [ ] Material task/context mismatch, expiry, or explicit invalidation returns
  non-reusable with an exact reason.
- [ ] The registry stores evidence metadata only and does not mutate task
  lifecycle, run manifests, reviews, or helper output files.
- [ ] Checklist 6.19 is updated from `NOT STARTED` to `IN PROGRESS` with the
  limitation that real provider health/auto-resume remains future work.

## Verification and evidence

- Verification: `git diff --check`; targeted helper continuity tests; existing
  bounded helper tests.
- Evidence to preserve: task file, checklist row, test output, and independent
  review evidence.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: local MAPS_Lean worktree only.
- Ordered procedure: add registry primitive; update docs; test exact reuse and
  fail-closed invalidation/expiry; update checklist.
- Failure branches: if reuse cannot be proven, return non-reusable rather than
  guessing.
- Rollback / recovery: revert implementation commit.
- Security / privacy controls: store opaque session references and context
  hashes/keys only; do not store prompts or helper output content.
- External side effects: GitHub PR publication only.
- Effort limit: registry primitive only; no automatic provider session resume.
- Approved reference: roadmap 6.19.

## Stop / escalate

Stop rather than guess if:

- helper health requires provider-specific network/process calls;
- task/context revision semantics need broader integration than a caller-owned
  context key;
- task authority, review authority, or output scope would change; or
- actual helper auto-resume is needed to satisfy acceptance.

Escalate to: operator for scope expansion; a separate provider-specific task
for real health checks or auto-resume.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`
