# Legacy Removal Checklist

Use this before deleting top-level `legacy/`.

**Current answer: DO NOT DELETE YET.** The useful runtime/knowledge has been
preserved and the replacement stack is verified, but independent review/merge,
final reference/privacy checks, and explicit operator deletion approval remain.

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
- [x] run-manifest relationship to AGI documented.
- [x] implementer evidence vs reviewer verification documented.
- [x] semantic reviewer-independence/continuity rule documented.

## 3. Replacement runtime — current stacked branch

The following are implemented in the PR #9→TASK-014 review stack and were
verified together in GitHub Actions run `31845946112`:

- [x] SQLite task state has one canonical mutable store.
- [x] atomic claim race has exactly one winner.
- [x] owner vs active claimant semantics are separate.
- [x] stale lease recovery does not change accountable owner.
- [x] durable submission author enforces current no-self-review gate.
- [x] structural AGI gate protects `READY` in the same write transaction.
- [x] active output paths reserve conflicting task scope.
- [x] explicit policy fields and operator approval gate consequential dispatch.
- [x] durable halt state blocks lanes without mutating task truth.
- [x] LangGraph is read-first and checkpoints into a separate SQLite DB.
- [x] hcom adapter is project-isolated and has no task-store authority dependency.
- [x] RnS checks ACTIVE task + current claimant before recovery and cannot steal a claim.
- [x] RnS has no mandatory WezTerm dependency.
- [x] Ollama/Aider helpers require ACTIVE parent scope and have no completion/review authority.
- [x] fresh-clone installer/smoke executes from active code without reading/executing `legacy/` or migration snapshots.

**Important:** these checks describe the current stacked review branch. They do
not mean the replacement runtime is already merged to `main`.

## 4. Integrated verification

GitHub Actions run `31845946112`:

- [x] installed `runtime/requirements.txt` on Python 3.12.
- [x] **64/64 tests passed** with `ResourceWarning` treated as error.
- [x] real LangGraph SQLite checkpoint integration passed.
- [x] hcom adapter fake-CLI tests passed without live session side effects.
- [x] RnS recovery tests passed.
- [x] bounded Ollama/Aider helper tests passed with fake tools.
- [x] SQLite concurrency/AGI/review tests passed.
- [x] disposable smoke reached `DONE` through guarded lifecycle.
- [x] disposable smoke verified FK=ON, WAL, 5000ms busy timeout.
- [x] LangGraph smoke created a DB separate from task truth.
- [x] installer passed Bash syntax check and preview execution.

The first integrated run exposed misuse of nonexistent `MutationResult.data` in
new tests/smoke code. It was corrected to `.task`, propagated across the stack,
and the full suite was rerun green.

## 5. Preserved execution-integrity work not yet fully active

These are not reasons to restore old legacy subsystems, but their preserved
lessons still need an explicit final disposition before migration snapshots are
removed:

- [ ] frozen run manifest for high-risk/resumable executions.
- [ ] active continuity-lineage enforcement for reviewer independence after session rotation.
- [ ] general core-agent filesystem run-scope verification beyond task output reservation/helper scope.
- [ ] decide whether criterion-level evidence needs a richer active schema than current submission + review records.
- [ ] decide whether a separate release gate is needed beyond risk-tiered review/completion for Lean.

Migration snapshots stay until these are deliberately implemented or rejected.

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

Before deleting `legacy/`, all of these must be explicit:

```text
Legacy audit complete: YES
Useful source/knowledge preserved: YES
Replacement runtime reviewed: NO — deferred
Replacement runtime merged to main: NO
Full integrated verification green: YES — run 31845946112
Execution-integrity follow-ups disposed: NO
Final dependency/reference sweep: NO
Final privacy/secret sweep: NO
Removal approved by operator: NO
Removal PR/commit: none
```

Do not delete `legacy/` while any required `NO` remains.
