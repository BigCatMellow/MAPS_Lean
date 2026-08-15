# Review packet: Status surface v1

- Status: `QUEUED`
- PR: `#19`
- Task record: `work/tasks/status-surface-v1.md`
- CI evidence: Runtime stack tests run `31886549262` passed with
  `tests/test_status.py` present.

## Review scope

Inspect:

- `runtime/status.py`
- `runtime/cli.py`
- `tests/test_status.py`

## Intended behavior

`python -m runtime.cli status` is a disposable read model over canonical SQLite
state. It shows:

- counts by task status;
- active claimant/lease/heartbeat/attempt information;
- attention for review-needed tasks, blocked tasks, stale/missing active leases,
  and latest post-completion failure outcomes;
- recent event type/actor/time without free-text event summaries;
- explicit coverage gaps for hcom, recovery, and helper-run state.

## Review questions

1. Does status remain completely read-only?
2. Are attention classifications facts derived from canonical state rather than
   inferred intent?
3. Does latest-outcome handling avoid surfacing a superseded failure after a
   later success observation?
4. Is omission of free-text event summaries the right privacy/signal tradeoff?
5. Are hcom/recovery/helper gaps explicit enough to prevent users treating v1 as
   complete system observability?

## Intentionally deferred

- no UI/dashboard;
- no polling daemon;
- no auto-kill, retry, reassign, approve, or recover action;
- no helper `NO PROGRESS` inference yet;
- no explainable-wait/hcom join yet.
