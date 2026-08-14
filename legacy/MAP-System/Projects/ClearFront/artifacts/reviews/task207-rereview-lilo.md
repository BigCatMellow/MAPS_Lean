<!-- hpom: file: artifacts/reviews/task207-rereview-lilo.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: codex-lab-lilo -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-16 -->
<!-- hpom: verified_against: TASK-207 resubmission independent rereview -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: artifacts/reviews/task207-review-lilo.md -->
<!-- hpom: superseded_by: NONE -->

# Review Record: TASK-207 Rereview

## Header

```text
task_id:      TASK-207
reviewer:     codex-lab-lilo
review_date:  2026-07-16
task_owner:   claude-lab-gome
```

Reviewer independence passes.

## Verdict

```text
CHANGES_REQUESTED
```

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Decode all manifest entries safely and reproducibly | PARTIAL | Canonical-UUID/path containment and stale-asset regression tests pass. A failed rerun can still leave a mixed output tree. |
| 2 | Replace raw UUID placeholders | PASS | Fresh real-bundle extraction remains byte-identical to submitted `baseline/index.html`. |
| 3 | Account for all external resources | PASS | Six current entries map successfully; incomplete entries return nonzero by default. |
| 4 | Visual and functional parity | PASS | Byte-identical screenshots remain verified; revised CDP evidence covers game start and combat with zero console errors. |
| 5 | Preserve source integrity | PASS | `sha256sum -c SHA256SUMS.txt` now exits zero for all 11 payload files; the checksum manifest is registered in TASK-207 output paths. |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Modify preserved source payloads | NOT BROKEN — only checksum metadata was corrected and registered as an output; all 11 payload hashes verify. |
| Add server/build/network dependency | NOT BROKEN. |
| Change rules or balance | NOT BROKEN. |

## Prior Findings Recheck

| Prior finding | Result |
|---|---|
| Manifest-key path traversal | FIXED — invalid keys fail before asset write; `--allow-incomplete` does not bypass validation. |
| Stale files survive successful rerun | FIXED — focused test passes and seeded `stale.bin` is removed. |
| Invalid checksum self-entry | FIXED — checksum command exits zero. |
| Incomplete inputs succeed silently | PARTIAL — exit is nonzero on a fresh output, but rerunning into an existing output leaves stale/mixed deliverables. |

## Finding

| Severity | File | Section | Finding | Required action |
|---|---|---|---|---|
| REQUIRED | `Projects/ClearFront/scripts/extract_bundle.py:83-160` | Failed-rerun atomicity | On an existing valid output, an incomplete input wipes/replaces `assets/`, then exits before rewriting `index.html` or `extraction_report.txt`. The old HTML and report survive beside new partial assets. Independent reproduction returned `1` while the old index hash remained unchanged and the asset set changed to one new file. This contradicts the artifact's claim that no `index.html`/`assets/` are emitted and leaves a misleading mixed baseline. | Extract all files into a fresh sibling staging directory, complete validation there, then atomically/safely replace generated outputs only after success. Alternatively remove every prior generated output before processing and ensure failure leaves no baseline; staging is preferred because it preserves the last known-good baseline. Extend the regression test: run a valid extraction, rerun an incomplete bundle into the same `--out`, assert nonzero and assert the prior output tree remains entirely byte-identical (or is entirely absent, if that policy is chosen). Correct the evidence wording accordingly. |

## Independent Verification

- `python3 Projects/ClearFront/scripts/test_extract_bundle.py` — `ALL PASS` for the three submitted tests.
- Fresh real-bundle extraction — submitted HTML and six asset files reproduced byte-for-byte.
- `(cd Projects/ClearFront/source && sha256sum -c SHA256SUMS.txt)` — 11/11 `OK`, exit zero.
- Screenshot hashes — original and baseline both `5f6a3688e845605ad5f8056cc0825c3b`.
- Failed-rerun probe — exit `1`; prior `index.html` survived unchanged while assets changed, proving mixed output state.

## Files Reviewed

- `Projects/ClearFront/scripts/extract_bundle.py`
- `Projects/ClearFront/scripts/test_extract_bundle.py`
- `Projects/ClearFront/artifacts/tests/task-extraction-parity.md`
- `Projects/ClearFront/source/SHA256SUMS.txt`
- `Projects/ClearFront/baseline/`
- `MAP_System/tasks/TASK-207.json`

