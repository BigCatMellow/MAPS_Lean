# THINK, PLAN, DO, JUDGE, LEARN — should MAPS_L add GROW?

**Research as of 2026-11-04. Status: RESEARCH / DESIGN QUESTION, NOT APPROVED ARCHITECTURE.**
**No runtime changes, agent installation, paid evaluation, policy change or automatic promotion authorized by this file.**

Parent: [Research index](../README.md); [MAPS_L master roadmap](../../roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md); [existing learning/evaluation research](2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md).
Related upstream work: [Pilot_Projects THINK](https://github.com/BigCatMellow/Pilot_Projects/tree/main/complete-ai-work-system/roadmaps/03-THINK-CREATIVITY-AND-IDEA-ECOLOGY.md), [PLAN](https://github.com/BigCatMellow/Pilot_Projects/tree/main/complete-ai-work-system/roadmaps/05-PLAN-ORCHESTRATION-AND-TASK-COMPILATION.md), [JUDGE / governed learning](https://github.com/BigCatMellow/Pilot_Projects/blob/main/complete-ai-work-system/roadmaps/06-JUDGE-EVIDENCE-OUTCOMES-AND-LEARNING.md). The external project already uses **THINK → PLAN → CONTEXT → DO → JUDGE → LEARN**. A search of MAPS_L and Pilot_Projects GitHub code did not find an authoritative named GROW definition. Treat "GROW" as a **hypothesis/working label**, not an existing component or a requested new product.

## Question, decision and baseline

Does MAPS_L lack a *deliberate comparative improvement mechanism*, as distinct from thinking about tasks and learning lessons? If yes, can the missing connection be closed in **existing** evidence/evaluation/operational-learning owners, without a second persistent agent, controller, scheduler, approval hierarchy, or task database?

**Provisional answer:** A GROW *function* may be useful, but a new *subsystem* is not yet justified. Existing MAPS_L already captures post-completion outcomes, frozen regression cases, `CANDIDATE → ACTIVE → RETIRED` lessons, controlled promotion, operational friction, and comparative evaluation scaffolding. Pilot JUDGE's §9–12 explicitly plans optimizer candidates such as GEPA and PromptBreeder. What remains uncertain is actual end-to-end connection: observation → localized causal hypothesis → candidate mutation → paired test → independent decision → retained improvement. Research alone must not mark this gap verified.

A clear conceptual separation:
- **THINK:** find ideas, explanations, and alternative strategies.
- **PLAN:** select requirements, dependencies and feasible next work.
- **DO:** execute under current task/policy authority.
- **JUDGE:** verify the artifact, constraints and real result.
- **LEARN:** retain grounded, scoped observations with provenance.
- **GROW (proposed):** *deliberately vary and compare the system itself* and ask which evidence-supported change should be proposed for promotion. This is a feedback activity across the existing lanes, not an actor with independent authority.

If ordinary governed learning already produces and tests improvements, GROW is only a convenient label for that same work and should **not** be separately implemented.

## Mechanism-by-mechanism upstream inspection

Source classes: `CODE-INSPECTED` = inspected named upstream implementation files; `README-REPORTED` = public project explanation, not replicated; `EXTERNAL-RESEARCH` = paper/benchmark findings not validated on MAPS_L. Inspected 2026-11-04; upstream may change.

### 1. GEPA — reflective optimization with explicit metric calls

- Primary repository: https://github.com/gepa-ai/gepa
- Code/documentation: https://github.com/gepa-ai/gepa/tree/main/src ; https://github.com/gepa-ai/gepa/tree/main/tests ; https://github.com/gepa-ai/gepa/blob/main/README.md
- **Mechanism (README-REPORTED, repository structure observed):** Treat prompt, code, architecture or configuration as a text-valued candidate; execute on selected examples, read detailed feedback/traces, propose targeted edits with an LLM, keep a Pareto-aware archive and select by evaluation performance. `gepa.optimize` specifies separate train/validation inputs and a maximum metric-call budget.
- **Compared to MAPS_L:** THINK generates alternatives; MAPS eval can score frozen cases; MAPS operational learning stores candidates. An optimizer can sit **outside** these authoritative stores and return a *proposal artifact with evidence*. Do not equate optimizer output with an authorized new default.
- **Smallest experiment:** Given one frozen, sanitized skill-routing defect corpus, compare a human-designed one-edit fix with a bounded GEPA-inspired mutation loop using the **same** evaluator/holdout and cost ceiling. Record train/holdout separation, negative controls, latency, wrong activations and regressions. Use deterministic/mock candidates before any external API.
- **Failure conditions:** reward overfitting, holdout leakage, non-robust optimizer judgment, hidden API cost, prompt bloat. Upstream performance numbers are upstream claims, not MAPS_L results.
- **Disposition:** `STUDY/TEST`, not `INSTALL`.

### 2. Hermes Agent Self-Evolution — a concrete skill-level mutation pipeline

- Repository: https://github.com/NousResearch/hermes-agent-self-evolution
- **CODE-INSPECTED**: `evolution/skills/evolve_skill.py`, `evolution/skills/skill_module.py` (links: https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/skills/evolve_skill.py and https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/skills/skill_module.py ).
- Actual code path: find and parse `SKILL.md`; choose golden, recorded-session or synthetic evaluation examples; split train/validation/holdout; wrap the skill body as `SkillModule` text input; invoke `dspy.GEPA(...).compile(...)`; check constraints; report candidate. `reassemble_skill` retains original frontmatter and replaces only the skill body. CLI also has a `--dry-run` branch. (Inspect downstream output/PR code before assuming automatic PR semantics.)
- **Important current reality:** README's phase table marks only **skill optimization implemented**. Tool descriptions, prompt sections, code evolution and continuous loop are *planned*, not shipped. Its `evolve` code uses an optimizer fallback path, so an experiment must record **effective optimizer**, not just requested one. The baseline can fail constraints and the code prints a warning then continues; MAPS_L should fail closed when a mandatory acceptance invariant fails.
- **MAPS_L extraction:** scoped `candidate skill body + immutable baseline hash + corpus identity + effective optimizer + constraint results + held-out result` as a reviewed proposal. No automatic Skill trust promotion. This targets existing S6/SEC4/L4/L5 owners.
- **Experiment:** use a deliberately flawed skill fixture, a small frozen negative corpus and a baseline that already passes authority constraints. Confirm candidate improvement does not weaken forbidden-action negatives or exceed context budget.
- **Disposition:** strongest **implementation example** for a narrow GROW prototype; no full dependency.

### 3. ADAS / Meta Agent Search — candidate architecture search

- Repository: https://github.com/ShengranHu/ADAS
- **CODE-INSPECTED:** https://github.com/ShengranHu/ADAS/blob/main/_mmlu/search.py . Candidate agent-system implementations are kept in an archive; a meta-agent proposes new executable program designs, evaluates them on a domain-specific `evaluate_forward_fn`, and records fitness/generation metadata. The repository explicitly warns that model-generated code is executed.
- **MAPS_L extraction:** architecture/workflow variants are legitimate *experiment candidates*, but the search must not be allowed to change policy, evaluator code, GitHub review gates, or executable write boundaries. Testing may start with **data-only routing-policy** variants rather than generated arbitrary Python.
- **Discriminating experiment:** compare two fixed orchestration policies vs a bounded searched policy on held-out, task-shape-stratified cases. Keep reviewer independence and acceptance criteria identical. Record quality, unsafe actions, CPU/token cost and false helper activations.
- **Risk:** reward hacking, unsafe generated code, expensive combinatorial search. **Disposition:** `FUTURE EXPERIMENT`; not a default MAPS runtime optimizer.

### 4. Darwinian Evolver — selection among explicit candidates

- Repository: https://github.com/imbue-ai/darwinian_evolver
- **README-REPORTED:** supplies **organism (candidate)**, **evaluator** returning score/failure cases, and **mutator** returning variations. Maintains a population; selects using score plus novelty/offspring diversity, logs `results.jsonl` and snapshots. Distinguishes static mutators from agents improving themselves; no requirement to adopt self-modifying code.
- **MAPS_L extraction:** independent evaluator owns the test, proposal owns the candidate, Git SHA owns revision. Keeping multiple near-miss approaches may be better than repeatedly overwriting one "best" prompt.
- **Test:** 2–3 competing plan/skill templates with frozen tasks, select by objective metrics plus false positives. Verify candidate lineage and reverted variants. **Disposition:** small pattern worth borrowing, not a second persistent search database.

### 5. karpathy/autoresearch — constrained edit / test / keep-or-revert

- Repository: https://github.com/karpathy/autoresearch ; protocol: https://github.com/karpathy/autoresearch/blob/master/program.md
- **README-REPORTED:** `prepare.py` and evaluation remain immutable; a worker modifies `train.py`, runs fixed-budget experiments, records a scalar `val_bpb`, keeps improvements and reverts non-improvements. The project is for a narrow model-training setting.
- **MAPS_L extraction:** **immutable evaluator + narrow write scope + bounded per-test cost + explicit failed-variant rejection**, not autonomous forever-running agents or unrestricted code mutation.
- **Test:** on disposable repository fixtures use candidate-only changes and locked scoring. Explicit stopping budget, independent approval and no auto-merge; compare false promotions and time-to-good-change.
- **Limit:** a single scalar metric is insufficient for MAPS_L safety, human value and multiobjective quality. Do not copy its endless loop or GPU assumptions.

### 6. Agent Lightning — learning from *real harness* trajectories

- Repository: https://github.com/microsoft/agent-lightning
- **README-REPORTED, source tree observed:** v1.0 separates training, API gateway tracing/collection, and rollout controller; it is designed to preserve real agent tool/context environment during learning. Documentation and source include `agentlightning/`, examples and tests.
- **MAPS_L extraction:** a proposed improvement should be tested through the **actual execution path**, not exclusively an isolated prompt simulation, because recovery, tools and context routing affect outcomes. For MAPS_L this supports binding effective harness configuration to Run Records and choosing representative reality-based fixtures.
- **Limit:** GPU/RL, centralized proxy and data-capture infrastructure would be disproportionate for current MAPS_L. **Disposition:** architectural reference, no training import.

### 7. LangMem — hot-path vs background memory improvement

- Repository: https://github.com/langchain-ai/langmem
- **README-REPORTED:** separates immediate memory management tool calls from an asynchronous memory manager that extracts, consolidates and updates information; storage and retrieval API is decoupled from agent behavior.
- **MAPS_L extraction:** keep task-critical facts/authority in the existing current path; consider offline *candidate* distillation from completed runs only when provenance and scope are intact. Never grant autonomously produced memory the right to amend task policy.
- **Test:** replay stale/conflicting memories and omissions; compare naive summarization with scoped, source-linked candidate. **Disposition:** reference/negative-controls, not new memory engine.

### 8. AgentRx — evidence-grounded failure attribution

- Repository: https://github.com/microsoft/agentrx
- **README-REPORTED:** `Raw logs → Trajectory IR → static/dynamic invariants → checker → judge → report`; the checker produces auditable violation evidence before LLM classification. Source has `agentrx/ir`, `invariants`, `judge`, `pipeline`, `reports`, `tests`.
- **MAPS_L extraction:** if GROW consumes mistakes, start from deterministic failure steps and task/Run Record evidence. Do not trust a plausible model story that the incident was caused by the last failed action.
- **Test:** frozen labeled failure traces with blind held-out labels; require abstention when missing evidence, not invented causality. **Disposition:** high-priority adjunct to evaluation, not independent permission to fix production.

### 9. AI Scientist v2 — broader exploration can reduce success rate

- Repository: https://github.com/SakanaAI/AI-Scientist-v2
- **README-REPORTED:** hypotheses, experiments and analysis through progressive agentic tree search. Its own documentation cautions that relative to template-based v1 it can have lower experiment success rates in well-structured problem settings.
- **MAPS_L extraction:** THINK should increase search depth only where task uncertainty warrants it; GROW should not multiply candidates by default. Use a meaningful stop rule and matched simpler baseline.
- **Risk:** arbitrary generated code and expensive experiments. **Disposition:** evidence against default expansive search.

## Where a genuine GROW function would fit (candidate only)

```
REAL OUTCOME / TRACE / USER OBSERVATION
    ↓
JUDGE: criterion, provenance, missing-evidence checks
    ↓
LEARN: bounded defect or performance hypothesis
    ↓
THINK: alternative fixes and causal challenges
    ↓
GROW: choose controlled variants + frozen discriminating experiment
    ↓
PLAN/DO: execute tests inside existing authority (never free-running)
    ↓
JUDGE: objective + adversarial + cost + independent review
    ↓
PROPOSE: adopt / narrow / reject / park
    ↓
HUMAN OR EXISTING APPROVED GATE before production/policy change
```

**Do not create a GROW database or perpetual agent.** The above is a conceptual routing overlay on existing MAPS_L and Pilot owners, not a new lifecycle or policy. The previous `JUDGE → LEARN` work may already make such an overlay redundant.

### Minimum viable proof, before a name or implementation

1. Select **one** existing MAPS_L weakness that has frozen examples (skill-routing vocabulary-shift false negatives, trace-level failure attribution, or unnecessary delegation). Do **not** manufacture an improvement target.
2. Freeze a small baseline, holdout, adversarial/negative cases, and success criteria. Separate optimizer examples from promotion holdout.
3. Use the existing owner to propose **at most 2–3** candidate changes; an initial zero-cost test can use hand-authored variants before API optimizers.
4. Run the **unchanged** baseline and candidate through identical evaluator/runtime conditions, including configuration identity and captured cost.
5. Accept only a *research finding* on this initial pass. Adoption requires existing explicit authority and independent review. If no incremental gain over ordinary MAPS_L learning, **reject a new GROW mechanism**.
6. Measure not only correctness but also extra work, false approvals, regression leakage, intervention time, and task completion; no claim of general superiority from one benchmark.

## Recommendation / open decision

**Default:** keep THINK/PLAN/DO/JUDGE/LEARN as the conceptual capabilities, and call the experimental optimization activity **GROW** informally *within* the existing Learning and Evaluation owner. Do not spin out a named GROW service until experiments show a distinct need. The missing capability, if any, is **evidence-bound improvement search with held-out selection**, not "more self-reflection."

Strongest narrow first mechanism to test: **Hermes-style skill-body candidate mutation with GEPA-style trace feedback and autoresearch-style locked evaluator**, using the existing MAPS_L skill gate and revision-bound review. First run should require no new dependency or paid calls.

**Source caveat:** repo READMEs are claims, not independent replicates. This note inspected named code files for Hermes and ADAS; other mechanisms are documented at public interfaces only. No upstream experiments or MAPS_L improvements were executed for this report.
