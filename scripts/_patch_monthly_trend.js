
      function initGraphMonthlyCumulativeTrend() {
        var frame = document.querySelector('.insight-graph-monthly-trend__frame');
        var svg = document.getElementById('insight-graph-monthly-trend-chart');
        if (!frame || !svg) return;

        var axesG = svg.querySelector('.insight-graph-monthly-trend__axes');
        var seriesG = svg.querySelector('.insight-graph-monthly-trend__series');
        var hoverRect = document.getElementById('insight-graph-monthly-trend-hover');
        var periodEl = document.getElementById('insight-graph-monthly-trend-period');
        var achievementEl = document.getElementById('insight-graph-monthly-trend-achievement');
        var tooltipEl = document.getElementById('insight-graph-monthly-trend-tooltip');
        var endKgiEl = document.getElementById('insight-graph-monthly-trend-end-kgi');
        var endKpiEl = document.getElementById('insight-graph-monthly-trend-end-kpi');

        var CFG = {
          axisLeft: 110,
          axisTop: 100,
          plotW: 800,
          plotH: 400,
          yTicks: 5,
          xTickSlots: 7
        };
        CFG.plotRight = CFG.axisLeft + CFG.plotW;
        CFG.plotBottom = CFG.axisTop + CFG.plotH;

        var isEn = /\/en\//.test(String(location.pathname || ''));
        var labels = isEn
          ? {
              sales: "Today's Sales",
              target: "Today's Target Sales",
              diff: 'Difference',
              achievement: 'Achievement'
            }
          : {
              sales: '本日の売上',
              target: '本日の目標売上',
              diff: '差額',
              achievement: '達成率'
            };

        function getFocusYearMonth() {
          var data = window.__ANNUAL_DATA || {};
          var iso = data.daily && data.daily.selectedDate;
          if (iso) {
            var parts = String(iso).split('-');
            var y = Number(parts[0]);
            var m = Number(parts[1]);
            if (Number.isFinite(y) && Number.isFinite(m)) return { year: y, month: m };
          }
          var now = new Date();
          return { year: now.getFullYear(), month: now.getMonth() + 1 };
        }

        function daysInMonth(year, month) {
          return new Date(year, month, 0).getDate();
        }

        function formatAxisMoney(v) {
          var n = Math.round(v);
          if (isEn) return '$' + n.toLocaleString('en-US');
          return '\u00a5' + n.toLocaleString('ja-JP');
        }

        function formatDetailMoney(v) {
          var n = Number(v);
          if (!Number.isFinite(n)) return isEn ? '$0' : '\u00a50';
          if (isEn) return '$' + n.toLocaleString('en-US', { maximumFractionDigits: 0 });
          return '\u00a5' + n.toLocaleString('ja-JP', { maximumFractionDigits: 0 });
        }

        function niceYMax(rawMax, tickCount) {
          var maxVal = Math.max(rawMax, 1);
          var step0 = maxVal / (tickCount - 1);
          var mag = Math.pow(10, Math.floor(Math.log10(step0)));
          if (!Number.isFinite(mag) || mag <= 0) mag = 1;
          var norm = step0 / mag;
          var niceStep = norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 5 ? 5 : 10;
          niceStep *= mag;
          var niceMax = Math.ceil(maxVal / niceStep) * niceStep;
          if (niceMax < maxVal) niceMax += niceStep;
          return niceMax;
        }

        function xForDay(day, dim) {
          if (dim <= 1) return CFG.axisLeft;
          return CFG.axisLeft + ((day - 1) / (dim - 1)) * CFG.plotW;
        }

        function yForValue(val, yMax) {
          var ratio = yMax > 0 ? val / yMax : 0;
          return CFG.plotBottom - ratio * CFG.plotH;
        }

        function buildXTickDays(dim) {
          if (dim <= 1) return [1];
          var slots = CFG.xTickSlots;
          var days = [];
          for (var i = 0; i < slots; i++) {
            var d = Math.round(1 + ((dim - 1) * i) / (slots - 1));
            if (days.indexOf(d) === -1) days.push(d);
          }
          if (days[days.length - 1] !== dim) days[days.length - 1] = dim;
          return days;
        }

        function buildDemoPayload(dim) {
          var baseDaily = isEn ? 4000 : 400000;
          var targetDaily = baseDaily * 0.92;
          var target = [];
          var actual = [];
          var dailyTarget = [];
          var dailyActual = [];
          var tSum = 0;
          var aSum = 0;
          for (var d = 1; d <= dim; d++) {
            var dt = targetDaily * (0.98 + 0.04 * (d / dim));
            var da = dt * (d < 8 ? 0.72 : d < 12 ? 0.9 : 1.02 + 0.08 * Math.sin(d / 2));
            dailyTarget.push(dt);
            dailyActual.push(da);
            tSum += dt;
            aSum += da;
            target.push(tSum);
            actual.push(aSum);
          }
          var todayDay = Math.min(dim, 18);
          return { target: target, actual: actual, dailyTarget: dailyTarget, dailyActual: dailyActual, todayDay: todayDay };
        }

        function pathFromPoints(pts) {
          if (!pts.length) return '';
          var d = 'M' + pts[0][0] + ' ' + pts[0][1];
          for (var i = 1; i < pts.length; i++) d += ' L' + pts[i][0] + ' ' + pts[i][1];
          return d;
        }

        function render() {
          var ym = getFocusYearMonth();
          var dim = daysInMonth(ym.year, ym.month);
          if (periodEl) periodEl.textContent = ym.year + '.' + ym.month;

          var payload = buildDemoPayload(dim);
          var yMax = niceYMax(
            Math.max.apply(null, payload.target.concat(payload.actual)),
            CFG.yTicks
          );

          axesG.innerHTML = '';
          seriesG.innerHTML = '';

          var ns = 'http://www.w3.org/2000/svg';
          function svgLine(x1, y1, x2, y2) {
            var el = document.createElementNS(ns, 'line');
            el.setAttribute('x1', x1);
            el.setAttribute('y1', y1);
            el.setAttribute('x2', x2);
            el.setAttribute('y2', y2);
            el.setAttribute('stroke', '#0f9403');
            el.setAttribute('stroke-width', '1');
            return el;
          }
          function svgText(x, y, anchor, content) {
            var el = document.createElementNS(ns, 'text');
            el.setAttribute('x', x);
            el.setAttribute('y', y);
            el.setAttribute('fill', '#58e1f3');
            el.setAttribute('font-size', '13');
            el.setAttribute('font-family', 'Orbitron, sans-serif');
            el.setAttribute('class', 'insight-graph-monthly-trend__axis-label');
            if (anchor) el.setAttribute('text-anchor', anchor);
            el.textContent = content;
            return el;
          }

          axesG.appendChild(svgLine(CFG.axisLeft, CFG.axisTop, CFG.axisLeft, CFG.plotBottom));
          axesG.appendChild(svgLine(CFG.axisLeft, CFG.plotBottom, CFG.plotRight, CFG.plotBottom));

          for (var ti = 0; ti < CFG.yTicks; ti++) {
            var val = (yMax * ti) / (CFG.yTicks - 1);
            var yy = yForValue(val, yMax);
            axesG.appendChild(svgText(CFG.axisLeft - 8, yy + 4, 'end', formatAxisMoney(val)));
          }

          buildXTickDays(dim).forEach(function (day) {
            var xx = xForDay(day, dim);
            axesG.appendChild(svgText(xx, CFG.plotBottom + 18, 'middle', String(day)));
          });

          var kpiPts = [];
          for (var d2 = 1; d2 <= dim; d2++) {
            kpiPts.push([xForDay(d2, dim), yForValue(payload.target[d2 - 1], yMax)]);
          }
          var kgiPts = [];
          for (var d3 = 1; d3 <= payload.todayDay; d3++) {
            kgiPts.push([xForDay(d3, dim), yForValue(payload.actual[d3 - 1], yMax)]);
          }

          var kpiPath = document.createElementNS(ns, 'path');
          kpiPath.setAttribute('class', 'insight-graph-monthly-trend__line--kpi');
          kpiPath.setAttribute('d', pathFromPoints(kpiPts));
          var kgiPath = document.createElementNS(ns, 'path');
          kgiPath.setAttribute('class', 'insight-graph-monthly-trend__line--kgi');
          kgiPath.setAttribute('d', pathFromPoints(kgiPts));
          seriesG.appendChild(kpiPath);
          seriesG.appendChild(kgiPath);

          if (endKpiEl && kpiPts.length) {
            var kp = kpiPts[kpiPts.length - 1];
            endKpiEl.textContent = formatDetailMoney(payload.target[dim - 1]);
            endKpiEl.style.left = kp[0] + 'px';
            endKpiEl.style.top = kp[1] - 6 + 'px';
          }
          if (endKgiEl && kgiPts.length) {
            var kg = kgiPts[kgiPts.length - 1];
            endKgiEl.textContent = formatDetailMoney(payload.actual[payload.todayDay - 1]);
            endKgiEl.style.left = kg[0] + 'px';
            endKgiEl.style.top = kg[1] - 6 + 'px';
          }

          var ach =
            payload.target[payload.todayDay - 1] > 0
              ? (payload.actual[payload.todayDay - 1] / payload.target[payload.todayDay - 1]) * 100
              : 0;
          if (achievementEl) achievementEl.textContent = ach.toFixed(1) + '%';

          function showTooltip(clientX, clientY, day) {
            if (!tooltipEl) return;
            var idx = day - 1;
            var sales = payload.dailyActual[idx];
            var tgt = payload.dailyTarget[idx];
            var diff = sales - tgt;
            var pct = tgt > 0 ? (sales / tgt) * 100 : 0;
            tooltipEl.querySelectorAll('[data-field]').forEach(function (row) {
              var field = row.getAttribute('data-field');
              if (field === 'date') row.textContent = ym.year + '/' + ym.month + '/' + day;
              if (field === 'sales') row.textContent = labels.sales + ': ' + formatDetailMoney(sales);
              if (field === 'target') row.textContent = labels.target + ': ' + formatDetailMoney(tgt);
              if (field === 'diff') row.textContent = labels.diff + ': ' + formatDetailMoney(diff);
              if (field === 'achievement') row.textContent = labels.achievement + ': ' + pct.toFixed(1) + '%';
            });
            var rect = frame.getBoundingClientRect();
            var localX = clientX - rect.left + 12;
            var localY = clientY - rect.top + 12;
            tooltipEl.style.left = Math.min(localX, rect.width - 220) + 'px';
            tooltipEl.style.top = Math.min(localY, rect.height - 100) + 'px';
            tooltipEl.classList.add('is-visible');
            tooltipEl.removeAttribute('hidden');
          }

          function hideTooltip() {
            if (!tooltipEl) return;
            tooltipEl.classList.remove('is-visible');
            tooltipEl.setAttribute('hidden', '');
          }

          if (hoverRect && !hoverRect.__trendBound) {
            hoverRect.__trendBound = true;
            hoverRect.addEventListener('mousemove', function (ev) {
              var svgRect = svg.getBoundingClientRect();
              var scaleX = 965 / svgRect.width;
              var svgX = (ev.clientX - svgRect.left) * scaleX;
              var day = Math.round(1 + ((svgX - CFG.axisLeft) / CFG.plotW) * (dim - 1));
              day = Math.max(1, Math.min(dim, day));
              showTooltip(ev.clientX, ev.clientY, day);
            });
            hoverRect.addEventListener('mouseleave', hideTooltip);
          }
        }

        render();
        document.addEventListener('annual:calendarDateChanged', render);
      }
      initGraphMonthlyCumulativeTrend();
