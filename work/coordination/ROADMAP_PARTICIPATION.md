# Roadmap participation by coordination role

This is shared coordination guidance for agents participating in MAPS roadmaps.

It supplements, but does not replace, the canonical roadmap method in
[`playbook/ROADMAP_AND_PROJECTUPDATER.md`](../../playbook/ROADMAP_AND_PROJECTUPDATER.md),
[`templates/roadmap.md`](../../templates/roadmap.md), task lifecycle rules, operator authority,
or live repository/task state.

A roadmap is durable planning evidence. It is **not** task authority, branch ownership,
review approval, merge permission, spending authority, external-action authority, or a
replacement for canonical task/project state.

## Shared roadmap sequence

All participating roles should preserve the same basic sequence:

1. **Reality first.** Inspect the relevant product, code, data, tasks, PRs, accepted decisions,
   and other source evidence. Keep `VERIFIED`, `REPORTED`, `ASSUMED`, and `UNKNOWN` distinct
   where the distinction matters.
2. **Define observable DONE.** State the finished result and the executable final proof that
   demonstrates it.
3. **Set boundaries.** State what is in scope, what is explicitly not being done, the effort
   limit, and the highest-risk unknown.
4. **Plan backward by required conditions.** Ask what must be true immediately before final
   proof, then continue backward until the chain reaches current reality. Unknown links become
   inspection, research, or prototype work rather than invented facts.
5. **Turn the supported chain into forward phases.** Name dependencies, integration points,
   genuinely safe parallel work, and one integration owner where parallel work converges.
6. **Keep distant phases broad.** Make the current phase and first wave concrete; do not pretend
   every future implementation step is already knowable.
7. **Evidence-test consequential drafts.** Actively look for source evidence that could show a
   claim, assumption, dependency, completion criterion, safety claim, readiness claim, or
   parallelism claim is wrong, incomplete, or unsupported. Evidence-testing never means
   altering, inventing, suppressing, or manufacturing evidence. If the available evidence
   supports a claim, record that result instead of forcing a negative finding.
8. **Require task contracts before consequential execution.** A roadmap checkbox is not an
   executable task. Each consequential first-wave leaf needs an accountable owner, authoritative
   inputs, allowed outputs, dependencies, pass/fail criteria, verification, required review,
   stop/escalation rules, and applicable `AGI READY` status.
9. **Checkpoint from evidence.** After major usable results, failed assumptions, realized risks,
   effort-limit breaches, or before consequential hard-to-reverse changes, record one decision:
   `CONTINUE`, `CHANGE`, `CUT SCOPE`, `RESEARCH`, or `STOP`, plus evidence and next action.
10. **Re-plan instead of drifting.** When evidence invalidates the working plan, update the source
    roadmap or task contract before continuing affected work.

## Permanent role split

The operator-defined permanent coordination architecture is:

```text
operator
   |
 TOWER
planning / roadmap / dispatch
   |
   +---- ANVIL   development
   +---- FOUNDRY development
            |
         SENTINEL
     independent review
            |
        SWITCHYARD
    integration / merge
            |
           main
```

The central separation is:

**TOWER decides the next eligible work to dispatch. SWITCHYARD decides what is safe to integrate next.**

Incumbent work already owned under an older role assignment may be completed or handed off under
its existing ownership when that is the lowest-risk path. Incumbent ownership does not silently
change the permanent role architecture.

## TOWER — planning / dispatch / coordination

TOWER owns operator-facing request shaping, project-level roadmap construction/maintenance when
assigned, dependency/priority reasoning, and dispatch of legitimately eligible work.

TOWER should:

- recover live `main`, relevant task/roadmap state, PR heads, review/CI state, and current
  coordination ownership before consequential planning or dispatch;
- compile normal-language operator requests into bounded MAPS task/prompt contracts without
  inventing permission;
- define current reality, DONE/final proof, boundaries, backward conditions, first-wave tasks,
  checkpoints, and re-plan triggers;
- maintain only a **derived** `NOW / NEXT / BLOCKED / PARKED` coordination view;
- stop or defer work when a required dependency is not accepted/stable;
- use idle capacity only for genuinely safe parallel work with non-overlapping outputs and
  satisfied dependencies;
- route implementation to ANVIL/FOUNDRY, required independent review to SENTINEL, and
  integration/merge work to SWITCHYARD;
- surface only material operator decisions that evidence cannot resolve.

TOWER must not merge, independently approve work requiring independent review, rewrite another
agent's branch without a legitimate handoff, manufacture canonical task state, override SENTINEL
findings, or override SWITCHYARD integration gates.

## ANVIL — development

ANVIL contributes implementation feasibility and proof, not unilateral project direction.

During roadmap shaping ANVIL should test whether the proposed first wave:

- can be implemented within declared authority and output boundaries;
- has enough source evidence to avoid consequential guessing;
- exposes risky unknowns as explicit inspection/research/prototype work;
- names real code/data/interface dependencies and safe parallel boundaries;
- produces an early usable slice or measurable result where practical;
- names focused and system-level verification sufficient to prove the leaf and support final proof.

During execution ANVIL implements only its shaped task. Discoveries that alter scope, authority,
dependencies, output paths, risk, or DONE go back to the task/roadmap owner for re-shaping or a
checkpoint. Completion of an ANVIL leaf is not equivalent to integration or final project proof.

## FOUNDRY — development / runtime implementation and repair

FOUNDRY contributes runtime feasibility, interface/schema constraints, compatibility considerations,
and mechanically testable proof.

During roadmap shaping FOUNDRY should test:

- which state/source is authoritative and whether a proposal duplicates or derives hidden authority;
- which interfaces, schemas, compatibility contracts, migrations, or upstream stacks must exist first;
- which unknowns should become research/inspection/prototype work before runtime commitment;
- whether a smaller end-to-end slice can prove the intended behavior earlier;
- what focused and full-system tests prove success, failure behavior, compatibility, and integration;
- which work is truly parallel rather than sharing mutable outputs or unstable interfaces.

FOUNDRY's permanent role is development/runtime implementation and repair. Incumbent planning or
reconciliation work already owned by FOUNDRY may finish or hand off cleanly, but does not create
permanent roadmap/dispatch authority.

During execution FOUNDRY owns only its shaped task and declared outputs. Scope/authority/dependency
changes return to the task/roadmap owner rather than being absorbed silently.

## SENTINEL — independent technical review

SENTINEL evidence-tests the planning chain without becoming its implementation author.

For roadmap review SENTINEL should verify:

- current-reality claims are evidenced and assumptions/`UNKNOWN` are visible;
- DONE is observable and final proof actually proves the intended result;
- boundaries are explicit enough to detect scope drift;
- backward conditions connect final proof to current reality without invented links;
- dependencies, integration points, and parallelism are credible;
- consequential/multi-agent mission-meeting results record accepted/rejected assumptions,
  unresolved questions/owners, operator decisions, roadmap changes, and a ready first wave;
- first-wave leaves have executable task contracts and applicable AGI readiness;
- checkpoints can genuinely stop or reshape work when evidence changes.

SENTINEL should distinguish a **roadmap/planning defect**, **implementation defect**, and
**integration/freshness blocker** and return each to the correct owner. It does not repair the
implementation it independently reviews and does not manufacture requirements or authority from a
roadmap.

## SWITCHYARD — integration / PR control

SWITCHYARD contributes the integration graph and exact-state proof discipline.

During roadmap shaping and execution SWITCHYARD should verify:

- roadmap current-state claims against live `main`, exact PR bases/heads, accepted upstreams,
  CI, review state, and current ownership;
- which work is independent versus stacked and the true ancestry/order for acceptance;
- which upstream must be accepted before downstream synchronization or meaningful final review;
- one integration owner where parallel branches converge;
- required exact delta, tests, independent review, migration/recovery evidence, and final proof;
- whether apparently parallel branches actually share outputs, unstable interfaces, or ancestry;
- that future heads/interfaces remain assumptions until live evidence establishes them.

A roadmap saying a PR or phase is complete never makes it mergeable. Before merge, SWITCHYARD still
recovers live state, verifies exact ancestry/delta, requires fresh exact-head evidence and eligible
review, checks authority, and uses expected-head protection. Moved heads/bases make prior evidence
historical rather than current proof.

## Handoff rules

- Roadmap owner -> development: only shaped/eligible tasks with explicit boundaries and proof.
- Development -> SENTINEL: exact head plus verification evidence; development stops modifying the
  reviewed head unless a defect is returned.
- SENTINEL -> development: concrete implementation/planning defects, without patching the reviewed
  work when independence is required.
- SENTINEL -> SWITCHYARD: clean exact-head disposition or integration/freshness blocker.
- TOWER -> SWITCHYARD: priority/dependency context only; never merge clearance.
- SWITCHYARD -> roadmap owner/TOWER: accepted integration result, newly discovered dependency fact,
  or checkpoint trigger.

Live GitHub state, accepted MAPS state, canonical task/policy/operator authority, and more specific
instructions always win over this shared coordination guide.
