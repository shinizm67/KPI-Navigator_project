    /* INSIGHT-WEEKLY-MEMO */
    (function () {
      var MEMO_COLS = ['store', 'area', 'social', 'marketing', 'promo', 'reservation'];
      var WD_EN = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
      var WEATHER_PRESETS = [
        { code: '', ja: '—', en: '—' },
        { code: 'sunny', ja: '晴れ', en: 'Sunny' },
        { code: 'cloudy', ja: '曇り', en: 'Cloudy' },
        { code: 'rain', ja: '雨', en: 'Rain' },
        { code: 'snow', ja: '雪', en: 'Snow' },
        { code: 'thunder', ja: '雷', en: 'Thunder' },
        { code: 'storm', ja: '嵐', en: 'Storm' },
        { code: 'gale', ja: '暴風', en: 'Gale' }
      ];
      var useJa =
        String(document.documentElement.getAttribute('lang') || '')
          .toLowerCase()
          .indexOf('ja') === 0;
      var memoTooltipMax = useJa ? 300 : 500;
      var noneLabel = useJa ? 'なし' : 'None';
      var offSuffix = useJa ? ' OFF' : ' OFF';
      var todayNavLabel = useJa ? '本日' : 'Today';
      var dash = '—';
      var sharedAnchorIso = null;
      var roots = [];

      function pad2(n) {
        return n < 10 ? '0' + n : String(n);
      }

      function isoFromParts(y, m0, d) {
        return y + '-' + pad2(m0 + 1) + '-' + pad2(d);
      }

      function parseIso(iso) {
        var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso || ''));
        if (!m) return null;
        return {
          y: Number(m[1]),
          m0: Number(m[2]) - 1,
          d: Number(m[3])
        };
      }

      function dateFromIso(iso) {
        var p = parseIso(iso);
        if (!p) return null;
        return new Date(p.y, p.m0, p.d);
      }

      function isoFromDate(dt) {
        return isoFromParts(dt.getFullYear(), dt.getMonth(), dt.getDate());
      }

      function addDaysIso(iso, delta) {
        var dt = dateFromIso(iso);
        if (!dt) return iso;
        dt.setDate(dt.getDate() + delta);
        return isoFromDate(dt);
      }

      function operatingYear() {
        if (window.KpiYearStore && typeof KpiYearStore.getOperatingYear === 'function') {
          var oy = Number(KpiYearStore.getOperatingYear());
          if (Number.isFinite(oy)) return oy;
        }
        if (window.__ANNUAL_DATA && Number.isFinite(Number(window.__ANNUAL_DATA.calendarYear))) {
          return Number(window.__ANNUAL_DATA.calendarYear);
        }
        return new Date().getFullYear();
      }

      function defaultAnchorIso() {
        if (
          window.__ANNUAL_DATA &&
          window.__ANNUAL_DATA.daily &&
          window.__ANNUAL_DATA.daily.selectedDate
        ) {
          var sel = String(window.__ANNUAL_DATA.daily.selectedDate);
          if (parseIso(sel)) return sel;
        }
        var now = new Date();
        var y = operatingYear();
        if (now.getFullYear() === y) return isoFromDate(now);
        return y + '-01-01';
      }

      function todayIso() {
        var now = new Date();
        var y = operatingYear();
        if (now.getFullYear() === y) return isoFromDate(now);
        return y + '-01-01';
      }

      function weatherLabel(code) {
        var s = String(code == null ? '' : code);
        for (var i = 0; i < WEATHER_PRESETS.length; i++) {
          if (WEATHER_PRESETS[i].code === s) {
            return useJa ? WEATHER_PRESETS[i].ja : WEATHER_PRESETS[i].en;
          }
        }
        return dash;
      }

      function readBusinessDay(iso) {
        if (window.KpiYearStore && typeof KpiYearStore.readBusinessDay === 'function') {
          return KpiYearStore.readBusinessDay(iso);
        }
        return null;
      }

      function loadYearPayload(year) {
        if (!window.KpiYearStore || typeof KpiYearStore.loadMepYearPayload !== 'function') {
          return null;
        }
        return KpiYearStore.loadMepYearPayload(year);
      }

      function memoRowIdsForYear(year) {
        var payload = loadYearPayload(year);
        if (!payload) return [];
        if (payload.mepMemoRows && payload.mepMemoRows.length) {
          return payload.mepMemoRows.slice(0, 6).map(function (row) {
            return row.id;
          });
        }
        var memos = (payload.dailyMeta && payload.dailyMeta.memos) || {};
        return Object.keys(memos);
      }

      function readMemoText(year, rowId, iso) {
        var payload = loadYearPayload(year);
        if (!payload || !payload.dailyMeta || !payload.dailyMeta.memos) return '';
        var byRow = payload.dailyMeta.memos[rowId];
        if (!byRow) return '';
        return String(byRow[iso] == null ? '' : byRow[iso]).trim();
      }

      function readWeatherCode(year, iso) {
        var payload = loadYearPayload(year);
        if (!payload || !payload.dailyMeta || !payload.dailyMeta.weather) return '';
        return String(payload.dailyMeta.weather[iso] == null ? '' : payload.dailyMeta.weather[iso]);
      }

      function truncateTooltip(text) {
        text = String(text || '');
        if (text.length <= memoTooltipMax) return text;
        return text.slice(0, memoTooltipMax);
      }

      function memoDisplayText(text) {
        var t = String(text || '').trim();
        return t ? t : noneLabel;
      }

      function setCellInner(td, text) {
        var inner = td.querySelector('.insight-analyze-weekly__cell-inner');
        if (inner) inner.textContent = text;
        else td.textContent = text;
      }

      function applyMemoCell(td, rawText) {
        var full = truncateTooltip(rawText);
        var display = memoDisplayText(full);
        setCellInner(td, display);
        if (full) {
          td.classList.add('insight-analyze-weekly__memo');
          td.setAttribute('data-memo', full);
        } else {
          td.classList.remove('insight-analyze-weekly__memo');
          td.removeAttribute('data-memo');
        }
      }

      function weekIsoList(anchorIso) {
        var list = [];
        var i;
        for (i = -3; i <= 3; i++) list.push(addDaysIso(anchorIso, i));
        return list;
      }

      function formatNavDate(iso) {
        var p = parseIso(iso);
        if (!p) return iso;
        var dt = new Date(p.y, p.m0, p.d);
        return p.m0 + 1 + '/' + p.d + ' ' + WD_EN[dt.getDay()];
      }

      function formatRowDate(iso, isOff) {
        var p = parseIso(iso);
        if (!p) return iso;
        var dt = new Date(p.y, p.m0, p.d);
        var base = p.m0 + 1 + '/' + p.d + ' ' + WD_EN[dt.getDay()];
        return isOff ? base + offSuffix : base;
      }

      function updateNav(root, anchorIso) {
        var yearEl = root.querySelector('.insight-analyze-weekly__year');
        var dateBtn = root.querySelector('[data-weekly-nav="date-pick"]');
        var todayBtn = root.querySelector('[data-weekly-nav="today"]');
        var dateInput = root.querySelector('.insight-analyze-weekly__date-input');
        var p = parseIso(anchorIso);
        if (yearEl && p) yearEl.textContent = String(p.y);
        if (dateBtn) dateBtn.textContent = formatNavDate(anchorIso);
        if (todayBtn) todayBtn.textContent = todayNavLabel;
        if (dateInput) dateInput.value = anchorIso;
      }

      function renderRoot(root) {
        var anchorIso = root.__weeklyAnchorIso || sharedAnchorIso || defaultAnchorIso();
        root.__weeklyAnchorIso = anchorIso;
        sharedAnchorIso = anchorIso;
        var tbody = root.querySelector('.insight-analyze-weekly__table tbody');
        if (!tbody) return;
        updateNav(root, anchorIso);
        var isoList = weekIsoList(anchorIso);
        tbody.innerHTML = '';
        isoList.forEach(function (iso) {
          var p = parseIso(iso);
          if (!p) return;
          var biz = readBusinessDay(iso);
          var isOff = biz === false;
          var isToday = iso === anchorIso;
          var tr = document.createElement('tr');
          if (isOff) tr.className = 'insight-analyze-weekly__row--off';
          else if (isToday) tr.className = 'insight-analyze-weekly__row--today';

          var tdDate = document.createElement('td');
          tdDate.className = 'insight-analyze-weekly__col--date';
          var spanDate = document.createElement('span');
          spanDate.className = 'insight-analyze-weekly__cell-inner';
          spanDate.textContent = formatRowDate(iso, isOff);
          tdDate.appendChild(spanDate);
          tr.appendChild(tdDate);

          var tdWeather = document.createElement('td');
          tdWeather.className = 'insight-analyze-weekly__col--weather';
          var spanWeather = document.createElement('span');
          spanWeather.className = 'insight-analyze-weekly__cell-inner';
          spanWeather.textContent = isOff ? dash : weatherLabel(readWeatherCode(p.y, iso));
          tdWeather.appendChild(spanWeather);
          tr.appendChild(tdWeather);

          var rowIds = memoRowIdsForYear(p.y);
          MEMO_COLS.forEach(function (colKey, idx) {
            var td = document.createElement('td');
            td.className = 'insight-analyze-weekly__col--' + colKey;
            var span = document.createElement('span');
            span.className = 'insight-analyze-weekly__cell-inner';
            td.appendChild(span);
            if (isOff) setCellInner(td, dash);
            else {
              var rowId = rowIds[idx];
              applyMemoCell(td, rowId ? readMemoText(p.y, rowId, iso) : '');
            }
            tr.appendChild(td);
          });
          tbody.appendChild(tr);
        });
      }

      function renderAll() {
        roots.forEach(renderRoot);
      }

      function setAnchor(iso) {
        if (!parseIso(iso)) return;
        sharedAnchorIso = iso;
        roots.forEach(function (root) {
          root.__weeklyAnchorIso = iso;
        });
        renderAll();
      }

      function bindRoot(root) {
        if (root.__weeklyMemoBound) return;
        root.__weeklyMemoBound = true;
        var scroll = root.querySelector('.insight-analyze-weekly__table-scroll');
        if (scroll) scroll.style.pointerEvents = 'auto';
        var nav = root.querySelector('.insight-analyze-weekly__nav');
        var dateInput = root.querySelector('.insight-analyze-weekly__date-input');
        if (!nav) return;
        nav.addEventListener('click', function (ev) {
          var btn = ev.target.closest('[data-weekly-nav]');
          if (!btn || !root.contains(btn)) return;
          var action = btn.getAttribute('data-weekly-nav');
          var anchor = root.__weeklyAnchorIso || sharedAnchorIso || defaultAnchorIso();
          var p = parseIso(anchor);
          if (!p) return;
          if (action === 'year-prev') {
            setAnchor(isoFromParts(p.y - 1, p.m0, p.d));
            return;
          }
          if (action === 'year-next') {
            setAnchor(isoFromParts(p.y + 1, p.m0, p.d));
            return;
          }
          if (action === 'day-prev') {
            setAnchor(addDaysIso(anchor, -1));
            return;
          }
          if (action === 'day-next') {
            setAnchor(addDaysIso(anchor, 1));
            return;
          }
          if (action === 'today') {
            setAnchor(todayIso());
            return;
          }
          if (action === 'date-pick' && dateInput) {
            dateInput.value = anchor;
            if (typeof dateInput.showPicker === 'function') dateInput.showPicker();
            else dateInput.click();
          }
        });
        if (dateInput) {
          dateInput.addEventListener('change', function () {
            if (dateInput.value) setAnchor(dateInput.value);
          });
        }
      }

      function init() {
        roots = Array.prototype.slice.call(document.querySelectorAll('.insight-analyze-weekly'));
        if (!roots.length) return;
        if (!sharedAnchorIso) sharedAnchorIso = defaultAnchorIso();
        roots.forEach(bindRoot);
        renderAll();
      }

      document.addEventListener('kpi:mepDataChanged', function () {
        renderAll();
      });
      window.addEventListener('storage', function (ev) {
        if (!ev || !ev.key) return;
        if (ev.key === 'kpiNavigator.kpiYearStore') renderAll();
      });

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
      } else {
        init();
      }
    })();
