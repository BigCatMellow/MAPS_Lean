# Experiment — Paraphrase Robustness of the FTS5/RRF Task-Memory Retriever

- owner: claude-lab-lure
- date: 2026-07-20
- type: independent cross-model probe of the TASK-256..262 retrieval chain
- authority: none; disposable local benchmark, no integration, no task authority
- harness: `scripts/task_memory_fts.py benchmark` (Codex's frozen retriever, unmodified)

## 1. Purpose

My earlier review (`artifacts/reviews/ei-triage-design-and-retrieval-chain-review-lure-2026-07-19.md`)
accepted Codex's reported numbers without reproducing them, and flagged that as
a limit. This probe (a) reproduces them independently and (b) tests the
*conclusion* that followed from them:

> "Do not add embeddings yet: fresh task recall is already 100%, so the measured
> bottlenecks are no longer first-stage semantic recall." (TASK-260)

## 2. Reproduction — Codex's numbers are accurate

Ran the frozen benchmark unmodified against both known-development corpora.
Every headline figure reproduced exactly:

| Corpus | Metric | Codex reported | My reproduction |
|---|---|---:|---:|
| TASK-257-known | task recall@6 | 9/9 (100%) | **9/9 (100%)** |
| TASK-257-known | source visibility | 13/16 (81.25%) | **13/16 (81.25%)** |
| TASK-258-known | task recall@6 | 8/9 (88.9%) | **8/9 (88.9%)** |
| TASK-258-known | source visibility | 13/15 (86.67%) | **13/15 (86.67%)** |

Codex's reporting is honest and reproducible. Build ~0.64s, DB ~823KB, query
~12ms — the performance claims also hold.

## 3. New finding A — the retrieval metric is highly phrasing-sensitive

**Method.** Controlled single-variable probe. Identical corpus, identical
`expected_task_ids` and `expected_source_paths`, identical retriever and
settings. The *only* change: each of the 8 questions was rewritten to preserve
intent while avoiding the corpus's distinctive vocabulary — the way a different
agent months later would plausibly ask, not knowing the original wording.

**Result.**

| Condition | task recall@6 | source visibility | task_mrr | source_mrr |
|---|---:|---:|---:|---:|
| ORIGINAL wording | 9/9 (100%) | 13/16 (81%) | 0.771 | 0.320 |
| PARAPHRASED wording | **3/9 (33%)** | **5/16 (31%)** | **0.188** | **0.057** |

Five of eight queries flipped HIT to MISS on wording alone:

| Query | Target | Original | Paraphrase |
|---|---|---|---|
| H1 | TASK-173 session replay | HIT | MISS |
| H2 | TASK-179 librarian paths | HIT | HIT |
| H3 | TASK-191 redaction | HIT | MISS |
| H4 | TASK-199 review claims | HIT | MISS |
| H5 | TASK-201 halt authority | HIT | MISS |
| H6 | TASK-205 ProjectUpdater backup | HIT | HIT |
| H7 | TASK-190 cost/yield | HIT | HIT |
| H8 | TASK-187/195 limit watcher | HIT | MISS |

**Interpretation.** The 100% task recall that justified deferring embeddings was
measured on questions whose wording closely tracks the indexed text. It is
therefore evidence that *lexical matching works when vocabulary matches* — not
evidence that first-stage recall is solved. For the actual E/I use case (an
agent later searching for connections it does not yet have words for),
vocabulary drift is the normal case, not the exception. **The "embeddings not
justified" conclusion is not supported by the evidence that was used to reach
it.**

### 3b. Second corpus — a deliberately *less* adversarial replication

To address the single-corpus limitation, the probe was repeated on the TASK-258
corpus (9 queries, including one negative/abstention case). This time **proper
nouns were retained** (a real asker would say "CommandCenterUI"); only
descriptive vocabulary was changed. This is the realistic middle ground.

| Condition | task recall@6 | source visibility | task_mrr | source_mrr | abstention |
|---|---:|---:|---:|---:|---:|
| C2 ORIGINAL | 8/9 (89%) | 13/15 (87%) | 0.615 | 0.179 | 9/9 |
| C2 PARAPHRASED | **6/9 (67%)** | **8/15 (53%)** | **0.286** | 0.157 | **7/9** |

Degradation is milder than corpus 1, as expected for a less adversarial rewrite.

**Two observed stress points (NOT formal bounds).** Per independent method
review (kiri, 2026-07-20), these are two measured operating points, not a
proven range — they do not establish that real query traffic lies between them:

- heavier drift (distinctive vocabulary removed): 100% -> **33%**
- lighter drift (proper nouns retained): 89% -> **67%**

The defensible claim is therefore: **task recall degrades substantially and
reproducibly from wording alone, at both stress points measured.** Either point
invalidates using a single-phrasing 100% as evidence that first-stage recall is
solved.

**Meaning-preservation audit (independent).** kiri judged 3 of the 8 corpus-1
pairs (H3, H5, H6) to be only *partial* meaning matches — a fair criticism of my
rewrites. Restricting corpus 1 to the strong-only pairs, the effect **survives**:
task 5/5 -> **2/5**, sources 7/8 -> **3/8**. All 9 corpus-2 pairs were judged
meaning-preserving, and corpus 2 still falls 8/9 -> 6/9 with task MRR .6146 ->
.2865. The finding does not depend on the weaker paraphrases.

### 3c. Finding D — abstention is phrasing-sensitive, in one specific direction

Corpus 2 abstention accuracy fell from 9/9 to 7/9 under paraphrase. Precisely
(per method review): the two errors are **false no-match decisions on the
positive queries S2 and S7** — the system wrongly declared "no strong match" for
questions that did have correct answers. The sole true negative (S9) **remained
correct** in both conditions.

So the failure mode is *over-abstention under drift*, not false confidence. That
is the safer direction, but it still means a vocabulary-drifted query can miss
the right task and then also suppress its own candidates. It compounds the
abstention weakness Codex documented in TASK-260.

### 3d. Confirms Codex's own documented blind spot

Query S6 (TASK-150, "what should operators see when an agent goes quiet")
**failed in both the original and paraphrased conditions.** This is precisely
the miss Codex recorded in TASK-259 (quiet-agent/dashboard wording versus
silent-agent/mission-control vocabulary). It is therefore an intrinsic
vocabulary blind spot, not an artifact of my rewrite — independent
corroboration of their diagnosis.

## 4. New finding B — a magnet-document failure mode re-emerges under drift

In the paraphrase run, `TASK-181` ("Use local librarian to compact emergence
records") occupied the top slot in most failures. It registers **55 output
paths**, versus 5-7 for the correct targets.

The retriever already anticipates this: `TEMPORAL_WEIGHTS` documents that
source-to-task propagation is "a recall fallback, not a vote proportional to how
many outputs a task happened to register."

**Status: observed behaviour, causal mechanism UNPROVEN.** Per method review,
output fan-out is only a *causal hypothesis* here — per-channel/mode task IDs are
deduplicated, so high fan-out does not straightforwardly convert into
proportional ranking weight. What is established is that TASK-181 occupies the
top slot in most drift failures; *why* is not. **Required next step: isolate it
with a fan-out cap / inverse-link-weight ablation** before claiming the
anti-magnet defence fails. Do not treat this as a confirmed defect.

## 5. New finding C — visibility overstates usable evidence

Even in the favourable ORIGINAL condition, `source_mrr` is 0.32 and 0.18 while
source *visibility* is 81% and 87%.

**Caveat (method review):** `source_mrr` here is a *global* source ranking and
does **not** directly represent the two per-task sources actually delivered in
the packet, so it cannot be read as "the agent opens rank-5 evidence." The valid
form of this concern is narrower: visibility counts a source appearing anywhere
in a candidate's choices, which is a weaker guarantee than it sounds.

**Correct gate:** measure **end-to-end acceptable-evidence rank within the
delivered packet**, not global MRR and not visibility. That metric does not yet
exist and should be added before any evidence-layer adoption decision.

## 6. Limitations (stated plainly)

- The paraphrases are one author's judgement. Corpus 1 deliberately strips
  distinctive vocabulary (33%); corpus 2 retains proper nouns (67%). These are
  **two observed stress points, not formal bounds** — real query traffic is
  **not** proven to lie between them, and neither point should be read as an
  expected average. (Corpus 1 additionally contains three only-partial meaning
  matches, H3/H5/H6; the effect survives excluding them — see 3b.)
- Two corpora, 17 queries total, one paraphrase author. No blinded second
  author, unlike Codex's holdouts — a second author should re-run this before
  the finding is treated as settled.
- Measures first-stage retrieval and the abstention gate; does not re-test the
  bounded reader, which Codex showed can recover some evidence errors.
- Corpus 2's S6 failed in both conditions, so its miss is not attributable to
  paraphrasing.

## 7. Independent method review — CONFIRMED with qualifications

Reviewed by codex-lab-kiri, 2026-07-20. Record:
`artifacts/reviews/task-memory-paraphrase-robustness-method-review-kiri-2026-07-20.md`
(sha256 e378d8c4d1770d2ce7a3cf2dac70461e1c3b764f71b668fbfe247ed248990162).
Both corpora reproduced exactly by the reviewer; nine retriever tests and
emergence validation pass.

**Verdict: main conclusion CONFIRMED — reopen the semantic-fallback /
query-expansion experiment decision, but DO NOT adopt embeddings.**

All four required qualifications have been applied above: stress points not
bounds (3b), abstention errors are false no-match on positives S2/S7 with the
true negative intact (3c), magnet causality unproven pending ablation (4), and
global source MRR is not the delivered-packet metric (5).

## 8. Recommendation (post-review)

1. **Reopen the semantic-fallback / query-expansion decision** — the deferral
   rationale does not survive rewording. This explicitly does **not** mean adopt
   embeddings; it means a bounded synonym-expansion / semantic-fallback
   experiment is now justified, cheapest option first.
2. **Adopt paraphrase robustness as a standing retrieval metric.** Future
   holdouts should report vocabulary-matched *and* vocabulary-drifted recall.
   A single-phrasing number is not a safe adoption signal.
3. **Run a fan-out cap / inverse-link-weight ablation** to test whether the
   TASK-181 magnet effect is actually caused by output fan-out. Do not change
   weighting before that isolation.
4. **Add an end-to-end acceptable-evidence-rank metric** on the delivered packet,
   and gate the evidence layer on it rather than on visibility or global MRR.
5. **Blinded second-author replication** of the paraphrase set would settle the
   remaining method risk (single author, no blinding).

None of this diminishes the chain: the engineering is sound, reproducible, and
correctly withheld from integration. This probe changes one conclusion, not the
verdict.
