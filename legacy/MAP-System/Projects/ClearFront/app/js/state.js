(() => {
  'use strict';
  const CF = (window.CF = window.CF || {});
  const { MAX_BOARD, MAX_CARDS_PER_TURN, STARTING_HAND, HAND_LIMIT, CARD_LIBRARY, DECKS, FACTION_POOLS } = CF;

  // Mutable game state stays declared once in app/index.html's inline script
  // (DEC-CF-004). `ctx` is the shared-state contract handed in by the host:
  // accessor properties (getter+setter over the host's `let` bindings) for
  // state, undoRecord, uidCounter, playerDeckChoice, enemyDeckChoice, plus
  // stable host bindings ($, refs). Reassignments like `ctx.state = ...`
  // write through to the host binding, so all files see the same objects.
  // Functions owned by other modules (checkGameOver/damageHero/aiMainPhase
  // in combat.js since TASK-214; render/playClashSequence/renderCombatReport
  // in render.js since TASK-215) are called via their window.CF-published
  // form, not through ctx.
  CF.installStateModule = (ctx) => {
  const { $, refs } = ctx;

  function buildDecklist(deckDef) {
    return [...FACTION_POOLS[deckDef.factions[0]], ...FACTION_POOLS[deckDef.factions[1]]];
  }

  function applyDeckIdentity() {
    const p = ctx.playerDeckChoice, e = ctx.enemyDeckChoice;
    const playerPortrait = $('playerPortrait'), enemyPortrait = $('enemyPortrait');
    playerPortrait.src = p.img; playerPortrait.alt = p.name;
    playerPortrait.style.setProperty('--deck-color', p.color);
    $('playerDeckName').textContent = p.name;
    $('playerDeckSub').textContent = `You \u00b7 ${p.factions.join(' & ')}`;
    enemyPortrait.src = e.img; enemyPortrait.alt = e.name;
    enemyPortrait.style.setProperty('--deck-color', e.color);
    $('enemyDeckName').textContent = e.name;
    $('enemyDeckSub').textContent = `AI \u00b7 ${e.factions.join(' & ')}`;
    const clashYou = $('clashPortraitYou'), clashFoe = $('clashPortraitFoe');
    clashYou.src = p.img; clashYou.style.setProperty('--deck-color', p.color);
    clashFoe.src = e.img; clashFoe.style.setProperty('--deck-color', e.color);
    document.documentElement.style.setProperty('--accent', p.color);
  }

  function showDeckSelect() {
    const grid = $('deckGrid');
    grid.innerHTML = '';
    DECKS.forEach(deck => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'deck-option';
      btn.style.setProperty('--deck-color', deck.color);
      btn.innerHTML = `<img src="${deck.img}" alt="" /><strong>${deck.name}</strong><span class="deck-factions">${deck.factions.join(' \u00b7 ')}</span><span class="deck-blurb">${deck.blurb}</span>`;
      btn.addEventListener('click', () => {
        ctx.playerDeckChoice = deck;
        const rivals = DECKS.filter(d => d.id !== deck.id);
        ctx.enemyDeckChoice = rivals[Math.floor(Math.random() * rivals.length)];
        $('deckSelectOverlay').classList.remove('show');
        resetGame();
      });
      grid.appendChild(btn);
    });
    $('deckSelectOverlay').classList.add('show');
  }


  function makeCard(id) {
    const base = CARD_LIBRARY[id];
    return {
      ...base,
      id,
      uid: ctx.uidCounter++,
      keywords: [...(base.keywords || [])],
      currentHealth: base.health ?? null,
      maxHealth: base.health ?? null,
      bonusAttack: 0,
      summoningSick: base.type === 'unit',
      exhausted: false,
      shield: (base.keywords || []).includes('Shield')
    };
  }

  function shuffle(array) {
    const a = [...array];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function createSide(decklist, champDef) {
    return {
      life: 20,
      maxMana: 0,
      mana: 0,
      deck: shuffle(decklist.map(makeCard)),
      hand: [],
      board: [],
      relics: [],
      graveyard: [],
      swapUsed: false,
      combatUsed: false,
      cardsPlayed: 0,
      firstSpellBonusUsed: false,
      healthGainTriggerUsed: false,
      deathTriggerUsed: false,
      surviveTriggerUsed: false,
      championCost: champDef.baseCost,
      championInPlay: false,
      championUid: null,
      championDamageUsed: false,
      championUnitUsed: false,
      championOrderReady: false,
      championDeathUsed: false
    };
  }

  function resetGame() {
    ctx.uidCounter = 1;
    ctx.undoRecord = null;
    ctx.state = {
      player: createSide(buildDecklist(ctx.playerDeckChoice), ctx.playerDeckChoice.champion),
      enemy: createSide(buildDecklist(ctx.enemyDeckChoice), ctx.enemyDeckChoice.champion),
      turn: 'player',
      phase: 'main',
      selectedAttackers: new Set(),
      aiAttackers: [],
      blockAssignments: new Map(),
      selectedBlocker: null,
      targetMode: null,
      gameOver: false,
      log: [],
      lastCombatReport: null,
      pendingCombatReport: false,
      swapMode: false
    };

    applyDeckIdentity();
    dealStartingHand('player');
    dealStartingHand('enemy');
    const firstPlayer = Math.random() < 0.5 ? 'player' : 'enemy';
    addLog(`New game started. ${ctx.playerDeckChoice.name} vs ${ctx.enemyDeckChoice.name}. ${firstPlayer === 'player' ? 'You go' : 'The enemy goes'} first.`, 'info');
    startTurn(firstPlayer);
  }

  function sideOf(who) { return ctx.state[who]; }
  function otherSide(who) { return who === 'player' ? 'enemy' : 'player'; }
  function controllerLabel(who) { return who === 'player' ? 'You' : 'Enemy'; }

  function championDef(who) {
    return (who === 'player' ? ctx.playerDeckChoice : ctx.enemyDeckChoice).champion;
  }

  function resetChampionTurnFlags(who) {
    const side = sideOf(who);
    side.championDamageUsed = false;
    side.championUnitUsed = false;
    side.championOrderReady = championDef(who).abilityKey === 'orderPrevent';
    side.championDeathUsed = false;
  }

  function championDeployReason(who) {
    const side = sideOf(who);
    const def = championDef(who);
    if (side.championInPlay) return 'Already on the battlefield';
    if (ctx.state.turn !== who || ctx.state.phase !== 'main') return 'Not your action window';
    if (ctx.state.targetMode) return 'Finish target selection';
    if (ctx.state.swapMode) return 'Finish card replacement';
    if (side.cardsPlayed >= MAX_CARDS_PER_TURN) return '2-card limit reached';
    if (side.board.length >= MAX_BOARD) return 'Board is full';
    if (side.mana < side.championCost) return `Needs ${side.championCost - side.mana} more mana`;
    return '';
  }

  function deployChampion(who) {
    const side = sideOf(who);
    const def = championDef(who);
    if (championDeployReason(who)) return false;
    if (who === 'player') saveUndo(`deploying ${def.name}`);
    side.mana -= side.championCost;
    side.cardsPlayed += 1;
    const unit = {
      id: def.id,
      uid: ctx.uidCounter++,
      name: def.name,
      type: 'unit',
      faction: def.faction,
      cost: side.championCost,
      text: def.abilityText,
      attack: def.attack,
      health: def.health,
      keywords: [...def.keywords],
      currentHealth: def.health,
      maxHealth: def.health,
      bonusAttack: 0,
      summoningSick: !def.keywords.includes('Charge') && !def.keywords.includes('Rush'),
      rushLocked: def.keywords.includes('Rush'),
      exhausted: false,
      shield: def.keywords.includes('Shield'),
      isChampion: true
    };
    side.board.push(unit);
    side.championInPlay = true;
    side.championUid = unit.uid;
    addLog(`${controllerLabel(who)} deployed ${def.name} as Champion.`, who === 'player' ? 'good' : 'bad', def.abilityText);
    CF.removeDeadUnits();
    CF.checkGameOver();
    CF.render();
    return true;
  }

  function returnChampionToSlot(who, unit) {
    const side = sideOf(who);
    side.championInPlay = false;
    side.championUid = null;
    side.championCost += 2;
    addLog(`${unit.name} returns to the Champion slot at ${side.championCost} mana.`, who === 'player' ? 'bad' : 'good', 'A destroyed Champion returns to its slot with its cost increased by 2.');
  }

  function saveUndo(label) {
    if (ctx.state.gameOver) return;
    ctx.undoRecord = { label, state: structuredClone(ctx.state), uidCounter: ctx.uidCounter };
  }

  function clearUndo() { ctx.undoRecord = null; }

  function canUndo() {
    return !!ctx.undoRecord && !ctx.state.gameOver && ((ctx.state.turn === 'player' && ctx.state.phase === 'main') || (ctx.state.turn === 'enemy' && ctx.state.phase === 'blocking'));
  }

  function undoLastAction() {
    if (!canUndo()) return;
    const label = ctx.undoRecord.label;
    ctx.state = ctx.undoRecord.state;
    ctx.uidCounter = ctx.undoRecord.uidCounter;
    ctx.undoRecord = null;
    refs.gameOverOverlay.classList.remove('show');
    refs.blockOverlay.classList.remove('show');
    refs.combatReportOverlay.classList.remove('show');
    addLog(`Undid ${label}.`, 'info');
    CF.render();
  }

  function aiConsiderChampion() {
    if (!championDeployReason('enemy')) deployChampion('enemy');
  }

  function addLog(text, tone = '', detail = '') {
    ctx.state.log.unshift({ text, tone, detail });
    ctx.state.log = ctx.state.log.slice(0, 60);
  }

  function dealStartingHand(who) {
    const side = sideOf(who);
    let oneCostIndex = -1;
    for (let i = side.deck.length - 1; i >= 0; i--) {
      if (side.deck[i].cost === 1) {
        oneCostIndex = i;
        break;
      }
    }
    if (oneCostIndex >= 0) side.hand.push(side.deck.splice(oneCostIndex, 1)[0]);
    while (side.hand.length < STARTING_HAND) {
      if (!drawCard(who, false)) break;
    }
  }

  function drawCard(who, logIt = true) {
    const side = sideOf(who);
    if (side.hand.length >= HAND_LIMIT) return false;
    if (!side.deck.length) {
      side.life -= 1;
      if (logIt) addLog(`${controllerLabel(who)} could not refill and took 1 fatigue damage.`, who === 'player' ? 'bad' : 'good');
      CF.checkGameOver();
      return false;
    }
    const card = side.deck.pop();
    side.hand.push(card);
    if (logIt) addLog(`${controllerLabel(who)} drew a card.`);
    return true;
  }

  function refillHand(who, logIt = true) {
    const side = sideOf(who);
    const before = side.hand.length;
    while (side.hand.length < HAND_LIMIT) {
      if (!drawCard(who, false)) break;
    }
    const drawn = side.hand.length - before;
    if (logIt && drawn > 0) {
      addLog(`${controllerLabel(who)} refilled ${drawn} card${drawn === 1 ? '' : 's'} to a ${side.hand.length}-card hand.`, 'info', 'Hands refill only when their owner ends a turn.');
    }
    return drawn;
  }

  function replaceCard(who, cardUid, markTurnSwap = true, logIt = true) {
    const side = sideOf(who);
    const index = side.hand.findIndex(card => card.uid === cardUid);
    if (index < 0 || (markTurnSwap && side.swapUsed)) return false;
    const [discarded] = side.hand.splice(index, 1);
    side.graveyard.push(discarded);
    const drew = drawCard(who, false);
    if (markTurnSwap) side.swapUsed = true;
    if (logIt) {
      addLog(`${controllerLabel(who)} replaced ${discarded.name}.`, who === 'player' ? 'info' : 'bad', drew ? 'The discarded card moved to the discard pile and a new card took its place.' : 'The discarded card moved to the discard pile, but the deck was empty.');
    }
    return true;
  }

  function startTurn(who) {
    if (ctx.state.gameOver) return;
    clearUndo();
    resetChampionTurnFlags(who);
    ctx.state.turn = who;
    ctx.state.phase = 'main';
    ctx.state.selectedAttackers.clear();
    ctx.state.aiAttackers = [];
    ctx.state.blockAssignments.clear();
    ctx.state.selectedBlocker = null;
    ctx.state.targetMode = null;
    ctx.state.swapMode = false;

    ['player', 'enemy'].forEach(key => {
      sideOf(key).deathTriggerUsed = false;
      sideOf(key).surviveTriggerUsed = false;
    });
    const side = sideOf(who);
    side.swapUsed = false;
    side.combatUsed = false;
    side.cardsPlayed = 0;
    side.firstSpellBonusUsed = false;
    side.healthGainTriggerUsed = false;
    side.deathTriggerUsed = false;
    side.surviveTriggerUsed = false;
    side.maxMana = Math.min(10, side.maxMana + 1);
    side.mana = side.maxMana;
    side.board.forEach(unit => {
      unit.exhausted = false;
      unit.summoningSick = false;
      unit.rushLocked = false;
    });

    side.relics.forEach(relic => {
      if (relic.effect === 'turnHeal') {
        side.life = Math.min(20, side.life + 1);
        addLog(`${relic.name} restored 1 life to ${controllerLabel(who).toLowerCase()}.`, who === 'player' ? 'good' : 'bad');
      }
      if (relic.effect === 'turnPing') {
        const relicDamage = CF.damageHero(otherSide(who), 1, who, relic.name);
        addLog(`${relic.name} dealt ${relicDamage} damage to ${controllerLabel(otherSide(who)).toLowerCase()}.`, who === 'player' ? 'good' : 'bad');
      }
      if (relic.effect === 'turnReplaceHurt1') {
        if (side.hand.length) {
          const highest = [...side.hand].sort((a, b) => b.cost - a.cost)[0];
          replaceCard(who, highest.uid, false, false);
          addLog(`${relic.name} replaced ${highest.name} and dealt 1 damage to ${controllerLabel(who).toLowerCase()}.`, who === 'player' ? 'bad' : 'good');
        }
        side.life -= 1;
      }
    });

    if (CF.checkGameOver()) return;
    addLog(`${controllerLabel(who)} started turn ${side.maxMana} with ${side.hand.length} card${side.hand.length === 1 ? '' : 's'}.`, 'info', side.championInPlay ? '' : `Deploy ${championDef(who).name} for ${side.championCost} mana when ready.`);
    CF.render();

    if (who === 'enemy') {
      window.setTimeout(CF.aiMainPhase, 550);
    }
  }
  const api = {
    buildDecklist, applyDeckIdentity, showDeckSelect, makeCard, shuffle, createSide,
    resetGame, sideOf, otherSide, controllerLabel, championDef, resetChampionTurnFlags,
    championDeployReason, deployChampion, returnChampionToSlot, saveUndo, clearUndo,
    canUndo, undoLastAction, aiConsiderChampion, addLog, dealStartingHand, drawCard,
    refillHand, replaceCard, startTurn
  };
  Object.assign(CF, api);
  CF.ctx = ctx;
  return api;
  };
})();
