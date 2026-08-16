# Context Builder v2 — evidence-integrity experiment design

Date: 2026-08-15

Status: `RESEARCH / EVALUATION DESIGN — NOT ACTIVE AUTHORITY`

## 1. Decision this package makes

The next Context Builder experiment should **not** begin by choosing lexical, semantic, vector, graph, or model-based retrieval.

It should first establish whether MAPS can represent and score **trustworthy evidence** once a relevant source is in hand.

The experiment is therefore split:

```text
STAGE 1 — evidence-card integrity
known/frozen source set
→ candidate evidence cards
→ exact source / anchor / hash / temporal / boundary scoring

STAGE 2 — retrieval supplementation
frozen question + corpus
→ explicit-first control
vs candidate retrieval
→ same evidence-card integrity scorer
→ recall/abstention/cost comparison
```

A system that retrieves the right document but cites the wrong section, wrong version, stale hash, proposal as policy, or an unreturned “acceptable substitute” has failed Stage 1 even if its prose answer sounds correct.

## 2. Why this is the smallest useful next step

Merged Context Builder v1 already does one important thing well: it stays explicit-first. It projects task-linked sources and root authority, records hashes for available files, exposes missing/outside/directory boundaries, and explicitly reports that it did not scan the repository or use semantic retrieval.

Legacy evidence shows the next gap is not “we need embeddings.” The durable gap is evidence integrity:

- exact Markdown section or code-symbol anchors;
- exact source identity and hash;
- source-drift reporting;
- current versus historical attribution;
- source authority/proof role;
- positive evidence separated from negative boundaries;
- abstention when evidence does not establish the answer;
- paraphrase/vocabulary-shift robustness;
- frozen holdouts;
- acceptable-substitute credit only when the substitute was actually produced as evidence.

The old lexical claim-card implementation from `EXP-0006` is specifically **not** restored. Its decision was `REVISE`; the evidence-quality requirements survive, not its retrieval algorithm.

## 3. Frozen corpus shape

`work/evals/context-builder-evidence-integrity-v1.json` is self-contained and synthetic.

Each source includes:

```text
source id
logical path
version/status
exact content
sha256
```

The fixture deliberately includes same-path old/current versions so drift can be evaluated without filesystem or Git ambiguity.

Each question declares an expected outcome:

- `EVIDENCE`
- `ABSTAIN`
- `DRIFT_REPORTED`
- `UNKNOWN`

Evidence cards use:

```text
source_id
source_sha256
anchor:
  type
  value
proof_role
polarity
temporal_scope
```

The current corpus supports these anchor forms only:

- `MARKDOWN_SECTION`
- `CODE_SYMBOL`
- `DOCUMENT_STATUS`

That narrowness is deliberate. Add anchor types only when an experiment requires them.

## 4. Case classes

The v1 corpus includes:

1. **Direct current evidence** — obvious source/anchor.
2. **Mechanical guard** — exact code-symbol proof.
3. **Paraphrase** — same truth, different wording.
4. **Vocabulary shift** — meaning preserved while corpus terms change.
5. **Hard negatives** — related vocabulary but no supported answer.
6. **Temporal current** — retired evidence must not answer a current question.
7. **Temporal historical** — current evidence must not erase the historical question.
8. **Authority status** — proposal/overview must not be promoted into active authority.
9. **Negative boundaries** — source says what it does *not* prove.
10. **Source drift** — same logical path, different frozen/current hashes.
11. **Substitute credit** — alternate evidence is acceptable only if actually returned.
12. **Exact release anchor** — operator-visible acquisition-path claim requires the precise section.

## 5. Scoring contract

A future scorer should report dimensions separately rather than collapse everything into one optimistic score:

```text
case outcome accuracy
exact-source accuracy
anchor accuracy
source-hash accuracy
proof-role accuracy
negative-boundary accuracy
negative abstention accuracy
temporal/version accuracy
source-drift detection accuracy
acceptable-substitute precision
vocabulary-shift case accuracy
```

Recommended hard failures for Stage 1:

- invented source ID;
- source hash that does not match the cited frozen source;
- current claim supported only by retired/historical evidence;
- proposal represented as active authority;
- stale frozen source silently treated as current after drift;
- negative/no-answer case converted into unsupported positive evidence;
- substitute credit awarded to evidence not actually returned.

Do not hide those failures inside an aggregate recall score.

## 6. Stage 1 experiment — evidence projector

### Question

Given a known bounded source set, can a candidate build evidence cards with correct identity, anchors, hashes, temporal status, proof role, and boundaries?

### Control

No retrieval comparison is needed yet. The source set is supplied directly.

### Treatment

A candidate **evidence projector** consumes the frozen source set + question and emits the output contract defined by the corpus.

The projector may use deterministic parsing or a model, but it must not change the frozen truth data while being evaluated.

### Gate

Do not proceed to retrieval claims until Stage 1 is credible on:

- exact anchors;
- hashes/drift;
- temporal/authority cases;
- negative boundaries;
- abstention.

This is an integrity gate, not a production activation gate.

## 7. Stage 2 experiment — retrieval supplementation

Only after Stage 1:

### Control

Merged explicit-first Context Builder behavior plus only explicitly referenced sources.

### Candidate

A bounded retrieval supplement may be proposed. The algorithm is intentionally unspecified.

Possible candidates could later include query expansion, semantic/vector retrieval, symbol-aware search, or another method, but none is presumed superior.

### Frozen evaluation requirements

Keep the same questions/sources fixed and add task-level selection expectations where needed.

Required dimensions:

- useful source recall;
- false-positive source inclusion;
- hard-negative abstention;
- vocabulary/paraphrase performance;
- temporal/version correctness;
- evidence-card integrity;
- context bytes/tokens;
- authority mistakes.

A candidate does not win merely by retrieving more text.

## 8. Acceptable substitutes

Some questions have more than one genuinely valid proof source—for example, an active policy section and a mechanical code guard.

The scoring rule is strict:

```text
acceptable in theory
≠ retrieved
≠ proven
≠ credit
```

A substitute earns credit only if the candidate output actually identifies that source, correct hash, and correct anchor/proof role.

This directly prevents the over-credit failure identified in the legacy experiment review.

## 9. Drift semantics

A frozen evidence card is bound to a content hash.

When the current source at the same logical path has a different hash:

```text
frozen evidence
+ current source
+ hash mismatch
→ DRIFT_REPORTED
```

The system must not silently move the old anchor onto the new content.

A later source revalidation step may establish a new current card, but that is new evidence rather than mutation of the frozen historical card.

## 10. Authority and temporal semantics

The corpus deliberately separates:

- active authority;
- active mechanical guard;
- descriptive current documentation;
- proposal;
- retired historical evidence;
- historical context.

A citation is not ratification. A current question must not be answered by a retired rule merely because wording matches better. A historical question must not be rewritten as a current-policy question.

## 11. What this package does not build

No:

- semantic/vector index;
- embeddings dependency;
- knowledge graph;
- lexical claim-card retriever;
- repository crawler;
- policy database;
- durable evidence-card registry;
- automatic operational-memory promotion;
- model/provider runner;
- production Context Builder behavior change.

The frozen cards are evaluation truth/projections only.

## 12. Follow-on sequence

```text
this frozen package
→ independent review
→ Stage 1 evidence-projector prototype
→ score Stage 1
→ revise/freeze v2 only if the truth fixture itself is wrong
→ once integrity is credible, define Stage 2 explicit-first vs retrieval treatment
→ run frozen comparison
→ proposal
→ independent review/operator decision
→ only then consider production Context Builder v2 behavior
```

The corpus must not be edited merely to make a candidate score better. If a genuine fixture defect is found, supersede with a new version and preserve why the old frozen version changed.
