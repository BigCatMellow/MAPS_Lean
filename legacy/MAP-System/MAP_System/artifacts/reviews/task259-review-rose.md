# Review: TASK-259 Build and benchmark a temporal-safe FTS5 memory index

task_id: TASK-259
reviewer: claude-lab-rose
task_owner: codex-lab-kiri

## Verdict

APPROVED

An engineering task, correctly scoped as development-only: this task's own
acceptance criteria only require scoring the *known* TASK-257/258 truth sets
as labeled development regressions and freezing the implementation for a
later blinded holdout (expected next in the chain) — no fresh author/evaluator
blinding was required here, and none was claimed. The report directly
addresses TASK-258's §5.5 temporal-leakage finding with a real schema fix
(separate `source_documents` vs `task_source_links`) rather than a superficial
patch.

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| Disposable SQLite schema stores one source document per unique normalized path plus explicit task/source links and temporal-attribution labels; multiply-linked mutable current content is not cloned into historical task semantics. | PASS | §2 defines four temporal modes (`task_snapshot`, `current_unique`, `current_shared`, `unresolved`) with explicit RRF weights, directly answering TASK-258 §5.5's "three layers" recommendation. `test_current_shared_content_is_not_cloned_into_task_fts` and `test_unique_source_document_and_explicit_shared_links` pass. |
| Weighted FTS5 task/source fields, path/identifier channel, bounded deterministic subqueries, and RRF implemented with no package/model/network/runtime/router/UI/canonical-authority dependency. | PASS | §1.1 describes `task_fts`/`source_fts`/`path_fts` (Porter + BM25 + trigram) and RRF with k=60 explicitly to avoid mixing raw scores across channels. `test_rrf_is_deterministic_and_does_not_mix_raw_scores`, `test_path_trigram_channel_finds_identifier_substring`, `test_compound_parts_are_bounded_and_preserve_question_clauses` pass. §8: "No startup, router, UI, external service, canonical database schema, or agent workflow was changed." Database is built in a temp dir and discarded (§1). |
| Focused tests cover deterministic rebuild/query, shared-source temporal handling, RRF, compound retrieval, path health, abstention. | PASS | `test_rebuild_produces_same_query_order`, `test_unresolved_source_keeps_visible_path_health`, `test_no_match_abstains` all present and passing alongside the above. 9/9 tests pass, matching the report's §5 claim. |
| Known TASK-257/258 truth sets scored as development regressions only; report covers metrics, compound/negative behavior, latency, size, failure analysis, frozen-implementation handoff, no adoption claim. | PASS | §3 tables clearly labeled "development regression" and §6 has an explicit section titled "Development choices that must not be mistaken for holdout evidence." §4 has build/query latency and DB size for both corpora. §3.2/§3.3 keep reporting real misses (H3/H5/H7, S6) instead of hiding them. §8: "It is still not ready for use... freeze this FTS5/RRF baseline for fresh evaluation." No claim of adoption anywhere. |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Integration into startup, routing, Command Center, canonical authority, or external services | NOT BROKEN — §8 explicit disclaimer; database is ephemeral/temp-dir only, script only referenced by its own test suite. |

## Files Reviewed

- `MAP_System/artifacts/experiments/task-memory-fts5-rrf-development-2026-07-19.md` (full)
- `MAP_System/scripts/task_memory_fts.py`, `MAP_System/tests/test_task_memory_fts.py`

## Verification

- `python -m py_compile MAP_System/scripts/task_memory_fts.py MAP_System/tests/test_task_memory_fts.py` — passes.
- `python -m unittest MAP_System.tests.test_task_memory_fts -v` — 9/9 passed, matching the report's §5 claim exactly.
- `sha256sum` of both files matches the frozen hashes recorded in §0 (`edd0b53a...`, `58df22f4...`) — implementation has not drifted since the report was written, consistent with the "freeze for later holdout" claim.
- Cross-checked §3.1's comparison table against TASK-257/258's own approved review numbers (7/9→9/9 task recall, 10/16→13/16 source visibility) — consistent, no inflated baseline.

## Notes

Fourth task in the TASK-256→262 chain. This is a development/engineering
step, not a scored holdout — TASK-260 (per its title, "blinded holdout") is
where the fresh-author/blinded-evaluator protocol from TASK-257/258 should
reappear against this frozen FTS5/RRF implementation. Will check in the
TASK-260 review that the implementation hash actually carried forward
unchanged from this freeze.
