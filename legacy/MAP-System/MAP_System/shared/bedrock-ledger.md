<!-- hpom: file: shared/bedrock-ledger.md -->
<!-- hpom: project: MAP Bedrock -->
<!-- hpom: state_owner: claude-lab-sumi -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-08-10 -->
<!-- hpom: confidence: MEDIUM (first population, not yet cross-checked by a second agent) -->

# MAP Bedrock Program Ledger

Schema and update rule: see `artifacts/planning/map-bedrock-operating-structure-2026-08-10.md`
Sec 3. This is a durable checkpoint snapshot, not a live projection — it does
not replace `tasks/`, SQLite, or `workflow/task_graph.json`.

| Phase | Gate | Task | Role | Status | Blocker | Next action |
|---|---|---|---|---|---|---|
| 0 | combined P0.1+P0.2+P0.3 (map-2 sec 7) | TASK-321 | Task Owner | released | none | Reconcile remaining Phase 0 baseline gaps below before claiming the combined exit gate met |
| 0 | P0.1 sub-item (authority/rotation) | TASK-316 | Task Owner | approved | none recorded since 2026-08-04 | Release — part of general 29-task release-ceremony backlog, not individually blocked (citation error found/corrected 2026-08-10) |
| 0 | P0.1 sub-item (authority/rotation) | TASK-317 | Task Owner | approved | none recorded since 2026-08-04 | Release — same backlog bucket as TASK-316 |
| 0 | P0.1-adjacent dependency (rotation-transfer gateway, Sec 2 rule 2 depends on it) | TASK-307 | Task Owner | approved | none recorded | Release — same backlog bucket, soft dependency for Bedrock's rotation-transfer rule |
| 0 | P0.1-adjacent dependency | TASK-308 | Task Owner | approved | none recorded | Release — same backlog bucket |
| 0 | P0.1 three-cycle sync proof (map-2 sec 7 exit criterion) | none | Task Owner | not_started | not confirmed reconciled | Explicit check: 3 consecutive scheduled sync cycles succeed under normal load, `map-authority status`/`route` agree |
| 0 | P0.2 durable validation debt | none | Task Owner | blocked | `events.jsonl` NUL corruption at line 18,785 still unfixed, TASK-315 stale `/home/home/...` backlink still broken, 22 wikilink findings unchanged, per `inbox/helpers/helper-librarian.md` 2026-08-09 rerun | Promote to a claimed task; repair in a reviewed, append-only-preserving way per map-2 P0.2 |
| 0 | P0.3 lifecycle backlog disposition | none | Task Owner | not_started | no confirmed disposition record for the map-2-listed APPROVED task set | Produce an explicit released/deferred/superseded/blocked record per task |
| — | D0 program coordinator designation | none | Operator | approved | none | Satisfied — bound to `map-coordinator-hobo` per DEC-039, not re-litigated by this charter |
| — | Bedrock charter itself | none | Task Owner (claude-lab-sumi, informal) | in_review | not yet promoted to a real MAP task; drafted/reviewed outside the formal claim pipeline | Decide whether to formally promote via a claimed task, or accept as-is via a decisions.md entry — currently neither has happened |
| — | Sec 6 `stale_role_bindings` runner check | none | Task Owner | in_review | implemented in `graph/runner.py` (`scan_role_bindings`), backed by `shared/bedrock-role-bindings.json`, 5 focused tests pass; not yet independently reviewed | Route to `helper-bedrock-review-data` for functional review |
| — | map-2 plan rename to "MAP Bedrock" | none | Program Coordinator / Operator | deferred | explicitly deferred by charter Sec 8 — no formal rename decision yet | Operator/coordinator decision, not a default action |

## Checkpoint history

- 2026-08-10: first population, by claude-lab-sumi, immediately after Bedrock
  charter review closed. Not yet cross-checked by a second agent — treat rows
  above as a good-faith initial pass, verify before treating any single row
  as final truth for a real decision.

## P0.1 exit-criterion evidence (2026-08-10, claude-lab-sumi)

Three consecutive scheduled `map-authority-mirror.service` runs (systemd
timer, not manually triggered), all `"ok": true`, same authority revision:
12:30:16, 12:31:56, 12:33:56 EDT (journalctl --user -u
map-authority-mirror.service). Satisfies map-2 plan sec 7 P0.1 exit
criterion "three consecutive scheduled sync cycles succeed under the normal
fixed roster and watcher load." Combined with 30 finalized context-rotations
tonight and repeated freshness/topology-agreement checks, P0.1's exit gate
is now evidenced, not just claimed.
