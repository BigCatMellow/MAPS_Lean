# Review: TASK-252 ClearFront collapsed-card type glyphs

- task_id: TASK-252
- reviewer: codex-lab-lilo
- task_owner: codex-lab-kiri
- risk_tier: low

## Verdict

APPROVED

## Files Reviewed

- `MAP_System/tasks/TASK-252.json`
- `Projects/ClearFront/app/assets/glyph-unit.png`
- `Projects/ClearFront/app/assets/glyph-spell.png`
- `Projects/ClearFront/app/assets/glyph-relic.png`
- `Projects/ClearFront/AGENTS.md`

## Forbidden Changes Check

PASS — the deliverable consists of the three registered visual assets only;
no ClearFront source bundle, game code, rules, or provenance material was
edited in this review scope.

## Acceptance Criteria Check

| Criterion | Result | Evidence |
|---|---|---|
| Square transparent RGBA PNGs without text/background/shadow | PASS | Each file is 128×128 8-bit RGBA; all four corner pixels have alpha 0; visual inspection finds no text, watermark, opaque background, or cast shadow. |
| Distinct readable type silhouettes at collapsed-card scale | PASS | Visual inspection identifies a blade/sword (Unit), starburst/spark (Spell), and diamond/gem (Relic). The silhouettes differ independently of their shared warm/blue palette. |
| Consistent high-contrast ClearFront family and scoped assets | PASS | The three glyphs use the same beveled fantasy-card treatment and remain visibly distinct on the transparent canvas. The task registers exactly these three glyph paths. |

## Verification

- `file`/`identify` on each glyph — PASS: `128x128`, `RGBA`/`srgba`.
- ImageMagick corner-alpha check — PASS: all corners `srgba(0,0,0,0)`; alpha range includes both transparent and opaque pixels.
- Visual inspection of all three PNGs — PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py` — PASS.

## Release Note

The assets meet the stated visual and accessibility-by-shape requirements.
Release remains the accountable owner’s normal lifecycle action.
