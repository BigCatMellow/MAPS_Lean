# Capability Status — How to Tell What Is Real

This page does **not** pin a dated subsystem inventory. That was useful during a
specific audit, but it became stale and could cause a fresh agent to operate on
old assumptions.

Back to [[Home]].

## Live capability truth belongs in the repository

When deciding whether MAPS_L can actually do something today, use this evidence
order:

```text
production call path / real behavior
        ↓
current tests + CI evidence
        ↓
current runtime/source implementation
        ↓
CAPABILITY_CHECKLIST status + evidence
        ↓
roadmap/design notes
        ↓
wiki summaries
```

The canonical cross-roadmap status surface is
[`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md).
Re-verify important claims against current code/tests before making a
consequential decision.

Do not use an old commit count, PR number, test count, or wiki snapshot as live
truth.

---

## Three questions for every capability

A fresh operator should distinguish:

1. **Does the method/concept exist?** Documentation or design may answer yes.
2. **Is there implemented/tested machinery?** Source and tests may answer yes.
3. **Is it production-wired on the path I need?** Only a real call path or
   executed behavior answers this.

A capability can pass #1 and #2 while still being unusable as an autonomous
production dependency.

Useful shorthand when auditing:

- **wired** — implemented, tested, and invoked by a real active path;
- **implemented/tested** — real machinery exists but the needed production path
  is not proven;
- **design/scaffold** — documentation, schema, enum/type, or planned mechanism
  without the required behavior.

These are evidence descriptions, not replacement status labels for the canonical
checklist.

---

## Capability map: what each part is for

| Capability | Use it for | Do not confuse it with |
| --- | --- | --- |
| Operating contract + playbook | stable methods, task shaping, review, routing principles | runtime enforcement |
| Task/roadmap records | human-readable objective, scope, criteria, decisions, evidence | concurrent mutable task truth |
| SQLite task state | guarded claims, lifecycle, ownership/review facts | project permission or planning |
| LangGraph | deterministic route selection/checkpointing from known state | authority, product planning, or parent ownership |
| hcom | messages/session transport | task truth or authority |
| RnS | bounded recovery of known active sessions | inventing/reassigning new work |
| Helpers / agent slots | bounded delegated execution/research/review | parent ownership |
| Execution integrity | bind consequential runs to exact contract/context/scope/proof | new permission |
| Model capability routing | choose a competent worker/harness/effort | permission to perform an action |
| Skills / retrieval / learning mechanisms | focused context or evaluated reusable capability when live | automatic authority or truth promotion |

For component boundaries, use
[`playbook/CONTROL_PLANE.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/CONTROL_PLANE.md)
and the current `runtime/` + `tests/` tree.

---

## Before depending on a runtime feature

Check all of these when material:

```text
1. Is the feature present in current main?
2. Is there a test for the behavior I need?
3. Is there a real caller/path, not only a unit test?
4. Does the path preserve MAPS_L authority/ownership invariants?
5. Is the capability gated, experimental, or evidence-limited by the roadmap?
6. What happens on failure or missing evidence?
```

If #3 is unknown, treat “production-wired” as unverified.

---

## Gated work is not an invitation

`NOT STARTED`, `TRIGGERED`, `EVIDENCE-GATED`, deferred, or explicitly rejected
work must be interpreted from the **current roadmap/checklist**, not from this
wiki.

An orchestration operator should make forward progress inside the approved
objective, but initiative does not mean crossing a deliberate gate. If a
candidate action would create a new objective or cross the approved permission
envelope, that is a reauthorization boundary.

---

## For a fresh agent

Unless your task is specifically to develop MAPS_L itself, you usually do not
need the entire capability inventory. Start with the method-only/orchestrated
workflow on [[Home]], then inspect runtime capability only if the task actually
needs the control plane.

The best use of MAPS_L is not “turn on every subsystem.” It is **apply the
smallest reliable mechanism that removes a real coordination or verification
failure mode.**
