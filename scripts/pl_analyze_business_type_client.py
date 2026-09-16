"""PL Analyze — Business Type layout adapter (Unit 5B-3).

Inserted after pl_analyze_client_js() inside the main PL IIFE.
Does not change restaurant fill maps in pl_analyze_client.py.

Non-restaurant layouts are driven by KpiPlExpensePresets.getAnalysisMetrics().
"""

from __future__ import annotations

JS_BEGIN = "      /* === UNIT-5B-3-ANALYZE-BT-BEGIN === */"
JS_END = "      /* === UNIT-5B-3-ANALYZE-BT-END === */"
CSS_BEGIN = "    /* === UNIT-5B-3-ANALYZE-R2-BEGIN === */"
CSS_END = "    /* === UNIT-5B-3-ANALYZE-R2-END === */"


def pl_analyze_business_type_css() -> str:
    return f"""{CSS_BEGIN}
    .pl-v-major--analyze.pl-v-major--r2 {{
      height: calc(var(--pl-row-label-h) * 2);
      min-height: calc(var(--pl-row-label-h) * 2);
      max-height: calc(var(--pl-row-label-h) * 2);
    }}
{CSS_END}
"""


def pl_analyze_business_type_client_js() -> str:
    return rf"""
{JS_BEGIN}
      (function () {{
        var restaurantRefresh = refreshAnalyzeBlock;
        var restaurantLabelHtml = null;
        var restaurantDataHtml = null;
        var renderedMode = null;
        var renderedSig = null;

        function plAnalyzeEsc(s) {{
          return String(s || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
        }}

        function plAnalyzePageLang() {{
          var lang = '';
          try {{
            lang = String(
              document.documentElement.getAttribute('lang') || ''
            ).toLowerCase();
          }} catch (_e) {{}}
          if (lang.indexOf('zh') === 0) return 'zh';
          if (lang.indexOf('en') === 0) return 'en';
          return 'ja';
        }}

        function plAnalyzeEditAria() {{
          var lang = plAnalyzePageLang();
          if (lang === 'zh') return '編輯科目名稱（雙擊或 F2）';
          if (lang === 'en') return 'Edit label (double-click or F2)';
          return 'ラベルを編集（ダブルクリックまたは F2）';
        }}

        function plAnalyzeReadMetrics() {{
          var api = window.KpiPlExpensePresets;
          if (api && typeof api.getAnalysisMetrics === 'function') {{
            try {{
              return api.getAnalysisMetrics();
            }} catch (_e) {{}}
          }}
          return {{ mode: 'restaurant_fl', groups: [] }};
        }}

        function plAnalyzeIsRestaurant() {{
          var metrics = plAnalyzeReadMetrics();
          return !metrics || metrics.mode !== 'key_expenses';
        }}

        function plAnalyzeMetricsSignature(metrics) {{
          var rec = metrics || plAnalyzeReadMetrics();
          var parts = [String(rec.mode || '')];
          (rec.groups || []).forEach(function (group) {{
            parts.push(String(group.id || ''));
            (group.rows || []).forEach(function (row) {{
              parts.push(String(row.id || ''));
            }});
          }});
          return parts.join('|');
        }}

        function plAnalyzeSnapshotRestaurant() {{
          if (restaurantLabelHtml != null) return;
          var labelBody = document.getElementById('pl-analyze-label-collapsible');
          var dataBody = document.getElementById('pl-analyze-data-collapsible');
          if (!labelBody || !dataBody) return;
          restaurantLabelHtml = labelBody.innerHTML;
          restaurantDataHtml = dataBody.innerHTML;
        }}

        function plAnalyzePickLabel(row, lang) {{
          if (lang === 'zh') return row.labelZh || row.labelJa || row.labelEn || '';
          if (lang === 'en') return row.labelEn || row.labelJa || '';
          return row.labelJa || row.labelEn || '';
        }}

        function plAnalyzePickMajor(group, lang) {{
          var lines =
            lang === 'zh'
              ? group.majorZh || group.majorJa
              : lang === 'en'
                ? group.majorEn || group.majorJa
                : group.majorJa || group.majorEn;
          if (!Array.isArray(lines) || !lines.length) return ['', ''];
          return lines;
        }}

        function plAnalyzeMajorHtml(group, lang) {{
          var lines = plAnalyzePickMajor(group, lang);
          var inner = '';
          for (var i = 0; i < lines.length; i++) {{
            inner +=
              '<span class="pl-v-major__line">' + plAnalyzeEsc(lines[i]) + '</span>';
          }}
          return (
            '<span class="pl-v-major__text pl-v-major__text--multiline">' +
            inner +
            '</span>'
          );
        }}

        function plAnalyzeMonthCells(rid) {{
          var html = '';
          var mi;
          for (mi = 0; mi < 12; mi++) {{
            html +=
              '<td class="pl-amt-cell pl-amt-cell--analyze" data-row="' +
              plAnalyzeEsc(rid) +
              '" data-month="' +
              mi +
              '" data-field="amount"><span class="pl-amt-cell__text"></span></td>' +
              '<td class="pl-ratio-cell pl-ratio-cell--analyze" data-row="' +
              plAnalyzeEsc(rid) +
              '" data-month="' +
              mi +
              '" data-field="ratio"><span class="pl-ratio-cell__text"></span></td>';
          }}
          html +=
            '<td class="pl-amt-cell pl-amt-cell--analyze pl-amt-cell--year-total" data-row="' +
            plAnalyzeEsc(rid) +
            '" data-month="year" data-field="amount"><span class="pl-amt-cell__text">—</span></td>' +
            '<td class="pl-ratio-cell pl-ratio-cell--analyze pl-ratio-cell--year-total" data-row="' +
            plAnalyzeEsc(rid) +
            '" data-month="year" data-field="ratio"><span class="pl-ratio-cell__text"></span></td>';
          return html;
        }}

        function plAnalyzeRenderKeyLayout() {{
          var metrics = plAnalyzeReadMetrics();
          var groups = metrics && metrics.groups ? metrics.groups : [];
          var lang = plAnalyzePageLang();
          var aria = plAnalyzeEsc(plAnalyzeEditAria());
          var labelHtml = '';
          var dataHtml = '';
          groups.forEach(function (group) {{
            var rows = group.rows || [];
            var n = rows.length;
            if (!n) return;
            var gid = plAnalyzeEsc(group.id || 'key_expenses');
            rows.forEach(function (row, i) {{
              var rid = plAnalyzeEsc(row.id || '');
              if (!rid) return;
              var isTotal = !!row.isTotal;
              var label = plAnalyzeEsc(plAnalyzePickLabel(row, lang));
              var majorTd = '';
              if (i === 0) {{
                majorTd =
                  '<td class="pl-v-major pl-v-major--analyze pl-v-major--r' +
                  n +
                  '" rowspan="' +
                  n +
                  '" data-pl-section="analyze" data-pl-group="' +
                  gid +
                  '">' +
                  plAnalyzeMajorHtml(group, lang) +
                  '</td>';
              }}
              var labelCls = 'pl-h-label';
              var labelInner;
              if (isTotal) {{
                labelCls += ' pl-h-label--total';
                labelInner = '<span class="pl-h-label__text">' + label + '</span>';
              }} else {{
                labelCls += ' pl-h-label--editable';
                labelInner =
                  '<span class="pl-h-label__row"><span class="pl-h-label__text pl-h-label__text--editable" data-pl-label-editable="1" data-label-id="' +
                  rid +
                  '" data-label-scope="analyze" tabindex="0" role="button" aria-label="' +
                  aria +
                  '">' +
                  label +
                  '</span></span>';
              }}
              var rowCls = 'pl-data-row pl-data-row--analyze pl-analyze-zone';
              if (isTotal) rowCls += ' pl-data-row--total';
              labelHtml +=
                '<tr class="' +
                rowCls +
                '" data-pl-section="analyze" data-pl-group="' +
                gid +
                '" data-row="' +
                rid +
                '">' +
                majorTd +
                '<th scope="row" class="' +
                labelCls +
                '">' +
                labelInner +
                '</th></tr>';
              dataHtml +=
                '<tr class="' +
                rowCls +
                '" data-row="' +
                rid +
                '" data-pl-section="analyze" data-pl-group="' +
                gid +
                '">' +
                plAnalyzeMonthCells(rid) +
                '</tr>';
            }});
          }});
          var labelBody = document.getElementById('pl-analyze-label-collapsible');
          var dataBody = document.getElementById('pl-analyze-data-collapsible');
          if (labelBody) labelBody.innerHTML = labelHtml;
          if (dataBody) dataBody.innerHTML = dataHtml;
        }}

        function plAnalyzeRestoreRestaurantLayout() {{
          var labelBody = document.getElementById('pl-analyze-label-collapsible');
          var dataBody = document.getElementById('pl-analyze-data-collapsible');
          if (labelBody && restaurantLabelHtml != null) {{
            labelBody.innerHTML = restaurantLabelHtml;
          }}
          if (dataBody && restaurantDataHtml != null) {{
            dataBody.innerHTML = restaurantDataHtml;
          }}
        }}

        function plAnalyzeLaborLineIds() {{
          var api = window.KpiPlExpensePresets;
          var attrs = {{}};
          var extraIds = ['exp_variable_labor', 'exp_fixed_labor'];
          var i;
          if (api && api.LABOR_ANALYSIS_ATTRIBUTES) {{
            (api.LABOR_ANALYSIS_ATTRIBUTES || []).forEach(function (a) {{
              attrs[a] = true;
            }});
          }} else {{
            attrs.salaries_wages = true;
            attrs.variable_labor = true;
            attrs.labor_related = true;
          }}
          if (api && api.LABOR_ANALYSIS_LINE_IDS) {{
            extraIds = api.LABOR_ANALYSIS_LINE_IDS.slice();
          }}
          var ids = [];
          var seen = {{}};
          function consider(line) {{
            if (!line || !line.lineId || line.active === false) return;
            var hit = !!attrs[line.expenseAttribute];
            if (!hit) {{
              for (i = 0; i < extraIds.length; i++) {{
                if (line.lineId === extraIds[i]) {{
                  hit = true;
                  break;
                }}
              }}
            }}
            if (!hit || seen[line.lineId]) return;
            seen[line.lineId] = true;
            ids.push(line.lineId);
          }}
          if (api && typeof api.getDefaultExpenseLines === 'function') {{
            (api.getDefaultExpenseLines() || []).forEach(consider);
          }}
          try {{
            var raw = localStorage.getItem('kpiNavigator.plLineCatalog');
            var parsed = raw ? JSON.parse(raw) : null;
            var lines = parsed && parsed.lines
              ? parsed.lines
              : Array.isArray(parsed)
                ? parsed
                : [];
            lines.forEach(consider);
          }} catch (_e) {{}}
          return ids;
        }}

        function plAnalyzeSumLineIds(lineIds, mi) {{
          var value = 0;
          var has = false;
          (lineIds || []).forEach(function (lineId) {{
            var parsed = plAnalyzeParseExpenseMonth(lineId, mi);
            if (parsed.has) {{
              has = true;
              value += parsed.value;
            }}
          }});
          return {{ value: value, has: has }};
        }}

        function plAnalyzeFillKeyLayout() {{
          var metrics = plAnalyzeReadMetrics();
          var groups = (metrics && metrics.groups) || [];
          groups.forEach(function (group) {{
            (group.rows || []).forEach(function (row) {{
              if (!row || !row.id) return;
              var lineIds =
                row.source === 'labor' ? plAnalyzeLaborLineIds() : row.lineIds || [];
              for (var mi = 0; mi < 12; mi++) {{
                var parsed = plAnalyzeSumLineIds(lineIds, mi);
                plAnalyzeSetAmount(row.id, mi, parsed.value, parsed.has);
              }}
            }});
          }});
        }}

        function plAnalyzeEnsureLayout() {{
          plAnalyzeSnapshotRestaurant();
          if (plAnalyzeIsRestaurant()) {{
            if (renderedMode && renderedMode !== 'restaurant_fl') {{
              plAnalyzeRestoreRestaurantLayout();
            }}
            renderedMode = 'restaurant_fl';
            renderedSig = 'restaurant_fl';
            return 'restaurant_fl';
          }}
          var sig = plAnalyzeMetricsSignature();
          if (renderedMode !== 'key_expenses' || renderedSig !== sig) {{
            plAnalyzeRenderKeyLayout();
            renderedMode = 'key_expenses';
            renderedSig = sig;
          }}
          return 'key_expenses';
        }}

        refreshAnalyzeBlock = function () {{
          var mode = plAnalyzeEnsureLayout();
          if (mode === 'restaurant_fl') {{
            restaurantRefresh();
            return;
          }}
          plAnalyzeFillKeyLayout();
          if (typeof refreshPlRatios === 'function') refreshPlRatios();
        }};
        window.__plRefreshAnalyzeBlock = refreshAnalyzeBlock;
      }})();
{JS_END}
"""