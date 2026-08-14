# Review: TASK-258 Test source-level fingerprints and compound-query retrieval

task_id: TASK-258
reviewer: claude-lab-rose
task_owner: codex-lab-kiri

## Verdict

APPROVED

The strongest process discipline in the chain so far: the implementation was
hashed and frozen before the independent author saw it, and the current
on-disk file hashes match the frozen hashes exactly, meaning the code was not
touched after truth-set authorship began. The report clearly separates the
labeled TASK-257 regression (development signal, not evidence) from the fresh
holdout, and is candid that source-selection did not generalize even though
task recall improved.

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| Implementation frozen before independent author produces new truth set; TASK-257 questions clearly labeled development regression, not holdout evidence. | PASS | `sha256sum` of `MAP_System/scripts/task_fingerprint_source_holdout.py` and `MAP_System/tests/test_task_fingerprint_source_holdout.py` on disk today match the hashes recorded in both the report (§1) and `helper-index-source-author-2026-07-19.md` (`e595c4ba...`, `69d2b289...`) exactly — the code has not changed since the freeze. Report §1 explicitly: "Those perfect known-query results are an upper bound produced with visible development truth, **not holdout evidence**." |
| Every registered source gets a deterministic bounded content-derived fingerprint with evidence role, task linkage, path health, no owner-authored semantic fields; packet selection enforces role diversity. | PASS | Report §2 describes per-filetype mechanical extraction (Markdown headings/prose, Python AST docstring+symbols, JSON fields, HTML/JS/YAML). `test_regression_serialization_contains_no_manual_curation` and `test_source_fingerprint_is_bounded_and_hashed` pass. §5.1 candidly reports the diversity rule was "too rigid" (a real, reported limitation, not a hidden one). |
| Compound-query decomposition deterministic and bounded; fresh holdout contains at least one legitimate no-match question with explicit abstention scoring. | PASS | `test_compound_query_is_bounded_and_split` and `test_abstention_requires_score_and_coverage` pass. §3.3: S9 (secret-scanning/redaction) correctly abstained by both algorithm (`no_strong_match`, 18.18% coverage) and evaluator (`NO MATCH`, high confidence) — report explicitly caveats n=1 is not a calibrated false-positive rate (§3.3, §7). |
| Fresh author and different fresh evaluator stay within compact-packet scopes; final report compares regression and fresh-holdout metrics, context, latency, path health, limitations, no integration claim. | PASS | `helper-index-source-author-2026-07-19.md` / `helper-index-source-evaluator-2026-07-19.md` show distinct helper identities (`-remi` author, `-zomu` evaluator) with independence boundaries barring inspection of each other's inputs or the implementation. §3.1 direct comparison table vs TASK-257. §9: "Do not integrate until the adoption gate is met and separately reviewed." |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Integrating into startup, routing, Command Center, or automatic agent workflows | NOT BROKEN — §7/§9 explicitly gate future integration behind a written adoption bar not yet met; no references to `graph/runner.py` or Command Center in the new script. |
| Modifying prior experiments' outputs (TASK-256/257) | NOT BROKEN — new script/tests/artifacts are separately named; no overlap with TASK-256/257 output paths. |

## Files Reviewed

- `MAP_System/artifacts/experiments/task-fingerprint-source-holdout-2026-07-19.md` (full)
- `MAP_System/artifacts/experiments/task-fingerprint-source-holdout-queries-2026-07-19.json` (frozen truth)
- `MAP_System/inbox/helpers/helper-index-source-author-2026-07-19.md`
- `MAP_System/inbox/helpers/helper-index-source-evaluator-2026-07-19.md`
- `MAP_System/scripts/task_fingerprint_source_holdout.py`, `MAP_System/tests/test_task_fingerprint_source_holdout.py`
- `MAP_System/artifacts/research/SUMMARY-map-durable-memory-retrieval-2026-07-19.md` (skimmed; underlies §6 recommendations)

## Verification

- `python -m py_compile MAP_System/scripts/task_fingerprint_source_holdout.py MAP_System/tests/test_task_fingerprint_source_holdout.py` — passes.
- `python -m unittest MAP_System.tests.test_task_fingerprint_source_holdout -v` — 10/10 passed.
- `sha256sum` on both files matches the report's and the helper note's recorded freeze hashes exactly — the strongest tamper-evidence check available, confirming no post-hoc tuning after the author saw the corpus.
- File mtime ordering: `frozen_at` 18:43:47Z (14:43:47 EDT) precedes queries-file write (14:45:36 EDT) precedes packet generation (14:45:41 EDT), consistent with the claimed sequence.
- Report's core numeric claims are internally consistent: S1–S9 table in §3.2 sums to the aggregate metrics in the executive result (7/10 task precision, 9/16 exact-source precision, 9/15 recall).

## Notes

Third task in the TASK-256→262 chain. §6 gives a concrete, specific
next-architecture recommendation (SQLite FTS5/BM25 + reciprocal-rank fusion)
that TASK-259 is expected to test — worth checking in that review that
TASK-259 actually builds on this rather than re-deriving it. §5.5 (temporal
leakage from shared mutable paths like `current-state.md`) is a genuinely
new and non-obvious finding not present in TASK-256/257; flagging it as
worth carrying forward into later design discussions even outside this
retrieval-experiment chain.
