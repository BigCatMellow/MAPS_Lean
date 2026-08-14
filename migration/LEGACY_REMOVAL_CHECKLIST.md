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

The merged rules are centered in `playbook/EXECUTION_INTEGRITY.md` and linked
from `TASK_LIFECYCLE.md` and the playbook index.

## 4. Runtime promotion

Legacy deletion does not require every optional feature to be active. It does
require a deliberate home for all P0 behavior.

- [x] migration snapshots are intentionally retained until active runtime promotion completes.
- [x] active state runtime imports nothing from `legacy/`.
- [x] active state runtime imports no executable code from a migration snapshot.
- [x] promoted task state has one canonical mutable SQLite store.
- [x] atomic claim race has exactly one winner in active regression tests.
- [x] owner vs active claimant semantics are preserved.
- [x] submission author is durable enough to enforce no-self-review.
- [x] required structural AGI gate protects READY.
- [x] review transition requires durable submission evidence and the required review owner.
- [ ] recovery cannot silently steal a live claim across the full RnS path.
- [ ] hcom active adapter preserves transport-not-authority boundary.
- [ ] LangGraph active router uses checkpoints separate from task truth.
- [ ] RnS active recovery works without mandatory WezTerm.

TASK-009 satisfies the state-layer promotion gates. The remaining unchecked
items belong to later routing/communication/recovery slices.

## 5. Test preservation

At minimum, active or migration tests must continue to cover:

- [x] duplicate task-ID prevention / allocation invariant — active state test.
- [x] atomic claim exclusivity — active state test.
- [x] lease expiry and claim recovery — active state test; full RnS recovery remains pending.
- [x] no-self-review — active state test.
- [x] continuity-aware reviewer independence — preserved migration test; active continuity-lineage port remains later work.
- [x] AGI READY/promotion refusal for incomplete work — active state test.
- [x] active output-path reservation conflict — active state test; filesystem run-scope enforcement remains later work.
- [x] pre-dispatch authority/policy gates — preserved migration tests; active policy port pending.
- [x] release/verification gate — preserved migration test; active state currently reaches DONE through review rather than a separate release layer.
- [x] RnS limit/stale-session recovery — preserved migration tests; active port pending.
- [x] run-manifest staleness/scope checks — preserved migration tests; active port pending.
- [x] context packet structural validation — preserved migration test/template.
- [x] criterion evidence + independent verdict separation — preserved source plus active durable submission/review separation.
- [x] derived read-model behavior is covered by session-replay tests/design; Lean rewrite must preserve read-only authority.
- [x] local helper/Aider scope boundaries — preserved migration tests; active helper port pending.

Preserved tests remain migration regression evidence until their subsystem is
promoted. The active state subset currently passes 15 focused tests.

## 6. Reference cleanup

Run a repository search before deletion.

- [x] active README/playbook/template does not require reading `legacy/` for ordinary state-runtime execution.
- [x] active `runtime/` code imports no `legacy` modules.
- [x] active state tests require no legacy runtime state.
- [ ] setup/install docs are fully independent of legacy/migration references for every subsystem.
- [x] migration docs clearly say snapshots are source/reference only.
- [ ] references intentionally kept for provenance receive the final historical/non-execution labeling sweep.

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
Active legacy execution dependencies: <resolve remaining runtime/reference gates above>
Known deferred optional features: see LEGACY_PROMOTION_LEDGER.md
Removal approved by operator: YES / NO
Removal commit/PR: <link or SHA>
```

Do not delete `legacy/` while any required answer above is unknown.
