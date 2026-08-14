# Task: Add run manifests, continuity-aware review, and run-scope proof

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `implementation-agent`
- Risk: `HIGH`
- Goal: Freeze the exact task/context/scope given to a worker at execution time, reject stale/out-of-scope runs, enforce reviewer independence across identity rotation, and preserve optional criterion-level evidence without recreating the legacy subsystem.

## Inputs and source of truth

- Inputs: active runtime stack through TASK-014, `playbook/EXECUTION_INTEGRITY.md`, preserved `run_manifest.py`, `review_routing.py`, `submission_records.py`, and their tests/evidence.
- Authoritative sources: current SQLite task contract and active Lean execution-integrity rules. Migration source is historical implementation evidence only.
- Dependencies: TASK-009 state runtime and routing/review behavior in the current stacked branches.

## Change boundary

- MAY CHANGE: `runtime/state/**`, `runtime/integrity/**`, routing reviewer eligibility, CLI/tests/docs/checklists, this task record.
- MUST NOT CHANGE: hcom/RnS/helper authority boundaries, operator approval semantics, legacy/migration source.
- OPERATOR APPROVAL REQUIRED: none for local implementation; weakening independent review or expanding agent authority requires escalation.

## Decision authority

- Owner may decide: run-manifest schema/API, task revision hashing, context hashing, scope representation, continuity-edge representation, optional criterion evidence schema.
- Owner must escalate: mandatory new release ceremony, changing who owns consequential decisions, or automatically reverting out-of-scope changes.

## Acceptance criteria

- [x] Run manifest may be created only for an ACTIVE task claimed by that worker.
- [x] Manifest immutably records stable task revision, worker/session, readable/writable/forbidden scope, context file hashes, runtime limits, base revision, and timestamp.
- [x] Requested writable scope cannot exceed parent task `output_paths`.
- [x] Staleness check detects changed task definition, changed/missing context, or missing task.
- [x] Git/run-scope verifier reports changes outside frozen writable scope without auto-reverting them.
- [x] Continuity links are durable and review claim rejects the submission author plus every connected continuation identity.
- [x] Router does not recommend a continuity-disqualified reviewer.
- [x] Optional criterion claims preserve implementer evidence separately from reviewer verdicts; reviewer verdict never rewrites original claim.
- [x] Integrity code has focused regression tests and full stack remains green.

## Verification and evidence

- GitHub Actions run `31847038026`: full active stack PASS on Python 3.12.
- Current suite count: **79 tests, 79 PASS**, with `ResourceWarning` treated as error.
- The same run also passed the disposable SQLite/AGI/claim/review/DONE smoke, real LangGraph SQLite checkpoint smoke, and installer syntax/preview checks.
- Run-manifest regression coverage includes ACTIVE/current-claimant enforcement, task/context revision hashes, writable-scope subset, stale task/context detection, real temporary-Git scope reporting, and no auto-repair.
- SQLite triggers mechanically reject UPDATE/DELETE of run manifests and UPDATE/DELETE of run context refs; the final CI run includes this raw-SQL immutability test.
- Continuity coverage includes transitive lineage, claim-time rejection, router filtering, and final-review re-check when continuity evidence appears after review claim.
- Criterion coverage proves implementer claims and reviewer verdicts remain separate and that opting into criterion mode blocks overall approval until every current criterion is complete + confirmed.
- Review required: `INDEPENDENT_REVIEW` — saved for later per operator instruction.

## Conditional execution rules

- Run manifests are required by method for high-risk/resumable work, but this task does not force ceremony onto trivial edits.
- Out-of-scope verification is report/fail only; it never resets, restores, cleans, or auto-reverts filesystem state.
- Criterion-level evidence remains optional. If no criterion claims exist for a submission, the existing simpler submission/review path remains unchanged.
- If criterion claims are used, overall `APPROVED` requires every acceptance criterion's latest claim to be `complete` and its latest reviewer verdict to be `confirmed`.
- Continuity lineage affects review independence only; it grants no task ownership or authority.

## Stop / escalate

Stop if implementation would create another mutable task truth source or silently modify/revert user work.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Completion / handoff

- Completed: immutable run-manifest/context-hash state, stable task revisions, staleness detection, writable-scope proof, read-only Git verifier, continuity graph, continuity-aware router/review transitions, optional criterion claims/verdicts, CLI/docs, focused tests, and integrated CI verification.
- Not completed: independent review/merge of the stacked runtime; separate-release-gate disposition; final legacy reference/privacy sweep.
- Last verified result: `79/79 PASS` plus disposable runtime/LangGraph smoke and installer checks in Actions run `31847038026`.
- Exact next action: keep review deferred; decide whether Lean needs any separate release gate beyond current risk-tiered review/completion, then update legacy-removal disposition accordingly.
