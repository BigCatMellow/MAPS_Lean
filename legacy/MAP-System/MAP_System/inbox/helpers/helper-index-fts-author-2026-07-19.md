# Helper Assignment - TASK-260 fresh FTS holdout author

- status: complete
- owner: codex-lab-kiri
- provider: codex
- created_at: 2026-07-19
- scope: independently author a frozen retrieval truth set after the FTS and packet harness freeze

## Frozen boundary

- retriever SHA-256:
  `edd0b53ab6d9c480360e19f4d14d667f459fcaa3155748a9bd96e741b70cca27`
- retriever tests SHA-256:
  `58df22f41258c3cea27d48ddbf413bf1b0c9c63eead9016b58008718a677949f`
- holdout harness SHA-256:
  `65219824dc3c2d5f62b77923a0bd9cd3f6c21d3222ee9db9f3e5bcff723a83ff`
- harness tests SHA-256:
  `3d97e70c1624a714ae2620993959f7c23abf39cbc4cdca5a45aec149f2dacd0c`

Do not inspect any of those files. They are recorded only so the owner can
prove they predate your truth.

## Corpus

The 43 completed task records from TASK-206 through TASK-249, excluding the
non-completed TASK-236:

`TASK-206` through `TASK-235`, `TASK-237` through `TASK-249`.

Allowed reads:

- repository and MAP agent instructions;
- only those 43 task JSON records;
- only output paths registered by those task records, when needed to verify a
  proposed strongest evidence source.

Forbidden:

- repository-wide search outside the corpus;
- raw hcom/model transcripts;
- TASK-256 through TASK-260 experiment scripts, tests, truth, indexes,
  packets, reports, research, helper notes, or metrics;
- current task, source, policy, index, or truth writes;
- operator, evaluator, or other helper contact.

## Required output

Return one hcom `inform` message containing valid JSON with exactly 11 query
objects: eight positive IDs `F1` through `F8`, then three legitimate no-match
IDs `N1` through `N3`.

Each positive query must contain:

- `id`;
- `question`: a natural paraphrased user problem that does not copy a task
  title;
- `work_area`: a short stable label;
- `expected_task_ids`: one or two corpus tasks;
- `expected_source_paths`: one to three strongest registered sources you
  actually opened;
- `expected_source_roles`: one per source from task_scope, implementation,
  test, review, decision, release, outcome, current_state, guide, research,
  artifact, or bundle;
- `source_justifications`: one per source;
- optional `ambiguity`.

Across the eight positive questions:

- cover at least five work areas;
- include at least two questions whose complete answer requires two distinct
  task IDs;
- include at least three questions where code or focused tests are strongest
  evidence;
- prefer specific task-owned evidence over shared mutable current-state files.

Each no-match query must be plausible and specific, with empty task/source/
role/justification arrays and a `no_match_reason` explaining how all corpus
task records were checked. Related plans, policies, or proposals do not count
as implementation when the question asks what was implemented. Do not invent
a negative if a corpus task actually answers it.

## Stop

Stop after the single JSON report and at most one owner-authorized clarification.
Do not write files. The owner will freeze the message verbatim and stop the
visible helper.

## Outcome

- truth event: hcom `7726` at 2026-07-19T19:27:55Z
- result: eight positives across eight work areas, three two-task compound
  questions, six code/test-centered questions, and three implementation-
  specific no-match controls
- expected labels: twelve task IDs and twenty evidence paths
- scope: passed; only corpus task records, required repository instructions,
  and registered evidence were read; no writes or retriever/prior-truth access
  observed
