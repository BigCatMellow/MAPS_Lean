<!-- hpom: file: artifacts/reviews/task263-independent-review-kino.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: mapfinish-kino -->
<!-- hpom: status: CURRENT -->

# Review Record: TASK-263

## Header

```
task_id:      TASK-263
reviewer:     mapfinish-kino
review_date:  2026-07-28
task_owner:   codex-lab-kiri
```

Reviewer (mapfinish-kino) is not the task owner (codex-lab-kiri), the treatment
implementer (claude-lab-lili), or the frozen-holdout author (claude-lab-gabi).
Independence check passes.

---

## Verdict

```
CHANGES_REQUESTED
```

---

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Independent helper freezes fresh questions/evidence/negatives before treatment; **a different helper evaluates blinded results after implementation**. | PARTIAL | Freeze half verified independent: `helper-index-claim-holdout-2026-07-19.md` documents `claude-lab-gabi` authoring the holdout with no access to any treatment (none existed at freeze time), disjoint corpus range (TASK-001-099 + TASK-250-266 minus TASK-256-262) from three prior holdout attempts, and freeze sha256 `635aa5f0b41...` matches the file on disk today (`sha256sum` re-verified). **Blind-evaluation half did not happen**: no second helper scored the results; `claude-lab-lili` (the implementer) self-scored. `helper-index-claim-evaluator-2026-07-19.md` is listed in the task's `output_paths` but does not exist on disk. The gap is prominently disclosed in both EXP-0006 and the JSON payload's `blind_evaluation_disclosure` field, and `soba` (the reserved blind evaluator) is confirmed absent from `MAP_System/map.db`'s `agents` table as of this review. Mitigating: the scorer is fully mechanical (exact string/path comparison against frozen fields, no subjective judgment), and I independently re-ran `task_memory_claim_evidence_pilot.py` from a clean shell and reproduced the identical reported numbers byte-for-metric (see criterion 3). This substitutes partial independent verification for blind scoring, but literal criterion 1 is not met. |
| 2 | Claim-evidence units carry exact anchor, proof role, source hash, time watermark; positive proof and negative boundaries indexed/scored separately, never act as authority. | PASS | Read `task_memory_claim_evidence_pilot.py:207-321` (`build_claim_cards`): each card carries `anchor_type`/`anchor` (code symbol via `ast.walk` or Markdown heading via regex), `role` (via `task_fingerprint_holdout.evidence_role`), `current_sha256` (explicitly labeled drift-only, never historical proof, in the module docstring and `authority` field), and `watermark_utc` from `read_events_watermarks`. Negatives are real capability gaps (verified by the holdout author via grep, not constructed absences) so there is no negative-card type to co-mingle with positive cards; abstention is a score/coverage/polarity gate in `retrieve()`, not an authority claim. `authority` field on the JSON payload explicitly disclaims production authority. |
| 3 | Report recall, exact-source/anchored accuracy, abstention, historical-version correctness, substitutes, packet size, authoring cost, parser coverage vs 18/20 and 12/12 baselines. | PASS | `task-memory-claim-evidence-development-2026-07-19.json/.md` contain all named fields. I re-ran `MAP_System/.venv/bin/python MAP_System/scripts/task_memory_claim_evidence_pilot.py` after independently verifying the holdout's sha256 (`635aa5f0b41bdded414fac6b6a7cf82cb2841395751813ad6213619eb0f75e3f`, matches `HOLDOUT_EXPECTED_SHA256` in the script) and reproduced identical output: task_recall 12/23, exact_source_accuracy 17/41, anchored_evidence_accuracy 7/41, abstention 2/5 (3 false positives), historical_version_correctness 2/3 — all below the 18/20 / 12/12 baselines as reported, no discrepancy found. |
| 4 | Focused tests cover unit extraction, claim-card validation, positive-vs-boundary isolation, deterministic ranking, **source-hash drift**, **acceptable evidence sets**, and abstention; TASK-260-262 hashes/artifacts unchanged. | FAIL (partial) | Ran `MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_task_memory_claim_evidence_pilot -v`: 9/9 pass, covering claim-card attribution (unique link, inline tag, version-header, acceptance-text fallback, deterministic tie-break), polarity (enable/block/neutral), watermark selection, one end-to-end positive+negative case, and holdout-hash-mismatch refusal. **`grep -n "sha256\|substitute\|acceptable" test_task_memory_claim_evidence_pilot.py` returns zero matches** — two of the seven named test categories (source-hash drift, acceptable evidence sets) have no test at all, not even partial coverage; the `current_sha256` field and `acceptable_substitute_hits_on_missed_queries` scoring path in `evaluate()` are exercised only implicitly by the one full end-to-end holdout run, never by a unit test. TASK-260-262 outputs verified unchanged (see Forbidden Changes Check). |

---

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Do not modify TASK-260 through TASK-262 scripts, tests, reports, or frozen result artifacts. | NOT BROKEN — `task_fingerprint_pilot.py`, `task_fingerprint_holdout.py`, `task_memory_capsule_pilot.py`, `task_memory_packet_selector.py`, and the TASK-260/261/262 experiment artifacts (`task-memory-capsule-development-*`, `task-memory-evidence-verifier-development-*`) all carry filesystem mtimes of 2026-07-19, predating this task's 2026-07-27/28 work; TASK-263's own script only imports them read-only. |
| Do not integrate the experiment into production retrieval, startup, routing, UI, task authority, or canonical policy. | NOT BROKEN — repo-wide grep for `task_memory_claim_evidence_pilot`/`task-memory-claim-evidence` outside the task's own output paths returns only `workflow/task_graph.json` (the task-graph mirror) and the prior freeze handoff note; no startup/routing/policy file references it. |
| Do not add embeddings, external services, a learned reranker, or a knowledge graph. | NOT BROKEN — retrieval is a from-scratch TF-IDF-style lexical scorer (`ClaimIndex`) over local corpus text; no network or model calls in the script. |
| Do not author treatment against evaluation questions before the holdout is independently frozen. | NOT BROKEN — `helper-index-claim-holdout-2026-07-19.md` confirms no treatment file or draft existed at freeze time (2026-07-22), and treatment file mtimes (2026-07-27) postdate the freeze. |

---

## Files Reviewed

- `MAP_System/scripts/task_memory_claim_evidence_pilot.py`
- `MAP_System/tests/test_task_memory_claim_evidence_pilot.py`
- `MAP_System/artifacts/experiments/task-memory-claim-evidence-development-2026-07-19.json`
- `MAP_System/artifacts/experiments/task-memory-claim-evidence-development-2026-07-19.md`
- `MAP_System/artifacts/experiments/task-memory-claim-evidence-holdout-2026-07-19.json` (hash-verified, not content-audited line-by-line)
- `MAP_System/inbox/helpers/helper-index-claim-holdout-2026-07-19.md`
- `MAP_System/emergence/experiments/EXP-0006-a-frozen-holdout-can-test-claim-evidence-units-against-capsules-.md`
- `MAP_System/tasks/TASK-263.json`

---

## Scope Check

| Changed file | In scope? |
|---|---|
| `MAP_System/scripts/task_memory_claim_evidence_pilot.py` | YES — listed output path |
| `MAP_System/tests/test_task_memory_claim_evidence_pilot.py` | YES — listed output path |
| `MAP_System/artifacts/experiments/task-memory-claim-evidence-development-2026-07-19.{json,md}` | YES — listed output path |
| `MAP_System/artifacts/experiments/task-memory-claim-evidence-holdout-2026-07-19.json` | YES — listed output path, authored by disqualified-independent helper before this attempt |
| `MAP_System/emergence/experiments/EXP-0006-...md` | YES — listed output path |
| `MAP_System/inbox/helpers/helper-index-claim-evaluator-2026-07-19.md` | NOT CREATED — see Findings |

---

## Risk Identification

| Risk | Severity | Recommended action |
|---|---|---|
| Reported metrics are implementer-self-scored, not blind-evaluated | MEDIUM | Mitigated this round by independent reproduction (this review) and full disclosure; a genuinely separate scorer should still run before any future promotion attempt. |
| Two of two free thresholds (`MIN_TASK_SCORE`, `MIN_COVERAGE_RATIO`) were tuned while watching aggregate holdout metrics during development | LOW-MEDIUM | Disclosed plainly in EXP-0006's Result section; does not change the decision (still below baseline even with the tuning advantage, which if anything means true generalization is likely worse than reported). Next iteration should use a margin-based abstention rule instead of hand-tuned aggregate thresholds, as EXP-0006's Decision section already proposes. |
| Untested code paths (`current_sha256` drift semantics, `acceptable_substitute_hits` scoring) could silently misbehave and nobody would notice via CI | MEDIUM | See REQUIRED finding below. |

---

## Findings

| Severity | File | Section | Finding | Required action |
|---|---|---|---|---|
| REQUIRED | `MAP_System/tests/test_task_memory_claim_evidence_pilot.py` | whole file | Acceptance criterion 4 explicitly names "source-hash drift" and "acceptable evidence sets" as required test coverage; neither appears anywhere in the delivered test file (confirmed via `grep -n "sha256\|substitute\|acceptable"` returning zero matches). The `current_sha256` field and the `acceptable_substitute_hits_on_missed_queries` computation in `evaluate()` are exercised only end-to-end via one full holdout run, never by a targeted unit test. | Add at least one focused test for source-hash drift (e.g., build a card, mutate the source file, rebuild, assert `current_sha256` changes and is never treated as historical proof) and one for acceptable-substitute scoring (a query whose primary expected source is missed but whose `acceptable_substitutes` entry is returned should count as a substitute hit, per `evaluate()`'s `sub_hit` logic at pilot.py:522-529). |
| RECOMMENDED | `MAP_System/inbox/helpers/helper-index-claim-evaluator-2026-07-19.md` | (missing) | This file is listed in TASK-263's `output_paths` and in `expected_artifacts` ("evaluator notes") but was never created, because no blind evaluator was available. This is consistent with the disclosed blind-evaluation gap (see Acceptance Criteria #1) rather than an oversight, but the missing deliverable should be tracked explicitly rather than left as a silent gap between the task record and the filesystem. | When a blind evaluator becomes available for a future iteration, write this note (or formally drop it from `output_paths` if the task is closed out as "revise" without further attempts). |
| RECOMMENDED | `MAP_System/tests/test_task_memory_claim_evidence_pilot.py` | `EndToEndTests` | Only Python (`.py`, via `ast`) symbol extraction is exercised end-to-end; the Markdown-heading extraction path (`HEADING_RE` branch in `build_claim_cards`) has no dedicated test, even though roughly half of claim cards in the real run come from `.md` files (per `cards_by_source_suffix` in the development JSON). | Add one end-to-end test using a small synthetic Markdown file with a heading, mirroring the existing `widget.py` case. |

No BLOCKER findings — nothing here is unsafe, data-losing, or a production-integration violation.

---

## Notes

- Attempt context: TASK-263 is at attempt 3/3 (`max_attempts=3`, confirmed via `map.db`). This review reports the two REQUIRED/RECOMMENDED test-coverage gaps honestly regardless of attempt-cap consequences, per explicit operator instruction relayed by `claude-lab-lili`; the operator has separately indicated willingness to grant a repair-style extension if genuinely blocking issues are found.
- The experiment's own Decision (`revise`, not `adopt`) is not being second-guessed here — the reported numbers are below the 18/20 / 12/12 baselines and the report says so plainly. This review's CHANGES_REQUESTED verdict is about the **deliverable's compliance with its own stated acceptance criteria** (test coverage gap), not about whether the underlying experiment idea should be pursued further. The historical-attribution mechanism genuinely resolving 2/3 temporal-trap queries to the correct originating task (vs. naive newest-file attribution) is a real, verified positive result within an overall miss.
- No evidence of treatment leakage, authority duplication, or production wiring was found. Frozen-holdout hash matches exactly. TASK-260-262 artifacts are untouched (verified via mtimes, since the whole repo currently has an unrelated pending reorg-move diff that makes `git diff` unusable as a signal here).
