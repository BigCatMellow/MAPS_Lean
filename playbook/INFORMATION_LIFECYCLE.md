# Information Lifecycle

Keep current truth easy to find without destroying provenance or forcing agents
to reconstruct relationships by search.

## Information states

- **Active:** current brief, requirement, decision, task state, risk, or next action.
- **Retired/superseded:** preserved with status + link to its replacement/disposition.
- **Archived/compacted:** raw history removed from default context after a forward
  summary preserves what still matters and links the source.

Do not archive stale-but-still-active information to avoid reconciling it. Correct
or mark its status first.

## Lifecycle

For forward-relevant information:

```text
capture → review → disposition → reconcile when reality changes
```

Preserving a file is not enough. If later implementation/evidence changes what a
record means, preserve the historical observation and add a concise current
status or successor link. Do not leave old “future task,” “not implemented,” or
“not promoted” wording looking current after reality changes.

## Nothing durable should be an island

A forward-relevant durable record should normally link to the record that gives
it meaning: parent roadmap/task, source, decision, evidence, review, handoff,
implementation, experiment, repair, successor, or explicit disposition.

Use **standard relative Markdown links** for repository artifacts. They work on
GitHub, Obsidian, and ordinary agent tooling.

Prefer:

```markdown
Related decision: [DEC-001](../work/decisions/DEC-001-example.md)
```

over copying the decision rationale into another file.

### Route-quality rules

- **Link, do not duplicate.** State the local implication; point to the owner for detail.
- Prefer a few strong relationship edges over many topical links.
- An outbound relationship is enough; do not maintain manual backlink pairs when
  tooling can derive backlinks.
- An unlinked artifact is not automatically wrong, but an active forward-relevant
  artifact with no meaningful relationship is an orphan candidate worth review.
- Do not promote an idea, reopen a decision, or create a task merely to increase
  graph connectivity.

The goal is shortest reliable retrieval, not a visually dense graph.

## Compaction

When active context becomes hard to navigate, retain decisions, constraints,
unresolved work, evidence links, and current relationships; replace activity
narration with a small forward summary and preserve raw historical material in an
appropriate archive/reference surface.

At an existing arc closeout, ask only:

> What forward-relevant idea, warning, decision, workaround, finding, or partial
> capability appeared here, and where is its current disposition?

Point to the existing owner. Do not create a second backlog to answer the question.
