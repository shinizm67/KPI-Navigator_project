/**
 * BR-ONBOARDING-01 Phase 2 — Business Profile Step 0 (Hard Required 7).
 * Opened from the Navigation Readiness guard. One implementation for JP / EN / ZH-TW
 * and Sci-Fi / Office (body.office-mode).
 *
 * profile.php PUT overwrites every column: always GET the current profile, merge only
 * the fields this form changed, then PUT the full payload. Never partial-PUT.
 *
 * Phase 3 — STEP 02 Historical Data (openHistory) shares this dialog.
 * store.meta.setup writes: Step 01 save creates an empty object when opened with
 * startSetup (non-grandfathered only), so importing history cannot grandfather the user
 * mid-setup; STEP 02 Skip sets historicalSkipped only. setup.complete is never written here.
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
      kicker: 'KPN INITIAL SETUP',
      title: 'Business Profile',
      lead: 'KPNを開始するために、ビジネスの基本情報を設定してください。',
      lead2: '必須項目をすべて入力すると保存できます。',
      required: '必須',
      optional: '任意',
      sectionRequired: '必須項目',
      sectionOptional: '任意項目',
      sectionOptionalNote: '空欄のままでも保存できます',
      progressLabel: 'REQUIRED FIELDS',
      stepsLabel: 'KPN 初期設定 {total} ステップ中 {current}',
      steps: ['ビジネス情報', '過去データ', '今年度', '年間目標', '最終確認'],
      stepState: { completed: '完了', active: '入力中', skipped: 'スキップ', future: '未着手' },
      businessName: '屋号 / サービス名 / 店名',
      companyName: '会社名',
      businessType: '業種',
      openingDate: '事業開始年月',
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
      storeWarn: '事業開始年月・業種のサーバ同期がまだ完了していません。画面を再読み込みすると再送されます。',
      savedTitle: 'BUSINESS PROFILE SAVED',
      savedLead: 'ビジネス情報を保存しました。',
      savedBody: 'このまま KPN をご利用いただけます。',
      savedBodyContinue: '次は過去データの確認です。',
      next: 'KPN に進む',
      nextStep: '次へ',
      history: {
        title: 'Historical Data',
        lead: '過去の売上データを登録すると、KPNがより正確に傾向を把握できます。',
        start: '事業開始',
        range: '対象期間',
        status: '状態',
        detected: '検出した年',
        level: 'おすすめ度',
        none: 'なし',
        rangeSep: ' 〜 ',
        state: {
          absent: '過去データは見つかりません',
          present: '過去データがあります',
          skipped: 'スキップ中',
          not_applicable: '対象外（今年開業）',
        },
        levelText: { not_applicable: '不要', recommended: 'おすすめ', strong: '強くおすすめ', present: '登録済み' },
        msg: {
          not_applicable: '今年開業のため、過去データは必要ありません。',
          recommended: '過去データを登録すると、年間傾向や比較精度を高められます。',
          strong: 'KPNの分析精度を高めるため、過去データの登録をおすすめします。',
          present: '過去データが登録されています。追加の登録は後からでもできます。',
          skipped: '過去データの登録をスキップしています。後から登録できます。',
        },
        register: '過去データを登録する',
        addMore: '過去データを追加する',
        skip: '今はスキップする',
        close: '閉じる',
        next: '次へ',
        viaAnnual: '登録は年間ビューの「過去売上データ」で行います。',
        confirmTitle: '過去データの登録をスキップしますか？',
        confirmLines: [
          '過去データは後から登録できます。',
          'スキップしても KPN はそのまま使えます。',
          '一部の比較・分析の精度が低くなる場合があります。',
        ],
        confirmSkip: 'スキップする',
        confirmBack: '戻る',
        skipFailed: 'スキップを保存できませんでした。もう一度お試しください。',
        skipWarn: 'スキップの設定がサーバーにまだ届いていません。画面を再読み込みすると再送されます。',
        doneTitle: {
          present: 'HISTORICAL DATA READY',
          skipped: 'HISTORICAL DATA SKIPPED',
          not_applicable: 'HISTORICAL DATA NOT REQUIRED',
        },
        doneLead: {
          present: '過去データを確認しました。',
          skipped: '過去データの登録をスキップしました。',
          not_applicable: '過去データは必要ありません。',
        },
        doneBody: '次のステップは「今年度」です（準備中）。このまま KPN をご利用いただけます。',
      },
    },
    en: {
      kicker: 'KPN INITIAL SETUP',
      title: 'Business Profile',
      lead: 'Set up your basic business information to start KPN.',
      lead2: 'You can save once all required fields are filled in.',
      required: 'Required',
      optional: 'Optional',
      sectionRequired: 'Required',
      sectionOptional: 'Optional',
      sectionOptionalNote: 'Can be left blank',
      progressLabel: 'REQUIRED FIELDS',
      stepsLabel: 'KPN initial setup, step {current} of {total}',
      steps: ['Business Profile', 'History', 'Current Year', 'Target', 'Review'],
      stepState: { completed: 'Done', active: 'In progress', skipped: 'Skipped', future: 'Not started' },
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
      savedTitle: 'BUSINESS PROFILE SAVED',
      savedLead: 'Your business information has been saved.',
      savedBody: 'You can continue to KPN now.',
      savedBodyContinue: 'Next, check your past data.',
      next: 'Continue to KPN',
      nextStep: 'Next',
      history: {
        title: 'Historical Data',
        lead: 'Adding past sales data helps KPN read your trends more accurately.',
        start: 'Business Start',
        range: 'Historical Range',
        status: 'Status',
        detected: 'Detected Years',
        level: 'Recommendation',
        none: 'None',
        rangeSep: ' – ',
        state: {
          absent: 'No historical data detected',
          present: 'Historical data found',
          skipped: 'Skipped',
          not_applicable: 'Not applicable (opened this year)',
        },
        levelText: { not_applicable: 'Not needed', recommended: 'Recommended', strong: 'Strongly recommended', present: 'Registered' },
        msg: {
          not_applicable: 'Your business started this year, so no past data is needed.',
          recommended: 'Adding past data improves yearly trends and comparisons.',
          strong: 'To improve KPN analysis accuracy, we recommend adding your past data.',
          present: 'Past data is registered. You can add more at any time.',
          skipped: 'Past data is skipped for now. You can add it later.',
        },
        register: 'Add Past Data',
        addMore: 'Add More Past Data',
        skip: 'Skip for Now',
        close: 'Close',
        next: 'Next',
        viaAnnual: 'Past data is added from Past Sales Data in Annual view.',
        confirmTitle: 'Skip adding past data?',
        confirmLines: [
          'You can add past data later.',
          'You can keep using KPN.',
          'Some comparisons and analysis may be less accurate.',
        ],
        confirmSkip: 'Skip',
        confirmBack: 'Back',
        skipFailed: 'Could not save the skip. Please try again.',
        skipWarn: 'The skip has not reached the server yet. Reloading the page will retry.',
        doneTitle: {
          present: 'HISTORICAL DATA READY',
          skipped: 'HISTORICAL DATA SKIPPED',
          not_applicable: 'HISTORICAL DATA NOT REQUIRED',
        },
        doneLead: {
          present: 'Your past data is confirmed.',
          skipped: 'Past data is skipped for now.',
          not_applicable: 'No past data is needed.',
        },
        doneBody: 'Next step: Current Year (coming soon). You can continue to KPN now.',
      },
    },
    zh: {
      kicker: 'KPN INITIAL SETUP',
      title: 'Business Profile',
      lead: '開始使用 KPN 前，請設定商家的基本資訊。',
      lead2: '填妥所有必填項目後即可儲存。',
      required: '必填',
      optional: '選填',
      sectionRequired: '必填項目',
      sectionOptional: '選填項目',
      sectionOptionalNote: '可以留空',
      progressLabel: 'REQUIRED FIELDS',
      stepsLabel: 'KPN 初始設定，共 {total} 步中的第 {current} 步',
      steps: ['商家資訊', '過去資料', '本年度', '年度目標', '最終確認'],
      stepState: { completed: '已完成', active: '填寫中', skipped: '已略過', future: '尚未開始' },
      businessName: '店名 / 服務名稱',
      companyName: '公司名稱',
      businessType: '產業',
      openingDate: '事業開始年月',
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
      storeWarn: '事業開始年月與產業尚未完成伺服器同步。重新整理頁面後會再次傳送。',
      savedTitle: 'BUSINESS PROFILE SAVED',
      savedLead: '已儲存商家資訊。',
      savedBody: '現在可以直接進入 KPN。',
      savedBodyContinue: '接下來確認過去資料。',
      next: '進入 KPN',
      nextStep: '下一步',
      history: {
        title: 'Historical Data',
        lead: '登錄過去的營業額資料，KPN 能更準確地掌握趨勢。',
        start: '事業開始',
        range: '對象期間',
        status: '狀態',
        detected: '偵測到的年份',
        level: '建議程度',
        none: '無',
        rangeSep: ' ～ ',
        state: {
          absent: '未偵測到過去資料',
          present: '已有過去資料',
          skipped: '已略過',
          not_applicable: '不適用（本年度開業）',
        },
        levelText: { not_applicable: '不需要', recommended: '建議', strong: '強烈建議', present: '已登錄' },
        msg: {
          not_applicable: '本年度開業，不需要過去資料。',
          recommended: '登錄過去資料可提升年度趨勢與比較的準確度。',
          strong: '為提升 KPN 的分析準確度，建議登錄過去資料。',
          present: '已登錄過去資料，之後也可以隨時追加。',
          skipped: '目前已略過過去資料，之後仍可登錄。',
        },
        register: '登錄過去資料',
        addMore: '追加過去資料',
        skip: '暫時略過',
        close: '關閉',
        next: '下一步',
        viaAnnual: '過去資料請在年度檢視的「過去營業額資料」登錄。',
        confirmTitle: '要略過過去資料的登錄嗎？',
        confirmLines: [
          '之後仍可登錄過去資料。',
          '略過後仍可繼續使用 KPN。',
          '部分比較與分析的準確度可能降低。',
        ],
        confirmSkip: '略過',
        confirmBack: '返回',
        skipFailed: '無法儲存略過設定，請再試一次。',
        skipWarn: '略過設定尚未傳送到伺服器。重新整理頁面後會再次傳送。',
        doneTitle: {
          present: 'HISTORICAL DATA READY',
          skipped: 'HISTORICAL DATA SKIPPED',
          not_applicable: 'HISTORICAL DATA NOT REQUIRED',
        },
        doneLead: {
          present: '已確認過去資料。',
          skipped: '已略過過去資料的登錄。',
          not_applicable: '不需要過去資料。',
        },
        doneBody: '下一步是「本年度」（準備中）。現在可以直接進入 KPN。',
      },
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

  function writeStoreJson(store) {
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

  function writeHistoricalSkipped() {
    var store = readStore();
    if (!store) return false;
    if (!store.meta || typeof store.meta !== 'object') store.meta = {};
    var bag = store.meta.setup;
    if (!bag || typeof bag !== 'object') bag = store.meta.setup = {};
    bag.historicalSkipped = true;
    return writeStoreJson(store);
  }

  function writeOpeningDate(iso, startSetup) {
    var store = readStore();
    if (!store) return false;
    if (!store.meta || typeof store.meta !== 'object') store.meta = {};
    store.meta.openingDate = iso;
    if (startSetup && (!store.meta.setup || typeof store.meta.setup !== 'object')) {
      store.meta.setup = {};
    }
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
      '#kpi-s0{position:fixed;inset:0;z-index:100001;display:flex;align-items:flex-start;justify-content:center;padding:32px 24px;overflow:auto;background:rgba(2,8,18,.84);}',
      '#kpi-s0[hidden]{display:none !important;}',
      '#kpi-s0 .kpi-s0-card{position:relative;width:100%;max-width:640px;margin:auto 0;padding:28px 32px 24px;border:1px solid rgba(0,229,255,.5);background:rgba(3,11,22,.97);color:#e8fbff;font-size:14px;}',
      '#kpi-s0 .kpi-s0-card::before{content:\'\';position:absolute;top:-1px;left:-1px;width:64px;height:2px;background:#00e5ff;}',
      '#kpi-s0 .kpi-s0-head{margin:0 0 18px;padding:0 0 16px;border-bottom:1px solid rgba(0,229,255,.18);}',
      '#kpi-s0 .kpi-s0-kicker{margin:0 0 14px;font-size:11px;letter-spacing:.16em;color:rgba(0,229,255,.9);font-weight:700;}',
      '#kpi-s0 .kpi-s0-ruler{list-style:none;margin:0 0 22px;padding:0;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));}',
      '#kpi-s0 .kpi-s0-ruler-step{position:relative;display:flex;flex-direction:column;align-items:center;min-width:0;padding:0 4px;text-align:center;}',
      '#kpi-s0 .kpi-s0-ruler-step::before,#kpi-s0 .kpi-s0-ruler-step::after{content:\'\';position:absolute;top:6px;width:50%;height:4px;background:rgba(0,229,255,.18);}',
      '#kpi-s0 .kpi-s0-ruler-step::before{left:0;}',
      '#kpi-s0 .kpi-s0-ruler-step::after{left:50%;}',
      '#kpi-s0 .kpi-s0-ruler-step:first-child::before,#kpi-s0 .kpi-s0-ruler-step:last-child::after{display:none;}',
      '#kpi-s0 .kpi-s0-ruler-step.is-skipped::after,#kpi-s0 .kpi-s0-ruler-step.is-skipped+.kpi-s0-ruler-step::before{background:repeating-linear-gradient(90deg,rgba(0,229,255,.55) 0 5px,transparent 5px 9px);}',
      '#kpi-s0 .kpi-s0-ruler-step.is-active::after,#kpi-s0 .kpi-s0-ruler-step.is-completed::after,#kpi-s0 .kpi-s0-ruler-step.is-completed+.kpi-s0-ruler-step::before{background:#0F9403;}',
      '#kpi-s0 .kpi-s0-ruler-node{position:relative;z-index:1;width:16px;height:16px;box-sizing:border-box;border:2px solid rgba(0,229,255,.4);border-radius:50%;background:#030b16;}',
      '#kpi-s0 .kpi-s0-ruler-step.is-active .kpi-s0-ruler-node{border-color:#0F9403;background:#0F9403;box-shadow:0 0 0 4px rgba(15,148,3,.24);}',
      '#kpi-s0 .kpi-s0-ruler-step.is-completed .kpi-s0-ruler-node{border-color:#0F9403;background:#0F9403;}',
      '#kpi-s0 .kpi-s0-ruler-step.is-skipped .kpi-s0-ruler-node{border-style:dashed;border-color:rgba(0,229,255,.65);}',
      '#kpi-s0 .kpi-s0-ruler-num{margin-top:8px;font-size:10.5px;letter-spacing:.12em;font-weight:700;font-variant-numeric:tabular-nums;color:rgba(232,251,255,.52);}',
      '#kpi-s0 .kpi-s0-ruler-label{margin-top:2px;max-width:100%;font-size:12px;line-height:1.3;color:rgba(232,251,255,.62);overflow-wrap:break-word;hyphens:auto;}',
      '#kpi-s0 .kpi-s0-ruler-step.is-active .kpi-s0-ruler-num{color:#e8fbff;}',
      '#kpi-s0 .kpi-s0-ruler-step.is-active .kpi-s0-ruler-label{color:#fff;font-weight:600;}',
      '#kpi-s0 .kpi-s0-ruler-step.is-completed .kpi-s0-ruler-num,#kpi-s0 .kpi-s0-ruler-step.is-completed .kpi-s0-ruler-label{color:rgba(232,251,255,.84);}',
      '#kpi-s0 .kpi-s0-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;}',
      '#kpi-s0 .kpi-s0-title{margin:0 0 10px;font-size:22px;letter-spacing:.04em;font-weight:700;}',
      '#kpi-s0 .kpi-s0-lead{margin:0;line-height:1.65;color:rgba(232,251,255,.9);}',
      '#kpi-s0 .kpi-s0-lead2{margin:2px 0 0;font-size:13px;line-height:1.6;color:rgba(232,251,255,.62);}',
      '#kpi-s0 .kpi-s0-progress{margin:0 0 20px;}',
      '#kpi-s0 .kpi-s0-progress-count{display:flex;align-items:baseline;justify-content:space-between;gap:12px;}',
      '#kpi-s0 .kpi-s0-progress-label{font-size:11px;letter-spacing:.16em;font-weight:700;color:rgba(0,229,255,.85);}',
      '#kpi-s0 .kpi-s0-progress-num{font-size:15px;font-weight:700;letter-spacing:.06em;font-variant-numeric:tabular-nums;}',
      '#kpi-s0 .kpi-s0-progress-line{position:relative;height:2px;margin:8px 0 7px;background:rgba(0,229,255,.16);}',
      '#kpi-s0 .kpi-s0-progress-fill{position:absolute;left:0;top:0;bottom:0;width:0;background:#00e5ff;transition:width .2s ease;}',
      '#kpi-s0 .kpi-s0-progress-rest{font-size:12.5px;line-height:1.5;color:rgba(232,251,255,.66);}',
      '#kpi-s0 .kpi-s0-progress.is-done .kpi-s0-progress-rest{color:#7ff3ff;}',
      '#kpi-s0 .kpi-s0-section{margin:0 0 16px;padding:0;border:0;min-width:0;}',
      '#kpi-s0 .kpi-s0-section-title{display:block;width:100%;box-sizing:border-box;margin:0 0 12px;padding:0 0 6px;border-bottom:1px solid rgba(0,229,255,.16);font-size:12px;letter-spacing:.1em;font-weight:700;color:rgba(0,229,255,.85);}',
      '#kpi-s0 .kpi-s0-section-note{margin-left:10px;font-size:11.5px;letter-spacing:.02em;font-weight:400;color:rgba(232,251,255,.55);}',
      '#kpi-s0 .kpi-s0-field{display:grid;grid-template-columns:200px 1fr;gap:6px 16px;align-items:start;margin:0 0 12px;}',
      '#kpi-s0 .kpi-s0-label{padding-top:8px;font-weight:600;line-height:1.35;}',
      '#kpi-s0 .kpi-s0-badge{display:inline-block;margin-left:8px;padding:0 6px;font-size:10.5px;line-height:17px;font-weight:600;letter-spacing:.06em;vertical-align:1px;border:1px solid rgba(0,229,255,.7);color:#7ff3ff;background:rgba(0,229,255,.07);}',
      '#kpi-s0 .kpi-s0-badge.is-optional{border:1px dashed rgba(232,251,255,.32);color:rgba(232,251,255,.6);background:transparent;}',
      '#kpi-s0 .kpi-s0-control input,#kpi-s0 .kpi-s0-control select{width:100%;box-sizing:border-box;padding:8px 10px;font:inherit;background:rgba(0,0,0,.4);color:#e8fbff;border:1px solid rgba(0,229,255,.32);border-radius:0;}',
      '#kpi-s0 .kpi-s0-control select option{color:#111;background:#fff;}',
      '#kpi-s0 .kpi-s0-control input:focus,#kpi-s0 .kpi-s0-control select:focus{outline:none;border-color:#00e5ff;box-shadow:0 0 0 1px rgba(0,229,255,.55);}',
      '#kpi-s0 .kpi-s0-date{display:grid;grid-template-columns:1.3fr 1fr 1.2fr;gap:8px;}',
      '#kpi-s0 .kpi-s0-hint{margin-top:5px;font-size:12px;line-height:1.45;color:rgba(232,251,255,.58);}',
      '#kpi-s0 .kpi-s0-error{margin-top:5px;font-size:12px;color:#ff8a8a;}',
      '#kpi-s0 .kpi-s0-error:empty{display:none;}',
      '#kpi-s0 .kpi-s0-field.is-missing input,#kpi-s0 .kpi-s0-field.is-missing select{border-color:#ffb44d;}',
      '#kpi-s0 .kpi-s0-status{min-height:18px;margin:6px 0 0;font-size:12.5px;line-height:1.5;}',
      '#kpi-s0 .kpi-s0-status.is-error{color:#ff8a8a;}',
      '#kpi-s0 .kpi-s0-status.is-warn{color:#ffd27a;}',
      '#kpi-s0 .kpi-s0-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:12px;padding-top:16px;border-top:1px solid rgba(0,229,255,.14);}',
      '#kpi-s0 .kpi-s0-btn{min-width:108px;padding:9px 20px;font:inherit;font-size:13px;font-weight:700;letter-spacing:.04em;cursor:pointer;border:1px solid rgba(232,251,255,.3);background:transparent;color:rgba(232,251,255,.85);}',
      '#kpi-s0 .kpi-s0-btn:hover:not([disabled]){border-color:rgba(0,229,255,.7);color:#e8fbff;}',
      '#kpi-s0 .kpi-s0-btn.is-primary{border-color:#00e5ff;background:rgba(0,229,255,.2);color:#fff;}',
      '#kpi-s0 .kpi-s0-btn.is-primary:hover:not([disabled]){background:rgba(0,229,255,.32);}',
      '#kpi-s0 .kpi-s0-btn[disabled]{opacity:.38;cursor:not-allowed;}',
      '#kpi-s0 .kpi-s0-saved{padding:4px 0 2px;}',
      '#kpi-s0 .kpi-s0-saved-head{margin-bottom:0;}',
      '#kpi-s0 .kpi-s0-saved-head ~ .kpi-s0-status:empty{display:none;}',
      '#kpi-s0 .kpi-s0-saved-head ~ .kpi-s0-actions{border-top:0;}',
      '#kpi-s0 .kpi-s0-saved-title{margin:0 0 12px;font-size:18px;letter-spacing:.1em;font-weight:700;}',
      '#kpi-s0 .kpi-s0-saved-lead{margin:0;font-size:15px;line-height:1.6;}',
      '#kpi-s0 .kpi-s0-saved-body{margin:2px 0 0;font-size:13px;line-height:1.6;color:rgba(232,251,255,.62);}',
      '#kpi-s0 .kpi-s0-summary{display:grid;grid-template-columns:160px 1fr;gap:8px 16px;margin:0 0 16px;padding:14px 16px;border:1px solid rgba(0,229,255,.18);background:rgba(0,229,255,.04);}',
      '#kpi-s0 .kpi-s0-summary dt{margin:0;font-size:12px;letter-spacing:.06em;font-weight:700;color:rgba(0,229,255,.85);}',
      '#kpi-s0 .kpi-s0-summary dd{margin:0;font-variant-numeric:tabular-nums;overflow-wrap:anywhere;}',
      '#kpi-s0 .kpi-s0-note{margin:0 0 4px;padding:10px 14px;border-left:3px solid rgba(0,229,255,.7);background:rgba(0,229,255,.06);line-height:1.6;}',
      '#kpi-s0 .kpi-s0-note.is-strong{border-left-color:#ffd27a;background:rgba(255,210,122,.07);}',
      '#kpi-s0 .kpi-s0-note.is-ok{border-left-color:#0F9403;background:rgba(15,148,3,.08);}',
      '#kpi-s0 .kpi-s0-actions .kpi-s0-btn.is-left{margin-right:auto;}',
      '#kpi-s0 .kpi-s0-via{margin:10px 0 0;font-size:12px;line-height:1.5;color:rgba(232,251,255,.58);text-align:right;}',
      '#kpi-s0 .kpi-s0-confirm{margin-top:12px;padding:14px 16px 4px;border:1px solid rgba(0,229,255,.32);}',
      '#kpi-s0 .kpi-s0-confirm-title{margin:0 0 8px;font-weight:700;}',
      '#kpi-s0 .kpi-s0-confirm ul{margin:0;padding-left:1.2em;font-size:13px;line-height:1.65;color:rgba(232,251,255,.8);}',
      '#kpi-s0 .kpi-s0-confirm .kpi-s0-actions{border-top:0;padding-top:8px;}',
      'body.office-mode #kpi-s0{background:rgba(20,20,20,.32);}',
      'body.office-mode #kpi-s0 .kpi-s0-card{border:1px solid #1c1c1c;background:#f4f1ea;color:#1a1a1c;}',
      'body.office-mode #kpi-s0 .kpi-s0-card::before{background:#1c1c1c;}',
      'body.office-mode #kpi-s0 .kpi-s0-head{border-bottom-color:#d6d0c4;}',
      'body.office-mode #kpi-s0 .kpi-s0-kicker,body.office-mode #kpi-s0 .kpi-s0-progress-label{color:#555;}',
      'body.office-mode #kpi-s0 .kpi-s0-ruler-step::before,body.office-mode #kpi-s0 .kpi-s0-ruler-step::after{background:#d9d2c4;}',
      'body.office-mode #kpi-s0 .kpi-s0-ruler-step.is-skipped::after,body.office-mode #kpi-s0 .kpi-s0-ruler-step.is-skipped+.kpi-s0-ruler-step::before{background:repeating-linear-gradient(90deg,#8a857c 0 5px,transparent 5px 9px);}',
      'body.office-mode #kpi-s0 .kpi-s0-ruler-step.is-active::after,body.office-mode #kpi-s0 .kpi-s0-ruler-step.is-completed::after,body.office-mode #kpi-s0 .kpi-s0-ruler-step.is-completed+.kpi-s0-ruler-step::before{background:#0F9403;}',
      'body.office-mode #kpi-s0 .kpi-s0-ruler-node{border-color:#a9a395;background:#f4f1ea;}',
      'body.office-mode #kpi-s0 .kpi-s0-ruler-step.is-active .kpi-s0-ruler-node{border-color:#0F9403;background:#0F9403;box-shadow:0 0 0 4px rgba(15,148,3,.16);}',
      'body.office-mode #kpi-s0 .kpi-s0-ruler-step.is-completed .kpi-s0-ruler-node{border-color:#0F9403;background:#0F9403;}',
      'body.office-mode #kpi-s0 .kpi-s0-ruler-step.is-skipped .kpi-s0-ruler-node{border-color:#6b665e;}',
      'body.office-mode #kpi-s0 .kpi-s0-ruler-num,body.office-mode #kpi-s0 .kpi-s0-ruler-label{color:#77726a;}',
      'body.office-mode #kpi-s0 .kpi-s0-ruler-step.is-active .kpi-s0-ruler-num,body.office-mode #kpi-s0 .kpi-s0-ruler-step.is-active .kpi-s0-ruler-label{color:#1c1c1c;}',
      'body.office-mode #kpi-s0 .kpi-s0-ruler-step.is-completed .kpi-s0-ruler-num,body.office-mode #kpi-s0 .kpi-s0-ruler-step.is-completed .kpi-s0-ruler-label{color:#3a3a3a;}',
      'body.office-mode #kpi-s0 .kpi-s0-title{letter-spacing:.03em;font-weight:600;}',
      'body.office-mode #kpi-s0 .kpi-s0-lead{color:#2a2a2c;}',
      'body.office-mode #kpi-s0 .kpi-s0-lead2,body.office-mode #kpi-s0 .kpi-s0-progress-rest,body.office-mode #kpi-s0 .kpi-s0-section-note,body.office-mode #kpi-s0 .kpi-s0-hint,body.office-mode #kpi-s0 .kpi-s0-saved-body{color:#66625b;}',
      'body.office-mode #kpi-s0 .kpi-s0-progress-line{background:#ddd6c8;}',
      'body.office-mode #kpi-s0 .kpi-s0-progress-fill{background:#1c1c1c;}',
      'body.office-mode #kpi-s0 .kpi-s0-progress.is-done .kpi-s0-progress-rest{color:#1c1c1c;}',
      'body.office-mode #kpi-s0 .kpi-s0-section-title{color:#3a3a3a;border-bottom-color:#d6d0c4;}',
      'body.office-mode #kpi-s0 .kpi-s0-badge{border-color:#1c1c1c;color:#1c1c1c;background:transparent;}',
      'body.office-mode #kpi-s0 .kpi-s0-badge.is-optional{border-color:#9a948a;color:#6b665e;}',
      'body.office-mode #kpi-s0 .kpi-s0-control input,body.office-mode #kpi-s0 .kpi-s0-control select{background:#fff;color:#1a1a1c;border-color:#a9a395;}',
      'body.office-mode #kpi-s0 .kpi-s0-control input:focus,body.office-mode #kpi-s0 .kpi-s0-control select:focus{border-color:#1c1c1c;box-shadow:0 0 0 1px #1c1c1c;}',
      'body.office-mode #kpi-s0 .kpi-s0-field.is-missing input,body.office-mode #kpi-s0 .kpi-s0-field.is-missing select{border-color:#c77700;}',
      'body.office-mode #kpi-s0 .kpi-s0-error,body.office-mode #kpi-s0 .kpi-s0-status.is-error{color:#b3261e;}',
      'body.office-mode #kpi-s0 .kpi-s0-status.is-warn{color:#9a5a00;}',
      'body.office-mode #kpi-s0 .kpi-s0-actions{border-top-color:#d6d0c4;}',
      'body.office-mode #kpi-s0 .kpi-s0-btn{border-color:#9a948a;color:#1c1c1c;}',
      'body.office-mode #kpi-s0 .kpi-s0-btn:hover:not([disabled]){border-color:#1c1c1c;color:#1c1c1c;}',
      'body.office-mode #kpi-s0 .kpi-s0-btn.is-primary{border-color:#1c1c1c;background:#1c1c1c;color:#fff;}',
      'body.office-mode #kpi-s0 .kpi-s0-btn.is-primary:hover:not([disabled]){background:#3a3a3a;color:#fff;}',
      'body.office-mode #kpi-s0 .kpi-s0-summary{border-color:#d6d0c4;background:#fbf9f4;}',
      'body.office-mode #kpi-s0 .kpi-s0-summary dt{color:#555;}',
      'body.office-mode #kpi-s0 .kpi-s0-note{border-left-color:#1c1c1c;background:#ece7dc;}',
      'body.office-mode #kpi-s0 .kpi-s0-note.is-strong{border-left-color:#c77700;background:#f6ead4;}',
      'body.office-mode #kpi-s0 .kpi-s0-note.is-ok{border-left-color:#0F9403;background:#e6f0e2;}',
      'body.office-mode #kpi-s0 .kpi-s0-via{color:#66625b;}',
      'body.office-mode #kpi-s0 .kpi-s0-confirm{border-color:#a9a395;background:#fbf9f4;}',
      'body.office-mode #kpi-s0 .kpi-s0-confirm ul{color:#2a2a2c;}',
    ].join('');
    (global.document.head || global.document.documentElement).appendChild(style);
  }

  /* Initial Setup steps. Code-side Step 0 is shown to users as step 01. */
  var SETUP_STEPS = ['profile', 'history', 'current', 'target', 'review'];
  var STEP_STATES = ['completed', 'active', 'skipped', 'future'];

  /**
   * opts.current: 0-based active step (-1 for none).
   * opts.states: optional per-step state overriding the default
   * (before current = completed, current = active, after = future).
   * opts.position: 1-based step announced to screen readers (default current + 1).
   */
  function renderStepRuler(c, opts) {
    var o = opts || {};
    var current = typeof o.current === 'number' ? o.current : 0;
    var given = o.states || [];
    var total = SETUP_STEPS.length;
    var items = SETUP_STEPS.map(function (key, i) {
      var st = STEP_STATES.indexOf(given[i]) >= 0 ? given[i] : i < current ? 'completed' : i === current ? 'active' : 'future';
      var num = (i < 9 ? '0' : '') + (i + 1);
      return (
        '<li class="kpi-s0-ruler-step is-' + st + '" data-step="' + key + '" data-state="' + st + '"' +
        (st === 'active' ? ' aria-current="step"' : '') + '>' +
        '<span class="kpi-s0-ruler-node" aria-hidden="true"></span>' +
        '<span class="kpi-s0-ruler-num">' + num + '</span>' +
        '<span class="kpi-s0-ruler-label">' + esc(c.steps[i]) + '</span>' +
        '<span class="kpi-s0-sr">' + esc(c.stepState[st]) + '</span></li>'
      );
    }).join('');
    var position = typeof o.position === 'number' ? o.position : current + 1;
    return (
      '<ol class="kpi-s0-ruler" id="kpi-s0-ruler" aria-label="' +
      esc(fmt(c.stepsLabel, { current: position, total: total })) + '">' + items + '</ol>'
    );
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
      '<div class="kpi-s0-head">' +
      '<p class="kpi-s0-kicker">' + esc(c.kicker) + '</p>' +
      renderStepRuler(c, { current: 0 }) +
      '<h2 class="kpi-s0-title" id="kpi-s0-title">' + esc(c.title) + '</h2>' +
      '<p class="kpi-s0-lead">' + esc(c.lead) + '</p>' +
      '<p class="kpi-s0-lead2">' + esc(c.lead2) + '</p></div>' +
      '<div class="kpi-s0-progress" id="kpi-s0-progress" aria-live="polite">' +
      '<div class="kpi-s0-progress-count" id="kpi-s0-progress-count">' +
      '<span class="kpi-s0-progress-label">' + esc(c.progressLabel) + '</span>' +
      '<span class="kpi-s0-progress-num" id="kpi-s0-progress-num"></span></div>' +
      '<div class="kpi-s0-progress-line" aria-hidden="true"><span class="kpi-s0-progress-fill" id="kpi-s0-progress-fill"></span></div>' +
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
      '<legend class="kpi-s0-section-title">' + esc(c.sectionOptional) +
      '<span class="kpi-s0-section-note">' + esc(c.sectionOptionalNote) + '</span></legend>' +
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
    var cont = !!(state && state.continueSetup);
    return (
      '<div class="kpi-s0-head kpi-s0-saved-head">' +
      '<p class="kpi-s0-kicker">' + esc(c.kicker) + '</p>' +
      renderStepRuler(c, { current: -1, states: ['completed'], position: 1 }) +
      '<div class="kpi-s0-saved" id="kpi-s0-saved">' +
      '<h2 class="kpi-s0-saved-title" id="kpi-s0-title">' + esc(c.savedTitle) + '</h2>' +
      '<p class="kpi-s0-saved-lead">' + esc(c.savedLead) + '</p>' +
      '<p class="kpi-s0-saved-body">' + esc(cont ? c.savedBodyContinue : c.savedBody) + '</p></div></div>' +
      '<div class="kpi-s0-status" id="kpi-s0-status" role="status"></div>' +
      '<div class="kpi-s0-actions">' +
      '<button type="button" class="kpi-s0-btn is-primary" id="kpi-s0-next">' + esc(cont ? c.nextStep : c.next) + '</button></div>'
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
    var num = el('kpi-s0-progress-num');
    var fill = el('kpi-s0-progress-fill');
    var rest = el('kpi-s0-progress-rest');
    if (num) num.textContent = done + ' / ' + total;
    if (fill) fill.style.width = Math.round((done / total) * 100) + '%';
    if (box) box.setAttribute('aria-label', fmt(c.progress, { done: done, total: total }));
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
        var storeOk = writeOpeningDate(form.openingDate, state.startSetup);
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
    card.setAttribute('data-s0-view', 'profile-saved');
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
      startSetup: !!(opts && opts.startSetup === true),
      continueSetup: !!(opts && opts.continueSetup === true),
      onDone: opts && typeof opts.onDone === 'function' ? opts.onDone : null,
    };
    hist = null;
    var card = el('kpi-s0-card');
    card.setAttribute('data-s0-view', 'profile');
    card.removeAttribute('data-s2-kind');
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

  /* ---------- STEP 02 Historical Data ---------- */

  var hist = null;

  function historySummary() {
    var r = readiness();
    if (!r || typeof r.historicalSummary !== 'function') return null;
    return r.historicalSummary(readStore());
  }

  function hasImporterHere() {
    var r = readiness();
    return !!(r && typeof r.hasHistoryImporter === 'function' && r.hasHistoryImporter());
  }

  function renderHistorySummary(h, sum) {
    var na = sum.level === 'not_applicable';
    var rows = [['start', h.start, sum.openingYm]];
    if (!na) rows.push(['range', h.range, sum.rangeStart + h.rangeSep + sum.rangeEnd]);
    rows.push(['status', h.status, h.state[sum.state] || '']);
    if (!na) rows.push(['detected', h.detected, sum.detectedYears.length ? sum.detectedYears.join(', ') : h.none]);
    rows.push(['level', h.level, h.levelText[sum.state === 'present' ? 'present' : sum.level] || '']);
    return (
      '<dl class="kpi-s0-summary" id="kpi-s0-hist-summary">' +
      rows.map(function (r) {
        return '<dt>' + esc(r[1]) + '</dt><dd data-s2-row="' + r[0] + '">' + esc(r[2]) + '</dd>';
      }).join('') +
      '</dl>'
    );
  }

  function historyMessageKey(sum) {
    if (sum.state === 'present' || sum.state === 'skipped') return sum.state;
    return sum.level;
  }

  function renderHistory(c, sum) {
    var h = c.history;
    var msgKey = historyMessageKey(sum);
    var noteClass = msgKey === 'strong' ? ' is-strong' : msgKey === 'present' || msgKey === 'not_applicable' ? ' is-ok' : '';
    var btn = function (id, label, primary, left) {
      return (
        '<button type="button" class="kpi-s0-btn' + (primary ? ' is-primary' : '') + (left ? ' is-left' : '') +
        '" id="' + id + '">' + esc(label) + '</button>'
      );
    };
    var actions = btn('kpi-s0-hist-close', h.close, false, true);
    var hasRegister = true;
    if (sum.state === 'absent') {
      actions += btn('kpi-s0-hist-skip', h.skip) + btn('kpi-s0-hist-register', h.register, true);
    } else if (sum.state === 'present') {
      actions += btn('kpi-s0-hist-register', h.addMore) + btn('kpi-s0-hist-next', h.next, true);
    } else if (sum.state === 'skipped') {
      actions += btn('kpi-s0-hist-register', h.register) + btn('kpi-s0-hist-next', h.next, true);
    } else {
      hasRegister = false;
      actions += btn('kpi-s0-hist-next', h.next, true);
    }
    return (
      '<div class="kpi-s0-head">' +
      '<p class="kpi-s0-kicker">' + esc(c.kicker) + '</p>' +
      renderStepRuler(c, { current: 1 }) +
      '<h2 class="kpi-s0-title" id="kpi-s0-title">' + esc(h.title) + '</h2>' +
      '<p class="kpi-s0-lead">' + esc(h.lead) + '</p></div>' +
      renderHistorySummary(h, sum) +
      '<p class="kpi-s0-note' + noteClass + '" id="kpi-s0-hist-note" data-s2-level="' + esc(msgKey) + '">' +
      esc(h.msg[msgKey] || '') + '</p>' +
      '<div class="kpi-s0-status" id="kpi-s0-status" role="status"></div>' +
      '<div class="kpi-s0-actions" id="kpi-s0-hist-actions">' + actions + '</div>' +
      (hasRegister && !hasImporterHere() ? '<p class="kpi-s0-via" id="kpi-s0-hist-via">' + esc(h.viaAnnual) + '</p>' : '') +
      '<div id="kpi-s0-hist-confirm-host"></div>'
    );
  }

  function renderHistoryDone(c, kind) {
    var h = c.history;
    return (
      '<div class="kpi-s0-head kpi-s0-saved-head">' +
      '<p class="kpi-s0-kicker">' + esc(c.kicker) + '</p>' +
      renderStepRuler(c, { current: -1, states: ['completed', kind === 'skipped' ? 'skipped' : 'completed'], position: 2 }) +
      '<div class="kpi-s0-saved" id="kpi-s0-hist-done-body">' +
      '<h2 class="kpi-s0-saved-title" id="kpi-s0-title">' + esc(h.doneTitle[kind] || '') + '</h2>' +
      '<p class="kpi-s0-saved-lead">' + esc(h.doneLead[kind] || '') + '</p>' +
      '<p class="kpi-s0-saved-body">' + esc(h.doneBody) + '</p></div></div>' +
      '<div class="kpi-s0-status" id="kpi-s0-status" role="status"></div>' +
      '<div class="kpi-s0-actions">' +
      '<button type="button" class="kpi-s0-btn is-primary" id="kpi-s0-hist-done">' + esc(c.next) + '</button></div>'
    );
  }

  function closeHistory() {
    if (rootEl) rootEl.hidden = true;
    hist = null;
  }

  function finishHistory() {
    var done = hist && hist.onDone;
    closeHistory();
    if (typeof done === 'function') done();
  }

  function focusEl(id) {
    try {
      var n = el(id);
      if (n) n.focus();
    } catch (_e) {}
  }

  function showHistoryDone(kind, warn) {
    var c = t(hist.lang);
    var card = el('kpi-s0-card');
    if (!card) return;
    hist.view = 'done';
    card.setAttribute('data-s0-view', 'history-done');
    card.setAttribute('data-s2-kind', kind);
    card.innerHTML = renderHistoryDone(c, kind);
    if (warn) setStatus(c.history.skipWarn, 'warn');
    var btn = el('kpi-s0-hist-done');
    if (btn) btn.addEventListener('click', finishHistory);
    focusEl('kpi-s0-hist-done');
  }

  /** Reuses the existing Annual Past Sales dialog (CSV / Excel import included); STEP 02 returns when it closes. */
  function openPastSalesFromSetup() {
    var btn = global.document.getElementById('annual-past-sales-btn');
    var modal = global.document.getElementById('past-sales-modal');
    var opts = hist ? hist.opts : {};
    var reopen = function () {
      openHistory(Object.assign({}, opts, { entry: 'flow' }));
    };
    closeHistory();
    btn.click();
    if (!modal || modal.hasAttribute('hidden') || typeof global.MutationObserver !== 'function') {
      reopen();
      return;
    }
    var mo = new global.MutationObserver(function () {
      if (!modal.hasAttribute('hidden')) return;
      mo.disconnect();
      reopen();
    });
    mo.observe(modal, { attributes: true, attributeFilter: ['hidden'] });
  }

  function startHistoryImport() {
    if (!hist) return;
    if (hasImporterHere()) {
      openPastSalesFromSetup();
      return;
    }
    var r = readiness();
    var url = r && typeof r.annualSetupUrl === 'function' ? r.annualSetupUrl() : '';
    if (url) global.location.href = url;
  }

  function showSkipConfirm() {
    var c = t(hist.lang);
    var h = c.history;
    var actions = el('kpi-s0-hist-actions');
    var host = el('kpi-s0-hist-confirm-host');
    if (!host) return;
    if (actions) actions.style.display = 'none';
    host.innerHTML =
      '<div class="kpi-s0-confirm" id="kpi-s0-hist-confirm" role="group" aria-labelledby="kpi-s0-hist-confirm-title">' +
      '<p class="kpi-s0-confirm-title" id="kpi-s0-hist-confirm-title">' + esc(h.confirmTitle) + '</p>' +
      '<ul>' + h.confirmLines.map(function (line) {
        return '<li>' + esc(line) + '</li>';
      }).join('') + '</ul>' +
      '<div class="kpi-s0-actions">' +
      '<button type="button" class="kpi-s0-btn" id="kpi-s0-hist-confirm-back">' + esc(h.confirmBack) + '</button>' +
      '<button type="button" class="kpi-s0-btn is-primary" id="kpi-s0-hist-confirm-skip">' + esc(h.confirmSkip) + '</button>' +
      '</div></div>';
    el('kpi-s0-hist-confirm-back').addEventListener('click', function () {
      host.innerHTML = '';
      if (actions) actions.style.display = '';
      focusEl('kpi-s0-hist-skip');
    });
    el('kpi-s0-hist-confirm-skip').addEventListener('click', confirmSkip);
    focusEl('kpi-s0-hist-confirm-back');
  }

  function confirmSkip() {
    if (!hist || hist.saving) return;
    var session = hist;
    var c = t(hist.lang);
    var buttons = [el('kpi-s0-hist-confirm-back'), el('kpi-s0-hist-confirm-skip')];
    if (!writeHistoricalSkipped()) {
      setStatus(c.history.skipFailed, 'error');
      return;
    }
    hist.saving = true;
    buttons.forEach(function (b) {
      if (b) b.disabled = true;
    });
    pushStore().then(function (push) {
      if (hist !== session) return;
      hist.saving = false;
      showHistoryDone('skipped', !(push && push.ok === true));
    });
  }

  function bindHistory() {
    var on = function (id, fn) {
      var n = el(id);
      if (n) n.addEventListener('click', fn);
    };
    on('kpi-s0-hist-close', finishHistory);
    on('kpi-s0-hist-register', startHistoryImport);
    on('kpi-s0-hist-skip', showSkipConfirm);
    on('kpi-s0-hist-next', function () {
      if (hist && hist.sum) showHistoryDone(hist.sum.state);
    });
  }

  /**
   * opts.entry: 'flow' shows STEP 02 itself; 'resume' goes past it when history is not absent
   * (the next soft step is not built yet, so that is the done card).
   */
  function openHistory(opts) {
    var o = opts || {};
    var done = typeof o.onDone === 'function' ? o.onDone : null;
    var root = ensureRoot();
    var sum = historySummary();
    if (!root || !sum) {
      if (done) done();
      return;
    }
    state = null;
    var lang = detectLang();
    hist = { lang: lang, opts: o, onDone: done, sum: sum, view: 'history', saving: false };
    var card = el('kpi-s0-card');
    root.hidden = false;
    if (o.entry === 'resume' && sum.state !== 'absent') {
      showHistoryDone(sum.state);
      return;
    }
    card.setAttribute('data-s0-view', 'history');
    card.setAttribute('data-s2-kind', sum.state);
    card.innerHTML = renderHistory(t(lang), sum);
    bindHistory();
    focusEl(el('kpi-s0-hist-register') && sum.state === 'absent' ? 'kpi-s0-hist-register' : 'kpi-s0-hist-next');
  }

  global.KpiSetupStep0 = {
    __ready: true,
    open: open,
    close: close,
    openHistory: openHistory,
    closeHistory: closeHistory,
    mergeProfile: mergeProfile,
    SETUP_STEPS: SETUP_STEPS.slice(),
    renderStepRuler: function (opts) {
      ensureStyle();
      return renderStepRuler(t(detectLang()), opts);
    },
    COPY: COPY,
  };
})(typeof window !== 'undefined' ? window : this);
