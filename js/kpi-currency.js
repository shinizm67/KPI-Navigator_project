/**
 * Shared currency catalog + display for KPI Pilot / Profile.
 * Canonical save: ISO 4217 3-letter code.
 * Source of truth for app symbol: localStorage['kpi-currency']
 * No FX conversion — display symbol / labels only.
 */
(function (global) {
  /* KPI-PROFILE-CURRENCY-CATALOG */
  var KEY = 'kpi-currency';

  var CURRENCY_CODES = [
    'JPY', 'USD', 'GBP', 'CAD', 'AUD', 'NZD', 'EUR', 'SGD', 'TWD', 'HKD',
    'KRW', 'CNY', 'CHF', 'SEK', 'NOK', 'DKK', 'AED', 'INR', 'ZAR'
  ];

  var SYMBOLS = {
    JPY: '¥',
    USD: '$',
    GBP: '£',
    CAD: 'C$',
    AUD: 'A$',
    NZD: 'NZ$',
    EUR: '€',
    SGD: 'S$',
    TWD: 'NT$',
    HKD: 'HK$',
    KRW: '₩',
    CNY: 'CN¥',
    CHF: 'CHF',
    SEK: 'kr',
    NOK: 'kr',
    DKK: 'kr',
    AED: 'AED',
    INR: '₹',
    ZAR: 'R'
  };

  var LABELS_BY_LOCALE = {
    ja: {
      JPY: '¥ - 日本円',
      USD: '$ - 米ドル',
      GBP: '£ - 英ポンド',
      CAD: 'C$ - カナダドル',
      AUD: 'A$ - 豪ドル',
      NZD: 'NZ$ - NZドル',
      EUR: '€ - ユーロ',
      SGD: 'S$ - シンガポールドル',
      TWD: 'NT$ - 台湾ドル',
      HKD: 'HK$ - 香港ドル',
      KRW: '₩ - 韓国ウォン',
      CNY: 'CN¥ - 人民元',
      CHF: 'CHF - スイスフラン',
      SEK: 'kr - スウェーデンクローナ',
      NOK: 'kr - ノルウェークローネ',
      DKK: 'kr - デンマーククローネ',
      AED: 'AED - UAEディルハム',
      INR: '₹ - インドルピー',
      ZAR: 'R - 南アフリカランド'
    },
    en: {
      JPY: '¥ - Japanese Yen',
      USD: '$ - US Dollar',
      GBP: '£ - British Pound',
      CAD: 'C$ - Canadian Dollar',
      AUD: 'A$ - Australian Dollar',
      NZD: 'NZ$ - New Zealand Dollar',
      EUR: '€ - Euro',
      SGD: 'S$ - Singapore Dollar',
      TWD: 'NT$ - New Taiwan Dollar',
      HKD: 'HK$ - Hong Kong Dollar',
      KRW: '₩ - South Korean Won',
      CNY: 'CN¥ - Chinese Yuan',
      CHF: 'CHF - Swiss Franc',
      SEK: 'kr - Swedish Krona',
      NOK: 'kr - Norwegian Krone',
      DKK: 'kr - Danish Krone',
      AED: 'AED - UAE Dirham',
      INR: '₹ - Indian Rupee',
      ZAR: 'R - South African Rand'
    },
    'zh-tw': {
      JPY: '¥ - 日圓',
      USD: '$ - 美元',
      GBP: '£ - 英鎊',
      CAD: 'C$ - 加拿大元',
      AUD: 'A$ - 澳幣',
      NZD: 'NZ$ - 紐西蘭元',
      EUR: '€ - 歐元',
      SGD: 'S$ - 新加坡元',
      TWD: 'NT$ - 新台幣',
      HKD: 'HK$ - 港幣',
      KRW: '₩ - 韓元',
      CNY: 'CN¥ - 人民幣',
      CHF: 'CHF - 瑞士法郎',
      SEK: 'kr - 瑞典克朗',
      NOK: 'kr - 挪威克朗',
      DKK: 'kr - 丹麥克朗',
      AED: 'AED - 阿聯迪拉姆',
      INR: '₹ - 印度盧比',
      ZAR: 'R - 南非蘭特'
    }
  };

  /** Backward-compatible flat English labels. */
  var LABELS = LABELS_BY_LOCALE.en;

  /** Default list order (after preferred pins). */
  var DEFAULT_ORDER = CURRENCY_CODES.slice();

  var COUNTRY_CURRENCY = {
    JP: 'JPY',
    US: 'USD',
    GB: 'GBP',
    CA: 'CAD',
    AU: 'AUD',
    NZ: 'NZD',
    IE: 'EUR',
    SG: 'SGD',
    TW: 'TWD',
    HK: 'HKD',
    KR: 'KRW',
    CN: 'CNY',
    DE: 'EUR',
    FR: 'EUR',
    IT: 'EUR',
    ES: 'EUR',
    NL: 'EUR',
    BE: 'EUR',
    AT: 'EUR',
    FI: 'EUR',
    PT: 'EUR',
    CH: 'CHF',
    SE: 'SEK',
    NO: 'NOK',
    DK: 'DKK',
    AE: 'AED',
    IN: 'INR',
    ZA: 'ZAR'
  };

  function localeOf(locale) {
    var s = String(locale || '').toLowerCase().replace(/_/g, '-');
    if (s.indexOf('ja') === 0) return 'ja';
    if (s.indexOf('zh') === 0) return 'zh-tw';
    return 'en';
  }

  function localeFromDocument() {
    if (global.KpiProfileLocation && typeof global.KpiProfileLocation.localeFromDocument === 'function') {
      return localeOf(global.KpiProfileLocation.localeFromDocument());
    }
    var docLang = String(
      (global.document && document.documentElement && document.documentElement.lang) || ''
    ).toLowerCase();
    return localeOf(docLang);
  }

  function isCode(c) {
    return !!(c && SYMBOLS[c]);
  }

  function fold(s) {
    return String(s == null ? '' : s)
      .trim()
      .toLowerCase()
      .replace(/\s+/g, ' ');
  }

  function buildLegacyAliasMap() {
    var map = {
      yen: 'JPY',
      'japanese yen': 'JPY',
      '¥ - yen': 'JPY',
      '日本円': 'JPY',
      '日圓': 'JPY',
      dollar: 'USD',
      'us dollar': 'USD',
      '米ドル': 'USD',
      '美元': 'USD',
      euro: 'EUR',
      'ユーロ': 'EUR',
      '歐元': 'EUR',
      pound: 'GBP',
      'british pound': 'GBP',
      '£ - pound': 'GBP',
      '英ポンド': 'GBP',
      '英鎊': 'GBP',
      'new taiwan dollar': 'TWD',
      'taiwan dollar': 'TWD',
      'nt$ - new taiwan dollar': 'TWD',
      '台湾ドル': 'TWD',
      '新台幣': 'TWD'
    };
    var locs = ['ja', 'en', 'zh-tw'];
    for (var i = 0; i < locs.length; i++) {
      var labels = LABELS_BY_LOCALE[locs[i]];
      Object.keys(labels).forEach(function (code) {
        map[fold(labels[code])] = code;
        map[fold(code)] = code;
        var sym = SYMBOLS[code];
        if (sym) map[fold(sym)] = code;
      });
    }
    return map;
  }

  var LEGACY_ALIASES = buildLegacyAliasMap();

  /**
   * Lightweight locale guess (no IP / no network).
   * Priority: timezone → navigator.languages → document.lang → USD
   */
  function guessCode() {
    try {
      var tz =
        (global.Intl &&
          Intl.DateTimeFormat &&
          Intl.DateTimeFormat().resolvedOptions().timeZone) ||
        '';
      if (tz === 'Asia/Taipei') return 'TWD';
      if (tz === 'Asia/Tokyo') return 'JPY';
      if (tz === 'Europe/London') return 'GBP';
      if (tz.indexOf('Europe/') === 0) return 'EUR';
      if (tz.indexOf('America/') === 0) return 'USD';
      if (tz === 'Australia/Sydney' || tz.indexOf('Australia/') === 0) return 'AUD';
      if (tz.indexOf('Pacific/Auckland') === 0) return 'NZD';
      if (tz === 'Asia/Singapore') return 'SGD';
      if (tz === 'Asia/Hong_Kong') return 'HKD';
      if (tz === 'Asia/Seoul') return 'KRW';
      if (tz === 'Asia/Shanghai') return 'CNY';
      if (tz === 'Europe/Zurich') return 'CHF';
      if (tz === 'Europe/Stockholm') return 'SEK';
      if (tz === 'Europe/Oslo') return 'NOK';
      if (tz === 'Europe/Copenhagen') return 'DKK';
      if (tz === 'Asia/Dubai') return 'AED';
      if (tz === 'Asia/Kolkata' || tz === 'Asia/Calcutta') return 'INR';
      if (tz === 'Africa/Johannesburg') return 'ZAR';
    } catch (_e) {}

    var langs = [];
    try {
      if (global.navigator && navigator.languages && navigator.languages.length) {
        langs = Array.prototype.slice.call(navigator.languages);
      } else if (global.navigator && navigator.language) {
        langs = [navigator.language];
      }
    } catch (_e2) {}
    for (var i = 0; i < langs.length; i++) {
      var l = String(langs[i] || '').toLowerCase().replace(/_/g, '-');
      if (l === 'zh-tw' || l.indexOf('zh-tw') === 0 || l === 'zh-hant-tw') return 'TWD';
      if (l.indexOf('ja') === 0) return 'JPY';
      if (l === 'en-gb' || l.indexOf('en-gb') === 0) return 'GBP';
      if (l === 'en-au' || l.indexOf('en-au') === 0) return 'AUD';
      if (l === 'en-ca' || l.indexOf('en-ca') === 0) return 'CAD';
      if (l === 'en-nz' || l.indexOf('en-nz') === 0) return 'NZD';
      if (
        l.indexOf('de') === 0 ||
        l.indexOf('fr') === 0 ||
        l.indexOf('it') === 0 ||
        l.indexOf('nl') === 0 ||
        l.indexOf('es') === 0 ||
        l.indexOf('pt-pt') === 0 ||
        l.indexOf('fi') === 0
      ) {
        return 'EUR';
      }
      if (l.indexOf('sv') === 0) return 'SEK';
      if (l.indexOf('nb') === 0 || l.indexOf('nn') === 0 || l === 'no') return 'NOK';
      if (l.indexOf('da') === 0) return 'DKK';
      if (l.indexOf('ko') === 0) return 'KRW';
      if (l.indexOf('zh-cn') === 0 || l === 'zh-hans') return 'CNY';
      if (l.indexOf('ar-ae') === 0) return 'AED';
      if (l.indexOf('hi') === 0 || l.indexOf('en-in') === 0) return 'INR';
      if (l.indexOf('af') === 0 || l.indexOf('en-za') === 0) return 'ZAR';
    }

    var docLang = String(
      (global.document && document.documentElement && document.documentElement.lang) || ''
    ).toLowerCase();
    if (
      docLang.indexOf('zh-tw') === 0 ||
      docLang === 'zh-hant' ||
      docLang.indexOf('zh-hant-tw') === 0
    ) {
      return 'TWD';
    }
    if (docLang.indexOf('ja') === 0) return 'JPY';
    return 'USD';
  }

  function code() {
    try {
      var c = localStorage.getItem(KEY);
      var n = normalizeCode(c);
      if (n) return n;
    } catch (_e) {}
    return guessCode();
  }

  function symbol() {
    return SYMBOLS[code()] || '$';
  }

  function label(c, locale) {
    var loc = localeOf(locale || localeFromDocument());
    var map = LABELS_BY_LOCALE[loc] || LABELS_BY_LOCALE.en;
    var key = normalizeCode(c) || c;
    return (key && map[key]) || LABELS[key] || key || '';
  }

  function displayLabel(raw, locale) {
    var n = normalizeCode(raw);
    if (n) return label(n, locale);
    return String(raw == null ? '' : raw).trim();
  }

  function normalizeCode(raw) {
    var s = String(raw == null ? '' : raw).trim();
    if (!s) return '';
    var upper = s.toUpperCase();
    if (isCode(upper)) return upper;
    var aliased = LEGACY_ALIASES[fold(s)];
    if (aliased && isCode(aliased)) return aliased;
    var m = s.match(/\b([A-Z]{3})\b/);
    if (m && isCode(m[1])) return m[1];
    return '';
  }

  function saveCode(raw) {
    return normalizeCode(raw);
  }

  function resolveCountryCode(countryRaw) {
    var s = String(countryRaw == null ? '' : countryRaw).trim();
    if (!s) return '';
    if (global.KpiProfileLocation) {
      if (typeof global.KpiProfileLocation.canonicalCountry === 'function') {
        var c1 = global.KpiProfileLocation.canonicalCountry(s);
        if (c1) return c1;
      }
      if (typeof global.KpiProfileLocation.saveCountry === 'function') {
        var c2 = global.KpiProfileLocation.saveCountry(s);
        if (c2 && /^[A-Z]{2}$/.test(c2)) return c2;
      }
    }
    if (/^[A-Za-z]{2}$/.test(s)) return s.toUpperCase();
    return '';
  }

  function currencyForCountry(countryRaw) {
    var cc = resolveCountryCode(countryRaw);
    return (cc && COUNTRY_CURRENCY[cc]) || '';
  }

  /**
   * Preferred order for <select>: saved → guessed → country hint → defaults.
   * @returns {string[]}
   */
  function preferredOrder(opts) {
    opts = opts || {};
    var saved = null;
    try {
      saved = normalizeCode(localStorage.getItem(KEY));
    } catch (_e) {}
    var guessed = guessCode();
    var fromCountry = currencyForCountry(opts.country);
    var out = [];
    var seen = {};
    function push(c) {
      var n = normalizeCode(c);
      if (!isCode(n) || seen[n]) return;
      seen[n] = 1;
      out.push(n);
    }
    push(opts.selected);
    push(saved);
    push(fromCountry);
    push(guessed);
    for (var i = 0; i < DEFAULT_ORDER.length; i++) push(DEFAULT_ORDER[i]);
    return out;
  }

  function blankOptionLabel(locale) {
    var loc = localeOf(locale || localeFromDocument());
    if (loc === 'ja') return '— 選択 —';
    if (loc === 'zh-tw') return '— 選擇 —';
    return '— Select —';
  }

  /**
   * Rebuild currency <select> from catalog (locale labels).
   * Restores selected / saved value when present.
   */
  function fillSelect(selectEl, opts) {
    if (!selectEl) return;
    opts = opts || {};
    var locale = localeOf(opts.locale || localeFromDocument());
    var labels = LABELS_BY_LOCALE[locale] || LABELS_BY_LOCALE.en;
    var keep = normalizeCode(opts.selected != null ? opts.selected : selectEl.value);
    if (!keep) {
      try {
        keep = normalizeCode(localStorage.getItem(KEY));
      } catch (_e) {}
    }
    var order = preferredOrder({ selected: keep, country: opts.country });
    while (selectEl.firstChild) selectEl.removeChild(selectEl.firstChild);
    var blank = global.document.createElement('option');
    blank.value = '';
    blank.textContent = blankOptionLabel(locale);
    selectEl.appendChild(blank);
    for (var i = 0; i < order.length; i++) {
      var codeVal = order[i];
      var opt = global.document.createElement('option');
      opt.value = codeVal;
      opt.textContent = labels[codeVal] || LABELS[codeVal] || codeVal;
      selectEl.appendChild(opt);
    }
    if (keep && isCode(keep)) selectEl.value = keep;
    else selectEl.value = '';
  }

  /**
   * Reorder a currency <select>: blank first, then preferredOrder.
   * Also refreshes option labels when catalog codes are present.
   * Restores saved value when present.
   */
  function arrangeSelect(selectEl, opts) {
    if (!selectEl || !selectEl.options) return;
    opts = opts || {};
    var existingCodes = [];
    var i;
    for (i = 0; i < selectEl.options.length; i++) {
      var v = selectEl.options[i].value;
      if (v && isCode(v)) existingCodes.push(v);
    }
    if (existingCodes.length || opts.forceCatalog) {
      fillSelect(selectEl, opts);
      return;
    }
    var blank = [];
    var byCode = {};
    for (i = 0; i < selectEl.options.length; i++) {
      var opt = selectEl.options[i];
      if (!opt.value) blank.push(opt);
      else if (isCode(opt.value)) byCode[opt.value] = opt;
      else byCode[opt.value] = opt;
    }
    var order = preferredOrder(opts);
    var keepValue = normalizeCode(selectEl.value);
    try {
      var saved = normalizeCode(localStorage.getItem(KEY));
      if (saved) keepValue = saved;
    } catch (_e) {}

    while (selectEl.firstChild) selectEl.removeChild(selectEl.firstChild);
    for (i = 0; i < blank.length; i++) selectEl.appendChild(blank[i]);
    for (i = 0; i < order.length; i++) {
      if (byCode[order[i]]) {
        selectEl.appendChild(byCode[order[i]]);
        delete byCode[order[i]];
      }
    }
    Object.keys(byCode).forEach(function (k) {
      selectEl.appendChild(byCode[k]);
    });
    if (keepValue) selectEl.value = keepValue;
  }

  /**
   * Suggest representative currency from country when select is empty
   * and the user has not explicitly chosen a currency.
   */
  function maybeSuggestFromCountry(selectEl, countryRaw, opts) {
    opts = opts || {};
    if (!selectEl) return '';
    if (opts.userSet) return selectEl.value || '';
    if (normalizeCode(selectEl.value)) return selectEl.value;
    var suggested = currencyForCountry(countryRaw);
    if (suggested) {
      if (![].some.call(selectEl.options, function (o) { return o.value === suggested; })) {
        fillSelect(selectEl, {
          locale: opts.locale,
          selected: suggested,
          country: countryRaw,
          forceCatalog: true
        });
      }
      selectEl.value = suggested;
    }
    return selectEl.value || '';
  }

  /**
   * @param {number|string} n
   * @param {{round?:boolean,signed?:boolean,minusGlyph?:string,locale?:string,maximumFractionDigits?:number,minimumFractionDigits?:number}} [opts]
   */
  function format(n, opts) {
    opts = opts || {};
    var num = Number(n);
    if (!isFinite(num)) num = 0;
    var rounded = opts.round ? Math.round(num) : num;
    var abs = Math.abs(rounded);
    var locale = opts.locale || 'en-US';
    var locOpts = {};
    if (opts.maximumFractionDigits != null || opts.minimumFractionDigits != null) {
      locOpts.maximumFractionDigits =
        opts.maximumFractionDigits != null ? opts.maximumFractionDigits : 0;
      locOpts.minimumFractionDigits =
        opts.minimumFractionDigits != null ? opts.minimumFractionDigits : 0;
    }
    var body = abs.toLocaleString(locale, locOpts);
    var sym = symbol();
    var minus = opts.minusGlyph || '−';
    if (opts.signed) {
      if (rounded > 0) return '+' + sym + body;
      if (rounded < 0) return minus + sym + body;
      return sym + body;
    }
    if (rounded < 0) return minus + sym + body;
    return sym + body;
  }

  function zero() {
    return symbol() + '0';
  }

  /** Display precision: JPY → 0 decimals, others → 2. Display-only. */
  function fractionDigits(currencyCode) {
    var c = normalizeCode(currencyCode != null ? currencyCode : code()) || code();
    return c === 'JPY' ? 0 : 2;
  }

  /**
   * Currency-aware money display (does not mutate stored values).
   * @param {number|string} n
   * @param {{signed?:boolean,minusGlyph?:string,locale?:string,currency?:string}} [opts]
   */
  function formatMoney(n, opts) {
    opts = opts || {};
    var digits = fractionDigits(opts.currency);
    var num = Number(n);
    if (!isFinite(num)) num = 0;
    var scaled = digits === 0 ? Math.round(num) : Math.round(num * 100) / 100;
    return format(scaled, {
      signed: opts.signed,
      minusGlyph: opts.minusGlyph,
      locale: opts.locale,
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    });
  }

  global.KpiCurrency = {
    KEY: KEY,
    CURRENCY_CODES: CURRENCY_CODES,
    SYMBOLS: SYMBOLS,
    LABELS: LABELS,
    LABELS_BY_LOCALE: LABELS_BY_LOCALE,
    DEFAULT_ORDER: DEFAULT_ORDER,
    COUNTRY_CURRENCY: COUNTRY_CURRENCY,
    code: code,
    symbol: symbol,
    label: label,
    displayLabel: displayLabel,
    normalizeCode: normalizeCode,
    saveCode: saveCode,
    currencyForCountry: currencyForCountry,
    guessCode: guessCode,
    preferredOrder: preferredOrder,
    fillSelect: fillSelect,
    arrangeSelect: arrangeSelect,
    maybeSuggestFromCountry: maybeSuggestFromCountry,
    format: format,
    zero: zero,
    fractionDigits: fractionDigits,
    formatMoney: formatMoney,
  };

  global.__twFmtMoney = function (n) {
    return format(n, { round: true });
  };
})(typeof window !== 'undefined' ? window : this);
