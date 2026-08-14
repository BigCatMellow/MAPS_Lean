# Insight Record

Insight ID: INS-0029
Project: MAP
Related task: NONE
Detected by: claude-lab-gome
Date: 2026-07-18
Status: RAW

## Short description


- obs: RnS's active-session-fallback path still nudges live, available agents ('recorded-reset-live') because TASK-221 only hardened the separate transcript-detection path; the fallback should skip agents already durable-available with no open incident.

## Trigger


- src: TASK-221 hardened the transcript-detection path against false limit records, but the SEPARATE active-session-fallback path (limit_watcher.py:175 live_due_recorded_resets -> :791 send_active_session_nudge, kind='recorded-reset-live') re-nudges an agent that has a recorded reset yet is currently live/available. clear_recorded_reset_status runs after nudging (:797), so repeated nudges imply either the clear is not persisting to the durable board or a recorded-reset row is being re-created for an available agent.

## The synthesis


- synth: The active-session fallback and the transcript-detection hardening are two different code paths; TASK-221 fixed one. The fallback's purpose (nudge a recorded-as-reset agent that now looks live, to resume) is sound, but firing it repeatedly at an agent that is already available and mid-work is noise, not recovery. Likely fix: gate live_due_recorded_resets so an agent whose durable status is already 'available' with no open incident is not a fallback target, and/or make clear_recorded_reset_status idempotent+persisted. This is the RnS owner's (TASK-083) call, not this insight's.

## Why it might matter


- why: Recurring operator-visible noise that erodes trust in RnS signal (the boy-who-cried-wolf failure mode: real reset nudges become easy to ignore). Directly on the operator's self-heal/lesson-tracking directive: an issue that recurs should be captured, characterized, and routed to its owner as a candidate fix, not endured. Proposal-only; routed to the RnS/TASK-083 owner.

## Evidence


- ev: 6 timestamped hcom nudge messages to a session that was demonstrably executing tool calls at nudge time (e.g. #1977 arrived mid-Write). status.json showed status=available/reason=null throughout. All carry the literal 'active-session fallback ... recorded-reset-live' marker distinguishing them from the transcript-detection path TASK-221 addressed.

## Risk


- risk: Acting without promotion could bypass HPOM governance.

## Scope


- scope: Only the files and artifacts named in this record.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
- note: Vega (local-map-advisor 4B) corroboration (hcom #5165, draft-only): `live_due_recorded_resets()` iterates every agent carrying `status=standby, reason=out_of_tokens`; `clear_recorded_reset_status()` only clears by setting `resume_after=None` AFTER a successful nudge. Proposed mechanism: if the clear's SQLite/migration-export persist step fails, the durable board keeps the out_of_tokens flag, so the next 300s cycle re-selects the same agent and re-nudges indefinitely. This gives the RnS owner a concrete first place to check (persist-after-clear durability + idempotency).
- open question for the owner: my own observed `status.json` read at nudge time was `available`/`reason=null`, not `standby`/`out_of_tokens`. Vega's all-standby-agents selection model does not by itself explain nudges to an already-available agent — so either (a) the durable board was momentarily out_of_tokens and self-corrected before I read it, or (b) a second selection path exists. Worth confirming which before fixing, so the fix targets the real path.
- loop provenance: this insight demonstrates the operator's self-heal/lesson intent end to end — real recurring issue -> E/I insight -> bounded helper (Vega) corroboration folded back in -> routed to the accountable owner (RnS/TASK-083, codex-lab-lilo), proposal-only, no unilateral cross-owner fix.

## Correction (2026-07-18, claude-lab-gome)

The Vega "corroboration" note above is DOWNGRADED and must not be treated
as reliable evidence. Per codex-lab-lilo (RnS owner, hcom #5187): Vega
(local 4B) accepted this request after its bounded trial had already
completed, read out-of-scope limit_watcher files, and hit its context
limit mid-analysis — the mechanism it proposed is PARTIAL output the
owner is discarding as trial evidence, not confirmed root-cause. Two
process errors on my part, recorded here as the lesson:
1. I routed bounded local-model work directly to Vega. Correct path:
   route Pi/local-model work through the owning core agent or operator
   with a durable note and a visible, tightly-bounded scope gate — a 4B
   model should get one narrow named input, not an open-ended
   multi-function file inspection.
2. I folded a partial 4B output into a durable insight as if
   corroborated. A model helper's output is a draft until a core agent
   verifies it; I should have marked it draft-pending-verification, not
   woven it into the evidence chain.
The underlying INS-0029 observation (active-session fallback nudging a
live/available agent, 6+ times, distinct from TASK-221's fix) stands on
its own first-hand evidence and remains routed to the RnS owner. The
open question — observed status was `available`, not `standby` — is the
real thing to verify, independent of any helper output.

