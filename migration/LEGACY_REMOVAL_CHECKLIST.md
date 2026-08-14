# Legacy Removal Checklist

Use this before deleting the top-level `legacy/` directory.

Removal is allowed only when legacy is no longer required for ordinary MAPS
execution, migration, or interpretation.

## 1. Knowledge extraction

- [x] Root policy/system documents reviewed for useful rules.
- [x] Runtime/control-plane directories reviewed.
- [x] `scripts/` inventoried and mapped to behavior/tests.
- [x] `tests/` inventoried; safety-critical regression families identified.
- [x] `notes/` inventoried; unique operating guides reviewed.
- [x] representative repairs and retrospectives reviewed for incident-backed lessons.
- [x] important audits/measurements/experiments reviewed, including negative results.
- [x] large generated datasets explicitly classified rather than falsely described as line-by-line reads.
- [x] presentation/UI/WezTerm material separated from authority/runtime behavior.
- [x] durable findings recorded in `LEGACY_KNOWLEDGE_AUDIT.md`.
- [x] actionable disposition recorded in `LEGACY_PROMOTION_LEDGER.md`.

## 2. Source preservation

First extraction:

- [x] SQLite schema / claims / review authorship preserved.
- [x] LangGraph source preserved.
- [x] pre-dispatch policy / scope validation preserved.
- [x] RnS/recovery/resilience source preserved.
- [x] local Ollama/Aider wrappers preserved.
- [x] migration/install knowledge preserved.
- [x] focused core tests preserved.

Second extraction:

- [x] run manifest source + tests preserved.
- [x] criterion-level submission evidence source + tests preserved.
- [x] continuity-aware review routing source + tests preserved.
- [x] session replay source + design + tests preserved.
- [x] intake/decomposition source + tests preserved as rewrite reference.
- [x] context packet validator/template + tests preserved.
- [x] decision/event/research/review validators + tests preserved.
- [x] conflict behavior preserved as rewrite reference.
- [x] Git global-operation lock behavior/test/formal invariant preserved as rewrite reference.
- [x] optional cost-governance source/test preserved as reference.
- [x] selected measured audit/experiment evidence preserved.

Second-pass source lives under `migration/legacy-knowledge-source/` and is
migration/reference material only.

## 3. Active Lean rule coverage

- [x] consequential human/operator authority.
- [x] one accountable owner.
- [x] bounded helpers.
- [x] AGI `READY` gate.
- [x] output paths/write boundaries.
- [x] decision authority separated from technical capability.
- [x] verification/evidence/review/escalation requirements.
- [x] repair severity and repeat-failure learning.
- [x] SQLite/LangGraph/hcom responsibility separation.
- [x] durable handoff requirement for long-running work.
- [x] explicit context packet / trigger-gated context rule merged.
- [x] typed operational failure rule merged.
- [x] semantic reviewer-independence / continuity lineage rule merged.
- [x] conflict-freeze rule merged.
- [x] diagnostic-vs-repair authority rule merged.
- [x] security-specific review trigger merged.
- [x] run-manifest relationship to AGI documented.
- [x] implementer evidence claim vs reviewer verification distinction documented for high-risk work.

The newly merged rules are centered in `playbook/EXECUTION_INTEGRITY.md` and
linked from `TASK_LIFECYCLE.md` and the playbook index.

## 4. Runtime promotion

Legacy deletion does not require every optional feature to be active. It does
require a deliberate home for all P0 behavior.

- [x] migration snapshots are intentionally retained until active runtime promotion completes.
- [ ] active runtime does not import from `legacy/`.
- [ ] active runtime does not import executable code from a migration snapshot.
- [ ] task state has one canonical mutable store.
- [ ] atomic claim race has exactly one winner.
- [ ] owner vs active claimant semantics are preserved.
- [ ] submission author is durable enough to enforce no-self-review.
- [ ] required AGI gate protects READY.
- [ ] review transition requires required evidence/review.
- [ ] recovery cannot silently steal a live claim.
- [ ] hcom remains transport, not task authority.
- [ ] LangGraph checkpoints remain separate from task truth.
- [ ] RnS does not require WezTerm to recover a session.

These unchecked items are runtime-promotion gates, not evidence that the legacy
audit is incomplete.

## 5. Test preservation

At minimum, active or migration tests must continue to cover:

- [x] duplicate task-ID prevention / allocation invariant.
- [x] atomic claim exclusivity.
- [x] lease expiry and orphan recovery.
- [x] no-self-review.
- [x] continuity-aware reviewer independence.
- [x] READY/promotion refusal for incomplete work; AGI-specific validator implementation remains future work.
- [x] output/write-scope enforcement.
- [x] pre-dispatch authority/policy gates.
- [x] release/verification gate.
- [x] RnS limit/stale-session recovery.
- [x] run-manifest staleness/scope checks.
- [x] context packet structural validation.
- [x] criterion evidence + independent verdict separation.
- [x] derived read-model behavior is covered by session-replay tests/design; Lean rewrite must preserve read-only authority.
- [x] local helper/Aider scope boundaries.

Preserved tests are migration regression evidence. They are not considered
passing Lean runtime tests until their behavior is ported into active runtime.

## 6. Reference cleanup

Run a repository search before deletion.

- [ ] no active README/playbook/template points agents to `legacy/` as required reading.
- [ ] no active code imports `legacy` modules.
- [ ] no active test requires legacy runtime state.
- [ ] setup/install docs do not require legacy paths.
- [x] migration docs clearly say snapshots are source/reference only.
- [ ] references intentionally kept for provenance are labeled historical and are not execution dependencies.

Suggested checks:

```bash
rg -n 'legacy/' --glob '!legacy/**'
rg -n 'migration/legacy-runtime-source|migration/legacy-knowledge-source' runtime tests playbook docs templates
rg -n 'MAP_System|MultiAgentProject' --glob '!legacy/**' --glob '!migration/legacy-runtime-source/**' --glob '!migration/legacy-knowledge-source/**'
```

Review each result; not every textual provenance reference is a blocker.

## 7. Data handling

- [x] old `map.db`, WAL, SHM and runtime state were not copied as Lean canonical state.
- [x] old task graph was not promoted as another mutable source of truth.
- [x] old event log is not required for Lean startup.
- [x] migration extraction did not intentionally duplicate hcom transcript/message history.
- [x] hcom message history remains outside MAPS task authority.
- [ ] selected evidence documents receive a final secret/privacy check before legacy deletion.

## 8. Optional systems explicitly decided

Deletion does **not** mean these must be implemented. Their disposition is now
recorded in `LEGACY_PROMOTION_LEDGER.md`:

- [x] full Library/Librarian: `DEFER unless new measurements justify it`.
- [x] task fingerprint/memory retrieval: `EXPERIMENTAL; negative/mixed results preserved`.
- [x] continuous Discovery Agent: `REJECT; use bounded event-triggered discovery`.
- [x] cost governance: `OPTIONAL; build when autonomous paid dispatch makes it useful`.
- [x] formal verification beyond state-machine/property tests: `OPTIONAL`.
- [x] CommandCenterUI/Mission Control implementation: `NOT PART OF LEAN CORE`.
- [x] WezTerm cockpit: `NOT REQUIRED`.

## 9. Final removal decision

Before deleting `legacy/`, record:

```text
Audit complete: YES
Second preservation snapshot complete: YES
P0 behavior has an active or preserved destination: YES
Active legacy execution dependencies: <resolve reference-cleanup/runtime gates above>
Known deferred optional features: see LEGACY_PROMOTION_LEDGER.md
Removal approved by operator: YES / NO
Removal commit/PR: <link or SHA>
```

Do not delete `legacy/` while any required answer above is unknown.
