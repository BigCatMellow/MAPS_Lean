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

## Information-routing maintenance pass

Run this procedure when navigation cost has plausibly degraded, not merely because
time passed. Useful triggers include:

- meaningful documentation/roadmap growth or restructuring;
- an entry surface or routing hub approaching its explicit size budget;
- agents repeatedly searching, chain-reading, or opening the wrong large document
  to answer a routine question;
- Digital Fungus reporting new broken routes, orphan candidates, or increased
  route/read cost; or
- duplicated/stale prose becoming a competing source of truth.

Do not create a recurring cleanup ritual when none of those conditions exists.

### Procedure

1. **Baseline.** Run:

   ```bash
   python3 tools/digital_fungus.py --root .
   ```

   Record the relevant entry/hub sizes, common-route hops and token proxy, broken
   routes/orphan candidates, and the current canonical owner(s). Use the analyzer's
   token count only as a comparative planning proxy, never billing data.

2. **Route by intent.** For each common question, identify the smallest owning
   source. Prefer direct links from stable hubs; keep large specialist/history
   surfaces behind a question router instead of the normal orientation path.

3. **Consolidate before adding.** When two files explain the same rule/fact,
   preserve one owner, keep only the local implication elsewhere, and link to the
   owner. Remove stale status snapshots, repeated rule prose, activity narration,
   and instructions whose only purpose is finding other instructions.

4. **Connect or retire islands.** Give forward-relevant durable records a meaningful
   parent/source/decision/evidence/review/successor relationship. If a file has no
   unique forward value, retire/archive/remove it rather than inventing links to
   justify its existence.

5. **Compact without semantic loss.** Preserve authority, decisions, constraints,
   unresolved work, acceptance criteria, risks, evidence/provenance, and current
   relationships. Never trade correctness or recoverability merely for a smaller
   byte count.

6. **Remeasure.** Run Digital Fungus and the documentation/routing tests again.
   Keep the maintenance change only when it produces a real routing benefit such
   as lower common-path read cost, fewer hops/searches, a repaired route, a retired
   duplicate/orphan, or clearer ownership without increasing common-path cost.
   If the only result is more links/files/process, do not keep the churn.

7. **Verify and review proportionally.** Normal documentation-only changes need
   relevant tests. Changes to always-read contracts, authority wording, or other
   medium/high-risk surfaces require the repository's normal independent-review gate.

### Maintenance result

Report only the useful delta:

```text
before → after
entry/hub size: ...
route hops/read proxy: ...
fixed/retired: ...
verification: ...
```

Do not create a second graph registry, maintenance ledger, or copied navigation
truth just to record the pass. The repository links and canonical files remain
the source; preserve a report only when future work needs the evidence.

## Compaction

When active context becomes hard to navigate, retain decisions, constraints,
unresolved work, evidence links, and current relationships; replace activity
narration with a small forward summary and preserve raw historical material in an
appropriate archive/reference surface.

At an existing arc closeout, ask only:

> What forward-relevant idea, warning, decision, workaround, finding, or partial
> capability appeared here, and where is its current disposition?

Point to the existing owner. Do not create a second backlog to answer the question.
