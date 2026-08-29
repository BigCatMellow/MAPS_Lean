# First Run

Use this route when joining the repository. Orientation should end as soon as you
can name the owner, allowed scope, next action, verification, and escalation
boundary.

## Minimum route

1. Read [`AGENTS.md`](../AGENTS.md), the **single repository-wide operating contract**.
2. Read the approved roadmap/project scope and active task. If authorized roadmap
   work exists but no child task does, the orchestration operator shapes/selects
   the next in-scope task and continues.
3. Select **one** relevant method from the [playbook index](../playbook/INDEX.md).
   Read a second only when a distinct concern actually requires it.
4. Confirm owner, outputs/actions, acceptance criteria, verification/review, and
   the true authority boundary. Shape missing detail inside inherited authority;
   escalate only a real boundary crossing.

Common-case reading budget:

```text
AGENTS.md + approved roadmap/task + one relevant playbook method
```

## Route by need

Do not browse directories to discover these paths:

| Need | Route |
| --- | --- |
| Role-bound browser session / PR coordination | [`work/coordination/README.md`](../work/coordination/README.md) → required coordination route → live GitHub |
| Resume prior cross-session work | [`state/CURRENT.md`](../state/CURRENT.md) → linked handoff → live GitHub |
| Find a `work/` record class | [`work/README.md`](../work/README.md) |
| Capability/roadmap question | [`work/roadmaps/README.md`](../work/roadmaps/README.md) before opening a large roadmap/checklist |
| Runtime/control-plane concern | [`playbook/CONTROL_PLANE.md`](../playbook/CONTROL_PLANE.md) |
| Fresh runtime installation | [`docs/FRESH_INSTALL.md`](FRESH_INSTALL.md) |
| Verification/review level | [`docs/CHECKS_AND_BALANCES.md`](CHECKS_AND_BALANCES.md) |

Read current state only for continuation/coordination. Read control-plane material
only when runtime state/routing/recovery/transport matters. Read `legacy/` only
when an active higher-level source links a specific legacy source for a specific
reason.

Do not read the whole wiki, `work/`, roadmap corpus, or playbook as a prerequisite
ritual. If routine work requires stitching several overlapping documents together,
treat that as a routing/consolidation problem.
