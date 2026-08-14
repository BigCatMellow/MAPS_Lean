# Review: TASK-260 Run a fresh blinded holdout for the frozen FTS5 memory index

task_id: TASK-260
reviewer: claude-lab-rose
task_owner: codex-lab-kiri

## Verdict

APPROVED

The strongest result in the chain so far, precisely because it reports a
clear failure the previous tasks didn't surface: the automatic numeric
abstention gate was wrong on 3/3 genuine negatives (would have fabricated
candidates for nonexistent capabilities) while the blinded human-equivalent
evaluator caught all four bad algorithm signals correctly. The report treats
that as disqualifying for adoption rather than softening it. All four
frozen-hash carries (retriever, retriever tests, harness, harness tests) are
verified unchanged on disk.

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| TASK-259 retriever hash remains frozen; generic harness + focused tests frozen before author creates truth. | PASS | `sha256sum MAP_System/scripts/task_memory_fts.py` = `edd0b53a...` — identical to the hash TASK-259 froze and this report's §1 cites. Harness (`task_memory_fts_holdout.py`) and all four test files also hash-match §1's recorded values exactly. `frozen_at` (19:27:55Z) precedes the queries-file write (15:29:05 EDT) and packet generation (15:29:31 EDT). |
| Fresh author uses only TASK-206–249 excluding TASK-236, produces ≥8 positive questions, ≥2 compound sets, ≥3 no-match questions across ≥5 work areas. | PASS | `corpus_task_ids` in the frozen queries file = 43 entries, confirmed `TASK-236` absent. 11 queries total: F1–F8 (8 positive, including 4 compound sets per report §1) + N1–N3 (3 no-match). `test_contract_rejects_too_few_negatives_and_compounds` enforces this contract structurally. |
| Different fresh evaluator receives one bounded packet at a time, no access to truth/combined packet/index/task files/source files/research/prior experiments/repo search. | PASS | `helper-index-fts-evaluator-rumi` is a distinct identity from `helper-index-fts-author-nuzi`. Report §8: "Terminal/event monitoring showed only the current authorized packet plus the evaluator protocol note. Both helpers reported no other access." 11 response events cited (7753–7883). |
| Final report compares frozen FTS metrics, evaluator precision/recall, compound completion, task-only ablation, no-match false positives, context, latency, path/temporal warnings, limitations, no adoption/integration claim. | PASS | §2.1 has the task-only ablation table (11/12 vs 12/12, showing the source-link channel's real incremental value). §2.3 reports the abstention failure explicitly (3/3 false positives on negatives). §4 has context/latency. §5 has temporal/path findings. §7: "The system does **not** meet the proposed TASK-258 adoption gate" — explicit non-adoption verdict with itemized pass/fail against that gate. |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Changing the frozen TASK-259 retriever | NOT BROKEN — hash-verified identical to the TASK-259 freeze; report §1 confirms "No retriever, field weight, temporal weight, query splitter, source selector, abstention threshold, renderer, or scoring code changed after the author response." |
| Integration into startup, routing, UI, canonical authority, external services | NOT BROKEN — §7/§9 explicit non-adoption; database is disposable/temp-dir. |

## Files Reviewed

- `MAP_System/artifacts/experiments/task-memory-fts5-rrf-holdout-2026-07-19.md` (full)
- `MAP_System/artifacts/experiments/task-memory-fts5-rrf-holdout-queries-2026-07-19.json` (frozen truth)
- `MAP_System/inbox/helpers/helper-index-fts-author-2026-07-19.md`, `helper-index-fts-evaluator-2026-07-19.md`
- `MAP_System/artifacts/experiments/task-memory-fts5-rrf-holdout-packets-2026-07-19/` (F1–F8, N1–N3)
- `MAP_System/scripts/task_memory_fts_holdout.py`, `MAP_System/tests/test_task_memory_fts_holdout.py`

## Verification

- `python -m py_compile MAP_System/scripts/task_memory_fts_holdout.py MAP_System/tests/test_task_memory_fts_holdout.py` — passes.
- `python -m unittest MAP_System.tests.test_task_memory_fts_holdout -v` — 5/5 passed.
- `sha256sum` confirms all four frozen hashes (`task_memory_fts.py`, its tests, the holdout harness, and the harness tests) match the values recorded in §1 exactly — the retriever genuinely carried forward unmodified from TASK-259, closing the open item flagged in the TASK-259 review.
- Frozen queries JSON: `frozen_at` predates queries-file and packet mtimes; corpus is exactly 43 tasks (TASK-206–249 minus TASK-236); 11 queries (8 positive + 3 negative) confirmed by ID list.
- Report's abstention-failure claim (§2.3) is a genuinely negative, adoption-blocking result stated plainly in §7's gate comparison — not downplayed relative to the strong 100% task-recall headline.

## Notes

Fifth task in the TASK-256→262 chain. TASK-261 ("Prototype query-global
evidence selection and local capability verification") maps directly onto
this report's §6.1 (query-global evidence budget replacing the fixed
two-source-per-task rule) and §6.2 (treat abstention as verification, not
retrieval strength) — will check that TASK-261 actually builds on those two
proposals rather than re-deriving them.
