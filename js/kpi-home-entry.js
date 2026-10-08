/* Home entry. The readiness decision stays in KpiNavigationReadiness.
   Incomplete profile or initial setup leaves Home for the Annual host.
   Ready Basic and Pro stay here. Home does not load KpiYearStore, so the
   snapshot is taken from the same local store Annual already wrote. */
(function () {
  'use strict';

  var windows = document.querySelector('.home-windows');
  if (windows) windows.hidden = true;

  function annualHref(result) {
    var nr = window.KpiNavigationReadiness;
    if (
      result &&
      result.status === 'SETUP_INITIAL_REQUIRED' &&
      nr &&
      typeof nr.annualSetupUrl === 'function'
    ) {
      var setupUrl = nr.annualSetupUrl();
      if (setupUrl) return setupUrl;
    }
    var link = document.querySelector('a.nav-frame-btn[href*="annual/index.html"]');
    return link && link.href ? link.href : '';
  }

  function needsAnnualHost(result) {
    if (!result || result.grandfathered) return false;
    return result.status === 'SETUP_PROFILE_REQUIRED' || result.status === 'SETUP_INITIAL_REQUIRED';
  }

  function readStore() {
    try {
      if (window.KpiYearStore && typeof window.KpiYearStore.getStore === 'function') {
        var mem = window.KpiYearStore.getStore();
        if (mem && typeof mem === 'object') return mem;
      }
    } catch (_e) {}
    try {
      var parsed = JSON.parse(localStorage.getItem('kpiNavigator.kpiYearStore') || 'null');
      if (parsed && typeof parsed === 'object') return parsed;
    } catch (_e2) {}
    return null;
  }

  function profileUrl() {
    try {
      if (window.__KPI_AUTH && typeof window.__KPI_AUTH.resolveAuthBase === 'function') {
        return window.__KPI_AUTH.resolveAuthBase().replace(/\/?$/, '') + '/profile.php';
      }
    } catch (_e) {}
    return '/api/v1/profile.php';
  }

  var decided = false;

  function consider(result) {
    if (decided || !result || result.status === 'PENDING') return;
    decided = true;
    if (needsAnnualHost(result)) {
      var href = annualHref(result);
      if (href) {
        window.location.replace(href);
        return;
      }
    }
    if (windows) windows.hidden = false;
  }

  function run(plan) {
    var nr = window.KpiNavigationReadiness;
    if (!nr || typeof nr.evaluateSnapshot !== 'function') {
      if (windows) windows.hidden = false;
      return;
    }
    var store = readStore();
    if (!store) {
      var pendingHref = annualHref(null);
      if (pendingHref) {
        window.location.replace(pendingHref);
        return;
      }
      if (windows) windows.hidden = false;
      return;
    }
    fetch(profileUrl(), { credentials: 'same-origin', cache: 'no-store' })
      .then(function (res) { return res.json().then(function (body) { return { res: res, body: body }; }); })
      .then(function (pair) {
        if (!pair.res.ok || !pair.body || pair.body.ok !== true) {
          if (windows) windows.hidden = false;
          return;
        }
        var bt = false;
        try {
          bt = !!(
            window.KpiBusinessType &&
            typeof window.KpiBusinessType.isBusinessTypeSet === 'function' &&
            window.KpiBusinessType.isBusinessTypeSet()
          );
        } catch (_e) {}
        consider(nr.evaluateSnapshot({
          storeHydrated: true,
          profileOk: true,
          store: store,
          profile: pair.body.profile || null,
          businessTypeSet: bt,
          plan: plan,
        }));
      })
      .catch(function () {
        if (windows) windows.hidden = false;
      });
  }

  document.addEventListener('kpi:storeHydrateSettled', function (ev) {
    var plan = ev && ev.detail ? ev.detail.plan : null;
    run(plan);
  });
  run(null);
})();
