/**
 * Annual Cockpit facts that do not depend on a confirmed annual-target source.
 * Confirmed targets stay limited to source "sales-data-save" with a positive target.
 * Other stored source strings are left unchanged.
 */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.KpiCockpitFacts = api;
})(typeof window !== 'undefined' ? window : this, function () {
  var USER_SAVED_SOURCE = 'sales-data-save';

  function pad2(n) {
    return (n < 10 ? '0' : '') + n;
  }

  function finiteYear(value) {
    if (value == null || value === '') return null;
    var year = Number(value);
    return Number.isFinite(year) ? year : null;
  }

  function cockpitPlanConfirmed(plan) {
    if (!plan || typeof plan !== 'object') return false;
    if (plan.source !== USER_SAVED_SOURCE) return false;
    var target = Number(plan.targetSales);
    return Number.isFinite(target) && target > 0;
  }

  /**
   * A named source is stored as given. An omitted source sets kpi-year-store.
   * existingSource is not copied forward, so an unnamed write cannot keep sales-data-save.
   */
  function targetSourceOnSave(existingSource, meta) {
    if (meta && typeof meta.source === 'string' && meta.source) return meta.source;
    return 'kpi-year-store';
  }

  /**
   * The year being edited wins. The calendar year is the next choice.
   * The operating year is only a last resort when neither is a year.
   */
  function resolveTargetSaveYear(editYear, calendarYear, operatingYear) {
    var edit = finiteYear(editYear);
    if (edit != null) return edit;
    var calendar = finiteYear(calendarYear);
    if (calendar != null) return calendar;
    return finiteYear(operatingYear);
  }

  function explicitOpenDays(year, businessDays) {
    var monthly = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
    var y = finiteYear(year);
    if (y == null || !businessDays || typeof businessDays !== 'object') {
      return { explicit: 0, total: null, monthly: monthly };
    }
    var explicit = 0;
    var total = 0;
    for (var m = 0; m < 12; m++) {
      var dc = new Date(y, m + 1, 0).getDate();
      for (var day = 1; day <= dc; day++) {
        var iso = y + '-' + pad2(m + 1) + '-' + pad2(day);
        if (!Object.prototype.hasOwnProperty.call(businessDays, iso)) continue;
        if (typeof businessDays[iso] !== 'boolean') continue;
        explicit += 1;
        if (businessDays[iso] === true) {
          total += 1;
          monthly[m] += 1;
        }
      }
    }
    if (!explicit) return { explicit: 0, total: null, monthly: monthly };
    return { explicit: explicit, total: total, monthly: monthly };
  }

  /**
   * Cockpit open days follow Sales Data: explicit false is closed,
   * explicit true and a missing flag are open. Sales amount is not consulted.
   * This does not write flags or decide a confirmed plan.
   */
  function displayOpenDays(year, businessDays) {
    var monthly = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
    var y = finiteYear(year);
    if (y == null) return { explicit: 0, total: null, monthly: monthly };
    var map = businessDays && typeof businessDays === 'object' ? businessDays : {};
    var explicit = 0;
    var total = 0;
    for (var m = 0; m < 12; m++) {
      var dc = new Date(y, m + 1, 0).getDate();
      for (var day = 1; day <= dc; day++) {
        var iso = y + '-' + pad2(m + 1) + '-' + pad2(day);
        var has = Object.prototype.hasOwnProperty.call(map, iso);
        if (has && typeof map[iso] === 'boolean') explicit += 1;
        var flag = has ? !!map[iso] : null;
        if (flag === false) continue;
        total += 1;
        monthly[m] += 1;
      }
    }
    return { explicit: explicit, total: total, monthly: monthly };
  }

  function recordedSalesByMonth(year, salesMap) {
    var months = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
    var present = [false, false, false, false, false, false, false, false, false, false, false, false];
    var y = finiteYear(year);
    if (y == null || !salesMap || typeof salesMap !== 'object') {
      return { any: false, months: months, present: present };
    }
    var any = false;
    for (var m = 0; m < 12; m++) {
      var dc = new Date(y, m + 1, 0).getDate();
      for (var day = 1; day <= dc; day++) {
        var iso = y + '-' + pad2(m + 1) + '-' + pad2(day);
        if (!Object.prototype.hasOwnProperty.call(salesMap, iso)) continue;
        var amount = Number(salesMap[iso]);
        if (!Number.isFinite(amount)) continue;
        present[m] = true;
        any = true;
        months[m] += amount;
      }
    }
    return { any: any, months: months, present: present };
  }

  function recordedSalesThrough(year, throughIso, salesMap) {
    var y = finiteYear(year);
    if (y == null || !salesMap || typeof salesMap !== 'object') {
      return { any: false, mtd: null, ytd: null };
    }
    var through = String(throughIso || '');
    var monthPrefix = through.slice(0, 7);
    var mtd = 0;
    var ytd = 0;
    var any = false;
    for (var m = 0; m < 12; m++) {
      var dc = new Date(y, m + 1, 0).getDate();
      for (var day = 1; day <= dc; day++) {
        var iso = y + '-' + pad2(m + 1) + '-' + pad2(day);
        if (through && iso > through) continue;
        if (!Object.prototype.hasOwnProperty.call(salesMap, iso)) continue;
        var amount = Number(salesMap[iso]);
        if (!Number.isFinite(amount)) continue;
        any = true;
        ytd += amount;
        if (iso.slice(0, 7) === monthPrefix) mtd += amount;
      }
    }
    if (!any) return { any: false, mtd: null, ytd: null };
    return { any: true, mtd: mtd, ytd: ytd };
  }

  /**
   * Same-account tabs may save. A stale tab, a missing page user,
   * or a page user that does not own the hydrated store may not.
   */
  function allowStorePut(pageUserId, boundUserId, stale) {
    if (stale) return false;
    if (!pageUserId) return false;
    if (boundUserId && String(pageUserId) !== String(boundUserId)) return false;
    return true;
  }

  return {
    USER_SAVED_SOURCE: USER_SAVED_SOURCE,
    cockpitPlanConfirmed: cockpitPlanConfirmed,
    targetSourceOnSave: targetSourceOnSave,
    resolveTargetSaveYear: resolveTargetSaveYear,
    explicitOpenDays: explicitOpenDays,
    displayOpenDays: displayOpenDays,
    recordedSalesByMonth: recordedSalesByMonth,
    recordedSalesThrough: recordedSalesThrough,
    allowStorePut: allowStorePut,
  };
});
