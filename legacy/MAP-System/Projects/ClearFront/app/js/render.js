(() => {
  'use strict';
  const CF = (window.CF = window.CF || {});
  const { MAX_CARDS_PER_TURN, CARD_LIBRARY, HERO_NAMES } = CF;

  // Render + clash-animation layer (DEC-CF-006). Shares mutable game state
  // through the same ctx contract state.js/combat.js use: ctx.state and
  // ctx.undoRecord are the two mutable bindings this module reads (never
  // reassigns), plus $/refs for DOM access. clashTimers and clashSkip are
  // private to this module (declared, assigned, and read entirely within
  // it, except the one clashOverlay listener below, which is why that
  // listener lives here rather than in the inline host). state.js/combat.js
  // functions are called via their window.CF-published form (CF.sideOf,
  // CF.canAttack, etc.), never through ctx.
  CF.installRenderModule = (ctx) => {
  const { $, refs } = ctx;

  let clashTimers = [];
  let clashSkip = null;

  function clashDelay(fn, ms) { clashTimers.push(window.setTimeout(fn, ms)); }

  function buildClashCard(info, sideClass) {
    const el = document.createElement('div');
    el.className = `clash-card ${sideClass} f-${String(info.faction || '').toLowerCase()}`;
    el.innerHTML = `
      <span class="clash-role">${escapeHtml(info.role)}</span>
      ${info.shielded ? '<span class="shield-dot" title="Shield active"></span>' : ''}
      <div class="clash-card-top"><span class="clash-cost">${Number.isFinite(info.cost) ? info.cost : ''}</span><span class="clash-name">${escapeHtml(info.name)}</span></div>
      <div class="clash-type">${escapeHtml(info.faction || '')} unit</div>
      <div class="clash-stats">
        <span class="clash-stat atk">⚔ ${info.power}</span>
        <span class="clash-stat hp">♥ <b>${Math.max(0, info.health)}</b>/${info.maxHealth}</span>
      </div>
      <div class="clash-flag"></div>
    `;
    return el;
  }

  function buildClashFx(offsetLeft) {
    const fx = document.createElement('div');
    fx.className = 'clash-fx';
    if (offsetLeft) fx.style.left = offsetLeft;
    let inner = '<span class="clash-flash"></span><span class="clash-ring"></span>';
    for (let i = 0; i < 10; i++) {
      const ang = Math.round((360 / 10) * i + (Math.random() * 22 - 11));
      const dist = 78 + Math.round(Math.random() * 74);
      inner += `<span class="clash-spark" style="--ang:${ang}deg;--dist:${dist}px"></span>`;
    }
    fx.innerHTML = inner;
    return fx;
  }

  function spawnClashNumber(parent, text, cls = '') {
    const n = document.createElement('span');
    n.className = `clash-dmg on${cls ? ' ' + cls : ''}`;
    n.textContent = text;
    parent.appendChild(n);
  }

  function showClashHit(cardEl, dealt, hadShield, healthAfter) {
    if (hadShield && dealt === 0) {
      spawnClashNumber(cardEl, 'Shielded', 'blocked-zero');
      const dot = cardEl.querySelector('.shield-dot');
      if (dot) dot.remove();
      return;
    }
    if (dealt > 0) {
      spawnClashNumber(cardEl, `-${dealt}`);
      const hpValue = cardEl.querySelector('.clash-stat.hp b');
      const hpStat = cardEl.querySelector('.clash-stat.hp');
      if (hpValue) hpValue.textContent = Math.max(0, healthAfter);
      if (hpStat) {
        hpStat.classList.remove('dropped');
        void hpStat.offsetWidth;
        hpStat.classList.add('dropped');
      }
    }
  }

  function flagClashCard(cardEl, text) {
    const flag = cardEl.querySelector('.clash-flag');
    if (!flag) return;
    flag.textContent = text;
    flag.classList.add('on');
  }

  function stageImpact(fx) {
    refs.clashStage.classList.remove('shake');
    void refs.clashStage.offsetWidth;
    refs.clashStage.classList.add('shake');
    fx.classList.add('on');
  }

  function runBlockedClash(row) {
    const stage = refs.clashStage;
    stage.classList.remove('shake');
    stage.innerHTML = '';
    const attackerEl = buildClashCard({ role: 'Attacker', name: row.attackerName, faction: row.attackerFaction, cost: row.attackerCost, power: row.attackerPower, health: row.attackerHealthBefore, maxHealth: row.attackerMaxHealth, shielded: row.attackerShielded }, 'side-a');
    const blockerEl = buildClashCard({ role: 'Blocker', name: row.blockerName, faction: row.blockerFaction, cost: row.blockerCost, power: row.blockerPower, health: row.blockerHealthBefore, maxHealth: row.blockerMaxHealth, shielded: row.blockerShielded }, 'side-b');
    const vs = document.createElement('span');
    vs.className = 'clash-vs on';
    vs.textContent = 'VS';
    const fx = buildClashFx();
    stage.append(attackerEl, blockerEl, vs, fx);

    window.requestAnimationFrame(() => window.requestAnimationFrame(() => {
      attackerEl.classList.add('charge');
      blockerEl.classList.add('charge');
    }));

    clashDelay(() => {
      attackerEl.classList.add('hit');
      blockerEl.classList.add('hit');
      vs.classList.remove('on');
      vs.classList.add('out');
      stageImpact(fx);
      showClashHit(blockerEl, row.dealtToBlocker, row.blockerShielded, row.blockerHealthAfter);
      showClashHit(attackerEl, row.dealtToAttacker, row.attackerShielded, row.attackerHealthAfter);
    }, 430);

    clashDelay(() => {
      attackerEl.classList.add('recoil');
      blockerEl.classList.add('recoil');
    }, 580);

    clashDelay(() => {
      if (row.attackerDrain && row.dealtToBlocker > 0) spawnClashNumber(attackerEl, `Drain +${row.dealtToBlocker}`, 'heal');
      if (row.blockerDrain && row.dealtToAttacker > 0) spawnClashNumber(blockerEl, `Drain +${row.dealtToAttacker}`, 'heal');
    }, 760);

    const attackerDies = row.attackerHealthAfter <= 0;
    const blockerDies = row.blockerHealthAfter <= 0;
    if (attackerDies || blockerDies) {
      clashDelay(() => {
        if (attackerDies) flagClashCard(attackerEl, 'Destroyed');
        if (blockerDies) flagClashCard(blockerEl, 'Destroyed');
      }, 1060);
      clashDelay(() => {
        if (attackerDies) attackerEl.classList.add('destroyed');
        if (blockerDies) blockerEl.classList.add('destroyed');
      }, 1340);
      return 1920;
    }
    return 1560;
  }

  function runHeroClash(row, report) {
    const stage = refs.clashStage;
    stage.classList.remove('shake');
    stage.innerHTML = '';
    const attackerEl = buildClashCard({ role: 'Attacker', name: row.attackerName, faction: row.attackerFaction, cost: row.attackerCost, power: row.attackerPower, health: row.attackerHealth ?? 1, maxHealth: row.attackerMaxHealth ?? Math.max(1, row.attackerHealth ?? 1), shielded: row.attackerShielded }, 'side-a');
    const defenderOwner = report.defenderOwner;
    const heroEl = document.createElement('div');
    heroEl.className = 'clash-hero';
    heroEl.innerHTML = `
      <span class="clash-hero-sub">${defenderOwner === 'player' ? 'You' : 'Enemy'}</span>
      <strong class="clash-hero-name">${escapeHtml(HERO_NAMES[defenderOwner] || 'Hero')}</strong>
      <div class="clash-hero-life"><b>${Math.max(0, row.lifeBefore ?? 0)}</b></div>
      <span class="clash-hero-sub">Life</span>
      <div class="clash-flag"></div>
    `;
    const fx = buildClashFx('54%');
    stage.append(attackerEl, heroEl, fx);

    window.requestAnimationFrame(() => window.requestAnimationFrame(() => {
      attackerEl.classList.add('charge');
      heroEl.classList.add('in');
    }));

    clashDelay(() => {
      attackerEl.classList.add('hit');
      stageImpact(fx);
      heroEl.classList.add('hit');
      const lifeValue = heroEl.querySelector('.clash-hero-life b');
      if (lifeValue) lifeValue.textContent = Math.max(0, row.lifeAfter ?? 0);
      if (row.dealtToHero > 0) spawnClashNumber(heroEl, `-${row.dealtToHero}`);
      else spawnClashNumber(heroEl, 'Prevented', 'blocked-zero');
    }, 430);

    clashDelay(() => {
      attackerEl.classList.add('recoil');
    }, 580);

    clashDelay(() => {
      const prevented = (row.attackerPower ?? 0) - (row.dealtToHero ?? 0);
      if (prevented > 0 && row.dealtToHero > 0) spawnClashNumber(heroEl, `${prevented} prevented`, 'blocked-zero');
      if (row.attackerDrain && row.dealtToHero > 0) spawnClashNumber(attackerEl, `Drain +${row.dealtToHero}`, 'heal');
    }, 780);

    if ((row.lifeAfter ?? 1) <= 0) {
      clashDelay(() => flagClashCard(heroEl, 'Defeated'), 1060);
      return 1800;
    }
    return 1520;
  }

  function playClashSequence(report, onDone) {
    const rows = report && Array.isArray(report.rows) ? report.rows : [];
    if (!rows.length) { onDone(); return; }
    clashTimers.forEach(window.clearTimeout);
    clashTimers = [];
    let finished = false;
    const finish = () => {
      if (finished) return;
      finished = true;
      clashSkip = null;
      clashTimers.forEach(window.clearTimeout);
      clashTimers = [];
      refs.clashOverlay.classList.remove('show');
      refs.clashStage.classList.remove('shake');
      refs.clashStage.innerHTML = '';
      onDone();
    };
    clashSkip = finish;
    const playerAttack = report.attackerOwner === 'player';
    refs.clashRound.textContent = playerAttack ? 'Your attack' : 'Enemy attack';
    refs.clashRound.classList.toggle('enemy-round', !playerAttack);
    refs.clashStep.textContent = '';
    refs.clashOverlay.classList.add('show');
    let index = 0;
    const nextStep = () => {
      if (finished) return;
      if (index >= rows.length) {
        clashDelay(finish, 140);
        return;
      }
      const row = rows[index];
      refs.clashStep.textContent = `Clash ${index + 1} of ${rows.length}`;
      index += 1;
      const duration = row.type === 'blocked' ? runBlockedClash(row) : runHeroClash(row, report);
      clashDelay(nextStep, duration);
    };
    nextStep();
  }


  function updateBoardScrollIndicator(board, track, thumb) {
    if (!board || !track || !thumb) return;
    const overflow = Math.max(0, board.scrollWidth - board.clientWidth);
    if (overflow <= 2) {
      track.classList.add('inactive');
      thumb.style.width = '100%';
      thumb.style.left = '0%';
      return;
    }
    track.classList.remove('inactive');
    const widthPercent = Math.max(18, Math.min(100, (board.clientWidth / board.scrollWidth) * 100));
    const progress = Math.max(0, Math.min(1, board.scrollLeft / overflow));
    thumb.style.width = `${widthPercent}%`;
    thumb.style.left = `${progress * (100 - widthPercent)}%`;
  }

  function updateBoardScrollbars() {
    updateBoardScrollIndicator(refs.enemyBoard, refs.enemyBoardScrollbar, refs.enemyBoardScrollThumb);
    updateBoardScrollIndicator(refs.playerBoard, refs.playerBoardScrollbar, refs.playerBoardScrollThumb);
  }

  function bindBoardScrollbar(board, track) {
    board.addEventListener('scroll', updateBoardScrollbars, { passive: true });
    track.addEventListener('pointerdown', event => {
      const overflow = Math.max(0, board.scrollWidth - board.clientWidth);
      if (!overflow) return;
      const rect = track.getBoundingClientRect();
      const ratio = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width));
      board.scrollTo({ left: overflow * ratio, behavior: 'smooth' });
    });
  }

  function render() {
    refs.playerLife.textContent = Math.max(0, ctx.state.player.life);
    refs.enemyLife.textContent = Math.max(0, ctx.state.enemy.life);
    refs.playerMana.textContent = `${ctx.state.player.mana}/${ctx.state.player.maxMana}`;
    refs.enemyMana.textContent = `${ctx.state.enemy.mana}/${ctx.state.enemy.maxMana}`;

    renderEnemyHand();
    renderRelics('player');
    renderRelics('enemy');
    renderChampionSlot('player');
    renderChampionSlot('enemy');
    renderBoard('player');
    renderBoard('enemy');
    renderHand();
    renderPhase();
    renderLog();
    window.requestAnimationFrame(updateBoardScrollbars);
  }

  function renderEnemyHand() {
    refs.enemyHand.innerHTML = '';
    refs.enemyDeckInfo.textContent = `${ctx.state.enemy.hand.length} hand · ${ctx.state.enemy.championInPlay ? CF.championDef('enemy').name + ' deployed · ' : ''}${ctx.state.enemy.deck.length} deck`;
    ctx.state.enemy.hand.forEach(() => {
      const back = document.createElement('div');
      back.className = 'enemy-card-back';
      refs.enemyHand.appendChild(back);
    });
    const count = document.createElement('span');
    count.style.color = 'var(--muted)';
    count.style.fontSize = '.82rem';
    count.textContent = `${ctx.state.enemy.hand.length} cards · ${ctx.state.enemy.deck.length} in deck`;
    refs.enemyHand.appendChild(count);
  }

  function renderRelics(owner) {
    const container = owner === 'player' ? refs.playerRelics : refs.enemyRelics;
    const relics = CF.sideOf(owner).relics;
    container.innerHTML = '';
    const zone = container.closest('.relic-zone');
    if (zone) zone.classList.toggle('empty', relics.length === 0);
    if (!relics.length) {
      container.innerHTML = '<span style="color:var(--muted);font-size:.8rem;align-self:center">No relics</span>';
      return;
    }
    relics.forEach(relic => {
      const el = document.createElement('div');
      el.className = 'relic-card';
      const condition = CF.getCardCondition(relic, owner);
      el.innerHTML = `<strong>${escapeHtml(relic.name)}</strong><span>${escapeHtml(relic.text)}</span>${condition ? `<span class="relic-trigger">${escapeHtml(condition.text)}</span>` : ''}`;
      container.appendChild(el);
    });
  }

  function renderChampionSlot(who) {
    const side = CF.sideOf(who);
    const def = CF.championDef(who);
    const container = who === 'player' ? refs.playerChampionSlot : refs.enemyChampionSlot;
    container.innerHTML = '';
    if (side.championInPlay) {
      container.innerHTML = `<span style="color:var(--muted);font-size:.8rem;align-self:center">${escapeHtml(def.name)} is on the battlefield.</span>`;
      return;
    }
    const reason = who === 'player' ? CF.championDeployReason('player') : '';
    const preview = { id: def.id, name: def.name, type: 'unit', faction: def.faction, cost: side.championCost, text: def.abilityText, attack: def.attack, health: def.health, keywords: [...def.keywords], currentHealth: def.health, maxHealth: def.health, bonusAttack: 0, summoningSick: false, exhausted: false, shield: def.keywords.includes('Shield') };
    const el = createCardElement(preview, {
      owner: who,
      clickable: who === 'player' && !reason,
      unavailable: who === 'player' && !!reason,
      commander: true,
      statusLabel: who === 'player' ? (reason || 'Tap to deploy') : 'Waiting in Champion slot',
      statusTone: who === 'player' ? (reason ? 'danger' : 'safe') : ''
    });
    if (who === 'player' && !reason) el.addEventListener('click', () => CF.deployChampion('player'));
    container.appendChild(el);
  }

  function renderBoard(owner) {
    const container = owner === 'player' ? refs.playerBoard : refs.enemyBoard;
    container.innerHTML = '';
    const board = CF.sideOf(owner).board;
    if (!board.length) {
      container.innerHTML = '<span style="color:var(--muted);font-size:.8rem;align-self:center">Board is empty</span>';
      return;
    }
    board.forEach(unit => {
      const assignedBlocker = ctx.state.phase === 'blocking' && owner === 'player' && ctx.state.blockAssignments.has(unit.uid);
      const blockedAttacker = ctx.state.phase === 'blocking' && owner === 'enemy' && [...ctx.state.blockAssignments.values()].includes(unit.uid);
      const selected = ctx.state.selectedAttackers.has(unit.uid) || ctx.state.selectedBlocker === unit.uid || assignedBlocker || blockedAttacker;
      const targetable = ctx.state.targetMode?.validUids.has(unit.uid);
      const playerAttackWindow = ctx.state.turn === 'player' && ctx.state.phase === 'main' && owner === 'player' && !ctx.state.player.combatUsed;
      let unavailableReason = '';
      if (ctx.state.targetMode && !targetable) unavailableReason = 'Not a valid target';
      if (playerAttackWindow && owner === 'player' && !CF.canAttack(unit)) unavailableReason = unit.summoningSick ? 'Played this turn' : unit.exhausted ? 'Already attacked' : 'Cannot attack';
      if (ctx.state.turn === 'player' && ctx.state.phase === 'main' && owner === 'player' && ctx.state.player.combatUsed) unavailableReason = 'Attack step used';
      if (ctx.state.turn === 'enemy' && ctx.state.phase === 'blocking' && owner === 'player' && unit.exhausted) unavailableReason = 'Already used: cannot block';
      if (ctx.state.turn === 'enemy' && ctx.state.phase === 'blocking' && owner === 'enemy') unavailableReason = CF.blockTargetReason(unit);
      const blockingClickable = ctx.state.turn === 'enemy' && ctx.state.phase === 'blocking' && ((owner === 'player' && !unit.exhausted) || (owner === 'enemy' && !!ctx.state.selectedBlocker && !unavailableReason));
      const clickable = targetable || (playerAttackWindow && CF.canAttack(unit)) || blockingClickable;
      let statusLabel = '';
      let statusTone = '';
      if (ctx.state.turn === 'player' && ctx.state.phase === 'main' && owner === 'player' && ctx.state.selectedAttackers.has(unit.uid)) {
        statusLabel = `Will attack for ${CF.cardAttack(unit, true, 'player')}`;
        statusTone = 'safe';
      }
      if (ctx.state.turn === 'enemy' && ctx.state.phase === 'blocking') {
        if (owner === 'enemy' && ctx.state.aiAttackers.some(a => a.uid === unit.uid)) {
          const blockerUid = [...ctx.state.blockAssignments.entries()].find(([, attackerUid]) => attackerUid === unit.uid)?.[0];
          const blocker = ctx.state.player.board.find(card => card.uid === blockerUid);
          statusLabel = blocker ? `Blocked by ${blocker.name}` : `Unblocked: ${CF.cardAttack(unit, true, 'enemy')} damage`;
          statusTone = blocker ? 'safe' : 'danger';
        } else if (owner === 'player' && ctx.state.blockAssignments.has(unit.uid)) {
          const attacker = ctx.state.aiAttackers.find(card => card.uid === ctx.state.blockAssignments.get(unit.uid));
          statusLabel = attacker ? `Blocking ${attacker.name}` : '';
          statusTone = 'safe';
        } else if (owner === 'player' && ctx.state.selectedBlocker === unit.uid) {
          statusLabel = 'Selected: choose attacker';
        }
      }
      if (unavailableReason) { statusLabel = unavailableReason; statusTone = 'danger'; }
      const condition = !statusLabel ? CF.getCardCondition(unit, owner) : null;
      if (condition) {
        statusLabel = condition.text;
        statusTone = condition.tone;
      }
      const readyState = unit.type === 'unit' ? (unit.exhausted ? 'spent' : (unit.summoningSick || unit.stunned || unit.rushLocked) ? 'waiting' : 'ready') : null;
      const el = createCardElement(unit, { readyState, selected, targetable, clickable, unavailable: !!unavailableReason && !targetable, owner, statusLabel, statusTone, synergyActive: !!condition?.active, commander: !!unit.isChampion, attacking: (owner === 'player' && ctx.state.selectedAttackers.has(unit.uid)) || (owner === 'enemy' && ctx.state.aiAttackers.some(a => a.uid === unit.uid)) });
      if (clickable) el.addEventListener('click', () => CF.handleUnitTarget(unit, owner));
      container.appendChild(el);
    });
  }

  function renderHand() {
    refs.playerHand.innerHTML = '';
    refs.playerHandLabel.textContent = ctx.state.player.hand.length
      ? `Your hand · cards played ${ctx.state.player.cardsPlayed}/${MAX_CARDS_PER_TURN}`
      : 'Your hand · empty';
    ctx.state.player.hand.forEach(card => {
      const canSwap = ctx.state.swapMode && ctx.state.turn === 'player' && ctx.state.phase === 'main' && !ctx.state.player.swapUsed;
      const playable = ctx.state.turn === 'player' && ctx.state.phase === 'main' && !ctx.state.targetMode && !ctx.state.swapMode && CF.isCardPlayable('player', card);
      const clickable = canSwap || playable;
      const condition = !canSwap ? CF.getCardCondition(card, 'player') : null;
      const unavailableReason = CF.handUnavailableReason('player', card);
      const statusLabel = canSwap
            ? 'Tap to replace'
            : unavailableReason || condition?.text || '';
      const statusTone = canSwap ? 'safe' : unavailableReason ? 'danger' : condition?.tone || '';
      const el = createCardElement(card, {
        clickable,
        unavailable: !!unavailableReason,
        owner: 'player',
        statusLabel,
        statusTone,
        synergyActive: !!condition?.active && !unavailableReason
      });
      if (clickable) el.addEventListener('click', () => CF.handleHandCard(card));
      refs.playerHand.appendChild(el);
    });
    if (!ctx.state.player.hand.length) refs.playerHand.innerHTML = '<span style="color:var(--muted);font-size:.8rem;align-self:center">Your hand is empty. It refills when your turn ends.</span>';
  }

  function createCardElement(card, opts = {}) {
    const el = document.createElement('article');
    el.className = `card ${card.type}`;
    if (opts.clickable) el.classList.add('clickable');
    if (opts.selected) el.classList.add('selected');
    if (opts.targetable) el.classList.add('targetable');
    if (opts.unavailable) el.classList.add('unavailable');
    if (opts.commander) el.classList.add('commander', `commander-${String(card.faction || '').toLowerCase()}`);
    if (card.exhausted) el.classList.add('exhausted');
    if (opts.synergyActive) el.classList.add('synergy-active');

    const tags = (card.keywords || []).map(k => `<span class="tag">${escapeHtml(k)}</span>`).join('');
    const stats = card.type === 'unit'
      ? `<div class="stats"><span class="stat attack-stat">⚔ ${CF.cardAttack(card, !!opts.attacking, opts.owner)}</span><span class="stat health-stat">♥ ${card.currentHealth}/${card.maxHealth}</span></div>`
      : '<div class="stats"></div>';
    // Type glyphs (mockup look); champions show their faction animal art.
    const artByType = {
      unit: 'assets/glyph-unit.png',
      spell: 'assets/glyph-spell.png',
      relic: 'assets/glyph-relic.png'
    };
    let artSrc = artByType[card.type] || artByType.relic;
    if (opts.commander && typeof card.id === 'string' && card.id.startsWith('champion_')) {
      artSrc = `assets/champ-${card.id.slice('champion_'.length)}.png`;
    }

    // Flat structure: renders as a compact glyph tile in play (board/hand) and
    // as a full card in the catalog / hover-peek, driven by scoped CSS.
    el.innerHTML = `
      ${opts.commander ? '<span class="commander-badge">CHAMPION</span>' : ''}
      ${card.shield ? '<span class="shield-dot" title="Shield active"></span>' : ''}
      <span class="cost">${opts.owner ? CF.effectiveCost(card, opts.owner) : card.cost}</span>
      <div class="card-art"><img src="${artSrc}" alt="${escapeHtml(card.type)} icon" draggable="false" /></div>
      <div class="card-name">${escapeHtml(card.name)}</div>
      <div class="card-type">${escapeHtml(card.faction)} ${escapeHtml(card.type)}</div>
      <div class="card-text">${escapeHtml(card.text)}</div>
      <div class="keywords">${tags}</div>
      ${opts.statusLabel ? `<div class="card-status ${escapeHtml(opts.statusTone || '')}">${escapeHtml(opts.statusLabel)}</div>` : ''}
      ${stats}
      ${opts.readyState ? `<span class="ready-dot ${opts.readyState}" title="${opts.readyState === 'ready' ? 'Ready to attack' : opts.readyState === 'waiting' ? 'Not ready this turn' : 'Already acted'}"></span>` : ''}
    `;
    return el;
  }

  function renderCardCatalog() {
    refs.cardCatalog.innerHTML = '';
    const factionOrder = ['Flame', 'Wild', 'Order', 'Shadow'];
    factionOrder.forEach(faction => {
      const section = document.createElement('section');
      section.className = 'catalog-section';
      const title = document.createElement('h3');
      title.textContent = faction;
      const grid = document.createElement('div');
      grid.className = 'card-catalog';
      Object.entries(CARD_LIBRARY)
        .filter(([, card]) => card.faction === faction)
        .sort((a, b) => a[1].cost - b[1].cost || a[1].name.localeCompare(b[1].name))
        .forEach(([id, base]) => {
          const preview = {
            ...base,
            id,
            keywords: [...(base.keywords || [])],
            currentHealth: base.health ?? null,
            maxHealth: base.health ?? null,
            bonusAttack: 0,
            summoningSick: false,
            exhausted: false,
            shield: (base.keywords || []).includes('Shield')
          };
          grid.appendChild(createCardElement(preview, { owner: faction === 'Order' || faction === 'Shadow' ? 'enemy' : 'player' }));
        });
      section.append(title, grid);
      refs.cardCatalog.appendChild(section);
    });
  }

  function getBlockingSnapshot() {
    const attackers = ctx.state.aiAttackers.filter(attacker => ctx.state.enemy.board.some(unit => unit.uid === attacker.uid));
    const assignments = [...ctx.state.blockAssignments.entries()].filter(([blockerUid, attackerUid]) =>
      ctx.state.player.board.some(unit => unit.uid === blockerUid) && attackers.some(unit => unit.uid === attackerUid)
    );
    const blockedIds = new Set(assignments.map(([, attackerUid]) => attackerUid));
    const unblocked = attackers.filter(attacker => !blockedIds.has(attacker.uid));
    const incomingDamage = unblocked.reduce((sum, attacker) => sum + CF.cardAttack(attacker, true, 'enemy'), 0);
    const availableBlockers = ctx.state.player.board.filter(unit => !unit.exhausted);
    return { attackers, assignments, blockedIds, unblocked, incomingDamage, availableBlockers };
  }

  function predictCombat(attacker, blocker) {
    const attackerPower = CF.cardAttack(attacker, true, 'enemy');
    const blockerPower = CF.cardAttack(blocker, false, 'player');
    const attackerSurvives = attacker.shield || attacker.currentHealth > blockerPower;
    const blockerSurvives = blocker.shield || blocker.currentHealth > attackerPower;
    return { attackerPower, blockerPower, attackerSurvives, blockerSurvives };
  }

  function renderBlockReview() {
    if (ctx.state.turn !== 'enemy' || ctx.state.phase !== 'blocking') {
      refs.blockReviewBody.innerHTML = '<p>There is no attack to review.</p>';
      return;
    }
    const snapshot = getBlockingSnapshot();
    const lifeAfter = Math.max(0, ctx.state.player.life - snapshot.incomingDamage);
    const rows = snapshot.attackers.map(attacker => {
      const assignment = snapshot.assignments.find(([, attackerUid]) => attackerUid === attacker.uid);
      const power = CF.cardAttack(attacker, true, 'enemy');
      const keywordNote = attacker.keywords.includes('Flying') ? ' Flying attackers require a Flying blocker.' : attacker.keywords.includes('Guard') ? ' Guard attackers must be blocked before non-Guard attackers.' : '';
      if (!assignment) {
        return `<div class="combat-row"><div class="combat-row-head"><strong>${escapeHtml(attacker.name)}</strong><span>${power} damage</span></div><p>Unblocked.${escapeHtml(keywordNote)}</p><div class="combat-outcome bad">This unit will deal ${power} damage to you.</div></div>`;
      }
      const blocker = ctx.state.player.board.find(unit => unit.uid === assignment[0]);
      if (!blocker) return '';
      const result = predictCombat(attacker, blocker);
      const attackerOutcome = result.attackerSurvives ? `${attacker.name} survives` : `${attacker.name} is destroyed`;
      const blockerOutcome = result.blockerSurvives ? `${blocker.name} survives` : `${blocker.name} is destroyed`;
      const shieldNote = attacker.shield || blocker.shield ? ' An active Shield prevents that unit’s incoming damage once.' : '';
      const drainNote = blocker.keywords.includes('Drain') ? ` ${blocker.name} restores life equal to the damage it deals.` : '';
      return `<div class="combat-row"><div class="combat-row-head"><strong>${escapeHtml(attacker.name)} → ${escapeHtml(blocker.name)}</strong><span>Blocked</span></div><p>${escapeHtml(attacker.name)} deals ${result.attackerPower}; ${escapeHtml(blocker.name)} deals ${result.blockerPower}. Damage happens at the same time.${escapeHtml(shieldNote + drainNote)}</p><div class="combat-outcome ${result.blockerSurvives ? 'good' : 'bad'}">${escapeHtml(attackerOutcome)}. ${escapeHtml(blockerOutcome)}. You take 0 damage from this attacker.</div></div>`;
    }).join('');

    refs.blockReviewBody.innerHTML = `
      <div class="combat-summary-box"><strong>${snapshot.incomingDamage} incoming damage</strong><span>${snapshot.assignments.length} of ${snapshot.attackers.length} attackers blocked. Before Drain or other healing, your life is projected to change from ${ctx.state.player.life} to ${lifeAfter}.</span></div>
      <div class="combat-rules-note"><strong>How blocking works:</strong> Blocking is optional. Each of your units can block one attacker. A blocked attacker deals no damage to you, even if your blocker is destroyed. The attacker and blocker damage each other simultaneously.</div>
      <div class="combat-list">${rows || '<p>No attackers.</p>'}</div>`;
  }

  function renderCombatReport() {
    const report = ctx.state.lastCombatReport;
    if (!report) {
      refs.combatReportBody.innerHTML = '<p>No combat has happened yet.</p>';
      return;
    }
    const blockedCount = report.rows.filter(row => row.type === 'blocked').length;
    const rows = report.rows.map(row => {
      if (row.type === 'unblocked') {
        return `<div class="combat-row"><div class="combat-row-head"><strong>${escapeHtml(row.attackerName)}</strong><span>${row.attackerPower} damage</span></div><p>No blocker was assigned, so it damaged the defending player directly.</p></div>`;
      }
      const attackerOutcome = row.attackerHealthAfter <= 0 ? `${row.attackerName} was destroyed` : `${row.attackerName} survived at ${row.attackerHealthAfter}/${row.attackerMaxHealth}`;
      const blockerOutcome = row.blockerHealthAfter <= 0 ? `${row.blockerName} was destroyed` : `${row.blockerName} survived at ${row.blockerHealthAfter}/${row.blockerMaxHealth}`;
      const shieldText = row.attackerShielded || row.blockerShielded ? ' A Shield prevented one side’s incoming damage.' : '';
      return `<div class="combat-row"><div class="combat-row-head"><strong>${escapeHtml(row.attackerName)} vs. ${escapeHtml(row.blockerName)}</strong><span>Blocked</span></div><p>${escapeHtml(row.attackerName)} dealt ${row.dealtToBlocker}; ${escapeHtml(row.blockerName)} dealt ${row.dealtToAttacker}. Damage was simultaneous.${escapeHtml(shieldText)}</p><div class="combat-outcome ${row.blockerHealthAfter <= 0 ? 'bad' : 'good'}">${escapeHtml(attackerOutcome)}. ${escapeHtml(blockerOutcome)}.</div></div>`;
    }).join('');
    refs.combatReportBody.innerHTML = `
      <div class="combat-summary-box"><strong>${report.directHeroDamage} damage reached ${CF.controllerLabel(report.defenderOwner).toLowerCase()}</strong><span>Life changed from ${report.defenderLifeBefore} to ${Math.max(0, report.defenderLifeAfter)} after all damage, Drain, and healing. ${blockedCount} of ${report.rows.length} attackers were blocked.</span></div>
      <div class="combat-list">${rows}</div>`;
  }

  function renderPhase() {
    refs.undoBtn.disabled = !CF.canUndo();
    refs.undoBtn.textContent = ctx.undoRecord ? 'Undo' : 'Undo';
    refs.undoBtn.title = ctx.undoRecord ? `Undo ${ctx.undoRecord.label}` : 'No reversible action to undo';
    refs.combatReviewBtn.classList.remove('show');
    refs.combatReviewBtn.disabled = true;
    refs.swapCardBtn.style.display = '';
    refs.swapCardBtn.classList.toggle('primary', ctx.state.swapMode);
    refs.swapCardBtn.textContent = ctx.state.swapMode ? 'Cancel swap' : ctx.state.player.swapUsed ? 'Swap used' : 'Swap 1 card';
    refs.swapCardBtn.disabled = ctx.state.gameOver || ctx.state.turn !== 'player' || ctx.state.phase !== 'main' || !!ctx.state.targetMode || ctx.state.player.swapUsed || !ctx.state.player.hand.length;
    if (ctx.state.gameOver) {
      refs.phaseTitle.textContent = 'Game over';
      refs.phaseHelp.textContent = 'Start a new game to continue.';
      refs.mainActionBtn.textContent = 'Game over';
      refs.mainActionBtn.disabled = true;
      return;
    }

    refs.mainActionBtn.disabled = false;
    if (ctx.state.targetMode) {
      refs.phaseTitle.textContent = 'Choose a target';
      refs.phaseHelp.textContent = ctx.state.targetMode.description;
      refs.mainActionBtn.textContent = 'Cancel';
      return;
    }

    if (ctx.state.turn === 'player' && ctx.state.phase === 'main') {
      refs.phaseTitle.textContent = ctx.state.player.championInPlay ? `${CF.championDef('player').name} active` : 'Your turn';
      const count = ctx.state.selectedAttackers.size;
      const damage = ctx.state.player.board.filter(unit => ctx.state.selectedAttackers.has(unit.uid)).reduce((sum, unit) => sum + CF.cardAttack(unit, true, 'player'), 0);
      refs.phaseHelp.textContent = ctx.state.swapMode
        ? 'Tap one card in your hand to discard it and draw a replacement.'
        : ctx.state.player.combatUsed
          ? `Attack complete. Cards played: ${ctx.state.player.cardsPlayed}/${MAX_CARDS_PER_TURN}. You may still play cards or end your turn.`
          : count
            ? `${count} attacker${count === 1 ? '' : 's'} selected for ${damage} total Attack before blocks.`
            : `Cards played: ${ctx.state.player.cardsPlayed}/${MAX_CARDS_PER_TURN}. ${ctx.state.player.championInPlay ? CF.championDef('player').abilityText : `Deploy ${CF.championDef('player').name} for ${ctx.state.player.championCost} mana to activate your Champion.`}`;
      refs.mainActionBtn.textContent = count && !ctx.state.player.combatUsed ? 'Confirm attack' : 'End turn';
      return;
    }

    if (ctx.state.turn === 'enemy' && ctx.state.phase === 'blocking') {
      const snapshot = getBlockingSnapshot();
      const lifeAfter = Math.max(0, ctx.state.player.life - snapshot.incomingDamage);
      refs.phaseTitle.textContent = `${snapshot.incomingDamage} damage is unblocked`;
      refs.phaseHelp.textContent = `${snapshot.assignments.length}/${snapshot.attackers.length} attackers blocked · life ${ctx.state.player.life} → ${lifeAfter}. Tap Review for outcomes.`;
      refs.mainActionBtn.textContent = snapshot.incomingDamage ? `Take ${snapshot.incomingDamage} damage` : 'Resolve: 0 damage';
      refs.combatReviewBtn.classList.add('show');
      refs.combatReviewBtn.disabled = false;
      return;
    }

    refs.phaseTitle.textContent = 'Enemy turn';
    refs.phaseHelp.textContent = 'The enemy is making its move.';
    refs.mainActionBtn.textContent = 'Waiting';
    refs.mainActionBtn.disabled = true;
  }

  function renderLog() {
    [refs.gameLog, refs.mobileGameLog].forEach(container => {
      container.innerHTML = '';
      ctx.state.log.forEach(entry => {
        const el = document.createElement('div');
        el.className = `log-entry ${entry.tone || ''}`;
        el.innerHTML = `<strong>${escapeHtml(entry.text)}</strong>${entry.detail ? `<span class="log-detail">${escapeHtml(entry.detail)}</span>` : ''}`;
        container.appendChild(el);
      });
    });
    const latest = ctx.state.log.slice(0, 4).find(entry => /destroyed|burned/.test(entry.text.toLowerCase())) || ctx.state.log[0];
    refs.latestEventText.textContent = latest ? latest.text : 'No events yet.';
    refs.latestEventBtn.title = latest?.detail || 'Open recent events';
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[ch]));
  }

  // Relocated from the inline host's event-listener wiring (DEC-CF-006
  // point 7): clashSkip is otherwise fully private to this module, so its
  // one external read site moves here instead of forwarding it through ctx.
  refs.clashOverlay.addEventListener('click', () => { if (clashSkip) clashSkip(); });

  const api = {
    clashDelay, buildClashCard, buildClashFx, spawnClashNumber, showClashHit,
    flagClashCard, stageImpact, runBlockedClash, runHeroClash, playClashSequence,
    updateBoardScrollIndicator, updateBoardScrollbars, bindBoardScrollbar, render,
    renderEnemyHand, renderRelics, renderChampionSlot, renderBoard, renderHand,
    createCardElement, renderCardCatalog, getBlockingSnapshot, predictCombat,
    renderBlockReview, renderCombatReport, renderPhase, renderLog, escapeHtml
  };
  Object.assign(CF, api);
  return api;
  };
})();
