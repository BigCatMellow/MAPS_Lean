// TASK-217 compact card-art and detail-preview regression.
// usage: node task217-card-art-check.mjs <port> <fileUrl> <face.png> <hover.png>
import { writeFileSync } from 'node:fs';
const [port, target, facePath, hoverPath] = process.argv.slice(2);
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function wsUrl() {
  for (let i = 0; i < 60; i++) {
    try {
      const pages = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
      const page = pages.find(item => item.type === 'page');
      if (page) return page.webSocketDebuggerUrl;
    } catch {}
    await sleep(100);
  }
  throw new Error('CDP target unavailable');
}
const ws = new WebSocket(await wsUrl());
let id = 0;
const pending = new Map();
const consoleMessages = [];
const exceptions = [];
ws.onmessage = event => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) {
    const { resolve, reject } = pending.get(message.id);
    pending.delete(message.id);
    message.error ? reject(new Error(JSON.stringify(message.error))) : resolve(message.result);
  } else if (message.method === 'Runtime.consoleAPICalled') consoleMessages.push(message.params.type);
  else if (message.method === 'Runtime.exceptionThrown') exceptions.push(message.params.exceptionDetails.text);
};
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const requestId = ++id;
  pending.set(requestId, { resolve, reject });
  ws.send(JSON.stringify({ id: requestId, method, params }));
});
const evaluate = async expression =>
  (await send('Runtime.evaluate', { expression, returnByValue: true })).result.value;
await new Promise(resolve => { ws.onopen = resolve; });
await send('Page.enable');
await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
await send('Page.addScriptToEvaluateOnNewDocument', { source: `
  (() => { const original = window.matchMedia.bind(window); window.matchMedia = query => query.includes('(hover: hover)')
    ? { matches:true, media:query, onchange:null, addListener(){}, removeListener(){}, addEventListener(){}, removeEventListener(){}, dispatchEvent(){return true;} }
    : original(query); })();`
});
await send('Page.navigate', { url: target });
await sleep(900);
await evaluate(`document.querySelector('#deckGrid .deck-option').click()`);
await sleep(400);
await evaluate(`document.getElementById('cardsBtn').click()`);
await sleep(150);

const assertions = [];
const check = async (label, expression) => assertions.push({ label, value: await evaluate(expression) });
await check('three category art sources render', `(() => {
  const sources = new Set([...document.querySelectorAll('#cardCatalog .card-art img')].map(img => img.getAttribute('src')));
  return ['assets/card-unit.png','assets/card-spell.png','assets/card-relic.png'].every(src => sources.has(src));
})()`);
await check('all catalog art loaded', `[...document.querySelectorAll('#cardCatalog .card-art img')].every(img => img.complete && img.naturalWidth > 0)`);
await check('compact hand keeps name and art visible', `(() => {
  const card=document.querySelector('#playerHand .card');
  return !!card?.querySelector('.card-name') && getComputedStyle(card.querySelector('.card-art')).display !== 'none';
})()`);
await check('compact hand hides detailed rules', `getComputedStyle(document.querySelector('#playerHand .card .card-details')).display === 'none'`);

await evaluate(`document.getElementById('closeCardsBtn').click()`);
const rect = JSON.parse(await evaluate(`(() => { const card=document.querySelector('#playerHand .card'); card.scrollIntoView({block:'center'}); const r=card.getBoundingClientRect(); return JSON.stringify({x:r.x+r.width/2,y:r.y+r.height/2}); })()`));
await send('Input.dispatchMouseEvent', { type:'mouseMoved', x:5, y:5 });
await send('Input.dispatchMouseEvent', { type:'mouseMoved', x:rect.x, y:rect.y });
await sleep(120);
await check('hover preview exists', `!!document.querySelector('.card-peek.show')`);
await check('hover preview shows rules', `(() => { const el=document.querySelector('.card-peek.show .card-details'); return !!el && getComputedStyle(el).display !== 'none'; })()`);
await check('hover preview retains art', `!!document.querySelector('.card-peek.show .card-art img')`);

const faceShot = await send('Page.captureScreenshot', { format:'png', clip:{ x:0, y:0, width:1280, height:900, scale:1 } });
writeFileSync(hoverPath, Buffer.from(faceShot.data, 'base64'));
await send('Input.dispatchMouseEvent', { type:'mouseMoved', x:5, y:5 });
await sleep(80);
const compactShot = await send('Page.captureScreenshot', { format:'png', clip:{ x:0, y:0, width:1280, height:900, scale:1 } });
writeFileSync(facePath, Buffer.from(compactShot.data, 'base64'));

const failed = assertions.filter(item => item.value !== true);
console.log(JSON.stringify({ assertions, consoleMessageCount:consoleMessages.length, exceptionCount:exceptions.length, exceptions }, null, 2));
ws.close();
if (failed.length || consoleMessages.length || exceptions.length) process.exit(1);
