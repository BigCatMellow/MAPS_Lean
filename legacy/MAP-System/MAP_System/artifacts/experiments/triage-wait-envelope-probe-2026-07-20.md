# Experiment — How should an explainable wait record be produced?

- owner: claude-lab-lure
- date: 2026-07-20
- type: bounded triage-envelope probe (first test of the Triage half of
  `conversation_notes.md`)
- authority: none; disposable local analysis, read-only, no integration, no
  state mutation
- status: **CORRECTED after independent method review (kiri, 2026-07-20).** The
  original headline conclusion was wrong; see §3. Review record:
  `artifacts/reviews/triage-wait-envelope-probe-method-review-kiri-2026-07-20.md`

## 0. Frozen corpus provenance

| Field | Value |
|---|---|
| Events | 4,000 |
| Event ID range | 4787 – 8786 |
| Time range | 2026-07-18T02:29:25 – 2026-07-20T13:40:54 |
| SHA-256 of `events.jsonl` | `2f7f63d4cf3a317c07230e0efd91995f47e5d3b28ccac4835e5550cb3db0f7d4` |
| Request messages | 41 |
| Life events | 113 |
| Frozen input retained? | No. The byte-exact input is not present in the repository. |
| Export procedure retained? | No. The original command and selected-field projection were not recorded. |

The ID/time bounds and hash identify the historical input but do not make it
independently reproducible. The export's default JSON projection omitted
`msg_mentions` and `msg_delivered_to`; subsequent correction used the queryable
`events_v` fields directly. A future rerun must freeze both the input and its
export command/schema.

## 1. Question

The operator's design says "a task may wait, but its waiting state must be
explainable." Before building that, one question shapes the work:

> Can an explainable wait be **inferred** from existing signals, or must it be
> **declared** by the requester at ask time?

## 2. Held-out labels (8 reqwatch-positive non-responses)

Labels come from hcom's own reqwatch notices, which the detector never read.
They establish that reqwatch observed no response during its watch interval;
they are not exhaustive ground truth for every stranded wait.

| # | Request ID | Intended recipient | Notice event ID | Notice timestamp |
|---|---:|---|---:|---|
| 1 | 5600 | lilo | 5635 | 2026-07-18T19:48:23 |
| 2 | 6035 | hana | 6084 | 2026-07-19T03:38:27 |
| 3 | 6095 | hana | 6098 | 2026-07-19T03:41:23 |
| 4 | 6102 | lilo | 6177 | 2026-07-19T04:01:26 |
| 5 | 6388 | lure | 6405 | 2026-07-19T12:47:59 |
| 6 | 6461 | lilo | 6467 | 2026-07-19T13:23:29 |
| 7 | 8567 | lilo | 8616 | 2026-07-20T03:34:33 |
| 8 | 8585 | hana | 8652 | 2026-07-20T03:47:33 |

## 3. CORRECTION — my original conclusion was wrong

**What I originally claimed:** that hcom's event stream records deliveries but
not addressees, so a request to a stopped agent leaves no link to its intended
recipient, making stranded waits *structurally undetectable* — and therefore
that a requester-declared record was **necessary**.

**That claim is false.** Independent review established, and I re-verified
directly, that intended recipients are already available in queryable
`msg_mentions` metadata. A direct check recovers the correct addressee for
**8/8** held-out incidents, including #8567 and #8585 — the two cases I had
cited as proof of the structural limit:

```
5600 lilo RECOVERED   6035 hana RECOVERED   6095 hana RECOVERED   6102 lilo RECOVERED
6388 lure RECOVERED   6461 lilo RECOVERED   8567 lilo RECOVERED   8585 hana RECOVERED
```

The field is not exposed in the default JSON projection of `hcom events`, but it
is present in the underlying table and filterable via `--sql`. My detector
inferred recipients from *delivery* events — **my own design choice**, not an
hcom limitation.

**Therefore the 1/8 result measures my detector's later-delivery-status
heuristic, not a property of the system.** The delivery-based observations in
the original write-up (recipients stopped at send time, ~17h-late delivery) are
still factually true, but they do **not** support the structural claim I built
on them.

## 4. Corrected result framing

| Metric | Value | Correct interpretation |
|---|---:|---|
| Requests examined | 41 | — |
| Wait records reconstructed | 16 | via delivery-inference heuristic |
| Strands detected | 1 / 8 | **sensitivity of my heuristic to known reqwatch positives** — not absolute recall |
| False positives | 0 observed | **unproven**: the other 33 requests are not independently labelled, so a false-positive rate cannot be claimed |

Absolute recall is **unknown**, because the labelled set covers only reqwatch's
own positives; reqwatch may itself miss strands.

## 5. Corrected conclusion — auto-derive first, declare only the remainder

Because the addressee, request body, ID, timestamp and thread are all already
available, the cheapest correct path is **not** to require agents to hand-author
wait records:

1. **hcom auto-creates the wait record** from `requester`, `msg_mentions`,
   request body, and request ID/time/thread. This covers the common case with
   zero agent effort and works regardless of delivery.
2. **Agent-authored fields only when defaults are insufficient** — `resumes_when`,
   `timeout_action`, `impact`. These are the parts telemetry genuinely cannot
   supply.
3. **Text mining of recipient names is a fallback only**, for messages lacking
   structured mentions.

This is strictly cheaper than my original proposal and does not depend on the
false premise. The design's insight — that a wait must be *explainable* — still
holds; what changes is that most of the envelope can be derived rather than
demanded.

## 6. What survives unchanged

- **The reroute rule is mechanisable.** All four manual re-routes this session
  used the same decision — pick a live core agent who did not author the item —
  and the detector reproduced it correctly whenever it had a recipient.
- The friction is real and repeated: four manual re-routes in one session.
- Two bugs found during the probe (recipient cross-attribution; counting any
  later message as a reply) were fixed.

## 7. Flagged, still unverified

Two `stopped` life events carry the exact timestamp of the send, consistent with
stop being *detected at delivery attempt* rather than when the session ended. I
did **not** establish this. It needs its own check before stop timestamps are
used for timing.

## 8. Limitations

- Single 2-day window, one operator session; 8 labelled incidents.
- Labels are reqwatch-positive non-responses only — absolute recall and
  false-positive rate both remain unknown without independently labelling the
  remaining 33 requests.
- The detector is disposable and deliberately simple.
- Read-only; no hcom, agent, or task state was modified.

## 9. Provenance

- Probe script: `scripts/triage_wait_envelope_probe.py` (disposable, read-only)
- Records: `artifacts/experiments/triage-wait-envelope-records-2026-07-20.json`
- Method review: `artifacts/reviews/triage-wait-envelope-probe-method-review-kiri-2026-07-20.md`
- Related: INS-0034, INS-0036, `conversation_notes.md` sections 2-3
- Reproducibility boundary: the historical input itself and its exact export
  command/schema were not retained; only its bounds and hash survive.
