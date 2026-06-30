
      function initGraphMonthlyCumulativeTrendGraph2() {
        var root = document.getElementById('insight-graph-monthly-graph2');
        var frame = root && root.querySelector('.insight-graph-monthly-trend__frame');
        var svg = document.getElementById('insight-graph-monthly-graph2-chart');
        if (!frame || !svg) return;

        var axesG = svg.querySelector('.insight-graph-monthly-trend__axes');
        var seriesG = svg.querySelector('.insight-graph-monthly-trend__series');
        var hoverRect = document.getElementById('insight-graph-monthly-graph2-hover');
        var tooltipEl = document.getElementById('insight-graph-monthly-graph2-tooltip');
        var endCurrentEl = document.getElementById('insight-graph-monthly-graph2-end-current');
        var endLastYearEl = document.getElementById('insight-graph-monthly-graph2-end-last-year');
        var endBestEl = document.getElementById('insight-graph-monthly-graph2-end-best');

        var CFG = {
          axisLeft: 110,
          axisTop: 100,
          plotW: 800,
          plotH: 400,
          yTicks: 6,
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

        var SERIES_ORDER = [
          { key: 'best', lineClass: 'insight-graph-monthly-trend__line--best', dotClass: 'insight-graph-monthly-trend__hit-dot--best', fullMonth: true },
          { key: 'lastYear', lineClass: 'insight-graph-monthly-trend__line--last-year', dotClass: 'insight-graph-monthly-trend__hit-dot--last-year', fullMonth: true },
          { key: 'current', lineClass: 'insight-graph-monthly-trend__line--current', dotClass: 'insight-graph-monthly-trend__hit-dot--current', fullMonth: false }
        ];

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

        function formatTooltipDate(year, month, day) {
          var dt = new Date(year, month - 1, day);
          var wd = isEn ? weekdayEn[dt.getDay()] : weekdayJa[dt.getDay()];
          if (isEn) return year + '.' + month + '.' + day + ' ' + wd;
          return year + '.' + month + '.' + day + ' (' + wd + ')';
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

        function buildComparePayload(dim) {
          var baseDaily = isEn ? 650 : 65000;
          function dailyAmount(day, mult, phase) {
            return baseDaily * mult * (0.92 + 0.12 * (day / dim) + 0.06 * Math.sin(day * 0.45 + phase));
          }
          function toCumulative(untilDay, mult, phase) {
            var arr = [];
            var sum = 0;
            for (var d = 1; d <= untilDay; d++) {
              sum += dailyAmount(d, mult, phase);
              arr.push(sum);
            }
            return arr;
          }
          var todayDay = Math.min(dim, 22);
          return {
            current: toCumulative(todayDay, 1, 0),
            lastYear: toCumulative(dim, 0.9, 1.3),
            best: toCumulative(dim, 1.08, 2.4),
            todayDay: todayDay
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

        function seriesEndDay(meta, dim, todayDay) {
          return meta.fullMonth ? dim : Math.min(todayDay, dim);
        }

        function seriesPoint(meta, day, state) {
          var endDay = seriesEndDay(meta, state.dim, state.payload.todayDay);
          if (day > endDay) return null;
          var idx = day - 1;
          var val = state.payload[meta.key][idx];
          if (!Number.isFinite(val)) return null;
          return [xForDay(day, state.dim), yForValue(val, state.yMax)];
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
          SERIES_ORDER.forEach(function (meta) {
            var pt = seriesPoint(meta, day, state);
            if (!pt) return;
            var dist = Math.hypot(svgX - pt[0], svgY - pt[1]);
            if (dist <= CFG.hitRadius && (!best || dist < best.dist)) {
              best = { meta: meta, day: day, x: pt[0], y: pt[1], dist: dist };
            }
          });
          return best;
        }

        function hideHoverUi() {
          if (frame.__trendHoverEls) {
            frame.__trendHoverEls.guideV.classList.remove('is-visible');
            frame.__trendHoverEls.hitDot.classList.remove(
              'is-visible',
              'insight-graph-monthly-trend__hit-dot--current',
              'insight-graph-monthly-trend__hit-dot--last-year',
              'insight-graph-monthly-trend__hit-dot--best'
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
          var cur = state.payload.current[idx];
          var ly = state.payload.lastYear[idx];
          var bestVal = state.payload.best[idx];

          els.guideV.setAttribute('x1', hit.x);
          els.guideV.setAttribute('x2', hit.x);
          els.guideV.setAttribute('y1', CFG.axisTop);
          els.guideV.setAttribute('y2', CFG.plotBottom);
          els.guideV.classList.add('is-visible');

          els.hitDot.setAttribute('cx', hit.x);
          els.hitDot.setAttribute('cy', hit.y);
          els.hitDot.setAttribute('r', '6');
          els.hitDot.classList.remove(
            'insight-graph-monthly-trend__hit-dot--current',
            'insight-graph-monthly-trend__hit-dot--last-year',
            'insight-graph-monthly-trend__hit-dot--best'
          );
          els.hitDot.classList.add('is-visible', hit.meta.dotClass);

          var dateEl = tooltipEl.querySelector('[data-field="date"]');
          if (dateEl) dateEl.textContent = formatTooltipDate(state.ym.year, state.ym.month, hit.day);
          var salesEl = tooltipEl.querySelector('[data-field="sales"]');
          if (salesEl) salesEl.textContent = formatDetailMoney(cur);
          var targetEl = tooltipEl.querySelector('[data-field="target"]');
          if (targetEl) targetEl.textContent = formatDetailMoney(ly);
          var diffEl = tooltipEl.querySelector('[data-field="diff"]');
          if (diffEl) diffEl.textContent = formatDetailMoney(bestVal);
          var achEl = tooltipEl.querySelector('[data-field="achievement"]');
          if (achEl) {
            var pct = ly > 0 && hit.day <= state.payload.todayDay ? (cur / ly) * 100 : 0;
            achEl.textContent = pct.toFixed(1) + '%';
          }

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

        function placeEndpoint(el, pts, value) {
          if (!el || !pts.length) return;
          var p = pts[pts.length - 1];
          el.textContent = formatDetailMoney(value);
          el.style.left = p[0] + 'px';
          el.style.top = p[1] - 6 + 'px';
        }

        function render() {
          var ym = getFocusYearMonth();
          var dim = daysInMonth(ym.year, ym.month);
          var payload = buildComparePayload(dim);
          var allVals = payload.best.concat(payload.lastYear).concat(payload.current);
          var yMax = niceYMax(Math.max.apply(null, allVals), CFG.yTicks);

          frame.__trendChartState = { dim: dim, ym: ym, payload: payload, yMax: yMax };

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

          SERIES_ORDER.forEach(function (meta) {
            var endDay = seriesEndDay(meta, dim, payload.todayDay);
            var pts = [];
            for (var d = 1; d <= endDay; d++) {
              pts.push([xForDay(d, dim), yForValue(payload[meta.key][d - 1], yMax)]);
            }
            var path = document.createElementNS(ns, 'path');
            path.setAttribute('class', meta.lineClass);
            path.setAttribute('d', pathFromPoints(pts));
            seriesG.appendChild(path);

            if (meta.key === 'current') {
              placeEndpoint(endCurrentEl, pts, payload.current[payload.todayDay - 1]);
            } else if (meta.key === 'lastYear') {
              placeEndpoint(endLastYearEl, pts, payload.lastYear[dim - 1]);
            } else if (meta.key === 'best') {
              placeEndpoint(endBestEl, pts, payload.best[dim - 1]);
            }
          });

          var hoverUiG = svg.querySelector('.insight-graph-monthly-trend__hover-ui');
          if (!hoverUiG) {
            hoverUiG = document.createElementNS(ns, 'g');
            hoverUiG.setAttribute('class', 'insight-graph-monthly-trend__hover-ui');
            hoverUiG.setAttribute('aria-hidden', 'true');
            svg.appendChild(hoverUiG);
          }
          hoverUiG.innerHTML = '';
          var guideV = document.createElementNS(ns, 'line');
          guideV.setAttribute('class', 'insight-graph-monthly-trend__guide-v');
          var hitDot = document.createElementNS(ns, 'circle');
          hitDot.setAttribute('class', 'insight-graph-monthly-trend__hit-dot');
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
