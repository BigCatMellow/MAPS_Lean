# Task: local EnvironmentFingerprint and compatibility v1

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: stack bounded local environment inspection and explicit compatibility semantics on EnvironmentSpec v1 without adding run binding, environment mutation, containers, or recovery authority.

## Inputs and source of truth

- Inputs: `AGENTS.md`, PR #28 / `agent/environment-spec-wave2`, `work/roadmaps/agent-harness-capabilities/03-environment-and-reproducibility.md` E2.
- Authoritative sources: active repository instructions and observed local facts win; EnvironmentSpec defines requirements; fingerprint/compatibility output is evidence, not task authority.
- Dependencies / preconditions: verified EnvironmentSpec implementation with full Runtime stack CI `31897492718`.

## Change boundary

- MAY CHANGE: `runtime/environment/fingerprint.py`, `runtime/environment/__init__.py`, focused fingerprint/compatibility tests, this task file.
- MUST NOT CHANGE: task/run schema, Harness/recovery behavior, setup/validation execution, CI workflow, containers/sandboxes/worktrees, external systems.
- MAY CHANGE IF NECESSARY: E2 observation/compatibility representation within this narrow tranche.
- OPERATOR APPROVAL REQUIRED: environment mutation, run binding, credential values, external network actions, destructive cleanup, or material scope expansion.

## Decision authority

- Owner may decide: bounded local read-only probes, observation states, fingerprint identity fields/hash, narrow version-constraint evaluation, compatibility precedence, explicit reason codes, and tests consistent with the roadmap.
- Owner must escalate: any design requiring secret values, arbitrary environment dumps, executing setup commands, or treating fingerprint compatibility as task permission.

## Acceptance criteria

- [x] fingerprint is bound to exact EnvironmentSpec hash and records only bounded execution facts: runtime/tool versions, repo revision, dirty state, dependency hashes, network mode/domains, declared service availability, and declared credential-capability availability.
- [x] fingerprint does not record absolute repo path, arbitrary environment variables, provider transcripts, or secret values.
- [x] credential capability availability is supplied explicitly as `true` / `false` / unknown; inspector does not inspect `os.environ` for secret values or assume capability names are environment variables.
- [x] runtime/tool observation distinguishes `OBSERVED`, `MISSING`, and `UNKNOWN`.
- [x] local version probing and Git inspection are read-only; setup/validation commands are not executed.
- [x] fingerprint stable SHA-256 excludes observation timestamp so identical observed facts have identical identity.
- [x] v1 runtime constraint evaluator supports plain numeric prefixes plus numeric `< <= > >= ==` clauses and returns unknown for unsupported syntax.
- [x] compatibility states are explicit: `COMPATIBLE`, `COMPATIBLE_WITH_WARNINGS`, `DRIFTED`, `INCOMPATIBLE`, `UNKNOWN`.
- [x] missing required runtime/tool/service/credential/network capability is incompatible.
- [x] unknown material evidence remains unknown rather than silently compatible.
- [x] dirty required worktree, spec mismatch, repo/reference change, or dependency-input change is surfaced as drift.
- [x] compatible-but-different runtime/tool versions and broader-than-required network can be warnings rather than false incompatibility where requirements still hold.
- [x] optional reference fingerprint can compare replacement/recovery environment facts without becoming authority.
- [x] focused tests and full Runtime stack CI pass.
- [ ] independent review remains required before completion.

## Verification and evidence

- Verification: PR-triggered full Runtime stack CI run `31897745175` passed on implementation commit `6d639380fe3683745611dc0092edb0ec9b30414a`.
- Evidence to preserve: GitHub Actions run `31897745175`, PR #29 diff, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: local MAPS Lean workspace only for E2.
- Ordered procedure: define bounded observations → fingerprint hash → compatibility evaluator → focused tests → stacked draft PR → full CI → independent review.
- Failure branches: IF a fact cannot be inspected safely/reliably THEN represent it as `UNKNOWN`; IF environment setup/mutation is needed THEN stop and defer to a later authorized setup lifecycle tranche.
- Rollback / recovery: revert isolated stacked commit/PR; no schema/data migration.
- Security / privacy controls: no environment dump, no secret values, only declared capability availability, no absolute repo path in fingerprint, no arbitrary shell commands.
- External side effects: Git branch/PR publication only; read-only version/Git probes when inspector is explicitly called.
- Effort limit: E2 fingerprint/compatibility only; no E3 run binding.
- Approved reference: Environment & Reproducibility roadmap E2.

## Stop / escalate

Stop rather than guess if:

- compatibility requires interpreting unsupported package/version syntax;
- credential capability cannot be represented without a value;
- an environment fact would need to widen task/policy authority;
- E2 starts growing into sandbox/container/recovery orchestration.

Escalate to: operator / roadmap re-shaping as appropriate.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task stacks on verified PR #28 and may continue before independent review because the dependency is explicit.
- `UNKNOWN` is first-class and intentionally conservative. The inspector never converts missing evidence into compatibility.
- Fingerprint identity excludes `observed_at`; timestamp remains audit metadata while stable facts determine the fingerprint hash.
- Secret requirements are treated as capabilities, not environment-variable names. Availability must be supplied by a trusted caller/broker and only boolean/unknown state is retained.
- Reference comparison is evidence for equivalence/recovery decisions, not permission to resume a task.
- E2 supports only a narrow numeric runtime-constraint grammar. Unsupported syntax produces `UNKNOWN` rather than adding a large versioning dependency or guessing.

## Completion / handoff

- Completed: local fingerprinting, explicit compatibility evaluator, focused tests, draft PR #29, and full Runtime stack CI.
- Not completed: independent review / merge.
- Current blocker: independent review required for completion; E3 run-evidence binding may continue as a separate stacked tranche.
- Next action if not DONE: independent review of PR #29; if continuing, bind EnvironmentSpec/fingerprint evidence to immutable run records without turning compatibility into authority.
