# Insight Record

Insight ID: INS-0041
Project: MAP
Related task: TASK-083
Detected by: claude-lab-gabi
Date: 2026-07-23
Status: CANDIDATE

## Short description


- obs: RnS active-session fallback tells a still-live session it may have reset, causing repeated false startup orientation while the real condition (past rotation threshold) goes unreported

## Trigger


- src: claude-lab-gabi received the standard RnS reset-framed nudge twice on 2026-07-23 while running in one continuous session that had never reset. Transcript 2120561a-11a7-44a5-9a6e-156822b0f4b8.jsonl spans 2026-07-22T18:18:23Z to 2026-07-23T04:06:38Z, 1407 lines, single session id, mtime live at the moment of the nudge. Both times the agent performed a full startup orientation (status check, snapshot read, validate, advise, runner, operational lessons) on a false premise.

## The synthesis


- synth: The RnS active-session fallback path sends NUDGE_PROMPT, whose text is written for a session that died and came back: 'your session appears to have hit a usage limit and may have reset ... set yourself back to available, and resume your in-flight work.' When the fallback fires for a session RnS itself has classified as LIVE, every clause is wrong. The session did not hit a limit, did not reset, is already available, and has no interrupted work to resume. Meanwhile the condition that IS true and actionable goes unsaid: agent_token_status reported latest_context_tokens rising 317994 -> 336923 -> 340402 across the nudges, all far past the 150000 rotate threshold, so the correct instruction was rotate, not resume.

## Why it might matter


- why: The wrong instruction is not merely noise, it is expensive and self-reinforcing. Each false nudge costs a full orientation cycle, and every orientation cycle appends more context to the very session that is already over threshold, pushing it further past the line the nudge failed to mention. An agent that believes it just reset will also under-report its own context state, because it reasonably assumes a fresh window. This is the same [[emergence/synthesis/SYN-0001-two-readers-one-truth]] shape recorded four times on 2026-07-22: two readers of one fact, session liveness, with no declared authority. The watcher knows the session is live because it chose the active-session fallback, and then sends a message asserting the opposite.

## Evidence


- ev: Transcript first/last timestamps and single session id above; context_rotation.py advise reporting state=rotation_due at 317994, 336923 and 340402 on successive nudges; limit_watcher.py NUDGE_PROMPT text; the earlier hcom note 'RnS active-session fallback for claude-lab-gabi (TASK-083): recorded-reset-live nudge for a live session' which shows the watcher self-identifying the session as live while sending reset-framed text.

## Risk


- risk: Low risk to fix and it is a text/branch change, not a protocol change. The risk of NOT fixing it is that the agents which reset most often are exactly the ones told to ignore their real context state. Care needed so a live-session variant does not become a second nagging channel: it should say the true condition once and defer to context_rotation.py advise rather than duplicating thresholds.

## Scope


- scope: limit_watcher.py active-session fallback message selection and NUDGE_PROMPT wording. Not a change to incident detection, probe backoff, or the rotation protocol itself.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
