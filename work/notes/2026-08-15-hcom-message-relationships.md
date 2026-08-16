# hcom provider-local message relationship projection

Status: `IMPLEMENTED ON STACKED DRAFT BRANCH — DERIVED COMMUNICATION EVIDENCE ONLY`

Branch: `agent/hcom-message-relationships-wave3`

Base dependency: PR #44 exact head `4e10f8dadcd64e7b91fb8d608b92f268fde00821`.

## Purpose

Use the stable, body-free metadata exposed by the full-fidelity hcom read to derive provider-local communication relationships without pretending that communication alone establishes task/run ownership or operator attention state.

This is the second bounded A4 prerequisite:

```text
A4a — read exact full-fidelity message metadata   (#44)
A4b — resolve exact provider-local relationships (this tranche)
A4c — later join to accepted task/run lineage
A4d — only then derive explainable waits
```

## Input boundary

Input must be the normalized PR #44 event shape and must explicitly assert:

```text
full_fidelity_read: true
message_body_included: false
```

The resolver rejects non-full/body-including input rather than silently accepting a weaker evidence source.

Each input event carries stable metadata such as:

```text
event_id
sender
delivered_to
intent?
thread?
reply_to_local?
```

No message text is needed.

## Exact relationships

### Delivery

Every explicit `delivered_to` recipient becomes a delivery edge:

```text
event_id
sender
recipient
```

No addressee is inferred from message text.

### Reply

Only explicit `reply_to_local` creates a parent/child reply link.

If the parent event exists in the bounded input:

```text
parent_state: IN_INPUT
```

If it does not:

```text
parent_state: PARENT_NOT_IN_INPUT
```

The latter does not mean the parent is invalid or nonexistent globally; it may simply be outside the bounded read window.

### Thread

Events are grouped into a thread only when the explicit `thread` field is present and equal.

Critical boundary:

> Same-thread membership is grouping evidence, not reply evidence.

A later message in the same thread without `reply_to_local` is not counted as a response to a specific request.

## Request and ack observations

A request exists only when hcom explicitly records:

```text
intent: request
```

For each explicit request, the projection lists exact child events whose `reply_to_local` references that request.

An ack is counted only when an exact child also has:

```text
intent: ack
```

Request summary fields:

```text
request_event_id
thread
delivered_to
response_event_ids
ack_event_ids
response_observation
ack_observation
```

Observation values are intentionally bounded:

```text
OBSERVED_IN_INPUT
NOT_OBSERVED_IN_INPUT
```

There is deliberately no:

```text
PENDING
WAITING
TIMED_OUT
ABANDONED
```

## Why absence is not a wait state

A bounded event read may omit:

- older parent requests;
- newer replies beyond the selected window;
- remote/device communication not represented in the local input;
- task/run correlation evidence from another source.

Therefore:

```text
no ack observed in this input
```

cannot honestly become:

```text
this task is waiting on agent B
```

The projection explicitly records:

```text
absence_is_not_global_negative: true
wait_state_included: false
```

This preserves UNKNOWN until later coverage/correlation can prove more.

## Determinism

Events are sorted by stable event ID before relationships are built.

Input order therefore does not change:

- reply links;
- delivery edges;
- thread groups;
- request summaries.

Duplicate event IDs fail closed rather than introducing an arbitrary winner.

## Corrupt/ambiguous evidence

The resolver rejects:

- malformed event shape;
- duplicate event IDs;
- invalid explicit intent;
- self-reply via `reply_to_local`;
- input that no longer preserves the body-free/full-fidelity contract.

It does not repair or infer around corrupted evidence.

## Authority boundary

The projection states:

```text
kind: DERIVED_COMMUNICATION_EVIDENCE
can_grant_task_authority: false
can_grant_session_authority: false
can_grant_review_or_approval: false
```

It also explicitly states:

```text
task_run_correlation_included: false
wait_state_included: false
```

## What this unlocks later

Once A1/A2/A3 execution lineage has an accepted representation, A4c can attempt exact joins such as:

```text
task/run explicit communication binding
        ↓
hcom request event_id
        ↓
exact delivery/reply/thread evidence
```

Only after those joins have coverage semantics can a wait projection safely ask:

```text
what obligation is unresolved?
who/what is it waiting on?
what exact request proves that?
```

This tranche intentionally stops before that boundary.

## Verification cases

Tests prove:

- exact request→ack via `reply_to_local`;
- same-thread message without reply is not a response;
- no ack in bounded input is not pending/waiting;
- parent outside input is preserved explicitly;
- exact sender/recipient fan-out;
- explicit-only thread grouping;
- input-order determinism;
- duplicate IDs fail closed;
- self-reply fails closed;
- invalid intent fails closed;
- non-full/body-including input fails closed;
- projection cannot grant authority.
