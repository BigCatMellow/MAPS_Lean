# Durable Memory Index Readiness Audit — 2026-07-18

- Status: `evidence-only; implementation deferred`
- Owner: `codex-lab-lilo`
- Audit helper: `helper-review-steward-moku`
- Scope: fresh-session navigation only; no index, task, policy, or shared-state change
- Related task: `TASK-227` (`CHANGES_REQUESTED`, owner `claude-lab-gome`)

## Principal finding

**INVESTIGATE — do not create `MAP_System/notes/INDEX.md` yet.**
`MAP_System/shared/memory-map.md` already presents itself as MAP's durable
Markdown-memory index. It has useful current/historical routing, but it is not
yet a safe canonical orientation surface: it conflicts with other startup read
contracts and names a missing target, `notes/task-metadata-repair-plan.md`.
A second index now would add a shadow route before the existing one is
reconciled. The smallest safe next action is to finish TASK-227's required
bounded index design, explicitly choosing whether to repair `memory-map.md` or
to create a thin notes projection.

## 1. Smallest durable orientation set after `AGENTS.md`

This is the smallest *required plus conditional* set supported by current
rules. It is not a request to load every file at startup.

| Path | State | Role | Read when | Authority / use |
|---|---|---|---|---|
| `MAP_System/shared/current-state.md` | CURRENT | live system posture | every session | Canonical current state; preferred over historical artifacts. |
| `MAP_System/shared/memory-map.md` | CURRENT, but stale-link evidence found | navigation | every session | Navigational reference, not an authority for task state or decisions. It classifies canonical versus historical memory. |
| `MAP_System/shared/project-brief.md` | CURRENT | objective | every session under `MAP_System/AGENTS.md` Core Protocol | Canonical project purpose/completion condition. |
| `MAP_System/shared/requirements.md` | CURRENT | operating requirements | every session under Core Protocol | Canonical requirements/capabilities. |
| `MAP_System/shared/decisions.md` | CURRENT | approved authority/architecture decisions | every session under Core Protocol; mandatory for authority/policy work | Canonical approved decision record. |
| `MAP_System/agents/operational-lessons.json` | CURRENT, scoped | active promoted behavior | startup scopes only | Canonical active-lesson source; orientation command output is a projection, not a new authority. |
| `MAP_System/tasks/TASK-NNN.json` | CURRENT when assigned | executable work | only after assignment/claim routing | Canonical task scope; then read registered inputs/outputs. |

Conditional, not baseline: `agents/status.json` plus live `hcom list` for
availability; latest relevant handoff; task input/output paths; a runbook such
as `notes/review-guide.md` or `notes/helper-agent-guide.md`. `artifacts/`,
`inbox/`, and most `handoffs/` are HISTORICAL or scoped evidence, not a global
startup source. `notes/` generally describes procedure; it is useful reference
but not a replacement for current state, decisions, or an assigned task.

Evidence: `MAP_System/AGENTS.md` Core Protocol requires project brief,
requirements, decisions, and task file; `notes/context-routing-guide.md`
requires current state/memory map/task; the lab startup note additionally
requires operational lessons, durable/live agent checks, and handoff/task graph
checks. The differing lists are why the index must route by trigger rather than
claim that one flat list fits every session.

## 2. Current navigation evidence and gaps

| Evidence | Finding | Classification |
|---|---|---|
| `shared/memory-map.md` §Read First | It already calls itself the index for durable Markdown memory and routes AGENTS → current-state → memory map → task. | ESSENTIAL to reconcile before adding a peer index. |
| `notes/context-routing-guide.md` §Default Context Stack | It adds task input/output paths and describes conflict precedence, but its default differs from the AGENTS Core Protocol. | ESSENTIAL: index must link to the controlling trigger, not collapse rules. |
| `notes/command-center-lab-restart-startup.md` §Startup orientation | Startup requires operational lessons, live hcom state, durable agent state, task graph, and handoff checks. | LIKELY: give startup a dedicated route rather than make all task sessions read it. |
| `notes/README.md` and `shared/memory-map.md` | `notes/README.md` omits current Pi, restart, operational-learning, and incident-taxonomy notes; `memory-map.md` names missing `notes/task-metadata-repair-plan.md`. | ESSENTIAL: initial population must be checked against actual paths. |
| `emergence/README.md`, `IDEA_PROMOTION_RULES.md`, `notes/operational-learning-guide.md` | E/I creates candidates; promoted lessons become scoped active behavior. | LIKELY: index as a route only; never turn raw E/I records into mandatory startup policy. |

Observed scope: 31 Markdown files under `MAP_System/notes/` and 22 under
`MAP_System/shared/`. A complete directory listing is therefore not a bounded
fresh-session contract.

## 3. Proposed bounded index schema

This schema is a proposal, not a new policy or file.

| Field | Required value | Guardrail |
|---|---|---|
| `path` | Existing repo-relative path | The entry links; it does not copy the target's facts. |
| `role` | `authority`, `current-state`, `task`, `navigation`, `procedure`, or `historical-evidence` | A navigation entry cannot confer authority. |
| `lifecycle` | `CURRENT`, `HISTORICAL`, or `SCOPED` | `SCOPED` requires a trigger, such as assigned task or startup. |
| `read_when` | Concrete trigger and next hop | Prevents every session from loading every note. |
| `canonical_for` | Exact domain or `none` | Points to the source of truth; never summarizes mutable status. |
| `owner` | Existing state/document owner | Maintenance follows existing ownership. |
| `verified_against` | Existing metadata/date or `unverified` | Makes stale entries visible instead of silently authoritative. |
| `supersedes_or_note` | Direct path or `none` | Supports historical routing without deletion. |

Maximum initial scope: **12 routes**: the seven baseline/conditional routes
above plus one each for review, helper routing, task authoring, operational
recovery, and emergence/promotion. No task rows, hcom messages, inbox notes,
handoffs, artifacts, runtime status values, or copied acceptance criteria.

Maintainer and trigger: the current `shared/memory-map.md` state owner
(`command-center`) remains accountable for the navigation contract. A task
owner who adds, supersedes, or materially changes a CURRENT operating document
proposes its row update in that same task; independent review checks the five
lookup samples below. A missing/ambiguous classification is `unverified`, not
an inferred route.

Link rule: the index may point to canonical sources and say when to read them.
It must not mirror task status, agent presence, capacity, authority rules, or
lesson text. Those values remain in their existing sources and their existing
precedence rules.

## 4. Two fresh-session path walks

| Path (maximum two hops after index) | Context retained | Loss / stale risk | Required route correction |
|---|---|---|---|
| Rework an assigned task: Index → `tasks/TASK-227.json` → `notes/system-improvement-implementation-plan.md` | Owner, status, registered output, and submitted plan. | TASK-227 is `CHANGES_REQUESTED`, but its task JSON has no review artifact in `input_paths`; the plan itself does not point to the five REQUIRED review findings. A fresh agent can reach the plan without the required rework constraints. | The task/rework route must explicitly include the latest review record (here `artifacts/reviews/task227-review-lilo.md`) when status is `CHANGES_REQUESTED`; do not embed findings in the index. |
| Set up a bounded helper: Index → `notes/helper-agent-guide.md` → `notes/local-model-helper-guide.md` | Visibility, owner, scoped-note, and local-model authority boundaries. | It does not by itself load live availability (`hcom list`/`agents/status.json`) or scoped active lessons. A stale generic route could select an unavailable or paused lane. | The helper route must name `current-state`, live/durable availability checks, and operational-lesson lookup as conditional checks, not infer a helper's capacity from the index. |

These walks show that ≤2 hops is feasible only for navigation. Required
task/review facts and live capacity still belong to their existing sources.

## 5. Recommended smallest follow-on and measurable evidence

### Immediate legitimate action

**ESSENTIAL — complete TASK-227 rework first.** Its independent review already
requires a bounded initial population, five lookup samples, new-note
classification, and maintainer/update path. It also remains owned by
`claude-lab-gome`; this audit does not transfer ownership or authorize edits.

### Proposed implementation task after that rework is approved

- Suggested title: `Reconcile fresh-session navigation without a second source of truth`.
- Suggested owner: `claude-lab-gome` (or explicitly reassigned core owner).
- Suggested reviewer: a different core reviewer; reproduce the five lookups
  from a fresh context packet.
- Scope: first choose the canonical navigation host. Prefer repairing
  `shared/memory-map.md`; create `notes/INDEX.md` only if the approved plan
  shows why a notes-only projection is needed and how it remains subordinate.
- Output limit: one navigation file plus, if necessary, one short evidence
  artifact. No policy, task-state, authority, or runtime changes.

Acceptance evidence:

1. Every initial entry resolves to an existing path; the missing
   `notes/task-metadata-repair-plan.md` reference is removed, corrected, or
   explicitly HISTORICAL with a valid replacement.
2. Five reproducible lookup samples identify the governing document in ≤2
   hops: active-task rework, review, helper routing, startup/recovery, and
   E/I promotion.
3. Each sample labels the target CURRENT/HISTORICAL/SCOPED and names its
   canonical source. The index contains no copied mutable state.
4. A new-note classification procedure names owner, trigger, and a no-guess
   outcome for ambiguous notes.
5. An independent reviewer confirms links, samples, and that the index did
   not become authority or a startup-wide loading mandate.

## 6. Recommendation classification

| Proposal | Class | Reason |
|---|---|---|
| Reconcile existing `shared/memory-map.md` before any new index | ESSENTIAL | It is already an index and has a missing target. |
| Bound first population, five lookup samples, maintainer, and trigger | ESSENTIAL | Directly resolves TASK-227 review finding C2. |
| Route by task type/startup trigger, with CURRENT/HISTORICAL/SCOPED labels | LIKELY | Reduces context without suppressing authority or live-state checks. |
| Thin notes-only projection capped at 12 routes | OPTIONAL | Useful only if the approved rework shows `memory-map.md` cannot carry the route cleanly. |
| Automatic index validator or broad note inventory | OPTIONAL | Defer until measured drift persists; one stale link does not justify another gate yet. |
| Create `notes/INDEX.md` immediately | INVESTIGATE | Current evidence favors repair/host decision first; immediate creation risks a duplicate navigation authority. |

## Blocker

No blocker to the audit. Implementation should wait for TASK-227 rework because
the current plan is `CHANGES_REQUESTED` and its index action has the exact
unresolved design gaps this audit measured.

## Sources

- `MAP_System/AGENTS.md`
- `MAP_System/tasks/TASK-227.json`
- `MAP_System/artifacts/reviews/task227-review-lilo.md`
- `MAP_System/notes/system-improvement-implementation-plan.md`
- `MAP_System/shared/current-state.md`, `shared/decisions.md`, `shared/memory-map.md`, `shared/README.md`
- `MAP_System/notes/README.md`, `context-routing-guide.md`, `helper-agent-guide.md`, `local-model-helper-guide.md`, `command-center-lab-restart-startup.md`, `operational-learning-guide.md`, `documentation-style-guide.md`
- `MAP_System/shared/hpom.md`
- `MAP_System/emergence/README.md`, `MAP_System/emergence/IDEA_PROMOTION_RULES.md`
