# Idea Card

Idea ID: IDEA-0013
Project: MAP
Source insight or synthesis: NONE
Owner: claude-lab-valo
Date: 2026-07-02
Status: APPROVED_FOR_EXPERIMENT

## Idea


Add an Idea-Scouting role: a role/cadence responsible for actively scanning MAP + project state for promotable insights and presenting candidates to command-center, rather than relying on emergence capture happening incidentally during other tasks.

## Problem or opportunity


Emergence capture (insight/idea/synthesis) currently happens only as a side effect of whatever task an agent is doing; nothing is dedicated to actively looking for improvement opportunities.

## Why now


Operator explicitly floated this idea (hcom #19306) alongside the process-watcher idea.

## Expected benefit


Could surface more MAP-system and project-level improvements proactively instead of only during gap reviews.

## Cost


Risk of generating idea volume that outpaces promotion capacity/review bandwidth; needs a cadence and a stale/prune rule (map_emergence.py stale already exists for this).

## Reversibility

Can this be undone easily?

- [ ] Yes
- [ ] No
- [ ] Partially — explain: TBD

## Smallest safe experiment


Create and validate file-backed emergence records.

## Decision needed

Who must approve this before it can be promoted?

- [ ] Task DRI — within current task scope
- [ ] Review DRI — requires review gate
- [ ] State Steward — changes shared state
- [ ] Project DRI — changes project direction
- [ ] Human Owner — changes MAP-level rules or governance

## Recommendation

- [x] Park — valid but not the right time
- [ ] Reject — not worth pursuing
- [ ] Test — run the smallest safe experiment
- [ ] Promote to task — evidence is sufficient, ready for HPOM

## Resolution (2026-07-04, TASK-146 triage, claude-lab-magi)

Parked for the same reason as `IDEA-0011`, which this card overlaps with
heavily (both propose a standing role to actively watch/scout MAP rather than
capture happening as a side effect of task work). `IDEA-0012`'s promoted
systems-adherence audit, and the five audits it has since spawned
(TASK-129/130/140/141/142/143/145), are already functioning as exactly the
proactive-scouting cadence this card asks for — without the risk this card's
own Cost section names (idea volume outpacing review bandwidth) or the
standing-role ceremony AGENTS.md's Pushback Standard cautions against.
Revisit only if the organic cadence stalls or the operator explicitly wants a
dedicated role despite the existing bounded-audit pattern.

## Reopened (2026-07-17, operator evidence)

The revisit condition is satisfied. The operator reported that E/I “never
seems to be taken advantage of” and that effective use needs an agent
continually looking for candidates. The live TASK-222/TASK-223 incident
supports that diagnosis: a reusable operational lesson was first written as a
task-scoped note and only entered E/I after the operator explicitly identified
the missing learning loop. The prior assumption that organic audits and a
closeout habit were sufficient is therefore not supported by current behavior.

Approved direction for a bounded experiment, not an unbounded paid-agent
session:

- a token-free deterministic sentinel scans durable state changes for
  candidate signals such as repeated blockers, repeated operator corrections,
  changes-requested clusters, recurring incidents, and untriaged emergence;
- its activity, last run, candidates, errors, and stop control are visible in
  Command Center; it is not represented as a hidden agent;
- it writes candidates to a review queue without promoting them;
- a core agent performs bounded scheduled or event-triggered curation in a
  visible terminal/session and decides capture, merge, park, dismiss, or
  promote; no background/headless agent is allowed;
- noise, duplicate rate, useful-candidate rate, operator rediscovery, and
  curation cost determine whether the role becomes permanent.

This complements IDEA-0022/TASK-223: TASK-223 makes promoted lessons loadable;
the reopened IDEA-0013 makes discovery persistent enough to supply that loop.

## Discovery Agent refinement (2026-07-17, INS-0028)

The operator supplied a concrete Discovery Agent design that resolves the
semantic gap exposed by EXP-0002. Preserve these boundaries in a future pilot:

- The deterministic E/I Sentinel continuously notices typed durable signals;
  it does not interpret or propose.
- A visible, bounded Discovery Agent absorbs project purpose, lifecycle,
  components, recent decisions, known/rejected proposals, and sentinel
  candidates before generating anything.
- It independently performs purpose/lifecycle, omission, emergence, analogy,
  contradiction, divergent-idea, and evaluation passes.
- Every reported finding uses exactly one classification:
  `essential_omission`, `likely_requirement`, `emergent_opportunity`,
  `optional_enhancement`, `risk_or_contradiction`, or `rejected_idea`.
- It separates necessity from optional value and records evidence, confidence,
  scores, minimal version, alternatives, recommendation, and reasoning.
- It never implements. The coordinating agent and normal E/I/HPOM gates decide
  whether a proposal moves forward.
- No idea quota is allowed. The prepared-spontaneity cycle—absorb, clear,
  notice, wander, return, offer—explicitly permits a no-finding result and
  rejects novelty or complexity without proportional value.

Smallest next experiment: run this prompt as a visible Discovery Agent on one
completed project phase, compare its findings with the deterministic sentinel,
existing audit/E/I records, and operator-identified omissions, then measure
useful-new finding rate, duplicate/rejected rate, classification accuracy,
curation time, and scope drift. Do not make it continuous until that evidence
shows value beyond the sentinel and ordinary review.
