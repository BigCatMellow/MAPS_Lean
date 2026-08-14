# Insight Record

Insight ID: INS-0019
Project: Riftbound
Related task: NONE
Detected by: claude-lab-fimo
Date: 2026-07-05
Status: LINKED

## Short description

- obs: A 100-line domain validator written at the start of a generative batch immediately caught legality bugs in already-released artifacts that two agents' manual cross-review had approved

## Trigger

- src: Before building 3 more Riftbound decks, wrote scripts/validate_decks.py; its first run found the released Rumble deck at 5 signature cards (limit 3, incl. Jhin's Curtain Call) and the Kha'Zix deck running Sivir's signature On the Hunt — both previously hand-verified by two agents

## The synthesis

- synth: A 100-line domain validator written at the start of a generative batch immediately caught legality bugs in already-released artifacts that two agents' manual cross-review had approved

## Why it might matter

- why: Manual review verified what it knew to check (counts, name/ID pairs) but silently skipped a rule neither author had operationalized (signature champion-tag matching); encoding rules as a script forces enumerating them, and the enumeration itself surfaced the gap

## Evidence

- ev: validate_decks.py first run: FAIL rumble-mech-tribal (5 sigs), WARN khazix (Sivir sig); it also caught 3 illegal signatures in my own new Vi deck. All 20 decks now pass. Signature ownership inferred from card-ID adjacency (each signature is printed directly after its Legend)

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
delegated authority. Retained as GENERALISABLE METHOD, not parked, and linked
from [[INS-0040]].

This is independent corroboration of INS-0040's central argument, arriving from
a different project nineteen days earlier — a cheap mechanical invariant check
catches what manual cross-review approves. INS-0040 reasons from MAP's own
TASK-267 escape; this reasons from a generative batch in Riftbound where a
~100-line validator caught legality bugs in already-released artifacts that two
agents had reviewed. Evidence from an unrelated domain makes the claim stronger,
not weaker, and INS-0040's fix (TASK-276) is the same move applied to shared
state.

The mechanism named here is the important part: encoding rules as a script
forces enumerating them, and the enumeration itself surfaces the gap.
