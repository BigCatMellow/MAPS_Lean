# Helper Assignment — TASK-234 Parity Contradiction Pass

- status: complete
- owner: codex-lab-lilo
- helper: helper-discovery-clearfront-zero
- provider: codex
- created_at: 2026-07-18
- scope: read-only contradiction and omission pass for deployment-source parity

## Purpose

Independently test whether MAP's current records support a claim about the
operator's CommandCenter source/update path. Focus on contradictions between
the installer/template, documented checkout paths, task/release artifacts, and
the no-deployment-change boundary.

## Boundary

- Read only workspace records and explicitly accessible candidate paths.
- Do not edit UI, deployment state, task state, policy, authority, shared
  state, or TASK-227.
- Do not propose UI features. Classify only source-parity blockers, evidence
  gaps, or a minimal read-only next action.

Write your report at:

- `MAP_System/artifacts/experiments/task234-parity-contradiction-zero-2026-07-18.md`

Use concise evidence-backed findings and notify lilo through hcom
`intent=inform` on completion.

## Outcome

Completed at `2026-07-18T06:46:53Z`; report:
`MAP_System/artifacts/experiments/task234-parity-contradiction-zero-2026-07-18.md`.
It found two blockers: stale `/home/home` provenance disagrees with the
configured `/home/mellow` launch target, and the installed backend differs
materially from the installer template. No deployment, UI, policy, or
authority change was made.
