"""Phase 5 — View/Edit toggle HTML/CSS + edit lease hooks.

Path UI behavior lives in `_kpi_sales_input_path_ui.js` (View / Edit, lease-based).
Do not regenerate `data-kpi-path-side` Annual/Monthly labels.
"""

from __future__ import annotations

import re
from pathlib import Path

KPI_SALES_INPUT_PATH_MARKER = "/* KPI-SALES-INPUT-PATH-UI */"
KPI_SALES_INPUT_PATH_MARKER_LEGACY = "/* KPI-SALES-INPUT-PATH */"
KPI_EDIT_LEASE_HOOKS_MARKER = "/* KPI-EDIT-LEASE-HOOKS */"
_SCRIPTS_DIR = Path(__file__).resolve().parent

TOGGLE_DIV_BY_ID_RE = re.compile(
    r'\n        <div\n          class="kpi-daily-input-path[^\n]*\n          id="(?P<id>[^"]+)"[\s\S]*?\n        </div>',
    re.MULTILINE,
)

PHASE5_TOGGLE_CSS_START = "    /* KPI-PHASE5-TOGGLE-CSS */"
PHASE5_TOGGLE_CSS_END = "    /* /KPI-PHASE5-TOGGLE-CSS */"

PHASE5_TOGGLE_CSS = """
    /* KPI-PHASE5-TOGGLE-CSS */
    .kpi-daily-input-path {
      box-sizing: border-box;
      color: #0db13a;
      font-family: 'Orbitron', sans-serif;
      z-index: 6;
      user-select: none;
      width: auto;
      min-width: 172px;
    }
    .kpi-daily-input-path[hidden] {
      display: none !important;
    }
    .kpi-daily-input-path__title {
      margin: 0 0 5px;
      text-align: center;
      color: #0db13a;
      font-size: 11px;
      line-height: 1;
      letter-spacing: 0.06em;
      font-weight: 500;
    }
    .kpi-daily-input-path__row {
      display: grid;
      grid-template-columns: auto 52px auto;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    .kpi-daily-input-path__side {
      font-size: 10px;
      line-height: 1.1;
      color: #0db13a;
      text-align: center;
      white-space: nowrap;
      cursor: pointer;
    }
    .kpi-daily-input-path__side.is-active {
      opacity: 1;
      font-weight: 600;
    }
    .kpi-daily-input-path__side.is-inactive {
      opacity: 0.34;
      font-weight: 500;
    }
    .kpi-daily-input-path__switch {
      position: relative;
      width: 52px;
      height: 17px;
      border: 1.5px solid #0db13a;
      border-radius: 999px;
      background: rgba(0, 0, 0, 0.2);
      cursor: pointer;
      padding: 0;
      margin: 0 auto;
      flex-shrink: 0;
    }
    .kpi-daily-input-path__knob {
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
    .kpi-daily-input-path.is-edit .kpi-daily-input-path__knob,
    .kpi-daily-input-path.is-mep .kpi-daily-input-path__knob {
      transform: translateX(31px);
    }
    .kpi-daily-input-path__switch:focus-visible {
      outline: 2px solid rgba(88, 225, 243, 0.8);
      outline-offset: 2px;
    }
    .kpi-daily-input-path--sales-data {
      position: absolute;
      top: calc(var(--sdm-tab-top) - 30px);
      right: 22px;
      z-index: 7;
    }
    .kpi-daily-input-path--mep {
      position: absolute;
      top: 8px;
      left: calc(
        var(--mef-toolbar-pad) + var(--mef-page-inset, 0px) + var(--mef-summary-toggle-w) +
          var(--mef-nav-gap) + var(--mef-today-shift) + 106px
      );
      z-index: 7;
    }
    body.office-mode .kpi-daily-input-path {
      color: #4a4a4a;
    }
    body.office-mode .kpi-daily-input-path__title,
    body.office-mode .kpi-daily-input-path__side.is-active {
      color: #4a4a4a;
    }
    body.office-mode .kpi-daily-input-path__side.is-inactive {
      color: #7a7a7a;
      opacity: 0.55;
    }
    body.office-mode .kpi-daily-input-path__switch {
      border-color: #4a4a4a;
      background: #f2f2f2;
    }
    body.office-mode .kpi-daily-input-path__knob {
      background: #5a5a5a;
      box-shadow: none;
    }
    /* /KPI-PHASE5-TOGGLE-CSS */"""


def toggle_element_id(variant: str) -> str:
    return "mep-sales-input-path" if variant == "mep" else "sales-data-input-path"


def sales_input_path_toggle_html(variant: str, lang: str) -> str:
    is_ja = lang == "ja"
    is_zh = str(lang).lower().startswith("zh")
    if variant == "mep":
        cls = "kpi-daily-input-path kpi-daily-input-path--mep"
    else:
        cls = "kpi-daily-input-path kpi-daily-input-path--sales-data"
    el_id = toggle_element_id(variant)
    if variant == "mep":
        title = "売上編集" if is_ja else ("營業額編輯" if is_zh else "Sales Edit")
        aria = "売上の閲覧と編集" if is_ja else ("營業額的檢視與編輯" if is_zh else "Sales view and edit")
    else:
        title = "売上データ編集" if is_ja else ("營業額資料編輯" if is_zh else "Sales Data Edit")
        aria = "売上データの閲覧と編集" if is_ja else ("營業額資料的檢視與編輯" if is_zh else "Sales Data view and edit")
    switch_aria = (
        "閲覧と編集を切り替え" if is_ja else ("在檢視與編輯之間切換" if is_zh else "Switch between view and edit")
    )
    view_label = "閲覧" if is_ja else ("檢視" if is_zh else "View")
    edit_label = "編集" if is_ja else ("編輯" if is_zh else "Edit")
    return f"""        <div
          class="{cls}"
          id="{el_id}"
          data-kpi-sales-input-path
          aria-label="{aria}"
        >
          <p class="kpi-daily-input-path__title">{title}</p>
          <div class="kpi-daily-input-path__row">
            <span class="kpi-daily-input-path__side is-active" data-kpi-edit-side="view">{view_label}</span>
            <button
              type="button"
              class="kpi-daily-input-path__switch"
              data-kpi-path-switch
              data-kpi-edit-switch
              role="switch"
              aria-checked="false"
              aria-label="{switch_aria}"
              data-kpi-guard-ignore
            >
              <span class="kpi-daily-input-path__knob" aria-hidden="true"></span>
            </button>
            <span class="kpi-daily-input-path__side is-inactive" data-kpi-edit-side="edit">{edit_label}</span>
          </div>
        </div>"""


def replace_or_insert_toggle(
    text: str,
    variant: str,
    lang: str,
    insert_anchor: str,
    *,
    insert_before: bool = False,
) -> str:
    el_id = toggle_element_id(variant)
    snippet = sales_input_path_toggle_html(variant, lang) + "\n"

    def repl(match: re.Match[str]) -> str:
        if match.group("id") != el_id:
            return match.group(0)
        current = match.group(0)
        if 'data-kpi-edit-side="view"' in current and "data-kpi-path-side" not in current:
            return current
        return "\n" + snippet.rstrip()

    updated, n = TOGGLE_DIV_BY_ID_RE.subn(repl, text, count=1)
    if n:
        return updated
    if insert_anchor not in text:
        raise ValueError(f"toggle insert anchor missing ({variant})")
    if insert_before:
        return text.replace(insert_anchor, snippet + insert_anchor, 1)
    return text.replace(insert_anchor, insert_anchor + snippet, 1)


def sales_input_path_client_js() -> str:
    """View/Edit lease UI. Source of truth: `_kpi_sales_input_path_ui.js`."""
    js = (_SCRIPTS_DIR / "_kpi_sales_input_path_ui.js").read_text(encoding="utf-8")
    return js if js.endswith("\n") else js + "\n"


def edit_lease_hooks_js() -> str:
    return f"""      {KPI_EDIT_LEASE_HOOKS_MARKER}
      (function () {{
        var LEASE_SURFACE = 'daily-sales';
        var heartbeatTimer = null;

        function storeReady() {{
          return !!(window.KpiYearStore && KpiYearStore.acquireEditLease);
        }}
        function isJa() {{
          return (
            String(document.documentElement.getAttribute('lang') || '')
              .toLowerCase()
              .indexOf('ja') === 0
          );
        }}
        function leaseConflictMessage(holder) {{
          var label = (holder && holder.label) || (isJa() ? '別タブ' : 'another tab');
          return isJa()
            ? '「' + label + '」が別タブで編集中です。閲覧のみ可能です。'
            : '"' + label + '" is being edited in another tab. This view is read-only.';
        }}
        function startHeartbeat() {{
          stopHeartbeat();
          heartbeatTimer = window.setInterval(function () {{
            if (storeReady()) KpiYearStore.heartbeatEditLease(LEASE_SURFACE);
          }}, 60000);
        }}
        function stopHeartbeat() {{
          if (heartbeatTimer) {{
            window.clearInterval(heartbeatTimer);
            heartbeatTimer = null;
          }}
        }}
        function tryAcquireLease(label, opts) {{
          if (!storeReady()) return true;
          var result = KpiYearStore.acquireEditLease(LEASE_SURFACE, {{ label: label }});
          if (result && result.ok) {{
            startHeartbeat();
            return true;
          }}
          if (!opts || !opts.silent) {{
            window.alert(leaseConflictMessage(result && result.holder));
          }}
          document.dispatchEvent(new CustomEvent('kpi:editGuardsRefresh'));
          return false;
        }}
        function releaseLease() {{
          stopHeartbeat();
          if (storeReady()) KpiYearStore.releaseEditLease(LEASE_SURFACE);
        }}
        window.__KPI_EDIT_LEASE = {{
          tryAcquire: tryAcquireLease,
          release: releaseLease,
          startHeartbeat: startHeartbeat,
          stopHeartbeat: stopHeartbeat,
        }};
        document.addEventListener('kpi:editLeaseChanged', function () {{
          document.dispatchEvent(new CustomEvent('kpi:editGuardsRefresh'));
        }});
        window.addEventListener('beforeunload', releaseLease);
        window.addEventListener('pagehide', releaseLease);
      }})();
"""
