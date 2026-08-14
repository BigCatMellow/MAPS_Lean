# Insight Record

Insight ID: INS-0059
Project: MAP
Related task: TASK-307
Detected by: claude-lab-mimi
Date: 2026-07-30
Status: RAW

## Short description


- obs: Cross-host or otherwise privileged gateway code that mutates lifecycle/authority state benefits from a dedicated adversarial security-framed review pass, distinct from and in addition to functional/architecture review.

## Trigger


- src: TASK-307 (the Biggie/Smalls rotation gateway patch) needed 3 review rounds. The first two CHANGES_REQUESTED each found a distinct, real vulnerability that a purely functional review would plausibly have missed: (1) remote-writable rotation-restore not bound to authority-generated transfer state (an arbitrary-row-restore risk), (2) transfer_rotation_claims building its rollback snapshot before BEGIN IMMEDIATE, so the snapshot was not captured atomically with the transfer transaction (a race condition).

## The synthesis


- synth: Both defects are the kind a reviewer only finds by asking 'what could an attacker or a bad timing window do here' rather than 'does this implement the spec.' TASK-307 is also the single task most of this recovery session's coordination work has been blocked on (context-rotation ack/finalize, cross-PC deployment) -- the review discipline that caught these two bugs is exactly what should be named and reused before it deploys, not re-derived from scratch next time.

## Why it might matter


- why: Deployment of this exact patch is still pending (TASK-308), and the recovery kickoff plan's WS-6 explicitly calls for a security/structural review pass on cross-host work. This insight gives that requirement a concrete, evidenced justification instead of a general policy statement.

## Evidence


- ev: [[artifacts/reviews/task307-smalls-predeploy-review-codex-lab-vumo]]; [[artifacts/reviews/task307-smalls-rereview-codex-lab-vumo]]; [[artifacts/reviews/task307-smalls-rereview3-codex-lab-vumo]]

## Risk


- risk: Acting without promotion could bypass HPOM governance.

## Scope


- scope: Review-process guidance only; no code or task-graph change.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
