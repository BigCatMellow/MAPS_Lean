# Context Builder v2 — Stage 1 evidence projector/scorer

Status: `IMPLEMENTED ON STACKED DRAFT BRANCH — NOT PRODUCTION AUTHORITY`

Branch: `agent/context-evidence-scorer-wave3`

Base dependency: repaired PR #39 exact head `adf25a5721808cd272bc9eb9af90a25038f568eb`. Earlier head `57b42557af1db2d7d23849766b0841c3a0395460` is historical/superseded.

## Purpose

Implement the smallest executable mechanism needed to test the frozen Context Builder v2 evidence-integrity corpus **before** evaluating any retrieval algorithm.

The Stage 1 question is:

> Given an explicitly selected source/anchor and externally supplied candidate evidence, does MAPS preserve exact source identity, hash, anchor, proof role, polarity, temporal scope, negative boundaries, abstention, and source drift honestly?

It is deliberately **not**:

> Can MAPS search the repository and find the right source?

That remains Stage 2.

## Projector boundary

`project_evidence_card()` accepts an explicitly chosen frozen source plus an explicit anchor/proof-role/polarity/temporal scope.

It:

- recomputes and validates the source content hash;
- verifies the anchor resolves in that source;
- returns the exact six-field evidence card.

It does **not**:

- search;
- rank;
- expand a query;
- use embeddings;
- choose a source;
- choose an anchor;
- infer policy/authority;
- write durable evidence.

## Scorer boundary

`evaluate_evidence_integrity()` consumes:

1. the frozen PR #39 corpus;
2. externally supplied per-case candidate results.

Candidate result shape:

```text
case_id
outcome: EVIDENCE | ABSTAIN | DRIFT_REPORTED | UNKNOWN
cards[]
drift?  # only when reporting exact source drift
```

Each returned card must use the six-field frozen contract:

```text
source_id
source_sha256
anchor
proof_role
polarity
temporal_scope
```

The scorer does not execute an agent/model/retriever itself.

## Important scoring rules

### Wrong evidence vs incomplete evidence

These remain different states:

```text
wrong source/hash/anchor/role/time/sign
→ FAIL

missing case
or explicit UNKNOWN
→ INCOMPLETE
```

This preserves the MAPS rule that uncertainty must not be silently converted into certainty.

### Exact alternatives only

An acceptable substitute receives credit only when the candidate **actually returns it** with the full exact card semantics.

A related source, partial card, correct source with wrong polarity, or correct anchor with stale hash does not receive substitute credit.

### Evidence pollution fails

Returning a valid primary card plus an unrelated/uncredited card fails the case. This prevents a high-recall strategy from hiding false positives behind one correct answer.

### Temporal forbidden evidence fails

Where the frozen case forbids a source because it answers the wrong historical/current question, returning it fails even if its text is otherwise related.

### Drift is explicit

A source-drift result must identify:

- frozen source ID + exact frozen hash;
- current source ID + exact current hash;
- whether the paths are the same;
- whether the hashes differ.

No silent rebinding of an old evidence reference to current content is allowed.

### Hard negatives require clean abstention

An `ABSTAIN` case passes only with no evidence cards and no drift payload.

### No auto-promotion

The report embeds:

```text
automatic: false
```

A perfect score remains evaluation evidence only.

## Metrics

The scorer reports the frozen corpus metrics separately rather than collapsing everything into one scalar:

- case outcome accuracy;
- exact source accuracy;
- anchor accuracy;
- source-hash accuracy;
- proof-role accuracy;
- negative-boundary accuracy;
- negative-abstention accuracy;
- temporal/version accuracy;
- source-drift detection accuracy;
- acceptable-substitute precision when a substitute is actually attempted;
- vocabulary-shift case accuracy.

Case status is separately `PASS`, `FAIL`, or `INCOMPLETE`.

## Adversarial tests

Focused tests cover:

- exact projector output;
- missing anchor rejection;
- a perfect 16-case candidate;
- exact substitute credit;
- wrong-polarity substitute rejection;
- current-vs-historical forbidden evidence;
- hard-negative evidence pollution;
- incorrect drift reporting;
- missing case → `INCOMPLETE`;
- explicit `UNKNOWN` → `INCOMPLETE`;
- extra uncredited evidence;
- wrong source hash;
- result-order determinism;
- unknown candidate-result fields fail closed.

## What this unlocks

After this scorer and PR #39 are eventually accepted, Stage 2 can compare retrieval strategies on the **same frozen truth**:

```text
explicit-first control
vs
candidate supplementation
```

The retriever can then be judged on whether it supplies evidence that passes this integrity layer, rather than merely whether it returns plausible-looking text.

## Non-goals / do not infer

This work does not show that:

- semantic retrieval is needed;
- embeddings are preferred;
- lexical retrieval is acceptable;
- the old EXP-0006 retriever was validated;
- Context Builder should scan the repository;
- any retrieval approach should be activated in production.

Those remain separate evidence-gated decisions.
