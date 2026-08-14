# Legacy Removal Checklist

Use this immediately before deleting top-level `legacy/`.

**Current migration state: READY FOR THE SEPARATE DELETION ACTION.**

The replacement runtime is merged, reviewed with the independence caveat recorded
below, mechanically verified, privacy-swept, and proven free of active execution
dependencies on `legacy/` or the curated migration snapshots.

Deletion itself is intentionally **not** performed here and still requires an
explicit operator-approved deletion change.

## 1. Knowledge and source extraction

- [x] Root policy/system documents audited.
- [x] Runtime/control-plane code inventoried and deep-read where behavior was unique.
- [x] Scripts/tests/notes mapped to useful invariants and regression evidence.
- [x] Repairs/retros/audits/experiments mined, including negative results.
- [x] Large historical/generated datasets classified without falsely claiming line-by-line review.
- [x] Presentation/UI/WezTerm material separated from authority/runtime behavior.
- [x] Durable findings recorded in `LEGACY_KNOWLEDGE_AUDIT.md`.
- [x] Dispositions recorded in `LEGACY_PROMOTION_LEDGER.md`.
- [x] Runtime source preserved under `migration/legacy-runtime-source/`.
- [x] Second-pass execution-integrity source preserved under `migration/legacy-knowledge-source/`.

## 2. Replacement runtime

PR #16 merged the complete reviewed integration to `main` as squash commit:

```text
78791fca0d5cd0def5bae2c5b2eb9addcbf0770e
```

The former stacked PRs #9–#15 are closed as superseded and retained only as
implementation/review history.

Active Lean now has deliberate homes for the required behavior:

- [x] one canonical SQLite task store.
- [x] structural AGI gate and atomic `READY` mutation.
- [x] atomic claims, leases, stale-lease recovery, owner/claimant separation.
- [x] parent/child output-scope reservation conflicts.
- [x] explicit task policy + operator approval + halt gates.
- [x] capability data separate from authority.
- [x] read-first LangGraph routing with a separate checkpoint DB.
- [x] hcom transport with no task-authority dependency.
- [x] RnS recovery only for current known ACTIVE claims/bindings.
- [x] bounded Ollama/Aider helper lanes with no parent-task approval authority.
- [x] preview-first fresh-clone installer and disposable smoke.
- [x] immutable run/context binding and task/context staleness proof.
- [x] writable/forbidden Git scope verification, including rename endpoints.
- [x] declared run-budget checks + durable exhaustion evidence.
- [x] continuity-aware reviewer independence at route/claim/final review.
- [x] optional criterion-level implementer claims and reviewer verdicts.
- [x] criterion/run records mechanically protected as append-only where specified.
- [x] no universal second `APPROVED → RELEASED` state machine.

## 3. Integration review

See [`../work/reviews/RUNTIME_INTEGRATION_REVIEW.md`](../work/reviews/RUNTIME_INTEGRATION_REVIEW.md).

- [x] fresh adversarial integration review completed.
- [x] review found and fixed material correctness/safety issues before merge.
- [x] GitHub-hosted compile, Ruff, Bandit, dependency, regression, smoke, and
  installer checks independently reproduced the mechanical evidence.
- [x] independence caveat is explicit: the adversarial review was performed by
  the same assistant continuity that participated in implementation, so it is
  **not** mislabeled as an independent human/model reviewer.

The operator subsequently instructed the migration work to be completed until
legacy deletion is the final step. The integrated review + mechanical verification
is the recorded review basis for this migration closure; historical stacked task
files remain snapshots of their earlier per-PR review requirements rather than
being rewritten to claim an independent model review that did not occur.

## 4. Verification

Merged `main` verification after PR #16:

- [x] Actions run `31850974870` passed the full runtime workflow.

Final removal-readiness verification on the merged runtime plus the dependency
gate:

- [x] Actions run `31851301307` passed.
- [x] active dependency gate scanned **50 executable/config files** and reported PASS.
- [x] Python compile passed.
- [x] Ruff fatal-error checks passed.
- [x] Bandit medium/high scan passed with only the separately audited B608 class excluded.
- [x] `pip check` passed.
- [x] **93/93 unit tests passed** with `ResourceWarning` treated as error.
- [x] disposable SQLite lifecycle reached `DONE`.
- [x] smoke verified FK=ON, WAL, 5000 ms busy timeout.
- [x] real LangGraph SQLite smoke returned `wait_or_reconcile` using a separate checkpoint DB.
- [x] installer Bash syntax and preview passed.

## 5. Preservation privacy / secret sweep

See [`PRESERVATION_PRIVACY_SWEEP.md`](PRESERVATION_PRIVACY_SWEEP.md).

- [x] current curated preservation set: PASS.
- [x] no checked high-signal credential/private-key patterns identified.
- [x] no copied live DB/sidecar, transcript/inbox/message store, log/JSONL,
  settings/status/state snapshot, screenshot/image, or machine-private home path
  identified in the curated snapshots/current indexed tree.

Scope limitation remains explicit: this is a current-tree/snapshot audit, **not**
a forensic scan of every historical Git object or external/local state.

## 6. Final active dependency/reference sweep

See [`FINAL_LEGACY_DEPENDENCY_SWEEP.md`](FINAL_LEGACY_DEPENDENCY_SWEEP.md).

- [x] no active Python import from `legacy`.
- [x] no active runtime/test/script/workflow execution path requires top-level `legacy/`.
- [x] no active execution path requires `migration/legacy-runtime-source/`.
- [x] no active execution path requires `migration/legacy-knowledge-source/`.
- [x] no active old `MAP_System` / `MultiAgentProject` runtime path marker remains.
- [x] no active symlink targets legacy, escapes the repository, or is broken.
- [x] fresh installer/smoke remains independent of legacy/migration execution state.
- [x] remaining `legacy/` mentions are historical, provenance, negative-test, or
  deletion-safety references and are not runtime dependencies.
- [x] the dependency gate is now part of CI, including `main`.

## 7. Optional systems already decided

- [x] full Library/Librarian: defer unless new measurements justify it.
- [x] task fingerprint/memory retrieval: experimental; negative/mixed evidence preserved.
- [x] continuous paid Discovery Agent: reject; use bounded event-triggered discovery.
- [x] cost governance: optional when autonomous paid dispatch makes it useful.
- [x] formal verification beyond focused state/property tests: optional.
- [x] CommandCenterUI/Mission Control implementation: not Lean core.
- [x] WezTerm cockpit: not required.

## 8. Final gate

```text
Legacy audit complete: YES
Useful source/knowledge preserved: YES
Replacement runtime reviewed: YES — same-lineage caveat recorded; independent mechanical verification green
Replacement runtime merged to main: YES — PR #16 / 78791fca0d5cd0def5bae2c5b2eb9addcbf0770e
Full integrated verification green: YES
Execution-integrity follow-ups disposed: YES
Current preservation privacy/secret sweep: YES — PASS
Final dependency/reference sweep: YES — PASS
Deletion safety gate installed in CI: YES

Removal approved by operator: NO
Removal PR/commit: none
```

## Only remaining migration action

**Explicit operator-approved deletion of top-level `legacy/`.**

Do not infer deletion authority from any other approval, merge, task state, or
this checklist. The deletion must be its own explicit operator instruction/change.
