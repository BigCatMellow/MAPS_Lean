# Task: Add hcom transport/session adapter

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `implementation-agent`
- Risk: `HIGH`
- Goal: Add a narrow MAPS adapter for hcom messaging and session control that keeps hcom state strictly separate from MAPS task authority and does not require WezTerm.

## Inputs and source of truth

- Inputs: current hcom README/source, `docs/CONTROL_PLANE_SETUP.md`, `migration/legacy-runtime-source/notes/communication-architecture.md`, active runtime boundaries.
- Authoritative sources: active Lean rules for authority; current upstream hcom CLI/source for command syntax.
- Dependencies / preconditions: stacked runtime branch contains SQLite and routing slices; adapter itself does not depend on task-state mutations.

## Change boundary

- MAY CHANGE: `runtime/communication/**`, tests, runtime/setup docs, this task record, migration checklists.
- MUST NOT CHANGE: task lifecycle/authority semantics, hcom upstream code, RnS implementation, local helper implementation, legacy/migration snapshots.
- MAY CHANGE IF NECESSARY: small runtime README/index references.
- OPERATOR APPROVAL REQUIRED: no real agent kill/spawn/send operations are executed by tests; adapter only provides explicit APIs.

## Decision authority

- Owner may decide: subprocess wrapper shape, JSON parsing, typed errors/results, safe command argument validation.
- Owner must escalate: direct hcom DB coupling, using hcom messages as task truth, authenticated-authority claims, or broadening into RnS behavior.

## Acceptance criteria

- [x] Adapter always sets project-local `HCOM_DIR` and uses argv/subprocess with `shell=False`.
- [x] `list_sessions()` parses `hcom list --json` into session dictionaries.
- [x] `read_events()` parses bounded hcom JSON event records and never copies them into MAPS canonical state.
- [x] `send()`, `spawn()`, `resume()`, and `stop()` execute only explicit hcom CLI operations.
- [x] No module under `runtime/communication/` imports `runtime.state` or mutates MAPS task state.
- [x] Tests use a fake hcom executable; they do not require or alter a real hcom installation.
- [x] No WezTerm-specific terminal choice is required.
- [ ] Fake-CLI suite executed on a configured checkout.

## Verification and evidence

- Verification: `tests/test_hcom_adapter.py` uses a generated fake executable and includes a source-boundary assertion.
- Evidence to preserve: test output and PR diff.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: Python 3.10+; current hcom CLI.
- Ordered procedure: verify upstream machine-readable commands → implement narrow adapter → fake-CLI tests → docs.
- Failure branches: invalid JSON from machine-readable commands returns `HcomProtocolError`; command nonzero exits return `HcomCommandError`; missing binary/timeouts return `HcomError`.
- Rollback / recovery: remove `runtime/communication/`; no SQLite task migration involved.
- Security / privacy controls: no credentials logged; message/transcript/event content remains hcom transport data unless explicitly promoted by a separate authorized MAPS operation.
- External side effects: production adapter methods may launch/send/kill agents when explicitly called; tests do not.
- Effort limit: do not implement RnS in this task.
- Approved reference: upstream hcom source plus preserved communication architecture.

## Stop / escalate

Stop rather than guess if:
- hcom command syntax cannot be verified;
- adapter would need direct hcom SQLite access;
- transport state would need to grant MAPS authority.

Escalate to: operator for authority/architecture changes.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Current upstream source verifies `hcom list --json`, JSON event querying, `hcom send`, `hcom r`, and `hcom kill` command contracts.
- hcom transport is useful for live coordination; durable outcomes still belong in MAPS task/decision/review/handoff records.
- hcom `intent` is optional metadata and must not be treated as durable authority.
- Attempted configured-checkout execution was blocked because this sandbox cannot resolve GitHub; no test pass is claimed.

## Completion / handoff

- Completed: adapter, public boundary docs, fake-CLI regression suite, current upstream command verification.
- Not completed: configured-checkout test execution and independent review.
- Current blocker: current execution sandbox cannot clone/fetch the branch over the network.
- Next action if not DONE: run `python -m unittest tests.test_hcom_adapter -v` on a configured checkout; continue RnS separately.
