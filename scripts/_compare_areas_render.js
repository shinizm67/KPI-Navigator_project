      function fmtComparePeriodDate(year, month, period, axisMode) {
        if (axisMode === 'month') return year + '/' + period;
        return fmtDateYmd(year, month, period);
      }

      function buildCompareChartData(areaId, iso) {
        if (areaId === 2) return buildArea2ChartData(iso);
        if (areaId === 3) return buildArea3ChartData(iso);
        return buildArea1ChartData(iso);
      }

      function compareAreaText(areaId) {
        if (areaId === 2) {
          return { line: L.compare_area2_line_title, daily: L.compare_area2_daily_title };
        }
        if (areaId === 3) {
          return { line: L.compare_area3_line_title, daily: L.compare_area3_daily_title };
        }
        return { line: L.compare_line_title, daily: L.compare_daily_title };
      }

      function compareXTicksForChart(chartData) {
        if (chartData.axisMode === 'month') {
          return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
        }
        return area1XTickDays(chartData.periodCount);
      }

      function compareXTickSvgHtml(periodCount, ticks, padL, plotW, padT, plotH) {
        var y = padT + plotH + 16;
        return ticks
          .map(function (t) {
            var x = comparePeriodCenterX(t, periodCount, padL, plotW);
            return (
              '<text x="' +
              x.toFixed(1) +
              '" y="' +
              y.toFixed(1) +
              '" text-anchor="middle" class="pl-compare-line__axis-label">' +
              t +
              '</text>'
            );
          })
          .join('');
      }

      function renderCompareLine(areaId, iso) {
        var mount = document.getElementById('pl-compare-area-' + areaId + '-line');
        if (!mount) return;
        var chartData = buildCompareChartData(areaId, iso);
        if (!chartData) {
          mount.innerHTML = '<p class="pl-compare-hsnap__empty">' + L.compare_no_data + '</p>';
          return;
        }
        var state = compareLineState[areaId];
        var metric = state.metric;
        var canShowBest = area1CanShowBestYear(iso);
        var showBest = state.showBest && canShowBest;
        var data = chartData.cumulative[metric] || chartData.cumulative.income;
        var periodCount = chartData.periodCount;
        var dim = chartData.dim;
        var axisMode = chartData.axisMode || 'day';
        var labels = compareAreaText(areaId);
        var yMax = 0;
        area1ChartMetrics().forEach(function (k) {
          if (k === 'lastYear' && !state.showLast) return;
          if (k === 'bestYear' && !showBest) return;
          var arr = data[k];
          if (!arr || !arr.length) return;
          var end = arr[arr.length - 1];
          if (end > yMax) yMax = end;
        });
        if (!yMax) yMax = 1;
        yMax = Math.ceil(yMax / 10000) * 10000;
        var pad = area1ChartPad();
        var w = pad.w;
        var h = pad.h;
        var padL = pad.padL;
        var padR = pad.padR;
        var padT = pad.padT;
        var padB = pad.padB;
        var plotW = w - padL - padR;
        var plotH = h - padT - padB;
        var toPts = function (arr) {
          return arr
            .map(function (v, idx) {
              var x = comparePeriodCenterX(idx + 1, periodCount, padL, plotW);
              var y = padT + (1 - Math.min(1, v / yMax)) * plotH;
              return x.toFixed(1) + ',' + y.toFixed(1);
            })
            .join(' ');
        };
        var thisPts = toPts(data.thisYear);
        var lastPts = toPts(data.lastYear);
        var bestPts = toPts(data.bestYear);
        var xTickSvg = compareXTickSvgHtml(
          periodCount,
          compareXTicksForChart(chartData),
          padL,
          plotW,
          padT,
          plotH
        );
        var yTicks = [0, 0.25, 0.5, 0.75, 1]
          .map(function (r) {
            var y = padT + (1 - r) * plotH;
            return '<span style="top:' + area1ChartPctY(y, h) + '">' + formatScale(yMax * r) + '</span>';
          })
          .join('');
        var active = function (k) {
          return metric === k ? ' is-active' : '';
        };
        mount.innerHTML =
          '<section class="pl-compare-line">' +
          '<h4 class="pl-compare-line__title">' +
          labels.line +
          '</h4>' +
          '<div class="pl-compare-line__date pl-compare-hsnap__date">' +
          fmtDate(iso) +
          '</div>' +
          '<div class="pl-compare-line__metric-tabs">' +
          '<button type="button" class="pl-compare-line__metric' +
          active('income') +
          '" data-pl-line-metric="income">' +
          L.compare_income +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('expenses') +
          '" data-pl-line-metric="expenses">' +
          L.compare_expenses +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('fixed') +
          '" data-pl-line-metric="fixed">' +
          L.compare_fixed +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('expected') +
          '" data-pl-line-metric="expected">' +
          L.compare_expected +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('profit') +
          '" data-pl-line-metric="profit">' +
          L.compare_profit +
          '</button>' +
          '</div>' +
          '<div class="pl-compare-line__chart-wrap">' +
          '<svg class="pl-compare-line__svg" viewBox="0 0 ' +
          w +
          ' ' +
          h +
          '" preserveAspectRatio="none" aria-hidden="true">' +
          '<line x1="' +
          padL +
          '" y1="' +
          padT +
          '" x2="' +
          padL +
          '" y2="' +
          (padT + plotH) +
          '" stroke="#58e1f3" stroke-width="1"/>' +
          '<line x1="' +
          padL +
          '" y1="' +
          (padT + plotH) +
          '" x2="' +
          (padL + plotW) +
          '" y2="' +
          (padT + plotH) +
          '" stroke="#58e1f3" stroke-width="1"/>' +
          '<polyline points="' +
          thisPts +
          '" fill="none" stroke="#66e7ff" stroke-width="2" vector-effect="non-scaling-stroke"/>' +
          (state.showLast
            ? '<polyline points="' +
              lastPts +
              '" fill="none" stroke="#e8e54b" stroke-width="2" vector-effect="non-scaling-stroke"/>'
            : '') +
          (showBest
            ? '<polyline points="' +
              bestPts +
              '" fill="none" stroke="#16d33a" stroke-width="2" vector-effect="non-scaling-stroke"/>'
            : '') +
          xTickSvg +
          '</svg>' +
          '<div class="pl-compare-line__y-ticks">' +
          yTicks +
          '</div>' +
          area1ChartHoverLayer(w, h, padL, padT, plotW, plotH, true) +
          '</div>' +
          area1LegendHtml(state, canShowBest, 'data-pl-line-toggle') +
          '</section>';

        mount.querySelectorAll('[data-pl-line-metric]').forEach(function (btn) {
          btn.addEventListener('click', function () {
            compareLineState[areaId].metric = btn.getAttribute('data-pl-line-metric') || 'income';
            renderCompareLine(areaId, iso);
          });
        });
        mount.querySelectorAll('[data-pl-line-toggle]').forEach(function (box) {
          box.addEventListener('change', function () {
            var key = box.getAttribute('data-pl-line-toggle');
            if (key === 'last') compareLineState[areaId].showLast = !!box.checked;
            if (key === 'best') compareLineState[areaId].showBest = !!box.checked;
            renderCompareLine(areaId, iso);
          });
        });
        var chartWrap = mount.querySelector('.pl-compare-line__chart-wrap');
        bindArea1LineChartHover(chartWrap, {
          w: w,
          h: h,
          padL: padL,
          padT: padT,
          plotW: plotW,
          plotH: plotH,
          yMax: yMax,
          daysInMonth: periodCount,
          dim: dim,
          axisMode: axisMode,
          metric: metric,
          isoParts: isoParts(iso),
          bestYear: area1BestYearNumber(iso),
          showLast: state.showLast,
          showBest: showBest,
          canShowBest: canShowBest,
          values: data,
        });
      }

      function renderCompareDaily(areaId, iso) {
        var mount = document.getElementById('pl-compare-area-' + areaId + '-daily');
        if (!mount) return;
        var chartData = buildCompareChartData(areaId, iso);
        if (!chartData) {
          mount.innerHTML = '<p class="pl-compare-hsnap__empty">' + L.compare_no_data + '</p>';
          return;
        }
        var state = compareDailyState[areaId];
        var metric = state.metric;
        var canShowBest = area1CanShowBestYear(iso);
        var showBest = state.showBest && canShowBest;
        var dailyData = chartData.daily;
        var data = dailyData[metric] || dailyData.income;
        var periodCount = chartData.periodCount;
        var dim = chartData.dim;
        var axisMode = chartData.axisMode || 'day';
        var labels = compareAreaText(areaId);
        var yMax = 0;
        area1ChartMetrics().forEach(function (k) {
          if (k === 'lastYear' && !state.showLast) return;
          if (k === 'bestYear' && !showBest) return;
          var arr = data[k];
          if (!arr || !arr.length) return;
          arr.forEach(function (v) {
            if (v > yMax) yMax = v;
          });
        });
        if (!yMax) yMax = 1;
        yMax = Math.ceil(yMax / 1000) * 1000;
        var pad = area1ChartPad();
        var w = pad.w;
        var h = pad.h;
        var padL = pad.padL;
        var padR = pad.padR;
        var padT = pad.padT;
        var padB = pad.padB;
        var plotW = w - padL - padR;
        var plotH = h - padT - padB;
        var bars = renderArea1DailyBars(
          dailyData,
          metric,
          state.showLast,
          state.showBest,
          canShowBest,
          yMax,
          padL,
          padT,
          plotW,
          plotH,
          periodCount,
          dim
        );
        var xTickSvg = compareXTickSvgHtml(
          periodCount,
          compareXTicksForChart(chartData),
          padL,
          plotW,
          padT,
          plotH
        );
        var yTicks = [0, 0.25, 0.5, 0.75, 1]
          .map(function (r) {
            var y = padT + (1 - r) * plotH;
            return '<span style="top:' + area1ChartPctY(y, h) + '">' + formatScale(yMax * r) + '</span>';
          })
          .join('');
        var active = function (k) {
          return metric === k ? ' is-active' : '';
        };
        mount.innerHTML =
          '<section class="pl-compare-line pl-compare-daily">' +
          '<h4 class="pl-compare-line__title">' +
          labels.daily +
          '</h4>' +
          '<div class="pl-compare-line__date pl-compare-hsnap__date">' +
          fmtDate(iso) +
          '</div>' +
          '<div class="pl-compare-line__metric-tabs">' +
          '<button type="button" class="pl-compare-line__metric' +
          active('income') +
          '" data-pl-daily-metric="income">' +
          L.compare_income +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('expenses') +
          '" data-pl-daily-metric="expenses">' +
          L.compare_expenses +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('fixed') +
          '" data-pl-daily-metric="fixed">' +
          L.compare_fixed +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('expected') +
          '" data-pl-daily-metric="expected">' +
          L.compare_expected +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('profit') +
          '" data-pl-daily-metric="profit">' +
          L.compare_profit +
          '</button>' +
          '</div>' +
          '<div class="pl-compare-line__chart-wrap">' +
          '<svg class="pl-compare-line__svg" viewBox="0 0 ' +
          w +
          ' ' +
          h +
          '" preserveAspectRatio="none" aria-hidden="true">' +
          '<line x1="' +
          padL +
          '" y1="' +
          padT +
          '" x2="' +
          padL +
          '" y2="' +
          (padT + plotH) +
          '" stroke="#58e1f3" stroke-width="1"/>' +
          '<line x1="' +
          padL +
          '" y1="' +
          (padT + plotH) +
          '" x2="' +
          (padL + plotW) +
          '" y2="' +
          (padT + plotH) +
          '" stroke="#58e1f3" stroke-width="1"/>' +
          bars +
          xTickSvg +
          '</svg>' +
          '<div class="pl-compare-line__y-ticks">' +
          yTicks +
          '</div>' +
          area1ChartHoverLayer(w, h, padL, padT, plotW, plotH, false) +
          '</div>' +
          area1LegendHtml(state, canShowBest, 'data-pl-daily-toggle') +
          '</section>';

        mount.querySelectorAll('[data-pl-daily-metric]').forEach(function (btn) {
          btn.addEventListener('click', function () {
            compareDailyState[areaId].metric = btn.getAttribute('data-pl-daily-metric') || 'income';
            renderCompareDaily(areaId, iso);
          });
        });
        mount.querySelectorAll('[data-pl-daily-toggle]').forEach(function (box) {
          box.addEventListener('change', function () {
            var key = box.getAttribute('data-pl-daily-toggle');
            if (key === 'last') compareDailyState[areaId].showLast = !!box.checked;
            if (key === 'best') compareDailyState[areaId].showBest = !!box.checked;
            renderCompareDaily(areaId, iso);
          });
        });
        var chartWrap = mount.querySelector('.pl-compare-line__chart-wrap');
        bindArea1DailyChartHover(chartWrap, {
          w: w,
          h: h,
          padL: padL,
          padT: padT,
          plotW: plotW,
          plotH: plotH,
          yMax: yMax,
          daysInMonth: periodCount,
          dim: dim,
          axisMode: axisMode,
          metric: metric,
          isoParts: isoParts(iso),
          bestYear: area1BestYearNumber(iso),
          showLast: state.showLast,
          showBest: showBest,
          canShowBest: canShowBest,
          values: data,
        });
      }

      function renderCompareFl(areaId, iso) {
        var mount = document.getElementById('pl-compare-area-' + areaId + '-fl');
        if (!mount) return;
        iso = iso || selectedIso || resolveIso();
        var parts = isoParts(iso);
        if (!parts) return;
        var pad2 = function (n) {
          return n < 10 ? '0' + n : String(n);
        };
        var current;
        var previous;
        var primaryLabel;
        var secondaryLabel;
        if (areaId === 1) {
          var refIso = sameWeekdayLastYearIso(iso);
          current = fetchCurrentFlSnapshot(iso);
          previous = fetchPreviousFlSnapshot(refIso);
          primaryLabel = fmtDate(iso);
          secondaryLabel = L.compare_same_weekday_of + fmtDate(refIso);
        } else if (areaId === 2) {
          var lyIso = parts.year - 1 + '-' + pad2(parts.month) + '-' + pad2(parts.day);
          var tyIso = parts.year - 2 + '-' + pad2(parts.month) + '-' + pad2(parts.day);
          current = fetchCurrentFlSnapshot(lyIso);
          previous = fetchPreviousFlSnapshot(tyIso);
          primaryLabel = L.compare_area2_hsnap_primary + fmtDate(lyIso);
          secondaryLabel = L.compare_area2_hsnap_secondary + fmtDate(tyIso);
        } else {
          var lyYtdIso = parts.year - 1 + '-' + pad2(parts.month) + '-' + pad2(parts.day);
          current = fetchCurrentFlSnapshot(iso);
          previous = fetchPreviousFlSnapshot(lyYtdIso);
          primaryLabel = L.compare_area3_hsnap_primary + fmtDate(iso);
          secondaryLabel = L.compare_area3_hsnap_secondary + fmtDate(lyYtdIso);
        }
        var maxIncome = current ? current.income : 0;
        if (previous && previous.income > maxIncome) maxIncome = previous.income;
        if (!maxIncome) maxIncome = 1;
        mount.innerHTML =
          renderHsnapBlock(primaryLabel, current, maxIncome, 0, false) +
          renderHsnapBlock(secondaryLabel, previous, maxIncome, 1, true);
      }

      function renderAllCompareAreas(iso) {
        iso = iso || selectedIso || resolveIso();
        [1, 2, 3].forEach(function (areaId) {
          renderCompareFl(areaId, iso);
          renderCompareLine(areaId, iso);
          renderCompareDaily(areaId, iso);
        });
      }
