<!-- hpom: file: artifacts/reviews/task207-review-lilo.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: codex-lab-lilo -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-16 -->
<!-- hpom: verified_against: TASK-207 independent functional and security review -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Review Record: TASK-207

## Header

```text
task_id:      TASK-207
reviewer:     codex-lab-lilo
review_date:  2026-07-16
task_owner:   claude-lab-gome
```

Reviewer (`codex-lab-lilo`) != task owner (`claude-lab-gome`). Independence check passes. The reviewer performed only the earlier read-only intake inventory and made no TASK-207 source changes.

## Verdict

```text
CHANGES_REQUESTED
```

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Decode every manifest entry under `baseline/assets/`, including gzip | PARTIAL | Current bundle independently reproduced 6/6 byte-identical assets. A manifest-controlled key can traverse outside `assets/`, so the location guarantee is not enforced. Existing stale files are also retained across reruns. |
| 2 | Replace raw UUID placeholders | PASS | Independent temporary extraction produced an `index.html` byte-identical to the submitted baseline; six distinct `assets/<uuid>.png` references were present and no unresolved current-manifest placeholder was found. |
| 3 | Enumerate/account for `ext_resources` | PASS | Independent run reported and mapped all six current entries. |
| 4 | Prove visual/functional parity | PASS | Submitted evidence includes byte-identical initial screenshots plus a CDP interaction trace with zero console errors/exceptions. Independent extraction reproduced the submitted HTML and all asset bytes. |
| 5 | Keep `source/` untouched | PARTIAL | All 11 source payload entries listed in `SHA256SUMS.txt` verify, but `sha256sum -c SHA256SUMS.txt` exits nonzero because line 12 hashes the checksum file as if it were empty. The report's unqualified verification claim is therefore inaccurate. |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Modify preserved payloads under `Projects/ClearFront/source/` | NOT BROKEN — the review found no evidence the extractor writes there; the checksum-record defect predates/exceeds the extractor run and is reported separately. |
| Add a server, backend, build step, or network dependency | NOT BROKEN — extraction uses only the Python standard library and emits a directly openable HTML entry point. |
| Mix game-rule/balance changes into extraction | NOT BROKEN — the emitted game template matches the extracted source template apart from required resource substitution/injection. |

## Functional Review Pass

- `python3 Projects/ClearFront/scripts/extract_bundle.py --out <temp>/out` completed with 6 manifest and 6 external-resource entries.
- Temporary `index.html` was byte-identical to `baseline/index.html`.
- `diff -qr` found no difference between temporary and submitted asset directories.
- The extraction report differed only in the expected output path.
- The parity evidence is proportionate and stronger than a static load-only check.

## Security Review Pass

This separate pass is required because the extractor writes files based on parsed input.

The manifest key is used directly in `filename = f"{uuid}{ext}"` and then joined to `assets_dir`. A synthetic bundle with the first key renamed to `../../escaped` wrote `<temp>/escaped.png`, outside `<temp>/out/assets/`. The CLI accepts an arbitrary `--source`, so preservation of the checked-in bundle does not eliminate this trust boundary.

Required mitigation: validate manifest keys as canonical UUIDs (preferred, since that is the format contract) or otherwise reject path separators, `.`/`..`, absolute paths, and any resolved destination outside `assets_dir`. Add a focused negative test asserting no outside file is created.

## Findings

| Severity | File | Section | Finding | Required action |
|---|---|---|---|---|
| REQUIRED | `Projects/ClearFront/scripts/extract_bundle.py:97` | Manifest asset write | Manifest keys control the output filename without validation. `../../escaped` writes outside `assets/`. | Validate canonical UUID keys and confirm the resolved destination remains under `assets_dir`; fail before writing. Add a traversal regression test. |
| REQUIRED | `Projects/ClearFront/scripts/extract_bundle.py:83` | Output reproducibility | The output asset directory is reused without removing or rejecting stale files. A seeded `stale.bin` survives extraction, so directory contents are not a pure function of the bundle. | Extract through a clean/staged asset directory or safely remove only the prior generated directory, then replace it. Add a stale-output test. |
| REQUIRED | `Projects/ClearFront/artifacts/tests/task-extraction-parity.md` | Source integrity evidence | The report says `source/SHA256SUMS.txt` verified unchanged, but `sha256sum -c` fails because the file contains an impossible empty-file self-hash. | Correct the evidence to state exactly what passed, and route correction of the invalid provenance record under an authorized source-preservation task/exception. Do not claim the checksum set fully validates until its check exits zero. |
| RECOMMENDED | `Projects/ClearFront/scripts/extract_bundle.py:115` | Invalid-input handling | Unknown external-resource UUIDs, unresolved UUIDs, and missing `<head>` are warnings followed by successful output. | Fail closed for conditions that make the emitted baseline incomplete, or provide an explicit allow-incomplete mode. |

## Files Reviewed

- `Projects/ClearFront/scripts/extract_bundle.py`
- `Projects/ClearFront/baseline/index.html`
- `Projects/ClearFront/baseline/assets/`
- `Projects/ClearFront/baseline/extraction_report.txt`
- `Projects/ClearFront/artifacts/tests/task-extraction-parity.md`
- `Projects/ClearFront/source/SHA256SUMS.txt`
- `MAP_System/tasks/TASK-207.json`

## Notes

The current bundle extraction and parity result are credible. Approval is withheld because the filesystem boundary and clean-output guarantee are properties of the extractor itself, not merely of today's trusted manifest. No task-owned implementation file was changed during review.
