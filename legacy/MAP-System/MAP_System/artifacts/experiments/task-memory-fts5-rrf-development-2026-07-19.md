<!-- hpom: file: artifacts/experiments/task-memory-fts5-rrf-development-2026-07-19.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: codex-lab-kiri -->
<!-- hpom: status: DEVELOPMENT_BASELINE_COMPLETE -->
<!-- hpom: last_verified: 2026-07-19 -->
<!-- hpom: verified_against: TASK-259 script/test hashes, nine focused tests, known TASK-257/TASK-258 development truth, generated metrics JSON, and MAP validators -->
<!-- hpom: confidence: HIGH_FOR_MEASURED_DEVELOPMENT_RESULTS_LOW_FOR_GENERALIZATION -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# TASK-259 Temporal-Safe FTS5/RRF Development Baseline

- owner: codex-lab-kiri
- mode: local, disposable, known-query development regression
- date: 2026-07-19
- verdict: **freeze for a fresh holdout; do not integrate**

## Executive result

TASK-259 replaced the hand-written lexical counter with a local SQLite FTS5
baseline and fixed a more fundamental data-model problem: current source
content is now stored once, separately from the historical tasks that
registered the path.

On the two **known** truth sets used for development:

- TASK-257 task recall@6 improved from 7/9 to **9/9 (100%)**.
- TASK-257 strongest-source visibility improved from 10/16 to **13/16
  (81.25%)**.
- TASK-258 task recall@6 remained **8/9 (88.9%)**.
- TASK-258 strongest-source visibility improved from 9/15 to **13/15
  (86.67%)**.
- Both known compound queries returned every expected task in the top six.
- All positive questions received candidate sets, and TASK-258's negative
  question retained `no_strong_match`.
- The 45-task corpus built in 579 ms into an 823,296-byte database; median
  query time was 17.5 ms.
- The 60-task corpus built in 490 ms into an 897,024-byte database; median
  query time was 13.7 ms.

These are useful engineering results, not evidence of generalization. The
owner could see both truth sets while developing field weights, temporal
weights, clause splitting, and evidence-selection heuristics. The
implementation is now frozen for a separate fresh-author/blinded-evaluator
holdout.

Frozen hashes:

- implementation:
  `edd0b53ab6d9c480360e19f4d14d667f459fcaa3155748a9bd96e741b70cca27`
- focused tests:
  `58df22f41258c3cea27d48ddbf413bf1b0c9c63eead9016b58008718a677949f`
- generated development metrics:
  `3148c0e837975cb970f56da5d133cd01e9399048b7235bbcfcc66856bd5af6a5`

## 1. Architecture

```text
task JSON mirrors                         registered current paths
       |                                          |
       v                                          v
task_documents + task_fts        source_documents + source_fts/path_fts
       |                                          |
       +------------ task_source_links -----------+
                            |
        full query + bounded deterministic clauses
                            |
       independent task/source/path ranked channels
                            |
                reciprocal rank fusion
                            |
          coverage-aware evidence selection
                            |
       task candidates + explicit temporal labels
```

The database is created in a temporary directory for benchmarks and discarded.
It has no authority and no availability dependency for MAP.

### 1.1 Retrieval channels

- `task_fts`: Porter-tokenized task title, goal, acceptance criteria, output
  path terms, project, and workstream. BM25 gives title the highest weight.
- `source_fts`: Porter-tokenized source title, bounded summary, code symbols,
  path terms, and evidence role.
- `path_fts`: trigram filename/identifier matching for code names, partial
  identifiers, and minor lexical variation.
- full question plus at most three deterministic clause/sentence variants;
- reciprocal-rank fusion with `k=60`, so raw BM25 and trigram scores are never
  added as if they shared a scale.

### 1.2 Evidence selection

After task retrieval, the selector reranks only sources linked to that task.
It combines:

- query-term coverage;
- lower-weight overlap with the selected task's mechanically derived title and
  goal, which helps identify the relevant output without inventing synonyms;
- source RRF rank;
- evidence-role demand;
- incremental term coverage after the first source;
- test/implementation and review/implementation complementarity;
- generic functional signals for validation files and user-facing HTML.

Unlike TASK-258, it does not require every selected source to have a different
broad role. Two planning artifacts can both be selected when they cover
different clauses.

## 2. Temporal attribution model

The prototype creates exactly one `source_documents` row per normalized path
and separate `task_source_links` rows. Source text is never copied into the
task FTS document.

| Temporal mode | Meaning | Source-to-task RRF weight |
|---|---|---:|
| `task_snapshot` | Current task JSON record; authoritative scope/status mirror, but not proof of implementation | 0.10 |
| `current_unique` | Current content of a path linked to one corpus task; historical version not proven | 0.25 |
| `current_shared` | Current content linked by multiple tasks; high attribution risk | 0.05 |
| `unresolved` | Registered path is currently absent | 0.00 |

Direct task-field channels retain weight 1.0. This keeps source content as a
bounded recall fallback and prevents tasks with many registered outputs from
winning merely because they have more sources.

This is intentionally conservative. A current unique implementation file may
still have changed after task completion, so it is labeled `current_unique`,
not a historical snapshot. Only a future recorded task-time hash or immutable
version can support stronger attribution.

### 2.1 Corpus shape

| Measure | TASK-257 corpus | TASK-258 corpus |
|---|---:|---:|
| Tasks | 45 | 60 |
| Unique source documents, including task records | 242 | 268 |
| Task/source links | 309 | 395 |
| Multiply linked sources | 40 | 45 |
| Unresolved link instances | 12 | 19 |
| Current shared sources | 36 | 39 |
| Current unique sources | 154 | 155 |
| Task snapshots | 45 | 61 |
| Unique unresolved source rows | 7 | 13 |

The 61 task-snapshot rows in the 60-task corpus are expected: TASK-100 also
registered the older TASK-096 record as an output. It remains a separate task
record, not cloned shared source prose.

## 3. Development regression

### 3.1 Comparison with prior prototypes

| Metric | TASK-257 prototype | TASK-258 prototype | TASK-259 FTS on TASK-257 | TASK-259 FTS on TASK-258 |
|---|---:|---:|---:|---:|
| Task recall@6 | 7/9 (77.8%) | 8/9 (88.9%) | 9/9 (100%) | 8/9 (88.9%) |
| Strongest-source visibility | 10/16 (62.5%) | 9/15 (60%) | 13/16 (81.25%) | 13/15 (86.67%) |
| Task MRR | not recorded | not recorded | 0.7708 | 0.6146 |
| Global source MRR | not recorded | not recorded | 0.3197 | 0.1794 |
| Compound task sets complete | 0/1 | 1/1 | 1/1 | 1/1 |
| Positive/no-match decisions correct | positives only | 9/9, one negative | 8/8 positives | 9/9, one negative |

The low global source MRR is important. The right source can rank poorly across
the entire corpus even when it becomes one of the best two sources after a
correct task is selected. This supports a two-stage design rather than asking
an agent to read a global source list.

### 3.2 TASK-257 remaining exact-source misses

- H3 exposed the redaction regression test but not `scripts/redaction.py`.
- H5 exposed the halt-authority test and a related implementation source but
  not `workflow/runtime_policy.yaml`.
- H7 exposed the cost/yield implementation but not the frozen rollup report.

All expected tasks were found, including both TASK-187 and TASK-195 for the
compound active-session-versus-hung-resume question. The negative abstention
rate is unknown because this truth set contains no negative question.

### 3.3 TASK-258 remaining miss

S6 still omitted TASK-150 and both expected planning specs. The query used
"quiet agent," "dashboard," and a recovery progression; the task and sources
use "silent agents," "mission-control TUI," "liveness reaper," and
"intervention affordances." Porter stemming, trigram identifiers, bounded
clause splitting, and current source summaries did not bridge the conceptual
vocabulary gap.

This is a useful residual error. Adding owner-written synonyms would hide the
problem. A later local semantic-channel experiment should be judged by whether
it uniquely recovers this kind of miss without increasing false positives,
privacy risk, model dependency, latency, or index complexity.

## 4. Performance and storage

| Metric | 45-task corpus | 60-task corpus |
|---|---:|---:|
| Build time | 579.0 ms | 489.8 ms |
| SQLite database | 823,296 bytes | 897,024 bytes |
| Query minimum | 9.6 ms | 8.8 ms |
| Query median | 17.5 ms | 13.7 ms |
| Query maximum | 22.6 ms | 18.9 ms |

The timing difference between corpora is normal run-to-run variation at this
small scale, not evidence that a larger corpus is faster. The practical result
is that rebuild and query costs are comfortably local and subsecond/millisecond
without a new package or service.

Packet-token cost is not scored in this development task because no evaluator
packet was rendered. The next holdout must preserve the TASK-258 one-packet
ceiling and measure final context, not infer it from database size.

## 5. Focused verification

Nine tests cover:

- unique source storage plus multiple explicit task links;
- prevention of current shared content appearing in task FTS text;
- unresolved path visibility;
- deterministic RRF and provenance;
- bounded compound-clause splitting;
- complementary implementation/test selection;
- no-match abstention;
- trigram identifier lookup;
- deterministic result ordering across rebuilds.

All nine pass. SQLite FTS5, Porter, BM25, and trigram support are available in
the existing MAP Python/SQLite runtime.

## 6. Development choices that must not be mistaken for holdout evidence

The owner inspected known failures while changing:

- source-to-task weights to stop source-volume bias;
- compound-clause splitting around question-bearing `and` clauses;
- task-context terms used only for linked-source selection;
- complementarity between tests/reviews and implementations;
- validation-file and user-facing HTML signals;
- weak-source coverage and abstention thresholds.

These are generic, testable rules, but the truth was visible. Their value must
be tested unchanged on new questions authored after the freeze.

## 7. Fresh-holdout contract

The next task should keep the script and focused-test hashes frozen, then:

1. use a new completed-task corpus not used by TASK-257 or TASK-258;
2. ask a fresh visible read-only author for heterogeneous paraphrased
   questions, including at least two compound questions and several genuine
   no-match questions;
3. generate one compact packet per query from the frozen FTS result;
4. use a different fresh visible read-only evaluator;
5. score task recall/precision, exact-source recall/precision, source MRR,
   compound completeness, negative false positives, context, latency, and
   temporal warnings;
6. compare with a simple task-only FTS ablation so source-channel value is
   measurable;
7. keep the implementation out of startup, routing, Command Center, and
   canonical state regardless of development scores.

Only after that holdout should MAP decide whether to test a separately scored
local semantic fallback.

## 8. Final decision

Freeze this FTS5/RRF baseline for fresh evaluation. It is faster, more
inspectable, more temporally honest, and materially better on known source
retrieval than the prior prototypes. It is still not ready for use: one fresh
holdout has not been run, source MRR is noisy, negative calibration has only
one example, and the remaining conceptual vocabulary miss is unresolved.

No startup, router, UI, external service, canonical database schema, or agent
workflow was changed.
