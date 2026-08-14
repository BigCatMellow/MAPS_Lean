# RnS Recovery

Rise & Shine (RnS) recovers **known sessions for already-active work**.

It does not allocate work.

```text
ACTIVE MAPS task + existing claim
        │
        ├─ explicit worker → hcom session binding
        │
        ▼
known session stops / scheduled resume becomes due
        │
        ▼
RnS verifies task is still ACTIVE and claim still matches
        │
        ├─ mismatch / terminal session → suppress
        ├─ session already live → resolve
        └─ stopped + due → hcom resume (headless) → bounded backoff
```

## Durable state

Default:

```text
.maps/state/recovery.json
```

It records incidents, retry timing, prior liveness observations, and terminal
session suppression. It is recovery state, not task authority.

## Silent-stop rule

RnS does not treat every missing/stopped hcom row as something to resurrect.
A silent-stop incident opens only when:

1. the MAPS task is currently `ACTIVE`;
2. the task has an existing claimant;
3. an explicit worker→session binding exists;
4. that session was previously observed live; and
5. it is now observed not-live.

First observation of an already-dead session does not create an incident.

## Liveness

Live hcom statuses are `active`, `listening`, `waiting`, and `blocked`.
When hcom supplies `process_bound`, it wins: a stale displayed status with no
process is not live. Otherwise RnS falls back to a bounded status-age heuristic.

## Retry

Default retry delays:

```text
5m → 15m → 30m → 60m → 120m → fail
```

This prevents resume spam. A successful resume command moves the incident to
`probing`; a later live observation resolves it.

## Terminal sessions

These are explicitly suppressible:

```text
session_superseded
disposable_session_ended
```

RnS never resurrects them.

## Authority boundary

RnS may read task state. It must not call task mutations such as:

```text
claim_task
promote_ready
update_contract
submit_task
record_review
```

If the task is gone, no longer ACTIVE, or its claimant changed, recovery is
suppressed. RnS does not repair that by stealing or rewriting the claim.

## WezTerm

No terminal multiplexer is required. The active path resumes through the hcom
adapter with headless mode; presentation can be added separately by an operator.
