# Helper Assignment — TASK-256 Fingerprint Retrieval Evaluator

- owner: codex-lab-kiri
- helper: helper-index-neko
- started_at: 2026-07-19
- status: complete
- completed_at: 2026-07-19T17:56:00Z
- visibility: hcom-managed WezTerm tab
- authority: read-only evaluation; no MAP, task, source, or policy writes

## Bounded purpose

Evaluate whether a compact, token-budgeted historical task index helps a fresh
agent identify useful prior MAP evidence without loading broad repository
history.

## Inputs

The owner will send a frozen query packet and the compact generated index only
after the corpus, expected evidence, and scoring rules are durably recorded.

## Required behavior

- Do not inspect or search the repository before receiving the pilot packet.
- Answer each frozen query from the compact index first.
- Name up to two primary sources that would be opened for confirmation.
- Report confidence, ambiguity, and any query with no strong match.
- Estimate how much compact context was used.
- Do not edit files, task state, policy, indexes, or source artifacts.
- Do not promote findings or contact the operator.
- Return the evaluation through hcom to codex-lab-kiri.

## Monitoring and stop condition

The owner monitors hcom status, messages, and terminal activity, checks the
helper's answers against a predeclared truth set, and records latency and any
scope deviation. The helper stops after one frozen evaluation pass and any one
bounded clarification/confirmation pass requested by the owner.

## Deliverable

One hcom report containing, for each query: ranked fingerprint IDs, source
expansions, confidence, match rationale, and uncertainty. The owner preserves
the report and scoring in
`MAP_System/artifacts/experiments/task-fingerprint-index-pilot-2026-07-19.md`.

## Outcome

- Initial packet report: hcom event 6915.
- Bounded confirmation report: hcom event 6946.
- Scope adherence: passed. Monitoring showed reads of the one frozen packet,
  followed by exactly the three separately authorized confirmation sources;
  no repository search, link following, or writes occurred.
- Stop condition: met after the initial ten-query pass and one confirmation
  pass.
