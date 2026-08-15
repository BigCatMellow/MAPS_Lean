# Roadmap 01 — Harness Mechanics

Status: `PLANNING ONLY — NOT ACTIVE AUTHORITY`

Purpose: give MAPS a deterministic, provider-neutral control surface around workers and sessions so lifecycle behavior, authority checks, validation, evidence capture, and recovery do not depend on provider-specific code or an agent remembering procedural rules.

Source research themes:

- Prime-style Host/Runtime API
- Claude/Copilot lifecycle hooks
- SWE-agent ACI design
- aider/SWE-agent post-edit validation
- SWE-agent trajectories
- OpenTelemetry-style correlation semantics

---

# 1. Why this roadmap exists

MAPS already has task truth, claims, leases, run manifests, hcom, RnS, helpers, trace, outcomes, and policy. What it lacks is one narrow mechanical layer that says:

> Given a canonical task/run binding, what operations can the harness perform against a worker/session, what must be checked before the operation, and what structured evidence comes back?

Without this layer, orchestration tends to accumulate provider-specific branches and duplicated checks:

```text
if Claude: do X
if Codex: do Y
if local helper: do Z
```

and cross-cutting guarantees can drift because each code path implements them differently.

The target is not a new daemon. It is a **typed in-process contract plus adapters and hooks**.

---

# 2. Current MAPS baseline

Already available:

- canonical task lifecycle in SQLite;
- atomic claims/leases/heartbeats;
- immutable run manifests and context hashes;
- worker capability envelopes;
- hcom session transport;
- RnS recovery state;
- bounded helper lanes;
- explicit policy/approval state;
- trace/status/outcome evidence;
- secret-safer diagnostic paths.

These remain authoritative. Harness Mechanics wraps them; it does not replace them.

---

# 3. Target architecture

```text
CANONICAL TASK / POLICY / RUN
            │
            ▼
      HarnessService
            │
   ┌────────┼────────┐
   ▼        ▼        ▼
 HookBus  Adapter  Evidence
   │        │        │
   │        ▼        │
   │   Claude/Codex/ │
   │   hcom/helper   │
   │                 │
   └──────► normalized result
```

Important separation:

```text
HarnessService knows HOW to perform an operation.
Task/policy/run state determines WHETHER it is allowed.
Adapter knows HOW a provider/session represents it.
HookBus enforces deterministic cross-cutting checks.
```

---

# 4. Core entities

## 4.1 SessionRef

Minimum shape:

```text
session_id
worker_id
provider/adaptor kind
project_id
created_at / discovered_at
remote/local reference if needed
```

A SessionRef does not imply task ownership.

## 4.2 ExecutionBinding

References the already-authoritative run/task state:

```text
task_id
run_id
worker_id
session_id optional until attached
stable task revision
context/environment references
```

The binding must be explicit. Never infer it from “only active session.”

## 4.3 NormalizedSessionState

Candidate vocabulary:

```text
STARTING
RUNNING
WAITING
IDLE
STOPPING
STOPPED
FAILED
UNREACHABLE
UNKNOWN
```

Provider-specific states map into this vocabulary, but raw provider state may be retained as evidence.

`UNKNOWN` is required. Ambiguous state must not be coerced into RUNNING or FAILED.

## 4.4 OperationResult

Candidate envelope:

```json
{
  "ok": true,
  "code": "SENT",
  "summary": "Message accepted by session.",
  "data": {},
  "evidence_refs": [],
  "mutated": true,
  "complete": true,
  "next": null,
  "operation_id": "op-..."
}
```

Required semantic distinctions:

- transport success versus semantic completion;
- no output versus failure;
- partial/paginated versus complete;
- mutation versus read;
- retry-safe versus unsafe-to-repeat where relevant.

---

# 5. Harness API v1

Candidate operations:

```text
start(binding, launch_spec)
attach(binding, session_ref)
send(binding, payload)
inspect(binding/session_ref)
heartbeat(binding)
resume(binding)
stop(binding, reason)
collect(binding)
```

Not every adapter must support every operation. Unsupported operations return a structured `UNSUPPORTED` result, not an exception that masquerades as infrastructure failure.

## 5.1 start

Responsibilities:

1. verify task is executable and claim/run binding is current;
2. run `run_starting` hooks;
3. call adapter start;
4. persist/associate the explicit session ID using the appropriate existing evidence mechanism;
5. run `run_started` hooks;
6. return a normalized result.

Idempotency rule:

- if start acknowledgement is lost but a matching explicit session reference is later discovered, do not create a duplicate run blindly;
- require adapter idempotency key or explicit reconciliation evidence.

## 5.2 attach

Used when a known session exists and must be bound to a run.

Must verify:

- worker identity matches binding expectations;
- session is not already bound incompatibly;
- task/run state still allows continuation;
- no authority is gained by attachment itself.

## 5.3 send

Before sending task-changing or privileged instructions:

- confirm run/task binding current;
- run applicable hooks;
- preserve operation ID and result.

Transport acceptance does not prove worker execution.

## 5.4 inspect

Read-only.

Should return:

```text
normalized state
provider raw state
last activity timestamp if reliable
session identity
known wait/request metadata if structured
coverage/confidence notes
```

No inferred ownership.

## 5.5 heartbeat

Separate two concepts:

```text
task claim heartbeat
session/process liveness
```

They may correlate but are not equivalent.

## 5.6 resume / recover

`resume` asks the adapter to continue a known compatible session.

`recover` remains governed by RnS rules. The Harness API should call or normalize recovery behavior, not duplicate RnS retry policy.

## 5.7 stop

Stopping a session is consequential.

Required checks:

- caller/task authority;
- target session identity;
- whether stop is destructive relative to uncollected work;
- hook/policy result;
- explicit reason.

A stop must never be triggered only because a dashboard thinks a task is stale.

## 5.8 collect

Collect result/evidence without granting completion authority.

May include:

```text
provider final status
artifact references
structured output references
operation timeline reference
usage/cost summary where available
```

Task submission/review still uses canonical MAPS transitions.

---

# 6. Hook / interceptor framework

## 6.1 Goal

Make deterministic cross-cutting behavior run because an event occurred, not because an agent remembered to do it.

## 6.2 Initial events

```text
run_starting
run_started
before_tool
after_tool
before_write
after_write
before_external_action
before_destructive_action
before_send
submission_created
review_starting
review_completing
session_stopping
run_failed
```

Do not add dozens of events up front. Add events only where a real invariant or validation needs a stable interception point.

## 6.3 Hook outcomes

```text
ALLOW
DENY(reason)
REQUIRE_APPROVAL(reason)
ANNOTATE(evidence)
```

Potential combined result should preserve every blocking reason rather than only the first when safe to do so.

## 6.4 Authority rule

Hooks may:

- deny;
- require existing approval;
- annotate;
- trigger deterministic validation;
- narrow capabilities.

Hooks may not:

- claim a task;
- approve operator-required actions;
- widen write scope;
- mark DONE;
- grant a capability the task/policy did not authorize.

## 6.5 Registration

Start with an in-process ordered registry.

Each hook declares:

```text
hook_id
event
priority/order if truly required
side-effect class: read-only | evidence-write | guarded mutation
failure policy
```

Avoid plugin/event-bus infrastructure until extension needs prove it.

---

# 7. First hooks to implement

## 7.1 Scope guard

Before write/tool operations with filesystem mutation:

- compare target path to run writable/forbidden scope;
- deny outside scope;
- record concise evidence.

## 7.2 Destructive/external policy guard

Before consequential actions:

- inspect task policy;
- require operator approval if configured;
- deny if caller lacks task authority.

## 7.3 Immediate mutation validator

After relevant edits:

```text
.py     → compile/lint command if declared
.json   → parse
.yaml   → parse
schema  → schema-specific validator
policy  → property/security tests where configured
```

Validation commands should come from EnvironmentSpec/Skill/task metadata, not arbitrary hidden defaults.

## 7.4 Diagnostic redaction hook

Before diagnostic/event persistence:

- apply current secret-safety boundary;
- preserve explicit redaction markers.

## 7.5 Evidence correlation hook

Ensure operation/run/session/task IDs are attached to emitted telemetry/evidence.

---

# 8. ACI quality standard

Every agent-facing operation should be reviewed as an interface, not just a function.

Checklist:

- Is success/failure explicit?
- Is no-result distinct from failure?
- Is output bounded?
- Is pagination explicit?
- Are IDs stable?
- Does the result say whether state mutated?
- Can consequential actions be distinguished from safe reads?
- Are errors actionable without dumping logs into context?
- Does the result preserve enough evidence to verify important claims?
- Can the agent avoid parsing prose to discover machine state?

Bad:

```text
Done.
```

Good:

```json
{
  "ok": true,
  "code": "WRITE_APPLIED",
  "mutated": true,
  "paths": ["runtime/foo.py"],
  "validation": {"code": "COMPILE_OK"}
}
```

---

# 9. Operation telemetry and lineage

Every harness operation should have an `operation_id` and explicit references where applicable:

```text
task_id
run_id
worker_id
session_id
operation_id
parent_operation_id optional
tool/capability identifier
started_at
completed_at
result code
mutation flag
evidence refs
```

Do not automatically store full prompts/tool payloads as telemetry. Sensitive/raw content requires separate explicit evidence handling.

---

# 10. Run Record integration

Harness Mechanics should emit enough structured evidence for the later portable Run Record.

Minimum operation stream:

```text
run start
session attach/start
messages/tool operations
validation outcomes
helper/recovery child links
submission boundary
stop/failure/completion observation
```

The Run Record is a derived export, not the primary event database.

---

# 11. Failure modes

## 11.1 Remote session started but start response lost

Required behavior:

- do not blindly start another;
- use idempotency key/provider reconciliation if available;
- otherwise surface `UNKNOWN_START_RESULT` and require safe inspection/reconciliation.

## 11.2 Session alive but task authority revoked/reshaped

Required behavior:

- liveness does not restore authority;
- next consequential operation fails current-binding check;
- status/trace may show orphaned/stale session evidence.

## 11.3 Adapter says RUNNING but transport unreachable

Return raw and normalized uncertainty, for example `UNREACHABLE`, not assumed RUNNING.

## 11.4 Hook crashes

Default for security/authority hooks: fail closed for the guarded action and record the hook failure.

Default for purely observational hooks: operation may continue if policy explicitly allows fail-open behavior.

Hook failure semantics must be declared, not implicit.

## 11.5 Post-write validation fails

Do not automatically revert arbitrary work.

Return structured validation failure to the worker and preserve changed-path evidence. Recovery/repair remains task-scoped.

## 11.6 Duplicate operation request

Where safe, operation IDs/idempotency keys should return prior result or explicit duplicate status.

For operations unsafe to repeat, return `REQUIRES_RECONCILIATION` rather than retrying automatically.

---

# 12. Security requirements

- adapter/provider credentials do not become task text;
- hooks cannot invent authority;
- operation telemetry is secret-safer and content-minimal by default;
- stop/kill/external/destructive operations receive explicit guards;
- provider session identifiers are untrusted inputs until validated;
- tool output cannot change task authority;
- cross-project session attachment is rejected;
- session identity collisions must be detectable.

---

# 13. Testing strategy

## 13.1 Unit tests

- state normalization;
- OperationResult semantics;
- hook ordering/combination;
- DENY/REQUIRE_APPROVAL behavior;
- unsupported adapter operations;
- idempotency handling;
- scope guard;
- immediate validation routing.

## 13.2 Contract tests

Every adapter must pass the same suite for supported operations.

Examples:

- inspect returns stable session identity;
- no-output success is not failure;
- unsupported stop returns `UNSUPPORTED`;
- duplicate start behavior defined;
- failed transport cannot be reported as semantic success.

## 13.3 Integration tests

- task claim → run manifest → harness start → attach → send → collect;
- session survives process restart if adapter supports it;
- reshaped task blocks stale continuation;
- RnS recovery remains bounded;
- helper child operations preserve lineage.

## 13.4 Adversarial tests

- forged session ID;
- old session after task revision change;
- provider output claiming approval;
- malicious tool output trying to widen scope;
- hook failure during destructive request;
- duplicate send/start under network ambiguity.

---

# 14. Metrics

Measure whether the harness improves reliability rather than activity.

Useful metrics:

- ambiguous operation-result rate;
- duplicate-session incidents;
- stale-session continuation attempts blocked;
- tool calls repeated because prior result was unclear;
- post-write validation failures caught before submission;
- mean operator interventions per run;
- recovery success without duplicate work;
- percentage of traceable operations with complete correlation IDs.

Avoid optimizing:

- number of hook invocations;
- number of tool calls;
- number of sessions;
- raw message volume.

---

# 15. Implementation phases

## H1 — Result envelope and state vocabulary

Build:

- `OperationResult`;
- normalized session-state enum;
- stable operation IDs;
- ACI checklist/tests.

Exit gate: existing/read-only sample adapter can produce unambiguous structured results.

## H2 — Harness interface + one adapter

Build the typed interface and wrap the simplest current provider/session path first.

Exit gate: start/inspect/send/collect behavior works without provider-specific orchestration branches in the caller.

## H3 — Hook registry

Implement in-process hooks and the first authority/scope hooks.

Exit gate: security/authority regression tests prove hooks can block but cannot grant authority.

## H4 — Immediate validation hooks

Connect EnvironmentSpec/task/Skill-declared validators.

Exit gate: representative syntax/parse failures are caught immediately after mutation.

## H5 — Remaining adapters + contract suite

Migrate current provider/helper/session mechanisms incrementally.

Exit gate: all supported adapters pass shared contracts.

## H6 — Lineage/trace integration

Attach operation/session evidence to richer trace/Run Record projections.

Exit gate: a run can be reconstructed without provider-specific manual archaeology.

---

# 16. Concrete task backlog

Suggested individually shapeable tasks:

1. Define normalized operation-result schema.
2. Define normalized session-state vocabulary.
3. Implement Harness interface skeleton.
4. Wrap hcom session adapter.
5. Add adapter contract test harness.
6. Add stable operation IDs.
7. Implement HookResult and in-process registry.
8. Implement run/task binding guard hook.
9. Implement write-scope hook.
10. Implement destructive/external policy hook.
11. Implement immediate file-validation hook interface.
12. Add ACI quality checklist to review guidance.
13. Normalize helper adapter behavior where appropriate.
14. Normalize recovery-facing operations without replacing RnS.
15. Add operation telemetry projection.
16. Extend trace with explicit operation/session lineage.
17. Add failure-injection tests for ambiguous starts and stale sessions.

---

# 17. Definition of done

Harness Mechanics v1 is done when:

- orchestration can control supported workers/sessions through one typed interface;
- adapters expose provider differences without leaking them into task authority logic;
- consequential operations re-check canonical binding/policy;
- deterministic hooks can block/validate operations independent of model memory;
- tools return bounded, machine-readable, unambiguous results;
- immediate cheap validation catches representative errors near mutation time;
- operation/run/session IDs make lineage reconstructable;
- failure/ambiguity produces explicit UNKNOWN/reconciliation states instead of guesses;
- no daemon, second task store, or new authority system was introduced.
