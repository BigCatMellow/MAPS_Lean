# Checks and Balances

The point is trustworthy autonomous work, not a larger approval process.

| Risk | Typical examples | Minimum check |
| --- | --- | --- |
| Low | Documentation, formatting, isolated mechanical move | Owner checks result. |
| Medium | Multi-file refactor, UI behavior, meaningful configuration | Relevant tests/reproduction plus independent review. |
| High | Security, data loss, persistence, payments, release packaging, external side effects | Explicit task, reproduced evidence, independent review, operator-visible completion/release summary. |

## Non-negotiable controls

1. One accountable owner per active task.
2. Observable acceptance criteria before consequential implementation.
3. No self-approval where independent review is required.
4. Preserve enough evidence for another reviewer to verify the claim.
5. Stay inside the approved roadmap/task permission envelope.
6. Escalate to the human only for a true permission-envelope crossing; do not
   turn review/checkpoints into routine human approval gates.

## Review

An independent reviewer reads the task, changed paths, and evidence. Verdict:

- `APPROVED` — acceptance criteria met.
- `CHANGES_REQUESTED` — concrete required issue remains.
- `BLOCKED` — required context/evidence missing.

The verdict routes back to the orchestration operator. It does not pause for the
human merely because review finished.

- `APPROVED` → reconcile, close task when complete, continue roadmap.
- `CHANGES_REQUESTED` → route correction, re-review as required.
- `BLOCKED` → research/recover/reassign; human only if resolving the blocker
  would cross approved authority.

Only concrete safety, correctness, authority, or acceptance-criteria failures
block approval. Use [the review template](../templates/review.md) for medium/high
risk work.

### Applicable review lenses

Use only lenses the task triggers. One independent reviewer may cover several.

- **Functional / acceptance** — requested behavior and criteria.
- **Security / trust boundary** — inputs, identities, permissions, secrets,
  privileged actions.
- **Privacy** — sensitive/personal data collection, exposure, persistence,
  transmission.
- **Destructive / data-loss** — deletion, overwrite, corruption, irreversible
  mutation.
- **Release / acquisition** — real package/artifact/install/deploy path.
- **Authority** — executed actions remain inside inherited permission envelope.

Prefer tests of executed behavior over source-text matching. Verify the exact
state/revision being approved.

## Preauthorization and high-risk actions

High risk does not automatically mean repeated human approval.

If the approved roadmap explicitly preauthorizes a destructive, external,
security/privacy-sensitive, or other consequential action with a bounded target
or class, limits/impact, and required recovery/verification, the orchestration
operator may execute it after its required checks without asking again.

If the action is not covered by the approved envelope, the human must authorize
that resolved action before execution.

A review can reject an unsafe implementation even when the action itself is
preauthorized. Preauthorization removes redundant permission prompts; it does
not remove verification, review, least privilege, or acceptance criteria.

## Enforced `main` merge gate

`main` is protected by GitHub branch protection (issue #61):

- pull requests only; direct pushes rejected;
- required up-to-date checks:
  - `test` — Runtime stack CI;
  - `review-evidence` — `scripts/check_review_evidence.py`, requiring committed
    `work/reviews/pr-<N>-review-evidence.md` bound to the reviewed code head;
- force-push and branch deletion disabled.

The connected GitHub identity may also be the repository/PR author identity, so
GitHub cannot prove reviewer independence through identity alone.
`review-evidence` proves the review artifact is bound to the reviewed commit; it
does not prove a distinct reviewer. Dispatch a fresh independent reviewer and
do not self-certify.

`enforce_admins=false` permits owner emergency bypass for genuine recovery such
as CI infrastructure failure. Routine work uses the standard gate. Record any
bypass so it is not mistaken for a normal reviewed merge.

Passing automated/independent review gates is authorization to continue the
already approved roadmap; it is not a reason to ask the human whether to merge
or start the next task unless the roadmap explicitly names a human checkpoint.

## High-risk completion summary

`OPERATOR_VISIBLE_RELEASE_CHECK` is visibility, not another state or approval
subsystem.

The compact summary states:

- what changed / became true;
- verification reproduced;
- material residual risk or `none`;
- any action still outside the approved permission envelope; and
- exact artifact/PR/revision when relevant.

The task may become `DONE` after required review/evidence. The orchestration
operator then continues the approved roadmap automatically.

Do not recreate an `APPROVED → RELEASED` lifecycle merely to duplicate canonical
task/review evidence. A substantive deploy/release may be its own task, but if
that task is already inside the approved roadmap it does not require another
human permission step.
