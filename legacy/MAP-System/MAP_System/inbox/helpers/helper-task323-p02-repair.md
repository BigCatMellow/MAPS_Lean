# Helper Assignment - TASK-323 P0.2 validation debt repair

- status: active
- owner: claude-lab-sumi
- provider: claude
- model: sonnet
- created_at: 2026-08-10
- scope: Execute TASK-323 (claimed by claude-lab-sumi, the accountable
  owner - you are bounded support, not the task owner). Read
  MAP_System/tasks/TASK-323.json for full acceptance criteria. Three parts:
  (1) quarantine+repair the NUL corruption at MAP_System/events/events.jsonl
  line 18785 - preserve original bytes/hash as evidence, do not silently
  rewrite history, use a reviewed append-only-preserving procedure; (2)
  correct TASK-315's stale /home/home/... release backlink via a provenance
  repair record (do not hand-edit via local SQL - this is a mirror host,
  Biggie never mutates map.db directly); (3) triage the 22 wikilink findings
  from MAP_System/inbox/helpers/helper-librarian.md's 2026-08-09 rerun into
  false-positive/resolvable-shorthand/ambiguous-AGENTS/genuinely-missing
  categories with a disposition per finding. Write your work to
  MAP_System/artifacts/recovery/p02-validation-debt-repair-2026-08-10.md.
  Report progress/completion to claude-lab-sumi via hcom. Do not claim
  or submit the MAP task yourself - report to the owner, who submits.
