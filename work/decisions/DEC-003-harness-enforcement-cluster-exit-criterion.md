# DEC-003: Harness-enforcement cluster (6.4 / 6.5 / 6.16 / 6.22 / H5 / E4 / L6) — resolve the exit criterion

- Date: 2026-09-<DD>
- Owner: Operator (accountable); session-27 coordinator dispatched the framing
- Status: `PROPOSED`
- Decision class: Roadmap exit-criterion / status-truth
- Related task/roadmap: `work/roadmaps/CAPABILITY_CHECKLIST.md` rows 6.4, 6.5,
  6.16, 6.22, H5, E4, L6; `work/notes/2026-09-02-ask1-control-plane-runbook.md`
  §6 / §8
- Source/evidence:
  - `work/insights/` — `INSIGHT-651d8c62` (13 passes, no movement toward the
    criterion)
  - `work/insights/` — `INSIGHT-102296b5` (criterion may be structurally
    unexercisable under the current operating mode)
  - `work/notes/2026-09-03-item5-enforced-pass-results.md` (#277 — runbook §8
    option A pass, 0 incidents / 0 denials, synthetic `bind-session`)
  - `work/notes/2026-09-02-lineage-bootstrap-wiring-scoping.md` (runbook §8
    option B scope)
  - `work/notes/2026-09-03-roadmap-trajectory-check-21.md` and passes #8–#20
    (the "one step away" history)
- Supersedes / superseded by: none

## Problem

The 7-row cluster's exit criterion is "first real production exposure of an
enforced `--enforce-canonical-run` pass producing a routable `resume_denied`".
Trajectory checks #8–#21 have each framed the cluster as "one step" from that
criterion; the step has receded every pass (no prod caller → composition
default-off → lineage-bootstrap deadlock → hcom 0.7.25 adapter defect → synthetic
session opens no incident → option B). #277 ran the enforced pass but against a
synthetic `bind-session`, which opens no incident, so the guard never fired. A
*real* `resume_denied` needs a genuinely-live session that stalls unattended
until its lease expires — and the current operating mode (coordinator seats,
`gule`, `limit_watcher`, active babysitting) is specifically designed to prevent
that.

## Options

- **(A) Accept option-A instantiation evidence as sufficient for DONE, with a
  documented caveat.** #277 proved the composition root + option C run on the
  real production path. Mark the rows DONE with an explicit "enforcement verified
  by instantiation, not by a live routable denial — that failure mode is rare by
  design" note. Lowest cost; weakest evidence.
- **(B) Run a controlled real-stall exercise.** Launch a throwaway real hcom
  session, bind it via `maps run bind-session`, let its lease expire with zero
  babysitting, then run the enforced tick and capture the real `resume_denied`.
  Requires the option-B lineage-bootstrap wiring first (scoped in
  `2026-09-02-lineage-bootstrap-wiring-scoping.md`; = NEXT WORK §2). Strongest
  evidence; a few days of work.
- **(C) Hold the rows IN PROGRESS indefinitely** and stop treating the enforced
  pass as imminent — re-scope the cluster's DONE definition at a later phase
  boundary.

## Recommendation

<coordinator fills — suggest (B) if the option-B wiring is confirmed near-term
(it is currently NEXT WORK §2 and the #22 STOP-condition), else (A) with the
caveat and a tracked follow-up for (B).>

## Operator authorization

<pending>

## Consequences

- **A:** 7 rows flip DONE; roadmap scoreboard moves; the caveat is load-bearing
  for anyone relying on "enforcement is proven".
- **B:** option-B wiring becomes top-of-runway; a real denial is captured and
  frozen as a regression case.
- **C:** the cluster stops distorting every trajectory pass's "one step away"
  framing.
