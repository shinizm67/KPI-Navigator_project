/**
 * KPN-RG-CAL-02A — pure JPY integer allocation.
 * Does not read or write a store, and does not convert conflict days.
 * Tie-break: larger remainder, then lower month index or earlier ISO date.
 * Conflict membership in N and warning UI belong to CAL-02B.
 */
(function (global) {
  'use strict';

  if (global.KpiAllocation && global.KpiAllocation.__ready) return;

  var MODES = {
    fixed: 'fixed-weekday',
    irregular: 'irregular',
    always: 'always-open',
  };
  var OPEN_STATUSES = {
    'explicit-open': true,
    'actual-open': true,
    'provisional-open': true,
  };
  var CLOSED_STATUSES = {
    'explicit-closed': true,
    'provisional-closed': true,
  };

  function fail(reason) {
    return { ok: false, reason: reason };
  }

  function isSafeInt(value) {
    return typeof value === 'number' && isFinite(value) && Math.floor(value) === value && Math.abs(value) <= 9007199254740991;
  }

  function currencyError(input) {
    if (!input || input.currency == null || input.currency === '' || input.currency === 'JPY') return null;
    return fail('currency-unapproved');
  }

  function readTarget(value, reason) {
    if (!isSafeInt(value) || value < 0) return fail(reason || 'invalid-target');
    return { ok: true, value: value };
  }

  function readWeightList(list, reason) {
    if (!Array.isArray(list) || !list.length) return fail(reason || 'invalid-weight');
    var out = [];
    var i;
    for (i = 0; i < list.length; i++) {
      if (typeof list[i] !== 'number' || !isFinite(list[i]) || list[i] < 0) return fail(reason || 'invalid-weight');
      out.push(list[i]);
    }
    return { ok: true, weights: out };
  }

  function distribute(total, weights) {
    var parsed = readWeightList(weights, 'invalid-weight');
    if (!parsed.ok) return parsed;
    var target = readTarget(total, 'invalid-target');
    if (!target.ok) return target;
    var i;
    var sumW = 0;
    var integer = true;
    for (i = 0; i < parsed.weights.length; i++) {
      sumW += parsed.weights[i];
      if (!isSafeInt(parsed.weights[i])) integer = false;
    }
    if (!(sumW > 0)) return fail('zero-weight-sum');
    var amounts = integer ? distributeInteger(target.value, parsed.weights, sumW) : distributeFloat(target.value, parsed.weights, sumW);
    var sum = 0;
    for (i = 0; i < amounts.length; i++) sum += amounts[i];
    return { ok: true, amounts: amounts, sum: sum, total: target.value };
  }

  function distributeInteger(total, weights, sumW) {
    var floors = [];
    var rems = [];
    var assigned = 0;
    var i;
    for (i = 0; i < weights.length; i++) {
      var prod = total * weights[i];
      var floor = Math.floor(prod / sumW);
      floors.push(floor);
      rems.push(prod - floor * sumW);
      assigned += floor;
    }
    var order = indexOrder(rems);
    var left = total - assigned;
    for (i = 0; i < left; i++) floors[order[i]] += 1;
    return floors;
  }

  function distributeFloat(total, weights, sumW) {
    var floors = [];
    var fracs = [];
    var assigned = 0;
    var i;
    for (i = 0; i < weights.length; i++) {
      var quota = (total * weights[i]) / sumW;
      var floor = Math.floor(quota);
      var frac = quota - floor;
      if (frac < 1e-9) frac = 0;
      if (1 - frac < 1e-9) {
        floor += 1;
        frac = 0;
      }
      floors.push(floor);
      fracs.push(frac);
      assigned += floor;
    }
    var order = indexOrder(fracs);
    var left = total - assigned;
    for (i = 0; i < left; i++) floors[order[i]] += 1;
    return floors;
  }

  function indexOrder(scores) {
    var order = [];
    var i;
    for (i = 0; i < scores.length; i++) order.push(i);
    order.sort(function (a, b) {
      if (scores[a] !== scores[b]) return scores[b] - scores[a];
      return a - b;
    });
    return order;
  }

  function monthWeights(counts, seasonality) {
    if (!Array.isArray(counts) || counts.length !== 12) return fail('invalid-business-day-counts');
    if (!Array.isArray(seasonality) || seasonality.length !== 12) return fail('invalid-seasonality');
    var weights = [];
    var i;
    for (i = 0; i < 12; i++) {
      if (!isSafeInt(counts[i]) || counts[i] < 0) return fail('invalid-business-day-counts');
      if (typeof seasonality[i] !== 'number' || !isFinite(seasonality[i]) || seasonality[i] < 0) return fail('invalid-seasonality');
      weights.push(counts[i] * seasonality[i]);
    }
    return { ok: true, weights: weights };
  }

  function allocateMonths(input) {
    var src = input || {};
    var currency = currencyError(src);
    if (currency) return currency;
    var target = readTarget(src.annualTarget, 'invalid-target');
    if (!target.ok) return target;
    var built = monthWeights(src.businessDayCounts, src.seasonality);
    if (!built.ok) return built;
    var split = distribute(target.value, built.weights);
    if (!split.ok) return split;
    return {
      ok: true,
      annualTarget: target.value,
      months: split.amounts,
      sum: split.sum,
      conflicts: copyConflicts(src.conflicts),
    };
  }

  function copyConflicts(list) {
    if (!Array.isArray(list)) return [];
    var out = [];
    var i;
    for (i = 0; i < list.length; i++) out.push(list[i]);
    return out;
  }

  function isoText(day) {
    return day && typeof day.iso === 'string' ? day.iso : '';
  }

  function allocateDays(input) {
    var src = input || {};
    var currency = currencyError(src);
    if (currency) return currency;
    var target = readTarget(src.monthTarget, 'invalid-target');
    if (!target.ok) return target;
    if (!Array.isArray(src.days)) return fail('invalid-days');
    var mode = src.mode == null ? 'weights' : src.mode;
    if (mode !== 'average' && mode !== 'weekday' && mode !== 'weights') return fail('invalid-mode');
    var copied = [];
    var seen = {};
    var i;
    for (i = 0; i < src.days.length; i++) {
      var day = src.days[i];
      if (!day || typeof day !== 'object') return fail('invalid-days');
      var iso = isoText(day);
      if (!isoParts(iso)) return fail('invalid-date');
      if (seen[iso]) return fail('duplicate-date');
      seen[iso] = true;
      var weight = mode === 'average' ? 1 : day.weight;
      if (typeof weight !== 'number' || !isFinite(weight) || weight < 0) return fail('invalid-weight');
      copied.push({ iso: iso, weight: weight });
    }
    if (!copied.length) {
      if (target.value === 0) return { ok: true, monthTarget: 0, days: [], sum: 0, conflicts: copyConflicts(src.conflicts) };
      return fail('no-days');
    }
    copied.sort(function (a, b) {
      return a.iso < b.iso ? -1 : a.iso > b.iso ? 1 : 0;
    });
    var weights = [];
    for (i = 0; i < copied.length; i++) weights.push(copied[i].weight);
    var split = distribute(target.value, weights);
    if (!split.ok) return split;
    var days = [];
    for (i = 0; i < copied.length; i++) days.push({ iso: copied[i].iso, amount: split.amounts[i] });
    return {
      ok: true,
      monthTarget: target.value,
      mode: mode,
      days: days,
      sum: split.sum,
      conflicts: copyConflicts(src.conflicts),
    };
  }

  function allocateYear(input) {
    var src = input || {};
    var currency = currencyError(src);
    if (currency) return currency;
    if (src.mode !== 'average' && src.mode !== 'weekday') return fail('invalid-mode');
    var monthly = allocateMonths(src);
    if (!monthly.ok) return monthly;
    if (!Array.isArray(src.daysByMonth) || src.daysByMonth.length !== 12) return fail('invalid-days');
    var monthsOut = [];
    var yearSum = 0;
    var m;
    for (m = 0; m < 12; m++) {
      var list = src.daysByMonth[m];
      if (!Array.isArray(list)) return fail('invalid-days');
      if (list.length !== src.businessDayCounts[m]) return fail('count-mismatch');
      var daily = allocateDays({
        monthTarget: monthly.months[m],
        mode: src.mode,
        days: list,
        currency: 'JPY',
      });
      if (!daily.ok) return daily;
      monthsOut.push(daily);
      yearSum += daily.sum;
    }
    return {
      ok: true,
      annualTarget: monthly.annualTarget,
      mode: src.mode,
      months: monthly.months,
      monthSum: monthly.sum,
      daysByMonth: monthsOut,
      daySum: yearSum,
      conflicts: copyConflicts(src.conflicts),
    };
  }

  function isFiniteNumber(value) {
    return typeof value === 'number' && isFinite(value);
  }

  function normalizeClosedWeekdays(days) {
    if (!Array.isArray(days) || !days.length) return null;
    var seen = {};
    var out = [];
    var i;
    for (i = 0; i < days.length; i++) {
      var n = days[i];
      if (typeof n !== 'number' || n !== Math.floor(n) || n < 0 || n > 6 || seen[n]) continue;
      seen[n] = true;
      out.push(n);
    }
    if (!out.length || out.length !== days.length) return null;
    out.sort(function (a, b) {
      return a - b;
    });
    return out;
  }

  function normalizeRecord(raw) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
    var mode = raw.mode;
    if (mode === MODES.irregular || mode === MODES.always) return { mode: mode };
    if (mode !== MODES.fixed) return null;
    var days = normalizeClosedWeekdays(raw.closedWeekdays);
    if (!days) return null;
    return { mode: MODES.fixed, closedWeekdays: days };
  }

  function own(map, iso) {
    return !!(map && typeof map === 'object' && Object.prototype.hasOwnProperty.call(map, iso));
  }

  function explicitFlag(map, iso) {
    if (!own(map, iso)) return null;
    var value = map[iso];
    if (value === true) return true;
    if (value === false) return false;
    return null;
  }

  function salesValue(map, iso) {
    if (!own(map, iso)) return null;
    var value = map[iso];
    if (typeof value === 'string' && value.trim() !== '' && isFinite(Number(value))) value = Number(value);
    if (!isFiniteNumber(value) || value < 0) return null;
    return value;
  }

  function isoParts(iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso || ''));
    if (!m) return null;
    var y = Number(m[1]);
    var month = Number(m[2]);
    var day = Number(m[3]);
    var dt = new Date(y, month - 1, day);
    if (dt.getFullYear() !== y || dt.getMonth() !== month - 1 || dt.getDate() !== day) return null;
    return { year: y, month: month - 1, day: day, dow: dt.getDay() };
  }

  function provisional(record, dow) {
    if (!record) return { status: 'unset', moldApplied: false };
    if (record.mode === MODES.fixed) {
      var closed = record.closedWeekdays.indexOf(dow) >= 0;
      return { status: closed ? 'provisional-closed' : 'provisional-open', moldApplied: true };
    }
    if (record.mode === MODES.irregular || record.mode === MODES.always) {
      return { status: 'provisional-open', moldApplied: true };
    }
    return { status: 'unset', moldApplied: false };
  }

  function classifyDay(input) {
    var src = input || {};
    var parts = isoParts(src.iso);
    if (!parts) return { status: 'invalid-date', moldApplied: false, salesEntered: false };
    var oy = Number(src.operatingYear);
    if (!isFiniteNumber(oy)) return { status: 'unset', moldApplied: false, salesEntered: false };
    if (parts.year < oy) return { status: 'past', moldApplied: false, salesEntered: salesValue(src.dailySales, src.iso) != null };
    if (parts.year !== oy) return { status: 'other-year', moldApplied: false, salesEntered: salesValue(src.dailySales, src.iso) != null };
    var sales = salesValue(src.dailySales, src.iso);
    var entered = sales != null;
    var flag = explicitFlag(src.businessDays, src.iso);
    if (flag === true) return { status: 'explicit-open', moldApplied: false, salesEntered: entered };
    if (flag === false && entered) return { status: 'conflict', moldApplied: false, salesEntered: true };
    if (flag === false) return { status: 'explicit-closed', moldApplied: false, salesEntered: false };
    if (entered) return { status: 'actual-open', moldApplied: false, salesEntered: true };
    var mold = provisional(normalizeRecord(src.calendar), parts.dow);
    mold.salesEntered = false;
    return mold;
  }

  function daysInMonth(year, monthIndex) {
    return new Date(year, monthIndex + 1, 0).getDate();
  }

  function pad2(n) {
    return n < 10 ? '0' + n : String(n);
  }

  function classifyOperatingYear(input) {
    var src = input || {};
    var year = Number(src.operatingYear);
    if (!isSafeInt(year) || year < 1) return fail('invalid-year');
    var days = [];
    var conflicts = [];
    var m;
    var day;
    for (m = 0; m < 12; m++) {
      var dc = daysInMonth(year, m);
      for (day = 1; day <= dc; day++) {
        var iso = year + '-' + pad2(m + 1) + '-' + pad2(day);
        var found = classifyDay({
          iso: iso,
          operatingYear: year,
          businessDays: src.businessDays,
          dailySales: src.dailySales,
          calendar: src.calendar,
        });
        days.push({
          iso: iso,
          status: found.status,
          moldApplied: found.moldApplied,
          salesEntered: found.salesEntered,
        });
        if (found.status === 'conflict') conflicts.push(iso);
      }
    }
    return {
      ok: true,
      operatingYear: year,
      days: days,
      conflicts: conflicts,
    };
  }

  function statusGroup(status) {
    if (status === 'conflict') return 'conflict';
    if (OPEN_STATUSES[status]) return 'open';
    if (CLOSED_STATUSES[status]) return 'closed';
    return 'unentered';
  }

  function storeYear(store, year) {
    if (!store || !store.years) return null;
    if (store.years[year]) return store.years[year];
    return store.years[String(year)] || null;
  }

  function operatingCalendar(store, year) {
    if (!store || !store.meta) return null;
    var oy = Number(store.meta.operatingYear);
    if (!isSafeInt(oy) || oy !== Number(year)) return null;
    var rec = storeYear(store, year);
    var plan = rec && rec.plan;
    return normalizeRecord(plan && plan.businessCalendar);
  }

  /**
   * null: no operating-year mold, caller keeps its existing rule.
   * true/false: mold year, conflict and explicit closed are false.
   */
  function planningDay(store, year, iso) {
    var calendar = operatingCalendar(store, year);
    if (!calendar) return null;
    var found = classifyDay({
      iso: iso,
      operatingYear: Number(year),
      calendar: calendar,
      dailySales: store.timeline && store.timeline.dailySales,
      businessDays: store.timeline && store.timeline.businessDays,
    });
    return !!OPEN_STATUSES[found.status];
  }

  function operatingPlan(input) {
    var src = input || {};
    var year = Number(src.year);
    var calendar = operatingCalendar(src.store, year);
    if (!calendar) return { ok: true, legacy: true };
    var target = readTarget(src.annualTarget, 'invalid-target');
    if (!target.ok) return target;
    var classified = classifyOperatingYear({
      operatingYear: year,
      calendar: calendar,
      dailySales: src.store.timeline && src.store.timeline.dailySales,
      businessDays: src.store.timeline && src.store.timeline.businessDays,
    });
    if (!classified.ok) return classified;
    var counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
    var daysByMonth = [[], [], [], [], [], [], [], [], [], [], [], []];
    var i;
    for (i = 0; i < classified.days.length; i++) {
      var row = classified.days[i];
      if (!OPEN_STATUSES[row.status]) continue;
      var parts = isoParts(row.iso);
      counts[parts.month] += 1;
      daysByMonth[parts.month].push({ iso: row.iso, dow: parts.dow });
    }
    var monthly = allocateMonths({
      annualTarget: target.value,
      businessDayCounts: counts,
      seasonality: src.seasonality,
      conflicts: classified.conflicts,
    });
    if (!monthly.ok) return monthly;
    var totalBD = 0;
    for (i = 0; i < 12; i++) totalBD += counts[i];
    return {
      ok: true,
      legacy: false,
      plan: {
        year: year,
        annualTarget: target.value,
        weights: src.seasonality.slice(),
        monthlyBD: counts,
        totalBD: totalBD,
        monthlyTargets: monthly.months,
        allocation: 'hamilton',
        daysByMonth: daysByMonth,
        conflicts: classified.conflicts.slice(),
        provisional: classified.conflicts.length > 0,
      },
    };
  }

  function displayMapFromPlan(plan, month, weightFn) {
    var list = plan && plan.daysByMonth ? plan.daysByMonth[month] : null;
    var target = plan && plan.monthlyTargets ? plan.monthlyTargets[month] : 0;
    if (!list || !list.length || !(target > 0)) return {};
    var days = [];
    var i;
    for (i = 0; i < list.length; i++) {
      var weight = 1;
      if (typeof weightFn === 'function') weight = weightFn(list[i]);
      days.push({ iso: list[i].iso, weight: weight });
    }
    var split = allocateDays({ monthTarget: target, days: days });
    if (!split.ok) return {};
    var map = {};
    for (i = 0; i < split.days.length; i++) {
      map[split.days[i].iso] = {
        value: split.days[i].amount,
        rawValue: split.days[i].amount,
        adjusted: false,
      };
    }
    return map;
  }

  function warningCopy(lang) {
    var key = String(lang || '').toLowerCase();
    if (key.indexOf('zh') === 0) {
      return {
        title: '公休與營業額尚未解決',
        body: '有 {n} 天同時留著公休與營業額。營業額仍計入實績，這幾天先不計入預定營業日。目前目標是暫定值。',
        close: '關閉',
        note: '關閉後仍未解決。',
      };
    }
    if (key.indexOf('en') === 0) {
      return {
        title: 'Unresolved closed day with sales',
        body: '{n} days still have both a closed flag and sales. Sales stay in actuals, and those days are left out of planned business days for now. The targets shown are provisional.',
        close: 'Close',
        note: 'Closing this does not resolve them.',
      };
    }
    return {
      title: '休店と売上の未解決',
      body: '{n}日は休店の指定と売上が同時に残っています。売上は実績として残し、これらの日は予定営業日数から外しています。表示中の目標は暫定です。',
      close: '閉じる',
      note: '閉じても解決したことにはなりません。',
    };
  }

  var warningDismissed = false;

  function pageLang() {
    try {
      return (global.document && global.document.documentElement.getAttribute('lang')) || '';
    } catch (_e) {
      return '';
    }
  }

  function readLiveStore() {
    try {
      if (global.KpiYearStore && typeof global.KpiYearStore.getStore === 'function') {
        var mem = global.KpiYearStore.getStore();
        if (mem && typeof mem === 'object') return mem;
      }
    } catch (_e) {}
    try {
      var raw = global.localStorage && global.localStorage.getItem('kpiNavigator.kpiYearStore');
      return raw ? JSON.parse(raw) : null;
    } catch (_e2) {
      return null;
    }
  }

  function refreshWarning() {
    if (!global.document || warningDismissed) return;
    var store = readLiveStore();
    var year = store && store.meta ? Number(store.meta.operatingYear) : NaN;
    var found = isSafeInt(year)
      ? classifyOperatingYear({
          operatingYear: year,
          calendar: operatingCalendar(store, year) || null,
          dailySales: store.timeline && store.timeline.dailySales,
          businessDays: store.timeline && store.timeline.businessDays,
        })
      : null;
    var conflicts = found && found.ok ? found.conflicts : [];
    var existing = global.document.getElementById('kpi-alloc-warning');
    if (!conflicts.length) {
      if (existing && existing.parentNode) existing.parentNode.removeChild(existing);
      return;
    }
    var copy = warningCopy(pageLang());
    var shown = conflicts.slice(0, 8).join(', ');
    if (conflicts.length > 8) shown += ' +' + (conflicts.length - 8);
    var text = copy.body.replace('{n}', String(conflicts.length)) + ' ' + shown;
    if (!existing) {
      existing = global.document.createElement('div');
      existing.id = 'kpi-alloc-warning';
      existing.setAttribute('role', 'status');
      existing.style.cssText = 'position:sticky;top:0;z-index:100002;margin:0;padding:12px 16px;background:#3a2a12;color:#fff8ea;font:14px/1.5 sans-serif;';
      var title = global.document.createElement('strong');
      title.setAttribute('data-warning-title', '1');
      var body = global.document.createElement('span');
      body.setAttribute('data-warning-body', '1');
      var note = global.document.createElement('span');
      note.setAttribute('data-warning-note', '1');
      var close = global.document.createElement('button');
      close.type = 'button';
      close.style.cssText = 'margin-left:12px;';
      close.addEventListener('click', function () {
        warningDismissed = true;
        if (existing.parentNode) existing.parentNode.removeChild(existing);
      });
      existing.appendChild(title);
      existing.appendChild(global.document.createTextNode(' '));
      existing.appendChild(body);
      existing.appendChild(global.document.createTextNode(' '));
      existing.appendChild(note);
      existing.appendChild(close);
      global.document.body.insertBefore(existing, global.document.body.firstChild);
      existing._close = close;
    }
    existing.querySelector('[data-warning-title]').textContent = copy.title;
    existing.querySelector('[data-warning-body]').textContent = text;
    existing.querySelector('[data-warning-note]').textContent = copy.note;
    existing._close.textContent = copy.close;
  }

  function bootWarning() {
    if (!global.document) return;
    var tries = 0;
    var timer = setInterval(function () {
      tries += 1;
      refreshWarning();
      if (tries >= 8 || warningDismissed) clearInterval(timer);
    }, 500);
    if (global.document.readyState === 'loading') {
      global.document.addEventListener('DOMContentLoaded', refreshWarning);
    } else {
      refreshWarning();
    }
  }

  global.KpiAllocation = {
    __ready: true,
    allocateMonths: allocateMonths,
    allocateDays: allocateDays,
    allocateYear: allocateYear,
    classifyDay: classifyDay,
    classifyOperatingYear: classifyOperatingYear,
    statusGroup: statusGroup,
    planningDay: planningDay,
    operatingPlan: operatingPlan,
    displayMapFromPlan: displayMapFromPlan,
    refreshWarning: refreshWarning,
  };
  bootWarning();
})(typeof window !== 'undefined' ? window : globalThis);
