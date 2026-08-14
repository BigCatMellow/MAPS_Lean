# Insight Record

Insight ID: INS-0036
Project: MAP
Related task: NONE
Detected by: claude-lab-lure
Date: 2026-07-20
Status: OPEN

## Short description


- obs: hcom can auto-derive most of an explainable-wait record from metadata it already stores. Intended recipients are queryable via msg_mentions, so requester, addressee, request body, ID, timestamp and thread need no agent effort; agents only author resumes_when, timeout_action or impact when safe defaults are insufficient.

## Trigger


- src: Bounded probe of the Triage half of conversation_notes.md against a frozen 4000-event hcom corpus with 8 reqwatch-positive non-responses held out. A detector was built to infer waits from delivery events; independent method review then established that msg_mentions already carries the intended recipient, recovering the correct addressee for all 8 of 8 held-out cases.

## The synthesis


- synth: The explainable-wait envelope should be auto-derived first and declared only for the remainder. hcom composes requester, addressee, request body, ID, time and thread from stored metadata; safe policy defaults can cover ordinary resume and timeout behavior, while agents supply resumes_when, timeout_action or impact only when those defaults are insufficient. Text mining of recipient names is a fallback for messages lacking structured mentions. This is strictly cheaper than requiring agents to hand-author the whole record.

## Why it might matter


- why: It sizes the triage build down substantially and removes a repeated, operator-visible friction. Four review requests in a single session were stranded and re-routed by hand. The re-route decision itself is mechanisable: every one of the four used the same rule, pick a live core agent who did not author the item, and the detector reproduced that rule correctly whenever it had a recipient. Because the addressee is already stored, an auto-derived wait record works even when a request is never delivered, which is the case that costs the most.

## Evidence


- ev: [[artifacts/experiments/triage-wait-envelope-probe-2026-07-20]], records JSON, and scripts/triage_wait_envelope_probe.py. Direct verification recovered the addressee for 8 of 8 held-out cases via msg_mentions. The detector's 1 of 8 figure measures the sensitivity of its delivery-inference heuristic to reqwatch-positive non-responses; it is not absolute recall, and its zero-false-positive count is unproven because the other 33 requests are unlabelled. Frozen corpus: event ids 4787-8786, 2026-07-18T02:29:25 to 2026-07-20T13:40:54, sha256 2f7f63d4cf3a317c07230e0efd91995f47e5d3b28ccac4835e5550cb3db0f7d4. Secondary unverified observation: two stopped events carry the exact send timestamp, which would indicate delivery-triggered detection rather than true stop time, and needs its own check.

## Risk


- risk: Acting without promotion could bypass HPOM governance. Auto-derivation must not become a task-state authority; it is a projection over hcom metadata only.

## Scope


- scope: Only the files and artifacts named in this record.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [x] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- retraction history (concise): this record was first filed under the slug
  "stranded-waits-are-structurally-undetectable-from-hcom-telemetry" claiming
  that hcom stores deliveries but not addressees, making stranded waits
  undetectable and a fully agent-declared record necessary. That claim was
  FALSE. Independent method review (codex-lab-kiri, 2026-07-20) established that
  msg_mentions already carries the addressee; the field is simply absent from
  the default JSON projection of hcom events. Inferring recipients from delivery
  events was the probe author's design choice, not a system limitation. Renamed
  and normalised 2026-07-20 so the retracted claim no longer appears in the
  indexed fields.
- Review record: artifacts/reviews/triage-wait-envelope-probe-method-review-kiri-2026-07-20.md
