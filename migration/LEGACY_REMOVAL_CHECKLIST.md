# Legacy Removal Checklist

Use this before deleting top-level `legacy/`.

**Current answer: DO NOT DELETE YET.** The useful runtime/knowledge is preserved
and the replacement stack is verified. Remaining blockers are deferred
independent review/merge, the final reference/privacy sweep, and explicit
operator deletion approval.

## 1. Knowledge and source extraction

- [x] Root policy/system documents audited.
- [x] Runtime/control-plane code inventoried and deep-read where behavior was unique.
- [x] Scripts/tests/notes mapped to useful invariants and regression evidence.
- [x] Repairs/retros/audits/experiments mined, including negative results.
- [x] Large historical/generated datasets explicitly classified rather than falsely described as line-by-line reads.
- [x] Presentation/UI/WezTerm material separated from authority/runtime behavior.
- [x] Durable findings recorded in `LEGACY_KNOWLEDGE_AUDIT.md`.
- [x] Dispositions recorded in `LEGACY_PROMOTION_LEDGER.md`.
- [x] Runtime source preserved under `migration/legacy-runtime-source/`.
- [x] Second-pass execution-integrity source preserved under `migration/legacy-knowledge-source/`.

## 2. Active Lean rule coverage

- [x] consequential operator authority.
- [x] one accountable owner.
- [x] AGI `READY` gate.
- [x] output/write boundaries.
- [x] capability != authority.
- [x] verification/evidence/review/escalation requirements.
- [x] context packet / trigger-gated context.
- [x] typed failure guidance.
- [x] conflict freeze.
- [x] diagnostic vs repair authority.
- [x] security-specific review trigger.
- [x] run-manifest relationship to AGI.
- [x] implementer evidence vs reviewer verification.
- [x] semantic reviewer-independence/continuity rule.

## 3. Replacement runtime — current stacked branch

The PR #9→TASK-015 review stack now contains deliberate Lean homes for the P0
runtime behavior:

- [x] one canonical SQLite task store.
- [x] atomic claims, leases, owner/claimant separation, and stale-lease recovery.
- [x] structural AGI gate protects `READY` in the same write transaction.
- [x] active output paths reserve conflicting task scope.
- [x] explicit policy flags + operator approval gate consequential dispatch.
- [x] durable halt state blocks routing lanes without mutating task truth.
- [x] LangGraph is read-first and checkpoints into a separate SQLite DB.
- [x] hcom adapter is project-isolated transport with no task-authority dependency.
- [x] RnS verifies ACTIVE task + current claimant before recovery and cannot steal work.
- [x] RnS has no mandatory WezTerm dependency.
- [x] Ollama/Aider helpers require ACTIVE parent scope and cannot complete/review/approve parent work.
- [x] fresh-clone installer/smoke uses only active runtime code.
- [x] high-risk/resumable runs can freeze immutable task/context/scope manifests.
- [x] run staleness detects changed task definition and changed/missing context.
- [x] Git run-scope verification reports out-of-scope changes without auto-reverting them.
- [x] continuity lineage is enforced by router, review claim, and final review transition.
- [x] optional criterion-level implementer claims and reviewer verdicts remain separate.

These checks describe the stacked review branch. They do **not** mean the stack
is already merged to `main`.

## 4. Integrated verification

Latest full-stack GitHub Actions run: `31847038026`.

- [x] Python 3.12 active dependency install passed.
- [x] **79/79 tests passed** with `ResourceWarning` treated as error.
- [x] SQLite concurrency/AGI/claim/review tests passed.
- [x] real LangGraph SQLite checkpoint integration passed.
- [x] hcom fake-CLI transport tests passed without live side effects.
- [x] RnS recovery/backoff/suppression tests passed.
- [x] bounded Ollama/Aider fake-tool tests passed.
- [x] run-manifest/context-hash/staleness/scope tests passed.
- [x] SQLite mechanically rejected run-manifest/context mutation.
- [x] continuity and criterion-evidence review gates passed.
- [x] disposable smoke reached `DONE` through guarded lifecycle.
- [x] disposable smoke verified FK=ON, WAL, 5000ms busy timeout.
- [x] LangGraph smoke created a DB separate from task truth.
- [x] installer Bash syntax and preview execution passed.

## 5. Execution-integrity disposition

The second archaeology pass is now intentionally disposed rather than left as
an open-ended "maybe rebuild it" list:

- [x] **Run manifest:** implemented in smaller active form for high-risk/resumable work.
- [x] **Continuity-lineage reviewer independence:** implemented at routing and canonical review transitions.
- [x] **General filesystem run scope:** implemented as frozen writable scope + read-only Git verifier.
- [x] **Criterion evidence:** implemented as an optional mode; ordinary tasks retain the simpler review path.
- [x] **Separate release state machine:** rejected for Lean core.

### Release rationale

Legacy's `APPROVED → RELEASED` subsystem largely reconciled multiple task/file
mirrors and an old mandatory checklist. Lean has one task truth and risk-tiered
review.

For `OPERATOR_VISIBLE_RELEASE_CHECK`, the final approved review/completion
summary is the durable operator-visible release summary. Actual destructive,
external, security-sensitive, or otherwise operator-gated actions still require
explicit operator approval through policy. A product that needs a real deploy or
release operation should model that operation as its own task/action rather than
add a universal second lifecycle.

Migration snapshots remain until the reviewed stack reaches `main` and the
final reference/privacy sweep is complete.

## 6. Reference cleanup before legacy deletion

Run from repository root after the reviewed stack reaches `main`:

```bash
rg -n 'legacy/' --glob '!legacy/**'
rg -n 'migration/legacy-runtime-source|migration/legacy-knowledge-source' runtime tests playbook docs templates scripts
rg -n 'MAP_System|MultiAgentProject' --glob '!legacy/**' --glob '!migration/legacy-runtime-source/**' --glob '!migration/legacy-knowledge-source/**'
```

Then confirm:

- [ ] no active runtime imports `legacy` or migration source.
- [ ] no active test requires legacy runtime state.
- [ ] fresh install/setup requires no legacy/migration execution path.
- [ ] remaining provenance references are clearly historical/non-executable.
- [ ] selected preserved evidence documents receive final secret/privacy review.

## 7. Optional systems already decided

- [x] full Library/Librarian: defer unless new measurements justify it.
- [x] task fingerprint/memory retrieval: experimental; negative/mixed evidence preserved.
- [x] continuous paid Discovery Agent: reject; use bounded event-triggered discovery.
- [x] cost governance: optional when autonomous paid dispatch makes it useful.
- [x] formal verification beyond focused state/property tests: optional.
- [x] CommandCenterUI/Mission Control implementation: not Lean core.
- [x] WezTerm cockpit: not required.

## 8. Merge/removal gate

```text
Legacy audit complete: YES
Useful source/knowledge preserved: YES
Replacement runtime reviewed: NO — deferred by operator
Replacement runtime merged to main: NO
Full integrated verification green: YES — run 31847038026
Execution-integrity follow-ups disposed: YES
Final dependency/reference sweep: NO — perform after reviewed merge
Final privacy/secret sweep: NO
Removal approved by operator: NO
Removal PR/commit: none
```

Do not delete `legacy/` while any required `NO` remains.
