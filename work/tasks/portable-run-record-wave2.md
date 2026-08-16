# Task: portable Run Record v1

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: create a deterministic, sanitized, read-only portable projection for one exact MAPS run so real incidents can later become reproducible regression cases without creating a new task/run authority store or pretending incomplete external lineage is complete.

## Inputs and source of truth

- Inputs: `AGENTS.md`, merged `main`, `runtime/state/observability.py`, `runtime/cli.py`, Learning & Evaluation roadmap section 4, prior trace/Run Record research notes.
- Authoritative sources: canonical SQLite/task trace evidence remains authoritative; Run Record is a disposable/exportable read model over `trace_task()`.
- Dependencies / preconditions: merged PR #19 trace/outcome/run-manifest foundation. Draft Environment/review-subject/Harness enrichments are not required and must not be treated as merged authority.

## Change boundary

- MAY CHANGE: new `runtime/run_record.py`, `runtime/cli.py` narrow read-only command, focused Run Record tests, this task file, minimal runtime documentation if needed.
- MUST NOT CHANGE: canonical SQLite schema/state mutation, task/run/review/outcome authority, trace source semantics, provider/hcom/helper/recovery systems, Skills/Environment draft branches, external systems.
- MAY CHANGE IF NECESSARY: v1 projection/coverage schema inside this read-only export task.
- OPERATOR APPROVAL REQUIRED: new persistent authority store, raw private-data export by default, provider transcript export, external publication, or material scope expansion.

## Decision authority

- Owner may decide: sanitized v1 record fields, deterministic record identity, free-text omission policy, coverage-state vocabulary, exact-run selection, future-trace enrichment detection, and read-only CLI exposure consistent with roadmap intent.
- Owner must escalate: any design that needs hidden chain-of-thought, copies writable task truth into a new store, claims complete replay without evidence, or exports raw prompts/private file contents by default.

## Acceptance criteria

- [x] `build_run_record(source, task_id, run_id)` selects exactly one run from the existing sanitized `trace_task()` projection and fails explicitly for missing/ambiguous task/run identity.
- [x] record is versioned and has deterministic `record_id` / SHA-256 based on normalized portable content.
- [x] same unchanged source evidence yields same Run Record identity.
- [x] default record includes structural task metadata, stable task revision, policy flags, exact run manifest, scopes/runtime limits/base revision, context path/hash refs, submission metadata, review metadata, criterion evidence, run-bound/task-unbound outcomes, event metadata, coverage, and replay limitations.
- [x] task/run authority remains only in canonical sources; Run Record performs no writes.
- [x] raw task title/outcome/authority/verification/escalation text, raw submission evidence, review summaries, criterion verdict notes, event summaries, and outcome source/notes are omitted by default and represented only as bounded presence/length metadata.
- [x] context file contents are never embedded; path/hash refs remain available.
- [x] outcomes are separated into exact `run_bound` and task-level `task_unbound` observations rather than guessed joins.
- [x] task-level review/timeline data is labeled with unknown run-join state unless an accepted future immutable subject/source explicitly resolves it.
- [x] coverage uses explicit `VERIFIED`, `SOURCE_LOCAL`, `MISSING`, `UNKNOWN` vocabulary and does not claim hcom/helper/recovery/session/harness trajectory coverage that current accepted sources cannot prove.
- [x] replay is explicitly `complete: false` in v1.
- [x] accepted future trace enrichments such as environment evidence or review subjects can flow into the record and upgrade their specific coverage labels without changing the authority model.
- [x] CLI exposes `python -m runtime.cli run-record TASK_ID RUN_ID` as JSON output only; no new writable state is added.
- [x] record JSON round-trips cleanly and focused tests prove sanitized text is not copied.
- [x] focused tests and full Runtime stack CI pass.
- [ ] independent review remains required before completion.

## Verification and evidence

- Verification: PR-triggered full Runtime stack CI run `31899074481` passed on implementation commit `f2eb44a1cf180a2e58de85904eafb891df75bf7c`.
- Evidence to preserve: deterministic record tests, privacy/coverage tests, GitHub Actions run `31899074481`, PR #33 diff, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: accepted `main` TaskStore trace projection.
- Ordered procedure: define projection/privacy/coverage contract → build exact-run record → CLI → focused tests → independent draft PR → full CI → review.
- Failure branches: IF a source cannot be joined safely THEN label it `UNKNOWN`/`MISSING`; do not infer by timestamps/prose. IF a future trace enrichment exists THEN include only the already-sanitized structured projection it exposes.
- Rollback / recovery: revert isolated independent commit/PR; no schema/data migration.
- Security / privacy controls: free text omitted by default, no raw evidence/file contents/provider transcripts, no hidden reasoning, deterministic structural export only.
- External side effects: Git branch/PR publication only; CLI writes JSON to stdout.
- Effort limit: portable read model v1 only; no incident classifier, regression-case freezer, model replay engine, or full harness trajectory.
- Approved reference: Learning & Evaluation roadmap Portable Run Record.

## Stop / escalate

Stop rather than guess if:

- portable export requires copying raw sensitive/private source text by default;
- a missing external source would need inferred correlation;
- a Run Record field starts becoming writable canonical state;
- “portable” begins being represented as complete deterministic replay without provider/session/operation evidence.

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

- This task starts independently from merged `main`. Draft PR #30 environment evidence and PR #32 review-subject bindings are intentionally optional enrichments, not dependencies.
- Run Record v1 is built over `trace_task()` rather than issuing another set of canonical database queries. This keeps one existing sanitized read boundary and avoids duplicate truth/projection logic.
- Free text is omitted, not merely secret-redacted, because portability may eventually cross project/evaluation boundaries where private task prose should not be exported accidentally.
- Structural actor/reviewer/worker IDs remain because provenance/independence analysis needs identity; raw prose/file contents do not.
- `timeline` and general `reviews` remain task-level with `UNKNOWN` run join unless exact subject evidence says otherwise.
- The record content hash contains no export timestamp; identical source projection yields identical identity.
- Future incident freezing should reference this Run Record and add a separately reviewed sanitized fixture/problem statement rather than changing Run Record privacy defaults.

## Completion / handoff

- Completed: deterministic sanitized Run Record v1, exact-run selection, coverage/replay limitations, read-only CLI, focused tests, draft PR #33, and full Runtime stack CI.
- Not completed: independent review / merge.
- Current blocker: independent review required for completion; downstream incident/regression-case work may stack on this verified head.
- Next action if not DONE: independent review of PR #33; a frozen regression-case format may now safely reference Run Record identity without changing Run Record privacy defaults.
