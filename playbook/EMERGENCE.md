# Emergence and Improvement (E/I)

Discovery is valuable. It must be *elicited* deliberately, *captured* cheaply,
and *promoted* carefully — and it must not hijack an assigned task.

```text
IMAGINE → CAPTURE → PROMOTE
(diverge)  (converge)  (decide)
```

This lifecycle is the **current operating method, not a design ceiling**. Emergence
may challenge, compare, redesign, or propose replacement of any established
mechanism — including this emergence lifecycle itself — when evidence suggests a
better way. Current authority continues to govern execution until deliberately
changed; being established is not evidence that a mechanism should remain.

## Phase 1 — Imagine (divergent)

Run at a cadence, not continuously. The trajectory check is the standing anchor
(see [`ROADMAP_TRAJECTORY_CHECK.md`](ROADMAP_TRAJECTORY_CHECK.md) §"Emergence
pass (every pass)"); an operator may also call one at a phase boundary or on
demand. This is **not an automated step** and there is no imagination daemon —
the anchor is the existing cadence, not new machinery.

The cadence itself is also open to improvement. If evidence supports a better
triggering/search mechanism, capture and test that alternative rather than
preserving cadence merely because it is current practice.

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
- Which established mechanism survives mainly because it is already established,
  and what alternative would outperform it on the actual objective?

### Cross-root synthesis

Do not restrict emergence to one arc or to the nearest obvious idea family.
When compact, trustworthy source summaries are available, deliberately compare
observations and ideas from **different project roots, arcs, branches, domains,
idea families, or established mechanisms/processes** to look for relationships
that local work may not reveal.

Ask:

- Do two apparently separate problems share the same underlying mechanism or
  cause?
- Does a method, constraint, or solution from one root transfer to another?
- Do assumptions or findings from separate roots contradict, constrain, or
  qualify one another?
- Can useful fragments from separate roots compose into a capability neither
  contains alone?
- Does one root already contain a latent dependency, missing capability, or
  unused asset that matters to another?
- Does a structurally distant root suggest an alternative frame that changes
  how another problem should be understood?
- Does another root expose a better mechanism than a process currently treated
  as standard?
- Does combining roots suggest changing the emergence/search/evaluation process
  itself?

Do not equate resemblance with synthesis. A cross-root candidate is worth
**Capture** only when it can name:

```text
source A + source B (or more)
connection type / linking mechanism
new implication that is not merely restating either source
why the implication may matter
current baseline when an established mechanism is challenged
smallest discriminating test or falsifier
```

Shared vocabulary, theme, superficial analogy, or incumbency is insufficient.
It is valid for a pass to conclude `NO MATERIAL CROSS-ROOT SYNTHESIS FOUND`.

Where the search space is large, inspect compact summaries/indexes first and
expand source detail only for promising candidates. Include some bounded
structurally distant comparisons rather than relying only on nearest semantic
neighbors; otherwise the pass will mostly rediscover obvious relationships.
Do not create durable graph links merely because a candidate connection was
noticed — preserve only links that change understanding, retrieval, evaluation,
or action.

Established process is a legitimate root of inquiry. If a synthesis appears to
outperform a current mechanism, compare it against the incumbent rather than
forcing the new idea to conform. The incumbent may still win; novelty receives
no automatic preference either.

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
A candidate may explicitly target an existing MAPS_L process for adaptation or
supersession; current process does not receive immunity from evaluation.

## Phase 3 — Promote (deliberate)

Promotion turns a captured record into real work: a `work/tasks/` contract, a
`work/decisions/DEC-NNN` record, or an in-scope line on an existing roadmap
item. It is never an automated step, and only a promoted item may expand
implementation scope under the current operating model.

Promotion may also authorize work whose purpose is to replace or supersede an
existing mechanism. Preserve lineage and the reason for replacement; do not
keep an inferior process solely for continuity.

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

Rule: **imagine widely, challenge precedent, file cheaply, promote deliberately,
supersede when earned, sweep every arc.**
