const CDP_PORT = process.argv[2];
const target = process.argv[3];

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
    source: `(function(){var s=42;Math.random=function(){s=(s*1103515245+12345)&0x7fffffff;return s/0x7fffffff;};})();`
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

  // This seed can deterministically have the enemy go first; wait until it's
  // genuinely the player's main phase before running undo assertions.
  for (let i = 0; i < 20; i++) {
    const phaseCheck = await send('Runtime.evaluate', {
      expression: `(document.getElementById('phaseTitle')||{}).textContent`,
      returnByValue: true,
    });
    if (phaseCheck.result.value === 'Your turn') break;
    await new Promise((r) => setTimeout(r, 600));
  }

  const assertions = [];
  const check = async (label, expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    assertions.push({ label, value: r.result.value });
  };

  await check('undo disabled before any action', `document.getElementById('undoBtn').disabled === true`);

  const before = await send('Runtime.evaluate', {
    expression: `JSON.stringify({hand: document.querySelectorAll('#playerHand .card').length, mana: document.getElementById('playerMana').textContent})`,
    returnByValue: true,
  });

  await send('Runtime.evaluate', {
    expression: `(function(){ const c = document.querySelector('#playerHand .card:not(.unavailable)'); if (c) c.dispatchEvent(new MouseEvent('click',{bubbles:true})); })()`,
    returnByValue: true,
  });
  await new Promise((r) => setTimeout(r, 400));
  await check('ordinary play enables undo', `document.getElementById('undoBtn').disabled === false`);

  await send('Runtime.evaluate', {
    expression: `document.getElementById('undoBtn').dispatchEvent(new MouseEvent('click',{bubbles:true}))`,
    returnByValue: true,
  });
  await new Promise((r) => setTimeout(r, 400));
  const after = await send('Runtime.evaluate', {
    expression: `JSON.stringify({hand: document.querySelectorAll('#playerHand .card').length, mana: document.getElementById('playerMana').textContent})`,
    returnByValue: true,
  });
  assertions.push({ label: 'undo restores hand/mana', value: before.result.value === after.result.value });
  await check('undo disabled after undoing', `document.getElementById('undoBtn').disabled === true`);

  // Replay a play to re-arm undo, then do a replacement -- undo must become unavailable.
  await send('Runtime.evaluate', {
    expression: `(function(){ const c = document.querySelector('#playerHand .card:not(.unavailable)'); if (c) c.dispatchEvent(new MouseEvent('click',{bubbles:true})); })()`,
    returnByValue: true,
  });
  await new Promise((r) => setTimeout(r, 400));
  await check('re-play re-arms undo', `document.getElementById('undoBtn').disabled === false`);

  await send('Runtime.evaluate', {
    expression: `(function(){ const btn = document.getElementById('swapCardBtn'); if (btn && !btn.disabled) btn.dispatchEvent(new MouseEvent('click',{bubbles:true})); })()`,
    returnByValue: true,
  });
  await new Promise((r) => setTimeout(r, 200));
  await send('Runtime.evaluate', {
    expression: `(function(){ const c = document.querySelector('#playerHand .card'); if (c) c.dispatchEvent(new MouseEvent('click',{bubbles:true})); })()`,
    returnByValue: true,
  });
  await new Promise((r) => setTimeout(r, 400));
  await check('undo UNAVAILABLE after replacement (TASK-213/INS-0025)', `document.getElementById('undoBtn').disabled === true`);

  console.log(JSON.stringify({ assertions, consoleMsgCount: consoleMsgs.length, exceptionCount: exceptions.length, exceptions }, null, 2));

  await send('Page.close');
  ws.close();

  // Exit nonzero on any failed assertion or captured exception, so this
  // harness can be registered in an automated/maintenance context and
  // actually fail loudly instead of requiring a human to read the JSON.
  const failed = assertions.filter((a) => a.value !== true);
  if (failed.length || exceptions.length) {
    console.error('FAIL:', JSON.stringify({ failed, exceptions }));
    process.exit(1);
  }
}
main().catch(e => { console.error('FATAL', e); process.exit(1); });
