/* HOME-READINESS-01. Home stays visible when Initial Setup is incomplete. */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { spawnSync } = require('child_process');

const root = path.resolve(__dirname, '..');
const pages = [
  'app/home/index.html',
  'en/app/home/index.html',
  'zh-tw/app/home/index.html',
];
const fails = [];

function fail(msg) {
  fails.push(msg);
}

function read(rel) {
  return fs.readFileSync(path.join(root, rel), 'utf8');
}

const entrySrc = read('js/kpi-home-entry.js');
const shellSrc = read('js/kpi-home-shell.js');
const kpiSrc = read('js/kpi-home-kpi.js');
if (entrySrc.includes('location.replace') || entrySrc.includes('needsAnnualHost')) {
  fail('home-entry still redirects from readiness');
}
if (!shellSrc.includes("addEventListener('kpi:storeHydrateSettled'")) fail('shell does not repaint after hydrate');
if (!kpiSrc.includes("var DASH = '—'")) fail('home kpi dash convention missing');

const lists = pages.map((rel) => [...read(rel).matchAll(/<script[^>]+src="([^"]+)"/g)].map((m) => m[1].split('?')[0].split('/').pop()));
if (lists[0].join('|') !== lists[1].join('|') || lists[0].join('|') !== lists[2].join('|')) {
  fail('JP/EN/ZH-TW script parity');
}
for (const rel of pages) {
  const html = read(rel);
  if (html.includes('data-kpi-pro-pending')) fail(rel + ' pending gate');
  if (!html.includes('kpi-home-entry.js?v=20261008-hr01')) fail(rel + ' entry cache');
  if (!html.includes('kpi-home-shell.js?v=20261008-hr01')) fail(rel + ' shell cache');
  if (!html.includes('syncPlanFromServer')) fail(rel + ' logged-out session check');
  const dir = path.dirname(path.join(root, rel));
  for (const src of [...html.matchAll(/<script[^>]+src="([^"]+)"/g)].map((m) => m[1])) {
    const file = path.normalize(path.join(dir, src.split('?')[0]));
    if (!fs.existsSync(file)) fail('missing ' + src);
  }
}
const auth = read('js/kpi-auth-client.js');
if (!auth.includes('function handleUnauthorizedSession') || !auth.includes('redirectToLogin')) {
  fail('login redirect source missing');
}
for (const rel of ['js/kpi-home-entry.js', 'js/kpi-home-shell.js', 'js/kpi-home-kpi.js']) {
  const chk = spawnSync(process.execPath, ['--check', path.join(root, rel)], { encoding: 'utf8' });
  if (chk.status !== 0) fail('syntax ' + rel);
}

function bootEntry(opts) {
  const windows = { hidden: true };
  const calls = { sync: 0, replaced: '' };
  const sandbox = {
    console,
    document: {
      querySelector(sel) {
        return sel === '.home-windows' ? windows : null;
      },
      addEventListener() {},
    },
    location: {
      pathname: '/kpi-navigator/app/home/index.html',
      replace(url) { calls.replaced = String(url); },
    },
    CustomEvent: function CustomEvent(type) { this.type = type; },
    dispatchEvent() {},
    __KPI_AUTH: {
      resolveAppRoot: () => '/kpi-navigator',
      syncPlanFromServer: () => Promise.resolve(opts.me),
    },
    __KPI_DATA_GATEWAY: {
      enableSessionSync(url) { calls.sync += 1; calls.url = url; },
    },
  };
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(entrySrc, sandbox);
  return { windows, calls };
}

function bootKpi(store) {
  const values = [];
  const win = {
    getAttribute: () => 'daily',
    querySelectorAll(sel) {
      if (String(sel).indexOf('kpi-value') >= 0) {
        return [0, 1, 2, 3].map(() => {
          const node = { textContent: '' };
          values.push(node);
          return node;
        });
      }
      return [];
    },
    querySelector: () => null,
  };
  const sandbox = {
    console,
    document: {
      querySelectorAll: () => [win],
    },
    localStorage: {
      getItem(key) {
        if (key === 'kpiNavigator.kpiYearStore') return JSON.stringify(store);
        return null;
      },
    },
    window: null,
  };
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(kpiSrc, sandbox);
  sandbox.__KPI_HOME_KPI.paint('2026-10-07');
  const goal = sandbox.__KPI_HOME_KPI.goal('2026-10-07');
  return { values: values.map((n) => n.textContent), goal };
}

(async () => {
  const cases = [
    ['fresh no store', { status: 200, data: { ok: true } }, null],
    ['opening date missing', { status: 200, data: { ok: true } }, { meta: { operatingYear: 2026, businessType: 'restaurant' } }],
    ['setup incomplete', { status: 200, data: { ok: true } }, { meta: { operatingYear: 2026, businessType: 'restaurant', setup: { complete: false } } }],
    ['complete setup', { status: 200, data: { ok: true } }, { meta: { operatingYear: 2026, businessType: 'restaurant', openingDate: '2020-04-01', setup: { complete: true } } }],
    ['partial store', { status: 200, data: { ok: true } }, { meta: { businessType: 'restaurant' } }],
    ['logged out', { status: 401, data: { ok: false, error: 'unauthorized' } }, null],
  ];
  for (const row of cases) {
    const label = row[0];
    const result = bootEntry({ me: row[1] });
    await new Promise((r) => setTimeout(r, 20));
    if (result.calls.replaced) fail(label + ' redirected ' + result.calls.replaced);
    if (result.windows.hidden !== false) fail(label + ' left windows hidden');
    const authed = row[1].status === 200;
    if (authed && result.calls.sync !== 1) fail(label + ' sync count ' + result.calls.sync);
    if (authed && result.calls.url !== '/kpi-navigator/api/v1/store.php') fail(label + ' store url');
    if (!authed && result.calls.sync !== 0) fail(label + ' started store sync');
    else console.log('PASS', label);
  }

  const painted = bootKpi({ meta: { operatingYear: 2026, businessType: 'restaurant' } });
  const bad = painted.values.some((text) => text === 'NaN' || text === 'undefined' || text.indexOf('NaN') >= 0);
  if (bad || painted.values.length !== 4) fail('empty kpi paint ' + JSON.stringify(painted.values));
  else console.log('PASS empty kpi paint', painted.values.join(' | '));

  if (fails.length) {
    console.log('FAIL');
    fails.forEach((m) => console.log(' -', m));
    process.exit(1);
  }
  console.log('HOME-READINESS-01 CHECK PASS');
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
