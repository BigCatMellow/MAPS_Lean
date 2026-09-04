# Emergence and Improvement (E/I)

Discovery is valuable. It must be *elicited* deliberately, *captured* cheaply,
and *promoted* carefully — and it must not hijack an assigned task.

```text
IMAGINE → CAPTURE → PROMOTE
(diverge)  (converge)  (decide)
```

## Phase 1 — Imagine (divergent)

Run at a cadence, not continuously. The trajectory check is the standing anchor
(see [`ROADMAP_TRAJECTORY_CHECK.md`](ROADMAP_TRAJECTORY_CHECK.md) §"Emergence
pass (every pass)"); an operator may also call one at a phase boundary or on
demand. This is **not an automated step** and there is no imagination daemon —
the anchor is the existing cadence, not new machinery.

This phase has **no filing discipline** — the goal is volume and range. Ask,
against the work of the arc (or the project as a whole):

- What recurred that is *not* a defect — a rough edge, a workaround that keeps
  reappearing, a step that is always slower than it should be?
- What did a PR, a review, or an incident *reveal* about the system that is
  captured nowhere?
- What are we not doing that a competent outsider would expect us to?
- What would make this 10× cheaper / faster / safer — even if it sounds
  disproportionate right now?
- What did we decide once, long ago, that nobody has re-examined against current
  reality?

Speculation is explicitly allowed here. Get candidates onto the table first;
judge them in Capture.

## Phase 2 — Capture (convergent)

Take the candidates worth keeping and file each as a concise record in
`work/insights/`, `work/ideas/`, or `work/experiments/` (use
`scripts/emergence.py capture`). Include: the observation, its source/context,
its potential value, and the **smallest next test**.

- **Insight:** a notable observation.
- **Synthesis:** a meaningful connection between observations.
- **Idea:** a bounded possible improvement.
- **Experiment:** a safe, small test.

Filing is not endorsement. A captured record is a candidate, not a commitment.

## Phase 3 — Promote (deliberate)

Promotion turns a captured record into real work: a `work/tasks/` contract, a
`work/decisions/DEC-NNN` record, or an in-scope line on an existing roadmap
item. It is never an automated step, and only a promoted item may expand
implementation scope.

**Propose vs. dispose.** The Emergence pass
([`ROADMAP_TRAJECTORY_CHECK.md`](ROADMAP_TRAJECTORY_CHECK.md) §"Emergence pass
(every pass)") *proposes* a disposition for each open record with a one-line
rationale. The orchestration operator — or a coordinator acting under delegated
authority for the bounded / low-risk cases — *disposes*. This is the same split
as friction-log escalation: the pass surfaces and recommends; it does not
authorize.

**Ripeness bar.** Promote a record when its "smallest next test" is concrete AND
either (a) the value is clear and the change is bounded (→ task contract), or
(b) it names a choice only the operator can make and that choice now blocks
progress (→ decision record), or (c) it is in-scope work on an item already on
the roadmap (→ roadmap line). Otherwise leave it **incubating** — a valid state,
but every pass must record *why* it is still incubating, not silently skip it.

**After disposition.** Update the record's `## Promotion` section in place
(append-only): from "Not promoted" to a dated line linking the task / DEC /
roadmap item it became (promote), or to a dated disposition line stating what
later reality changed (stale) or what supersedes it (kill). A promoted or stale
/ killed record stops consuming sweep attention; the file is never deleted.

## Consumption

[`ROADMAP_TRAJECTORY_CHECK.md`](ROADMAP_TRAJECTORY_CHECK.md) §"Emergence pass
(every pass)" sweeps the `work/insights/` + `work/ideas/` backlog every pass:
each open record is **promoted**, marked **stale**, **killed**, or explicitly
**incubated with a reason**. A record incubated across **N = 3** consecutive
passes with no movement is named in the pass's operator section. This mirrors the
FRICTION_LOG consumption duty and uses the same N = 3 ladder.

Rule: **imagine widely, file cheaply, promote deliberately, sweep every arc.**
