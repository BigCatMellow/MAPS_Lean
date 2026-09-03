# Authoring conversation-derived note packets

Status: **local authoring guide for this packet and a candidate pattern for future Pilot conversation capture; not repository-wide authority**.

Use this guide when a conversation produces several forward-relevant findings that need to survive the chat and be independently referenceable later. Repository-wide information-lifecycle authority remains [`playbook/INFORMATION_LIFECYCLE.md`](../../../playbook/INFORMATION_LIFECYCLE.md); work-record routing remains [`work/README.md`](../../README.md); global invariants remain [`AGENTS.md`](../../../AGENTS.md).

## Core rule

Do not save the conversation. Preserve what a future worker needs from it.

A useful packet should answer:

```text
What durable topics emerged?
What does each topic mean now?
What owns the topic next?
What evidence/decision/source gives it meaning?
What is its current disposition?
What should a future worker read or do next?
```

The final check is:

> **If the conversation disappeared, could a fresh worker recover every material finding, its relationships, and its current disposition without reconstructing the chat?**

## When to create a packet

Create/adopt a packet when a conversation produces multiple related durable topics, especially when one or more are:

- intentionally deferred;
- likely to span sessions or models;
- consequential design findings;
- reusable procedures/workflows;
- separate future implementation/review items;
- blocked by current coordination/collision state;
- findings whose meaning depends on several decisions/evidence sources.

Do **not** create a packet when:

- the interaction is throwaway;
- one existing task/issue/decision already owns the only durable result;
- the only thing being preserved is routine narration;
- a new note would merely duplicate a canonical README, task, roadmap, decision, runbook, or source file.

## Folder shape

This packet uses:

```text
work/notes/YYYY-MM-DD-<short-topic>/
  README.md
  AUTHORING.md
  <topic-a>.md
  <topic-b>.md
  ...
```

This is still a local pattern under the existing `work/notes/` record class, not a new global record class.

### `README.md`

The packet README is the small hub. Route by **future question**, not conversation chronology.

Good:

```markdown
| Question | Note |
| --- | --- |
| How should project memory work? | [Durable Project Memory](durable-project-memory.md) |
| What wording/context changes were identified? | [AI Instruction Architecture](ai-instruction-context-architecture.md) |
```

Avoid a chronological table such as “message 1 / message 2 / message 3.”

### Topic notes

Create a separate topic note only when it has an independent future lifecycle: it may be implemented, reviewed, rejected, superseded, or revisited independently of the other topics.

Split by **meaning/owner**, not by who said it or when it appeared.

## Suggested topic-note shape

Use only the sections that add value.

```markdown
# <specific topic>

Status: <finding / deferred design / snapshot / supporting evidence>

## Current meaning

<What this note means now.>

## Finding / proposal

<Forward-relevant substance.>

## Why it matters

<Only rationale that changes future understanding/action/risk.>

## Open questions / unresolved work

- ...

## Connections

- Parent / supports: [<owner>](relative/path.md)
- Derived from: [<source>](relative/path.md)
- Evidence: [<evidence>](relative/path.md)
- Implemented by: [<implementation>](relative/path.md)
- Superseded by: [<successor>](relative/path.md)
- Revisit trigger: <condition>

## Re-entry

<What a future worker must recover/check before acting.>
```

Do not force every heading into every note. Minimum sufficient context wins.

# Spiderweb relationship model

“Spiderweb” is the conceptual relationship model: **nothing durable should be an island**.

The accepted owner for that behavior is [`playbook/INFORMATION_LIFECYCLE.md`](../../../playbook/INFORMATION_LIFECYCLE.md), which requires forward-relevant records to connect to the record that gives them meaning: parent roadmap/task, source, decision, evidence, review, handoff, implementation, experiment, repair, successor, or explicit disposition.

Think of each note as a node and each useful relationship as a labeled edge:

```text
conversation finding
      │ derived from
      ▼
research/source
      │ supports
      ▼
design note
      │ resulted in
      ▼
decision
      │ implemented by
      ▼
PR / source change
      │ verified by
      ▼
review/evidence
```

A different path might be:

```text
proposal ──superseded by──> later decision
   │
   └──related to──> experiment
                       │
                       └──rejected because──> evidence
```

The goal is not graph density. The goal is that a future worker can follow a **short, meaningful route** from a finding to its owner, evidence, disposition, and successor.

## Preferred connection labels

Use a small descriptive vocabulary. These are useful labels for note packets; they are not a new global schema:

- **Parent / supports** — the task, roadmap, issue, project, or larger finding this belongs under.
- **Derived from** — source/research/conversation finding that produced this conclusion.
- **Related** — genuinely useful lateral relationship when a stronger relation does not fit.
- **Depends on** — cannot proceed correctly until the linked item is resolved/accepted.
- **Contradicts** — evidence or conclusion materially conflicts with the linked record.
- **Supersedes** / **Superseded by** — older meaning was replaced; preserve history and point forward.
- **Implemented by** / **Promoted to** — finding or design became code, task, decision, procedure, or accepted capability.
- **Resulted in** — this finding directly caused a later task/decision/experiment.
- **Evidence** / **Validated by** / **Tested by** / **Verified by** — proof supporting the current interpretation.
- **Blocked by** — current forward action is stopped by the linked dependency/boundary.
- **Revisit trigger** — explicit condition under which a dormant/rejected/parked idea should be reconsidered.

Prefer the strongest truthful relationship over generic `Related`.

## One-way links are enough

Do **not** manually maintain backlink pairs such as:

```text
A links to B
B must also be edited to link back to A
```

Canonical outbound relationships are enough. Backlinks/graph views should be derived by tooling. Manual backlink duplication creates stale maintenance work.

# Markdown links, wikilinks, and Obsidian

MAPS_L is intended to have **wiki behavior with tool-agnostic Markdown storage**.

The accepted repository convention is **standard relative Markdown links**:

```markdown
[Information Lifecycle](../../../playbook/INFORMATION_LIFECYCLE.md)
```

rather than relying only on an Obsidian-style wikilink:

```text
[[INFORMATION_LIFECYCLE]]
```

Why:

- standard relative links work directly on GitHub;
- they work in ordinary Markdown tools and agents;
- they work in Obsidian;
- they preserve an unambiguous repository path when duplicate filenames exist.

`tools/digital_fungus.py` understands **both ordinary Markdown links and Obsidian-style wikilinks**, so `[[...]]` links can still be recognized by analysis tooling. However, literal wikilinks should be treated as an optional convenience/derived view, not the only canonical relationship when the record lives in the repository.

Practical rule for these packets:

> **Write canonical repository relationships as relative Markdown links. Let Obsidian/backlink/graph tooling provide the wiki experience.**

If a future accepted convention explicitly adds `[[wikilink]]` syntax, reconcile this guide with that owner rather than maintaining two contradictory link standards.

# Connecting a new note into the Spiderweb

For each new forward-relevant topic note:

1. **Find its canonical parent/owner.** Usually an issue, task, roadmap, decision, project-memory file, procedure, or source artifact.
2. **Add at least one meaningful outbound relationship** when one exists. Do not invent a weak link merely to avoid being an orphan.
3. **Link evidence rather than copy it.** State the local implication, then point to the source.
4. **Record disposition.** If the note is deferred, rejected, partial, implemented, superseded, or dormant, say so and point to the successor/trigger where applicable.
5. **Update the packet README** if the topic should be independently discoverable from the packet hub.
6. **Cross-link the external owner** when useful and appropriate, such as adding the packet/topic link to the GitHub issue that will later implement it.
7. **Do not create manual backlink registries.** Let repository links and analyzers derive the graph.

## Disposition matters as much as connection

A Spiderweb that merely links old ideas together can still mislead a future agent.

Preserve the relationship from historical idea to current meaning:

```text
proposal
  ↓ decision
accepted / rejected / partial
  ↓ implementation or evidence
current result
  ↓ remaining / superseded / revisit trigger
future meaning
```

Useful disposition vocabulary for supporting notes may include:

- `OPEN`
- `EXPERIMENT`
- `PARTIAL`
- `INCORPORATED`
- `DUPLICATE`
- `SUPERSEDED`
- `REJECTED`
- `DORMANT`
- `NOT_DURABLE`

Do not treat this list as a new canonical task-state machine. It is descriptive note disposition unless/until an accepted owner defines a formal vocabulary.

# Digital Fungus check

[`tools/digital_fungus.py`](../../../tools/digital_fungus.py) is the read-only knowledge-graph and route-cost analyzer. It parses both Markdown links and wikilinks, reports broken links/unlinked mentions/orphan candidates, and measures route/read-cost proxies. It does **not** decide semantic truth or automatically edit notes.

When a packet is large enough that route quality is uncertain, or when adding it materially changes documentation structure, run:

```bash
python3 tools/digital_fungus.py --root .
```

Review especially:

- broken internal links;
- active orphan candidates;
- unlinked file mentions that should be real relationships;
- whether the packet has a short route to its owning issue/task/project;
- whether links create useful retrieval or merely graph noise.

Do not add random links solely to make an orphan count go down. [`playbook/INFORMATION_LIFECYCLE.md`](../../../playbook/INFORMATION_LIFECYCLE.md) explicitly prioritizes shortest reliable retrieval over a visually dense graph.

# Packet lifecycle

Follow the repository information lifecycle:

```text
capture → review → disposition → reconcile when reality changes
```

### Capture

Extract forward-relevant findings. Do not archive the entire chat by default.

### Review

Check whether each note has unique value, correct relationships, and an appropriate owner.

### Disposition

Mark what happened to the finding: deferred, implemented, rejected, superseded, incorporated, etc.

### Reconcile

When later evidence/implementation changes what the note means, preserve the historical finding but add/update its current disposition and successor links. Do not leave “future work” wording looking current after the work landed.

# Anti-sprawl rules

Before creating a note, ask:

> **Does this note own a distinct forward-relevant concept, or am I creating another copy of something that already has an owner?**

Prefer:

```text
small README hub
  → focused topic note
      → canonical task/issue/decision/evidence
```

over:

```text
README
  → summary
      → summary of summary
          → copied decision
              → copied evidence
```

Do not:

- dump full transcripts by default;
- create one file per conversational turn;
- preserve routine tool narration;
- create a second task/status database in Markdown;
- duplicate canonical decisions or procedures;
- add dozens of weak topical links;
- maintain hand-written backlink indexes;
- convert every interesting thought into an active task merely because it was captured.

# Minimum completion checklist

Before ending a durable conversation-capture pass:

- [ ] Every material topic has either an existing canonical owner or a focused note.
- [ ] The packet README routes to independently useful topics.
- [ ] Important notes have meaningful Spiderweb relationships to parent/source/decision/evidence/successor where applicable.
- [ ] Canonical repository links use standard relative Markdown syntax.
- [ ] Wikilink/Obsidian compatibility is not being used as the sole source of link truth.
- [ ] Current disposition is clear for deferred/rejected/partial/superseded findings.
- [ ] Volatile GitHub/runtime facts are labeled snapshots and require live recovery.
- [ ] No useful information remains only in chat.
- [ ] No transcript/context dump was created without a specific need.
- [ ] No duplicate authority or manual backlink registry was introduced.

The packet is successful when the conversation can disappear and the useful ideas remain **findable, connected, correctly disposed, and cheap to retrieve**.
