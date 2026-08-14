// TASK-208 smoke harness: drive a ClearFront page over CDP.
// usage: node cdp-smoke.mjs <port> <fileUrl> <postClickShotPath>
import { writeFileSync } from 'node:fs';

const [port, target, shotPath] = process.argv.slice(2);

async function getWsUrl() {
  for (let i = 0; i < 50; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/list`);
      const list = await res.json();
      const page = list.find(t => t.type === 'page');
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

await new Promise(r => { ws.onopen = r; });
await send('Page.enable');
await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: target });
await loaded;
await sleep(1000);

console.log('PRE', await evalJs(`JSON.stringify({
  overlayShown: document.getElementById('deckSelectOverlay').classList.contains('show'),
  deckOptions: document.querySelectorAll('#deckGrid .deck-option').length,
  firstDeck: document.querySelector('#deckGrid .deck-option strong')?.textContent,
  cfKeys: Object.keys(window.CF || {}).sort().join(',') || '(none)'
})`));

// Click the first deck option (Emberwild) with real input events.
const rect = JSON.parse(await evalJs(`(() => {
  const b = document.querySelector('#deckGrid .deck-option');
  const r = b.getBoundingClientRect();
  return JSON.stringify({ x: r.x + r.width / 2, y: r.y + r.height / 2 });
})()`));
await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: rect.x, y: rect.y, button: 'left', clickCount: 1 });
await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: rect.x, y: rect.y, button: 'left', clickCount: 1 });
await sleep(2000);

console.log('POST', await evalJs(`JSON.stringify({
  overlayShown: document.getElementById('deckSelectOverlay').classList.contains('show'),
  playerDeckName: document.getElementById('playerDeckName').textContent,
  enemyDeckName: document.getElementById('enemyDeckName').textContent,
  handCards: document.getElementById('playerHand').children.length,
  playerLife: document.getElementById('playerLife').textContent,
  enemyLife: document.getElementById('enemyLife').textContent,
  playerMana: document.getElementById('playerMana').textContent,
  phaseTitle: document.getElementById('phaseTitle').textContent,
  handLabel: document.getElementById('playerHandLabel').textContent
})`));

const shot = await send('Page.captureScreenshot', { format: 'png' });
writeFileSync(shotPath, Buffer.from(shot.data, 'base64'));

console.log('CONSOLE_COUNT', consoleMsgs.length);
consoleMsgs.forEach(m => console.log('CONSOLE', m));
console.log('EXCEPTION_COUNT', exceptions.length);
exceptions.forEach(m => console.log('EXCEPTION', m));
ws.close();
process.exit(0);
