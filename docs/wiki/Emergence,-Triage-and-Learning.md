# Emergence, Triage and Learning

MAPS_L has two related improvement loops:

- **Emergence** finds and tests possible insights or improvements.
- **Triage and repair** captures actual friction and prevents recurrence.

Neither loop silently changes project authority or promotes a suggestion into
implementation.

Back to [[Home]].

## Emergence lifecycle

```text
IMAGINE -> CAPTURE -> PROMOTE
diverge    converge    decide
```

### Imagine

At a trajectory check, phase boundary, or explicit request, look for recurring
rough edges, unrecorded implications, missing expected capabilities, and ways to
make the current arc materially cheaper, faster, or safer. There is no
imagination daemon and no continuous autonomous generation loop.

### Capture

Keep only candidates worth testing as compact insight, synthesis, idea, or
experiment records. Each record names its source/context, possible value, and
smallest discriminating test. Filing is not endorsement.

### Promote

A deliberate disposition may turn a candidate into a task, decision, or
in-scope roadmap item. Otherwise it remains incubating, becomes stale, or is
killed with rationale. Promotion is never automatic and is the only current
route from a captured candidate to implementation scope.

The trajectory check sweeps open records every pass. A record incubated without
movement for **N = 3** consecutive passes is surfaced to the operator rather
than silently ignored. Disposed records remain as history and stop consuming
routine sweep attention.

## Cross-root synthesis

The Emergence pass can compare separate project roots, arcs, branches, domains,
or idea families. It looks for:

- a shared underlying mechanism;
- transfer of a method or constraint;
- contradiction or qualification;
- composition into a capability neither source contains alone;
- a latent dependency or unused asset; or
- an alternative frame that changes understanding.

Similarity alone is not synthesis. A captured cross-root candidate must name:

```text
source A + source B (or more)
connection type or mechanism
a genuinely new implication
why the implication matters
the smallest test or falsifier
```

It is valid to conclude that no material synthesis exists. The pass uses
compact trustworthy summaries first and opens deeper source material only for
promising candidates.

Cross-root synthesis is current behavior from merged PR #315. It did not expand
Capture or Promote authority.

## Established-mechanism supersession authority is current behavior

[PR #319](https://github.com/BigCatMellow/MAPS_Lean/pull/319) is **merged**
(commit `69d6497`, 2026-09-09). Emergence may now explicitly challenge,
redesign, or propose replacement of an established MAPS_L mechanism while the
existing authority gates are retained: proposal authority stays distinct from
execution/merge authority.

#319 carried independent review, a Tenth Seat minority report, and a recorded
narrow/conditional operator substance ruling before it landed.

## Mandatory friction capture

A `FRICTION_LOG` entry is required when work encounters a failed run that costs
rework, a stalled worker, a wrong assumption, a missing/broken tool or
environment, operator-expressed friction, or a review-caught defect class.

Expected negative tests, one-off cosmetic mistakes, normal design iteration,
routine conflict resolution, and already-recorded incidents do not require a
new entry.

The modern triage loop is:

```text
capture
-> classify severity
-> check recurrence
-> first occurrence: fix and record
-> repeated occurrence: enforced safeguard, not another instruction
-> verify against live state
-> close
```

Severity uses one vocabulary:

| Severity | Meaning | Response |
| --- | --- | --- |
| Cosmetic | harmless formatting/stale detail | correct and verify |
| Drift | recorded state differs from verified reality | mechanical repair and repair record |
| Blocking | drift prevents valid work | repair if authorized; otherwise propose/escalate |
| Structural | repair changes authority, ownership, data shape, or approved behavior | decision/change path; no silent repair |

## Recurrence and mechanical safeguards

The first occurrence may be fixed by documentation or instruction when that is
proportionate. A second occurrence of the same root-cause pattern proves the
first countermeasure was insufficient. The next response must be mechanical:
a test, hook, schema constraint, template field, CI check, or script that fails
or blocks when the pattern recurs.

The record must explain why the first fix did not hold. If no mechanical
safeguard is feasible, the item is escalated to the operator rather than
receiving a third instruction.

`tools/triage_status.py` reads the dated friction-log anchors and reports
unverified, overdue, or stale entries. Closing requires a concrete
countermeasure, live verification, disposed follow-ups, and—where the fix must
be observed over time—three clean trajectory arcs with no recurrence.

## Frozen regression cases

A severe or repeated real incident can be converted into a deterministic
`MAPS_FROZEN_REGRESSION_CASE` using `maps freeze-case`. The case binds a
sanitized fixture and expected properties to the exact portable Run Record.

Regression cases are evidence, not authority. They never automatically change
policy, routing, or the harness. Any resulting refinement still follows the
normal decision, implementation, and review path.

## Operational learning

An incident becomes an operational lesson only when it generalizes beyond its
local fix. That reusable claim enters the Emergence lifecycle; it is not copied
into startup guidance automatically. Promotion and retirement remain deliberate
operator decisions.

Sources:
[`playbook/EMERGENCE.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/EMERGENCE.md),
[`playbook/REPAIR_AND_LEARNING.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/REPAIR_AND_LEARNING.md),
and
[`tools/triage_status.py`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/tools/triage_status.py).
