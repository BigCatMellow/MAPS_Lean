# Task: EnvironmentSpec v1 schema foundation

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: implement the first declarative EnvironmentSpec schema/parser/hash and describe the existing Runtime stack CI environment without introducing containers, setup execution, fingerprints, or new run authority.

## Inputs and source of truth

- Inputs: `AGENTS.md`, `work/roadmaps/agent-harness-capabilities/03-environment-and-reproducibility.md` E1, `.github/workflows/runtime-stack-tests.yml`, merged `main`.
- Authoritative sources: active repository instructions and actual CI/runtime behavior win; the roadmap provides planning intent; EnvironmentSpec is an execution requirement description, not task authority.
- Dependencies / preconditions: none from draft Harness/Skills PRs; branch starts independently from merged `main`.

## Change boundary

- MAY CHANGE: new `runtime/environment/**`, one versioned EnvironmentSpec describing current Runtime stack CI, focused tests, this task file.
- MUST NOT CHANGE: task/run schema, Harness behavior, recovery, CI workflow itself, provider execution, setup behavior, secret handling outside the new parser, external systems.
- MAY CHANGE IF NECESSARY: EnvironmentSpec v1 field representation inside this narrow schema task.
- OPERATOR APPROVAL REQUIRED: executing setup commands, binding environment state into canonical runs, containers/sandboxes, credential material, external side effects, or material scope expansion.

## Decision authority

- Owner may decide: strict JSON v1 syntax, normalized hashing rules, identifier/path/domain validation, validation-tier representation, and focused tests consistent with the roadmap.
- Owner must escalate: any design requiring secret values, environment mutation, a second run/task authority store, or a container/sandbox platform merely to satisfy E1.

## Acceptance criteria

- [x] `EnvironmentSpec` v1 has explicit environment ID/version, repository assumptions, runtime constraints, required tools, setup/maintenance commands, validation tiers, network mode/domains, services, secret capability names, and dependency-input paths.
- [x] parser is strict about unknown fields so material environment requirements are not silently ignored.
- [x] required secret entries are capability/name identifiers only; secret values/assignment syntax are rejected.
- [x] dependency inputs are safe repo-relative portable paths.
- [x] network modes distinguish `NOT_REQUIRED`, `REQUIRED_RESTRICTED`, `REQUIRED_GENERAL`, and `UNKNOWN`; restricted mode requires explicit domains.
- [x] quick/normal/full validation tiers are explicit and preserve command order.
- [x] semantic unordered fields are normalized; command order remains semantic.
- [x] deterministic SHA-256 is computed from normalized spec semantics rather than source whitespace/key order.
- [x] one versioned spec accurately describes the current Runtime stack CI workflow closely enough to serve as the E1 pilot.
- [x] parser does not execute setup/validation commands or inspect the host.
- [x] no task/run authority, fingerprint, compatibility judgment, or environment mutation is added.
- [x] focused tests and full Runtime stack CI pass.
- [ ] independent review remains required before completion.

## Verification and evidence

- Verification: PR-triggered full Runtime stack CI run `31897492718` passed on implementation commit `21622438602bc22a70c3dc735c1d918a45463171`.
- Evidence to preserve: pilot spec hash, GitHub Actions run `31897492718`, PR #28 diff, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: existing MAPS Lean Python runtime; standard library only.
- Ordered procedure: define strict v1 semantics → describe current CI → focused tests → independent draft PR against `main` → full CI → review.
- Failure branches: IF actual environment comparison becomes necessary THEN stop at E1 and implement E2 fingerprint/compatibility as a separate tranche; IF a field requires broad YAML/TOML features THEN evaluate format change separately rather than hiding semantics in ad hoc parsing.
- Rollback / recovery: revert isolated independent commit/PR; no schema/data migration.
- Security / privacy controls: no environment dump; no secret values; parser rejects secret assignment syntax and unknown secret fields; commands are data only.
- External side effects: Git branch/PR publication only.
- Effort limit: E1 schema/parser/hash + one pilot spec only.
- Approved reference: Environment & Reproducibility roadmap E1.

## Stop / escalate

Stop rather than guess if:

- setup/validation commands would need to execute during parsing;
- current CI cannot be represented without inventing hidden environment state;
- environment requirements would be treated as task permission or operator approval.

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

- E1 uses strict JSON and the standard library. The format decision is intentionally conservative; semantics matter more than YAML aesthetics.
- Unknown fields fail closed in v1 because silently ignoring a new environment requirement would create false reproducibility confidence.
- Setup/maintenance/validation commands are preserved as ordered strings but never executed by this layer.
- Network mode is explicit. The current CI pilot uses `REQUIRED_GENERAL` because dependency installation reaches external package infrastructure.
- The pilot spec describes the existing GitHub Runtime stack workflow; it is not yet a universal spec for every local MAPS execution environment.
- EnvironmentSpec hash is descriptive execution evidence, not task authority.

## Completion / handoff

- Completed: EnvironmentSpec v1 schema/parser/hash, pilot Runtime CI spec, focused tests, draft PR #28, and full Runtime stack CI.
- Not completed: independent review / merge.
- Current blocker: independent review required for completion; downstream E2 work may stack on this verified head.
- Next action if not DONE: independent review of PR #28; E2 fingerprint/compatibility may continue as a separate stacked tranche against this verified implementation.
