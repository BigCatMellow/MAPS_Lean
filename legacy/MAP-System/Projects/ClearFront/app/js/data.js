(() => {
  'use strict';

  const MAX_BOARD = 6;
  const MAX_RELICS = 3;
  const HAND_LIMIT = 3;
  const STARTING_HAND = 3;
  const MAX_CARDS_PER_TURN = 2;

  const CARD_LIBRARY = {
    // Flame — fast units and direct damage
    spark_imp: { name: 'Spark Imp', type: 'unit', faction: 'Flame', cost: 1, attack: 1, health: 2, text: 'When played: Deal 1 damage to the enemy player.', effect: 'pingHero' },
    coal_hound: { name: 'Coal Hound', type: 'unit', faction: 'Flame', cost: 1, attack: 2, health: 1, text: 'No ability.' },
    ember_runner: { name: 'Ember Runner', type: 'unit', faction: 'Flame', cost: 1, attack: 1, health: 1, text: 'Charge.', keywords: ['Charge'] },
    flare: { name: 'Flare', type: 'spell', faction: 'Flame', cost: 1, text: 'Deal 1 damage to the enemy player.', effect: 'pingHero' },
    ash_runner: { name: 'Ash Runner', type: 'unit', faction: 'Flame', cost: 2, attack: 2, health: 1, text: 'Charge.', keywords: ['Charge'] },
    smoke_scout: { name: 'Smoke Scout', type: 'unit', faction: 'Flame', cost: 2, attack: 2, health: 2, text: 'When played: Deal 1 damage to the enemy player.', effect: 'pingHero' },
    ember_mage: { name: 'Ember Mage', type: 'unit', faction: 'Flame', cost: 3, attack: 2, health: 3, text: 'When played: Deal 1 damage to an enemy unit.', effect: 'pingUnit' },
    forge_brute: { name: 'Forge Brute', type: 'unit', faction: 'Flame', cost: 3, attack: 4, health: 3, text: 'No ability.' },
    phoenix_hatchling: { name: 'Phoenix Hatchling', type: 'unit', faction: 'Flame', cost: 3, attack: 2, health: 2, text: 'Flying.', keywords: ['Flying'] },
    fire_drake: { name: 'Fire Drake', type: 'unit', faction: 'Flame', cost: 4, attack: 4, health: 3, text: 'Flying.', keywords: ['Flying'] },
    lava_elemental: { name: 'Lava Elemental', type: 'unit', faction: 'Flame', cost: 5, attack: 5, health: 5, text: 'When played: Deal 1 damage to all enemy units.', effect: 'aoe1' },
    cinder_giant: { name: 'Cinder Giant', type: 'unit', faction: 'Flame', cost: 6, attack: 6, health: 5, text: 'No ability.' },
    firebolt: { name: 'Firebolt', type: 'spell', faction: 'Flame', cost: 2, text: 'Deal 3 damage to an enemy unit.', effect: 'damage3' },
    scorch: { name: 'Scorch', type: 'spell', faction: 'Flame', cost: 1, text: 'Deal 2 damage to an enemy unit.', effect: 'damage2' },
    flame_wave: { name: 'Flame Wave', type: 'spell', faction: 'Flame', cost: 5, text: 'Deal 2 damage to all enemy units.', effect: 'aoe2' },
    inferno: { name: 'Inferno', type: 'spell', faction: 'Flame', cost: 7, text: 'Deal 3 damage to all enemy units.', effect: 'aoe3' },
    ember_shrine: { name: 'Ember Shrine', type: 'relic', faction: 'Flame', cost: 3, text: 'Your first damage spell each turn deals 1 extra damage.', effect: 'firstSpellBonus' },

    // Wild — efficient creatures, growth, and healing
    young_wolf: { name: 'Young Wolf', type: 'unit', faction: 'Wild', cost: 1, attack: 2, health: 1, text: 'No ability.' },
    acorn_scout: { name: 'Acorn Scout', type: 'unit', faction: 'Wild', cost: 1, attack: 1, health: 3, text: 'No ability.' },
    seedling: { name: 'Seedling', type: 'unit', faction: 'Wild', cost: 1, attack: 1, health: 2, text: 'No ability.' },
    bark_guard: { name: 'Bark Guard', type: 'unit', faction: 'Wild', cost: 2, attack: 1, health: 4, text: 'Shield.', keywords: ['Shield'] },
    thorn_lizard: { name: 'Thorn Lizard', type: 'unit', faction: 'Wild', cost: 2, attack: 3, health: 2, text: 'No ability.' },
    sky_stag: { name: 'Sky Stag', type: 'unit', faction: 'Wild', cost: 3, attack: 3, health: 2, text: 'Flying.', keywords: ['Flying'] },
    river_bear: { name: 'River Bear', type: 'unit', faction: 'Wild', cost: 3, attack: 3, health: 5, text: 'No ability.' },
    pack_alpha: { name: 'Pack Alpha', type: 'unit', faction: 'Wild', cost: 4, attack: 3, health: 4, text: 'When played: Give another friendly unit +1/+1.', effect: 'buffFriendly' },
    ancient_boar: { name: 'Ancient Boar', type: 'unit', faction: 'Wild', cost: 4, attack: 5, health: 4, text: 'No ability.' },
    moss_titan: { name: 'Moss Titan', type: 'unit', faction: 'Wild', cost: 5, attack: 4, health: 7, text: 'Guard.', keywords: ['Guard'] },
    world_tree_guard: { name: 'World-Tree Guard', type: 'unit', faction: 'Wild', cost: 7, attack: 6, health: 9, text: 'Guard.', keywords: ['Guard'] },
    wild_growth: { name: 'Wild Growth', type: 'spell', faction: 'Wild', cost: 2, text: 'Give a friendly unit +2/+2.', effect: 'buff2' },
    renewal: { name: 'Renewal', type: 'spell', faction: 'Wild', cost: 2, text: 'Restore 4 health to a friendly unit.', effect: 'heal4' },
    mend: { name: 'Mend', type: 'spell', faction: 'Wild', cost: 1, text: 'Restore 3 health to a friendly unit.', effect: 'heal3' },
    stampede: { name: 'Stampede', type: 'spell', faction: 'Wild', cost: 4, text: 'Give all friendly units +1/+1.', effect: 'buffAll1' },
    war_drum: { name: 'War Drum', type: 'relic', faction: 'Wild', cost: 3, text: 'Your attacking units have +1 Attack.', effect: 'attackBoost' },

    // Order — defense, shields, and steady healing
    recruit: { name: 'Recruit', type: 'unit', faction: 'Order', cost: 1, attack: 1, health: 2, text: 'No ability.' },
    vanguard_squire: { name: 'Vanguard Squire', type: 'unit', faction: 'Order', cost: 1, attack: 1, health: 1, text: 'Charge.', keywords: ['Charge'] },
    ward_novice: { name: 'Ward Novice', type: 'unit', faction: 'Order', cost: 1, attack: 1, health: 2, text: 'Shield.', keywords: ['Shield'] },
    shield_bearer: { name: 'Shield Bearer', type: 'unit', faction: 'Order', cost: 2, attack: 1, health: 4, text: 'Guard.', keywords: ['Guard'] },
    skyguard: { name: 'Skyguard', type: 'unit', faction: 'Order', cost: 2, attack: 2, health: 2, text: 'Flying.', keywords: ['Flying'] },
    field_medic: { name: 'Field Medic', type: 'unit', faction: 'Order', cost: 2, attack: 2, health: 2, text: 'When played: Restore 2 life.', effect: 'healHero2' },
    dawn_knight: { name: 'Dawn Knight', type: 'unit', faction: 'Order', cost: 3, attack: 3, health: 3, text: 'Shield.', keywords: ['Shield'] },
    sun_priest: { name: 'Sun Priest', type: 'unit', faction: 'Order', cost: 3, attack: 2, health: 4, text: 'When played: Restore 2 life.', effect: 'healHero2' },
    wall_sentinel: { name: 'Wall Sentinel', type: 'unit', faction: 'Order', cost: 3, attack: 1, health: 6, text: 'Guard.', keywords: ['Guard'] },
    griffin: { name: 'Griffin', type: 'unit', faction: 'Order', cost: 4, attack: 4, health: 3, text: 'Flying.', keywords: ['Flying'] },
    banner_knight: { name: 'Banner Knight', type: 'unit', faction: 'Order', cost: 4, attack: 4, health: 4, text: 'No ability.' },
    golden_lion: { name: 'Golden Lion', type: 'unit', faction: 'Order', cost: 5, attack: 5, health: 6, text: 'No ability.' },
    high_guardian: { name: 'High Guardian', type: 'unit', faction: 'Order', cost: 6, attack: 4, health: 8, text: 'Guard.', keywords: ['Guard'] },
    radiant_blessing: { name: 'Radiant Blessing', type: 'spell', faction: 'Order', cost: 2, text: 'Give a friendly unit Shield.', effect: 'giveShield' },
    smite: { name: 'Smite', type: 'spell', faction: 'Order', cost: 2, text: 'Deal 2 damage to an enemy unit.', effect: 'damage2' },
    rally: { name: 'Rally', type: 'spell', faction: 'Order', cost: 3, text: 'Give all friendly units +1/+1.', effect: 'buffAll1' },
    healing_spring: { name: 'Healing Spring', type: 'relic', faction: 'Order', cost: 3, text: 'At turn start: Restore 1 life.', effect: 'turnHeal' },

    // Shadow — sacrifice, drain, and removal
    grave_rat: { name: 'Grave Rat', type: 'unit', faction: 'Shadow', cost: 1, attack: 1, health: 1, text: 'When destroyed: Deal 1 damage to the enemy player.', deathEffect: 'deathPing' },
    bonecrawler: { name: 'Bonecrawler', type: 'unit', faction: 'Shadow', cost: 1, attack: 2, health: 1, text: 'No ability.' },
    shade_bolt: { name: 'Shade Bolt', type: 'spell', faction: 'Shadow', cost: 1, text: 'Deal 1 damage to the enemy player.', effect: 'pingHero' },
    blood_leech: { name: 'Blood Leech', type: 'unit', faction: 'Shadow', cost: 2, attack: 2, health: 2, text: 'Drain.', keywords: ['Drain'] },
    pain_acolyte: { name: 'Pain Acolyte', type: 'unit', faction: 'Shadow', cost: 2, attack: 3, health: 2, text: 'When played: Take 1 damage.', effect: 'selfDamage1' },
    night_wing: { name: 'Night Wing', type: 'unit', faction: 'Shadow', cost: 3, attack: 3, health: 2, text: 'Flying.', keywords: ['Flying'] },
    hollow_guard: { name: 'Hollow Guard', type: 'unit', faction: 'Shadow', cost: 3, attack: 2, health: 5, text: 'Guard.', keywords: ['Guard'] },
    vampire_bat: { name: 'Vampire Bat', type: 'unit', faction: 'Shadow', cost: 3, attack: 2, health: 2, text: 'Flying. Drain.', keywords: ['Flying', 'Drain'] },
    dusk_reaper: { name: 'Dusk Reaper', type: 'unit', faction: 'Shadow', cost: 4, attack: 4, health: 4, text: 'When played: Take 2 damage.', effect: 'selfDamage2' },
    crypt_horror: { name: 'Crypt Horror', type: 'unit', faction: 'Shadow', cost: 5, attack: 5, health: 6, text: 'No ability.' },
    cruel_end: { name: 'Cruel End', type: 'spell', faction: 'Shadow', cost: 3, text: 'Destroy a damaged enemy unit.', effect: 'destroyDamaged' },
    doom_blade: { name: 'Doom Blade', type: 'spell', faction: 'Shadow', cost: 4, text: 'Destroy an enemy unit.', effect: 'destroyUnit' },
    soul_drain: { name: 'Soul Drain', type: 'spell', faction: 'Shadow', cost: 3, text: 'Deal 2 damage to an enemy unit and restore 2 life.', effect: 'damage2heal2' },
    dark_bargain: { name: 'Dark Bargain', type: 'spell', faction: 'Shadow', cost: 2, text: 'Discard your other cards, refill to 3, and take 2 damage.', effect: 'refreshHandHurt2' },
    soul_lantern: { name: 'Soul Lantern', type: 'relic', faction: 'Shadow', cost: 3, text: 'When your unit is destroyed, restore 1 life.', effect: 'deathHeal' },
    blood_idol: { name: 'Blood Idol', type: 'relic', faction: 'Shadow', cost: 3, text: 'At turn start: Replace your highest-cost card and take 1 damage.', effect: 'turnReplaceHurt1' },

    // Synergy package — short setup, payoff, and engine cards
    cinder_imp: { name: 'Cinder Imp', type: 'unit', faction: 'Flame', cost: 1, attack: 1, health: 1, text: 'When played: Deal 1 damage to an enemy unit.', effect: 'pingUnit' },
    ash_hunter: { name: 'Ash Hunter', type: 'unit', faction: 'Flame', cost: 3, attack: 3, health: 3, text: 'Has +2 Attack while an enemy unit is damaged.', effect: 'damagedEnemyBoost' },
    prepared_strike: { name: 'Prepared Strike', type: 'spell', faction: 'Flame', cost: 2, text: 'Deal 2 damage, or 4 if this is your second card.', effect: 'preparedStrike' },
    finish_weak: { name: 'Finish the Weak', type: 'spell', faction: 'Flame', cost: 2, text: 'Deal 4 damage to a damaged enemy unit.', effect: 'finishWeak' },

    young_sprout: { name: 'Young Sprout', type: 'unit', faction: 'Wild', cost: 1, attack: 1, health: 2, text: 'After this gains Health, give it +1 Attack.', effect: 'growOnHealth' },
    grove_tender: { name: 'Grove Tender', type: 'unit', faction: 'Wild', cost: 2, attack: 2, health: 2, text: 'When played: Give another friendly unit +2 Health.', effect: 'giveHealth2' },
    ancient_stag: { name: 'Ancient Stag', type: 'unit', faction: 'Wild', cost: 5, attack: 5, health: 5, text: 'When played: Gain Shield if another friendly unit has 5 Health.', effect: 'shieldIfBigFriend' },
    pack_instinct: { name: 'Pack Instinct', type: 'spell', faction: 'Wild', cost: 2, text: 'Give a unit +1/+1, or +2/+2 if played first.', effect: 'packInstinct' },
    living_grove: { name: 'Living Grove', type: 'relic', faction: 'Wild', cost: 3, text: 'The first unit to gain Health each turn also gains +1 Attack.', effect: 'healthGainAttack' },

    shield_recruit: { name: 'Shield Recruit', type: 'unit', faction: 'Order', cost: 1, attack: 1, health: 2, text: 'When played: Give another friendly unit Shield.', effect: 'shieldOther' },
    steadfast_guard: { name: 'Steadfast Guard', type: 'unit', faction: 'Order', cost: 3, attack: 2, health: 5, text: 'After this survives combat, give it +1 Attack.', effect: 'growAfterSurvive' },
    rally_line: { name: 'Rally the Line', type: 'spell', faction: 'Order', cost: 2, text: 'Give your damaged units +1/+2.', effect: 'buffDamaged' },
    patient_guardian: { name: 'Patient Guardian', type: 'unit', faction: 'Order', cost: 3, attack: 2, health: 5, text: 'At turn end: Gain Shield if you played only 1 card.', effect: 'shieldIfOneCard' },
    fortress_bell: { name: 'Fortress Bell', type: 'relic', faction: 'Order', cost: 3, text: 'After your first unit survives combat each turn, restore 1 life.', effect: 'surviveHeal' },

    doomed_servant: { name: 'Doomed Servant', type: 'unit', faction: 'Shadow', cost: 1, attack: 1, health: 1, text: 'When destroyed: Deal 2 damage to the enemy player.', deathEffect: 'deathPing2' },
    bone_collector: { name: 'Bone Collector', type: 'unit', faction: 'Shadow', cost: 3, attack: 3, health: 3, text: 'After a friendly unit is destroyed, give this +1/+1.', effect: 'growOnFriendlyDeath' },
    sacrifice_blast: { name: 'Sacrifice Blast', type: 'spell', faction: 'Shadow', cost: 2, text: 'Destroy your weakest unit, then deal 4 damage to an enemy unit.', effect: 'sacrificeBlast' },
    bone_altar: { name: 'Bone Altar', type: 'relic', faction: 'Shadow', cost: 3, text: 'After your first unit is destroyed each turn, deal 1 damage to the enemy player.', effect: 'firstDeathPing' }
  };

  // Each deck contains 30 different cards so the expanded pool appears in normal play.
  const PLAYER_DECKLIST = [
    'cinder_imp','coal_hound','ember_runner','flare','ash_runner','smoke_scout','ash_hunter','forge_brute','phoenix_hatchling','fire_drake','firebolt','scorch','prepared_strike','finish_weak','ember_shrine',
    'young_sprout','acorn_scout','seedling','bark_guard','grove_tender','thorn_lizard','sky_stag','river_bear','pack_alpha','ancient_stag','moss_titan','wild_growth','mend','pack_instinct','living_grove'
  ];

  const AI_DECKLIST = [
    'shield_recruit','recruit','vanguard_squire','ward_novice','shield_bearer','skyguard','field_medic','steadfast_guard','dawn_knight','wall_sentinel','patient_guardian','radiant_blessing','rally_line','fortress_bell','healing_spring',
    'doomed_servant','grave_rat','bonecrawler','shade_bolt','blood_leech','pain_acolyte','bone_collector','night_wing','hollow_guard','vampire_bat','cruel_end','soul_drain','sacrifice_blast','bone_altar','soul_lantern'
  ];

  const DECKS = [
    { id: 'lion', name: 'Emberwild', factions: ['Flame', 'Wild'], color: '#fb923c', img: window.__resources.deck_lion, blurb: 'Fast damage backed by growing beasts.', champion: { id: 'champion_lion', name: 'Ember Warden', faction: 'Flame', baseCost: 6, attack: 4, health: 6, keywords: ['Charge'], abilityKey: 'flameDamage', abilityMag: 1, abilityText: 'While on the battlefield: your first damage card each turn deals +1 damage.' } },
    { id: 'stag', name: 'Verdant Court', factions: ['Wild', 'Order'], color: '#4ade80', img: window.__resources.deck_stag, blurb: 'Tall health, shields, and steady healing.', champion: { id: 'champion_stag', name: 'Verdant Sentinel', faction: 'Wild', baseCost: 6, attack: 3, health: 8, keywords: ['Shield'], abilityKey: 'wildHealth', abilityMag: 1, abilityText: 'While on the battlefield: the first unit you play each turn gains +1 Health.' } },
    { id: 'badger', name: 'Iron Covenant', factions: ['Order', 'Shadow'], color: '#93c5fd', img: window.__resources.deck_badger, blurb: 'Defensive walls that profit from losses.', champion: { id: 'champion_badger', name: 'Iron Warden', faction: 'Order', baseCost: 6, attack: 3, health: 9, keywords: ['Guard'], abilityKey: 'orderPrevent', abilityMag: 1, abilityText: 'While on the battlefield: prevent the first 1 damage dealt to you each turn cycle.' } },
    { id: 'raven', name: 'Ashen Murder', factions: ['Flame', 'Shadow'], color: '#c084fc', img: window.__resources.deck_raven, blurb: 'Burn everything, even your own units.', champion: { id: 'champion_raven', name: 'Ashen Reaper', faction: 'Shadow', baseCost: 6, attack: 5, health: 5, keywords: ['Flying'], abilityKey: 'shadowDeath', abilityMag: 1, abilityText: 'While on the battlefield: the first friendly unit destroyed each turn cycle deals 1 damage to the enemy.' } },
    { id: 'owl', name: 'Gilded Vigil', factions: ['Order', 'Flame'], color: '#facc15', img: window.__resources.deck_owl, blurb: 'Patient defense that strikes back hard.', champion: { id: 'champion_owl', name: 'Gilded Champion', faction: 'Flame', baseCost: 6, attack: 4, health: 7, keywords: ['Shield'], abilityKey: 'flameDamage', abilityMag: 2, abilityText: 'While on the battlefield: your first damage card each turn deals +2 damage.' } },
    { id: 'fox', name: 'Thicket Guile', factions: ['Wild', 'Shadow'], color: '#34d399', img: window.__resources.deck_fox, blurb: 'Tricky growth with cruel sacrifices.', champion: { id: 'champion_fox', name: 'Thicket Stalker', faction: 'Wild', baseCost: 6, attack: 5, health: 5, keywords: ['Rush'], abilityKey: 'wildHealth', abilityMag: 2, abilityText: 'While on the battlefield: the first unit you play each turn gains +2 Health. Rush: can attack enemy units the turn it enters play, but not the opposing player.' } }
  ];

  const FACTION_POOLS = { Flame: [], Wild: [], Order: [], Shadow: [] };
  [...PLAYER_DECKLIST, ...AI_DECKLIST].forEach(id => FACTION_POOLS[CARD_LIBRARY[id].faction].push(id));

  const HERO_NAMES = { player: 'Emberwild', enemy: 'Iron Covenant' };

  // Shared namespace per DEC-CF-002: plain file:// scripts, no ES modules, no bare globals.
  window.CF = Object.assign(window.CF || {}, {
    MAX_BOARD, MAX_RELICS, HAND_LIMIT, STARTING_HAND, MAX_CARDS_PER_TURN,
    CARD_LIBRARY, PLAYER_DECKLIST, AI_DECKLIST, DECKS, FACTION_POOLS, HERO_NAMES
  });
})();
