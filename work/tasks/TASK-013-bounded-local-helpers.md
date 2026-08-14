# Task: Add bounded Ollama and Aider helpers

- Status: `READY`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `implementation-agent`
- Risk: `MEDIUM`
- Goal: Add narrow local-helper wrappers for Ollama text work and Aider file edits that enforce task output scope and cannot own, approve, or complete MAPS work.

## Inputs and source of truth

- Inputs: active task contract shape, HPOM/model-capability playbooks, preserved local/Aider wrappers, current Ollama/Aider CLI docs.
- Authoritative sources: active MAPS task output paths/limits; current upstream CLI syntax.
- Dependencies: stacked active runtime through RnS.

## Acceptance criteria

- [ ] Shared scope validator requires ACTIVE task snapshot and keeps outputs inside declared task output paths.
- [ ] Ollama helper runs one explicit model/prompt and writes only the declared bounded output.
- [ ] Aider helper targets only declared task output paths and refuses dirty targets.
- [ ] Aider uses one-shot `--message`, disables auto/dirty commits, and never supplies blanket yes flags.
- [ ] Helper invocation/result records are durable but are not task authority.
- [ ] Wrappers do not call task completion/review/approval mutations.
- [ ] Tests use fake executables/repos; no live model/tool required.

## Verification and evidence

- Verification: fake CLI + temporary git repo tests; source-boundary assertions.
- Review required: `INDEPENDENT_REVIEW`

## Stop / escalate

Stop if a helper needs wider output scope, final approval authority, or unbounded shell/tool permissions.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Completion / handoff

- Completed: task shaped.
- Not completed: implementation/tests/docs.
- Next action: implement shared helper scope and wrappers.
