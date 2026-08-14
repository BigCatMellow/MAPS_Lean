# Helper Assignment - TASK-323/324 independent review

- status: active
- owner: claude-lab-sumi
- provider: claude
- model: sonnet
- created_at: 2026-08-10
- scope: Independent review of two SUBMITTED tasks (owner claude-lab-sumi,
  cannot self-review). TASK-323 (P0.2 repair): verify events.jsonl NUL
  corruption at line 18785 is actually repaired (check REPAIR-0013,
  validate_events.py should report 0 errors), TASK-315's checklist_path
  backlink is actually fixed (REPAIR-0014, check
  MAP_System/tasks/TASK-315.json / task_release_records table), and spot-check
  a few of the 22 wikilink dispositions in
  MAP_System/artifacts/recovery/p02-validation-debt-repair-2026-08-10.md for
  plausibility. TASK-324 (P0.3 disposition): spot-check a few of the 12
  disposition entries in
  MAP_System/artifacts/reports/p03-lifecycle-backlog-disposition-2026-08-10.md
  against their actual events.jsonl history, especially TASK-311's
  "genuinely-blocked" claim. Report BLOCKER/REQUIRED/RECOMMENDED findings via
  hcom to claude-lab-sumi. Do not approve/release either task yourself.
