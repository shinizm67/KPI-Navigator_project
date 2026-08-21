"""PL toolbar — read-only daily sales input path indicator (Option A).

Mirrors MEP / Sales Data toggle appearance; does not switch path.
Pro only (Standard is always annual, toggle hidden elsewhere too).

2026-08-18: UI 非表示（混乱回避）。復活手順 → docs/pl-edit-status-and-workspace-memo.md §8
"""

from __future__ import annotations

PL_SALES_PATH_INDICATOR_MARKER = "/* PL-SALES-INPUT-PATH-INDICATOR */"

# False = PL ツールバーに出さない（HTML/CSS/JS は残す）。True で Pro 向け表示を復活。
PL_SALES_INPUT_PATH_INDICATOR_ENABLED = False


def pl_sales_path_indicator_css() -> str:
    return """
    /* PL-SALES-INPUT-PATH-INDICATOR-CSS */
    .kpi-daily-input-path--pl-readonly {
      box-sizing: border-box;
      color: #0db13a;
      font-family: 'Orbitron', sans-serif;
      user-select: none;
      min-width: 172px;
      margin-left: 14px;
      flex-shrink: 0;
    }
    .kpi-daily-input-path--pl-readonly[hidden] {
      display: none !important;
    }
    .kpi-daily-input-path--pl-readonly .kpi-daily-input-path__title {
      margin: 0 0 5px;
      text-align: center;
      color: #0db13a;
      font-size: 11px;
      line-height: 1;
      letter-spacing: 0.06em;
      font-weight: 500;
    }
    .kpi-daily-input-path--pl-readonly .kpi-daily-input-path__row {
      display: grid;
      grid-template-columns: auto 52px auto;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    .kpi-daily-input-path--pl-readonly .kpi-daily-input-path__side {
      font-size: 10px;
      line-height: 1.1;
      color: #0db13a;
      text-align: center;
      white-space: nowrap;
    }
    .kpi-daily-input-path--pl-readonly .kpi-daily-input-path__side.is-active {
      opacity: 1;
      font-weight: 600;
    }
    .kpi-daily-input-path--pl-readonly .kpi-daily-input-path__side.is-inactive {
      opacity: 0.34;
      font-weight: 500;
    }
    .kpi-daily-input-path--pl-readonly .kpi-daily-input-path__switch--readonly {
      position: relative;
      display: block;
      width: 52px;
      height: 17px;
      border: 1.5px solid #0db13a;
      border-radius: 999px;
      background: rgba(0, 0, 0, 0.2);
      pointer-events: none;
      cursor: default;
    }
    .kpi-daily-input-path--pl-readonly .kpi-daily-input-path__knob {
      position: absolute;
      top: 2px;
      left: 2px;
      width: 13px;
      height: 13px;
      border-radius: 999px;
      background: #0db13a;
      box-shadow: 0 0 8px rgba(13, 177, 58, 0.35);
      transition: transform 0.2s ease;
    }
    .kpi-daily-input-path--pl-readonly.is-mep .kpi-daily-input-path__knob {
      transform: translateX(31px);
    }
    body.office-mode .kpi-daily-input-path--pl-readonly {
      color: #4a4a4a;
    }
    body.office-mode .kpi-daily-input-path--pl-readonly .kpi-daily-input-path__title,
    body.office-mode .kpi-daily-input-path--pl-readonly .kpi-daily-input-path__side.is-active {
      color: #4a4a4a;
    }
    body.office-mode .kpi-daily-input-path--pl-readonly .kpi-daily-input-path__side.is-inactive {
      color: #7a7a7a;
      opacity: 0.55;
    }
    body.office-mode .kpi-daily-input-path--pl-readonly .kpi-daily-input-path__switch--readonly {
      border-color: #4a4a4a;
      background: #f2f2f2;
    }
    body.office-mode .kpi-daily-input-path--pl-readonly .kpi-daily-input-path__knob {
      background: #5a5a5a;
      box-shadow: none;
    }
    /* /PL-SALES-INPUT-PATH-INDICATOR-CSS */"""


def pl_sales_path_indicator_html(lang: str) -> str:
    is_ja = lang == "ja"
    title = "編集" if is_ja else "Edit"
    aria = "日次売上の入力経路（表示のみ）" if is_ja else "Daily sales input path (read-only)"
    tip = (
        "日次売上の入力経路（表示のみ）。切替は MEP または Sales Data で行います。"
        if is_ja
        else "Daily sales input path (read-only). Switch in MEP or Sales Data."
    )
    disabled_note = (
        '\n              <!-- PL-SALES-INPUT-PATH-INDICATOR: disabled. Restore: docs/pl-edit-status-and-workspace-memo.md §8 -->'
        if not PL_SALES_INPUT_PATH_INDICATOR_ENABLED
        else ""
    )
    disabled_attr = (
        ' data-pl-sales-path-indicator-disabled="1"'
        if not PL_SALES_INPUT_PATH_INDICATOR_ENABLED
        else ""
    )
    return f"""{disabled_note}
              <div
                class="kpi-daily-input-path kpi-daily-input-path--pl-readonly"
                id="pl-sales-input-path"
                data-kpi-sales-input-path-readonly{disabled_attr}
                hidden
                aria-label="{aria}"
                data-tooltip="{tip}"
                title="{tip}"
              >
                <p class="kpi-daily-input-path__title">{title}</p>
                <div class="kpi-daily-input-path__row">
                  <span class="kpi-daily-input-path__side is-active" data-kpi-path-side="annual">Annual</span>
                  <span class="kpi-daily-input-path__switch kpi-daily-input-path__switch--readonly" aria-hidden="true">
                    <span class="kpi-daily-input-path__knob"></span>
                  </span>
                  <span class="kpi-daily-input-path__side is-inactive" data-kpi-path-side="mep">Monthly</span>
                </div>
              </div>"""


def pl_sales_input_path_indicator_js() -> str:
    return f"""      {PL_SALES_PATH_INDICATOR_MARKER}
      (function () {{
        var STORE_KEY = 'kpiNavigator.kpiYearStore';
        var TIER_KEY = 'kpiNavigator.subscriptionTier';
        var wrap = document.getElementById('pl-sales-input-path');
        if (!wrap) return;
        var PL_SALES_INPUT_PATH_INDICATOR_ENABLED = {str(PL_SALES_INPUT_PATH_INDICATOR_ENABLED).lower()};

        function isJa() {{
          return (
            String(document.documentElement.getAttribute('lang') || '')
              .toLowerCase()
              .indexOf('ja') === 0
          );
        }}
        function t(ja, en) {{
          return isJa() ? ja : en;
        }}
        function readStore() {{
          if (window.KpiYearStore && typeof KpiYearStore.getDailySalesInputPath === 'function') {{
            return {{ path: KpiYearStore.getDailySalesInputPath(), pro: KpiYearStore.isProSubscription() }};
          }}
          var store = null;
          if (window.__KPI_DATA_GATEWAY && typeof __KPI_DATA_GATEWAY.getJson === 'function') {{
            store = __KPI_DATA_GATEWAY.getJson(STORE_KEY);
          }} else {{
            try {{
              var raw = localStorage.getItem(STORE_KEY);
              store = raw ? JSON.parse(raw) : null;
            }} catch (_e) {{
              store = null;
            }}
          }}
          var pathRaw = store && store.meta && store.meta.dailySalesInputPath;
          var path = pathRaw === 'mep' ? 'mep' : 'annual';
          var tier = 'pro';
          try {{
            tier =
              sessionStorage.getItem(TIER_KEY) ||
              localStorage.getItem(TIER_KEY) ||
              'pro';
          }} catch (_e2) {{}}
          return {{ path: path, pro: tier !== 'basic' }};
        }}
        function applyPath(path) {{
          var isMep = path === 'mep';
          wrap.classList.toggle('is-mep', isMep);
          wrap.querySelectorAll('[data-kpi-path-side]').forEach(function (el) {{
            var side = el.getAttribute('data-kpi-path-side');
            var active = side === 'mep' ? isMep : !isMep;
            el.classList.toggle('is-active', active);
            el.classList.toggle('is-inactive', !active);
          }});
          wrap.setAttribute(
            'aria-label',
            t(
              '日次売上の入力経路: ' + (isMep ? 'Monthly（MEP）' : 'Annual / Sales Data') + '（表示のみ）',
              'Daily sales input path: ' + (isMep ? 'Monthly (MEP)' : 'Annual / Sales Data') + ' (read-only)'
            )
          );
        }}
        function syncIndicator() {{
          if (!PL_SALES_INPUT_PATH_INDICATOR_ENABLED) {{
            wrap.hidden = true;
            return;
          }}
          var st = readStore();
          wrap.hidden = !st.pro;
          if (!st.pro) return;
          applyPath(st.path);
        }}
        syncIndicator();
        document.addEventListener('kpi:dailySalesInputPathChanged', syncIndicator);
        window.addEventListener('storage', function (ev) {{
          if (!ev || (ev.key !== STORE_KEY && ev.key !== TIER_KEY)) return;
          syncIndicator();
        }});
        window.__plSyncSalesInputPathIndicator = syncIndicator;
      }})();"""
