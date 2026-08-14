# Helper Assignment - release checklists batch 2 (TASK-301/302/303/305/309/313)

- status: active
- owner: claude-lab-sumi
- provider: claude
- model: sonnet
- created_at: 2026-08-10
- scope: Write real, verified release checklists (template:
  MAP_System/templates/release-checklist.md) for TASK-301, TASK-302,
  TASK-303, TASK-305, TASK-309, TASK-313 - all APPROVED, all classified
  ready in
  MAP_System/artifacts/reports/p03-lifecycle-backlog-disposition-2026-08-10.md
  (read that file's entries for each - don't redo its verification, DO
  re-check flagged caveats). Special handling: TASK-303 - thin evidence for
  a policy-tier operator-approval change (no standalone review artifact,
  3-minute review-to-approve gap); independently verify hcom request 30843
  (search transcripts/events for it) before writing the checklist, note the
  verification result explicitly. TASK-309 - task JSON cites a dead path
  (03_kickoff/MAP_RECOVERY_PLAN_REVIEW.md) as approval evidence; correct or
  remove that citation (map-authority task describe/amend-criteria, not
  direct SQL) before/as part of releasing, don't just ignore it. Do NOT
  touch TASK-311 (excluded, genuinely-blocked - missing deliverable). For
  each ready task: write the checklist, then run: map-authority task
  release TASK-NNN --released-by claude-lab-sumi --checklist <path>
  --summary "...". Report progress to claude-lab-sumi via hcom as you go,
  final summary when done.
