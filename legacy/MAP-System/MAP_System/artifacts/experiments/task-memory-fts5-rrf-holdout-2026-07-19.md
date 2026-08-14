<!-- hpom: file: artifacts/experiments/task-memory-fts5-rrf-holdout-2026-07-19.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: codex-lab-kiri -->
<!-- hpom: status: EXPERIMENT_COMPLETE -->
<!-- hpom: last_verified: 2026-07-19 -->
<!-- hpom: verified_against: frozen retriever/harness hashes, author event 7726, generated index/packets, evaluator events 7753/7766/7779/7792/7805/7818/7831/7844/7857/7870/7883, focused tests, and MAP validators -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# TASK-260 Fresh Blinded FTS5/RRF Holdout

- owner: codex-lab-kiri
- truth author: helper-index-fts-author-nuzi
- blinded evaluator: helper-index-fts-evaluator-rumi
- corpus: 43 completed tasks, TASK-206 through TASK-249 excluding TASK-236
- date: 2026-07-19
- verdict: **task retrieval and compact-packet reasoning pass this holdout;
  evidence selection and automatic abstention do not**

## Executive result

The frozen temporal-safe FTS5/RRF retriever generalized strongly for task
discovery:

- The algorithm returned all **12/12 expected task labels** in the top six.
- All **4/4 compound task sets** were complete.
- A task-only FTS ablation found 11/12 labels. The source-link channels added
  the missing TASK-213 without losing another expected task.
- The blinded evaluator selected **12 correct task labels among 12 selections**:
  100% precision and 100% recall.
- The evaluator completed all eight positive task sets and correctly returned
  `NO MATCH` on all three negatives.

The evidence and abstention layers did not meet the adoption gate:

- Packets exposed **15/20 exact strongest sources (75%)**.
- The evaluator selected those same 15 exact sources among 20 selections:
  **75% exact-source precision and 75% recall**.
- Every visible expected source was used; no hidden expected source was
  recovered. Evidence-slot construction, not reader comprehension, remains the
  exact-source bottleneck.
- The frozen numeric abstention gate made **four errors**: it returned candidate
  sets for all three genuine negatives and `no_strong_match` for one positive.
  Its positive-versus-negative accuracy was only **7/11 (63.6%)**.
- The blinded evaluator overrode all four bad algorithm signals correctly from
  the candidate descriptions.

Packets used 16,138 estimated tokens total, versus about 2,240,305 tokens for
the 188 readable unique corpus files: a **99.28% total-context reduction**.
Median packet size was 1,455 tokens. The evaluator independently estimated
16,012 tokens.

Decision: keep the FTS5/RRF retriever as a promising offline candidate, but do
not integrate it. The next engineering work should be query-global dynamic
evidence budgeting, temporal snapshots, and a calibrated candidate verifier.
Do **not** add embeddings yet: fresh task recall is already 100%, so the
measured bottlenecks are no longer first-stage semantic recall.

## 1. Independence and frozen boundary

The implementation and packet harness were frozen before the author saw the
corpus:

- retriever SHA-256:
  `edd0b53ab6d9c480360e19f4d14d667f459fcaa3155748a9bd96e741b70cca27`
- retriever-test SHA-256:
  `58df22f41258c3cea27d48ddbf413bf1b0c9c63eead9016b58008718a677949f`
- holdout-harness SHA-256:
  `65219824dc3c2d5f62b77923a0bd9cd3f6c21d3222ee9db9f3e5bcff723a83ff`
- harness-test SHA-256:
  `3d97e70c1624a714ae2620993959f7c23abf39cbc4cdca5a45aec149f2dacd0c`
- truth freeze: hcom event 7726 at 2026-07-19T19:27:55Z

No retriever, field weight, temporal weight, query splitter, source selector,
abstention threshold, renderer, or scoring code changed after the author
response.

The author read only the 43 corpus task records, required repository
instructions, and registered evidence needed to verify its answers. It created:

- eight positive questions across eight work areas;
- twelve expected task labels;
- twenty strongest evidence paths;
- four compound two-task sets;
- six code/test-centered questions;
- three legitimate implementation-specific no-match controls.

The evaluator received one packet at a time. It did not access the combined
packet, truth, generated JSON, task records, source files, research, prior
experiments, or repository search.

## 2. Algorithm results before the evaluator

### 2.1 Task retrieval and ablation

| Measure | Full FTS5/RRF | Task-only FTS |
|---|---:|---:|
| Expected task labels in top six | 12/12 (100%) | 11/12 (91.7%) |
| Compound task sets complete | 4/4 (100%) | 3/4 (75%) |
| Critical misses | 0 | 1 (TASK-213 in F2) |

The source channels produced a real incremental gain. F2's task-only list
contained TASK-220 but missed TASK-213; the full ranking placed TASK-213 third
and TASK-220 sixth. This is exactly the intended role of task/source links: add
recall without copying source content into task documents.

The result is also fragile at the packet boundary. F2's correct tasks occupied
positions three and six, so a smaller top-K would have failed even though
recall@6 is perfect.

### 2.2 Source visibility

| Query | Expected sources | Visible exact sources | Hidden exact source |
|---|---:|---:|---|
| F1 ClearFront state/combat extraction | 3 | 2 | combat parity report |
| F2 replacement Undo + headless cases | 2 | 2 | none |
| F3 persistent limit supervisor | 3 | 2 | supervisor outcome report |
| F4 local Ollama advisory boundary | 3 | 2 | advisory-lane outcome report |
| F5 manual-helper capacity accounting | 2 | 1 | AGENTS guide |
| F6 attention popup + formatting | 3 | 2 | attention-popup focused test |
| F7 negated destructive clauses | 2 | 2 | none |
| F8 practice run + measured scenario | 2 | 2 | none |
| **Total** | **20** | **15 (75%)** | **5** |

Two misses were structurally inevitable under the frozen per-task source limit:
F3 and F4 each define three required evidence roles for one task, but the
retriever can expose only two sources per task. The maximum possible score on
this truth under that contract was therefore 18/20 (90%). Actual visibility
was three paths below that ceiling.

This shows that a fixed "two sources per candidate" rule is the wrong unit.
The packet needs a query-level evidence budget that can allocate three slots to
one task when the question requires implementation, test, and outcome, or
spread three slots across a compound task set.

### 2.3 Abstention failure

| Query | Truth | Frozen signal | Coverage | Supporting channels |
|---|---|---|---:|---:|
| F2 hidden-information Undo | positive | no strong match | 19.05% | 12 |
| N1 ClearFront multiplayer | no match | candidate set | 22.22% | 3 |
| N2 transcript encryption/deletion | no match | candidate set | 26.67% | 3 |
| N3 deployment auto-rollback | no match | candidate set | 20% | 4 |

The frozen rule required at least 20% query coverage and two supporting
channels. It fails because superficial corpus vocabulary can satisfy both
conditions for a nonexistent capability, while a real paraphrased behavior can
fall just below the coverage cutoff.

No single threshold adjustment separates these four cases. Lowering the
coverage threshold admits the negatives; raising it rejects more positives.
The system needs candidate-level capability verification, not another decimal
place on the same score.

## 3. Blinded evaluator result

| Query | Expected tasks | Evaluator tasks | Exact sources | Decision |
|---|---|---|---:|---|
| F1 | TASK-212, TASK-214 | TASK-214, TASK-212 | 2/3 | correct |
| F2 | TASK-213, TASK-220 | TASK-213, TASK-220 | 2/2 | correct despite false abstain signal |
| F3 | TASK-221 | TASK-221 | 2/3 | correct |
| F4 | TASK-228 | TASK-228 | 2/3 | correct |
| F5 | TASK-231 | TASK-231 | 1/2 | correct |
| F6 | TASK-237, TASK-240 | TASK-237, TASK-240 | 2/3 | correct |
| F7 | TASK-249 | TASK-249 | 2/2 | correct |
| F8 | TASK-239, TASK-233 | TASK-239, TASK-233 | 2/2 | correct |
| N1 | no match | NO MATCH | n/a | correct despite candidate signal |
| N2 | no match | NO MATCH | n/a | correct despite candidate signal |
| N3 | no match | NO MATCH | n/a | correct despite candidate signal |

Strict evaluator metrics:

- task-label precision: 12/12 = **100%**;
- task-label recall: 12/12 = **100%**;
- complete positive task sets: 8/8 = **100%**;
- compound task sets: 4/4 = **100%**;
- no-match decisions: 3/3 = **100%**;
- exact-source precision: 15/20 = **75%**;
- exact-source recall: 15/20 = **75%**.

All answers were high confidence. Unlike TASK-258's high-confidence partial S4
answer, every task/no-match decision here was correct. The evaluator also
explicitly described missing or indirect evidence where a strongest path was
not visible.

The reader's success does not validate the numeric abstention gate. It shows
that the compact task descriptions and evidence snippets contain enough
meaning for a strong bounded verifier to judge capability fit.

## 4. Context, latency, and storage

### 4.1 Context

The corpus contains 250 task/source registrations to 193 unique paths. Of
those, 188 are readable files, two are legitimate directory bundles, and three
are unresolved legacy CommandCenterUI paths.

| Context | Estimated tokens |
|---|---:|
| 188 readable unique corpus files | about 2,240,305 |
| Single packet, minimum | 1,401 |
| Single packet, median | 1,455 |
| Single packet, maximum | 1,563 |
| Eleven packets combined | 16,138 |
| Evaluator's estimate | about 16,012 |

The combined packet set is 99.28% smaller than loading the readable corpus
once. A median one-query packet is about 99.94% smaller. The unusually large
raw corpus includes ClearFront application and extracted bundle evidence; this
is precisely the kind of history an agent should not load speculatively.

### 4.2 Runtime

- disposable database build: 595 ms;
- database size: 704,512 bytes;
- local query time: 5.3 to 16.3 ms, median 12.5 ms;
- packet delivery-to-evaluator response: 8 to 34 seconds, median 13 seconds.

Evaluator response latencies for F1 through N3 were 34, 13, 11, 13, 23, 23,
14, 13, 10, 8, and 15 seconds. F1 includes the one-time protocol read.

The index must remain behind a local query tool. Reading the database or a
full JSON projection directly would defeat the context-saving boundary.

## 5. Temporal and path findings

The disposable database contains:

- 193 unique source documents;
- 250 task/source links;
- 22 current shared sources;
- 125 current unique sources;
- 43 task snapshots;
- 3 unresolved source rows.

The three unresolved paths are legacy `../CommandCenterUI/src/chat.css`,
`chat.html`, and `chat.js` registrations. Packets retain resolution and
temporal labels rather than hiding the gap.

F1 demonstrates the remaining temporal problem. `state.js` and `combat.js` are
current shared implementation files linked by multiple extraction tasks. The
author explicitly noted that current `combat.js` includes a later render-call
form. The index labels these paths `current_shared`, but that label alone does
not prove what the file contained when TASK-212 or TASK-214 completed.

For historical questions, a task-specific parity report is stronger than the
current shared source unless MAP records a task-time hash or Git version. The
next data-model improvement should capture immutable evidence snapshots or
source hashes at submission/release, then resolve the historical version when
available.

## 6. What should change next

### 6.1 Replace per-task source slots with a query-global evidence budget

Allocate up to three sources across the entire answer, using:

- clause coverage;
- expected proof roles implied by the question;
- non-redundancy, not forced role difference;
- task linkage;
- historical attribution quality;
- path health.

For F3/F4, the budget should intentionally return implementation, focused test,
and outcome. For F1, it should prefer the combat-specific parity report over a
state parity report when covering the "combat behavior preserved" clause.

### 6.2 Treat abstention as verification, not retrieval strength

The candidate list can remain high-recall. A separate bounded verifier should
ask: "Does any candidate actually claim or prove the requested capability?"

Candidate approaches, in order:

1. deterministic clause coverage plus explicit implementation/proposal/status
   distinctions;
2. a strong agent reading only the compact packet, as this evaluator did;
3. a smaller local verifier only if it can reproduce the 11/11 decisions on
   frozen packets and pass new negatives.

Until calibrated, suppress or clearly label the numeric `candidate_set` /
`no_strong_match` signal. It was wrong on every negative in this holdout.

### 6.3 Capture task-time evidence identity

At submission/release, record hashes or commit/version references for registered
files when practical. Keep current source documents separate. Historical
retrieval can then choose the task-time version; current-state retrieval can
choose the latest version honestly.

### 6.4 Do not add semantic retrieval yet

The research sequence proposed semantic retrieval only if frozen sparse recall
misses remained. This fresh holdout has 12/12 task recall. Adding embeddings now
would address an unmeasured problem while leaving the measured evidence and
abstention failures untouched.

Reconsider a semantic channel only if a later heterogeneous holdout produces a
real first-stage task miss after the evidence-budget and verification fixes.

## 7. Adoption decision

The system does **not** meet the proposed TASK-258 adoption gate:

- task recall: passes this holdout;
- compound completion: passes this holdout;
- source visibility/recall: 75%, below the proposed 90%;
- negative false positives from the automatic gate: 3/3, unacceptable;
- historical attribution: labeled but not version-resolved;
- independent repeated holdouts after the next changes: not yet run.

No startup, router, UI, external service, canonical database schema, or agent
workflow was changed.

## 8. Monitoring and scope adherence

- Author `helper-index-fts-author-nuzi` returned truth at event 7726 and was
  stopped after its bounded read-only assignment.
- Evaluator `helper-index-fts-evaluator-rumi` returned F1-N3 at events 7753,
  7766, 7779, 7792, 7805, 7818, 7831, 7844, 7857, 7870, and 7883.
- Terminal/event monitoring showed only the current authorized packet plus the
  evaluator protocol note. Both helpers reported no other access.
- Both visible WezTerm panes were closed after the bounded work completed.

## 9. Final recommendation

Retain the FTS5/RRF task-retrieval architecture and temporal separation as the
leading candidate. Retire the current fixed two-source allocation and numeric
abstention rule. Build and regression-test a three-slot query-global evidence
selector plus a capability verifier, add task-time source identity where
available, and run another fresh blinded holdout before any integration.
