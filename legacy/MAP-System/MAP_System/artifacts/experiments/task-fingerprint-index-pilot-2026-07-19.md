<!-- hpom: file: artifacts/experiments/task-fingerprint-index-pilot-2026-07-19.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: codex-lab-kiri -->
<!-- hpom: status: EXPERIMENT_COMPLETE -->
<!-- hpom: last_verified: 2026-07-19 -->
<!-- hpom: verified_against: TASK-256 frozen corpus/spec, generated index/packet, test suite, hcom helper events 6894/6915/6946, and primary-source spot checks -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# TASK-256 Task-Fingerprint Retrieval Pilot

- owner: codex-lab-kiri
- evaluator: helper-index-neko, fresh visible Codex helper
- mode: read-only, frozen-corpus experiment
- date: 2026-07-19
- verdict: **promising task retrieval; source ranking needs another iteration**

## Executive result

The compact lexical index worked very well for finding the **right prior
tasks** and only moderately well for finding the **best primary evidence inside
those tasks**.

- Deterministic retrieval placed all 16 expected task IDs in the top six:
  **100% recall@6, zero critical misses**.
- The fresh helper selected exactly those 16 expected tasks and no others:
  **100% task-selection precision** across 10/10 queries.
- Each single-query candidate packet stayed between **951 and 1,117 estimated
  tokens**, below the frozen 1,200-token ceiling.
- The helper stayed within scope, used no broad search, wrote nothing, and
  returned its first pass in about **98 seconds**.
- Only **11 of 16 expected best-evidence paths (68.75%)** were visible in the
  candidate packet. The naive "first three source paths" rule hid five better
  sources.
- Under the deliberately strict frozen-source metric, the helper selected 11
  exact expected paths among 19 selections: **57.9% source precision** and
  **68.75% source recall**. The other selections were generally relevant but
  weaker or less complete evidence.

Conclusion: the indexing approach is viable enough to continue testing. It is
not ready for startup, Command Center, or automatic agent use. The next run
should preserve lexical task ranking but add query-aware evidence-role ranking,
use one query per retrieval call, and test a genuinely uncurated holdout.

## 1. Frozen design

The truth set was written before the helper received the packet:

- 37 recent task fingerprints;
- 10 realistic historical questions;
- 16 expected task IDs;
- 16 expected primary-source paths;
- top-six candidate limit;
- 1,200 estimated-token ceiling per query;
- two source expansions per query;
- explicit recall, precision, latency, context, staleness, and scope metrics.

The corpus covered ClearFront delivery and engine work, E/I and discovery,
local-helper qualification, Command Center deployment/UI work, safety-policy
repair, and the new indexing design. Sixteen relevant fingerprints received
short owner-curated result/concept fields; the remaining 21 used deterministic
task-record extraction.

This curation makes the run a test of the **fingerprint/search design**, not a
fair test of fully automatic fingerprint generation.

Durable inputs and outputs:

- frozen spec/truth:
  `artifacts/experiments/task-fingerprint-index-pilot-queries-2026-07-19.json`
- generated index:
  `artifacts/experiments/task-fingerprint-index-pilot-2026-07-19.json`
- helper packet:
  `artifacts/experiments/task-fingerprint-index-helper-packet-2026-07-19.md`
- generator/search prototype: `scripts/task_fingerprint_pilot.py`
- focused tests: `tests/test_task_fingerprint_pilot.py`
- helper scope record: `inbox/helpers/helper-index-neko-2026-07-19.md`

## 2. What the prototype did

The prototype generated one disposable fingerprint per task containing:

- task, project, workstream, status, goal, and result;
- changed/output paths;
- up to eight concepts;
- optional unexpected finding or friction;
- resolvable source references and source hashes;
- broken-output warnings and curation provenance.

Lexical scoring weighted title, concepts, result, surprises/friction, paths,
workstream, project, and goal. The agent did not load the JSON index. For each
question, the prototype returned at most six compact candidates with match
reasons and up to three source choices.

The helper received only the rendered result packet. It was explicitly denied
the JSON index, truth file, task files, primary artifacts, and repository
search during the selection pass.

## 3. Retrieval results

### 3.1 Algorithm and helper task selection

| Metric | Result |
|---|---:|
| Expected task IDs | 16 |
| Expected IDs in algorithm top six | 16/16 (100%) |
| Critical misses | 0 |
| Total candidates shown | 60 |
| Strict candidate precision@6 | 16/60 (26.7%) |
| Helper-selected task IDs | 16 |
| Correct helper task selections | 16/16 (100%) |
| Queries answered | 10/10 |
| Reported task-selection confidence | High for all 10 |

The lower candidate precision is not itself a failure: top-six retrieval is a
recall stage. The fresh helper correctly discarded all 44 distractors. More
important, every expected pair occupied the top two positions, and every
single expected task occupied rank one. The queries were therefore not close
calls for this curated corpus.

### 3.2 Query-by-query outcome

| Query | Expected task selection | Helper task selection | Exact expected sources selected |
|---|---:|---:|---:|
| Q1 replacement/undo exploit | 2 | 2 | 2/2 |
| Q2 extraction and parity gate | 2 | 2 | 1/2 |
| Q3 headless engine seam | 2 | 2 | 1/2 |
| Q4 Pi terminal vs hcom | 2 | 2 | 1/2 |
| Q5 E/I recall and truth set | 2 | 2 | 1/2 |
| Q6 deployment-source parity | 2 | 2 | 2/2 |
| Q7 destructive false positive | 1 | 1 | 1/1 |
| Q8 serial UI consolidation | 1 | 1 | 0/1 |
| Q9 ClearFront prototype continuity | 1 | 1 | 1/1 |
| Q10 fingerprint/index design | 1 | 1 | 1/1 |

The task-level answer was perfect. The source-level misses were systematic,
not random: evidence paths later in a task's registered output list were
truncated from the packet.

### 3.3 Missing best-evidence paths

The packet hid these five frozen expected sources even though it found the
correct task:

- TASK-208's dedicated skeleton-parity note;
- TASK-214's combat-parity note;
- the Pi communication guide;
- TASK-226's complete known-findings/truth-set artifact;
- TASK-254's final reconciliation packet.

The helper compensated with task JSON, source code, a release checklist, or an
adjacent adjudication artifact. Those choices were relevant, but they were not
always sufficient to verify completion or inspect the exact evidence requested.

This is the pilot's main negative result. A task fingerprint needs **typed and
ranked evidence roles**, not an arbitrary first-N slice of output paths.

## 4. Token and size effects

| Context/record | Estimated tokens |
|---|---:|
| All 37 raw task JSON records | 19,253 |
| Generated JSON index stored on disk | 26,451 |
| Single query packet, minimum | 951 |
| Single query packet, median | 1,060 |
| Single query packet, maximum | 1,117 |
| Ten-query helper packet | 10,794 |
| Helper's own first-pass estimate | about 10,480 |
| Three-source confirmation pass | about 2,517 |

A normal one-query retrieval used roughly **94.5% less context** than loading
all 37 task records. The artificial 10-query batch was about **44% smaller**
than the raw task-record corpus.

However, the generated JSON index itself was **larger** than the task records.
Hashes, paths, metadata, and repeated field names caused that growth. This is
not a context problem if a local search tool queries the index and sends only a
small packet. It becomes a serious failure if an agent is told to read the
whole index.

The agent-facing fingerprint semantic content was shorter than the proposed
100–180 words: 53–101 words, median 72. The strong task recall suggests the
shorter form is worth retaining for the next test.

Monitoring also exposed a batch-delivery issue: the helper's first display was
truncated, so it read a later range of the same packet to recover Q5–Q10. No
scope breach occurred, but production retrieval should send one query response
at a time, not a ten-query omnibus document.

## 5. Bounded helper confirmation

After the first report, the helper received one authorized confirmation pass
over the ambiguous Q5 and Q8 selections.

### Q5 — E/I recall and frozen discovery truth

The selected sentinel pilot directly proved 1/4 (25%) recall and named the
positive discoveries/corrections that transition-only detection missed. The
selected Discovery adjudication proved that the known set was frozen before
the helper ran and demonstrated value beyond it.

But the adjudication did not enumerate the full truth set. The hidden
`clearfront-discovery-known-findings-2026-07-17.md` path was still needed to
audit the actual frozen contents. The selected pair supported the answer but
was not fully self-contained evidence.

### Q8 — which record consolidated rapid UI changes?

TASK-254.json was adequate to answer **which record** and to state its declared
scope: consolidate TASK-241–248 into one final review boundary.

It was not adequate to prove that consolidation and verification were
completed because the task remained SUBMITTED. That claim requires the hidden
reconciliation artifact and its parity/test evidence.

This confirms a useful retrieval distinction:

- a task record is primary evidence for intent, scope, ownership, and status;
- a delivery/review/test artifact is primary evidence for what actually
  happened and whether it passed.

## 6. Monitoring and scope adherence

- Helper launched visibly in a managed WezTerm tab as `helper-index-neko`.
- Frozen packet delivered at hcom event 6894.
- Initial report received at event 6915, about 98 seconds later.
- Confirmation report received at event 6946.
- Terminal/events showed only `cat` and a bounded `sed` range on the packet for
  the first pass.
- Confirmation showed exactly the three authorized file reads.
- No repository search, JSON-index read, truth-file read, link following,
  source mutation, or task-state mutation occurred.
- Two attempted acknowledgements failed because the triggering messages were
  `inform`, then the helper continued correctly. This added minor coordination
  noise but did not affect retrieval results.

Scope adherence: **PASS**.

## 7. Staleness and path health

- All 37 task records were present.
- All 16 frozen expected source paths resolved.
- One fingerprint, TASK-237, carried three unresolved registered output paths.
  Its task record remained resolvable and the packet exposed a source warning.

This validates the value of visible broken-reference state, while showing that
path normalization for external Command Center checkouts needs separate care.

## 8. Interpretation and limits

This result is encouraging but is an upper-bound sample:

1. Sixteen of 37 fingerprints were curated with concepts closely aligned to
   the frozen questions.
2. The same owner designed the queries, truth set, and curation before the
   helper saw them. Freezing prevents helper leakage, but not designer bias.
3. The helper was a strong fresh Codex model, so this does not establish that a
   smaller local model can disambiguate the same candidate set.
4. The corpus was recent and internally well linked.
5. The helper selected source paths but opened only three during the separate
   confirmation pass.
6. No paraphrase, misspelling, old-task, cross-domain analogy, or completely
   uncurated holdout challenge was included.

The pilot proves that compact lexical retrieval can work under a hard context
budget. It does not yet prove general historical memory recall.

## 9. Recommended second iteration

### Keep

- deterministic local lexical retrieval;
- short 50–100 word semantic fingerprints;
- top-six recall stage with match reasons;
- explicit `no strong match` option;
- one-query 1,200-token ceiling;
- source hashes and stale/broken warnings in backend storage;
- fresh-agent, frozen-truth evaluation.

### Fix before the next run

1. Classify source references by evidence role: task record, review, test,
   delivery note, decision, current state, implementation source, release
   checklist, or historical note.
2. Rank source paths against the query instead of taking the first three.
3. Make the packet say what each source can prove: intent/scope, implementation,
   verification, approval, release, or later outcome.
4. Keep hashes and bulky provenance out of the agent-facing packet.
5. Deliver one query at a time to avoid display truncation and cumulative
   context growth.
6. Normalize external/workspace-relative paths and retain explicit broken-link
   warnings.

### Next experiment

Run a holdout on older, uncurated tasks using paraphrased questions authored by
a different evaluator. Freeze the truth set before generation. Compare:

- mechanical-only fingerprints;
- owner-curated fingerprints;
- lexical retrieval with typed evidence ranking;
- a no-index `rg`/task-record baseline.

Do not add embeddings yet. Lexical task recall was already perfect in this
sample; the immediate measured weakness is evidence ranking, not semantic task
matching.

## 10. Adoption decision

**Continue experimentation; do not integrate.**

The design passed its first feasibility question: a fresh agent can identify
the correct prior task from small ranked packets without loading broad history.
It failed the stronger evidence-selection standard often enough to block
adoption. The next iteration should repair that exact weakness and challenge
the system with an uncurated holdout before any startup, Command Center, or
automatic workflow integration is proposed.

## Verification

- `python -m py_compile` passed for prototype and tests.
- `python -m unittest MAP_System.tests.test_task_fingerprint_pilot -v`:
  5/5 passed.
- Frozen algorithm score: recall@6 1.0, 0 critical misses.
- Task mirrors validated during the run.
- Helper monitoring evidence: hcom events 6894, 6915, 6946 and the completed
  helper note.
