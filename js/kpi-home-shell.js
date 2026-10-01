/* Home shell date + expand. Shared cursor is annualNav.selectedIso.
   Does not create a date store. operatingYear is not read. */
(function () {
  'use strict';

  var HOLD_DELAY = 400;
  var HOLD_INTERVAL = 75;
  var root = document.querySelector('.home-windows');
  if (!root) return;

  var lang = (document.documentElement.lang || 'ja').toLowerCase();
  var windows = Array.prototype.slice.call(root.querySelectorAll('[data-home-window]'));

  function padIso(d) {
    function p(n) { return n < 10 ? '0' + n : String(n); }
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
  }
  function parseIso(iso) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(String(iso || ''))) return null;
    var parts = String(iso).split('-');
    var y = Number(parts[0]);
    var m = Number(parts[1]);
    var day = Number(parts[2]);
    var dt = new Date(y, m - 1, day);
    if (dt.getFullYear() !== y || dt.getMonth() !== m - 1 || dt.getDate() !== day) return null;
    return dt;
  }
  function shiftIso(iso, delta) {
    var d = parseIso(iso);
    if (!d) return iso;
    d.setDate(d.getDate() + delta);
    return padIso(d);
  }
  function todayIso() {
    return padIso(new Date());
  }
  function formatIso(iso) {
    var d = parseIso(iso);
    if (!d) return '—';
    var text = d.getFullYear() + '/' + (d.getMonth() + 1) + '/' + d.getDate();
    if (lang === 'en') {
      return text + ' ' + ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][d.getDay()];
    }
    if (lang.indexOf('zh') === 0) {
      return text + ' 週' + ['日', '一', '二', '三', '四', '五', '六'][d.getDay()];
    }
    return text + '(' + ['日', '月', '火', '水', '木', '金', '土'][d.getDay()] + ')';
  }
  function readStoredIso() {
    try {
      var gw = window.__KPI_DATA_GATEWAY;
      var nav = gw && typeof gw.getJson === 'function' ? gw.getJson('kpiNavigator.annualNav') : null;
      if (nav && parseIso(nav.selectedIso)) return nav.selectedIso;
    } catch (_e) {}
    try {
      var raw = JSON.parse(localStorage.getItem('kpiNavigator.annualNav') || 'null');
      if (raw && parseIso(raw.selectedIso)) return raw.selectedIso;
    } catch (_e2) {}
    return '';
  }
  function writeShared(iso, source) {
    if (!parseIso(iso)) return;
    var year = Number(String(iso).slice(0, 4));
    window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
    window.__ANNUAL_DATA.calendarYear = year;
    window.__ANNUAL_DATA.daily = window.__ANNUAL_DATA.daily || {};
    window.__ANNUAL_DATA.daily.selectedDate = iso;
    var nav = { calendarYear: year, selectedIso: iso };
    try {
      var gw = window.__KPI_DATA_GATEWAY;
      if (gw && typeof gw.setJson === 'function') gw.setJson('kpiNavigator.annualNav', nav);
      else localStorage.setItem('kpiNavigator.annualNav', JSON.stringify(nav));
    } catch (_e) {}
    try {
      document.dispatchEvent(new CustomEvent('annual:dailyDateChanged', {
        detail: { isoDate: iso, source: source || 'home-shell' }
      }));
    } catch (_e2) {}
  }
  function initialIso() {
    var shared = window.__KPI_SHARED_DATE;
    var boot = shared && typeof shared.bootCockpitIso === 'function' ? shared.bootCockpitIso() : null;
    if (boot && boot.iso && parseIso(boot.iso)) return boot.iso;
    var stored = readStoredIso();
    if (stored) return stored;
    if (shared && typeof shared.openingIso === 'function') return shared.openingIso(new Date());
    var y = new Date();
    y.setDate(y.getDate() - 1);
    return padIso(y);
  }

  var currentIso = initialIso();

  function paint() {
    var label = formatIso(currentIso);
    var isToday = currentIso === todayIso();
    var d = parseIso(currentIso);
    var year = d ? String(d.getFullYear()) : '';
    var month = d ? String(d.getMonth() + 1) : '';
    windows.forEach(function (win) {
      win.querySelectorAll('[data-home-date-label]').forEach(function (el) {
        el.textContent = label;
      });
      win.querySelectorAll('[data-home-date-input]').forEach(function (el) {
        el.value = currentIso;
      });
      win.querySelectorAll('[data-home-today]').forEach(function (el) {
        el.hidden = isToday;
      });
      var detail = win.querySelector('[data-home-detail]');
      if (!detail) return;
      var kind = win.getAttribute('data-home-window');
      var q = 'year=' + encodeURIComponent(year) + '&month=' + encodeURIComponent(month) + '&iso=' + encodeURIComponent(currentIso);
      detail.setAttribute('data-home-handoff', q);
      /* Daily destination is not chosen. H4-C picks the page. Keep the iso handoff only. */
      if (kind === 'daily') {
        detail.setAttribute('data-home-detail-status', 'provisional');
        detail.setAttribute('href', '#');
        return;
      }
      var base = detail.getAttribute('data-home-href') || '';
      var path = base.split('?')[0];
      detail.setAttribute('href', path + '?' + q);
    });
  }
  function commit(iso) {
    if (!parseIso(iso) || iso === currentIso) {
      paint();
      return;
    }
    currentIso = iso;
    paint();
    writeShared(iso, 'home-shell');
  }

  function bindHold(btn, delta) {
    if (!btn) return;
    var delayId = null;
    var repeatId = null;
    function clearHold() {
      if (delayId != null) { clearTimeout(delayId); delayId = null; }
      if (repeatId != null) { clearInterval(repeatId); repeatId = null; }
    }
    function step() {
      commit(shiftIso(currentIso, delta));
    }
    btn.addEventListener('pointerdown', function (ev) {
      if (ev.pointerType === 'mouse' && ev.button !== 0) return;
      ev.preventDefault();
      clearHold();
      step();
      delayId = setTimeout(function () {
        repeatId = setInterval(step, HOLD_INTERVAL);
      }, HOLD_DELAY);
    });
    btn.addEventListener('pointerup', clearHold);
    btn.addEventListener('pointercancel', clearHold);
    btn.addEventListener('lostpointercapture', clearHold);
    btn.addEventListener('keydown', function (ev) {
      if (ev.key !== 'Enter' && ev.key !== ' ') return;
      ev.preventDefault();
      step();
    });
  }

  windows.forEach(function (win) {
    bindHold(win.querySelector('[data-home-prev]'), -1);
    bindHold(win.querySelector('[data-home-next]'), 1);
    var todayBtn = win.querySelector('[data-home-today]');
    if (todayBtn) todayBtn.addEventListener('click', function () { commit(todayIso()); });
    var dateBtn = win.querySelector('[data-home-date-label]');
    var dateInput = win.querySelector('[data-home-date-input]');
    if (dateBtn && dateInput) {
      dateBtn.addEventListener('click', function () {
        if (typeof dateInput.showPicker === 'function') {
          try { dateInput.showPicker(); } catch (_e) { dateInput.focus(); }
        } else dateInput.focus();
      });
      dateInput.addEventListener('change', function () {
        if (!dateInput.value) return;
        commit(dateInput.value);
      });
    }
    var detailLink = win.querySelector('[data-home-detail]');
    if (detailLink) {
      detailLink.addEventListener('click', function (ev) {
        if (detailLink.getAttribute('data-home-detail-status') === 'provisional') ev.preventDefault();
      });
    }
    var expandBtn = win.querySelector('[data-home-expand]');
    var expanded = win.querySelector('[data-home-expanded]');
    if (expandBtn && expanded) {
      expandBtn.setAttribute('aria-expanded', 'false');
      expandBtn.addEventListener('click', function () {
        var open = expandBtn.getAttribute('aria-expanded') === 'true';
        var next = !open;
        expandBtn.setAttribute('aria-expanded', next ? 'true' : 'false');
        expanded.hidden = !next;
        win.classList.toggle('is-expanded', next);
        var label = next ? expandBtn.getAttribute('data-label-collapse') : expandBtn.getAttribute('data-label-expand');
        if (label) expandBtn.textContent = label;
      });
    }
  });

  document.addEventListener('annual:dailyDateChanged', function (ev) {
    var iso = ev.detail && ev.detail.isoDate;
    if (!parseIso(iso) || iso === currentIso) return;
    currentIso = iso;
    paint();
  });

  paint();
  if (readStoredIso() !== currentIso) writeShared(currentIso, 'home-initial');

  var body = document.getElementById('body-el');
  var modeBtn = document.getElementById('btn-mode-toggle');
  var modeText = document.getElementById('btn-mode-text');
  var officeLabel = document.getElementById('settings-office-label');
  var MODE_KEY = 'kpi-office-mode';
  function paintMode() {
    if (!body || !modeBtn || !modeText) return;
    var office = body.classList.contains('office-mode');
    var toOffice = modeBtn.getAttribute('data-aria-office') || '';
    var toSci = modeBtn.getAttribute('data-aria-scifi') || '';
    modeBtn.setAttribute('aria-label', office ? toSci : toOffice);
    modeText.textContent = 'OFFICE MODE';
    if (officeLabel) officeLabel.textContent = office ? 'Sci-Fi Mode' : 'Office Mode';
  }
  if (body && sessionStorage.getItem(MODE_KEY) === '1') body.classList.add('office-mode');
  paintMode();
  if (modeBtn && body) {
    modeBtn.addEventListener('click', function (ev) {
      ev.preventDefault();
      var office = !body.classList.contains('office-mode');
      body.classList.toggle('office-mode', office);
      if (office) sessionStorage.setItem(MODE_KEY, '1');
      else sessionStorage.removeItem(MODE_KEY);
      paintMode();
    });
  }
  var officeToggle = document.getElementById('settings-office-toggle');
  if (officeToggle && modeBtn) {
    officeToggle.addEventListener('click', function (ev) {
      ev.preventDefault();
      modeBtn.click();
    });
  }
  var backTop = document.getElementById('footerBackToTop');
  if (backTop) {
    backTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
})();
