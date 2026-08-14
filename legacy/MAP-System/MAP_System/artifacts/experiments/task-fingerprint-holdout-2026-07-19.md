<!-- hpom: file: artifacts/experiments/task-fingerprint-holdout-2026-07-19.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: codex-lab-kiri -->
<!-- hpom: status: EXPERIMENT_COMPLETE -->
<!-- hpom: last_verified: 2026-07-19 -->
<!-- hpom: verified_against: TASK-257 frozen truth event 7014, generated index/packets, evaluator events 7055/7066/7081/7097/7113/7129/7147/7171, focused tests, and task-mirror validators -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# TASK-257 Uncurated Task-Fingerprint Holdout

- owner: codex-lab-kiri
- truth-set author: helper-index-author-bono
- blinded evaluator: helper-index-eval-mono
- mode: read-only, frozen older-corpus experiment
- date: 2026-07-19
- verdict: **the compact-packet pattern remains useful, but the automatic
  lexical index failed the adoption gate**

## Executive result

TASK-256 showed that a compact task index can save an agent from loading broad
history. TASK-257 tested the harder question: can the index work without
owner-written semantic hints, on older tasks, with independently authored
paraphrases and a new typed evidence ranker?

Not reliably enough yet.

- The algorithm retrieved 7 of 9 expected tasks in the top six: **77.8%
  recall@6**, with two critical misses.
- The blinded helper selected 7 correct task IDs among 10 selections: **70%
  task precision**. It produced the complete expected task set for 6 of 8
  questions.
- The packets exposed only 10 of 16 expected best-evidence paths: **62.5%
  evidence visibility**.
- The helper selected 6 exact expected evidence paths among 15 selections:
  **40% exact-source precision** and **37.5% exact-source recall**.
- All eight packets stayed below the 1,200-token ceiling. A median query packet
  was about 1,107 tokens versus about 19,885 tokens for all 45 raw task records,
  a **94.4% context reduction**.
- The two wrong/partial answers were both reported with medium confidence; all
  six exact task-set answers were high confidence. Uncertainty reporting was
  therefore directionally well calibrated.
- Both helpers stayed inside their read-only scopes and were stopped when their
  bounded work ended.

The negative result is specific and actionable. Deterministic task-level
lexical fingerprints are too thin for some paraphrases, a flat query cannot
reliably recover two distinct historical causes, and evidence-role labels do
not provide enough information to rank the best source inside a task.

Decision: continue one narrower experiment on **source-level fingerprints,
evidence diversity, and compound-query decomposition**. Do not add this index
to startup, routing, Command Center, or automatic agent workflows.

## 1. Independence and frozen design

The experiment separated authorship, generation, and evaluation:

1. The owner fixed a corpus of 45 completed task records: TASK-160 through
   TASK-205, excluding non-completed TASK-186.
2. A fresh visible helper read those task records and only their registered
   outputs. It authored eight paraphrased user questions, nine expected task
   IDs, and sixteen expected evidence paths.
3. The truth set was frozen at hcom event 7014 before the evaluator started.
4. Fingerprints were generated mechanically from task records. No result,
   concept, synonym, or expected-answer field was owner-curated.
5. A different fresh visible helper received one compact packet at a time. It
   could not read the combined packet, JSON index, truth set, task records,
   named evidence, or search the repository.
6. The owner preserved the generated ranking before scoring. The two misses
   were not tuned away after the truth became visible.

Durable inputs and outputs:

- frozen truth:
  `artifacts/experiments/task-fingerprint-holdout-queries-2026-07-19.json`
- generated index and pre-evaluator metrics:
  `artifacts/experiments/task-fingerprint-holdout-2026-07-19.json`
- individual evaluator packets:
  `artifacts/experiments/task-fingerprint-holdout-packets-2026-07-19/`
- combined audit copy:
  `artifacts/experiments/task-fingerprint-holdout-helper-packet-2026-07-19.md`
- ranker prototype: `scripts/task_fingerprint_holdout.py`
- focused tests: `tests/test_task_fingerprint_holdout.py`
- helper scope records:
  `inbox/helpers/helper-index-author-2026-07-19.md` and
  `inbox/helpers/helper-index-holdout-evaluator-2026-07-19.md`

## 2. What changed from TASK-256

TASK-256 used owner-curated semantic fields on 16 of 37 task fingerprints and
took the first three registered source paths. TASK-257 removed the semantic
curation and added a second retrieval stage for evidence.

The evidence ranker classified registered paths as:

- task scope;
- implementation;
- test;
- review;
- release;
- decision;
- current state;
- outcome;
- research;
- guide;
- general artifact or bundle.

It then inferred what the query appeared to ask for, boosted matching roles
and filename/path terms, and showed at most two evidence choices per candidate.
Each choice told the evaluator what that evidence class could normally prove.

This made the packet more explicit, but the role text was generic. It could say
that a test proves behavior; it could not say whether that particular test
proved *this query's behavior*.

## 3. Results

### 3.1 Comparison with TASK-256

The corpora and questions differ, so this table is diagnostic rather than a
controlled head-to-head benchmark.

| Metric | TASK-256 curated pilot | TASK-257 uncurated holdout |
|---|---:|---:|
| Corpus | 37 recent tasks | 45 older tasks |
| Questions | 10 owner-authored | 8 independently authored |
| Expected task labels | 16 | 9 |
| Algorithm task recall@6 | 16/16 (100%) | 7/9 (77.8%) |
| Critical task misses | 0 | 2 |
| Helper task precision | 16/16 (100%) | 7/10 (70%) |
| Complete query task sets | 10/10 (100%) | 6/8 (75%) |
| Expected-source visibility | 11/16 (68.75%) | 10/16 (62.5%) |
| Helper exact-source recall | 11/16 (68.75%) | 6/16 (37.5%) |
| Helper exact-source precision | 11/19 (57.9%) | 6/15 (40%) |
| Per-query packet range | 951–1,117 tokens | 1,061–1,196 tokens |

The first pilot's perfect task score did not generalize. Typed roles also did
not repair source selection: exact-source recall fell by 31.25 percentage
points in this harder holdout.

### 3.2 Query-by-query task and evidence outcome

| Query | Expected tasks | Helper selection | Exact expected evidence selected | Confidence |
|---|---|---|---:|---|
| H1 disposable replay/read model | TASK-173 | TASK-172, TASK-170 | 0/2 | Medium |
| H2 nested Related-files resolution | TASK-179 | TASK-179 | 0/2 | High |
| H3 capture redaction | TASK-191 | TASK-191 | 1/2 | High |
| H4 atomic review claims | TASK-199 | TASK-199 | 1/2 | High |
| H5 bounded halt authority | TASK-201 | TASK-201 | 1/2 | High |
| H6 ProjectUpdater backup/restore | TASK-205 | TASK-205 | 1/2 | High |
| H7 cost/yield proxies | TASK-190 | TASK-190 | 1/2 | High |
| H8 active session plus resume timeout | TASK-187, TASK-195 | TASK-187, TASK-198 | 1/2 | Medium |

The algorithm's two task misses directly explain the two helper task failures:

- H1 did not place TASK-173 in the top six. Its top six were TASK-170,
  TASK-174, TASK-189, TASK-181, TASK-190, and TASK-172.
- H8 found TASK-187 but omitted TASK-195. TASK-198 looked like a plausible
  substitute in the packet, so the helper chose it.

Evidence ranking had a separate failure. H2 found the correct task and exposed
the expected focused test, but the helper chose a generic simulation-probe
artifact instead. Across all questions, the helper chose only 6 of the 10
expected paths that were actually visible. Visibility alone is therefore not
enough; each evidence option needs query-specific meaning.

## 4. Context, storage, and response time

| Context/record | Estimated tokens |
|---|---:|
| All 45 raw task JSON records | 19,885 |
| Generated JSON index stored on disk | 31,898 |
| Single query packet, minimum | 1,061 |
| Single query packet, median | 1,106.5 |
| Single query packet, maximum | 1,196 |
| Eight-query combined audit packet | 8,992 |
| Evaluator's own total packet estimate | about 8,894 |

The context saving remains real when a local tool searches first and sends one
packet. The generated index itself is still larger than the raw task records,
because it repeats paths, hashes, and field names. The index must remain a
backend projection; asking an agent to read it would defeat its purpose.

Delivery-to-response latency was 28, 19, 13, 12, 15, 11, 15, and 31 seconds
for H1 through H8. Median latency was 15 seconds; maximum latency was 31
seconds. One-query delivery avoided the display truncation seen in TASK-256.

## 5. Failure analysis

### 5.1 Task records do not contain enough semantic vocabulary

The uncurated fingerprint used task title, description, project/workstream,
status, and registered path names. H1's natural phrasing—rebuild a disposable
local view, query by task/agent/trace, and detect canonical drift—did not share
enough high-weight vocabulary with TASK-173. Recent curated concepts had hidden
this weakness in TASK-256.

The first repair should not be manual synonyms. A source-level fingerprint can
derive a short sentence from a file title, heading, module docstring, or test
name and attach it to the task without requiring the agent to load the file.

### 5.2 A flat query loses compound historical causes

H8 intentionally asked for two distinct fixes behind one operational symptom:
TASK-187 handled an already-live target; TASK-195 handled a hung resume call.
Flat lexical ranking found the first but not the second.

This needs query decomposition or a lightweight multi-hop relation, not a
larger top-N list. The retriever should split distinct causes, retrieve each
subquestion, then union and rerank the candidates.

### 5.3 Evidence roles are categories, not relevance summaries

The ranker heavily boosted tests for questions containing words such as
"prove", "corrected", or "validation". A task with several tests could expose
an arbitrary high-scoring test while hiding the implementation or the focused
test. H2 demonstrated this directly.

Role labels still matter, but each source also needs a tiny content-derived
fingerprint. Evidence selection should optimize both relevance and proof
diversity, rather than simply taking the two highest role scores.

### 5.4 Task intent and completion evidence remain different

A task JSON record is authoritative for title, goal, owner, status, and
registered outputs. It is not sufficient by itself to prove that code behaved
as intended, a review passed, or an outcome occurred. Several helper answers
used task JSON as their second source because the better implementation/current
state source was hidden.

The packet should deliberately reserve evidence slots based on the question,
for example one scope/decision source, one implementation source, and one
verification/outcome source, rather than letting two similar artifacts crowd
out a different kind of proof.

### 5.5 Historical path drift is visible and useful

All 16 frozen expected paths resolved. The wider 45-task index exposed broken
registered outputs on TASK-181, TASK-182, TASK-195, and TASK-203, including
legacy `/home/home/Projects/CommandCenterUI/...` locations and missing older
artifacts. Broken paths did not determine the two task misses, but a production
retriever must continue showing a stale/broken warning rather than silently
treating an incomplete fingerprint as complete.

## 6. Recommended next experiment

Keep the deterministic local search and hard one-query token ceiling. Change
the retrieval unit and packet composition:

1. Create a disposable **source fingerprint** for every registered output:
   normalized path, evidence role, task linkage, lifecycle/hash state, and one
   short content-derived description from a heading, docstring, metadata block,
   or test name.
2. Rank sources by query overlap with that description, not only path and role.
3. Fill diverse proof slots appropriate to the query: intent/decision/current
   state, implementation, and verification/review/outcome.
4. Detect compound phrasing, run bounded subqueries, and union the candidate
   tasks before final ranking.
5. Add relation boosts only where durable evidence supports them: shared source,
   dependency, supersession, or trace linkage.
6. Repeat with a fresh author and evaluator, retain `no strong match`, and add
   at least one negative query whose correct answer is no task.

Do **not** add embeddings yet. The next measured bottlenecks are source-level
meaning and multi-part retrieval. Test the simpler lexical repair before adding
an opaque service, model dependency, or larger stored representation.

## 7. Monitoring and scope adherence

- Author helper launched visibly as `helper-index-author-bono`, returned the
  frozen truth at event 7014, and was stopped.
- Evaluator helper launched visibly as `helper-index-eval-mono` and received
  H1 through H8 only after the prior answer arrived.
- Evaluator responses are preserved at hcom events 7055, 7066, 7081, 7097,
  7113, 7129, 7147, and 7171.
- Event and terminal monitoring showed only the currently authorized packet
  read. No combined packet, index, truth set, task/evidence source, broad
  repository search, write, or task-state mutation was observed.
- Both helper notes are marked complete and both terminal panes were closed.

Scope adherence: **PASS**.

## 8. Adoption decision

**Continue a focused experiment; do not integrate the current index.**

The compact retrieval boundary is worth preserving because it reduced normal
query context by about 94%. The current automatic contents are not trustworthy
enough: a 22.2% task-label miss rate and 62.5% exact-evidence miss rate would
cause agents to overlook relevant prior work or cite weaker proof. Source-level
fingerprints and compound-query decomposition are the smallest next changes
that directly address the observed failures.

## Verification

- `python -m py_compile` passed for the prototype and focused tests.
- `python -m unittest MAP_System.tests.test_task_fingerprint_holdout -v`:
  7/7 passed.
- Frozen pre-evaluator metrics: task recall@6 7/9, evidence visibility 10/16.
- Blinded helper metrics: task precision 7/10, exact-source precision 6/15,
  exact-source recall 6/16.
- Task mirrors and task graph were validated after TASK-257 submission.
- Event validation reported zero errors. It preserved one new warning for an
  initially noncanonical `TASK_SUBMITTED` closeout label; a following canonical
  `SUBMISSION` event explicitly corrects the label without rewriting the
  append-only log.
- No new Emergence card was opened because this experiment directly extends
  TASK-255, TASK-256, INS-0027, and INS-0028 rather than introducing a separate
  insight.
