# Review: TASK-285 Independent Review

- task_id: TASK-285
- reviewer: codex-lab-nita
- task_owner: command-center
- submitter: task285-replacement-solo
- reviewed_at: 2026-07-26
- review_claim: `REV-TASK-285-codex-lab-nita-563cb3b9`
- prerequisite_constraint: TASK-284 final re-review approved three-way lifecycle agreement and fail-closed contradiction handling

## Verdict

CHANGES_REQUESTED

The pilot is well bounded and noncanonical, but two required evaluation
properties are not implemented: actual refreshes cannot detect stale evidence,
and the frozen reduction metric measures bytes rather than tokens.

## Acceptance Criteria Check

| # | Result | Evidence |
|---|---|---|
| 1 | PASS | The report declares one bounded workstream, a threshold of five related tasks, and verifies all five as `RELEASED` across task JSON, read-only SQLite, and task graph. |
| 2 | PASS with surfaced gap | Decisions, repeated failures, key files, unresolved risk, task/review/submission/source references, hashes, and evidence issues are retained. Live evidence correctly surfaces the missing TASK-199 submission instead of inventing one. |
| 3 | PARTIAL / FAIL | Three-way lifecycle contradictions are surfaced and make eligibility false; missing and anchor-missing evidence is withheld. However, after a previously captured primary-source hash changes, a normal `build_digest()` rebuild returns the new source as `available` and emits no stale issue because no prior digest/hash is supplied. Only the synthetic `detect_probe()` sees stale values. |
| 4 | FAIL | Required-fact retention, source traceability, and synthetic health probes pass at 100%. The frozen metric is `context_byte_reduction`, calculated from serialized byte lengths; no tokenization or token count is measured. |
| 5 | PASS | The report explicitly declares `canonical: false`, disables production routing, documents refresh/invalidation, requires independent review before proposal, and gives disposable-report rollback rules. TASK-284’s approved three-source contradiction boundary is preserved. |

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/scripts/workstream_digest_pilot.py:source_ref`, `MAP_System/scripts/workstream_digest_pilot.py:build_digest` | Refresh has no prior evidence manifest or expected-hash input. A primary source changed between two builds was returned as `state=available` with its new hash and no stale issue. The report's refresh rule says backlink hash changes require refresh, but the implementation cannot identify that change as stale. | Add an explicit prior/frozen manifest input (or equivalent comparison against the previous digest) and carry expected hashes into `source_ref`; emit structured stale evidence and withhold affected claims/results until reviewed. Add a regression that builds, mutates a source, rebuilds, and asserts stale detection. Preserve the three-way TASK-284 fail-closed lifecycle behavior. |
| REQUIRED | `MAP_System/scripts/workstream_digest_pilot.py:evaluate`, `MAP_System/scripts/workstream_digest_pilot.py:render`, `MAP_System/artifacts/experiments/task285-workstream-digest-pilot.md:Frozen Evaluation` | Criterion 4 requires token reduction against raw context, but the implementation and report measure only serialized context bytes (`context_bytes_raw`, `context_bytes_digest`, `context_byte_reduction`). Byte reduction is not token reduction and can vary materially with encoding/content. | Add a deterministic token-counting method and frozen token metrics for raw versus digest context (retaining byte metrics only as an additional diagnostic if useful). Update the report and focused tests to assert token reduction and its frozen inputs. |
| REQUIRED | `MAP_System/tests/test_workstream_digest_pilot.py` | Existing tests cover synthetic stale probes and deterministic directory manifests, but do not exercise stale detection across a digest refresh and do not assert token metrics. They therefore pass while both required gaps remain. | Add focused refresh/mutation and token-metric tests, and ensure the delivery note/report evidence names those tests. |

## Files Reviewed

- `MAP_System/tasks/TASK-285.json`
- `MAP_System/events/events.jsonl` (TASK-285 `SUBMISSION` at `2026-07-26T19:58:41Z`)
- `MAP_System/artifacts/experiments/task285-workstream-digest-pilot.md`
- `MAP_System/scripts/workstream_digest_pilot.py`
- `MAP_System/tests/test_workstream_digest_pilot.py`
- `MAP_System/tasks/TASK-284.json`
- `MAP_System/artifacts/reviews/task284-final-rereview-romi.md`
- `MAP_System/notes/review-guide.md`

## Verification

- `claim_review("TASK-285", "codex-lab-nita")` — PASS; atomically created `REV-TASK-285-codex-lab-nita-563cb3b9` before writing this artifact.
- `python MAP_System/tests/test_workstream_digest_pilot.py` — PASS, 5/5 focused tests.
- `python -m py_compile MAP_System/scripts/workstream_digest_pilot.py MAP_System/tests/test_workstream_digest_pilot.py` — PASS.
- Live `build_digest()` / `evaluate()` — eligibility true for five tasks; evidence issue `missing_submission_evidence` for TASK-199 is surfaced; required-fact retention 100%, source traceability 100%, synthetic stale/health accuracy 100%, `canonical=false`, `production_routing_enabled=false`.
- Independent task JSON, SQLite, and task-graph mismatch fixtures — each produced `eligible=false`, `contradictory=true`, and source-specific status details.
- Directory-manifest fixture — nested file mutation changed the manifest SHA-256 and returned `state=stale` when checked against the prior expected hash.
- Refresh mutation probe — primary source changed from `284ec8aaf4ba3f9c1c33f4c4d35a73fad058dbde87841d9cd26b9e679244b780` to `42667f170d3f52816db46ccfdec499675beff1a982f6a73cb53eaa29255a8d5e`; a normal rebuild returned `available` and produced no stale issue.
- Frozen hash — implementation recomputes the report's declared `f94aef8b207a37cff9cd90a583351672b713a4be48121c42e1eb04f56c1816d9`, confirming the static probe inputs are reproducible; this does not cure the missing refresh comparison.
- `validate_task_schema.py` and `validate_task_mirrors.py --db MAP_System/map.db --root MAP_System` — PASS.

## TASK-284 Constraint Check

The predecessor's final re-review approved three-way agreement among task JSON,
read-only SQLite, and task graph before a released fingerprint becomes
searchable, with typed contradiction records and fail-closed abstention. TASK-
285 applies the same three-source lifecycle check to eligibility and makes
contradiction visible; no production routing or canonical promotion is enabled.

## Forbidden Changes Check

- PASS: No TASK-285 implementation or registered output was edited by this reviewer.
- PASS: Mutation probes used temporary fixtures only; the submitted report was not regenerated.
- PASS: The pilot remains offline/disposable, and no task, decision, runner, or Command Center state depends on its output.
- PASS: No helpers were spawned and no unrelated work was taken.

