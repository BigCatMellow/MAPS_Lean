# Idea Card

Idea ID: IDEA-0028
Project: MAP
Source insight or synthesis: Operator design proposal 2026-07-23, relayed verbatim by claude-lab-bima (hcom #13542) for capture on the normal promotion path. NOT a decision and NOT authorisation. Mechanics independently verified against live map.db by claude-lab-zaro before recording.
Owner: claude-lab-zaro
Date: 2026-07-23
Status: CANDIDATE

## Idea


- idea: Parent ownership: resolve an unreachable task owner to a durable parent lane at read time, and make the parent responsible for routing independent review

## Problem or opportunity


- gap: Tasks get lost when their owning session disappears. Measured live: of 82 nonterminal tasks, 56 are owned by session names and 21 of those are stale, while all 26 durable-owned tasks (all 'command-center') are stale-free. Nothing routes a stranded task to anyone; TASK-236's monitor now reports them but reporting is not routing.

## Why now


- now: Operator, verbatim: 'add parent ownership, so the two core agents of claude and codex and whatever other ones are there at start are given parent ownership to default to when the assigned owner cant be found, and then have a rule where its on the parent to pass it on for independent review. so that way tasks dont go getting lost.'

## Expected benefit


- gain: Two things at once. (1) Stranded work has a standing home: when an owner is not live, responsibility resolves to that owner's parent lane, whose duty is to route the work for INDEPENDENT review — not to do it. (2) It enables a STRONGER self-review guard than exists today. Current rule is reviewer != owner, a string match on a session name that goes stale. Parent-based is reviewer.parent != owner.parent, i.e. lane-level separation, which is what DEC-008 already implies (Codex implements, Claude reviews) and which session churn cannot defeat because parents do not churn. It also makes the operator's earlier session-start idea well-founded: 'what has fallen to my parent and is unattended?' is a better question than 'what can I grab?'

## Cost


- cost: Schema change (a parent column on agents), a resolution helper, guard rework, and a registration change so every new agent records a parent. Gated behind TASK-274.

## Reversibility

- [ ] yes
- [ ] no
- [ ] partial: TBD

## Smallest safe experiment


- test: Read-only: add no schema. Build a parent map in memory from an explicit table of agent -> parent, then replay every nonterminal task and report (i) how many stranded tasks would resolve to each parent, (ii) how many would resolve to NO parent under the current roster, and (iii) how many historical approvals would have been blocked by reviewer.parent != owner.parent versus the current reviewer != owner. Proves the routing load, the coverage hole, and the guard's real strength before any column exists.

## Decision needed

- [ ] task-DRI
- [ ] review-DRI
- [ ] state-steward
- [ ] project-DRI
- [ ] human-owner

## Recommendation

- [ ] park
- [ ] reject
- [ ] test
- [ ] promote-task
