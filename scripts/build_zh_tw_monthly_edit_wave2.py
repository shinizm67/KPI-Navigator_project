#!/usr/bin/env python3
"""zh-tw Monthly Edit Wave 2: MEP grid labels, Auto Calc, tooltips, t() i18n.

Wave 1 covered static chrome. This wave makes the MEP daily grid (row labels,
AUTO CALC badge, weather, months/weekdays, dynamic tips) Traditional Chinese.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "monthly" / "edit" / "index.html"

# English (or JA labelJa on EN copy) → Traditional Chinese (TW)
# Prefer terms already used in KPI export / PL zh-tw where they exist.
ROW_LABEL_ZH: dict[str, str] = {
    "INCOME": "收入",
    "Business Day": "營業日",
    "営業日": "營業日",
    "Profit": "利潤",
    "Total Sales": "總營業額",
    "Lunch Sales": "午餐營業額",
    "Dinner Sales": "晚餐營業額",
    "Target Sales": "目標營業額",
    "Difference": "差額",
    "Achievement": "達成率",
    "Customers": "來客數",
    "Lunch Customers": "午餐來客數",
    "Dinner Customers": "晚餐來客數",
    "Avg Spend": "客單價",
    "客単価": "客單價",
    "Lunch Avg Spend": "午餐客單價",
    "ランチ客単価": "午餐客單價",
    "Dinner Avg Spend": "晚餐客單價",
    "ディナー客単価": "晚餐客單價",
    "Number of Groups": "組數",
    "Lunch Groups": "午餐組數",
    "Dinner Groups": "晚餐組數",
    "EXPENSES": "支出",
    "Total Expenses": "支出合計",
    "Fixed": "固定費",
    "Expected": "變動費",
    "WEATHER": "天氣",
    "Daily Notes": "每日備註",
    "日次メモ": "每日備註",
    # weekly memo
    "店舗イベント": "店家活動",
    "Store Event": "店家活動",
    "エリアイベント": "地區活動",
    "Area Event": "地區活動",
    "SNS": "社群媒體",
    "Social Media": "社群媒體",
    "マーケ": "行銷",
    "Marketing": "行銷",
    "プロモ": "促銷轉換",
    "Promo Conversion": "促銷轉換",
    "予約": "預約",
    "Reservation": "預約",
    "メモ": "備註",
    "Memo": "備註",
    "メモ1": "備註1",
    "Memo 1": "備註1",
}

CATALOG_ZH: dict[str, str] = {
    "store_sales": "店面營業額",
    "sales_a": "營業額 A",
    "sales_b": "營業額 B",
    "food_sales": "餐點營業額",
    "drink_sales": "飲料營業額",
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

# English key → zh for t(ja, en) → t(ja, en, zh)
T_ZH: dict[str, str] = {
    "Apply to the table?": "套用到表格嗎？",
    "Import daily sales from CSV or Excel (.xlsx). Optional Food/Drink columns (either side OK).":
        "以 CSV 或 Excel（.xlsx）匯入每日銷售。可選的餐點／飲料欄（左右皆可）。",
    "Could not load the Excel library. Save as CSV and try again.":
        "無法載入 Excel 程式庫。請先存成 CSV 後再試。",
    "The file is empty.": "檔案是空的。",
    "Could not detect columns. Row 1 needs headers such as Date, Store Sales (optional Food Sales / Drink Sales).":
        "無法辨識欄位。第 1 列需要 Date、Store Sales 等標題（可選 Food Sales／Drink Sales）。",
    "No valid date rows found. Check the date column (YYYY-MM-DD, etc.).":
        "找不到有效的日期列。請檢查日期欄（YYYY-MM-DD 等）。",
    "Monthly (MEP)": "月度（MEP）",
    "Annual / Sales Data": "年度／Sales Data",
    "Show summary panel": "顯示摘要面板",
    "Hide summary panel": "隱藏摘要面板",
    "Open below Analyze area": "開啟下方分析區",
    "Close below Analyze area": "關閉下方分析區",
    "Manual entry — type values in the cells": "需手動輸入（請直接在儲存格輸入）",
    "Calculated automatically": "自動計算",
    "Parent minus lunch (auto)": "父列 − 午餐列（自動）",
    "Edit label": "編輯科目名稱",
    "Business Day": "營業日",
    "Business-day input is via Annual / Sales Data": "營業日請透過年度／Sales Data 輸入",
    "Memo saved. Click to open": "已有備註。點擊開啟",
    "You have a memo. Click to view.": "有備註。點擊查看。",
    "Open memo": "開啟備註",
    "Click to open Daily Notes": "點擊開啟每日備註",
    "Weather": "天氣",
    "Weather ": "天氣 ",
    "Store − Food (auto)": "店面 − 餐點（自動）",
    "Daily sales input is via Annual / Sales Data (switch to MEP in settings)":
        "每日銷售請透過年度／Sales Data 輸入（可在設定切換至 MEP）",
    "Enter monthly on PL table": "請在 PL 表以月次輸入",
    "No free memo rows to delete.": "沒有可刪除的自由備註列。",
    "Enter row number to delete:": "請輸入要刪除的列號：",
    "Enter a valid row number.": "請輸入有效的列號。",
    "Delete this row?": "確定要刪除此列嗎？",
    "Edit memo title": "編輯備註標題",
    "Add free memo below": "在下方新增自由備註",
    "Remove this free memo row": "刪除此自由備註列",
    "You have unsaved memos. Close anyway?": "尚有未儲存的備註。仍要關閉嗎？",
}

WEATHER_ZH = {
    "—": "—",
    "Sunny": "晴",
    "Cloudy": "多雲",
    "Rain": "雨",
    "Snow": "雪",
    "Thunder": "雷",
    "Storm": "暴風雨",
}


def patch_locale_and_helpers(text: str) -> str:
    old = (
        "      var useJa = String(document.documentElement.getAttribute('lang') || '').toLowerCase().indexOf('ja') === 0;\n"
        "      var MONTHS_JA = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];\n"
        "      var MONTHS_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];\n"
        "      var WD_JA = ['日', '月', '火', '水', '木', '金', '土'];\n"
        "      var WD_EN = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];\n"
    )
    new = (
        "      var docLang = String(document.documentElement.getAttribute('lang') || '').toLowerCase();\n"
        "      var useZh = docLang.indexOf('zh') === 0;\n"
        "      var useJa = docLang.indexOf('ja') === 0;\n"
        "      var MONTHS_JA = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];\n"
        "      var MONTHS_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];\n"
        "      var MONTHS_ZH = MONTHS_JA;\n"
        "      var WD_JA = ['日', '月', '火', '水', '木', '金', '土'];\n"
        "      var WD_EN = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];\n"
        "      var WD_ZH = ['日', '一', '二', '三', '四', '五', '六'];\n"
    )
    if old not in text:
        raise SystemExit("locale block not found")
    text = text.replace(old, new, 1)

    old_t = "      function t(ja, en) {\n        return useJa ? ja : en;\n      }"
    new_t = (
        "      function t(ja, en, zh) {\n"
        "        if (useZh) return zh != null && zh !== '' ? zh : ja;\n"
        "        return useJa ? ja : en;\n"
        "      }"
    )
    if old_t not in text:
        raise SystemExit("main t() not found")
    text = text.replace(old_t, new_t, 1)

    old_rl = "      function rowLabel(r) {\n        return useJa ? r.labelJa : r.labelEn;\n      }"
    new_rl = (
        "      function rowLabel(r) {\n"
        "        if (useZh) return r.labelZh || r.labelJa || r.labelEn;\n"
        "        return useJa ? r.labelJa : r.labelEn;\n"
        "      }"
    )
    if old_rl not in text:
        raise SystemExit("rowLabel not found")
    text = text.replace(old_rl, new_rl, 1)

    # Nested isJa / t helpers (CSV import + sales-path chooser)
    nested_isja = (
        "        function isJa() {\n"
        "          return (\n"
        "            String(document.documentElement.getAttribute('lang') || '')\n"
        "              .toLowerCase()\n"
        "              .indexOf('ja') === 0\n"
        "          );\n"
        "        }\n\n"
        "        function t(ja, en) {\n"
        "          return isJa() ? ja : en;\n"
        "        }"
    )
    nested_new = (
        "        function isZh() {\n"
        "          return (\n"
        "            String(document.documentElement.getAttribute('lang') || '')\n"
        "              .toLowerCase()\n"
        "              .indexOf('zh') === 0\n"
        "          );\n"
        "        }\n"
        "        function isJa() {\n"
        "          return (\n"
        "            String(document.documentElement.getAttribute('lang') || '')\n"
        "              .toLowerCase()\n"
        "              .indexOf('ja') === 0\n"
        "          );\n"
        "        }\n\n"
        "        function t(ja, en, zh) {\n"
        "          if (isZh()) return zh != null && zh !== '' ? zh : ja;\n"
        "          return isJa() ? ja : en;\n"
        "        }"
    )
    count = text.count(nested_isja)
    if count < 1:
        # try alternate spacing (one occurrence may differ)
        alt = nested_isja.replace("\n\n        function t", "\n        function t")
        if text.count(alt) >= 1:
            text = text.replace(alt, nested_new)
        else:
            raise SystemExit(f"nested isJa/t not found (count={count})")
    else:
        text = text.replace(nested_isja, nested_new)

    return text


def patch_ternaries(text: str) -> str:
    reps = [
        (
            "useJa ? monthsJa : monthsEn",
            "useZh || useJa ? monthsJa : monthsEn",
        ),
        (
            "useJa ? MONTHS_JA[month0] : MONTHS_EN[month0]",
            "useZh ? MONTHS_ZH[month0] : useJa ? MONTHS_JA[month0] : MONTHS_EN[month0]",
        ),
        (
            "useJa ? MONTHS_JA[m] : MONTHS_EN[m]",
            "useZh ? MONTHS_ZH[m] : useJa ? MONTHS_JA[m] : MONTHS_EN[m]",
        ),
        (
            "useJa ? WD_JA[dt.getDay()] : WD_EN[dt.getDay()]",
            "useZh ? WD_ZH[dt.getDay()] : useJa ? WD_JA[dt.getDay()] : WD_EN[dt.getDay()]",
        ),
        (
            "useJa ? r.labelJa : r.labelEn",
            "useZh ? (r.labelZh || r.labelJa || r.labelEn) : useJa ? r.labelJa : r.labelEn",
        ),
        (
            "useJa ? preset.ja : preset.en",
            "useZh ? (preset.zh || preset.ja) : useJa ? preset.ja : preset.en",
        ),
        (
            "useJa ? MEF_WEATHER_PRESETS[wi].ja : MEF_WEATHER_PRESETS[wi].en",
            "useZh ? (MEF_WEATHER_PRESETS[wi].zh || MEF_WEATHER_PRESETS[wi].ja) : useJa ? MEF_WEATHER_PRESETS[wi].ja : MEF_WEATHER_PRESETS[wi].en",
        ),
        ("useJa ? 8 : 12", "(useJa || useZh) ? 8 : 12"),
        (
            "return useJa\n          ? { hard: 300, tiers: [200, 300] }\n          : { hard: 500, tiers: [200, 300, 500] };",
            "return (useJa || useZh)\n          ? { hard: 300, tiers: [200, 300] }\n          : { hard: 500, tiers: [200, 300, 500] };",
        ),
        (
            "          var lockedMsg = useJa\n"
            "            ? 'メモを保存できませんでした（年がロックされているか、ストアが未準備です）。'\n"
            "            : 'Could not save memos (year may be locked, or store is not ready).';",
            "          var lockedMsg = useZh\n"
            "            ? '無法儲存備註（年度可能已鎖定，或資料尚未就緒）。'\n"
            "            : useJa\n"
            "            ? 'メモを保存できませんでした（年がロックされているか、ストアが未準備です）。'\n"
            "            : 'Could not save memos (year may be locked, or store is not ready).';",
        ),
        ("prefix.textContent = 'Auto Calc';", "prefix.textContent = t('自動計算', 'Auto Calc', '自動計算');"),
    ]
    for a, b in reps:
        if a not in text:
            print("WARN missing ternary/patch:", repr(a[:70]))
            continue
        text = text.replace(a, b)
    return text


def patch_weather_presets(text: str) -> str:
    # Expand { code, ja, en } → add zh
    def repl(m: re.Match[str]) -> str:
        code, ja, en = m.group(1), m.group(2), m.group(3)
        zh = WEATHER_ZH.get(en, WEATHER_ZH.get(ja, ja))
        return f"{{ code: '{code}', ja: '{ja}', en: '{en}', zh: '{zh}' }}"

    pat = re.compile(
        r"\{ code: '((?:\\'|[^'])*)', ja: '((?:\\'|[^'])*)', en: '((?:\\'|[^'])*)' \}"
    )
    new_text, n = pat.subn(repl, text)
    if n < 5:
        print("WARN weather presets replaced:", n)
    return new_text


def patch_catalog_labels(text: str) -> str:
    m = re.search(r"var PL_LINE_CATALOG = (\[[\s\S]*?\]);\n\s*var PL_CATALOG_BY_ID", text)
    if not m:
        raise SystemExit("PL_LINE_CATALOG not found")
    catalog = json.loads(m.group(1))
    for e in catalog:
        lid = e.get("lineId")
        if lid in CATALOG_ZH:
            e["labelJa"] = CATALOG_ZH[lid]
            e["labelZh"] = CATALOG_ZH[lid]
    # keep pretty-ish dump similar to source (2-space indent inside)
    dumped = json.dumps(catalog, ensure_ascii=False, indent=2)
    # indent each line by 2 spaces to sit inside script
    dumped = "\n".join(("  " + line if line else line) for line in dumped.splitlines())
    text = text[: m.start(1)] + dumped + text[m.end(1) :]
    return text


def patch_static_row_labels(text: str) -> str:
    """Rewrite labelJa: '…' when the English twin is known, inside currentRows / weekly defs."""

    def repl_pair(m: re.Match[str]) -> str:
        ja, en = m.group(1), m.group(2)
        zh = ROW_LABEL_ZH.get(en) or ROW_LABEL_ZH.get(ja)
        if not zh:
            return m.group(0)
        return f"labelJa: '{zh}',\n          labelEn: '{en}'"

    # multiline form used in currentRows
    text2 = re.sub(
        r"labelJa: '((?:\\'|[^'])*)',\s*\n(\s*)labelEn: '((?:\\'|[^'])*)'",
        lambda m: (
            f"labelJa: '{ROW_LABEL_ZH.get(m.group(3)) or ROW_LABEL_ZH.get(m.group(1)) or m.group(1)}',\n"
            f"{m.group(2)}labelEn: '{m.group(3)}'"
            if (ROW_LABEL_ZH.get(m.group(3)) or ROW_LABEL_ZH.get(m.group(1)))
            else m.group(0)
        ),
        text,
    )

    # single-line group pushes: labelJa: 'X', labelEn: 'Y'
    def repl_one(m: re.Match[str]) -> str:
        ja, en = m.group(1), m.group(2)
        zh = ROW_LABEL_ZH.get(en) or ROW_LABEL_ZH.get(ja)
        if not zh:
            return m.group(0)
        return f"labelJa: '{zh}', labelEn: '{en}'"

    text2 = re.sub(
        r"labelJa: '((?:\\'|[^'])*)', labelEn: '((?:\\'|[^'])*)'",
        repl_one,
        text2,
    )

    # makeRow('memo', 'メモ1', 'Memo 1' ...) defaults
    text2 = text2.replace(
        "state.memoItems.push(makeRow('memo', 'メモ1', 'Memo 1', { editableLabel: true, deletable: true }));",
        "state.memoItems.push(makeRow('memo', '備註1', 'Memo 1', { editableLabel: true, deletable: true }));",
    )
    text2 = text2.replace(
        "makeRow('memo', 'メモ', 'Memo', { editableLabel: true, deletable: true })",
        "makeRow('memo', '備註', 'Memo', { editableLabel: true, deletable: true })",
    )
    # renumber free memo
    text2 = text2.replace(
        "if (isAutoMemoLabelJa(row.labelJa)) row.labelJa = n === 1 ? 'メモ' : 'メモ' + n;",
        "if (isAutoMemoLabelJa(row.labelJa)) row.labelJa = n === 1 ? '備註' : '備註' + n;",
    )
    # expand isAutoMemoLabelJa to accept 備註
    old_auto = "return /^メモ\\d*$/.test(String(label || '').trim());"
    new_auto = "return /^(メモ|備註)\\d*$/.test(String(label || '').trim());"
    if old_auto in text2:
        text2 = text2.replace(old_auto, new_auto, 1)
    return text2


def patch_t_calls(text: str) -> str:
    """Expand t('ja','en') → t('ja','en','zh') using T_ZH keyed by en."""

    def repl(m: re.Match[str]) -> str:
        ja, en = m.group(1), m.group(2)
        # skip if already 3-arg (next char is comma) — regex shouldn't match
        zh = T_ZH.get(en)
        if zh is None:
            return m.group(0)
        # escape for JS single-quoted string
        zh_esc = zh.replace("\\", "\\\\").replace("'", "\\'")
        return f"t('{ja}', '{en}', '{zh_esc}')"

    # Only 2-arg calls (no third arg yet)
    pat = re.compile(r"\bt\(\s*'((?:\\'|[^'])*)'\s*,\s*'((?:\\'|[^'])*)'\s*\)")
    return pat.sub(repl, text)


def verify(text: str) -> None:
    checks = [
        ("useZh", "var useZh =" in text),
        ("t 3-arg main", "if (useZh) return zh != null" in text),
        ("rowLabel zh", "if (useZh) return r.labelZh || r.labelJa" in text),
        ("Auto Calc i18n", "prefix.textContent = t('自動計算'" in text),
        ("總營業額", "總營業額" in text),
        ("營業日", "營業日" in text),
        ("店面營業額", "店面營業額" in text),
        ("午餐營業額", "午餐營業額" in text),
        ("自動計算 tip", "'自動計算'" in text),
        ("weather zh", "zh: '晴'" in text),
        ("WD_ZH", "var WD_ZH =" in text),
    ]
    for name, ok in checks:
        print(("OK" if ok else "FAIL"), name)
        if not ok:
            raise SystemExit(1)
    # leftover English static labels in currentRows should be gone from labelJa
    m = re.search(r"function currentRows\(\) \{[\s\S]*?\n      \}", text)
    if not m:
        raise SystemExit("currentRows missing")
    block = m.group(0)
    for bad in ["labelJa: 'INCOME'", "labelJa: 'Total Sales'", "labelJa: 'Profit'", "labelJa: 'Business Day'"]:
        if bad in block:
            raise SystemExit(f"still English in currentRows: {bad}")
    print("verify: ALL OK")


def patch_remaining_helpers(text: str) -> str:
    """Sales-path UI + edit-lease messages (may differ slightly from nested CSV block)."""
    old_path = (
        "      /* KPI-SALES-INPUT-PATH-UI */\n"
        "      (function () {\n"
        "        function storeReady() {\n"
        "          return !!(window.KpiYearStore && KpiYearStore.getDailySalesInputPath);\n"
        "        }\n"
        "        function isJa() {\n"
        "          return (\n"
        "            String(document.documentElement.getAttribute('lang') || '')\n"
        "              .toLowerCase()\n"
        "              .indexOf('ja') === 0\n"
        "          );\n"
        "        }\n"
        "        function t(ja, en) {\n"
        "          return isJa() ? ja : en;\n"
        "        }"
    )
    new_path = (
        "      /* KPI-SALES-INPUT-PATH-UI */\n"
        "      (function () {\n"
        "        function storeReady() {\n"
        "          return !!(window.KpiYearStore && KpiYearStore.getDailySalesInputPath);\n"
        "        }\n"
        "        function isZh() {\n"
        "          return (\n"
        "            String(document.documentElement.getAttribute('lang') || '')\n"
        "              .toLowerCase()\n"
        "              .indexOf('zh') === 0\n"
        "          );\n"
        "        }\n"
        "        function isJa() {\n"
        "          return (\n"
        "            String(document.documentElement.getAttribute('lang') || '')\n"
        "              .toLowerCase()\n"
        "              .indexOf('ja') === 0\n"
        "          );\n"
        "        }\n"
        "        function t(ja, en, zh) {\n"
        "          if (isZh()) return zh != null && zh !== '' ? zh : ja;\n"
        "          return isJa() ? ja : en;\n"
        "        }"
    )
    if old_path in text:
        text = text.replace(old_path, new_path, 1)
    elif "KPI-SALES-INPUT-PATH-UI" in text and "function isZh()" in text[text.find("KPI-SALES-INPUT-PATH-UI"):text.find("KPI-SALES-INPUT-PATH-UI")+800]:
        print("sales-path UI already has isZh")
    else:
        print("WARN sales-path UI helper not patched")

    old_lease = (
        "        function isJa() {\n"
        "          return (\n"
        "            String(document.documentElement.getAttribute('lang') || '')\n"
        "              .toLowerCase()\n"
        "              .indexOf('ja') === 0\n"
        "          );\n"
        "        }\n"
        "        function leaseConflictMessage(holder) {\n"
        "          var label = (holder && holder.label) || (isJa() ? '別タブ' : 'another tab');\n"
        "          return isJa()\n"
        "            ? '「' + label + '」が別タブで編集中です。閲覧のみ可能です。'\n"
        "            : '\"' + label + '\" is being edited in another tab. This view is read-only.';\n"
        "        }"
    )
    new_lease = (
        "        function isZh() {\n"
        "          return (\n"
        "            String(document.documentElement.getAttribute('lang') || '')\n"
        "              .toLowerCase()\n"
        "              .indexOf('zh') === 0\n"
        "          );\n"
        "        }\n"
        "        function isJa() {\n"
        "          return (\n"
        "            String(document.documentElement.getAttribute('lang') || '')\n"
        "              .toLowerCase()\n"
        "              .indexOf('ja') === 0\n"
        "          );\n"
        "        }\n"
        "        function leaseConflictMessage(holder) {\n"
        "          var label =\n"
        "            (holder && holder.label) ||\n"
        "            (isZh() ? '其他分頁' : isJa() ? '別タブ' : 'another tab');\n"
        "          if (isZh()) {\n"
        "            return '「' + label + '」正在其他分頁編輯中。此畫面僅可瀏覽。';\n"
        "          }\n"
        "          return isJa()\n"
        "            ? '「' + label + '」が別タブで編集中です。閲覧のみ可能です。'\n"
        "            : '\"' + label + '\" is being edited in another tab. This view is read-only.';\n"
        "        }"
    )
    if old_lease in text:
        text = text.replace(old_lease, new_lease, 1)
    elif "正在其他分頁編輯中" in text:
        print("lease conflict already zh")
    else:
        print("WARN lease conflict not patched")
    return text


def main() -> None:
    if not DST.is_file():
        raise SystemExit(f"missing {DST}")
    text = DST.read_text(encoding="utf-8")
    if "KPI-MEP-ZH-TW-WAVE2" in text:
        print("wave2 marker present — applying remaining helper patches only")
        text = patch_remaining_helpers(text)
        DST.write_text(text, encoding="utf-8")
        verify(DST.read_text(encoding="utf-8"))
        print("build_zh_tw_monthly_edit_wave2: OK (incremental)")
        return

    text = patch_locale_and_helpers(text)
    text = patch_ternaries(text)
    text = patch_weather_presets(text)
    text = patch_catalog_labels(text)
    text = patch_static_row_labels(text)
    text = patch_t_calls(text)
    text = patch_remaining_helpers(text)

    # marker near locale block
    text = text.replace(
        "      var useZh = docLang.indexOf('zh') === 0;\n",
        "      /* KPI-MEP-ZH-TW-WAVE2 */\n      var useZh = docLang.indexOf('zh') === 0;\n",
        1,
    )

    DST.write_text(text, encoding="utf-8")
    verify(DST.read_text(encoding="utf-8"))
    print("build_zh_tw_monthly_edit_wave2: OK")


if __name__ == "__main__":
    main()
