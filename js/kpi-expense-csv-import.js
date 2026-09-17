/**
 * Unit 6C — expense CSV item resolver.
 * Mapping order: canonical lineId, then current catalog label, then import alias.
 * Runtime twin of the contract tests in scripts/_test_expense_csv_import_6c.py
 */
(function (global) {
  'use strict';

  if (global.KpiExpenseCsvImport && global.KpiExpenseCsvImport.__ready) {
    return;
  }

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

  function makeResolver(lines, aliases) {
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
      return null;
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
