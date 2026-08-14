# Insight Record

Insight ID: INS-0055
Project: MAP
Related task: NONE
Detected by: claude-lab-muza
Date: 2026-07-29
Status: PROMOTED

## Short description


- obs: The mandatory Emergence capture considered release checkbox never invokes the actual Discovery Agent method it is meant to gate

## Trigger


- src: Created from command-center emergence capture.

## The synthesis


- synth: Nothing connects the release-gate checkbox to actually running the adopted Discovery Agent method. An agent can satisfy the gate with a five-second glance and a checkmark while the higher-signal, already-adopted discovery method sits unused. This gives a concrete mechanism for [[emergence/insights/INS-0032-promoted-process-rules-stay-ineffective-unless-mechanically-surf]]'s general claim that promoted rules go unused without mechanical surfacing.

## Why it might matter


- why: The operator asked today whether something exists to actively generate new E/I ideas, echoing [[emergence/ideas/IDEA-0013-add-an-idea-scouting-role-a-role-cadence-responsible-for-activel]]'s reopening note that E/I never seems to be taken advantage of. The method already exists and is adopted; the gap is that the one gate that fires at every release does not require using it.

## Evidence


- ev: [[CHANGE_CONTROL_SYSTEM]] lines 65 and 124; MAP_System/emergence/experiments/[[emergence/experiments/EXP-0003-pilot-the-non-forcing-discovery-agent-on-the-completed-clearfron]]-*.md Decision/Notes; MAP_System/emergence/ideas/[[emergence/ideas/IDEA-0013-add-an-idea-scouting-role-a-role-cadence-responsible-for-activel]]-*.md Reopened section.

## Risk


- risk: Low: proposed fix is a checklist wording change, reversible, no automation added.

## Scope


- scope: Every task release going through [[CHANGE_CONTROL_SYSTEM]]'s checklist gate.

## Recommended next action

- [ ] ignore
- [ ] park
- [x] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note: Promoted through IDEA-0032 and PROMO-0016. Implementation must remain
  backward compatible with existing release records and must not invoke a
  model automatically.
