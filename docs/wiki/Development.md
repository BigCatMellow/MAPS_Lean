# Development

> **Status snapshot, not authority.** GitHub `main`, approved task/roadmap
> state, and
> [`CAPABILITY_CHECKLIST.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
> remain canonical. Open PRs and proposals do not change current behavior.

**Last refreshed:** 2026-09-09

**Current canonical `main`:** `18b064c` — later than the capability
reconciliation only by two Wiki-source commits

**Canonical capability scoreboard:** **19 DONE / 10 IN PROGRESS / 6 NOT
STARTED**, re-derived at `25c7729` by trajectory check #26

For the deeper maintained view, open the
[MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit).
The scheduled `MAPS Lean Daily` process maintains its Development tab; this page
is a compact published snapshot.

Back to [[Home]].

## Current focus

The immediate focus is row-specific enforcement evidence. Production call sites
already exist for both items below, but implementation alone is not closure.

| State | Work | Required next evidence | Constraint |
| --- | --- | --- | --- |
| **NEXT** | **6.4 destructive-action enforcement** | exercise the smallest safe real `--terminate-denied-sessions` path that reaches `BEFORE_DESTRUCTIVE_ACTION` | no DONE flip until that Hook's own evidence is reviewed; write/credential guard gaps also remain |
| **NEXT** | **6.22 send/memory provenance** | exercise one safe bound-run `send-context --deliver-context` path and capture `BEFORE_SEND` plus provenance behavior | the command is default-off and fail-closed; no status flip from the merged caller alone |

Relevant shipped call sites:
[PR #306](https://github.com/BigCatMellow/MAPS_Lean/pull/306) and
[PR #310](https://github.com/BigCatMellow/MAPS_Lean/pull/310).

## In review / proposed

| State | Item | Current verified position |
| --- | --- | --- |
| **IN REVIEW — NOT CURRENT** | [PR #319](https://github.com/BigCatMellow/MAPS_Lean/pull/319), Emergence mechanism-supersession authority | Its head is not in `main`. The branch now contains independent APPROVE evidence, a Tenth Seat YELLOW report recommending merge, and a recorded narrow/conditional operator substance ruling. Until merged, the Wiki documents this only as a proposal. |
| **DECISION / DISPOSITION NEEDED** | trajectory-check #26 follow-ups | Recurring insight/idea items still need explicit promote, defer, revise, or kill dispositions; captured ideas do not authorize work by themselves. |

No open PR is counted in the scoreboard above.

## Recently shipped

- **Wiki Development surface — SHIPPED.** Commits `d042ab2` and `18b064c`
  added the status page and top-level navigation without changing capability
  state.
- **Trajectory check #26 — SHIPPED.** [PR #318](https://github.com/BigCatMellow/MAPS_Lean/pull/318)
  re-derived **19 / 10 / 6**, confirmed 6.16 DONE, and kept 6.4/6.22 IN
  PROGRESS pending their own first-exposure evidence.
- **Cross-root synthesis — SHIPPED.** [PR #315](https://github.com/BigCatMellow/MAPS_Lean/pull/315)
  added deliberate comparisons across roots/arcs/domains without expanding
  Capture or Promote authority.
- **`HCOM_DIR` precedence — SHIPPED.** [PR #317](https://github.com/BigCatMellow/MAPS_Lean/pull/317)
  established explicit flag > inherited environment > `.hcom`, with a one-time
  warning on resolved-path conflict.
- **Tagged hcom session resolution — SHIPPED.** [PR #313](https://github.com/BigCatMellow/MAPS_Lean/pull/313)
  reconciled display names and `base_name` while refusing ambiguity.
- **Worktree requirement failure — SHIPPED.** [PR #308](https://github.com/BigCatMellow/MAPS_Lean/pull/308)
  made `--require-worktree-binding` fail with
  `WORKTREE_BINDING_REQUIRES_BASE_REVISION` when `--base-revision` is absent;
  [PR #314](https://github.com/BigCatMellow/MAPS_Lean/pull/314) aligned related
  help text.
- **Guarded context-send caller — SHIPPED, capability incomplete.**
  [PR #310](https://github.com/BigCatMellow/MAPS_Lean/pull/310) added the
  default-off `HarnessService.send()` route; 6.22 still lacks the live Hook
  exposure required for DONE.
- **Guarded stop caller — SHIPPED, capability incomplete.**
  [PR #306](https://github.com/BigCatMellow/MAPS_Lean/pull/306) added bounded
  optional session termination after persistent canonical denial; 6.4 still
  lacks the destructive Hook's own exposure and broader guard work.

## Broad capability areas

| Area | Current read | Main limitation / next direction |
| --- | --- | --- |
| Harness mechanics | advanced, active | finish row-specific destructive Hook evidence |
| Skills | explicit-first routing DONE; supply-chain controls active | no semantic synonym routing; 6.10 remains incomplete |
| Environment/worktrees | worktree enforcement DONE; wider environment work mixed | no snapshot/rehydration; some routing/validation evidence still partial |
| Security | canonical denial and incident corpus demonstrated | 6.4 and 6.22 need distinct Hook exposures; credential broker not started |
| Flow lifecycle | five verbs implemented | no complete recovery/replacement lifecycle; 6.21 remains IN PROGRESS |
| Learning/evaluation | trajectory, triage, regression cases, Emergence, and cross-root synthesis operate | research experiments and controlled refinement remain incomplete |
| Portable deployment | design and preflight planning exist | no real external pilot yet |

## Likely next sequence

1. Produce and review the first real 6.4 destructive-action Hook exposure.
2. Produce and review the first real 6.22 send/provenance Hook exposure.
3. Reconcile only the exact checklist rows supported by those observations.
4. Finish disposition/merge handling for #319 while keeping it proposal-only
   until it lands.
5. Select the next capability increment from the updated checklist and approved
   roadmap rather than from an older planned order.

## Live development surfaces

- [MAPS Lean Live Roadmap](https://docs.google.com/spreadsheets/d/1R8NqxfO1ZVvSl0up20fnTCcmXozXIRKbMWI9DQeDbC8/edit)
- [Capability checklist](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md)
- [Roadmap router](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/README.md)
- [Agent-harness roadmaps](https://github.com/BigCatMellow/MAPS_Lean/tree/main/work/roadmaps/agent-harness-capabilities)
- [Open pull requests](https://github.com/BigCatMellow/MAPS_Lean/pulls)

Future refreshes should preserve these sections and replace their contents from
verified current sources; the page should not grow into a second roadmap.
