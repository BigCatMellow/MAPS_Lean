# TASK-281 Pilot: Immutable Task Revisions and Minimal Run Manifests

- task: `TASK-281`
- implementer: `claude-lab-venu`
- date: 2026-07-27
- status: bounded pilot evidence, PARKED pending independent review
- source: `MAP_System/artifacts/planning/roles-system-map-improvement-review.md`
  (P1 — Add task revision and minimal run manifests), building on
  `EXP-0005`'s manifest-size-reduction pattern

## Scope

Deliver a standalone, additive capability (`scripts/run_manifest.py` plus
`migration/run_manifest_schema.sql`) that can bind one immutable task
revision to a unique run ID and record its execution context by reference,
not by copying content. This pilot does **not** wire manifest creation into
`graph/runner.py`'s live dispatch loop (not a TASK-281 output path; changing
shared dispatch code is out of this task's registered scope) and does **not**
authorize production rollout. It demonstrates the capability against a real
task and measures it the way `EXP-0005` measured orientation manifests.

## Hypothesis

A run manifest can retain every fact a reviewer needs to reproduce which
exact task and context revision a run used, and to detect drift after the
fact, while using substantially fewer bytes than copying the full task
definition and referenced context.

## Safety-fact rubric (analogous to EXP-0005's six-row rubric)

| # | Fact | Retained by | Proven by |
|---|---|---|---|
| 1 | Exact task revision used (content hash of the task's stable definition) | `run_manifests.task_revision` | `test_reviewer_can_reproduce_exact_revision_from_run_id`, `test_check_stale_detects_task_definition_change` |
| 2 | Exact context revision used, per reference | `run_manifest_context_refs.sha256` | `test_context_stored_as_reference_and_hash_not_copy`, `test_check_stale_detects_context_file_change` |
| 3 | Accountable execution identity (worker, session) | `run_manifests.worker_id`, `.session_id` | `test_manifest_records_all_required_fields` |
| 4 | Normalized role used for the run (never raw free-form role text) | `run_manifests.role_id`, `.role_source` | `test_manifest_records_all_required_fields` |
| 5 | Declared writable scope and runtime limits | `run_manifests.writable_scope`, `.runtime_limits` | `test_manifest_records_all_required_fields` |
| 6 | Staleness is detectable, and lifecycle churn (status/attempt/heartbeat) never manufactures a false positive | `check_stale()` | `test_check_stale_detects_task_definition_change`, `test_check_stale_detects_context_file_change`, `test_check_stale_ignores_lifecycle_field_churn` |

All six rows pass under `MAP_System/tests/test_run_manifest.py` (10/10
focused tests, run against isolated scratch databases). Evidence is the
automated regression suite rather than a separate blinded human evaluator —
`EXP-0005`'s methodology fits a one-shot orientation-context comparison;
here, the independent review this task still requires before approval
(`AGENTS.md`'s standard review gate, distinct from the implementer) serves
the equivalent independence role for the safety-fact claims.

## Size measurement

Method: for a real completed task (`TASK-280`), generate a run manifest
against an isolated scratch database seeded from that task's live canonical
fields, referencing the six real source files most relevant to that task's
work as context. Compare the manifest's JSON byte size against the byte size
of (a) copying those six files in full plus (b) the task's full exported
JSON — the two things a reviewer would otherwise need retained in full to
answer "what exactly did this run see."

| Metric | Bytes |
|---|---|
| Full context files (6 files, copied in full) | 99,551 |
| Full task JSON | 2,112 |
| **Full control total** | **101,663** |
| **Run manifest (references + hashes only)** | **1,499** |
| **Reduction** | **98.53%** |

This exceeds `EXP-0005`'s 94.11% scenario-local reduction and its
predeclared-maximum framing, though the two experiments measure different
things (orientation-recovery context vs. dispatch-time run context) and are
not directly comparable pass/fail against each other's numeric threshold —
`EXP-0005` did not predeclare a threshold for this scenario. The comparison
here is offered as a size-order sanity check, not a repeat of `EXP-0005`'s
own hypothesis test.

Reproduction: the measurement script builds an isolated scratch DB (never
the canonical `map.db`), copies `TASK-280`'s real row from the live database
read-only, and calls `scripts/run_manifest.py`'s `create_manifest()`
directly. No canonical state was written by this measurement.

## Result

- pass: all six safety-fact rubric rows are retained and regression-tested;
  the pilot manifest is 98.53% smaller than the equivalent full-copy
  control for a real task; document-only and Git-backed runs are both
  supported without forcing a meaningless commit revision
  (`test_document_only_task_does_not_require_base_revision`,
  `test_git_backed_task_records_base_revision`); staleness detection
  distinguishes genuine task/context drift from ordinary lifecycle field
  churn.

## Decision

- [ ] adopt
- [ ] revise
- [ ] reject
- [x] park

## Notes

- Parked as bounded pilot evidence, not adopted as a dispatch requirement.
  This pass validates that the manifest schema and script can retain the
  needed facts compactly for one real task; it does not authorize wiring
  manifest creation into `graph/runner.py`'s live dispatch loop, making
  manifests mandatory, or treating an absent manifest as a policy violation.
  A later proposal to integrate manifests into dispatch needs its own task,
  its own independent review, and explicit operator authorization, per this
  task's acceptance criteria and `SELF_REPAIR_SYSTEM.md`'s STRUCTURAL-change
  posture for anything that would change dispatch behavior.
- `migration/run_manifest_schema.sql` is intentionally kept separate from
  `migration/schema.sql` for the same reason: this is additive pilot schema,
  applied idempotently by `run_manifest.py` itself, not yet merged into the
  core schema any other task's `connect()` implicitly depends on.
- Compatibility: `run_manifest.py` reuses `validate_task_schema.normalize_role`/
  `load_role_registry` (TASK-280) read-only to derive `role_id`/`role_source`;
  it does not modify that module and has no output-path claim on it.
