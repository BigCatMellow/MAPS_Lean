# MAP System Housekeeping Survey

- author: claude-lab-sumi
- date: 2026-08-10
- purpose: operator-requested survey of file/folder organization; propose a
  protocol, not execute a mass reorg.

## Finding: not structureless, enforcement has drifted

`artifacts/` already has a real taxonomy (see its own `README.md`):
planning/reviews/tests/releases/reports/research/drafts/final/code/
command-center-ui/. On disk it also has `operations/`, `audits/`,
`experiments/`, `recovery/`, `designs/` — real, used subdirs the README
never documents. One stray file sits in the root:
`TASK-135-muva-integration-boundary-note.md`.

`repairs/` has its own ID scheme (`REPAIR-NNNN`) and README — already fine.

`notes/` (41 files) has no categorization at all — topically mixed
(incident taxonomy, book-reading logs, command-center guides, communication
rules) with only filenames to navigate by. This is the real mess.

`tasks/` (312), `handoffs/` (127), `tests/` (108), `scripts/` (88) are flat
by design — scripts very likely glob these directly
(`tasks/TASK-*.json`, `handoffs/STATE_SNAPSHOT-*.yaml`). **Do not
restructure these** without first grepping every script for hardcoded
glob/path assumptions; the blast radius of getting this wrong is every
task-claim, rotation, and mirror script in the system.

## Why even a "trivial" move isn't zero-risk

Checked before proposing execution: the one stray artifacts file
(`TASK-135-muva-integration-boundary-note.md`) is referenced by
`tasks/TASK-135.json`'s `output_paths` and by `workflow/task_graph.json`'s
mirror. Moving it means editing a completed task's historical record, not
a pure filesystem operation. Generalize this: **any** proposed move must
first be checked against task `output_paths`, `workflow/task_graph.json`,
and cross-references in other docs, or it silently breaks provenance -
exactly the failure class `AGENTS.md`'s Pushback Standard calls out
("changes that hide task ownership, status, output paths, or acceptance
criteria").

## Proposed protocol (for review, not yet approved)

1. **Sync `artifacts/README.md`** to the subdirs that actually exist.
2. **Relocate the one stray file**, updating `TASK-135.json` output_paths
   and the graph mirror in the same change (small, bounded, reviewable).
3. **Categorize `notes/`** into subfolders by topic (e.g.
   `notes/agents/`, `notes/command-center/`, `notes/context-rotation/`,
   `notes/reading/`) with redirects/notes at old paths only if anything
   external links them — grep first.
4. **New-file placement rule going forward**: before writing any new
   artifact/note, check the existing taxonomy for a fitting subfolder;
   don't create a new top-level file when a subdir already fits (this is
   the actual root cause - drift happens one convenient shortcut at a
   time, not from a missing folder).
5. **Do not touch** `tasks/`, `handoffs/`, `tests/`, `scripts/` structure
   without a prior grep-audit of every hardcoded path/glob referencing
   them, run as its own reviewed step before any move.
6. **Archival rule**: `archive/` already exists at the repo root for
   retired material - completed helper notes, superseded plans, and
   resolved handoffs older than N days (operator to set N) move there on
   a cadence, rather than accumulating forever in live directories.

## Recommendation

Promote items 1-2 as one small, low-risk MAP task (mechanical, cheap
review). Items 3 and 6 as a second task once item 1's grep-audit habit is
proven. Item 5 is a standing constraint, not a task - fold it into the
Bedrock charter or `AGENTS.md` directly as a rule, since it's a "don't"
that needs to survive independent of any one task's completion.
