# hcom full-fidelity message lineage read

Status: `IMPLEMENTED ON ISOLATED DRAFT BRANCH — COMMUNICATION EVIDENCE ONLY`

Branch: `agent/hcom-lineage-read-wave3`

Base: `main@1652d515a5b991b1ed07c7f2e624fea95927ddfb`.

Upstream evidence checked: hcom release `v0.7.25`, commit `79ebde134c4d29b5ba64e5c9839a12bedb7ee125`.

## Why this exists

The execution-lineage design identified a concrete gap between what hcom stores and what MAPS currently reads.

Current MAPS `HcomAdapter.read_events()` invokes ordinary:

```text
hcom events ...
```

Upstream hcom intentionally streamlines that output. In v0.7.25, `streamline_event()` removes universal `delivered_to`, removes message `reply_to`, and may remove `mentions` when not requested as a filter.

Upstream also exposes:

```text
hcom events --full
```

which skips that streamlined projection.

Therefore a future request/thread/addressee lineage implementation should use a dedicated full-fidelity read path rather than silently assuming ordinary event output is complete.

## Important upstream nuance

Reading hcom's `send_message()` source corrected an overly strict initial design assumption.

Every message event is built with:

```text
from
scope
text
delivered_to
```

but these fields are conditional:

```text
mentions
intent
reply_to
reply_to_local
thread
```

For example, an ordinary informational direct message may have no explicit `intent`, no thread, and no reply relationship.

Therefore:

> Missing optional correlation fields are not protocol failure and must not be invented/defaulted.

The reader records field presence explicitly.

## Implementation

`HcomLineageAdapter` subclasses the existing narrow `HcomAdapter` so the original lightweight path remains untouched.

### Full message read

```text
read_message_lineage(last, intent?, agent?, thread?)
```

invokes:

```text
hcom events --last N --full --type message ...
```

using the same bounded `last` range and identifier/intent validation style as the existing adapter.

It requires core provider evidence:

```text
event.id
event.ts
event.instance
data.from
data.delivered_to
```

It optionally preserves, only when actually present:

```text
data.mentions
data.intent
data.thread
data.reply_to
data.reply_to_local
```

The projected record uses:

```text
event_id
timestamp
instance
sender
delivered_to
mentions?
intent?
thread?
reply_to?
reply_to_local?
coverage.field_presence
```

## Message body exclusion

Although `hcom events --full` contains message text, MAPS' lineage projection deliberately does not copy it.

Coverage explicitly reports:

```text
source: hcom events --full
full_fidelity_read: true
message_body_included: false
```

This keeps the future lineage layer focused on correlation rather than creating another message/transcript persistence surface.

## Absence vs UNKNOWN/default

For optional fields, the result contains both the projected nullable value and a presence bit.

Example ordinary message:

```text
intent: null
thread: null
reply_to: null

field_presence:
  intent: false
  thread: false
  reply_to: false
```

This means:

> hcom did not store/expose this field on this event.

It does **not** mean:

> MAPS inferred an `inform` intent or proved there was logically no surrounding workflow relationship.

That distinction matters for honest request/wait reconstruction.

## Capability probe

`probe_lineage_capability()` does not trust `hcom --version`.

It runs a bounded real:

```text
hcom events --full --type message
```

and returns:

### No message rows

```text
state: UNKNOWN
core_fields_verified: false
```

The CLI accepted the query, but MAPS has no returned event with which to prove the metadata shape.

### Valid message rows

```text
state: SUPPORTED
core_fields_verified: true
observed_message_events: N
observed_optional_fields: [...]
```

Only optional fields actually observed in returned events appear in `observed_optional_fields`.

This is preferable to:

```text
version >= X
→ assume all message lineage fields work
```

because installed builds/configurations can still differ and optional fields depend on actual message semantics.

## Fail-closed boundaries

The reader rejects:

- non-JSON full records;
- non-message records from the message query;
- missing/invalid event IDs;
- missing timestamps/instances;
- missing sender or delivery metadata;
- malformed delivery/mention lists;
- unsupported explicit intent values;
- invalid reply identifiers;
- invalid filter arguments.

It does not guess around those failures.

## What this does not establish

Even exact provider message metadata does not establish:

- task ownership;
- a live claim/lease;
- permission to continue;
- review authority;
- operator approval;
- which task/run a message belongs to;
- provider/API readiness;
- whether an unanswered request should count as a wait.

Those require future A4 correlation against accepted canonical lineage/task evidence.

## Intended future use

After execution/session lineage interfaces are accepted, a later A4 adapter can join explicit identifiers:

```text
task/run
↕ explicit correlation evidence
hcom event_id
thread
sender
delivered_to
reply_to_local
```

and preserve `UNKNOWN` wherever no stable join exists.

This read path removes one prerequisite without prematurely creating that join or another authority store.

## Verification cases

The fake-hcom suite covers:

- `--full --type message` invocation with bounded filters;
- body-free projections;
- ordinary messages with absent optional fields;
- rich thread/request/reply metadata;
- no-message capability => UNKNOWN;
- observed optional-field capability reporting;
- missing core delivery metadata failure;
- malformed JSON failure;
- unsupported returned intent failure;
- invalid filters rejected before subprocess execution;
- no task-store/authority dependency.
