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
    ROOT / "zh-tw/app/annual/index.html",
]

MEP_PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
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
          persistByCsvYear: true,
          getYear: function () { return state.year; },
          applyMaps: function (maps, year) {
            pushUndoSnapshot();
            persistPastSalesCsvByYear(maps);
            var yShow = Number(year);
            var csvYears = maps.years || [];
            if (csvYears.indexOf(yShow) < 0) return;
            window.__KPI_DAILY_IMPORT.applyToRowState(state.rowStateByIso, maps, yShow);
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
          persistByCsvYear: true,
          getYear: function () { return mefYear; },
          applyMaps: function (maps, year) {
            pushUndo();
            var persistP = persistMepSalesCsvByYear(maps);
            Promise.resolve(persistP).catch(function () {});
            var yShow = Number(mefYear);
            var csvYears = maps.years || [];
            if (csvYears.indexOf(yShow) < 0) return Promise.resolve();
            var applied = applyDailyImportMapsToOpenYear(maps, yShow);
            if (!applied) return Promise.resolve();
            markDirty();
            syncUndoButton();
            buildGrid();
            return Promise.resolve();
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

PAST_SALES_CSV_HELPER = """      function persistPastSalesCsvByYear(maps) {
        if (!maps) return Promise.resolve();
        var oy =
          window.KpiYearStore && typeof KpiYearStore.getOperatingYear === 'function'
            ? Number(KpiYearStore.getOperatingYear())
            : NaN;
        var sales = {};
        var biz = {};
        Object.keys(maps.salesByDate || {}).forEach(function (iso) {
          var y = typeof isoYearFromIso === 'function' ? isoYearFromIso(iso) : Number(String(iso).slice(0, 4));
          if (!Number.isFinite(y)) return;
          if (Number.isFinite(oy) && y >= oy) return;
          var n = Number(maps.salesByDate[iso]);
          sales[iso] = Number.isFinite(n) ? n : 0;
          if (
            maps.businessDayByDate &&
            Object.prototype.hasOwnProperty.call(maps.businessDayByDate, iso)
          ) {
            biz[iso] = !!maps.businessDayByDate[iso];
          }
        });
        var ps = ensurePastSalesDaily();
        Object.keys(sales).forEach(function (iso) {
          ps.salesByDate[iso] = sales[iso];
        });
        Object.keys(biz).forEach(function (iso) {
          ps.businessDayByDate[iso] = biz[iso];
        });
        if (window.KpiYearStore && typeof KpiYearStore.persistFromPastSales === 'function') {
          var done = KpiYearStore.persistFromPastSales(
            { salesByDate: sales, businessDayByDate: biz },
            { source: 'past-sales-csv-import' }
          );
          var payload = {
            salesByDate: ps.salesByDate || {},
            businessDayByDate: ps.businessDayByDate || {},
            referenceAnnualSalesByYear: ps.referenceAnnualSalesByYear || {}
          };
          if (ps.lastSession && typeof ps.lastSession === 'object') {
            payload.lastSession = ps.lastSession;
          }
          if (window.__KPI_DATA_GATEWAY && typeof window.__KPI_DATA_GATEWAY.setJson === 'function') {
            window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.pastSalesShared', payload);
          }
          return done;
        }
        return persistPastSalesShared({ source: 'past-sales-csv-import' });
      }"""

MEP_SALES_CSV_HELPER = """      function persistMepSalesCsvByYear(maps) {
        if (!maps) return Promise.resolve();
        var csvSales = {};
        var csvBiz = {};
        var incomeByYear = {};
        function addIncome(streamId, iso, val) {
          var y = mepIsoYear(iso);
          if (!Number.isFinite(y)) return;
          if (!incomeByYear[y]) incomeByYear[y] = {};
          if (!incomeByYear[y][streamId]) incomeByYear[y][streamId] = {};
          var n = Number(val);
          incomeByYear[y][streamId][iso] = Number.isFinite(n) ? Math.round(n) : 0;
        }
        Object.keys(maps.salesByDate || {}).forEach(function (iso) {
          var n = Number(maps.salesByDate[iso]);
          csvSales[iso] = Number.isFinite(n) ? n : 0;
          if (
            maps.businessDayByDate &&
            Object.prototype.hasOwnProperty.call(maps.businessDayByDate, iso)
          ) {
            csvBiz[iso] = !!maps.businessDayByDate[iso];
          }
        });
        Object.keys(maps.foodByDate || {}).forEach(function (iso) {
          addIncome('food_sales', iso, maps.foodByDate[iso]);
        });
        Object.keys(maps.drinkByDate || {}).forEach(function (iso) {
          addIncome('drink_sales', iso, maps.drinkByDate[iso]);
        });
        var daily = ensureAnnualDailyStore();
        daily.targetSalesByDate = daily.targetSalesByDate || {};
        daily.businessDayByDate = daily.businessDayByDate || {};
        Object.keys(csvSales).forEach(function (iso) {
          daily.targetSalesByDate[iso] = csvSales[iso];
        });
        Object.keys(csvBiz).forEach(function (iso) {
          daily.businessDayByDate[iso] = csvBiz[iso];
        });
        Object.keys(incomeByYear).forEach(function (y) {
          if (
            window.KpiYearStore &&
            typeof KpiYearStore.bulkPersistMepYear === 'function'
          ) {
            KpiYearStore.bulkPersistMepYear(
              Number(y),
              { dailyIncome: incomeByYear[y] },
              {
                source: 'mep-sales-csv-import',
                forceIncome: true,
                allowLockedYearImport: true,
                deferPersist: true
              }
            );
          }
        });
        if (window.KpiYearStore && typeof KpiYearStore.persistFromAnnualDaily === 'function') {
          return KpiYearStore.persistFromAnnualDaily(
            { targetSalesByDate: csvSales, businessDayByDate: csvBiz },
            { source: 'mep-sales-csv-import', serverRebuild: true }
          );
        }
        if (typeof persistAnnualDailyShared === 'function') {
          return persistAnnualDailyShared({ serverRebuild: true });
        }
        return Promise.resolve();
      }"""

MEP_CSV_BIND_INNER = """window.__KPI_DAILY_IMPORT.bindButton(btnCsvUpload, {
            persistByCsvYear: true,
            getYear: function () { return mefYear; },
            applyMaps: function (maps, year) {
              pushUndo();
              var persistP = persistMepSalesCsvByYear(maps);
              Promise.resolve(persistP).catch(function () {});
              var yShow = Number(mefYear);
              var csvYears = maps.years || [];
              if (csvYears.indexOf(yShow) < 0) return Promise.resolve();
              var applied = applyDailyImportMapsToOpenYear(maps, yShow);
              if (!applied) return Promise.resolve();
              markDirty();
              syncUndoButton();
              buildGrid();
              return Promise.resolve();
            },
          });"""

MEP_APPLY_IMPORT_NEW = """      function applyDailyImportMapsToOpenYear(maps, year) {
        var primary = state.incomeItems && state.incomeItems[0];
        if (!primary || !maps) return 0;
        var yf = Number(year);
        var applied = 0;
        var foodMap = maps.foodByDate || {};
        Object.keys(maps.salesByDate || {}).forEach(function (iso) {
          if (Number.isFinite(yf) && mepIsoYear(iso) !== yf) return;
          if (window.KpiYearStore && !KpiYearStore.canWriteDailySalesFrom('mep-sales-csv-import', iso)) return;
          var bizMapImp = maps.businessDayByDate || {};
          var sales = Number(maps.salesByDate[iso]);
          if (Object.prototype.hasOwnProperty.call(bizMapImp, iso)) {
            bizDayByIso[iso] = !!bizMapImp[iso];
          }
          if (Number.isFinite(sales) && sales > 0) {
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


def upsert_function_before(text: str, helper: str, helper_name: str, next_fn: str) -> str:
    helper_block = helper.rstrip() + "\n\n"
    start_token = f"      function {helper_name}("
    next_token = f"      function {next_fn}("
    start = text.find(start_token)
    nxt = text.find(next_token)
    if start >= 0:
        if nxt < 0 or nxt < start:
            raise SystemExit(f"{next_fn} missing after {helper_name}")
        return text[:start] + helper_block + text[nxt:]
    if nxt < 0:
        raise SystemExit(f"insert anchor missing: {next_fn}")
    return text[:nxt] + helper_block + text[nxt:]


def replace_function_by_signature(text: str, signature: str, new_src: str) -> str | None:
    start = text.find(signature)
    if start < 0:
        return None
    nxt = text.find("\n      function ", start + 1)
    if nxt < 0:
        raise SystemExit(f"next function missing after {signature}")
    return text[:start] + new_src.rstrip() + text[nxt:]


def replace_js_call_object(text: str, call_prefix: str, new_call: str) -> str:
    start = text.find(call_prefix)
    if start < 0:
        return text
    brace = text.find("{", start)
    if brace < 0:
        raise SystemExit("bindButton object missing")
    depth = 0
    for j in range(brace, len(text)):
        ch = text[j]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = j + 1
                if end < len(text) and text[end] == ")":
                    end += 1
                if end < len(text) and text[end] == ";":
                    end += 1
                return text[:start] + new_call + text[end:]
    raise SystemExit("bindButton object unclosed")


def ensure_mep_csv_bind(text: str) -> str:
    return replace_js_call_object(
        text,
        "window.__KPI_DAILY_IMPORT.bindButton(btnCsvUpload, {",
        MEP_CSV_BIND_INNER,
    )


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
    is_ja = "/en/" not in str(path) and "/zh-tw/" not in str(path)
    text = inject_import_js(text)
    text = upsert_function_before(
        text,
        PAST_SALES_CSV_HELPER,
        "persistPastSalesCsvByYear",
        "persistPastSalesShared",
    )
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
    replaced = replace_function_by_signature(
        text,
        "      function applyDailyImportMapsToOpenYear(maps, year) {",
        MEP_APPLY_IMPORT_NEW,
    )
    if replaced is not None:
        return replaced
    if MEP_APPLY_IMPORT_OLD in text:
        return text.replace(MEP_APPLY_IMPORT_OLD, MEP_APPLY_IMPORT_NEW, 1)
    raise SystemExit("patch miss (mep applyDailyImportMaps food/drink)")


def patch_mep_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_ja = "/en/" not in str(path) and "/zh-tw/" not in str(path)
    text = inject_import_js(text)
    text = upsert_function_before(
        text,
        MEP_SALES_CSV_HELPER,
        "persistMepSalesCsvByYear",
        "applyDailyImportMapsToOpenYear",
    )
    text = patch_tooltips(text, is_ja)
    text = patch_mep_apply_food_drink(text)
    text = ensure_mep_csv_bind(text)
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
