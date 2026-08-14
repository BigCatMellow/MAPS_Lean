# Review: <task name>

- Task: <link>
- Reviewer: <independent reviewer>
- Verdict: `APPROVED | CHANGES_REQUESTED | BLOCKED`

## Acceptance criteria check

For each criterion, review against the agreed task. Do not invent new
requirements during review.

- `PASS | FAIL | PARTIAL` — <criterion>
  - Evidence: <observable proof>

## Findings

For each blocking finding:

- Severity: <risk/severity>
- Path / surface: <affected path, system, or behavior>
- Failed criterion or control: <what requirement is not met>
- Observable issue: <what is wrong>
- Evidence: <how it was reproduced or observed>
- Required correction: <what must change>
- Do not change: <unaffected work that should remain intact>

If an idea is only an improvement and does not reveal a correctness, safety,
security, scope, or acceptance-criteria failure, record it as future work
instead of blocking approval.

## Evidence checked

- <commands, screenshots, logs, links, artifacts, or reproduction steps>

## Reviewer limits

- Missing context/evidence: <none or blocker>
- New requirements discovered: <none or route to future task/decision>
