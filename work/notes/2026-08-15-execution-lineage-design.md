# Execution lineage design — Wave 3

Status: `PLANNING / DESIGN EVIDENCE — NOT ACTIVE AUTHORITY`

Date: `2026-08-15`

Base inspected: `main@086e066f723d793273441dd52b500e62ac981deb`

Prospective interfaces inspected:

- harness/security stack through PR #24 head `3110457c78a1d30b4b6692d78108617d88c4d0ba`;
- portable Run Record PR #33 head `3d618a4d74d8be4ba42e119cc5d659e204ccd9d5`;
- reconciliation PR #36 as planning evidence only.

These PR heads are **not accepted runtime authority** until independently reviewed and merged. Re-check exact heads/base state before implementation.

---

## 1. Executive summary

MAPS Lean already has strong local identities for tasks, runs, workers, reviews, helper results, recovery incidents, and hcom sessions. The missing capability is not another supervisor or another database of copied state. It is the set of **explicit cross-source relationships** required to reconstruct one execution without guessing.

The smallest Lean-native target is:

```text
task
  ↓
immutable run
  ↓
worker
  ↓
provider session(s) for that same run
  ↓
helper/child invocation(s)
  ↓
recovery/replacement run links
  ↓
request/thread/addressee correlation
  ↓
exact submission attempt
```

The core design rule is:

> Existing systems continue to own their own facts. MAPS stores only cross-source links that no existing source owns, and derives combined lineage at read time.

That means:

- SQLite `tasks` remains task authority;
- immutable `run_manifests` remain the initial task/run/worker contract;
- hcom remains provider communication/session fact authority;
- helper result storage remains helper-result evidence;
- RnS remains recovery incident/action evidence;
- review/submission tables retain their existing lifecycle roles;
- new lineage records are append-only references/correlation evidence only;
- Trace and Run Record remain derived views.

Do **not** mutate an old run manifest merely because a provider session becomes known later. Do **not** add a mutable `tasks.current_session_id`. Do **not** mirror hcom messages or recovery/helper state into a generic blackboard.

A worker identity change is also a hard boundary: an immutable run is bound to one worker. If recovery changes the worker or materially changes the run contract/context, create a **new run** and link predecessor → replacement explicitly.

---

## 2. Verified baseline

### 2.1 Accepted `main` identities and authorities

| Fact | Current source | Status | Design consequence |
|---|---|---|---|
| Task lifecycle / claimant / lease | SQLite `tasks` | `VERIFIED` | Never infer from provider/session state |
| Initial run identity | SQLite `run_manifests.run_id` | `VERIFIED` | Immutable; remains the run anchor |
| Run task revision | `run_manifests.task_revision` | `VERIFIED` | Late links must not rewrite it |
| Run worker | `run_manifests.worker_id` | `VERIFIED` | Different worker means different run |
| Initial provider session | optional `run_manifests.session_id` | `VERIFIED` when present | Existing initial binding remains authoritative evidence |
| Context identity | `run_context_refs(path, sha256)` | `VERIFIED` | Lineage should reference, not copy contents |
| Identity continuity | `continuity_links` | `VERIFIED` evidence | Used for review independence; does not grant task authority |
| Submission attempt number | `task_submissions.submission_count` | `VERIFIED` | Stable logical submission-attempt key, but no run join exists |
| Criterion claim → run | `submission_criterion_claims.run_id` | `VERIFIED` when present | Do not duplicate this relation |
| Review lifecycle | `reviews` | `VERIFIED` | Review is task-level on current main |
| Helper result ID | `HelperResult.helper_run_id` | `VERIFIED` | Stable helper evidence identity exists |
| Helper → task | `HelperResult.task_id` | `VERIFIED` | Helper → run/session/parent is missing |
| Recovery incident ID | `RecoveryIncident.incident_id` | `VERIFIED` | Stable recovery evidence identity exists |
| Recovery → task/worker/session name | recovery store | `VERIFIED` | Run/session-ID replacement lineage is incomplete |
| hcom session/message facts | hcom adapter | `VERIFIED` source boundary | Must not be treated as task authority |
| Task trace | `trace_task()` | `VERIFIED` derived view | Explicitly marks communication/helper/recovery gaps |

### 2.2 Accepted gaps are already explicit

`trace_task()` on current `main` says:

- communication is not included because hcom events are not correlated to tasks;
- external runtime evidence from recovery/helper state is not included;
- the trace is a canonical task-DB projection only.

That is correct behavior. The lineage work should close joins only when exact stable identifiers exist. Until then, the view must keep saying `MISSING` or `UNKNOWN`.

### 2.3 Recovery already demonstrates why worker/name inference is insufficient

Current RnS silent-stop detection accepts a `worker -> session_name` binding. It groups ACTIVE tasks by worker and refuses to guess when one worker has multiple ACTIVE tasks.

That is direct evidence for explicit task/run/session lineage:

```text
worker + session name + time
!=
exact task/run/session relationship
```

The current refusal to guess is a property to preserve, not a bug to bypass.

---

## 3. Prospective interface observations

These observations come from open draft PRs and must be re-checked after review.

### 3.1 Harness types through PR #24

Prospective `ExecutionBinding` contains:

```text
task_id
run_id
worker_id
task_revision
project_id
session_id?          # optional
context_hashes
environment_spec_hash?
```

Prospective `SessionRef` contains:

```text
session_id
worker_id
adapter
project_id
remote_ref?
```

Prospective `OperationResult` already has an opaque `operation_id`, bounded result code, mutation/completeness/retry semantics, and evidence refs.

Useful boundary:

- these are correlation types, not authority;
- session state remains provider evidence, not task truth.

### 3.2 Current draft hcom harness deliberately blocks dishonest attachment

At PR #24's current head:

- hcom `start` is unsupported until spawn can return structured session identity;
- hcom `attach` is unsupported until durable run/session lineage exists;
- `send`/`resume`/`stop` require explicit session binding;
- the canonical guard requires the session to be durably present in the immutable run manifest for session-bound operations.

This is a healthy stop condition, but it exposes the next design problem:

> An immutable manifest cannot honestly acquire a session discovered after creation.

The answer must not be to mutate the manifest or add a second mutable session authority.

### 3.3 Prospective Run Record already reserves the gap

PR #33 currently reports:

```text
communication                      UNKNOWN
session/helper/recovery lineage    UNKNOWN
harness operation trajectory       MISSING
replay.complete                    false
```

The lineage design should enrich this read model incrementally without changing its authority boundary or claiming complete replay prematurely.

---

## 4. Invariants

Every implementation tranche derived from this note should enforce these mechanically where practical.

### L1 — one authority per fact

A lineage record may own a cross-source relationship that no existing source owns. It must not copy mutable task/session/recovery/review state as a competing truth.

### L2 — run manifests stay immutable

`run_manifests` continue to describe the execution contract known at run creation. Late facts append elsewhere.

### L3 — one run has one worker identity

`run_manifests.worker_id` is immutable. A new worker or materially different execution contract requires a new run.

### L4 — provider/session evidence cannot grant task authority

Linking or observing a provider session must never:

- claim a task;
- renew a task lease;
- change task status;
- satisfy operator approval;
- create independent-review authority.

### L5 — missing relation remains `UNKNOWN`

Do not infer a join because:

- timestamps are close;
- names look similar;
- a task has only one run;
- a worker has only one visible session;
- a message says it belongs to a task;
- a process is alive.

### L6 — liveness and readiness are separate evidence dimensions

```text
process exists
!= session is usable
!= provider/API is ready
!= task is owned
!= task is progressing
```

A `RUNNING` session state does not imply provider/API readiness.

### L7 — lineage records are append-only

Historical linkage must be inspectable. Corrections happen through explicit superseding/replacement relations, not silent UPDATE/DELETE.

### L8 — raw private content stays out of lineage

Do not persist message bodies, provider transcripts, raw helper output, raw submission evidence, prompts, or secrets merely to improve joins.

### L9 — derived "current" pointers stay derived

There is no persisted mutable `current_session_id`, `current_helper`, or `current_wait` on the task row.

### L10 — communication lineage is correlation, not a second inbox

MAPS may remember that an explicit request belongs to a run/thread/addressee. hcom remains the source for actual message/event facts.

---

## 5. Proposed data ownership model

Do **not** create a universal generic entity graph. Use a few narrow append-only relationships with constrained semantics.

The exact SQL belongs in implementation PRs after upstream review, but these are the intended contracts.

### 5.1 `run_session_links`

Purpose: represent provider-session facts learned **after** immutable run creation, including same-worker session replacement.

Proposed fields:

```text
id                      integer/opaque stable link ID
run_id                  FK -> run_manifests.run_id
session_id              provider session ID
adapter                  provider adapter ID
project_id               project identity
worker_id                worker identity
link_kind                ATTACHED | REPLACEMENT
predecessor_session_id   nullable; required for REPLACEMENT
binding_source           bounded provenance code
source_ref               exact evidence/provider/operator reference
created_by               actor recording the link
created_at               timestamp
```

Required invariants:

1. `worker_id == run_manifests.worker_id`.
2. `project_id` matches the run's task project.
3. The first extension for a run whose manifest has `session_id = NULL` may be `ATTACHED` with no predecessor.
4. If the manifest already has a session, the first extension must be `REPLACEMENT` whose predecessor is that manifest session.
5. Later replacements must name the current derived session endpoint exactly.
6. Conflicting branches from the same predecessor are rejected.
7. A session cannot replace itself.
8. UPDATE/DELETE are rejected.
9. Recording the link does not renew task lease, change claimant, or change task state.
10. A bare caller-supplied `SessionRef` is not, by itself, proof that the provider session belongs to the run.

`binding_source` must be narrow. Intended examples:

```text
PROVIDER_RESULT
RECOVERY_RESULT
OPERATOR_CONFIRMED
```

Do not accept free-form "I think this is the session" provenance.

`source_ref` must point to the exact evidence used. If a provider adapter cannot return a stable identity/evidence reference, automatic binding remains `UNKNOWN` rather than guessed.

### 5.2 Derived session chain

The current session for a run is a read-time projection:

```text
manifest.session_id (if present)
    ↓ optional replacement
run_session_links
    ↓ optional replacement
run_session_links
    ↓
derived endpoint
```

If the chain is missing, branching, or contradictory, return `UNKNOWN`/error. Never choose "latest timestamp wins".

The canonical harness guard can later consume this resolver instead of reading only `run_manifests.session_id`.

### 5.3 Worker replacement is a new run

Do not use `run_session_links` to change worker identity.

If recovery changes worker:

```text
RUN-A / worker-1
      ↓ recovery/replacement
RUN-B / worker-2
```

`RUN-A` remains immutable historical evidence. `RUN-B` gets its own manifest.

### 5.4 `run_recovery_links`

Purpose: explain that one exact run was replaced/restarted because of a recovery event, without turning RnS state into task authority.

Proposed fields:

```text
id                  stable link ID
predecessor_run_id  FK -> run_manifests
replacement_run_id  FK -> run_manifests
incident_ref        optional exact RnS incident ID/reference
reason_code         bounded code
created_by
created_at
```

Required invariants:

- predecessor and replacement are different;
- both runs belong to the same task;
- replacement run is not silently treated as equivalent to predecessor;
- differing task revisions/context hashes remain visible;
- relationship does not imply inherited review authority;
- if worker/session identity continuity matters for independent-review rules, the existing `continuity_links` mechanism remains the authority for that continuity fact.

No new recovery supervisor is required.

### 5.5 `run_helper_links`

Purpose: associate an exact helper invocation with an exact run and parent execution context while leaving helper results in the existing helper evidence source.

Proposed fields:

```text
helper_run_id         exact helper ID; references existing helper evidence identity
run_id                FK -> run_manifests
invoked_by_worker_id  explicit parent worker
parent_session_id     nullable exact provider session ref when known
parent_helper_run_id  nullable exact parent helper ID for nested helper work
created_by
created_at
```

Required behavior:

- helper ID must be allocated **before** the helper side effect begins;
- the link is written before invocation so a crash can still leave invocation lineage;
- existing helper-result storage continues to own status/summary/output paths;
- no helper output or prompt is copied into SQLite lineage;
- parent session is optional and stays `UNKNOWN` when not established;
- parent helper link must resolve to the same run;
- helper completion/result uses the same `helper_run_id`.

Current helper code creates the helper ID as part of result creation. The implementation tranche should split opaque helper-ID allocation from result construction rather than inventing a second helper identity.

### 5.6 `run_request_links`

Purpose: correlate a deliberate MAPS request with an exact run, thread, and addressee without mirroring hcom messages.

Proposed fields:

```text
request_id            MAPS-generated opaque request correlation ID
run_id                FK -> run_manifests
requester_worker_id   explicit worker
transport             hcom (v1)
addressee_ref          exact intended addressee identity
thread_ref             exact hcom thread/correlation value
provider_event_ref     nullable exact external event ID when supported/proven
created_by
created_at
```

Intentionally absent:

```text
message_body
message_summary
waiting_status
resolved_status
human_intent_guess
provider transcript
```

Rules:

- create `request_id` before sending;
- send with an explicit thread/correlation value rather than deriving from prose;
- store intended addressee from the structured send call, not parsed message text;
- hcom remains source authority for whether an event actually exists;
- `provider_event_ref` stays null/`UNKNOWN` unless the provider exposes a stable event identity that MAPS can mechanically validate;
- an `ack` does not automatically mean the requested work is complete;
- this table does not become a wait/status authority plane.

#### Current evidence limitation

The inspected hcom adapter supports:

```text
send(target, message, intent, thread, from_name)
read_events(last, event_type, intent, agent, thread)
```

but currently accepts event dictionaries generically and does not validate a stable provider event-ID/addressee schema.

Therefore:

> Exact hcom event-ID/addressee joining beyond the outbound structured send inputs is `UNKNOWN` until a bounded real/schema fixture proves what upstream hcom exposes.

Do not implement a parser that guesses from arbitrary event/message fields.

### 5.7 `submission_run_links`

Purpose: bind the exact logical submission attempt to the exact run that produced it, without replacing `task_submissions`.

Proposed key/fields:

```text
(task_id, submission_count)   unique logical submission-attempt key
run_id                        FK -> run_manifests
author_id                     exact author/worker
created_at
```

Required behavior:

- write this relation in the **same SQLite transaction** as the submission count/state transition when the caller supplies an explicit run ID;
- validate run belongs to task;
- validate run worker matches the submitting worker;
- validate run revision is appropriate/current for the submission path;
- do not infer a run from timestamps, "only run", claimant name, or criterion evidence;
- existing submissions without a link remain valid historical submissions but their run join is `UNKNOWN`.

Criterion claims that already carry `run_id` remain their own evidence and must not be copied/reinterpreted as proof that the whole submission came from that run.

---

## 6. Provider/API readiness is not session lineage

Do not add readiness state to `run_session_links`.

A session link answers:

> Which provider session is associated with this run?

It does **not** answer:

> Can the provider API actually accept/complete an operation right now?

Prospective `SessionStatus` can report normalized provider session state, but provider/API readiness needs separate evidence.

Initial rule:

```text
session exists / RUNNING
→ provider_api_readiness = UNKNOWN
```

until an adapter-specific, bounded readiness check proves otherwise.

Future readiness evidence may be an operation result or a separate append-only observation if repeated use justifies persistence. It must never be used to renew task claims or grant authority.

This preserves the legacy lesson behind process-alive/provider-blocked failures without introducing another liveness supervisor.

---

## 7. Late session attachment semantics

Late attachment is the most important correctness case.

### Allowed shape

```text
immutable run created with session_id = NULL
        ↓
provider later yields exact stable session identity
        ↓
canonical task/run/worker/project checks still pass
        ↓
append ATTACHED run_session_link with exact provenance
        ↓
derived session chain now has an endpoint
```

### Not allowed

```text
find a session with a similar name/time
        ↓
UPDATE run_manifests.session_id
```

or:

```text
caller supplies SessionRef fields
        ↓
trust caller as provider proof
```

without an accepted source of binding evidence.

### Why provenance matters

The prospective harness types prove correlation fields but do not themselves prove that the provider created a session for this run. A future hcom `start`/`attach` path should return structured provider evidence or the link must be explicitly operator-confirmed.

If hcom cannot produce a trustworthy binding result, automated late attachment remains blocked rather than weakening identity rules.

---

## 8. Session replacement semantics

Same worker, same immutable run contract, new provider session:

```text
RUN-A / worker-1 / session-S1
        ↓ exact recovery/provider evidence
append REPLACEMENT(S1 -> S2)
        ↓
RUN-A / worker-1 / derived session-S2
```

Different worker or materially different run contract:

```text
RUN-A / worker-1 / S1
        ↓
recovery incident
        ↓
RUN-B / worker-2 / S2
        ↓
run_recovery_link(RUN-A -> RUN-B)
```

Do not smuggle worker changes into session replacement.

---

## 9. Helper and recovery interaction

A helper is not automatically a provider session and a provider session is not automatically a helper.

Keep the vocabularies separate:

```text
run
├── provider session chain
├── helper invocation(s)
└── recovery replacement run(s)
```

A helper may optionally record the exact parent provider session if the invocation occurred from one. A nested helper may point to `parent_helper_run_id`.

If a helper crashes before producing a result, the pre-invocation `run_helper_link` still proves that the invocation existed. That later enables progress-sensitive `NO_PROGRESS` analysis without a permanent watcher.

Recovery evidence should point to stable run/session/helper IDs where known. It should not reconstruct them from names after the fact.

---

## 10. Communication lineage and future explainable waits

The communication tranche should only establish exact request correlation.

It should **not** implement explainable waits yet.

Lineage first:

```text
run
→ request_id
→ addressee_ref
→ thread_ref
→ exact provider event ref when available
```

Then a later derived wait projection may ask:

```text
what is waiting?
what exact request/thread is relevant?
who/what is the addressee?
what resume condition is known?
what readiness evidence exists?
what remains UNKNOWN?
```

No mutable `waits` authority table is needed for the first version.

Do not parse arbitrary message prose to infer:

- assignment;
- acceptance;
- completion;
- ownership;
- approval;
- resume conditions.

---

## 11. Trace projection

`trace_task()` should remain a derived read.

Once implemented, add a bounded lineage section such as:

```text
lineage:
  runs:
    - run_id
      worker_id
      sessions:
        initial: ...
        extensions: [...]
        derived_endpoint: ... | UNKNOWN
      helpers: [...]
      outgoing_requests: [...]
      predecessor_run: ... | null
      replacement_runs: [...]
      submission_attempts: [...]
```

Each subsection needs explicit coverage metadata.

Suggested states, compatible with the prospective Run Record vocabulary:

```text
VERIFIED      exact source relationship was resolved
SOURCE_LOCAL  local correlation exists but external/provider confirmation is incomplete
MISSING       the source/mechanism does not exist for this record/version
UNKNOWN       source exists or may exist but attribution/completeness cannot be proven
```

Examples:

- manifest session ID present: `VERIFIED` initial binding;
- late link with exact provider result: `VERIFIED`;
- outbound request has run/thread/addressee but no validated hcom event ID: `SOURCE_LOCAL`;
- legacy helper result has task ID but no run link: `UNKNOWN`;
- old recovery incident has task/worker/session name only: `UNKNOWN`;
- no operation trajectory mechanism exists: `MISSING`.

Trace should never issue live provider mutations to fill gaps.

---

## 12. Portable Run Record projection

After PR #33 is accepted, Run Record can project lineage from Trace.

The derived record should include only bounded identifiers/metadata by default.

Expected improvement:

```text
session_helper_recovery_lineage:
  UNKNOWN/MISSING
        ↓
  VERIFIED/SOURCE_LOCAL per exact sub-source
```

Communication remains partial until exact provider-event correlation is proven.

`replay.complete` must remain `false` until all required operation/provider/helper/recovery trajectories are genuinely represented. Better lineage does not justify calling replay complete by itself.

---

## 13. Harness operation trajectory — defer from the first tranche

Prospective `OperationResult.operation_id` is useful, but the current draft service does not yet establish a durable pre-mutation operation record/ID contract.

Do not block core lineage on building a full execution log.

If evaluation evidence later requires it, add a separate bounded append-only operation-evidence tranche with fields no broader than:

```text
operation_id
run_id
operation
adapter
session_id?
result_code
ok
mutated
complete
retry
bounded evidence_refs
created_at/completed_at
```

Never persist raw payloads/provider transcripts by default.

For strong crash/post-mutation correlation, the service should own/generate the operation ID **before** mutation rather than inventing it only in a returned result.

This is useful follow-up, not permission to build a general event-sourcing platform.

---

## 14. Backward compatibility and migration

### Existing run manifests

- Do not rewrite or backfill `run_manifests`.
- Existing non-null `session_id` is the initial session in the derived chain.
- Existing null `session_id` remains `UNKNOWN` unless a future exact link is created from valid evidence.

### Existing helper results

- Existing helper records remain valid task-level helper evidence.
- No run/parent/session correlation is inferred.
- Trace/Run Record reports lineage `UNKNOWN` for those records.

### Existing recovery incidents

- Existing task/worker/session-name records remain valid RnS evidence.
- Do not backfill run IDs from worker/name/time heuristics.
- Future incidents can record exact lineage when the calling path has it.

### Existing submissions

- Existing `(task_id, submission_count)` attempts remain valid.
- Missing `submission_run_link` means run attribution is `UNKNOWN`.
- Do not use "only one run" as a backfill rule.

### Existing hcom history

- Do not bulk mirror/import the hcom event store.
- Historical correlation is only recovered when exact provider IDs/thread metadata make the join mechanical; otherwise preserve `UNKNOWN`.

### Schema migration style

If SQLite tables are added, follow the current additive `CREATE TABLE IF NOT EXISTS` pattern and add no-update/no-delete triggers for lineage tables.

No destructive migration is required for the proposed v1.

---

## 15. Security and privacy boundary

Lineage records should be boring.

Allowed by default:

```text
stable IDs
bounded relation/reason codes
timestamps
adapter/project identifiers
immutable hashes/evidence refs
```

Not allowed by default:

```text
message bodies
prompts
provider transcripts
raw helper outputs
raw submission evidence
credentials/secrets
arbitrary exception text
large free-form annotations
```

Use existing redaction/sensitive-text practices for any diagnostic projection, but prefer structured fields that do not need redaction.

A lineage relation can improve observability without becoming a surveillance/telemetry dump.

---

## 16. Behavioral acceptance tests for implementation

The eventual implementation should prove behavior, not source spelling.

### Session linkage

1. A run with null manifest `session_id` can accept one exact `ATTACHED` link only when task/run/worker/project checks and approved binding provenance pass.
2. The manifest remains byte-for-byte logically immutable after attachment.
3. A second same-run session requires `REPLACEMENT` and exact predecessor.
4. Branching/conflicting replacements are rejected.
5. A replacement using a different worker is rejected and requires a new run.
6. Session linking does not heartbeat, renew lease, claim task, alter review state, or grant approval.
7. Missing provider binding evidence yields explicit failure/`UNKNOWN`, not inferred success.
8. The harness guard resolves accepted late-session lineage after its integration tranche rather than requiring manifest mutation.

### Recovery

9. A replacement run can be linked to one predecessor run for the same task.
10. Different task IDs are rejected.
11. A recovery link does not imply same task revision, context, or review independence.
12. Existing `continuity_links` remain the separate source for continuity-based independent-review disqualification.

### Helpers

13. `helper_run_id` exists before helper side effect begins.
14. Helper link is durable even if helper completion/result is absent.
15. Helper result uses the same helper ID.
16. Parent helper must belong to the same run.
17. Raw helper output is absent from lineage storage.

### Communication

18. Request correlation is created from structured run/addressee/thread inputs, never message prose.
19. Message body is absent from lineage storage.
20. Missing provider event ID remains `SOURCE_LOCAL`/`UNKNOWN`.
21. An hcom `ack` alone does not change task/review/wait authority.
22. Provider/session liveness cannot mark a request complete.

### Submission

23. A run-bound submission link is written atomically with the exact submission count.
24. Mismatched task/run/worker is rejected.
25. Existing unlinked submissions remain valid with run attribution `UNKNOWN`.

### Trace / Run Record

26. Legacy unlinked helper/recovery/communication records do not become falsely `VERIFIED`.
27. Lineage projections contain IDs/refs, not raw private content.
28. Run Record remains deterministic for unchanged source evidence.
29. Replay remains explicitly incomplete while operation/provider trajectories are incomplete.

---

## 17. Recommended implementation sequence

Do not start these until the reviewer settles the relevant upstream interfaces.

### A0 — integration preflight

After #20-#24 and #33 receive dispositions:

- re-check current `main`;
- re-read exact accepted/final harness binding/session/guard interfaces;
- re-read exact accepted/final Run Record coverage shape;
- amend task details if interfaces materially differ from this prospective snapshot.

No code yet if upstream state is still moving.

### A1 — run/session lineage core

Smallest first implementation:

- append-only `run_session_links`;
- deterministic session-chain resolver;
- exact binding provenance requirements;
- guard integration with the resolver;
- Trace session-lineage projection;
- behavioral tests above.

Deliberate non-features:

- no new daemon;
- no provider start implementation merely to make tests pass;
- no helper/recovery/communication tables yet;
- no operation trajectory;
- no explainable waits.

### A2 — recovery + helper lineage

- append-only `run_recovery_links`;
- append-only `run_helper_links`;
- allocate helper ID before invocation;
- pass exact run identity into RnS/helper paths where mechanically available;
- preserve old unlinked evidence as `UNKNOWN`.

### A3 — submission-attempt lineage

- `submission_run_links`;
- explicit run-bound submit API path;
- transactionally bind `(task_id, submission_count)` to run;
- Trace/Run Record projection.

This tranche should compose with review-subject work rather than inventing a second review lifecycle.

### A4 — communication correlation

Before coding, perform a bounded hcom schema/evidence check for:

- stable event ID, if any;
- exact sender/addressee representation;
- thread identity/uniqueness;
- project-local scope.

Then add only the correlation fields that are actually supported.

If stable provider event identity is absent, keep `provider_event_ref = UNKNOWN` and do not fake one.

### A5 — bounded operation evidence, only if evaluation needs it

Add the minimal operation record described above when Run Record/regression evaluation demonstrates that missing operation trajectory materially limits diagnosis.

### Next capability after A4

With exact request/thread/addressee/session lineage in place, implement **explainable waits as a derived projection**, not as a new authority store.

---

## 18. Explicitly rejected designs

Do not revive these during implementation:

### Mutable task session pointer

```text
tasks.current_session_id
```

Rejected: duplicates/overwrites run/session truth and hides history.

### Updating immutable run manifests after launch

Rejected: destroys the exact run contract and review/replay identity.

### Generic universal lineage graph / blackboard

Rejected for v1: too easy to become an unbounded second state plane with weak per-relation invariants.

### hcom event mirror

Rejected: hcom already owns communication facts; copying the whole database adds drift/privacy risk.

### Timestamp/name inference

Rejected: current RnS ambiguity behavior already demonstrates it is not reliable enough.

### Session liveness as ownership/readiness/progress

Rejected: violates existing architecture and legacy evidence.

### Permanent process-police/watcher agent

Rejected: lineage should be written at existing deterministic transition points and read on demand.

### Automatic recovery/policy changes from lineage

Rejected: evidence does not self-authorize behavior.

---

## 19. Remaining `UNKNOWN`s

These are deliberately unresolved rather than guessed.

### U1 — exact hcom event identity schema

Current adapter proves JSON event objects and thread/agent/intent filtering, but not a validated stable event-ID/addressee schema.

Impact: communication correlation can record structured outbound request intent now in design, but exact provider-event verification requires a bounded evidence check before implementation.

### U2 — final reviewed attach/start semantics

PR #24 currently leaves hcom start/attach unsupported where durable session identity cannot be represented honestly.

Impact: A1 must integrate with the final accepted interface, not the current draft by assumption.

### U3 — final Run Record coverage schema

PR #33 is still draft.

Impact: lineage should expose exact structured evidence to Trace first; Run Record adaptation follows the final accepted read-model contract.

None of these unknowns require weakening the design or guessing.

---

## 20. Definition of done for the capability

Execution lineage is "good enough" when MAPS can answer the following for an exact run without name/time inference:

```text
Which task/revision is this run for?
Which worker owns the run identity?
Which provider session chain is explicitly associated with it?
Which helpers were invoked from it?
Which predecessor/replacement run relationships are explicit?
Which outbound requests belong to it, to whom, and on which thread?
Which exact submission attempt did it produce?
Which parts are still MISSING or UNKNOWN?
```

It is **not** required to answer:

```text
What did every message say?
What was every provider token/prompt?
Is a live process authorized to act?
Should MAPS automatically recover/promote/change policy?
```

That boundary keeps the capability useful without rebuilding the legacy supervisor/blackboard shape.

---

## 21. Recommended next action

1. Independently review this planning design.
2. Let the separate reviewer complete exact-head review of #20-#24 and #33.
3. Re-check accepted/final interfaces.
4. Shape **A1 — run/session lineage core** as the first implementation PR.
5. Do not begin explainable waits until communication/request lineage is exact enough to derive them honestly.
