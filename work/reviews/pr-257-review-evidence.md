# PR #257 review evidence — lineage-bootstrap wiring scoping note (#255 §8 B)

Independent verification-only review by maps-lean-nava (gela authored; nava
reviewed #255 and traced the deadlock). Design note, 1 file, +386/-0. No
runtime/checklist change. Verdict SCOPE-FOR-IMPL.

## 1. `record_run_session_link` is a fully standalone guarded store write — CONFIRMED

`runtime/state/run_lineage.py:262`, `RunSessionLineageMixin` method. Direct
`sqlite3` under `BEGIN IMMEDIATE`; does not import/construct/call
`HarnessService` or any adapter. Signature matches the note exactly:
`(run_id, worker_id, *, adapter_id, session_id, evidence_ref, created_by,
replaces_link_id=None, now=None) -> MutationResult`.

First-ATTACH precondition table in §2 matches the source line-for-line and in
order: `INVALID_SESSION_LINK` → `RUN_NOT_FOUND` → `RUN_WORKER_MISMATCH` →
`TASK_NOT_FOUND` → `PROJECT_CONTEXT_UNAVAILABLE` → `RUN_NOT_OWNED`
(`status==ACTIVE and claimed_by==worker_id`) → `LEASE_EXPIRED` → `RUN_STALE`
→ `SESSION_LINEAGE_INVALID` → `SESSION_ALREADY_BOUND` (schema
`UNIQUE(project_id,adapter_id,session_id)`) → `UNEXPECTED_REPLACEMENT_LINK` /
`MANIFEST_SESSION_CONFLICT`. On success inserts `relation='ATTACH',
replaces_link_id=NULL`; append-only.

Chain-validity rules (`_resolve_run_session_conn`) all require ≥2 rows or a
manifest/project mismatch; on empty history the resolver returns
`UNBOUND`/`ADAPTER_UNPROVEN` and the first ATTACH cannot trip any of them.

## 2. One ATTACH row breaks the deadlock on BOTH paths — CONFIRMED

- Reverse lookup: `resolve_session_run(project_id, "hcom", session_id)` selects
  `run_id FROM run_session_links` on the `UNIQUE` triple → feeds
  `RecoverySupervisor._resolve_run_id` (`supervisor.py:178`); without a row the
  incident gets no `run_id` → `_resolve_harness_binding` returns
  `no_run_id_bound`.
- EXPLICIT lineage: `_resolve_run_session_conn` with a single well-formed ATTACH
  → terminal `"state": "EXPLICIT"`. `_resolve_harness_binding` checks
  `resolve_run_session(run_id)["state"] == "EXPLICIT"` (`supervisor.py:244–246`)
  then the `adapter_id`/`session_id` match.

Same table, same row, satisfies both.

## 3. No operator decision — self-gate to the run's live ACTIVE claimant — CONFIRMED

`RUN_NOT_OWNED` unless `task.status == "ACTIVE" and task.claimed_by ==
worker_id`, plus `LEASE_EXPIRED`. The only writer is the worker currently
running the task, on their own run — same authority level as `maps heartbeat` /
`maps submit`, strictly narrower than `create_run_manifest` / `maps flow start`.
Lineage records "do not grant task authority". §4's "no operator decision" is
correct; the *whether-to-wire* question is already answered by the operator per
#255 §8.

## 4. §6 flip claims — CONFIRMED each

- **H5** — flips with a documented exercised pass (a real `resume_denied`,
  remediated). The wiring PR alone does not flip it.
- **6.16 / E6(b)** — flips with a `--require-canonical-run` (worktree-bound)
  exercised pass so `_require_bound_worktree` executes.
- **6.22** — does NOT flip. `MemoryProvenanceGuard` fires on `BEFORE_SEND`;
  `HarnessService.send()` has no production caller; the recovery path calls
  `harness_service.resume()` only. 6.22 needs a distinct `send()`-path caller —
  the note says exactly this.

## 5. §5 first-exercised-pass trace — ACCURATE

Verified against `runtime/policy/harness_guard.py::__call__`: order is
`_base_evidence` → `_require_live_claim` → `_require_bound_worktree` →
`_require_durable_session`. `_require_live_claim` returns
`_deny("LEASE_EXPIRED", "Continuing execution requires a live task lease.")` —
matches the note's dominant denial. A DENY → `HOOK_DENIED` →
`action="resume_denied"`, `canonical_denials += 1`, 3rd consecutive →
`failed`/`canonical_denial_persistent`. Remediation `maps claim T --worker-id W`
→ re-tick → passes. Alternative first-pass denials (`RUN_WORKTREE_MISMATCH`,
`RUN_STALE`, `TASK_REVISION_STALE`) are all real guard branches.

## 6. Impl slice is genuinely ~1 CLI verb + tests — CONFIRMED

MAY-touch: `runtime/cli.py` (new `run` subparser + `bind-session` +
`_dispatch_run` mirroring `_dispatch_operator`/`_dispatch_skill`; dispatch calls
`store.record_run_session_link(...)` directly) + `tests/test_cli_run.py`.
MUST-NOT fences `runtime/harness/`, `runtime/recovery/`, the store method
signature/guard, any authority gate / `--enforce-*` flag / checklist STATUS
flip / running a pass. Acceptance criteria concrete. SCOPE-FOR-IMPL sound.

## Nits (non-blocking, for the impl lane)

- §5 predicts `LEASE_EXPIRED` as the dominant denial from "a stopped session's
  lease has typically lapsed". The integration test should control the lease
  explicitly (seed an expired `lease_expires_at`) and assert the denial *class*
  (`HOOK_DENIED` → `resume_denied`) rather than pin one code.
- The `session_id` (hcom id) vs `session_name` (display, used by
  `recovery-tick --binding`) distinction should surface in `--help`, not just
  the note.

## Verdict: APPROVE

`python3 -m runtime.smoke` → exit 0.

reviewer: maps-lean-nava
head_sha: 88d38e0948c5119df27e38e4946c09a7355e81c6
independent: true
summary: APPROVE — verification-only review of the lineage-bootstrap wiring scoping note (#255 §8 B); verified against merged code that record_run_session_link is a standalone claimant-gated store write with no HarnessService/adapter dependency, that one first ATTACH row breaks the deadlock on both the reverse-lookup and EXPLICIT-lineage paths, that the self-gate to the run's live ACTIVE claimant means no operator decision, and that §5/§6 traces are accurate (H5 + 6.16/E6(b) flip with an exercised pass, 6.22 does not — it needs separate send()-path wiring); the impl slice is genuinely ~1 CLI verb (maps run bind-session) + tests with a clean MAY/MUST-NOT.
