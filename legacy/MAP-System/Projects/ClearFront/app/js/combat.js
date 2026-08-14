(() => {
  'use strict';
  const CF = (window.CF = window.CF || {});
  const { MAX_BOARD, MAX_RELICS, MAX_CARDS_PER_TURN } = CF;

  // Combat layer (DEC-CF-005). Shares mutable game state through the same
  // ctx contract state.js uses: ctx.state is the only mutable binding this
  // module touches (getter/setter over the binding declared once in
  // app/index.html). render/playClashSequence/renderCombatReport moved
  // into js/render.js (DEC-CF-006); state.js and render.js functions are
  // both called via their window.CF-published form (CF.addLog, CF.render,
  // etc.) since ctx is reserved for cross-file reassignment.
  CF.installCombatModule = (ctx) => {
  const { refs } = ctx;

  function cardAttack(card, attacking = false, owner = 'player') {
    let value = (card.attack || 0) + (card.bonusAttack || 0);
    if (card.effect === 'damagedEnemyBoost' && CF.sideOf(CF.otherSide(owner)).board.some(unit => unit.currentHealth < unit.maxHealth)) value += 2;
    if (attacking && CF.sideOf(owner).relics.some(r => r.effect === 'attackBoost')) value += 1;
    return value;
  }

  function effectiveCost(card, owner) {
    return card.cost;
  }

  function isDamageCard(card) {
    return ['pingHero','pingUnit','damage2','damage3','aoe1','aoe2','aoe3','damage2heal2','preparedStrike','finishWeak','sacrificeBlast'].includes(card.effect);
  }

  function isDamageSpell(card) {
    return card.type === 'spell' && isDamageCard(card);
  }

  function damageHero(targetOwner, amount, sourceOwner, sourceName) {
    const target = CF.sideOf(targetOwner);
    const targetChamp = CF.championDef(targetOwner);
    let prevented = 0;
    if (sourceOwner !== targetOwner && target.championInPlay && targetChamp.abilityKey === 'orderPrevent' && target.championOrderReady && amount > 0) {
      prevented = Math.min(targetChamp.abilityMag, amount);
      target.championOrderReady = false;
      CF.addLog(`${targetChamp.name} prevented ${prevented} damage to ${CF.controllerLabel(targetOwner).toLowerCase()}.`, targetOwner === 'player' ? 'good' : 'bad', `${sourceName || 'The damage source'} dealt ${amount - prevented} instead of ${amount}.`);
    }
    const dealt = Math.max(0, amount - prevented);
    target.life -= dealt;
    return dealt;
  }

  function getCardCondition(card, owner) {
    const side = CF.sideOf(owner);
    const enemy = CF.sideOf(CF.otherSide(owner));
    const first = side.cardsPlayed === 0;
    const second = side.cardsPlayed === 1;
    switch (card.effect) {
      case 'damagedEnemyBoost': {
        const active = enemy.board.some(unit => unit.currentHealth < unit.maxHealth);
        return { active, tone: active ? 'synergy' : 'setup', text: active ? 'Bonus active: +2 Attack' : 'Needs a damaged enemy' };
      }
      case 'preparedStrike':
        return { active: second, tone: second ? 'synergy' : 'setup', text: second ? 'Second-card bonus: 4 damage' : 'Play second for 4 damage' };
      case 'finishWeak': {
        const count = enemy.board.filter(unit => unit.currentHealth < unit.maxHealth).length;
        return { active: count > 0, tone: count > 0 ? 'synergy' : 'setup', text: count ? `Payoff ready: ${count} damaged target${count === 1 ? '' : 's'}` : 'Needs a damaged enemy' };
      }
      case 'packInstinct':
        return { active: first, tone: first ? 'synergy' : 'setup', text: first ? 'First-card bonus: +2/+2' : 'Now gives +1/+1' };
      case 'growOnHealth':
        return { active: side.hand.some(c => ['giveHealth2','heal3','heal4','buff2','packInstinct'].includes(c.effect)) || side.relics.some(r => r.effect === 'healthGainAttack'), tone: 'setup', text: 'Grows whenever it gains Health' };
      case 'giveHealth2': {
        const active = side.board.some(unit => unit.effect === 'growOnHealth') || side.relics.some(r => r.effect === 'healthGainAttack');
        return { active, tone: active ? 'synergy' : 'setup', text: active ? 'Growth synergy ready' : 'Sets up high-Health units' };
      }
      case 'shieldIfBigFriend': {
        const active = side.board.some(unit => unit.uid !== card.uid && (unit.currentHealth >= 5 || unit.maxHealth >= 5));
        return { active, tone: active ? 'synergy' : 'setup', text: active ? 'Bonus active: enters Shielded' : 'Needs another 5-Health unit' };
      }
      case 'shieldOther': {
        const active = side.board.length > 0;
        return { active, tone: active ? 'synergy' : 'setup', text: active ? 'Shield target ready' : 'Play later to grant Shield' };
      }
      case 'buffDamaged': {
        const count = side.board.filter(unit => unit.currentHealth < unit.maxHealth).length;
        return { active: count > 0, tone: count > 0 ? 'synergy' : 'setup', text: count ? `Bonus ready: ${count} damaged unit${count === 1 ? '' : 's'}` : 'Needs damaged friendly units' };
      }
      case 'shieldIfOneCard':
        return { active: side.cardsPlayed <= 1, tone: 'setup', text: 'End after 1 card to gain Shield' };
      case 'growAfterSurvive':
        return { active: true, tone: 'setup', text: 'Grows after surviving combat' };
      case 'growOnFriendlyDeath':
        return { active: side.board.some(unit => unit.uid !== card.uid), tone: 'setup', text: 'Grows whenever an ally dies' };
      case 'sacrificeBlast': {
        const active = side.board.length > 0 && enemy.board.length > 0;
        return { active, tone: active ? 'synergy' : 'setup', text: active ? `Sacrifice ready: ${side.board.length} possible` : 'Needs units on both boards' };
      }
      case 'firstSpellBonus':
        return { active: !side.firstSpellBonusUsed, tone: !side.firstSpellBonusUsed ? 'synergy' : 'setup', text: !side.firstSpellBonusUsed ? 'Next damage spell: +1 damage' : 'Bonus used this turn' };
      case 'healthGainAttack':
        return { active: !side.healthGainTriggerUsed, tone: !side.healthGainTriggerUsed ? 'synergy' : 'setup', text: !side.healthGainTriggerUsed ? 'Next Health gain: +1 Attack' : 'Trigger used this turn' };
      case 'surviveHeal':
        return { active: !side.surviveTriggerUsed, tone: !side.surviveTriggerUsed ? 'synergy' : 'setup', text: !side.surviveTriggerUsed ? 'Next survivor restores 1 life' : 'Trigger used this turn' };
      case 'firstDeathPing':
        return { active: !side.deathTriggerUsed, tone: !side.deathTriggerUsed ? 'synergy' : 'setup', text: !side.deathTriggerUsed ? 'Next ally death deals 1' : 'Trigger used this turn' };
      default:
        return null;
    }
  }

  function canAttack(card) {
    return card.type === 'unit' && !card.summoningSick && !card.exhausted && !card.stunned;
  }

  function usesCompactLayout() {
    return window.matchMedia('(max-width: 760px)').matches;
  }

  function scrollZoneIntoView(element) {
    if (!usesCompactLayout() || !element) return;
    window.setTimeout(() => {
      element.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' });
    }, 40);
  }

  function scrollToTargets(targetInfo, owner) {
    if (!usesCompactLayout()) return;
    const enemyTarget = targetInfo.targets.some(target => CF.sideOf(CF.otherSide(owner)).board.some(unit => unit.uid === target.uid));
    scrollZoneIntoView(enemyTarget ? refs.enemyBoard : refs.playerBoard);
  }

  function handleHandCard(card) {
    if (ctx.state.gameOver || ctx.state.turn !== 'player' || ctx.state.phase !== 'main') return;
    const side = ctx.state.player;
    if (ctx.state.swapMode) {
      // Replacement reveals a new hidden card, so neither this action nor an
      // earlier snapshot may remain reversible after the draw.
      CF.clearUndo();
      CF.replaceCard('player', card.uid, true, true);
      ctx.state.swapMode = false;
      CF.render();
      return;
    }
    if (ctx.state.targetMode) return;
    if (side.cardsPlayed >= MAX_CARDS_PER_TURN) {
      CF.addLog('You have already played 2 cards this turn.', 'bad', 'You may still attack, swap a card, or end your turn.');
      CF.render();
      return;
    }
    const cost = effectiveCost(card, 'player');
    if (cost > side.mana) {
      CF.addLog(`Not enough mana for ${card.name}.`, 'bad');
      CF.render();
      return;
    }
    if (card.type === 'unit' && side.board.length >= MAX_BOARD) {
      CF.addLog('Your board is full.', 'bad');
      CF.render();
      return;
    }
    if (card.type === 'relic' && side.relics.length >= MAX_RELICS) {
      CF.addLog('Your relic row is full.', 'bad');
      CF.render();
      return;
    }

    const targetInfo = getTargetInfo(card, 'player');
    if (targetInfo.needsTarget) {
      if (!targetInfo.targets.length) {
        CF.addLog(`There is no valid target for ${card.name}.`, 'bad');
        CF.render();
        return;
      }
      ctx.state.targetMode = { cardUid: card.uid, owner: 'player', validUids: new Set(targetInfo.targets.map(t => t.uid)), description: targetInfo.description };
      CF.addLog(`Choose a target for ${card.name}.`, 'info');
      CF.render();
      scrollToTargets(targetInfo, 'player');
      return;
    }

    playCard('player', card, null);
  }

  function getTargetInfo(card, owner) {
    const friendly = CF.sideOf(owner).board;
    const enemy = CF.sideOf(CF.otherSide(owner)).board;
    switch (card.effect) {
      case 'pingUnit':
        return { needsTarget: card.type === 'spell' || enemy.length > 0, targets: enemy, description: 'Choose an enemy unit.' };
      case 'damage2':
      case 'damage3':
      case 'damage2heal2':
      case 'preparedStrike':
      case 'sacrificeBlast':
      case 'destroyUnit':
        return { needsTarget: true, targets: enemy, description: 'Choose an enemy unit.' };
      case 'destroyDamaged':
      case 'finishWeak':
        return { needsTarget: true, targets: enemy.filter(u => u.currentHealth < u.maxHealth), description: 'Choose a damaged enemy unit.' };
      case 'buffFriendly':
      case 'shieldOther':
        return { needsTarget: friendly.length > 0, targets: friendly, description: 'Choose another friendly unit.' };
      case 'buff2':
      case 'heal3':
      case 'heal4':
      case 'giveShield':
      case 'packInstinct':
        return { needsTarget: true, targets: friendly, description: 'Choose a friendly unit.' };
      case 'giveHealth2':
        return { needsTarget: friendly.length > 0, targets: friendly, description: 'Choose another friendly unit.' };
      default:
        return { needsTarget: false, targets: [], description: '' };
    }
  }

  function isCardPlayable(owner, card) {
    const side = CF.sideOf(owner);
    if (side.cardsPlayed >= MAX_CARDS_PER_TURN) return false;
    if (effectiveCost(card, owner) > side.mana) return false;
    if (card.type === 'unit' && side.board.length >= MAX_BOARD) return false;
    if (card.type === 'relic' && side.relics.length >= MAX_RELICS) return false;
    if (card.effect === 'buffDamaged' && !side.board.some(unit => unit.currentHealth < unit.maxHealth)) return false;
    if (card.effect === 'sacrificeBlast' && (!side.board.length || !CF.sideOf(CF.otherSide(owner)).board.length)) return false;
    const targetInfo = getTargetInfo(card, owner);
    if (targetInfo.needsTarget && !targetInfo.targets.length) return false;
    return true;
  }

  function handUnavailableReason(owner, card) {
    const side = CF.sideOf(owner);
    if (ctx.state.turn !== owner || ctx.state.phase !== 'main') return 'Not your action window';
    if (ctx.state.targetMode) return 'Finish target selection';
    if (ctx.state.swapMode) return '';
    if (side.cardsPlayed >= MAX_CARDS_PER_TURN) return '2-card limit reached';
    if (effectiveCost(card, owner) > side.mana) return `Needs ${effectiveCost(card, owner) - side.mana} more mana`;
    if (card.type === 'unit' && side.board.length >= MAX_BOARD) return 'Board is full';
    if (card.type === 'relic' && side.relics.length >= MAX_RELICS) return 'Relic row is full';
    if (card.effect === 'buffDamaged' && !side.board.some(unit => unit.currentHealth < unit.maxHealth)) return 'Needs a damaged ally';
    if (card.effect === 'sacrificeBlast' && (!side.board.length || !CF.sideOf(CF.otherSide(owner)).board.length)) return 'Needs units on both boards';
    const targetInfo = getTargetInfo(card, owner);
    if (targetInfo.needsTarget && !targetInfo.targets.length) return 'No valid target';
    return '';
  }

  function handleUnitTarget(unit, owner) {
    if (ctx.state.targetMode) {
      if (!ctx.state.targetMode.validUids.has(unit.uid)) return;
      const card = ctx.state.player.hand.find(c => c.uid === ctx.state.targetMode.cardUid);
      if (!card) return;
      playCard('player', card, unit);
      return;
    }

    if (ctx.state.turn === 'player' && ctx.state.phase === 'main' && owner === 'player' && !ctx.state.player.combatUsed && canAttack(unit)) {
      CF.saveUndo(ctx.state.selectedAttackers.has(unit.uid) ? 'attacker removal' : 'attacker selection');
      if (ctx.state.selectedAttackers.has(unit.uid)) ctx.state.selectedAttackers.delete(unit.uid);
      else ctx.state.selectedAttackers.add(unit.uid);
      CF.render();
      return;
    }

    if (ctx.state.turn === 'enemy' && ctx.state.phase === 'blocking') {
      if (owner === 'player') {
        if (unit.exhausted) return;
        CF.saveUndo('blocker selection');
        ctx.state.selectedBlocker = ctx.state.selectedBlocker === unit.uid ? null : unit.uid;
        CF.render();
        if (ctx.state.selectedBlocker) scrollZoneIntoView(refs.enemyBoard);
        return;
      }
      if (owner === 'enemy' && ctx.state.selectedBlocker && ctx.state.aiAttackers.some(a => a.uid === unit.uid)) {
        assignBlock(ctx.state.selectedBlocker, unit.uid);
      }
    }
  }

  function blockTargetReason(attacker) {
    if (!ctx.state.aiAttackers.some(unit => unit.uid === attacker.uid)) return 'Not attacking';
    if (!ctx.state.selectedBlocker) return '';
    const blocker = ctx.state.player.board.find(unit => unit.uid === ctx.state.selectedBlocker);
    if (!blocker) return '';
    if (attacker.keywords.includes('Flying') && !blocker.keywords.includes('Flying')) return 'Needs a Flying blocker';
    const blockedAttackerUids = new Set([...ctx.state.blockAssignments.values()]);
    const unblockedGuardExists = ctx.state.aiAttackers.some(unit => unit.keywords.includes('Guard') && !blockedAttackerUids.has(unit.uid));
    if (unblockedGuardExists && !attacker.keywords.includes('Guard')) return 'Block Guard first';
    return '';
  }

  function assignBlock(blockerUid, attackerUid) {
    const blocker = ctx.state.player.board.find(u => u.uid === blockerUid);
    const attacker = ctx.state.aiAttackers.find(u => u.uid === attackerUid);
    if (!blocker || !attacker) return;
    if (attacker.keywords.includes('Flying') && !blocker.keywords.includes('Flying')) {
      CF.addLog('Only a Flying unit can block a Flying attacker.', 'bad');
      CF.render();
      return;
    }

    const guardAttackers = ctx.state.aiAttackers.filter(a => a.keywords.includes('Guard'));
    const blockedAttackerUids = new Set([...ctx.state.blockAssignments.values()]);
    const unblockedGuardExists = guardAttackers.some(g => !blockedAttackerUids.has(g.uid));
    if (unblockedGuardExists && !attacker.keywords.includes('Guard')) {
      CF.addLog('A Guard attacker must be blocked before other attackers.', 'bad');
      CF.render();
      return;
    }

    CF.saveUndo(ctx.state.blockAssignments.get(blockerUid) === attackerUid ? 'block removal' : 'block assignment');

    if (ctx.state.blockAssignments.get(blockerUid) === attackerUid) {
      ctx.state.blockAssignments.delete(blockerUid);
      ctx.state.selectedBlocker = null;
      CF.addLog(`${blocker.name} is no longer blocking ${attacker.name}.`, 'info', `${attacker.name} will now deal ${cardAttack(attacker, true, 'enemy')} damage to you unless another blocker is assigned.`);
      CF.render();
      scrollZoneIntoView(refs.playerBoard);
      return;
    }

    for (const [bUid, aUid] of [...ctx.state.blockAssignments.entries()]) {
      if (bUid === blockerUid || aUid === attackerUid) ctx.state.blockAssignments.delete(bUid);
    }
    ctx.state.blockAssignments.set(blockerUid, attackerUid);
    ctx.state.selectedBlocker = null;
    CF.addLog(`${blocker.name} will block ${attacker.name}.`, 'info', 'A blocked attacker deals no damage to you. The two units deal damage to each other at the same time.');
    CF.render();
    scrollZoneIntoView(refs.playerBoard);
  }

  function playCard(owner, card, target) {
    const side = CF.sideOf(owner);
    const index = side.hand.findIndex(c => c.uid === card.uid);
    const cost = effectiveCost(card, owner);
    if (index < 0 || side.mana < cost || side.cardsPlayed >= MAX_CARDS_PER_TURN) return false;
    if (owner === 'player') CF.saveUndo(`playing ${card.name}`);

    const champ = CF.championDef(owner);
    const playNumber = side.cardsPlayed + 1;
    let spellBonus = 0;
    const willDealDamage = isDamageCard(card) && !(card.effect === 'pingUnit' && !target) && !(['aoe1','aoe2','aoe3'].includes(card.effect) && CF.sideOf(CF.otherSide(owner)).board.length === 0);
    if (willDealDamage && side.championInPlay && champ.abilityKey === 'flameDamage' && !side.championDamageUsed) {
      spellBonus += champ.abilityMag;
      side.championDamageUsed = true;
      CF.addLog(`${champ.name} empowered ${card.name}.`, owner === 'player' ? 'good' : 'bad', `The first damage card each turn deals ${champ.abilityMag} extra damage while ${champ.name} is on the battlefield.`);
    }
    if (isDamageSpell(card) && side.relics.some(relic => relic.effect === 'firstSpellBonus') && !side.firstSpellBonusUsed) {
      spellBonus = 1;
      side.firstSpellBonusUsed = true;
      CF.addLog(`Ember Shrine empowered ${card.name}.`, owner === 'player' ? 'good' : 'bad', 'The first damage spell this turn deals 1 extra damage.');
    }

    side.mana -= cost;
    side.hand.splice(index, 1);
    side.cardsPlayed += 1;
    ctx.state.targetMode = null;
    ctx.state.swapMode = false;

    if (card.type === 'unit') {
      card.summoningSick = !card.keywords.includes('Charge') && !card.keywords.includes('Rush');
      card.rushLocked = card.keywords.includes('Rush');
      side.board.push(card);
      if (side.championInPlay && champ.abilityKey === 'wildHealth' && !side.championUnitUsed) {
        side.championUnitUsed = true;
        gainUnitHealth(card, champ.abilityMag, owner, { name: champ.name });
      }
      CF.addLog(`${CF.controllerLabel(owner)} played ${card.name} as card ${playNumber} of ${MAX_CARDS_PER_TURN}.`, owner === 'player' ? 'good' : 'bad');
      resolveEffect(owner, card, target, { playNumber, spellBonus });
    } else if (card.type === 'relic') {
      side.relics.push(card);
      CF.addLog(`${CF.controllerLabel(owner)} played ${card.name} as card ${playNumber} of ${MAX_CARDS_PER_TURN}.`, owner === 'player' ? 'good' : 'bad');
    } else {
      CF.addLog(`${CF.controllerLabel(owner)} cast ${card.name} as card ${playNumber} of ${MAX_CARDS_PER_TURN}.`, owner === 'player' ? 'good' : 'bad', 'Spells resolve once, then move to the discard pile.');
      resolveEffect(owner, card, target, { playNumber, spellBonus });
      side.graveyard.push(card);
    }

    removeDeadUnits();
    checkGameOver();
    CF.render();
    return true;
  }

  function resolveEffect(owner, card, target, context = {}) {
    const playNumber = context.playNumber || CF.sideOf(owner).cardsPlayed || 1;
    const spellBonus = context.spellBonus || 0;
    const friendly = CF.sideOf(owner);
    const enemy = CF.sideOf(CF.otherSide(owner));
    switch (card.effect) {
      case 'pingHero':
        const pingDamage = damageHero(CF.otherSide(owner), 1 + spellBonus, owner, card.name);
        CF.addLog(`${card.name} dealt ${pingDamage} damage to ${CF.controllerLabel(CF.otherSide(owner)).toLowerCase()}.`, owner === 'player' ? 'good' : 'bad');
        break;
      case 'pingUnit':
        if (target) dealDamage(target, 1 + spellBonus, owner, card);
        break;
      case 'damage2':
        if (target) dealDamage(target, 2 + spellBonus, owner, card);
        break;
      case 'damage3':
        if (target) dealDamage(target, 3 + spellBonus, owner, card);
        break;
      case 'aoe1':
        enemy.board.forEach(unit => dealDamage(unit, 1 + spellBonus, owner, card));
        break;
      case 'aoe2':
        enemy.board.forEach(unit => dealDamage(unit, 2 + spellBonus, owner, card));
        break;
      case 'aoe3':
        enemy.board.forEach(unit => dealDamage(unit, 3 + spellBonus, owner, card));
        break;
      case 'buffFriendly':
        if (target) buffUnit(target, 1, 1, owner, card);
        break;
      case 'buff2':
        if (target) buffUnit(target, 2, 2, owner, card);
        break;
      case 'buffAll1':
        friendly.board.forEach(unit => buffUnit(unit, 1, 1, owner, card));
        break;
      case 'heal3':
        if (target) {
          const old = target.currentHealth;
          target.currentHealth = Math.min(target.maxHealth, target.currentHealth + 3);
          CF.addLog(`${card.name} restored ${target.currentHealth - old} health to ${target.name}.`);
        }
        break;
      case 'heal4':
        if (target) {
          const old = target.currentHealth;
          target.currentHealth = Math.min(target.maxHealth, target.currentHealth + 4);
          CF.addLog(`${card.name} restored ${target.currentHealth - old} health to ${target.name}.`);
        }
        break;
      case 'healHero2':
        friendly.life = Math.min(20, friendly.life + 2);
        break;
      case 'giveShield':
        if (target) target.shield = true;
        break;
      case 'selfDamage1':
        friendly.life -= 1;
        break;
      case 'selfDamage2':
        friendly.life -= 2;
        break;
      case 'destroyUnit':
        if (target) {
          target.lastDamageSource = { type: 'destroy', sourceName: card.name, amount: 0 };
          target.currentHealth = 0;
        }
        break;
      case 'destroyDamaged':
        if (target) {
          target.lastDamageSource = { type: 'destroy', sourceName: card.name, amount: 0 };
          target.currentHealth = 0;
        }
        break;
      case 'damage2heal2':
        if (target) {
          dealDamage(target, 2 + spellBonus, owner, card);
          friendly.life = Math.min(20, friendly.life + 2);
        }
        break;
      case 'preparedStrike':
        if (target) {
          const amount = (playNumber === 2 ? 4 : 2) + spellBonus;
          dealDamage(target, amount, owner, card);
          if (playNumber === 2) CF.addLog(`${card.name} received its second-card bonus.`, owner === 'player' ? 'good' : 'bad');
        }
        break;
      case 'finishWeak':
        if (target) dealDamage(target, 4 + spellBonus, owner, card);
        break;
      case 'giveHealth2':
        if (target) gainUnitHealth(target, 2, owner, card);
        break;
      case 'packInstinct':
        if (target) {
          const amount = playNumber === 1 ? 2 : 1;
          buffUnit(target, amount, amount, owner, card);
          if (playNumber === 1) CF.addLog(`${card.name} received its first-card bonus.`, owner === 'player' ? 'good' : 'bad');
        }
        break;
      case 'shieldIfBigFriend': {
        const hasBigFriend = friendly.board.some(unit => unit.uid !== card.uid && (unit.currentHealth >= 5 || unit.maxHealth >= 5));
        if (hasBigFriend) {
          card.shield = true;
          CF.addLog(`${card.name} gained Shield from a high-Health ally.`, owner === 'player' ? 'good' : 'bad');
        }
        break;
      }
      case 'shieldOther':
        if (target) {
          target.shield = true;
          CF.addLog(`${card.name} gave ${target.name} Shield.`, owner === 'player' ? 'good' : 'bad');
        }
        break;
      case 'buffDamaged': {
        const damaged = friendly.board.filter(unit => unit.currentHealth < unit.maxHealth);
        damaged.forEach(unit => buffUnit(unit, 1, 2, owner, card));
        CF.addLog(`${card.name} strengthened ${damaged.length} damaged unit${damaged.length === 1 ? '' : 's'}.`, owner === 'player' ? 'good' : 'bad');
        break;
      }
      case 'sacrificeBlast': {
        const sacrifice = [...friendly.board].sort((a, b) => cardAttack(a, false, owner) - cardAttack(b, false, owner) || a.currentHealth - b.currentHealth)[0];
        if (sacrifice && target) {
          sacrifice.lastDamageSource = { type: 'destroy', sourceName: card.name, amount: 0 };
          sacrifice.currentHealth = 0;
          CF.addLog(`${card.name} sacrificed ${sacrifice.name}.`, owner === 'player' ? 'bad' : 'good', 'The weakest friendly unit is destroyed before the damage is dealt.');
          removeDeadUnits();
          dealDamage(target, 4 + spellBonus, owner, card);
        }
        break;
      }
      case 'refreshHandHurt2': {
        const discarded = [...friendly.hand];
        friendly.hand = [];
        friendly.graveyard.push(...discarded);
        CF.refillHand(owner, false);
        friendly.life -= 2;
        CF.addLog(`${card.name} replaced ${discarded.length} card${discarded.length === 1 ? '' : 's'} and dealt 2 damage to ${CF.controllerLabel(owner).toLowerCase()}.`, owner === 'player' ? 'bad' : 'good');
        break;
      }
    }
  }

  function gainUnitHealth(unit, amount, owner, sourceCard = null) {
    if (!unit || amount <= 0) return;
    unit.maxHealth += amount;
    unit.currentHealth += amount;
    CF.addLog(`${sourceCard ? sourceCard.name : 'An effect'} gave ${unit.name} +${amount} Health.`, owner === 'player' ? 'good' : 'bad');
    if (unit.effect === 'growOnHealth') {
      unit.bonusAttack += 1;
      CF.addLog(`${unit.name} gained +1 Attack from its growth ability.`, owner === 'player' ? 'good' : 'bad');
    }
    const side = CF.sideOf(owner);
    if (side.relics.some(relic => relic.effect === 'healthGainAttack') && !side.healthGainTriggerUsed) {
      side.healthGainTriggerUsed = true;
      unit.bonusAttack += 1;
      CF.addLog(`Living Grove gave ${unit.name} +1 Attack.`, owner === 'player' ? 'good' : 'bad', 'This was the first friendly Health gain this turn.');
    }
  }

  function buffUnit(unit, attack, health, owner = null, sourceCard = null) {
    unit.bonusAttack += attack;
    if (health > 0) {
      if (owner) gainUnitHealth(unit, health, owner, sourceCard);
      else {
        unit.maxHealth += health;
        unit.currentHealth += health;
      }
    }
  }

  function dealDamage(unit, amount, sourceOwner, sourceCard = null) {
    if (unit.shield) {
      unit.shield = false;
      CF.addLog(`${unit.name}'s Shield prevented the damage.`, 'info');
      return 0;
    }
    unit.currentHealth -= amount;
    unit.lastDamageSource = { type: sourceCard ? 'card' : 'damage', sourceName: sourceCard ? sourceCard.name : 'damage', amount };
    CF.addLog(`${sourceCard ? sourceCard.name : 'Combat'} dealt ${amount} damage to ${unit.name}.`, sourceOwner === 'player' ? 'good' : 'bad', `${unit.name} is now at ${Math.max(0, unit.currentHealth)}/${unit.maxHealth} health.`);
    return amount;
  }

  function removeDeadUnits() {
    ['player', 'enemy'].forEach(owner => {
      const side = CF.sideOf(owner);
      const champ = CF.championDef(owner);
      const dead = side.board.filter(u => u.currentHealth <= 0);
      side.board = side.board.filter(u => u.currentHealth > 0);
      dead.forEach(unit => {
        if (unit.isChampion) CF.returnChampionToSlot(owner, unit); else side.graveyard.push(unit);
        const cause = unit.lastDamageSource;
        let reason = 'Its health reached 0.';
        let headline = `${unit.name} was destroyed.`;
        if (cause?.type === 'combat') {
          headline = `${unit.name} was destroyed by ${cause.sourceName}.`;
          reason = `${cause.sourceName} dealt ${cause.amount} combat damage, reducing ${unit.name} to 0 health.`;
        } else if (cause?.type === 'destroy') {
          headline = `${unit.name} was destroyed by ${cause.sourceName}.`;
          reason = `${cause.sourceName} destroys a unit directly, regardless of its remaining health.`;
        } else if (cause?.sourceName) {
          headline = `${unit.name} was destroyed by ${cause.sourceName}.`;
          reason = `${cause.sourceName} dealt ${cause.amount} damage, reducing ${unit.name} to 0 health.`;
        }
        CF.addLog(headline, owner === 'player' ? 'bad' : 'good', reason);
        if (unit.deathEffect === 'deathPing') {
          const dealt = damageHero(CF.otherSide(owner), 1, owner, unit.name);
          CF.addLog(`${unit.name} dealt ${dealt} damage when destroyed.`, owner === 'player' ? 'good' : 'bad');
        }
        if (unit.deathEffect === 'deathPing2') {
          const dealt = damageHero(CF.otherSide(owner), 2, owner, unit.name);
          CF.addLog(`${unit.name} dealt ${dealt} damage when destroyed.`, owner === 'player' ? 'good' : 'bad');
        }
        if (side.championInPlay && champ.abilityKey === 'shadowDeath' && !side.championDeathUsed) {
          side.championDeathUsed = true;
          const dealt = damageHero(CF.otherSide(owner), champ.abilityMag, owner, champ.name);
          CF.addLog(`${champ.name} dealt ${dealt} damage after ${unit.name} was destroyed.`, owner === 'player' ? 'good' : 'bad');
        }
        side.board.filter(card => card.effect === 'growOnFriendlyDeath').forEach(collector => {
          buffUnit(collector, 1, 1, owner, unit);
          CF.addLog(`${collector.name} gained +1/+1 when ${unit.name} was destroyed.`, owner === 'player' ? 'good' : 'bad');
        });
        if (side.relics.some(r => r.effect === 'firstDeathPing') && !side.deathTriggerUsed) {
          side.deathTriggerUsed = true;
          const dealt = damageHero(CF.otherSide(owner), 1, owner, 'Bone Altar');
          CF.addLog(`Bone Altar dealt ${dealt} damage after ${unit.name} was destroyed.`, owner === 'player' ? 'good' : 'bad');
        }
        if (side.relics.some(r => r.effect === 'deathHeal')) {
          side.life = Math.min(20, side.life + 1);
          CF.addLog(`Soul Lantern restored 1 life.`, owner === 'player' ? 'good' : 'bad');
        }
      });
    });
  }

  function beginPlayerAttack() {
    if (ctx.state.turn !== 'player' || ctx.state.phase !== 'main' || ctx.state.targetMode || ctx.state.player.combatUsed) return;
    ctx.state.swapMode = false;
    const attackers = ctx.state.player.board.filter(u => ctx.state.selectedAttackers.has(u.uid) && canAttack(u));
    if (!attackers.length) {
      endPlayerTurn();
      return;
    }
    CF.clearUndo();
    ctx.state.phase = 'resolving';
    CF.render();
    attackers.forEach(u => u.exhausted = true);
    ctx.state.selectedAttackers.clear();
    const blocks = aiChooseBlocks(attackers, ctx.state.enemy.board);
    resolveCombat('player', attackers, blocks, () => {
      if (!ctx.state.gameOver) {
        ctx.state.player.combatUsed = true;
        ctx.state.phase = 'main';
        CF.addLog('Your attack step is complete.', 'info', 'You may still play cards, replace a card, or end your turn. You cannot attack again this turn.');
        CF.render();
        scrollZoneIntoView(refs.playerHand);
      }
    });
  }

  function aiChooseBlocks(attackers, defenders) {
    const blocks = new Map();
    const available = [...defenders].filter(u => !u.exhausted);
    const sortedAttackers = [...attackers].sort((a, b) => {
      const guardDiff = Number(b.keywords.includes('Guard')) - Number(a.keywords.includes('Guard'));
      if (guardDiff) return guardDiff;
      return cardAttack(b, true, 'player') - cardAttack(a, true, 'player');
    });

    for (const attacker of sortedAttackers) {
      const valid = available.filter(d => !attacker.keywords.includes('Flying') || d.keywords.includes('Flying'));
      if (!valid.length) continue;
      valid.sort((a, b) => {
        const aSurvives = a.currentHealth > cardAttack(attacker, true, 'player') ? 1 : 0;
        const bSurvives = b.currentHealth > cardAttack(attacker, true, 'player') ? 1 : 0;
        if (aSurvives !== bSurvives) return bSurvives - aSurvives;
        return cardAttack(a) - cardAttack(b);
      });
      const blocker = valid[0];
      blocks.set(blocker.uid, attacker.uid);
      available.splice(available.indexOf(blocker), 1);
    }
    return blocks;
  }

  function triggerCombatSurvival(owner, unit) {
    if (!unit || unit.currentHealth <= 0) return;
    const side = CF.sideOf(owner);
    if (unit.effect === 'growAfterSurvive') {
      unit.bonusAttack += 1;
      CF.addLog(`${unit.name} survived combat and gained +1 Attack.`, owner === 'player' ? 'good' : 'bad');
    }
    if (side.relics.some(relic => relic.effect === 'surviveHeal') && !side.surviveTriggerUsed) {
      side.surviveTriggerUsed = true;
      const before = side.life;
      side.life = Math.min(20, side.life + 1);
      CF.addLog(`Fortress Bell restored ${side.life - before} life after ${unit.name} survived combat.`, owner === 'player' ? 'good' : 'bad');
    }
  }

  function resolveCombat(attackerOwner, attackers, blockMap, onComplete) {
    const defenderOwner = CF.otherSide(attackerOwner);
    const attackerSide = CF.sideOf(attackerOwner);
    const defenderSide = CF.sideOf(defenderOwner);
    const defenderLifeBefore = defenderSide.life;
    let directHeroDamage = 0;
    const reportRows = [];

    for (const attacker of attackers) {
      const blockerEntry = [...blockMap.entries()].find(([, aUid]) => aUid === attacker.uid);
      const attackerPower = cardAttack(attacker, true, attackerOwner);
      if (blockerEntry) {
        const blocker = defenderSide.board.find(u => u.uid === blockerEntry[0]);
        if (!blocker) continue;
        const blockerPower = cardAttack(blocker, false, defenderOwner);
        const attackerShielded = !!attacker.shield;
        const blockerShielded = !!blocker.shield;
        const attackerHealthBefore = attacker.currentHealth;
        const blockerHealthBefore = blocker.currentHealth;
        const dealtToBlocker = dealCombatDamage(blocker, attackerPower, attacker);
        const dealtToAttacker = dealCombatDamage(attacker, blockerPower, blocker);
        triggerCombatSurvival(attackerOwner, attacker);
        triggerCombatSurvival(defenderOwner, blocker);
        CF.addLog(`${attacker.name} fought ${blocker.name}.`, attackerOwner === 'player' ? 'good' : 'bad', `${attacker.name} dealt ${dealtToBlocker} damage; ${blocker.name} dealt ${dealtToAttacker} damage. Combat damage happens simultaneously.`);
        if (attacker.keywords.includes('Drain') && dealtToBlocker > 0) attackerSide.life = Math.min(20, attackerSide.life + dealtToBlocker);
        if (blocker.keywords.includes('Drain') && dealtToAttacker > 0) defenderSide.life = Math.min(20, defenderSide.life + dealtToAttacker);
        reportRows.push({
          type: 'blocked',
          attackerName: attacker.name,
          attackerPower,
          attackerFaction: attacker.faction,
          attackerCost: attacker.cost,
          attackerHealthBefore,
          attackerDrain: attacker.keywords.includes('Drain'),
          blockerFaction: blocker.faction,
          blockerCost: blocker.cost,
          blockerHealthBefore,
          blockerDrain: blocker.keywords.includes('Drain'),
          attackerHealthAfter: attacker.currentHealth,
          attackerMaxHealth: attacker.maxHealth,
          attackerShielded,
          blockerName: blocker.name,
          blockerPower,
          blockerHealthAfter: blocker.currentHealth,
          blockerMaxHealth: blocker.maxHealth,
          blockerShielded,
          dealtToBlocker,
          dealtToAttacker
        });
      } else {
        const rushLocked = attacker.keywords.includes('Rush') && attacker.rushLocked;
        const lifeBeforeHit = defenderSide.life;
        const dealtToHero = rushLocked ? 0 : damageHero(defenderOwner, attackerPower, attackerOwner, attacker.name);
        directHeroDamage += dealtToHero;
        CF.addLog(rushLocked ? `${attacker.name} has Rush and cannot damage ${CF.controllerLabel(defenderOwner).toLowerCase()} the turn it entered play.` : `${attacker.name} dealt ${dealtToHero} damage to ${CF.controllerLabel(defenderOwner).toLowerCase()}.`, attackerOwner === 'player' ? 'good' : 'bad', rushLocked ? 'Rush units can attack immediately but cannot hit the opposing player on their entry turn.' : dealtToHero < attackerPower ? 'A Champion ability prevented some damage. The attacker was otherwise unblocked.' : 'It was not assigned a blocker, so all of its Attack damaged the defending player.');
        if (attacker.keywords.includes('Drain') && dealtToHero > 0) attackerSide.life = Math.min(20, attackerSide.life + dealtToHero);
        reportRows.push({ type: 'unblocked', attackerName: attacker.name, attackerPower, attackerFaction: attacker.faction, attackerCost: attacker.cost, attackerHealth: attacker.currentHealth, attackerMaxHealth: attacker.maxHealth, attackerShielded: !!attacker.shield, attackerDrain: attacker.keywords.includes('Drain'), dealtToHero, lifeBefore: lifeBeforeHit, lifeAfter: defenderSide.life });
      }
    }
    removeDeadUnits();
    const netLifeLoss = Math.max(0, defenderLifeBefore - defenderSide.life);
    ctx.state.lastCombatReport = {
      attackerOwner,
      defenderOwner,
      defenderLifeBefore,
      defenderLifeAfter: defenderSide.life,
      directHeroDamage,
      netLifeLoss,
      rows: reportRows
    };
    const casualties = reportRows.filter(row => row.type === 'blocked' && (row.attackerHealthAfter <= 0 || row.blockerHealthAfter <= 0)).length;
    CF.addLog(`Combat ended: ${directHeroDamage} damage reached ${CF.controllerLabel(defenderOwner).toLowerCase()}.`, attackerOwner === 'player' ? 'good' : 'bad', `${reportRows.length} attacker${reportRows.length === 1 ? '' : 's'}, ${reportRows.filter(r => r.type === 'blocked').length} blocked, ${casualties} combat pair${casualties === 1 ? '' : 's'} with a destroyed unit. Final life reflects Drain or other healing.`);
    const finishCombat = () => {
      checkGameOver();
      CF.render();

      if (!ctx.state.gameOver && attackerOwner === 'enemy' && (directHeroDamage > 0 || casualties > 0)) {
        ctx.state.pendingCombatReport = true;
        window.setTimeout(() => {
          if (!ctx.state.pendingCombatReport) return;
          CF.renderCombatReport();
          refs.combatReportOverlay.classList.add('show');
        }, 100);
      }
      if (onComplete) onComplete();
    };
    CF.playClashSequence(ctx.state.lastCombatReport, finishCombat);
  }

  function dealCombatDamage(unit, amount, sourceUnit) {
    if (unit.shield) {
      unit.shield = false;
      unit.lastDamageSource = null;
      CF.addLog(`${unit.name}'s Shield prevented ${amount} combat damage from ${sourceUnit.name}.`, 'info', 'Shield prevents the entire next instance of damage, then disappears.');
      return 0;
    }
    unit.currentHealth -= amount;
    unit.lastDamageSource = { type: 'combat', sourceName: sourceUnit.name, amount };
    return amount;
  }
  function resolveEndTurnEffects(who) {
    const side = CF.sideOf(who);
    if (side.cardsPlayed === 1) {
      side.board.filter(unit => unit.effect === 'shieldIfOneCard').forEach(unit => {
        if (!unit.shield) {
          unit.shield = true;
          CF.addLog(`${unit.name} gained Shield because only 1 card was played.`, who === 'player' ? 'good' : 'bad');
        }
      });
    }
  }

  function endPlayerTurn() {
    if (ctx.state.gameOver) return;
    CF.clearUndo();
    ctx.state.swapMode = false;
    resolveEndTurnEffects('player');
    CF.refillHand('player');
    ctx.state.phase = 'waiting';
    CF.render();
    window.setTimeout(() => CF.startTurn('enemy'), 450);
  }

  function endEnemyTurn() {
    if (ctx.state.gameOver) return;
    CF.clearUndo();
    resolveEndTurnEffects('enemy');
    CF.refillHand('enemy');
    ctx.state.phase = 'waiting';
    CF.render();
    window.setTimeout(() => CF.startTurn('player'), 450);
  }

  function scoreAiCardBase(card) {
    let score = card.cost * 0.7;
    if (card.type === 'relic') score += 1;
    return score;
  }

  function scoreAiCard(card) {
    const side = ctx.state.enemy;
    let score = scoreAiCardBase(card);
    const condition = getCardCondition(card, 'enemy');
    if (condition?.active) score += 4;
    if (card.effect === 'growOnFriendlyDeath' && side.cardsPlayed === 0) score += 3;
    if (card.effect === 'sacrificeBlast' && side.board.some(unit => unit.deathEffect)) score += 4;
    if (card.effect === 'shieldIfOneCard' && side.cardsPlayed === 0) score += 1.5;
    return score;
  }

  function aiMainPhase() {
    if (ctx.state.gameOver || ctx.state.turn !== 'enemy') return;
    CF.aiConsiderChampion();
    let safety = 8;
    while (safety-- > 0 && ctx.state.enemy.cardsPlayed < MAX_CARDS_PER_TURN) {
      const playable = ctx.state.enemy.hand.filter(card => isCardPlayable('enemy', card));
      if (!playable.length) {
        if (!ctx.state.enemy.swapUsed && ctx.state.enemy.hand.length) {
          const replacement = [...ctx.state.enemy.hand].sort((a, b) => b.cost - a.cost)[0];
          CF.replaceCard('enemy', replacement.uid, true, true);
          continue;
        }
        break;
      }
      playable.sort((a, b) => scoreAiCard(b) - scoreAiCard(a));
      const card = playable[0];
      const info = getTargetInfo(card, 'enemy');
      const target = info.needsTarget ? chooseAiTarget(card, info.targets) : null;
      if (!playCard('enemy', card, target)) break;
    }
    window.setTimeout(aiDeclareAttackers, 500);
  }

  function chooseAiTarget(card, targets) {
    if (!targets.length) return null;
    switch (card.effect) {
      case 'damage2':
      case 'damage3':
      case 'damage2heal2':
      case 'preparedStrike':
      case 'finishWeak':
      case 'sacrificeBlast':
      case 'pingUnit':
      case 'destroyUnit':
      case 'destroyDamaged':
        return [...targets].sort((a,b) => cardAttack(b) - cardAttack(a))[0];
      case 'buffFriendly':
      case 'buff2':
      case 'giveShield':
      case 'giveHealth2':
      case 'packInstinct':
      case 'shieldOther':
        return [...targets].sort((a,b) => cardAttack(b) - cardAttack(a))[0];
      case 'heal3':
      case 'heal4':
        return [...targets].sort((a,b) => (b.maxHealth-b.currentHealth) - (a.maxHealth-a.currentHealth))[0];
      default:
        return targets[0];
    }
  }

  function aiDeclareAttackers() {
    if (ctx.state.gameOver || ctx.state.turn !== 'enemy') return;
    ctx.state.aiAttackers = ctx.state.enemy.board.filter(canAttack);
    ctx.state.aiAttackers.forEach(u => u.exhausted = true);
    if (!ctx.state.aiAttackers.length) {
      CF.addLog('Enemy ended the turn without attacking.', 'info');
      window.setTimeout(endEnemyTurn, 450);
      return;
    }
    ctx.state.phase = 'blocking';
    CF.addLog(`Enemy attacked with ${ctx.state.aiAttackers.length} unit${ctx.state.aiAttackers.length === 1 ? '' : 's'}.`, 'bad');
    CF.render();
  }

  function resolvePlayerBlocks() {
    if (ctx.state.turn !== 'enemy' || ctx.state.phase !== 'blocking') return;
    CF.clearUndo();
    ctx.state.phase = 'waiting';
    CF.render();
    resolveCombat('enemy', ctx.state.aiAttackers, ctx.state.blockAssignments, () => {
      if (!ctx.state.gameOver) window.setTimeout(endEnemyTurn, 450);
    });
  }

  function checkGameOver() {
    if (ctx.state.gameOver) return true;
    if (ctx.state.player.life <= 0 || ctx.state.enemy.life <= 0) {
      ctx.state.gameOver = true;
      const playerWon = ctx.state.enemy.life <= 0 && ctx.state.player.life > 0;
      const draw = ctx.state.enemy.life <= 0 && ctx.state.player.life <= 0;
      refs.gameOverTitle.textContent = draw ? 'Draw' : playerWon ? 'Victory' : 'Defeat';
      refs.gameOverText.textContent = draw ? 'Both players reached 0 life.' : playerWon ? 'You reduced the enemy to 0 life.' : 'The enemy reduced you to 0 life.';
      refs.gameOverOverlay.classList.add('show');
      CF.render();
      return true;
    }
    return false;
  }
  const api = {
    cardAttack, effectiveCost, isDamageCard, isDamageSpell, damageHero,
    getCardCondition, canAttack, usesCompactLayout, scrollZoneIntoView,
    scrollToTargets, handleHandCard, getTargetInfo, isCardPlayable,
    handUnavailableReason, handleUnitTarget, blockTargetReason, assignBlock,
    playCard, resolveEffect, gainUnitHealth, buffUnit, dealDamage,
    removeDeadUnits, beginPlayerAttack, aiChooseBlocks, triggerCombatSurvival,
    resolveCombat, dealCombatDamage, resolveEndTurnEffects, endPlayerTurn,
    endEnemyTurn, scoreAiCardBase, scoreAiCard, aiMainPhase, chooseAiTarget,
    aiDeclareAttackers, resolvePlayerBlocks, checkGameOver
  };
  Object.assign(CF, api);
  return api;
  };
})();
