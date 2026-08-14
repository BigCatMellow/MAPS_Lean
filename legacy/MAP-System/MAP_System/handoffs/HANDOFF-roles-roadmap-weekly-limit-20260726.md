# Roles Roadmap Shutdown Handoff — 2026-07-26

This is the durable pause point requested after the weekly Codex limit was reached. It records what was completed, what is safely stopped, and the exact next actions. SQLite task state, task mirrors, event JSONL, and the linked review artifacts remain canonical.

## Lane state at shutdown

| Task | Canonical state | Last identity | Evidence / result | Safe next action |
|---|---|---|---|---|
| TASK-274 | APPROVED | codex-lab-hana; reviewed by codex-lab-feta | Durable `SUBMISSION` event 1724; review `MAP_System/artifacts/reviews/task274-independent-review-feta.md`; focused checks 7/7 | No further work |
| TASK-278 | READY (released for shutdown) | task278-levi | Core implementation green: authorship/review races 7/7, submission 7/7, TASK-268 lifecycle 3/3, review claims 12/12, owner reassignment 5/5, no-self-review 2/2; schema/mirrors pass | Clear shared-path ownership, then validate and submit; independent review required |
| TASK-280 | READY (attempt 2 released for shutdown) | codex-lab-feta, process stopped | Attempt 1 review `MAP_System/artifacts/reviews/task280-independent-review-nita.md` found real gaps: sanctioned task creation accepts unknown roles; tier-2 policy rereads raw roles; tests omit both paths. Attempt 2 paused without further edits because `map_task.py` collides with TASK-278 and `pre_dispatch_policy.py` collides with TASK-283 | Reconcile output ownership durably; resume Feta only after collision-free registration |
| TASK-285 | SUBMITTED | task285-replacement-solo; reviewed by codex-lab-nita | Review `MAP_System/artifacts/reviews/task285-independent-review-nita.md`; focused checks pass, but verdict is CHANGES_REQUESTED because refresh does not detect changed primary hashes and frozen metric measures context bytes rather than tokens. Canonical rejection correctly failed closed because submission author row is missing until TASK-278 migration | After TASK-278, migrate/resolve unknown author conservatively, then rework and rereview |
| TASK-281 | READY | none | Blocked on TASK-280 approval | Dispatch after TASK-280 |
| TASK-282 | READY | none | Blocked on TASK-278 and TASK-281 approval | Dispatch after both predecessors |
| TASK-283 | READY | none | Operator authorization event 1721; its `pre_dispatch_policy.py` path currently collides with TASK-280 | Dispatch only after ownership repair |
| TASK-286 | READY | none | Operator authorization event 1720; minimal CCL startup/lifecycle correction | Dispatch after TASK-280 approval |
| TASK-287 | READY | none | Final evidence-linked orchestration report required by operator | Run only after all roadmap dependencies are independently approved |

## Agent/session state

- `task278-levi`: implementation complete but blocked at canonical submission by shared-path ownership; final request was event 18049. Claim was released to READY with a durable PROGRESS event and the identity is in standby. The visible pane remained listening when process termination hit the weekly usage-limit guard; it must be closed on the next available control window.
- `codex-lab-feta`: TASK-280 attempt 2 paused at the collision; claim was released to READY with a durable PROGRESS event and process stopped. Do not resume until ownership is repaired.
- `codex-lab-nita`: TASK-285 independent review complete; process stopped. Review artifact is durable.
- `codex-lab-riko`: replacement coordinator could not acknowledge the stale Kazu snapshot because canonical task state drifted; process stopped. The prepared snapshot is not a valid continuation point.
- `codex-lab-kazu`: coordinator session is being shut down for the weekly limit. The prepared snapshot `STATE_SNAPSHOT-codex-lab-kazu-20260726T200303Z.yaml` is superseded by this handoff because canonical task state changed; do not acknowledge it.

## Confirmed orchestration defects

1. Output ownership is write-once with no supported unregister/defer operation. TASK-280 had to discover that its needed paths were concurrently owned by TASK-278/TASK-283 after claim, turning a valid implementation into a graph-red pause.
2. Pre-dispatch approval is advisory: durable operator decisions exist (1716, 1717, 1720, 1721, 1727), but the policy checker does not consume them automatically.
3. Submission authorship is now emitted by TASK-274, but legacy/new submissions without the separate authorship row fail closed, correctly blocking TASK-285 lifecycle mutation until migration exists.
4. Context rotation requires a canonical-task snapshot match. Riko’s refusal to acknowledge drift was correct; delayed duplicate launches (Riko/Hula) created extra visible sessions during the attempted handoff.
5. `hcom kill` usually terminates processes, but WezTerm pane closure intermittently times out, leaving empty operator panes. This is evidence for TASK-286/TASK-287, not a reason to fabricate terminal state.

## Resume order

1. Start from SQLite and validate task mirrors/graph.
2. Repair TASK-280/TASK-278/TASK-283 output ownership through a sanctioned durable metadata repair; never edit overlapping paths.
3. Finish TASK-278 validation/submission and obtain independent approval.
4. Resolve TASK-285 unknown-author migration and rework its two evidence/metric findings; independently rereview.
5. Resume TASK-280, then dispatch TASK-281 and TASK-286 in separate scopes.
6. Dispatch TASK-282 and TASK-283 only after their dependencies and output ownership are clear.
7. Run TASK-287 last; link this handoff, all event IDs, review artifacts, metrics, and session-cleanup evidence.

Graph validation is intentionally red at shutdown because the two READY tasks still have overlapping registered paths; mirror validation passes. No task is marked complete merely because the weekly limit was reached. All unfinished work is recoverable from the canonical records above.
