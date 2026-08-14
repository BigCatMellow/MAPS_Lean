# Review: TASK-262 Prototype structured retrieval capsules for durable Markdown

task_id: TASK-262
reviewer: claude-lab-rose
task_owner: codex-lab-kiri

## Verdict

APPROVED

Clean, additive-only convention with a real parser/validator (not just a
style guide), applied to six live documents and self-validated by its own
test suite against those real files. The measured gain (16/20 → 18/20 exact
source visibility on known development data) is modest and honestly scoped
as non-generalizing development data, with a correctly identified new risk
(capsule staleness) and a correctly identified danger in `Does not provide`
being usable as false positive-evidence — both flagged rather than glossed
over.

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| Capsule convention is human-readable, 60–120 words, uses required six fields in order, remains descriptive metadata not authority. | PASS | `MAP_System/notes/retrieval-capsule-guide.md` §"Required shape" specifies the exact heading/field order; the guide's own capsule is a live, real instance of the format (read directly, matches the six-field shape). §"Purpose" states explicitly: "It never overrides the document body, SQLite task state, decisions, review records, release gates, or operator authority." |
| Parser/validator rejects duplicate capsules, missing/unknown fields, invalid evidence types/status, excessive length, empty boundaries; documents without capsules are valid fallbacks. | PASS | `test_duplicate_heading_is_rejected`, `test_missing_unknown_and_out_of_order_fields_are_rejected`, `test_invalid_type_status_and_short_boundary_are_rejected`, `test_excessive_and_too_short_capsules_are_rejected`, `test_missing_capsule_is_valid_fallback`, `test_example_heading_inside_fence_is_ignored` — all 6 pass, matching this criterion's 6 named failure modes exactly. |
| ≥6 representative Markdown documents get capsules via additive-only edits; body prose preserved; each capsule states limitations/non-authority boundaries. | PASS | Exactly 6 documents listed in the report's table, spanning governing rule / procedure / measured outcome / test evidence roles. `grep` confirms each capsule begins within the first 13 lines of its file (well inside the 40-line placement rule) with substantial body content following. `test_all_six_pilot_documents_have_valid_capsules` validates the live files, not synthetic fixtures. |
| Capsule-aware pilot leaves TASK-261 code/tests/results byte-for-byte unchanged; allocates ≤3 query-global sources; records capsule-vs-fallback provenance; compares against the recorded 16/20. | PASS | `sha256sum MAP_System/scripts/task_memory_packet_selector.py` = `1c33ed6c...`, matching TASK-261's frozen value exactly. Report §"Known-development comparison" directly compares against "TASK-261 recorded" 16/20 column, with provenance ("6 of 24 selected source slots used validated capsules"). |
| Focused tests cover parsing, validation, no-capsule fallback, role/boundary scoring, deterministic allocation, stale/current attribution; report covers benefits, authoring cost, staleness risk, negative-query implications, fresh-holdout recommendation, no integration/embedding claim. | PASS | 11 tests map to all named categories (`ScoringTests.test_status_bonus_preserves_temporal_warning` covers stale/current; `ScoringTests.test_fallback_and_allocation_remain_deterministic` covers deterministic allocation). Report §"Negative-query and temporal limitations" explicitly warns `Does not provide` text could be misread as positive evidence by a naive lexical system. §"Candidate freeze" — explicit freeze-for-holdout, no integration claim. |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Rewriting existing body prose in the six documents | NOT BROKEN — capsule insertion is a small additive block near the top; remaining file content in each document is substantial pre-existing prose (e.g. `AGENTS.md` 363 lines, `task-214-combat-parity.md` 191 lines), consistent with additive-only editing. |
| Modifying TASK-260/TASK-261 results byte-for-byte | NOT BROKEN — `task_memory_packet_selector.py` hash matches TASK-261's frozen value exactly; report imports rather than edits it. |
| Integrating capsules into startup, canonical authority, routing, UI, embeddings, external services, or every Markdown file | NOT BROKEN — only 6 documents touched (not repo-wide); report explicitly: "It does not show that all Markdown should be rewritten... Adding capsules indiscriminately would create maintenance load without retrieval value." |

## Files Reviewed

- `MAP_System/artifacts/experiments/task-memory-capsule-development-2026-07-19.md` (full)
- `MAP_System/notes/retrieval-capsule-guide.md`
- `MAP_System/scripts/task_memory_capsule_pilot.py`, `MAP_System/tests/test_task_memory_capsule_pilot.py`
- The six capsule-bearing documents: `MAP_System/AGENTS.md`, `MAP_System/notes/practice-scenario-runbook.md`, `MAP_System/artifacts/tests/rns-persistent-supervisor.md`, `MAP_System/artifacts/tests/local-ollama-advisory-lane-test-2026-07-18.md`, `Projects/ClearFront/artifacts/tests/task-214-combat-parity.md`, `MAP_System/artifacts/experiments/map-kickoff-alignment-scenario-2026-07-18.md`

## Verification

- `python -m py_compile MAP_System/scripts/task_memory_capsule_pilot.py MAP_System/tests/test_task_memory_capsule_pilot.py` — passes.
- `python -m unittest MAP_System.tests.test_task_memory_capsule_pilot -v` — 11/11 passed.
- `python -m unittest` across capsule + selector + retriever + holdout-harness test modules together — 32/32 passed, exactly matching the report's "32 total capsule, selector, frozen retriever, and holdout-harness tests passed" claim.
- `sha256sum` confirms the guide, parser/scorer, and tests match the frozen hashes recorded in the report's "Candidate freeze" section, and that the TASK-261 selector remains byte-for-byte unchanged.
- Confirmed all six capsule headers appear within the first 13 lines of their respective files (well inside the guide's 40-line placement rule) via `grep -n`.

## Notes

Sixth and final task in the TASK-256→262 retrieval-experiment chain. Taken
together, TASK-256→262 form a genuinely disciplined research sequence: each
step's negative results were carried forward and addressed by the next
(curated→uncurated holdout, path-slice→typed roles→source fingerprints,
fixed evidence slots→query-global budget, hand-rolled lexical→FTS5/BM25,
unstructured Markdown→capsules), none were integrated prematurely, and every
holdout in the chain used real author/evaluator blinding with hash-verified
frozen implementations. This is the standard the chain should be held to
going forward.
