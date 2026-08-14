<!-- hpom: file: artifacts/tests/task-217-card-art-preview.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: codex-lab-lilo -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: TASK-217; clearfront_design_principles.md section 21; app card UI -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# TASK-217 — Category Artwork and Detail-on-Preview Evidence

## Result

Compact hand/board cards now present cost, name, faction/type, category art,
state-dependent status, and applicable attack/health stats. Full rules text and
keyword tags are hidden on compact hand/board faces and restored in the
existing desktop-hover and touch-hold preview.

The category system deliberately uses only three shared images:

- `app/assets/card-unit.png` — armored spear-and-shield guardian.
- `app/assets/card-spell.png` — cyan/violet arcane vortex.
- `app/assets/card-relic.png` — gold-and-emerald enchanted amulet.

All assets are text-free, watermark-free, project-local 512×512 RGB PNGs.
They were generated with the built-in image generation tool, then resized and
metadata-stripped locally from 1254×1254 to reduce their combined size from
about 6.1 MiB to about 1.1 MiB without changing their card-scale purpose.

## Image prompts

Shared prompt language: polished painterly digital fantasy card-game
illustration, clean readable silhouette at thumbnail size, centered square
composition, generous margins, simple dark atmospheric background, no text,
letters, numbers, logo, watermark, border, or card frame; category-generic
rather than faction-specific.

- Unit: one armored frontline guardian with spear and round shield; warm rim
  light; ember orange, muted teal, and dark navy.
- Spell: a luminous magical vortex above an open hand; electric cyan, violet,
  and deep navy; energetic focused glow.
- Relic: an ancient crystal amulet on a stone pedestal; gold, emerald, and deep
  navy; quiet mysterious inner glow; no people.

## Design-review checklist

| Question | Assessment |
|---|---|
| Clarity | Category artwork makes unit/spell/relic recognition immediate; full details remain one hover or hold away. |
| Depth | No rules or decisions change; this is presentation only. |
| Necessity | Reuses one asset per existing type rather than adding per-card art or a new taxonomy. |
| Identity | Artwork is category-generic and does not overwrite faction identity conveyed by color/name. |
| Tracking | Adds no state, counter, memory rule, or hidden gameplay information. Current status remains visible on compact faces. |

This satisfies the “interface must explain current game state” principle while
avoiding ornamental mechanics or new tracking burden.

## Focused browser verification

Registered harness: `artifacts/tests/task217-card-art-check.mjs`.

| Assertion | Result |
|---|---|
| Unit, Spell, and Relic sources all render | PASS |
| Every catalog artwork finishes loading | PASS |
| Compact hand card keeps name and art visible | PASS |
| Compact hand card hides detailed rules | PASS |
| Desktop hover preview appears | PASS |
| Hover preview restores detailed rules | PASS |
| Hover preview retains artwork | PASS |
| Console messages / runtime exceptions | 0 / 0 |

Visual evidence:

- `artifacts/tests/screenshots/task217-card-face.png`
- `artifacts/tests/screenshots/task217-card-hover.png`

Both were visually inspected: compact cards show readable category images and
the hover card restores rules text/status/stats without clipping.

## Gameplay regression

- Released seed-42 combat/blocking harness: PASS through card play, attack,
  block assignment, combat resolution/report, end turns, and AI turns; zero
  console messages/exceptions.
- Fail-loud undo harness: 6/6 PASS, including TASK-213 replacement protection;
  zero console messages/exceptions.
- Card clickability, unavailable grayscale treatment, status messaging, target
  state, and stats continue to use the same DOM/card logic; only artwork and
  detail visibility were added.

## Integrity and hashes

- Unit PNG sha256:
  `1da4ccf9def57fe115d06ae66f61fef6d81553df4ed0b33de65d22128ae102f7`
- Spell PNG sha256:
  `9d173af3f847d29ff5d1703466c8f26e8e83492d11225d275113f4bfa9cf9dae`
- Relic PNG sha256:
  `2805d4145787591a0222140824415c86bf7c6e38087ecfd01b145a3304f0c717`
- Preserved source `Clearfront.html` sha256:
  `57e67f190b5a7f05418af1ad1884f8f99602ed6cc9731e02a9975086c0744fa6`
- Preserved baseline sha256:
  `fa4dea9c0c5987b6c5e50f6e6707a36942f432edfb7951851367a70c5e4cfe9a`
- `source/SHA256SUMS.txt`: all 11 payloads PASS.
- `node --check`: render logic and focused harness PASS.
- Task graph, schema, and mirror validators PASS.

## Acceptance criteria

1. Three original, distinct, text-free category artworks: **PASS**.
2. Compact name/art face plus full hover/touch details: **PASS**.
3. Existing interactions/rules and regressions unchanged: **PASS**.
4. Design-review checklist and smallest three-asset system: **PASS**.
5. `file://`, runtime health, evidence, and preserved inputs: **PASS**.

Emergence capture considered: no new insight beyond the requested UI pattern
and existing image-generation/parity workflows; no artifact created.
