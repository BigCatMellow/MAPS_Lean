<!-- hpom: file: artifacts/releases/task-207-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-16 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-207

## Header

```
task_id:      TASK-207
released_by:  claude-lab-gome
release_date: 2026-07-16
reviewed_by:  codex-lab-lilo
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

TASK-207 converts the ClearFront prototype from a generated 4.16 MB
self-extracting HTML bundle into a plain, directly-editable baseline
(`Projects/ClearFront/baseline/`) via a reproducible, security-reviewed
extractor, with parity against the original proven before any refactor
work builds on it (operator directive hcom #311).

- Files: `Projects/ClearFront/scripts/extract_bundle.py`,
  `Projects/ClearFront/scripts/test_extract_bundle.py`,
  `Projects/ClearFront/baseline/` (index.html, assets/,
  extraction_report.txt), `Projects/ClearFront/artifacts/tests/task-extraction-parity.md`,
  `Projects/ClearFront/source/SHA256SUMS.txt` (self-hash correction only).
- Shared files: ClearFront project bootstrap records (project-brief,
  requirements, decisions DEC-CF-001..003, risk register) were created
  under the same directive as project bootstrap, not this task's outputs;
  no MAP-wide shared policy files changed.
- Decisions: DEC-CF-001 (preserve original under source/, work on the
  copy), DEC-CF-002/003 (decomposition architecture) recorded in
  `Projects/ClearFront/shared/decisions.md`.
- Follow-ups: TASK-208 (multi-file skeleton, SUBMITTED, depends on
  TASK-207) and TASK-209 (rules-conformance audit, IN_PROGRESS,
  pi-lab-puma lease) already created and in flight.
- Events: creation, both submissions, both CHANGES_REQUESTED cycles,
  approval, and this release are in `events/events.jsonl`
  (trace_id task:TASK-207), validated with `--fail-on-new` (0 errors,
  0 new warnings).
- Emergence: considered — captured
  `MAP_System/emergence/insights/INS-0024-cdp-parity-gate-for-html-refactors.md`
  (byte-identical-screenshot + CDP-interaction parity gate, harness
  already reused by TASK-208).
- Operator-facing friction: no new operator-friction candidate found
  (task touched no operator-facing surface).

## Review

- Verdict: APPROVED —
  `Projects/ClearFront/artifacts/reviews/task207-final-review-lilo.md`
  by `codex-lab-lilo`, after two substantive CHANGES_REQUESTED rounds
  (`task207-review-lilo.md`, `task207-rereview-lilo.md`) that caught a
  manifest-key path-traversal write, non-reproducible stale output, an
  invalid checksum self-entry, silent incomplete output, and a
  failed-rerun mixed-tree atomicity gap. All fixed with 5 regression
  tests (`scripts/test_extract_bundle.py`, all passing) and re-verified
  independently by the reviewer, including reviewer-side reproduction of
  byte-identical extraction output.
- Reviewer independence: lilo authored only the read-only intake
  inventory; no implementation contributions. The reviewer-authored
  review records were explicitly removed from this task's output_paths
  to keep provenance clean.

## Verification

- Extraction: 6/6 manifest assets decoded, all `ext_resources` mapped,
  zero unresolved placeholders; staged atomic output (failure leaves any
  prior baseline byte-identical, verified by regression test).
- Asset provenance: all 6 extracted PNGs SHA-256-match the named
  `deck_*.png` files shipped beside the original bundle.
- Visual parity: original bundle vs extracted baseline headless
  screenshots byte-identical (md5 `5f6a3688e845605ad5f8056cc0825c3b`).
- Functional parity: CDP-driven real-input session (champion select →
  turn 1 → AI attack → combat resolution) with zero console messages and
  zero exceptions.
- Source integrity: `sha256sum -c source/SHA256SUMS.txt` exits 0, 11/11
  payload files OK.
- `MAP_System/scripts/validate_task_mirrors.py`: pass.
- `MAP_System/scripts/validate_task_graph.py`: pass.
- `MAP_System/scripts/validate_events.py --fail-on-new`: pass (0 errors,
  0 new warnings, 33 pre-existing legacy warnings).
