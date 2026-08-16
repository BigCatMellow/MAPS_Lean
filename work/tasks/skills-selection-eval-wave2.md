# Task: frozen Skill-selection evaluation corpus

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: establish the first frozen, model-agnostic Skill-selection evaluation corpus and scorer before MAPS gains autonomous Skill routing.

## Inputs and source of truth

- Inputs: `AGENTS.md`, PR #26 / `agent/skills-catalog-wave2`, `work/roadmaps/agent-harness-capabilities/02-procedural-knowledge-and-skills.md` S4, historical MAPS retrieval failures documented in the roadmap/research notes.
- Authoritative sources: active repository instructions and code win; the roadmap defines evaluation intent; the frozen corpus is test evidence, not routing authority.
- Dependencies / preconditions: verified Skills catalog implementation head `564498285be1519b10183247eab5f73a42f5cc6c` with successful Runtime stack CI `31896101565` on its implementation commit.

## Change boundary

- MAY CHANGE: new `runtime/skills/evaluation.py`, `runtime/skills/__init__.py` exports, frozen `work/evals/skill-selection-v1.json`, focused tests, this task file.
- MUST NOT CHANGE: Skill discovery/catalog semantics, Context Builder, routing, task/policy/review authority, Skill trust/approval state, script/tool execution, external systems.
- MAY CHANGE IF NECESSARY: corpus/test wording and scorer representation inside this evaluation-only boundary.
- OPERATOR APPROVAL REQUIRED: autonomous Skill activation/routing, persistent trust/approval state, external model/provider calls, or material scope expansion.

## Decision authority

- Owner may decide: corpus schema, representative cases, score definitions, strict prediction validation, and report serialization consistent with the roadmap.
- Owner must escalate: any design that embeds a production selector in the evaluator, makes benchmark expected answers runtime authority, or turns evaluation results directly into automatic promotion.

## Acceptance criteria

- [x] frozen corpus includes direct positives, paraphrases, vocabulary shifts, near misses, hard negatives, no-Skill cases, multi-Skill cases, and explicit ambiguity.
- [x] candidate Skill metadata is frozen with the corpus so routing strategies can be compared against the same discovery surface.
- [x] evaluator accepts externally produced predictions; it does not implement or choose a production routing strategy.
- [x] predictions distinguish `SELECT`, `ABSTAIN`, and `AMBIGUOUS` rather than encoding all outcomes as a ranked list.
- [x] missing/duplicate/unknown-case predictions fail explicitly rather than being silently scored as abstention.
- [x] predictions naming unknown Skills fail explicitly.
- [x] scorer reports exact-case accuracy, selection precision/recall/F1, abstention accuracy, ambiguity accuracy, false activations, missed activations, ambiguity misses, and category accuracy.
- [x] report is bound to a deterministic corpus SHA-256 and is serializable for future comparative eval records.
- [x] perfect predictions score 1.0 across all applicable metrics.
- [x] focused tests and full Runtime stack CI pass.
- [ ] independent review remains required before completion.

## Verification and evidence

- Verification: PR-triggered full Runtime stack CI run `31897351677` passed on implementation commit `7175282c25584761f52059b36282c1f062d185c0`.
- Evidence to preserve: frozen corpus hash, GitHub Actions run `31897351677`, PR #27 diff, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: existing MAPS Lean Python runtime; no model/provider required.
- Ordered procedure: freeze candidate/case corpus → implement loader/scorer → focused behavioral tests → stacked draft PR → full CI → independent review.
- Failure branches: IF a production routing strategy is needed to make the evaluator useful THEN stop; keep evaluation separate and add candidate selectors in later experiments.
- Rollback / recovery: revert isolated stacked commit/PR; no schema/data migration.
- Security / privacy controls: corpus contains synthetic tasks only; hard negatives include instruction-bearing fixture text to measure false activation; no credentials/provider calls.
- External side effects: Git branch/PR publication only.
- Effort limit: S4 evaluation infrastructure only; no autonomous routing or Context Builder integration.
- Approved reference: Procedural Knowledge & Skills roadmap S4 / EXP-A.

## Stop / escalate

Stop rather than guess if:

- scoring requires inventing a preferred model/provider;
- the benchmark begins deciding task authority or activating procedures;
- a benchmark result would be automatically promoted into production behavior.

Escalate to: operator / roadmap re-shaping as appropriate.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task stacks on PR #26 rather than blocking on its review because the dependency is explicit and its implementation passed full Runtime stack CI.
- The corpus freezes five synthetic candidate Skills and 24 representative tasks. It is deliberately small enough to inspect manually but covers the failure modes MAPS most needs to measure before routing.
- `AMBIGUOUS` is a first-class expected outcome because silently choosing among materially different procedures is itself a routing failure.
- Hard negatives include wording that resembles a Skill trigger while the actual requested action should not load that Skill.
- The evaluator scores predictions only. Candidate selectors/models will be separate experiments so the benchmark cannot quietly become production routing code.

## Completion / handoff

- Completed: frozen corpus, model-agnostic evaluator/scorer, focused tests, draft PR #27, and full Runtime stack CI.
- Not completed: independent review / merge.
- Current blocker: independent review required for completion; production Skill routing remains intentionally unimplemented.
- Next action if not DONE: independent review of PR #27; candidate routing strategies may be evaluated only as separate experiments against this frozen corpus before any production integration.
