# Clearfront — Current Playtest Rules

**Status:** Working ruleset for prototype testing  
**Design target:** Tactical card-game depth with short, readable rules and cards

---

## 1. Goal

Reduce the opposing player from **20 life to 0**.

You win immediately when the opponent reaches 0 life.

---

## 2. Decks and Champions

Each player chooses a **Champion-led deck**.

A standard deck contains:

- **30 cards**
- A primary faction
- An allied faction
- A small group of neutral cards
- One Champion kept outside the deck

The current suggested distribution is:

| Card group | Cards |
|---|---:|
| Primary faction | 17 |
| Allied faction | 7 |
| Neutral | 6 |

The Champion does not occupy a hand slot and is always visible.

---

## 3. Starting the Game

Each player begins with:

- **20 life**
- **1 maximum mana**
- **3 cards**
- Their Champion in the Champion slot

Choose the starting player randomly.

The starting player does not receive additional compensation in the current prototype.

---

## 4. Mana

At the start of your turn:

1. Increase your maximum mana by 1, up to a maximum of 10.
2. Refill your mana to its maximum.

Example:

- Turn 1: 1 mana
- Turn 2: 2 mana
- Turn 3: 3 mana
- Maximum: 10 mana

There are no land cards.

---

## 5. The Three-Card Hand

Your hand normally contains **3 cards**.

You may play no more than **2 cards during your turn**.

At the end of your turn, draw until you have 3 cards again.

Cards that remain in your hand are kept.

### Replace a card

Once during your turn, you may discard one card and draw a replacement.

Replacing a card does not count as playing a card.

---

## 6. Turn Structure

A turn has one flexible main phase.

During your turn, you may:

- Play cards
- Deploy your Champion
- Replace one card
- Attack
- Play cards after attacking

You may take these actions in any legal order.

You may attack only **once per turn**.

Attacking does not automatically end your turn.

When finished, choose **End Turn**.

---

## 7. Card Types

### Units

Units remain on the battlefield.

A unit has:

- Mana cost
- Attack
- Health
- Possibly one short ability

Units normally cannot attack on the turn they enter play.

Damage remains on a unit until it is healed or destroyed.

A unit is destroyed when its remaining Health reaches 0.

### Spells

Spells resolve once and then go to the discard pile.

Spells do not remain on the battlefield.

### Relics

Relics remain in play and provide an ongoing effect.

Relics do not attack or block.

Relics should normally support a deck strategy rather than provide generic power.

### Equipment

Equipment attaches to one friendly unit.

Equipment provides a temporary bonus and is discarded after the equipped unit:

- Attacks, or
- Blocks

If the equipped unit leaves the battlefield first, the Equipment is also discarded.

A unit may have only one Equipment at a time unless a card explicitly says otherwise.

---

## 8. Champions

Your Champion begins in a separate, visible Champion slot.

A Champion:

- Is always available
- Costs mana to deploy
- Counts as one of your two cards played that turn
- Enters the battlefield as a unit
- Has one short ongoing ability
- Provides that ability only while on the battlefield

### Returning Champions

When a Champion is destroyed:

1. Return it to its Champion slot.
2. Increase its cost by 2.

Example:

- First deployment: 6 mana
- Second deployment: 8 mana
- Third deployment: 10 mana

A Champion is not permanently removed from the match unless a future card explicitly says so.

Champions should not normally have both a major entrance effect and a major passive ability. Their identity should come from one clear ability.

---

## 9. Combat

### Declaring attackers

During your turn, choose any ready units to attack.

Units played this turn normally cannot attack.

After attackers are chosen, the defending player assigns blockers.

### Blocking

Each defending unit may block one attacker.

Each attacker may normally be blocked by one unit.

Unblocked attackers deal damage to the defending player.

Blocked attackers and blockers deal damage to each other at the same time.

Example:

- A 3-Attack attacker is blocked by a 2-Attack unit.
- The attacker takes 2 damage.
- The blocker takes 3 damage.

### Persistent damage

Damage stays on units after combat.

Example:

A 5-Health unit that takes 3 damage remains in play with 2 Health.

---

## 10. Core Keywords

Keywords should always use the same meaning.

### Charge

This unit can attack immediately.

### Rush

This unit can attack enemy units immediately, but cannot attack the opposing player on the turn it enters play.

### Guard

The opponent must block a Guard unit before blocking other attackers when able.

### Flying

Only units with Flying can block this unit.

### Shield

Prevent the next instance of damage dealt to this unit, then remove Shield.

### Drain

Damage dealt by this card restores that much life to its controller.

### Stun

The unit cannot attack during its next turn.

---

## 11. Faction Identities

Each faction should have a distinct primary strategy.

### Flame

- Direct damage
- Aggressive units
- Bonuses against damaged enemies

### Wild

- Health growth
- Large units
- Strengthening units already in play

### Order

- Shields
- Survival
- Defensive combat

### Shadow

- Friendly-unit deaths
- Sacrifice
- Drain and destruction

### Mind

- Stun
- Spell sequencing
- Temporary control and delay

### Forge

- Relics
- Equipment
- Drones and constructed units

### Neutral

- Reliable basic effects
- General-purpose units
- Limited synergy

Neutral cards should fill gaps, not outperform faction cards.

---

## 12. Board Limits

The current prototype uses a maximum of:

- **6 units**
- **3 relics**

A player cannot play a unit or relic if the relevant zone is full.

Generated units also fail to enter play if there is no available space.

---

## 13. Information and Interface Rules

The game should clearly show:

- Current and maximum mana
- Cards played this turn
- Whether the attack step has been used
- Which units can attack
- Which cards cannot currently be played
- Why a card is unavailable
- Incoming unblocked damage
- Assigned blockers
- Why a card left play
- Equipment attached to a unit
- Champion cost and active ability

Unavailable cards should be visibly desaturated and labeled with a reason such as:

- Not enough mana
- Played this turn
- Cannot attack yet
- Already attacked
- Attack already used
- Board full
- No valid target
- Champion not in play

---

## 14. Undo

The player may undo the most recent reversible action.

Examples of reversible actions:

- Playing a card
- Replacing a card
- Selecting attackers
- Assigning a blocker
- Deploying a Champion before combat resolves

The following actions are not reversible:

- Resolving combat
- Ending the turn
- Actions that reveal hidden information and cannot be restored fairly

Only one action needs to be stored for the current prototype.

---

## 15. Card-Writing Standard

Most cards should be understandable through:

- Name
- Mana cost
- Attack and Health, when applicable
- Keywords
- One short sentence

Preferred structures:

- **When played:** Do something.
- **When destroyed:** Do something.
- **After attacking:** Do something.
- **At turn start:** Do something.
- **While damaged:** Gain a bonus.

Avoid unnecessary exceptions, nested conditions, and multiple independent effects.

---

## 16. Current Open Playtest Questions

These are not fully settled:

- Whether the maximum mana should remain 10
- Whether all Champions should begin at 6 mana
- Whether Champion replay cost should rise by 2 or another amount
- Whether Equipment should always expire after one combat
- Whether some decks need more than one viable strategy
- Whether the first player needs a balancing disadvantage
- Whether Guard needs a simpler blocking rule

These should be tested through play rather than solved by adding more rules.
