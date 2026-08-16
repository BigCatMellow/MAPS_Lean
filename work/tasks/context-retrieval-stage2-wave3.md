# Task: Context Builder v2 retrieval Stage 2 Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `EVALUATION`
- Owner: `agent/context-retrieval-stage2-wave3`
- Risk: `MEDIUM`
- Goal: Add an evaluation-only source-retrieval comparison on top of the frozen Context Builder evidence-integrity corpus without changing production Context Builder behavior or reviving the legacy lexical claim-card retriever.

## Inputs / source of truth

- Root `AGENTS.md`.
- PR #39 frozen `context-builder-evidence-integrity-v1` corpus.
- PR #41 Stage-1 evidence projector/scorer at exact head `c997821c4a5f3d11c2bc7f8a98dd7a33750c3feb`.
- Legacy `EXP-0006` conclusion: lexical claim-card retrieval was not validated and must not be treated as production evidence.

Frozen truth remains owned by the #39 corpus and #41 scorer. This task adds only a retrieval-input overlay and source-selection evaluator.

## Change boundary

MAY CHANGE:

- `runtime/context_retrieval_eval.py`
- `tests/test_context_retrieval_stage2.py`
- `work/evals/context-builder-retrieval-stage2-v1.json`
- `work/tasks/context-retrieval-stage2-wave3.md`
- `work/notes/2026-08-15-context-retrieval-stage2.md`

MUST NOT CHANGE:

- production Context Builder behavior;
- `runtime/context_builder.py` or equivalent production planning/routing path;
- #39 frozen truth;
- #41 evidence-integrity semantics;
- repository crawling/indexing state;
- semantic/vector/embedding dependencies;
- task/policy/review/routing authority;
- other agents' branches.

## Experiment design

The Stage-2 overlay freezes which source IDs would already be explicitly task-linked in each synthetic case. It does not alter expected answer/evidence truth.

Three deterministic controls are compared:

1. `explicit_only` — use only frozen explicit source IDs;
2. `same_path_drift` — preserve explicit-first order and, only for stale/non-current explicit sources, add exact same-path different-hash siblings;
3. `lexical_negative_control` — when the explicit source set is empty, rank source path/content by bounded token overlap.

The lexical control is explicitly `promotion_candidate: false`. Its purpose is to measure the known safety failure mode, not propose production retrieval.

Future semantic/vector or other methods may submit externally produced source rankings to the same evaluator without changing its truth labels.

## Separation from Stage 1

Stage 2 answers only:

> Did the candidate select a source set containing the right evidence source without unsafe activations/version mistakes?

It does **not** construct or validate final evidence cards.

Stage 1 still owns:

- source hash correctness;
- anchor correctness;
- proof role;
- polarity;
- temporal scope;
- exact drift reporting;
- acceptable-substitute evidence credit.

Thus a Stage-2 source hit is not sufficient evidence or production authority.

## Metrics / gates

Report metrics include:

- evidence-source recall;
- evidence-source precision;
- hard-negative abstention accuracy;
- forbidden-source case count;
- drift-pair recall;
- vocabulary-shift recall;
- average candidate count;
- case pass rate.

A candidate can be eligible only for **proposal**, never automatic promotion, when all strict gates pass:

- perfect hard-negative abstention;
- zero forbidden temporal-source cases;
- complete drift-pair recall;
- vocabulary-shift recall;
- perfect evidence-source recall;
- frozen explicit prefix preserved.

Passing remains evaluation evidence only.

## Acceptance criteria

- [x] Explicit-first source order is mechanically preserved.
- [x] Same-path drift supplementation improves stale-source pairing without adding historical siblings to already-current explicit evidence.
- [x] Lexical negative control is deterministic and dependency-free.
- [x] Hard-negative lexical false activation is executable and visible in the report.
- [x] Lexical negative control is forced non-candidate regardless of measured recall.
- [x] Future externally supplied rankings can use the same evaluator.
- [x] Missing cases, unknown sources, duplicate sources, invalid overlay coverage fail closed.
- [x] Report never claims automatic production promotion.
- [x] No production Context Builder or routing behavior changes.

## Verification

Focused:

```text
python -m json.tool work/evals/context-builder-retrieval-stage2-v1.json >/dev/null
python -m unittest tests.test_context_retrieval_stage2 -v
```

Full PR-triggered Runtime CI is the repository validation gate.

Review required: `INDEPENDENT_REVIEW`.

## Stop / escalation

Stop rather than promote if:

- hard-negative abstention is imperfect;
- temporal forbidden sources are selected;
- vocabulary-shift robustness is weak;
- a candidate requires production indexing/routing changes before evaluation;
- a new dependency or model/provider choice would materially widen scope;
- another agent claims the same retrieval-evaluation paths.

## Continuation

If this evaluation scaffold is accepted:

1. record exact control results;
2. submit one or more bounded semantic/other candidate source rankings from outside the evaluator;
3. compare them on the same frozen corpus/overlay;
4. feed selected source candidates through Stage-1 evidence integrity;
5. only after both stages pass, shape a production proposal for independent review/operator decision where required.
