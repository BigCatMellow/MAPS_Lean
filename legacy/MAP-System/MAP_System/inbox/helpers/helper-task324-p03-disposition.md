# Helper Assignment - TASK-324 P0.3 lifecycle backlog disposition

- status: active
- owner: claude-lab-sumi
- provider: claude
- model: sonnet
- created_at: 2026-08-10
- scope: Execute TASK-324 (claimed by claude-lab-sumi, the accountable
  owner - you are bounded support, not the task owner). Read
  MAP_System/tasks/TASK-324.json for full acceptance criteria. For each of
  TASK-295, 297, 298, 299, 300, 301, 302, 303, 305, 309, 311, 313 (all
  currently APPROVED, not RELEASED - confirmed via
  batch_release_low_risk.py --dry-run that none auto-qualify as low-risk,
  each needs a real hand-checked disposition): check its events.jsonl
  history, task JSON, and any cited artifacts; record an explicit
  disposition (ready-to-release-with-real-checklist / deliberately-deferred
  with reason / superseded / genuinely-blocked with evidence). Do NOT write
  release checklists or release anything yourself in this pass - just
  produce the disposition record. Write to
  MAP_System/artifacts/reports/p03-lifecycle-backlog-disposition-2026-08-10.md.
  Watch for the TASK-307/308 pattern found earlier tonight: a cited evidence
  artifact that doesn't actually exist, or a stale status line contradicted
  by later events - check events.jsonl's full history, don't trust a single
  status field. Report progress to claude-lab-sumi via hcom periodically.
