# Review, Authority and Merge Safety

MAPS_L keeps three questions separate:

1. Is the work correct and sufficiently evidenced?
2. Is the reviewer independent of the implementer?
3. Who is authorized to merge or cross an external/destructive boundary?

A passing review does not create permission, and permission does not remove the
need for verification.

Back to [[Home]].

## Proportional review

| Risk | Minimum evidence |
| --- | --- |
| Low | accountable owner verifies the observable result |
| Medium | relevant tests/reproduction plus independent review |
| High | explicit criteria, reproduced evidence, independent review, and an operator-visible completion/release summary |

Review verdicts are `APPROVED`, `CHANGES_REQUESTED`, or `BLOCKED`. They return to
the orchestration operator for reconciliation and continuation. Review is a
quality gate, not a routine request for new human permission.

## Independence

The submission author cannot approve the same work. A replacement identity that
inherited the author's work through a continuity link is also ineligible. The
runtime checks the connected continuity component when review is claimed and
again at approval.

Separate session names alone do not prove independence. A reviewer should
receive the task contract, exact output/revision, acceptance criteria, evidence,
and only the necessary reference material—not the author's entire reasoning
history.

## Revision-bound evidence and revalidation

Review evidence is bound to the code state the reviewer inspected. If a PR is
rebased or merged onto newer `main`, the evidence normally must be refreshed.

A narrow zero-diff revalidation tier exists for a purely mechanical update. It
requires proof that:

1. the old reviewed commit is an ancestor of the new head; and
2. the diff between those states is empty for the reviewed content.

If anything relevant changed, a full review is required. This exception does
not apply to an ordinary author-fix/review round. The repository check
[`scripts/check_review_evidence.py`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/scripts/check_review_evidence.py)
implements the exact-head/evidence-only and tree-equality rules used by CI.

## Authorized operators

MAPS_L has an append-only authorized-operator registry in the canonical task
database.

- `maps init --operator ID --operator-decision-ref REF` creates the genesis
  operator using the special `GENESIS` authorizer.
- `maps operator add ID --by AUTHORIZED_ID --decision-ref REF` appends another
  operator.
- `maps operator revoke ID --by AUTHORIZED_ID --decision-ref REF` appends a
  revocation.
- `maps operator list` shows the composed current state and history fields.

After genesis, new additions and revocations must be made by a currently
authorized operator. The last authorized operator cannot be revoked. A revoked
identifier cannot be re-added in the current slice; rotation and external
identity/signing are not implemented.

### Important current limitation

An empty registry leaves the Skill lifecycle actor gate disabled. This is an
opt-in-by-data compatibility design: before genesis, `maps skill` transitions
retain the earlier behavior. Once seeded, all Skill transition verbs—approve,
activate, retire, and supersede—require an authorized `--actor`.

The registry checks the supplied operator ID against local state. It does not
authenticate the OS user, provider session, cryptographic identity, or external
identity provider. It also does not automatically gate every other
operator-shaped action in the runtime.

## Repository merge authority

Every merge to repository `main` must use
[`scripts/opcmd_merge.py`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/scripts/opcmd_merge.py),
not ordinary `gh pr merge` by an arbitrary coordinator.

The wrapper fails closed unless it can:

1. resolve a concrete operator-authored hcom authorization message;
2. confirm the sender is a configured operator identity;
3. confirm the message authorizes that PR or gives the caller a fresh batch
   merge-seat designation;
4. confirm the authorization itself does not contain a HOLD/STOP;
5. find no later operator HOLD/STOP for the merge;
6. append an audit entry to the merge ledger; and
7. print the authorization quote before running the squash merge.

A coordinator's claim that it is the merge seat is insufficient. A PR-scoped
authorization covers only that PR; a batch designation is currently limited to
12 hours. If no authorized merge seat is active, peers may keep approved PRs
rebased and evidence-bound but must not merge them.

The ledger is local, append-only execution evidence and is Git-ignored. The
merge runner also posts the printed authorization quote in-channel so later
trajectory review can audit it.

## Branch protection and review evidence

Repository `main` is intended to use pull requests, current CI, and committed
review evidence. The connected GitHub identity may be shared by several agents,
so GitHub account identity alone cannot prove reviewer independence. The
committed evidence binds a named independent reviewer and exact reviewed head;
the operating process must still ensure the reviewer is genuinely separate.

## HOLD, STOP, and operator acknowledgement

These mechanisms solve different problems:

- An hcom HOLD/STOP after merge authorization blocks the merge wrapper.
- A release-check `BLOCKED` composite blocks an `APPROVED` review unless the
  latest check records a non-empty `operator_ack_ref`.
- An operator acknowledgement is durable evidence of an override; it is not a
  general `--force` escape hatch and does not grant unrelated authority.

Sources:
[`AGENTS.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/AGENTS.md),
[`docs/CHECKS_AND_BALANCES.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/docs/CHECKS_AND_BALANCES.md),
and
[`playbook/EXECUTION_INTEGRITY.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/EXECUTION_INTEGRITY.md).
