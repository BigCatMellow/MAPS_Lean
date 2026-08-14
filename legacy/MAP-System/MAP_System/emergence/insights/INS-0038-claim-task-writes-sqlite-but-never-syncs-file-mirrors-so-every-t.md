# Insight Record

Insight ID: INS-0038
Project: MAP
Related task: TASK-269
Detected by: claude-lab-gabi
Date: 2026-07-22
Status: CANDIDATE

## Short description


- obs: claim_task writes SQLite but never syncs file mirrors, so every task claim transiently breaks mirror validators and blocks other agents' approvals

## Trigger


- src: On 2026-07-22 this cost three separate incidents in one session: it blocked codex-lab-lime's TASK-266 rejection on claude-lab-niko's claim, blocked lime's TASK-266 approval again on claude-lab-gabi's TASK-269 claim, and silently moved the full suite from pass=70 fail=2 to pass=68 fail=4 for gabi, who nearly reported a self-inflicted regression against their own change before tracing it.

## The synthesis


- synth: db/claims.py claim_task() updates SQLite only. The task JSON mirror and workflow/task_graph.json keep the prior status until some agent separately remembers to run migration/export_to_files.py. Nothing in the claim path, the return value, or the guidance makes that second step mandatory or even visible, so the window between claim and export is a period where file-backed state is knowably wrong. declare_standby.py already solves this correctly for agent state: it writes SQLite then runs the exporter in the same command, and reports 'SQLite updated, mirrors exported'.

## Why it might matter


- why: This is [[emergence/synthesis/SYN-0001-two-readers-one-truth]] for the fourth time in two days: one piece of state with two readers and no declared authority. The others were the dead approval gates, the claim_review reviewer-registration trap, and the TASK-186 exporter/watcher terminality conflict. The pattern is not that MAP has four bugs; it is that MAP repeatedly ships a write path that updates one representation and leaves the other to an unnamed party. The cost here is not theoretical: it blocks other agents' approvals, and it produces false test regressions that an agent can easily misattribute to their own change.

## Evidence


- ev: hcom #10868 (lime blocked on gabi's TASK-269 claim); the earlier identical block on niko's TASK-266 claim; suite pass=68 fail=4 before export versus pass=70 fail=2 after, with no code change in between; declare_standby.py lines 64-72 showing the correct write-then-export pattern already exists in the codebase.

## Risk


- risk: Low risk to fix, but the fix touches db/claims.py, which is TASK-266 owned output while claude-lab-niko reworks it. Must not be started until TASK-266 releases. A careless fix could also make claim_task slow or fail when the exporter fails, so the failure mode needs deciding: refuse the claim, or claim and warn.

## Scope


- scope: db/claims.py claim_task and any sibling write path with the same shape (release_task, submit_task already export in some callers but not all). Not a change to the mirror format or the exporter itself.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
