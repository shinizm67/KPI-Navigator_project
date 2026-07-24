/**
 * Shared currency symbol for KPI Navigator.
 * Source of truth: localStorage['kpi-currency'] = JPY|USD|EUR|GBP
 * Fallback: document lang (ja → JPY, else USD). No FX conversion — display symbol only.
 */
(function (global) {
  var KEY = 'kpi-currency';
  var SYMBOLS = { JPY: '¥', USD: '$', EUR: '€', GBP: '£' };

  function code() {
    try {
      var c = localStorage.getItem(KEY);
      if (c && SYMBOLS[c]) return c;
    } catch (_e) {}
    var lang = String(
      (global.document && document.documentElement && document.documentElement.lang) || ''
    ).toLowerCase();
    return lang.indexOf('ja') === 0 ? 'JPY' : 'USD';
  }

  function symbol() {
    return SYMBOLS[code()] || '$';
  }

  /**
   * @param {number|string} n
   * @param {{round?:boolean,signed?:boolean,minusGlyph?:string,locale?:string,maximumFractionDigits?:number}} [opts]
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
    code: code,
    symbol: symbol,
    format: format,
    zero: zero,
  };

  // Insight / TW helpers used across pages
  global.__twFmtMoney = function (n) {
    return format(n, { round: true });
  };
})(typeof window !== 'undefined' ? window : this);
