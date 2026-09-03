# Conversation-to-durable-notes procedure gap

Status: **finding / future procedure requirement**, not a new global rule.

## Operator expectation

The operator expected MAPS_L/Pilot to already have a procedure that prevents an important multi-topic conversation from disappearing into chat history.

The desired behavior is roughly:

```text
important Pilot conversation
  ↓
identify durable parent/project
  ↓
separate distinct forward-relevant topics
  ↓
create/adopt one project/topic folder
  ↓
write multiple focused notes
  ↓
index the packet
  ↓
link each note to its issue/task/decision/roadmap/implementation owner
  ↓
review / disposition / implementation later
```

The key requirement is **not** “save the transcript.” It is “make the forward-relevant findings discoverable and independently referenceable.”

## What the repository currently provides

Current repository guidance already contains strong pieces:

- [`AGENTS.md`](../../../AGENTS.md) says to keep forward-relevant durable records, use one concept/one owner, link rather than duplicate, and route design/working notes through `work/notes/`.
- [`work/README.md`](../../README.md) routes design/working notes to `work/notes/` and says supporting notes are not authority.
- [`playbook/INFORMATION_LIFECYCLE.md`](../../../playbook/INFORMATION_LIFECYCLE.md) provides the lifecycle:

```text
capture → review → disposition → reconcile when reality changes
```

and requires useful relationship links rather than orphaned records.

However, a search during this conversation did **not** find an explicit repository procedure specifically for:

- recognizing that a chat/conversation has produced multiple durable topics;
- automatically creating/adopting a conversation/project note folder;
- splitting findings by topic instead of one giant session summary;
- indexing those notes for later review/implementation;
- checking that no important conversation-only information remains before the chat ends.

This is therefore a procedure/automation gap worth preserving for #247/#248 rather than assuming the behavior already exists.

## Why one giant note is insufficient

A long conversation can contain separate concerns with different future owners and timelines. In this discussion alone, the durable topics include:

1. Durable Project Memory feature design;
2. AI instruction/context architecture and wording review;
3. MAPS_L implementation maturity/roadmap observations;
4. active-agent collision/sequencing findings;
5. the conversation-capture procedure gap itself;
6. future implementation/re-entry steps.

If all are stored in one transcript-like note:

- a future reviewer must read irrelevant sections;
- individual findings cannot be cleanly linked from separate issues/tasks;
- disposition becomes ambiguous when one topic is implemented and another remains deferred;
- a later update risks rewriting unrelated history;
- the note becomes another context dump.

The packet/index pattern is intended to preserve **one conversation provenance** while giving each topic its own forward lifecycle.

## Proposed future procedure shape

A future Pilot procedure should be trigger-based rather than run after every chat.

### WHEN

Trigger when a Pilot interaction produces forward-relevant information likely to matter after the current session, especially when:

- work spans sessions;
- multiple distinct findings/decisions/todos emerge;
- a reusable procedure/workflow is discovered;
- work is intentionally deferred;
- implementation cannot safely start because of another active lane;
- the operator explicitly says the conversation must be preserved;
- the chat-loss durability check would otherwise fail.

### READ / RESOLVE

1. Resolve the durable project/root.
2. Read the project's existing memory/note conventions.
3. Identify existing canonical owners (task, issue, decision, roadmap, runbook, source file).
4. Adopt existing artifacts instead of creating duplicate notes when they already own the topic.

### DO

1. Extract only forward-relevant findings.
2. Group them by **future meaning/owner**, not by message chronology.
3. Create one bounded packet/folder when several related topics came from the same discussion.
4. Create a short packet `README.md` that routes by question.
5. Create separate topic notes only where they have independent future value.
6. Link each note to its canonical issue/task/decision/roadmap/implementation owner where known.
7. Mark volatile snapshots as snapshots and require live recovery before action.

### VERIFY

Ask:

> If this conversation disappeared, could a fresh worker find each material finding and know its current disposition/next owner without reconstructing the chat?

Also verify:

- no full transcript was copied without need;
- no duplicate authority was created;
- topics that already had an owner were linked rather than restated unnecessarily;
- the packet has a short retrieval route;
- deferred items have a clear re-entry condition;
- volatile facts are labeled as snapshots.

### STOP / OTHERWISE

Do not create a packet for trivial, throwaway, or fully self-contained interactions where no forward-relevant state would be lost.

If only one durable topic exists and an existing issue/task/decision can own it cleanly, update/link that owner instead of manufacturing a folder.

## Folder convention question

This packet uses:

```text
work/notes/YYYY-MM-DD-<short-topic>/
  README.md
  <topic-a>.md
  <topic-b>.md
  ...
```

as a **local experiment within the existing `work/notes/` record class**, not a new global convention yet.

Before standardizing this shape, review whether:

- it improves retrieval compared with the current flat `work/notes/` archive;
- Digital Fungus can route/index it without increasing common-path cost;
- the rule belongs in Information Lifecycle, Project Bootstrap, Pilot behavior, or a more specific existing owner;
- a folder should be keyed by conversation date, project/topic, or an existing task/issue ID;
- automatic creation would cause note sprawl.

## Relationship to Durable Project Memory

This procedure gap is one expression of the larger #247 problem.

Long-term desired behavior:

```text
Pilot durable work
  → project memory exists/adopted
  → conversation findings reconcile into canonical project memory
  → separate notes/decisions/tasks only when they add forward value
  → chat may disappear without losing necessary state
```

The procedure should therefore become part of the automatic durability lifecycle rather than a manual “remember to summarize the chat” ritual.
