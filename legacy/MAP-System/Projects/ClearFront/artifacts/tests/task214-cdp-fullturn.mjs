// TASK-212 full-turn smoke driver: deck select -> play a card -> attack -> end turn,
// adaptively handling random first player, enemy attacks (blocking phase), clash
// animations, and report overlays. Zero console/exception tolerance.
// usage: node task212-cdp-fullturn.mjs <port> <fileUrl> <finalShotPath>
import { writeFileSync } from 'node:fs';

const [port, target, shotPath, seed] = process.argv.slice(2);

async function getWsUrl() {
  for (let i = 0; i < 50; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/list`);
      const page = (await res.json()).find(t => t.type === 'page');
      if (page) return page.webSocketDebuggerUrl;
    } catch {}
    await new Promise(r => setTimeout(r, 200));
  }
  throw new Error('no CDP target on port ' + port);
}

const ws = new WebSocket(await getWsUrl());
let id = 0;
const pending = new Map();
const consoleMsgs = [];
const exceptions = [];
let loadFired;
const loaded = new Promise(r => { loadFired = r; });

ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
  } else if (msg.method === 'Runtime.consoleAPICalled') {
    consoleMsgs.push(`${msg.params.type}: ${msg.params.args.map(a => a.value ?? a.description ?? '').join(' ')}`);
  } else if (msg.method === 'Runtime.exceptionThrown') {
    const d = msg.params.exceptionDetails;
    exceptions.push(`${d.text} ${d.exception?.description || ''}`);
  } else if (msg.method === 'Page.loadEventFired') {
    loadFired();
  }
};

function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const i = ++id;
    pending.set(i, { resolve, reject });
    ws.send(JSON.stringify({ id: i, method, params }));
  });
}
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const evalJs = async (expr) =>
  (await send('Runtime.evaluate', { expression: expr, returnByValue: true })).result.value;

async function clickSelector(sel, nth = 0) {
  // Scroll into view, then probe candidate points until one hit-tests to the
  // element itself (bottom-of-viewport cards are partially clipped).
  const rect = await evalJs(`(() => {
    const el = document.querySelectorAll(${JSON.stringify(sel)})[${nth}];
    if (!el) return null;
    el.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    const r = el.getBoundingClientRect();
    const pts = [[.5,.5],[.5,.25],[.5,.75],[.25,.5],[.75,.5],[.5,.1]]
      .map(([fx,fy]) => ({ x: r.x + r.width*fx, y: r.y + r.height*fy }));
    for (const p of pts) {
      if (p.x < 0 || p.y < 0 || p.x >= innerWidth || p.y >= innerHeight) continue;
      const hit = document.elementFromPoint(p.x, p.y);
      if (hit && (hit === el || el.contains(hit))) return JSON.stringify(p);
    }
    return null;
  })()`);
  if (!rect) return false;
  const { x, y } = JSON.parse(rect);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
  return true;
}

const snapshot = async () => JSON.parse(await evalJs(`JSON.stringify({
  deckSelect: document.getElementById('deckSelectOverlay').classList.contains('show'),
  clash: document.getElementById('clashOverlay').classList.contains('show'),
  combatReport: document.getElementById('combatReportOverlay').classList.contains('show'),
  blockOverlay: document.getElementById('blockOverlay').classList.contains('show'),
  gameOver: document.getElementById('gameOverOverlay').classList.contains('show'),
  phaseTitle: document.getElementById('phaseTitle').textContent,
  phaseHelp: document.getElementById('phaseHelp').textContent,
  btnText: document.getElementById('mainActionBtn').textContent,
  btnDisabled: document.getElementById('mainActionBtn').disabled,
  handLabel: document.getElementById('playerHandLabel').textContent,
  handClickable: document.querySelectorAll('#playerHand .card.clickable').length,
  handTotal: document.getElementById('playerHand').children.length,
  boardClickable: document.querySelectorAll('#playerBoard .card.clickable').length,
  boardTotal: document.getElementById('playerBoard').children.length,
  playerLife: document.getElementById('playerLife').textContent,
  enemyLife: document.getElementById('enemyLife').textContent,
  playerMana: document.getElementById('playerMana').textContent
})`));

await new Promise(r => { ws.onopen = r; });
await send('Page.enable');
await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
if (seed) {
  // Deterministic Math.random so two page versions play the identical game.
  await send('Page.addScriptToEvaluateOnNewDocument', { source: `
    (() => { let s = ${Number(seed)} >>> 0;
      Math.random = () => { s |= 0; s = s + 0x6D2B79F5 | 0;
        let t = Math.imul(s ^ s >>> 15, 1 | s);
        t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
        return ((t ^ t >>> 14) >>> 0) / 4294967296; }; })();` });
}
await send('Page.navigate', { url: target });
await loaded;
await sleep(800);

const cardsPlayedOf = (label) => { const m = label.match(/cards played (\d+)/); return m ? +m[1] : null; };
const goals = { deckPicked: false, playedCard: false, attacked: false, endedTurn: 0, endedAfterAttack: false, blocked: false, aiTurnSeen: false };
let attackConfirmPending = false;
let triedCards = new Set();
let lastClicked = null;
const clickableNames = async () => JSON.parse(await evalJs(`JSON.stringify([...document.querySelectorAll('#playerHand .card.clickable')].map(c => c.querySelector('.card-name').textContent))`));
const log = (s) => console.log('STEP', s);

for (let tick = 0; tick < 240; tick++) {
  const s = await snapshot();
  if (s.gameOver) { log(`game over reached: ${s.phaseHelp}`); break; }

  if (s.deckSelect) {
    if (!goals.deckPicked) { log('pick deck: Emberwild'); await clickSelector('#deckGrid .deck-option'); goals.deckPicked = true; }
    await sleep(600); continue;
  }
  if (s.clash) { await sleep(500); continue; }
  if (s.combatReport) { log('close combat report'); await clickSelector('#closeCombatReportBtn'); await sleep(400); continue; }
  if (s.blockOverlay) { log('close block review'); await clickSelector('#closeBlockBtn'); await sleep(400); continue; }

  if (s.phaseTitle === 'Choose a target') {
    if (lastClicked) { triedCards.add(lastClicked); lastClicked = null; }
    log('cancel target mode'); await clickSelector('#mainActionBtn'); await sleep(400); continue;
  }

  // Blocking phase: enemy attacked us; try to assign one block, then resolve.
  if (/damage is unblocked/.test(s.phaseTitle) && !s.btnDisabled) {
    goals.aiTurnSeen = true;
    if (!goals.blocked && s.boardClickable > 0) {
      log('select blocker (own ready unit)');
      await clickSelector('#playerBoard .card.clickable'); await sleep(400);
      const mid = await snapshot();
      if (JSON.parse(await evalJs(`document.querySelectorAll('#enemyBoard .card.clickable').length`)) > 0) {
        await clickSelector('#enemyBoard .card.clickable'); await sleep(400);
        const after = await snapshot();
        if (after.btnText !== s.btnText) { goals.blocked = true; log(`block assigned ("${s.btnText}" -> "${after.btnText}")`); }
        else log('block click did not change projection; resolving anyway');
      } else { log('no assignable attacker after selecting blocker'); }
    }
    const cur = await snapshot();
    log(`resolve enemy attack: "${cur.btnText}"`); await clickSelector('#mainActionBtn'); await sleep(800); continue;
  }

  // Enemy turn / waiting.
  if (s.btnDisabled || s.btnText === 'Waiting') { if (s.phaseTitle === 'Enemy turn') goals.aiTurnSeen = true; await sleep(500); continue; }

  const playerMain = s.btnText === 'End turn' || s.btnText === 'Confirm attack';
  if (!playerMain) { await sleep(500); continue; }

  if (attackConfirmPending && /attack complete/i.test(s.phaseHelp)) {
    goals.attacked = true; attackConfirmPending = false;
    log(`attack resolved (life ${s.playerLife} vs ${s.enemyLife})`);
  }

  // 1) Play cards whenever possible (build board presence so blockers exist).
  if (s.handClickable > 0) {
    const names = await clickableNames();
    const nth = names.findIndex(n => !triedCards.has(n));
    if (nth >= 0) {
      const before = cardsPlayedOf(s.handLabel);
      lastClicked = names[nth];
      log(`play hand card "${names[nth]}" (cards played before: ${before})`);
      await clickSelector('#playerHand .card.clickable', nth);
      await sleep(700);
      const after = await snapshot();
      if (after.phaseTitle === 'Choose a target') { triedCards.add(names[nth]); lastClicked = null; log('target mode -> cancel, skip that card'); await clickSelector('#mainActionBtn'); await sleep(400); continue; }
      if (cardsPlayedOf(after.handLabel) > before) { goals.playedCard = true; lastClicked = null; log(`card played (${after.handLabel}, board ${after.boardTotal})`); }
      continue;
    }
    // every clickable card is a target-mode dud this turn: fall through to end turn
  }

  // 2) Attack if a ready unit exists and we have not attacked yet.
  if (!goals.attacked && !attackConfirmPending && s.boardClickable > 0 && s.btnText === 'End turn') {
    log('select attacker (click own board unit)');
    await clickSelector('#playerBoard .card.clickable');
    await sleep(400); continue;
  }
  if (!goals.attacked && s.btnText === 'Confirm attack') {
    log('confirm attack'); attackConfirmPending = true;
    await clickSelector('#mainActionBtn');
    await sleep(800); continue;
  }

  // 3) End turn (only after we have at least played a card; attack may need a later turn).
  if (s.btnText === 'End turn') {
    if (goals.playedCard && goals.attacked && goals.endedAfterAttack && goals.blocked) { log('all goals met; stopping at player main'); break; }
    log(`end turn #${goals.endedTurn + 1} (played=${goals.playedCard} attacked=${goals.attacked})`);
    goals.endedTurn++;
    if (goals.attacked) goals.endedAfterAttack = true;
    triedCards = new Set();
    await clickSelector('#mainActionBtn');
    await sleep(1000); continue;
  }
  await sleep(400);
}

const final = await snapshot();
console.log('FINAL', JSON.stringify(final));
console.log('GOALS', JSON.stringify(goals));
const shot = await send('Page.captureScreenshot', { format: 'png' });
writeFileSync(shotPath, Buffer.from(shot.data, 'base64'));
console.log('CONSOLE_COUNT', consoleMsgs.length);
consoleMsgs.forEach(m => console.log('CONSOLE', m));
console.log('EXCEPTION_COUNT', exceptions.length);
exceptions.forEach(m => console.log('EXCEPTION', m));
const ok = goals.playedCard && goals.attacked && goals.endedAfterAttack && goals.blocked && goals.aiTurnSeen && exceptions.length === 0 && consoleMsgs.length === 0;
console.log('RESULT', ok ? 'PASS' : 'FAIL');
ws.close();
process.exit(ok ? 0 : 1);
