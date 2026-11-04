# Community GitHub mechanisms — evaluation, trace diagnosis, regression (2026-11-04)

Status: **RESEARCH — NOT ACTIVE AUTHORITY**. Primary repository READMEs inspected 2026-11-04; proposed MAPS_L experiments have NOT been run. Link to [existing reliability research](2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md) for previous incident/fix history.

## Candidate A — THU-KEG TrajDebug: first decisive error vs last visible failure
- Source: https://github.com/THU-KEG/TrajDebug.
- Upstream described method: build multi-resolution trajectory views; find evidence-grounded wrong commitments, classify whether they were resolved and whether they affected terminal outcome, and attribute the earliest decisive failure. Includes data adapters/evaluation/viewer.
- MAPS_L current baseline: Run Records, incident taxonomy, regression cases, review summaries. They may document **that** work failed but not accurately **where** it became irrecoverably wrong.
- Smallest candidate: freeze 10–20 known-failure traces; require step+evidence references and human-labeled critical step before any automated diagnostic promotion. Compare agreement and false attribution vs manually reading current Run Records.
- Caveat: research-stage diagnostics; judges can produce plausible but wrong causes. **TEST; no automated corrective mutation.**

## Candidate B — AgentRx: typed trace -> invariants -> audit -> diagnosis
- Source: https://github.com/microsoft/agentrx.
- Upstream describes a normalized trajectory IR, static/dynamic invariants, deterministic checking, then LLM-aided judgment with a concrete violation log.
- Reusable principle: put auditable invariant failures **before** narrative diagnosis. MAPS_L already has deterministic integrity checks; use their results as the evidence layer rather than importing AgentRx's pipeline or judge.
- Test same frozen failures as TrajDebug; score attribution accuracy, abstention on missing events, and per-trace cost. **STUDY/TEST.**

## Candidate C — Inspect AI: task + solver + scorer independent composition
- Source: https://github.com/UKGovernmentBEIS/inspect_ai.
- Upstream: modular evaluation tasks, datasets, model solvers, scorers, tool/sandbox support and evaluation logs.
- MAPS_L already has frozen cases and deterministic evaluator. Extract **matched-arm experimental discipline**: same task inputs and scoring between lean-agent, current MAPS, modified MAPS, with separate cost/latency/outcome metrics and immutable configuration identity.
- Test: small predeclared evaluation matrix; no paid execution without approval, no promotion from a single sample or judge alone. **ADAPT TEST DESIGN**, not whole eval framework.

## Candidate D — promptfoo: CI regression suite + adversarial scenarios
- Source: https://github.com/promptfoo/promptfoo.
- Upstream: declarative prompts/agents assertions, cross-model comparisons, red-team test cases and CI integration.
- MAPS_L already has regression and security corpora. Extract compact **negative scenarios** (wrongly authorized tool use, stale review, prompt injection through tool output), and test false-positive rate on benign equivalents.
- Reject a new promptfoo runtime dependency until it has a concrete coverage advantage over built-in tests. **STUDY test corpus patterns.**

## Candidate E — elementics/ag + Pi extensions: cost of ineffective actions
- Sources: https://github.com/elementics/ag ; https://github.com/corporealshift/pi-extensions.
- Upstream descriptions include repeated-file-edit loop guards and end-of-turn lint checks. Their claimed thresholds are project-specific, not demonstrated universal rules.
- MAPS_L hypothesis: non-progress needs operational metrics, not only stall labels. Frozen diagnostics could measure repeated writes with no new evidence, retry churn, unnecessary review handoffs, and validation time per corrected defect.
- Test: replay good iterative work as negative controls; detect only evidence-backed waste. **TEST, no automatic stops initially.**

## Evaluation quality invariants
- Every test must distinguish `observed` vs `reported` results, task shape, model/provider identity, and actual tool/runtime config where available.
- Preserve incomplete/unknown coverage; never infer success or failure from missing traces.
- Do not let a self-evaluating model approve its own substantive changes.
- Compare proposed addition against simplest current MAPS_L behavior and a non-MAPS baseline where appropriate.
- Use task correctness, cost, elapsed time, interruptions, recovery, operator interventions, and unsafe/false-blocked actions.
- Avoid treating benchmark scores as real-world outcomes; record the boundary.

## Priority
**First:** source-linked failure attribution over existing Run Records. **Second:** matched-arm eval structure for small-vs-swarm routing. **Third:** context retrieval and compaction hard negatives. Execution and production promotion remain separately authorized.
