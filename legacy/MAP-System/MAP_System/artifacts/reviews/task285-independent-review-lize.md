# Review: TASK-285 Independent Review - Rework/Attempt 2

- task_id: TASK-285
- reviewer: helper-review-task-285-lize
- task_owner: command-center
- submitter: claude-lab-venu
- reviewed_at: 2026-07-27
- review_claim: `REV-TASK-285-helper-review-task-285-lize`
- predecessor_review: task285-independent-review-nita (CHANGES_REQUESTED)

## Verdict

APPROVED

The rework successfully closes all three REQUIRED findings from nita's original review. The implementation demonstrates correct stale detection across digests, token metrics are properly documented as estimates, and tests comprehensively cover the gaps. The pilot remains appropriately noncanonical with refresh, invalidation, and rollback documentation intact.

## Acceptance Criteria Check

| # | Result | Evidence |
|---|---|---|
| 1 | PASS | Five related tasks verified RELEASED across task JSON, SQLite, and task graph. Eligibility computed as true with verified_released_tasks=5. |
| 2 | PASS | Decisions (2), repeated_failures (5), key_files (8), open_risks (1) all retained with full backlinks to hashed raw evidence. Evidence issues surface one missing_submission_evidence (TASK-199), same as nita found. |
| 3 | PASS | Three-way lifecycle contradictions cause eligibility=false. Missing/stale/anchor-missing evidence is surfaced in evidence_issues. Claims with non-available backlink state are withheld. End-to-end test confirms a mutated source is correctly detected as stale and claim is withheld. |
| 4 | PASS | frozen_evaluation_sha256=`f94aef8b207a37cff9cd90a583351672b713a4be48121c42e1eb04f56c1816d9` matches nita's original report (frozen probes unchanged). Required-fact retention=100%, source traceability=100%, stale-detection accuracy=100%. Token metrics present: raw=442011 tokens, digest=1608 tokens, reduction=99.64%. Byte metrics retained as diagnostic. |
| 5 | PASS | canonical=false, production_routing_enabled=false, raw_evidence_required=true. Refresh documentation names extract_manifest() and prior_manifest pattern. Invalidation rules for lifecycle contradictions and missing backlinks documented. Rollback is by deletion (no task state depends on report). |

## Nita's Three REQUIRED Findings - Verification

### Finding 1: Stale detection on refresh was missing

**Original gap:** `source_ref()` accepted `expected_sha256` param but `build_digest()` never passed one; a real hash change between builds went undetected.

**Fix verification:**
- `build_digest()` now takes `prior_manifest: dict[str, str] | None` parameter (line 326).
- New helper `_expected_for()` looks up prior hashes by display path (lines 286-288).
- Every `source_ref()` call threads `expected_sha256` via `_expected_for()` (lines 341, 350, 390, 407, 417).
- New `extract_manifest()` flattens digest backlinks into {path: sha256} for next build (lines 291-316).
- New `load_prior_digest()` + `--prior-report` CLI flag enable refresh workflow (lines 695-703, 710-712).
- Claims with stale backlinks move to `withheld_claims` (lines 398-401).

**Test coverage:** `test_refresh_detects_stale_claim_source_and_withholds_it` (lines 203-245) proves:
- First build: decision-one-owner present in claims
- Extract prior manifest
- Mutate decisions.md
- Second build WITH prior_manifest: decision-one-owner moved to withheld_claims with state="stale"
- Third build with same prior_manifest: stable (detects mutation, not rebuild)
- Fourth build without prior_manifest: reports as available (proves the gap was real)

**End-to-end reproduction:**
- Initial build of temporary MAP_System, extract prior manifest
- Mutate decisions.md: hash ec78...→ a426...
- Refresh build with prior manifest
- Confirmed: decision-one-owner withheld as stale, not reported available
- ✓ CLOSED

### Finding 2: Reduction metric measured bytes, not tokens

**Original gap:** Implementation reported `context_byte_reduction` only; no tokenization or token count measured.

**Fix verification:**
- New `estimate_tokens()` function (lines 498-499) uses deterministic regex `\w+|[^\w\s]` (word/symbol boundaries).
- New `estimate_value_tokens()` helper (lines 502-503) for JSON serialized values.
- `evaluate()` returns `context_tokens_raw`, `context_tokens_digest`, `context_token_reduction` (lines 605-607).
- Documentation explicitly says "estimate" not "specific model's BPE tokenizer" (lines 489-494, 661-665).
- Byte metrics retained as diagnostic (lines 602-604, 656-658).
- Report shows raw=442011 tokens, digest=1608 tokens, reduction=99.64%.
- Note: No `tiktoken` or other tokenizer library in project venv (claim confirmed as reasonable).

**Test coverage:** 
- `test_token_metrics_are_computed_and_reduce_context` (lines 248-259) asserts tokens present, digest < raw, reduction in (0.0, 1.0), tokens ≠ bytes.
- `test_estimate_tokens_is_deterministic_and_word_symbol_bounded` (lines 261-265) verifies "hello world"→2, "a,b"→3.

**Frozen evaluation section (lines 661-665):**
> "Token counts are a deterministic word/symbol-boundary estimate (`estimate_tokens`), not a specific model's BPE tokenizer -- no tokenizer library is available in this project's venv, and the metric name/report say 'estimate' rather than overclaiming an exact count."

- ✓ CLOSED

### Finding 3: Tests didn't cover either gap

**Original gap:** Existing tests covered synthetic probes and directory manifests but not refresh/mutation or token metrics.

**Fix verification:** Five new tests added to `test_workstream_digest_pilot.py`:
1. `test_refresh_detects_stale_claim_source_and_withholds_it` (lines 203-245) — directly addresses gap 1
2. `test_token_metrics_are_computed_and_reduce_context` (lines 248-259) — directly addresses gap 2
3. `test_estimate_tokens_is_deterministic_and_word_symbol_bounded` (lines 261-265)
4. `test_extract_manifest_only_keeps_hashed_backlinks` (lines 268-287)
5. `test_render_roundtrip_supports_prior_report_refresh` (lines 290-305)

**Test run:** All 10 tests PASS (including original 5):
```
PASS test_contradictory_lifecycle_fails_eligibility_and_is_visible
PASS test_directory_evidence_uses_deterministic_manifest_classification
PASS test_estimate_tokens_is_deterministic_and_word_symbol_bounded
PASS test_extract_manifest_only_keeps_hashed_backlinks
PASS test_frozen_evaluation_and_noncanonical_rules
PASS test_missing_and_stale_evidence_are_not_synthesized_away
PASS test_refresh_detects_stale_claim_source_and_withholds_it
PASS test_render_roundtrip_supports_prior_report_refresh
PASS test_threshold_and_required_evidence_and_is_preserved
PASS test_token_metrics_are_computed_and_reduce_context
```

- ✓ CLOSED

## Files Reviewed

- `MAP_System/scripts/workstream_digest_pilot.py` (730 lines, all sections reviewed)
- `MAP_System/tests/test_workstream_digest_pilot.py` (319 lines, all tests run)
- `MAP_System/artifacts/experiments/task285-workstream-digest-pilot.md` (rendered report)
- `MAP_System/tasks/TASK-285.json` (acceptance criteria)
- Original review: `MAP_System/artifacts/reviews/task285-independent-review-nita.md`

## Verification

- `claim_review("TASK-285", "helper-review-task-285-lize")` — PASS; atomically created review claim before starting.
- `python MAP_System/tests/test_workstream_digest_pilot.py` — PASS, 10/10 tests.
- `python -m py_compile MAP_System/scripts/workstream_digest_pilot.py MAP_System/tests/test_workstream_digest_pilot.py` — PASS.
- Live `build_digest()` with and without `prior_manifest` — both execute without error; stale detection only activates with prior manifest.
- Token estimator: tested "hello world" → 2 tokens, "a,b" → 3 tokens (word/symbol boundary rule confirmed).
- End-to-end stale detection: mutated decisions.md in temporary MAP_System copy, refresh build with prior manifest detected mutation and withheld affected claim.
- Frozen hash: `f94aef8b207a37cff9cd90a583351672b713a4be48121c42e1eb04f56c1816d9` matches nita's original report (probes unchanged).
- Pilot state check: `canonical: false`, `production_routing_enabled: false`, `raw_evidence_required: true` — all correct.

## Forbidden Changes Check

- PASS: Three output_paths exist with expected content:
  - `MAP_System/artifacts/experiments/task285-workstream-digest-pilot.md` (regenerated from live data, frozen_evaluation_sha256 unchanged)
  - `MAP_System/scripts/workstream_digest_pilot.py` (contains all three fixes)
  - `MAP_System/tests/test_workstream_digest_pilot.py` (contains all five new tests)
- PASS: No unauthorized files modified. Only expected output_paths touched.
- PASS: The pilot remains offline/disposable. No task state, decision, runner route, or Command Center startup depends on its output.
- PASS: No helpers were spawned during this review. No unrelated work taken.

## Additional Checks

**Noncanonical status verification:** The report and code both explicitly declare this as an offline, disposable projection:
- `mode: offline_disposable_projection`
- `canonical: false`
- `production_routing_enabled: false`
- Refresh/invalidation/rollback rules documented
- No evidence that this became load-bearing anywhere (TASK-285 is still the only consumer)

**TASK-284 constraint check:** The predecessor's three-way lifecycle agreement is preserved and correctly applied. No changes to the contradiction/fail-closed behavior.

