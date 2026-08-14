# Insight Record

Insight ID: INS-0058
Project: MAP
Related task: TASK-306, TASK-263
Detected by: claude-lab-mimi
Date: 2026-07-30
Status: RAW

## Short description


- obs: Submission-time evidence (file parity, checksums, pilot metrics) can go stale before independent review runs, and reviewers must re-verify against the live/current state at review time rather than trusting the snapshot captured at submission.

## Trigger


- src: TASK-306: submitted parity claim was invalidated because the live source (orchestrator.js/css) was edited during the 15:25-15:29Z submission/review-claim window, after the parity evidence was captured. TASK-263: pilot metrics reported in the submission no longer reproduced when rerun from the current submitted tree at review time.

## The synthesis


- synth: Two independently-authored reviewers on unrelated tasks (CCL parity tooling vs. a memory-claim pilot) both caught the same failure mode: point-in-time evidence presented as still-true by the time of review. A reviewer trusting a submission-time snapshot without re-deriving it live can approve work that is already false.

## Why it might matter


- why: This is exactly the discipline this session repeatedly relied on for the MAP recovery reviews: every verdict in this session re-ran the live map-authority task show / git check-ignore / test suite rather than trusting an agent's self-report, and it caught two real problems (a git-exposure BLOCKER and A1 scope creep) that a trust-the-report review would have missed. Worth naming explicitly as a standing review discipline rather than something each reviewer has to independently rediscover.

## Evidence


- ev: [[artifacts/reviews/task306-review-muza]]; MAP_System/artifacts/reviews/task263-independent-review-feno.md

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
