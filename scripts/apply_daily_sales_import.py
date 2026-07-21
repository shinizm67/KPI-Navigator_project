#!/usr/bin/env python3
"""Wire CSV / Excel daily-sales import to all Upload CSV buttons."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from daily_sales_import_client import (  # noqa: E402
    DAILY_SALES_IMPORT_MARKER,
    daily_sales_import_js,
)

ANNUAL_PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MEP_PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

CSV_BTN_TOOLTIP_JA_OLD = 'title="CSVファイルを取り込んで表を更新（準備中）"'
CSV_BTN_TOOLTIP_JA_NEW = (
    'title="CSVで日次売上を取り込めます。Excel（.xlsx）も可。任意でフード/ドリンク列（どちらか一方でも可）。"\n'
    '        data-tooltip="CSVで日次売上を取り込めます。Excel（.xlsx）も可。任意でフード/ドリンク列（どちらか一方でも可）。"'
)

CSV_BTN_TOOLTIP_JA_PLAIN_OLD = 'title="CSVファイルを取り込んで表を更新"'
CSV_BTN_TOOLTIP_JA_PLAIN_NEW = CSV_BTN_TOOLTIP_JA_NEW

CSV_BTN_TOOLTIP_EN_OLD = 'title="Import a CSV file to update the table (coming soon)"'
CSV_BTN_TOOLTIP_EN_NEW = (
    'title="Import daily sales from CSV or Excel (.xlsx). Optional Food/Drink columns (either side OK)."\n'
    '        data-tooltip="Import daily sales from CSV or Excel (.xlsx). Optional Food/Drink columns (either side OK)."'
)

CSV_BTN_TOOLTIP_EN_PLAIN_OLD = 'title="Import a CSV file to update the table"'
CSV_BTN_TOOLTIP_EN_PLAIN_NEW = CSV_BTN_TOOLTIP_EN_NEW

MEP_CSV_TITLE_JA_OLD = 'title="CSVファイルを取り込んで表を更新"'
MEP_CSV_TITLE_JA_NEW = CSV_BTN_TOOLTIP_JA_NEW

MEP_CSV_TITLE_EN_OLD = 'title="Import a CSV file to update the table"'
MEP_CSV_TITLE_EN_OLD_AND = 'title="Import a CSV file and update the table"'
MEP_CSV_TITLE_EN_NEW = CSV_BTN_TOOLTIP_EN_NEW

AEM_CSV_OLD = """      if (btnCsv) {
        btnCsv.addEventListener('click', function () {
          window.alert('CSV取込は次フェーズで実装予定です。');
        });
      }"""

AEM_CSV_NEW = """      if (btnCsv && window.__KPI_DAILY_IMPORT) {
        window.__KPI_DAILY_IMPORT.bindButton(btnCsv, {
          getYear: function () { return state.year; },
          applyMaps: function (maps, year) {
            pushUndoSnapshot();
            window.__KPI_DAILY_IMPORT.applyToRowState(state.rowStateByIso, maps, year);
            recomputeModalDirty();
            syncUndoButton();
            renderTable();
            scrollToViewMonth();
          },
        });
      }"""

AEM_CSV_OLD_EN = """      if (btnCsv) {
        btnCsv.addEventListener('click', function () {
          window.alert('CSV import will be implemented in a coming phase.');
        });
      }"""

PSM_CSV_STUB_BLOCK = """      if (btnCsv) {
        btnCsv.addEventListener('click', function () {
          window.alert(MSG_CSV_STUB);
        });
      }"""

PSM_CSV_NEW = """      if (btnCsv && window.__KPI_DAILY_IMPORT) {
        window.__KPI_DAILY_IMPORT.bindButton(btnCsv, {
          getYear: function () { return state.year; },
          applyMaps: function (maps, year) {
            pushUndoSnapshot();
            window.__KPI_DAILY_IMPORT.applyToRowState(state.rowStateByIso, maps, year);
            recomputeModalDirty();
            syncUndoButton();
            renderPastSalesTable();
            updatePastSalesSummary();
            refreshPastSalesTableTotals();
          },
        });
      }"""

SDM_CSV_NEW = """      if (btnCsv && window.__KPI_DAILY_IMPORT) {
        window.__KPI_DAILY_IMPORT.bindButton(btnCsv, {
          getYear: function () { return state.year; },
          applyMaps: function (maps, year) {
            pushUndoSnapshot();
            window.__KPI_DAILY_IMPORT.applyToRowState(state.rowStateByIso, maps, year);
            recomputeModalDirty();
            syncUndoButton();
            renderSalesDataTable();
            updateSalesDataSummary();
          },
        });
      }"""

MEP_CSV_OLD_JA = """      if (btnCsvUpload) {
        btnCsvUpload.addEventListener('click', function () {
          window.alert('CSV取込は次フェーズで実装予定です。');
        });
      }"""

MEP_CSV_OLD_EN = """      if (btnCsvUpload) {
        btnCsvUpload.addEventListener('click', function () {
          window.alert('CSV import will be implemented in a coming phase.');
        });
      }"""

MEP_CSV_NEW = """      if (btnCsvUpload && window.__KPI_DAILY_IMPORT) {
        window.__KPI_DAILY_IMPORT.bindButton(btnCsvUpload, {
          getYear: function () { return mefYear; },
          applyMaps: function (maps, year) {
            pushUndo();
            var applied = applyDailyImportMapsToOpenYear(maps, year);
            if (!applied) return;
            syncMonthlySalesToAnnualStoreForYear(mefYear);
            markDirty();
            syncUndoButton();
            buildGrid();
          },
        });
      }"""

MEP_CSV_PUSH_UNDO_BUG = """          applyMaps: function (maps, year) {
            pushUndoSnapshot();
            var applied = applyDailyImportMapsToOpenYear(maps, year);"""

MEP_CSV_PUSH_UNDO_FIX = """          applyMaps: function (maps, year) {
            pushUndo();
            var applied = applyDailyImportMapsToOpenYear(maps, year);"""

MEP_APPLY_IMPORT_OLD = """      function applyDailyImportMapsToOpenYear(maps, year) {
        var primary = state.incomeItems && state.incomeItems[0];
        if (!primary || !maps) return 0;
        var yf = Number(year);
        var applied = 0;
        Object.keys(maps.salesByDate || {}).forEach(function (iso) {
          if (Number.isFinite(yf) && mepIsoYear(iso) !== yf) return;
          if (window.KpiYearStore && !KpiYearStore.canWriteDailySalesFrom('mep', iso)) return;
          var biz = maps.businessDayByDate[iso] !== false;
          var sales = Number(maps.salesByDate[iso]);
          bizDayByIso[iso] = biz;
          if (biz && Number.isFinite(sales) && sales > 0) {
            writeValue(primary.id, iso, Math.round(sales));
          } else {
            writeValue(primary.id, iso, 0);
          }
          applied++;
        });
        return applied;
      }"""

MEP_APPLY_IMPORT_NEW = """      function applyDailyImportMapsToOpenYear(maps, year) {
        var primary = state.incomeItems && state.incomeItems[0];
        if (!primary || !maps) return 0;
        var yf = Number(year);
        var applied = 0;
        var foodMap = maps.foodByDate || {};
        Object.keys(maps.salesByDate || {}).forEach(function (iso) {
          if (Number.isFinite(yf) && mepIsoYear(iso) !== yf) return;
          if (window.KpiYearStore && !KpiYearStore.canWriteDailySalesFrom('mep', iso)) return;
          var biz = maps.businessDayByDate[iso] !== false;
          var sales = Number(maps.salesByDate[iso]);
          bizDayByIso[iso] = biz;
          if (biz && Number.isFinite(sales) && sales > 0) {
            writeValue(primary.id, iso, Math.round(sales));
          } else {
            writeValue(primary.id, iso, 0);
          }
          if (Object.prototype.hasOwnProperty.call(foodMap, iso) && typeof writeValue === 'function') {
            var food = Number(foodMap[iso]);
            writeValue('food_sales', iso, Number.isFinite(food) ? Math.round(food) : 0);
          }
          applied++;
        });
        return applied;
      }"""


def inject_import_js(text: str) -> str:
    block = daily_sales_import_js().rstrip() + "\n"
    if DAILY_SALES_IMPORT_MARKER in text:
        pattern = re.escape(DAILY_SALES_IMPORT_MARKER) + r"[\s\S]*?\}\)\(\);\n"
        if re.search(pattern, text):
            return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)
        raise SystemExit("daily sales import marker found but block boundary missing")
    anchor = "/* KPI-YEAR-STORE */"
    if anchor not in text:
        raise SystemExit(f"inject anchor missing: {anchor}")
    m = re.search(re.escape(anchor) + r"[\s\S]*?\}\)\(\);\n", text)
    if not m:
        raise SystemExit("KpiYearStore block end not found")
    insert_at = m.end()
    return text[:insert_at] + "\n" + block + text[insert_at:]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n")[1].strip() in text:
        return text
    raise SystemExit(f"patch miss ({label})")


PSM_CSV_STUB_RE = re.compile(
    r"if \(btnCsv\) \{\n"
    r"        btnCsv\.addEventListener\('click', function \(\) \{\n"
    r"          window\.alert\((?:MSG_CSV_STUB|isJa \? '[^']*' : '[^']*')\);\n"
    r"        \}\);\n"
    r"      \}",
    re.MULTILINE,
)


def replace_modal_csv_stub(text: str, btn_anchor: str, new: str, label: str, *, optional: bool = False) -> str:
    idx = text.find(btn_anchor)
    if idx < 0:
        if optional:
            return text
        raise SystemExit(f"js anchor missing ({label})")
    tail = text[idx:]
    m = PSM_CSV_STUB_RE.search(tail)
    if not m:
        if new.split("\n")[1].strip() in tail[:80000]:
            return text
        raise SystemExit(f"patch miss ({label})")
    start = idx + m.start()
    end = idx + m.end()
    return text[:start] + new + text[end:]


def patch_tooltips(text: str, is_ja: bool) -> str:
    if is_ja:
        for old in (CSV_BTN_TOOLTIP_JA_OLD, CSV_BTN_TOOLTIP_JA_PLAIN_OLD):
            if old in text:
                text = text.replace(old, CSV_BTN_TOOLTIP_JA_NEW, 1)
        old_ja_mid = (
            'title="CSVまたはExcel（.xlsx）ファイルを取り込んで日次売上を入力します"\n'
            '        data-tooltip="CSVまたはExcel（.xlsx）ファイルを取り込んで日次売上を入力します"'
        )
        if old_ja_mid in text:
            text = text.replace(old_ja_mid, CSV_BTN_TOOLTIP_JA_NEW)
        old_ja_xlsx = (
            'title="CSVで日次売上を取り込めます。Excel（.xlsx）も利用できます。"\n'
            '        data-tooltip="CSVで日次売上を取り込めます。Excel（.xlsx）も利用できます。"'
        )
        if old_ja_xlsx in text:
            text = text.replace(old_ja_xlsx, CSV_BTN_TOOLTIP_JA_NEW)
    else:
        for old in (
            CSV_BTN_TOOLTIP_EN_OLD,
            CSV_BTN_TOOLTIP_EN_PLAIN_OLD,
            MEP_CSV_TITLE_EN_OLD,
            MEP_CSV_TITLE_EN_OLD_AND,
            'title="Import daily sales from a CSV or Excel (.xlsx) file"\n'
            '        data-tooltip="Import daily sales from a CSV or Excel (.xlsx) file"',
            'title="Import daily sales from CSV. You can upload Excel (.xlsx) files as well."\n'
            '        data-tooltip="Import daily sales from CSV. You can upload Excel (.xlsx) files as well."',
        ):
            if old in text:
                text = text.replace(old, CSV_BTN_TOOLTIP_EN_NEW)
    return text


def patch_annual_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_ja = "/en/" not in str(path)
    text = inject_import_js(text)
    text = patch_tooltips(text, is_ja)
    if is_ja:
        text = replace_once(text, AEM_CSV_OLD, AEM_CSV_NEW, "annual edit csv ja")
    else:
        text = replace_once(text, AEM_CSV_OLD_EN, AEM_CSV_NEW, "annual edit csv en")
    text = replace_modal_csv_stub(
        text,
        "var btnCsv = document.getElementById('past-sales-modal-csv');",
        PSM_CSV_NEW,
        "past sales csv",
    )
    text = replace_modal_csv_stub(
        text,
        "var btnCsv = document.getElementById('sales-data-modal-csv');",
        SDM_CSV_NEW,
        "sales data csv",
        optional=True,
    )
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def patch_mep_apply_food_drink(text: str) -> str:
    if "var foodMap = maps.foodByDate || {};" in text and "writeValue('food_sales'" in text:
        return text
    if MEP_APPLY_IMPORT_OLD in text:
        return text.replace(MEP_APPLY_IMPORT_OLD, MEP_APPLY_IMPORT_NEW, 1)
    raise SystemExit("patch miss (mep applyDailyImportMaps food/drink)")


def patch_mep_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_ja = "/en/" not in str(path)
    text = inject_import_js(text)
    text = patch_tooltips(text, is_ja)
    text = patch_mep_apply_food_drink(text)
    if MEP_CSV_PUSH_UNDO_BUG in text:
        text = text.replace(MEP_CSV_PUSH_UNDO_BUG, MEP_CSV_PUSH_UNDO_FIX, 1)
    if is_ja:
        if MEP_CSV_TITLE_JA_OLD in text:
            text = text.replace(MEP_CSV_TITLE_JA_OLD, MEP_CSV_TITLE_JA_NEW, 1)
        text = replace_once(text, MEP_CSV_OLD_JA, MEP_CSV_NEW, "mep csv ja")
    else:
        if MEP_CSV_TITLE_EN_OLD in text:
            text = text.replace(MEP_CSV_TITLE_EN_OLD, MEP_CSV_TITLE_EN_NEW, 1)
        if MEP_CSV_TITLE_EN_OLD_AND in text:
            text = text.replace(MEP_CSV_TITLE_EN_OLD_AND, MEP_CSV_TITLE_EN_NEW, 1)
        text = replace_once(text, MEP_CSV_OLD_EN, MEP_CSV_NEW, "mep csv en")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in ANNUAL_PAGES + MEP_PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
    for path in ANNUAL_PAGES:
        patch_annual_page(path)
    for path in MEP_PAGES:
        patch_mep_page(path)
    import subprocess

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "apply_csv_upload_tooltip_css.py")],
        cwd=str(ROOT),
        check=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
