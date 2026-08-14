# TASK-005 — Linked route-selection report

## Result

The minimum active-method set is **Research Before Architecture** and
**Project Bootstrap**, supported by **Risk and Change Control** for the initial
risk register. The roadmap method is relevant but deferred: a roadmap can be
prepared only after research informs an operator-approved direction. It must
not be used to imply that an implementation design, budget, or coding work has
been authorized.

## Actual linked route taken

1. Repository root [`README.md`](../../README.md) → canonical first-run route
   [`docs/FIRST_RUN.md`](../../docs/FIRST_RUN.md).
2. First Run → [`AGENTS.md`](../../AGENTS.md), the assigned
   [TASK-005](../tasks/TASK-005-linked-route-selection-simulation.md), and
   [`state/CURRENT.md`](../../state/CURRENT.md). Current state is unrelated to
   this evaluation, so it is a constraint source only.
3. First Run → [playbook index](../../playbook/INDEX.md).
4. The index → [Research Before Architecture](../../playbook/RESEARCH.md),
   [Project Bootstrap](../../playbook/PROJECT_BOOTSTRAP.md),
   [Risk and Change Control](../../playbook/RISK_AND_CHANGE.md), and
   [Roadmaps and ProjectUpdater Checklists](../../playbook/ROADMAP_AND_PROJECTUPDATER.md).
5. Project Bootstrap → [task template](../../templates/task.md) and
   [decision template](../../templates/decision.md). The index's continuation
   link → [Context](../../docs/CONTEXT.md) and the
   [handoff template](../../templates/handoff.md).

No legacy document, runtime command, or ProjectUpdater command was used.

## Methods considered and selection

| Method | Fit to scenario | Route decision |
| --- | --- | --- |
| Research Before Architecture | Pricing, authentication behavior, and SDK support are external, technical, and time-sensitive claims that have not been verified. The method requires source-grounded claims, dated retrieval, assumptions, and re-verification. | Selected. It produces evidence and recommendations only. |
| Project Bootstrap | The intended project spans sessions and agents, so it needs an explicit project brain, decision paths, risks, and durable locations before the first implementation task. | Selected. It establishes the project structure and authority boundaries. |
| Risk and Change Control | Third-party dependency choices can create availability, security, cost, and architecture risks. A change is not currently proposed, but bootstrap specifically calls for an initial risk register. | Supporting method, limited to recording risk ownership, mitigation, evidence, and reversibility; no change path begins now. |
| Roadmaps and ProjectUpdater Checklists | The operator eventually wants a ProjectUpdater roadmap, and this method defines its durable Markdown checklist/import source. | Deferred. It is useful after research and an operator-approved direction; it cannot grant design, budget, or implementation authority. |
| Task Lifecycle | A future implementation task will need shaping, assignment, and completion controls. | Not part of the minimum present route: Project Bootstrap says to write the first task only after its prerequisites are answerable. |

## Records to create first, in order

1. **Project brief** (Project Bootstrap record, no dedicated template linked):
   state intent, success condition, non-goals, quality standards, constraints,
   decision paths, and planned locations for tasks, decisions, evidence, and
   handoffs. Name the operator as the authority for budget and direction.
2. **Research brief and evidence/claims record** (Research Before Architecture
   flow, no dedicated template linked): make the API questions answerable;
   collect primary documentation/source evidence for price, authentication, and
   SDK support; attach precise locations, retrieval dates, disagreements,
   assumptions and blast radius, plus a re-verification date.
3. **Assumptions/unanswered-questions record and initial risk register**
   (Project Bootstrap plus Risk and Change Control): record unresolved facts
   and cost, availability, security, privacy, and architecture risks with an
   owner, mitigation, evidence needed, and rollback/reversibility path.
4. **Proposed decision record** from
   [`templates/decision.md`](../../templates/decision.md): summarize the
   research-backed options and tradeoffs for the operator. It remains
   `PROPOSED` until the operator selects a direction and approves any budget.
5. **Roadmap source checklist**, only after that decision: use
   Roadmaps and ProjectUpdater Checklists to make concrete, observable Markdown
   leaves. This is the future import source; do not run the legacy import
   command during evaluation or before approval.
6. **First scoped task** from [`templates/task.md`](../../templates/task.md),
   only when the brief, unknowns, risks, decision path, and approved roadmap
   make an implementation outcome and allowed paths observable.

## Authority boundaries

| Activity | Authorized result now | Not authorized now |
| --- | --- | --- |
| Research | Verify and date external facts; record evidence, assumptions, and recommendation. | Selecting a vendor, committing spend, changing a dependency, or writing code. |
| Architecture/design | Frame options and consequences in the proposed decision. | Declaring a design settled without the operator's decision. |
| Operator approval | Approve a direction, design/budget boundary, and any consequential next task. | Assumed from a request for research or an eventual roadmap. |
| Roadmap preparation | After approval, create the durable Markdown checklist that could be imported later. | Importing it into ProjectUpdater or treating checkboxes as implementation authorization. |
| Implementation | Begins only through a scoped, owned task with allowed paths and observable acceptance criteria. | Any coding at the present stage. |

## Verification

- The route above follows active Markdown links starting at the Lean root; it
  does not discover the route through a directory-wide search.
- The only files created for this evaluation are this report and its compact
  handoff.
