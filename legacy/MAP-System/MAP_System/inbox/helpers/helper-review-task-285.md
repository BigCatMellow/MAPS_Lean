# Helper Assignment - Independent review of TASK-285 rework (workstream digest pilot)

- status: complete
- outcome: TASK-285 APPROVED cleanly. Review artifact:
  `MAP_System/artifacts/reviews/task285-independent-review-lize.md`.
  All three original findings confirmed closed with independent
  reproduction, sanctioned approve run by the reviewer.
- owner: claude-lab-venu
- provider: claude
- model: haiku
- created_at: 2026-07-27
- scope: Independent review of TASK-285's rework resubmission per the
  standard MAP review gate (`AGENTS.md` Review Standard). Not a
  self-review: reviewer must not be `claude-lab-venu` (submitter),
  `claude-lab-nora` (predecessor session), or `task285-replacement-solo`
  (the original implementer/submitter of attempt 1).

## Why a helper

`codex-lab-diro` ack'd the review request but cannot claim (mandatory
context-rotation threshold, replacement pending). No other clean core
reviewer is currently live. Per `notes/helper-agent-guide.md`'s
Review-Conflict Default, routing to a spawned visible helper rather than
escalating routing to the operator.

## Process notes from three prior reviews today

1. Do **not** use raw `git diff` against `git HEAD` to check forbidden
   changes. This repo has not committed since 2026-07-15/23, so `git diff`
   shows unrelated cumulative work. Compare against the exact
   `output_paths` list in `MAP_System/tasks/TASK-285.json`, or check `stat`
   mtimes.
2. Review records need these exact section headers for
   `scripts/validate_review.py` to accept them: `## Verdict`,
   `## Acceptance Criteria Check`, `## Files Reviewed`,
   `## Forbidden Changes Check`.
3. An "LGTM" over hcom is not itself an approval. If you approve, you must
   run the sanctioned `map_task.py approve` command yourself and verify the
   canonical DB status actually changed.

## Task summary and history

TASK-285: "Pilot evidence-linked workstream digests" (final TASK-277
roadmap item). This is a **rework**, attempt 2/3. The original submission
(attempt 1, by `task285-replacement-solo`) was reviewed by
`codex-lab-nita`, verdict `CHANGES_REQUESTED`
(`MAP_System/artifacts/reviews/task285-independent-review-nita.md`) — read
this first, it has the full original findings. That verdict could not be
canonically applied for months because the submission predated TASK-278's
authorship tracking (`UNKNOWN SUBMISSION AUTHOR`); `REPAIR-0011`
(`MAP_System/repairs/REPAIR-0011-task285-legacy-submission-author-migration.md`)
backfilled that from the durable `SUBMISSION` event, then the already-written
`CHANGES_REQUESTED` verdict was applied via sanctioned `reject`. This
rework then fixed nita's three REQUIRED findings.

Nita's three findings, and what changed:

1. **Stale detection on refresh was missing.** `source_ref()` accepted an
   `expected_sha256` param but `build_digest()` never passed one in, so a
   real hash change between two builds went undetected. Fix:
   `build_digest()` now takes `prior_manifest: dict[str, str] | None` and
   threads `expected_sha256` into every `source_ref()` call via a new
   `_expected_for()` helper; a new `extract_manifest()` function flattens a
   digest's backlinks into `{path: sha256}` for the *next* build to compare
   against; a new `load_prior_digest()` + `--prior-report` CLI flag support
   a real refresh workflow. When a source goes stale, the affected claim
   moves from `claims`/`decisions`/etc. into `withheld_claims` (this was
   already the existing behavior for any non-"available" state — the gap
   was purely that "stale" was never reachable before).
2. **Reduction metric measured bytes, not tokens.** Added
   `estimate_tokens()`, a deterministic word/symbol-boundary regex
   tokenizer (`\w+|[^\w\s]`), explicitly documented as an *estimate*, not a
   specific model's BPE tokenizer (no tokenizer library like `tiktoken` is
   available in the project venv — worth confirming that claim is true if
   you want to double check). `evaluate()` now returns
   `context_tokens_raw`/`context_tokens_digest`/`context_token_reduction`
   alongside the existing byte metrics (kept as an additional diagnostic,
   per nita's own suggested resolution).
3. **Tests didn't cover either gap.** Five new tests in
   `test_workstream_digest_pilot.py`, most importantly
   `test_refresh_detects_stale_claim_source_and_withholds_it`, which
   explicitly includes a "no prior manifest" control proving the original
   bug (same mutated content, no baseline supplied, still reported
   available) alongside the fixed behavior (with a baseline, it's
   correctly withheld as stale).

## Input paths (output_paths registered to TASK-285)

- `MAP_System/artifacts/experiments/task285-workstream-digest-pilot.md`
  (regenerated from live data this round; `frozen_evaluation_sha256`
  should be unchanged from nita's original review since the frozen probe
  inputs didn't change — worth checking)
- `MAP_System/scripts/workstream_digest_pilot.py`
- `MAP_System/tests/test_workstream_digest_pilot.py`

No delivery note is registered for this task (only these three paths); the
pilot report itself is the delivery artifact.

## Task record

`MAP_System/tasks/TASK-285.json` — read `acceptance_criteria` there.

## Expected review artifact

Cover, with evidence, not just trust:

1. Each acceptance criterion, PASS/FAIL/PARTIAL.
2. Whether all three of nita's REQUIRED findings are genuinely closed —
   re-run the exact reproduction nita described (a source hash changing
   between two builds going undetected) and confirm it's now caught.
3. Independent verification: run
   `MAP_System/.venv/bin/python MAP_System/tests/test_workstream_digest_pilot.py`
   directly, confirm 10/10. Try mutating a real source file yourself (in a
   throwaway copy, not the canonical repo) and confirm stale detection
   actually works end to end, not just inside the test fixture.
4. Forbidden-changes check using output-path/mtime comparison, not
   `git diff`.
5. Whether the token estimator's documentation is honest (does it actually
   avoid claiming to be a real model tokenizer?).
6. Whether this pilot still correctly stays noncanonical/disposable and
   doesn't quietly become load-bearing anywhere.

Save the review artifact to
`MAP_System/artifacts/reviews/task285-independent-review-<helper-tag>.md`.
Use `MAP_System/db/claims.py`'s `claim_review("TASK-285", "<your-hcom-name>",
db_path="MAP_System/map.db")` before reviewing, then — if approved — run the
sanctioned `map_task.py approve` command yourself. Report your verdict back
to `claude-lab-venu` via hcom either way.

## Stop condition

Stop after the review artifact is delivered, the sanctioned approve/reject
has actually run (verify canonical status changed), and the verdict is
reported via hcom — or if you cannot reach a verdict within your context/
turn budget, report back what was found so far and hand off rather than
stalling silently.
