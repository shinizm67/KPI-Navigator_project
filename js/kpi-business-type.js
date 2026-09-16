/**
 * Business Type Foundation — canonical store.meta.businessType.
 * Subsequent units should read via window.KpiBusinessType.getBusinessType()
 * and window.KpiBusinessType.isRestaurantLike().
 */
(function (global) {
  'use strict';

  if (global.KpiBusinessType && global.KpiBusinessType.__ready) {
    return;
  }

  var STORE_KEY = 'kpiNavigator.kpiYearStore';
  var PROFILE_KEY = 'kpi-profile-last';
  var DEFAULT_TYPE = 'restaurant';
  var CANONICAL = [
    'restaurant',
    'retail',
    'hair_salon',
    'fitness',
    'hotel',
    'other',
  ];

  var LEGACY_TO_CANONICAL = {
    restaurant: 'restaurant',
    cafe: 'restaurant',
    wear_shop: 'retail',
    retail: 'retail',
    personal_trainer: 'fitness',
    fitness: 'fitness',
  };

  var LABEL_ALIASES = {
    restaurant: 'restaurant',
    cafe: 'restaurant',
    bar: 'restaurant',
    'coffee shop': 'restaurant',
    wear_shop: 'retail',
    'wear shop': 'retail',
    retail: 'retail',
    personal_trainer: 'fitness',
    fitness: 'fitness',
    gym: 'fitness',
    'personal training': 'fitness',
    'personal trainer': 'fitness',
    飲食店: 'restaurant',
    レストラン: 'restaurant',
    カフェ: 'restaurant',
    バー: 'restaurant',
    服飾店: 'retail',
    小売: 'retail',
    零售: 'retail',
    餐廳: 'restaurant',
    咖啡廳: 'restaurant',
    酒吧: 'restaurant',
    パーソナルトレーナー: 'fitness',
    フィットネス: 'fitness',
    ジム: 'fitness',
    私人教練: 'fitness',
    健身: 'fitness',
  };

  var LABELS = {
    en: {
      restaurant: 'Restaurant',
      retail: 'Retail',
      hair_salon: 'Hair Salon',
      fitness: 'Fitness / Gym / Personal Training',
      hotel: 'Hotel',
      other: 'Other',
      placeholder: '— Select —',
      hintBasic:
        'Business Type is also used for future analysis and to optimize how Pro features are displayed.',
      hintPro:
        'Business Type changes the default PL / MEP expense items and some KPI, Insight, PL Insight, and Floating Window displays.',
      regTitle: 'Register with this Business Type?',
      regBody:
        'Register with this Business Type?\n\nBusiness Type changes the default PL / MEP expense items, some KPIs, Insight, PL Insight, and Floating Window displays.\n\nYou can change it later, but after data has been entered, some past data may no longer fit the current display and analysis model.',
      regBack: 'Back',
      regConfirm: 'Register with this Business Type',
      changeTitle: 'Change Business Type?',
      changeBody:
        'Change Business Type?\n\nChanging Business Type will change the default PL / MEP expense items and some KPI, Insight, PL Insight, and Floating Window displays.\n\nExisting data is not deleted, but some data entered under the previous Business Type may no longer fit the current display and analysis model.',
      changeCancel: 'Cancel',
      changeConfirm: 'Change Business Type',
    },
    ja: {
      restaurant: '飲食店',
      retail: '小売',
      hair_salon: 'ヘアサロン',
      fitness: 'フィットネス / ジム / パーソナルトレーニング',
      hotel: 'ホテル',
      other: 'その他',
      placeholder: '— 選択 —',
      hintBasic:
        'Business Typeは将来の分析およびPro機能の表示最適化にも使用されます。',
      hintPro:
        'Business TypeによってPL / MEP標準費目、一部KPI、Insight、PL Insight、Floating Windowの表示が変化します。',
      regTitle: 'このBusiness Typeで登録しますか？',
      regBody:
        'このBusiness Typeで登録しますか？\n\nBusiness TypeによってPL / MEPの標準費目、一部KPI、Insight、PL Insight、Floating Windowの表示内容が変わります。\n\n後から変更できますが、データ入力後に変更した場合、過去データの一部が現在の表示・分析モデルに適合しなくなる可能性があります。',
      regBack: '戻る',
      regConfirm: 'このBusiness Typeで登録',
      changeTitle: 'Business Typeを変更しますか？',
      changeBody:
        'Business Typeを変更しますか？\n\nBusiness Typeを変更すると、PL / MEPの標準費目、一部KPI、Insight、PL Insight、Floating Windowの表示内容が変更されます。\n\n既存データは削除されませんが、以前のBusiness Typeで入力されたデータの一部が現在の表示・分析モデルに適合しなくなる場合があります。',
      changeCancel: 'Cancel',
      changeConfirm: 'Change Business Type',
    },
    zh: {
      restaurant: '餐廳',
      retail: '零售',
      hair_salon: '美髮沙龍',
      fitness: '健身 / 健身房 / 私人教練',
      hotel: '飯店',
      other: '其他',
      placeholder: '— 請選擇 —',
      hintBasic:
        '業種（Business Type）也會用於日後分析，以及 Pro 功能的顯示最佳化。',
      hintPro:
        '業種會改變 PL / MEP 標準費目，以及部分 KPI、Insight、PL Insight、Floating Window 的顯示內容。',
      regTitle: '要以此業種註冊嗎？',
      regBody:
        '要以此業種註冊嗎？\n\n業種會改變 PL / MEP 的標準費目、部分 KPI、Insight、PL Insight、Floating Window 的顯示內容。\n\n之後可以變更，但若在輸入資料後變更，部分既有資料可能不再符合目前的顯示與分析模型。',
      regBack: '返回',
      regConfirm: '以此業種註冊',
      changeTitle: '要變更業種嗎？',
      changeBody:
        '要變更業種嗎？\n\n變更業種後，PL / MEP 的標準費目、部分 KPI、Insight、PL Insight、Floating Window 的顯示內容會改變。\n\n既有資料不會被刪除，但先前業種所輸入的部分資料，可能不再符合目前的顯示與分析模型。',
      changeCancel: 'Cancel',
      changeConfirm: 'Change Business Type',
    },
  };

  function detectLang() {
    var raw = '';
    try {
      raw = String(
        (document.documentElement && document.documentElement.getAttribute('lang')) || ''
      );
    } catch (_e) {}
    var l = raw.toLowerCase();
    if (l.indexOf('ja') === 0) return 'ja';
    if (l.indexOf('zh') === 0) return 'zh';
    return 'en';
  }

  function copy(msg) {
    return LABELS[detectLang()] || LABELS.en;
  }

  function isCanonical(value) {
    return CANONICAL.indexOf(String(value || '')) >= 0;
  }

  function normalizeBusinessType(raw) {
    if (raw == null) return null;
    var s = String(raw).trim();
    if (!s) return null;
    if (isCanonical(s)) return s;
    var lower = s.toLowerCase();
    if (LEGACY_TO_CANONICAL[lower]) return LEGACY_TO_CANONICAL[lower];
    if (LABEL_ALIASES[lower]) return LABEL_ALIASES[lower];
    if (LABEL_ALIASES[s]) return LABEL_ALIASES[s];
    var langs = ['en', 'ja', 'zh'];
    for (var i = 0; i < langs.length; i++) {
      var pack = LABELS[langs[i]];
      for (var j = 0; j < CANONICAL.length; j++) {
        var code = CANONICAL[j];
        if (pack[code] === s) return code;
      }
    }
    return null;
  }

  function readJson(key) {
    try {
      var raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (_e) {
      return null;
    }
  }

  function writeJson(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (_e) {
      return false;
    }
  }

  function emptyStoreSkeleton() {
    return {
      meta: {
        schemaVersion: 4,
        operatingYear: new Date().getFullYear(),
        legacyMigrated: false,
        selectedDate: null,
      },
      timeline: { dailySales: {}, businessDays: {} },
      years: {},
    };
  }

  function readStoreObject() {
    if (global.KpiYearStore && typeof global.KpiYearStore.getStore === 'function') {
      try {
        var mem = global.KpiYearStore.getStore();
        if (mem && typeof mem === 'object') return mem;
      } catch (_eMem) {}
    }
    var fromLs = readJson(STORE_KEY);
    return fromLs && typeof fromLs === 'object' ? fromLs : null;
  }

  function readMetaBusinessType() {
    var store = readStoreObject();
    if (!store || !store.meta || typeof store.meta !== 'object') return null;
    return normalizeBusinessType(store.meta.businessType);
  }

  function readLegacyProfileBusinessType() {
    var profile = readJson(PROFILE_KEY);
    if (!profile || typeof profile !== 'object') return null;
    return (
      normalizeBusinessType(profile.businessType) ||
      normalizeBusinessType(profile.industry)
    );
  }

  function readPersistedBusinessType() {
    return readMetaBusinessType() || readLegacyProfileBusinessType() || null;
  }

  function getBusinessType() {
    return readPersistedBusinessType() || DEFAULT_TYPE;
  }

  function isRestaurantLike() {
    return getBusinessType() === 'restaurant';
  }

  function persistStoreObject(store) {
    if (!store || typeof store !== 'object') return false;
    if (global.KpiYearStore && typeof global.KpiYearStore.getStore === 'function') {
      try {
        var mem = global.KpiYearStore.getStore();
        if (mem && mem.meta && typeof mem.meta === 'object' && store.meta) {
          mem.meta.businessType = store.meta.businessType;
        }
      } catch (_eMem) {}
    }
    return writeJson(STORE_KEY, store);
  }

  function setBusinessType(value) {
    var next = normalizeBusinessType(value);
    if (!next) return false;
    var store = readStoreObject();
    if (!store || typeof store !== 'object') {
      store = emptyStoreSkeleton();
    } else {
      try {
        store = JSON.parse(JSON.stringify(store));
      } catch (_eCopy) {
        store = emptyStoreSkeleton();
      }
    }
    if (!store.meta || typeof store.meta !== 'object') {
      store.meta = emptyStoreSkeleton().meta;
    }
    store.meta.businessType = next;
    return persistStoreObject(store);
  }

  function label(code, lang) {
    var pack = LABELS[lang || detectLang()] || LABELS.en;
    var canonical = normalizeBusinessType(code) || DEFAULT_TYPE;
    return pack[canonical] || LABELS.en[canonical] || canonical;
  }

  function populateSelect(sel) {
    if (!sel) return;
    var pack = copy();
    var current = String(sel.value || '');
    sel.innerHTML = '';
    var placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = pack.placeholder;
    sel.appendChild(placeholder);
    CANONICAL.forEach(function (code) {
      var opt = document.createElement('option');
      opt.value = code;
      opt.textContent = pack[code];
      sel.appendChild(opt);
    });
    if (current && isCanonical(current)) sel.value = current;
  }

  function applyHint(el, plan) {
    if (!el) return;
    var pack = copy();
    var isPro = String(plan || '').toLowerCase() === 'pro';
    el.textContent = isPro ? pack.hintPro : pack.hintBasic;
  }

  function closeDialog(overlay) {
    if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
  }

  function openDialog(opts) {
    opts = opts || {};
    var existing = document.getElementById('kpi-bt-dialog-overlay');
    if (existing) closeDialog(existing);
    var overlay = document.createElement('div');
    overlay.id = 'kpi-bt-dialog-overlay';
    overlay.className = 'kpi-bt-dialog-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    var box = document.createElement('div');
    box.className = 'kpi-bt-dialog';
    var title = document.createElement('p');
    title.className = 'kpi-bt-dialog__title';
    title.textContent = opts.title || '';
    var body = document.createElement('p');
    body.className = 'kpi-bt-dialog__body';
    body.textContent = opts.body || '';
    var actions = document.createElement('div');
    actions.className = 'kpi-bt-dialog__actions';
    var cancelBtn = document.createElement('button');
    cancelBtn.type = 'button';
    cancelBtn.className = 'kpi-bt-dialog__btn kpi-bt-dialog__btn--cancel';
    cancelBtn.textContent = opts.cancelLabel || 'Cancel';
    var confirmBtn = document.createElement('button');
    confirmBtn.type = 'button';
    confirmBtn.className = 'kpi-bt-dialog__btn kpi-bt-dialog__btn--confirm';
    confirmBtn.textContent = opts.confirmLabel || 'OK';
    actions.appendChild(cancelBtn);
    actions.appendChild(confirmBtn);
    box.appendChild(title);
    box.appendChild(body);
    box.appendChild(actions);
    overlay.appendChild(box);
    document.body.appendChild(overlay);
    function finish(ok) {
      closeDialog(overlay);
      if (ok) {
        if (typeof opts.onConfirm === 'function') opts.onConfirm();
      } else if (typeof opts.onCancel === 'function') {
        opts.onCancel();
      }
    }
    cancelBtn.addEventListener('click', function () {
      finish(false);
    });
    confirmBtn.addEventListener('click', function () {
      finish(true);
    });
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) finish(false);
    });
    confirmBtn.focus();
    return overlay;
  }

  function confirmRegistration(onConfirm, onCancel) {
    var pack = copy();
    return openDialog({
      title: pack.regTitle,
      body: pack.regBody,
      cancelLabel: pack.regBack,
      confirmLabel: pack.regConfirm,
      onConfirm: onConfirm,
      onCancel: onCancel,
    });
  }

  function confirmChange(onConfirm, onCancel) {
    var pack = copy();
    return openDialog({
      title: pack.changeTitle,
      body: pack.changeBody,
      cancelLabel: pack.changeCancel,
      confirmLabel: pack.changeConfirm,
      onConfirm: onConfirm,
      onCancel: onCancel,
    });
  }

  global.KpiBusinessType = {
    __ready: true,
    STORE_KEY: STORE_KEY,
    CANONICAL: CANONICAL.slice(),
    DEFAULT: DEFAULT_TYPE,
    normalizeBusinessType: normalizeBusinessType,
    getBusinessType: getBusinessType,
    readPersistedBusinessType: readPersistedBusinessType,
    setBusinessType: setBusinessType,
    isRestaurantLike: isRestaurantLike,
    label: label,
    populateSelect: populateSelect,
    applyHint: applyHint,
    confirmRegistration: confirmRegistration,
    confirmChange: confirmChange,
    detectLang: detectLang,
  };
})(typeof window !== 'undefined' ? window : this);
