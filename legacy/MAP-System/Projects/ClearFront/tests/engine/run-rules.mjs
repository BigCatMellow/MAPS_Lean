// ClearFront deterministic rule-matrix runner (TASK-220).
// usage: node tests/engine/run-rules.mjs [--verbose]
//
// Runs every case in rules.cases.mjs against the real engine loaded headless
// via engine-host.mjs. Exit 0 iff every assertion in every case passes.
// Deviation-tagged cases (current behavior differing from clearfront_rules.md,
// per the released TASK-211 audit) are summarized separately — they PASS when
// the engine behaves as shipped; they are the flip-list for the pending
// rules-conformance disposition, not failures.
import { createEngineHost } from './engine-host.mjs';
import { cases } from './rules.cases.mjs';

const verbose = process.argv.includes('--verbose');
const host = createEngineHost();

let failedCases = 0;
let totalAssertions = 0;
let failedAssertions = 0;
const deviations = [];

for (const testCase of cases) {
  const results = [];
  let setupBroken = false;
  const t = {
    pre(label, cond) {
      if (!cond) { setupBroken = true; results.push({ label: `SETUP: ${label}`, ok: false }); }
    },
    eq(label, actual, expected) {
      const ok = actual === expected;
      results.push({ label, ok, detail: ok ? '' : `expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}` });
    },
    ok(label, cond) {
      results.push({ label, ok: !!cond, detail: cond ? '' : 'expected truthy' });
    },
  };

  try {
    testCase.run(host, t);
  } catch (error) {
    results.push({ label: 'case threw', ok: false, detail: error?.stack?.split('\n')[0] ?? String(error) });
  }

  const caseFailed = setupBroken || results.some(r => !r.ok);
  totalAssertions += results.length;
  failedAssertions += results.filter(r => !r.ok).length;
  if (caseFailed) failedCases += 1;
  if (testCase.deviation && !caseFailed) deviations.push(testCase);

  const tag = testCase.deviation ? ' [deviation]' : '';
  console.log(`${caseFailed ? 'FAIL' : 'PASS'}  ${testCase.domain}/${testCase.id}${tag}`);
  for (const r of results) {
    if (!r.ok) console.log(`      ✗ ${r.label}${r.detail ? ` — ${r.detail}` : ''}`);
    else if (verbose) console.log(`      ✓ ${r.label}`);
  }
}

console.log(`\n${cases.length - failedCases}/${cases.length} cases passed (${totalAssertions - failedAssertions}/${totalAssertions} assertions)`);

if (deviations.length) {
  console.log(`\nKnown rules-doc deviations asserted at CURRENT behavior (${deviations.length}) — the flip-list for the pending conformance disposition:`);
  for (const d of deviations) {
    console.log(`  • ${d.id} — ${d.deviation.audit}`);
  }
}

process.exitCode = failedCases === 0 ? 0 : 1;
