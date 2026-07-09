      /* SDM-WEEKDAY-BASELINE */
      (function () {
        var root = document.getElementById('sdm-weekday-baseline');
        if (!root) return;

        var listEl = document.getElementById('sdm-weekday-baseline-list');
        var resetBtn = document.getElementById('sdm-weekday-baseline-reset');
        var statusEl = document.getElementById('sdm-weekday-baseline-status');
        var STORE_KEY = 'kpiNavigator.kpiYearStore';
        var MAX_LOOKBACK = 5;

        function storeReady() {
          return !!(
            window.KpiYearStore &&
            typeof KpiYearStore.readWeekdayBaselineYears === 'function' &&
            typeof KpiYearStore.writeWeekdayBaselineYears === 'function' &&
            typeof KpiYearStore.getDefaultWeekdayBaselineYears === 'function' &&
            typeof KpiYearStore.getOperatingYear === 'function'
          );
        }

        function isJa() {
          return (
            String(document.documentElement.getAttribute('lang') || '')
              .toLowerCase()
              .indexOf('ja') === 0
          );
        }

        function t(ja, en) {
          return isJa() ? ja : en;
        }

        function getOperatingYear() {
          if (storeReady()) return KpiYearStore.getOperatingYear();
          var d = window.__ANNUAL_DATA;
          if (d && d.calendarYear != null && isFinite(Number(d.calendarYear))) {
            return Number(d.calendarYear);
          }
          return new Date().getFullYear();
        }

        function countPositiveTimelineDays(year) {
          var y = Number(year);
          if (!isFinite(y)) return 0;
          try {
            var gw = window.__KPI_DATA_GATEWAY;
            if (!gw || typeof gw.getJson !== 'function') return 0;
            var parsed = gw.getJson(STORE_KEY);
            if (!parsed || !parsed.timeline || !parsed.timeline.dailySales) return 0;
            var count = 0;
            Object.keys(parsed.timeline.dailySales).forEach(function (iso) {
              if (String(iso).indexOf(String(y) + '-') !== 0) return;
              var n = Number(parsed.timeline.dailySales[iso]);
              if (isFinite(n) && n > 0) count++;
            });
            return count;
          } catch (_e) {
            return 0;
          }
        }

        function yearHasData(year) {
          if (
            storeReady() &&
            typeof KpiYearStore.listEligibleWeekdayBaselineYears === 'function'
          ) {
            var eligible = KpiYearStore.listEligibleWeekdayBaselineYears(getOperatingYear(), MAX_LOOKBACK);
            return eligible.indexOf(Number(year)) >= 0;
          }
          return countPositiveTimelineDays(year) > 0;
        }

        function listDisplayYears(operatingYear) {
          var oy = Number(operatingYear);
          if (!isFinite(oy)) return [];
          var out = [];
          for (var i = 1; i <= MAX_LOOKBACK; i++) {
            out.push(oy - i);
          }
          return out;
        }

        function readSelectedYears(operatingYear) {
          if (!storeReady()) return [];
          return KpiYearStore.readWeekdayBaselineYears(operatingYear).slice();
        }

        function hideStatus() {
          if (!statusEl) return;
          statusEl.textContent = '';
          statusEl.setAttribute('hidden', '');
        }

        function showStatus(msg) {
          if (!statusEl) return;
          statusEl.textContent = msg;
          statusEl.removeAttribute('hidden');
        }

        function hintForYear(year, hasData) {
          if (!hasData) return t('データなし', 'No data');
          var n = countPositiveTimelineDays(year);
          if (n > 0) {
            return t('日次 ' + n + ' 日入力済み', n + ' daily entries saved');
          }
          return t('入力済み', 'Has data');
        }

        function writeSelection(years, operatingYear) {
          if (!storeReady()) return false;
          return KpiYearStore.writeWeekdayBaselineYears(operatingYear, years, {
            source: 'sales-data-analyze',
          });
        }

        function isWeekdayMode() {
          if (!storeReady() || typeof KpiYearStore.readDailyTargetMode !== 'function') {
            return true;
          }
          return KpiYearStore.readDailyTargetMode(getOperatingYear()) === 'weekday-weighted';
        }

        function updateVisibility() {
          if (!root) return;
          if (isWeekdayMode()) root.removeAttribute('hidden');
          else root.setAttribute('hidden', '');
        }

        function render() {
          if (!listEl) return;
          updateVisibility();
          if (!isWeekdayMode()) return;
          hideStatus();
          var oy = getOperatingYear();
          var selected = readSelectedYears(oy);
          var selectedSet = {};
          selected.forEach(function (y) {
            selectedSet[y] = true;
          });

          listEl.innerHTML = '';
          var years = listDisplayYears(oy);
          years.forEach(function (year) {
            var hasData = yearHasData(year);
            var row = document.createElement('label');
            row.className = 'sdm-weekday-baseline__row' + (hasData ? '' : ' is-disabled');
            row.setAttribute('data-wbl-year', String(year));

            var cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.className = 'sdm-weekday-baseline__cb';
            cb.value = String(year);
            cb.checked = !!selectedSet[year];
            cb.disabled = !hasData;
            cb.setAttribute('data-kpi-guard-ignore', '');

            var yearEl = document.createElement('span');
            yearEl.className = 'sdm-weekday-baseline__year';
            yearEl.textContent = String(year);

            var hintEl = document.createElement('span');
            hintEl.className = 'sdm-weekday-baseline__hint';
            hintEl.textContent = hintForYear(year, hasData);

            row.appendChild(cb);
            row.appendChild(yearEl);
            row.appendChild(hintEl);
            listEl.appendChild(row);
          });
        }

        function collectCheckedYears() {
          if (!listEl) return [];
          var out = [];
          listEl.querySelectorAll('.sdm-weekday-baseline__cb:checked').forEach(function (cb) {
            var y = Number(cb.value);
            if (isFinite(y)) out.push(y);
          });
          return out.sort(function (a, b) {
            return a - b;
          });
        }

        function onCheckboxChange(ev) {
          var cb = ev.target;
          if (!cb || !cb.classList || !cb.classList.contains('sdm-weekday-baseline__cb')) return;
          var oy = getOperatingYear();
          var next = collectCheckedYears();
          if (!next.length) {
            cb.checked = true;
            showStatus(t('1年以上選んでください', 'Select at least one year'));
            return;
          }
          hideStatus();
          if (!writeSelection(next, oy)) {
            render();
            showStatus(t('保存できませんでした', 'Could not save'));
          }
        }

        function onResetClick() {
          if (!storeReady()) return;
          var oy = getOperatingYear();
          var defaults = KpiYearStore.getDefaultWeekdayBaselineYears(oy);
          if (!defaults.length) {
            showStatus(t('選択可能な年がありません', 'No eligible years to select'));
            return;
          }
          hideStatus();
          if (!writeSelection(defaults, oy)) {
            showStatus(t('保存できませんでした', 'Could not save'));
          }
          render();
        }

        if (listEl) {
          listEl.addEventListener('change', onCheckboxChange);
        }
        if (resetBtn) {
          resetBtn.addEventListener('click', onResetClick);
        }

        document.addEventListener('kpi:weekdayBaselineChanged', function () {
          render();
        });
        document.addEventListener('kpi:dailyTargetModeChanged', function () {
          render();
        });

        window.__SDM_WEEKDAY_BASELINE = { render: render };
        render();
      })();
