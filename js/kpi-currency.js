/**
 * Shared currency symbol for KPI Navigator.
 * Source of truth: localStorage['kpi-currency'] = JPY|USD|EUR|GBP|TWD
 * Fallback: browser timezone / language guess, then document lang.
 * No FX conversion — display symbol only.
 */
(function (global) {
  var KEY = 'kpi-currency';
  var SYMBOLS = {
    JPY: '¥',
    USD: '$',
    EUR: '€',
    GBP: '£',
    TWD: 'NT$',
  };
  var LABELS = {
    JPY: '¥ - Yen',
    USD: '$ - US Dollar',
    EUR: '€ - Euro',
    GBP: '£ - Pound',
    TWD: 'NT$ - New Taiwan Dollar',
  };
  /** Default list order (after preferred pins). */
  var DEFAULT_ORDER = ['JPY', 'USD', 'EUR', 'GBP', 'TWD'];

  function isCode(c) {
    return !!(c && SYMBOLS[c]);
  }

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
      if (
        l.indexOf('de') === 0 ||
        l.indexOf('fr') === 0 ||
        l.indexOf('it') === 0 ||
        l.indexOf('nl') === 0 ||
        l.indexOf('es') === 0 ||
        l.indexOf('pt-pt') === 0
      ) {
        return 'EUR';
      }
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
      if (isCode(c)) return c;
    } catch (_e) {}
    return guessCode();
  }

  function symbol() {
    return SYMBOLS[code()] || '$';
  }

  function label(c) {
    return LABELS[c] || c || '';
  }

  /**
   * Preferred order for <select>: saved → guessed → defaults.
   * @returns {string[]}
   */
  function preferredOrder() {
    var saved = null;
    try {
      saved = localStorage.getItem(KEY);
    } catch (_e) {}
    var guessed = guessCode();
    var out = [];
    var seen = {};
    function push(c) {
      if (!isCode(c) || seen[c]) return;
      seen[c] = 1;
      out.push(c);
    }
    push(saved);
    push(guessed);
    for (var i = 0; i < DEFAULT_ORDER.length; i++) push(DEFAULT_ORDER[i]);
    return out;
  }

  /**
   * Reorder a currency <select>: blank first, then preferredOrder.
   * Restores saved value when present.
   */
  function arrangeSelect(selectEl) {
    if (!selectEl || !selectEl.options) return;
    var blank = [];
    var byCode = {};
    var i;
    for (i = 0; i < selectEl.options.length; i++) {
      var opt = selectEl.options[i];
      if (!opt.value) blank.push(opt);
      else if (isCode(opt.value)) byCode[opt.value] = opt;
      else byCode[opt.value] = opt;
    }
    var order = preferredOrder();
    var keepValue = selectEl.value;
    try {
      var saved = localStorage.getItem(KEY);
      if (isCode(saved)) keepValue = saved;
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

  global.KpiCurrency = {
    KEY: KEY,
    SYMBOLS: SYMBOLS,
    LABELS: LABELS,
    DEFAULT_ORDER: DEFAULT_ORDER,
    code: code,
    symbol: symbol,
    label: label,
    guessCode: guessCode,
    preferredOrder: preferredOrder,
    arrangeSelect: arrangeSelect,
    format: format,
    zero: zero,
  };

  global.__twFmtMoney = function (n) {
    return format(n, { round: true });
  };
})(typeof window !== 'undefined' ? window : this);
