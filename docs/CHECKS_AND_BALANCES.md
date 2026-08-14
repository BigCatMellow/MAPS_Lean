# Checks and Balances

The point is trustworthy work, not a larger process.

| Risk | Typical examples | Minimum check |
| --- | --- | --- |
| Low | Documentation, formatting, isolated mechanical move | Owner checks the result. |
| Medium | Multi-file refactor, UI behavior, meaningful configuration | Relevant tests or reproduction plus independent review. |
| High | Security, data loss, persistence, payments, release packaging, external side effects | Explicit task, reproduced evidence, independent review, and operator-visible release summary. |

## Non-negotiable controls

1. Name one owner for each active task.
2. State observable acceptance criteria before consequential implementation.
3. Do not self-approve substantive work.
4. Preserve evidence sufficient for another person to verify the claim.
5. Escalate scope, privacy, security, destructive, and irreversible decisions.

## Review

An independent reviewer reads the task first, then the changed paths and
evidence. Their verdict is one of:

- `APPROVED` — acceptance criteria are met.
- `CHANGES_REQUESTED` — a concrete required issue remains.
- `BLOCKED` — required context or evidence is missing.

Only concrete safety, correctness, or acceptance-criteria failures block
approval. Use [the review template](../templates/review.md) for medium and high risk work.
