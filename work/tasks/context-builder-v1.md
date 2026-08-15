# Task: Context Builder v1

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT`
- Risk: `MEDIUM`
- Goal: Produce a small, read-only context plan from explicit task relationships
  and active repository authority so an agent can see what it should read
  without semantic retrieval or repository-wide context dumping.

## Inputs and source of truth

- Inputs: canonical task contract, root `AGENTS.md` when present, explicit task
  `inputs`/`sources`/dependencies, repository files referenced exactly.
- Authoritative sources: SQLite task contract and current bytes at exact paths.
- Evidence labels: explicit references/hashes `VERIFIED`; descriptive references
  remain references; missing/outside-repo paths are surfaced, never guessed.
- Dependencies / preconditions: task exists; repo root exists.

## Change boundary

- MAY CHANGE: `runtime/context_builder.py`, `runtime/cli.py`,
  `runtime/README.md`, `tests/test_context_builder.py`, review packet, this task.
- MUST NOT CHANGE: task state, policy, routing, review, outcomes, repository files
  referenced by the context plan.
- MAY CHANGE IF NECESSARY: none without task amendment.
- OPERATOR APPROVAL REQUIRED: none.

## Decision authority

- Owner may decide: compact output structure and safe path classification.
- Owner must escalate: semantic/vector retrieval, generated knowledge graphs,
  automatic policy inference, or context mutation/caching as canonical state.

## Acceptance criteria

- [x] Context plan is read-only and derived from canonical task state/current
  files.
- [x] Root `AGENTS.md` is included as active authority when it exists.
- [x] Explicit task input/source files include exact repo-relative paths, SHA-256,
  size, role, and existence status.
- [x] Descriptive/non-file references are preserved without pretending they are
  files.
- [x] Missing, directory, and outside-repo references are explicit.
- [x] Dependency state and task boundaries/acceptance criteria are included
  without copying unrelated repository content.
- [x] Output explicitly states that semantic retrieval is not used.
- [x] CLI/tests cover exact files, references, missing/outside paths,
  dependencies, non-inclusion of unrelated files, and no mutation.

## Verification and evidence

- Verification: pull-request CI plus focused tests.
- Evidence to preserve: Runtime stack tests run `31886431884` passed every job
  step with `tests/test_context_builder.py` present.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: Python 3.12, repository filesystem, SQLite task store.
- Ordered procedure: explicit task state → safe path resolution → file hashes →
  compact derived plan.
- Failure branches: outside-repo paths are reported and never opened; unknown
  references remain references; missing files are reported.
- Rollback / recovery: revert implementation; no schema/state migration.
- Security / privacy controls: do not include file contents in v1; only path,
  size/hash, role, and task metadata.
- External side effects: GitHub branch/PR only.
- Effort limit: no embeddings, semantic index, claim-card retriever, cache, or
  knowledge graph.
- Approved reference: preserved Context Builder evidence and corrected EXP-0006
  findings.

## Stop / escalate

Stop if usefulness requires guessing relationships not represented in canonical
state or explicit repository authority.

Escalate to: operator.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- v1 is deliberately a context **plan**: it identifies trustworthy inputs to
  read; it does not dump file contents into another stored representation.
- Future semantic supplementation must earn itself through paraphrase/hard-
  negative evaluation rather than being assumed necessary.

## Completion / handoff

- Completed: explicit context-plan builder, CLI, tests, docs, and CI validation.
- Not completed: independent review.
- Current blocker: none.
- Next action if not DONE: review the queued packet and current PR revision.
