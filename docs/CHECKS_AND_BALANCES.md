# Checks and Balances

The point is trustworthy work, not a larger process.

| Risk | Typical examples | Minimum check |
| --- | --- | --- |
| Low | Documentation, formatting, isolated mechanical move | Owner checks the result. |
| Medium | Multi-file refactor, UI behavior, meaningful configuration | Relevant tests or reproduction plus independent review. |
| High | Security, data loss, persistence, payments, release packaging, external side effects | Explicit task, reproduced evidence, independent review, and operator-visible completion/release summary. |

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
approval. Use [the review template](../templates/review.md) for medium and high
risk work.

### Applicable review lenses

Use only the lenses the task actually triggers. One independent reviewer may
cover multiple lenses; do not add reviewers merely to satisfy a checklist.

- **Functional / acceptance** — does the requested behavior work and do the
  stated criteria pass?
- **Security / trust boundary** — can inputs, identities, permissions, secrets,
  or privileged actions cross a boundary they should not?
- **Privacy** — is sensitive or personal data collected, exposed, persisted, or
  transmitted beyond the declared need?
- **Destructive / data-loss** — can the change delete, overwrite, corrupt, or
  irreversibly mutate state?
- **Release / acquisition path** — does the actual package, generated artifact,
  install/download path, or deployment behave like the reviewed source?
- **Authority** — does the implementation execute only actions that the task,
  policy, and operator actually authorized?

For security and authority properties, prefer tests of executed behavior over
tests that merely match exact source text. For consequential evidence, verify
the state/revision actually being approved rather than assuming an older
submission snapshot is still current.

## High-risk completion summary

`OPERATOR_VISIBLE_RELEASE_CHECK` does **not** create another task status or a
second release subsystem.

For high-risk work, the final approved review/completion summary is the durable
operator-facing release summary. It should state, compactly:

- what changed / what became true;
- the verification actually reproduced;
- material residual risk or `none`;
- any external/destructive action still requiring operator approval; and
- the exact artifact/PR/revision being released when that distinction matters.

The task may become `DONE` after its required independent review and evidence
are complete. This summary is visibility, not a substitute for explicit
operator approval of a destructive, external, security-sensitive, or otherwise
operator-gated action.

Do not recreate a separate `APPROVED → RELEASED` lifecycle merely to duplicate
already-canonical task/review evidence. If a specific product needs a real
deploy/release operation, model that operation as its own task or explicit
policy-gated action with its own verification.
