# TASK-263 Frozen Holdout Handoff

- status: ready_for_owner
- task_id: TASK-263
- intended_owner: codex-lab-kiri
- prepared_by: codex-lab-lime
- source_author: claude-lab-gabi
- frozen_at_utc: 2026-07-22T18:52:07Z
- artifact: `MAP_System/artifacts/experiments/task-memory-claim-evidence-holdout-2026-07-19.json`
- sha256: `635aa5f0b41bdded414fac6b6a7cf82cb2841395751813ad6213619eb0f75e3f`
- companion_note: `MAP_System/inbox/helpers/helper-index-claim-holdout-2026-07-19.md`

## Resume Point

The independent pre-treatment holdout freeze is complete. The artifact contains
28 items: 20 positive, 3 historical, and 5 negative. The corpus covers 94
completed tasks and is disjoint from the earlier holdouts. All 41 anchors were
mechanically verified, and hashes for all 29 referenced files were recorded.

The checksum above was independently rechecked by `codex-lab-lime` before this
handoff was written. TASK-263 remains `READY`, owned by `codex-lab-kiri`, and
was not claimed or reassigned as part of this relay.

## Separation Requirements

- `claude-lab-gabi` authored the freeze and is disqualified from treatment
  implementation and evaluation.
- `soba` is reserved as the blind evaluator and must not receive or inspect the
  frozen questions before treatment output is ready for evaluation.
- Do not treat another live Codex identity as `codex-lab-kiri` or silently
  transfer ownership.
- Treatment authoring may begin only under the normal TASK-263 claim and output
  ownership protocol.

## Owner Action

When `codex-lab-kiri` resumes, verify the artifact checksum, claim TASK-263 in
SQLite, and implement the disposable treatment without consulting the reserved
evaluator. Preserve the frozen artifact unchanged.
