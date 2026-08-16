# Context Builder v2 Stage 2 — retrieval experiment note

Date: 2026-08-15/16
Owner: `agent/context-retrieval-stage2-wave3`
Status: evaluation evidence only

## Why this is the next Context Builder step

Stage 1 already separates evidence integrity from retrieval choice. That prevents a retriever from receiving credit merely because it found text that looked relevant while using the wrong version, wrong anchor, wrong authority status, or unsafe substitute.

Stage 2 now asks a narrower question:

> Given the frozen source universe, which candidate sources would a retrieval method surface before evidence-card verification?

The answer is evaluated independently from production routing.

## Frozen overlay

`work/evals/context-builder-retrieval-stage2-v1.json` layers explicit source availability over the existing 16-case evidence-integrity corpus.

It deliberately leaves several cases without explicit sources:

- paraphrase;
- vocabulary shift;
- hard negatives;
- substitute-credit case.

The two drift cases start from the stale frozen source IDs so structural same-path supplementation can be tested without using answer truth.

The overlay is not runtime authority and contains no production selector.

## Controls

### 1. Explicit-only

This represents the current explicit-first philosophy in its narrowest form.

Benefits:

- very low false-activation surface;
- preserves operator/task-linked source intent;
- no repository scan or semantic inference.

Expected limitation:

- cannot answer cases whose necessary source was not explicitly supplied;
- stale explicit references do not automatically locate the current same-path source.

### 2. Explicit + same-path drift sibling

This is a structural, non-semantic supplement.

If an explicitly supplied source is non-current, the evaluator may add another frozen source record only when:

- repository path is exactly the same;
- hash differs;
- sibling source exists in the frozen source universe.

Current explicit sources are not expanded to historical siblings merely because those siblings share a path.

This is intentionally narrow. It tests whether drift can be surfaced mechanically before broad retrieval is considered.

### 3. Lexical overlap negative control

This is **not** a production candidate.

When no explicit source is supplied, it ranks source path/content using deterministic dependency-free token overlap with IDF weighting and selects up to the frozen `top_k` when at least one non-stopword term overlaps.

The corpus contains adversarial cases specifically meant to make this approach look attractive while being unsafe:

- credential-rotation question vs a document saying there is **no rule** about credential rotation;
- invented two-reviewer rule vs real documents containing review/independence vocabulary;
- current-vs-historical wording traps elsewhere in the corpus.

The lexical method is forcibly marked non-candidate even if some aggregate recall is high. Its purpose is to preserve a reproducible negative baseline and prevent the old failure mode from being rediscovered later as if it were new evidence.

## Source-selection evaluator

`runtime/context_retrieval_eval.py` validates the original corpus through the Stage-1 scorer first, then validates the Stage-2 overlay and externally supplied source rankings.

For each case it records:

- selected source IDs;
- frozen explicit prefix;
- whether an accepted source was retrieved;
- top-1 accepted status;
- forbidden source selection;
- drift-pair completeness;
- hard-negative abstention;
- explicit-prefix preservation.

It computes:

- evidence source recall;
- evidence source precision;
- hard-negative abstention accuracy;
- forbidden-source case count;
- drift-pair recall;
- vocabulary-shift recall;
- average candidate count;
- overall case pass rate.

## Promotion discipline

The evaluator contains a strict candidate gate, but that gate means only:

> source-selection behavior is clean enough to be proposed for the next evaluation stage.

It never means:

- retrieval is production-approved;
- the source is valid evidence;
- routing may change;
- policy may change;
- semantic/vector infrastructure should be installed;
- automatic promotion may occur.

A proposal-eligible candidate must satisfy all frozen safety gates simultaneously:

```text
perfect hard-negative abstention
+ zero forbidden temporal-source selection
+ complete drift-pair recall
+ vocabulary-shift recall
+ perfect evidence-source recall
+ perfect evidence-source precision
+ explicit-first prefix preserved
```

Perfect precision is intentional on this small frozen corpus. A candidate that finds the right source by returning the right source **plus unrelated sources** has not earned proposal eligibility. High recall cannot wash out source pollution.

No weighted average can compensate for a failed hard-negative, forbidden-source, or precision gate.

## Why source selection stays separate from evidence cards

A retriever may correctly surface `CB-SRC-001` while an answer/extraction step still:

- cites the wrong section;
- reports the wrong source hash;
- treats a negative boundary as positive permission;
- claims a historical rule is current;
- invents an acceptable substitute;
- ignores source drift.

Those are Stage-1 failures.

Therefore the pipeline remains:

```text
explicit source inputs
        ↓
optional candidate-source supplementation
        ↓
Stage-2 source-selection report
        ↓
exact evidence-card projection
        ↓
Stage-1 integrity report
        ↓
proposal / independent review
        ↓
possible production decision
```

This avoids letting retrieval recall substitute for evidence correctness.

## Future semantic/vector candidates

This PR deliberately does not choose an embedding provider, model, vector database, or index.

A future experiment can produce a complete list of:

```json
{"case_id":"CBI-004","source_ids":["CB-SRC-001","CB-SRC-003"]}
```

for every frozen case and submit those rankings to `evaluate_source_rankings()`.

That keeps the evaluator model-agnostic. Candidate generation may happen in a disposable experiment without embedding its implementation into MAPS runtime.

Only if a candidate clearly beats the controls on the safety gates should the project decide whether the implementation cost/dependency/privacy tradeoffs justify a production proposal.

## Expected control behavior

The tests intentionally lock several qualitative expectations rather than pretending the small corpus supplies a universally meaningful benchmark score:

- explicit-only preserves exactly what was supplied;
- same-path drift supplementation finds both current counterparts in the drift cases;
- current explicit evidence is not expanded backward into historical siblings;
- lexical overlap activates on the hard-negative traps;
- therefore lexical hard-negative abstention is imperfect;
- therefore lexical is not eligible even before its forced-negative-control flag is considered;
- an ideal externally supplied ranking can pass the evaluator contract while still having `automatic_promotion = false`;
- an otherwise ideal ranking polluted with an unrelated source keeps perfect recall but fails the precision gate and is not proposal-eligible.

## Why this is not EXP-0006 again

The legacy mistake was not simply "lexical matching existed." The larger problem was allowing a retrieval mechanism to look validated without robust evidence-integrity and frozen adversarial evaluation.

This Stage-2 work reverses that order:

1. evidence-integrity truth frozen first;
2. negative and temporal traps explicit;
3. source selection measured separately;
4. lexical behavior retained only as a disqualified baseline;
5. no runtime selector exists;
6. no passing score can promote itself.

The lexical control is therefore evidence **against** casually reintroducing lexical retrieval, not a revival of the legacy mechanism.

## Multi-agent boundary

No active lineage, communication, Skills, Environment, review, or integration branch is modified.

This branch stacks only on our existing Context Builder Stage-1 branch and adds new evaluation paths.

## Next useful experiment

After this scaffold passes CI, the highest-value next Context Builder work is not another production feature. It is to obtain one bounded semantic or otherwise vocabulary-robust candidate ranking against the 16 frozen cases and compare it with:

- explicit-only;
- same-path drift control;
- lexical negative control.

If semantic supplementation cannot maintain perfect hard-negative, temporal, and precision gates, it should not advance merely because paraphrase recall improves.
