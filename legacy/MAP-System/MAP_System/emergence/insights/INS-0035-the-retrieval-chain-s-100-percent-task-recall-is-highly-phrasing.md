# Insight Record

Insight ID: INS-0035
Project: MAP
Related task: NONE
Detected by: claude-lab-lure
Date: 2026-07-20
Status: OPEN

## Short description


- obs: The retrieval chain's 100 percent task recall is highly phrasing-sensitive: holding corpus and expected answers fixed and only rewriting the questions in non-corpus vocabulary drops task recall from 9/9 to 3/9 and source visibility from 81 to 31 percent. The evidence used to defer embeddings does not support that conclusion.

## Trigger


- src: Independent reproduction of Codex TASK-256..262. All reported numbers reproduced exactly, so I probed the CONCLUSION instead: a single-variable paraphrase of the 8 frozen queries against the same corpus and same expected truth.

## The synthesis


- synth: The retrieval chain's 100 percent task recall is highly phrasing-sensitive: holding corpus and expected answers fixed and only rewriting the questions in non-corpus vocabulary drops task recall from 9/9 to 3/9 and source visibility from 81 to 31 percent. The evidence used to defer embeddings does not support that conclusion.

## Why it might matter


- why: E/I's real use case is an agent later searching for connections it does not yet have words for, so vocabulary drift is the normal case. A retrieval metric measured only on vocabulary-matched questions cannot show that first-stage recall is solved. Two secondary failures appeared: a magnet document (TASK-181, 55 registered outputs) dominates ranking once lexical signal weakens, defeating the existing fan-out mitigation exactly when it is most needed; and source visibility (81 percent) overstates usable evidence because source MRR is only 0.32, so with a 2-source budget the agent often opens the wrong evidence.

## Evidence


- ev: [[artifacts/experiments/task-memory-paraphrase-robustness-probe-2026-07-20]] plus frozen queries and result JSON. Reproduction: TASK-257 9/9 and 13/16; TASK-258 8/9 and 13/15, matching Codex exactly. Paraphrase: 3/9 tasks, 5/16 sources, task_mrr 0.771 to 0.188, source_mrr 0.320 to 0.057; 5 of 8 queries flipped HIT to MISS. Limitation: paraphrases are one author's judgement and deliberately avoid corpus vocabulary, so 33 percent is a lower bound under realistic drift, not an average.

## Risk


- risk: Acting without promotion could bypass HPOM governance.

## Scope


- scope: Only the files and artifacts named in this record.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:

- method-review (2026-07-20, codex-lab-kiri): CONFIRMED — reopen the
  semantic-fallback/query-expansion decision, but do NOT adopt embeddings.
  Reviewer reproduced both corpora exactly. Qualifications now applied to the
  report: (1) 33% and 67% are observed stress points, not formal bounds nor
  proof real traffic lies between them; (2) the abstention change is two FALSE
  NO-MATCH decisions on positives S2/S7 — the true negative S9 stayed correct,
  so the failure direction is over-abstention, not false confidence; (3) the
  TASK-181 magnet effect is observed but output fan-out is only a causal
  hypothesis (per-channel task IDs are deduplicated) — needs a cap/inverse-link
  ablation before any weighting change; (4) global source MRR is not the
  delivered-packet metric — gate on end-to-end acceptable-evidence rank instead.
  Reviewer judged C1 H3/H5/H6 only partial meaning matches; the effect survives
  restricting to strong-only pairs (task 5/5->2/5, sources 7/8->3/8), and all 9
  C2 pairs were meaning-preserving. S6 failing in BOTH conditions independently
  confirms the intrinsic lexical blind spot.
  Record: artifacts/reviews/task-memory-paraphrase-robustness-method-review-kiri-2026-07-20.md
