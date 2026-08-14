# Helper Assignment - release checklists batch 1 (TASK-295/297/298/299/300)

- status: active
- owner: claude-lab-sumi
- provider: claude
- model: sonnet
- created_at: 2026-08-10
- scope: Write real, verified release checklists (template:
  MAP_System/templates/release-checklist.md) for TASK-295, TASK-297,
  TASK-298, TASK-299, TASK-300 - all APPROVED, all classified
  "ready-to-release-with-real-checklist" in
  MAP_System/artifacts/reports/p03-lifecycle-backlog-disposition-2026-08-10.md
  (read that file's entries for each task first - it already did real
  verification work, don't redo it, but DO re-check anything it flagged as
  a caveat). Special handling: TASK-297 - the disposition report flagged no
  explicit operator-approval event found in events.jsonl despite
  requires_operator_approval=true; search harder (hcom transcripts,
  decisions.md) before writing the checklist - if genuinely absent, do NOT
  write a checklist claiming it's satisfied, report back to owner instead.
  For each task ready: write MAP_System/artifacts/releases/task-<NNN>-release-checklist.md,
  then run: map-authority task release TASK-NNN --released-by claude-lab-sumi
  --checklist <path> --summary "..." (yes, you can run map-authority
  directly, it's not owner-specific). Report progress to claude-lab-sumi via
  hcom as you go, and a final summary when done (released X, held Y with
  reason).

## Outcome

Completed at 2026-08-10 (helper-releases-batch1-mive). Released 4/5:
TASK-295, TASK-298, TASK-299, TASK-300. Checklists at
`MAP_System/artifacts/releases/task-{295,298,299,300}-release-checklist.md`.
Each re-verified against the disposition report's specific caveats (not just
existence-checked): TASK-298's evidence doc content checked against all 6
acceptance criteria including the dual functional+security review; TASK-299's
reviewer identity confirmed genuine via context-rotation/watchdog events;
test suites re-run independently via the project venv
(`MAP_System/.venv/bin/python3 -m unittest`), 59 tests pass. Checklists had
to be scp'd to RUKI (`smalls`) before `map-authority task release` would
accept them, since the release script runs on the authority host and
validates the checklist path there, not on this (mirror/KUDU) host — same
for the emergence-capture checklist line, which the release script's regex
requires on one unwrapped line.

HELD: TASK-298 — wait, released, see above. HELD: **TASK-297**. Searched
harder per instructions: `events.jsonl` (only shows peer APPROVED by
helper-review-task297-308-halo, no operator-approval event),
`shared/decisions.md` (no TASK-297 entry), hcom transcript search for
"TASK-297" and separately "operator" (no explicit operator sign-off found
in either). `requires_operator_approval: true` is set and unmet. Did not
write a release checklist claiming it's satisfied. Reported to owner
(claude-lab-sumi) via hcom send — agent was offline (stopped ~10 min prior),
message could not be delivered; recorded here instead. Needs operator
sign-off located/attached, or an explicit decision to keep TASK-297 held,
before release.
