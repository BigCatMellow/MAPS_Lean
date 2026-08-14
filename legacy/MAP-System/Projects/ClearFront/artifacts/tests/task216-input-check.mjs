// TASK-216 card-preview regression over CDP.
// usage: node task216-input-check.mjs <port> <fileUrl>
const [port, target] = process.argv.slice(2);
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

async function getWsUrl() {
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

const ws = new WebSocket(await getWsUrl());
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
  } else if (message.method === 'Runtime.consoleAPICalled') {
    consoleMessages.push(message.params.type);
  } else if (message.method === 'Runtime.exceptionThrown') {
    exceptions.push(message.params.exceptionDetails.text);
  }
};
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const requestId = ++id;
  pending.set(requestId, { resolve, reject });
  ws.send(JSON.stringify({ id: requestId, method, params }));
});
const evaluate = async expression =>
  (await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })).result.value;

await new Promise(resolve => { ws.onopen = resolve; });
await send('Page.enable');
await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: target });
await sleep(800);

await evaluate(`document.querySelector('#deckGrid .deck-option').click()`);
for (let i = 0; i < 50; i++) {
  if (await evaluate(`document.querySelector('#playerHand .card') !== null`)) break;
  await sleep(100);
}

const assertions = [];
const check = async (label, expression) => assertions.push({ label, value: await evaluate(expression) });
await check('input installer published', `typeof window.CF.installInputModule === 'function'`);
await check('ctx remains seven keys', `Object.keys(window.CF.ctx).sort().join(',') === '$,enemyDeckChoice,playerDeckChoice,refs,state,uidCounter,undoRecord'`);

// Headless Chromium may not advertise hover through matchMedia, so replace
// only this installer's media-query result, reinstall once on a clean reload,
// and exercise the unchanged desktop listener path.
await send('Page.addScriptToEvaluateOnNewDocument', { source: `
  (() => {
    const original = window.matchMedia.bind(window);
    window.matchMedia = query => query.includes('(hover: hover)')
      ? { matches: true, media: query, onchange: null, addListener(){}, removeListener(){}, addEventListener(){}, removeEventListener(){}, dispatchEvent(){ return true; } }
      : original(query);
  })();`
});
await send('Page.navigate', { url: target });
await sleep(800);
await evaluate(`document.querySelector('#deckGrid .deck-option').click()`);
await sleep(300);
await evaluate(`document.querySelector('#playerHand .card').dispatchEvent(new MouseEvent('mouseover', { bubbles: true }))`);
await sleep(100);
await check('desktop hover creates visible preview', `!!document.querySelector('.card-peek.show:not(.touch)')`);
await check('desktop preview is noninteractive', `!document.querySelector('.card-peek').classList.contains('clickable')`);
await evaluate(`document.querySelector('#playerHand .card').dispatchEvent(new MouseEvent('mouseout', { bubbles: true, relatedTarget: document.body }))`);
await sleep(50);
await check('desktop mouseout removes preview', `document.querySelector('.card-peek') === null`);

await evaluate(`document.querySelector('#playerHand .card').dispatchEvent(new TouchEvent('touchstart', { bubbles: true, cancelable: true }))`);
await sleep(450);
await check('touch hold creates touch preview', `!!document.querySelector('.card-peek.touch.show')`);
await check('touch hold creates backdrop', `!!document.querySelector('.peek-backdrop')`);
await evaluate(`document.querySelector('#playerHand .card').dispatchEvent(new TouchEvent('touchend', { bubbles: true, cancelable: true }))`);
await sleep(50);
await check('touch end removes preview and backdrop', `!document.querySelector('.card-peek') && !document.querySelector('.peek-backdrop')`);

const failed = assertions.filter(item => item.value !== true);
console.log(JSON.stringify({ assertions, consoleMessageCount: consoleMessages.length, exceptionCount: exceptions.length, exceptions }, null, 2));
ws.close();
if (failed.length || consoleMessages.length || exceptions.length) process.exit(1);
