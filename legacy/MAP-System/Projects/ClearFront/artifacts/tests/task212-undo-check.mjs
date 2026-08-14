// Cross-file undo check: ordinary play is undoable; swap-replacement is not (TASK-213).
// usage: node task212-undo-check.mjs <port> <fileUrl> <seed>
const [port, target, seed] = process.argv.slice(2);
async function getWsUrl() {
  for (let i = 0; i < 50; i++) {
    try { const p = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t => t.type === 'page'); if (p) return p.webSocketDebuggerUrl; } catch {}
    await new Promise(r => setTimeout(r, 200));
  }
  throw new Error('no target');
}
const ws = new WebSocket(await getWsUrl());
let id = 0; const pending = new Map(); const exceptions = []; const consoleMsgs = [];
ws.onmessage = ev => { const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id); }
  else if (m.method === 'Runtime.exceptionThrown') exceptions.push(m.params.exceptionDetails.text);
  else if (m.method === 'Runtime.consoleAPICalled') consoleMsgs.push(m.params.type);
};
const send = (method, params = {}) => new Promise(r => { pending.set(++id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const evalJs = async e => (await send('Runtime.evaluate', { expression: e, returnByValue: true })).result.value;
async function click(sel, nth = 0) {
  const r = await evalJs(`(() => { const el = document.querySelectorAll(${JSON.stringify(sel)})[${nth}]; if (!el) return null;
    el.scrollIntoView({block:'nearest'}); const b = el.getBoundingClientRect();
    for (const [fx,fy] of [[.5,.5],[.5,.25],[.25,.5],[.5,.1]]) {
      const x=b.x+b.width*fx, y=b.y+b.height*fy;
      if (x<0||y<0||x>=innerWidth||y>=innerHeight) continue;
      const h=document.elementFromPoint(x,y); if (h && (h===el||el.contains(h))) return JSON.stringify({x,y});
    } return null; })()`);
  if (!r) return false;
  const { x, y } = JSON.parse(r);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
  return true;
}
const snap = async () => JSON.parse(await evalJs(`JSON.stringify({
  undoDisabled: document.getElementById('undoBtn').disabled,
  undoTitle: document.getElementById('undoBtn').title,
  handTotal: document.getElementById('playerHand').children.length,
  handLabel: document.getElementById('playerHandLabel').textContent,
  boardTotal: document.querySelectorAll('#playerBoard .card').length,
  swapText: document.getElementById('swapCardBtn').textContent,
  handNames: [...document.querySelectorAll('#playerHand .card .card-name')].map(n => n.textContent)
})`));
await new Promise(r => { ws.onopen = r; });
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
await send('Page.addScriptToEvaluateOnNewDocument', { source: `
  (() => { let s = ${Number(seed)} >>> 0;
    Math.random = () => { s |= 0; s = s + 0x6D2B79F5 | 0;
      let t = Math.imul(s ^ s >>> 15, 1 | s);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296; }; })();` });
await send('Page.navigate', { url: target });
await sleep(1500);
await click('#deckGrid .deck-option'); await sleep(2000);

const checks = [];
const s0 = await snap();
checks.push(['undo disabled before any action', s0.undoDisabled === true]);
// ordinary play: Seedling (seed 42 hand), then undo it
await click('#playerHand .card.clickable'); await sleep(800);
const s1 = await snap();
checks.push(['card played (board 1, hand 2)', s1.boardTotal === 1 && s1.handTotal === 2]);
checks.push(['undo ENABLED after ordinary play', s1.undoDisabled === false]);
await click('#undoBtn'); await sleep(800);
const s2 = await snap();
checks.push(['undo restored hand (3 cards, board 0)', s2.handTotal === 3 && s2.boardTotal === 0]);
checks.push(['undo disabled again after undoing', s2.undoDisabled === true]);
// re-play to create a fresh undo snapshot, then swap-replace: undo must be unavailable (TASK-213)
await click('#playerHand .card.clickable'); await sleep(800);
const s3 = await snap();
checks.push(['re-play succeeded with undo snapshot', s3.boardTotal === 1 && s3.undoDisabled === false]);
await click('#swapCardBtn'); await sleep(500);
await click('#playerHand .card', 0); await sleep(800);
const s4 = await snap();
checks.push(['swap consumed (button says Swap used)', /Swap used/.test(s4.swapText)]);
checks.push(['hand still 2 cards after replacement', s4.handTotal === 2]);
checks.push(['undo UNAVAILABLE after replacement (TASK-213)', s4.undoDisabled === true]);
checks.push(['hand changed by replacement', JSON.stringify(s4.handNames) !== JSON.stringify(s3.handNames)]);

let pass = true;
for (const [name, ok] of checks) { console.log(ok ? 'PASS' : 'FAIL', name); if (!ok) pass = false; }
console.log('EXCEPTIONS', exceptions.length, 'CONSOLE', consoleMsgs.length);
if (exceptions.length || consoleMsgs.length) pass = false;
console.log('RESULT', pass ? 'PASS' : 'FAIL');
ws.close(); process.exit(pass ? 0 : 1);
