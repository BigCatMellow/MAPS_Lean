# Capability Status

This page does pin a dated subsystem inventory so readers can understand the
reconciled snapshot below. It must always be checked against live evidence and
the current roadmap/checklist before it drives a consequential decision.

> **Snapshot, not authority.** The canonical cross-roadmap status source is
> [`work/roadmaps/CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md).
> Re-check production code, tests, CI, and merged history before a consequential
> decision.

**Last capability reconciliation:** trajectory check #26 at `25c7729`

**Current Wiki-audit `main`:** `18b064c` (only later Wiki-source commits)

**Scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT STARTED**

Back to [[Home]]. For near-term development work, see [[Development]].

The decisive evidence is a **production call path / real behavior** and a real
caller/path, not only a unit test. A passing test or merged helper can prove that
machinery exists without proving that the capability row's exit gate is done.

## How to read a status

- **DONE** — the capability row's own exit gate is satisfied and reconciled.
- **IN PROGRESS** — real code/tests or design may exist, but the row's stated
  exit evidence is incomplete.
- **NOT STARTED** — the current checklist found no implementation that satisfies
  the row.

These labels apply to the named row, not every possible future version of the
idea. For example, Git worktree isolation is DONE even though automated
snapshot/rehydration is a separate NOT STARTED row.

## Canonical capability scoreboard

| Capability | Status |
| --- | --- |
| 6.1 Task truth, ownership and authority | **DONE** |
| 6.2 Provider-neutral Harness API | **DONE** |
| 6.3 Normalized ACI results | **DONE** |
| 6.4 Deterministic Hooks/Interceptors | **IN PROGRESS** |
| 6.5 Immediate deterministic validation | **DONE** |
| 6.6 Explicit run/session/helper/recovery lineage | **DONE** |
| 6.7 Explainable waits | **DONE** |
| 6.8 Reusable Agent Skills | **DONE** |
| 6.9 Skill routing and progressive disclosure | **DONE** |
| 6.10 Skill provenance, trust and quarantine | **IN PROGRESS** |
| 6.11 Context budgets / progressive context | **IN PROGRESS** |
| 6.12 Capability Packs | **NOT STARTED** |
| 6.13 EnvironmentSpec | **DONE** |
| 6.14 EnvironmentFingerprint and compatibility | **DONE** |
| 6.15 Harness/compute separation | **DONE** |
| 6.16 Git worktree isolation | **DONE** |
| 6.17 Sandboxes/snapshots/rehydration | **NOT STARTED** |
| 6.18 Revision-bound review/evidence | **DONE** |
| 6.19 Task-scoped helper continuity | **IN PROGRESS** |
| 6.20 Advisory NO_PROGRESS detection | **IN PROGRESS** |
| 6.21 Deterministic `maps flow` lifecycle operations | **IN PROGRESS** |
| 6.22 Memory trust classes | **IN PROGRESS** |
| 6.23 Agentic threat model and adversarial regression corpus | **DONE** |
| 6.24 Least-privilege capability intersection | **IN PROGRESS** |
| 6.25 Credential broker | **NOT STARTED** |
| 6.26 Portable Run Records / trajectories | **DONE** |
| 6.27 Outcome-linked incident taxonomy | **DONE** |
| 6.28 Frozen regression corpus | **DONE** |
| 6.29 Three-layer evaluation | **DONE** |
| 6.30 Operational learning lifecycle | **DONE** |
| 6.31 Controlled harness refinement | **NOT STARTED** |
| 6.32 Time-travel / fork debugging | **NOT STARTED** |
| 6.33 Semantic retrieval / query expansion | **IN PROGRESS — evaluation only** |
| 6.34 Mission / multi-task goal object | **NOT STARTED** |
| 6.35 Portable deployment to external projects | **IN PROGRESS** |

## Important IN PROGRESS distinctions

| Row | What exists | Why it is not DONE |
| --- | --- | --- |
| **6.4 Hooks** | Hook registry, canonical-run enforcement, destructive-action guard, and an opt-in production stop caller | `BEFORE_DESTRUCTIVE_ACTION` still lacks its own real exposure; wider write/credential guards are incomplete |
| **6.10 Skill trust** | provenance catalog, quarantine lifecycle, real flow-start refusal, operator-driven transitions, capability sidecars | third-party/countersign and wider activation/enforcement work remain |
| **6.11 context budgets** | budget classes and an on-demand Skill-resource surface | budget labels do not generally drive downstream retrieval/loading |
| **6.19 helper continuity** | exact-match metadata/TTL reuse candidates | no provider health check or automatic helper resume |
| **6.20 NO_PROGRESS** | read-only advisory from caller-supplied evidence | no provider integration, incident state, or recovery action |
| **6.21 flows** | five deterministic verbs with explicit stop boundaries | no full recover/replacement-session lifecycle; several steps remain intentionally separate |
| **6.22 memory trust** | LOAD/WITHHOLD/DENY gate, provenance renderer, guarded production send caller | no first live `BEFORE_SEND`/memory-provenance exercise yet |
| **6.24 least privilege** | task-policy/Skill-capability intersection and environment-report routing inputs | enforcement is partial; path-level and broader policy mappings remain incomplete |
| **6.33 semantic retrieval** | an evaluation candidate and tests | explicitly not a production context route |
| **6.35 portable deployment** | audit and design through first-pilot planning | no real external pilot has been completed |

## Evidence order

When a claim matters, use:

```text
observed production behavior
-> current tests and CI
-> current merged implementation
-> capability checklist status/evidence
-> roadmap or design
-> Wiki summary
```

Ask three separate questions:

1. Does the method or concept exist?
2. Does implementation and test machinery exist?
3. Is the required production path actually wired and exercised?

Only the evidence required by the row's own exit gate supports a status change.
A production caller can ship while the wider row remains IN PROGRESS.

## Deliberate exclusions from current behavior

- [PR #319](https://github.com/BigCatMellow/MAPS_Lean/pull/319) is not in
  `main`; established-mechanism supersession authority is not current behavior.
- Semantic synonym/query-expansion routing is not in production.
- Capability Packs, credential brokering, snapshots/rehydration, controlled
  harness refinement, time-travel debugging, and a Mission object are not
  implemented.
- Portable deployment has not been proven in a real external target project.

The checklist contains the row-by-row evidence and is intentionally more
detailed than this page.
