# Task: Digital Fungus pilot

- Status: `DONE`
- Owner: `Codex`
- Risk: `LOW`
- Type: `implementation / analysis`
- Goal: Build and run a read-only Markdown knowledge-graph analyzer for MAP
  Lean that recognizes standard Markdown links and Obsidian wikilinks, then
  reports graph-health findings without changing documentation links.
- Allowed output paths:
  - `tools/digital_fungus.py`
  - `work/reports/TASK-003-digital-fungus-report.md`
  - `work/reports/TASK-003-digital-fungus-findings.json`
- Do not change:
  - `legacy/` source documents or runtime code
  - active guidance links automatically
  - databases, launchers, installers, or external services

## Acceptance criteria

- [x] The analyzer discovers `.md` files while excluding `.git` and parses both
  Markdown links and `[[wikilinks]]`.
- [x] Findings distinguish active Lean material from `legacy/` reference
  material and do not recommend legacy as a default onboarding destination.
- [x] The report includes broken links, orphans, high-traffic hubs, and
  first-run reachability/resilience observations.
- [x] The script writes Markdown and JSON output only when explicitly asked,
  and never edits source documentation.
- [x] The pilot runs successfully against this repository and records its
  method and limitations.

## Verification

- Run the analyzer from repository root.
- Check output JSON parses and output paths remain within scope.

## Completion

- Command: `python3 tools/digital_fungus.py --root . --output-dir work/reports`
- Validation: `python3 -m py_compile tools/digital_fungus.py` and
  `python3 -m json.tool work/reports/TASK-003-digital-fungus-findings.json`
- Result: completed read-only; see the Markdown report and JSON findings.
