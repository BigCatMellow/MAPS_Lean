# MAPS Lean capability checklist

Durable "what's next" source of truth, replacing the need to re-derive roadmap
status from scratch each session. Every status below was checked against
actual code, tests, and merged-PR history in this repo as of **2026-08-18**
(local clone at `~/Projects/MAPS_Lean`, `main` at `03e771d`) — not guessed from
roadmap prose. Re-verify before trusting an entry once enough time has passed
that it may have gone stale; a status here is a snapshot, not authority.

Status legend:

- `DONE` — implemented, tested, merged to `main`.
- `IN PROGRESS` — real code/tests exist but the phase's own stated exit gate
  is not fully met yet (explained in the evidence column), or it is actively
  being implemented on an open branch/PR right now.
- `NOT STARTED` — no corresponding code found; roadmap prose only.

## 1. Harness Mechanics (`agent-harness-capabilities/01-harness-mechanics.md`)

| Phase | Status | Evidence |
|---|---|---|
| H1 — Result envelope and state vocabulary | DONE | `runtime/harness/types.py` (`OperationResult`, `NormalizedSessionState`) + `tests/test_harness_types.py`; merged via PR #20 (`git log`: "Merge PR #20: Add Wave 1 harness contract foundation"). |
| H2 — Harness interface + one adapter | DONE | `runtime/harness/protocol.py` (`HarnessAdapter`), `runtime/harness/adapters/hcom.py`; merged via PR #21 ("Add hcom harness normalization and Hook registry") + `tests/test_harness_hcom_adapter.py`. |
| H3 — Hook registry | DONE | `runtime/harness/hooks.py` (`HookRegistry`, `HookEnforcement.CANONICAL_RUN`), `runtime/policy/harness_guard.py` (`CanonicalRunGuard`); merged via PR #22 ("Add provider-neutral HarnessService") and PR #23 ("Add canonical run guard for harness operations") + `tests/test_harness_hooks.py`, `tests/test_harness_canonical_guard.py`. |
| H4 — Immediate validation hooks | IN PROGRESS | `runtime/environment/validation.py` + `tests/test_environment_validation.py`; merged via PR #106. Gives `EnvironmentSpec.validation` tiers a real executor and a Hook-callback factory; no production call site invokes it yet, so the exit gate ("representative failures caught immediately after mutation") is only partly met. |
| H5 — Remaining adapters + contract suite | IN PROGRESS | `runtime/harness/contract.py` (`AdapterContractMixin`) + `tests/test_harness_adapter_contract.py`; merged via PR #107. Proves the one existing adapter (hcom) satisfies a shared structural/behavioral contract — the "contract suite" half of the exit gate. The "remaining adapters" half is still not done: `runtime/helpers/ollama.py`/`aider.py` and `runtime/recovery/supervisor.py` remain unwrapped, deliberately out of scope (their one-shot invocation shape doesn't naturally fit the session-lifecycle protocol; see `work/tasks/harness-adapter-contract-suite-wave7.md` stop conditions). |
| H6 — Lineage/trace integration | DONE | `runtime/state/run_lineage_trace.py` (`RunSessionTraceMixin.trace_task`), `runtime/state/run_lineage.py`, `tests/test_run_session_lineage.py`; run/session/helper/recovery lineage reconstructable via `trace_task`. |

## 2. Procedural Knowledge & Skills (`agent-harness-capabilities/02-procedural-knowledge-and-skills.md`)

| Phase | Status | Evidence |
|---|---|---|
| S1 — Information classification | DONE | `playbook/INFORMATION_CLASSES.md` names all 7 classes (authority/task context/fact/Skill/flow/tool/example) with the roadmap's own examples, ties them to what `runtime/context_builder.py` and `runtime/skills/` already do, and is indexed in `playbook/INDEX.md`; `runtime/README.md`'s `context_builder.py` bullet now points to it as the applied vocabulary for the plan's `authority`/`required`/`guidance` fields. `work/tasks/information-classification-doc-wave9.md`. |
| S2 — Skills format support | DONE | `runtime/skills/format.py` (`discover_skills`, `load_skill`, hash-verified snapshot activation); merged via PR #25 ("Add Agent Skills format foundation") + `tests/test_skills_format.py`. |
| S3 — Catalog + provenance | DONE | `runtime/skills/catalog.py` (`SkillCatalog`, `SkillProvenance`, `SkillTrustState.UNASSESSED`); merged via PR #26 ("Add Skills catalog provenance read model") + `tests/test_skills_catalog.py`. |
| S4 — Routing evaluation | DONE | `runtime/skills/evaluation.py` (`SkillSelectionCorpus`, `evaluate_skill_selection`, precision/recall/F1/hard-negative/ambiguity metrics); merged via PR #27 ("Add frozen Skill selection evaluation corpus") + `tests/test_skills_selection_evaluation.py`. This is an eval harness only — see S6 for why it is not yet wired to a production selector. |
| S5 — Quality/security gate | DONE | `runtime/skills/gate.py` (`_DESTRUCTIVE_RE`, `_CREDENTIAL_HARVEST_RE` content lint), `runtime/skills/gate_hardened.py`; merged via PR #31 ("Add static Skill quality and security gate") + `tests/test_skills_quality_gate.py`, `tests/test_skills_quality_gate_metadata.py`. Note: this is static content linting, not the full SEC4 quarantine *lifecycle* (see SEC4 below) — S5's own scope (lint + quarantine trigger classification) is met. |
| S6 — Context Builder integration | IN PROGRESS | `runtime/context_builder.py::_select_skills` (merged via PR #109) surfaces keyword-token-matched Skill catalog entries as attributed evidence (`skill_id`/matched signals) in `build_context_plan`'s output — but this only reads descriptor/provenance metadata; `load_skill`/`load_catalog_skill` (procedure body activation) is never called, so no Skill content is actually loaded into context yet, and unrelated Skills are excluded by construction (only matched-signal entries are surfaced). Progressive *loading* of the matched Skill's body remains future work. |
| S7 — Capability Packs experiment | NOT STARTED | No `CapabilityPack`-shaped code anywhere; explicitly gated on S6 + Harness/EnvironmentSpec stability per the roadmap. S6 is now in progress but not done, so this remains blocked. |

## 3. Environment & Reproducibility (`agent-harness-capabilities/03-environment-and-reproducibility.md`)

| Phase | Status | Evidence |
|---|---|---|
| E1 — EnvironmentSpec schema | DONE | `runtime/environment/spec.py` (`EnvironmentSpec`, `parse_environment_spec`, `load_environment_spec`), real fixture `runtime/environment/specs/maps-runtime-ci.json`; merged via PR #28 ("Add EnvironmentSpec v1 foundation") + `tests/test_environment_spec.py`. |
| E2 — Fingerprint + compatibility | DONE | `runtime/environment/fingerprint.py` (`inspect_local_environment`, `evaluate_environment_compatibility`, `CompatibilityState`); merged via PR #29 ("Add local environment fingerprint compatibility") + `tests/test_environment_fingerprint.py`, `tests/test_environment_fingerprint_safety.py`. |
| E3 — Run binding | DONE | `runtime/state/environment.py` (`EnvironmentEvidenceMixin`, binds `environment_spec_hash`/fingerprint to run evidence) + `tests/test_run_environment_evidence.py`; `ExecutionBinding.environment_spec_hash` field in `runtime/harness/types.py` carries the reference end-to-end. |
| E4 — Validation tiers | IN PROGRESS | Same evidence as H4 (`runtime/environment/validation.py`); merged via PR #106. `ValidationTiers` (quick/normal/full) previously existed as pure declared data with zero callers; this task adds the first executor + Hook wiring, but no real caller (`HarnessService` or an adapter) invokes it yet. |
| E5 — Recovery compatibility | IN PROGRESS | `runtime/recovery/supervisor.py::_advisory_environment_evidence` surfaces environment-compatibility evidence for an incident's bound run (Stage 2 Option A, `work/notes/2026-08-17-recovery-equivalence-authority-design.md`), but its own docstring states it is "purely advisory context, never consulted by any branch in `tick()` to make or change a recovery decision." E5's exit gate ("incompatible replacement cannot silently resume") is therefore **not** met — evidence is surfaced but not enforced. |
| E6 — Worktree isolation | NOT STARTED | No git-worktree-per-run code anywhere in `runtime/`; explicitly `TRIGGERED` in the roadmap and the trigger condition (observed shared-worktree collisions) has not been recorded anywhere. |
| E7 — Snapshot/rehydration experiment | NOT STARTED | No environment snapshot/rehydration code; all `snapshot` hits in `runtime/` are unrelated (Skill byte-snapshot hashing in `runtime/skills/format.py`/`gate.py`, evidence-dict variable names). Explicitly gated on E6 first. |

## 4. Agentic Security (`agent-harness-capabilities/04-agentic-security.md`)

| Phase | Status | Evidence |
|---|---|---|
| SEC1 — Threat model + trust taxonomy | DONE | `work/roadmaps/agent-harness-capabilities/04-agentic-security.md` itself + `runtime/skills/catalog.py::SkillTrustState`/`SkillSourceKind` give a consistent vocabulary; merged via PR ("Add agentic security roadmap", commit `fc39d95`). |
| SEC2 — Current-system adversarial baseline | DONE | `work/tasks/agentic-security-baseline-wave1.md`, `tests/test_agentic_security_baseline.py`, `tests/test_agentic_security_hook_context.py`; merged via PR #24 ("Add initial agentic security adversarial baseline"). |
| SEC3 — Security hooks | IN PROGRESS | Only one enforcement type exists: `HookEnforcement.CANONICAL_RUN` (`runtime/harness/hooks.py`, `runtime/policy/harness_guard.py::CanonicalRunGuard`), covering run/session identity binding only. `HookEvent.BEFORE_EXTERNAL_ACTION` and `BEFORE_DESTRUCTIVE_ACTION` are declared enum values with **zero** registered guards anywhere — the roadmap's full "scope/policy/destructive/external/credential/recovery guards" breadth is not built. |
| SEC4 — Skill/tool supply-chain controls | IN PROGRESS | `runtime/skills/gate.py` statically lints Skill content for `DESTRUCTIVE_OPERATION`/`CREDENTIAL_ENVIRONMENT_ACCESS` patterns (PR #31), `SkillCatalogEntry.provenance`/`SkillTrustState` (PR #26) record source/trust metadata, and `runtime/skills/lifecycle.py` (`SkillLifecycleState`, `transition()`, merged via PR #113) now provides the quarantine-lifecycle *transition validation* (discovered→validated→quarantined→approved→active→superseded→retired, with mandatory quarantine review and an explicit-actor requirement for approval transitions) — but this is a pure, unpersisted primitive with no durable storage of a Skill's current state and no real operator-authority wiring, and there is still no capability-declaration manifest for third-party Skills/tools. |
| SEC5 — Memory/learning security | DONE | `runtime/state/operational_learning_storage.py` (`record_operational_lesson_candidate`, `promote_operational_lesson`, `retire_operational_lesson`, decision history); merged via PR #79/#93 ("Authority-1: operator-only operational lesson promotion/retirement") + `tests/test_operational_learning_storage.py`. Candidate lessons cannot become active guidance without operator promotion. |
| SEC6 — Credential broker experiment | NOT STARTED | No credential-broker code anywhere; explicitly `TRIGGERED`, and no task/note records the triggering condition (frequent credential-bearing remote tasks) as having occurred. |
| SEC7 — Ongoing incident corpus | IN PROGRESS | The data format and evaluation exist (`runtime/evaluation/regression_case.py`, `tests/test_frozen_regression_case.py`, `test_frozen_regression_case_taxonomy.py`, merged via PR #34/"Add frozen regression case v1"), but no doc anywhere (`docs/`, `playbook/`) defines the *operational workflow* that turns a real incident into a frozen case as a repeatable, expected step — the mechanism exists, the process convention doesn't. |

## 5. Learning & Evaluation (`agent-harness-capabilities/05-learning-and-evaluation.md`)

| Phase | Status | Evidence |
|---|---|---|
| L1 — Run Record v1 | DONE | `runtime/run_record.py`; merged via PR #33 ("Add portable Run Record v1") + `tests/test_run_record.py`. |
| L2 — Incident taxonomy + case format | DONE | `runtime/evaluation/regression_case.py`; merged via PR #34 ("Add frozen regression case v1") + `tests/test_frozen_regression_case.py`, `test_frozen_regression_case_taxonomy.py`. |
| L3 — Three-layer eval harness | DONE | `runtime/evaluation/evaluator.py` (mechanical/property + comparison layer, merged via PR #35 "Add comparative frozen regression evaluator v1") + `runtime/benchmark_results.py`/`tests/test_maps_end_to_end_benchmark_fixture.py` (agent/task layer) + `runtime/state/outcomes.py` (production/outcome layer, observational). L3's own stated exit gate only requires layers 1+2 tested with layer 3 "observational until data accumulates" — met. |
| L4 — Research experiments A–E | IN PROGRESS | EXP-A is now run and labeled: `runtime/skills/eval_corpora/exp_a_skill_routing_v1.json` (frozen 12-case corpus) + `tests/test_exp_a_skill_routing.py` runs the real `runtime/context_builder.py::_select_skills` selector (S6, PR #109) through the real `runtime/skills/evaluation.py::evaluate_skill_selection` harness (S4, PR #27); results in `work/notes/2026-08-19-exp-a-skill-routing-benchmark.md` (precision 0.889, recall 0.889, one documented false activation, one documented missed activation). EXP-B..EXP-E remain unrun: no code is labeled `EXP-B`..`EXP-E` (only referenced in planning docs: `work/research/agent-harness-patterns-scan-2026-08.md`, the roadmap itself). `runtime/context_retrieval_semantic.py` + `tests/test_context_retrieval_semantic.py` remain adjacent-only infrastructure (~EXP shape) for a retrieval-comparison experiment, not yet run/labeled as such. |
| L5 — Operational-learning lifecycle | DONE | Same evidence as SEC5: `runtime/operational_learning.py`, `runtime/outcome_lesson_candidate.py`, `runtime/state/operational_learning_storage.py`, PR #79/#93 + `tests/test_operational_learning.py`, `test_operational_learning_storage.py`. Promotion requires explicit operator review/provenance; expiry/supersession implemented. |
| L6 — Harness configuration identity | IN PROGRESS | `runtime/harness/config_ref.py` (`HarnessConfigRef`, `harness_config_ref()`, merged via PR #112) deterministically hashes a `HarnessService`'s registered adapters + declared Hook metadata (excluding unstable callback identity), and `ExecutionBinding.harness_config_hash` / `run_record.py`'s coverage projection can represent it — but no production call site actually sets/persists the hash onto a real run manifest yet, so "each evaluated run can identify which configuration produced it" is not yet true in practice, only structurally possible. |
| L7 — Comparative harness evaluation | NOT STARTED | Still depends on L6's hash actually being persisted on real runs (not yet wired). `runtime/evaluation/evaluator.py`'s `compare_regression_cases` compares *test-case* outcomes, not harness configurations. |
| L8 — Proposal-only refinement workflow | NOT STARTED | No proposal/promotion workflow for harness-level changes exists; depends on L6/L7. |
| L9 — Fork/time-travel experiment | NOT STARTED | No replay/fork-from-checkpoint code anywhere; explicitly gated on Run Records/environment fixtures being mature (L1/E1-E2 are done, but the roadmap treats this as last-priority and it has not been attempted). |

## 6. Master roadmap capability inventory (`00-MASTER-MAPS-CAPABILITY-ROADMAP.md` §6)

Every item below maps to one or more phases above; evidence is not
re-researched, only cross-referenced, except where noted as a standalone gap.

| # | Item | Status | Maps to / evidence |
|---|---|---|---|
| 6.1 | Task truth, ownership and authority | DONE | `runtime/state/` (SQLite lifecycle/claims/leases/policy/review), foundational and pre-existing. |
| 6.2 | Provider-neutral Harness API | DONE | = H1–H3. |
| 6.3 | Normalized ACI results | DONE | = H1 (`OperationResult`). |
| 6.4 | Deterministic Hooks/Interceptors | IN PROGRESS | = H3 (registry done) + SEC3 (only `CANONICAL_RUN` enforcement exists; write/destructive/external guards not built). |
| 6.5 | Immediate deterministic validation | IN PROGRESS | = H4/E4. |
| 6.6 | Explicit run/session/helper/recovery lineage | DONE | = H6, plus `runtime/state/helper_recovery_lineage.py` + `tests/test_helper_recovery_lineage.py`. |
| 6.7 | Explainable waits | DONE | `runtime/wait_projection.py` + `tests/test_wait_projection.py`; task doc `work/tasks/explainable-waits-wave3.md`. |
| 6.8 | Reusable Agent Skills | DONE | = S2. |
| 6.9 | Skill routing and progressive disclosure | IN PROGRESS | = S4 (eval exists) + S6 (attributed-evidence selection now wired into Context Builder, but progressive *loading* of Skill bodies is still not real). |
| 6.10 | Skill provenance, trust and quarantine | IN PROGRESS | = S3 (provenance, done) + SEC4 (transition-validation primitive now exists, but unpersisted — no durable lifecycle state or real authority wiring yet). |
| 6.11 | Context budgets / progressive context | IN PROGRESS | `runtime/context_builder.py` now tags each `authority`/`required`/`dependencies`/`guidance`/`withheld_guidance`/`skills` item with a `budget_class` (MUST_LOAD/SHOULD_LOAD/ON_DEMAND), plus `coverage.budget_classification_present`; classification only, no new retrieval/search mechanism. No `MAY_LOAD` tier yet (no data source for it), and `budget_class` does not yet drive any actual load/fetch behavior downstream — see `work/tasks/context-budget-classification-wave12.md`. |
| 6.12 | Capability Packs | NOT STARTED | = S7. |
| 6.13 | EnvironmentSpec | DONE | = E1. |
| 6.14 | EnvironmentFingerprint and compatibility | DONE | = E2. |
| 6.15 | Harness/compute separation | DONE | Architectural invariant; `runtime/harness/service.py` docstring + `runtime/README.md` "Responsibility boundaries" table confirm SQLite/task-truth stays outside adapters. |
| 6.16 | Git worktree isolation | NOT STARTED | = E6. |
| 6.17 | Sandboxes/snapshots/rehydration | NOT STARTED | = E7. |
| 6.18 | Revision-bound review/evidence | DONE | `runtime/integrity/` (staleness/Git-scope/run-budget checks), `tests/test_execution_integrity.py`, `runtime/README.md` "AGI and run integrity" section. |
| 6.19 | Task-scoped helper continuity | NOT STARTED | No TTL/reuse logic in `runtime/helpers/` — each `OllamaHelper`/`AiderHelper` invocation is one-shot (`runtime/helpers/README.md` describes bounded one-shot lanes only, no continuity/reuse concept). |
| 6.20 | Advisory NO_PROGRESS detection | NOT STARTED | No repeated-tool-call / no-progress heuristic found in `runtime/recovery/` or elsewhere. |
| 6.21 | Deterministic `maps flow` lifecycle operations | NOT STARTED | No `maps flow` CLI verb or equivalent found in `runtime/cli.py`. |
| 6.22 | Memory trust classes | IN PROGRESS | `runtime/skills/catalog.py::SkillTrustState` only has `UNASSESSED` (S3); `runtime/operational_learning.py` has `GUIDANCE_ONLY`/`CANDIDATE` labels (SEC5/L5) — a partial trust vocabulary exists but not the full class list the roadmap names (e.g. no `QUARANTINED`, no unified cross-subsystem enum). |
| 6.23 | Agentic threat model and adversarial regression corpus | DONE | = SEC1/SEC2. |
| 6.24 | Least-privilege capability intersection | IN PROGRESS | `runtime/policy/` (capability envelopes) + `CanonicalRunGuard` intersect worker/task/policy for the one enforced path (canonical run identity); not proven across scope/environment-availability dimensions the roadmap lists. |
| 6.25 | Credential broker | NOT STARTED | = SEC6. |
| 6.26 | Portable Run Records / trajectories | DONE | = L1. |
| 6.27 | Outcome-linked incident taxonomy | DONE (foundation) | `runtime/state/outcomes.py` append-only outcomes exist (`tests/test_outcomes.py`); the roadmap's expanded incident-class enum (`TOOL_FAILURE`, `CONTEXT_POISONING`, etc.) is not itself encoded as a distinct type anywhere — foundation met, expansion not started. |
| 6.28 | Frozen regression corpus | DONE | = L2. |
| 6.29 | Three-layer evaluation | DONE | = L3. |
| 6.30 | Operational learning lifecycle | DONE | = L5/SEC5. |
| 6.31 | Controlled harness refinement | NOT STARTED | = L6–L8. |
| 6.32 | Time-travel / fork debugging | NOT STARTED | = L9. |
| 6.33 | Semantic retrieval / query expansion | IN PROGRESS (evaluation-only, by design) | `runtime/context_retrieval_semantic.py` + `tests/test_context_retrieval_semantic.py` exist as one evaluation-only candidate; `runtime/README.md` explicitly states it is "not a production path" — this matches the roadmap's own current decision (`EVIDENCE-GATED`, Context Builder stays explicit-first), so this is expected, not a gap. |
| 6.34 | Mission / multi-task goal object | NOT STARTED | No `Mission`-shaped object anywhere; matches the roadmap's own current decision not to build one yet. |

## How to keep this current

When a phase's status changes (a PR merges, a new gap is found), edit this
file in the same PR that changes the underlying code, or as a fast follow
docs-only PR immediately after. Do not let this drift the way
`work/tasks/*-wave*.md` status fields have drifted in prior sessions — those
files record individual task history and go stale; this file is meant to be
the one place that stays a true cross-roadmap snapshot.
