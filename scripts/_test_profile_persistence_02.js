/**
 * PROFILE-PERSISTENCE-02 — server-first profile hydration and save order.
 * Simulates a fresh browser with mocked storage and profile.php. No deploy.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const BT = fs.readFileSync(path.join(ROOT, 'js', 'kpi-business-type.js'), 'utf8');
const PS = fs.readFileSync(path.join(ROOT, 'js', 'kpi-profile-server.js'), 'utf8');

const fails = [];
function check(cond, msg) {
  if (!cond) fails.push(msg);
  else process.stdout.write('ok ' + msg + '\n');
}

function storage() {
  const map = new Map();
  const writes = [];
  return {
    getItem(k) { return map.has(k) ? map.get(k) : null; },
    setItem(k, v) { writes.push(k); map.set(k, String(v)); },
    removeItem(k) { map.delete(k); },
    clear() { map.clear(); },
    _map: map,
    _writes: writes,
  };
}

function boot(opts) {
  opts = opts || {};
  const local = storage();
  const session = storage();
  const calls = [];
  let serverProfile = JSON.parse(JSON.stringify(opts.profile || { synced: false, userId: 'u1' }));
  const inputs = {};
  function field(id) {
    if (!inputs[id]) inputs[id] = { id: id, value: '', textContent: '' };
    return inputs[id];
  }
  if (opts.store) {
    local.setItem('kpiNavigator.kpiYearStore', JSON.stringify(opts.store));
  }
  if (opts.localProfile) {
    local.setItem('kpi-profile-last', JSON.stringify(opts.localProfile));
  }
  const listeners = {};
  const document = {
    readyState: 'complete',
    documentElement: { getAttribute: function () { return 'ja'; }, lang: 'ja' },
    getElementById: field,
    addEventListener: function (name, fn) {
      (listeners[name] = listeners[name] || []).push(fn);
    },
    removeEventListener: function (name, fn) {
      listeners[name] = (listeners[name] || []).filter(function (item) { return item !== fn; });
    },
    dispatchEvent: function (ev) {
      (listeners[ev.type] || []).slice().forEach(function (fn) { fn(ev); });
    },
    createElement: function () { return { setAttribute: function () {}, style: {}, appendChild: function () {} }; },
    querySelector: function () { return null; },
    body: { insertBefore: function () {} },
  };
  const context = {
    console: console,
    Promise: Promise,
    setTimeout: setTimeout,
    clearTimeout: clearTimeout,
    Date: Date,
    JSON: JSON,
    Object: Object,
    Array: Array,
    String: String,
    Number: Number,
    Error: Error,
    CustomEvent: function CustomEvent(type) { this.type = type; },
    dispatchEvent: function () {},
    document: document,
    localStorage: local,
    sessionStorage: session,
    location: { pathname: '/setting/profile.html', href: '' },
    fetch: function (url, init) {
      const method = (init && init.method) || 'GET';
      const body = init && init.body ? JSON.parse(init.body) : null;
      calls.push({ url: String(url), method: method, body: body });
      if (String(url).indexOf('profile.php') < 0) {
        return Promise.resolve({ status: 404, json: function () { return Promise.resolve({ ok: false }); } });
      }
      if (method === 'POST') {
        if (opts.postFail) {
          return Promise.resolve({ status: 500, json: function () { return Promise.resolve({ ok: false, error: 'save_failed' }); } });
        }
        serverProfile = Object.assign({}, serverProfile, body, { synced: true, userId: 'u1' });
        const saved = serverProfile;
        return Promise.resolve({ status: 200, json: function () { return Promise.resolve({ ok: true, profile: saved }); } });
      }
      if (opts.getFail) {
        return Promise.resolve({ status: 500, json: function () { return Promise.resolve({ ok: false }); } });
      }
      return Promise.resolve({ status: 200, json: function () { return Promise.resolve({ ok: true, profile: serverProfile }); } });
    },
    __KPI_AUTH: {
      resolveAuthBase: function () { return '/api/v1'; },
      me: function () {
        if (opts.authed === false) return Promise.resolve({ status: 401, data: {} });
        return Promise.resolve({ status: 200, data: { ok: true, userId: 'u1' } });
      },
      assertCanMutateUserData: function () { return true; },
    },
    KpiYearStore: {
      getStore: function () {
        try { return JSON.parse(local.getItem('kpiNavigator.kpiYearStore') || 'null'); }
        catch (e) { return null; }
      },
    },
    __KPI_DATA_GATEWAY: opts.freshStore ? {
      enableSessionSync: function (baseUrl) {
        if (opts.storeInitFail) throw new Error('init');
        calls.push({ url: String(baseUrl), method: 'INIT', body: { authMode: 'session', hasToken: false } });
        document.dispatchEvent({ type: 'kpi:storeHydrateSettled' });
        return { enabled: true, authMode: 'session', baseUrl: baseUrl };
      },
      pushToServerWhenReady: function () {
        calls.push({ url: 'store', method: 'PUT', body: null });
        if (opts.crossUser) return Promise.resolve({ ok: false, error: 'stale_account' });
        if (opts.storeFail) return Promise.resolve({ ok: false, error: 'store_push_failed' });
        return Promise.resolve({ ok: true });
      },
    } : {
      pushToServerWhenReady: function () {
        calls.push({ url: 'store', method: 'PUT', body: null });
        if (opts.storeFail) return Promise.resolve({ ok: false, error: 'store_push_failed' });
        return Promise.resolve({ ok: true });
      },
    },
  };
  context.window = context;
  context.globalThis = context;
  vm.createContext(context);
  vm.runInContext(BT, context);
  vm.runInContext(PS, context);
  return {
    context: context,
    local: local,
    calls: calls,
    field: field,
    profile: function () { return serverProfile; },
  };
}

function metaType(local) {
  try {
    const store = JSON.parse(local.getItem('kpiNavigator.kpiYearStore') || 'null');
    return store && store.meta && store.meta.businessType ? store.meta.businessType : '';
  } catch (e) {
    return '';
  }
}

function posts(calls) {
  return calls.filter(function (c) { return c.method === 'POST'; });
}

const populated = {
  synced: true,
  userId: 'u1',
  businessName: 'Server Bistro',
  companyName: 'Server Co',
  businessType: 'restaurant',
  genre: 'cafe',
  country: 'Japan',
  stateRegion: 'Tokyo',
  city: 'Shibuya',
  currency: 'JPY',
};

async function flush() {
  await new Promise(function (r) { setTimeout(r, 20); });
}

async function main() {
  const stale = { businessName: 'Stale Local', company: 'Stale Co', businessType: 'hotel', genre: 'old', country: 'US', state: 'CA', currency: 'USD', timezone: 'Asia/Tokyo', kpiFocus: 'sales' };
  const storeRestaurant = { meta: { businessType: 'restaurant', openingDate: '2024-04-01', schemaVersion: 4 }, timeline: { dailySales: {} }, years: {} };

  const display = boot({ profile: populated, store: storeRestaurant, localProfile: stale });
  await flush();
  const shown = await display.context.__KPI_PROFILE_SERVER.hydrateDisplay({
    onReady: function (view) { display.shown = view; },
    onEmpty: function () { display.empty = true; },
    onUnavailable: function () { display.bad = true; },
  });
  check(shown.source === 'server' && display.shown && display.shown.businessName === 'Server Bistro', '1 display hydrates server business name');
  check(display.shown.company === 'Server Co' && display.shown.country === 'Japan', '1 display hydrates the rest of the server profile');
  check(!display.empty && !display.bad, '1 populated server profile is not treated as empty');

  const edit = boot({ profile: populated, store: storeRestaurant, localProfile: stale });
  await flush();
  const edited = await edit.context.__KPI_PROFILE_SERVER.hydrateEditForm({});
  check(edited.source === 'server' && edit.field('profile-business-name').value === 'Server Bistro', '2 edit hydrates server business name');
  check(edit.field('profile-company').value === 'Server Co', '2 edit hydrates server company');
  check(edit.field('profile-business-name').value !== 'Stale Local', '3 stale local name does not override server');
  check(edit.field('profile-timezone').value === 'Asia/Tokyo' && edit.field('profile-kpi-focus').value === 'sales', 'local-only timezone and focus still come from cache');

  const retailStore = { meta: { businessType: 'retail', openingDate: '2024-04-01', schemaVersion: 4 }, timeline: { dailySales: {} }, years: {} };
  const canonical = boot({ profile: populated, store: retailStore, localProfile: stale });
  await flush();
  const canonView = await canonical.context.__KPI_PROFILE_SERVER.hydrateDisplay({});
  check(canonView.profile.businessType === 'retail' && canonView.profile.businessName === 'Server Bistro', '8 canonical store business type wins on read');

  const same = boot({ profile: populated, store: storeRestaurant, localProfile: stale });
  await flush();
  same.calls.length = 0;
  same.local._writes.length = 0;
  const saved = await same.context.__KPI_PROFILE_SERVER.commitProfileEdit({
    businessName: 'Server Bistro',
    company: 'Server Co',
    businessType: 'restaurant',
    genre: 'cafe',
    country: 'Japan',
    state: 'Tokyo',
    city: 'Shibuya',
    currency: 'JPY',
    timezone: 'Asia/Tokyo',
    kpiFocus: 'sales',
  });
  const postList = posts(same.calls);
  check(saved.ok === true && postList.length === 1 && postList[0].body.businessName === 'Server Bistro', '4 successful save writes the server profile');
  check(same.local.getItem('kpi-profile-last') != null && same.profile().businessName === 'Server Bistro', '5 cache updates after the successful server write');
  const cached = JSON.parse(same.local.getItem('kpi-profile-last'));
  check(cached.timezone === 'Asia/Tokyo' && cached.kpiFocus === 'sales' && cached.city === 'Shibuya', '14 unrelated and local-only fields stay in the saved cache');
  check(postList[0].body.genre === 'cafe' && postList[0].body.city === 'Shibuya' && !('openingDate' in postList[0].body) && !('timezone' in postList[0].body), '13 14 profile payload keeps genre and city and omits opening date and timezone');

  const failed = boot({ profile: populated, store: storeRestaurant, localProfile: null, postFail: true });
  await flush();
  failed.local.removeItem('kpi-profile-last');
  const failedSave = await failed.context.__KPI_PROFILE_SERVER.commitProfileEdit({
    businessName: 'Nope',
    company: 'Nope Co',
    businessType: 'retail',
    country: 'Japan',
    state: 'Tokyo',
    currency: 'JPY',
  });
  check(failedSave.ok === false && failed.local.getItem('kpi-profile-last') == null, '6 server failure does not update cache or report success');
  check(metaType(failed.local) === 'restaurant', '6 failed profile copy rolls the canonical type back');
  check(failed.profile().businessName === 'Server Bistro', '6 failed save does not replace the server profile');

  const invalid = boot({ profile: populated, store: storeRestaurant });
  await flush();
  invalid.calls.length = 0;
  const blocked = await invalid.context.__KPI_PROFILE_SERVER.commitProfileEdit({
    businessName: '',
    company: '',
    businessType: '',
    country: '',
    state: '',
    currency: '',
  });
  check(blocked.ok === false && blocked.error === 'required' && posts(invalid.calls).length === 0, '7 required fields block an incomplete save');

  const changed = boot({ profile: populated, store: storeRestaurant });
  await flush();
  changed.calls.length = 0;
  const changedSave = await changed.context.__KPI_PROFILE_SERVER.commitProfileEdit({
    businessName: 'Server Bistro',
    company: 'Server Co',
    businessType: 'hotel',
    genre: 'cafe',
    country: 'Japan',
    state: 'Tokyo',
    city: 'Shibuya',
    currency: 'JPY',
  });
  const changedPosts = posts(changed.calls);
  const putBeforePost = changed.calls.findIndex(function (c) { return c.method === 'PUT'; }) < changed.calls.findIndex(function (c) { return c.method === 'POST'; });
  check(changedSave.ok === true && putBeforePost && changedPosts[0].body.businessType === 'hotel' && metaType(changed.local) === 'hotel', '9 business type edit updates store then the profile copy');

  const fresh = boot({ profile: populated, store: storeRestaurant });
  await flush();
  fresh.local.clear();
  const restored = await fresh.context.__KPI_PROFILE_SERVER.hydrateDisplay({});
  check(restored.profile.businessName === 'Server Bistro' && fresh.profile().businessName === 'Server Bistro', '10 11 clearing local storage does not remove the server profile');

  const down = boot({ profile: populated, store: storeRestaurant, localProfile: stale, getFail: true });
  await flush();
  let unavailable = false;
  const downRes = await down.context.__KPI_PROFILE_SERVER.hydrateDisplay({
    onReady: function () { unavailable = 'painted'; },
    onUnavailable: function () { unavailable = true; },
  });
  check(downRes.source === 'unavailable' && unavailable === true, 'API failure does not paint stale local data');

  const emptyServer = { synced: false, userId: 'u1' };
  const migrate = boot({
    profile: emptyServer,
    store: { meta: { openingDate: '2024-04-01', schemaVersion: 4 }, timeline: { dailySales: {} }, years: {} },
    localProfile: {
      businessName: 'Local Only',
      company: 'Local Co',
      businessType: 'fitness',
      country: 'Japan',
      state: 'Osaka',
      currency: 'JPY',
    },
  });
  await flush();
  migrate.calls.length = 0;
  const migrated = await migrate.context.__KPI_PROFILE_SERVER.hydrateDisplay({});
  check(migrated.source === 'server' && migrate.profile().businessName === 'Local Only' && posts(migrate.calls).length === 1, 'empty server row migrates compatible local values once');
  migrate.calls.length = 0;
  await migrate.context.__KPI_PROFILE_SERVER.hydrateDisplay({});
  check(posts(migrate.calls).length === 0 && migrate.profile().businessName === 'Local Only', 'migration does not run again or overwrite the saved server row');

  const keep = boot({ profile: populated, store: storeRestaurant, localProfile: { businessName: 'Other', genre: 'should-not-copy', company: 'Other Co' } });
  await flush();
  keep.calls.length = 0;
  await keep.context.__KPI_PROFILE_SERVER.hydrateDisplay({});
  check(posts(keep.calls).length === 0 && keep.profile().businessName === 'Server Bistro' && keep.profile().genre === 'cafe', 'populated server row is not patched from local cache');

  const ps = PS;
  check(ps.indexOf('openingDate') < 0, '13 profile client does not invent an opening date field');
  const readiness = fs.readFileSync(path.join(ROOT, 'js', 'kpi-navigation-readiness.js'), 'utf8');
  check(readiness.indexOf('openingDate') >= 0 && readiness.indexOf('businessName') >= 0 && readiness.indexOf('businessTypeSet') >= 0, '12 readiness still requires profile fields and opening date');
  const setup = fs.readFileSync(path.join(ROOT, 'js', 'kpi-setup-step0.js'), 'utf8');
  check(setup.indexOf('function writeOpeningDate') >= 0 && setup.indexOf('store.meta.openingDate') >= 0, '13 opening date still writes store.meta.openingDate');

  const demo = {
    businessName: 'Forge Bistro Demo',
    company: 'Forge Laboratory Demo',
    businessType: 'restaurant',
    genre: 'Italian',
    country: 'Japan',
    state: 'Kanagawa',
    city: 'Fujisawa',
    currency: 'JPY',
  };
  const direct = boot({ freshStore: true, profile: { synced: false, userId: 'u1' } });
  check(direct.local.getItem('kpi-profile-last') == null && direct.local.getItem('kpi-profile-tmp') == null, '04 fresh browser has no profile cache');
  check(direct.local.getItem('kpiNavigator.storeSync') == null, '04 fresh browser has no Annual sync flag');
  const directSave = await direct.context.__KPI_PROFILE_SERVER.commitProfileEdit(demo);
  const directInit = direct.calls.filter(function (c) { return c.method === 'INIT'; });
  const directPuts = direct.calls.filter(function (c) { return c.method === 'PUT'; });
  const directPosts = posts(direct.calls);
  check(directSave.ok === true, '04 first Business Type save succeeds');
  check(directInit.length === 1 && directInit[0].url.indexOf('/api/v1/store.php') >= 0 && directInit[0].body.authMode === 'session' && directInit[0].body.hasToken === false, '04 save enables authenticated session store sync');
  check(directPuts.length >= 1 && directPosts.length === 1 && direct.calls.indexOf(directPuts[0]) < direct.calls.indexOf(directPosts[0]), '04 canonical store write happens before profile.php');
  check(metaType(direct.local) === 'restaurant' && direct.local.getItem('kpi-profile-last') != null, '04 cache updates after both writes');

  const unchanged = boot({ freshStore: true, profile: populated, store: storeRestaurant });
  const unchangedSave = await unchanged.context.__KPI_PROFILE_SERVER.commitProfileEdit({
    businessName: 'Server Bistro',
    company: 'Server Co',
    businessType: 'restaurant',
    country: 'Japan',
    state: 'Tokyo',
    currency: 'JPY',
  });
  check(unchangedSave.ok === true && unchanged.calls.filter(function (c) { return c.method === 'PUT'; }).length === 0 && posts(unchanged.calls).length === 1, '04 unchanged Business Type does not rewrite the store');

  const changedFresh = boot({ freshStore: true, profile: populated, store: storeRestaurant });
  const changedFreshSave = await changedFresh.context.__KPI_PROFILE_SERVER.commitProfileEdit({
    businessName: 'Server Bistro',
    company: 'Server Co',
    businessType: 'hotel',
    country: 'Japan',
    state: 'Tokyo',
    currency: 'JPY',
  });
  check(changedFreshSave.ok === true && metaType(changedFresh.local) === 'hotel' && posts(changedFresh.calls).length === 1, '04 existing Business Type change still saves');

  const initFail = boot({ freshStore: true, storeInitFail: true, profile: { synced: false, userId: 'u1' } });
  const initFailSave = await initFail.context.__KPI_PROFILE_SERVER.commitProfileEdit(demo);
  check(initFailSave.ok === false && posts(initFail.calls).length === 0 && initFail.local.getItem('kpi-profile-last') == null, '04 store initialization failure does not save');

  const writeFail = boot({ freshStore: true, storeFail: true, profile: { synced: false, userId: 'u1' } });
  const writeFailSave = await writeFail.context.__KPI_PROFILE_SERVER.commitProfileEdit(demo);
  check(writeFailSave.ok === false && posts(writeFail.calls).length === 0 && writeFail.local.getItem('kpi-profile-last') == null, '04 store write failure does not save');

  const copyFail = boot({ freshStore: true, postFail: true, profile: populated, store: storeRestaurant });
  const copyFailSave = await copyFail.context.__KPI_PROFILE_SERVER.commitProfileEdit({
    businessName: 'Nope',
    company: 'Nope Co',
    businessType: 'hotel',
    country: 'Japan',
    state: 'Tokyo',
    currency: 'JPY',
  });
  check(copyFailSave.ok === false && copyFail.local.getItem('kpi-profile-last') == null && metaType(copyFail.local) === 'restaurant' && copyFail.profile().businessName === 'Server Bistro', '04 profile failure rolls the canonical type back');

  const loggedOut = boot({ freshStore: true, authed: false, profile: populated, store: storeRestaurant });
  const loggedOutSave = await loggedOut.context.__KPI_PROFILE_SERVER.commitProfileEdit(demo);
  check(loggedOutSave.ok === false && loggedOut.calls.filter(function (c) { return c.method === 'INIT'; }).length === 0 && posts(loggedOut.calls).length === 0, '04 logged-out save does not enable store sync');

  const cross = boot({ freshStore: true, crossUser: true, profile: populated, store: storeRestaurant });
  const crossSave = await cross.context.__KPI_PROFILE_SERVER.commitProfileEdit({
    businessName: 'Server Bistro',
    company: 'Server Co',
    businessType: 'hotel',
    country: 'Japan',
    state: 'Tokyo',
    currency: 'JPY',
  });
  check(crossSave.ok === false && posts(cross.calls).length === 0 && cross.local.getItem('kpi-profile-last') == null, '04 cross-user store rejection does not save');

  const gatewayJs = fs.readFileSync(path.join(ROOT, 'js', 'kpi-data-gateway.js'), 'utf8');
  const authPhp = fs.readFileSync(path.join(ROOT, 'api', 'v1', '_auth.php'), 'utf8');
  check(gatewayJs.indexOf('assertCanMutateUserData') >= 0 && gatewayJs.indexOf("authMode: 'session'") >= 0, '04 store sync stays on the session gateway');
  check(authPhp.indexOf('stale_account') >= 0, '04 expected-user mismatch stays rejected');

  const pages = [
    ['setting/profile.html', 'hydrateDisplay', 'サーバーのプロフィールを確認できません。'],
    ['en/setting/profile.html', 'hydrateDisplay', 'The server profile could not be confirmed.'],
    ['zh-tw/setting/profile.html', 'hydrateDisplay', '無法確認伺服器上的個人資料。'],
    ['setting/profile_edit.html', 'commitProfileEdit', '保存できませんでした。入力内容はこの画面に残しています。'],
    ['en/setting/profile_edit.html', 'commitProfileEdit', 'The profile could not be saved. Your entries are still in this form.'],
    ['zh-tw/setting/profile_edit.html', 'commitProfileEdit', '無法儲存。輸入內容仍留在此畫面。'],
  ];
  pages.forEach(function (row) {
    const text = fs.readFileSync(path.join(ROOT, row[0]), 'utf8');
    const edit = row[0].indexOf('profile_edit') >= 0;
    check(text.indexOf(row[1]) >= 0 && text.indexOf(row[2]) >= 0, '15 ' + row[0] + ' uses the server-first path');
    check(text.indexOf('kpi-profile-server.js?v=20261008-p04') >= 0, '15 ' + row[0] + ' cache bust');
    check(text.indexOf('kpi-data-gateway.js?v=20260927-bt1') >= 0, '04 ' + row[0] + ' can boot store sync');
    if (edit) {
      check(text.indexOf('.then(goProfile).catch(goProfile)') < 0 && text.indexOf('if (res && res.ok)') >= 0, '6 15 ' + row[0] + ' navigates only after ok');
      check(text.indexOf('localStorage.setItem(\'kpi-profile-last\'') < 0, '5 15 ' + row[0] + ' does not cache before save');
      check(text.indexOf('setBusinessType(fromServer)') >= 0, '9 ' + row[0] + ' still bridges an empty meta type');
    } else {
      check(text.indexOf('hydrateFromServerProfile') >= 0 && text.indexOf('paintIndustry') >= 0, '8 ' + row[0] + ' still repaints industry');
      check(text.indexOf("localStorage.getItem('kpi-profile-last')") < 0, '1 ' + row[0] + ' does not load from local cache');
    }
  });

  if (fails.length) {
    fails.forEach(function (f) { console.error('FAIL ' + f); });
    process.exit(1);
  }
  console.log('PROFILE-PERSISTENCE-02 checks passed');
}

main().catch(function (err) {
  console.error(err);
  process.exit(1);
});
