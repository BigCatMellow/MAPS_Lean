# Task: append-only run environment evidence

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `FOUNDRY / incumbent repair continuity`
- Risk: `MEDIUM`
- Goal: bind exact EnvironmentSpec/fingerprint/compatibility observations to immutable runs as append-only canonical evidence without changing run contracts, task authority, leases, recovery behavior, review authority, or policy.

## Inputs and source of truth

- root `AGENTS.md`;
- accepted EnvironmentSpec / EnvironmentFingerprint foundation (#28/#29);
- accepted review-subject binding (#32) and Portable Run Record behavior on the branch's integrated historical base;
- `runtime/state/environment.py`, `runtime/state/schema.sql`, `runtime/state/store.py`;
- `runtime/run_record.py`;
- independent PR #30 review finding on exact head `1a4016c424e188e06560c9af125e97be774ac269`.

Canonical task/run state remains authoritative for lifecycle/ownership. Environment evidence is bounded historical evidence only.

## Change boundary

May change only this E3 layer and its narrow Run Record integration:

- `runtime/state/environment.py`;
- `runtime/state/schema.sql`;
- `runtime/state/store.py`;
- `runtime/run_record.py` only where exact-run environment coverage is projected;
- focused E3/Run Record tests;
- this task record.

Must not change:

- immutable `run_manifests` contract;
- task claim/lease/recovery semantics;
- review/policy/operator authority;
- provider behavior;
- EnvironmentSpec/fingerprint meaning;
- complete-replay claims;
- unrelated lineage or Context Builder behavior.

## Core E3 semantics

- `run_environment_evidence` rows are append-only and keyed to an existing immutable run.
- Each row preserves exact EnvironmentSpec identity/hash, fingerprint identity/hash, internally derived compatibility report, optional reference fingerprint, bounded snapshots, actor, and timestamp.
- Compatibility is recomputed from supplied exact spec/fingerprint/reference; callers cannot write an arbitrary compatibility verdict.
- Evidence recording never claims/renews/stops/resumes a task and never mutates the immutable run manifest.
- Missing run or spec/fingerprint mismatch fails explicitly.
- sensitive EnvironmentSpec content is rejected rather than redacted under a changed hash identity.
- trace projection is read-only and places environment evidence under the exact owning run.
- multiple observations append rather than replace.
- SQLite UPDATE/DELETE of evidence rows is blocked.

## Returned review defect: Run Record coverage integrity

Independent review of exact feature head `1a4016c424e188e06560c9af125e97be774ac269` found one HIGH evidence-integrity defect.

`EnvironmentEvidenceMixin.trace_task()` intentionally exposes `environment_evidence` for every run, including `[]` when no E3 observation exists. `runtime/run_record.py` was treating **key presence** as sufficient for environment coverage `VERIFIED`.

That conflated two facts:

1. the source/read surface is available;
2. this exact selected run actually has recorded environment evidence.

A selected run with zero observations could therefore be reported as verified merely because the capability surface existed.

## Repair semantics

The repaired Run Record keeps those facts separate:

- `source_available = true` means the source trace exposes the environment-evidence surface for the selected run;
- `included = true` only when one or more exact-run environment evidence observations are actually present;
- one or more observations -> environment coverage `VERIFIED`;
- exposed surface + empty list -> environment coverage `MISSING`, not VERIFIED;
- no exposed surface -> environment coverage `MISSING`;
- malformed non-list projected environment evidence fails explicitly instead of being treated as truthy evidence;
- `replay.complete` remains `false`;
- review-subject coverage remains independent and stays `UNKNOWN` when exact selected-run binding is unproven.

No E3 storage/schema/writer authority change was required for this repair.

## Acceptance criteria

- [x] existing `run_manifests` schema and immutable contract remain unchanged.
- [x] run-environment evidence is append-only and keyed to an existing run.
- [x] exact spec/fingerprint/reference identities and normalized snapshots are preserved.
- [x] compatibility is internally derived and may record compatible/warning/drifted/incompatible/UNKNOWN observations without lifecycle authority.
- [x] task status/claim/lease/heartbeat and run manifest remain unchanged after evidence recording.
- [x] multiple observations append rather than replace.
- [x] SQLite UPDATE/DELETE of environment evidence is blocked.
- [x] missing run and spec/fingerprint mismatch fail explicitly.
- [x] parser rejects credential-like persisted command text.
- [x] persistence independently rejects a sensitive typed EnvironmentSpec even if constructed without the parser.
- [x] trace projects environment evidence under the exact run without making trace writable authority.
- [x] event summary omits full snapshots.
- [x] empty exact-run environment evidence no longer yields `VERIFIED` Run Record coverage.
- [x] actual exact-run environment evidence still yields `VERIFIED` coverage.
- [x] Run Record exposes source-surface availability separately from included evidence.
- [x] malformed projected environment evidence fails explicitly.
- [x] review-subject UNKNOWN and incomplete replay semantics are preserved.
- [x] Runtime CI #412 / `31932204762` passed on code/test repair head `e2c489abe00ffa23a48069192507e8a9815a340a` before this task-record evidence update.
- [ ] fresh Runtime CI passes on the final task-record head.
- [ ] continuity-independent exact-head review confirms the HIGH coverage blocker is mechanically closed.
- [ ] final current-main synchronization/integrated-head CI/review is completed by SWITCHYARD before merge.

## Verification evidence

Historical evidence:

- original E3 implementation CI passed;
- repair CI #338 reached the active suite and exposed the earlier stale Run Record expectation;
- synchronized feature CI #358 / `31929911245` passed on `1a4016c424e188e06560c9af125e97be774ac269`, after which SENTINEL found the semantic empty-evidence coverage defect.

Current repair evidence:

- blocked head: `1a4016c424e188e06560c9af125e97be774ac269`;
- code/test repair head: `e2c489abe00ffa23a48069192507e8a9815a340a`;
- exact blocked-head -> code/test repair delta: `runtime/run_record.py` and `tests/test_run_record.py` only;
- Runtime CI #412 / `31932204762`: PASS on that exact code/test repair head;
- the test pair proves empty exact-run evidence is MISSING while present exact-run evidence is VERIFIED, and malformed projected evidence is rejected.

This task-record update intentionally creates a new final head. Old CI cannot satisfy the final exact-head gate.

## Review requirement

`INDEPENDENT_REVIEW`.

FOUNDRY implemented the original repair and the returned coverage repair and is not eligible to provide the independent disposition.

Reviewer should verify:

- source availability is not confused with evidence presence;
- empty selected-run evidence cannot produce VERIFIED;
- non-empty selected-run evidence can produce VERIFIED;
- malformed projected evidence fails closed;
- `replay.complete = false` remains true to the incomplete source set;
- review-subject and other coverage states are not spuriously upgraded;
- the repair adds no task/recovery/policy/review authority.

## Integration boundary

After a clean feature-head review, SWITCHYARD owns:

1. genuine synchronization onto then-current accepted `main`;
2. preservation of all newer accepted schema/state/Run Record changes;
3. exact integrated delta verification;
4. fresh integrated-head Runtime CI;
5. fresh exact integrated-head independent review;
6. merge only if exact state remains clean.

## Stop / escalate

Stop rather than guess if environment evidence would need to mutate run/task authority, if compatibility is proposed as recovery permission, if sensitive snapshot persistence would require redaction under a changed identity, or if current-main synchronization cannot preserve both accepted upstream state and this E3 evidence boundary exactly.
