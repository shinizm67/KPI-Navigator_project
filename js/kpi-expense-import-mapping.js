/**
 * C2-L3-B — Persistent expense import mapping + user-scoped aliases.
 *
 * Not a PL catalog sibling (saveLines would wipe it). Gateway mirrors this
 * key as pl.expenseImportMapping. Amount hold stays in KpiExpenseUnknownHold.
 *
 * records keyed by normalizedLabel (upsert). Same-file reimport updates in
 * place; does not append infinite history. Amount replace/add/skip is L3-A.
 *
 * status: auto | user-assigned | unknown | skipped
 * via (internal): lineId | label | alias | synonym | none
 */
(function (global) {
  'use strict';

  if (global.KpiExpenseImportMapping && global.KpiExpenseImportMapping.__ready) {
    return;
  }

  var STORAGE_KEY = 'kpiNavigator.plExpenseImportMapping';
  var LEGACY_ALIAS_KEY = 'kpiNavigator.plExpenseImportAliases';
  var SCHEMA_VERSION = 1;

  function emptyBlob() {
    return { schemaVersion: SCHEMA_VERSION, aliases: {}, records: {} };
  }

  function normText(v) {
    return String(v == null ? '' : v).replace(/\s+/g, '').toLowerCase();
  }

  function isRealGateway(g) {
    return !!(g && g.__kpiStoreSyncReady && typeof g.setJson === 'function' && typeof g.getJson === 'function');
  }

  function readBlob() {
    var g = global.__KPI_DATA_GATEWAY;
    if (isRealGateway(g)) {
      try {
        var via = g.getJson(STORAGE_KEY);
        if (via && typeof via === 'object') return normalizeBlob(via);
      } catch (_eGw) {}
    }
    try {
      var raw = global.localStorage && global.localStorage.getItem(STORAGE_KEY);
      var parsed = raw ? JSON.parse(raw) : null;
      if (parsed && typeof parsed === 'object') return normalizeBlob(parsed);
    } catch (_e) {}
    return emptyBlob();
  }

  function normalizeBlob(raw) {
    var blob = emptyBlob();
    if (raw.schemaVersion) blob.schemaVersion = SCHEMA_VERSION;
    if (raw.aliases && typeof raw.aliases === 'object' && !Array.isArray(raw.aliases)) {
      blob.aliases = raw.aliases;
    }
    if (raw.records && typeof raw.records === 'object' && !Array.isArray(raw.records)) {
      blob.records = raw.records;
    }
    return blob;
  }

  function writeBlob(blob) {
    var next = normalizeBlob(blob || emptyBlob());
    next.schemaVersion = SCHEMA_VERSION;
    var g = global.__KPI_DATA_GATEWAY;
    if (isRealGateway(g)) {
      try {
        g.setJson(STORAGE_KEY, next);
        return true;
      } catch (_eGw) {}
    }
    try {
      global.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return true;
    } catch (_e) {
      return false;
    }
  }

  function migrateLegacyAliases(blob) {
    try {
      var raw = global.localStorage && global.localStorage.getItem(LEGACY_ALIAS_KEY);
      if (!raw) return blob;
      var legacy = JSON.parse(raw);
      if (!legacy || typeof legacy !== 'object' || Array.isArray(legacy)) {
        global.localStorage.removeItem(LEGACY_ALIAS_KEY);
        return blob;
      }
      Object.keys(legacy).forEach(function (k) {
        if (!blob.aliases[k] && legacy[k]) blob.aliases[k] = String(legacy[k]);
      });
      writeBlob(blob);
      global.localStorage.removeItem(LEGACY_ALIAS_KEY);
    } catch (_e) {}
    return blob;
  }

  function loadAliases() {
    var blob = migrateLegacyAliases(readBlob());
    return blob.aliases && typeof blob.aliases === 'object' ? blob.aliases : {};
  }

  function saveAliases(aliases) {
    var blob = readBlob();
    blob.aliases = aliases && typeof aliases === 'object' && !Array.isArray(aliases) ? aliases : {};
    writeBlob(blob);
    try {
      if (global.localStorage) global.localStorage.removeItem(LEGACY_ALIAS_KEY);
    } catch (_eRm) {}
    return blob.aliases;
  }

  function nextImportBatchId() {
    return 'imp_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 8);
  }

  function classifyVia(raw, line, aliases) {
    if (!line) return 'none';
    var id = String(line.lineId || '');
    var trimmed = String(raw == null ? '' : raw).trim();
    if (trimmed === id) return 'lineId';
    var k = normText(trimmed);
    if (k && normText(id) === k) return 'lineId';
    var labels = [line.labelJa, line.labelEn, line.labelZh, line.labelZhTw];
    var i;
    for (i = 0; i < labels.length; i++) {
      if (labels[i] && normText(labels[i]) === k) return 'label';
    }
    if (aliases && aliases[k] && String(aliases[k]) === id) return 'alias';
    return 'synonym';
  }

  function statusFor(via, resolvedLineId, skipped) {
    if (skipped) return 'skipped';
    if (!resolvedLineId) return 'unknown';
    if (via === 'alias' || via === 'user-assigned') return 'user-assigned';
    return 'auto';
  }

  function unknownIdFor(normalizedLabel) {
    if (global.KpiExpenseUnknownHold && typeof global.KpiExpenseUnknownHold.unknownIdFor === 'function') {
      return global.KpiExpenseUnknownHold.unknownIdFor(normalizedLabel);
    }
    return '';
  }

  function mergeDateRange(prev, incoming) {
    var from = incoming && incoming.from ? String(incoming.from) : '';
    var to = incoming && incoming.to ? String(incoming.to) : '';
    if (!from && prev && prev.from) from = String(prev.from);
    if (!to && prev && prev.to) to = String(prev.to);
    if (prev && prev.from && from && String(prev.from) < from) from = String(prev.from);
    if (prev && prev.to && to && String(prev.to) > to) to = String(prev.to);
    if (!from && !to) return null;
    return { from: from || to, to: to || from };
  }

  function upsertEntries(entries, meta) {
    var list = Array.isArray(entries) ? entries : [];
    if (!list.length) return readBlob();
    var blob = migrateLegacyAliases(readBlob());
    if (!blob.records || typeof blob.records !== 'object') blob.records = {};
    var importedAt = meta && meta.importedAt != null ? Number(meta.importedAt) : Date.now();
    if (!isFinite(importedAt)) importedAt = Date.now();
    var batchId = meta && meta.importBatchId ? String(meta.importBatchId) : nextImportBatchId();
    var filename = meta && meta.sourceFilename ? String(meta.sourceFilename) : '';
    list.forEach(function (rawEntry) {
      if (!rawEntry) return;
      var original = String(rawEntry.originalLabel == null ? '' : rawEntry.originalLabel).trim();
      var normalized = normText(rawEntry.normalizedLabel || original);
      if (!normalized) return;
      var resolvedLineId = rawEntry.resolvedLineId ? String(rawEntry.resolvedLineId) : '';
      var via = rawEntry.via ? String(rawEntry.via) : (resolvedLineId ? 'auto' : 'none');
      var skipped = !!rawEntry.skipped;
      var status = rawEntry.status || statusFor(via, resolvedLineId, skipped);
      if (status !== 'auto' && status !== 'user-assigned' && status !== 'unknown' && status !== 'skipped') {
        status = statusFor(via, resolvedLineId, skipped);
      }
      var rec = blob.records[normalized] || {};
      rec.originalLabel = rec.originalLabel || original || normalized;
      rec.normalizedLabel = normalized;
      rec.resolvedLineId = resolvedLineId;
      rec.status = status;
      rec.via = via;
      rec.sourceType = 'expense';
      rec.importBatchId = batchId;
      rec.importedAt = importedAt;
      if (filename) rec.sourceFilename = filename;
      rec.dateRange = mergeDateRange(rec.dateRange, rawEntry.dateRange);
      if (status === 'unknown' || status === 'skipped') {
        rec.unknownId = rawEntry.unknownId || rec.unknownId || unknownIdFor(normalized);
        if (!resolvedLineId) rec.resolvedLineId = '';
      } else {
        rec.unknownId = rawEntry.unknownId || '';
      }
      blob.records[normalized] = rec;
    });
    writeBlob(blob);
    return blob;
  }

  function clearLocal() {
    try {
      if (global.localStorage) global.localStorage.removeItem(LEGACY_ALIAS_KEY);
    } catch (_e) {}
    return writeBlob(emptyBlob());
  }

  try {
    if (typeof document !== 'undefined' && document.addEventListener) {
      document.addEventListener('kpi:localUserScopeChanged', function (ev) {
        if (ev && ev.detail && ev.detail.cleared) clearLocal();
      });
    }
  } catch (_eScope) {}

  global.KpiExpenseImportMapping = {
    __ready: true,
    STORAGE_KEY: STORAGE_KEY,
    LEGACY_ALIAS_KEY: LEGACY_ALIAS_KEY,
    SCHEMA_VERSION: SCHEMA_VERSION,
    emptyBlob: emptyBlob,
    normText: normText,
    readBlob: readBlob,
    writeBlob: writeBlob,
    loadAliases: loadAliases,
    saveAliases: saveAliases,
    nextImportBatchId: nextImportBatchId,
    classifyVia: classifyVia,
    statusFor: statusFor,
    upsertEntries: upsertEntries,
    clearLocal: clearLocal,
  };
})(typeof window !== 'undefined' ? window : this);
