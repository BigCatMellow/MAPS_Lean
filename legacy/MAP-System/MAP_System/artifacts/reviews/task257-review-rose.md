# Review: TASK-257 Run uncurated fingerprint holdout with typed evidence ranking

task_id: TASK-257
reviewer: claude-lab-rose
task_owner: codex-lab-kiri

## Verdict

APPROVED

Genuinely blinded holdout: truth-set authorship and evaluation were split
across two independently-scoped fresh helpers, neither of which could see
the other's inputs or the ranking implementation. The measured regression
versus TASK-256 (source-exact recall 68.75% → 37.5%) is reported plainly and
correctly drives a "do not integrate" conclusion rather than being explained
away.

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| An independent fresh helper authors the paraphrased query/truth set from an older completed-task corpus before the evaluator or ranking analysis sees it. | PASS | `helper-index-author-2026-07-19.md`: `helper-index-author-bono`, explicitly barred from inspecting ranking code or the generated index, returned truth at hcom event 7014. `task-fingerprint-holdout-queries-2026-07-19.json` has `frozen_at: 2026-07-19T14:05:00-04:00`, `independent_author: helper-index-author-bono`, `author_hcom_event: 7014`. File mtimes confirm ordering: queries file 14:08:06 (after freeze timestamp), evaluator packets 14:09:04 (after queries file). |
| Fingerprints use deterministic task records without owner-curated semantic fields; the source ranker labels evidence roles and what each source can prove. | PASS | `fingerprint_mode: "deterministic task record only; no owner-curated semantic fields"` in the frozen truth file. `test_holdout_fingerprints_are_uncurated` passes. Report §2 lists 11 typed evidence roles (task scope, implementation, test, review, release, decision, current state, outcome, research, guide, general) and §3.2/§5.3 discuss what each role can prove. |
| A different fresh helper receives only the frozen compact retrieval packet, performs no broad search or writes, reports selections/confidence/uncertainty under budget. | PASS | `helper-index-holdout-evaluator-2026-07-19.md`: `helper-index-eval-mono`, distinct identity from the truth-set author, received packets one at a time (H1–H8, events 7055–7171), explicitly barred from the combined packet/index/truth file/task files. Report §7: "no combined packet, index, truth set, task/evidence source, broad repository search, write, or task-state mutation was observed." All 8 packets stayed under the 1,200-token ceiling (§4, max 1,196). |
| Final report compares task/evidence recall/precision, token use, latency, path health, and limitations against TASK-256, preserves negative results, makes no integration claim. | PASS | §3.1 is a direct side-by-side table vs TASK-256. §3.2/§5 analyze both failures (2 task misses, compound-query loss, evidence-role mis-ranking) as negative results, not smoothed over. §5.5 reports broken registered paths found in the wider corpus (TASK-181/182/195/203). §8 explicitly: "Continue a focused experiment; do not integrate the current index." |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Modifying TASK-256 outputs | NOT BROKEN — `task_fingerprint_holdout.py` is a separate script from `task_fingerprint_pilot.py`; TASK-256's artifact files are untouched (verified via `git status` / no overlap in output_paths). |
| Integrating into startup, routing, Command Center, or external services | NOT BROKEN — script only referenced by its own test suite; no references to `graph/runner.py` or Command Center in the new script. |

## Files Reviewed

- `MAP_System/artifacts/experiments/task-fingerprint-holdout-2026-07-19.md` (full)
- `MAP_System/artifacts/experiments/task-fingerprint-holdout-queries-2026-07-19.json` (frozen truth set)
- `MAP_System/inbox/helpers/helper-index-author-2026-07-19.md`
- `MAP_System/inbox/helpers/helper-index-holdout-evaluator-2026-07-19.md`
- `MAP_System/artifacts/experiments/task-fingerprint-holdout-packets-2026-07-19/` (H1–H8)
- `MAP_System/scripts/task_fingerprint_holdout.py`, `MAP_System/tests/test_task_fingerprint_holdout.py`

## Verification

- `python -m py_compile MAP_System/scripts/task_fingerprint_holdout.py MAP_System/tests/test_task_fingerprint_holdout.py` — passes.
- `python -m unittest MAP_System.tests.test_task_fingerprint_holdout -v` — 7/7 passed, matching the report's claimed verification.
- File mtime ordering matches the claimed blinding sequence: `frozen_at` (14:05) → queries file written (14:08:06) → per-query packets generated (14:09:04) → report authored (14:19).
- Confirmed the two helper identities (`helper-index-author-bono`, `helper-index-eval-mono`) are distinct and each note's "Boundaries and stop" section forbids contact with the other helper or inspection of the other's inputs.
- Report's headline regression (source-exact recall 68.75%→37.5%, task recall 100%→77.8%) is consistent with a harder, uncurated, independently-authored holdout and is used to justify continued non-integration, not glossed over.

## Notes

Second task in the TASK-256→262 retrieval chain. This result meaningfully
narrows the design space for TASK-258+ (source-level fingerprints, compound
queries) — later reviews in this chain should check that those follow-ons
actually pick up §6's recommendations rather than re-deriving them from
scratch.
