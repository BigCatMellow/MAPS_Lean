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

## Enforced `main` merge gate

`main` is protected by a GitHub branch protection rule (configurable via
`repos/BigCatMellow/MAPS_Lean/branches/main/protection`), not by agent
discipline alone (issue #61):

- pull requests only — direct pushes to `main` are rejected;
- two required status checks must pass on an up-to-date head before merge:
  - `test` — the Runtime stack CI job;
  - `review-evidence` — `scripts/check_review_evidence.py`, which requires a
    committed `work/reviews/pr-<N>-review-evidence.md` bound to the PR's
    exact reviewed code head (see the script's module docstring for how it
    walks past evidence-only trailing commits to find that head);
- force-push and branch deletion are disabled on `main`.

**What this does not solve.** The connected GitHub identity used by MAPS
agents is also the repository/PR author identity, so GitHub cannot enforce a
native "required approving review" from a genuinely distinct identity, and
`required_approving_review_count` is deliberately left at `0` rather than
faked. The `review-evidence` check mechanically guarantees a review-shaped
artifact exists and is bound to the exact reviewed commit — it does **not**
prove the reviewer was a distinct identity from the author. Reviewer
distinctness is still a process discipline (dispatch a fresh agent for
review; never self-certify), not a mechanically enforced property.

**Emergency bypass.** `enforce_admins` is `false`: the repository owner can
merge around the required checks as a genuine recovery action (e.g. CI
infrastructure outage blocking all merges). This is not the normal path —
routine PRs merge through the standard gate above — and any admin-bypass
merge should be called out explicitly in the merge/handoff record so it
isn't mistaken for a reviewed, gate-passing change.

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
