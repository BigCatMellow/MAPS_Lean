# Task: communication task/run join Wave 3 design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `ARCHITECTURE`
- Owner: `agent/communication-task-run-join-design-wave3`
- Risk: `MEDIUM`
- Goal: Freeze the smallest exact-evidence contract for joining hcom communication events to MAPS runs without inference, message-body copying, or duplicate task/provider truth.

## Inputs and source of truth

- Root `AGENTS.md` and its one-fact/one-authority, `UNKNOWN`, and multi-agent ownership rules.
- Current merged `main@c787d26607da517349c1abdb47b72794e2d90ef5`.
- PR #44 `agent/hcom-lineage-read-wave3@4e10f8dadcd64e7b91fb8d608b92f268fde00821` as prospective full-fidelity hcom read behavior.
- PR #45 `agent/hcom-message-relationships-wave3@803db6e404a7a5256acda1c4b90648afb8e17933` as prospective provider-local reply/thread/delivery behavior.
- PR #48 `agent/run-session-lineage-wave3@13b3293781a43980066f642edb79cf7f4528d4aa` as prospective A1 adapter-qualified run/session behavior.
- PR #49 and branch `agent/submission-run-lineage-wave3` are active parallel-agent work and are not modified by this task.
- Upstream `aannoo/hcom@79ebde134c4d29b5ba64e5c9839a12bedb7ee125`, especially `src/commands/send.rs`.

Authoritative evidence ordering:

1. merged MAPS code for accepted MAPS behavior;
2. exact open PR heads only as prospective interfaces;
3. exact upstream hcom source for provider behavior;
4. summaries/prose only as navigation, never as stronger evidence.

## Verified provider-boundary finding

Current upstream hcom creates an exact message event ID inside `send_message()`:

```text
log_event("message", ...)
→ event_id
```

That ID is used internally for request watches, but `send_message()` returns only `delivered_to`. `cmd_send()` prints recipient feedback and does not emit the just-created message event ID. Therefore the current MAPS CLI boundary cannot prove which hcom event corresponds to a successful `HcomHarnessAdapter.send()`.

This means the following are **not** sufficient joins:

- session name;
- session ID alone;
- sender name;
- matching recipient;
- thread name;
- intent;
- timestamp proximity;
- message text/hash;
- "latest event" after send.

All such joins remain `UNKNOWN` unless a provider-issued exact correlation handle is captured.

## Change boundary

MAY CHANGE:

- `work/tasks/communication-task-run-join-wave3.md`
- `work/notes/2026-08-15-communication-task-run-join-design.md`

MUST NOT CHANGE:

- `runtime/state/schema.sql`;
- `runtime/state/store.py`;
- A1/A2/A3 branches or PRs;
- PR #44/#45 implementation branches;
- hcom upstream;
- runtime/policy/review/task authority;
- wait/pending semantics.

No runtime implementation is authorized by this planning task.

## Decision authority

Owner may decide:

- exact evidence classes and failure/UNKNOWN semantics;
- minimum future provider receipt shape;
- smallest future MAPS cross-source relationship;
- staged integration sequence and tests.

Owner must not decide:

- to infer event identity from mutable/provider-local prose or timing;
- to alter another agent's state schema work;
- to make communication evidence grant task/session/review/approval authority;
- to copy hcom message bodies into MAPS lineage;
- to treat bounded absence as a wait state.

## Acceptance criteria

- [x] Current hcom send boundary is inspected directly.
- [x] Exact provider event ID exists internally but is not exposed by current CLI send output.
- [x] Session/run IDs and hcom event identities are kept as separate facts.
- [x] Unsafe heuristic joins are explicitly prohibited.
- [x] Minimum provider receipt needed for exact outbound correlation is specified.
- [x] Crash-window semantics are specified honestly.
- [x] Provider-local replies can inherit run correlation only through an already exact root event link plus exact `reply_to_local` relationships.
- [x] Future persistence stores only cross-source relationships, not message bodies or duplicated hcom event state.
- [x] A4d explainable waits remains downstream and cannot infer global pending from bounded reads.
- [x] No active A1/A2/A3 or #44/#45 implementation branch is modified.

## Proposed staged contract

### A4c-0 — provider receipt prerequisite

Future hcom integration must expose a structured send receipt containing at least:

```json
{
  "event_id": 123,
  "delivered_to": ["agent-b"]
}
```

Preferred upstream shape: keep ordinary `hcom send` human output unchanged and add an explicit structured mode (for example `--json`) whose success output includes the exact event ID returned by `db.log_event()`.

MAPS must not synthesize this receipt by querying the newest event after send.

### A4c-1 — outbound root correlation

On an already-authorized MAPS harness send:

1. establish exact current run + adapter-qualified session evidence through accepted A1;
2. allocate a MAPS request/operation correlation ID before provider mutation if the accepted operation layer supports one;
3. perform hcom send through a capability path that returns the provider event ID;
4. validate the provider receipt;
5. append only the cross-source relationship from MAPS run/request/session relationship to the exact provider event reference;
6. keep hcom as authority for sender, recipients, thread, intent, reply links, and body.

A successful provider send followed by a MAPS crash before the relationship append is an honest coverage gap. Without a provider-echoed client correlation token, that event must remain unattributed rather than repaired by heuristic matching.

### A4c-2 — reply/ack inheritance

Once event `E` is exactly linked to run `R`, PR #45-style exact `reply_to_local` links may derive that child replies/acks are communication descendants of `R`.

Same-thread membership alone cannot inherit run attribution.

### A4c-3 — trace / Run Record projection

Trace may show:

- exact root event refs;
- exact derived reply/ack descendants;
- bounded coverage status;
- `UNKNOWN` for provider events without an exact MAPS root join.

Trace must not claim communication completeness merely because a bounded hcom read returned no additional events.

## Future relationship shape

The smallest likely durable fact is a cross-source root link, conceptually:

```text
MAPS run/request
  ↕ exact relationship only
provider event ref
```

Potential fields, subject to final A1/A3 accepted interfaces:

- MAPS `run_id`;
- optional accepted submission/request/operation ID when available;
- optional exact `run_session_links.id` target relationship;
- provider/transport = `hcom`;
- provider event scope/reference (local event ID plus any provider namespace needed for uniqueness);
- evidence/provenance ref;
- creator + timestamp.

Do not duplicate into that row:

- message body;
- sender/delivered_to arrays;
- intent/thread/reply state;
- provider liveness;
- task status/claim/lease;
- review/operator approval.

Those remain with their owning sources and are joined at read time.

## Provider namespace requirement

An integer hcom event ID is provider-local, not assumed globally unique. Before runtime persistence, the accepted implementation must prove the namespace needed to make a stable provider event reference. Local-only v1 may scope an event ID to the configured hcom state/project boundary; remote-device event references require their explicit provider/device identity rather than silently collapsing to the local integer.

## Crash and retry semantics

Cross-system send + MAPS append cannot be assumed atomic.

- provider rejects before event creation → no provider event link;
- provider creates event and returns exact receipt, MAPS append succeeds → exact correlation;
- provider creates event but MAPS loses receipt/crashes before append → event exists, correlation `UNKNOWN`;
- retry must not silently claim the earlier event;
- a future provider `client_ref` echoed into event data could make exact crash recovery possible, but that is a separate capability and is not assumed now.

## Verification / review

Verification for this task:

- exact upstream hcom source inspected at pinned commit;
- exact current PR #44/#45/#48 heads inspected;
- branch contains only the two approved planning files;
- no runtime/schema changes.

Review required: `INDEPENDENT_REVIEW` before this design becomes implementation authority.

## Stop / escalation

Stop rather than infer if:

- provider send does not expose an exact event receipt;
- provider event namespace cannot be made stable;
- A1/A3 accepted interfaces change the root identity relationship materially;
- implementation would require editing another active agent's branch;
- a proposed wait state depends only on bounded absence.

## Continuation

After A1/A2/A3 and #44/#45 interfaces settle:

1. re-check exact accepted interfaces;
2. prove/implement provider send receipt capability;
3. implement only the root cross-source event link;
4. derive exact reply descendants using #45 semantics;
5. enrich trace/Run Record with explicit coverage;
6. only then shape A4d explainable waits.
