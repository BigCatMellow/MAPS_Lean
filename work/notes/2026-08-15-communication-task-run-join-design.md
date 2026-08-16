# A4c exact communication task/run join — design note

Date: 2026-08-15/16
Owner: `agent/communication-task-run-join-design-wave3`
Status: planning evidence only

## Why this lane exists

A1, A2, and A3 execution-lineage work is being handled by other agents. This lane deliberately avoids their schema/runtime branches and answers the remaining A4c question:

> What exact evidence is sufficient to say a provider communication event belongs to a particular MAPS run?

The answer must survive concurrency, retries, multiple sessions, same-thread traffic, and provider-local identifiers without using message prose or timestamp guesses.

## Current prospective pieces

### A1 — run/session

PR #48 currently proposes adapter-qualified, append-only run/session relationships. This can prove that run `R` currently targets provider session `(adapter, session_id)` without mutating the immutable run manifest.

This is necessary but not sufficient to identify a particular communication event.

### A4a — full-fidelity hcom event read

PR #44 projects exact hcom message metadata from `hcom events --full`:

- event ID;
- provider instance;
- sender;
- `delivered_to`;
- optional intent/thread/reply fields when present;
- no message body.

### A4b — provider-local relationships

PR #45 derives only relationships hcom explicitly proves:

- delivery edges from `delivered_to`;
- reply edges from `reply_to_local`;
- request/ack classification from explicit intent;
- same thread is grouping only, not reply evidence;
- bounded absence is `NOT_OBSERVED_IN_INPUT`, not `PENDING` or `WAITING`.

Neither #44 nor #45 attributes an event to a MAPS task/run.

## Direct upstream hcom finding

Pinned source inspected: `aannoo/hcom@79ebde134c4d29b5ba64e5c9839a12bedb7ee125`, `src/commands/send.rs`.

Inside `send_message()` hcom performs:

```rust
let _event_id = db
    .log_event("message", &routing_instance, &data)
    ...?;
```

That value is a real provider-issued event identity. hcom then uses `_event_id` when creating targeted request watches.

However, `send_message()` returns:

```rust
Result<Vec<String>, String>
```

where the vector is `delivered_to`. `cmd_send()` receives only that recipient list. Normal CLI feedback prints recipient information; quiet mode prints nothing. The newly written event ID is not returned to the caller.

Therefore current MAPS `HcomAdapter.send()` / `HcomHarnessAdapter.send()` cannot know which exact hcom event was created by a successful send.

## Why the obvious joins are unsafe

### "Use the session ID"

A run/session link identifies a provider session, not a message event. One session can have many messages.

### "Use the hcom instance name"

Instance/name identifies an actor or routing endpoint, not one event. It is also not the same field as A1's provider-local session ID.

### "Read the latest event after sending"

Unsafe under concurrent sends. Another process can write between the send and read-back.

### "Match sender + recipient + timestamp"

Still ambiguous under concurrent/retried sends and creates probabilistic identity from timing.

### "Match thread + intent"

Multiple messages may share both. Thread membership is explicitly not reply identity.

### "Hash the message text"

Bodies are intentionally excluded from MAPS communication lineage, duplicate messages are valid, and using body content would violate the privacy/evidence boundary.

### "The next reply proves which request it answered"

`reply_to_local` proves a child→parent provider-event edge, but only helps MAPS after the parent event itself has an exact MAPS root correlation.

## Exact-correlation rule

A provider event is attributable to a MAPS run only when an explicit cross-source relationship contains the exact provider event reference.

Conceptually:

```text
MAPS run R
  │
  │ explicit cross-source root link
  ▼
hcom event E
  │
  ├── exact reply_to_local child E2
  └── exact reply_to_local child E3
```

Then `E2`/`E3` may inherit communication ancestry from `R` as a derived read model.

Without the root `R ↔ E` link:

```text
same session/name/thread/time/text
        ≠
exact task/run attribution
```

## Smallest provider change needed

Preferred hcom-side contract:

1. preserve existing human `hcom send` output;
2. expose an explicit structured send mode, e.g. `hcom send --json ...`;
3. have `send_message()` return a receipt rather than only recipient names;
4. receipt includes the exact event ID returned by `db.log_event()`.

Minimum conceptual receipt:

```json
{
  "event_id": 123,
  "delivered_to": ["agent-b"]
}
```

A richer receipt could also report thread/intent, but MAPS does not need to persist copies of those fields because hcom owns them and #44 can read them later.

The critical field is the provider event reference.

## MAPS send-boundary behavior after that capability exists

A future MAPS implementation should behave approximately as follows:

```text
canonical task/run authority check
        ↓
accepted A1 exact target session relation
        ↓
(optional) allocate MAPS request/operation ID before send
        ↓
hcom structured send
        ↓
provider returns exact event receipt
        ↓
validate receipt
        ↓
append MAPS↔provider-event cross-source link
        ↓
derive provider event details from hcom at read time
```

No event ID returned means no exact communication attribution.

## Relationship ownership

### MAPS may own

Only the relationship hcom cannot own itself:

- this MAPS run/request caused or intentionally adopted this exact hcom event;
- optionally, this exact run-session relationship was the target context for the operation;
- creation/evidence metadata for that cross-source assertion.

### hcom continues to own

- event ID within its namespace;
- sender/instance;
- recipients;
- message body;
- intent;
- thread;
- reply links;
- event time;
- delivery/provider state.

### task state continues to own

- task lifecycle;
- claimant/lease;
- run/task authority;
- review/operator approval.

The communication link grants none of those authorities.

## Suggested future schema concept

Do not freeze exact spelling until A1/A3 settle. The relationship is roughly:

```text
run_communication_event_links
  run_id
  optional request_or_operation_id
  optional run_session_link_id
  transport/provider = hcom
  provider_event_ref
  evidence_ref
  created_by
  created_at
```

Important constraints:

- append-only;
- exact run exists;
- exact provider reference is unique within its provider namespace;
- no body column;
- no mutable delivery/status column;
- no task status/claim copy;
- no "pending" bit;
- no inference-based backfill.

## Event namespace

The provider event reference must include enough scope to avoid false uniqueness.

hcom local event IDs are local database IDs. hcom also supports remote references such as reply IDs with device suffixes (`42:BOXE`). Therefore runtime implementation must not assume integer `42` is globally unique across all hcom devices/stores.

Possible stable forms, to be verified before implementation:

```text
hcom:<local-provider-scope>:123
```

or a provider-native event reference if hcom exposes one.

For a local-only first tranche, the configured hcom state/project boundary can be made explicit in the relationship evidence. Remote events remain unsupported/UNKNOWN until the device namespace is preserved exactly.

## Outbound vs inbound correlation

### Outbound root

The most reliable root is a MAPS-controlled send that receives event ID `E` from hcom. MAPS can record `run R ↔ event E` immediately after the provider mutation.

### Inbound response

If hcom later reports event `E2` with `reply_to_local = E`, #45 can prove `E2` is a reply descendant of `E`. MAPS can derive that `E2` belongs to the same communication lineage as run `R`.

This does **not** mean `E2` grants task authority or that the responder is a valid reviewer/operator.

### Unsolicited inbound event

An inbound event with no exact linked ancestor is not attributable to a run merely because its sender/recipient happens to match a known session. It remains provider communication evidence with run attribution `UNKNOWN` unless a separate explicit adoption/link operation is designed and authorized.

## Cross-system atomicity and crash window

hcom and MAPS SQLite are separate systems. An exact send receipt improves attribution but does not create a distributed transaction.

Possible sequence:

```text
provider event E created
        ↓
receipt E returned
        ↓
MAPS root link append
```

Crash cases:

- before provider event creation: no event, no link;
- event created but process dies before receipt reaches MAPS: event exists, run attribution unknown;
- receipt received but process dies before link append: event exists, run attribution unknown unless receipt is durably captured elsewhere;
- root link appended: exact correlation established.

Do not recover the unknown cases by "closest timestamp" or "latest matching message".

A stronger future protocol could allocate a MAPS `client_ref` before send and have hcom store/echo it in the event. That would support exact read-back after a crash. Current hcom message schema does not provide this generic correlation field, so it is a separate capability, not assumed here.

## Capability detection

MAPS should not optimistically call old hcom send and then discover the event ID is missing after the mutation.

A future structured-send implementation needs a non-mutating capability check first. Options include:

- inspect `hcom send --help` for an accepted structured-output flag, then require parseable structured output on the authorized send;
- preferably, use an explicit hcom capability command if upstream eventually provides one.

If capability cannot be established, fail before send with a bounded unsupported/correlation-unavailable result.

Do not fall back to the old uncorrelated send when exact lineage is required, because that would perform the side effect and then leave attribution ambiguous.

## Relationship to HcomHarnessAdapter

Current HcomHarnessAdapter resolves the binding session to an hcom session record and sends to that record's `name`. Its success result currently includes `session_id` and `remote_name`, but not provider event ID.

Those fields prove which provider session/target was selected. They do **not** prove which event was written.

After structured-send support exists, the adapter's success data should carry a validated provider event reference/receipt so the state/integration layer can append the root communication relationship.

## Relationship to A3

A3 submission lineage is owned by another agent and should not be coupled prematurely.

If A3 or a future operation layer exposes a stable request/operation ID, A4c can reference it. Otherwise `run_id + exact provider event ref` is sufficient for the first communication-root relationship.

Do not invent a second request lifecycle solely for A4c unless evidence shows it is necessary.

## Relationship to explainable waits (A4d)

A4d may only reason about waiting after communication coverage is trustworthy.

Valid future evidence might be:

```text
run R
→ exact request event E
→ exact addressee(s) from hcom
→ no exact reply descendant observed through a declared observation boundary
```

Even then, "not observed" is not automatically a task-global wait. A wait state needs an explicit task/run dependency or operation state saying progress requires that response.

Thus:

```text
no reply in bounded hcom window
        ≠
WAITING
```

and:

```text
exact request + explicit dependency + declared observation semantics
        →
possible explainable wait evidence
```

## Tests for future implementation

Minimum behavioral tests:

1. exact structured send receipt creates one root run↔event relationship;
2. missing event ID fails closed rather than timestamp-matching;
3. duplicate provider event ref cannot be rebound ambiguously;
4. session/name/thread/timestamp-only candidate never auto-links;
5. exact `reply_to_local` child inherits communication ancestry only after the parent is exactly linked;
6. same-thread non-reply does not inherit ancestry;
7. unsolicited inbound event remains run `UNKNOWN`;
8. message body never appears in durable MAPS lineage;
9. remote/local event namespace collision is rejected or remains unsupported;
10. crash-gap fixture remains `UNKNOWN` and is not heuristically repaired;
11. communication link changes no task claimant, lease, status, review, or approval state;
12. bounded lack of reply does not create `PENDING`/`WAITING` by itself.

## Multi-agent boundary

At creation time:

- A1 PR #48 is actively owned elsewhere;
- A2 PR #49 is actively owned elsewhere;
- A3 branch `agent/submission-run-lineage-wave3` exists and is actively occupied;
- #44/#45 are separate communication prerequisite branches.

This design branch modifies none of those branches and intentionally avoids `runtime/state/schema.sql`, `runtime/state/store.py`, or any runtime implementation path.

## Recommended continuation

```text
A1/A2/A3 settle
#44/#45 settle
        ↓
re-check exact accepted interfaces
        ↓
hcom structured send receipt / exact event ID capability
        ↓
A4c root run↔provider-event link
        ↓
exact reply-descendant projection
        ↓
trace / Run Record communication coverage
        ↓
A4d explainable waits
```

Until the provider event receipt exists, A4c runtime correlation is correctly **BLOCKED_ON_PROVIDER_EVENT_ID_EXPOSURE**, not an invitation to infer.
