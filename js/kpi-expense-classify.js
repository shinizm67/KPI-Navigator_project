/**
 * C2-L4 — Launch-safe expense classification.
 *
 * Reclass custom lines only. Preset/default buckets stay frozen (BT reconcile
 * copies def.bucket). lineId never changes. Amount storage is not touched by
 * bucket moves. No daily↔monthly conversion engine — setLineInputStyle cleanup
 * is not used here.
 *
 * Unknown hold -> classified custom: copy amounts to a new catalog line, update
 * mapping/alias, mark hold resolved (do not delete rows).
 */
(function (global) {
  'use strict';

  if (global.KpiExpenseClassify && global.KpiExpenseClassify.__ready) {
    return;
  }

  var STORE_KEY = 'kpiNavigator.kpiYearStore';
  var PL_EXP_PREFIX = 'kpi-pl-expenses-v1:';
  var ISO_DAY = /^\d{4}-\d{2}-\d{2}$/;
  var YEAR_MONTH = /^(\d{4})-(\d{1,2})$/;

  function isCustomLineId(lineId) {
    return String(lineId || '').indexOf('exp_custom_') === 0;
  }

  function isRealGateway(g) {
    return !!(g && g.__kpiStoreSyncReady && typeof g.setJson === 'function' && typeof g.getJson === 'function');
  }

  function readJson(key) {
    var g = global.__KPI_DATA_GATEWAY;
    if (isRealGateway(g)) {
      try {
        var via = g.getJson(key);
        if (via != null && typeof via === 'object') return via;
      } catch (_eGw) {}
    }
    try {
      var raw = global.localStorage && global.localStorage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (_e) {
      return null;
    }
  }

  function writeJson(key, val) {
    var g = global.__KPI_DATA_GATEWAY;
    if (isRealGateway(g)) {
      try {
        g.setJson(key, val);
        return true;
      } catch (_eGw) {}
    }
    try {
      if (global.localStorage) global.localStorage.setItem(key, JSON.stringify(val));
      return true;
    } catch (_e) {
      return false;
    }
  }

  function roundAmount(v) {
    var n = Number(v);
    return Number.isFinite(n) ? Math.round(n) : 0;
  }

  function rowsHaveDaily(rows) {
    var list = Array.isArray(rows) ? rows : [];
    var i;
    for (i = 0; i < list.length; i++) {
      if (list[i] && ISO_DAY.test(String(list[i].period || ''))) return true;
    }
    return false;
  }

  function hasNonzeroDailyExpenses(lineId) {
    var id = String(lineId || '');
    if (!id) return false;
    var store = readJson(STORE_KEY);
    var years = store && store.years && typeof store.years === 'object' ? store.years : {};
    var yk;
    for (yk in years) {
      if (!Object.prototype.hasOwnProperty.call(years, yk)) continue;
      var rec = years[yk];
      if (!rec || typeof rec !== 'object') continue;
      var de = rec.dailyExpenses;
      if (!de || typeof de !== 'object') continue;
      var map = de[id];
      if (!map || typeof map !== 'object') continue;
      var iso;
      for (iso in map) {
        if (!Object.prototype.hasOwnProperty.call(map, iso)) continue;
        var n = Number(map[iso]);
        if (Number.isFinite(n) && n !== 0) return true;
      }
    }
    return false;
  }

  function canSetLineBucket(line, nextBucket, opts) {
    if (!line) return { ok: false, reason: 'missing' };
    if (line.active === false) return { ok: false, reason: 'inactive' };
    if (line.presetOrphan) return { ok: false, reason: 'orphan' };
    if (!isCustomLineId(line.lineId) || line.isDefault === true) {
      return { ok: false, reason: 'not_custom' };
    }
    if (nextBucket !== 'fixed' && nextBucket !== 'variable') {
      return { ok: false, reason: 'invalid_bucket' };
    }
    if (line.bucket === nextBucket) return { ok: true, noop: true };
    var style = line.resolvedInputStyle || line.inputStyle || 'monthly';
    if (nextBucket === 'fixed' && style === 'daily') {
      if (opts && opts.hasNonzeroDaily) return { ok: false, reason: 'daily_data' };
    }
    return { ok: true };
  }

  function activeInBucket(lines, bucket) {
    return (lines || [])
      .filter(function (line) {
        return line && line.active !== false && line.bucket === bucket;
      })
      .sort(function (a, b) {
        return (Number(a.sortOrder) || 0) - (Number(b.sortOrder) || 0);
      });
  }

  function reindexActiveBucket(lines, bucket) {
    activeInBucket(lines, bucket).forEach(function (line, idx) {
      line.sortOrder = idx;
    });
  }

  function applySetLineBucket(lines, lineId, nextBucket, opts) {
    var list = Array.isArray(lines) ? lines : [];
    var line = list.find(function (l) {
      return l && String(l.lineId) === String(lineId);
    });
    var gate = canSetLineBucket(line, nextBucket, opts || {});
    if (!gate.ok) {
      return { ok: false, reason: gate.reason, lines: list, lineId: lineId };
    }
    if (gate.noop) {
      return {
        ok: true,
        changed: false,
        lineId: String(lineId),
        bucket: line.bucket,
        lines: list,
      };
    }
    var oldBucket = line.bucket;
    line.bucket = nextBucket;
    if (nextBucket === 'fixed') {
      line.inputStyle = 'monthly';
      line.resolvedInputStyle = 'monthly';
    }
    reindexActiveBucket(list, oldBucket);
    var others = activeInBucket(list, nextBucket).filter(function (l) {
      return String(l.lineId) !== String(lineId);
    });
    var maxOrder = -1;
    others.forEach(function (l) {
      var n = Number(l.sortOrder);
      if (Number.isFinite(n) && n > maxOrder) maxOrder = n;
    });
    line.sortOrder = maxOrder + 1;
    return {
      ok: true,
      changed: true,
      lineId: String(line.lineId),
      oldBucket: oldBucket,
      newBucket: nextBucket,
      lines: list,
    };
  }

  function addMonthlyAmount(lineId, year, month0, amt) {
    var key = PL_EXP_PREFIX + year;
    var map = readJson(key);
    if (!map || typeof map !== 'object' || Array.isArray(map)) map = {};
    var k = lineId + ':' + month0;
    map[k] = roundAmount((Number(map[k]) || 0) + amt);
    writeJson(key, map);
  }

  function addDailyAmount(lineId, iso, amt) {
    var year = Number(String(iso).slice(0, 4));
    var store = readJson(STORE_KEY);
    if (!store || typeof store !== 'object') store = { years: {} };
    if (!store.years || typeof store.years !== 'object') store.years = {};
    var rec = store.years[year] || store.years[String(year)] || {};
    if (!rec.dailyExpenses || typeof rec.dailyExpenses !== 'object') rec.dailyExpenses = {};
    if (!rec.dailyExpenses[lineId] || typeof rec.dailyExpenses[lineId] !== 'object') {
      rec.dailyExpenses[lineId] = {};
    }
    var cur = rec.dailyExpenses[lineId][iso];
    rec.dailyExpenses[lineId][iso] = roundAmount((Number(cur) || 0) + amt);
    store.years[year] = rec;
    writeJson(STORE_KEY, store);
  }

  function copyHoldAmountsToLine(lineId, rows) {
    var id = String(lineId || '');
    if (!id) return;
    (Array.isArray(rows) ? rows : []).forEach(function (row) {
      if (!row) return;
      var period = String(row.period == null ? '' : row.period);
      var amt = roundAmount(row.amount);
      if (!period) return;
      if (ISO_DAY.test(period)) {
        addDailyAmount(id, period, amt);
        return;
      }
      var m = period.match(YEAR_MONTH);
      if (m) addMonthlyAmount(id, Number(m[1]), Number(m[2]) - 1, amt);
    });
  }

  function decideUnknownClassify(rec, bucket) {
    if (!rec || rec.status === 'resolved') return { ok: false, reason: 'missing_or_resolved' };
    if (bucket !== 'fixed' && bucket !== 'variable') return { ok: false, reason: 'invalid_bucket' };
    if (rowsHaveDaily(rec.rows) && bucket !== 'variable') {
      return { ok: false, reason: 'daily_requires_variable' };
    }
    return {
      ok: true,
      bucket: bucket,
      inputStyle: rowsHaveDaily(rec.rows) ? 'daily' : 'monthly',
      originalLabel: rec.originalLabel || rec.normalizedLabel || '',
    };
  }

  function assignUserMapping(rec, lineId) {
    var mapApi = global.KpiExpenseImportMapping;
    if (!mapApi || typeof mapApi.upsertEntries !== 'function') return;
    mapApi.upsertEntries(
      [
        {
          originalLabel: rec.originalLabel || rec.normalizedLabel || '',
          normalizedLabel: rec.normalizedLabel,
          resolvedLineId: String(lineId),
          status: 'user-assigned',
          via: 'user-assigned',
          unknownId: rec.unknownId,
        },
      ],
      { importedAt: Date.now() }
    );
    if (typeof mapApi.loadAliases === 'function' && typeof mapApi.saveAliases === 'function') {
      var aliases = mapApi.loadAliases() || {};
      aliases[rec.normalizedLabel] = String(lineId);
      mapApi.saveAliases(aliases);
    }
  }

  function classifyUnknownHold(unknownId, bucket, createLineFn) {
    var hold = global.KpiExpenseUnknownHold;
    if (!hold || typeof hold.readBlob !== 'function') {
      return { ok: false, reason: 'hold_missing' };
    }
    var blob = hold.readBlob() || { records: {} };
    var rec = blob.records && blob.records[String(unknownId || '')];
    var decision = decideUnknownClassify(rec, bucket);
    if (!decision.ok) return decision;
    if (typeof createLineFn !== 'function') return { ok: false, reason: 'create_failed' };
    var lineId = createLineFn(
      decision.originalLabel,
      decision.originalLabel,
      decision.bucket,
      decision.inputStyle
    );
    if (!lineId) return { ok: false, reason: 'create_failed' };
    copyHoldAmountsToLine(lineId, rec.rows);
    assignUserMapping(rec, lineId);
    if (typeof hold.markResolved === 'function') hold.markResolved(unknownId, lineId);
    return {
      ok: true,
      lineId: String(lineId),
      originalLabel: rec.originalLabel,
      holdDeleted: false,
    };
  }

  global.KpiExpenseClassify = {
    __ready: true,
    isCustomLineId: isCustomLineId,
    rowsHaveDaily: rowsHaveDaily,
    hasNonzeroDailyExpenses: hasNonzeroDailyExpenses,
    canSetLineBucket: canSetLineBucket,
    applySetLineBucket: applySetLineBucket,
    copyHoldAmountsToLine: copyHoldAmountsToLine,
    decideUnknownClassify: decideUnknownClassify,
    classifyUnknownHold: classifyUnknownHold,
  };
})(typeof window !== 'undefined' ? window : this);
