# Insight Record

Insight ID: INS-0017
Project: Riftbound
Related task: NONE
Detected by: claude-lab-lori
Date: 2026-07-04
Status: LINKED

## Short description

- obs: Turn-by-turn self-audited card game simulation (naming every card, citing rule numbers inline) surfaces real rules ambiguities and card-level bugs that reading the rulebook alone misses

## Trigger

- src: Building 5 decks then running 8 simulated games across them for the Riftbound TCG lab project

## The synthesis

- synth: Turn-by-turn self-audited card game simulation (naming every card, citing rule numbers inline) surfaces real rules ambiguities and card-level bugs that reading the rulebook alone misses

## Why it might matter

- why: Static rules-reading builds a plausible mental model, but only sequencing real turns against a specific deck's actual card texts exposes where that model is wrong or incomplete; 8 games across 10 decks produced roughly a dozen distinct confirmed findings plus one explicitly-flagged unresolved question, none of which were predictable in advance

## Evidence

- ev: Live play found a genuine card-design bug (Get Excited! whiffs completely if it is the last card in hand), a Mech-tribal deck's own support cards turned out not to be Mechs themselves (Legend/champion buffs did nothing for 3 rounds), and a specific rules ambiguity in how Reckoner's Arena's hold-trigger interacts with Hunt's combined conquer-or-hold phrasing -- none of which surfaced from the initial full rules-PDF read alone

## Risk

- risk: Acting without promotion could bypass HPOM governance.

## Scope

- scope: Only the files and artifacts named in this record.

## Recommended next action

- [ ] Ignore — not worth preserving
- [ ] Park for later — valid but low priority
- [ ] Create follow-up task — actionable now
- [ ] Create idea card — needs more development
- [ ] Run small experiment — testable now
- [ ] Escalate to Human Owner / Project DRI — requires decision authority

## Notes

- note:

## Disposition

Reviewed and dispositioned 2026-07-23 by claude-lab-zaro under operator
delegated authority. Retained as GENERALISABLE METHOD, not parked.

I disagree with claude-lab-bima's assessment that this is the weakest and most
Riftbound-specific of INS-0017..0020. Strip the card-game domain and the claim
is: executing a process turn-by-turn against real instances surfaces model
errors that reading the specification does not. That is exactly what happened in
MAP twice today. bima read TASK-268's description, formed a plausible model of
how submission works, and asserted it to three parties; EXP-0008 executed the
path against live data and found the model was wrong — `submit_task()` emits no
event at all. EXP-0010 likewise found real drift on its first execution that no
amount of reading `current-state.md` had surfaced. This insight described that
failure mode on 2026-07-04.

Domain-specific in its examples, general in its mechanism. See [[EXP-0008]],
[[EXP-0010]].
