/**
 * Unit 6C — expense CSV item resolver.
 * Mapping order: canonical lineId, normalized lineId, exact catalog label,
 * saved user alias, then C2-L2 high-confidence synonym.
 * Runtime twin of the contract tests in scripts/_test_expense_csv_import_6c.py
 */
(function (global) {
  'use strict';

  if (global.KpiExpenseCsvImport && global.KpiExpenseCsvImport.__ready) {
    return;
  }

  var SHARED_SYNONYMS = {
    '店舗家賃': 'exp_rent',
    '賃借料': 'exp_rent',
    '広告費': 'exp_advertising'
  };
  var RESTAURANT_SYNONYMS = {
    '食材費': 'exp_food_cost',
    '食材仕入': 'exp_food_cost',
    '原材料費': 'exp_food_cost',
    '飲料費': 'exp_drink_cost',
    'ドリンク仕入': 'exp_drink_cost'
  };

  function normText(v) {
    return String(v == null ? '' : v).replace(/\s+/g, '').toLowerCase();
  }

  function looksLikeLineId(raw) {
    return /^exp_[a-z0-9_]+$/i.test(String(raw || '').trim());
  }

  function isImportableLine(line) {
    return !!(line && line.lineId && line.active !== false && !line.presetOrphan);
  }

  function isHeaderItemToken(raw) {
    var k = normText(raw);
    return k === 'lineid' || k === 'item' || k === 'label';
  }

  function readCanonicalBusinessType(opts) {
    if (opts && opts.businessType) return String(opts.businessType);
    var api = global.KpiBusinessType;
    if (!api || typeof api.readMetaBusinessType !== 'function') return '';
    return api.readMetaBusinessType() || '';
  }

  function resolveSynonym(k, byId, opts) {
    var sharedId = SHARED_SYNONYMS[k];
    if (sharedId && byId[sharedId]) return byId[sharedId];
    if (readCanonicalBusinessType(opts) !== 'restaurant') return null;
    var restId = RESTAURANT_SYNONYMS[k];
    if (restId && byId[restId]) return byId[restId];
    return null;
  }

  function makeResolver(lines, aliases, opts) {
    var importable = [];
    (lines || []).forEach(function (line) {
      if (isImportableLine(line)) importable.push(line);
    });
    var byId = {};
    var byIdNorm = {};
    importable.forEach(function (line) {
      var id = String(line.lineId);
      byId[id] = line;
      byIdNorm[normText(id)] = line;
    });
    var byLabel = {};
    importable.forEach(function (line) {
      [line.labelJa, line.labelEn, line.labelZh, line.labelZhTw].forEach(function (label) {
        var k = normText(label);
        if (k && !byLabel[k] && !byIdNorm[k]) byLabel[k] = line;
      });
    });
    return function (display) {
      var raw = String(display == null ? '' : display).trim();
      if (!raw || isHeaderItemToken(raw)) return null;
      if (byId[raw]) return byId[raw];
      var k = normText(raw);
      if (byIdNorm[k]) return byIdNorm[k];
      if (byLabel[k]) return byLabel[k];
      var aid = aliases && aliases[k];
      if (aid && byId[String(aid)]) return byId[String(aid)];
      if (looksLikeLineId(raw)) return null;
      return resolveSynonym(k, byId, opts) || null;
    };
  }

  global.KpiExpenseCsvImport = {
    __ready: true,
    normText: normText,
    looksLikeLineId: looksLikeLineId,
    isImportableLine: isImportableLine,
    isHeaderItemToken: isHeaderItemToken,
    makeResolver: makeResolver,
  };
})(typeof window !== 'undefined' ? window : this);
