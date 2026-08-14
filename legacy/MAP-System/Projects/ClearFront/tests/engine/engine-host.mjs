// Headless engine host for ClearFront rule tests (TASK-220, INS-0026).
//
// Loads the REAL, UNMODIFIED app/js/data.js + state.js + combat.js into a
// node:vm context with a minimal browser stub, then plays the same role
// app/index.html plays as "host": it owns the mutable bindings (state,
// undoRecord, uidCounter, deck choices) and hands the modules a ctx of
// accessors over them. Because the installer pattern makes the host
// swappable, a test harness is just another host — no engine changes, no
// DOM, no browser, no RNG (seeded), no timing (timers are queued for
// manual draining, and the render stub completes combat synchronously).
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const appJs = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'app', 'js');

function fakeElement() {
  return {
    classList: { add() {}, remove() {}, contains: () => false },
    style: { setProperty() {} },
    textContent: '',
    appendChild() {}, addEventListener() {}, remove() {},
    dataset: {}, innerHTML: '',
  };
}

export function createEngineHost() {
  const timers = [];
  const sandbox = {
    console,
    // saveUndo() uses structuredClone — a host API, not an ECMA builtin, so
    // fresh vm contexts don't have it. The outer-realm clone works fine on
    // the engine's plain-data state objects.
    structuredClone: (value) => structuredClone(value),
    document: {
      documentElement: fakeElement(),
      createElement: () => fakeElement(),
      getElementById: () => fakeElement(),
      addEventListener() {},
      querySelector: () => null,
      querySelectorAll: () => [],
      body: fakeElement(),
    },
    navigator: {},
  };
  sandbox.window = {
    CF: {},
    __resources: new Proxy({}, { get: (_, key) => `assets/${String(key)}.png` }),
    setTimeout: (fn, ms) => { timers.push({ fn, ms }); return timers.length; },
    clearTimeout() {},
    matchMedia: () => ({ matches: false }),
    addEventListener() {},
    innerWidth: 1280, innerHeight: 900,
    requestAnimationFrame: (fn) => fn(),
  };
  vm.createContext(sandbox);

  // Deterministic context-local RNG. Cases drive state directly, so nothing
  // should depend on RNG — this is insurance against incidental shuffle use.
  vm.runInContext(
    '(function(){var s=42;Math.random=function(){s=(s*1103515245+12345)&0x7fffffff;return s/0x7fffffff;};})();',
    sandbox,
  );

  for (const mod of ['data.js', 'state.js', 'combat.js']) {
    vm.runInContext(readFileSync(join(appJs, mod), 'utf-8'), sandbox, { filename: mod });
  }
  const CF = sandbox.window.CF;

  // Render layer stub (mirrors render.js's published surface as used by the
  // engine). playClashSequence completing synchronously via onDone() is what
  // makes combat resolution deterministic and instant under test.
  Object.assign(CF, {
    render() {},
    renderCombatReport() {},
    playClashSequence(report, onDone) { onDone(); },
  });

  // Host-owned mutable bindings + ctx accessors, exactly as app/index.html.
  const bindings = {
    state: undefined,
    undoRecord: null,
    uidCounter: 1,
    playerDeckChoice: CF.DECKS[0],
    enemyDeckChoice: CF.DECKS[2],
  };
  const refs = new Proxy({}, { get: () => fakeElement() });
  const ctx = {
    get state() { return bindings.state; }, set state(v) { bindings.state = v; },
    get undoRecord() { return bindings.undoRecord; }, set undoRecord(v) { bindings.undoRecord = v; },
    get uidCounter() { return bindings.uidCounter; }, set uidCounter(v) { bindings.uidCounter = v; },
    get playerDeckChoice() { return bindings.playerDeckChoice; }, set playerDeckChoice(v) { bindings.playerDeckChoice = v; },
    get enemyDeckChoice() { return bindings.enemyDeckChoice; }, set enemyDeckChoice(v) { bindings.enemyDeckChoice = v; },
    $: () => fakeElement(), refs,
  };
  const S = CF.installStateModule(ctx);
  const C = CF.installCombatModule(ctx);

  const host = {
    CF, S, C, ctx, timers,
    get state() { return bindings.state; },
    /** Fresh deterministic game. Decks selectable by DECKS index. */
    reset({ playerDeck = 0, enemyDeck = 2 } = {}) {
      bindings.playerDeckChoice = CF.DECKS[playerDeck];
      bindings.enemyDeckChoice = CF.DECKS[enemyDeck];
      bindings.undoRecord = null;
      bindings.uidCounter = 1;
      S.resetGame();
      timers.length = 0; // discard the queued AI kick / anything from reset
      // Normalize whoever won the random first-turn toss into a known state:
      // force player main phase with explicit resources for direct-drive tests.
      const st = bindings.state;
      st.turn = 'player';
      st.phase = 'main';
      st.gameOver = false;
      return st;
    },
    /** Run queued timer callbacks (e.g. deferred AI turn), draining fully. */
    drainTimers() {
      while (timers.length) timers.shift().fn();
    },
    /** Build a battle-ready unit on a side's board and return it. */
    spawn(cardId, who = 'player', overrides = {}) {
      const card = S.makeCard(cardId);
      card.summoningSick = false;
      Object.assign(card, overrides);
      bindings.state[who].board.push(card);
      return card;
    },
  };
  return host;
}
