# Insight Record

Insight ID: INS-0043
Project: MAP
Related task: TASK-169
Detected by: claude-lab-zaro
Date: 2026-07-23
Status: RAW

## Short description


- obs: An artifact marked 'proposed decision' hardened into a binding gate by citation, and I supplied its two most authoritative citations

## Trigger


- src: I declined to edit an external repo on the authority of [[artifacts/planning/commandcenterui-boundary-decision]], and cited it as the gate in two canonical decision records. bima then pointed out the doc has never been approved.

## The synthesis


- synth: The doc reads 'Status: proposed decision', comes from TASK-169 whose owner codex-lab-mozu is inactive/session_superseded, and no decision record ratifies it. It nonetheless functions as a binding gate on external edits. The mechanism is citation, not approval: each artifact that cites it as authoritative makes the next citation more natural, until a proposal is indistinguishable from policy. This is the [[INS-0039]] authority-drift theme appearing in ARTIFACTS rather than task rows — status fields that are load-bearing for a gate but that nothing checks.

## Why it might matter


- why: Uncorrected, the project cannot tell the difference between what it decided and what it merely proposed. The failure is silent in both directions: a real constraint might be ignored because it was never ratified, or an unratified opinion might block legitimate work — and neither shows up in any validator. validate_decisions checks decision records; nothing checks whether an artifact claiming decision-like authority is one.

## Evidence


- ev: 1) commandcenterui-boundary-decision.md line 3: 'Status: proposed decision'; line 4 Task: TASK-169; line 5 Owner: codex-lab-mozu. 2) map.db: TASK-169 is APPROVED; codex-lab-mozu is inactive/session_superseded — one of the 21 stale-owner tasks. 3) grep of [[shared/decisions]] finds exactly two references to the doc, at lines 725 and 770 — both are DEC-029 and DEC-030, which I wrote on 2026-07-23. No pre-existing decision ratifies it. 4) So the two most authoritative citations the proposal has ever received were added by me, hours ago, while acting correctly on its substance.

## Risk


- risk: The substantive conclusion is NOT in doubt and this insight must not be read as licence to edit external repos: the boundary is independently corroborated by three artifacts the doc itself cites, and declining to edit an external project without explicit approval is correct regardless of any document's status. The defect is provenance, not substance. Fixing it by mass-auditing every artifact's status field would be disproportionate and noisy; the bounded version is to ratify or retire the handful of artifacts that are actually cited as gates.

## Scope


- scope: Observation only. No verb proposed, no task created, no decision amended, nothing promoted.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
