<!-- hpom: file: artifacts/experiments/task-fingerprint-source-holdout-2026-07-19.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: codex-lab-kiri -->
<!-- hpom: status: EXPERIMENT_COMPLETE -->
<!-- hpom: last_verified: 2026-07-19 -->
<!-- hpom: verified_against: TASK-258 frozen implementation, truth event 7344, generated index/packets, evaluator events 7384/7399/7414/7431/7448/7465/7482/7505/7532, focused tests, and MAP validators -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# TASK-258 Source-Fingerprint and Compound-Query Holdout

- owner: codex-lab-kiri
- truth-set author: helper-index-source-author-remi
- blinded evaluator: helper-index-source-eval-zomu
- corpus: completed TASK-100 through TASK-159
- date: 2026-07-19
- verdict: **source descriptions improved task discovery and helper evidence
  use, but source retrieval itself did not generalize enough for adoption**

## Executive result

This third experiment tested whether deterministic descriptions derived from
registered source files, bounded compound-query decomposition, and role-diverse
evidence slots repair the failures in TASK-257.

They repaired part of the problem, not all of it.

- On the fresh holdout, the algorithm placed 8 of 9 expected task labels in
  the top six: **88.9% task recall@6**, up from 77.8% in TASK-257.
- It exposed only 9 of 15 expected evidence paths: **60% source visibility**,
  slightly below TASK-257's 62.5%.
- The blinded evaluator selected 7 exact task labels among 10 selections:
  **70% task precision** and **77.8% task-label recall**.
- The evaluator selected 9 exact expected paths among 16 source selections:
  **56.25% exact-source precision** and **60% exact-source recall**.
- The evaluator found every expected source that the packet exposed: its
  9/15 exact-source recall exactly matched the algorithm's 9/15 visibility.
  The main evidence bottleneck was packet construction, not evaluator reading.
- The genuine negative query was correctly marked `no strong match` by the
  algorithm and `NO MATCH` by the evaluator. This is encouraging but is only
  one negative example, not a calibrated abstention result.
- Query packets ranged from 1,314 to 1,494 estimated tokens, with a 1,409-token
  median. All nine packets totaled 12,798 tokens versus about 383,615 tokens
  for the 243 readable unique task/source files represented by the corpus: a
  **96.7% total-context reduction**.
- Median delivery-to-response latency was 15 seconds; the range was 10 to 31
  seconds.
- The 60 tasks registered 336 output references to 210 unique paths. Forty-six
  paths were reused by multiple tasks, and 19 registrations to 13 unique paths
  no longer resolved.

Decision: **do not integrate this prototype** into startup, routing, Command
Center, or automatic agent workflows. The next measured baseline should
replace the hand-written scorer with a local SQLite FTS5/BM25 index, fuse
full-query and subquery ranks, and fix temporal attribution for shared mutable
sources before considering embeddings.

## 1. Frozen design and independence

The implementation and focused tests were frozen before the independent author
created the fresh truth set:

- implementation SHA-256:
  `e595c4ba05e9adf8e271bceaceea5da3dd50d3aa831c18910ca764f961a6e5d9`
- focused-test SHA-256:
  `69d2b28994ae0f05cb054d4c6cc213897215870879b923da1c4c7df020a91600`
- truth freeze: hcom event 7344 at 2026-07-19T18:43:47Z

Before the new truth existed, the known TASK-257 questions were used as a
development regression. That labeled regression reached 9/9 task visibility
and 16/16 evidence visibility. Those perfect known-query results are an upper
bound produced with visible development truth, **not holdout evidence**. No
retrieval code or ranking rule changed after the fresh author response.

The author read only TASK-100 through TASK-159 and registered outputs needed to
verify evidence. The separate evaluator received only one generated packet at
a time. It did not read the truth set, index, combined packet, task records,
source files, research, or prior experiments.

The author's initial packet ceiling was 1,250 estimated tokens. The frozen
renderer showed that the first packet required 1,466 tokens, so the
non-ranking delivery ceiling was transparently raised to 1,700 before the
evaluator started. The questions, expected answers, rankings, evidence slots,
and implementation remained unchanged. This exception is recorded in the
truth contract and is a packet-size result, not hidden tuning.

Durable materials:

- frozen truth:
  `artifacts/experiments/task-fingerprint-source-holdout-queries-2026-07-19.json`
- generated index and pre-evaluator metrics:
  `artifacts/experiments/task-fingerprint-source-holdout-2026-07-19.json`
- one-query packets:
  `artifacts/experiments/task-fingerprint-source-holdout-packets-2026-07-19/`
- combined audit packet:
  `artifacts/experiments/task-fingerprint-source-holdout-helper-packet-2026-07-19.md`
- known-query development regression:
  `artifacts/experiments/task-fingerprint-source-regression-2026-07-19.json`
- prototype and focused tests:
  `scripts/task_fingerprint_source_holdout.py` and
  `tests/test_task_fingerprint_source_holdout.py`
- independent helper records:
  `inbox/helpers/helper-index-source-author-2026-07-19.md` and
  `inbox/helpers/helper-index-source-evaluator-2026-07-19.md`

## 2. What the prototype indexed

The disposable index generated 376 task-linked source fingerprints for 60
task records. It did not accept owner-authored synonyms or answer fields.
Instead, it derived bounded descriptions mechanically:

- Markdown: headings and first substantive prose;
- Python: module docstring, symbols, and focused test names through the AST;
- JSON/task records: title, description, metadata, and acceptance criteria;
- HTML: title, headings, buttons, and labels;
- JavaScript and related text: comments and named symbols;
- YAML: keys and comments.

Each source retained its normalized path, hash, evidence role, task linkage,
and resolution state. Query processing used the full question plus at most
three deterministic clause/subquestion variants. Candidate tasks were the
union of these rankings. Packet construction attempted to give different
evidence roles to behavior, policy, and verification questions.

This structure is auditable and rebuildable. It remains a projection: the task
database and durable files retain authority.

## 3. Results

### 3.1 Comparison with TASK-257

The two experiments use different corpora and independently authored
questions, so changes are diagnostic rather than a controlled head-to-head
benchmark.

| Metric | TASK-257 typed-path holdout | TASK-258 source-fingerprint holdout |
|---|---:|---:|
| Corpus | 45 tasks | 60 tasks / 376 linked sources |
| Questions | 8 positive | 8 positive + 1 no-match |
| Expected task labels | 9 | 9 |
| Algorithm task recall@6 | 7/9 (77.8%) | 8/9 (88.9%) |
| Critical task misses | 2 | 1 |
| Expected-source visibility | 10/16 (62.5%) | 9/15 (60%) |
| Helper task precision | 7/10 (70%) | 7/10 (70%) |
| Helper task-label recall | 7/9 (77.8%) | 7/9 (77.8%) |
| Helper exact-source precision | 6/15 (40%) | 9/16 (56.25%) |
| Helper exact-source recall | 6/16 (37.5%) | 9/15 (60%) |
| Packet median | 1,106.5 tokens | 1,409 tokens |

Source descriptions improved the evaluator's evidence use substantially: exact
source recall rose 22.5 percentage points. They also improved first-stage task
recall by 11.1 points. But the source-selection stage itself exposed no larger
share of the strongest evidence, and packets became about 27% larger at the
median. The known-query regression therefore overpredicted generalization.

### 3.2 Query-level scoring

Strict scoring uses only the independent author's frozen task IDs and source
paths. Plausible but unlisted related tasks or evidence count as extra, not as
exact matches.

| Query | Expected tasks | Evaluator tasks | Exact sources | Result |
|---|---|---|---:|---|
| S1 research packet validation | TASK-104 | TASK-104 | 2/2 | exact |
| S2 RELEASED dependency rule | TASK-116 | TASK-116 | 2/2 | exact |
| S3 real-usage evidence audit | TASK-130 | TASK-130 | 1/1 | exact |
| S4 ProjectUpdater snapshot boundary | TASK-135, TASK-136 | TASK-136 | 0/2 | partial task, no exact source |
| S5 SQLite/JSON/graph mirror drift | TASK-143 | TASK-143 | 2/2 | exact |
| S6 quiet-agent recovery lifecycle | TASK-150 | TASK-110, TASK-158 | 0/2 | critical miss |
| S7 spend halt versus failure breaker | TASK-151 | TASK-151, TASK-155 | 1/2 | expected task plus extra |
| S8 local-helper dispatch fields | TASK-153 | TASK-153 | 1/2 | exact task, partial source |
| S9 secret scanning/redaction | no match | NO MATCH | n/a | correct abstention |

The evaluator produced the complete strict task set for five of eight positive
queries; including the correct no-match decision, six of nine query decisions
were exact. It selected at least one correct task for seven of eight positive
questions.

### 3.3 Abstention

S9 asked which historical task implemented automatic secret scanning and
redaction of MAP event records before commit. The corpus contains related event
validation and a later safety plan, but no such implementation in TASK-100
through TASK-159.

The algorithm returned `no_strong_match` with 18.18% query coverage and the
evaluator independently returned `NO MATCH` with high confidence. The positive
queries were not abstained from. This makes 9/9 correct positive-versus-abstain
decisions under the frozen threshold, but only **one** decision was a negative.
No production false-positive or risk/coverage claim is justified from n=1.

## 4. Context, storage, and latency

| Context/record | Estimated size |
|---|---:|
| 243 readable unique task/source files | about 383,615 tokens |
| Generated JSON index if read directly | about 100,315 tokens |
| Single packet, minimum | 1,314 tokens |
| Single packet, median | 1,409 tokens |
| Single packet, maximum | 1,494 tokens |
| Nine packets combined | 12,798 tokens |
| Evaluator's own estimate | about 12,692 tokens |

The nine-packet total is 96.7% smaller than loading the represented readable
files once. A median one-question packet is about 99.6% smaller. The generated
JSON is still far too large for an agent to read directly; a local retriever
must query it and send only the compact projection.

Delivery-to-response times for S1 through S9 were 31, 10, 10, 14, 18, 15, 15,
20, and 31 seconds. Median latency was 15 seconds. The one-packet protocol kept
scope observable and avoided a single very large prompt.

## 5. What failed and why

### 5.1 Evidence diversity was defined too rigidly

S7 and S8 each needed two complementary planning artifacts with the same broad
role. The role-diversity rule exposed one strong artifact, then forced a
different category that added less query coverage. Diversity should mean
*non-redundant proof*, not automatically different labels.

The next selector should score incremental query/subquestion coverage and
similarity to already selected evidence. It must allow two sources with the
same role when they answer different clauses.

### 5.2 Task ranking and source ranking are separate problems

S4 ranked both expected tasks in the top two but exposed neither frozen best
source. The evaluator could infer the ProjectUpdater ownership boundary from
plausible alternatives, yet could not identify the exact integration note or
user-facing export control. Better task recall did not automatically yield
better evidence recall.

Retrieval should rank unique sources globally for the query, then aggregate
them to task candidates. Selecting evidence only after a task is chosen can
hide the best source behind a related task or duplicated registration.

### 5.3 Deterministic extracts remain vocabulary-thin

S6's words—quiet agent, suspicion, nudge, reclaim, dashboard, and state
store—matched current interface and liveness files strongly enough to look
plausible, but the expected TASK-150 and both planning specs were absent. A
first-heading/first-prose extract did not preserve enough of the specific
recovery lifecycle.

Weighted full-text search over title, headings, symbols, bounded sections, and
task fields is a better next lexical baseline than adding more hand-written
token rules.

### 5.4 Confidence can be high on an incomplete packet

S4 was answered with high confidence even though one expected task and both
strongest sources were missing from the answer. Confidence reflected how
coherent the packet looked, not whether the unseen corpus contained stronger
evidence. Packets need a retrieval-confidence signal based on clause coverage,
ranking margin, source completeness, and path/temporal quality—not just a
reader's confidence after the packet has already hidden evidence.

### 5.5 Shared mutable paths create temporal leakage

The 60 task records contain 336 output registrations but only 210 unique paths;
46 are reused. `shared/current-state.md` is linked from 15 tasks and
`shared/decisions.md` from 14. The prototype fingerprints each file's **current**
content and copies that meaning into every linked historical task.

That can make an old task appear to contain text added months later. Reused
current-state files should not contribute ordinary historical task semantics
unless the index can identify the task-time hash or version. The durable model
needs three layers:

1. `source_documents`: one current fingerprint per unique path;
2. `task_source_links`: the fact that a task registered that path;
3. `task_evidence_snapshots`: immutable artifact or task-time version/hash,
   when known.

Current shared sources remain valid for present-state questions, but must be
labeled and ranked with current-time semantics. This data-model correction is
more important than another round of weight tuning.

### 5.6 Path drift must stay visible

Nineteen registered references, covering 13 unique paths, no longer resolved.
They include legacy `/home/home/Projects/CommandCenterUI/...` paths and missing
historical handoffs/artifacts. Directory outputs remain legitimate bundles and
were not counted as missing. A future index should preserve broken-path state,
show it in match reasons, and avoid silently treating incomplete historical
evidence as complete.

## 6. Research-backed next architecture

The accompanying research review concludes that MAP is a small,
heterogeneous, evidence-sensitive retrieval problem. The next prototype should:

1. Build a disposable local SQLite FTS5 index with separate weighted task,
   source-title, summary, symbol, path, and role fields.
2. Compare `unicode61`, Porter stemming, and a separate trigram/path channel.
3. Retrieve the full question and bounded deterministic subqueries
   independently.
4. Fuse ranks using reciprocal-rank fusion rather than adding unlike raw
   scores.
5. Select evidence by incremental clause coverage and non-redundancy, while
   allowing complementary same-role sources.
6. Separate current source documents, task/source links, and historical
   snapshots; downweight shared mutable current content for historical task
   attribution.
7. Calibrate abstention on multiple fresh negative queries and report the
   recall-versus-false-positive tradeoff.
8. Add a local semantic channel only if the frozen FTS5/RRF baseline still has
   lexical misses, and score its incremental benefit separately.

SQLite 3.45.1 in this environment has FTS5 enabled and passed in-memory
Porter/BM25 and trigram probes, so the next lexical experiment requires no new
package or external service.

## 7. Adoption gate

TASK-258 does not justify operational integration. A later candidate should
meet a written gate on at least two fresh heterogeneous holdouts, including:

- no critical task misses in the adopted scope;
- at least 90% expected-source visibility and exact-source recall;
- separately reported compound-query completion;
- several real negatives with a bounded false-positive rate;
- explicit current-versus-historical attribution;
- deterministic rebuild, path-health reporting, and graceful failure;
- bounded packet context and local query latency;
- independent review before startup, router, or UI use.

These values are proposed experiment gates, not current performance.

## 8. Monitoring and scope adherence

- Author `helper-index-source-author-remi` returned the truth at event 7344,
  stayed within TASK-100 through TASK-159 and their registered outputs, and was
  stopped after its bounded assignment.
- Evaluator `helper-index-source-eval-zomu` returned S1-S9 at events 7384,
  7399, 7414, 7431, 7448, 7465, 7482, 7505, and 7532.
- Event and terminal monitoring showed one authorized packet read at a time.
  Apart from its required evaluator protocol note, it reported no
  outside-packet access.
- The evaluator was stopped and its WezTerm pane closed after completion.
- No runtime, router, startup, Command Center, external service, or canonical
  task authority was altered by the experiment.

## 9. Final decision

Source-level fingerprints are worth keeping as a representation idea, but the
current scorer and evidence-slot heuristic are retired as experiment code.
The useful outcome is a sharper decomposition of the problem:

- sparse task retrieval is improving;
- exact evidence selection is now the dominant measured bottleneck;
- compound questions need coverage-aware fusion;
- abstention is promising but under-tested;
- temporal attribution must be modeled before historical retrieval is trusted.

Proceed to a bounded FTS5/BM25 plus reciprocal-rank-fusion experiment with the
same independent-author and blinded-evaluator protocol. Do not integrate until
the adoption gate is met and separately reviewed.
