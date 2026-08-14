# Execution Integrity

AGI answers: **is the task ready?**

A run manifest answers: **what exact contract/context/scope did this worker get?**

These are different checks.

```text
AGI READY task
      ↓
worker claims task
      ↓
freeze run manifest
      ↓
execute
      ↓
check task/context staleness + Git write scope
      ↓
submit evidence
      ↓
independent review
```

## Run manifest

Created only for the current claimant of an `ACTIVE`, `AGI READY` task.

It records:

- stable task-definition SHA-256;
- worker and optional session identity;
- readable / writable / forbidden repo scope;
- context file paths plus SHA-256 hashes;
- runtime limits;
- optional Git base revision;
- creator and timestamp.

It does **not** copy the full context into SQLite. Context stays in its durable
source file; the manifest stores a pointer + hash.

`run_manifests` and `run_context_refs` are protected by SQLite triggers against
update/delete. A changed run is a **new run**, not an edited old record.

## Stable task revision

The task revision hashes the execution contract: goal, owner, authority, risk,
inputs/sources, dependencies, output paths, acceptance/verification/evidence,
stop/escalation, review requirement, and explicit policy flags.

It deliberately excludes lifecycle churn such as:

```text
status
claimed_by
lease timestamps
submission/review state
operator approval timestamp
```

Those facts can change during a valid run without redefining the task contract.

## Staleness

`check_run_stale()` reports stale if:

- the task disappeared;
- the stable task definition changed; or
- a referenced context file disappeared/changed hash.

It reports only. It does not rewrite the task or filesystem.

## Git scope proof

`verify_git_run()` compares the worktree to the manifest's base revision and
reports paths outside the frozen writable scope.

It never runs `reset`, `restore`, `checkout`, or `clean`. Out-of-scope changes
must be inspected because an automatic repair could destroy unrelated work.

## Continuity lineage

A continuity link says one identity/session inherited another's execution
context/obligations, for example during context rotation.

```text
author → replacement-1 → replacement-2
```

For independent review, all three are one continuity component. None may review
the author's submission merely because the session/agent ID changed.

Continuity grants **no task authority**. It only constrains independence.

The rule is enforced twice:

1. routing filters continuity-disqualified reviewers;
2. SQLite review claim/finalization re-check independence.

The second check matters if new continuity evidence appears after routing.

## Criterion-level evidence

This is optional.

Normal tasks can continue using the existing submission evidence + review
summary. If a task records criterion claims for the current submission, it opts
into a stricter gate:

```text
implementer claim
  criterion = complete / partial / blocked
  evidence file references

reviewer verdict
  confirmed / rejected
```

Claims and verdicts are separate append-only records. The reviewer never
rewrites the implementer's claim.

Once criterion mode is used, overall `APPROVED` requires every acceptance
criterion's latest claim to be `complete` and its latest reviewer verdict to be
`confirmed`.

## CLI

Examples:

```bash
python -m runtime.integrity.cli run-create TASK-0042 worker-1 \
  --created-by dispatcher --context AGENTS.md --write runtime/state \
  --base-revision HEAD

python -m runtime.integrity.cli run-stale RUN-... --repo .
python -m runtime.integrity.cli run-verify-git RUN-... --repo .

python -m runtime.integrity.cli continuity-link old-session new-session \
  --reason context-rotation
```
