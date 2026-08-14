<!-- hpom: file: artifacts/releases/task-221-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-18 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-221

```
task_id:      TASK-221
released_by:  claude-lab-gome
release_date: 2026-07-18
reviewed_by:  claude-lab-gome
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

TASK-221 hardens the RnS limit watcher into a persistent, deterministic
local supervisor: fresh provider-originated session-limit records are
detected from live transcript tails (provenance-gated so quoted text
cannot forge them), persisted SQLite-first as standby/out_of_tokens with
an ISO resume_after, and woken via the normal bounded-retry path; runs
as an enabled, reboot-safe systemd user service at 300s. Resolves the
2026-07-17 incident class (three documented false-positive nudges at a
live session, plus the missed-limit overnight gap). Implemented by
codex-lab-lilo; TASK-210 retired as superseded with a supersession note.

- Files: watcher script, launcher, systemd unit template, focused tests,
  protocol note, evidence artifact (all registered).
- Decisions: none new — operator-directed hardening within existing RnS
  architecture (TASK-083 lineage).
- Follow-ups: one RECOMMENDED (non-blocking) in the review — narrow the
  Codex `agent_message` provenance branch if a more specific provider
  record type exists. Also surfaced (not TASK-221 debt): ClearFront's
  risk register fails `validate_risk_registers` formatting — the
  reviewer's own file, fixed separately by the reviewer.
- Events: recorded in `events/events.jsonl` (trace_id task:TASK-221).
- Emergence: considered — no new card; deterministic-supervisor pattern
  is TASK-083's existing lineage, hardened.
- Operator-facing friction: this task IS the closeout of a real
  operator-felt friction (nudge storms + missed overnight limit).

## Review

APPROVED — `MAP_System/artifacts/reviews/task221-review-gome.md`
(claude-lab-gome), including the security-framed pass required for
write-capable components. Reviewer reproduced the 32/32 focused tests,
live systemd state (enabled/active/300s/no stray timers), and a live
dry-run with zero false detections; the reviewer's own session provides
before/after empirical evidence (three false nudges pre-221 on
2026-07-17 vs one correct due-time wake post-221 on 2026-07-18).

## Verification

Focused tests 32/32 (reviewer-reproduced); full suite 65/67 with both
failures verified pre-existing and out of scope; graph/schema/mirror
validators pass; live service verified running since 2026-07-17 20:55.
