# Task: Add run manifests, continuity-aware review, and run-scope proof

- Status: `READY`
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

- MAY CHANGE: `runtime/state/**`, new `runtime/integrity/**`, routing reviewer eligibility, CLI/tests/docs/checklists, this task record.
- MUST NOT CHANGE: hcom/RnS/helper authority boundaries, operator approval semantics, legacy/migration source.
- OPERATOR APPROVAL REQUIRED: none for local implementation; weakening independent review or expanding agent authority requires escalation.

## Decision authority

- Owner may decide: run-manifest schema/API, task revision hashing, context hashing, scope representation, continuity-edge representation, optional criterion evidence schema.
- Owner must escalate: mandatory new release ceremony, changing who owns consequential decisions, or automatically reverting out-of-scope changes.

## Acceptance criteria

- [ ] Run manifest may be created only for an ACTIVE task claimed by that worker.
- [ ] Manifest immutably records stable task revision, worker/session, readable/writable/forbidden scope, context file hashes, runtime limits, base revision, and timestamp.
- [ ] Requested writable scope cannot exceed parent task `output_paths`.
- [ ] Staleness check detects changed task definition, changed/missing context, or missing task.
- [ ] Git/run-scope verifier reports changes outside frozen writable scope without auto-reverting them.
- [ ] Continuity links are durable and review claim rejects the submission author plus every connected continuation identity.
- [ ] Router does not recommend a continuity-disqualified reviewer.
- [ ] Optional criterion claims preserve implementer evidence separately from reviewer verdicts; reviewer verdict never rewrites original claim.
- [ ] Integrity code has focused regression tests and full stack remains green.

## Verification and evidence

- Verification: SQLite/unit tests, temporary Git repo scope tests, full GitHub Actions stack.
- Review required: `INDEPENDENT_REVIEW` — saved for later per operator instruction.

## Conditional execution rules

- Run manifests are required by method for high-risk/resumable work, but this task does not force ceremony onto trivial edits.
- Out-of-scope verification fails/report-only; it does not auto-revert filesystem state.
- Criterion-level evidence remains optional unless a future explicit task/risk rule requires it.
- Continuity lineage affects review independence only; it does not grant task ownership or authority.

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

- Completed: task shaped.
- Not completed: implementation/tests/docs.
- Next action: add immutable run/continuity/evidence tables and guarded APIs.
