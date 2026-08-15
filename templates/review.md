# Review: <task name>

- Task: <link>
- Reviewer: <independent reviewer>
- Verdict: `APPROVED | CHANGES_REQUESTED | BLOCKED`

## Acceptance criteria check

For each criterion, review against the agreed task. Do not invent new
requirements during review.

- `PASS | FAIL | PARTIAL` — <criterion>
  - Evidence: <observable proof>

## Applicable review lenses

Mark only what materially applies. One reviewer may cover multiple lenses.

- `[ ]` Functional / acceptance
- `[ ]` Security / trust boundary
- `[ ]` Privacy
- `[ ]` Destructive / data-loss
- `[ ]` Release / acquisition path
- `[ ]` Authority / permission boundary

For each checked lens, record the behavior/evidence actually inspected. Prefer
behavior-level security/authority checks over source-text proxies. If evidence
can go stale, identify the exact revision/artifact reviewed or re-derive the
critical property before approval.

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

## High-risk completion / release summary

Complete this section when the task requires
`OPERATOR_VISIBLE_RELEASE_CHECK`; otherwise use `N/A`.

- Released/approved artifact or revision: <PR/SHA/build/path>
- What became true: <compact outcome>
- Verification reproduced: <tests/reproduction actually checked>
- Residual risk: <none or concise risk>
- Operator-gated action still pending: <none or exact action requiring approval>

This is the operator-visible summary for the existing task/review lifecycle. It
does not create another `RELEASED` task state and does not authorize an
external/destructive action by itself.

## Reviewer limits

- Missing context/evidence: <none or blocker>
- New requirements discovered: <none or route to future task/decision>
