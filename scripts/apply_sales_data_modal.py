#!/usr/bin/env python3
"""Insert Sales Data modal (current-year sister of Past Sales) into annual index.html (JA + EN)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

JA_PATH = ROOT / "app/annual/index.html"
EN_PATH = ROOT / "en/app/annual/index.html"

MARKER = "id=\"sales-data-modal\""

JA_TEXT = {
    "title": "売上データ",
    "close_chooser_title": "売上データを閉じます",
    "tablist": "売上データビュー",
    "summary": "売上サマリー",
    "btn_aria": "売上 — 当年の日次売上を入力します",
    "btn_title": "当年の日次売上を入力します",
}

EN_TEXT = {
    "title": "Sales Data",
    "close_chooser_title": "Close Sales Data",
    "tablist": "Sales data views",
    "summary": "Sales summary",
    "btn_aria": "Sales — Enter this year's daily sales",
    "btn_title": "Enter this year's daily sales",
}


def transform_css(block: str) -> str:
    block = block.replace("Past Sales モーダル", "Sales Data モーダル（当年）")
    block = block.replace("Past Sales modal", "Sales Data modal (current year)")
    block = re.sub(r"\.past-sales-modal", ".sales-data-modal", block)
    block = re.sub(r"#past-sales-", "#sales-data-", block)
    block = re.sub(r"--psm-", "--sdm-", block)
    block = re.sub(r"data-psm-tab", "data-sdm-tab", block)
    block = re.sub(
        r"--sdm-frame: #370aff;\s*\n\s*--sdm-panel-bg: #100052;",
        "--sdm-frame: #0f9403;\n      --sdm-panel-bg: #000000;",
        block,
        count=1,
    )
    office = """
    .sales-data-modal__ym-cell--year-fixed {
      flex: 1 1 auto;
      justify-content: center;
      min-width: 0;
    }
    .sales-data-modal__ym-year-label {
      font-size: var(--sdm-fs-body);
      color: var(--sdm-cyan);
      font-weight: 700;
      letter-spacing: 0.02em;
    }
"""
    if ".sales-data-modal__ym-year-label" not in block:
        block = block.replace(
            "body.office-mode .sales-data-modal__season-marker {",
            office + "\n    body.office-mode .sales-data-modal__season-marker {",
        )
    return block


def transform_html(block: str, lang: str) -> str:
    t = JA_TEXT if lang == "ja" else EN_TEXT
    block = re.sub(r"\.past-sales-modal", ".sales-data-modal", block)
    block = block.replace('class="past-sales-modal"', 'class="sales-data-modal"', 1)
    block = re.sub(r"id=\"past-sales-", 'id="sales-data-', block)
    block = re.sub(r"data-psm-tab", "data-sdm-tab", block)
    block = re.sub(r"for=\"past-sales-", 'for="sales-data-', block)
    block = re.sub(r"#past-sales-", "#sales-data-", block)
    block = re.sub(r"past-sales-modal__", "sales-data-modal__", block)
    block = re.sub(r"data-psm-sales", "data-sdm-sales", block)

    block = re.sub(
        r"<h2 id=\"sales-data-modal-title\" class=\"sales-data-modal__title\">[^<]+</h2>",
        f'<h2 id="sales-data-modal-title" class="sales-data-modal__title">{t["title"]}</h2>',
        block,
        count=1,
    )
    block = re.sub(
        r'aria-label="[^"]*ビュー"|aria-label="Past sales[^"]*"',
        f'aria-label="{t["tablist"]}"',
        block,
        count=1,
    )
    block = re.sub(
        r'aria-label="[^"]*サマリー"|aria-label="Past sales summary[^"]*"',
        f'aria-label="{t["summary"]}"',
        block,
        count=1,
    )
    block = re.sub(
        r"<p id=\"sales-data-close-chooser-title\"[^>]*>[^<]+</p>",
        f'<p id="sales-data-close-chooser-title" class="sales-data-modal__close-chooser-title">{t["close_chooser_title"]}</p>',
        block,
        count=1,
    )

    year_cell = (
        '        <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--year-fixed" aria-live="polite">\n'
        '          <span id="sales-data-year-label" class="sales-data-modal__ym-year-label"></span>\n'
        "        </div>\n"
    )
    block = re.sub(
        r'<div class="sales-data-modal__ym-cell">\s*<button[^>]*id="sales-data-year-prev"[\s\S]*?</div>\s*',
        year_cell,
        block,
        count=1,
    )

    return block


def transform_js(block: str) -> str:
    block = block.replace("annual-past-sales-btn", "annual-current-sales-btn")
    block = re.sub(r"past-sales-modal", "sales-data-modal", block)
    block = re.sub(r"past-sales-", "sales-data-", block)
    block = re.sub(r"PastSales", "SalesData", block)
    block = re.sub(r"pastSales", "salesData", block)
    block = re.sub(r"data-psm-", "data-sdm-", block)
    block = re.sub(r"--psm-", "--sdm-", block)

    block = block.replace("kpiNavigator.pastSalesShared", "kpiNavigator.annualDailyShared")
    block = block.replace("annual:pastSalesSaved", "annual:salesDataSaved")
    block = block.replace("annual:pastSalesMapChanged", "annual:salesMapChanged")
    block = block.replace("annual:pastBusinessDayMapChanged", "annual:businessDayMapChanged")
    block = block.replace("source: 'past-sales-modal'", "source: 'sales-data-modal'")

    block = block.replace("salesByDate", "targetSalesByDate")
    block = block.replace("ensureSalesDataDaily", "ensureSalesDataDaily")

    block = re.sub(
        r"function ensureSalesDataDaily\(\) \{[^}]+\}[^}]+\}[^}]+\}[^}]+\}",
        """function ensureSalesDataDaily() {
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
        window.__ANNUAL_DATA.daily = window.__ANNUAL_DATA.daily || {
          targetSalesByDate: {},
          businessDayByDate: {}
        };
        var daily = window.__ANNUAL_DATA.daily;
        daily.targetSalesByDate = daily.targetSalesByDate || {};
        daily.businessDayByDate = daily.businessDayByDate || {};
        return daily;
      }""",
        block,
        count=1,
    )

    block = re.sub(
        r"function persistSalesDataShared\(\) \{[^}]+\}[^}]+\}[^}]+\}[^}]+\}",
        """function persistSalesDataShared() {
        var daily = ensureSalesDataDaily();
        var payload = {
          targetSalesByDate: daily.targetSalesByDate || {},
          businessDayByDate: daily.businessDayByDate || {}
        };
        if (daily.referenceAnnualSales != null && isFinite(Number(daily.referenceAnnualSales))) {
          payload.referenceAnnualSales = Math.round(Number(daily.referenceAnnualSales));
        }
        if (daily.salesDataLastSession && typeof daily.salesDataLastSession === 'object') {
          payload.salesDataLastSession = daily.salesDataLastSession;
        }
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', payload);
      }""",
        block,
        count=1,
    )

    block = block.replace(
        "refreshSalesDataLastSessionFromStorage",
        "refreshSalesDataLastSessionFromStorage",
    )
    block = re.sub(
        r"function refreshSalesDataLastSessionFromStorage\(\) \{[^}]+\}[^}]+\}",
        """function refreshSalesDataLastSessionFromStorage() {
        var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.annualDailyShared');
        if (!parsed || !parsed.salesDataLastSession || typeof parsed.salesDataLastSession !== 'object') return;
        ensureSalesDataDaily().salesDataLastSession = parsed.salesDataLastSession;
      }""",
        block,
        count=1,
    )

    block = re.sub(
        r"function getSalesDataLastSession\(\) \{[^}]+\}[^}]+\}[^}]+\}",
        """function getSalesDataLastSession() {
        refreshSalesDataLastSessionFromStorage();
        var daily = ensureSalesDataDaily();
        var ui = daily.salesDataLastSession;
        if (!ui || typeof ui !== 'object') return null;
        return ui;
      }""",
        block,
        count=1,
    )

    block = re.sub(
        r"function getReferenceForYear\(y\) \{[^}]+\}[^}]+\}[^}]+\}",
        """function getReferenceForYear(y) {
        if (y !== getOperatingYear()) return null;
        var daily = ensureSalesDataDaily();
        var v = daily.referenceAnnualSales;
        if (v == null || !isFinite(Number(v))) return null;
        return Math.round(Number(v));
      }

      function getReferenceFromInputEl() {
        if (!summaryReferenceInput) return null;
        var parsed = parseSalesInputRaw(summaryReferenceInput);
        if (parsed == null || !isFinite(parsed) || parsed <= 0) return null;
        return Math.round(parsed);
      }""",
        block,
        count=1,
    )

    block = re.sub(
        r"function applyReferenceDraftsToPersisted\(\) \{[^}]+\}[^}]+\}[^}]+\}[^}]+\}",
        """function applyReferenceDraftsToPersisted() {
        var daily = ensureSalesDataDaily();
        var y = getOperatingYear();
        var key = String(y);
        if (!Object.prototype.hasOwnProperty.call(state.referenceByYear, key)) return;
        var v = state.referenceByYear[key];
        if (v == null) daily.referenceAnnualSales = null;
        else daily.referenceAnnualSales = Math.round(Number(v));
        delete state.referenceByYear[key];
      }""",
        block,
        count=1,
    )

    block = re.sub(
        r"ps\.lastSession = lastSessionSnap;",
        "daily.salesDataLastSession = lastSessionSnap;",
        block,
    )
    block = re.sub(
        r"var ps = ensureSalesDataDaily\(\);\s*var map = ps\.targetSalesByDate;\s*var bmap = ps\.businessDayByDate;",
        "var daily = ensureSalesDataDaily();\n        var map = daily.targetSalesByDate;\n        var bmap = daily.businessDayByDate;",
        block,
        count=1,
    )

    block = re.sub(
        r"function countYearPersistedSalesKeys\(y\) \{\s*var ps = ensureSalesDataDaily\(\);",
        "function countYearPersistedSalesKeys(y) {\n        var daily = ensureSalesDataDaily();",
        block,
        count=1,
    )
    block = block.replace(
        "var map = daily.targetSalesByDate || {};",
        "var map = daily.targetSalesByDate || {};",
        1,
    )

    block = re.sub(
        r"function baseRowDefaults\(iso, isWk\) \{\s*var ps = ensureSalesDataDaily\(\);\s*var bmap = ps\.businessDayByDate;\s*var map = ps\.targetSalesByDate;",
        """function baseRowDefaults(iso, isWk) {
        var daily = ensureSalesDataDaily();
        var bmap = daily.businessDayByDate;
        var map = daily.targetSalesByDate;""",
        block,
        count=1,
    )

    block = re.sub(
        r"function syncColheadDatePickerBounds\(\) \{\s*if \(!dateInput\) return;\s*var cy = currentCalendarYear\(\);\s*dateInput\.min = cy - 10 \+ '-01-01';\s*dateInput\.max = cy - 1 \+ '-12-31';\s*\}",
        """function syncColheadDatePickerBounds() {
        if (!dateInput) return;
        var cy = getOperatingYear();
        dateInput.min = cy + '-01-01';
        dateInput.max = cy + '-12-31';
      }""",
        block,
        count=1,
    )

    block = re.sub(
        r"if \(y < cy - 10 \|\| y > cy - 1\) return;",
        "if (y !== cy) return;",
        block,
    )

    block = re.sub(
        r"function populateYearMonthSelectors\(\) \{[\s\S]*?state\.viewMonth = 0;\s*\}",
        """function getOperatingYear() {
        var d = window.__ANNUAL_DATA;
        if (d && d.calendarYear != null && isFinite(Number(d.calendarYear))) {
          return Number(d.calendarYear);
        }
        return currentCalendarYear();
      }

      function syncYearLabel() {
        var el = document.getElementById('sales-data-year-label');
        if (!el) return;
        var y = getOperatingYear();
        el.textContent = isJa ? String(y) + '年' : String(y);
      }

      function populateYearMonthSelectors() {
        if (!monthSelect) return;
        var cy = getOperatingYear();
        state.year = cy;
        syncYearLabel();
        monthSelect.innerHTML = '';
        var monthLabels = isJa ? MONTHS_JA : MONTHS_EN;
        for (var m = 0; m < 12; m++) {
          var optM = document.createElement('option');
          optM.value = String(m + 1);
          optM.textContent = monthLabels[m];
          monthSelect.appendChild(optM);
        }
        monthSelect.value = '1';
        state.viewMonth = 0;
      }""",
        block,
        count=1,
    )

    block = re.sub(
        r"function renderSalesDataTable\(\) \{\s*if \(!modalTable \|\| !yearSelect\) return;\s*var y = Number\(yearSelect\.value\);",
        """function renderSalesDataTable() {
        if (!modalTable) return;
        var y = getOperatingYear();""",
        block,
        count=1,
    )

    block = re.sub(
        r"if \(!isFinite\(y\) && yearSelect\) y = Number\(yearSelect\.value\);",
        "if (!isFinite(y)) y = getOperatingYear();",
        block,
    )

    block = re.sub(
        r"state\.year = Number\(yearSelect\.value\);",
        "state.year = getOperatingYear();",
        block,
    )

    block = re.sub(
        r"if \(yearSelect\) \{\s*yearSelect\.addEventListener\('change',[\s\S]*?\}\s*\}\s*if \(monthSelect\)",
        "if (monthSelect)",
        block,
        count=1,
    )

    block = re.sub(
        r"if \(yearPrev\) \{[\s\S]*?\}\s*if \(yearNext\) \{[\s\S]*?\}\s*if \(monthPrev\)",
        "if (monthPrev)",
        block,
        count=1,
    )

    block = re.sub(
        r"if \(prevYear !== y\) \{[\s\S]*?renderSalesDataTable\(\);\s*\}",
        "",
        block,
        count=1,
    )

    block = block.replace("var yearSelect = document.getElementById('sales-data-year-select');", "var yearSelect = null;")
    block = block.replace("var yearPrev = document.getElementById('sales-data-year-prev');", "var yearPrev = null;")
    block = block.replace("var yearNext = document.getElementById('sales-data-year-next');", "var yearNext = null;")

    apply_session = r"""function applySalesDataLastSession(ui) {
        if (!ui) return false;
        var y = getOperatingYear();
        if (Number(ui.year) !== y) return false;
        state.year = y;
        syncYearLabel();
        var m = Number(ui.month);
        if (ui.focusIso && /^\d{4}-\d{2}-\d{2}$/.test(String(ui.focusIso))) {
          m = Number(String(ui.focusIso).split('-')[1]);
        }
        if (monthSelect && isFinite(m) && m >= 1 && m <= 12) {
          monthSelect.value = String(Math.round(m));
          state.viewMonth = Math.round(m) - 1;
        }
        return true;
      }"""

    def _repl_apply_session(_m: re.Match[str]) -> str:
        return apply_session

    block = re.sub(
        r"function applySalesDataLastSession\(ui\) \{[\s\S]*?return true;\s*\}",
        _repl_apply_session,
        block,
        count=1,
    )

    if "annual:calendarYearChanged" not in block:
        block = block.replace(
            "openBtn.addEventListener('click', openModal);",
            "openBtn.addEventListener('click', openModal);\n"
            "      document.addEventListener('annual:calendarYearChanged', function () {\n"
            "        if (modal.hasAttribute('hidden')) return;\n"
            "        populateYearMonthSelectors();\n"
            "        renderSalesDataTable();\n"
            "        updateSalesDataSummary();\n"
            "      });",
            1,
        )

    return block


def patch_hydrate(html: str) -> str:
    needle = """        if (parsed.businessDayByDate && typeof parsed.businessDayByDate === 'object') {
          daily.businessDayByDate = Object.assign({}, daily.businessDayByDate || {}, parsed.businessDayByDate);
        }
        window.__ANNUAL_DATA.daily = daily;"""
    extra = """        if (parsed.businessDayByDate && typeof parsed.businessDayByDate === 'object') {
          daily.businessDayByDate = Object.assign({}, daily.businessDayByDate || {}, parsed.businessDayByDate);
        }
        if (parsed.referenceAnnualSales != null && isFinite(Number(parsed.referenceAnnualSales))) {
          daily.referenceAnnualSales = Math.round(Number(parsed.referenceAnnualSales));
        }
        if (parsed.salesDataLastSession && typeof parsed.salesDataLastSession === 'object') {
          daily.salesDataLastSession = parsed.salesDataLastSession;
        }
        window.__ANNUAL_DATA.daily = daily;"""
    if "salesDataLastSession" in html:
        return html
    return html.replace(needle, extra, 1)


def patch_current_sales_btn(html: str, lang: str) -> str:
    t = JA_TEXT if lang == "ja" else EN_TEXT
    html = re.sub(
        r'(id="annual-current-sales-btn"[^>]*aria-label=")[^"]*(")',
        rf'\1{t["btn_aria"]}\2',
        html,
        count=1,
    )
    html = re.sub(
        r'(id="annual-current-sales-btn"[^>]*title=")[^"]*(")',
        rf'\1{t["btn_title"]}\2',
        html,
        count=1,
    )
    return html


def apply_file(path: Path, lang: str) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"skip (already applied): {path}")
        text = patch_hydrate(text)
        text = patch_current_sales_btn(text, lang)
        path.write_text(text, encoding="utf-8")
        return

    css_m = re.search(
        r"/\* Past Sales[^*]*\*/\s*\.past-sales-modal \{",
        text,
    )
    if not css_m:
        raise SystemExit(f"Past Sales CSS not found in {path}")
    css_start = css_m.start()
    css_end = text.find("/* Annual Edit", css_start)
    if css_end < 0:
        raise SystemExit(f"Annual Edit CSS anchor not found in {path}")
    css_block = transform_css(text[css_start:css_end])

    html_m = re.search(
        r'<div\s+class="past-sales-modal"\s+id="past-sales-modal"',
        text,
    )
    if not html_m:
        raise SystemExit(f"Past Sales HTML not found in {path}")
    html_start = html_m.start()
    html_end = text.find('<div\n    class="annual-edit-modal"', html_start)
    if html_end < 0:
        html_end = text.find('<div class="annual-edit-modal"', html_start)
    html_block = transform_html(text[html_start:html_end], lang)

    js_m = re.search(
        r"var openBtn = document\.getElementById\('annual-past-sales-btn'\);",
        text,
    )
    if not js_m:
        raise SystemExit(f"Past Sales JS not found in {path}")
    js_start = text.rfind("<script>", 0, js_m.start())
    js_end = text.find("})();\n  </script>", js_m.start())
    if js_end < 0:
        raise SystemExit(f"Past Sales JS end not found in {path}")
    js_end += len("})();\n  </script>")
    js_block = transform_js(text[js_start:js_end])

    text = text[:css_end] + css_block + text[css_end:]

    html_m2 = re.search(
        r'<div\s+class="past-sales-modal"\s+id="past-sales-modal"',
        text,
    )
    html_end2 = text.find('<div\n    class="annual-edit-modal"', html_m2.start())
    if html_end2 < 0:
        html_end2 = text.find('<div class="annual-edit-modal"', html_m2.start())
    text = text[:html_end2] + html_block + text[html_end2:]

    js_m2 = re.search(
        r"var openBtn = document\.getElementById\('annual-past-sales-btn'\);",
        text,
    )
    js_end2 = text.find("})();\n  </script>", js_m2.start())
    js_end2 += len("})();\n  </script>")
    text = text[:js_end2] + "\n  " + js_block + text[js_end2:]

    text = patch_hydrate(text)
    text = patch_current_sales_btn(text, lang)
    path.write_text(text, encoding="utf-8")
    print(f"applied: {path}")


def main() -> None:
    apply_file(JA_PATH, "ja")
    apply_file(EN_PATH, "en")


if __name__ == "__main__":
    main()
