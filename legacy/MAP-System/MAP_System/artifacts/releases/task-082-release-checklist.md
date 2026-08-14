<!-- hpom: file: artifacts/releases/task-082-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-28 -->
<!-- hpom: verified_against: DEC-032 release-backlog authority -->
<!-- hpom: confidence: MEDIUM -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-082

## Header

```
task_id:      TASK-082
released_by:  mapfinish-rafa
release_date: 2026-07-28
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Known gap (accepted, not glossed)

One of TASK-082's 10 `output_paths`,
`/home/home/Projects/Onion-workbench/claude-code-comms/COORDINATION_BRIDGE.md`,
cannot be verified. I independently confirmed (not just relying on prior
triage): `/home/home` does not exist on this host at all (`ls /home/home` →
No such file or directory), and no `Onion-workbench` directory exists
anywhere under `/`, `/home/mellow`, or `/home/mellow/Projects` (which
contains only `CommandCenterUI`, `MultiAgentProject`, `PocketOS`). This is
the `/home/home` → `/home/mellow` host user rename losing an external,
non-MAP-repo sub-output — a minor cross-repo bridging note, not the
substantive deliverable of this task.

I am releasing anyway, not holding this back, because: (a) the file was a
minor bridging note in a *different* project's repo, explicitly scoped as
"bridging note only" in `files_in_scope`, not this task's core deliverable;
(b) every other output path (coverage matrix, agent-status reconciliation,
DEC-013, SYN-0001) is intact, was independently verified below, and is
still actively depended upon by later work (TASK-097 explicitly re-applies
"TASK-082 semantics" for agent status); (c) the loss is an infrastructure
event (host rename) unrelated to the quality or completeness of the MAP-side
work, and nothing can recover or re-verify that file's content today. This
is recorded here as an accepted, visible gap, not silently ticked past.

## Summary

9 of 10 `output_paths` verified present and substantive today (the 10th is
the accepted gap above). Release tier is `full` (`classify_release()`:
output touches `shared/`).

- **Shared-file updates complete**: `shared/current-state.md` (261 lines)
  and `shared/decisions.md` (988 lines, contains `DEC-013`) both exist and
  are current — this check refers to the MAP `shared/` outputs, which are
  fully accounted for; the external Onion-workbench path is handled
  separately above since it is not a MAP shared file.
- **Decisions recorded**: `shared/decisions.md` line 201,
  `## DEC-013: Synthesis And Experiment Record Types Stay Active, Not
  Mandatory`, matches this task's acceptance criterion directly.
- **Follow-up tasks created**: `tasks/TASK-097.json` explicitly targets
  drift in "TASK-082 semantics" for agent status
  (inactive/session_ended/tool_identity conventions this task defined),
  citing SYN-0001 (also a TASK-082 output) by name for the same
  two-readers-one-truth pattern.
- **Event log entry prepared**: full real review cycle in
  `events/events.jsonl` — `:294` (created), `:298` (SUBMISSION), `:299`
  (CHANGES_REQUESTED, codex-lab-limo, 3 named findings), `:300` (rework),
  `:301` (resubmission with root-caused fixes for all 3 findings), `:302`
  (APPROVED), `:304` (operator-directive closure). This is a genuinely
  reviewed task, not a rubber-stamp.
- **Emergence capture considered**: this task's own deliverable created
  `emergence/synthesis/SYN-0001-two-readers-one-truth.md`, the first
  synthesis record in the system, built from six of that week's real
  incidents (per the SUBMISSION event) — emergence capture is not just
  considered, it is the task's own primary output.

Rollback: reversible by normal means for every verifiable output (git
revert, supersede DEC-013 with a later decision). The lost external file has
no rollback path since it cannot be re-created from anything recoverable on
this host; this is accepted as the one caveat above, not treated as
blocking.

This task is ready to be RELEASED with the caveat stated above: the core
deliverable is intact, independently re-verified, still actively depended
upon, and the one lost sub-output is an external, non-substantive artifact
whose loss is visible in this record rather than silently absorbed.
