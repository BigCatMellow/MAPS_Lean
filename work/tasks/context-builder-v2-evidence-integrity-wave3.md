# Task: Context Builder v2 evidence-integrity evaluation

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `RESEARCH`
- Owner: `agent/context-builder-evidence-integrity-wave3`
- Risk: `MEDIUM`
- Goal: Freeze an evaluation-first Context Builder v2 evidence-integrity package that can test exact evidence cards independently from any retrieval algorithm.

## Inputs and source of truth

- Inputs:
  - `AGENTS.md`
  - `runtime/context_builder.py`
  - `tests/test_context_builder.py`
  - `work/roadmaps/prime-agent-capability-roadmap.md`
  - `work/roadmaps/agent-harness-capabilities/05-learning-and-evaluation.md`
  - `migration/FUTURE_IDEAS_BACKLOG.md`
  - `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`
  - PR #36 reconciliation only as non-authoritative planning evidence
  - PR #27 frozen Skill-selection corpus only as a structural precedent for a frozen eval artifact
- Authoritative sources: merged `main` behavior and root `AGENTS.md` win over draft PR/planning prose.
- Evidence labels:
  - `VERIFIED`: merged Context Builder v1 is explicit-first, hashes referenced files, and does not scan or use semantic retrieval.
  - `VERIFIED`: legacy `EXP-0006` was `REVISE`; its lexical retriever is not a validated production direction.
  - `VERIFIED`: surviving evidence-integrity requirements include exact anchors, hashes/drift, temporal attribution, negative boundaries, frozen holdouts, paraphrase/vocabulary shift, and honest substitute credit.
  - `PLANNING`: PR #36's `NEXT C` classification is sequencing guidance, not runtime authority.
- Dependencies / preconditions: none for a frozen non-runtime evaluation package; production Context Builder v2 behavior remains a later reviewed task.

## Change boundary

- MAY CHANGE:
  - `work/tasks/context-builder-v2-evidence-integrity-wave3.md`
  - `work/notes/2026-08-15-context-builder-v2-evidence-integrity.md`
  - `work/evals/context-builder-evidence-integrity-v1.json`
  - `tests/test_context_builder_evidence_integrity_fixture.py`
- MUST NOT CHANGE:
  - `runtime/**`
  - canonical task/state/policy schemas
  - existing roadmaps/backlogs/audits
  - PR #20-#38 implementation/review branches
  - production Context Builder selection/retrieval behavior
- MAY CHANGE IF NECESSARY: none; new output paths or runtime behavior require a separate reshaped task.
- OPERATOR APPROVAL REQUIRED: any production retrieval strategy, semantic/vector dependency, authority change, or automatic promotion.

## Decision authority

- Owner may decide: synthetic fixture content, frozen case mix, evidence-card schema for evaluation, deterministic fixture-validation checks, and non-runtime experiment sequencing.
- Owner must escalate: production retrieval algorithm choice, new dependencies/services, changes to task/policy authority, persistence, user data retention, or automatic learning/promotion behavior.

## Acceptance criteria

- [x] Frozen corpus contains exact-source/anchor truth with deterministic source hashes.
- [x] Corpus covers direct wording, paraphrase, vocabulary shift, hard negatives, temporal/current-vs-historical questions, authority-status distinction, explicit negative boundaries, source drift, and substitute-credit discipline.
- [x] Candidate output contract preserves `ABSTAIN`/`UNKNOWN` and separates evidence integrity from retrieval algorithm choice.
- [x] Acceptable substitutes earn credit only if actually retrieved/proven.
- [x] Source-drift cases require explicit hash mismatch reporting rather than silently reusing stale evidence.
- [x] Fixture test mechanically validates IDs, hashes, anchors, drift pairs, and case invariants.
- [x] No semantic/vector/lexical retrieval implementation or production Context Builder behavior is added.
- [x] Design note defines the control/treatment sequence so evidence-card integrity is tested before retrieval improvements.
- [x] Independent review is required before treating the package as the frozen baseline for a future experiment.

## Verification and evidence

- Verification:
  - `python -m json.tool work/evals/context-builder-evidence-integrity-v1.json >/dev/null`
  - `python -m unittest tests.test_context_builder_evidence_integrity_fixture -v`
  - PR Runtime CI after publication.
- Evidence to preserve: exact branch/head, changed-file list, focused test result, Runtime CI result, independent review.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: repository-only deterministic fixture validation; no provider/model/network requirement.
- Ordered procedure:
  1. freeze synthetic source corpus and truth labels;
  2. validate hashes/anchors mechanically;
  3. independently review the frozen package;
  4. later run an explicit-source evidence-card projector against it;
  5. only after integrity passes, compare any retrieval supplementation against the explicit-first control.
- Failure branches:
  - IF an expected anchor is not mechanically resolvable THEN fix the frozen fixture before experiment use.
  - IF a case requires general knowledge or unstated truth THEN remove/reshape it.
  - IF a retrieval candidate is proposed before evidence-card integrity is separately measured THEN keep the retrieval work blocked.
- Rollback / recovery: delete/reject this draft package; it changes no runtime behavior.
- Security / privacy controls: all fixtures are synthetic; do not copy private prompts, credentials, user content, or raw legacy text into the corpus.
- External side effects: Git branch/draft PR only.
- Effort limit: bounded to the four declared paths; no retrieval implementation.
- Approved reference: `NEXT C — Context Builder v2 evidence integrity` in the reconciliation planning view, plus merged architecture invariants.

## Stop / escalate

Stop rather than guess if:

- merged Context Builder behavior materially changes;
- a case cannot distinguish current/historical/authority status from source evidence alone;
- the package would require a new runtime dependency or retrieval engine;
- an overlapping Context Builder v2 branch appears.

Escalate to: operator for scope/production strategy; independent reviewer for corpus correctness.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task intentionally does **not** answer which retrieval method should win.
- The first experiment isolates evidence-card integrity from retrieval. This prevents a retrieval algorithm from hiding bad anchors/status/hash handling behind a high recall score.
- `EXP-0006` contributes failure lessons and evaluation requirements, not a retriever implementation.
- The explicit-first Context Builder v1 remains the production baseline until a later reviewed change says otherwise.

## Completion / handoff

- Completed: frozen corpus, validation test, and experiment-design note prepared on an isolated branch.
- Not completed: model/agent Layer 2 execution, retrieval comparison, production Context Builder v2 implementation.
- Current blocker: independent review before this corpus should be treated as a frozen experimental baseline.
- Next action if not DONE: independently review the corpus truth labels, anchors, drift semantics, and evaluation boundaries.
