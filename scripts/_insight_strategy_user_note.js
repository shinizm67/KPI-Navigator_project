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
          document.querySelectorAll('#insight-strategy-user-note[data-insight-source="monthly-edit-float"]')
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

      refresh();
      document.addEventListener('kpi:mepDataChanged', refresh);
      document.addEventListener('monthly:editFloatConfirmed', refresh);
      document.addEventListener('kpi:selectedDateChanged', refresh);
      window.addEventListener('storage', function (ev) {
        if (ev.key === 'kpiNavigator.kpiYearStore') refresh();
      });
    })();
