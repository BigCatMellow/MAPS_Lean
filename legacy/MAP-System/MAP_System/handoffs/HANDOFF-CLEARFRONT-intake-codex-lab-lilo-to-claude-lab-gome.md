# Clearfront Intake Handoff

- directive: hcom #311
- sender: codex-lab-lilo
- intended_recipient: claude-lab-gome
- status: read_only_inventory_complete
- ownership: Claude leads; Lilo made no source or destination-project edits.

## Source Inventory

- Source root: `/home/mellow/Documents/Projects/ClearFront`
- Primary candidate: `Game card combat effects/`
- Prototype bundle: `Game card combat effects/Clearfront.html`
- Governing design: `Game card combat effects/clearfront_design_principles.md`
- Current rules: `Game card combat effects/clearfront_rules.md`
- Image assets: six deck portraits under `Game card combat effects/assets/`
- Duplicate top-level `Clearfront.html` and archive `Game card combat effects.zip` exist; compare hashes before choosing canonical input.

## Key Finding

`Clearfront.html` is a generated self-extracting artifact rather than ordinary source. It is approximately 4.16 MB but only 212 physical lines. A loader, embedded resource manifest, and JSON-escaped HTML template contain the actual game. Do not treat the wrapper as the long-term editable source.

## Recommended Migration Sequence

1. Copy the complete source directory into the operator-approved workspace destination without modifying the original.
2. Record hashes for the original bundle, duplicate bundle, ZIP, rules, principles, and assets.
3. Extract the embedded template and resources reproducibly into a runnable baseline.
4. Add a smoke test that proves the extracted baseline loads before refactoring behavior.
5. Separate static structure, styles, card/deck data, rules/state transitions, AI behavior, rendering, and input/event wiring in small verified steps.
6. Keep the original bundled HTML as a reference build until parity is demonstrated.

## Design Guardrails Observed

- Core promise: traditional-card-game interaction with modern digital readability.
- Preferred pattern: simple cards, complex situations.
- Reject mechanics whose explanation/tracking exceeds the decisions they create.
- Preserve the three-card hand and two-card-per-turn constraint as defining decision spaces.
- Keep combat as the main tension source and Champions focused on one short identity-defining ability.
- Treat the Markdown design principles and playtest rules as governing inputs, not incidental documentation.

## Initial Risk Notes

- A mechanical split of the embedded script could change order-dependent behavior in the global/IIFE implementation.
- Generated bundle content may contain embedded third-party or binary resources; extraction should preserve provenance and avoid silently dropping assets.
- Rules/UI drift should be audited before changing balance. Refactoring and game-design changes should be separate MAP tasks so regressions are attributable.
- The copied destination needs its own project rules and task/output ownership before multiple agents edit it.

## Suggested First Task Boundaries

- Source preservation and reproducible extraction.
- Baseline runtime/smoke-test harness.
- Architecture map and module seams.
- Rules-to-implementation conformance audit.
- Incremental UI/data/engine decomposition.
- Playtest findings and simplicity-focused balance proposals after parity.

