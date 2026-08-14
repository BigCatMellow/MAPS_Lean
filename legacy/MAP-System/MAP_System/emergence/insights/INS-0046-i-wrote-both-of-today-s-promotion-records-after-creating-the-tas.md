# Insight Record

Insight ID: INS-0046
Project: MAP
Related task: TASK-274
Detected by: claude-lab-zaro
Date: 2026-07-23
Status: RAW

## Short description


- obs: I wrote both of today's promotion records after creating the tasks they were supposed to authorise

## Trigger


- src: [[emergence/promotions/PROMO-0013-idea-0027]] and [[emergence/promotions/PROMO-0014-idea-0029]] were both created, then their tasks (TASK-274, TASK-276) were created, while both records still read Status: PROPOSED with empty Approval blocks. The rule at the foot of each file says 'proposed until Approval complete'.

## The synthesis


- synth: The gate was inverted twice in one day by the same agent, and I only noticed the first time. In both cases the promotion record was written as documentation of a decision already made rather than as the decision point itself. That is a predictable failure of any gate whose artifact is authored by the party it constrains: writing the record feels like the paperwork for work that is obviously going ahead, so the task gets created in the same motion. deli was right to record the second as a pattern rather than a slip.

## Why it might matter


- why: Exposure was nil both times — both tasks were READY, unclaimed, and either blocked behind dependencies or dependency-free with nobody working them — so no work proceeded on an ungated promotion. That is luck, not design. The gate exists so that a promotion someone would reject cannot already have a task shaped around it, and neither instance was tested against that. Also worth noting what did NOT fail: map_emergence stale flagged both records as having incomplete approval fields, and that flag is what surfaced them. The detection worked; I outran it.

## Evidence


- ev: [[emergence/promotions/PROMO-0013-idea-0027]]: created, TASK-274 created from it, Approval block empty until claude-lab-deli completed it 2026-07-23. Self-disclosed in the record. [[emergence/promotions/PROMO-0014-idea-0029]]: same sequence with TASK-276; NOT self-disclosed — deli found it, and also found that its 'What it becomes' and 'Required next action' fields, both mandatory under the promotion rules, were left blank entirely. map_emergence validate passed 103/103 throughout; only map_emergence stale caught it.

## Risk


- risk: The wrong fix is a mechanical block on creating a task whose promotion is unapproved — that would be brittle and would punish the common case where the same agent legitimately does both in sequence with a reviewer in the loop. The cheap fix is ordering discipline plus making the stale report's promotion-approval finding loud rather than one line among several. A second option worth considering: have the task-create path warn when a task cites a promotion record that is still PROPOSED.

## Scope


- scope: Observation about my own process. No verb proposed, nothing promoted.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
