# Task: Add bounded Ollama and Aider helpers

- Status: `ACTIVE`
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

- [x] Shared scope validator requires ACTIVE task snapshot and keeps outputs inside declared task output paths.
- [x] Ollama helper runs one explicit model/prompt and writes only the declared bounded output.
- [x] Aider helper targets only declared task output paths and refuses dirty targets.
- [x] Aider uses one-shot `--message`, disables auto/dirty commits, and never supplies blanket yes flags.
- [x] Aider has no generic argument escape hatch and checks newly produced Git changes against parent scope.
- [x] Helper invocation/result records are durable but are not task authority.
- [x] Wrappers do not call task completion/review/approval mutations.
- [x] Tests use fake executables/repos; no live model/tool required.
- [ ] Helper regression suite executed on a configured checkout.

## Verification and evidence

- Verification: `tests/test_bounded_helpers.py` exercises fake Ollama/Aider/Git commands, ACTIVE/scope rules, dirty-target refusal, safe Aider argv, and no-authority source boundary.
- Current tool syntax checked against official Ollama/Aider documentation on 2026-08-14.
- Test execution remains pending because the current sandbox cannot clone the branch.
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

- Completed: shared helper scope/result store, bounded Ollama helper, bounded Aider helper, docs, fake regression suite.
- Not completed: configured-checkout test execution and independent review.
- Current blocker: current sandbox cannot clone/fetch the branch for execution.
- Next action: run helper tests later; continue fresh-clone installer/smoke work separately.
