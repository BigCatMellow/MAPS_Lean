<!-- hpom: file: artifacts/releases/task-090-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-28 -->
<!-- hpom: verified_against: DEC-032 release-backlog authority -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-090

## Header

```
task_id:      TASK-090
released_by:  mapfinish-rafa
release_date: 2026-07-28
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

All 10 `output_paths` verified present today. Release tier is `full`
(`classify_release()`: output touches `shared/`).

- **Shared-file updates complete**: `shared/canonical-repo.md`,
  `shared/current-state.md`, `shared/decisions.md`,
  `notes/command-center-lab-restart-startup.md`, `agents/status.json`,
  `agents/limit-watcher-state.json`, `emergence/INDEX.md` all exist and
  remain current — `canonical-repo.md` itself still cites TASK-090 today
  ("Operator hcom #17759 instructed agents to stop waiting... TASK-090
  applies that confirmation to refresh this stale shared state").
- **Decisions recorded**: `shared/decisions.md` line 220,
  `## DEC-014: Canonical Repo Is Projects/MultiAgentProject`, explicit
  header `Owner: command-center (operator confirmation via hcom #17759;
  recorded by codex-lab-limo, TASK-090)`.
- **Follow-up tasks created**: `events/events.jsonl:349` shows TASK-097 set
  to `BLOCKED` with an explicit dependency on TASK-090 to avoid an
  output-path collision on `agents/status.json` — a direct, verifiable
  follow-up relationship, not an incidental mention.
- **Event log entry prepared**: `events/events.jsonl:352` (created), `:347`
  (PROGRESS, safe-portion completion), `:348` (SUBMISSION, full completion
  after operator confirmation), `:382` (APPROVED) all exist for TASK-090.
- **Emergence capture considered**: `emergence/ideas/IDEA-0009-rns-should-ignore-superseded-and-disposable-sessions.md`
  is a direct task output, filed to capture the RnS
  watcher-resurrects-superseded/disposable-sessions gap found during this
  task, per its own acceptance criterion ("Emergence idea filed for the RnS
  superseded/disposable-session gap").

Rollback: reversible by normal means — DEC-014 can be superseded by a later
decision (as it already documents happening to DEC-012), and the durable
agent-status/watcher-state changes are ordinary source/state files. No
special rollback steps required.

This task is ready to be RELEASED: DEC-014 is the live canonical-repo
decision today, still referenced and refined by later work
(`canonical-repo.md` cites TASK-267 as a later refinement), and all five
checks above are independently verifiable in the repo today.
