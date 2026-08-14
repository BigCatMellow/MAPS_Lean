<!-- hpom: file: artifacts/releases/task-206-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-206

## Header

```
task_id:      TASK-206
released_by:  claude-lab-gome
release_date: 2026-07-17
reviewed_by:  claude-lab-gome
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

TASK-206 fixes invalid hyphenated hcom `--name` defaults in the AI
Command Center operator wrapper (`ai`) and monitor
(`ai-command-center-monitor`) by omitting `--name` entirely from
operator-side read/control calls (the wrapper isn't itself a persistent
named agent), while preserving `--from command-center` for external
message attribution. Implemented by codex-lab-hana.

- Files: `MAP_System/templates/install/bin/ai`,
  `MAP_System/templates/install/bin/ai-command-center-monitor`,
  `/home/mellow/.local/bin/ai`,
  `/home/mellow/.local/bin/ai-command-center-monitor`.
- Shared files: none beyond the task's own registered output paths.
- Decisions: no new ARCHITECTURE/SCOPE decision — this is a bug fix
  matching the task's own stated acceptance criteria, not a design
  change.
- Follow-ups: none required. The one review round's finding (template/
  installed launcher mismatch from an `ai dashboard` feature that
  leaked into the installed copy during the same edit session) was
  resolved within this same task via rework, not deferred.
- Events: creation, submission, first review (CHANGES_REQUESTED),
  rework/resubmission, approval, and this release are in
  `events/events.jsonl` (trace_id task:TASK-206), `--fail-on-new`
  clean.
- Emergence: considered — no new card. A template/installed-launcher
  parity gap slipping in unnoticed during an edit session is a plausible
  general MAP-hygiene pattern, but this instance was caught by the
  task's own existing acceptance criteria (no new check/process
  needed) and resolved same-task; not distinct enough from ordinary
  review diligence to warrant a card.
- Operator-facing friction: no new operator-friction candidate found.

## Review

- Verdict: APPROVED —
  `MAP_System/artifacts/reviews/task206-review-gome.md` by
  `claude-lab-gome`, after one CHANGES_REQUESTED round. First pass
  verified the core `--name` fix live (working correctly) but found the
  installed `ai` launcher had an `ai dashboard` command absent from the
  repository template — introduced during the same edit session per
  file mtimes (0.14s apart), violating the task's own acceptance
  criterion 3. Rework added the (confirmed intentional) `dashboard`
  feature to the canonical template using the established
  `__LOCAL_BIN__` placeholder pattern; rereview independently
  reproduced an empty normalized diff between both template/installed
  pairs and reran all original live checks with no regression.
- Reviewer independence: implementer was codex-lab-hana; a prior Claude
  reviewer session had gone inactive and a visible helper launch was
  blocked (sandboxed wezterm-tab launch failed, no headless fallback
  used per the helper packet), so codex-lab-hana routed the review
  request to claude-lab-gome directly via hcom — a different core
  agent, no implementation overlap.

## Verification

- `grep -n -- "--name"` on all 4 files: zero self-identifying `--name`
  calls, only the unrelated legitimate `hcom list --names` flag.
- Live `ai status`: exit 0, clean output, no instance-name error.
- Live `ai-command-center-monitor feed` (bounded): renders hcom events,
  MAP events, and agent status cleanly.
- `sh -n` shell syntax: passes on all 4 files.
- Normalized diff (placeholders substituted back to real installed
  values) between each template and its installed launcher: empty for
  both files, independently reproduced by the reviewer.
- `validate_task_mirrors.py`, `validate_task_graph.py`,
  `validate_task_schema.py`, `validate_events.py --fail-on-new`: all
  pass.
