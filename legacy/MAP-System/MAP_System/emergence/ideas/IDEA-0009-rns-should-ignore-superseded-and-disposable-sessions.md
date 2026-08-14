# Idea Card

Idea ID: IDEA-0009
Project: MAP
Source insight or synthesis: TASK-090 post-restart reconciliation
Owner: codex-lab-limo
Date: 2026-07-02
Status: ADOPTED

## Idea

- idea: RnS ignore superseded/disposable sessions.

## Problem or opportunity

- gap: RnS sees dead-on-purpose sessions like limit-stopped sessions unless durable state marks every disposable/superseded identity.

## Why now

- now: restarted watcher probed `scratch-peso` and old lab identities after lab-open workflow changed.

## Expected benefit

- gain: fewer false wake-ups; less Monitor noise; lower obsolete-context resurrection risk.

## Cost

- cost: small RnS v2.2 design pass for lifecycle tags, helper metadata, incident suppression.

## Reversibility

- [ ] Yes
- [ ] No
- [x] Partially — explain: suppression rules can be reverted, but any skipped
  wake-up during the experiment must be visible in dry-run output before release.

## Smallest safe experiment

- test: dry-run suppression check treats `inactive/session_superseded` and `inactive/disposable_session_ended` as terminal.
- replay: current watcher state + hcom snapshot.

## Decision needed

Who must approve this before it can be promoted?
- [ ] Task DRI — within current task scope
- [ ] Review DRI — requires review gate
- [x] State Steward — changes shared state
- [ ] Project DRI — changes project direction
- [ ] Human Owner — changes MAP-level rules or governance

## Recommendation

- [ ] Park — valid but not the right time
- [ ] Reject — not worth pursuing
- [x] Test — run the smallest safe experiment
- [ ] Promote to task — evidence is sufficient, ready for HPOM

## Corroborating evidence (2026-07-04, TASK-146 triage, claude-lab-magi)

- status: left CANDIDATE; still recommend Test, not direct promotion.
- scope: dry-run suppression experiment is RnS/watcher implementation work, outside TASK-146 triage.
- ev: 2026-07-04 before `agents/status.json` reconciliation, limit watcher logged `BLOCKED` / "presumed down without a status record" / "giving up after 6 probes".
- ev-agents: `claude-lab-sara`, `claude-lab-valo`, `codex-lab-dino`, `codex-lab-lema`, `codex-lab-muva`; all later available.
- ref: `MAP_System/events/events.jsonl` around `2026-07-04T00:02:44-04:00`.
- meaning: same false-wake-up / Monitor-noise failure as TASK-090; experiment ready, not speculative.

## Lifecycle closeout (2026-07-22, claude-lab-gabi)

- status: ADOPTED. EXP-0001 ran, the Test recommendation is satisfied, and the
  idea is implemented and evidenced under TASK-186.
- outcome: the expected benefit was delivered — the seven genuinely-dead
  sessions (lure, mira, toku, zera, mozu, nivo, gune) now close as explicit
  terminal suppressions with zero probes, instead of being probed six times each
  and then silently given up on. The reversibility condition was honored: every
  suppression is visible in dry-run output, and the dry-run was confirmed to
  write nothing.
- decision required by this card: "State Steward — changes shared state". That
  approval was requested 2026-07-15, went unanswered for seven days, and was
  granted by the operator on 2026-07-22 as option A. Recorded as a
  DECISION_RECORDED event on TASK-186 rather than left in chat.
- what the experiment additionally found: the idea as originally implemented was
  structurally unreachable. Terminality was read from agents/status.json, which
  migration/export_to_files.py documents as "an operational routing view, not a
  full dump" and which drops exactly these agents. Resolving lifecycle from the
  SQLite agents table was the fix. This is SYN-0001 — one piece of state, two
  readers, no declared authority — and IDEA-0009 is now a worked example of it,
  not just another instance.
- scope honesty: the task text says 8 dead sessions; live state carried 7 with
  gave_up=true. Seven were marked. The four incidents opened 2026-07-22 were
  left alone deliberately: they had probes_sent=0 and may still be recoverable,
  and marking a recoverable session terminal is precisely the failure this
  card's reversibility condition guards against.
