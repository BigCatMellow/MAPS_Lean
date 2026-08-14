# Task: Link the active navigation spine

- Status: `DONE`
- Owner: `Codex`
- Risk: `LOW`
- Type: `documentation / information architecture`
- Goal: Convert intentional active Lean navigation references into standard
  Markdown links so the project remains portable and Obsidian can render a
  useful graph, without automatically linking all legacy references.
- Allowed output paths:
  - `README.md`
  - `AGENTS.md`
  - `docs/*.md`
  - `playbook/*.md`
  - `state/CURRENT.md`
  - `templates/*.md`
  - `obsidian/README.md`
  - `work/reports/TASK-004-digital-fungus-after-linking-report.md`
  - `work/reports/TASK-004-digital-fungus-after-linking.json`
- Do not change:
  - `legacy/`
  - runtime code, databases, launchers, installers, or external services
  - historical task/review/handoff records

## Acceptance criteria

- [x] The active first-run, authority, state, control-plane, playbook, task,
  review, handoff, and template routes use real Markdown links where they are
  intentional navigation.
- [x] Links remain portable outside Obsidian and resolve from their source file.
- [x] Legacy source references remain reference-only and are not bulk-relinked.
- [x] An Obsidian note explains opening the Lean root as a vault and excluding
  `legacy/` from Graph view.
- [x] Digital Fungus reruns successfully and the after report documents the
  graph change.

## Verification

- Run `python3 tools/digital_fungus.py --root . --output-dir work/reports`.
- Check the after JSON parses and Markdown links resolve by analyzer output.

## Completion

- After report: `work/reports/TASK-004-digital-fungus-after-linking-report.md`
- After findings: `work/reports/TASK-004-digital-fungus-after-linking-findings.json`
- Result: active first-run reachability increased from 1 to 24 notes; active
  orphans decreased from 32 to 9; active broken links remain 0.
