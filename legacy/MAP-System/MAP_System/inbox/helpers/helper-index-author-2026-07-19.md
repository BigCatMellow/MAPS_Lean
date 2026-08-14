# Helper Assignment — TASK-257 Independent Holdout Author

- owner: codex-lab-kiri
- helper: helper-index-author-bono
- status: complete
- started_at: 2026-07-19T18:02:00Z
- completed_at: 2026-07-19T18:05:00Z
- authority: read-only research; no source, task, index, or policy writes
- visibility: hcom-managed WezTerm tab required

## Purpose

Independently author a frozen historical-retrieval holdout over older completed
MAP tasks. The author must not see or tune the ranking implementation and must
return the truth set before the evaluator receives any packet.

## Frozen corpus

Completed TASK-160 through TASK-205, excluding non-completed TASK-186. The
corpus contains 45 APPROVED, RELEASED, or RETIRED task records.

## Allowed reads

- repository and MAP agent instructions;
- the 45 corpus task JSON files;
- only registered output paths from those task files, when needed to verify a
  proposed truth source.

No raw hcom/model transcripts, broad home-directory reads, external research,
or current TASK-256/TASK-257 implementation files.

## Required output

Return one hcom `inform` report containing valid JSON with exactly eight query
objects. Each query must include:

- stable ID H1–H8;
- a natural paraphrased user problem, avoiding copied task-title phrasing;
- one or two expected task IDs;
- one or two strongest registered source paths that were actually opened;
- why each expected source is the best evidence;
- the evidence role: task scope, implementation, test, review, decision,
  release, outcome, or current state.

Spread questions across at least five workstreams. Include ambiguity or a
`no suitable query` result rather than manufacturing certainty.

## Boundaries and stop

- Do not write files or task state.
- Do not contact the operator or future evaluator.
- Do not inspect the ranking code or generated index.
- Stop after the one JSON truth-set report and any single bounded clarification
  from the owner.

## Outcome

- hcom truth-set report: event 7014.
- produced: eight questions spanning session replay, Librarian resolution,
  redaction, atomic review claims, bounded halt authority, ProjectUpdater
  backup, cost/yield, and compound RnS recovery behavior.
- expected labels: nine task IDs and sixteen registered evidence paths.
- scope: task records and registered outputs only; no ranking/index inspection,
  writes, external research, operator contact, or evaluator contact observed.
