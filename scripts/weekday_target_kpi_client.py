"""Phase 11 Step 1 — weekday share / daily KPI compute (Store API only, no UI wiring)."""

from __future__ import annotations

WEEKDAY_TARGET_KPI_MARKER = "/* KPI-WEEKDAY-TARGET (Phase 11) */"


def weekday_target_kpi_js() -> str:
    return f"""
        {WEEKDAY_TARGET_KPI_MARKER}
        var WEEKDAY_SHARE_FALLBACK = 1 / 7;

        var __planMonthlyTargetsCache = {{}};
        var __weekdayShareMatrixCache = {{}};
        var __yearHasPositiveSalesCache = {{}};

        function yearHasPositiveTimelineSales(year) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return false;
          if (Object.prototype.hasOwnProperty.call(__yearHasPositiveSalesCache, y)) {{
            return __yearHasPositiveSalesCache[y];
          }}
          var has = false;
          Object.keys(store.timeline.dailySales).forEach(function (iso) {{
            if (isoYear(iso) !== y) return;
            var n = Number(store.timeline.dailySales[iso]);
            if (Number.isFinite(n) && n > 0) has = true;
          }});
          __yearHasPositiveSalesCache[y] = has;
          return has;
        }}

        function normalizeWeekdayBaselineYears(years, operatingYear) {{
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy)) return [];
          var seen = {{}};
          var out = [];
          (years || []).forEach(function (raw) {{
            var y = Number(raw);
            if (!Number.isFinite(y) || y >= oy || seen[y]) return;
            if (!yearHasPositiveTimelineSales(y)) return;
            seen[y] = true;
            out.push(y);
          }});
          return out.sort(function (a, b) {{ return a - b; }});
        }}

        function listEligibleWeekdayBaselineYears(operatingYear, maxLookback) {{
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy)) return [];
          var cap = maxLookback == null ? 5 : Math.max(1, Math.min(5, Number(maxLookback) || 5));
          var seen = {{}};
          var out = [];
          function tryYear(y) {{
            if (!Number.isFinite(y) || y >= oy || seen[y]) return;
            if (!yearHasPositiveTimelineSales(y)) return;
            seen[y] = true;
            out.push(y);
          }}
          Object.keys(store.years).forEach(function (yk) {{
            tryYear(Number(yk));
          }});
          listYearsWithData().forEach(function (y) {{
            tryYear(y);
          }});
          return out.sort(function (a, b) {{ return b - a; }}).slice(0, cap).sort(function (a, b) {{
            return a - b;
          }});
        }}

        function getDefaultWeekdayBaselineYears(operatingYear) {{
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy)) return [];
          var eligible = listEligibleWeekdayBaselineYears(oy, 5);
          var picked = [];
          for (var i = eligible.length - 1; i >= 0 && picked.length < 2; i--) {{
            picked.unshift(eligible[i]);
          }}
          return picked;
        }}

        function readWeekdayBaselineYears(year) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return getDefaultWeekdayBaselineYears(getOperatingYear());
          var rec = store.years[y];
          if (
            rec &&
            rec.plan &&
            rec.plan.weekdayBaselineYears &&
            rec.plan.weekdayBaselineYears.length
          ) {{
            var normalized = normalizeWeekdayBaselineYears(rec.plan.weekdayBaselineYears, y);
            if (normalized.length) return normalized;
          }}
          return getDefaultWeekdayBaselineYears(y);
        }}

        function writeWeekdayBaselineYears(year, years, meta) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return false;
          var normalized = normalizeWeekdayBaselineYears(years, y);
          if (!normalized.length) return false;
          var rec = ensureYearRecord(y);
          if (!rec.plan) rec.plan = {{}};
          rec.plan.weekdayBaselineYears = normalized.slice();
          rec.plan.weekdayBaselineUpdatedAt = Date.now();
          rec.plan.weekdayBaselineSource = (meta && meta.source) || 'kpi-year-store';
          persistStore();
          clearDailyTargetDisplayCache();
          document.dispatchEvent(
            new CustomEvent('kpi:weekdayBaselineChanged', {{
              detail: {{
                year: y,
                weekdayBaselineYears: normalized.slice(),
                source: rec.plan.weekdayBaselineSource,
              }},
            }})
          );
          return true;
        }}

        function readTimelineSalesAmount(iso) {{
          if (!Object.prototype.hasOwnProperty.call(store.timeline.dailySales, iso)) return 0;
          var n = Number(store.timeline.dailySales[iso]);
          return Number.isFinite(n) && n > 0 ? n : 0;
        }}

        function computeWeekdayMonthSalesTotal(y, m0) {{
          var year = Number(y);
          var month = Number(m0);
          if (!Number.isFinite(year) || !Number.isFinite(month) || month < 0 || month > 11) return 0;
          var dc = new Date(year, month + 1, 0).getDate();
          var total = 0;
          for (var day = 1; day <= dc; day++) {{
            if (!isCalendarBusinessDay(year, month, day)) continue;
            var iso = year + '-' + pad2(month + 1) + '-' + pad2(day);
            total += readTimelineSalesAmount(iso);
          }}
          return total;
        }}

        function computeWeekdayDowSalesTotal(y, m0, dow) {{
          var year = Number(y);
          var month = Number(m0);
          var weekday = Number(dow);
          if (!Number.isFinite(year) || !Number.isFinite(month) || month < 0 || month > 11) return 0;
          if (!Number.isFinite(weekday) || weekday < 0 || weekday > 6) return 0;
          var dc = new Date(year, month + 1, 0).getDate();
          var total = 0;
          for (var day = 1; day <= dc; day++) {{
            if (!isCalendarBusinessDay(year, month, day)) continue;
            var dt = new Date(year, month, day);
            if (dt.getDay() !== weekday) continue;
            var iso = year + '-' + pad2(month + 1) + '-' + pad2(day);
            total += readTimelineSalesAmount(iso);
          }}
          return total;
        }}

        function computeWeekdayShareForYear(y, m0, dow) {{
          var monthSales = computeWeekdayMonthSalesTotal(y, m0);
          if (!(monthSales > 0)) return null;
          var dowSales = computeWeekdayDowSalesTotal(y, m0, dow);
          return dowSales / monthSales;
        }}

        function computeWeekdayShareAvgUncached(operatingYear, m0, dow, baselineYears) {{
          var oy = Number(operatingYear);
          var month = Number(m0);
          var weekday = Number(dow);
          if (!Number.isFinite(oy) || !Number.isFinite(month) || month < 0 || month > 11) return null;
          if (!Number.isFinite(weekday) || weekday < 0 || weekday > 6) return null;
          var years = normalizeWeekdayBaselineYears(
            baselineYears || readWeekdayBaselineYears(oy),
            oy
          );
          if (!years.length) return WEEKDAY_SHARE_FALLBACK;
          var sum = 0;
          var n = 0;
          years.forEach(function (y) {{
            var share = computeWeekdayShareForYear(y, month, weekday);
            if (share == null || !Number.isFinite(share)) return;
            sum += share;
            n++;
          }});
          if (!n) return WEEKDAY_SHARE_FALLBACK;
          return sum / n;
        }}

        function weekdayShareMatrixCacheKey(oy, baselineYears) {{
          var yrs = (baselineYears || readWeekdayBaselineYears(oy)).join(',');
          return oy + ':' + yrs;
        }}

        function getWeekdayShareMatrixCached(operatingYear, baselineYears) {{
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy)) return null;
          var key = weekdayShareMatrixCacheKey(oy, baselineYears);
          if (__weekdayShareMatrixCache[key]) return __weekdayShareMatrixCache[key];
          var matrix = computeWeekdayShareMatrix(oy, baselineYears);
          __weekdayShareMatrixCache[key] = matrix;
          return matrix;
        }}

        function computeWeekdayShareAvg(operatingYear, m0, dow, baselineYears) {{
          var oy = Number(operatingYear);
          var month = Number(m0);
          var weekday = Number(dow);
          if (!Number.isFinite(oy) || !Number.isFinite(month) || month < 0 || month > 11) return null;
          if (!Number.isFinite(weekday) || weekday < 0 || weekday > 6) return null;
          var matrix = getWeekdayShareMatrixCached(oy, baselineYears);
          if (!matrix || !matrix.months || !matrix.months[month]) return WEEKDAY_SHARE_FALLBACK;
          var share = matrix.months[month][weekday];
          return share == null || !Number.isFinite(share) ? WEEKDAY_SHARE_FALLBACK : share;
        }}

        function countOperatingWeekdaysInMonth(year, m0, dow) {{
          var y = Number(year);
          var month = Number(m0);
          var weekday = Number(dow);
          if (!Number.isFinite(y) || !Number.isFinite(month) || month < 0 || month > 11) return 0;
          if (!Number.isFinite(weekday) || weekday < 0 || weekday > 6) return 0;
          var dc = new Date(y, month + 1, 0).getDate();
          var count = 0;
          for (var day = 1; day <= dc; day++) {{
            if (!isCalendarBusinessDay(y, month, day)) continue;
            var dt = new Date(y, month, day);
            if (dt.getDay() !== weekday) continue;
            count++;
          }}
          return count;
        }}

        function computePlanMonthlyTargets(year) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return null;
          if (__planMonthlyTargetsCache[y]) return __planMonthlyTargetsCache[y];
          var annualTarget = readAnnualTarget(y);
          if (annualTarget == null || !Number.isFinite(Number(annualTarget)) || Number(annualTarget) <= 0) {{
            return null;
          }}
          var weights = readMonthlyHlWeights(y);
          if (!weights || weights.length !== 12) weights = DEFAULT_HL_WEIGHTS.slice();
          var monthlyBD = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          var totalBD = 0;
          for (var m0 = 0; m0 < 12; m0++) {{
            var dc = new Date(y, m0 + 1, 0).getDate();
            for (var day = 1; day <= dc; day++) {{
              if (!isCalendarBusinessDay(y, m0, day)) continue;
              monthlyBD[m0]++;
              totalBD++;
            }}
          }}
          if (totalBD <= 0) return null;
          var monthlyTargets = [];
          for (var mi = 0; mi < 12; mi++) {{
            var hl = Number(weights[mi]);
            if (!Number.isFinite(hl)) hl = 100;
            var bdCount = monthlyBD[mi];
            if (bdCount <= 0) {{
              monthlyTargets.push(0);
              continue;
            }}
            var monthlyAvg = (Number(annualTarget) * bdCount) / totalBD;
            monthlyTargets.push((monthlyAvg * hl) / 100);
          }}
          var plan = {{
            year: y,
            annualTarget: Number(annualTarget),
            weights: weights.slice(),
            monthlyBD: monthlyBD.slice(),
            totalBD: totalBD,
            monthlyTargets: monthlyTargets,
          }};
          __planMonthlyTargetsCache[y] = plan;
          return plan;
        }}

        function computeWeekdayShareMatrix(operatingYear, baselineYears) {{
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy)) return null;
          var years = normalizeWeekdayBaselineYears(
            baselineYears || readWeekdayBaselineYears(oy),
            oy
          );
          var months = [];
          var fallbackMonths = [];
          for (var m0 = 0; m0 < 12; m0++) {{
            var row = [];
            var usedFallback = false;
            for (var dow = 0; dow < 7; dow++) {{
              var share = computeWeekdayShareAvgUncached(oy, m0, dow, years);
              if (share == null || !Number.isFinite(share)) {{
                share = WEEKDAY_SHARE_FALLBACK;
                usedFallback = true;
              }}
              row.push(share);
            }}
            months.push(row);
            if (usedFallback) fallbackMonths.push(m0);
          }}
          return {{
            year: oy,
            baselineYears: years.slice(),
            months: months,
            fallbackMonths: fallbackMonths,
          }};
        }}

        function computeDailyKpiByMonthDow(operatingYear, m0, dow, baselineYears) {{
          var oy = Number(operatingYear);
          var month = Number(m0);
          var weekday = Number(dow);
          if (!Number.isFinite(oy) || !Number.isFinite(month) || month < 0 || month > 11) return null;
          if (!Number.isFinite(weekday) || weekday < 0 || weekday > 6) return null;
          var plan = computePlanMonthlyTargets(oy);
          if (!plan) return null;
          var monthlyTarget = plan.monthlyTargets[month];
          if (!(monthlyTarget > 0)) return 0;
          var shareAvg = computeWeekdayShareAvg(oy, month, weekday, baselineYears);
          if (shareAvg == null || !Number.isFinite(shareAvg)) return null;
          var count = countOperatingWeekdaysInMonth(oy, month, weekday);
          if (count <= 0) return 0;
          return (monthlyTarget * shareAvg) / count;
        }}

        function computeDailyTargetByIso(operatingYear, iso, baselineYears) {{
          if (!validIso(iso)) return null;
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy)) return null;
          var y = isoYear(iso);
          if (y !== oy) return null;
          var parts = iso.split('-');
          var m0 = Number(parts[1]) - 1;
          var day = Number(parts[2]);
          if (!Number.isFinite(m0) || !Number.isFinite(day)) return null;
          if (!isCalendarBusinessDay(y, m0, day)) return 0;
          var dt = new Date(y, m0, day);
          return computeDailyKpiByMonthDow(oy, m0, dt.getDay(), baselineYears);
        }}

        var DAILY_TARGET_MODE_FLAT = 'monthly-flat';
        var DAILY_TARGET_MODE_WEEKDAY = 'weekday-weighted';
        var DAILY_TARGET_MODE_DEFAULT = DAILY_TARGET_MODE_WEEKDAY;

        function normalizeDailyTargetMode(mode) {{
          var m = String(mode || '');
          if (m === DAILY_TARGET_MODE_FLAT || m === DAILY_TARGET_MODE_WEEKDAY) return m;
          return DAILY_TARGET_MODE_DEFAULT;
        }}

        function readDailyTargetMode(year) {{
          var y = Number(year);
          if (!Number.isFinite(y)) {{
            return normalizeDailyTargetMode(null);
          }}
          var rec = store.years[y];
          if (rec && rec.plan && rec.plan.dailyTargetMode) {{
            return normalizeDailyTargetMode(rec.plan.dailyTargetMode);
          }}
          return DAILY_TARGET_MODE_DEFAULT;
        }}

        function writeDailyTargetMode(year, mode, meta) {{
          var y = Number(year);
          if (!Number.isFinite(y)) return false;
          var next = normalizeDailyTargetMode(mode);
          var rec = ensureYearRecord(y);
          if (!rec.plan) rec.plan = {{}};
          if (rec.plan.dailyTargetMode === next) return true;
          rec.plan.dailyTargetMode = next;
          rec.plan.dailyTargetModeUpdatedAt = Date.now();
          rec.plan.dailyTargetModeSource = (meta && meta.source) || 'kpi-year-store';
          clearDailyTargetDisplayCache();
          scheduleServerYearRebuild(y, 'daily-target-mode', {{
            dailyTargetMode: next,
            source: rec.plan.dailyTargetModeSource,
          }});
          document.dispatchEvent(
            new CustomEvent('kpi:dailyTargetModeChanged', {{
              detail: {{
                year: y,
                dailyTargetMode: next,
                source: rec.plan.dailyTargetModeSource,
              }},
            }})
          );
          return true;
        }}

        function weekdayTargetDataReady(operatingYear) {{
          var years = readWeekdayBaselineYears(operatingYear);
          return years && years.length > 0;
        }}

        function assessWeekdayTargetQuality(operatingYear) {{
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy)) return null;
          var mode = readDailyTargetMode(oy);
          var dataReady = weekdayTargetDataReady(oy);
          var usingFlatFallback = mode === DAILY_TARGET_MODE_WEEKDAY && !dataReady;
          var matrix = null;
          if (mode === DAILY_TARGET_MODE_WEEKDAY && dataReady) {{
            matrix = computeWeekdayShareMatrix(oy);
          }}
          var fallbackMonths =
            matrix && matrix.fallbackMonths ? matrix.fallbackMonths.slice() : [];
          return {{
            year: oy,
            mode: mode,
            dataReady: dataReady,
            usingFlatFallback: usingFlatFallback,
            fallbackMonths: fallbackMonths,
            baselineYears: matrix ? matrix.baselineYears.slice() : readWeekdayBaselineYears(oy).slice(),
          }};
        }}

        function computeFlatDailyTargetByIso(operatingYear, iso) {{
          if (!validIso(iso)) return null;
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy)) return null;
          var y = isoYear(iso);
          if (y !== oy) return null;
          var parts = iso.split('-');
          var m0 = Number(parts[1]) - 1;
          var day = Number(parts[2]);
          if (!Number.isFinite(m0) || !Number.isFinite(day)) return null;
          if (!isCalendarBusinessDay(y, m0, day)) return 0;
          var plan = computePlanMonthlyTargets(oy);
          if (!plan) return null;
          var bdCount = plan.monthlyBD[m0];
          if (!(bdCount > 0)) return 0;
          var monthlyTarget = plan.monthlyTargets[m0];
          if (!(monthlyTarget > 0)) return 0;
          return monthlyTarget / bdCount;
        }}

        /* KPI-WEEKDAY-TARGET-DISPLAY-11-6 */
        var __dailyTargetDisplayCache = {{}};

        function clearDailyTargetDisplayCache() {{
          __dailyTargetDisplayCache = {{}};
          __planMonthlyTargetsCache = {{}};
          __weekdayShareMatrixCache = {{}};
          __yearHasPositiveSalesCache = {{}};
        }}

        function dailyTargetDisplayCacheKey(oy, m0, mode, effectiveMode, fallback, monthlyTarget, baselineYears) {{
          var yrs = (baselineYears || readWeekdayBaselineYears(oy)).join(',');
          return (
            oy +
            ':' +
            m0 +
            ':' +
            mode +
            ':' +
            effectiveMode +
            ':' +
            (fallback ? '1' : '0') +
            ':' +
            Math.round(Number(monthlyTarget) || 0) +
            ':' +
            yrs
          );
        }}

        function resolveDailyTargetRawByIso(operatingYear, iso, opts) {{
          opts = opts || {{}};
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy) || !validIso(iso)) {{
            return {{ value: null, mode: null, effectiveMode: null, fallback: false }};
          }}
          var mode = normalizeDailyTargetMode(
            opts.dailyTargetMode != null ? opts.dailyTargetMode : readDailyTargetMode(oy)
          );
          var effectiveMode = mode;
          var fallback = false;
          var value = null;
          if (mode === DAILY_TARGET_MODE_WEEKDAY) {{
            if (weekdayTargetDataReady(oy)) {{
              value = computeDailyTargetByIso(oy, iso, opts.baselineYears);
            }}
            if (value == null || !Number.isFinite(value)) {{
              effectiveMode = DAILY_TARGET_MODE_FLAT;
              fallback = true;
              value = computeFlatDailyTargetByIso(oy, iso);
            }}
          }} else {{
            value = computeFlatDailyTargetByIso(oy, iso);
          }}
          return {{
            value: value,
            mode: mode,
            effectiveMode: effectiveMode,
            fallback: fallback,
          }};
        }}

        function buildDailyTargetDisplayMapForMonth(operatingYear, m0, opts) {{
          opts = opts || {{}};
          var oy = Number(operatingYear);
          var month = Number(m0);
          if (!Number.isFinite(oy) || !Number.isFinite(month) || month < 0 || month > 11) return {{}};
          var plan = computePlanMonthlyTargets(oy);
          if (!plan) return {{}};
          var monthlyTarget = plan.monthlyTargets[month];
          if (!(monthlyTarget > 0)) return {{}};

          var mode = normalizeDailyTargetMode(
            opts.dailyTargetMode != null ? opts.dailyTargetMode : readDailyTargetMode(oy)
          );
          var baselineYears = opts.baselineYears;
          var effectiveMode = mode;
          var fallback = false;
          if (mode === DAILY_TARGET_MODE_WEEKDAY && !weekdayTargetDataReady(oy)) {{
            effectiveMode = DAILY_TARGET_MODE_FLAT;
            fallback = true;
          }}

          var cacheKey = dailyTargetDisplayCacheKey(
            oy,
            month,
            mode,
            effectiveMode,
            fallback,
            monthlyTarget,
            baselineYears
          );
          if (__dailyTargetDisplayCache[cacheKey]) return __dailyTargetDisplayCache[cacheKey];

          var rows = [];
          var dc = new Date(oy, month + 1, 0).getDate();
          for (var day = 1; day <= dc; day++) {{
            if (!isCalendarBusinessDay(oy, month, day)) continue;
            var iso = oy + '-' + pad2(month + 1) + '-' + pad2(day);
            var rawResult = resolveDailyTargetRawByIso(oy, iso, opts);
            var raw = rawResult.value;
            if (raw == null || !Number.isFinite(raw)) raw = 0;
            rows.push({{ iso: iso, raw: raw }});
          }}

          var targetSum = Math.round(Number(monthlyTarget));
          var sumRounded = 0;
          var map = {{}};
          for (var i = 0; i < rows.length; i++) {{
            var row = rows[i];
            var display;
            var adjusted = false;
            if (i === rows.length - 1) {{
              display = targetSum - sumRounded;
              adjusted = display !== Math.round(row.raw);
            }} else {{
              display = Math.round(row.raw);
              sumRounded += display;
            }}
            map[row.iso] = {{
              value: display,
              rawValue: row.raw,
              adjusted: adjusted,
            }};
          }}
          __dailyTargetDisplayCache[cacheKey] = map;
          return map;
        }}

        function buildDailyTargetDisplayMapForYear(operatingYear, opts) {{
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy)) return {{}};
          var out = {{}};
          for (var mi = 0; mi < 12; mi++) {{
            var monthMap = buildDailyTargetDisplayMapForMonth(oy, mi, opts);
            Object.keys(monthMap).forEach(function (iso) {{
              out[iso] = monthMap[iso].value;
            }});
          }}
          return out;
        }}

        function resolveDailyTargetByIso(operatingYear, iso, opts) {{
          opts = opts || {{}};
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy) || !validIso(iso)) {{
            return {{
              value: null,
              rawValue: null,
              adjusted: false,
              mode: null,
              effectiveMode: null,
              fallback: false,
            }};
          }}
          var rawResult = resolveDailyTargetRawByIso(oy, iso, opts);
          var parts = iso.split('-');
          var m0 = Number(parts[1]) - 1;
          var day = Number(parts[2]);
          if (!Number.isFinite(m0) || !Number.isFinite(day) || !isCalendarBusinessDay(oy, m0, day)) {{
            return {{
              value: rawResult.value,
              rawValue: rawResult.value,
              adjusted: false,
              mode: rawResult.mode,
              effectiveMode: rawResult.effectiveMode,
              fallback: rawResult.fallback,
            }};
          }}
          var monthMap = buildDailyTargetDisplayMapForMonth(oy, m0, opts);
          var entry = monthMap[iso];
          if (!entry) {{
            var rounded =
              rawResult.value != null && Number.isFinite(rawResult.value)
                ? Math.round(rawResult.value)
                : rawResult.value;
            return {{
              value: rounded,
              rawValue: rawResult.value,
              adjusted: false,
              mode: rawResult.mode,
              effectiveMode: rawResult.effectiveMode,
              fallback: rawResult.fallback,
            }};
          }}
          return {{
            value: entry.value,
            rawValue: entry.rawValue,
            adjusted: entry.adjusted,
            mode: rawResult.mode,
            effectiveMode: rawResult.effectiveMode,
            fallback: rawResult.fallback,
          }};
        }}
"""
