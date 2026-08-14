# Method review — triage wait-envelope probe

- reviewer: codex-lab-kiri
- date: 2026-07-20
- reviewed artifact: `artifacts/experiments/triage-wait-envelope-probe-2026-07-20.md`
- supporting script: `scripts/triage_wait_envelope_probe.py`
- original verdict: **CHANGES_NEEDED**
- closure: **RESOLVED 2026-07-20**

## Bottom line

The probe supports a narrower finding: reconstructing recipients from later
`status context=deliver:<sender>` events is unreliable. It does **not** show
that hcom telemetry lacks the intended addressee, or that a manually declared
wait record is necessary. First-class request metadata already exposes the
intended target through `msg_mentions`, including for the eight held-out
reqwatch incidents.

The useful design conclusion is therefore smaller: hcom can create most of the
wait envelope automatically at `--intent request` send time. Requesters should
only have to declare wait semantics that differ from safe defaults.

## Required finding 1 — the addressee premise is false

`hcom events --help` documents `msg_mentions[]` and `msg_delivered_to[]` in the
queryable `events_v` view. The local hcom schema confirms that both fields are
extracted from the message event's JSON data. Direct queries recover the
reported intended target for **8/8** held-out incidents:

| request | target in `msg_mentions` | target in `msg_delivered_to` |
|---:|---|---|
| 5600 | lilo | lilo |
| 6035 | hana | hana |
| 6095 | hana | hana |
| 6102 | lilo | lilo |
| 6388 | lure | lure |
| 6461 | lilo | lilo |
| 8567 | lilo | lilo |
| 8585 | hana | hana |

This includes #8567 and #8585, for which the probe reports zero later delivery
status events. Thus, absence of a later delivery-status event is not absence of
an addressee in telemetry.

One direct reproduction form is:

```bash
hcom events --sql "id=8567 AND EXISTS (SELECT 1 FROM json_each(msg_mentions) WHERE value='lilo')" --name kiri
```

The script never reads `mentions` or `delivered_to`. Instead, it infers a
recipient exclusively from later status events between the request and the
sender's next message. Its 1/8 result therefore measures that specific
status-correlation heuristic, not the information available in hcom telemetry.

Required correction: replace the structural-undetectability claim in the
report and INS-0036 with the narrower heuristic failure, then rerun recipient
recovery using `msg_mentions` as the primary source. Clarify the precise
semantics of `msg_delivered_to`; `msg_mentions` alone is sufficient for intended
recipient recovery.

## Required finding 2 — qualify the labels and metrics

The eight reqwatch incidents are a reasonable denominator for **sensitivity to
known reqwatch-positive incidents**. They are not an exhaustive denominator for
all stranded waits. If reqwatch can miss strands, absolute recall is unknown;
the direction and size of any bias cannot be established from this sample.

Likewise, `0 false positives` is only established if the other examined
requests were independently annotated as non-stranded. With a positive-only
reqwatch label set, the defensible statement is that the one detector output
matched a known positive, or `1/1 known-positive precision`. Absence of a
reqwatch notice is not yet a verified negative.

Required correction:

1. Add a durable ground-truth table for all eight positives with request ID,
   intended target, reqwatch notice ID, the no-response interval, and reroute or
   other outcome evidence.
2. Either manually label the remaining requests before reporting false
   positives/specificity, or rename the metric as detections outside the known
   positive set.
3. Describe `1/8` as known-positive sensitivity, not overall recall.

## Required finding 3 — make the corpus reproducible

The report does not identify the exact 4,000-event input snapshot, its event-ID
range, or a hash. The script defaults to an undocumented `events.jsonl`, and its
output path is `triage_envelope_records.json` in the caller's working directory,
not the durable artifact path cited by the report. This prevents an independent
rerun of the stated 41-request corpus and makes it unclear whether routing
metadata was lost during export.

Required correction: retain or document a redacted frozen input with ID/time
bounds and SHA-256, document the export procedure and retained fields, and make
the script accept explicit input/output paths.

## Answer to the cheaper-inference question

Recipient-name mining from message text is unnecessary as the primary path.
The cheaper and more reliable path is already structured:

1. `requester`: `msg_from` / message instance.
2. `owner` or intended target: `msg_mentions`.
3. `waiting_for`: request body, with optional later structured extraction.
4. `request_id`, creation time, thread, and reply link: existing event fields.
5. delivery and response state: message metadata, `reply_to`, reqwatch, and
   lifecycle evidence, with their semantics documented separately.

Text mining remains a legacy/fallback path only when `mentions` is absent. It
would recover some explicit names (for example #5600 says `lilo`) but not
pronouns such as “you,” so it should not replace first-class routing metadata.

## Revised minimal design to test

On every `--intent request`, have the transport automatically create a wait
record containing:

- request ID, requester, intended target(s), request text, time, and thread;
- state transitions for delivered, acknowledged/replied, requester-rerouted,
  target-stopped, and resolved;
- default `resumes_when = target replies or requester reroutes`;
- a policy-provided timeout/reroute rule where one exists.

Only require an agent-authored `impact`, `resumes_when`, or `timeout_action`
when the safe default is wrong or insufficient. This avoids dual entry while
preserving explainability. The proposed “live core agent who is not the
author” reroute policy can be evaluated independently; authorship is not
established by the fields used in this probe.

## Preserved finding

The stop-timestamp observation remains appropriately marked unverified. Do not
use exact stop times for timeout reasoning until their semantics are tested.

## Closure verification — 2026-07-20

The owner accepted the findings and corrected the report and insight. Closure
verification confirmed:

- INS-0036 was renamed to
  `emergence/insights/INS-0036-hcom-can-auto-derive-wait-records-from-request-metadata.md`;
- its indexed fields now contain only the corrected auto-derive-first finding,
  while the false original claim remains solely as retraction history in Notes;
- the generated emergence index points to the corrected slug and summary;
- the report describes the eight labels as reqwatch-positive non-responses,
  includes their notice event IDs, and explicitly states that absolute recall
  and the false-positive rate remain unknown;
- the report now discloses that the historical input/export procedure was not
  retained, so its bounds and hash identify but do not reproduce the corpus;
- the disposable script requires an explicit input path, accepts an explicit
  output path, and no longer implies that it writes nothing; and
- `map_emergence.py validate` passes with 82 artifacts.

No implementation or promotion is authorized by this closure.
