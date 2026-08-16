# Task: Context evidence scorer Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `context-evidence-scorer-wave3`
- Risk: `MEDIUM`
- Goal: implement a deterministic, retrieval-agnostic Stage 1 evidence-card projector/scorer against the frozen Context Builder v2 evidence-integrity corpus without changing production context selection.

## Inputs and source of truth

- Inputs:
  - root `AGENTS.md`
  - `work/evals/context-builder-evidence-integrity-v1.json`
  - `work/notes/2026-08-15-context-builder-v2-evidence-integrity.md`
  - PR #39 exact accepted-for-stacking head `57b42557af1db2d7d23849766b0841c3a0395460`
- Authoritative sources: current repository operating contract plus the frozen corpus for this experiment.
- Evidence labels: PR #39 is a dependency/input, not merged runtime authority.
- Dependencies / preconditions: frozen corpus exists and mechanically validates.

## Change boundary

- MAY CHANGE:
  - `runtime/context_evidence.py`
  - `tests/test_context_evidence.py`
  - this task file
  - `work/notes/2026-08-15-context-evidence-scorer.md`
- MUST NOT CHANGE:
  - production Context Builder selection/retrieval behavior
  - task/state/policy/review/harness authority
  - PR #39 frozen corpus
  - semantic/vector indexes, embeddings, repository crawlers, knowledge graphs
  - existing review/harness PR branches
- MAY CHANGE IF NECESSARY: scoring semantics only through explicit task amendment and corresponding tests.
- OPERATOR APPROVAL REQUIRED: any production retrieval/routing activation or external side effect.

## Decision authority

- Owner may decide: bounded pure-function API shape, deterministic report structure, strict candidate-result validation, focused tests.
- Owner must escalate: any retrieval algorithm choice, runtime activation, authority interpretation, corpus-truth change, new dependency, or automatic promotion behavior.

## Acceptance criteria

- [x] Explicitly selected source/anchor can be projected into a card only when source hash and anchor resolve exactly.
- [x] No source search/ranking/retrieval occurs in the projector/scorer.
- [x] Expected primary cards and exact returned substitutes can receive credit.
- [x] Partial/malformed substitutes, extra uncredited cards, forbidden temporal sources, wrong hashes, and incorrect drift claims fail.
- [x] Missing/explicit `UNKNOWN` results remain `INCOMPLETE` rather than being silently coerced to fail/pass.
- [x] Hard negatives require clean abstention.
- [x] Same-path drift requires exact frozen/current IDs and hashes plus explicit mismatch/path facts.
- [x] Report is deterministic and explicitly disables automatic promotion.
- [x] Focused tests cover the above behavior.

## Verification and evidence

- Verification:
  - `python -m unittest tests.test_context_evidence -v`
  - full PR Runtime stack CI
- Evidence to preserve: exact head, focused/full CI result, changed-file list.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: repository Python runtime.
- Ordered procedure: validate frozen corpus → normalize externally supplied results → verify exact evidence integrity → produce read-only report.
- Failure branches: malformed candidate schema/corpus fails closed; missing or explicit unknown evidence remains incomplete.
- Rollback / recovery: revert this isolated stacked PR; no durable state migration exists.
- Security / privacy controls: no raw private prompts, credentials, provider transcripts, or hidden model reasoning required.
- External side effects: none.
- Effort limit: one bounded Stage 1 projector/scorer; no Stage 2 retrieval work.
- Approved reference: PR #39 frozen corpus.

## Stop / escalate

Stop rather than guess if:

- the frozen corpus truth must change;
- scoring would require choosing a retrieval algorithm;
- runtime task/policy authority would be affected;
- a new persistent evidence store appears necessary.

Escalate to: operator / separate shaped task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Stage 1 evaluates evidence integrity after a source/anchor has been explicitly selected. It deliberately does not answer how the source was found.
- `UNKNOWN` is preserved as incomplete evidence.
- Candidate outputs are externally supplied; passing results cannot self-promote a retrieval/routing change.

## Completion / handoff

- Completed: implementation and focused adversarial tests committed on the isolated branch.
- Not completed: independent review; Stage 2 retrieval comparison.
- Current blocker: none for implementation; review remains pending by operator choice.
- Next action if not DONE: run/inspect PR Runtime CI, then prepare exact-head review packet.
