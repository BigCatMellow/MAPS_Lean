const CDP_PORT = process.argv[2];
const target = process.argv[3];
const seed = parseInt(process.argv[4] || '42', 10);
const logFile = process.argv[5];

async function main() {
  const res = await fetch(`http://localhost:${CDP_PORT}/json/new?${encodeURIComponent(target)}`, { method: 'PUT' });
  const info = await res.json();
  const ws = new WebSocket(info.webSocketDebuggerUrl);
  let id = 0;
  const pending = new Map();
  const consoleMsgs = [];
  const exceptions = [];

  function send(method, params = {}) {
    const myId = ++id;
    ws.send(JSON.stringify({ id: myId, method, params }));
    return new Promise((resolve) => pending.set(myId, resolve));
  }
  await new Promise((resolve) => { ws.onopen = resolve; });
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg.result); pending.delete(msg.id); }
    else if (msg.method === 'Runtime.consoleAPICalled') consoleMsgs.push(msg.params.args.map(a => a.value ?? a.description ?? '').join(' '));
    else if (msg.method === 'Runtime.exceptionThrown') exceptions.push(msg.params.exceptionDetails.text);
  };

  await send('Runtime.enable');
  await send('Page.enable');
  await send('Page.addScriptToEvaluateOnNewDocument', {
    source: `(function(){var s=${seed};Math.random=function(){s=(s*1103515245+12345)&0x7fffffff;return s/0x7fffffff;};})();`
  });
  await send('Page.navigate', { url: target });
  await new Promise((r) => setTimeout(r, 2000));

  const clickResult = await send('Runtime.evaluate', {
    expression: `(function(){
      const card = Array.from(document.querySelectorAll('*')).find(el => el.textContent.trim() === 'Emberwild' && el.tagName !== 'BODY' && el.tagName !== 'HTML');
      const rect = card.getBoundingClientRect();
      return JSON.stringify({x: rect.x + rect.width/2, y: rect.y + rect.height/2});
    })()`,
    returnByValue: true,
  });
  const { x, y } = JSON.parse(clickResult.result.value);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
  await new Promise((r) => setTimeout(r, 1200));

  const steps = [];
  for (let turn = 0; turn < 8; turn++) {
    await send('Runtime.evaluate', {
      expression: `(function(){
        const cards = Array.from(document.querySelectorAll('#playerHand .card:not(.unavailable)'));
        if (cards.length) cards[0].dispatchEvent(new MouseEvent('click', {bubbles:true}));
      })()`,
      returnByValue: true,
    });
    await new Promise((r) => setTimeout(r, 300));
    await send('Runtime.evaluate', {
      expression: `(function(){ const btn = document.getElementById('mainActionBtn'); if (btn && !btn.disabled) btn.dispatchEvent(new MouseEvent('click',{bubbles:true})); })()`,
      returnByValue: true,
    });
    await new Promise((r) => setTimeout(r, 300));
    await send('Runtime.evaluate', {
      expression: `(function(){
        const readyUnits = Array.from(document.querySelectorAll('#playerBoard .card.ready, #playerBoard .unit.ready'));
        if (readyUnits.length) readyUnits[0].dispatchEvent(new MouseEvent('click', {bubbles:true}));
      })()`,
      returnByValue: true,
    });
    await new Promise((r) => setTimeout(r, 200));
    await send('Runtime.evaluate', {
      expression: `(function(){ const btn = document.getElementById('mainActionBtn'); if (btn && !btn.disabled) btn.dispatchEvent(new MouseEvent('click',{bubbles:true})); })()`,
      returnByValue: true,
    });
    await new Promise((r) => setTimeout(r, 1800));
    await send('Runtime.evaluate', {
      expression: `(function(){ const btn = document.getElementById('mainActionBtn'); if (btn && !btn.disabled) btn.dispatchEvent(new MouseEvent('click',{bubbles:true})); })()`,
      returnByValue: true,
    });
    await new Promise((r) => setTimeout(r, 1500));

    const snap = await send('Runtime.evaluate', {
      expression: `JSON.stringify({
        turn: ${turn},
        lifeYou: (document.getElementById('playerLife')||{}).textContent,
        lifeEnemy: (document.getElementById('enemyLife')||{}).textContent,
        phase: (document.getElementById('phaseTitle')||{}).textContent,
        handCount: document.querySelectorAll('#playerHand .card').length,
        boardCountYou: document.querySelectorAll('#playerBoard .card, #playerBoard .unit').length,
        boardCountEnemy: document.querySelectorAll('#enemyBoard .card, #enemyBoard .unit').length,
        log: Array.from(document.querySelectorAll('#gameLog .log-entry, .log-entry')).slice(-3).map(e=>e.textContent.trim())
      })`,
      returnByValue: true,
    });
    steps.push(JSON.parse(snap.result.value));
  }

  const result = { seed, steps, consoleMsgCount: consoleMsgs.length, exceptionCount: exceptions.length, exceptions };
  if (logFile) {
    const fs = await import('node:fs');
    fs.writeFileSync(logFile, JSON.stringify(result, null, 2));
  }
  console.log(JSON.stringify({ seed, finalStep: steps[steps.length - 1], consoleMsgCount: consoleMsgs.length, exceptionCount: exceptions.length, exceptions }));

  await send('Page.close');
  ws.close();
}
main().catch(e => { console.error('FATAL', e); process.exit(1); });
