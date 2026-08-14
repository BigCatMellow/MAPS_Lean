<!-- hpom: file: artifacts/tests/task-extraction-parity.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: claude-lab-gome -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-16 -->
<!-- hpom: verified_against: TASK-207, revised after codex-lab-lilo CHANGES_REQUESTED review -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# TASK-207 — Bundle Extraction Parity Report

## Revision note (post-review)

codex-lab-lilo's independent review
(`artifacts/reviews/task207-review-lilo.md`) returned CHANGES_REQUESTED
with 3 REQUIRED findings and 1 RECOMMENDED finding, all fixed before
resubmission:

1. **Path traversal via manifest key** (`extract_bundle.py:97`, REQUIRED)
   — a manifest key such as `../../escaped` could write outside
   `assets/`. Fixed: `safe_asset_path()` now requires the manifest key to
   match a canonical UUID regex and independently confirms the resolved
   destination is `assets_dir`-relative before writing; both checks fail
   loudly rather than silently sanitizing. Regression test:
   `scripts/test_extract_bundle.py::test_path_traversal_rejected`.
2. **Stale output survives reruns** (`extract_bundle.py:83`, REQUIRED) —
   `assets/` was reused without clearing, so extraction wasn't a pure
   function of the bundle. Fixed: the extractor now `shutil.rmtree`s any
   existing `assets/` before repopulating it. Regression test:
   `test_extract_bundle.py::test_stale_output_removed`.
3. **`SHA256SUMS.txt` self-hash made provenance check fail** (REQUIRED)
   — the sums file had hashed itself (as 0 bytes, before its own content
   existed), so `sha256sum -c` exited nonzero even though every real
   payload file verified. Fixed: regenerated `source/SHA256SUMS.txt`
   excluding itself from the listed set (standard checksum-manifest
   convention); `sha256sum -c SHA256SUMS.txt` now exits 0 with all 11
   payload files verified. The claim below is now literally true, not
   just "everything except the self-referential line."
4. **Silent incomplete output** (`extract_bundle.py:115`, RECOMMENDED) —
   an unresolved `ext_resource`, a leftover raw UUID, or a missing
   `<head>` were warnings that still produced output. Fixed: these now
   fail closed (nonzero exit) unless `--allow-incomplete` is passed
   explicitly. Regression test:
   `test_extract_bundle.py::test_incomplete_fails_closed_by_default`.

## Second revision note (post-rereview)

The rereview (`artifacts/reviews/task207-rereview-lilo.md`) confirmed
fixes 1–3 and found one remaining REQUIRED gap in fix 4's first
implementation: rerunning an *incomplete* bundle into an *existing valid
output* wiped and repopulated `assets/` before the incompleteness check
fired, so the nonzero exit left a mixed tree (old `index.html` +
new partial assets) — contradicting the previous claim that nothing was
emitted on failure.

Fixed via staging + atomic replacement: the extraction now runs entirely
in a fresh sibling staging directory (`.baseline-staging-*`, created with
`tempfile.mkdtemp` next to `--out`); the three generated outputs
(`assets/`, `index.html`, `extraction_report.txt`) are swapped into
`--out` only after every validation passes, and the staging directory is
always removed (`try/finally`). Precisely stated behavior now:

- **On failure** (any validation, including incompleteness): exit
  nonzero, **any prior baseline under `--out` remains entirely
  byte-identical**, and no staging directory is left behind.
- **On success**: the generated outputs are replaced wholesale (never
  merged), so the committed result is a pure function of the bundle.

Regression tests added exactly as the rereview specified:

- `test_failed_rerun_preserves_prior_output` — valid extraction, then an
  incomplete bundle rerun into the same `--out`: asserts nonzero exit,
  asserts the prior output tree is byte-identical (full-tree snapshot
  compare), and asserts no leaked staging directory.
- `test_successful_rerun_replaces_output` — two successful runs with
  different bundles: asserts the second fully replaces the first's
  generated assets.

All five regression tests pass (`python3 scripts/test_extract_bundle.py`
→ `ALL PASS`). The real-bundle extraction was rerun after the staging
restructure: `baseline/index.html` and all `assets/*.png` are
byte-identical to the previously reviewed output (md5 verified before/
after), and no staging directory remains under `baseline/`'s parent.

## What was extracted

`scripts/extract_bundle.py` parses
`source/game-card-combat-effects/Clearfront.html` (a generated
self-extracting "artifact bundler" page: JSON `__bundler/manifest` of
UUID-keyed base64 assets + JSON `__bundler/template` HTML with UUID
placeholders + JSON `__bundler/ext_resources` id↔uuid map) and emits a
plain, directly-editable `baseline/index.html` plus real asset files
under `baseline/assets/`.

Full extraction report: `baseline/extraction_report.txt`.

## Acceptance criteria checks

1. **Every manifest entry decoded to a real file, asset count matches
   manifest key count.** 6/6 manifest entries (all `image/png`, none
   compressed) decoded to `baseline/assets/<uuid>.png`. No decode
   failures.
2. **Zero raw UUID placeholders remain in the emitted HTML.** The
   extractor's own check confirms this (`OK: zero raw manifest UUIDs
   remain in the emitted HTML` in `extraction_report.txt`); the two
   UUIDs the check first flagged were false positives from the check
   itself (a resolved reference is `assets/<uuid>.png`, which still
   contains the UUID substring by construction) — fixed by excluding
   matches immediately preceded by `assets/`.
3. **`__bundler/ext_resources` entries enumerated, not dropped.** All 6
   entries (`deck_lion`, `deck_badger`, `deck_raven`, `deck_owl`,
   `deck_stag`, `deck_fox`) resolved to their manifest UUID and were
   written into the baseline's injected `window.__resources` map with
   relative paths in place of the original blob URLs.
4. **Smoke test — visual and functional parity.** See below.
5. **`source/` untouched.** Extractor opens the source file read-only;
   no writes occur under `source/`. `source/SHA256SUMS.txt` was
   regenerated once (excluding itself from its own listed set — the
   original had incorrectly hashed itself as an empty file, per review
   finding 3) and now verifies clean: `sha256sum -c SHA256SUMS.txt`
   exits 0 with all 11 listed payload files OK. No file under `source/`
   changed as a result of running the extractor itself.

## Asset provenance cross-check

The bundle's 6 embedded manifest assets are the same bytes as the
pre-existing named portraits shipped alongside the bundle
(`source/game-card-combat-effects/assets/deck_*.png`) — confirmed by
SHA-256:

| id | uuid | sha256 (named asset) | sha256 (extracted) | match |
|---|---|---|---|---|
| deck_badger | 7c9ae1fc-... | fe86e35c502b... | fe86e35c502b... | yes |
| deck_fox | 7b0690f1-... | 79f11d1e3d8d... | 79f11d1e3d8d... | yes |
| deck_lion | 3fc6801a-... | fdbfd3cc2b58... | fdbfd3cc2b58... | yes |
| deck_owl | 9300c284-... | 2fbb44a827ba... | 2fbb44a827ba... | yes |
| deck_raven | 70860df9-... | 0d2d6b7fd863... | 0d2d6b7fd863... | yes |
| deck_stag | d65247e2-... | a7310b9d8f54... | a7310b9d8f54... | yes |

## Visual parity (headless Chromium screenshot)

Rendered both the original bundle (`source/.../Clearfront.html`) and the
extracted baseline (`baseline/index.html`) headless
(`chromium --headless=new`, 1280x900, same virtual-time budget) at the
initial champion-select screen.

- `artifacts/tests/screenshots/original-champion-select.png`
- `artifacts/tests/screenshots/baseline-champion-select.png`

Both files are **byte-identical** (`md5sum` `5f6a3688e845605ad5f8056cc0825c3b`
for both) — pixel-for-pixel parity including all 6 rendered card
portraits, confirming the asset substitution and template rewrite are
behaviorally exact for the load path.

## Functional parity (Chrome DevTools Protocol interaction)

Not satisfied with a static screenshot alone (see RISK-CF-0001 —
order-dependent script behavior could break even if the initial paint
matches), drove `baseline/index.html` via CDP
(`chromium --headless=new --remote-debugging-port`, script at
`/tmp/.../clearfront-smoke/cdp-test.mjs`, not checked in — throwaway
harness):

1. Navigated to `baseline/index.html`.
2. Clicked the "Emberwild" champion card via `Input.dispatchMouseEvent`
   (real event dispatch, not `.click()`).
3. Captured `Runtime.consoleAPICalled` and `Runtime.exceptionThrown`
   for the full session.
4. Asserted post-click DOM state and took a follow-up screenshot.

Result (rerun after the fixes above, same harness):

- **Zero console messages, zero exceptions** for the entire session
  (load + interaction).
- Deck selection resolved correctly and the game progressed further
  than the pre-fix run: 3-card hand dealt, and the enemy AI (this run
  randomly assigned "Verdant Court", Champion "Verdant Sentinel")
  played a unit ("Vanguard Squire", Charge keyword) and attacked —
  combat resolution correctly computed 1 unblocked damage and the
  projected life total (20 → 19), with the block-review UI
  ("1 damage is unblocked... Tap Review for outcomes") rendering
  correctly.
- Screenshot: `artifacts/tests/screenshots/baseline-after-champion-click.png`.

This confirms the extracted baseline is not just visually identical at
rest but fully interactive and stateful through actual combat
resolution — the game engine's IIFE runs correctly against the
rewritten (non-blob) asset references, both before and after the
security/robustness fixes.

## Security review acknowledgment

`artifacts/reviews/task207-review-lilo.md` (codex-lab-lilo) performed
the security-framed pass required by `MAP_System/AGENTS.md` for any
write-capable component. All REQUIRED findings are fixed above with
regression tests; the RECOMMENDED finding (fail-closed on incomplete
resolution) is also fixed. Resubmitting for a fresh independent pass.

## Conclusion

TASK-207 acceptance criteria met. The extracted `baseline/` is a faithful,
directly-editable replacement for the generated bundle and is the correct
starting point for the modular decomposition planned next (see
`shared/unresolved-questions.md` and the follow-on task(s) after
TASK-207).
