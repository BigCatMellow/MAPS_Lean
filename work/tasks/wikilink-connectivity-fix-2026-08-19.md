# Task: fix unlinked navigational references flagged by digital_fungus

- Status: `READY_FOR_REVIEW`
- Owner: `Claude`
- Type: `docs/maintenance`
- Risk: `LOW`
- Goal: convert specific code-styled Markdown path mentions (invisible as
  graph edges) into real links, for docs added/edited on 2026-08-18/19, per
  the findings of `tools/digital_fungus.py` run against the full repo.

## Inputs and source of truth

- `tools/digital_fungus.py` — read-only knowledge-graph analyzer; its
  "Unlinked navigational references" section flags code-styled `` `path.md` ``
  mentions that read as prose to an agent but are not graph edges.
- `obsidian/README.md` — states explicitly: "The active navigation spine uses
  standard Markdown links, which Obsidian recognizes in Graph view, Local
  Graph, and Backlinks." A repo-wide grep confirms this: `[[wikilink]]` syntax
  does not appear as a real link anywhere active (`playbook/`, `docs/`,
  `work/`); it only appears in `legacy/` prose describing the *concept* of
  wikilinks, and once inside backticks in `work/tasks/TASK-003-digital-fungus-pilot.md`
  describing what the tool parses. The tool itself parses both Markdown links
  and `[[wikilinks]]` as edges, but this repo's actual established convention
  for real links is standard relative Markdown links
  (`[Display Text](relative/path.md)`), not `[[wikilinks]]`. This task follows
  that real, documented, already-in-use convention rather than the wikilink
  form assumed in the initial dispatch — the report's own phrase "Obsidian-
  style wikilinks" describes what the parser supports, not what the repo
  mandates.

## Allowed output paths

- `playbook/MODEL_CAPABILITY_ROUTING.md`
- `playbook/PROGRAM_STEERING.md`
- `playbook/INFORMATION_CLASSES.md`
- `work/roadmaps/CAPABILITY_CHECKLIST.md`
- `work/tasks/wikilink-connectivity-fix-2026-08-19.md` (this file)

## Do not change

- Anything under `legacy/` or `migration/` — treated by `digital_fungus.py`
  and repo convention as reference-only, expected historical noise, not a
  defect.
- Any orphan or unlinked mention not explicitly listed below (no mass-linking
  pass).

## Changes made

1. `playbook/MODEL_CAPABILITY_ROUTING.md` — linked its
   `work/roadmaps/CAPABILITY_CHECKLIST.md` mention.
2. `playbook/PROGRAM_STEERING.md` — linked its first
   `work/roadmaps/CAPABILITY_CHECKLIST.md` mention (the pair is deduplicated
   by the analyzer, so one real link resolves the flag for the file; the two
   other plain mentions later in the same file are left as prose for now,
   consistent with "surgical, not a mass pass").
3. `playbook/INFORMATION_CLASSES.md` — linked all four flagged mentions:
   `AGENTS.md`, `playbook/TASK_LIFECYCLE.md`,
   `work/roadmaps/CAPABILITY_CHECKLIST.md`, and
   `work/roadmaps/agent-harness-capabilities/02-procedural-knowledge-and-skills.md`.
4. Resilience gap: `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`
   was the only active link to
   `work/notes/2026-08-19-portable-deployment-operator-decisions.md`. No
   dedicated notes index exists anywhere in the repo (`work/notes/` has no
   `INDEX.md`/`README.md`, and other `work/notes/*.md` operator-decision
   files are discovered only through whichever task/roadmap/review doc
   happens to reference them — there is no established "second durable
   link" convention to follow). Rather than inventing one,
   `work/roadmaps/CAPABILITY_CHECKLIST.md` already carried a plain,
   code-styled mention of the same decision note (its Portable Deployment
   section, describing the same 2026-08-19 operator decisions) — that
   existing mention was converted into a real link, since
   `CAPABILITY_CHECKLIST.md` is itself the most central, durable, and
   heavily-referenced doc in the active corpus (dozens of incoming
   references) and already discussed this exact note. This both closes an
   unlinked-mention flag and gives the decision note a second, independent
   path into the active graph, without adding new prose or a new pattern.

## Verification

- `python3 tools/digital_fungus.py --root . --output-dir <scratch>/fungus-before --prefix before`
  run before edits, confirming all four gaps as reported.
- `python3 tools/digital_fungus.py --root . --output-dir <scratch>/fungus-after --prefix after`
  run after edits, confirming:
  - `playbook/MODEL_CAPABILITY_ROUTING.md`, `playbook/PROGRAM_STEERING.md`
    no longer appear in "Unlinked navigational references".
  - `playbook/INFORMATION_CLASSES.md` no longer appears for any of the four
    targets.
  - The "First-run resilience" section no longer lists
    `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md` as
    disconnecting `work/notes/2026-08-19-portable-deployment-operator-decisions.md`
    from `docs/FIRST_RUN.md`.
  - `resolved_edges` increased 510 -> 517 (exactly the 7 mentions converted:
    1 + 1 + 4 + 1), `first_run_active_reach` increased 55 -> 57.
  - Note on `unlinked_file_mentions`: measured against only the four
    `playbook/`/`work/roadmaps/` edits (before this task doc existed), the
    count dropped 1332 -> 1325 (-7), matching the 7 resolved edges exactly.
    Once this task doc itself is added to the tree, the *committed PR's*
    total rises to 1339, because this doc's own prose documents the fixed
    targets as code-styled paths (`work/roadmaps/CAPABILITY_CHECKLIST.md`,
    etc. — 14 new self-referential mentions), which the analyzer correctly
    counts as new unlinked mentions of its own. That is expected
    self-documentation noise from this file, not a regression in the
    fix — the four originally-flagged production docs remain fixed. An
    independent reviewer re-running the tool on the full committed PR
    branch should expect to see `unlinked_file_mentions` net *increase*
    versus `origin/main` (1332 -> 1339) for that reason, not decrease.

## Completion

- Result: read-only analyzer confirms all four target gaps closed; no
  `legacy/`/`migration/` files touched; no unrelated orphans linked.
