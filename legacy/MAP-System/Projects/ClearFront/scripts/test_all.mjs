#!/usr/bin/env node

import { mkdtemp, readdir, rm } from 'node:fs/promises';
import { createServer } from 'node:net';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawn } from 'node:child_process';

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const artifacts = join(projectRoot, 'artifacts', 'tests');
const appUrl = pathToFileURL(join(projectRoot, 'app', 'index.html')).href;
const results = [];
let chromium;
let profileDir;

function run(command, args, label) {
  return new Promise(resolveRun => {
    const child = spawn(command, args, { cwd: projectRoot, stdio: ['ignore', 'pipe', 'pipe'] });
    let output = '';
    child.stdout.on('data', chunk => { output += chunk; });
    child.stderr.on('data', chunk => { output += chunk; });
    child.on('error', error => resolveRun({ label, ok: false, output: String(error) }));
    child.on('close', code => resolveRun({ label, ok: code === 0, output }));
  });
}

async function freePort() {
  return new Promise((resolvePort, reject) => {
    const server = createServer();
    server.unref();
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      server.close(() => resolvePort(port));
    });
  });
}

async function waitForCdp(port) {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    if (chromium?.exitCode !== null) throw new Error(`Chromium exited before CDP was ready (${chromium.exitCode})`);
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (response.ok) return;
    } catch {}
    await new Promise(resolveWait => setTimeout(resolveWait, 100));
  }
  throw new Error('Chromium CDP endpoint did not become ready');
}

async function startChromium(port) {
  const executable = process.env.CHROMIUM_BIN || 'chromium';
  profileDir = await mkdtemp(join(tmpdir(), 'clearfront-chromium-'));
  chromium = spawn(executable, [
    '--headless=new',
    '--disable-gpu',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    'about:blank',
  ], { stdio: 'ignore', detached: true });
  await new Promise((resolveSpawn, reject) => {
    chromium.once('spawn', resolveSpawn);
    chromium.once('error', reject);
  });
  await waitForCdp(port);
}

async function stopChromium() {
  if (chromium && chromium.exitCode === null) {
    try { process.kill(-chromium.pid, 'SIGTERM'); } catch {}
    await Promise.race([
      new Promise(resolveExit => chromium.once('exit', resolveExit)),
      new Promise(resolveWait => setTimeout(resolveWait, 1500)),
    ]);
    if (chromium.exitCode === null) {
      try { process.kill(-chromium.pid, 'SIGKILL'); } catch {}
    }
  }
  if (profileDir) await rm(profileDir, { recursive: true, force: true });
}

function record(result) {
  results.push(result);
  console.log(`${result.ok ? 'PASS' : 'FAIL'}  ${result.label}`);
  if (!result.ok && result.output) {
    console.error(result.output.trim().split('\n').slice(-20).join('\n'));
  }
}

async function main() {
  const modules = (await readdir(join(projectRoot, 'app', 'js')))
    .filter(name => name.endsWith('.js'))
    .sort();
  for (const module of modules) {
    record(await run(process.execPath, ['--check', join('app', 'js', module)], `syntax: ${module}`));
  }

  record(await run('python3', [join('scripts', 'test_extract_bundle.py')], 'extractor regressions'));

  record(await run(process.execPath, [join('tests', 'engine', 'run-rules.mjs')], 'engine rule matrix'));

  const port = await freePort();
  await startChromium(port);
  const browserChecks = [
    ['input preview', 'task216-input-check.mjs', [String(port), appUrl]],
    ['undo', 'task215-undo-check.mjs', [String(port), appUrl]],
    ['seeded combat/blocking', 'task215-seeded-replay.mjs', [String(port), appUrl, '42']],
  ];
  for (const [label, script, args] of browserChecks) {
    record(await run(process.execPath, [join(artifacts, script), ...args], `browser: ${label}`));
  }
}

try {
  await main();
} catch (error) {
  record({ label: 'runner infrastructure', ok: false, output: error?.stack || String(error) });
} finally {
  await stopChromium();
}

const passed = results.filter(result => result.ok).length;
console.log(`\n${passed}/${results.length} checks passed`);
process.exitCode = passed === results.length ? 0 : 1;
