"""Focus Bar Graph popover — Store + TW metrics (Phase 9)."""

from __future__ import annotations

GRAPH_STORE_MARKER = "/* KPI-FOCUS-BAR-GRAPH-STORE */"

STR_JA_OLD = """      var STR = isJa
        ? {
            titles: { daily: '日次グラフ', monthly: '月次グラフ', annual: '年次グラフ' },
            drop: { daily: '▼ 日次', monthly: '▼ 月次', annual: '▼ 年次' },
            date: '日付 :',
            ach: '達成率 :',
            target: '目標売上 :',
            actual: '実績売上 :',
            diff: '差額 :',
            close: '閉じる',
            editTargetPrompt: '目標売上を入力（数値のみ）',
            editActualPrompt: '実績売上を入力（数値のみ）',
            invalidNumber: '数値を入力してください。'
          }"""

STR_JA_NEW = f"""      var STR = isJa
        ? {{
            titles: {{ daily: '日次グラフ', monthly: '月次グラフ', annual: '年次グラフ' }},
            drop: {{ daily: '▼ 日次', monthly: '▼ 月次', annual: '▼ 年次' }},
            labels: {{
              daily: {{ target: '本日目標売上 :', actual: '本日売上 :' }},
              monthly: {{ target: '月次累計目標売上 :', actual: '月次累計実績売上 :' }},
              annual: {{ target: '年次累計目標売上 :', actual: '年次累計実績売上 :' }},
            }},
            date: '日付 :',
            ach: '達成率 :',
            diff: '差額 :',
            close: '閉じる',
          }}"""

STR_EN_TAIL_OLD = """        : {
            titles: { daily: 'Daily Graph', monthly: 'Monthly Graph', annual: 'Annual Graph' },
            drop: { daily: '▼ Daily', monthly: '▼ Monthly', annual: '▼ Annual' },
            date: 'Date :',
            ach: 'Achievement :',
            target: 'Target Sales :',
            actual: 'Actual Sales :',
            diff: 'Difference :',
            close: 'Close',
            editTargetPrompt: 'Enter target sales (number only)',
            editActualPrompt: 'Enter actual sales (number only)',
            invalidNumber: 'Please enter a valid number.'
          };"""

STR_EN_TAIL_NEW = """        : {
            titles: { daily: 'Daily Graph', monthly: 'Monthly Graph', annual: 'Annual Graph' },
            drop: { daily: '▼ Daily', monthly: '▼ Monthly', annual: '▼ Annual' },
            labels: {
              daily: { target: "Today's Target Sales :", actual: "Today's Sales :" },
              monthly: { target: 'Cumulative Target Sales :', actual: 'Cumulative Actual Sales :' },
              annual: { target: 'Cumulative Target Sales :', actual: 'Cumulative Actual Sales :' },
            },
            date: 'Date :',
            ach: 'Achievement :',
            diff: 'Difference :',
            close: 'Close',
          };"""

MANUAL_VARS_OLD = """      var mode = 'daily';
      var manualByMode = {
        daily: { target: NaN, sales: NaN },
        monthly: { target: NaN, sales: NaN },
        annual: { target: NaN, sales: NaN }
      };
      var lastComputed = { target: NaN, sales: NaN };

      function fmtMoney(n) {"""

MANUAL_VARS_NEW = """      var mode = 'daily';

      function fmtMoney(n) {"""

GRAPH_FMT_OLD = """      var mode = 'daily';

      function fmtMoney(n) {
        if (n == null || !isFinite(Number(n))) return '—';
        var v = Math.round(Number(n));
        if (isJa) return '¥' + v.toLocaleString('ja-JP');
        return '$' + v.toLocaleString('en-US');
      }"""

GRAPH_FMT_NEW = """      var mode = 'daily';

      function fmtMoney(n) {
        if (typeof window.__twFmtMoney === 'function') return window.__twFmtMoney(n);
        if (n == null || !isFinite(Number(n))) return '—';
        var v = Math.round(Number(n));
        if (isJa) return '¥' + v.toLocaleString('ja-JP');
        return '$' + v.toLocaleString('en-US');
      }"""

TW_FMT_REVERT_OLD = f"""      {GRAPH_STORE_MARKER}
      function fmtMoney(n) {{
        if (typeof window.__twFmtMoney === 'function') return window.__twFmtMoney(n);
        if (n == null || !isFinite(Number(n))) return '—';
        var v = Math.round(Number(n));
        if (isJa) return '¥' + v.toLocaleString('ja-JP');
        return '$' + v.toLocaleString('en-US');
      }}"""

TW_FMT_REVERT_NEW = """      function fmtMoney(n) {
        if (n == null || !isFinite(Number(n))) return '—';
        var v = Math.round(Number(n));
        if (isJa) return '¥' + v.toLocaleString('ja-JP');
        return '$' + v.toLocaleString('en-US');
      }"""

FORMAT_DIFF_OLD = """      function formatSignedDiff(n) {
        if (!isFinite(n)) return '—';
        var r = Math.round(Math.abs(n));
        if (isJa) return (n >= 0 ? '+' : '−') + '¥' + r.toLocaleString('ja-JP');
        return (n >= 0 ? '+' : '−') + '$' + r.toLocaleString('en-US');
      }"""

FORMAT_DIFF_NEW = """      function formatSignedDiff(n) {
        if (typeof window.__twFmtDiff === 'function') {
          var target = 0;
          return window.__twFmtDiff(n + target, target);
        }
        if (!isFinite(n)) return '—';
        var r = Math.round(Math.abs(n));
        if (isJa) return (n >= 0 ? '+' : '−') + '¥' + r.toLocaleString('ja-JP');
        return (n >= 0 ? '+' : '−') + '$' + r.toLocaleString('en-US');
      }"""

PARSE_BLOCK_OLD = """      function parseMoneyText(s) {
        if (s == null) return NaN;
        var t = String(s).trim();
        if (t === '' || t === '—' || t === '-') return NaN;
        var n = parseFloat(t.replace(/[¥$,\s]/g, ''));
        return n;
      }

      function parseAchText(s) {
        if (s == null) return NaN;
        var t = String(s).trim();
        if (t === '' || t === '—' || t === '-') return NaN;
        return parseFloat(t.replace('%', ''));
      }

      function parseEditableMoneyInput(input) {
        if (input == null) return null;
        var t = String(input).trim();
        if (t === '') return NaN;
        var n = parseFloat(t.replace(/[¥$,\s]/g, ''));
        if (!isFinite(n) || n < 0) return undefined;
        return n;
      }

      function parseRowGroup(row, groupSel, order) {
        var g = row && row.querySelector(groupSel);
        if (!g) return { sales: NaN, target: NaN, diff: NaN, ach: NaN };
        var cells = g.querySelectorAll('.annual-daily-row__cell');
        if (!cells.length) return { sales: NaN, target: NaN, diff: NaN, ach: NaN };
        if (order === 'daily') {
          return {
            sales: parseMoneyText(cells[1] && cells[1].textContent),
            target: parseMoneyText(cells[2] && cells[2].textContent),
            diff: parseMoneyText(cells[3] && cells[3].textContent),
            ach: parseAchText(cells[4] && cells[4].textContent)
          };
        }
        return {
          sales: parseMoneyText(cells[1] && cells[1].textContent),
          target: parseMoneyText(cells[0] && cells[0].textContent),
          diff: parseMoneyText(cells[2] && cells[2].textContent),
          ach: parseAchText(cells[3] && cells[3].textContent)
        };
      }

      function getFocusedRow() {"""

PARSE_BLOCK_NEW = """      function resolveGraphFocusedIso(row) {
        if (row) {
          var isoAttr = row.getAttribute('data-iso-date');
          if (isoAttr && String(isoAttr).trim()) return String(isoAttr).trim();
        }
        if (typeof monthlyGraphBtn !== 'undefined' && monthlyGraphBtn && window.__MONTHLY_UI && typeof window.__MONTHLY_UI.getFocusedIsoDate === 'function') {
          var isoMonthly = window.__MONTHLY_UI.getFocusedIsoDate();
          if (isoMonthly) return isoMonthly;
        }
        if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily && window.__ANNUAL_DATA.daily.selectedDate) {
          return window.__ANNUAL_DATA.daily.selectedDate;
        }
        return null;
      }

      function graphMetricsForMode(m, graphMode) {
        if (!m) return null;
        if (graphMode === 'daily') {
          if (!m.isBusinessToday) {
            return { sales: NaN, target: NaN, hasData: false };
          }
          var dt = m.dailyTarget;
          var hasDailyPlan = dt != null && Number.isFinite(Number(dt)) && Number(dt) > 0;
          return {
            sales: Number(m.dailySales),
            target: hasDailyPlan ? Number(dt) : NaN,
            hasData: hasDailyPlan && Number.isFinite(Number(m.dailySales)),
          };
        }
        if (graphMode === 'monthly') {
          return {
            sales: Number(m.mtdA),
            target: Number(m.mtdT),
            hasData: m.hasPlan && Number.isFinite(Number(m.mtdT)) && Number(m.mtdT) > 0,
          };
        }
        return {
          sales: Number(m.ytdA),
          target: Number(m.ytdT),
          hasData: m.hasPlan && Number.isFinite(Number(m.ytdT)) && Number(m.ytdT) > 0,
        };
      }

      function getFocusedRow() {"""

REFRESH_GRAPH_OLD = """      function refreshGraphContent() {
        var row = getFocusedRow();
        panel.classList.remove('annual-graph-popover--win', 'annual-graph-popover--lose', 'annual-graph-popover--neutral');
        if (!row) {
          panel.classList.add('annual-graph-popover--neutral');
          valDate.textContent = '—';
          valAch.textContent = '0%';
          valTarget.textContent = '—';
          valActual.textContent = '—';
          lastComputed.target = NaN;
          lastComputed.sales = NaN;
          valDiff.textContent = '—';
          setGraphBarFromAchievementPercent(NaN);
          return;
        }

        var g =
          mode === 'daily'
            ? parseRowGroup(row, '.annual-daily-row__group--base', 'daily')
            : mode === 'monthly'
              ? parseRowGroup(row, '.annual-daily-row__group--monthly', 'monthly')
              : parseRowGroup(row, '.annual-daily-row__group--annual', 'annual');
        valDate.textContent = getFocusedDateText(row);

        var target = g.target;
        var sales = g.sales;
        var manual = manualByMode[mode] || { target: NaN, sales: NaN };
        if (isFinite(manual.target)) target = manual.target;
        if (isFinite(manual.sales)) sales = manual.sales;
        var hasData = isFinite(target) && isFinite(sales) && target >= 0 && sales >= 0;

        if (!hasData) {
          panel.classList.add('annual-graph-popover--neutral');
          var achFallback = Number(g.ach);
          if (!Number.isFinite(achFallback)) achFallback = 0;
          valAch.textContent = formatAchPercent(achFallback);
          valTarget.textContent = isFinite(target) ? fmtMoney(target) : '—';
          valActual.textContent = isFinite(sales) ? fmtMoney(sales) : '—';
          valDiff.textContent = formatSignedDiff(g.diff);
          lastComputed.target = target;
          lastComputed.sales = sales;
          setGraphBarFromAchievementPercent(achFallback);
          return;
        }

        var diff = sales - target;
        var achValue;
        if (target > 0) {
          achValue = (sales / target) * 100;
        } else if (sales > 0) {
          achValue = 0;
        } else {
          achValue = 0;
        }
        setGraphBarFromAchievementPercent(achValue);

        var win = diff >= 0;

        panel.classList.add(win ? 'annual-graph-popover--win' : 'annual-graph-popover--lose');

        valAch.textContent = formatAchPercent(achValue);
        valTarget.textContent = fmtMoney(target);
        valActual.textContent = fmtMoney(sales);
        valDiff.textContent = formatSignedDiff(diff);
        lastComputed.target = target;
        lastComputed.sales = sales;
      }"""

REFRESH_GRAPH_NEW = """      function graphTwDiffLevels() {
        return (
          window.__twDiffLevels || [
            'tw-diff--win',
            'tw-diff--neutral',
            'tw-diff--sev-90',
            'tw-diff--sev-80',
            'tw-diff--sev-70',
            'tw-diff--sev-60',
            'tw-diff--sev-50',
            'tw-diff--sev-below',
          ]
        );
      }

      function clearGraphTwDiffClass(el) {
        if (!el) return;
        graphTwDiffLevels().forEach(function (cls) {
          el.classList.remove(cls);
        });
      }

      function applyGraphTwDiffClass(el, actual, target) {
        clearGraphTwDiffClass(el);
        if (!el || typeof window.__twDiffSeverityClass !== 'function') return;
        if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) return;
        el.classList.add(window.__twDiffSeverityClass(actual, target));
      }

      function setGraphDiffText(actual, target) {
        if (typeof window.__twFmtDiff === 'function') {
          return window.__twFmtDiff(actual, target);
        }
        return formatSignedDiff(actual - target);
      }

      function refreshGraphContent() {
        var row = getFocusedRow();
        var iso = resolveGraphFocusedIso(row);
        panel.classList.remove('annual-graph-popover--win', 'annual-graph-popover--lose', 'annual-graph-popover--neutral');

        if (!iso) {
          panel.classList.add('annual-graph-popover--neutral');
          valDate.textContent = '—';
          valAch.textContent = '—';
          valTarget.textContent = '—';
          valActual.textContent = '—';
          valDiff.textContent = '—';
          clearGraphTwDiffClass(valDiff);
          setGraphBarFromAchievementPercent(NaN);
          return;
        }

        var compute =
          typeof window.__computeTwMetricsForIso === 'function'
            ? window.__computeTwMetricsForIso
            : null;
        var m = compute ? compute(iso) : null;
        var g = graphMetricsForMode(m, mode);

        valDate.textContent = row ? getFocusedDateText(row) : iso;

        if (!g || !g.hasData) {
          panel.classList.add('annual-graph-popover--neutral');
          valAch.textContent = '—';
          valTarget.textContent =
            g && Number.isFinite(g.target) ? fmtMoney(g.target) : '—';
          valActual.textContent =
            g && Number.isFinite(g.sales) ? fmtMoney(g.sales) : '—';
          valDiff.textContent = '—';
          clearGraphTwDiffClass(valDiff);
          setGraphBarFromAchievementPercent(NaN);
          return;
        }

        var target = g.target;
        var sales = g.sales;
        var diff = sales - target;
        var achValue = target > 0 ? (sales / target) * 100 : 0;
        setGraphBarFromAchievementPercent(achValue);
        panel.classList.add(diff >= 0 ? 'annual-graph-popover--win' : 'annual-graph-popover--lose');
        valAch.textContent = formatAchPercent(achValue);
        valTarget.textContent = fmtMoney(target);
        valActual.textContent = fmtMoney(sales);
        valDiff.textContent = setGraphDiffText(sales, target);
        applyGraphTwDiffClass(valDiff, sales, target);
      }"""

SYNC_LABELS_OLD = """      function syncLabels() {
        titleEl.textContent = STR.titles[mode] || STR.titles.daily;
        dropBtn.textContent = STR.drop[mode] || STR.drop.daily;
        lblDate.textContent = STR.date;
        lblAch.textContent = STR.ach;
        lblTarget.textContent = STR.target;
        lblActual.textContent = STR.actual;
        lblDiff.textContent = STR.diff;
        btnClose.setAttribute('aria-label', STR.close);
      }"""

SYNC_LABELS_NEW = """      function syncLabels() {
        var lbl = (STR.labels && STR.labels[mode]) || (STR.labels && STR.labels.daily) || {};
        titleEl.textContent = STR.titles[mode] || STR.titles.daily;
        dropBtn.textContent = STR.drop[mode] || STR.drop.daily;
        lblDate.textContent = STR.date;
        lblAch.textContent = STR.ach;
        lblTarget.textContent = lbl.target || '—';
        lblActual.textContent = lbl.actual || '—';
        lblDiff.textContent = STR.diff;
        btnClose.setAttribute('aria-label', STR.close);
      }"""

PROMPT_EDIT_BLOCK = """      function promptMoneyEdit(kind) {
        var manual = manualByMode[mode] || (manualByMode[mode] = { target: NaN, sales: NaN });
        var current = kind === 'target' ? manual.target : manual.sales;
        if (!isFinite(current)) current = kind === 'target' ? lastComputed.target : lastComputed.sales;
        var promptText = kind === 'target' ? STR.editTargetPrompt : STR.editActualPrompt;
        var input = window.prompt(promptText, isFinite(current) ? String(Math.round(current)) : '');
        var parsed = parseEditableMoneyInput(input);
        if (parsed === null) return;
        if (parsed === undefined) {
          window.alert(STR.invalidNumber);
          return;
        }
        if (isNaN(parsed)) {
          manual[kind] = NaN;
        } else {
          manual[kind] = parsed;
        }
        refreshGraphContent();
      }

      valTarget.addEventListener('click', function (ev) {
        ev.stopPropagation();
        promptMoneyEdit('target');
      });
      valActual.addEventListener('click', function (ev) {
        ev.stopPropagation();
        promptMoneyEdit('sales');
      });

"""

STORE_LISTENERS_ANCHOR = """      window.addEventListener(
        'resize',
        function () {
          if (!root.hidden) positionPanel();
        },
        { passive: true }
      );

      syncLabels();
    })();
  </script>
  <script>
    (function () {
      var modal = document.getElementById('annual-edit-modal');"""

STORE_LISTENERS_NEW = """      window.addEventListener(
        'resize',
        function () {
          if (!root.hidden) positionPanel();
        },
        { passive: true }
      );

      function refreshGraphPopoverFromStore() {
        if (!root.hidden) refreshGraphContent();
      }
      document.addEventListener('kpi:dailySalesChanged', refreshGraphPopoverFromStore);
      document.addEventListener('kpi:businessDayChanged', refreshGraphPopoverFromStore);
      document.addEventListener('kpi:annualPlanChanged', refreshGraphPopoverFromStore);
      document.addEventListener('annual:salesMapChanged', refreshGraphPopoverFromStore);
      document.addEventListener('annual:salesDataSaved', refreshGraphPopoverFromStore);
      document.addEventListener('annual:pastSalesSaved', refreshGraphPopoverFromStore);
      document.addEventListener('kpi:readSurfacesRefresh', refreshGraphPopoverFromStore);
      document.addEventListener('annual:timelineRowsRendered', refreshGraphPopoverFromStore);
      document.addEventListener('kpi:dailyTargetModeChanged', refreshGraphPopoverFromStore);
      document.addEventListener('kpi:weekdayBaselineChanged', refreshGraphPopoverFromStore);

      syncLabels();
    })();
  </script>
  <script>
    (function () {
      var modal = document.getElementById('annual-edit-modal');"""

EDITABLE_HTML_OLD = 'annual-graph-popover__value annual-graph-popover__value--editable'
EDITABLE_HTML_NEW = 'annual-graph-popover__value'
