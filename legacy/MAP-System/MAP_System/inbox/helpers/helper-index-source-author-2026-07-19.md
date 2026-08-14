# Helper Assignment - TASK-258 independent source-index holdout author

- status: complete
- owner: codex-lab-kiri
- provider: codex
- created_at: 2026-07-19
- scope: author one frozen older-corpus retrieval truth set after implementation freeze

## Independence boundary

The retrieval implementation was frozen before this authoring pass:

- script SHA-256:
  `e595c4ba05e9adf8e271bceaceea5da3dd50d3aa831c18910ca764f961a6e5d9`
- focused-test SHA-256:
  `69d2b28994ae0f05cb054d4c6cc213897215870879b923da1c4c7df020a91600`
- known TASK-257 development-regression SHA-256:
  `78cade29c7c1d0d6cd2bb42b5310c48f4b723c9b74a85e470bfa6d47b8841e08`
- known development result: 9/9 task and 16/16 source visibility; this is
  explicitly not fresh holdout evidence.

The author must not inspect the script, tests, regression, research summary,
generated index, packet renderer, TASK-256/TASK-257 truth, or evaluator.

## Corpus

Completed TASK-100 through TASK-159 inclusive: 60 RELEASED, APPROVED, or
RETIRED task records.

Allowed reads:

- repository and MAP agent instructions;
- `MAP_System/tasks/TASK-100.json` through `TASK-159.json`;
- only output paths registered by those task records, when needed to verify a
  proposed strongest evidence source.

Forbidden:

- raw hcom/model transcripts;
- repository-wide search outside the corpus task records;
- TASK-258 implementation, research, regression, index, or packets;
- current author/evaluator truth files;
- source, task, policy, or index writes;
- operator or future-evaluator contact.

## Required output

Return one hcom `inform` message containing valid JSON with exactly nine query
objects, IDs S1 through S9.

Eight positive queries must each contain:

- `id`;
- `question`: a natural paraphrased user problem that avoids copying a task
  title;
- `expected_task_ids`: one or two corpus task IDs;
- `expected_source_paths`: one or two strongest registered sources actually
  opened;
- `expected_source_roles`: one role per source from task_scope,
  implementation, test, review, decision, release, outcome, current_state,
  guide, research, or artifact;
- `source_justifications`: why each path is strongest evidence;
- optional `ambiguity`.

One query must be a plausible MAP historical question with **no suitable task
in this 60-task corpus**. It must contain empty `expected_task_ids`,
`expected_source_paths`, and `expected_source_roles`, plus a `no_match_reason`
stating how the corpus was checked. Do not invent a negative if a task actually
matches it.

Spread the eight positive queries across at least five workstreams. Include at
least one compound two-task query and at least two questions where code or
focused tests are the strongest evidence.

## Stop

Stop after the single JSON truth-set report and at most one owner-authorized
clarification. The owner will freeze it verbatim before generating packets.

## Outcome

- truth event: hcom 7344 at 2026-07-19T18:43:47Z
- result: nine questions; eight positive labels across eight work areas, one
  compound two-task label, and one verified no-match label
- expected labels: nine task IDs and fifteen evidence paths
- scope: passed; task records and registered outputs only, no writes or
  retriever/research/regression/prior-truth access observed
