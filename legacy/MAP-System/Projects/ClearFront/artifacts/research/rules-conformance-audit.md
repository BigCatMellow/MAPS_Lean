<!-- hpom: file: artifacts/research/rules-conformance-audit.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: codex-lab-lilo -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: TASK-211; clearfront_rules.md; baseline/index.html -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# ClearFront Rules-to-Implementation Conformance Audit

## Scope

- Task: `TASK-211`
- Governing specification: `source/game-card-combat-effects/clearfront_rules.md`
- Audited implementation: `baseline/index.html`
- Equivalence note: released `app/` was parity-proven against this baseline by TASK-208, so findings apply to both until behavior changes.
- Method: static rule/code trace with direct line references. No source, baseline, or app file was modified.

## Summary

| Rules section | Verdict | Short result |
|---|---|---|
| 1. Goal | MATCHES | Starts at 20 life and ends when either player reaches 0. |
| 2. Decks and Champions | DEVIATES | 30-card, two-faction Champion decks exist; neutral cards and the suggested 17/7/6 distribution do not. |
| 3. Starting the Game | MATCHES | 20 life, first-turn 1 mana, three cards, visible Champion, random first player, no compensation. |
| 4. Mana | MATCHES | Maximum mana rises by one to 10 and refills each turn; no lands. |
| 5. Three-Card Hand | DEVIATES | Hand/refill/two-play/replace rules match, but empty-deck refill adds undocumented fatigue damage. |
| 6. Turn Structure | MATCHES | Flexible main phase, one attack, cards/actions after combat, explicit end turn. |
| 7. Card Types | DEVIATES | Units, spells, and relics conform; Equipment is unimplemented. |
| 8. Champions | MATCHES | Separate slot, paid deployment, play-count cost, battlefield-only passive, +2 return cost. |
| 9. Combat | MATCHES | Ready attackers, one-to-one blockers, simultaneous combat, direct unblocked damage, persistent damage. |
| 10. Core Keywords | DEVIATES | Charge/Guard/Flying/Shield conform; Rush and Drain are narrower than written; Stun is unimplemented. |
| 11. Faction Identities | DEVIATES | Flame/Wild/Order/Shadow are represented; Mind/Forge/Neutral are absent. |
| 12. Board Limits | MATCHES | Six-unit and three-relic limits are enforced; generated-unit clause is presently unexercised. |
| 13. Information and Interface | DEVIATES | Most required state/reason displays exist; Equipment display cannot exist and some listed reason language is approximated. |
| 14. Undo | DEVIATES | One-step undo and combat/end-turn locks exist, but card replacement remains undoable after revealing hidden information. |
| 15. Card-Writing Standard | MATCHES | Current cards expose compact stats/keywords and generally one short effect sentence. |
| 16. Open Playtest Questions | UNVERIFIED | Code embodies provisional answers; playtest evidence is required to settle them. |

## Section Findings

### 1. Goal — MATCHES

- Rules: reduce 20 life to 0 and win immediately (`clearfront_rules.md:8-12`).
- Code: both sides initialize at 20 (`baseline/index.html:1868-1877`); `checkGameOver` ends the game when either life total is at or below 0 and presents Victory/Defeat/Draw (`baseline/index.html:3257-3267`).

### 2. Decks and Champions — DEVIATES

- Rules: 30 cards split among primary, allied, and neutral groups, suggested 17/7/6, with a Champion outside the deck (`clearfront_rules.md:16-36`).
- Code: each selected deck combines two 15-card faction pools into 30 cards (`baseline/index.html:1760-1769`, `baseline/index.html:1797-1802`), while six Champion-led two-faction identities are selectable (`baseline/index.html:1772-1777`, `baseline/index.html:1821-1839`). Champions are stored outside the deck and rendered separately (`baseline/index.html:1885-1891`, `baseline/index.html:3357-3377`).
- Deviation: the implementation uses an even 15/15 two-faction construction and has no Neutral cards, rather than the documented primary/allied/neutral distribution.

### 3. Starting the Game — MATCHES

- Rules: 20 life, 1 maximum mana, three cards, Champion slot, random first player, no compensation (`clearfront_rules.md:40-51`).
- Code: sides start at 20 life and 0 pre-turn mana (`baseline/index.html:1868-1877`), receive three-card starting hands (`baseline/index.html:1915-1917`, `baseline/index.html:2030-2042`), and a random first player immediately starts a turn (`baseline/index.html:1918-1920`). `startTurn` raises that player's maximum to 1 and refills it (`baseline/index.html:2112-2113`). Champion state/slot is separate (`baseline/index.html:1885-1891`, `baseline/index.html:3357-3377`). No first-player compensation branch exists.

### 4. Mana — MATCHES

- Rules: +1 maximum mana each turn, cap 10, refill to maximum, no land cards (`clearfront_rules.md:55-69`).
- Code: `Math.min(10, maxMana + 1)` followed by `mana = maxMana` (`baseline/index.html:2112-2113`). Cards have direct mana costs and the library contains no land type (`baseline/index.html:1661-1757`).

### 5. Three-Card Hand — DEVIATES

- Rules: normal hand three, at most two cards per turn, refill at end, retain unplayed cards, one replacement that does not count as a play (`clearfront_rules.md:73-87`).
- Code: constants are 3/3/2 (`baseline/index.html:1657-1659`); refill only draws to three (`baseline/index.html:2060-2069`) and runs when the owner ends a turn (`baseline/index.html:3144-3162`). Replacement discards/draws and sets `swapUsed` without incrementing `cardsPlayed` (`baseline/index.html:2073-2084`); play limits are enforced (`baseline/index.html:2272-2275`, `baseline/index.html:2343-2353`).
- Deviation: when a refill cannot draw, code deals 1 fatigue damage (`baseline/index.html:2045-2052`), a rule absent from the playtest document.

### 6. Turn Structure — MATCHES

- Rules: one flexible main phase; play, Champion, replacement, and one attack can be ordered flexibly; play may continue after combat (`clearfront_rules.md:91-109`).
- Code: player actions require the main phase but are not placed in fixed subphases (`baseline/index.html:2261-2308`); `combatUsed` prevents a second attack (`baseline/index.html:2745-2763`) while returning to `main` after combat and explicitly allowing further play (`baseline/index.html:2759-2765`). Ending the turn refills and transfers control (`baseline/index.html:3144-3162`).

### 7. Card Types — DEVIATES

- Rules: Units, Spells, Relics, and temporary attached Equipment (`clearfront_rules.md:113-157`).
- Code: units enter `board`, relics enter `relics`, and spells resolve then enter `graveyard` (`baseline/index.html:2456-2501`). Unit health persists on the stored card object and dead units are removed at 0 (`baseline/index.html:2681-2714`). Relics render in a noncombat row (`baseline/index.html:3338-3355`).
- Deviation: there are no `equipment` card definitions, attachment state, one-equipment limit, or attack/block expiry path. Equipment is unimplemented.

### 8. Champions — MATCHES

- Rules: always-visible external slot, mana deployment, counts as a play, enters as a unit, battlefield-only passive, returns at +2 cost (`clearfront_rules.md:161-189`).
- Code: deployment gates mana/board/two-card limit (`baseline/index.html:1939-1949`), spends mana and increments plays (`baseline/index.html:1952-1958`), creates a battlefield unit (`baseline/index.html:1959-1982`), and ongoing ability branches require `championInPlay` (for example `baseline/index.html:2467-2470`). Destruction returns the Champion and adds 2 cost (`baseline/index.html:1989-1994`, `baseline/index.html:2693-2701`).

### 9. Combat — MATCHES

- Rules: choose ready attackers; defender assigns at most one blocker per attacker/blocker; simultaneous blocked damage; unblocked hero damage; persistent unit damage (`clearfront_rules.md:193-225`).
- Code: `canAttack` excludes sick/exhausted/stunned units (`baseline/index.html:2240-2242`); block assignment maintains one-to-one mappings (`baseline/index.html:2416-2449`); combat computes both damage values before cleanup (`baseline/index.html:2818-2835`), unblocked damage goes to the defending player (`baseline/index.html:2859-2866`), and health remains reduced until healing/destruction (`baseline/index.html:2681-2690`, `baseline/index.html:2868-2869`).

### 10. Core Keywords — DEVIATES

See the individual keyword matrix below. The section deviates because Rush does not implement direct enemy-unit attacks, Drain is implemented only in combat, and Stun has no complete state transition.

| Keyword | Verdict | Evidence and actual behavior |
|---|---|---|
| Charge | MATCHES | Charge/Rush bypass summoning sickness on play/deployment (`baseline/index.html:1973-1974`, `baseline/index.html:2484-2486`), so Charge units satisfy `canAttack` immediately (`baseline/index.html:2240-2242`). |
| Rush | DEVIATES | Rush bypasses sickness and is marked `rushLocked` (`baseline/index.html:1973-1974`, `baseline/index.html:2484-2486`). It joins the normal player-attack flow rather than selecting an enemy unit; if unblocked on entry turn it deals 0 hero damage (`baseline/index.html:2859-2866`). The rules say it can attack enemy units immediately (`clearfront_rules.md:237-239`), which is not directly implemented. |
| Guard | MATCHES | Player blocking rejects non-Guard targets while any Guard attacker is unblocked (`baseline/index.html:2404-2413`, `baseline/index.html:2426-2433`); AI sorts Guard attackers first for blocking (`baseline/index.html:2770-2777`). |
| Flying | MATCHES | A Flying attacker requires a Flying blocker in both player and AI block paths (`baseline/index.html:2409-2423`, `baseline/index.html:2779-2781`). |
| Shield | MATCHES | Initial Shield state derives from the keyword (`baseline/index.html:1843-1856`); both effect and combat damage consume Shield and prevent the entire next instance (`baseline/index.html:2681-2685`, `baseline/index.html:2899-2908`). |
| Drain | DEVIATES | Combat damage to units or heroes heals by damage dealt (`baseline/index.html:2834-2835`, `baseline/index.html:2862-2866`). There is no general “any damage dealt by this card” hook; Drain outside combat would not work as written in `clearfront_rules.md:253-255`. Current Drain cards are combat units, so current-card behavior works. |
| Stun | UNIMPLEMENTED | `canAttack` and rendering inspect a `stunned` property (`baseline/index.html:2240-2242`, `baseline/index.html:3428-3429`), but no card/effect sets it and `startTurn` has no next-turn Stun consumption/clearing step (`baseline/index.html:2087-2146`). |

### 11. Faction Identities — DEVIATES

- Rules: seven identities—Flame, Wild, Order, Shadow, Mind, Forge, Neutral (`clearfront_rules.md:263-309`).
- Code: the card library and `FACTION_POOLS` implement only Flame, Wild, Order, and Shadow (`baseline/index.html:1661-1757`, `baseline/index.html:1797-1798`). Their cards visibly follow the stated themes: Flame damage/aggression (`baseline/index.html:1662-1679`), Wild growth/large units (`baseline/index.html:1681-1697`), Order shields/defense (`baseline/index.html:1699-1716`), and Shadow death/sacrifice/Drain/destruction (`baseline/index.html:1718-1734`).
- Deviation: Mind, Forge, and Neutral identities/card pools are absent. Equipment and Stun—the signature Forge/Mind systems—are likewise absent.

### 12. Board Limits — MATCHES

- Rules: six units, three relics, reject plays/generated units when full (`clearfront_rules.md:313-322`).
- Code: constants are 6 and 3 (`baseline/index.html:1655-1656`); UI/playability rejects full unit or relic zones (`baseline/index.html:2283-2291`, `baseline/index.html:2343-2349`), and Champion deployment also observes the unit cap (`baseline/index.html:1939-1948`).
- Caveat: no current effect generates units, so the generated-unit clause is not dynamically exercised; the ordinary unit-entry guard conforms for all current cards.

### 13. Information and Interface Rules — DEVIATES

- Rules require mana/play/attack readiness, unavailable reasons, incoming damage, blocks, leave-play reasons, Equipment, and Champion status (`clearfront_rules.md:326-351`).
- Code renders current/max mana and play count (`baseline/index.html:3307-3308`, `baseline/index.html:3435-3439`), detailed unavailable reasons (`baseline/index.html:2356-2369`, `baseline/index.html:3393-3429`), incoming damage/block assignments (`baseline/index.html:3522-3569`), destruction causes (`baseline/index.html:2693-2714`), and Champion cost/ability/status (`baseline/index.html:3357-3377`, `baseline/index.html:3622-3632`). `.card.unavailable` is visually desaturated (`baseline/index.html:226-231`).
- Deviation: Equipment attachment cannot be displayed because Equipment is unimplemented. Some exact example wording is normalized (for example “Needs N more mana” instead of “Not enough mana”), though the reason remains clear.

### 14. Undo — DEVIATES

- Rules: store one reversible action; combat, turn end, and hidden-information actions are not reversible (`clearfront_rules.md:355-373`).
- Code: one structured snapshot is stored (`baseline/index.html:1997-2019`); card plays, Champion deployment, attacker choices, and blocker choices save it (`baseline/index.html:1952-1957`, `baseline/index.html:2381-2385`, `baseline/index.html:2416-2438`, `baseline/index.html:2456-2462`). Combat and turn transitions clear undo (`baseline/index.html:2745-2755`, `baseline/index.html:3144-3162`).
- Deviation: card replacement saves undo before drawing a new hidden card (`baseline/index.html:2261-2269`), so the player may see the replacement and then undo—contrary to the hidden-information prohibition.

### 15. Card-Writing Standard — MATCHES

- Rules favor name/cost/stats/keywords plus one short sentence and standard trigger phrasing (`clearfront_rules.md:377-395`).
- Code/card data consistently uses compact fields and brief text such as “Charge,” “When played,” “When destroyed,” and “At turn start” (`baseline/index.html:1661-1757`). Rendering exposes type, name, cost, text, keywords, and applicable stats (`baseline/index.html:3464-3494`). A few prototype cards combine linked clauses, but the present library generally follows the standard without nested exception text.

### 16. Current Open Playtest Questions — UNVERIFIED

- Rules explicitly leave these questions for playtesting (`clearfront_rules.md:399-411`).
- Current implementation chooses: mana cap 10 (`baseline/index.html:2112`), all Champion base costs 6 (`baseline/index.html:1772-1777`), replay increment +2 (`baseline/index.html:1989-1994`), no Equipment, no first-player compensation (`baseline/index.html:1918-1920`), and the current Guard-first blocking implementation (`baseline/index.html:2404-2433`).
- Verdict: these are implemented prototype parameters, not validated answers. No playtest evidence in TASK-211 establishes whether they should remain.

## Prioritized Follow-Up Candidates

1. **Rules decision before implementation:** decide whether Equipment, Mind, Forge, and Neutral are committed near-term scope or future rules that should be labeled as such.
2. **Correctness:** disallow undo after replacement reveals a card, or redesign replacement undo so hidden information cannot be exploited.
3. **Keyword contract:** either implement Rush as direct enemy-unit engagement or rewrite its rule to describe the current normal-attack/zero-hero-damage behavior.
4. **Keyword completeness:** implement Stun lifecycle and tests before adding any Stun card.
5. **Rules documentation:** record fatigue damage or remove it; it currently changes the win condition in long games without appearing in the rules.
6. **Generalization:** if Drain may appear on noncombat damage cards, move healing into a common damage-source path; otherwise narrow the written keyword definition.

