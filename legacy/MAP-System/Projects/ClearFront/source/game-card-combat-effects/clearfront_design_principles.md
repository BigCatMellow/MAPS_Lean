# Clearfront — Design Principles

**Purpose:** A governing document for evaluating rules, cards, factions, and future additions

---

## 1. The Core Promise

Clearfront should provide:

> **The strategic interaction of a traditional card game with the readability of a modern digital card game.**

The player should be able to understand most cards immediately, while discovering depth through how simple cards interact.

---

## 2. Depth Should Come From Interaction

The game should not rely on complicated individual cards.

A simple card can become strategically rich when it interacts with:

- Board state
- Combat timing
- Damaged units
- Shields
- Equipment
- Unit deaths
- Relics
- Faction strategies
- The order in which cards are played

The preferred design pattern is:

> **Simple cards, complex situations.**

Not:

> **Complex cards, simple decisions.**

---

## 3. Avoid Purple Mechanics

### Definition

> **Purple mechanics are rules that create more explanation, tracking, and exceptions than meaningful decisions.**

The term is analogous to purple prose: ornamentation that draws attention to itself without improving the work.

A mechanic may be purple even when it is understandable.

The problem is not difficulty alone. The problem is poor return on complexity.

### Complexity-to-depth test

Ask:

1. How much does the player need to learn?
2. How much does the player need to track?
3. How many meaningful decisions does the mechanic create?
4. Does another system already serve the same purpose?
5. Would removing it substantially reduce strategy?

A healthy mechanic creates many decisions from a small rule.

A purple mechanic creates bookkeeping from a large rule.

### Warning signs

A mechanic may be purple when it:

- Requires several rules to produce one ordinary effect
- Adds a meter, token, zone, or counter used by few cards
- Contains multiple exceptions
- Frequently requires after-the-fact explanations
- Duplicates another mechanic
- Exists mainly because it sounds clever
- Adds tracking but not choice
- Makes the interface explain the rules more than the player uses them

### Governing rule

> **No mechanic should require more explanation than the decisions it creates.**

---

## 4. Every Mechanic Must Earn Its Place

A new mechanic should do at least one of the following:

- Create a new decision
- Strengthen a faction identity
- Make combat more interesting
- Solve a recurring play problem
- Replace a more complicated system
- Connect several existing cards

A mechanic should not be added merely to increase novelty.

When adding a system, first ask whether it can replace or consolidate an existing one.

---

## 5. One Clear Job Per System

Each major system should have one primary purpose.

| System | Primary purpose |
|---|---|
| Mana | Limit what can be played |
| Three-card hand | Limit visible options |
| Two-card turn limit | Preserve late-game choice |
| Combat | Create tactical interaction |
| Factions | Establish strategic identity |
| Champions | Define and reinforce deck identity |
| Relics | Support long-term plans |
| Equipment | Create a temporary combat decision |

When two systems perform the same job, remove or merge one.

This is why the Command-card mechanic was removed after Champions were introduced.

---

## 6. Champions Define the Deck

Champions should be the clearest expression of a deck's identity.

A Champion should:

- Be visible from the start
- Be available throughout the match
- Have one short ability
- Support the faction's normal behavior
- Be valuable without becoming mandatory
- Give the opponent a clear reason to interact with it

A Champion should not require several independent subsystems such as:

- A separate progress meter
- Multiple currencies
- A unique leveling system
- Both a large entrance effect and a large passive
- Several replay exceptions

The Champion should be memorable because of what it encourages, not because of how many rules surround it.

---

## 7. Factions Need Strengths and Weaknesses

Each faction should have:

- One central behavior
- One secondary behavior
- A recognizable visual identity
- At least one meaningful weakness

Factions should not all receive equal access to:

- Direct damage
- Healing
- Removal
- Card advantage
- Large units
- Defensive tools

Strategic identity requires limits.

A faction becomes less meaningful when it can solve every problem in the same way as every other faction.

---

## 8. Synergy Should Be Broad, Not Fragile

Good synergy uses conditions that occur naturally:

- A unit is damaged
- A unit gains Health
- A unit survives combat
- A friendly unit is destroyed
- A spell is played second
- A relic is in play

Avoid narrow synergy that requires drawing one exact named card.

A synergy card should ideally work with several cards in its deck.

### Setup and payoff

A healthy strategy usually contains:

- **Setup cards** that create a condition
- **Payoff cards** that reward it
- **Flexible cards** that work inside and outside the strategy

Payoff cards should not be completely useless without their setup unless the reward is exceptional and the risk is intentional.

---

## 9. Cards Should Create Decisions, Not Obligations

A card should not always be automatically correct to play.

Healthy cards may depend on:

- Timing
- Targets
- Combat position
- Current life
- Board space
- Whether the opponent can respond
- Whether the player is saving another card

If every card is pure immediate value, late turns become “play everything.”

Situational cards create reasons to hold, sequence, or replace cards.

---

## 10. The Three-Card Hand Must Stay Meaningful

The three-card hand is a defining constraint.

It should create:

- Limited but readable choices
- Strong card evaluation
- Reasons to keep one card
- Less visual clutter on mobile

Design around it.

Do not add systems that repeatedly fill, expand, or bypass the hand unless they create substantial strategic value.

The hand should remain a decision space, not merely a conveyor belt.

---

## 11. The Two-Card Limit Should Create Plans

The two-card-per-turn limit exists to stop late-game turns from becoming automatic.

It should encourage questions such as:

- Which two cards form the best plan?
- Which card should remain for next turn?
- Do I use removal now or develop the board?
- Do I play the Champion or two regular cards?
- Do I attack before or after playing?

Cards may care about sequencing, but order-based effects should remain easy to read and limited in number.

---

## 12. Combat Should Be the Main Source of Tension

Combat should remain understandable while producing tactical choices.

The player should consider:

- Which units attack
- Which units remain to defend
- Which blocker trades best
- Whether temporary Equipment is worth using
- Whether persistent damage makes a unit vulnerable
- Whether a Champion should enter combat

Avoid turning combat into a separate resource puzzle unless testing shows a clear need.

Ordinary attacking and blocking should not require mana by default.

---

## 13. Information Should Be Visible

The player should not need to guess why something happened.

The interface must show:

- Legal and illegal actions
- Reasons an action is illegal
- Projected combat damage
- Active bonuses
- Attached Equipment
- Champion abilities
- Destruction causes
- Discard and return effects
- Whether a unit can attack

Clarity is part of the rules, not merely presentation.

A hidden interaction is functionally a more complicated interaction.

---

## 14. Use Desaturation Consistently

Unavailable cards and units should be visually desaturated.

The reason should be stated directly.

Examples:

- Not enough mana
- Cannot attack this turn
- Already attacked
- Board full
- No valid target
- Champion not deployed
- Card limit reached

Visual language must stay consistent across cards, units, Champions, and buttons.

---

## 15. Randomness Should Create Variety, Not Confusion

Acceptable randomness includes:

- Card draw
- Opponent deck selection
- Limited random targeting where outcomes remain readable

Avoid excessive random generation of unknown cards or effects.

Randomness should produce different problems to solve, not remove the player's ability to plan.

---

## 16. Neutral Cards Should Be Reliable, Not Defining

Neutral cards should:

- Fill basic deck needs
- Provide straightforward units and utility
- Help a deck function consistently

Neutral cards should not:

- Supply the strongest synergy engines
- Outperform faction cards
- Become automatic inclusions in every deck
- Erase faction weaknesses

Faction cards should create identity. Neutral cards should provide structure.

---

## 17. Relics and Equipment Must Feel Different

### Relics

Relics provide long-term strategic effects.

They should encourage the player to build or play in a particular way.

### Equipment

Equipment creates a temporary combat advantage.

It should produce an immediate timing decision.

The distinction should remain clear:

> **Relics shape the match. Equipment shapes one fight.**

---

## 18. Keep Keywords Few and Stable

A keyword should:

- Have one meaning
- Be useful on several cards
- Be easy to represent visually
- Avoid exceptions

Do not create a keyword for an effect that appears on only one or two cards.

Do not redefine keywords between factions.

New keywords should replace repeated text, not conceal complicated rules.

---

## 19. Prefer Replacement Over Accumulation

When a new idea solves an old problem, remove the old solution.

Examples:

- Champions replaced Command cards as the main faction hook.
- A clear two-card limit replaced attempts to solve late-game dumping through cost inflation.
- Desaturation and reason labels replaced relying on the player to infer legality.

The game should become cleaner as it develops, not merely larger.

---

## 20. Test Decisions, Not Features

A playtest should ask:

- What decisions did the player make?
- Which decisions were obvious?
- Which decisions felt automatic?
- Which rules were forgotten?
- Which cards were never worth keeping?
- Which strategies lacked counterplay?
- When did the game become repetitive?
- Did the player understand why the board changed?

Do not judge a feature only by whether it functions.

Judge it by whether it improves the player's decisions.

---

## 21. Design Review Checklist

Before adding a card or mechanic, ask:

### Clarity

- Can it be explained in one short sentence?
- Can the interface show when it matters?
- Will a new player understand why it happened?

### Depth

- What decisions does it create?
- Does timing matter?
- Does the opponent have meaningful counterplay?
- Does it interact with several existing cards?

### Necessity

- Does another mechanic already do this?
- Can the same result be achieved with fewer rules?
- Would removing it noticeably harm the game?

### Identity

- Does it belong to this faction?
- Does it reinforce the deck's plan?
- Does it preserve the faction's weaknesses?

### Tracking

- Does it require memory, counters, or hidden state?
- Can the board display it directly?
- Is the tracking burden proportional to the strategic value?

If the answers are weak, the design should be simplified or removed.

---

## 22. Final Governing Principles

1. **Simple cards should create complex situations.**
2. **Depth should come from interaction, not ornamentation.**
3. **Every rule must create a meaningful decision.**
4. **No purple mechanics.**
5. **One clear job per system.**
6. **Champions define decks; factions define strategies.**
7. **The interface must explain the current game state.**
8. **New systems should replace complexity, not stack upon it.**
9. **Readable does not mean shallow.**
10. **When in doubt, simplify and playtest.**
