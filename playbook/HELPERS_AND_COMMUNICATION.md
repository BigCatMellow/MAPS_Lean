# Helpers and Communication

Helpers are temporary, bounded capacity—not independent project owners.

## Start a helper only when it helps

Good uses: independent review, focused research, named-file inspection, bounded
summarization, repetitive checks, isolated implementation, or answering an
in-scope question that would otherwise stall the orchestrator.

Do not spawn an agent merely to create activity.

Before spawning, record in the task or helper note when material:

- owner and helper identity;
- exact question/scope and input paths;
- expected output/response;
- model/tool choice if it matters;
- stop condition; and
- integration owner.

The orchestration operator remains accountable for integration, scope, review
routing, and the next action. A helper cannot self-promote into the parent owner,
final reviewer, or authority source.

### Standing dispatch triage clause

Every impl/review dispatch brief carries this clause verbatim (in addition to the
AGI-ready shape of rule 19 / [`AGI_STANDARD.md`](AGI_STANDARD.md)):

> **Triage capture:** if anything fails, stalls, surprises you, or the environment is
> missing something you need, append a `FRICTION_LOG.md` entry before you report back.
> Run test suites as a blocking foreground call — never background-and-wait on your
> own tests.

## Internal-first question resolution

Human escalation is not the default response to uncertainty.

Use this order:

```text
authoritative evidence
→ safe inspection
→ focused helper/research
→ independent challenge when consequential
→ orchestration operator decides inside approved permission envelope
→ human only for a true boundary crossing
```

Questions about implementation, architecture, task shaping, dependencies,
verification, or tradeoffs inside the approved roadmap are orchestration
questions. The orchestration operator should resolve them using evidence and
helpers rather than asking the human to choose every step.

## Lightweight tenth-seat consultation

For a consequential in-scope question where the leading answer remains
uncertain, assign a fresh helper to challenge it. Ask for:

- current proposed decision;
- weakest assumption;
- strongest plausible alternative;
- evidence for and against each;
- likely failure mode; and
- recommendation.

The challenger advises. The orchestration operator reconciles the evidence and
decides.

This lightweight consultation is not the formal
[Tenth Seat Review](TENTH_SEAT_REVIEW.md). Do not create a formal minority-report
artifact unless that protocol's narrow trigger applies or a durable decision
record is independently warranted.

## Parallel and broadcast work

Do not broadcast one implementation assignment to several workers and let them
race to become owner. Split work into explicit non-overlapping scopes, or assign
one owner and bounded helpers. Each worker should know its output, stop
condition, and integration owner.

## Communication rules

- Use direct messages for narrow factual questions; preserve only answers that
  change future work in the task, decision, or handoff.
- Route in-envelope questions to the orchestration operator, supported by
  helpers/research as useful.
- Route to the human only when the answer requires permission outside the
  approved roadmap, a human-only preference/authority, or a specifically named
  human checkpoint.
- State escalations as: exact boundary, attempted internal resolution, options,
  recommendation, and the minimum human decision required.
- A status report or checkpoint is not a request for permission to continue.
- Use a handoff—not casual chat—for transfer of responsibility.
- Stop a helper after its output is integrated, rejected, duplicated, or no
  longer useful.

Native Codex and Claude agent views are sufficient. Visibility is useful, but
an open pane/window never grants authority.

## Writable repo work in a shared clone

If a helper does writable repository work in a clone another lane might touch,
give it its own `git worktree` rather than the shared checkout. See
[WORKTREE_ISOLATION.md](WORKTREE_ISOLATION.md).

Worktree isolation is a safe place to work; it is not merge authority and does
not change who integrates or reviews the task.
