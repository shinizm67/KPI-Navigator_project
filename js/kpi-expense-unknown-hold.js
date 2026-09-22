/**
 * C2-L3-A — Unknown expense hold (catalog-outside).
 *
 * Do not create exp_custom_* / catalog lines. Do not set bucket or inputStyle.
 * Importers call ingest* only. Gateway mirrors STORAGE_KEY as pl.unknownHold.
 *
 * Collision / identity:
 * - Identity key is normalizedLabel (whitespace stripped, lowercased).
 * - unknownId = 'unk_' + fnv1a32(normalizedLabel). Never exp_custom_* / exp_*.
 * - Same normalizedLabel reimport merges into the same unknownId (no extra records).
 * - Different originalLabel, same normalizedLabel: keep the first originalLabel.
 * - Hash collision (different normalizedLabel, same hash): suffix _2, _3, ...
 * - Row overlap uses the existing expense import policy: replace / add / skip.
 *   Default replace. Within one ingest, same period amounts are summed first.
 */
(function (global) {
  'use strict';

  if (global.KpiExpenseUnknownHold && global.KpiExpenseUnknownHold.__ready) {
    return;
  }

  var STORAGE_KEY = 'kpiNavigator.plExpenseUnknownHold';
  var SCHEMA_VERSION = 1;
  var STATUS_UNKNOWN = 'unknown';
  var STATUS_RESOLVED = 'resolved';

  function emptyBlob() {
    return { schemaVersion: SCHEMA_VERSION, records: {} };
  }

  function normText(v) {
    return String(v == null ? '' : v).replace(/\s+/g, '').toLowerCase();
  }

  function roundAmount(v) {
    var n = Number(v);
    return Number.isFinite(n) ? Math.round(n) : 0;
  }

  function fnv1a32Hex(str) {
    var h = 2166136261;
    var s = String(str || '');
    var i;
    for (i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    var hex = (h >>> 0).toString(16);
    while (hex.length < 8) hex = '0' + hex;
    return hex;
  }

  function unknownIdFor(normalizedLabel) {
    return 'unk_' + fnv1a32Hex(normalizedLabel);
  }

  function mergeValue(existingHas, existing, incoming, policy) {
    if (policy === 'add') return roundAmount((Number(existing) || 0) + (Number(incoming) || 0));
    if (policy === 'skip') return existingHas ? existing : roundAmount(incoming);
    return roundAmount(incoming);
  }

  function rowsToMap(rows) {
    var map = {};
    if (!rows) return map;
    if (!Array.isArray(rows) && typeof rows === 'object') {
      Object.keys(rows).forEach(function (period) {
        map[String(period)] = roundAmount(rows[period]);
      });
      return map;
    }
    (rows || []).forEach(function (row) {
      if (!row) return;
      var period = String(row.period == null ? '' : row.period);
      if (!period) return;
      map[period] = (map[period] || 0) + roundAmount(row.amount);
    });
    return map;
  }

  function mapToRows(map) {
    return Object.keys(map)
      .sort()
      .map(function (period) {
        return { period: period, amount: roundAmount(map[period]) };
      });
  }

  function isRealGateway(g) {
    return !!(g && g.__kpiStoreSyncReady && typeof g.setJson === 'function' && typeof g.getJson === 'function');
  }

  function readBlob() {
    var g = global.__KPI_DATA_GATEWAY;
    if (isRealGateway(g)) {
      try {
        var via = g.getJson(STORAGE_KEY);
        if (via && typeof via === 'object' && via.records && typeof via.records === 'object') {
          return via;
        }
      } catch (_eGw) {}
    }
    try {
      var raw = global.localStorage && global.localStorage.getItem(STORAGE_KEY);
      var parsed = raw ? JSON.parse(raw) : null;
      if (parsed && typeof parsed === 'object' && parsed.records && typeof parsed.records === 'object') {
        return parsed;
      }
    } catch (_e) {}
    return emptyBlob();
  }

  function writeBlob(blob) {
    var next = blob && typeof blob === 'object' ? blob : emptyBlob();
    if (!next.records || typeof next.records !== 'object') next.records = {};
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

  function allocateUnknownId(records, normalizedLabel) {
    var base = unknownIdFor(normalizedLabel);
    if (!records[base]) return base;
    if (String(records[base].normalizedLabel || '') === normalizedLabel) return base;
    var n = 2;
    var candidate = base + '_' + n;
    while (records[candidate] && String(records[candidate].normalizedLabel || '') !== normalizedLabel) {
      n += 1;
      candidate = base + '_' + n;
    }
    return candidate;
  }

  function incomingPeriodMap(info) {
    if (!info || typeof info !== 'object') return {};
    if (info.rowsByPeriod && typeof info.rowsByPeriod === 'object') return rowsToMap(info.rowsByPeriod);
    if (info.rows) return rowsToMap(info.rows);
    return {};
  }

  function ingestUnmatched(unmatched, meta) {
    var incoming = unmatched && typeof unmatched === 'object' ? unmatched : {};
    var keys = Object.keys(incoming);
    if (!keys.length) return readBlob();
    var policy = meta && (meta.policy === 'add' || meta.policy === 'skip') ? meta.policy : 'replace';
    var blob = readBlob();
    if (!blob.records || typeof blob.records !== 'object') blob.records = {};
    var importedAt = meta && meta.importedAt != null ? Number(meta.importedAt) : Date.now();
    if (!Number.isFinite(importedAt)) importedAt = Date.now();
    var batchId = meta && meta.importBatchId ? String(meta.importBatchId) : '';
    var filename = meta && meta.sourceFilename ? String(meta.sourceFilename) : '';
    keys.forEach(function (normKey) {
      var info = incoming[normKey] || {};
      var normalizedLabel = normText(normKey) || normText(info.display) || normText(info.originalLabel);
      if (!normalizedLabel) return;
      var periodMap = incomingPeriodMap(info);
      var unknownId = allocateUnknownId(blob.records, normalizedLabel);
      var rec = blob.records[unknownId];
      if (!rec) {
        rec = {
          unknownId: unknownId,
          originalLabel: String(info.display || info.originalLabel || normKey),
          normalizedLabel: normalizedLabel,
          status: STATUS_UNKNOWN,
          rows: [],
        };
        blob.records[unknownId] = rec;
      }
      var existingMap = rowsToMap(rec.rows);
      Object.keys(periodMap).forEach(function (period) {
        var has = Object.prototype.hasOwnProperty.call(existingMap, period);
        existingMap[period] = mergeValue(has, existingMap[period], periodMap[period], policy);
      });
      rec.rows = mapToRows(existingMap);
      rec.status = STATUS_UNKNOWN;
      if (!rec.originalLabel) rec.originalLabel = String(info.display || info.originalLabel || normKey);
      rec.normalizedLabel = normalizedLabel;
      if (batchId) rec.lastImportBatchId = batchId;
      rec.lastImportedAt = importedAt;
      if (filename) rec.sourceFilename = filename;
    });
    writeBlob(blob);
    return blob;
  }

  function ingestRawRows(rows, meta) {
    var unmatched = {};
    (rows || []).forEach(function (row) {
      if (!row) return;
      var original = String(row.originalLabel == null ? '' : row.originalLabel).trim();
      var period = String(row.period == null ? '' : row.period);
      if (!original || !period) return;
      var k = normText(original);
      if (!k) return;
      if (!unmatched[k]) {
        unmatched[k] = { display: original, originalLabel: original, rowsByPeriod: {} };
      }
      unmatched[k].rowsByPeriod[period] =
        (unmatched[k].rowsByPeriod[period] || 0) + roundAmount(row.amount);
    });
    return ingestUnmatched(unmatched, meta);
  }

  function listUnresolved() {
    var blob = readBlob();
    var out = [];
    var records = blob.records || {};
    Object.keys(records).forEach(function (id) {
      var rec = records[id];
      if (!rec) return;
      if (rec.status === STATUS_RESOLVED) return;
      out.push(rec);
    });
    return out;
  }

  function markResolved(unknownId, lineId) {
    var blob = readBlob();
    var rec = blob.records && blob.records[String(unknownId || '')];
    if (!rec) return { ok: false, reason: 'missing' };
    rec.status = STATUS_RESOLVED;
    rec.resolvedLineId = String(lineId || '');
    rec.resolvedAt = Date.now();
    writeBlob(blob);
    return { ok: true, record: rec };
  }

  function clearLocal() {
    return writeBlob(emptyBlob());
  }

  try {
    if (typeof document !== 'undefined' && document.addEventListener) {
      document.addEventListener('kpi:localUserScopeChanged', function (ev) {
        if (ev && ev.detail && ev.detail.cleared) clearLocal();
      });
    }
  } catch (_eScope) {}

  global.KpiExpenseUnknownHold = {
    __ready: true,
    STORAGE_KEY: STORAGE_KEY,
    SCHEMA_VERSION: SCHEMA_VERSION,
    emptyBlob: emptyBlob,
    normText: normText,
    fnv1a32Hex: fnv1a32Hex,
    unknownIdFor: unknownIdFor,
    mergeValue: mergeValue,
    readBlob: readBlob,
    writeBlob: writeBlob,
    ingestUnmatched: ingestUnmatched,
    ingestRawRows: ingestRawRows,
    listUnresolved: listUnresolved,
    markResolved: markResolved,
    clearLocal: clearLocal,
  };
})(typeof window !== 'undefined' ? window : this);
