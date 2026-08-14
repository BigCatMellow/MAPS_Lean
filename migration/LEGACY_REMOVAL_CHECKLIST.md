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

Second extraction — must be complete before deletion:

- [ ] run manifest source + tests preserved.
- [ ] criterion-level submission evidence source + tests preserved.
- [ ] continuity-aware review routing source + tests preserved.
- [ ] session replay source + design + tests preserved.
- [ ] intake/decomposition source + tests preserved as rewrite reference.
- [ ] context packet validator/template + tests preserved.
- [ ] decision/event/research/review validators + tests preserved.
- [ ] conflict behavior preserved as rewrite reference.
- [ ] Git global-operation lock behavior/test/formal invariant preserved as rewrite reference.
- [ ] optional cost-governance source/test preserved as reference.
- [ ] selected measured audit/experiment evidence preserved.

## 3. Active Lean rule coverage

Before deletion, verify active Lean has or intentionally rejects these rules:

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
- [ ] explicit context packet / trigger-gated context rule merged.
- [ ] typed operational failure rule merged.
- [ ] semantic reviewer-independence / continuity lineage rule merged.
- [ ] conflict-freeze rule merged.
- [ ] diagnostic-vs-repair authority rule confirmed/merged.
- [ ] security-specific review trigger confirmed/merged.
- [ ] run-manifest relationship to AGI documented.
- [ ] implementer evidence claim vs reviewer verification distinction documented for high-risk work.

## 4. Runtime promotion

Legacy deletion does not require every optional feature to be active. It does
require a deliberate home for all P0 behavior.

- [ ] active `runtime/` exists or the migration snapshot is explicitly retained until promotion completes.
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

## 5. Test preservation

At minimum, active or migration tests must continue to cover:

- [ ] duplicate task-ID prevention / allocation invariant.
- [ ] atomic claim exclusivity.
- [ ] lease expiry and orphan recovery.
- [ ] no-self-review.
- [ ] continuity-aware reviewer independence.
- [ ] READY/AGI promotion refusal for incomplete work.
- [ ] output/write-scope enforcement.
- [ ] pre-dispatch authority/policy gates.
- [ ] release/verification gate.
- [ ] RnS limit/stale-session recovery.
- [ ] run-manifest staleness/scope checks.
- [ ] context packet structural validation.
- [ ] criterion evidence + independent verdict separation.
- [ ] derived read model cannot mutate canonical state.
- [ ] local helper/Aider scope boundaries.

## 6. Reference cleanup

Run a repository search before deletion.

- [ ] no active README/playbook/template points agents to `legacy/` as required reading.
- [ ] no active code imports `legacy` modules.
- [ ] no active test requires legacy runtime state.
- [ ] setup/install docs do not require legacy paths.
- [ ] migration docs clearly say snapshots are source/reference only.
- [ ] references intentionally kept for provenance are labeled historical and are not execution dependencies.

Suggested checks:

```bash
rg -n 'legacy/' --glob '!legacy/**'
rg -n 'migration/legacy-runtime-source' runtime tests playbook docs templates
rg -n 'MAP_System|MultiAgentProject' --glob '!legacy/**' --glob '!migration/legacy-runtime-source/**'
```

Review each result; not every textual provenance reference is a blocker.

## 7. Data handling

- [ ] old `map.db`, WAL, SHM and runtime state are not copied as Lean canonical state.
- [ ] old task graph is not promoted as another mutable source of truth.
- [ ] old event log is not required for Lean startup.
- [ ] secrets/private transcript data are not newly duplicated into migration artifacts.
- [ ] hcom message history remains in its own transport store/history boundary.
- [ ] selected evidence documents contain no credentials that would make preservation unsafe.

## 8. Optional systems explicitly decided

Deletion does **not** mean these must be implemented. Their status must simply
be recorded so nobody later assumes they were accidentally lost.

- [ ] full Library/Librarian: `DEFER unless new measurements justify it`.
- [ ] task fingerprint/memory retrieval: `EXPERIMENTAL; negative/mixed results preserved`.
- [ ] continuous Discovery Agent: `REJECT; use bounded event-triggered discovery`.
- [ ] cost governance: `OPTIONAL; build when autonomous paid dispatch makes it useful`.
- [ ] formal verification beyond state-machine/property tests: `OPTIONAL`.
- [ ] CommandCenterUI/Mission Control implementation: `NOT PART OF LEAN CORE`.
- [ ] WezTerm cockpit: `NOT REQUIRED`.

## 9. Final removal decision

Before deleting `legacy/`, record:

```text
Audit complete: YES / NO
Second preservation snapshot complete: YES / NO
P0 behavior has an active or preserved destination: YES / NO
Active legacy execution dependencies: NONE / list
Known deferred optional features: list
Removal approved by operator: YES / NO
Removal commit/PR: <link or SHA>
```

Do not delete `legacy/` while any required answer above is unknown.
