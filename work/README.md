# Work routing index

This is **navigation, not authority and not a live status database**. Start with
[`docs/FIRST_RUN.md`](../docs/FIRST_RUN.md); use this page only when you need a
durable record under `work/` and do not already know its path.

Live PR/CI/review/ownership facts belong on GitHub. Repository-wide rules belong
in [`AGENTS.md`](../AGENTS.md). Reusable procedures belong in the
[playbook index](../playbook/INDEX.md).

## Fast route

| Need | Go to | Read rule |
| --- | --- | --- |
| Current browser-agent coordination / live GitHub recovery | [`coordination/README.md`](coordination/README.md) | Read only for role-bound or coordination-sensitive work; then recover live GitHub. |
| Program roadmap / capability planning | [`roadmaps/README.md`](roadmaps/README.md) | Use this router before opening a large roadmap. |
| Exact task contract | [`tasks/`](tasks/) | Prefer the task path supplied by roadmap/PR/handoff; do not scan the directory by default. |
| Durable decision/rationale | [`decisions/`](decisions/) | Follow a link from the task/roadmap when possible. |
| Cross-session continuation | [`handoffs/`](handoffs/) | Prefer the handoff linked by the active task or [`state/CURRENT.md`](../state/CURRENT.md). |
| Independent review evidence | [`reviews/`](reviews/) | Open the review linked by the task/PR; do not treat old reviews as current disposition. |
| Review-queue records | [`review_queue/`](review_queue/) | Coordination aid only; live GitHub remains current. |
| Research / source investigation | [`research/`](research/) | Open from the task/research brief that owns the question. |
| Evaluation / simulation evidence | [`evals/`](evals/) | Evidence, not authority. |
| Generated or preserved reports | [`reports/`](reports/) | Read only when an active record links the report as evidence. |
| Security-specific work records | [`security/`](security/) | Use when the active task/risk route points here. |
| Candidate ideas | [`ideas/`](ideas/) | Discovery backlog; not active work merely because it exists. |
| Reusable observations | [`insights/`](insights/) | Evidence/learning; follow current disposition links before acting. |
| Design/working notes | [`notes/`](notes/) | Supporting context only; prefer current owner documents. |
| Frozen regression cases | [`regression-cases/`](regression-cases/) | Evidence artifacts per [`playbook/REPAIR_AND_LEARNING.md`](../playbook/REPAIR_AND_LEARNING.md); not authority on its own. |
| Context packets / imported context | [`context/`](context/) | Bounded context, not global authority. |

## Relationship rule

A forward-relevant durable record should normally have a deliberate route to the
record that gives it meaning: parent roadmap/task, source, decision, evidence,
review, handoff, implementation, successor, or disposition.

Use **standard relative Markdown links** in repository files. They work on
GitHub, Obsidian, and ordinary agent tooling. Prefer one useful outbound link to
the canonical owner over copied explanation or many weak topical links.

Do not optimize for graph density. A useful graph behaves like a road network:
small hubs, clear destinations, and short paths.

## Record templates

- Task: [`../templates/task.md`](../templates/task.md)
- Decision: [`../templates/decision.md`](../templates/decision.md)
- Handoff: [`../templates/handoff.md`](../templates/handoff.md)
- Review: [`../templates/review.md`](../templates/review.md)
- Research brief: [`../templates/research-brief.md`](../templates/research-brief.md)
- Roadmap: [`../templates/roadmap.md`](../templates/roadmap.md)

Do not create a new record class or index when an existing owner/path is adequate.
