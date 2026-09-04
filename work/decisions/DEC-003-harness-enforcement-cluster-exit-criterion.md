# DEC-003: Harness-enforcement cluster (6.4 / 6.5 / 6.16 / 6.22 / H5 / E4 / L6) — resolve the exit criterion

- Date: 2026-09-04
- Owner: Operator (accountable); session-27 coordinator dispatched the framing,
  session-28 coordinator (`muzo`) filled the recommendation
- Status: `ADOPTED` (2026-09-04, session 31)
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
  **Update 2026-09-04:** the cited precondition — the option-B lineage-bootstrap
  wiring — is **already merged and exercised**: `maps run bind-session` verb
  (#258, `runtime/cli.py:131`), synthetic exercise on a fresh `.maps/` (#261,
  `work/notes/2026-09-02-lineage-bootstrap-exercise.md`), checklist evidence on
  H5 / 6.16 / 6.22 (#263). "A few days of work" is stale — what remains under (B)
  is a bounded (hours) controlled real-stall exercise, not new wiring.
- **(C) Hold the rows IN PROGRESS indefinitely** and stop treating the enforced
  pass as imminent — re-scope the cluster's DONE definition at a later phase
  boundary.

## Recommendation

**(B) — run the controlled real-stall exercise.** Filled by session-28
coordinator `muzo` 2026-09-04.

Reasoning:

1. **The decision rule points at (B).** The framing rule was "(B) if the
   option-B wiring is confirmed near-term, else (A)". The wiring is not merely
   near-term — it is **merged and exercised** (#258 verb, #261 synthetic
   exercise, #263 evidence). The gating dependency that made (B) expensive across
   passes #8–#21 is discharged. `git log --oneline --all | grep -i bind-session`
   and `runtime/cli.py:131` / `:585` confirm the verb; `check_review_evidence.py`
   passed on all three PRs.
2. **What remains under (B) is bounded, not open-ended.** A throwaway real hcom
   session, bound via `maps run bind-session`, lease left to expire with no
   babysitting, then one `recovery-tick --enforce-canonical-run` to capture a
   routable `resume_denied`. Hours, not days. The runbook §8 option-B path and
   the #277 option-A pass recipe are both already written.
3. **(A) permanently bakes a load-bearing caveat into 7 security-cluster rows.**
   Anyone later relying on "harness enforcement is proven" inherits "…proven by
   instantiation, not by a live routable denial". For a security cluster that is
   weak evidence to close on when the strong evidence is now a few hours away.
4. **(C) abandons a criterion that has just become reachable.** The "one step
   away" distortion that (C) is meant to end is genuinely resolved once (B)
   runs once; holding IN PROGRESS indefinitely trades a solvable problem for a
   permanent one.

Residual risk and mitigation (the real reason this needs operator sign-off):
option (B) deliberately runs against the grain of the babysat operating mode —
it requires a genuinely-unattended live session that stalls. Mitigation for the
exercise design: a dedicated throwaway tagged session explicitly excluded from
`limit_watcher` / coordinator babysitting, a shortened lease TTL, a single
bounded window. **Fallback:** if two controlled attempts cannot produce a
routable `resume_denied`, fall back to (A)-with-caveat and keep (B) as a tracked
follow-up — do not hold the cluster hostage to a third attempt.

## Operator authorization

**GO — 2026-09-04, session 31.** Operator authorized both:
1. adopt **(B)** as the cluster exit-criterion path; and
2. the controlled real-stall exercise itself (spawn a throwaway real hcom
   session and let it stall unattended — intentionally outside the normal
   babysat mode).

`INSIGHT-651d8c62` + `INSIGHT-102296b5` are promoted into this DEC by trajectory
check #22's Emergence-pass sweep. Mitigation from the Recommendation section
applies as designed: dedicated throwaway tagged session, explicitly not
babysat/watched by the coordinator, shortened `--lease-seconds`, single bounded
window; fallback to (A)-with-caveat after 2 failed attempts, do not hold the
cluster hostage to a third. Exercise dispatch: see
`work/tasks/dec003-b-real-stall-exercise.md`.

## Consequences

- **A:** 7 rows flip DONE; roadmap scoreboard moves; the caveat is load-bearing
  for anyone relying on "enforcement is proven".
- **B:** option-B wiring becomes top-of-runway; a real denial is captured and
  frozen as a regression case.
- **C:** the cluster stops distorting every trajectory pass's "one step away"
  framing.
