# Pilot memory/context review — conversation capture

Status: **supporting design/review notes; not implementation authority**.

Captured from the 2026-09-01 through 2026-09-03 operator discussion about Pilot/MAPS_L continuity, project memory, AI-facing instruction wording, context compilation, Prime Agent execution architecture, and implementation collision avoidance.

This packet exists because the discussion produced several distinct forward-relevant topics that should not remain trapped in chat history or be collapsed into one oversized note.

## Read by question

| Question | Note |
| --- | --- |
| How should notes like these be created, split, connected into the Spiderweb, and linked for GitHub/Obsidian use? | [Authoring Conversation-Derived Note Packets](AUTHORING.md) |
| How should Pilot make durable project memory so a fresh chat can continue without the old conversation? | [Durable Project Memory](durable-project-memory.md) |
| What did the MAPS_L instruction/context review conclude about `AGENTS.md`, wording, routing, context packets, and evaluation? | [AI Instruction and Context Architecture](ai-instruction-context-architecture.md) |
| What is Prime Agent's current potential role in MAPS_L, and which execution mechanisms should be adapted, merged, or incorporated rather than reimplemented? | [Prime Agent / MAPS_L Incorporation Review](prime-agent-mapsl-incorporation.md) |
| Where was MAPS_L in implementation, what active-agent collision risk was found, and what changed by 2026-09-03? | [Implementation and Collision State](implementation-and-collision-state.md) |
| What procedure is missing for turning conversations like this into durable, multi-topic repository notes? | [Conversation Capture Procedure Gap](conversation-capture-procedure-gap.md) |
| How should these findings be re-entered later for review and implementation without trusting this packet as live state? | [Implementation / Re-entry Plan](implementation-reentry-plan.md) |

## Authoring / Spiderweb rule

For future notes derived from conversations, start with [AUTHORING.md](AUTHORING.md). It explains:

- when a multi-topic note packet is justified;
- how to split by future meaning/owner rather than conversation chronology;
- the suggested topic-note shape;
- the Spiderweb principle that **nothing durable should be an island**;
- meaningful relationship labels such as `Derived from`, `Depends on`, `Superseded by`, `Implemented by`, `Evidence`, and `Revisit trigger`;
- why canonical repository edges should use standard relative Markdown links;
- how Obsidian-style `[[wikilinks]]` fit as optional/derived wiki behavior rather than the sole canonical link format;
- why backlinks should normally be derived rather than maintained manually; and
- how `tools/digital_fungus.py` can check broken links, orphan candidates, and route cost.

Repository-wide ownership remains with [`playbook/INFORMATION_LIFECYCLE.md`](../../../playbook/INFORMATION_LIFECYCLE.md), [`work/README.md`](../../README.md), and [`AGENTS.md`](../../../AGENTS.md). The local authoring guide does not override them.

## Related durable items

- GitHub issue **#247** — `Deferred feature: Durable Project Memory for Pilot-managed work`.
- GitHub issue **#248** — `Deferred architecture cleanup: AI instruction/context compilation and wording`.
- Existing project-memory foundations: [`playbook/PROJECT_BOOTSTRAP.md`](../../../playbook/PROJECT_BOOTSTRAP.md), [`playbook/INFORMATION_LIFECYCLE.md`](../../../playbook/INFORMATION_LIFECYCLE.md), [`work/README.md`](../../README.md), and Portable Deployment design under [`work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`](../../roadmaps/agent-harness-capabilities/06-portable-deployment.md).
- Prime/harness design owners: [`work/roadmaps/prime-agent-capability-roadmap.md`](../../roadmaps/prime-agent-capability-roadmap.md) and [`work/roadmaps/agent-harness-capabilities/README.md`](../../roadmaps/agent-harness-capabilities/README.md).

## Authority / freshness rule

These notes preserve findings and intended direction. They do **not** freeze volatile facts such as open PRs, current branch heads, CI, active ownership, roadmap status, Prime release state, or exact runtime seams.

Before implementation:

1. recover current `main`;
2. recover live GitHub coordination and active PR/branch overlap;
3. re-read the current owning roadmap/task/procedure;
4. re-check external implementation sources when a note depends on them;
5. reconcile these notes against accepted code/docs; and
6. implement only the still-valid smallest coherent slice.

The durable goal is recoverability of the ideas, not preservation of stale implementation snapshots.
