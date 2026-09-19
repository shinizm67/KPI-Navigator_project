      /* SDM-WEEKDAY-BASELINE */
      (function () {
        var root = document.getElementById('sdm-weekday-baseline');
        if (!root) return;

        var listEl = document.getElementById('sdm-weekday-baseline-list');
        var resetBtn = document.getElementById('sdm-weekday-baseline-reset');
        var statusEl = document.getElementById('sdm-weekday-baseline-status');
        var STORE_KEY = 'kpiNavigator.kpiYearStore';

        function storeReady() {
          return !!(
            window.KpiYearStore &&
            typeof KpiYearStore.readWeekdayBaselineYears === 'function' &&
            typeof KpiYearStore.writeWeekdayBaselineYears === 'function' &&
            typeof KpiYearStore.getDefaultWeekdayBaselineYears === 'function' &&
            typeof KpiYearStore.getOperatingYear === 'function'
          );
        }

        function pageLang() {
          try {
            var lang = String(
              (document.documentElement && document.documentElement.getAttribute('lang')) || ''
            ).toLowerCase();
            if (lang.indexOf('zh') === 0) return 'zh';
            if (lang.indexOf('en') === 0) return 'en';
            return 'ja';
          } catch (_e) {
            return 'ja';
          }
        }

        function t3(ja, en, zh) {
          var lang = pageLang();
          if (lang === 'zh') return zh || en;
          if (lang === 'en') return en;
          return ja;
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

        function listEligibleYears(operatingYear) {
          var oy = Number(operatingYear);
          if (!isFinite(oy)) return [];
          if (
            storeReady() &&
            typeof KpiYearStore.listEligibleWeekdayBaselineYears === 'function'
          ) {
            return KpiYearStore.listEligibleWeekdayBaselineYears(oy).slice();
          }
          var out = [];
          try {
            var gw = window.__KPI_DATA_GATEWAY;
            if (!gw || typeof gw.getJson !== 'function') return out;
            var parsed = gw.getJson(STORE_KEY);
            var sales = (parsed && parsed.timeline && parsed.timeline.dailySales) || {};
            var seen = {};
            Object.keys(sales).forEach(function (iso) {
              var y = Number(String(iso).slice(0, 4));
              if (!isFinite(y) || y >= oy || seen[y]) return;
              if (!(Number(sales[iso]) > 0)) return;
              seen[y] = true;
              out.push(y);
            });
          } catch (_e) {}
          return out.sort(function (a, b) {
            return a - b;
          });
        }

        function yearHasData(year) {
          return listEligibleYears(getOperatingYear()).indexOf(Number(year)) >= 0;
        }

        /* All prior years from oy-1 down to oldest eligible/selected (gaps = データなし).
           No fixed year-count cap — long-term accumulation. */
        function listDisplayYears(operatingYear) {
          var oy = Number(operatingYear);
          if (!isFinite(oy)) return [];
          var eligible = listEligibleYears(oy);
          var selected = readSelectedYears(oy);
          var minY = oy - 1;
          eligible.concat(selected).forEach(function (y) {
            var n = Number(y);
            if (isFinite(n) && n < oy && n < minY) minY = n;
          });
          var out = [];
          for (var y = oy - 1; y >= minY; y--) {
            out.push(y);
          }
          return out;
        }

        function readSelectedYears(operatingYear) {
          if (!storeReady()) return [];
          return KpiYearStore.readWeekdayBaselineYears(operatingYear).slice();
        }

        function anomalyYearsSet(operatingYear) {
          var set = {};
          if (
            !storeReady() ||
            typeof KpiYearStore.assessSeasonalityAnomalies !== 'function'
          ) {
            return set;
          }
          try {
            var pack = KpiYearStore.assessSeasonalityAnomalies(operatingYear);
            (pack && pack.flaggedYears ? pack.flaggedYears : []).forEach(function (y) {
              set[Number(y)] = true;
            });
          } catch (_e) {}
          return set;
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
          if (!hasData) {
            return t3('データなし', 'No data', '無資料');
          }
          var n = countPositiveTimelineDays(year);
          if (n > 0) {
            return t3(
              '日次 ' + n + ' 日入力済み',
              n + ' daily entries saved',
              '已輸入日次 ' + n + ' 日'
            );
          }
          return t3('入力済み', 'Has data', '已有資料');
        }

        function anomalyTip() {
          return t3(
            '他の選択年度と比べ、月次繁閑パターンの乖離が大きい年度です。',
            'Seasonality pattern diverges sharply from other selected years.',
            '與其他選定年度相比，月次淡旺季型態差異很大。'
          );
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
          var anomalies = anomalyYearsSet(oy);

          listEl.innerHTML = '';
          var years = listDisplayYears(oy);
          years.forEach(function (year) {
            var hasData = yearHasData(year);
            var isAnomaly = !!anomalies[year];
            var row = document.createElement('label');
            row.className =
              'sdm-weekday-baseline__row' +
              (hasData ? '' : ' is-disabled') +
              (isAnomaly ? ' is-anomaly' : '');
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
            if (isAnomaly) {
              var mark = document.createElement('span');
              mark.className = 'sdm-weekday-baseline__anomaly';
              mark.setAttribute('aria-hidden', 'true');
              mark.textContent = '⚠';
              mark.setAttribute('data-kpi-tutorial-tip', '');
              mark.setAttribute('data-tooltip', anomalyTip());
              mark.setAttribute('tabindex', '0');
              row.appendChild(mark);
            }
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
            showStatus(
              t3('1年以上選んでください', 'Select at least one year', '請至少選擇一年')
            );
            return;
          }
          hideStatus();
          if (!writeSelection(next, oy)) {
            render();
            showStatus(t3('保存できませんでした', 'Could not save', '無法儲存'));
          }
        }

        function onResetClick() {
          if (!storeReady()) return;
          var oy = getOperatingYear();
          var defaults = KpiYearStore.getDefaultWeekdayBaselineYears(oy);
          if (!defaults.length) {
            showStatus(
              t3(
                '選択可能な年がありません',
                'No eligible years to select',
                '沒有可選年度'
              )
            );
            return;
          }
          hideStatus();
          if (!writeSelection(defaults, oy)) {
            showStatus(t3('保存できませんでした', 'Could not save', '無法儲存'));
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
        document.addEventListener('kpi:observedChanged', function () {
          render();
        });

        window.__SDM_WEEKDAY_BASELINE = { render: render };
        render();
      })();
