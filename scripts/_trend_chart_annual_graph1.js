
      function initGraphAnnualCumulativeTrendGraph1() {
        var root = document.getElementById('insight-graph-annual-graph1');
        var frame = root && root.querySelector('.insight-graph-annual-trend__frame');
        var svg = document.getElementById('insight-graph-annual-graph1-chart');
        if (!frame || !svg) return;

        var axesG = svg.querySelector('.insight-graph-annual-trend__axes');
        var seriesG = svg.querySelector('.insight-graph-annual-trend__series');
        var hoverRect = document.getElementById('insight-graph-annual-graph1-hover');
        var periodEl = document.getElementById('insight-graph-annual-graph1-period');
        var achievementEl = document.getElementById('insight-graph-annual-graph1-achievement');
        var tooltipEl = document.getElementById('insight-graph-annual-graph1-tooltip');
        var endKgiEl = document.getElementById('insight-graph-annual-graph1-end-kgi');
        var endKpiEl = document.getElementById('insight-graph-annual-graph1-end-kpi');

        var CFG = {
          axisLeft: 110,
          axisTop: 100,
          plotW: 817,
          plotH: 400,
          yTicks: 5,
          xTickSlots: 7,
          hitRadius: 14,
          tooltipW: 400,
          tooltipH: 240,
          tooltipOffset: 16
        };
        CFG.plotRight = CFG.axisLeft + CFG.plotW;
        CFG.plotBottom = CFG.axisTop + CFG.plotH;

        var isEn = /\/en\//.test(String(location.pathname || ''));
        var weekdayEn = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
        var weekdayJa = ['\u65e5', '\u6708', '\u706b', '\u6c34', '\u6728', '\u91d1', '\u571f'];


        function getFocusYearContext() {
          var data = window.__ANNUAL_DATA || {};
          var iso = data.daily && data.daily.selectedDate;
          var year;
          var month;
          var day;
          if (iso) {
            var parts = String(iso).split('-');
            year = Number(parts[0]);
            month = Number(parts[1]);
            day = Number(parts[2]);
          } else {
            var now = new Date();
            year = now.getFullYear();
            month = now.getMonth() + 1;
            day = now.getDate();
          }
          if (!Number.isFinite(year)) year = new Date().getFullYear();
          if (!Number.isFinite(month)) month = 1;
          if (!Number.isFinite(day)) day = 1;
          var dim = daysInYear(year);
          var start = new Date(year, 0, 1);
          var dt = new Date(year, month - 1, day);
          var dayOfYear = Math.floor((dt - start) / 86400000) + 1;
          if (!Number.isFinite(dayOfYear) || dayOfYear < 1) dayOfYear = 1;
          if (dayOfYear > dim) dayOfYear = dim;
          return { year: year, month: month, day: day, dayOfYear: dayOfYear, dim: dim };
        }

        function daysInYear(year) {
          return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0 ? 366 : 365;
        }

        function calendarFromDayOfYear(year, dayOfYear) {
          var dt = new Date(year, 0, dayOfYear);
          return { year: dt.getFullYear(), month: dt.getMonth() + 1, day: dt.getDate() };
        }

        function formatTooltipDateFromDayOfYear(year, dayOfYear) {
          var cal = calendarFromDayOfYear(year, dayOfYear);
          var dt = new Date(cal.year, cal.month - 1, cal.day);
          var wd = isEn ? weekdayEn[dt.getDay()] : weekdayJa[dt.getDay()];
          if (isEn) return cal.year + '.' + cal.month + '.' + cal.day + ' ' + wd;
          return cal.year + '.' + cal.month + '.' + cal.day + ' (' + wd + ')';
        }

        function buildXTickMonths(year, dim) {
          var ticks = [];
          for (var m = 1; m <= 12; m++) {
            var start = new Date(year, m - 1, 1);
            var dayOfYear = Math.floor((start - new Date(year, 0, 1)) / 86400000) + 1;
            if (dayOfYear < 1) dayOfYear = 1;
            if (dayOfYear > dim) dayOfYear = dim;
            ticks.push({ day: dayOfYear, label: String(m) });
          }
          return ticks;
        }

        function formatAxisMoney(v) {
          var n = Math.round(v);
          if (window.KpiCurrency) return KpiCurrency.format(n, { round: true });
          if (isEn) return '$' + n.toLocaleString('en-US');
          return '¥' + n.toLocaleString('ja-JP');
        }

        function formatDetailMoney(v) {
          var n = Number(v);
          if (!Number.isFinite(n)) return isEn ? '$0' : '¥0';
          if (window.KpiCurrency) return KpiCurrency.format(n, { maximumFractionDigits: 0 });
          if (isEn) return '$' + n.toLocaleString('en-US', { maximumFractionDigits: 0 });
          return '¥' + n.toLocaleString('ja-JP', { maximumFractionDigits: 0 });
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

        function buildDemoPayload(dim, todayDay) {
          var baseDaily = isEn ? 12000 : 1200000;
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
          var endDay = Math.min(dim, todayDay || Math.min(dim, 132));
          return {
            target: target,
            actual: actual,
            dailyTarget: dailyTarget,
            dailyActual: dailyActual,
            todayDay: endDay
          };
        }

        function pathFromPoints(pts) {
          if (!pts.length) return '';
          var d = 'M' + pts[0][0] + ' ' + pts[0][1];
          for (var i = 1; i < pts.length; i++) d += ' L' + pts[i][0] + ' ' + pts[i][1];
          return d;
        }

        function clientToSvg(ev) {
          var svgRect = svg.getBoundingClientRect();
          var scaleX = 965 / svgRect.width;
          var scaleY = 618 / svgRect.height;
          return {
            x: (ev.clientX - svgRect.left) * scaleX,
            y: (ev.clientY - svgRect.top) * scaleY
          };
        }

        function snapDay(svgX, dim) {
          var day = Math.round(1 + ((svgX - CFG.axisLeft) / CFG.plotW) * (dim - 1));
          return Math.max(1, Math.min(dim, day));
        }

        function seriesPoint(series, day, state) {
          var idx = day - 1;
          if (series === 'kpi') {
            return [xForDay(day, state.dim), yForValue(state.payload.target[idx], state.yMax)];
          }
          if (series === 'kgi' && day <= state.payload.todayDay) {
            return [xForDay(day, state.dim), yForValue(state.payload.actual[idx], state.yMax)];
          }
          return null;
        }

        function hitTest(svgX, svgY, state) {
          if (
            svgX < CFG.axisLeft ||
            svgX > CFG.plotRight ||
            svgY < CFG.axisTop ||
            svgY > CFG.plotBottom
          ) {
            return null;
          }
          var day = snapDay(svgX, state.dim);
          var best = null;
          ['kgi', 'kpi'].forEach(function (series) {
            var pt = seriesPoint(series, day, state);
            if (!pt) return;
            var dist = Math.hypot(svgX - pt[0], svgY - pt[1]);
            if (dist <= CFG.hitRadius && (!best || dist < best.dist)) {
              best = { series: series, day: day, x: pt[0], y: pt[1], dist: dist };
            }
          });
          return best;
        }

        function hideHoverUi() {
          if (frame.__trendHoverEls) {
            frame.__trendHoverEls.guideV.classList.remove('is-visible');
            frame.__trendHoverEls.hitDot.classList.remove(
              'is-visible',
              'insight-graph-annual-trend__hit-dot--kgi',
              'insight-graph-annual-trend__hit-dot--kpi'
            );
          }
          if (tooltipEl) {
            tooltipEl.classList.remove('is-visible');
            tooltipEl.setAttribute('hidden', '');
          }
        }

        function showHoverUi(hit, state) {
          if (!frame.__trendHoverEls || !tooltipEl) return;
          var els = frame.__trendHoverEls;
          var idx = hit.day - 1;
          var sales = state.payload.dailyActual[idx];
          var tgt = state.payload.dailyTarget[idx];
          var diff = sales - tgt;
          var pct = tgt > 0 ? (sales / tgt) * 100 : 0;

          els.guideV.setAttribute('x1', hit.x);
          els.guideV.setAttribute('x2', hit.x);
          els.guideV.setAttribute('y1', CFG.axisTop);
          els.guideV.setAttribute('y2', CFG.plotBottom);
          els.guideV.classList.add('is-visible');

          els.hitDot.setAttribute('cx', hit.x);
          els.hitDot.setAttribute('cy', hit.y);
          els.hitDot.setAttribute('r', '6');
          els.hitDot.classList.remove('insight-graph-annual-trend__hit-dot--kgi', 'insight-graph-annual-trend__hit-dot--kpi');
          els.hitDot.classList.add(
            'is-visible',
            hit.series === 'kgi'
              ? 'insight-graph-annual-trend__hit-dot--kgi'
              : 'insight-graph-annual-trend__hit-dot--kpi'
          );

          var dateEl = tooltipEl.querySelector('[data-field="date"]');
          if (dateEl) dateEl.textContent = formatTooltipDateFromDayOfYear(state.ctx.year, hit.day);
          var salesEl = tooltipEl.querySelector('[data-field="sales"]');
          if (salesEl) salesEl.textContent = formatDetailMoney(sales);
          var targetEl = tooltipEl.querySelector('[data-field="target"]');
          if (targetEl) targetEl.textContent = formatDetailMoney(tgt);
          var diffEl = tooltipEl.querySelector('[data-field="diff"]');
          if (diffEl) diffEl.textContent = formatDetailMoney(diff);
          var achEl = tooltipEl.querySelector('[data-field="achievement"]');
          if (achEl) achEl.textContent = pct.toFixed(1) + '%';

          var left = hit.x + CFG.tooltipOffset;
          var top = hit.y - CFG.tooltipH - CFG.tooltipOffset;
          if (left + CFG.tooltipW > 965) left = hit.x - CFG.tooltipW - CFG.tooltipOffset;
          if (left < 0) left = CFG.tooltipOffset;
          if (top < 0) top = hit.y + CFG.tooltipOffset;
          if (top + CFG.tooltipH > 618) top = Math.max(0, 618 - CFG.tooltipH - CFG.tooltipOffset);

          tooltipEl.style.left = left + 'px';
          tooltipEl.style.top = top + 'px';
          tooltipEl.classList.add('is-visible');
          tooltipEl.removeAttribute('hidden');
        }

        function onHoverMove(ev) {
          var state = frame.__trendChartState;
          if (!state) {
            hideHoverUi();
            return;
          }
          var pt = clientToSvg(ev);
          var hit = hitTest(pt.x, pt.y, state);
          if (!hit) {
            hideHoverUi();
            return;
          }
          showHoverUi(hit, state);
        }

        function render() {
          var ctx = getFocusYearContext();
          var dim = ctx.dim;
          if (periodEl) periodEl.textContent = String(ctx.year);

          var payload = buildDemoPayload(dim, ctx.dayOfYear);
          var yMax = niceYMax(
            Math.max.apply(null, payload.target.concat(payload.actual)),
            CFG.yTicks
          );

          frame.__trendChartState = { dim: dim, ctx: ctx, payload: payload, yMax: yMax };

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
            el.setAttribute('class', 'insight-graph-annual-trend__axis-label');
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

          buildXTickMonths(ctx.year, dim).forEach(function (tick) {
            var xx = xForDay(tick.day, dim);
            axesG.appendChild(svgText(xx, CFG.plotBottom + 18, 'middle', tick.label));
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
          kpiPath.setAttribute('class', 'insight-graph-annual-trend__line--kpi');
          kpiPath.setAttribute('d', pathFromPoints(kpiPts));
          var kgiPath = document.createElementNS(ns, 'path');
          kgiPath.setAttribute('class', 'insight-graph-annual-trend__line--kgi');
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

          var hoverUiG = svg.querySelector('.insight-graph-annual-trend__hover-ui');
          if (!hoverUiG) {
            hoverUiG = document.createElementNS(ns, 'g');
            hoverUiG.setAttribute('class', 'insight-graph-annual-trend__hover-ui');
            hoverUiG.setAttribute('aria-hidden', 'true');
            svg.appendChild(hoverUiG);
          }
          hoverUiG.innerHTML = '';
          var guideV = document.createElementNS(ns, 'line');
          guideV.setAttribute('class', 'insight-graph-annual-trend__guide-v');
          var hitDot = document.createElementNS(ns, 'circle');
          hitDot.setAttribute('class', 'insight-graph-annual-trend__hit-dot');
          hoverUiG.appendChild(guideV);
          hoverUiG.appendChild(hitDot);
          frame.__trendHoverEls = { guideV: guideV, hitDot: hitDot, hoverUiG: hoverUiG };

          hideHoverUi();
        }

        if (hoverRect && !hoverRect.__trendBound) {
          hoverRect.__trendBound = true;
          hoverRect.addEventListener('mousemove', onHoverMove);
          hoverRect.addEventListener('mouseleave', hideHoverUi);
        }

        render();
        document.addEventListener('annual:calendarDateChanged', render);
      }
