#!/usr/bin/env python3
"""zh-tw Profit PL Wave 2: table row labels, catalog, Insight L dict, locale helpers.

Wave 1 covered chrome/toolbar. This wave localizes the PL grid itself (income /
expense / analyze labels), expense catalog defaults, graph/Insight strings, and
makes runtime label selection treat zh-TW like CJK (labelJa path) while keeping $ money.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "profit" / "pl" / "index.html"

# Align with MEP wave2 / export zh where possible
CATALOG_ZH: dict[str, str] = {
    "exp_rent": "租金",
    "exp_fixed_asset_tax": "固定資產稅",
    "exp_fixed_labor": "固定人事費用",
    "exp_lease": "租賃費",
    "exp_depreciable_asset_tax": "折舊資產稅",
    "exp_depreciation": "折舊費用",
    "exp_non_life_insurance": "產物保險",
    "exp_social_insurance": "社會保險",
    "exp_food_cost": "食材進貨成本",
    "exp_drink_cost": "飲料進貨成本",
    "exp_supplies": "備品／消耗品進貨",
    "exp_misc": "雜費／零用金",
    "exp_electric": "電費",
    "exp_gas": "瓦斯費",
    "exp_water": "水費",
    "exp_variable_labor": "工讀／臨時人事費用",
    "exp_telecom": "通訊費",
    "exp_advertising": "廣告宣傳費",
    "exp_uniforms": "制服／工作服",
    "exp_payment_fees": "信用卡手續費",
    "exp_employment_insurance": "就業保險",
    "exp_workers_comp": "職災保險",
    "exp_consumption_tax": "消費稅",
}

# data-label-id / static row text replacements (exact visible text)
HTML_LABEL_BY_ID: dict[str, str] = {
    "store_sales": "店面營業額",
    "sales_a": "營業額 A",
    "sales_b": "營業額 B",
    "expense_fixed": "固定費",
    "expense_expected": "變動費",
    "analyze_food_sales": "餐點營業額",
    "analyze_food_cost": "餐點進貨成本",
    "analyze_drink_sales": "飲料營業額",
    "analyze_drink_cost": "飲料進貨成本",
    "analyze_labor_employee": "正職人事費用",
    "analyze_labor_pt": "工讀／兼職工資",
    "analyze_monthly_food": "月度餐點支出",
    "analyze_monthly_labor": "月度人事費用",
}

STATIC_TEXT: list[tuple[str, str]] = [
    (
        'aria-label="Show this month in the PL table">▶ View month in table</button>',
        'aria-label="在 PL 表顯示此月">▶ 在表中查看此月</button>',
    ),
    ('aria-label="Compare areas"', 'aria-label="比較區域"'),
    (
        'data-pl-compare-jump="pl-compare-area-1">Area 1</button>',
        'data-pl-compare-jump="pl-compare-area-1">區域 1</button>',
    ),
    (
        'data-pl-compare-jump="pl-compare-area-2">Area 2</button>',
        'data-pl-compare-jump="pl-compare-area-2">區域 2</button>',
    ),
    (
        'data-pl-compare-jump="pl-compare-area-3">Area 3</button>',
        'data-pl-compare-jump="pl-compare-area-3">區域 3</button>',
    ),
    ('>Area 1. 當日 FL 快照</h3>', '>區域 1. 當日 FL 快照</h3>'),
    ('>Area 2. 去年同月 FL 快照</h3>', '>區域 2. 去年同月 FL 快照</h3>'),
    ('>Area 3. 年初至今 FL 快照</h3>', '>區域 3. 年初至今 FL 快照</h3>'),
    (">Total Sales</span>", ">總營業額</span>"),
    (
        'data-row="analyze_labor_total"><th scope="row" class="pl-h-label pl-h-label--total"><span class="pl-h-label__text">Total</span></th></tr>',
        'data-row="analyze_labor_total"><th scope="row" class="pl-h-label pl-h-label--total"><span class="pl-h-label__text">合計</span></th></tr>',
    ),
    (
        'data-row="analyze_fl_total"><th scope="row" class="pl-h-label pl-h-label--total"><span class="pl-h-label__text">Total</span></th></tr>',
        'data-row="analyze_fl_total"><th scope="row" class="pl-h-label pl-h-label--total"><span class="pl-h-label__text">合計</span></th></tr>',
    ),
    (">Expected</span>", ">變動費</span>"),
    (">Variable expense guideline</span>", ">變動費參考區間</span>"),
    (
        'title="Guideline for variable spend = target cost rate minus fixed-cost rate (not a prescribed ideal)"',
        'title="變動費目安＝目標總費率 − 固定費率（非強制標準值）"',
    ),
    (">Food cost</span>", ">餐點成本</span>"),
    (">Labor</span>", ">人事</span>"),
    (">share</span>", ">占比</span>"),
    (">Food &amp; Labor</span>", ">餐點與人事</span>"),
    (">Food & Labor</span>", ">餐點與人事</span>"),
    ('aria-label="Edit label (double-click or F2)"', 'aria-label="編輯科目名稱（雙擊或 F2）"'),
    (
        'aria-label="Show per-line reference budget"',
        'aria-label="顯示各科目參考預算"',
    ),
    (
        'data-tooltip="+ Show per-line reference budget (guideline). Median of your past ratios × this month\'s sales flags likely overspending per cell (not a prescribed ideal)."',
        'data-tooltip="+ 顯示各科目參考預算（尺規）。以過去比率中位數 × 本月營業額標示可能超支（非強制標準值）。"',
    ),
    (
        'aria-label="Upload Expenses"',
        'aria-label="匯入支出"',
    ),
    (
        'title="Import expenses from CSV/Excel (.xlsx). Download a template from "DL" (top-right); item names must match the catalog labels."',
        'title="以 CSV/Excel（.xlsx）匯入支出。範本可從右上「DL」下載；科目名稱請與目錄標籤一致。"',
    ),
    (
        'data-tooltip="Import expenses from CSV/Excel (.xlsx). Download a template from "DL" (top-right); item names must match the catalog labels."',
        'data-tooltip="以 CSV/Excel（.xlsx）匯入支出。範本可從右上「DL」下載；科目名稱請與目錄標籤一致。"',
    ),
    ('aria-label="Undo"', 'aria-label="復原"'),
    (
        'aria-label="Show attribute edit buttons for fixed and variable expenses"',
        'aria-label="顯示固定費／變動費的屬性編輯按鈕"',
    ),
    # JS string constants for mid labels / occupancy
    ('var midFixed = "Fixed";', 'var midFixed = "固定費";'),
    ('var midVar = "Expected";', 'var midVar = "變動費";'),
    ('var midVar = "Variable";', 'var midVar = "變動費";'),
    ('var occupancyRentOption = "Rented";', 'var occupancyRentOption = "租賃";'),
    ('var occupancyOwnedOption = "Owned";', 'var occupancyOwnedOption = "自有";'),
    # graph LABELS object
    (
        """      var LABELS = {
        band: "Graph",
        monthlySales: "Monthly Sales",
        income: "Income",
        expenses: "Expenses",
        fixed: "Fixed",
        expected: "Expected",
        yearTotal: "Annual",
      };""",
        """      var LABELS = {
        band: "圖表",
        monthlySales: "月度營業額",
        income: "收入",
        expenses: "支出",
        fixed: "固定費",
        expected: "變動費",
        yearTotal: "年度",
      };""",
    ),
    # MONTHS English names in graph block
    (
        'var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];',
        'var MONTHS = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"];',
    ),
]

L_ZH: dict[str, str] = {
    "compare_prev_day_aria": "前一天",
    "compare_next_day_aria": "後一天",
    "compare_date_pick_aria": "選擇日期",
    "compare_today": "今天",
    "compare_income": "收入",
    "compare_expenses": "支出",
    "compare_profit": "利潤",
    "compare_area1_title": "區域 1. 當日 FL 快照",
    "compare_area2_title": "區域 2. 去年同月 FL 快照",
    "compare_area3_title": "區域 3. 年初至今 FL 快照",
    "compare_food_labor": "餐點與人事",
    "compare_food_slash_labor": "餐點／人事",
    "compare_same_weekday_of": "同星期 ",
    "compare_area2_hsnap_primary": "去年同月 ",
    "compare_area2_hsnap_secondary": "前年同月 ",
    "compare_area3_hsnap_primary": "年初至今 ",
    "compare_area3_hsnap_secondary": "去年年初至今 ",
    "compare_no_data": "無資料",
    "compare_line_title": "與去年同星期累積進度比較",
    "compare_area2_line_title": "與去年同月累積進度比較",
    "compare_area3_line_title": "與年初至今累積進度比較",
    "compare_this_year": "今年",
    "compare_last_year": "去年",
    "compare_best_year": "最佳年度",
    "compare_fixed": "固定費",
    "compare_expected": "變動費",
    "compare_daily_title": "每日表現",
    "compare_area2_daily_title": "每日表現",
    "compare_area3_daily_title": "月度表現",
    "compare_breakdown_toggle": "支出明細",
    "compare_breakdown_fixed": "固定費",
    "compare_breakdown_variable": "變動費",
    "compare_breakdown_total": "支出合計",
    "compare_breakdown_none": "本月沒有支出科目資料",
    "compare_breakdown_jump_daily": "在月度編輯開啟此科目",
    "compare_breakdown_jump_monthly": "在 PL 表開啟此科目",
    "compare_plan_lock_cta": "專業方案限定。點擊前往變更方案。",
}


def patch_label_by_id(text: str) -> str:
    for lid, zh in HTML_LABEL_BY_ID.items():
        # editable span with data-label-id
        pat = re.compile(
            rf'(data-label-id="{re.escape(lid)}"[^>]*>)([^<]+)(</span>)'
        )
        text, n = pat.subn(rf"\g<1>{zh}\g<3>", text)
        if n == 0:
            print(f"WARN no data-label-id match for {lid}")
    return text


def patch_catalog_json(text: str) -> str:
    """Rewrite labelJa inside DEFAULT_CATALOG_LINES / DEFAULT_LINES JSON arrays."""

    def rewrite_array(raw: str) -> str:
        arr = json.loads(raw)
        for e in arr:
            lid = e.get("lineId")
            if lid in CATALOG_ZH:
                e["labelJa"] = CATALOG_ZH[lid]
                e["labelZh"] = CATALOG_ZH[lid]
        return json.dumps(arr, ensure_ascii=False, separators=(",", ": "))

    for var in ("DEFAULT_CATALOG_LINES", "DEFAULT_LINES"):
        m = re.search(rf"var {var} = (\[[\s\S]*?\]);", text)
        if not m:
            print(f"WARN missing {var}")
            continue
        text = text[: m.start(1)] + rewrite_array(m.group(1)) + text[m.end(1) :]
        print(f"patched {var}")
    return text


def patch_l_object(text: str) -> str:
    m = re.search(r"var L = (\{.*?\});", text)
    if not m:
        raise SystemExit("var L = {...} not found")
    L = json.loads(m.group(1))
    for k, v in L_ZH.items():
        if k in L:
            L[k] = v
        else:
            print(f"WARN L missing key {k}")
    dumped = json.dumps(L, ensure_ascii=False, separators=(", ", ": "))
    return text[: m.start(1)] + dumped + text[m.end(1) :]


def patch_locale_helpers(text: str) -> str:
    """Make label paths use Chinese via labelJa when lang is zh-TW; keep $ for money."""
    marker = "/* KPI-PL-ZH-TW-WAVE2 */"
    if marker in text:
        print("locale helpers already marked")
        return text

    # Common pattern at start of catalog / label IIFEs
    old = "var isJa = document.documentElement.lang === 'ja';"
    new = (
        f"{marker}\n"
        "      var docLang = String(document.documentElement.lang || '').toLowerCase();\n"
        "      var isZh = docLang.indexOf('zh') === 0;\n"
        "      var isJa = docLang.indexOf('ja') === 0;\n"
        "      var useJaLabels = isJa || isZh;"
    )
    count = text.count(old)
    if count < 1:
        raise SystemExit("isJa init not found")
    text = text.replace(old, new)
    print(f"patched isJa init x{count}")

    # Label selection ternaries that should use useJaLabels
    # Careful: money formatters must stay on isJa only.
    label_reps = [
        (
            "el.textContent = isJa ? (c.labelJa || el.textContent) : (c.labelEn || el.textContent);",
            "el.textContent = useJaLabels ? (c.labelJa || el.textContent) : (c.labelEn || el.textContent);",
        ),
        (
            "el.textContent = isJa ? (o.labelJa || el.textContent) : (o.labelEn || el.textContent);",
            "el.textContent = useJaLabels ? (o.labelJa || el.textContent) : (o.labelEn || el.textContent);",
        ),
        (
            "if (isJa) overrides[id].labelJa = next;\n        else overrides[id].labelEn = next;",
            "if (useJaLabels) overrides[id].labelJa = next;\n        else overrides[id].labelEn = next;",
        ),
        (
            "var bdIsJa = document.documentElement.lang === 'ja';",
            "var bdDocLang = String(document.documentElement.lang || '').toLowerCase();\n"
            "      var bdIsZh = bdDocLang.indexOf('zh') === 0;\n"
            "      var bdIsJa = bdDocLang.indexOf('ja') === 0;",
        ),
        (
            "        if (bdIsJa) return year + '年' + (month0 + 1) + '月';",
            "        if (bdIsJa || bdIsZh) return year + '年' + (month0 + 1) + '月';",
        ),
        (
            "          var label = bdIsJa ? r.labelJa : r.labelEn;",
            "          var label = (bdIsJa || bdIsZh) ? r.labelJa : r.labelEn;",
        ),
    ]
    for a, b in label_reps:
        if a not in text:
            print("WARN missing label patch:", repr(a[:70]))
            continue
        text = text.replace(a, b)

    # return document.documentElement.lang === 'ja' helpers used for labels
    text = text.replace(
        "          return document.documentElement.lang === 'ja';",
        "          var lg = String(document.documentElement.lang || '').toLowerCase();\n"
        "          return lg.indexOf('ja') === 0 || lg.indexOf('zh') === 0;",
    )

    # CJK font for zh-TW table labels (mirror ja)
    if "html[lang='zh-TW'] .pl-table--v1 .pl-h-label__text" not in text:
        text = text.replace(
            "    html[lang='ja'] .pl-table--v1 .pl-h-label__text {\n"
            "      font-family: 'BIZ UDPGothic', sans-serif;\n"
            "    }",
            "    html[lang='ja'] .pl-table--v1 .pl-h-label__text,\n"
            "    html[lang='zh-TW'] .pl-table--v1 .pl-h-label__text,\n"
            "    html[lang^='zh'] .pl-table--v1 .pl-h-label__text {\n"
            "      font-family: 'BIZ UDPGothic', sans-serif;\n"
            "    }",
            1,
        )
        text = text.replace(
            "    html[lang='ja'] .pl-table--v1 .pl-v-major__text {\n"
            "      font-family: 'BIZ UDPGothic', sans-serif;\n"
            "    }",
            "    html[lang='ja'] .pl-table--v1 .pl-v-major__text,\n"
            "    html[lang='zh-TW'] .pl-table--v1 .pl-v-major__text,\n"
            "    html[lang^='zh'] .pl-table--v1 .pl-v-major__text {\n"
            "      font-family: 'BIZ UDPGothic', sans-serif;\n"
            "    }",
            1,
        )
    return text


def patch_expense_detail_runtime(text: str) -> str:
    """Expense-detail rows use labelText(isJa); zh must use useJaLabels + refresh defaults."""
    old_lt = (
        "      function labelText(line) {\n"
        "        return isJa ? line.labelJa : line.labelEn;\n"
        "      }"
    )
    new_lt = (
        "      function labelText(line) {\n"
        "        if (useJaLabels) return line.labelZh || line.labelJa || line.labelEn;\n"
        "        return line.labelEn || line.labelJa;\n"
        "      }"
    )
    if old_lt in text:
        text = text.replace(old_lt, new_lt, 1)
    elif "if (useJaLabels) return line.labelZh" in text:
        print("labelText already patched")
    else:
        print("WARN labelText not patched")

    old_rec = (
        "          if (prev) {\n"
        "            if (typeof prev.active === 'boolean') line.active = prev.active;\n"
        "            if (typeof prev.sortOrder === 'number') line.sortOrder = prev.sortOrder;\n"
        "            if (prev.labelJa) line.labelJa = prev.labelJa;\n"
        "            if (prev.labelEn) line.labelEn = prev.labelEn;\n"
        "            if (prev.expenseAttribute) line.expenseAttribute = prev.expenseAttribute;"
    )
    new_rec = (
        "          if (prev) {\n"
        "            if (typeof prev.active === 'boolean') line.active = prev.active;\n"
        "            if (typeof prev.sortOrder === 'number') line.sortOrder = prev.sortOrder;\n"
        "            if (isZh) {\n"
        "              /* zh-TW: keep Chinese defaults for built-in lines (ignore stale EN/JA localStorage labels) */\n"
        "              line.labelJa = def.labelJa;\n"
        "              if (def.labelZh) line.labelZh = def.labelZh;\n"
        "              line.labelEn = def.labelEn;\n"
        "            } else {\n"
        "              if (prev.labelJa) line.labelJa = prev.labelJa;\n"
        "              if (prev.labelEn) line.labelEn = prev.labelEn;\n"
        "            }\n"
        "            if (prev.expenseAttribute) line.expenseAttribute = prev.expenseAttribute;"
    )
    if old_rec in text:
        text = text.replace(old_rec, new_rec, 1)
    elif "zh-TW: keep Chinese defaults" in text:
        print("reconcile already patched")
    else:
        print("WARN reconcile not patched")

    text = text.replace(
        "              previousLabel: isJa ? prevJa : prevEn,",
        "              previousLabel: useJaLabels ? prevJa : prevEn,",
    )
    text = text.replace(
        "        if (isJa) line.labelJa = next;\n        else line.labelEn = next;",
        "        if (useJaLabels) line.labelJa = next;\n        else line.labelEn = next;",
    )

    detail_ui = [
        (
            'var variableMidEditTip = "Double-click a line label to rename it and change the input location (Monthly / Daily).";',
            'var variableMidEditTip = "雙擊科目名稱可重新命名，並切換輸入位置（月次／日次）。";',
        ),
        ('var addAria = "Add row";', 'var addAria = "新增列";'),
        ('var hideAria = "Hide row";', 'var hideAria = "隱藏列";'),
        ('var hideConfirmTitle = "Hide this line?";', 'var hideConfirmTitle = "要隱藏此科目嗎？";'),
        (
            'var hideConfirmBodyTpl = "Hide \\"{label}\\". Past data will be kept.";',
            'var hideConfirmBodyTpl = "將隱藏「{label}」。過去資料會保留。";',
        ),
        ('var hideConfirmOk = "Hide";', 'var hideConfirmOk = "隱藏";'),
        ('var hideConfirmCancel = "Cancel";', 'var hideConfirmCancel = "取消";'),
        ('var deleteConfirmTitle = "Delete this row?";', 'var deleteConfirmTitle = "要刪除此列嗎？";'),
        (
            'var deleteConfirmBodyTpl = "Delete “{label}”. This cannot be undone.";',
            'var deleteConfirmBodyTpl = "將刪除「{label}」。此操作無法復原。";',
        ),
        ('var deleteConfirmOk = "Delete";', 'var deleteConfirmOk = "刪除";'),
        ('var lineManageTitle = "Hidden expense lines";', 'var lineManageTitle = "已隱藏的支出科目";'),
        ('var lineManageEmpty = "No hidden lines";', 'var lineManageEmpty = "沒有已隱藏的科目";'),
        ('var lineManageRestore = "Restore";', 'var lineManageRestore = "還原";'),
        ('var lineManageClose = "Close";', 'var lineManageClose = "關閉";'),
        ('var moveUpAria = "Move row up";', 'var moveUpAria = "上移";'),
        ('var moveDownAria = "Move row down";', 'var moveDownAria = "下移";'),
        ('var newRowLabel = "New item";', 'var newRowLabel = "新增科目";'),
        (
            'var labelEditAria = "Edit label (double-click or F2)";',
            'var labelEditAria = "編輯科目名稱（雙擊或 F2）";',
        ),
        (
            'var attributeAddTitle = "Select an expense attribute for this line";',
            'var attributeAddTitle = "請選擇此科目的屬性";',
        ),
        (
            'var attributeVariableAddTitle = "Select a variable expense attribute for this line";',
            'var attributeVariableAddTitle = "請選擇此變動費科目的屬性";',
        ),
        ('var attributeEditTitle = "Change attribute";', 'var attributeEditTitle = "變更屬性";'),
        ('var attributeBtnLabel = "Attr";', 'var attributeBtnLabel = "屬性";'),
        (
            'var attributeBtnAria = "Change expense attribute";',
            'var attributeBtnAria = "變更支出屬性";',
        ),
        ('var occupancyAria = "Occupancy";', 'var occupancyAria = "物件形態";'),
    ]
    for a, b in detail_ui:
        if a in text:
            text = text.replace(a, b, 1)
    return text


def verify(text: str) -> None:
    checks = [
        ("wave2 marker", "KPI-PL-ZH-TW-WAVE2" in text),
        ("店面營業額", "店面營業額" in text),
        ("總營業額", "總營業額" in text),
        ("變動費", "變動費" in text),
        ("餐點營業額", "餐點營業額" in text),
        ("租金 catalog", '"labelJa": "租金"' in text or '"labelJa":"租金"' in text),
        ("L 今天", '"compare_today": "今天"' in text or '"compare_today":"今天"' in text),
        ("useJaLabels", "useJaLabels" in text),
        ("labelText zh", "line.labelZh || line.labelJa" in text),
        ("reconcile zh defaults", "zh-TW: keep Chinese defaults" in text),
        ("Attr→屬性", 'attributeBtnLabel = "屬性"' in text),
        ("no Store Sales label", ">Store Sales<" not in text),
        ("no Total Sales label", ">Total Sales<" not in text),
    ]
    for name, ok in checks:
        print(("OK" if ok else "FAIL"), name)
        if not ok:
            raise SystemExit(1)
    print("verify: ALL OK")


def main() -> None:
    if not DST.is_file():
        raise SystemExit(f"missing {DST}")
    text = DST.read_text(encoding="utf-8")
    if "KPI-PL-ZH-TW-WAVE2" in text and ">店面營業額<" in text:
        print("wave2 base present — ensuring expense-detail runtime patches")
        text = patch_expense_detail_runtime(text)
        DST.write_text(text, encoding="utf-8")
        verify(DST.read_text(encoding="utf-8"))
        print("build_zh_tw_profit_pl_wave2: OK (incremental)")
        return

    for a, b in STATIC_TEXT:
        if a not in text:
            print("WARN missing static:", repr(a[:80]))
            continue
        text = text.replace(a, b)

    text = patch_label_by_id(text)
    text = patch_catalog_json(text)
    text = patch_l_object(text)
    text = patch_locale_helpers(text)
    text = patch_expense_detail_runtime(text)

    DST.write_text(text, encoding="utf-8")
    verify(DST.read_text(encoding="utf-8"))
    print("build_zh_tw_profit_pl_wave2: OK")


if __name__ == "__main__":
    main()
