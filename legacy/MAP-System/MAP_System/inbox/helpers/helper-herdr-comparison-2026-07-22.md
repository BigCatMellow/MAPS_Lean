# Helper Assignment - Herdr comparison research

- status: complete
- owner: codex-lab-lime
- provider: claude
- model: haiku
- created_at: 2026-07-22
- scope: research Herdr from public primary sources and compare its approach with MAP and the AI Command Center Lab

## Assignment

Research `https://herdr.dev/` and any official Herdr documentation or source
repository linked from it. Compare Herdr's purpose, architecture, coordination
model, operator experience, persistence, agent lifecycle, task authority,
review model, and observability with the system described by these local files:

- `AGENTS.md`
- `MAP_System/AGENTS.md`
- `MAP_System/shared/project-brief.md`
- `MAP_System/shared/current-state.md`
- `MAP_System/shared/hpom.md`
- `MAP_System/shared/agent-capability-matrix.md`
- `MAP_System/notes/helper-agent-guide.md`

## Deliverable

Write `MAP_System/artifacts/research/SUMMARY-herdr-comparison-2026-07-22.md`
with:

1. A concise factual description of Herdr, with links to primary sources.
2. A comparison table covering genuine similarities and material differences.
3. Practices MAP could adopt now, practices worth testing, and practices that
   do not fit MAP's goals.
4. Concrete recommendations ranked by benefit, effort, and risk.
5. Explicit uncertainty where Herdr's public material does not support a claim.

Do not edit implementation, task state, canonical policy, or Herdr itself. Do
not inspect secrets, private logs, transcripts, or unrelated workspace files.
Recommendations are advisory only; the owning core agent decides whether to
promote them into MAP tasks or emergence records.

## Tier And Safety

- requested_tier: Haiku
- approved_tier: Haiku (default bounded research tier)
- approver: codex-lab-lime under the documented default; no higher-tier
  escalation required
- lower_tier_attempt: not applicable; Haiku is the lowest Claude helper tier
- permission_mode: configured auto mode, limited to public browsing and the
  named read-only local inputs
- verification: every external factual claim needs a primary-source link; the
  owner will review the comparison before integration

## Stop Condition

Stop after the research artifact is written and a completion message with its
path is sent to `codex-lab-lime`. Do not begin implementation or spawn further
agents.
