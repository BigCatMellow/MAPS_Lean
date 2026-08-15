# Review packet: Priority observability and operating safeguards

- Status: `QUEUED`
- PR: `#19`
- Implementation commits: `13d1e11ce3078edbd270925acf244d2fb9686281`, `0776a6b45490d85487c725474e9d3bbf600524da`
- Task record: `work/tasks/priority-observability.md`

## Review scope

Review the referenced PR revision, especially:

- `AGENTS.md`
- `docs/CHECKS_AND_BALANCES.md`
- `templates/review.md`
- `runtime/state/observability.py`
- `runtime/state/store.py`
- `runtime/cli.py`
- `tests/test_trace_and_redaction.py`
- `runtime/README.md`

## Intended behavior

- active negative operating contract constrains unnecessary complexity,
  verbosity, guessing, scope expansion, duplicate truth, and needless permanent
  machinery;
- review guidance exposes risk-specific lenses without adding mandatory extra
  reviewers;
- task-event summaries cross a shared best-effort redaction boundary;
- diagnostic event/review reads redact recognized secret patterns without
  rewriting older canonical rows;
- `trace TASK-ID` is read-only, uses canonical SQLite task evidence, omits raw
  submission evidence, and states its hcom/external-runtime coverage gaps.

## Review questions

1. Can any new observability path mutate task authority or canonical lifecycle?
2. Does redaction reduce accidental exposure without claiming perfect secret
   detection or silently rewriting canonical historical evidence?
3. Does trace clearly distinguish included evidence from unavailable/unjoined
   sources?
4. Are the negative operating rules concise enough for routine loading and
   narrow enough not to cause needless clarification?
5. Do the review lenses remain proportional to actual risk?

## Verification state

Focused tests were added. Full repository CI had not run when this packet was
queued because the workflow did not trigger for arbitrary PR branches. A
separate queued change enables normal pull-request CI; record its result here
when available.

## Known/deferred work

- hcom/recovery/helper/escalation correlation is not in trace v1;
- outcome feedback is a separate next tranche;
- hard evidence-freshness enforcement needs immutable revision/artifact binding
  or review-time re-derivation and is not faked with a checkbox.
