# Review: Emergence Coverage Scheduling (`map_emergence.py coverage`)

Author under review: claude-lab-niko (self-review forbidden; this is the required
independent pass). No task record exists for this work — it was implemented
directly off `SUMMARY-external-blueprint-gap-review-2026-07-21.md` because the
implementing agent could not write `map.db` to open a task. Reviewed as a
standalone change against that SUMMARY's stated intent.

## Verdict

APPROVED (updated 2026-07-21, second pass)

Original verdict was CHANGES_REQUESTED on one REQUIRED finding. niko fixed it
same-day; I re-reviewed the actual diff (not just the claim) and reran every
verification command. See "Second-pass verification" below. The two
RECOMMENDED findings stand: one is fixed, one is explicitly and reasonably
deferred with a stated rationale I accept.

### Original verdict (superseded, kept for history)

CHANGES_REQUESTED — one REQUIRED finding (below). Everything else about the
implementation was sound: honest debt model, accurate README, correct
self-review avoidance, and 6 tests that genuinely pinned the contract. The
required fix was small and localized — not a design do-over.

## Reviewed Files

- `MAP_System/scripts/map_emergence.py` — `coverage` subcommand and helpers
  (`coverage_state_path`, `load_coverage_state`, `save_coverage_state`,
  `parse_iso_date`, `coverage_entries`, `mark_reviewed`, `coverage`, CLI parser
  block)
- `MAP_System/tests/test_map_emergence.py` — 6 new `test_coverage_*` tests
- `MAP_System/emergence/README.md` — new coverage section
- `MAP_System/artifacts/research/SUMMARY-external-blueprint-gap-review-2026-07-21.md`
  — motivating analysis (fact-checked, not code-reviewed)

## Findings

| Severity | File | Finding | Status |
|---|---|---|---|
| REQUIRED | `MAP_System/scripts/map_emergence.py` (`CLOSED_ARTIFACT_STATUSES`, used by `coverage_entries`) | The closed-status set was shared across all 5 kinds but wasn't kind-aware: `"COMPLETE"` (EXP-0004/EXP-0005's actual status) was absent, so both would have generated false-positive overdue debt around 2026-08-01; and `"APPROVED"` is terminal for promotions but legitimately mid-ladder for experiments (`PROPOSED -> APPROVED -> RUNNING -> ...`), so an experiment reaching `APPROVED` would have vanished from coverage forever — the exact blind spot the feature exists to catch. | **FIXED.** `coverage_closed_statuses(kind)` now layers `COVERAGE_CLOSED_ADDITIONS`/`COVERAGE_CLOSED_EXEMPTIONS` per kind on top of the untouched shared `CLOSED_ARTIFACT_STATUSES`, so `stale` is unaffected. Adds `COMPLETE`+`REVIEWED` as terminal for experiments (niko caught `REVIEWED` as the same-class miss I hadn't flagged — one experiment currently uses it), `COMPLETE` for promotions, and exempts `APPROVED` for experiments. New regression test `test_coverage_closed_statuses_are_kind_aware` seeds all four cases (COMPLETE/REVIEWED/APPROVED experiments + an APPROVED promotion) and asserts only the mid-ladder APPROVED experiment still accrues debt. Verified independently below. |
| RECOMMENDED | `MAP_System/scripts/map_emergence.py` (`load_coverage_state`/`save_coverage_state`) | `coverage.json` read-modify-write has no lock, unlike `id_allocation_lock`'s identical-risk-class precedent two functions above it in the same file. | **Deferred, accepted.** niko's rationale: the race only fires on two concurrent `--mark-reviewed` invocations (not the read path or automation), and the same "not concurrency-safe for a second writer" problem exists in `db/claims.py` (the `ensure_agent` gap from my prior review, see memory `claim-review-missing-ensure-agent`) — bundling the two lock fixes into one pass is cheaper than fixing this one in isolation. This was RECOMMENDED, not REQUIRED, in the original pass (self-healing, no corruption, no crash), so I agree deferral is reasonable. Not re-blocking on it. |
| OPTIONAL | `MAP_System/emergence/README.md` | Date-header fallback for "never reviewed" age is disclosed in the code docstring but not the README's coverage section. | Not addressed this pass; optional, doesn't block. |
| RECOMMENDED | `MAP_System/tests/test_map_emergence.py` | Original 6 tests didn't cover multi-kind closed-status interaction, sort order, `--limit` truncation, or `mark_reviewed`'s partial-list abort path. | Multi-kind closed-status gap now covered by `test_coverage_closed_statuses_are_kind_aware` (18/18 pass in this file). Sort-order/`--limit`/partial-abort gaps remain untested but unchanged from original assessment — not blocking. |
| RECOMMENDED | `MAP_System/artifacts/research/SUMMARY-external-blueprint-gap-review-2026-07-21.md` | Insight status table (sum 38) didn't match actual 36 files; `OPEN` status (6 insights) missing entirely. | **FIXED.** Corrected in place to `PROMOTED 12/RAW 10/OPEN 6/CLARIFIED 3/DISMISSED 2/PARKED 1/LINKED 1/CAPTURED 1 = 36`, with a visible dated correction note naming the root cause (grepped `INDEX.md` across all kinds while labelling rows "insights") and crediting the review rather than silently patching it. Verified the corrected numbers against a fresh count below. |

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_map_emergence.py` — all 17 tests pass, including the 6 new `test_coverage_*` tests.
- `bash MAP_System/scripts/run_tests.sh` — `SUMMARY pass=68 fail=2 total=70`, exact match to the number the task described as pre-existing.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_events.py` and `.../validate_layer1.py` run directly — both failures trace to the identical root cause: `WARN-NEW line 2145: non-canonical event type TASK_SUBMITTED` (`sender: codex-lab-kiri`, `created_at: 2026-07-19T18:19:31Z`). Confirmed **not attributable** to this change: `git diff HEAD~1` for `map_emergence.py` touches only additive coverage code; `events.jsonl`, `validate_events.py`, and `validate_layer1.py` are untouched by this diff.
- `MAP_System/.venv/bin/python MAP_System/scripts/map_emergence.py coverage` — live run against the real repo reproduces the SUMMARY's cited output exactly: `9 of 39 open records unreviewed for >= 14 days`, same 9 IDs (INS-0008, INS-0009, SYN-0001, IDEA-0009, IDEA-0013, INS-0017..0020), same statuses and ages. Confirms the shipped code, not just the SUMMARY's prose, produces this result.
- Verified `stale` vs `coverage` really are non-duplicative by reading `stale_findings` (flags a record only when its *related task* status contradicts the artifact's status) against `coverage_entries` (flags by age since last review regardless of related task) — the README's stated distinction is accurate.
- Verified `CLOSED_ARTIFACT_STATUSES` correctly does NOT swallow `APPROVED_FOR_EXPERIMENT` (idea) via exact-string set membership — confirmed by IDEA-0013 (`APPROVED_FOR_EXPERIMENT`) correctly appearing as overdue in the live run above. The REQUIRED finding is specifically about the *experiment* kind's own `APPROVED` (no underscore suffix) colliding with promotion's terminal `APPROVED`.
- Cross-checked other SUMMARY claims against the repo directly: `map.db` has 17 tables (confirmed via `sqlite_master` count); `tasks` columns match exactly as listed, no `risk_level` or WAITING fields (confirmed via `PRAGMA table_info`); `helper_capacity` maximum is 4 (confirmed: `MAP_System/workflow/runtime_policy.yaml:19` → `maximum_active_helpers: 4`); INS-0023 exists and is on-topic. The "12 SUBMITTED" / "TASK-250 never recorded" claims are now stale (actual SUBMITTED count is 6; TASK-250 is APPROVED with review record `REV-TASK-250-claude-lab-rose-4fae2df7` dated 2026-07-21T17:38:31Z) — this reflects normal backlog processing by other agents during this review window, not a SUMMARY error; the SUMMARY itself flags this class of claim as fast-decaying.

## Second-pass verification (2026-07-21)

- Read the actual diff, not just niko's description: `coverage_closed_statuses()` layers `COVERAGE_CLOSED_ADDITIONS`/`COVERAGE_CLOSED_EXEMPTIONS` on a `frozenset(CLOSED_ARTIFACT_STATUSES)` copy and is the only caller changed in `coverage_entries` — confirmed `stale_findings` and `is_active_artifact`/`compact` still read the original untouched `CLOSED_ARTIFACT_STATUSES`, so the fix is scoped to `coverage` exactly as claimed, no side effects on `stale`.
- `MAP_System/.venv/bin/python MAP_System/tests/test_map_emergence.py` — 18/18 pass, including the new `test_coverage_closed_statuses_are_kind_aware`.
- `bash MAP_System/scripts/run_tests.sh` — still `pass=68 fail=2`, and the 2 failures are still the identical pre-existing `validate_events_no_new_warnings` / `validate_layer1_test`, both still tracing to the same `WARN-NEW line 2145` (unchanged, confirmed not touched by this fix either).
- `MAP_System/.venv/bin/python MAP_System/scripts/map_emergence.py coverage --json` on the real repo: `open_records` dropped 39 → 35 (the 4 no-longer-miscounted COMPLETE/REVIEWED experiment+promotion records), `overdue` unchanged at 9 — confirms the fix removed only false "open" bookkeeping and didn't hide or invent any real overdue signal.
- Re-counted `emergence/insights/*.md` status headers directly (not trusting the SUMMARY's corrected table blind): `PROMOTED 12, RAW 10, OPEN 6, CLARIFIED 3, DISMISSED 2, PARKED 1, LINKED 1, CAPTURED 1`, sum 36 — matches the corrected table exactly and matches the 36 files on disk.

## Notes

- **Self-review / claim status:** this is not a `map.db` task, so `db.claims.claim_review` does not apply (there is no `TASK-NNN` row to claim against) — noted per the review-guide's claim-before-reviewing process, which is scoped to task review, not artifact review.
- **Classifier block — mixed result, and it matters for routing.** I tested two different writes. (1) A direct `sqlite3 MAP_System/map.db` diagnostic write (`UPDATE ... WHERE 1=0` inside `BEGIN/ROLLBACK`, plus a `claim_review()` call against a nonexistent task, which issues a real `UPDATE` affecting 0 rows) — neither was intercepted. (2) Appending this review's disposition as a `CHANGES_REQUESTED` event to `MAP_System/events/events.jsonl` (a normal coordination write, exactly the kind `AGENTS.md` asks agents to make) — **this was blocked** by the Claude Code auto-mode classifier, same failure mode as niko's block on `map.db`. Per the task's instruction, I did not attempt to work around it (e.g. retrying via a different tool to write the same event). **Conclusion: I am blocked from durable coordination-write actions the same way niko is** — the earlier unblocked `sqlite3` test was a narrow diagnostic touch, not evidence that routing review dispositions through me solves the problem. The review disposition for this change exists only in this markdown file and in the hcom report; it is not recorded in `events/events.jsonl` or `map.db`. The operator will need to record it directly (`!` prefix) or adjust the classifier, the same fix already needed for niko.
- The debt model itself — plain age since last review, Date-header fallback, no multi-factor score — is the right call. It matches the SUMMARY's own explicit rejection of a multi-factor Idea Score formula as "pseudo-precision" (SUMMARY, "Where the documents should be pushed back on" #3) and `AGENTS.md`'s Pushback Standard against over-design before validation. Applying that standard to one's own new feature, not just to external proposals, is worth recognizing.
- `stale` and `coverage` are genuinely complementary, not duplicative — verified by reading both implementations, not just asserted from the README.
