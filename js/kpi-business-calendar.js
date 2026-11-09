/**
 * KPN-RG-CAL-01 — operating-year business calendar.
 * Saves years[operatingYear].plan.businessCalendar only.
 * Does not write timeline.businessDays or sales, and does not decide conflict winners.
 */
(function (global) {
  'use strict';

  if (global.KpiBusinessCalendar && global.KpiBusinessCalendar.__ready) return;

  var STORE_KEY = 'kpiNavigator.kpiYearStore';
  var SYNC_KEY = 'kpiNavigator.storeSync';
  var MODES = {
    fixed: 'fixed-weekday',
    irregular: 'irregular',
    always: 'always-open',
  };

  function isFiniteNumber(value) {
    return typeof value === 'number' && isFinite(value);
  }

  function normalizeClosedWeekdays(days) {
    if (!Array.isArray(days) || !days.length) return null;
    var seen = {};
    var out = [];
    var i;
    for (i = 0; i < days.length; i++) {
      var n = days[i];
      if (typeof n !== 'number' || n !== Math.floor(n) || n < 0 || n > 6 || seen[n]) continue;
      seen[n] = true;
      out.push(n);
    }
    if (!out.length || out.length !== days.length) return null;
    out.sort(function (a, b) {
      return a - b;
    });
    return out;
  }

  function normalizeRecord(raw) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
    var mode = raw.mode;
    if (mode === MODES.irregular || mode === MODES.always) return { mode: mode };
    if (mode !== MODES.fixed) return null;
    var days = normalizeClosedWeekdays(raw.closedWeekdays);
    if (!days) return null;
    return { mode: MODES.fixed, closedWeekdays: days };
  }

  function operatingYearOf(store) {
    var n = store && store.meta ? Number(store.meta.operatingYear) : NaN;
    return isFiniteNumber(n) ? n : null;
  }

  function yearRecord(store, year, create) {
    var y = Number(year);
    if (!isFiniteNumber(y)) return null;
    if (!store || typeof store !== 'object') return null;
    if (!store.years || typeof store.years !== 'object' || Array.isArray(store.years)) {
      if (!create) return null;
      store.years = {};
    }
    var rec = store.years[y];
    if (!rec || typeof rec !== 'object' || Array.isArray(rec)) {
      if (!create) return null;
      rec = store.years[y] = { year: y };
    }
    if (!rec.plan || typeof rec.plan !== 'object' || Array.isArray(rec.plan)) {
      if (!create) return null;
      rec.plan = {};
    }
    return rec;
  }

  function readRecord(store, year) {
    var rec = yearRecord(store, year, false);
    if (!rec) return null;
    return normalizeRecord(rec.plan.businessCalendar);
  }

  function writeRecord(store, year, raw) {
    var record = normalizeRecord(raw);
    if (!record) return { ok: false, reason: 'invalid-record' };
    var y = Number(year);
    var oy = operatingYearOf(store);
    if (oy == null || y !== oy) return { ok: false, reason: 'not-operating-year' };
    var rec = yearRecord(store, y, true);
    if (!rec) return { ok: false, reason: 'no-store' };
    rec.plan.businessCalendar = record;
    return { ok: true, record: readRecord(store, y) };
  }

  function own(map, iso) {
    return !!(map && typeof map === 'object' && Object.prototype.hasOwnProperty.call(map, iso));
  }

  function explicitFlag(map, iso) {
    if (!own(map, iso)) return null;
    var value = map[iso];
    if (value === true) return true;
    if (value === false) return false;
    return null;
  }

  function salesValue(map, iso) {
    if (!own(map, iso)) return null;
    var value = map[iso];
    if (typeof value === 'string' && value.trim() !== '' && isFinite(Number(value))) value = Number(value);
    if (!isFiniteNumber(value) || value < 0) return null;
    return value;
  }

  function isoParts(iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso || ''));
    if (!m) return null;
    var y = Number(m[1]);
    var month = Number(m[2]);
    var day = Number(m[3]);
    var dt = new Date(y, month - 1, day);
    if (dt.getFullYear() !== y || dt.getMonth() !== month - 1 || dt.getDate() !== day) return null;
    return { year: y, dow: dt.getDay() };
  }

  function provisional(record, dow) {
    if (!record) return { status: 'unset', moldApplied: false };
    if (record.mode === MODES.fixed) {
      var closed = record.closedWeekdays.indexOf(dow) >= 0;
      return { status: closed ? 'provisional-closed' : 'provisional-open', moldApplied: true };
    }
    if (record.mode === MODES.irregular || record.mode === MODES.always) {
      return { status: 'provisional-open', moldApplied: true };
    }
    return { status: 'unset', moldApplied: false };
  }

  /**
   * Pure classification. Does not read or write a store.
   * salesEntered is true only for an existing finite sales value >= 0.
   */
  function resolveDay(input) {
    var src = input || {};
    var parts = isoParts(src.iso);
    if (!parts) return { status: 'invalid-date', moldApplied: false, salesEntered: false };
    var oy = Number(src.operatingYear);
    if (!isFiniteNumber(oy)) return { status: 'unset', moldApplied: false, salesEntered: false };
    if (parts.year < oy) return { status: 'past', moldApplied: false, salesEntered: salesValue(src.dailySales, src.iso) != null };
    if (parts.year !== oy) return { status: 'other-year', moldApplied: false, salesEntered: salesValue(src.dailySales, src.iso) != null };
    var sales = salesValue(src.dailySales, src.iso);
    var entered = sales != null;
    var flag = explicitFlag(src.businessDays, src.iso);
    if (flag === true) return { status: 'explicit-open', moldApplied: false, salesEntered: entered };
    if (flag === false && entered) return { status: 'conflict', moldApplied: false, salesEntered: true };
    if (flag === false) return { status: 'explicit-closed', moldApplied: false, salesEntered: false };
    if (entered) return { status: 'actual-open', moldApplied: false, salesEntered: true };
    var mold = provisional(normalizeRecord(src.calendar), parts.dow);
    mold.salesEntered = false;
    return mold;
  }

  function copy(lang) {
    var table = {
      ja: {
        label: '営業形態',
        fixed: '定休日あり',
        irregular: '不定休',
        always: '年中無休',
        days: '定休日',
        week: ['日', '月', '火', '水', '木', '金', '土'],
        hint: '今年の未入力日と未来日だけに使います。入力済みの売上と、個別の営業・休店は変更しません。',
        year: '運用年',
        need: '営業形態を選択してください。',
        needDay: '定休日の曜日を1つ以上選択してください。',
        saved: '営業形態を保存しました。',
        localSaved: 'このブラウザに営業形態を保存しました。',
        failed: '営業形態を保存できませんでした。',
        noStore: '店舗データがないため、営業形態は保存していません。',
        noYear: '運用年がないため、営業形態は保存していません。',
      },
      en: {
        label: 'Business week',
        fixed: 'Fixed closing days',
        irregular: 'Irregular closing',
        always: 'Open every day',
        days: 'Closing weekdays',
        week: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        hint: 'Applies only to unentered and future days this year. Entered sales and explicit open or closed days stay as they are.',
        year: 'Operating year',
        need: 'Choose a business week.',
        needDay: 'Choose at least one closing weekday.',
        saved: 'Business week saved.',
        localSaved: 'Business week saved in this browser.',
        failed: 'Could not save the business week.',
        noStore: 'No store data, so the business week was not saved.',
        noYear: 'No operating year, so the business week was not saved.',
      },
      'zh-tw': {
        label: '營業型態',
        fixed: '有固定公休',
        irregular: '不定期公休',
        always: '全年無休',
        days: '公休日',
        week: ['日', '一', '二', '三', '四', '五', '六'],
        hint: '只套用到本年度尚未輸入與未來的日期。已輸入的營業額，以及個別的營業、公休設定都不會被改寫。',
        year: '營運年',
        need: '請選擇營業型態。',
        needDay: '請至少選擇一個公休日。',
        saved: '已儲存營業型態。',
        localSaved: '已在此瀏覽器儲存營業型態。',
        failed: '無法儲存營業型態。',
        noStore: '沒有店鋪資料，因此未儲存營業型態。',
        noYear: '沒有營運年，因此未儲存營業型態。',
      },
    };
    var key = String(lang || '').toLowerCase();
    if (key.indexOf('zh') === 0) return table['zh-tw'];
    if (key.indexOf('en') === 0) return table.en;
    return table.ja;
  }

  function pageLang() {
    try {
      return (document.documentElement.getAttribute('lang') || '').toLowerCase();
    } catch (_e) {
      return 'ja';
    }
  }

  function readSyncEnabled() {
    try {
      var raw = localStorage.getItem(SYNC_KEY);
      var parsed = raw ? JSON.parse(raw) : null;
      return !!(parsed && parsed.enabled);
    } catch (_e) {
      return false;
    }
  }

  function storeUrl() {
    try {
      var raw = localStorage.getItem(SYNC_KEY);
      var parsed = raw ? JSON.parse(raw) : null;
      if (parsed && parsed.baseUrl) return String(parsed.baseUrl);
    } catch (_e) {}
    var path = (global.location && global.location.pathname) || '';
    var m = path.match(/^(.*?\/kpi-navigator)(?:\/|$)/);
    return (m ? m[1] : '') + '/api/v1/store.php';
  }

  function readLocalStore() {
    try {
      var raw = localStorage.getItem(STORE_KEY);
      var parsed = raw ? JSON.parse(raw) : null;
      return parsed && typeof parsed === 'object' ? parsed : null;
    } catch (_e) {
      return null;
    }
  }

  function writeLocalStore(store) {
    localStorage.setItem(STORE_KEY, JSON.stringify(store));
  }

  function formRecord(root) {
    var checked = root.querySelector('input[name="pref-cal-mode"]:checked');
    if (!checked) return { empty: true };
    if (checked.value !== MODES.fixed) return { record: { mode: checked.value } };
    var days = [];
    var boxes = root.querySelectorAll('input[name="pref-cal-day"]:checked');
    Array.prototype.forEach.call(boxes, function (box) {
      days.push(Number(box.value));
    });
    return { record: { mode: MODES.fixed, closedWeekdays: days } };
  }

  function paint(root, store) {
    var lang = copy(pageLang());
    var year = operatingYearOf(store);
    var saved = year == null ? null : readRecord(store, year);
    var days = '';
    var d;
    for (d = 0; d < 7; d++) {
      var on = saved && saved.closedWeekdays && saved.closedWeekdays.indexOf(d) >= 0;
      days +=
        '<label><input type="checkbox" name="pref-cal-day" value="' +
        d +
        '"' +
        (on ? ' checked' : '') +
        '> ' +
        lang.week[d] +
        '</label> ';
    }
    function radio(mode, label) {
      return (
        '<label><input type="radio" name="pref-cal-mode" value="' +
        mode +
        '"' +
        (saved && saved.mode === mode ? ' checked' : '') +
        '> ' +
        label +
        '</label> '
      );
    }
    root.innerHTML =
      '<label>' +
      lang.label +
      (year == null ? '' : '（' + lang.year + ' ' + year + '）') +
      '</label>' +
      '<div>' +
      radio(MODES.fixed, lang.fixed) +
      radio(MODES.irregular, lang.irregular) +
      radio(MODES.always, lang.always) +
      '</div>' +
      '<div data-cal-days' +
      (saved && saved.mode === MODES.fixed ? '' : ' hidden') +
      '><span>' +
      lang.days +
      '</span> ' +
      days +
      '</div>' +
      '<p class="profile-preferences-hint">' +
      lang.hint +
      '</p>' +
      '<p data-cal-status role="status"></p>';
    root.addEventListener('change', function (ev) {
      var target = ev.target;
      if (!target || target.name !== 'pref-cal-mode') return;
      var box = root.querySelector('[data-cal-days]');
      if (box) box.hidden = target.value !== MODES.fixed;
    });
  }

  function setStatus(root, text) {
    var node = root.querySelector('[data-cal-status]');
    if (node) node.textContent = text || '';
  }

  function saveFromPreferences(root) {
    var lang = copy(pageLang());
    var picked = formRecord(root);
    if (picked.empty) return Promise.resolve({ ok: true, skipped: true });
    var record = normalizeRecord(picked.record);
    if (!record) {
      setStatus(root, picked.record && picked.record.mode === MODES.fixed ? lang.needDay : lang.need);
      return Promise.resolve({ ok: false, reason: 'invalid-record' });
    }
    var local = readLocalStore();
    if (readSyncEnabled()) {
      if (!local) local = { meta: {} };
      return fetch(storeUrl(), { credentials: 'same-origin' })
        .then(function (res) {
          return res.json().then(function (data) {
            var store = data && data.store && typeof data.store === 'object' ? data.store : null;
            if (!res.ok || !data || data.ok !== true || !store) {
              setStatus(root, lang.failed);
              return { ok: false, reason: 'get-failed' };
            }
            var year = operatingYearOf(store);
            if (year == null) {
              setStatus(root, lang.noYear);
              return { ok: false, reason: 'not-operating-year' };
            }
            var written = writeRecord(store, year, record);
            if (!written.ok) {
              setStatus(root, lang.failed);
              return written;
            }
            var body = { store: store, expectedRevision: data.revision == null ? null : data.revision };
            var headers = { 'Content-Type': 'application/json' };
            var auth = global.__KPI_AUTH;
            if (auth && typeof auth.attachExpectedUser === 'function') {
              var attached = auth.attachExpectedUser(headers, body);
              headers = attached.headers;
              body = attached.body;
            }
            return fetch(storeUrl(), {
              method: 'PUT',
              credentials: 'same-origin',
              headers: headers,
              body: JSON.stringify(body),
            }).then(function (putRes) {
              return putRes.json().then(function (putData) {
                if (!putRes.ok || !putData || putData.ok !== true) {
                  setStatus(root, lang.failed);
                  return { ok: false, reason: 'put-failed' };
                }
                try {
                  var mirror = readLocalStore() || store;
                  writeRecord(mirror, year, record);
                  writeLocalStore(mirror);
                } catch (_e) {}
                setStatus(root, lang.saved);
                return { ok: true, remote: true };
              });
            });
          });
        })
        .catch(function () {
          setStatus(root, lang.failed);
          return { ok: false, reason: 'network' };
        });
    }
    if (!local) {
      setStatus(root, lang.noStore);
      return Promise.resolve({ ok: false, reason: 'no-store' });
    }
    var yearLocal = operatingYearOf(local);
    if (yearLocal == null) {
      setStatus(root, lang.noYear);
      return Promise.resolve({ ok: false, reason: 'not-operating-year' });
    }
    var localWrite = writeRecord(local, yearLocal, record);
    if (!localWrite.ok) {
      setStatus(root, lang.failed);
      return Promise.resolve(localWrite);
    }
    try {
      writeLocalStore(local);
    } catch (_e2) {
      setStatus(root, lang.failed);
      return Promise.resolve({ ok: false, reason: 'local-write' });
    }
    setStatus(root, lang.localSaved);
    return Promise.resolve({ ok: true, local: true });
  }

  function mountPreferences() {
    var root = document.getElementById('pref-business-calendar');
    if (!root || root.getAttribute('data-cal-ready') === '1') return;
    root.setAttribute('data-cal-ready', '1');
    paint(root, readLocalStore());
    var form = document.getElementById('preferences-form');
    if (!form) return;
    form.addEventListener(
      'submit',
      function (ev) {
        var picked = formRecord(root);
        if (picked.empty) return;
        if (!normalizeRecord(picked.record)) {
          ev.preventDefault();
          ev.stopImmediatePropagation();
          setStatus(root, picked.record && picked.record.mode === MODES.fixed ? copy(pageLang()).needDay : copy(pageLang()).need);
        } else {
          saveFromPreferences(root);
        }
      },
      true
    );
  }

  function boot() {
    if (!global.document) return;
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', mountPreferences);
    } else {
      mountPreferences();
    }
  }

  global.KpiBusinessCalendar = {
    __ready: true,
    MODES: MODES,
    normalizeRecord: normalizeRecord,
    readRecord: readRecord,
    writeRecord: writeRecord,
    resolveDay: resolveDay,
    copy: copy,
    operatingYearOf: operatingYearOf,
  };
  boot();
})(typeof window !== 'undefined' ? window : globalThis);
