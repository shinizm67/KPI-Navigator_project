    /* INSIGHT-STRATEGY-USER-NOTE */
    (function () {
      var HARD = 200;
      var TOOLTIP_MAX = 200;

      function parseIso(iso) {
        var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso || ''));
        if (!m) return null;
        return { y: Number(m[1]), m0: Number(m[2]) - 1 };
      }

      function focusYearMonth() {
        var iso = null;
        if (window.KpiYearStore && typeof KpiYearStore.getSelectedDate === 'function') {
          iso = KpiYearStore.getSelectedDate();
        }
        if (!iso && window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily && window.__ANNUAL_DATA.daily.selectedDate) {
          iso = window.__ANNUAL_DATA.daily.selectedDate;
        }
        var p = parseIso(iso);
        if (p) return p;
        var now = new Date();
        var y = now.getFullYear();
        if (window.KpiYearStore && typeof KpiYearStore.getOperatingYear === 'function') {
          var oy = Number(KpiYearStore.getOperatingYear());
          if (Number.isFinite(oy)) y = oy;
        }
        return { y: y, m0: now.getMonth() };
      }

      function readNote(year, month0) {
        if (!window.KpiYearStore || typeof KpiYearStore.readStrategyUserNote !== 'function') return '';
        return String(KpiYearStore.readStrategyUserNote(year, month0) || '').trim().slice(0, HARD);
      }

      function targets() {
        return Array.prototype.slice.call(
          document.querySelectorAll(
            '#insight-strategy-user-note[data-insight-source="monthly-edit-float"]'
          )
        );
      }

      function applyText(el, text) {
        el.textContent = text;
        if (text) {
          el.setAttribute('title', text.length > TOOLTIP_MAX ? text.slice(0, TOOLTIP_MAX) : text);
        } else {
          el.removeAttribute('title');
        }
      }

      function refresh() {
        var fm = focusYearMonth();
        var text = readNote(fm.y, fm.m0);
        targets().forEach(function (el) {
          applyText(el, text);
        });
      }

      function editHrefForFocus(fm) {
        var path = String(window.location.pathname || '');
        var base;
        if (/\/monthly\/?(?:index\.html)?$/i.test(path) || /\/monthly\/index\.html$/i.test(path)) {
          base = 'edit/index.html';
        } else if (/\/annual\/?(?:index\.html)?$/i.test(path) || /\/annual\/index\.html$/i.test(path)) {
          base = '../monthly/edit/index.html';
        } else {
          base = '../monthly/edit/index.html';
        }
        var q =
          'year=' +
          encodeURIComponent(String(fm.y)) +
          '&month=' +
          encodeURIComponent(String(fm.m0 + 1)) +
          '&openStrategyNote=1';
        var iso = null;
        if (window.KpiYearStore && typeof KpiYearStore.getSelectedDate === 'function') {
          iso = KpiYearStore.getSelectedDate();
        }
        if (iso && /^\d{4}-\d{2}-\d{2}$/.test(String(iso))) {
          var parts = String(iso).split('-');
          if (Number(parts[0]) === fm.y && Number(parts[1]) - 1 === fm.m0) {
            q += '&iso=' + encodeURIComponent(String(iso));
          }
        }
        return base + '?' + q;
      }

      function goToStrategyNoteEdit() {
        var fm = focusYearMonth();
        window.location.href = editHrefForFocus(fm);
      }

      function bindJump(el) {
        if (!el || el.getAttribute('data-insight-strategy-jump') === '1') return;
        el.setAttribute('data-insight-strategy-jump', '1');
        var useJa = String(document.documentElement.getAttribute('lang') || '')
          .toLowerCase()
          .indexOf('ja') === 0;
        var label = useJa
          ? 'Strategy Note を編集（Monthly Edit）'
          : 'Edit Strategy Note (Monthly Edit)';
        var tip = useJa
          ? 'クリックで Monthly Edit の Strategy Note を開きます'
          : 'Click to open Strategy Note in Monthly Edit';
        var box = el.closest('.insight-monthly-strategy-note__box') || el;
        if (box.getAttribute('data-insight-strategy-jump-bound') === '1') return;
        box.setAttribute('data-insight-strategy-jump-bound', '1');
        box.classList.add('insight-monthly-strategy-note__box--jump');
        box.setAttribute('role', 'link');
        box.setAttribute('tabindex', '0');
        box.setAttribute('aria-label', label);
        box.title = tip;
        box.addEventListener('click', function (ev) {
          ev.preventDefault();
          goToStrategyNoteEdit();
        });
        box.addEventListener('keydown', function (ev) {
          if (ev.key !== 'Enter' && ev.key !== ' ') return;
          ev.preventDefault();
          goToStrategyNoteEdit();
        });
      }

      function bindAll() {
        targets().forEach(bindJump);
      }

      refresh();
      bindAll();
      document.addEventListener('kpi:mepDataChanged', refresh);
      document.addEventListener('monthly:editFloatConfirmed', refresh);
      document.addEventListener('kpi:selectedDateChanged', refresh);
      window.addEventListener('storage', function (ev) {
        if (ev.key === 'kpiNavigator.kpiYearStore') refresh();
      });
    })();
