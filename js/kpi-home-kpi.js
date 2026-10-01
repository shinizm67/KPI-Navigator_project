/* Home collapsed KPIs.
   Prefers store.years[y].dailyFacts, the snapshot KpiYearStore.invalidateDailyFacts
   writes and Daily FW reads through metricsFromDailyFacts / __computeTwMetricsForIso.
   Does not copy HL daily-target allocation. If that snapshot is missing, sales are
   summed from timeline.dailySales with the UI business-day rule and targets stay blank. */
(function () {
  'use strict';

  var DASH = '—';
  var STORE_KEY = 'kpiNavigator.kpiYearStore';
  var remoteFacts = {};
  var remoteLoaded = {};
  var remotePending = {};
  var lastIso = '';

  function readStore() {
    try {
      var gw = window.__KPI_DATA_GATEWAY;
      var store = gw && typeof gw.getJson === 'function' ? gw.getJson(STORE_KEY) : null;
      if (store && typeof store === 'object') return store;
    } catch (_e) {}
    try {
      var raw = JSON.parse(localStorage.getItem(STORE_KEY) || 'null');
      if (raw && typeof raw === 'object') return raw;
    } catch (_e2) {}
    return null;
  }

  function yearOf(iso) {
    return Number(String(iso || '').slice(0, 4));
  }

  function operatingYear(store) {
    var y = store && store.meta ? Number(store.meta.operatingYear) : NaN;
    return Number.isFinite(y) ? y : new Date().getFullYear();
  }

  function yearRec(store, year) {
    if (!store || !store.years) return null;
    return store.years[year] || store.years[String(year)] || null;
  }

  function hasSavedPlan(store, year) {
    var rec = yearRec(store, year);
    if (!rec || !rec.plan) return false;
    if (String(rec.plan.source || '') !== 'sales-data-save') return false;
    var n = Number(rec.plan.targetSales);
    return Number.isFinite(n) && n > 0;
  }

  function isUiBusinessDay(store, iso) {
    var bmap = store && store.timeline ? store.timeline.businessDays : null;
    if (bmap && Object.prototype.hasOwnProperty.call(bmap, iso)) return !!bmap[iso];
    return true;
  }

  function salesAmt(store, iso) {
    var smap = store && store.timeline ? store.timeline.dailySales : null;
    if (!smap || !Object.prototype.hasOwnProperty.call(smap, iso)) return 0;
    var n = Number(smap[iso]);
    if (!Number.isFinite(n)) return 0;
    if (n === 1234) {
      var y = yearOf(iso);
      if (Number.isFinite(y) && y < operatingYear(store)) return n;
      return 0;
    }
    return n;
  }

  function factsFor(store, iso) {
    var rec = yearRec(store, yearOf(iso));
    if (!rec || !rec.dailyFacts) return null;
    return rec.dailyFacts[iso] || null;
  }

  function factsUsable(store, iso, fact) {
    if (!fact) return false;
    var annualTarget = hasSavedPlan(store, yearOf(iso)) ? Number(yearRec(store, yearOf(iso)).plan.targetSales) : 0;
    if (
      annualTarget > 0 &&
      !(Number(fact.dailyTarget) > 0) &&
      !(Number(fact.mtdTarget) > 0) &&
      !(Number(fact.ytdTarget) > 0)
    ) {
      return false;
    }
    return true;
  }

  function numOrNull(v) {
    if (v == null || v === '') return null;
    var n = Number(v);
    return Number.isFinite(n) ? n : null;
  }

  function walkSales(store, iso) {
    var y = yearOf(iso);
    var m0 = Number(String(iso).slice(5, 7)) - 1;
    var mtdA = 0;
    var ytdA = 0;
    var dailySales = 0;
    var open = false;
    if (!Number.isFinite(y) || !Number.isFinite(m0)) return null;
    for (var m = 0; m < 12; m++) {
      var dc = new Date(y, m + 1, 0).getDate();
      for (var day = 1; day <= dc; day++) {
        var dayIso = y + '-' + (m + 1 < 10 ? '0' : '') + (m + 1) + '-' + (day < 10 ? '0' : '') + day;
        if (dayIso > iso) break;
        if (!isUiBusinessDay(store, dayIso)) {
          if (dayIso === iso) open = false;
          continue;
        }
        var amt = salesAmt(store, dayIso);
        ytdA += amt;
        if (m === m0) mtdA += amt;
        if (dayIso === iso) {
          open = true;
          dailySales = amt;
        }
      }
    }
    return {
      isBusinessToday: open,
      hasPlan: false,
      dailySales: dailySales,
      dailyTarget: null,
      mtdA: mtdA,
      mtdT: null,
      ytdA: ytdA,
      ytdT: null
    };
  }

  function rowToFact(row) {
    return {
      sales: row.sales,
      businessDay: !!row.businessDay,
      dailyTarget: row.dailyTarget,
      mtdActual: row.mtdActual,
      mtdTarget: row.mtdTarget,
      ytdActual: row.ytdActual,
      ytdTarget: row.ytdTarget
    };
  }

  function adoptRows(rows) {
    var n = 0;
    (rows || []).forEach(function (row) {
      if (!row || !row.iso) return;
      remoteFacts[row.iso] = rowToFact(row);
      n += 1;
    });
    return n;
  }

  function yearHasRemote(year) {
    var prefix = String(year) + '-';
    var keys = Object.keys(remoteFacts);
    for (var i = 0; i < keys.length; i++) {
      if (keys[i].indexOf(prefix) === 0) return true;
    }
    return false;
  }

  /* POST only when every calendar day is an explicit boolean on timeline.businessDays.
     A missing key is not treated as open or closed, and this does not fill the map.
     Separate from the read-time fallback in isUiBusinessDay. */
  function businessDaysExplicitForYear(store, year) {
    var y = Number(year);
    if (!Number.isFinite(y)) return false;
    var bmap = store && store.timeline ? store.timeline.businessDays : null;
    if (!bmap || typeof bmap !== 'object') return false;
    for (var m = 0; m < 12; m++) {
      var dc = new Date(y, m + 1, 0).getDate();
      var mm = m + 1 < 10 ? '0' + (m + 1) : String(m + 1);
      for (var day = 1; day <= dc; day++) {
        var iso = y + '-' + mm + '-' + (day < 10 ? '0' : '') + day;
        if (typeof bmap[iso] !== 'boolean') return false;
      }
    }
    return true;
  }

  /* Blob persist strips dailyFacts. Read the server snapshot, then the existing
     rebuild endpoint once if that year has a saved plan, a complete explicit
     businessDays map, and no rows yet. */
  function loadRemoteYear(year) {
    if (remoteLoaded[year]) return Promise.resolve();
    if (remotePending[year]) return remotePending[year];
    var sync = window.__KPI_DAILY_FACTS_SYNC;
    if (!sync || typeof sync.hydrateWindow !== 'function') {
      remoteLoaded[year] = true;
      return Promise.resolve();
    }
    remotePending[year] = Promise.resolve()
      .then(function () {
        return sync.hydrateWindow({ force: true, backfill: false, year: year });
      })
      .then(function (data) {
        adoptRows(data && data.rows);
        var storeNow = readStore();
        if (
          yearHasRemote(year) ||
          !hasSavedPlan(storeNow, year) ||
          !businessDaysExplicitForYear(storeNow, year) ||
          typeof sync.rebuildYear !== 'function'
        ) {
          return null;
        }
        return sync.rebuildYear(year).then(function (res) {
          if (!res || res.ok !== true) return null;
          return sync.hydrateWindow({ force: true, backfill: false, year: year });
        }).then(function (data2) {
          adoptRows(data2 && data2.rows);
        });
      })
      .catch(function () {})
      .then(function () {
        remoteLoaded[year] = true;
        delete remotePending[year];
      });
    return remotePending[year];
  }

  function metricsFor(iso) {
    var store = readStore();
    if (!store || !/^\d{4}-\d{2}-\d{2}$/.test(String(iso || ''))) return null;
    var fact = remoteFacts[iso] || factsFor(store, iso);
    if (factsUsable(store, iso, fact)) {
      var openFact = !!fact.businessDay;
      return {
        isBusinessToday: openFact,
        hasPlan: hasSavedPlan(store, yearOf(iso)),
        dailySales: Number(fact.sales) || 0,
        dailyTarget: openFact ? numOrNull(fact.dailyTarget) : null,
        mtdA: Number(fact.mtdActual) || 0,
        mtdT: numOrNull(fact.mtdTarget),
        ytdA: Number(fact.ytdActual) || 0,
        ytdT: numOrNull(fact.ytdTarget)
      };
    }
    return walkSales(store, iso);
  }

  function money(n) {
    if (n == null || !Number.isFinite(Number(n))) return DASH;
    var v = Math.round(Number(n));
    if (window.KpiCurrency && typeof KpiCurrency.format === 'function') {
      return KpiCurrency.format(v, { round: true });
    }
    return String(v);
  }

  function signed(n) {
    if (!Number.isFinite(n)) return DASH;
    if (n === 0) return money(0);
    if (window.KpiCurrency && typeof KpiCurrency.format === 'function') {
      return KpiCurrency.format(n, { round: true, signed: true });
    }
    return (n > 0 ? '+' : '−') + money(Math.abs(n));
  }

  function diff(actual, target) {
    if (!Number.isFinite(actual) || !Number.isFinite(target)) return DASH;
    return signed(actual - target);
  }

  function ach(actual, target) {
    if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) return DASH;
    var pct = (actual / target) * 100;
    if (!Number.isFinite(pct)) return DASH;
    return Math.round(pct) + '%';
  }

  function cellsFor(kind, m) {
    if (!m) return [DASH, DASH, DASH, DASH];
    if (kind === 'daily') {
      if (!m.isBusinessToday) return [DASH, DASH, DASH, DASH];
      if (m.dailyTarget == null) return [money(m.dailySales), DASH, DASH, DASH];
      return [
        money(m.dailySales),
        money(m.dailyTarget),
        diff(m.dailySales, m.dailyTarget),
        ach(m.dailySales, m.dailyTarget)
      ];
    }
    var actual = kind === 'monthly' ? m.mtdA : m.ytdA;
    var target = kind === 'monthly' ? m.mtdT : m.ytdT;
    if (!m.hasPlan || target == null) return [money(actual), DASH, DASH, DASH];
    return [money(actual), money(target), diff(actual, target), ach(actual, target)];
  }

  function pad2(n) {
    return (n < 10 ? '0' : '') + n;
  }

  /* Same rule as KpiYearStore.isPlanningBusinessDay: saved plan, and explicit false is closed. */
  function planningDay(store, iso) {
    return hasSavedPlan(store, yearOf(iso)) && isUiBusinessDay(store, iso);
  }

  function storedFact(store, iso) {
    return remoteFacts[iso] || factsFor(store, iso);
  }

  function yearHasFacts(store, year) {
    if (yearHasRemote(year)) return true;
    var rec = yearRec(store, year);
    return !!(rec && rec.dailyFacts && Object.keys(rec.dailyFacts).length);
  }

  /* Home remaining days start the day after the reference date (dayIso > iso).
     Elapsed business days include the reference date when it is open (dayIso <= iso).
     monthlyFullTarget is the sum of stored dailyTarget. This does not allocate HL / seasonality. */
  function goalFor(iso) {
    var store = readStore();
    var base = metricsFor(iso);
    var out = {
      hasPlan: false,
      facts: false,
      isBusinessToday: false,
      dailySales: null,
      dailyTarget: null,
      finalMonthly: null,
      remainingMonthly: null,
      monthDays: null,
      monthPerDay: null,
      monthElapsed: null,
      monthTotal: null,
      finalAnnual: null,
      remainingAnnual: null,
      yearDays: null,
      yearPerDay: null,
      yearElapsed: null,
      yearTotal: null,
      mtdA: null,
      ytdA: null
    };
    if (!store || !base || !/^\d{4}-\d{2}-\d{2}$/.test(String(iso || ''))) return out;
    out.isBusinessToday = !!base.isBusinessToday;
    out.dailySales = base.isBusinessToday ? base.dailySales : null;
    out.dailyTarget = base.isBusinessToday ? base.dailyTarget : null;
    out.mtdA = base.mtdA;
    out.ytdA = base.ytdA;
    if (!base.hasPlan) return out;
    out.hasPlan = true;
    var y = yearOf(iso);
    var annualTarget = Number(yearRec(store, y).plan.targetSales);
    out.finalAnnual = Number.isFinite(annualTarget) ? annualTarget : null;
    out.remainingAnnual =
      out.finalAnnual != null && Number.isFinite(base.ytdA) ? out.finalAnnual - base.ytdA : null;
    if (!yearHasFacts(store, y)) return out;
    out.facts = true;
    var m0 = Number(String(iso).slice(5, 7)) - 1;
    var monthFull = 0;
    var monthRem = 0;
    var yearRem = 0;
    var monthElapsed = 0;
    var yearElapsed = 0;
    for (var m = 0; m < 12; m++) {
      var dc = new Date(y, m + 1, 0).getDate();
      for (var day = 1; day <= dc; day++) {
        var dayIso = y + '-' + pad2(m + 1) + '-' + pad2(day);
        if (!planningDay(store, dayIso)) continue;
        var fact = storedFact(store, dayIso);
        var tgt = fact ? numOrNull(fact.dailyTarget) : null;
        if (m === m0 && tgt != null) monthFull += tgt;
        if (dayIso > iso) {
          yearRem += 1;
          if (m === m0) monthRem += 1;
        } else {
          yearElapsed += 1;
          if (m === m0) monthElapsed += 1;
        }
      }
    }
    var monthNeed = Number.isFinite(monthFull) && Number.isFinite(base.mtdA) ? monthFull - base.mtdA : null;
    out.finalMonthly = monthFull;
    out.remainingMonthly = monthNeed;
    out.monthDays = monthRem;
    out.monthPerDay =
      monthRem > 0 && monthNeed != null && Number.isFinite(monthNeed) ? monthNeed / monthRem : null;
    out.monthElapsed = monthElapsed;
    out.monthTotal = monthElapsed + monthRem;
    out.yearDays = yearRem;
    out.yearPerDay =
      yearRem > 0 && out.remainingAnnual != null && Number.isFinite(out.remainingAnnual)
        ? out.remainingAnnual / yearRem
        : null;
    out.yearElapsed = yearElapsed;
    out.yearTotal = yearElapsed + yearRem;
    return out;
  }

  function countText(n) {
    if (!Number.isFinite(n)) return DASH;
    return String(Math.round(n));
  }

  function ratioPct(part, whole) {
    if (!Number.isFinite(part) || !Number.isFinite(whole) || whole <= 0) return null;
    var pct = (part / whole) * 100;
    return Number.isFinite(pct) ? pct : null;
  }

  function pctText(pct) {
    if (pct == null || !Number.isFinite(pct)) return DASH;
    return Math.round(pct) + '%';
  }

  /* Daily FW graph marker. Not a Home warning threshold. */
  function markerColor(percent) {
    var p = Number(percent);
    if (!Number.isFinite(p)) return '#E6FF00';
    if (p >= 100) return '#E6FF00';
    if (p >= 90) return '#F9A825';
    if (p >= 80) return '#EF6C00';
    if (p >= 70) return '#E65100';
    if (p >= 60) return '#E53935';
    if (p >= 50) return '#C62828';
    return '#B71C1C';
  }

  /* Candidate B. Raw percentage points, not the rounded label. */
  function paceWarning(bizPct, salesPct) {
    if (bizPct == null || salesPct == null) return 'normal';
    if (!Number.isFinite(bizPct) || !Number.isFinite(salesPct)) return 'normal';
    var sales = salesPct < 0 ? 0 : salesPct;
    if (sales >= bizPct) return 'normal';
    var gap = bizPct - sales;
    if (gap >= 20) return 'red';
    if (gap >= 10) return 'orange';
    return 'normal';
  }

  function setPace(rateEl, pace) {
    var progress = rateEl && rateEl.closest ? rateEl.closest('[data-home-progress]') : null;
    if (!progress) return;
    if (pace === 'orange' || pace === 'red') progress.setAttribute('data-home-pace', pace);
    else progress.removeAttribute('data-home-pace');
  }

  function paintBar(track, rateEl, pct, pace) {
    if (!track || !rateEl) return;
    if (pct == null || !Number.isFinite(pct)) {
      rateEl.textContent = DASH;
      track.style.setProperty('--kpi-x', '66.666%');
      track.style.setProperty('--kgi-x', '0%');
      track.style.setProperty('--fill-w', '0%');
      track.style.setProperty('--marker-color', '#E6FF00');
      setPace(rateEl, 'normal');
      return;
    }
    var kpi = 66.666;
    var maxKgi = 90;
    var kgi = Math.max(0, Math.min(maxKgi, kpi * (Math.max(0, pct) / 100)));
    var marker = markerColor(pct);
    if (pace === 'normal') marker = '#E6FF00';
    else if (pace === 'orange') marker = '#F9A825';
    else if (pace === 'red') marker = '#E53935';
    rateEl.textContent = pctText(pct);
    track.style.setProperty('--kpi-x', kpi + '%');
    track.style.setProperty('--kgi-x', kgi + '%');
    track.style.setProperty('--fill-w', kgi + '%');
    track.style.setProperty('--marker-color', marker);
    setPace(rateEl, pace);
  }

  function paintExpanded(win, kind, goal) {
    var expanded = win.querySelector('[data-home-expanded]');
    if (!expanded) return;
    if (kind === 'monthly' || kind === 'annual') {
      var finalN = kind === 'monthly' ? goal.finalMonthly : goal.finalAnnual;
      var remainN = kind === 'monthly' ? goal.remainingMonthly : goal.remainingAnnual;
      var daysN = kind === 'monthly' ? goal.monthDays : goal.yearDays;
      var perN = kind === 'monthly' ? goal.monthPerDay : goal.yearPerDay;
      var elapsed = kind === 'monthly' ? goal.monthElapsed : goal.yearElapsed;
      var total = kind === 'monthly' ? goal.monthTotal : goal.yearTotal;
      var actual = kind === 'monthly' ? goal.mtdA : goal.ytdA;
      var setGoal = function (key, text) {
        var el = expanded.querySelector('[data-home-goal="' + key + '"]');
        if (el) el.textContent = text;
      };
      var showMoney = goal.hasPlan && (kind === 'annual' || goal.facts);
      setGoal('final', showMoney && finalN != null ? money(finalN) : DASH);
      setGoal('remaining', showMoney && remainN != null ? money(remainN) : DASH);
      setGoal('days', goal.facts && daysN != null ? countText(daysN) : DASH);
      setGoal('perDay', goal.facts && perN != null ? money(perN) : DASH);
      var biz = expanded.querySelector('[data-home-progress="business"]');
      var sales = expanded.querySelector('[data-home-progress="sales"]');
      var bizPct = goal.facts ? ratioPct(elapsed, total) : null;
      var salesPct = showMoney ? ratioPct(actual, finalN) : null;
      paintBar(
        biz && biz.querySelector('[data-home-track]'),
        biz && biz.querySelector('[data-home-rate]'),
        bizPct
      );
      paintBar(
        sales && sales.querySelector('[data-home-track]'),
        sales && sales.querySelector('[data-home-rate]'),
        salesPct,
        paceWarning(bizPct, salesPct)
      );
    }
    if (kind === 'daily') {
      var daily = expanded.querySelector('[data-home-progress="daily"]');
      paintBar(
        daily && daily.querySelector('[data-home-track]'),
        daily && daily.querySelector('[data-home-rate]'),
        goal.isBusinessToday ? ratioPct(goal.dailySales, goal.dailyTarget) : null
      );
    }
  }

  function paint(iso) {
    lastIso = iso;
    var localFact = factsFor(readStore(), iso);
    var store = readStore();
    if (
      iso &&
      !remoteFacts[iso] &&
      !factsUsable(store, iso, localFact) &&
      !remoteLoaded[yearOf(iso)]
    ) {
      loadRemoteYear(yearOf(iso)).then(function () {
        if (lastIso === iso) paint(iso);
      });
    }
    var m = metricsFor(iso);
    var goal = goalFor(iso);
    document.querySelectorAll('[data-home-window]').forEach(function (win) {
      var kind = win.getAttribute('data-home-window');
      var texts = cellsFor(kind, m);
      var nodes = win.querySelectorAll('.home-window__kpi:not(.home-window__goal) .home-window__kpi-value');
      for (var i = 0; i < nodes.length; i++) {
        nodes[i].textContent = texts[i] != null ? texts[i] : DASH;
      }
      paintExpanded(win, kind, goal);
    });
  }

  function paintProgress(kind, bizPct, salesPct) {
    var win = document.querySelector('[data-home-window="' + kind + '"]');
    if (!win || (kind !== 'monthly' && kind !== 'annual')) return 'normal';
    var biz = win.querySelector('[data-home-progress="business"]');
    var sales = win.querySelector('[data-home-progress="sales"]');
    paintBar(
      biz && biz.querySelector('[data-home-track]'),
      biz && biz.querySelector('[data-home-rate]'),
      bizPct
    );
    var level = paceWarning(bizPct, salesPct);
    paintBar(
      sales && sales.querySelector('[data-home-track]'),
      sales && sales.querySelector('[data-home-rate]'),
      salesPct,
      level
    );
    return level;
  }

  window.__KPI_HOME_KPI = {
    paint: paint,
    metrics: metricsFor,
    goal: goalFor,
    pace: paceWarning,
    paintProgress: paintProgress
  };
})();
