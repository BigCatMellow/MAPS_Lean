# Information Lifecycle

Keep current truth easy to find without destroying provenance.

## Three states of information

- **Active:** current brief, requirements, decisions, task state, risks, and
  next actions. Read by default when relevant.
- **Retired/superseded:** remains in place with its status and replacement
  linked. It may still explain why the current state exists.
- **Archived/compacted:** historical raw material moved out of default context
  after a forward summary identifies what remains relevant and links sources.

Do not archive stale-but-active information to avoid reconciling it. First
correct or mark its status; then archive only when it is no longer part of the
active working set.

## Four lifecycle actions

Preserving a file is not the same as preserving its current meaning. For
forward-relevant information, keep these stages distinct:

```text
capture → review → disposition → reconciliation
```

- **Capture:** record the observation, source, decision, idea, evidence, or
  state while its context is available.
- **Review:** decide whether the record is supported, useful, current, and
  appropriately scoped.
- **Disposition:** make clear whether it is active, testing, deferred, blocked,
  resolved, rejected, or superseded where that distinction matters.
- **Reconciliation:** when later implementation/evidence changes the picture,
  link the old record to what happened next. Do not leave an old `future task`,
  `not implemented`, `Not promoted`, or similar statement looking current after
  reality has changed.

Historical observations should remain historically honest. Prefer adding a
short current-disposition/forward-link section over rewriting the original
observation as though the future were known when it was captured.

## Nothing durable should be an island

A forward-relevant durable artifact should link to the task, project, decision,
source, evidence, parent, successor, implementation, experiment, review, repair,
or other durable context that gives it meaning.

Use standard relative Markdown links for repository artifacts so the relationship
works on GitHub and remains inspectable by ordinary tooling. Stable IDs are
useful link text where available.

Prefer:

```markdown
[DEC-001](../work/decisions/DEC-001-....md)
```

over copying the decision's full rationale into another document.

**Link, do not duplicate.** The local artifact should state only the implication
it needs and point to the durable source for the rest.

Do not require humans/agents to maintain every relationship twice. Write the
forward/outbound relationship where it matters; backlinks, orphan reports, and
relationship views should be derived if tooling later proves useful. Derived
views are not new authority.

An unlinked artifact is not automatically invalid, but an active
forward-relevant artifact with no meaningful relationship should be treated as
an orphan candidate and reviewed.

## Document quality

Prefer stable IDs, status, owner, dates when time-sensitive, paths, and
explicit links. Use concise structured fields for normal state; use complete
sentences for risk, exceptions, tradeoffs, and rationale. A document must not
quietly override a recorded decision.

At phase close or when active context becomes hard to navigate, compact:
retain decisions, constraints, unresolved items, active work, and evidence
links; replace raw activity narration with a small forward summary; preserve
the raw source in `archive/`.

At an existing trajectory/arc closeout, also ask:

> What forward-relevant idea, warning, deferred decision, temporary workaround,
> review finding, or partial capability appeared during this arc, and where is
> its current disposition?

Do not create a second backlog merely to answer that question. Point to the
existing task, checklist row, decision, idea/experiment, handoff, repair record,
future-ideas backlog, or explicit rejected/superseded record that owns the
meaning.
