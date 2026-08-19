# Helpers and Communication

Helpers are temporary, bounded capacity—not independent project owners.

## Start a helper only when it helps

Good uses: independent review, focused research, a named-file inspection,
bounded summarization, repetitive checks, or a clearly isolated implementation
subtask. Do not spawn an agent just to look busy or because one is available.

Before spawning, record in the task or a helper note:

- owner and helper identity;
- exact question/scope and input paths;
- expected output path or response;
- model/tool choice if it matters;
- stop condition; and
- integration owner.

The owner remains accountable for results, scope, review routing, and cleanup.
A helper cannot self-promote into an owner, final reviewer, or decision-maker.

If a helper rule is required for routing, audit, or safety, the helper/task
record must have a durable field where that fact can be written. A rule that
exists only in prose but has nowhere to record its answer cannot be reliably
enforced or validated.

## Parallel and broadcast work

Do not broadcast one implementation assignment to several workers and let them
race to become the owner. Split the work into explicit non-overlapping scopes,
or assign one owner and bounded helpers. Each worker should know its output,
stop condition, and integration owner before acting.

## Communication rules

- Use direct messages for narrow factual questions; summarize any answer that
  changes another agent’s work in the task, decision, or handoff.
- Route scope, priority, ownership, approval, privacy, destructive-action, and
  architectural questions to the accountable owner or operator.
- State requests as: issue, options, recommendation, and what is needed.
- Use a handoff—not casual chat—for a transfer of responsibility.
- Stop a helper after its output is integrated, rejected, duplicated, or
  blocked indefinitely.

Native Codex and Claude agent views are sufficient. Visibility is useful for
the operator, but an open pane/window never confers authority.

## Writable repo work in a shared clone

If a helper does writable repository work (edits, commits, pushes) in a
clone another lane might also be touching, give it its own `git worktree`
rather than letting it operate directly in the shared checkout — see
[WORKTREE_ISOLATION.md](WORKTREE_ISOLATION.md) for the exact recipe, the
branch-behind-`main` sync procedure, and a known sharp edge with empty
commits and review evidence. Worktree isolation is a safe place to work; it
is not merge authority, and it does not change who owns, reviews, or
integrates the task.
