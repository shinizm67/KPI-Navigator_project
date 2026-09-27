/**
 * BR-ONBOARDING-01 Phase 2 — Business Profile Step 0 (Hard Required 7).
 * Opened from the Navigation Readiness guard. One implementation for JP / EN / ZH-TW
 * and Sci-Fi / Office (body.office-mode).
 *
 * profile.php PUT overwrites every column: always GET the current profile, merge only
 * the fields this form changed, then PUT the full payload. Never partial-PUT.
 * Never writes store.meta.setup.
 */
(function (global) {
  'use strict';

  if (global.KpiSetupStep0 && global.KpiSetupStep0.__ready) return;

  var STORE_KEY = 'kpiNavigator.kpiYearStore';
  var PROFILE_LOCAL_KEY = 'kpi-profile-last';
  var CURRENCY_LOCAL_KEY = 'kpi-currency';
  var PROFILE_FIELDS = [
    'businessName',
    'companyName',
    'businessType',
    'genre',
    'locale',
    'country',
    'stateRegion',
    'city',
    'currency',
  ];
  var FORM_FIELDS = [
    'businessName',
    'companyName',
    'businessType',
    'country',
    'stateRegion',
    'currency',
    'city',
    'genre',
  ];

  var COPY = {
    ja: {
      kicker: 'KPN SETUP — STEP 0',
      title: 'Business Profile',
      lead: 'KPN を始めるために、必須 7 項目を入力してください。任意項目は空欄のままでも保存できます。',
      required: '必須',
      optional: '任意',
      sectionRequired: '必須項目',
      sectionOptional: '任意項目',
      businessName: '屋号 / サービス名 / 店名',
      companyName: '会社名',
      businessType: '業種',
      openingDate: 'Business 開始年月',
      country: '国',
      regionJP: '都道府県',
      regionUS: '州',
      regionDefault: '州 / 都道府県 / Region',
      currency: '通貨',
      city: '市区町村',
      genre: 'ジャンル',
      year: '年',
      month: '月',
      day: '日（任意）',
      dateHint: '日は任意です。未入力の場合は 1 日として保存します。',
      dateInvalid: '存在しない日付です。',
      currencyHint: '国に合わせて候補を提案します。自由に変更できます。',
      regionHint: '候補にない地域もそのまま入力できます。',
      progress: '必須 {done} / {total} 入力済み',
      remaining: '残り: {list}',
      allDone: '必須項目はすべて入力済みです。',
      back: '戻る',
      save: '保存する',
      saving: '保存中…',
      loading: '読み込み中…',
      loadFailed: 'プロフィールを読み込めませんでした。時間をおいてもう一度お試しください。',
      saveFailed: '保存できませんでした。入力内容はそのままです。もう一度お試しください。',
      storeWarn: 'Business 開始年月・業種のサーバ同期がまだ完了していません。画面を再読み込みすると再送されます。',
      savedTitle: 'Business Profile を保存しました',
      savedBody: '次のステップ（過去データ・今年度・年間目標）は準備中です。このまま KPN に進めます。',
      next: 'KPN に進む',
    },
    en: {
      kicker: 'KPN SETUP — STEP 0',
      title: 'Business Profile',
      lead: 'To start KPN, fill in the 7 required fields. Optional fields can stay blank.',
      required: 'Required',
      optional: 'Optional',
      sectionRequired: 'Required',
      sectionOptional: 'Optional',
      businessName: 'Business / Service / Store Name',
      companyName: 'Company Name',
      businessType: 'Business Type',
      openingDate: 'Business Start (Year / Month)',
      country: 'Country',
      regionJP: 'Prefecture',
      regionUS: 'State',
      regionDefault: 'State / Prefecture / Region',
      currency: 'Currency',
      city: 'City / Town',
      genre: 'Genre',
      year: 'Year',
      month: 'Month',
      day: 'Day (optional)',
      dateHint: 'Day is optional. If left blank, it is saved as the 1st.',
      dateInvalid: 'This date does not exist.',
      currencyHint: 'Suggested from the country. You can change it.',
      regionHint: 'You can type a region that is not in the list.',
      progress: 'Required {done} / {total} complete',
      remaining: 'Still needed: {list}',
      allDone: 'All required fields are complete.',
      back: 'Back',
      save: 'Save',
      saving: 'Saving…',
      loading: 'Loading…',
      loadFailed: 'Could not load your profile. Please try again in a moment.',
      saveFailed: 'Could not save. Your input is kept. Please try again.',
      storeWarn: 'Business Start and Business Type have not finished syncing to the server. Reloading the page will retry.',
      savedTitle: 'Business Profile saved',
      savedBody: 'The next steps (past data, current year, annual target) are not ready yet. You can continue to KPN.',
      next: 'Continue to KPN',
    },
    zh: {
      kicker: 'KPN SETUP — STEP 0',
      title: 'Business Profile',
      lead: '開始使用 KPN 前，請填寫 7 個必填項目。選填項目可以留空。',
      required: '必填',
      optional: '選填',
      sectionRequired: '必填項目',
      sectionOptional: '選填項目',
      businessName: '店名 / 服務名稱',
      companyName: '公司名稱',
      businessType: '產業',
      openingDate: 'Business 開始年月',
      country: '國家',
      regionJP: '都道府縣',
      regionUS: '州',
      regionDefault: '縣市 / 州 / 地區',
      currency: '貨幣',
      city: '城市',
      genre: '類型',
      year: '年',
      month: '月',
      day: '日（選填）',
      dateHint: '日為選填。未填寫時以 1 日儲存。',
      dateInvalid: '此日期不存在。',
      currencyHint: '會依國家提供建議，可自由變更。',
      regionHint: '清單中沒有的地區也可以直接輸入。',
      progress: '必填 {done} / {total} 已完成',
      remaining: '尚需填寫：{list}',
      allDone: '必填項目已全部完成。',
      back: '返回',
      save: '儲存',
      saving: '儲存中…',
      loading: '讀取中…',
      loadFailed: '無法讀取個人資料，請稍後再試。',
      saveFailed: '無法儲存。輸入內容已保留，請再試一次。',
      storeWarn: 'Business 開始年月與產業尚未完成伺服器同步。重新整理頁面後會再次傳送。',
      savedTitle: '已儲存 Business Profile',
      savedBody: '下一步（過去資料、本年度、年度目標）尚在準備中。可以直接進入 KPN。',
      next: '進入 KPN',
    },
  };

  function readiness() {
    return global.KpiNavigationReadiness || null;
  }

  function detectLang() {
    var r = readiness();
    if (r && typeof r.detectLang === 'function') return r.detectLang();
    var l = '';
    try {
      l = String(global.document.documentElement.getAttribute('lang') || '').toLowerCase();
    } catch (_e) {}
    if (l.indexOf('ja') === 0) return 'ja';
    if (l.indexOf('zh') === 0) return 'zh';
    return 'en';
  }

  function locationLocale(lang) {
    return lang === 'ja' ? 'ja' : lang === 'zh' ? 'zh-tw' : 'en';
  }

  function t(lang) {
    return COPY[lang] || COPY.en;
  }

  function fmt(s, vars) {
    return String(s).replace(/\{(\w+)\}/g, function (_m, k) {
      return vars[k] != null ? String(vars[k]) : '';
    });
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function trimmed(v) {
    return v == null ? '' : String(v).trim();
  }

  function loc() {
    return global.KpiProfileLocation || null;
  }

  function cur() {
    return global.KpiCurrency || null;
  }

  function bt() {
    return global.KpiBusinessType || null;
  }

  function resolveProfileApi() {
    if (global.__KPI_AUTH && typeof global.__KPI_AUTH.resolveAuthBase === 'function') {
      try {
        return global.__KPI_AUTH.resolveAuthBase().replace(/\/?$/, '') + '/profile.php';
      } catch (_e) {}
    }
    return '/kpi-navigator/api/v1/profile.php';
  }

  function fetchProfileFresh() {
    if (typeof global.fetch !== 'function') return Promise.resolve({ ok: false, profile: null });
    return global
      .fetch(resolveProfileApi(), {
        method: 'GET',
        credentials: 'include',
        cache: 'no-store',
        headers: { Accept: 'application/json' },
      })
      .then(function (res) {
        return res
          .json()
          .catch(function () {
            return null;
          })
          .then(function (data) {
            if (!res.ok || !data || data.ok !== true) return { ok: false, profile: null };
            return { ok: true, profile: data.profile || {} };
          });
      })
      .catch(function () {
        return { ok: false, profile: null };
      });
  }

  function profileShape(raw) {
    var p = raw && typeof raw === 'object' ? raw : {};
    var out = {};
    PROFILE_FIELDS.forEach(function (k) {
      out[k] = p[k] == null ? '' : String(p[k]);
    });
    if (!out.companyName && p.company != null) out.companyName = String(p.company);
    if (!out.businessType && p.industry != null) out.businessType = String(p.industry);
    if (!out.stateRegion && p.state != null) out.stateRegion = String(p.state);
    return out;
  }

  /**
   * Full payload for profile.php: current server values, with only changed form fields
   * replaced. Fields this form never edits (locale, and anything unchanged) are kept.
   */
  function mergeProfile(serverProfile, changes) {
    var merged = profileShape(serverProfile);
    Object.keys(changes || {}).forEach(function (k) {
      if (PROFILE_FIELDS.indexOf(k) >= 0) merged[k] = changes[k] == null ? '' : String(changes[k]);
    });
    return merged;
  }

  function readStore() {
    try {
      if (global.KpiYearStore && typeof global.KpiYearStore.getStore === 'function') {
        var mem = global.KpiYearStore.getStore();
        if (mem && typeof mem === 'object') return mem;
      }
    } catch (_e) {}
    return null;
  }

  function readOpeningDate() {
    var s = readStore();
    return s && s.meta ? trimmed(s.meta.openingDate) : '';
  }

  function writeOpeningDate(iso) {
    var store = readStore();
    if (!store) return false;
    if (!store.meta || typeof store.meta !== 'object') store.meta = {};
    store.meta.openingDate = iso;
    var gw = global.__KPI_DATA_GATEWAY;
    try {
      if (gw && typeof gw.setJson === 'function') {
        gw.setJson(STORE_KEY, store);
        return true;
      }
      localStorage.setItem(STORE_KEY, JSON.stringify(store));
      return true;
    } catch (_e) {
      return false;
    }
  }

  function writeLocalProfile(merged, currency) {
    try {
      var prev = {};
      try {
        prev = JSON.parse(localStorage.getItem(PROFILE_LOCAL_KEY) || '{}') || {};
      } catch (_eParse) {
        prev = {};
      }
      var next = Object.assign({}, prev, {
        businessName: merged.businessName,
        company: merged.companyName,
        industry: merged.businessType,
        genre: merged.genre,
        country: merged.country,
        state: merged.stateRegion,
        city: merged.city,
        currency: merged.currency,
      });
      localStorage.setItem(PROFILE_LOCAL_KEY, JSON.stringify(next));
      if (currency) localStorage.setItem(CURRENCY_LOCAL_KEY, currency);
    } catch (_e) {}
  }

  function saveProfileFull(merged) {
    var server = global.__KPI_PROFILE_SERVER;
    if (!server || typeof server.saveServerProfile !== 'function') {
      return Promise.resolve({ ok: false, error: 'profile_server_missing' });
    }
    return Promise.resolve(server.saveServerProfile(merged));
  }

  function pushStore() {
    var gw = global.__KPI_DATA_GATEWAY;
    if (!gw || typeof gw.pushToServerWhenReady !== 'function') {
      return Promise.resolve({ ok: false, skipped: true });
    }
    return Promise.resolve(gw.pushToServerWhenReady(12000)).catch(function () {
      return { ok: false };
    });
  }

  /* ---------- UI ---------- */

  var rootEl = null;
  var state = null;

  function ensureStyle() {
    if (!global.document || global.document.getElementById('kpi-s0-css')) return;
    var style = global.document.createElement('style');
    style.id = 'kpi-s0-css';
    style.textContent = [
      '#kpi-s0{position:fixed;inset:0;z-index:100001;display:flex;align-items:flex-start;justify-content:center;',
      'padding:32px 24px;overflow:auto;background:rgba(2,8,18,.82);}',
      '#kpi-s0[hidden]{display:none !important;}',
      '#kpi-s0 .kpi-s0-card{width:100%;max-width:620px;margin:auto 0;padding:26px 28px 22px;border:1px solid rgba(0,229,255,.7);',
      'background:rgba(4,14,28,.96);color:#e8fbff;box-shadow:0 0 24px rgba(0,229,255,.18);font-size:14px;}',
      '#kpi-s0 .kpi-s0-kicker{margin:0 0 4px;font-size:11px;letter-spacing:.14em;color:rgba(0,229,255,.9);font-weight:700;}',
      '#kpi-s0 .kpi-s0-title{margin:0 0 8px;font-size:20px;letter-spacing:.06em;font-weight:700;}',
      '#kpi-s0 .kpi-s0-lead{margin:0 0 14px;line-height:1.6;opacity:.92;}',
      '#kpi-s0 .kpi-s0-progress{margin:0 0 16px;padding:10px 12px;border:1px solid rgba(0,229,255,.35);background:rgba(0,229,255,.06);}',
      '#kpi-s0 .kpi-s0-progress-count{font-weight:700;letter-spacing:.04em;}',
      '#kpi-s0 .kpi-s0-progress-rest{margin-top:4px;font-size:12.5px;line-height:1.5;color:#ffd27a;}',
      '#kpi-s0 .kpi-s0-progress.is-done .kpi-s0-progress-rest{color:#7dffb2;}',
      '#kpi-s0 .kpi-s0-section{margin:0 0 14px;padding:0;border:0;}',
      '#kpi-s0 .kpi-s0-section-title{margin:0 0 8px;font-size:12px;letter-spacing:.12em;font-weight:700;opacity:.8;}',
      '#kpi-s0 .kpi-s0-field{display:grid;grid-template-columns:200px 1fr;gap:6px 14px;align-items:start;margin:0 0 10px;}',
      '#kpi-s0 .kpi-s0-label{padding-top:7px;font-weight:600;line-height:1.35;}',
      '#kpi-s0 .kpi-s0-badge{display:inline-block;margin-left:6px;padding:1px 6px;font-size:10.5px;font-weight:700;letter-spacing:.06em;vertical-align:1px;',
      'border:1px solid rgba(0,229,255,.8);color:#9ff4ff;}',
      '#kpi-s0 .kpi-s0-badge.is-optional{border-color:rgba(232,251,255,.35);color:rgba(232,251,255,.65);}',
      '#kpi-s0 .kpi-s0-control input,#kpi-s0 .kpi-s0-control select{width:100%;box-sizing:border-box;padding:7px 9px;font:inherit;',
      'background:rgba(0,0,0,.35);color:#e8fbff;border:1px solid rgba(0,229,255,.4);border-radius:0;}',
      '#kpi-s0 .kpi-s0-control select option{color:#111;background:#fff;}',
      '#kpi-s0 .kpi-s0-control input:focus,#kpi-s0 .kpi-s0-control select:focus{outline:none;border-color:#00e5ff;box-shadow:0 0 0 1px #00e5ff;}',
      '#kpi-s0 .kpi-s0-date{display:grid;grid-template-columns:1.3fr 1fr 1.2fr;gap:8px;}',
      '#kpi-s0 .kpi-s0-hint{margin-top:4px;font-size:12px;line-height:1.45;opacity:.72;}',
      '#kpi-s0 .kpi-s0-error{margin-top:4px;font-size:12px;color:#ff8a8a;}',
      '#kpi-s0 .kpi-s0-error:empty{display:none;}',
      '#kpi-s0 .kpi-s0-field.is-missing input,#kpi-s0 .kpi-s0-field.is-missing select{border-color:#ffb44d;}',
      '#kpi-s0 .kpi-s0-status{min-height:18px;margin:6px 0 0;font-size:12.5px;line-height:1.5;}',
      '#kpi-s0 .kpi-s0-status.is-error{color:#ff8a8a;}',
      '#kpi-s0 .kpi-s0-status.is-warn{color:#ffd27a;}',
      '#kpi-s0 .kpi-s0-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:14px;}',
      '#kpi-s0 .kpi-s0-btn{padding:9px 18px;font:inherit;font-size:13px;font-weight:700;letter-spacing:.04em;cursor:pointer;',
      'border:1px solid rgba(0,229,255,.85);background:transparent;color:#e8fbff;}',
      '#kpi-s0 .kpi-s0-btn.is-primary{background:rgba(0,229,255,.18);}',
      '#kpi-s0 .kpi-s0-btn:hover:not([disabled]){background:rgba(0,229,255,.3);}',
      '#kpi-s0 .kpi-s0-btn[disabled]{opacity:.4;cursor:not-allowed;}',
      '#kpi-s0 .kpi-s0-saved{padding:6px 0 2px;}',
      '#kpi-s0 .kpi-s0-saved h3{margin:0 0 8px;font-size:17px;}',
      '#kpi-s0 .kpi-s0-saved p{margin:0;line-height:1.6;}',
      'body.office-mode #kpi-s0{background:rgba(20,20,20,.32);}',
      'body.office-mode #kpi-s0 .kpi-s0-card{border:1px solid #1c1c1c;background:#f4f1ea;color:#1a1a1c;box-shadow:none;}',
      'body.office-mode #kpi-s0 .kpi-s0-kicker{color:#555;}',
      'body.office-mode #kpi-s0 .kpi-s0-title{letter-spacing:.03em;font-weight:600;}',
      'body.office-mode #kpi-s0 .kpi-s0-progress{border-color:#c9c3b6;background:#fff;}',
      'body.office-mode #kpi-s0 .kpi-s0-progress-rest{color:#9a5a00;}',
      'body.office-mode #kpi-s0 .kpi-s0-progress.is-done .kpi-s0-progress-rest{color:#1f6b3a;}',
      'body.office-mode #kpi-s0 .kpi-s0-badge{border-color:#1c1c1c;color:#1c1c1c;}',
      'body.office-mode #kpi-s0 .kpi-s0-badge.is-optional{border-color:#9a948a;color:#6b665e;}',
      'body.office-mode #kpi-s0 .kpi-s0-control input,body.office-mode #kpi-s0 .kpi-s0-control select{background:#fff;color:#1a1a1c;border-color:#a9a395;}',
      'body.office-mode #kpi-s0 .kpi-s0-control input:focus,body.office-mode #kpi-s0 .kpi-s0-control select:focus{border-color:#1c1c1c;box-shadow:0 0 0 1px #1c1c1c;}',
      'body.office-mode #kpi-s0 .kpi-s0-field.is-missing input,body.office-mode #kpi-s0 .kpi-s0-field.is-missing select{border-color:#c77700;}',
      'body.office-mode #kpi-s0 .kpi-s0-error,body.office-mode #kpi-s0 .kpi-s0-status.is-error{color:#b3261e;}',
      'body.office-mode #kpi-s0 .kpi-s0-status.is-warn{color:#9a5a00;}',
      'body.office-mode #kpi-s0 .kpi-s0-btn{border-color:#1c1c1c;color:#1c1c1c;}',
      'body.office-mode #kpi-s0 .kpi-s0-btn.is-primary{background:#1c1c1c;color:#fff;}',
      'body.office-mode #kpi-s0 .kpi-s0-btn:hover:not([disabled]){background:#3a3a3a;color:#fff;}',
    ].join('');
    (global.document.head || global.document.documentElement).appendChild(style);
  }

  function badge(c, required) {
    return required
      ? '<span class="kpi-s0-badge">' + esc(c.required) + '</span>'
      : '<span class="kpi-s0-badge is-optional">' + esc(c.optional) + '</span>';
  }

  function fieldRow(c, key, labelHtml, controlHtml, required, extra) {
    return (
      '<div class="kpi-s0-field" data-s0-field="' + key + '">' +
      '<label class="kpi-s0-label" for="kpi-s0-' + key + '" id="kpi-s0-label-' + key + '">' +
      labelHtml + badge(c, required) + '</label>' +
      '<div class="kpi-s0-control">' + controlHtml + (extra || '') + '</div></div>'
    );
  }

  function optionList(from, to, step, blankLabel) {
    var html = '<option value="">' + esc(blankLabel) + '</option>';
    for (var n = from; step > 0 ? n <= to : n >= to; n += step) {
      html += '<option value="' + n + '">' + n + '</option>';
    }
    return html;
  }

  function renderForm(c) {
    var thisYear = new Date().getFullYear();
    var textInput = function (key, listId) {
      return (
        '<input type="text" id="kpi-s0-' + key + '" name="' + key + '" autocomplete="off"' +
        (listId ? ' list="' + listId + '"' : '') + '>' +
        (listId ? '<datalist id="' + listId + '"></datalist>' : '')
      );
    };
    var dateControl =
      '<div class="kpi-s0-date">' +
      '<select id="kpi-s0-openingDate" name="openingYear" aria-label="' + esc(c.year) + '">' +
      optionList(thisYear + 1, 1900, -1, c.year) + '</select>' +
      '<select id="kpi-s0-openingMonth" name="openingMonth" aria-label="' + esc(c.month) + '">' +
      optionList(1, 12, 1, c.month) + '</select>' +
      '<select id="kpi-s0-openingDay" name="openingDay" aria-label="' + esc(c.day) + '">' +
      optionList(1, 31, 1, c.day) + '</select></div>' +
      '<div class="kpi-s0-hint">' + esc(c.dateHint) + '</div>' +
      '<div class="kpi-s0-error" id="kpi-s0-date-error"></div>';
    return (
      '<p class="kpi-s0-kicker">' + esc(c.kicker) + '</p>' +
      '<h2 class="kpi-s0-title" id="kpi-s0-title">' + esc(c.title) + '</h2>' +
      '<p class="kpi-s0-lead">' + esc(c.lead) + '</p>' +
      '<div class="kpi-s0-progress" id="kpi-s0-progress" aria-live="polite">' +
      '<div class="kpi-s0-progress-count" id="kpi-s0-progress-count"></div>' +
      '<div class="kpi-s0-progress-rest" id="kpi-s0-progress-rest"></div></div>' +
      '<form id="kpi-s0-form" novalidate>' +
      '<fieldset class="kpi-s0-section" data-s0-section="required">' +
      '<legend class="kpi-s0-section-title">' + esc(c.sectionRequired) + '</legend>' +
      fieldRow(c, 'businessName', esc(c.businessName), textInput('businessName'), true) +
      fieldRow(c, 'companyName', esc(c.companyName), textInput('companyName'), true) +
      fieldRow(c, 'businessType', esc(c.businessType), '<select id="kpi-s0-businessType" name="businessType"></select>', true) +
      fieldRow(c, 'openingDate', esc(c.openingDate), dateControl, true) +
      fieldRow(c, 'country', esc(c.country), textInput('country', 'kpi-s0-country-list'), true) +
      fieldRow(
        c,
        'stateRegion',
        '<span id="kpi-s0-region-text">' + esc(c.regionDefault) + '</span>',
        textInput('stateRegion', 'kpi-s0-region-list'),
        true,
        '<div class="kpi-s0-hint">' + esc(c.regionHint) + '</div>'
      ) +
      fieldRow(
        c,
        'currency',
        esc(c.currency),
        '<select id="kpi-s0-currency" name="currency"></select>',
        true,
        '<div class="kpi-s0-hint">' + esc(c.currencyHint) + '</div>'
      ) +
      '</fieldset>' +
      '<fieldset class="kpi-s0-section" data-s0-section="optional">' +
      '<legend class="kpi-s0-section-title">' + esc(c.sectionOptional) + '</legend>' +
      fieldRow(c, 'city', esc(c.city), textInput('city', 'kpi-s0-city-list'), false) +
      fieldRow(c, 'genre', esc(c.genre), textInput('genre'), false) +
      '</fieldset>' +
      '<div class="kpi-s0-status" id="kpi-s0-status" role="status"></div>' +
      '<div class="kpi-s0-actions">' +
      '<button type="button" class="kpi-s0-btn" id="kpi-s0-back">' + esc(c.back) + '</button>' +
      '<button type="submit" class="kpi-s0-btn is-primary" id="kpi-s0-save" disabled>' + esc(c.save) + '</button>' +
      '</div></form>'
    );
  }

  function renderSaved(c) {
    return (
      '<p class="kpi-s0-kicker">' + esc(c.kicker) + '</p>' +
      '<div class="kpi-s0-saved" id="kpi-s0-saved">' +
      '<h3>' + esc(c.savedTitle) + '</h3><p>' + esc(c.savedBody) + '</p></div>' +
      '<div class="kpi-s0-status" id="kpi-s0-status" role="status"></div>' +
      '<div class="kpi-s0-actions">' +
      '<button type="button" class="kpi-s0-btn is-primary" id="kpi-s0-next">' + esc(c.next) + '</button></div>'
    );
  }

  function ensureRoot() {
    if (!global.document || !global.document.body) return null;
    ensureStyle();
    if (rootEl && rootEl.parentNode) return rootEl;
    rootEl = global.document.createElement('div');
    rootEl.id = 'kpi-s0';
    rootEl.setAttribute('role', 'dialog');
    rootEl.setAttribute('aria-modal', 'true');
    rootEl.setAttribute('aria-labelledby', 'kpi-s0-title');
    rootEl.hidden = true;
    rootEl.innerHTML = '<div class="kpi-s0-card" id="kpi-s0-card"></div>';
    global.document.body.appendChild(rootEl);
    return rootEl;
  }

  function el(id) {
    return global.document.getElementById(id);
  }

  function setStatus(text, kind) {
    var s = el('kpi-s0-status');
    if (!s) return;
    s.textContent = text || '';
    s.className = 'kpi-s0-status' + (kind ? ' is-' + kind : '');
  }

  function regionLabel(c, countryRaw) {
    var L = loc();
    var code = L && typeof L.toCanonicalCountry === 'function' ? L.toCanonicalCountry(countryRaw) : '';
    if (code === 'JP') return c.regionJP;
    if (code === 'US') return c.regionUS;
    return c.regionDefault;
  }

  function refreshRegionUi() {
    var L = loc();
    var countryRaw = el('kpi-s0-country') ? el('kpi-s0-country').value : '';
    var text = el('kpi-s0-region-text');
    if (text) text.textContent = regionLabel(t(state.lang), countryRaw);
    if (!L) return;
    var list = el('kpi-s0-region-list');
    if (list && typeof L.fillDatalist === 'function') {
      L.fillDatalist(list, L.stateLabels(countryRaw, state.locale) || []);
    }
    refreshCityList();
  }

  function refreshCityList() {
    var L = loc();
    var list = el('kpi-s0-city-list');
    if (!L || !list || typeof L.fillDatalist !== 'function') return;
    var stateRaw = el('kpi-s0-stateRegion') ? el('kpi-s0-stateRegion').value : '';
    L.fillDatalist(list, (stateRaw && L.cityLabels(stateRaw, state.locale)) || []);
  }

  function suggestCurrency() {
    var C = cur();
    var sel = el('kpi-s0-currency');
    if (!C || !sel) return;
    var countryRaw = el('kpi-s0-country') ? el('kpi-s0-country').value : '';
    if (typeof C.maybeSuggestFromCountry === 'function') {
      C.maybeSuggestFromCountry(sel, countryRaw, { userSet: state.currencyUserSet, locale: state.locale });
    }
  }

  /** Values exactly as the form would save them. */
  function readForm() {
    var L = loc();
    var C = cur();
    var B = bt();
    var val = function (id) {
      var n = el(id);
      return n ? n.value : '';
    };
    var country = val('kpi-s0-country');
    var region = val('kpi-s0-stateRegion');
    var city = val('kpi-s0-city');
    var currency = val('kpi-s0-currency');
    var type = val('kpi-s0-businessType');
    var r = readiness();
    var openingDate =
      r && typeof r.buildOpeningDate === 'function'
        ? r.buildOpeningDate(val('kpi-s0-openingDate'), val('kpi-s0-openingMonth'), val('kpi-s0-openingDay'))
        : '';
    return {
      businessName: trimmed(val('kpi-s0-businessName')),
      companyName: trimmed(val('kpi-s0-companyName')),
      businessType: B && typeof B.normalizeBusinessType === 'function' ? B.normalizeBusinessType(type) || '' : '',
      openingDate: openingDate,
      openingYear: val('kpi-s0-openingDate'),
      openingMonth: val('kpi-s0-openingMonth'),
      openingDay: val('kpi-s0-openingDay'),
      country: L ? L.saveCountry(country) : trimmed(country),
      stateRegion: L ? L.saveText(region) : trimmed(region),
      city: L ? L.saveText(city) : trimmed(city),
      currency: C && typeof C.saveCode === 'function' ? C.saveCode(currency) : trimmed(currency),
      genre: trimmed(val('kpi-s0-genre')),
      raw: {
        businessName: val('kpi-s0-businessName'),
        companyName: val('kpi-s0-companyName'),
        businessType: type,
        country: country,
        stateRegion: region,
        city: city,
        currency: currency,
        genre: val('kpi-s0-genre'),
      },
    };
  }

  function evaluateForm(form) {
    var r = readiness();
    if (!r || typeof r.evaluateBusinessProfile !== 'function') {
      return { complete: false, missing: [], flags: {} };
    }
    return r.evaluateBusinessProfile({
      businessName: form.businessName,
      companyName: form.companyName,
      businessTypeSet: !!form.businessType,
      openingDate: form.openingDate,
      country: form.country,
      stateRegion: form.stateRegion,
      currency: form.currency,
    });
  }

  function fieldLabelText(key) {
    var c = t(state.lang);
    if (key === 'stateRegion') {
      var n = el('kpi-s0-region-text');
      return n ? n.textContent : c.regionDefault;
    }
    return c[key] || key;
  }

  function refreshValidation() {
    if (!state || state.view !== 'form') return null;
    var c = t(state.lang);
    var form = readForm();
    var result = evaluateForm(form);
    var total = (readiness() && readiness().HARD_REQUIRED_FIELDS || []).length || 7;
    var done = total - result.missing.length;
    var box = el('kpi-s0-progress');
    var count = el('kpi-s0-progress-count');
    var rest = el('kpi-s0-progress-rest');
    if (count) count.textContent = fmt(c.progress, { done: done, total: total });
    if (rest) {
      rest.textContent = result.complete
        ? c.allDone
        : fmt(c.remaining, {
            list: result.missing.map(fieldLabelText).join(state.lang === 'en' ? ', ' : '、'),
          });
    }
    if (box) box.classList.toggle('is-done', result.complete);
    result.missing.forEach(function (k) {
      var row = rootEl.querySelector('[data-s0-field="' + k + '"]');
      if (row) row.classList.toggle('is-missing', !!state.touched[k]);
    });
    (readiness() && readiness().HARD_REQUIRED_FIELDS || []).forEach(function (k) {
      if (result.missing.indexOf(k) >= 0) return;
      var row = rootEl.querySelector('[data-s0-field="' + k + '"]');
      if (row) row.classList.remove('is-missing');
    });
    var dateErr = el('kpi-s0-date-error');
    if (dateErr) {
      var dateBad = !!(form.openingYear && form.openingMonth && form.openingDay && !form.openingDate);
      dateErr.textContent = dateBad ? c.dateInvalid : '';
    }
    var save = el('kpi-s0-save');
    if (save) save.disabled = !result.complete || state.saving;
    return { form: form, result: result };
  }

  function fillInitial(profile, openingDate) {
    var L = loc();
    var C = cur();
    var B = bt();
    var p = profileShape(profile);
    var setVal = function (id, v) {
      var n = el(id);
      if (n) n.value = v == null ? '' : v;
    };
    setVal('kpi-s0-businessName', p.businessName);
    setVal('kpi-s0-companyName', p.companyName);
    var typeSel = el('kpi-s0-businessType');
    if (typeSel && B && typeof B.populateSelect === 'function') {
      B.populateSelect(typeSel);
      var metaType = typeof B.readMetaBusinessType === 'function' ? B.readMetaBusinessType() : null;
      typeSel.value = B.normalizeBusinessType(p.businessType) || metaType || '';
    }
    if (L) {
      var clist = el('kpi-s0-country-list');
      if (clist) L.fillDatalist(clist, L.countryLabels(state.locale));
      setVal('kpi-s0-country', L.displayCountry(p.country, state.locale));
      setVal('kpi-s0-stateRegion', L.displayState(p.stateRegion, state.locale));
      setVal('kpi-s0-city', L.displayCity(p.city, state.locale));
    } else {
      setVal('kpi-s0-country', p.country);
      setVal('kpi-s0-stateRegion', p.stateRegion);
      setVal('kpi-s0-city', p.city);
    }
    setVal('kpi-s0-genre', p.genre);
    var curSel = el('kpi-s0-currency');
    var serverCurrency = C && typeof C.normalizeCode === 'function' ? C.normalizeCode(p.currency) : trimmed(p.currency);
    if (curSel && C && typeof C.fillSelect === 'function') {
      C.fillSelect(curSel, { locale: state.locale, selected: serverCurrency, country: p.country, forceCatalog: true });
      /* Only the saved server value pre-selects; a local display default is not a user choice. */
      curSel.value = serverCurrency || '';
    }
    state.currencyUserSet = !!serverCurrency;
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(openingDate || '');
    if (m) {
      setVal('kpi-s0-openingDate', String(Number(m[1])));
      setVal('kpi-s0-openingMonth', String(Number(m[2])));
      setVal('kpi-s0-openingDay', m[3] === '01' ? '' : String(Number(m[3])));
    }
    refreshRegionUi();
    state.initialRaw = readForm().raw;
    state.initialOpeningDate = openingDate || '';
  }

  function bindForm() {
    var form = el('kpi-s0-form');
    if (!form) return;
    var onChange = function (ev) {
      var target = ev && ev.target;
      if (!target || !target.id) return;
      if (target.id === 'kpi-s0-country') {
        refreshRegionUi();
        suggestCurrency();
      } else if (target.id === 'kpi-s0-stateRegion') {
        refreshCityList();
      } else if (target.id === 'kpi-s0-currency' && ev.type === 'change') {
        state.currencyUserSet = !!target.value;
      }
      refreshValidation();
    };
    form.addEventListener('input', onChange);
    form.addEventListener('change', onChange);
    form.addEventListener(
      'blur',
      function (ev) {
        var row = ev.target && ev.target.closest ? ev.target.closest('[data-s0-field]') : null;
        if (row) state.touched[row.getAttribute('data-s0-field')] = true;
        refreshValidation();
      },
      true
    );
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      save();
    });
    var back = el('kpi-s0-back');
    if (back) back.addEventListener('click', close);
  }

  function setFormDisabled(disabled) {
    var form = el('kpi-s0-form');
    if (!form) return;
    Array.prototype.forEach.call(form.querySelectorAll('input,select,button'), function (n) {
      n.disabled = disabled;
    });
  }

  /** Only fields whose visible input changed since open are sent over the server values. */
  function changedFields(form) {
    var out = {};
    var init = state.initialRaw || {};
    FORM_FIELDS.forEach(function (k) {
      if (String(form.raw[k] || '') !== String(init[k] || '')) out[k] = form[k];
    });
    return out;
  }

  function save() {
    if (!state || state.saving) return;
    var check = refreshValidation();
    if (!check || !check.result.complete) return;
    var c = t(state.lang);
    var form = check.form;
    state.saving = true;
    setFormDisabled(true);
    setStatus(c.saving, '');
    fetchProfileFresh()
      .then(function (fresh) {
        if (!fresh.ok) throw { stage: 'load' };
        var changes = changedFields(form);
        var merged = mergeProfile(fresh.profile, changes);
        /* Required fields must hold what the form validated, even if unchanged locally. */
        ['businessName', 'companyName', 'businessType', 'country', 'stateRegion', 'currency'].forEach(function (k) {
          if (!trimmed(merged[k])) merged[k] = form[k];
        });
        return saveProfileFull(merged).then(function (res) {
          if (!res || res.ok !== true) throw { stage: 'save' };
          return merged;
        });
      })
      .then(function (merged) {
        var B = bt();
        if (B && typeof B.setBusinessType === 'function') B.setBusinessType(merged.businessType);
        var storeOk = writeOpeningDate(form.openingDate);
        writeLocalProfile(merged, merged.currency);
        return pushStore().then(function (push) {
          return { storeOk: storeOk && !!(push && push.ok === true) };
        });
      })
      .then(function (out) {
        state.saving = false;
        showSaved(out.storeOk);
      })
      .catch(function (err) {
        state.saving = false;
        setFormDisabled(false);
        refreshValidation();
        setStatus(err && err.stage === 'load' ? c.loadFailed : c.saveFailed, 'error');
      });
  }

  function showSaved(storeOk) {
    var c = t(state.lang);
    state.view = 'saved';
    var card = el('kpi-s0-card');
    if (!card) return;
    card.innerHTML = renderSaved(c);
    if (!storeOk) setStatus(c.storeWarn, 'warn');
    var next = el('kpi-s0-next');
    if (next) {
      next.addEventListener('click', function () {
        var done = state.onDone;
        close();
        if (typeof done === 'function') done();
      });
      try {
        next.focus();
      } catch (_e) {}
    }
  }

  function close() {
    if (rootEl) rootEl.hidden = true;
    state = null;
  }

  function open(opts) {
    var root = ensureRoot();
    if (!root) return;
    var lang = detectLang();
    var c = t(lang);
    state = {
      lang: lang,
      locale: locationLocale(lang),
      view: 'form',
      saving: false,
      touched: {},
      currencyUserSet: false,
      initialRaw: null,
      onDone: opts && typeof opts.onDone === 'function' ? opts.onDone : null,
    };
    var card = el('kpi-s0-card');
    card.innerHTML = renderForm(c);
    root.hidden = false;
    bindForm();
    setFormDisabled(true);
    setStatus(c.loading, '');
    var session = state;
    fetchProfileFresh().then(function (res) {
      if (state !== session) return;
      if (!res.ok) {
        setStatus(c.loadFailed, 'error');
        var back = el('kpi-s0-back');
        if (back) back.disabled = false;
        return;
      }
      setFormDisabled(false);
      fillInitial(res.profile, readOpeningDate());
      setStatus('', '');
      refreshValidation();
      try {
        el('kpi-s0-businessName').focus();
      } catch (_e) {}
    });
  }

  global.KpiSetupStep0 = {
    __ready: true,
    open: open,
    close: close,
    mergeProfile: mergeProfile,
    COPY: COPY,
  };
})(typeof window !== 'undefined' ? window : this);
