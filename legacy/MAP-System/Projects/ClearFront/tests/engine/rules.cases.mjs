// Table-driven rule cases for the ClearFront engine (TASK-220).
//
// Each case: { id, domain, title, deviation?, run(host, t) }.
// `deviation` marks a case that intentionally asserts CURRENT engine
// behavior where it is known to differ from clearfront_rules.md, citing the
// released TASK-211 conformance audit section. These cases are the
// decision-support layer for the pending rules-conformance disposition:
// whichever direction is chosen, the deviation-tagged expectations are the
// exact list of assertions to flip (implement-to-spec) or the exact list of
// behaviors to write into the revised rules doc.
//
// t.pre() guards setup assumptions (card actually has the keyword the case
// needs, etc.) so a wrong card pick fails loudly as SETUP, never silently
// green. All cases drive state directly through the host — no RNG, no DOM.

export const cases = [
  // ── Keywords ─────────────────────────────────────────────────────────
  {
    id: 'kw-charge-attacks-immediately',
    domain: 'keywords',
    title: 'Charge: unit can attack the turn it is played',
    run(host, t) {
      const st = host.reset();
      const card = host.S.makeCard('ember_runner');
      t.pre('ember_runner has Charge', card.keywords.includes('Charge'));
      st.player.hand.push(card);
      st.player.mana = 10;
      t.ok('playCard succeeds', host.C.playCard('player', card, null));
      t.eq('not summoning-sick', card.summoningSick, false);
      t.eq('canAttack immediately', host.C.canAttack(card), true);
    },
  },
  {
    id: 'kw-vanilla-summoning-sick',
    domain: 'keywords',
    title: 'Non-Charge unit cannot attack the turn it is played',
    run(host, t) {
      const st = host.reset();
      const card = host.S.makeCard('cinder_imp');
      t.pre('cinder_imp has no Charge/Rush', !card.keywords.includes('Charge') && !card.keywords.includes('Rush'));
      st.player.hand.push(card);
      st.player.mana = 10;
      t.ok('playCard succeeds', host.C.playCard('player', card, null));
      t.eq('summoning-sick', card.summoningSick, true);
      t.eq('cannot attack yet', host.C.canAttack(card), false);
    },
  },
  {
    id: 'kw-rush-zero-hero-damage-on-entry-turn',
    domain: 'keywords',
    title: 'Rush: unblocked attack on entry turn deals 0 damage to the hero',
    deviation: {
      audit: 'TASK-211 §10 (Rush DEVIATES)',
      note: 'Rules text says Rush "can attack enemy units immediately"; the engine implements this as normal attack flow where an unblocked rushLocked attacker deals 0 hero damage. No direct unit-targeting path exists.',
    },
    run(host, t) {
      const st = host.reset();
      const attacker = host.spawn('cinder_imp', 'player', { keywords: ['Rush'], rushLocked: true });
      const lifeBefore = st.enemy.life;
      host.C.resolveCombat('player', [attacker], new Map(), () => {});
      t.eq('enemy hero took no damage from rush-locked attacker', st.enemy.life, lifeBefore);
    },
  },
  {
    id: 'kw-rush-damages-blockers-normally',
    domain: 'keywords',
    title: 'Rush: blocked combat on entry turn damages the blocker normally',
    run(host, t) {
      const st = host.reset();
      const attacker = host.spawn('cinder_imp', 'player', { keywords: ['Rush'], rushLocked: true });
      const blocker = host.spawn('recruit', 'enemy', { currentHealth: 5, maxHealth: 5 });
      const power = host.C.cardAttack(attacker, true, 'player');
      t.pre('attacker has positive attack', power > 0);
      host.C.resolveCombat('player', [attacker], new Map([[blocker.uid, attacker.uid]]), () => {});
      t.eq('blocker took full attacker damage', blocker.currentHealth, 5 - power);
    },
  },
  {
    id: 'kw-guard-must-be-blocked-first',
    domain: 'keywords',
    title: 'Guard: non-Guard attackers cannot be blocked while a Guard attacker is unblocked',
    run(host, t) {
      const st = host.reset();
      const guard = host.spawn('hollow_guard', 'enemy');
      const plain = host.spawn('grave_rat', 'enemy');
      t.pre('hollow_guard has Guard', guard.keywords.includes('Guard'));
      t.pre('grave_rat has no Guard', !plain.keywords.includes('Guard'));
      const blocker = host.spawn('recruit', 'player');
      st.aiAttackers = [guard, plain];
      st.blockAssignments = new Map();
      st.selectedBlocker = blocker.uid;
      t.eq('blocking the non-Guard is rejected', host.C.blockTargetReason(plain), 'Block Guard first');
      t.eq('blocking the Guard is allowed', host.C.blockTargetReason(guard), '');
      st.blockAssignments.set(blocker.uid, guard.uid);
      const blocker2 = host.spawn('recruit', 'player');
      st.selectedBlocker = blocker2.uid;
      t.eq('non-Guard blockable once Guard is covered', host.C.blockTargetReason(plain), '');
    },
  },
  {
    id: 'kw-flying-needs-flying-blocker',
    domain: 'keywords',
    title: 'Flying: only Flying units can block a Flying attacker',
    run(host, t) {
      const st = host.reset();
      const flyer = host.spawn('skyguard', 'enemy');
      t.pre('skyguard has Flying', flyer.keywords.includes('Flying'));
      const ground = host.spawn('recruit', 'player');
      const wing = host.spawn('night_wing', 'player');
      t.pre('night_wing has Flying', wing.keywords.includes('Flying'));
      st.aiAttackers = [flyer];
      st.blockAssignments = new Map();
      st.selectedBlocker = ground.uid;
      t.eq('ground blocker rejected', host.C.blockTargetReason(flyer), 'Needs a Flying blocker');
      st.selectedBlocker = wing.uid;
      t.eq('flying blocker accepted', host.C.blockTargetReason(flyer), '');
    },
  },
  {
    id: 'kw-shield-effect-damage',
    domain: 'keywords',
    title: 'Shield: absorbs one full effect-damage instance, then clears',
    run(host, t) {
      host.reset();
      const unit = host.spawn('shield_recruit', 'player', { currentHealth: 3, maxHealth: 3, shield: true });
      host.C.dealDamage(unit, 2, 'enemy');
      t.eq('first instance fully absorbed', unit.currentHealth, 3);
      t.eq('shield consumed', unit.shield, false);
      host.C.dealDamage(unit, 2, 'enemy');
      t.eq('second instance lands', unit.currentHealth, 1);
    },
  },
  {
    id: 'kw-shield-combat-damage',
    domain: 'keywords',
    title: 'Shield: absorbs one full combat-damage instance, then clears',
    run(host, t) {
      host.reset();
      const unit = host.spawn('ward_novice', 'player', { currentHealth: 2, maxHealth: 2, shield: true });
      const source = host.spawn('recruit', 'enemy'); // engine contract: source is always a real unit
      const dealt = host.C.dealCombatDamage(unit, 4, source);
      t.eq('shielded combat hit deals 0', dealt, 0);
      t.eq('health unchanged', unit.currentHealth, 2);
      t.eq('shield consumed', unit.shield, false);
    },
  },
  {
    id: 'kw-drain-blocked-combat-heals',
    domain: 'keywords',
    title: 'Drain: blocked combat damage heals the controller, capped at 20',
    deviation: {
      audit: 'TASK-211 §10 (Drain DEVIATES)',
      note: 'Rules say "damage dealt by this card" generally; the engine implements Drain only in combat resolution paths. All current Drain cards are combat units, so shipped behavior is correct for the shipped card pool.',
    },
    run(host, t) {
      const st = host.reset();
      const drainer = host.spawn('blood_leech', 'player');
      t.pre('blood_leech has Drain', drainer.keywords.includes('Drain'));
      const blocker = host.spawn('recruit', 'enemy', { currentHealth: 9, maxHealth: 9 });
      const power = host.C.cardAttack(drainer, true, 'player');
      st.player.life = 19;
      host.C.resolveCombat('player', [drainer], new Map([[blocker.uid, drainer.uid]]), () => {});
      t.eq('controller healed by damage dealt, capped at 20', st.player.life, Math.min(20, 19 + power));
    },
  },
  {
    id: 'kw-drain-unblocked-heals',
    domain: 'keywords',
    title: 'Drain: unblocked hero damage heals the controller',
    run(host, t) {
      const st = host.reset();
      const drainer = host.spawn('blood_leech', 'player');
      const power = host.C.cardAttack(drainer, true, 'player');
      st.player.life = 10;
      const enemyLifeBefore = st.enemy.life;
      host.C.resolveCombat('player', [drainer], new Map(), () => {});
      t.eq('hero took the damage', st.enemy.life, enemyLifeBefore - power);
      t.eq('controller healed by amount dealt', st.player.life, 10 + power);
    },
  },
  {
    id: 'kw-stun-respected-but-never-set',
    domain: 'keywords',
    title: 'Stun: canAttack respects the flag, but no engine path ever sets it',
    deviation: {
      audit: 'TASK-211 §10 (Stun UNIMPLEMENTED)',
      note: 'The stunned flag is read by canAttack and rendering but no card, effect, or lifecycle step assigns it. Rules doc lists Stun as a core keyword (Mind faction signature). Verified by source grep: zero `.stunned =` assignment sites.',
    },
    run(host, t) {
      host.reset();
      const unit = host.spawn('recruit', 'player');
      t.eq('ready unit can attack', host.C.canAttack(unit), true);
      unit.stunned = true;
      t.eq('stunned unit cannot attack', host.C.canAttack(unit), false);
    },
  },

  // ── Combat math ──────────────────────────────────────────────────────
  {
    id: 'combat-unblocked-full-hero-damage',
    domain: 'combat',
    title: 'Unblocked attacker deals full attack to the defending hero',
    run(host, t) {
      const st = host.reset();
      const attacker = host.spawn('recruit', 'player');
      const power = host.C.cardAttack(attacker, true, 'player');
      const before = st.enemy.life;
      host.C.resolveCombat('player', [attacker], new Map(), () => {});
      t.eq('hero life reduced by attack value', st.enemy.life, before - power);
    },
  },
  {
    id: 'combat-blocked-simultaneous',
    domain: 'combat',
    title: 'Blocked combat: attacker and blocker damage each other simultaneously',
    run(host, t) {
      host.reset();
      const attacker = host.spawn('recruit', 'player', { currentHealth: 6, maxHealth: 6 });
      const blocker = host.spawn('recruit', 'enemy', { currentHealth: 6, maxHealth: 6 });
      const ap = host.C.cardAttack(attacker, true, 'player');
      const bp = host.C.cardAttack(blocker, false, 'enemy');
      host.C.resolveCombat('player', [attacker], new Map([[blocker.uid, attacker.uid]]), () => {});
      t.eq('blocker damaged by attacker power', blocker.currentHealth, 6 - ap);
      t.eq('attacker damaged by blocker power', attacker.currentHealth, 6 - bp);
    },
  },
  {
    id: 'combat-simultaneous-lethal-both-die',
    domain: 'combat',
    title: 'Simultaneous lethal: both units are destroyed and leave the board',
    run(host, t) {
      const st = host.reset();
      const attacker = host.spawn('recruit', 'player', { currentHealth: 1, maxHealth: 1 });
      const blocker = host.spawn('recruit', 'enemy', { currentHealth: 1, maxHealth: 1 });
      t.pre('both have lethal attack vs 1 health', host.C.cardAttack(attacker, true, 'player') >= 1 && host.C.cardAttack(blocker, false, 'enemy') >= 1);
      host.C.resolveCombat('player', [attacker], new Map([[blocker.uid, attacker.uid]]), () => {});
      t.eq('attacker removed', st.player.board.some(u => u.uid === attacker.uid), false);
      t.eq('blocker removed', st.enemy.board.some(u => u.uid === blocker.uid), false);
    },
  },
  {
    id: 'combat-persistent-damage',
    domain: 'combat',
    title: 'Persistent damage: a surviving unit keeps its reduced health',
    run(host, t) {
      const st = host.reset();
      const attacker = host.spawn('recruit', 'player');
      const blocker = host.spawn('recruit', 'enemy', { currentHealth: 8, maxHealth: 8 });
      const ap = host.C.cardAttack(attacker, true, 'player');
      t.pre('non-lethal to 8 health', ap < 8);
      host.C.resolveCombat('player', [attacker], new Map([[blocker.uid, attacker.uid]]), () => {});
      t.eq('survivor keeps reduced health', blocker.currentHealth, 8 - ap);
      t.eq('survivor still on board', st.enemy.board.some(u => u.uid === blocker.uid), true);
    },
  },
  {
    id: 'combat-lethal-hero-damage-ends-game',
    domain: 'combat',
    title: 'Reducing the defending hero to 0 ends the game',
    run(host, t) {
      const st = host.reset();
      const attacker = host.spawn('recruit', 'player');
      st.enemy.life = host.C.cardAttack(attacker, true, 'player');
      host.C.resolveCombat('player', [attacker], new Map(), () => {});
      t.eq('enemy at 0', st.enemy.life <= 0, true);
      t.eq('game over', st.gameOver, true);
    },
  },

  // ── Champion lifecycle ───────────────────────────────────────────────
  {
    id: 'champion-deploy-gated-by-mana',
    domain: 'champion',
    title: 'Champion deployment is refused without enough mana',
    run(host, t) {
      const st = host.reset();
      st.player.mana = 0;
      st.player.cardsPlayed = 0;
      t.ok('a non-empty refusal reason is given', host.S.championDeployReason('player') !== '');
      t.eq('deployChampion refuses', host.S.deployChampion('player'), false);
    },
  },
  {
    id: 'champion-deploy-spends-and-counts',
    domain: 'champion',
    title: 'Deployment spends mana, counts as one of the two plays, enters as a unit',
    run(host, t) {
      const st = host.reset();
      st.player.mana = 10;
      st.player.cardsPlayed = 0;
      const cost = st.player.championCost;
      t.eq('deploy succeeds', host.S.deployChampion('player'), true);
      t.eq('mana spent', st.player.mana, 10 - cost);
      t.eq('counts as a play', st.player.cardsPlayed, 1);
      t.eq('champion flagged in play', st.player.championInPlay, true);
      t.eq('champion unit on board', st.player.board.some(u => u.isChampion), true);
    },
  },
  {
    id: 'champion-returns-at-plus-two',
    domain: 'champion',
    title: 'Destroyed champion returns to its slot at +2 cost',
    run(host, t) {
      const st = host.reset();
      st.player.mana = 10;
      st.player.cardsPlayed = 0;
      host.S.deployChampion('player');
      const unit = st.player.board.find(u => u.isChampion);
      const costBefore = st.player.championCost;
      host.S.returnChampionToSlot('player', unit);
      t.eq('champion back in slot', st.player.championInPlay, false);
      t.eq('cost escalated by exactly 2', st.player.championCost, costBefore + 2);
    },
  },
  {
    id: 'champion-order-prevent-once-per-cycle',
    domain: 'champion',
    title: 'orderPrevent passive shaves damage once per cycle, then is spent',
    run(host, t) {
      const st = host.reset({ enemyDeck: 2 }); // Iron Covenant: orderPrevent
      t.pre('enemy champion is orderPrevent', host.S.championDef('enemy').abilityKey === 'orderPrevent');
      st.enemy.championInPlay = true;
      st.enemy.championOrderReady = true;
      t.eq('first damage shaved by 1 (3→2)', host.C.damageHero('enemy', 3, 'player', 'test'), 2);
      t.eq('second damage lands in full', host.C.damageHero('enemy', 3, 'player', 'test'), 3);
    },
  },
  {
    id: 'champion-wild-health-first-unit',
    domain: 'champion',
    title: 'wildHealth passive: first unit played each cycle gains bonus health, once',
    run(host, t) {
      const st = host.reset({ playerDeck: 1 }); // Verdant Court: wildHealth
      const champ = host.S.championDef('player');
      t.pre('player champion is wildHealth', champ.abilityKey === 'wildHealth');
      st.player.championInPlay = true;
      st.player.championUnitUsed = false;
      st.player.mana = 10;
      st.player.cardsPlayed = 0;
      const base = host.S.makeCard('cinder_imp').maxHealth;
      const first = host.S.makeCard('cinder_imp');
      st.player.hand.push(first);
      host.C.playCard('player', first, null);
      t.eq('first unit gained bonus max health', first.maxHealth, base + champ.abilityMag);
      const second = host.S.makeCard('cinder_imp');
      st.player.hand.push(second);
      host.C.playCard('player', second, null);
      t.eq('second unit gets no bonus (used this cycle)', second.maxHealth, base);
    },
  },

  {
    id: 'champion-flame-damage-first-card',
    domain: 'champion',
    title: 'flameDamage passive: first damage card each cycle deals bonus damage, once',
    run(host, t) {
      const st = host.reset({ playerDeck: 0 }); // Emberwild: flameDamage
      const champ = host.S.championDef('player');
      t.pre('player champion is flameDamage', champ.abilityKey === 'flameDamage');
      st.player.championInPlay = true;
      st.player.championDamageUsed = false;
      st.player.mana = 10;
      st.player.cardsPlayed = 0;
      const first = host.spawn('recruit', 'enemy', { currentHealth: 5, maxHealth: 5 });
      const scorch = host.S.makeCard('scorch');
      t.pre('scorch is a damage2 spell', scorch.effect === 'damage2');
      st.player.hand.push(scorch);
      t.ok('empowered play succeeds', host.C.playCard('player', scorch, first));
      t.eq('first damage card deals 2 + passive bonus', first.currentHealth, 5 - (2 + champ.abilityMag));
      t.eq('passive consumed for the cycle', st.player.championDamageUsed, true);
      const second = host.spawn('recruit', 'enemy', { currentHealth: 5, maxHealth: 5 });
      const scorch2 = host.S.makeCard('scorch');
      st.player.hand.push(scorch2);
      host.C.playCard('player', scorch2, second);
      t.eq('second damage card deals base 2 only', second.currentHealth, 3);
    },
  },
  {
    id: 'champion-shadow-death-first-friendly-death',
    domain: 'champion',
    title: 'shadowDeath passive: first friendly death each cycle pings the enemy hero, once',
    run(host, t) {
      const st = host.reset({ playerDeck: 3 }); // Ashen Murder: shadowDeath
      const champ = host.S.championDef('player');
      t.pre('player champion is shadowDeath', champ.abilityKey === 'shadowDeath');
      st.player.championInPlay = true;
      st.player.championDeathUsed = false;
      const victim = host.spawn('cinder_imp', 'player', { currentHealth: 1, maxHealth: 1 });
      const source = host.spawn('recruit', 'enemy');
      const enemyLife = st.enemy.life;
      host.C.dealDamage(victim, 1, 'enemy', source);
      host.C.removeDeadUnits();
      t.eq('victim removed', st.player.board.some(u => u.uid === victim.uid), false);
      t.eq('enemy hero pinged by passive', st.enemy.life, enemyLife - champ.abilityMag);
      t.eq('passive consumed for the cycle', st.player.championDeathUsed, true);
      const victim2 = host.spawn('cinder_imp', 'player', { currentHealth: 1, maxHealth: 1 });
      host.C.dealDamage(victim2, 1, 'enemy', source);
      host.C.removeDeadUnits();
      t.eq('second friendly death does not ping again', st.enemy.life, enemyLife - champ.abilityMag);
    },
  },

  // ── Target legality (getTargetInfo switch, direct) ───────────────────
  {
    id: 'target-enemy-friendly-and-default-shapes',
    domain: 'targeting',
    title: 'getTargetInfo: enemy-target, friendly-target, and no-target card shapes',
    run(host, t) {
      const st = host.reset();
      const foe = host.spawn('recruit', 'enemy');
      const ally = host.spawn('recruit', 'player');
      const scorch = host.S.makeCard('scorch'); // damage2 → enemy units
      const mend = host.S.makeCard('mend'); // heal3 → friendly units
      t.pre('effects as expected', scorch.effect === 'damage2' && mend.effect === 'heal3');
      const enemyInfo = host.C.getTargetInfo(scorch, 'player');
      t.eq('damage spell needs a target', enemyInfo.needsTarget, true);
      t.eq('damage spell targets the enemy board', enemyInfo.targets.every(u => st.enemy.board.includes(u)) && enemyInfo.targets.length === st.enemy.board.length, true);
      t.eq('own units are not legal damage targets', enemyInfo.targets.includes(ally), false);
      const friendlyInfo = host.C.getTargetInfo(mend, 'player');
      t.eq('heal spell needs a target', friendlyInfo.needsTarget, true);
      t.eq('heal spell targets the friendly board', friendlyInfo.targets.includes(ally) && !friendlyInfo.targets.includes(foe), true);
      const vanilla = host.S.makeCard('recruit');
      const noneInfo = host.C.getTargetInfo(vanilla, 'player');
      t.eq('effect-less card needs no target', noneInfo.needsTarget, false);
      t.eq('effect-less card has no targets', noneInfo.targets.length, 0);
    },
  },
  {
    id: 'target-filtered-damaged-only',
    domain: 'targeting',
    title: 'getTargetInfo: finishWeak filters legal targets to damaged enemies only',
    run(host, t) {
      const st = host.reset();
      const healthy = host.spawn('recruit', 'enemy', { currentHealth: 4, maxHealth: 4 });
      const wounded = host.spawn('recruit', 'enemy', { currentHealth: 2, maxHealth: 4 });
      const card = host.S.makeCard('finish_weak');
      t.pre('finish_weak is finishWeak', card.effect === 'finishWeak');
      const info = host.C.getTargetInfo(card, 'player');
      t.eq('needs a target', info.needsTarget, true);
      t.eq('wounded enemy is legal', info.targets.includes(wounded), true);
      t.eq('healthy enemy is filtered out', info.targets.includes(healthy), false);
      t.eq('exactly the damaged set', info.targets.length, 1);
    },
  },

  // ── Resources and limits ─────────────────────────────────────────────
  {
    id: 'resource-fatigue-on-empty-deck',
    domain: 'resources',
    title: 'Empty-deck draw deals exactly 1 fatigue damage — but only when there is draw room',
    deviation: {
      audit: 'TASK-211 §5 (fatigue undocumented)',
      note: 'clearfront_rules.md has no fatigue rule at all; the engine deals 1 life per failed empty-deck draw. Nuance: the hand-limit guard runs before the fatigue branch, so a full hand short-circuits with no damage.',
    },
    run(host, t) {
      const st = host.reset();
      st.player.deck = [];
      st.player.hand.pop();
      const before = st.player.life;
      host.S.drawCard('player', false);
      t.eq('1 fatigue damage on empty-deck draw', st.player.life, before - 1);
      st.player.hand.push(host.S.makeCard('cinder_imp'));
      const before2 = st.player.life;
      host.S.drawCard('player', false);
      t.eq('full hand short-circuits before fatigue', st.player.life, before2);
    },
  },
  {
    id: 'resource-board-limit-six',
    domain: 'resources',
    title: 'A seventh unit is not playable onto a full board',
    run(host, t) {
      const st = host.reset();
      for (let i = 0; i < 6; i++) host.spawn('cinder_imp', 'player');
      st.player.mana = 10;
      st.player.cardsPlayed = 0;
      t.eq('unit unplayable at 6 on board', host.C.isCardPlayable('player', host.S.makeCard('cinder_imp')), false);
    },
  },
  {
    id: 'resource-relic-limit-three',
    domain: 'resources',
    title: 'A fourth relic is not playable onto a full relic row',
    run(host, t) {
      const st = host.reset();
      const relic = host.S.makeCard('ember_shrine');
      t.pre('ember_shrine is a relic', relic.type === 'relic');
      for (let i = 0; i < 3; i++) st.player.relics.push(host.S.makeCard('ember_shrine'));
      st.player.mana = 10;
      st.player.cardsPlayed = 0;
      t.eq('relic unplayable at 3 relics', host.C.isCardPlayable('player', relic), false);
    },
  },
  {
    id: 'resource-play-limits',
    domain: 'resources',
    title: 'playCard enforces mana, the two-card limit, and hand membership',
    run(host, t) {
      const st = host.reset();
      const card = host.S.makeCard('cinder_imp');
      st.player.hand.push(card);
      st.player.mana = 0;
      st.player.cardsPlayed = 0;
      t.eq('refused without mana', host.C.playCard('player', card, null), false);
      st.player.mana = 10;
      st.player.cardsPlayed = 2;
      t.eq('refused after two plays', host.C.playCard('player', card, null), false);
      st.player.cardsPlayed = 0;
      const ghost = host.S.makeCard('cinder_imp'); // never added to hand
      t.eq('refused when card not in hand', host.C.playCard('player', ghost, null), false);
      t.eq('accepted when all constraints satisfied', host.C.playCard('player', card, null), true);
    },
  },
  {
    id: 'resource-replace-once-per-turn',
    domain: 'resources',
    title: 'Replacement discards+draws once per turn and never counts as a play',
    run(host, t) {
      const st = host.reset();
      const target = st.player.hand[0];
      const graveBefore = st.player.graveyard.length;
      const playsBefore = st.player.cardsPlayed;
      t.eq('first replacement succeeds', host.S.replaceCard('player', target.uid, true, false), true);
      t.eq('discard went to graveyard', st.player.graveyard.length, graveBefore + 1);
      t.eq('hand refilled to same size', st.player.hand.length, 3);
      t.eq('does not count as a play', st.player.cardsPlayed, playsBefore);
      t.eq('swap marked used', st.player.swapUsed, true);
      t.eq('second replacement refused', host.S.replaceCard('player', st.player.hand[0].uid, true, false), false);
    },
  },
  {
    id: 'resource-deck-construction-15-15',
    domain: 'resources',
    title: 'Decks are an even 15+15 two-faction pool of 30 cards',
    deviation: {
      audit: 'TASK-211 §2 (deck composition DEVIATES)',
      note: 'Rules doc specifies 30 cards as 17 primary / 7 allied / 6 neutral; the engine builds an even 15/15 split of two faction pools and no Neutral cards exist.',
    },
    run(host, t) {
      const host2 = host; // same context fine — pure function
      const deckDef = host2.CF.DECKS[0];
      const list = host2.S.buildDecklist(deckDef);
      t.eq('deck is 30 cards', list.length, 30);
      const [a, b] = deckDef.factions;
      const countA = list.filter(id => host2.CF.CARD_LIBRARY[id].faction === a).length;
      const countB = list.filter(id => host2.CF.CARD_LIBRARY[id].faction === b).length;
      t.eq('15 cards from primary faction', countA, 15);
      t.eq('15 cards from allied faction', countB, 15);
    },
  },

  // ── Undo (engine level, incl. TASK-213 semantics) ────────────────────
  {
    id: 'undo-snapshot-roundtrip',
    domain: 'undo',
    title: 'saveUndo/undoLastAction restores the full prior state snapshot',
    run(host, t) {
      const st = host.reset();
      const lifeBefore = st.player.life;
      const handBefore = st.player.hand.length;
      host.S.saveUndo('probe');
      host.state.player.life -= 5;
      host.state.player.hand.pop();
      t.eq('canUndo true after save', host.S.canUndo(), true);
      host.S.undoLastAction();
      t.eq('life restored', host.state.player.life, lifeBefore);
      t.eq('hand restored', host.state.player.hand.length, handBefore);
      t.eq('undo consumed', host.S.canUndo(), false);
    },
  },
  {
    id: 'undo-clear-drops-older-snapshot',
    domain: 'undo',
    title: 'clearUndo wipes any existing snapshot (TASK-213/INS-0025 hidden-information rule)',
    run(host, t) {
      host.reset();
      host.S.saveUndo('older reversible action');
      t.eq('snapshot exists', host.S.canUndo(), true);
      host.S.clearUndo();
      t.eq('snapshot gone — replacement reveal cannot be reverted', host.S.canUndo(), false);
    },
  },
  {
    id: 'undo-play-creates-then-replace-clears',
    domain: 'undo',
    title: 'Playing a card arms undo; the replacement flow disarms it',
    run(host, t) {
      const st = host.reset();
      const card = host.S.makeCard('cinder_imp');
      st.player.hand.push(card);
      st.player.mana = 10;
      st.player.cardsPlayed = 0;
      host.C.playCard('player', card, null);
      t.eq('play armed undo', host.S.canUndo(), true);
      // Engine-level equivalent of handleHandCard's swap branch (TASK-213):
      host.S.clearUndo();
      host.S.replaceCard('player', st.player.hand[0].uid, true, false);
      t.eq('undo unavailable after replacement', host.S.canUndo(), false);
    },
  },
];
