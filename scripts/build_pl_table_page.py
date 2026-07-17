#!/usr/bin/env python3
"""Generate JA/EN PL table mock pages from embedded template."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from kpi_leave_close_chooser import (  # noqa: E402
    CLOSE_CHOOSER_CSS,
    CLOSE_CHOOSER_HTML,
    close_chooser_js,
)
from site_chrome import build_header  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

# Sample data: Jan–Mar from PL表例2.pdf; Apr–Oct interpolated; Nov–Dec + annual from PL表例3.pdf (rounded)
MONTHS_JA = [f"{m}月" for m in range(1, 13)]
MONTHS_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# [amount, ratio%] per month; annual [amount, ratio%]
SALES_TOTAL = [
    [4982374, None], [5001830, None], [6460634, None],
    [5200000, None], [5400000, None], [5600000, None],
    [5800000, None], [6000000, None], [6200000, None],
    [6400000, None], [6112150, None], [7899460, None],
    [71220857, None],
]
FOOD_COST_RATE = [
    [37.86, None], [35.54, None], [33.08, None],
    [34.0, None], [33.5, None], [33.0, None],
    [32.5, None], [32.0, None], [31.5, None],
    [31.0, None], [28.55, None], [33.52, None],
    [40.30, None],
]
LABOR_RATE = [
    [43.11, None], [49.24, None], [39.27, None],
    [42.0, None], [41.0, None], [40.0, None],
    [39.5, None], [39.0, None], [38.5, None],
    [38.0, None], [47.51, None], [37.87, None],
    [43.99, None],
]
FL_RATE = [
    [53.68, None], [56.84, None], [49.07, None],
    [52.0, None], [51.0, None], [50.0, None],
    [49.5, None], [49.0, None], [48.5, None],
    [48.0, None], [47.66, None], [50.21, None],
    [56.26, None],
]
GROSS_MARGIN = [
    [46, None], [46, None], [46, None],
    [45, None], [45, None], [44, None],
    [44, None], [43, None], [43, None],
    [43, None], [44, None], [44, None],
    [44, None],
]

def _pad(jan_amt: float, jan_pct: float) -> list:
    out = []
    for i in range(12):
        scale = 1.0 + (i % 3) * 0.02
        out.append([int(jan_amt * scale) if jan_amt else 0, jan_pct if jan_pct else 0.0])
    out.append([int(jan_amt * 12 * 0.95) if jan_amt else 0, jan_pct])
    return out


EXPENSE_ROWS = [
    ("rent", "家賃◉", "Rent◉", [
        [696429, 13.98], [696429, 13.92], [696429, 10.78],
        [696429, 11.5], [696429, 11.5], [696429, 11.5],
        [696429, 11.5], [696429, 11.5], [696429, 11.5],
        [696429, 11.5], [696429, 11.39], [696429, 8.82],
        [8357148, 11.73],
    ]),
    ("labor_fixed", "人件費(社員)", "Labor (staff)", [
        [1359735, 27.29], [1397503, 27.94], [1503672, 23.27],
        [1400000, 26.0], [1400000, 25.5], [1450000, 25.0],
        [1500000, 24.5], [1550000, 24.0], [1600000, 23.5],
        [1650000, 23.0], [1736152, 28.40], [1673367, 21.18],
        [19958663, 28.02],
    ]),
    ("food_purchase", "★仕入（食材）◉", "★Food purchase◉", [
        [1886544, 37.86], [1945204, 38.89], [2312204, 35.79],
        [2000000, 36.0], [2050000, 35.5], [2100000, 35.0],
        [2150000, 34.5], [2200000, 34.0], [2250000, 33.5],
        [2300000, 33.0], [2413240, 39.48], [2830519, 35.83],
        [27450573, 38.54],
    ]),
    ("labor_pt", "★人件費(アルバイト)", "★Part-time labor", [
        [788242, 15.82], [1065475, 21.30], [1033411, 16.00],
        [950000, 17.0], [980000, 17.5], [1000000, 18.0],
        [1020000, 18.2], [1050000, 18.5], [1080000, 18.8],
        [1100000, 19.0], [1168012, 19.11], [1318465, 16.69],
        [11371252, 15.97],
    ]),
    ("music", "音楽費（バンド）◉", "Music (band)◉", _pad(0, 0)),
    ("plants", "植木◉", "Plants◉", _pad(40920, 0.7)),
    ("town", "町会費◉", "Town fee◉", _pad(500, 0.01)),
    ("pest", "害虫駆除費用◉", "Pest control◉", _pad(112200, 2.0)),
    ("repair", "修繕費◉", "Repairs◉", _pad(0, 0)),
    ("lease", "リース料（厨房・レジ）◉", "Lease (kitchen/POS)◉", _pad(122620, 2.4)),
    ("bgm", "有線放送（ＢＧＭ）◉", "BGM◉", _pad(0, 0)),
    ("tablecheck", "Table Check◉", "Table Check◉", _pad(0, 0)),
    ("alsok", "アルソック◉", "ALSOK◉", _pad(11770, 0.2)),
    ("asset_tax", "償却資産税", "Fixed asset tax", _pad(17860, 0.35)),
    ("depr", "減価償却費（想定）", "Depreciation (est.)", _pad(220485, 4.4)),
    ("insurance", "店舗用損害賠償保険", "Shop liability ins.", _pad(19120, 0.38)),
    ("social", "社会保険料", "Social insurance", _pad(288295, 5.5)),
    ("supplies", "★仕入（備品・消耗品）◉", "★Supplies◉", _pad(41030, 0.8)),
    ("petty", "★雑費（小口精算等）◉", "★Petty cash◉", _pad(66179, 1.2)),
    ("maint", "★メンテナンス料◉", "★Maintenance◉", _pad(18090, 0.35)),
    ("electric", "★電気◉", "★Electricity◉", _pad(174792, 3.5)),
    ("gas", "★ガス◉", "★Gas◉", _pad(112613, 2.2)),
    ("water", "★水道◉", "★Water◉", _pad(45267, 0.9)),
    ("waste", "★産廃処理費◉", "★Waste disposal◉", _pad(39600, 0.8)),
    ("card_fee", "★クレジットカード手数料◉", "★Card fees◉", _pad(59471, 1.2)),
    ("ad", "広告宣伝費◉", "Advertising◉", _pad(27500, 0.55)),
    ("telecom", "通信費◉", "Telecom◉", _pad(13346, 0.27)),
    ("uniform", "被服費◉", "Uniforms◉", _pad(52469, 1.05)),
    ("hq", "本部費用", "Head office", _pad(189240, 3.8)),
    ("emp_ins", "雇用保険料", "Employment ins.", _pad(16242, 0.33)),
    ("workers_comp", "労災保険料", "Workers' comp.", _pad(11675, 0.23)),
    ("consumption_tax", "消費税（想定）", "Consumption tax (est.)", _pad(108225, 2.17)),
]

FOOD_DRINK_ROWS = [
    ("food_sales", "フード売上", "Food sales", _pad(3658680, 73.4)),
    ("food_cost", "フード仕入れ額", "Food COGS", _pad(1264422, 34.5)),
    ("drink_sales", "ドリンク売上", "Beverage sales", _pad(1323694, 26.5)),
    ("drink_cost", "ドリンク仕入れ額", "Beverage COGS", _pad(486956, 36.8)),
    ("labor_fixed_row", "社員人件費(固定費)", "Staff labor (fixed)", _pad(1359735, 27.3)),
    ("labor_var_row", "アルバイト人件費(変動費)", "Part-time (variable)", _pad(788242, 15.8)),
    ("fl_sum", "合計", "Total", _pad(2147977, 43.1)),
    ("monthly_food", "月次食材費", "Monthly food cost", _pad(1886544, 37.9)),
    ("monthly_labor_pt", "月次人件費(アルバイト)", "Monthly PT labor", _pad(788242, 15.8)),
    ("fl_total", "合計", "Total", _pad(2674786, 53.7)),
]

PROFIT1 = [
    [-1558085, -31.27], [-2122004, -42.42], [-1326829, -20.54],
    [-1800000, -32.0], [-1500000, -28.0], [-1200000, -22.0],
    [-1000000, -18.0], [-900000, -16.0], [-800000, -14.0],
    [-700000, -12.0], [-1995216, -32.64], [-1117477, -14.15],
    [-21705131, -30.48],
]

BUSINESS_DAYS = [
    [22, None], [23, None], [25, None],
    [24, None], [24, None], [25, None],
    [26, None], [25, None], [24, None],
    [25, None], [25, None], [24, None],
    [290, None],
]


def fmt_money(v: int | float | None, lang: str) -> str:
    if v is None:
        return "—"
    n = int(round(v))
    if lang == "en":
        return f"${n:,}"
    return f"¥{n:,}"


def fmt_pct(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{v:.2f}%"


def cell_pair(amount, ratio, lang: str) -> str:
    return (
        f'<td class="pl-num">{fmt_money(amount, lang)}</td>'
        f'<td class="pl-pct">{fmt_pct(ratio)}</td>'
    )


def row_cells(data, lang: str, neg_class: bool = False) -> str:
    parts = []
    for pair in data:
        amt, pct = pair[0], pair[1]
        cls = " pl-negative" if neg_class and amt is not None and amt < 0 else ""
        parts.append(f'<td class="pl-num{cls}">{fmt_money(amt, lang)}</td>')
        parts.append(f'<td class="pl-pct{cls}">{fmt_pct(pct)}</td>')
    return "".join(parts)


def row_cells_editable(key: str, data, lang: str) -> str:
    parts = []
    for mi, pair in enumerate(data):
        amt, pct = pair[0], pair[1]
        if mi < 12:
            parts.append(
                f'<td class="pl-num pl-cell-editable" contenteditable="true" '
                f'data-pl-editable="1" data-pl-field="amount" data-row="{key}" data-month="{mi}" '
                f'inputmode="decimal" spellcheck="false">{fmt_money(amt, lang)}</td>'
            )
        else:
            parts.append(f'<td class="pl-num">{fmt_money(amt, lang)}</td>')
        parts.append(f'<td class="pl-pct">{fmt_pct(pct)}</td>')
    return "".join(parts)


def build_rows(lang: str, labels: dict) -> str:
    L = labels
    out = []

    def section(title: str, cls: str = "pl-section") -> None:
        out.append(
            f'<tr class="{cls}"><th class="pl-label" colspan="27">{title}</th></tr>'
        )

    def data_row(key: str, label: str, data, bold=False, neg=False):
        b = " pl-row-bold" if bold else ""
        out.append(
            f'<tr class="pl-data-row{b}" data-row="{key}">'
            f'<th scope="row" class="pl-label">{label}</th>'
            f"{row_cells(data, lang, neg)}"
            f"</tr>"
        )

    section(L["store_sales"])
    zeros = [[0, None] for _ in range(13)]
    data_row("sales_a", L["sales_a"], zeros, neg=False)
    data_row("sales_b", L["sales_b"], zeros, neg=False)
    data_row("sales_total", L["sales_total"], SALES_TOTAL, bold=True)

    data_row("fixed", L["fixed"], [
        [2889934, 58.0], [2832002, 56.62], [2859770, 44.26],
        [2900000, 52.0], [2950000, 51.0], [3000000, 50.0],
        [3050000, 49.0], [3100000, 48.0], [3150000, 47.0],
        [3200000, 46.0], [3092550, 50.60], [3053965, 38.66],
        [36509441, 51.26],
    ])
    data_row("variable", L["variable"], [
        [3650525, 73.27], [4291832, 85.81], [4927693, 76.27],
        [4000000, 72.0], [4100000, 71.0], [4200000, 70.0],
        [4300000, 69.0], [4400000, 68.0], [4500000, 67.0],
        [4600000, 66.0], [5014816, 82.05], [5962972, 75.49],
        [56416547, 79.21],
    ])
    data_row("expense_sum", L["expense_sum"], [
        [6540459, 131.27], [7123834, 142.42], [7787463, 120.54],
        [6900000, 124.0], [7050000, 122.0], [7200000, 120.0],
        [7350000, 118.0], [7500000, 116.0], [7650000, 114.0],
        [7800000, 112.0], [8107366, 132.64], [9016937, 114.15],
        [92925988, 130.48],
    ], bold=True)

    section(L.get("food_labor", "フード・人件費内訳"))
    for _id, ja, en, data in FOOD_DRINK_ROWS:
        data_row(_id, en if lang == "en" else ja, data)

    section(L["expenses"])
    for _id, ja, en, data in EXPENSE_ROWS:
        label = en if lang == "en" else ja
        out.append(
            f'<tr class="pl-data-row pl-expense-row" data-row="{_id}" data-pl-expense="1">'
            f'<th scope="row" class="pl-label">{label}</th>'
            f"{row_cells_editable(_id, data, lang)}"
            f"</tr>"
        )

    data_row("subtotal", L["subtotal"], [
        [6540459, 131.27], [7123834, 142.42], [7787463, 120.54],
        [6900000, 124.0], [7050000, 122.0], [7200000, 120.0],
        [7350000, 118.0], [7500000, 116.0], [7650000, 114.0],
        [7800000, 112.0], [8107366, 132.64], [9016937, 114.15],
        [92925988, 130.48],
    ], bold=True)
    data_row("profit1", L["profit1"], PROFIT1, bold=True, neg=True)
    data_row("bizdays", L["bizdays"], BUSINESS_DAYS)

    out.append(
        f'<tr class="pl-group-head">'
        f'<th scope="row" class="pl-label">'
        f'<button type="button" class="pl-group-toggle" id="pl-kpi-toggle" aria-expanded="true" aria-controls="pl-kpi-group">'
        f'<span class="pl-group-toggle__icon" aria-hidden="true">▼</span> {L["kpi_group"]}'
        f"</button></th>"
        f'<td colspan="26" class="pl-group-head__hint">{L["kpi_hint"]}</td></tr>'
    )
    kpi_rows = [
        ("food_cost_rate", L["food_cost_rate"], FOOD_COST_RATE),
        ("labor_rate", L["labor_rate"], LABOR_RATE),
        ("fl_rate", L["fl_rate"], FL_RATE),
        ("gross_margin", L["gross_margin"], GROSS_MARGIN),
    ]
    for key, label, data in kpi_rows:
        out.append(
            f'<tr class="pl-kpi-row" id="pl-kpi-group" data-row="{key}">'
            f'<th scope="row" class="pl-label pl-label--kpi">{label}</th>'
            f"{row_cells(data, lang)}"
            f"</tr>"
        )
    return "\n".join(out)


LABELS_JA = {
    "title": "損益表（PL）",
    "corner_title": "損益表",
    "guide_toggle_aria": "費目別の参考予算を表示",
    "guide_toggle_show_title": "費目別の参考予算を表示（過去実績の中央値比率 × 売上）",
    "guide_toggle_hide_title": "費目別の参考予算を隠す",
    "guide_toggle_tip": "＋ 費目別の参考予算（定規）を表示。過去実績の中央値比率 × 今月の売上で「使いすぎ」を各セルに目安表示します（断定の適正値ではありません）。",
    "guide_toggle_tip_on": "− 費目別の参考予算（定規）を隠します。",
    "guide_toggle_tip_nodata": "参考予算は、過去の売上・支出データが貯まると自動で表示されます（あなたの店の実績から算出）。",
    "year": "2024",
    "store_sales": "店舗売上",
    "sales_a": "売上A",
    "sales_b": "売上B",
    "sales_total": "売上合計",
    "fixed": "固定費",
    "variable": "変動費",
    "expense_sum": "合計",
    "food_labor": "売上／仕入・人件費内訳",
    "expenses": "支出",
    "subtotal": "小計",
    "profit1": "利益①",
    "bizdays": "営業日数",
    "bizdays_row": "営業日",
    "income_major": "収入",
    "edit_label_aria": "ラベルを編集（ダブルクリックまたは F2）",
    "kpi_group": "原価・FL指標",
    "kpi_hint": "▶ で行を折りたたみ（Excel のグループ化と同様）",
    "food_cost_rate": "食材原価率",
    "labor_rate": "労働分配率（人件費）",
    "fl_rate": "FL率",
    "gross_margin": "粗利益率（総売上−FLコスト）÷総売上",
    "amount": "金額",
    "ratio": "比率",
    "total": "合計",
    "year_total_head": "年計",
    "occupancy_aria": "物件形態",
    "occupancy_rent": "賃貸",
    "occupancy_owned": "自持",
    "analyze_band": "分析",
    "analyze_toggle_aria": "分析セクションの表示を切り替え",
    "expense_detail_add_aria": "行を追加",
    "expense_detail_hide_aria": "行を非表示",
    "expense_detail_hide_confirm_aria": "選択した行を非表示",
    "expense_detail_hide_mode_hint": "非表示にする行をクリックして選択し、−をもう一度押してください（データは保持されます）",
    "expense_detail_hide_cancel": "キャンセル",
    "expense_detail_move_up_aria": "行を上へ",
    "expense_detail_move_down_aria": "行を下へ",
    "expense_detail_new_row": "新規科目",
    "line_manage_btn": "科目管理",
    "line_manage_title": "非表示の支出科目",
    "line_manage_empty": "非表示の科目はありません",
    "line_manage_restore": "復活",
    "line_manage_close": "閉じる",
    "hide_line_confirm_title": "この科目を非表示にしますか？",
    "hide_line_confirm_body": "「{label}」を非表示にします。過去のデータは保持されます。",
    "hide_line_confirm_ok": "非表示にする",
    "hide_line_confirm_cancel": "キャンセル",
    "delete_line_confirm_title": "この行を削除しますか？",
    "delete_line_confirm_body": "「{label}」を削除します。この操作は取り消せません。",
    "delete_line_confirm_ok": "削除する",
    "input_source_title": "編集は下記どちらで行いますか？",
    "input_source_daily": "Monthly Edit Page（日次入力）",
    "input_source_monthly": "PL表（月次入力）",
    "input_source_skip": "今後この確認を表示しない",
    "input_source_confirm": "決定",
    "input_source_cancel": "キャンセル",
    "label_edit_modal_title": "科目を編集",
    "label_edit_modal_label": "科目名",
    "label_edit_modal_source": "数値の入力先",
    "label_edit_modal_confirm": "決定",
    "label_edit_modal_cancel": "キャンセル",
    "adj_modal_title": "月次調整額",
    "adj_modal_daily": "日次合計",
    "adj_modal_adj": "調整額",
    "adj_modal_result": "PL表示額",
    "adj_modal_hint": "請求書などとのズレを調整します。日次入力は消えません。",
    "adj_modal_confirm": "決定",
    "adj_modal_cancel": "キャンセル",
    "variable_mid_edit_tip": "科目ラベルをダブルクリックすると、科目名の変更と入力先（月次 / 日次）の切り替えができます。",
    "expense_attribute_title": "この科目の属性を選択してください",
    "expense_attribute_variable_title": "この変動費科目の属性を選択してください",
    "expense_attribute_edit_title": "属性を変更",
    "expense_attribute_confirm": "決定",
    "expense_attribute_cancel": "キャンセル",
    "expense_attribute_btn": "属性",
    "expense_attribute_btn_aria": "属性を変更",
    "expense_attr_edit_toggle": "属性編集",
    "expense_attr_edit_toggle_aria": "固定費・変動費の属性編集ボタンを表示",
    "expense_attr_edit_on": "ON",
    "expense_attr_edit_off": "OFF",
    "graph_band": "グラフ",
    "graph_monthly_sales": "月次売上",
    "graph_expenses": "支出",
    "profit_row": "利益",
    "ref_budget_row": "変動費の参考枠",
    "ref_budget_tip": "目標総費率から固定費率を引いた、変動費の目安（断定の適正値ではありません）",
    "mock": "PL表 — 再描画準備中（表グリッドのみ削除・メニュー等は維持）",
    "back": "利益サマリーへ",
    "back_edit": "月次編集へ",
    "back_edit_aria": "月次編集ページへ戻る",
    "year_label": "年度",
    "year_aria": "表示する会計年度を選択",
    "csv_upload": "支出CSV取込",
    "csv_upload_tooltip": "支出をCSV/Excel（.xlsx）で取り込みます。雛形は右上「DL」からダウンロードできます（費目名は雛形＝カタログのラベルに合わせてください）。",
    "download_excel": "Download Excel",
    "download_excel_aria": "PL表を Excel 用 CSV でダウンロード",
    "toolbar_graph": "PL Insight",
    "toolbar_graph_aria": "PL Insight を開く",
    "zoom_label": "表示",
    "zoom_out_aria": "表示を縮小",
    "zoom_in_aria": "表示を拡大",
    "zoom_range_alert": "Zoomは{min}%〜{max}%で入力してください。",
    "graph_overlay_title": "比較",
    "graph_overlay_close_aria": "閉じる",
    "compare_prev_day_aria": "前日",
    "compare_next_day_aria": "翌日",
    "compare_date_pick_aria": "日付を選択",
    "compare_today": "本日",
    "compare_section1_title": "1. Last Year Same Month Profit & Loss",
    "compare_income": "Income",
    "compare_expenses": "Expenses",
    "compare_expected_fixed": "Expected / Fixed",
    "compare_profit": "Profit",
    "compare_open_monthly_edit": "Monthly Edit で開く",
    "compare_open_current_month": "今月を Monthly Edit で開く",
    "compare_chart_open_aria": "Monthly Edit でこの月を開く",
    "compare_area1_title": "Area 1. Current FL Snapshot",
    "compare_area2_title": "Area 2. Last Year Same Month FL Snapshot",
    "compare_area3_title": "Area 3. Year-to-Date FL Snapshot",
    "compare_food_labor": "Food & Labor",
    "compare_food_slash_labor": "Food / Labor",
    "compare_same_weekday_of": "Same Weekday of ",
    "compare_area2_hsnap_primary": "Last Year Same Month ",
    "compare_area2_hsnap_secondary": "Two Years Prior Same Month ",
    "compare_area3_hsnap_primary": "Year-to-Date ",
    "compare_area3_hsnap_secondary": "Last Year YTD ",
    "compare_no_data": "No Data",
    "compare_line_title": "Compare PL to Same weekday of Last Year Cumulative Pace",
    "compare_area2_line_title": "Compare Last Year Same Month Cumulative Pace",
    "compare_area3_line_title": "Compare Year-to-Date Cumulative Pace",
    "compare_this_year": "This Year",
    "compare_last_year": "Last Year",
    "compare_best_year": "Best Year",
    "compare_fixed": "Fixed",
    "compare_expected": "Expected",
    "compare_daily_title": "Daily Performance",
    "compare_area2_daily_title": "Daily Performance",
    "compare_area3_daily_title": "Monthly Performance",
    "graph_overlay_placeholder": "年次の収入・支出比較グラフは次フェーズで実装予定です。",
    "undo": "戻る",
    "save": "Save",
    "nav_insight": "考察",
    "nav_insight_aria": "月次ページで考察（Insight）を開く",
    "nav_insight_basic_aria": "Basicプランはプラン変更へ",
}

LABELS_EN = {
    "title": "Profit & Loss (PL)",
    "corner_title": "Profit & Loss",
    "guide_toggle_aria": "Show per-line reference budget",
    "guide_toggle_show_title": "Show per-line reference budget (median past ratio × sales)",
    "guide_toggle_hide_title": "Hide per-line reference budget",
    "guide_toggle_tip": "+ Show per-line reference budget (guideline). Median of your past ratios × this month's sales flags likely overspending per cell (not a prescribed ideal).",
    "guide_toggle_tip_on": "− Hide the per-line reference budget (guideline).",
    "guide_toggle_tip_nodata": "Reference budget appears automatically once you have past sales & expense data (computed from your own store's records).",
    "year": "2024",
    "store_sales": "Store sales",
    "sales_a": "Sales A",
    "sales_b": "Sales B",
    "sales_total": "Total sales",
    "fixed": "Fixed",
    "variable": "Variable",
    "expense_sum": "Total",
    "food_labor": "Sales / COGS / labor detail",
    "expenses": "Expenses",
    "subtotal": "Subtotal",
    "profit1": "Profit ①",
    "bizdays": "Business days",
    "bizdays_row": "Business Days",
    "income_major": "Income",
    "edit_label_aria": "Edit label (double-click or F2)",
    "kpi_group": "Cost & FL metrics",
    "kpi_hint": "Collapse rows like Excel grouping",
    "food_cost_rate": "Food cost %",
    "labor_rate": "Labor ratio (payroll)",
    "fl_rate": "FL %",
    "gross_margin": "Gross margin (sales − FL) ÷ sales",
    "amount": "Amount",
    "ratio": "Ratio",
    "total": "Annual total",
    "year_total_head": "Annual",
    "occupancy_aria": "Occupancy",
    "occupancy_rent": "Rented",
    "occupancy_owned": "Owned",
    "analyze_band": "Analysis",
    "analyze_toggle_aria": "Toggle analysis section",
    "expense_detail_add_aria": "Add row",
    "expense_detail_hide_aria": "Hide row",
    "expense_detail_hide_confirm_aria": "Hide selected row",
    "expense_detail_hide_mode_hint": "Click a row to select it, then press − again (data is kept, row is hidden)",
    "expense_detail_hide_cancel": "Cancel",
    "expense_detail_move_up_aria": "Move row up",
    "expense_detail_move_down_aria": "Move row down",
    "expense_detail_new_row": "New item",
    "line_manage_btn": "Line items",
    "line_manage_title": "Hidden expense lines",
    "line_manage_empty": "No hidden lines",
    "line_manage_restore": "Restore",
    "line_manage_close": "Close",
    "hide_line_confirm_title": "Hide this line?",
    "hide_line_confirm_body": 'Hide "{label}". Past data will be kept.',
    "hide_line_confirm_ok": "Hide",
    "hide_line_confirm_cancel": "Cancel",
    "delete_line_confirm_title": "Delete this row?",
    "delete_line_confirm_body": "Delete “{label}”. This cannot be undone.",
    "delete_line_confirm_ok": "Delete",
    "input_source_title": "Where will you enter amounts for this item?",
    "input_source_daily": "Monthly Edit Page (daily entries)",
    "input_source_monthly": "Profit & Loss table (monthly)",
    "input_source_skip": "Don't ask again",
    "input_source_confirm": "Confirm",
    "input_source_cancel": "Cancel",
    "label_edit_modal_title": "Edit line item",
    "label_edit_modal_label": "Label",
    "label_edit_modal_source": "Where to enter amounts",
    "label_edit_modal_confirm": "Confirm",
    "label_edit_modal_cancel": "Cancel",
    "adj_modal_title": "Monthly adjustment",
    "adj_modal_daily": "Daily total",
    "adj_modal_adj": "Adjustment",
    "adj_modal_result": "PL amount",
    "adj_modal_hint": "Adjust gaps vs invoice totals. Daily entries are kept.",
    "adj_modal_confirm": "Confirm",
    "adj_modal_cancel": "Cancel",
    "variable_mid_edit_tip": "Double-click a line label to rename it and change the input location (Monthly / Daily).",
    "expense_attribute_title": "Select an expense attribute for this line",
    "expense_attribute_variable_title": "Select a variable expense attribute for this line",
    "expense_attribute_edit_title": "Change attribute",
    "expense_attribute_confirm": "Confirm",
    "expense_attribute_cancel": "Cancel",
    "expense_attribute_btn": "Attr",
    "expense_attribute_btn_aria": "Change expense attribute",
    "expense_attr_edit_toggle": "Attributes",
    "expense_attr_edit_toggle_aria": "Show attribute edit buttons for fixed and variable expenses",
    "expense_attr_edit_on": "ON",
    "expense_attr_edit_off": "OFF",
    "graph_band": "Graph",
    "graph_monthly_sales": "Monthly Sales",
    "graph_expenses": "Expenses",
    "profit_row": "Profit",
    "ref_budget_row": "Variable expense guideline",
    "ref_budget_tip": "Guideline for variable spend = target cost rate minus fixed-cost rate (not a prescribed ideal)",
    "mock": "PL table — redrawing (grid removed; nav and toolbar kept)",
    "back": "Back to profit hub",
    "back_edit": "Monthly Edit",
    "back_edit_aria": "Back to Monthly Edit page",
    "year_label": "Year",
    "year_aria": "Select fiscal year to display",
    "csv_upload": "Upload Expenses",
    "csv_upload_tooltip": "Import expenses from CSV/Excel (.xlsx). Download a template from \"DL\" (top-right); item names must match the catalog labels.",
    "download_excel": "Download Excel",
    "download_excel_aria": "Download PL table as CSV for Excel",
    "toolbar_graph": "PL Insight",
    "toolbar_graph_aria": "Open PL Insight",
    "zoom_label": "Zoom",
    "zoom_out_aria": "Zoom out",
    "zoom_in_aria": "Zoom in",
    "zoom_range_alert": "Zoom must be between {min}% and {max}%.",
    "graph_overlay_title": "Compare",
    "graph_overlay_close_aria": "Close",
    "compare_prev_day_aria": "Previous day",
    "compare_next_day_aria": "Next day",
    "compare_date_pick_aria": "Select date",
    "compare_today": "Today",
    "compare_section1_title": "1. Last Year Same Month Profit & Loss",
    "compare_income": "Income",
    "compare_expenses": "Expenses",
    "compare_expected_fixed": "Expected / Fixed",
    "compare_profit": "Profit",
    "compare_open_monthly_edit": "Open in Monthly Edit",
    "compare_open_current_month": "Open this month in Monthly Edit",
    "compare_chart_open_aria": "Open this month in Monthly Edit",
    "compare_area1_title": "Area 1. Current FL Snapshot",
    "compare_area2_title": "Area 2. Last Year Same Month FL Snapshot",
    "compare_area3_title": "Area 3. Year-to-Date FL Snapshot",
    "compare_food_labor": "Food & Labor",
    "compare_food_slash_labor": "Food / Labor",
    "compare_same_weekday_of": "Same Weekday of ",
    "compare_area2_hsnap_primary": "Last Year Same Month ",
    "compare_area2_hsnap_secondary": "Two Years Prior Same Month ",
    "compare_area3_hsnap_primary": "Year-to-Date ",
    "compare_area3_hsnap_secondary": "Last Year YTD ",
    "compare_no_data": "No Data",
    "compare_line_title": "Compare PL to Same weekday of Last Year Cumulative Pace",
    "compare_area2_line_title": "Compare Last Year Same Month Cumulative Pace",
    "compare_area3_line_title": "Compare Year-to-Date Cumulative Pace",
    "compare_this_year": "This Year",
    "compare_last_year": "Last Year",
    "compare_best_year": "Best Year",
    "compare_fixed": "Fixed",
    "compare_expected": "Expected",
    "compare_daily_title": "Daily Performance",
    "compare_area2_daily_title": "Daily Performance",
    "compare_area3_daily_title": "Monthly Performance",
    "graph_overlay_placeholder": "Year-over-year income and expense comparison charts are planned for a later phase.",
    "undo": "Undo",
    "save": "Save",
    "nav_insight": "Insight",
    "nav_insight_aria": "Open Insight on Monthly",
    "nav_insight_basic_aria": "Basic plan: go to Change Plan",
}


from pl_expense_detail_client import expense_detail_client_js  # noqa: E402
from pl_expense_import_client import pl_expense_import_client_js  # noqa: E402
from pl_monthly_allocate_client import pl_monthly_allocate_client_js  # noqa: E402
from pl_income_client import pl_income_client_js  # noqa: E402
from pl_ratio_client import pl_ratio_client_js  # noqa: E402
from pl_reference_budget_client import pl_reference_budget_client_js  # noqa: E402
from pl_year_total_client import pl_year_total_client_js  # noqa: E402
from pl_line_catalog import (  # noqa: E402
    CATALOG_SCHEMA_VERSION,
    EXPENSE_DETAIL_LINES_V1,
    EXPENSES_SUMMARY_ROWS_V1 as EXPENSES_ROWS_V1,
    FIXED_EXPENSE_ATTRIBUTES,
    INCOME_ROWS_V1,
    VARIABLE_EXPENSE_ATTRIBUTES,
    expense_detail_default_catalog,
)

# Analyze block — KPI / cost health (below Total Expenses)
ANALYZE_GROUPS_V1 = [
    (
        "food_cost_ratio",
        ("Food cost", "Ratio"),
        ("食材", "原価率"),
        [
            ("analyze_food_sales", "フード売上", "Food Sales", False),
            ("analyze_food_cost", "フード仕入れ額", "Food Procurement Costs", False),
            ("analyze_drink_sales", "ドリンク売上", "Drink Purchase Amount", False),
            ("analyze_drink_cost", "ドリンク仕入れ額", "Drink Procurement Costs", False),
        ],
    ),
    (
        "labor_share",
        ("Labor", "share"),
        ("労働", "分配率"),
        [
            ("analyze_labor_employee", "社員人件費", "Employee Personnel Costs", False),
            ("analyze_labor_pt", "アルバイト人件費", "Part-Time Worker Wages", False),
            ("analyze_labor_total", "合計", "Total", True),
        ],
    ),
    (
        "fl_ratio",
        ("Food & Labor", "Ratio"),
        ("FL", "率"),
        [
            ("analyze_monthly_food", "月次食材費", "Monthly food expenses", False),
            ("analyze_monthly_labor", "月次人件費", "Monthly personnel costs", False),
            ("analyze_fl_total", "合計", "Total", True),
        ],
    ),
]

def pl_label_colgroup() -> str:
    return (
        '<colgroup><col class="pl-col-v-major">'
        '<col class="pl-col-h-label"></colgroup>'
    )


def pl_expense_detail_label_colgroup() -> str:
    return (
        '<colgroup><col class="pl-col-v-mid">'
        '<col class="pl-col-h-label-detail"></colgroup>'
    )


def pl_data_colgroup() -> str:
    parts = ["<colgroup>"]
    for _ in range(13):
        parts.append('<col class="pl-col-amt"><col class="pl-col-ratio">')
    parts.append("</colgroup>")
    return "".join(parts)


def dummy_money(lang: str) -> str:
    return "¥123,456" if lang == "ja" else "$123,456"


def editable_label_span(row_id: str, label: str, scope: str, edit_aria: str) -> str:
    """Inline label text — double-click / F2 to edit (no pencil icon)."""
    return (
        f'<span class="pl-h-label__text pl-h-label__text--editable" '
        f'data-pl-label-editable="1" data-label-id="{row_id}" '
        f'data-label-scope="{scope}" tabindex="0" role="button" '
        f'aria-label="{edit_aria}">{label}</span>'
    )


def income_label_rows_v1(lang: str) -> str:
    """Income label pane rows (vertical Income + horizontal labels)."""
    L = LABELS_EN if lang == "en" else LABELS_JA
    major = L["income_major"]
    edit_aria = L["edit_label_aria"]
    rows: list[str] = []
    n = len(INCOME_ROWS_V1)
    for i, (rid, ja, en, _editable, is_total) in enumerate(INCOME_ROWS_V1):
        label = en if lang == "en" else ja
        major_td = ""
        if i == 0:
            major_td = (
                f'<td class="pl-v-major" rowspan="{n}" data-pl-section="income">'
                f'<span class="pl-v-major__text">{major}</span></td>'
            )
        label_cls = "pl-h-label"
        if is_total:
            label_cls += " pl-h-label--total"
            label_inner = f'<span class="pl-h-label__text">{label}</span>'
        else:
            label_cls += " pl-h-label--editable"
            label_inner = editable_label_span(rid, label, "income", edit_aria)
            label_inner = f'<span class="pl-h-label__row">{label_inner}</span>'
        row_cls = "pl-data-row pl-data-row--income"
        if is_total:
            row_cls += " pl-data-row--total"
        rows.append(
            f'<tr class="{row_cls}" data-pl-section="income" data-row="{rid}">'
            f"{major_td}"
            f'<th scope="row" class="{label_cls}">{label_inner}</th></tr>'
        )
    return "".join(rows)


def income_data_rows_v1(lang: str) -> str:
    """Income data pane rows (12 months × Amount 160px + Ratio 100px).

    All income rows are READ-ONLY in PL (income is entered daily on MEP; PL shows
    the monthly cumulative). Filled by pl_income_client / pl_ratio_client:
      - store_sales = Total Sales − (A + B)
      - sales_a / sales_b = years.{Y}.dailyIncome[stream] monthly sum (—until MEP writes it)
      - sales_total = timeline.dailySales monthly sum
      - Ratio(%) = amount ÷ sales_total (same denominator as expense ratios)
    """
    rows: list[str] = []
    for rid, _ja, _en, _editable, is_total in INCOME_ROWS_V1:
        if is_total:
            role = "total"
        elif rid == "store_sales":
            role = "store"
        else:
            role = "stream"
        data_cells: list[str] = []
        for mi in range(12):
            data_cells.append(
                f'<td class="pl-amt-cell pl-amt-cell--income-{role}" data-row="{rid}" '
                f'data-month="{mi}" data-field="amount" data-pl-income-role="{role}">'
                f'<span class="pl-amt-cell__text">—</span></td>'
                f'<td class="pl-ratio-cell pl-ratio-cell--income-{role}" data-row="{rid}" '
                f'data-month="{mi}" data-field="ratio">'
                f'<span class="pl-ratio-cell__text"></span></td>'
            )
        data_cells.append(
            year_amt_ratio_pair_html(
                rid,
                amt_class=f"pl-amt-cell pl-amt-cell--income-{role} pl-amt-cell--year-total",
                ratio_class=f"pl-ratio-cell pl-ratio-cell--income-{role} pl-ratio-cell--year-total",
            )
        )
        row_cls = "pl-data-row pl-data-row--income"
        if is_total:
            row_cls += " pl-data-row--total"
        rows.append(
            f'<tr class="{row_cls}" data-row="{rid}" data-pl-section="income">'
            f'{"".join(data_cells)}</tr>'
        )
    return "".join(rows)


def expenses_major_label_html(lang: str) -> str:
    """Vertical Total / Expenses label (line break after first word, same orientation as Income)."""
    return _major_label_html(lang, ("Total", "Expenses"), ("総", "支出"))


def expenses_label_rows_v1(lang: str) -> str:
    """Total Expenses label pane (vertical major + Fixed / Expected / Total Expenses)."""
    L = LABELS_EN if lang == "en" else LABELS_JA
    edit_aria = L["edit_label_aria"]
    major_html = expenses_major_label_html(lang)
    rows: list[str] = []
    n = len(EXPENSES_ROWS_V1)
    for i, (rid, ja, en, _editable, is_total) in enumerate(EXPENSES_ROWS_V1):
        label = en if lang == "en" else ja
        major_td = ""
        if i == 0:
            major_td = (
                f'<td class="pl-v-major pl-v-major--expenses" rowspan="{n}" '
                f'data-pl-section="expenses">{major_html}</td>'
            )
        label_cls = "pl-h-label"
        if is_total:
            label_cls += " pl-h-label--total"
            label_inner = f'<span class="pl-h-label__text">{label}</span>'
        else:
            label_cls += " pl-h-label--editable"
            label_inner = editable_label_span(rid, label, "expenses-summary", edit_aria)
            label_inner = f'<span class="pl-h-label__row">{label_inner}</span>'
        row_cls = "pl-data-row pl-data-row--expenses"
        if is_total:
            row_cls += " pl-data-row--total"
        rows.append(
            f'<tr class="{row_cls}" data-pl-section="expenses" data-row="{rid}">'
            f"{major_td}"
            f'<th scope="row" class="{label_cls}">{label_inner}</th></tr>'
        )
    return "".join(rows)


def expenses_data_rows_v1(lang: str) -> str:
    """Total Expenses data pane rows (12 months × Amount/Ratio dummy)."""
    return _section_data_rows_v1(lang, EXPENSES_ROWS_V1, "expenses")


def reference_budget_label_row_v1(lang: str) -> str:
    """L1 variable-expense guideline label (read-only, after expenses summary)."""
    L = LABELS_EN if lang == "en" else LABELS_JA
    label = L["ref_budget_row"]
    tip = L["ref_budget_tip"]
    return (
        f'<tr class="pl-data-row pl-data-row--ref-budget" data-pl-section="ref-budget" '
        f'data-row="var_ref_budget">'
        f'<th scope="row" class="pl-h-label pl-h-label--ref-budget" colspan="2" '
        f'title="{tip}"><span class="pl-h-label__text">{label}</span></th></tr>'
    )


def reference_budget_data_row_v1(lang: str) -> str:
    """L1 guideline data cells — filled by pl_reference_budget_client."""
    cells: list[str] = []
    for mi in range(12):
        cells.append(
            month_amt_ratio_pair_html(
                "var_ref_budget",
                mi,
                amt_class="pl-amt-cell pl-amt-cell--ref-budget",
                ratio_class="pl-ratio-cell pl-ratio-cell--ref-budget",
                amt_text="—",
                ratio_text="—",
            )
        )
    cells.append(
        year_amt_ratio_pair_html(
            "var_ref_budget",
            amt_class="pl-amt-cell pl-amt-cell--ref-budget pl-amt-cell--year-total",
            ratio_class="pl-ratio-cell pl-ratio-cell--ref-budget pl-ratio-cell--year-total",
            amt_text="—",
            ratio_text="—",
        )
    )
    return (
        f'<tr class="pl-data-row pl-data-row--ref-budget" data-row="var_ref_budget" '
        f'data-pl-section="ref-budget">{"".join(cells)}</tr>'
    )


def _major_label_html(lang: str, lines_en: tuple[str, ...], lines_ja: tuple[str, ...]) -> str:
    lines = lines_ja if lang == "ja" else lines_en
    if len(lines) == 1:
        return f'<span class="pl-v-major__text">{lines[0]}</span>'
    inner = "".join(f'<span class="pl-v-major__line">{line}</span>' for line in lines)
    return f'<span class="pl-v-major__text pl-v-major__text--multiline">{inner}</span>'


def analyze_label_rows_v1(lang: str) -> str:
    """Analyze label rows (3 vertical groups × detail rows)."""
    L = LABELS_EN if lang == "en" else LABELS_JA
    edit_aria = L["edit_label_aria"]
    rows: list[str] = []
    for group_id, major_en, major_ja, group_rows in ANALYZE_GROUPS_V1:
        n = len(group_rows)
        major_html = _major_label_html(lang, major_en, major_ja)
        for i, (rid, ja, en, is_total) in enumerate(group_rows):
            label = en if lang == "en" else ja
            major_td = ""
            if i == 0:
                major_td = (
                    f'<td class="pl-v-major pl-v-major--analyze pl-v-major--r{n}" '
                    f'rowspan="{n}" data-pl-section="analyze" data-pl-group="{group_id}">'
                    f"{major_html}</td>"
                )
            label_cls = "pl-h-label"
            if is_total:
                label_cls += " pl-h-label--total"
                label_inner = f'<span class="pl-h-label__text">{label}</span>'
            else:
                label_cls += " pl-h-label--editable"
                label_inner = editable_label_span(rid, label, "analyze", edit_aria)
                label_inner = f'<span class="pl-h-label__row">{label_inner}</span>'
            row_cls = "pl-data-row pl-data-row--analyze pl-analyze-zone"
            if is_total:
                row_cls += " pl-data-row--total"
            rows.append(
                f'<tr class="{row_cls}" data-pl-section="analyze" data-pl-group="{group_id}" '
                f'data-row="{rid}">'
                f"{major_td}"
                f'<th scope="row" class="{label_cls}">{label_inner}</th></tr>'
            )
    return "".join(rows)


def year_amt_ratio_pair_html(
    row_id: str,
    *,
    amt_text: str = "—",
    ratio_text: str = "",
    amt_class: str = "pl-amt-cell pl-amt-cell--year-total",
    ratio_class: str = "pl-ratio-cell pl-ratio-cell--year-total",
) -> str:
    """Year-total column: Amount 160px + Ratio 100px (= 260px), read-only."""
    return (
        f'<td class="{amt_class}" data-row="{row_id}" data-month="year" data-field="amount">'
        f'<span class="pl-amt-cell__text">{amt_text}</span></td>'
        f'<td class="{ratio_class}" data-row="{row_id}" data-month="year" data-field="ratio">'
        f'<span class="pl-ratio-cell__text">{ratio_text}</span></td>'
    )


def month_amt_ratio_pair_html(
    row_id: str,
    month_index: int,
    *,
    amt_text: str = "",
    ratio_text: str = "",
    amt_class: str = "pl-amt-cell",
    ratio_class: str = "pl-ratio-cell",
) -> str:
    """One month column split: Amount 160px + Ratio 100px (= 260px)."""
    return (
        f'<td class="{amt_class}" data-row="{row_id}" data-month="{month_index}" data-field="amount">'
        f'<span class="pl-amt-cell__text">{amt_text}</span></td>'
        f'<td class="{ratio_class}" data-row="{row_id}" data-month="{month_index}" data-field="ratio">'
        f'<span class="pl-ratio-cell__text">{ratio_text}</span></td>'
    )


def analyze_data_rows_v1(lang: str) -> str:
    """Analyze data rows — 160px amount + 100px ratio per month."""
    rows: list[str] = []
    for group_id, _major_en, _major_ja, group_rows in ANALYZE_GROUPS_V1:
        for rid, _ja, _en, is_total in group_rows:
            data_cells: list[str] = []
            for mi in range(12):
                data_cells.append(
                    month_amt_ratio_pair_html(
                        rid,
                        mi,
                        amt_class="pl-amt-cell pl-amt-cell--analyze",
                        ratio_class="pl-ratio-cell pl-ratio-cell--analyze",
                    )
                )
            data_cells.append(
                year_amt_ratio_pair_html(
                    rid,
                    amt_class="pl-amt-cell pl-amt-cell--analyze pl-amt-cell--year-total",
                    ratio_class="pl-ratio-cell pl-ratio-cell--analyze pl-ratio-cell--year-total",
                )
            )
            row_cls = "pl-data-row pl-data-row--analyze pl-analyze-zone"
            if is_total:
                row_cls += " pl-data-row--total"
            rows.append(
                f'<tr class="{row_cls}" data-row="{rid}" data-pl-section="analyze" '
                f'data-pl-group="{group_id}">{"".join(data_cells)}</tr>'
            )
    return "".join(rows)


def _section_data_rows_v1(
    lang: str,
    rows_def: list[tuple[str, str, str, bool, bool]],
    section_id: str,
) -> str:
    dummy = dummy_money(lang)
    rows: list[str] = []
    for rid, _ja, _en, _editable, is_total in rows_def:
        data_cells: list[str] = []
        for mi in range(12):
            data_cells.append(
                month_amt_ratio_pair_html(rid, mi, amt_text=dummy)
            )
        data_cells.append(year_amt_ratio_pair_html(rid, amt_text="—"))
        row_cls = f"pl-data-row pl-data-row--{section_id}"
        if is_total:
            row_cls += " pl-data-row--total"
        rows.append(
            f'<tr class="{row_cls}" data-row="{rid}" data-pl-section="{section_id}">'
            f'{"".join(data_cells)}</tr>'
        )
    return "".join(rows)


def profit_label_row_v1(lang: str) -> str:
    L = LABELS_EN if lang == "en" else LABELS_JA
    label = L["profit_row"]
    return (
        f'<tr class="pl-data-row pl-data-row--profit" data-pl-section="profit">'
        f'<th class="pl-h-label pl-h-label--total pl-h-label--profit" scope="row" colspan="2" '
        f'id="pl-row-profit"><span class="pl-h-label__text">{label}</span></th></tr>'
    )


def expenses_detail_header_label_row(lang: str, L: dict) -> str:
    label = L["expenses"]
    return (
        f'<tr class="pl-data-row pl-data-row--expenses-head" data-pl-section="expense-detail">'
        f'<th class="pl-v-mid pl-v-mid--expenses-head" scope="row">'
        f'<button type="button" class="pl-expense-attr-toggle" id="pl-expense-attr-toggle" '
        f'aria-pressed="false" aria-label="{L["expense_attr_edit_toggle_aria"]}">'
        f'<span class="pl-expense-attr-toggle__label">{L["expense_attr_edit_toggle"]}</span>'
        f'<span class="pl-expense-attr-toggle__state" data-state="off">{L["expense_attr_edit_off"]}</span>'
        f'</button></th>'
        f'<th class="pl-h-label pl-h-label--total pl-h-label--expenses-head" scope="row">'
        f'<span class="pl-h-label__text pl-h-label__text--expenses-head">{label}</span>'
        f'</th></tr>'
    )


def expenses_detail_header_data_row() -> str:
    return (
        '<tr class="pl-data-row pl-data-row--expenses-head" data-pl-section="expense-detail">'
        '<td colspan="26" class="pl-expenses-head__data-band"></td></tr>'
    )


def profit_data_row_v1(lang: str) -> str:
    cells: list[str] = []
    for mi in range(12):
        cells.append(
            f'<td class="pl-month-cell pl-month-cell--profit" colspan="2" '
            f'data-row="profit" data-month="{mi}">'
            f'<span class="pl-month-cell__text"></span></td>'
        )
    cells.append(
        '<td class="pl-month-cell pl-month-cell--profit pl-month-cell--year-total" colspan="2" '
        'data-row="profit" data-month="year">'
        '<span class="pl-month-cell__text">—</span></td>'
    )
    return (
        f'<tr class="pl-data-row pl-data-row--profit" data-row="profit" data-pl-section="profit">'
        f'{"".join(cells)}</tr>'
    )


def pl_label_edit_client_js(*, edit_aria: str, expense_catalog_json: str) -> str:
    """Double-click / F2 inline label editing for PL table rows."""
    return f"""
    (function () {{
      var isJa = document.documentElement.lang === 'ja';
      var OVERRIDES_KEY = 'kpiNavigator.plLabelOverrides';
      var CATALOG_KEY = 'kpiNavigator.plLineCatalog';
      var DEFAULT_CATALOG_LINES = {expense_catalog_json};
      var editAria = {json.dumps(edit_aria, ensure_ascii=False)};
      var windowEl = document.getElementById('pl-table-window');
      var editingEl = null;

      function loadOverrides() {{
        try {{
          var raw = localStorage.getItem(OVERRIDES_KEY);
          if (raw) {{
            var parsed = JSON.parse(raw);
            if (parsed && typeof parsed === 'object') return parsed;
          }}
        }} catch (_e) {{}}
        return {{}};
      }}

      function saveOverrides(map) {{
        try {{
          localStorage.setItem(OVERRIDES_KEY, JSON.stringify(map));
        }} catch (_e) {{}}
      }}

      function loadCatalogLines() {{
        try {{
          var raw = localStorage.getItem(CATALOG_KEY);
          if (raw) {{
            var parsed = JSON.parse(raw);
            if (parsed && Array.isArray(parsed.lines) && parsed.lines.length) {{
              return parsed.lines;
            }}
          }}
        }} catch (_e) {{}}
        return JSON.parse(JSON.stringify(DEFAULT_CATALOG_LINES));
      }}

      function saveCatalogLines(lines) {{
        try {{
          localStorage.setItem(
            CATALOG_KEY,
            JSON.stringify({{ lines: lines, updatedAt: Date.now() }})
          );
          window.dispatchEvent(new Event('pl-expense-catalog-changed'));
        }} catch (_e) {{}}
      }}

      function applyLabelOverrides() {{
        var catalogById = {{}};
        try {{
          var craw = localStorage.getItem(CATALOG_KEY);
          if (craw) {{
            var cparsed = JSON.parse(craw);
            (cparsed && cparsed.lines ? cparsed.lines : []).forEach(function (line) {{
              if (line && line.lineId) catalogById[line.lineId] = line;
            }});
          }}
        }} catch (_e) {{}}
        var overrides = loadOverrides();
        document.querySelectorAll('[data-pl-label-editable="1"]').forEach(function (el) {{
          var scope = el.getAttribute('data-label-scope');
          if (scope === 'expense-detail') return;
          var id = el.getAttribute('data-label-id');
          if (!id) return;
          if (scope === 'income' && catalogById[id]) {{
            var c = catalogById[id];
            el.textContent = isJa ? (c.labelJa || el.textContent) : (c.labelEn || el.textContent);
            return;
          }}
          if (!overrides[id]) return;
          var o = overrides[id];
          el.textContent = isJa ? (o.labelJa || el.textContent) : (o.labelEn || el.textContent);
        }});
      }}

      function selectAll(el) {{
        var range = document.createRange();
        range.selectNodeContents(el);
        var sel = window.getSelection();
        if (!sel) return;
        sel.removeAllRanges();
        sel.addRange(range);
      }}

      function finishEdit(save, reason) {{
        if (!editingEl) return;
        var el = editingEl;
        var original = el.getAttribute('data-original-label') || '';
        var scope = el.getAttribute('data-label-scope');
        var id = el.getAttribute('data-label-id');
        var next = (el.textContent || '').replace(/\\s+/g, ' ').trim();
        el.contentEditable = 'false';
        el.classList.remove('pl-h-label__text--editing');
        el.removeAttribute('data-original-label');
        editingEl = null;
        if (!save || !next) {{
          el.textContent = original;
          return;
        }}
        /* expense-detail は統合モーダル（pl-expense-label-edit-modal）で編集する */
        if (scope === 'expense-detail') {{
          el.textContent = original;
          return;
        }}
        if (next === original) return;
        var overrides = loadOverrides();
        if (!overrides[id]) overrides[id] = {{}};
        if (isJa) overrides[id].labelJa = next;
        else overrides[id].labelEn = next;
        saveOverrides(overrides);
        el.textContent = next;
      }}

      function startEdit(el) {{
        if (!el || el.classList.contains('pl-h-label__text--editing')) return;
        var scope = el.getAttribute('data-label-scope');
        var id = el.getAttribute('data-label-id');
        if (scope === 'expense-detail' && id) {{
          window.dispatchEvent(
            new CustomEvent('pl-expense-label-edit-request', {{ detail: {{ lineId: id }} }})
          );
          return;
        }}
        if (editingEl && editingEl !== el) finishEdit(true, 'blur');
        editingEl = el;
        el.setAttribute('data-original-label', el.textContent || '');
        el.classList.add('pl-h-label__text--editing');
        el.contentEditable = 'true';
        el.focus();
        selectAll(el);
      }}

      if (windowEl) {{
        windowEl.addEventListener('dblclick', function (e) {{
          var el = e.target && e.target.closest ? e.target.closest('[data-pl-label-editable="1"]') : null;
          if (!el || !windowEl.contains(el)) return;
          e.preventDefault();
          e.stopPropagation();
          startEdit(el);
        }});
        windowEl.addEventListener('keydown', function (e) {{
          var focused = document.activeElement;
          if (
            focused &&
            focused.getAttribute &&
            focused.getAttribute('data-pl-label-editable') === '1' &&
            !focused.classList.contains('pl-h-label__text--editing') &&
            e.key === 'F2'
          ) {{
            e.preventDefault();
            startEdit(focused);
            return;
          }}
          if (!editingEl) return;
          if (e.key === 'Enter') {{
            e.preventDefault();
            finishEdit(true, 'enter');
          }} else if (e.key === 'Escape') {{
            e.preventDefault();
            finishEdit(false, 'escape');
          }}
        }});
        windowEl.addEventListener('focusout', function (e) {{
          if (!editingEl || e.target !== editingEl) return;
          var el = editingEl;
          setTimeout(function () {{
            if (editingEl === el && document.activeElement !== el) {{
              finishEdit(true, 'blur');
            }}
          }}, 0);
        }});
      }}

      applyLabelOverrides();
      window.addEventListener('pl-expense-catalog-changed', applyLabelOverrides);
      window.addEventListener('storage', function (ev) {{
        if (ev.key === CATALOG_KEY || ev.key === OVERRIDES_KEY) applyLabelOverrides();
      }});

      window.addEventListener('pl-expense-line-added', function (e) {{
        var lineId = e.detail && e.detail.lineId;
        if (!lineId) return;
        setTimeout(function () {{
          window.dispatchEvent(
            new CustomEvent('pl-expense-label-edit-request', {{ detail: {{ lineId: lineId }} }})
          );
        }}, 50);
      }});
    }})();
"""


def pl_compare_client_js(*, monthly_edit: str, labels: dict) -> str:
    lj = json.dumps(labels, ensure_ascii=False)
    return f"""
    (function () {{
      var L = {lj};
      var root = document.getElementById('pl-graph-overlay');
      var btnOpen = document.getElementById('pl-graph-open');
      var btnClose = document.getElementById('pl-graph-overlay-close');
      var dateBtn = document.getElementById('pl-compare-date-btn');
      var todayBtn = document.getElementById('pl-compare-today');
      var prevBtn = document.getElementById('pl-compare-prev-day');
      var nextBtn = document.getElementById('pl-compare-next-day');
      var dateInput = document.getElementById('pl-compare-date-input');
      var scrollEl = document.getElementById('pl-compare-scroll');
      var contentEl = document.getElementById('pl-compare-content');
      var lastFocused = null;
      var selectedIso = null;
      var areaButtons = root ? root.querySelectorAll('[data-pl-compare-jump]') : [];

      function pad2(n) {{
        return n < 10 ? '0' + n : String(n);
      }}

      function getTodayIso() {{
        var now = new Date();
        return now.getFullYear() + '-' + pad2(now.getMonth() + 1) + '-' + pad2(now.getDate());
      }}

      function shiftIso(iso, delta) {{
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return iso;
        d.setDate(d.getDate() + delta);
        return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate());
      }}

      function resolveIso() {{
        var params = new URLSearchParams(window.location.search);
        var y = Number(params.get('year'));
        var m = Number(params.get('month'));
        if (Number.isFinite(y) && Number.isFinite(m) && m >= 1 && m <= 12) {{
          var now = new Date();
          var day = now.getFullYear() === y && now.getMonth() + 1 === m
            ? now.getDate()
            : 1;
          return y + '-' + pad2(m) + '-' + pad2(day);
        }}
        return getTodayIso();
      }}

      function fmtDate(iso) {{
        if (!iso) return '—';
        var d = new Date(iso + 'T00:00:00');
        if (!isFinite(d.getTime())) return iso;
        if (document.documentElement.lang === 'ja') {{
          var wd = ['日', '月', '火', '水', '木', '金', '土'][d.getDay()];
          return d.getFullYear() + '/' + (d.getMonth() + 1) + '/' + d.getDate() + '(' + wd + ')';
        }}
        var wdEn = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'][d.getDay()];
        return d.getFullYear() + '/' + (d.getMonth() + 1) + '/' + d.getDate() + ' ' + wdEn;
      }}

      function sameWeekdayLastYearIso(iso) {{
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return iso;
        d.setDate(d.getDate() - 364);
        return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate());
      }}

      function money(n) {{
        var v = Math.round(Number(n) || 0);
        if (document.documentElement.lang === 'ja') return '¥' + v.toLocaleString('en-US');
        return '$' + v.toLocaleString('en-US');
      }}

      function pct1(n) {{
        return (Math.round(Number(n) * 10) / 10) + '%';
      }}

      function fetchCurrentFlSnapshot(iso) {{
        /* 当月累積: PL 連携前のギミック。上段は常に描画 */
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        var bump = isFinite(d.getTime()) ? d.getDate() % 97 : 0;
        var income = 123456 + bump;
        var expenses = 3456 + Math.round(bump * 0.35);
        var variable = 2456 + Math.round(bump * 0.22);
        var fixed = Math.max(0, expenses - variable);
        if (fixed < 900) {{
          fixed = 1234 + Math.round(bump * 0.08);
          variable = Math.max(0, expenses - fixed);
        }}
        return {{
          income: income,
          expenses: expenses,
          variable: variable,
          fixed: fixed,
        }};
      }}

      function fetchPreviousFlSnapshot(iso) {{
        /* 前年同曜日累積: PL 未入力時は null（現状はギミックで常時返却） */
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return null;
        var bump = d.getDate() % 89;
        var income = 123432 + bump;
        var expenses = 3432 + Math.round(bump * 0.31);
        var variable = 2421 + Math.round(bump * 0.19);
        var fixed = Math.max(0, expenses - variable);
        if (fixed < 900) {{
          fixed = 1456 + Math.round(bump * 0.07);
          variable = Math.max(0, expenses - fixed);
        }}
        return {{
          income: income,
          expenses: expenses,
          variable: variable,
          fixed: fixed,
        }};
      }}

      function expenseVisualWidth(incomeW, expensePct, blockIndex) {{
        /* Figma 寄せ: 支出棒は売上比の実数値ではなく Income 棒に対する視覚比率で描画 */
        var ratio = 0.662 + blockIndex * 0.021 + (expensePct - 10) * 0.0035;
        if (ratio < 0.62) ratio = 0.62;
        if (ratio > 0.745) ratio = 0.745;
        return incomeW * ratio;
      }}

      function renderHsnapRow(label, trackHtml, meta) {{
        return (
          '<div class="pl-compare-hsnap-row">' +
          '<span class="pl-compare-hsnap-row__label">' +
          label +
          '</span>' +
          '<div class="pl-compare-hsnap-row__track">' +
          trackHtml +
          '</div>' +
          '<span class="pl-compare-hsnap-row__meta">' +
          meta +
          '</span></div>'
        );
      }}

      function renderHsnapBlock(caption, metrics, maxIncome, blockIndex, allowNoData) {{
        if (!metrics) {{
          if (!allowNoData) return '';
          return (
            '<section class="pl-compare-hsnap">' +
            '<h4 class="pl-compare-hsnap__date">' +
            caption +
            '</h4>' +
            '<p class="pl-compare-hsnap__empty">' +
            L.compare_no_data +
            '</p></section>'
          );
        }}
        if (!maxIncome) maxIncome = metrics.income || 1;
        var incomeW = Math.max(0, Math.min(100, (metrics.income / maxIncome) * 100));
        var expensePct = metrics.income ? (metrics.expenses / metrics.income) * 100 : 0;
        var expenseW = expenseVisualWidth(incomeW, expensePct, blockIndex || 0);
        var variablePct = metrics.income ? (metrics.variable / metrics.income) * 100 : 0;
        var fixedPct = metrics.income ? (metrics.fixed / metrics.income) * 100 : 0;
        var splitOrangeW = metrics.expenses ? (metrics.variable / metrics.expenses) * 100 : 0;
        var splitYellowW = metrics.expenses ? (metrics.fixed / metrics.expenses) * 100 : 0;
        var splitBar =
          '<span class="pl-compare-hbar-stack" style="width:' +
          expenseW.toFixed(4) +
          '%">' +
          '<span class="pl-compare-hbar pl-compare-hbar--orange" style="width:' +
          splitOrangeW.toFixed(4) +
          '%"></span>' +
          '<span class="pl-compare-hbar pl-compare-hbar--yellow" style="width:' +
          splitYellowW.toFixed(4) +
          '%"></span></span>';
        return (
          '<section class="pl-compare-hsnap">' +
          '<h4 class="pl-compare-hsnap__date">' +
          caption +
          '</h4>' +
          '<div class="pl-compare-hsnap__rows">' +
          renderHsnapRow(
            L.compare_income,
            '<span class="pl-compare-hbar pl-compare-hbar--green" style="width:' +
              incomeW.toFixed(4) +
              '%"></span>',
            money(metrics.income)
          ) +
          renderHsnapRow(
            L.compare_food_labor,
            '<span class="pl-compare-hbar pl-compare-hbar--red" style="width:' +
              expenseW.toFixed(4) +
              '%"></span>',
            money(metrics.expenses) + ' : ' + pct1(expensePct)
          ) +
          renderHsnapRow(
            L.compare_food_slash_labor,
            splitBar,
            money(metrics.variable) +
              ' : ' +
              pct1(variablePct) +
              ' : ' +
              money(metrics.fixed) +
              ' : ' +
              pct1(fixedPct)
          ) +
          '</div></section>'
        );
      }}

      var compareLineState = {{
        1: {{ metric: 'income', showLast: true, showBest: true }},
        2: {{ metric: 'income', showLast: true, showBest: true }},
        3: {{ metric: 'income', showLast: true, showBest: true }},
      }};
      var compareDailyState = {{
        1: {{ metric: 'income', showLast: true, showBest: true }},
        2: {{ metric: 'income', showLast: true, showBest: true }},
        3: {{ metric: 'income', showLast: true, showBest: true }},
      }};
      var AREA1_SERVICE_START_YEAR = 2024;

      function area1YearsWithData(iso) {{
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return 1;
        return Math.max(1, d.getFullYear() - AREA1_SERVICE_START_YEAR + 1);
      }}

      function area1CanShowBestYear(iso) {{
        return area1YearsWithData(iso) >= 3;
      }}

      function area1BestYearNumber(iso) {{
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return AREA1_SERVICE_START_YEAR;
        return d.getFullYear() - 2;
      }}

      function isoParts(iso) {{
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return null;
        return {{ year: d.getFullYear(), month: d.getMonth() + 1, day: d.getDate() }};
      }}

      function fmtDateYmd(year, month, day) {{
        var d = new Date(year, month - 1, day);
        if (!isFinite(d.getTime())) return year + '/' + month + '/' + day;
        if (document.documentElement.lang === 'ja') {{
          var wd = ['日', '月', '火', '水', '木', '金', '土'][d.getDay()];
          return year + '/' + month + '/' + day + '(' + wd + ')';
        }}
        var wdEn = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'][d.getDay()];
        return year + '/' + month + '/' + day + ' ' + wdEn;
      }}

      function area1MetricLabel(metric) {{
        var map = {{
          income: L.compare_income,
          expenses: L.compare_expenses,
          fixed: L.compare_fixed,
          expected: L.compare_expected,
          profit: L.compare_profit,
        }};
        return map[metric] || metric;
      }}

      function snapArea1Day(svgX, daysInMonth, dim, padL, plotW) {{
        var x1 = comparePeriodCenterX(1, daysInMonth, padL, plotW);
        var xN = comparePeriodCenterX(daysInMonth, daysInMonth, padL, plotW);
        var span = xN - x1;
        if (span <= 0) return 1;
        var day = Math.round(1 + ((svgX - x1) / span) * (daysInMonth - 1));
        return Math.max(1, Math.min(dim, day));
      }}

      function area1YForValue(v, yMax, padT, plotH) {{
        return padT + (1 - Math.min(1, (v || 0) / yMax)) * plotH;
      }}

      function fmtComparePeriodDate(year, month, period, axisMode) {{
        if (axisMode === 'month') return year + '/' + period;
        return fmtDateYmd(year, month, period);
      }}

      function compareRefYear(cfg, seriesKey) {{
        if (cfg.refYears && cfg.refYears[seriesKey] != null) return cfg.refYears[seriesKey];
        var parts = cfg.isoParts;
        if (!parts) return cfg.bestYear;
        if (seriesKey === 'thisYear') return parts.year;
        if (seriesKey === 'lastYear') return parts.year - 1;
        return cfg.bestYear;
      }}

      function area1FillChartTooltip(tooltip, cfg, day) {{
        var parts = cfg.isoParts;
        if (!parts || !tooltip) return null;
        var axisMode = cfg.axisMode || 'day';
        var idx = day - 1;
        var rows = [];
        rows.push({{
          label: L.compare_this_year,
          date: fmtComparePeriodDate(compareRefYear(cfg, 'thisYear'), parts.month, day, axisMode),
          value: cfg.values.thisYear[idx] || 0,
          color: '#66e7ff',
        }});
        if (cfg.showLast) {{
          rows.push({{
            label: L.compare_last_year,
            date: fmtComparePeriodDate(compareRefYear(cfg, 'lastYear'), parts.month, day, axisMode),
            value: cfg.values.lastYear[idx] || 0,
            color: '#e8e54b',
          }});
        }}
        if (cfg.showBest && cfg.canShowBest) {{
          rows.push({{
            label: L.compare_best_year,
            date: fmtComparePeriodDate(compareRefYear(cfg, 'bestYear'), parts.month, day, axisMode),
            value: cfg.values.bestYear[idx] || 0,
            color: '#16d33a',
          }});
        }}
        var snapEl = tooltip.querySelector('[data-field="snap"]');
        if (snapEl) {{
          snapEl.textContent = fmtComparePeriodDate(compareRefYear(cfg, 'thisYear'), parts.month, day, axisMode);
        }}
        var metricEl = tooltip.querySelector('[data-field="metric"]');
        if (metricEl) {{
          metricEl.textContent = area1MetricLabel(cfg.metric);
        }}
        var rowsEl = tooltip.querySelector('[data-field="rows"]');
        if (rowsEl) {{
          rowsEl.innerHTML = rows
            .map(function (r) {{
              return (
                '<p class="pl-compare-chart-tooltip__row">' +
                '<span class="pl-compare-chart-tooltip__series" style="color:' +
                r.color +
                '">' +
                r.label +
                ' (' +
                r.date +
                ')</span>' +
                '<span class="pl-compare-chart-tooltip__value">' +
                money(r.value) +
                '</span></p>'
              );
            }})
            .join('');
        }}
        var anchorY = area1YForValue(cfg.values.thisYear[idx] || 0, cfg.yMax, cfg.padT, cfg.plotH);
        return {{
          x: comparePeriodCenterX(day, cfg.daysInMonth, cfg.padL, cfg.plotW),
          y: anchorY,
        }};
      }}

      function area1PositionChartTooltip(tooltip, wrap, cfg, anchorX, anchorY) {{
        var rect = wrap.getBoundingClientRect();
        if (!rect.width || !rect.height) return;
        var pxLeft = (anchorX / cfg.w) * rect.width;
        var pxTop = (anchorY / cfg.h) * rect.height;
        var left = pxLeft + 16;
        var top = pxTop - 16;
        if (left + 280 > rect.width) left = Math.max(8, pxLeft - 296);
        if (top + 150 > rect.height) top = Math.max(8, pxTop - 140);
        if (top < 8) top = pxTop + 16;
        tooltip.style.left = left + 'px';
        tooltip.style.top = top + 'px';
      }}

      function bindArea1LineChartHover(wrap, cfg) {{
        if (!wrap) return;
        var hoverLayer = wrap.querySelector('[data-pl-chart-hover]');
        var tooltip = wrap.querySelector('[data-pl-chart-tooltip]');
        var svg = wrap.querySelector('.pl-compare-line__svg');
        if (!hoverLayer || !tooltip || !svg) return;

        var ns = 'http://www.w3.org/2000/svg';
        var hoverG = document.createElementNS(ns, 'g');
        hoverG.setAttribute('class', 'pl-compare-line__hover-ui');
        hoverG.setAttribute('aria-hidden', 'true');
        var guideV = document.createElementNS(ns, 'line');
        guideV.setAttribute('class', 'pl-compare-line__guide-v-svg');
        var dotKeys = ['thisYear', 'lastYear', 'bestYear'];
        var dots = {{}};
        dotKeys.forEach(function (key) {{
          var c = document.createElementNS(ns, 'circle');
          c.setAttribute('class', 'pl-compare-line__hit-dot pl-compare-line__hit-dot--' + key);
          c.setAttribute('r', '6');
          dots[key] = c;
          hoverG.appendChild(c);
        }});
        hoverG.insertBefore(guideV, hoverG.firstChild);
        svg.appendChild(hoverG);

        var HIT_RADIUS = 22;

        function visibleSeries() {{
          var list = [{{ key: 'thisYear' }}];
          if (cfg.showLast) list.push({{ key: 'lastYear' }});
          if (cfg.showBest && cfg.canShowBest) list.push({{ key: 'bestYear' }});
          return list;
        }}

        function pointAt(key, day) {{
          var idx = day - 1;
          var v = cfg.values[key][idx];
          if (!Number.isFinite(v)) return null;
          return {{
            x: comparePeriodCenterX(day, cfg.daysInMonth, cfg.padL, cfg.plotW),
            y: area1YForValue(v, cfg.yMax, cfg.padT, cfg.plotH),
            v: v,
          }};
        }}

        function hide() {{
          guideV.classList.remove('is-visible');
          dotKeys.forEach(function (key) {{
            dots[key].classList.remove('is-visible');
          }});
          tooltip.hidden = true;
          tooltip.classList.remove('is-visible');
        }}

        function onMove(ev) {{
          var rect = wrap.getBoundingClientRect();
          if (!rect.width || !rect.height) return;
          var ratioX = cfg.w / rect.width;
          var ratioY = cfg.h / rect.height;
          var svgX = (ev.clientX - rect.left) * ratioX;
          var svgY = (ev.clientY - rect.top) * ratioY;
          if (
            svgX < cfg.padL ||
            svgX > cfg.padL + cfg.plotW ||
            svgY < cfg.padT ||
            svgY > cfg.padT + cfg.plotH
          ) {{
            hide();
            return;
          }}
          var day = snapArea1Day(svgX, cfg.daysInMonth, cfg.dim, cfg.padL, cfg.plotW);
          var hit = null;
          visibleSeries().forEach(function (s) {{
            var pt = pointAt(s.key, day);
            if (!pt) return;
            var dist = Math.hypot(svgX - pt.x, svgY - pt.y);
            if (dist <= HIT_RADIUS && (!hit || dist < hit.dist)) {{
              hit = {{ day: day, x: pt.x, dist: dist }};
            }}
          }});
          if (!hit) {{
            hide();
            return;
          }}
          guideV.setAttribute('x1', hit.x);
          guideV.setAttribute('x2', hit.x);
          guideV.setAttribute('y1', cfg.padT);
          guideV.setAttribute('y2', cfg.padT + cfg.plotH);
          guideV.classList.add('is-visible');
          dotKeys.forEach(function (key) {{
            dots[key].classList.remove('is-visible');
          }});
          visibleSeries().forEach(function (s) {{
            var pt = pointAt(s.key, hit.day);
            if (pt && dots[s.key]) {{
              dots[s.key].setAttribute('cx', pt.x);
              dots[s.key].setAttribute('cy', pt.y);
              dots[s.key].classList.add('is-visible');
            }}
          }});
          var anchor = area1FillChartTooltip(tooltip, cfg, hit.day);
          if (!anchor) {{
            hide();
            return;
          }}
          tooltip.hidden = false;
          tooltip.classList.add('is-visible');
          area1PositionChartTooltip(tooltip, wrap, cfg, anchor.x, anchor.y);
        }}

        hoverLayer.addEventListener('mousemove', onMove);
        hoverLayer.addEventListener('mouseleave', hide);
      }}

      function bindArea1DailyChartHover(wrap, cfg) {{
        if (!wrap) return;
        var hoverLayer = wrap.querySelector('[data-pl-chart-hover]');
        var tooltip = wrap.querySelector('[data-pl-chart-tooltip]');
        var guide = wrap.querySelector('.pl-compare-line__guide-v');
        if (!hoverLayer || !tooltip) return;

        function hide() {{
          tooltip.hidden = true;
          tooltip.classList.remove('is-visible');
          if (guide) guide.hidden = true;
        }}

        function onMove(ev) {{
          var rect = wrap.getBoundingClientRect();
          if (!rect.width || !rect.height) return;
          var ratioX = cfg.w / rect.width;
          var ratioY = cfg.h / rect.height;
          var svgX = (ev.clientX - rect.left) * ratioX;
          var svgY = (ev.clientY - rect.top) * ratioY;
          if (
            svgX < cfg.padL ||
            svgX > cfg.padL + cfg.plotW ||
            svgY < cfg.padT ||
            svgY > cfg.padT + cfg.plotH
          ) {{
            hide();
            return;
          }}
          var day = snapArea1Day(svgX, cfg.daysInMonth, cfg.dim, cfg.padL, cfg.plotW);
          var anchor = area1FillChartTooltip(tooltip, cfg, day);
          if (!anchor) {{
            hide();
            return;
          }}
          var x = anchor.x;
          if (guide) {{
            guide.hidden = false;
            guide.style.left = ((x / cfg.w) * 100).toFixed(4) + '%';
          }}
          tooltip.hidden = false;
          tooltip.classList.add('is-visible');
          area1PositionChartTooltip(tooltip, wrap, cfg, anchor.x, anchor.y);
        }}

        hoverLayer.addEventListener('mousemove', onMove);
        hoverLayer.addEventListener('mouseleave', hide);
      }}

      function buildArea1ChartData(iso) {{
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return null;
        var dim = d.getDate();
        var year = d.getFullYear();
        var month = d.getMonth() + 1;
        var periodCount = new Date(year, month, 0).getDate();
        var daySeed = (year * 37 + month * 97 + dim * 13) % 1000;
        return buildCompareDayChartData(dim, periodCount, daySeed);
      }}

      function compareArea2FirstSunday(year) {{
        for (var d = 1; d <= 31; d++) {{
          if (new Date(year, 0, d).getDay() === 0) return d;
        }}
        return 32;
      }}

      function compareArea2LastSundayOfYear(year) {{
        var decDays = new Date(year, 12, 0).getDate();
        for (var d = decDays; d >= 1; d--) {{
          if (new Date(year, 11, d).getDay() === 0) return d;
        }}
        return 0;
      }}

      /* Area2 店休: 1月は最初の日曜まで休み / 以降毎週日曜 / 12月は最終日曜〜年末（該当なければ30日〜） */
      function compareArea2StoreClosed(year, month, day) {{
        if (month === 1) {{
          var firstSun = compareArea2FirstSunday(year);
          if (day < firstSun) return true;
        }}
        var dow = new Date(year, month - 1, day).getDay();
        if (dow === 0) {{
          if (month === 1 && day === compareArea2FirstSunday(year)) return false;
          return true;
        }}
        if (month === 12) {{
          var lastSun = compareArea2LastSundayOfYear(year);
          var closeFrom = lastSun >= 30 ? lastSun : 30;
          if (day >= closeFrom) return true;
        }}
        return false;
      }}

      function compareMockDayValues(i, daySeed, yearSalt) {{
        var salt = (daySeed || 0) + (yearSalt || 0) * 17;
        var cyc = 1 + ((i + salt) % 7) * 0.045;
        var baseSales = 5900 + ((i * 73 + salt) % 2100);
        var salesTY = Math.round(baseSales * cyc);
        var salesLY = Math.round(salesTY * (0.93 + ((i + 2) % 4) * 0.012));
        var salesBY = Math.round(Math.max(salesTY, salesLY) * (1.12 + ((i + 1) % 3) * 0.008));
        var expTY = Math.round(salesTY * (0.29 + ((i + 1) % 4) * 0.01));
        var expLY = Math.round(salesLY * (0.285 + ((i + 2) % 4) * 0.01));
        var expBY = Math.round(salesBY * (0.278 + ((i + 3) % 4) * 0.01));
        var fixedTY = Math.round(expTY * (0.46 + (i % 2) * 0.02));
        var fixedLY = Math.round(expLY * (0.45 + ((i + 1) % 2) * 0.02));
        var fixedBY = Math.round(expBY * (0.44 + ((i + 2) % 2) * 0.02));
        var expectedTY = Math.max(0, expTY - fixedTY);
        var expectedLY = Math.max(0, expLY - fixedLY);
        var expectedBY = Math.max(0, expBY - fixedBY);
        var profitTY = salesTY - expTY;
        var profitLY = salesLY - expLY;
        var profitBY = salesBY - expBY;
        return {{
          income: {{ thisYear: salesTY, lastYear: salesLY, bestYear: salesBY }},
          expenses: {{ thisYear: expTY, lastYear: expLY, bestYear: expBY }},
          fixed: {{ thisYear: fixedTY, lastYear: fixedLY, bestYear: fixedBY }},
          expected: {{ thisYear: expectedTY, lastYear: expectedLY, bestYear: expectedBY }},
          profit: {{ thisYear: profitTY, lastYear: profitLY, bestYear: profitBY }},
        }};
      }}

      function compareZeroDayValues() {{
        return {{
          income: {{ thisYear: 0, lastYear: 0, bestYear: 0 }},
          expenses: {{ thisYear: 0, lastYear: 0, bestYear: 0 }},
          fixed: {{ thisYear: 0, lastYear: 0, bestYear: 0 }},
          expected: {{ thisYear: 0, lastYear: 0, bestYear: 0 }},
          profit: {{ thisYear: 0, lastYear: 0, bestYear: 0 }},
        }};
      }}

      function comparePushCumulative(cumulative, cum, dayVals, closedBySeries) {{
        area1ChartMetrics().forEach(function (seriesKey) {{
          ['income', 'expenses', 'fixed', 'expected', 'profit'].forEach(function (k) {{
            var v = dayVals[k][seriesKey] || 0;
            if (!closedBySeries[seriesKey]) {{
              cum[seriesKey][k] += v;
            }}
            cumulative[k][seriesKey].push(cum[seriesKey][k]);
          }});
        }});
      }}

      function buildArea2ChartData(iso) {{
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return null;
        var selYear = d.getFullYear();
        var month = d.getMonth() + 1;
        var yearTY = selYear - 1;
        var yearLY = selYear - 2;
        var yearBY = area1BestYearNumber(iso);
        var periodCount = new Date(yearTY, month, 0).getDate();
        var dim = periodCount;
        var daySeed = ((selYear * 37 + month * 97) % 1000) + 571;
        var daily = {{
          income: {{ thisYear: [], lastYear: [], bestYear: [] }},
          expenses: {{ thisYear: [], lastYear: [], bestYear: [] }},
          fixed: {{ thisYear: [], lastYear: [], bestYear: [] }},
          expected: {{ thisYear: [], lastYear: [], bestYear: [] }},
          profit: {{ thisYear: [], lastYear: [], bestYear: [] }},
        }};
        var cumulative = {{
          income: {{ thisYear: [], lastYear: [], bestYear: [] }},
          expenses: {{ thisYear: [], lastYear: [], bestYear: [] }},
          fixed: {{ thisYear: [], lastYear: [], bestYear: [] }},
          expected: {{ thisYear: [], lastYear: [], bestYear: [] }},
          profit: {{ thisYear: [], lastYear: [], bestYear: [] }},
        }};
        var cum = {{
          thisYear: {{ income: 0, expenses: 0, fixed: 0, expected: 0, profit: 0 }},
          lastYear: {{ income: 0, expenses: 0, fixed: 0, expected: 0, profit: 0 }},
          bestYear: {{ income: 0, expenses: 0, fixed: 0, expected: 0, profit: 0 }},
        }};
        var seriesYears = {{ thisYear: yearTY, lastYear: yearLY, bestYear: yearBY }};
        for (var i = 1; i <= periodCount; i++) {{
          var closedBySeries = {{
            thisYear: compareArea2StoreClosed(yearTY, month, i),
            lastYear: compareArea2StoreClosed(yearLY, month, i),
            bestYear: compareArea2StoreClosed(yearBY, month, i),
          }};
          var dayVals = compareMockDayValues(i, daySeed, 0);
          if (closedBySeries.thisYear && closedBySeries.lastYear && closedBySeries.bestYear) {{
            dayVals = compareZeroDayValues();
          }} else {{
            if (closedBySeries.thisYear) {{
              ['income', 'expenses', 'fixed', 'expected', 'profit'].forEach(function (k) {{
                dayVals[k].thisYear = 0;
              }});
            }}
            if (closedBySeries.lastYear) {{
              ['income', 'expenses', 'fixed', 'expected', 'profit'].forEach(function (k) {{
                dayVals[k].lastYear = 0;
              }});
            }}
            if (closedBySeries.bestYear) {{
              ['income', 'expenses', 'fixed', 'expected', 'profit'].forEach(function (k) {{
                dayVals[k].bestYear = 0;
              }});
            }}
          }}
          ['income', 'expenses', 'fixed', 'expected', 'profit'].forEach(function (k) {{
            daily[k].thisYear.push(dayVals[k].thisYear);
            daily[k].lastYear.push(dayVals[k].lastYear);
            daily[k].bestYear.push(dayVals[k].bestYear);
          }});
          comparePushCumulative(cumulative, cum, dayVals, closedBySeries);
        }}
        return {{
          daily: daily,
          cumulative: cumulative,
          dim: dim,
          periodCount: periodCount,
          axisMode: 'day',
          refYears: seriesYears,
          storeClosedRule: 'area2',
        }};
      }}

      function buildArea3ChartData(iso) {{
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return null;
        var dim = d.getMonth() + 1;
        var periodCount = 12;
        var year = d.getFullYear();
        var daySeed = (year * 11 + dim * 31) % 1000;
        var daily = {{
          income: {{ thisYear: [], lastYear: [], bestYear: [] }},
          expenses: {{ thisYear: [], lastYear: [], bestYear: [] }},
          fixed: {{ thisYear: [], lastYear: [], bestYear: [] }},
          expected: {{ thisYear: [], lastYear: [], bestYear: [] }},
          profit: {{ thisYear: [], lastYear: [], bestYear: [] }},
        }};
        var cumulative = {{
          income: {{ thisYear: [], lastYear: [], bestYear: [] }},
          expenses: {{ thisYear: [], lastYear: [], bestYear: [] }},
          fixed: {{ thisYear: [], lastYear: [], bestYear: [] }},
          expected: {{ thisYear: [], lastYear: [], bestYear: [] }},
          profit: {{ thisYear: [], lastYear: [], bestYear: [] }},
        }};
        var cum = {{
          thisYear: {{ income: 0, expenses: 0, fixed: 0, expected: 0, profit: 0 }},
          lastYear: {{ income: 0, expenses: 0, fixed: 0, expected: 0, profit: 0 }},
          bestYear: {{ income: 0, expenses: 0, fixed: 0, expected: 0, profit: 0 }},
        }};
        for (var m = 1; m <= dim; m++) {{
          var skip = (m + daySeed) % 5 === 0;
          var cyc = 1 + ((m + daySeed) % 4) * 0.05;
          var baseSales = skip ? 0 : Math.round((185000 + ((m * 8900 + daySeed) % 52000)) * cyc);
          var salesTY = baseSales;
          var salesLY = skip ? 0 : Math.round(salesTY * (0.91 + ((m + 1) % 3) * 0.015));
          var salesBY = skip ? 0 : Math.round(Math.max(salesTY, salesLY) * (1.1 + ((m + 2) % 3) * 0.01));
          var expTY = skip ? 0 : Math.round(salesTY * (0.31 + ((m + 1) % 3) * 0.012));
          var expLY = skip ? 0 : Math.round(salesLY * (0.305 + ((m + 2) % 3) * 0.012));
          var expBY = skip ? 0 : Math.round(salesBY * (0.298 + ((m + 3) % 3) * 0.012));
          var fixedTY = skip ? 0 : Math.round(expTY * (0.47 + (m % 2) * 0.02));
          var fixedLY = skip ? 0 : Math.round(expLY * (0.46 + ((m + 1) % 2) * 0.02));
          var fixedBY = skip ? 0 : Math.round(expBY * (0.45 + ((m + 2) % 2) * 0.02));
          var expectedTY = skip ? 0 : Math.max(0, expTY - fixedTY);
          var expectedLY = skip ? 0 : Math.max(0, expLY - fixedLY);
          var expectedBY = skip ? 0 : Math.max(0, expBY - fixedBY);
          var profitTY = skip ? 0 : salesTY - expTY;
          var profitLY = skip ? 0 : salesLY - expLY;
          var profitBY = skip ? 0 : salesBY - expBY;
          ['income', 'expenses', 'fixed', 'expected', 'profit'].forEach(function (k) {{
            var map = {{
              income: [salesTY, salesLY, salesBY],
              expenses: [expTY, expLY, expBY],
              fixed: [fixedTY, fixedLY, fixedBY],
              expected: [expectedTY, expectedLY, expectedBY],
              profit: [profitTY, profitLY, profitBY],
            }};
            daily[k].thisYear.push(map[k][0]);
            daily[k].lastYear.push(map[k][1]);
            daily[k].bestYear.push(map[k][2]);
          }});
          cum.thisYear.income += salesTY;
          cum.thisYear.expenses += expTY;
          cum.thisYear.fixed += fixedTY;
          cum.thisYear.expected += expectedTY;
          cum.thisYear.profit += profitTY;
          cum.lastYear.income += salesLY;
          cum.lastYear.expenses += expLY;
          cum.lastYear.fixed += fixedLY;
          cum.lastYear.expected += expectedLY;
          cum.lastYear.profit += profitLY;
          cum.bestYear.income += salesBY;
          cum.bestYear.expenses += expBY;
          cum.bestYear.fixed += fixedBY;
          cum.bestYear.expected += expectedBY;
          cum.bestYear.profit += profitBY;
          ['income', 'expenses', 'fixed', 'expected', 'profit'].forEach(function (k) {{
            cumulative[k].thisYear.push(cum.thisYear[k]);
            cumulative[k].lastYear.push(cum.lastYear[k]);
            cumulative[k].bestYear.push(cum.bestYear[k]);
          }});
        }}
        return {{ daily: daily, cumulative: cumulative, dim: dim, periodCount: periodCount, axisMode: 'month' }};
      }}

      function buildCompareDayChartData(dim, periodCount, daySeed) {{
        var daily = {{
          income: {{ thisYear: [], lastYear: [], bestYear: [] }},
          expenses: {{ thisYear: [], lastYear: [], bestYear: [] }},
          fixed: {{ thisYear: [], lastYear: [], bestYear: [] }},
          expected: {{ thisYear: [], lastYear: [], bestYear: [] }},
          profit: {{ thisYear: [], lastYear: [], bestYear: [] }},
        }};
        var cumulative = {{
          income: {{ thisYear: [], lastYear: [], bestYear: [] }},
          expenses: {{ thisYear: [], lastYear: [], bestYear: [] }},
          fixed: {{ thisYear: [], lastYear: [], bestYear: [] }},
          expected: {{ thisYear: [], lastYear: [], bestYear: [] }},
          profit: {{ thisYear: [], lastYear: [], bestYear: [] }},
        }};
        var cum = {{
          thisYear: {{ income: 0, expenses: 0, fixed: 0, expected: 0, profit: 0 }},
          lastYear: {{ income: 0, expenses: 0, fixed: 0, expected: 0, profit: 0 }},
          bestYear: {{ income: 0, expenses: 0, fixed: 0, expected: 0, profit: 0 }},
        }};
        for (var i = 1; i <= dim; i++) {{
          var skip = (i + daySeed) % 11 === 0;
          var cyc = 1 + ((i + daySeed) % 7) * 0.045;
          var baseSales = 5900 + ((i * 73 + daySeed) % 2100);
          var salesTY = skip ? 0 : Math.round(baseSales * cyc);
          var salesLY = skip ? 0 : Math.round(salesTY * (0.93 + ((i + 2) % 4) * 0.012));
          var salesBY = skip ? 0 : Math.round(Math.max(salesTY, salesLY) * (1.12 + ((i + 1) % 3) * 0.008));
          var expTY = skip ? 0 : Math.round(salesTY * (0.29 + ((i + 1) % 4) * 0.01));
          var expLY = skip ? 0 : Math.round(salesLY * (0.285 + ((i + 2) % 4) * 0.01));
          var expBY = skip ? 0 : Math.round(salesBY * (0.278 + ((i + 3) % 4) * 0.01));
          var fixedTY = skip ? 0 : Math.round(expTY * (0.46 + (i % 2) * 0.02));
          var fixedLY = skip ? 0 : Math.round(expLY * (0.45 + ((i + 1) % 2) * 0.02));
          var fixedBY = skip ? 0 : Math.round(expBY * (0.44 + ((i + 2) % 2) * 0.02));
          var expectedTY = skip ? 0 : Math.max(0, expTY - fixedTY);
          var expectedLY = skip ? 0 : Math.max(0, expLY - fixedLY);
          var expectedBY = skip ? 0 : Math.max(0, expBY - fixedBY);
          var profitTY = skip ? 0 : salesTY - expTY;
          var profitLY = skip ? 0 : salesLY - expLY;
          var profitBY = skip ? 0 : salesBY - expBY;
          daily.income.thisYear.push(salesTY);
          daily.income.lastYear.push(salesLY);
          daily.income.bestYear.push(salesBY);
          daily.expenses.thisYear.push(expTY);
          daily.expenses.lastYear.push(expLY);
          daily.expenses.bestYear.push(expBY);
          daily.fixed.thisYear.push(fixedTY);
          daily.fixed.lastYear.push(fixedLY);
          daily.fixed.bestYear.push(fixedBY);
          daily.expected.thisYear.push(expectedTY);
          daily.expected.lastYear.push(expectedLY);
          daily.expected.bestYear.push(expectedBY);
          daily.profit.thisYear.push(profitTY);
          daily.profit.lastYear.push(profitLY);
          daily.profit.bestYear.push(profitBY);
          cum.thisYear.income += salesTY;
          cum.thisYear.expenses += expTY;
          cum.thisYear.fixed += fixedTY;
          cum.thisYear.expected += expectedTY;
          cum.thisYear.profit += profitTY;
          cum.lastYear.income += salesLY;
          cum.lastYear.expenses += expLY;
          cum.lastYear.fixed += fixedLY;
          cum.lastYear.expected += expectedLY;
          cum.lastYear.profit += profitLY;
          cum.bestYear.income += salesBY;
          cum.bestYear.expenses += expBY;
          cum.bestYear.fixed += fixedBY;
          cum.bestYear.expected += expectedBY;
          cum.bestYear.profit += profitBY;
          ['income', 'expenses', 'fixed', 'expected', 'profit'].forEach(function (k) {{
            cumulative[k].thisYear.push(cum.thisYear[k]);
            cumulative[k].lastYear.push(cum.lastYear[k]);
            cumulative[k].bestYear.push(cum.bestYear[k]);
          }});
        }}
        return {{ daily: daily, cumulative: cumulative, dim: dim, periodCount: periodCount, axisMode: 'day' }};
      }}

      function buildArea1Series(iso) {{
        var data = buildArea1ChartData(iso);
        if (!data) return null;
        return Object.assign({{ dim: data.dim }}, data.cumulative);
      }}

      function area1ChartMetrics() {{
        return ['thisYear', 'lastYear', 'bestYear'];
      }}

      var AREA1_DAILY_CLUSTER_W = 15;
      var AREA1_DAILY_CLUSTER_HALF = AREA1_DAILY_CLUSTER_W / 2;
      var AREA1_BAR_CENTER_INSET = 15;

      function area1ChartPad() {{
        return {{ w: 860, h: 420, padL: 28, padR: 12, padT: 8, padB: 34 }};
      }}

      function area1PlotSpan(plotW) {{
        return plotW - 2 * AREA1_BAR_CENTER_INSET;
      }}

      function area1DayAnchors(padL, plotW) {{
        return {{
          xFirst: padL + AREA1_BAR_CENTER_INSET,
          xLast: padL + plotW - AREA1_BAR_CENTER_INSET,
        }};
      }}

      /* Y軸+15px=1日棒中心、X軸右端-15px=月末棒中心。その間を daysInMonth-1 等分 */
      function comparePeriodCenterX(day, daysInMonth, padL, plotW) {{
        var anchors = area1DayAnchors(padL, plotW);
        if (daysInMonth <= 1) return anchors.xFirst;
        return anchors.xFirst + ((day - 1) / (daysInMonth - 1)) * (anchors.xLast - anchors.xFirst);
      }}

      function area1BarClusterLeft(day, daysInMonth, padL, plotW) {{
        return comparePeriodCenterX(day, daysInMonth, padL, plotW) - AREA1_DAILY_CLUSTER_HALF;
      }}

      function compareXTickSvgHtml(periodCount, ticks, padL, plotW, padT, plotH) {{
        var y = padT + plotH + 16;
        return ticks
          .map(function (t) {{
            var x = comparePeriodCenterX(t, periodCount, padL, plotW);
            return (
              '<text x="' +
              x.toFixed(1) +
              '" y="' +
              y.toFixed(1) +
              '" text-anchor="middle" class="pl-compare-line__axis-label">' +
              t +
              '</text>'
            );
          }})
          .join('');
      }}

      function area1XTickSvgHtml(daysInMonth, padL, plotW, padT, plotH) {{
        return compareXTickSvgHtml(daysInMonth, area1XTickDays(daysInMonth), padL, plotW, padT, plotH);
      }}

      function area1ChartPctX(x, w) {{
        return ((x / w) * 100).toFixed(4) + '%';
      }}

      function area1ChartPctY(y, h) {{
        return ((y / h) * 100).toFixed(4) + '%';
      }}

      function area1XTickDays(daysInMonth) {{
        var ticks = [1, 5, 10, 15, 20, 25, 30].filter(function (t) {{
          return t <= daysInMonth;
        }});
        if (ticks.indexOf(daysInMonth) < 0) ticks.push(daysInMonth);
        ticks.sort(function (a, b) {{ return a - b; }});
        return ticks;
      }}

      function renderArea1DailyBars(dailyData, metric, showLast, showBest, canShowBest, yMax, padL, padT, plotW, plotH, daysInMonth, dim) {{
        var clusterW = AREA1_DAILY_CLUSTER_W;
        var showBestEff = showBest && canShowBest;
        var n = 1 + (showLast ? 1 : 0) + (showBestEff ? 1 : 0);
        var barW = clusterW / n;
        var baseY = padT + plotH;
        var html = '';
        var series = [
          {{ key: 'thisYear', show: true, color: '#66e7ff' }},
          {{ key: 'lastYear', show: showLast, color: '#e8e54b' }},
          {{ key: 'bestYear', show: showBestEff, color: '#16d33a' }},
        ];
        for (var day = 1; day <= dim; day++) {{
          var idx = day - 1;
          var cx = area1BarClusterLeft(day, daysInMonth, padL, plotW);
          var clusterLeft = cx;
          var offset = 0;
          series.forEach(function (s) {{
            if (!s.show) return;
            var v = (dailyData[metric][s.key][idx] || 0);
            var bh = v > 0 ? (v / yMax) * plotH : 0;
            var x = clusterLeft + offset * barW;
            if (bh > 0) {{
              html +=
                '<rect x="' +
                x.toFixed(2) +
                '" y="' +
                (baseY - bh).toFixed(2) +
                '" width="' +
                barW.toFixed(2) +
                '" height="' +
                bh.toFixed(2) +
                '" fill="' +
                s.color +
                '"/>';
            }}
            offset += 1;
          }});
        }}
        return html;
      }}

      function area1ChartHoverLayer(w, h, padL, padT, plotW, plotH, forLine) {{
        var guideDiv = forLine ? '' : '<div class="pl-compare-line__guide-v" hidden></div>';
        return (
          '<div class="pl-compare-line__hover-layer" data-pl-chart-hover style="left:' +
          ((padL / w) * 100).toFixed(4) +
          '%;top:' +
          ((padT / h) * 100).toFixed(4) +
          '%;width:' +
          ((plotW / w) * 100).toFixed(4) +
          '%;height:' +
          ((plotH / h) * 100).toFixed(4) +
          '%"></div>' +
          guideDiv +
          '<div class="pl-compare-chart-tooltip" data-pl-chart-tooltip hidden role="tooltip">' +
          '<p class="pl-compare-chart-tooltip__snap" data-field="snap"></p>' +
          '<p class="pl-compare-chart-tooltip__metric" data-field="metric"></p>' +
          '<div class="pl-compare-chart-tooltip__rows" data-field="rows"></div>' +
          '</div>'
        );
      }}

      function area1LegendHtml(state, canShowBest, toggleAttr) {{
        var bestLegend =
          canShowBest
            ? '<label class="pl-compare-line__legend-item"><input type="checkbox" ' +
              toggleAttr +
              '="best" ' +
              (state.showBest ? 'checked' : '') +
              '><span class="pl-compare-line__swatch pl-compare-line__swatch--best"></span>' +
              L.compare_best_year +
              '</label>'
            : '';
        return (
          '<div class="pl-compare-line__legend">' +
          '<label class="pl-compare-line__legend-item"><span class="pl-compare-line__swatch pl-compare-line__swatch--this"></span>' +
          L.compare_this_year +
          '</label>' +
          '<label class="pl-compare-line__legend-item"><input type="checkbox" ' +
          toggleAttr +
          '="last" ' +
          (state.showLast ? 'checked' : '') +
          '><span class="pl-compare-line__swatch pl-compare-line__swatch--last"></span>' +
          L.compare_last_year +
          '</label>' +
          bestLegend +
          '</div>'
        );
      }}

      function formatScale(v) {{
        var n = Math.abs(Math.round(v || 0));
        if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
        if (n >= 1000) return (n / 1000).toFixed(0) + 'k';
        return String(n);
      }}



      function buildCompareChartData(areaId, iso) {{
        if (areaId === 2) return buildArea2ChartData(iso);
        if (areaId === 3) return buildArea3ChartData(iso);
        return buildArea1ChartData(iso);
      }}

      function compareAreaText(areaId) {{
        if (areaId === 2) {{
          return {{ line: L.compare_area2_line_title, daily: L.compare_area2_daily_title }};
        }}
        if (areaId === 3) {{
          return {{ line: L.compare_area3_line_title, daily: L.compare_area3_daily_title }};
        }}
        return {{ line: L.compare_line_title, daily: L.compare_daily_title }};
      }}

      function compareXTicksForChart(chartData) {{
        if (chartData.axisMode === 'month') {{
          return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
        }}
        return area1XTickDays(chartData.periodCount);
      }}


      function renderCompareLine(areaId, iso) {{
        var mount = document.getElementById('pl-compare-area-' + areaId + '-line');
        if (!mount) return;
        var chartData = buildCompareChartData(areaId, iso);
        if (!chartData) {{
          mount.innerHTML = '<p class="pl-compare-hsnap__empty">' + L.compare_no_data + '</p>';
          return;
        }}
        var state = compareLineState[areaId];
        var metric = state.metric;
        var canShowBest = area1CanShowBestYear(iso);
        var showBest = state.showBest && canShowBest;
        var data = chartData.cumulative[metric] || chartData.cumulative.income;
        var periodCount = chartData.periodCount;
        var dim = chartData.dim;
        var axisMode = chartData.axisMode || 'day';
        var labels = compareAreaText(areaId);
        var yMax = 0;
        area1ChartMetrics().forEach(function (k) {{
          if (k === 'lastYear' && !state.showLast) return;
          if (k === 'bestYear' && !showBest) return;
          var arr = data[k];
          if (!arr || !arr.length) return;
          var end = arr[arr.length - 1];
          if (end > yMax) yMax = end;
        }});
        if (!yMax) yMax = 1;
        yMax = Math.ceil(yMax / 10000) * 10000;
        var pad = area1ChartPad();
        var w = pad.w;
        var h = pad.h;
        var padL = pad.padL;
        var padR = pad.padR;
        var padT = pad.padT;
        var padB = pad.padB;
        var plotW = w - padL - padR;
        var plotH = h - padT - padB;
        var toPts = function (arr) {{
          return arr
            .map(function (v, idx) {{
              var x = comparePeriodCenterX(idx + 1, periodCount, padL, plotW);
              var y = padT + (1 - Math.min(1, v / yMax)) * plotH;
              return x.toFixed(1) + ',' + y.toFixed(1);
            }})
            .join(' ');
        }};
        var thisPts = toPts(data.thisYear);
        var lastPts = toPts(data.lastYear);
        var bestPts = toPts(data.bestYear);
        var xTickSvg = compareXTickSvgHtml(
          periodCount,
          compareXTicksForChart(chartData),
          padL,
          plotW,
          padT,
          plotH
        );
        var yTicks = [0, 0.25, 0.5, 0.75, 1]
          .map(function (r) {{
            var y = padT + (1 - r) * plotH;
            return '<span style="top:' + area1ChartPctY(y, h) + '">' + formatScale(yMax * r) + '</span>';
          }})
          .join('');
        var active = function (k) {{
          return metric === k ? ' is-active' : '';
        }};
        mount.innerHTML =
          '<section class="pl-compare-line">' +
          '<h4 class="pl-compare-line__title">' +
          labels.line +
          '</h4>' +
          '<div class="pl-compare-line__date pl-compare-hsnap__date">' +
          fmtDate(iso) +
          '</div>' +
          '<div class="pl-compare-line__metric-tabs">' +
          '<button type="button" class="pl-compare-line__metric' +
          active('income') +
          '" data-pl-line-metric="income">' +
          L.compare_income +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('expenses') +
          '" data-pl-line-metric="expenses">' +
          L.compare_expenses +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('fixed') +
          '" data-pl-line-metric="fixed">' +
          L.compare_fixed +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('expected') +
          '" data-pl-line-metric="expected">' +
          L.compare_expected +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('profit') +
          '" data-pl-line-metric="profit">' +
          L.compare_profit +
          '</button>' +
          '</div>' +
          '<div class="pl-compare-line__chart-wrap">' +
          '<svg class="pl-compare-line__svg" viewBox="0 0 ' +
          w +
          ' ' +
          h +
          '" preserveAspectRatio="none" aria-hidden="true">' +
          '<line x1="' +
          padL +
          '" y1="' +
          padT +
          '" x2="' +
          padL +
          '" y2="' +
          (padT + plotH) +
          '" stroke="#58e1f3" stroke-width="1"/>' +
          '<line x1="' +
          padL +
          '" y1="' +
          (padT + plotH) +
          '" x2="' +
          (padL + plotW) +
          '" y2="' +
          (padT + plotH) +
          '" stroke="#58e1f3" stroke-width="1"/>' +
          '<polyline points="' +
          thisPts +
          '" fill="none" stroke="#66e7ff" stroke-width="2" vector-effect="non-scaling-stroke"/>' +
          (state.showLast
            ? '<polyline points="' +
              lastPts +
              '" fill="none" stroke="#e8e54b" stroke-width="2" vector-effect="non-scaling-stroke"/>'
            : '') +
          (showBest
            ? '<polyline points="' +
              bestPts +
              '" fill="none" stroke="#16d33a" stroke-width="2" vector-effect="non-scaling-stroke"/>'
            : '') +
          xTickSvg +
          '</svg>' +
          '<div class="pl-compare-line__y-ticks">' +
          yTicks +
          '</div>' +
          area1ChartHoverLayer(w, h, padL, padT, plotW, plotH, true) +
          '</div>' +
          area1LegendHtml(state, canShowBest, 'data-pl-line-toggle') +
          '</section>';

        mount.querySelectorAll('[data-pl-line-metric]').forEach(function (btn) {{
          btn.addEventListener('click', function () {{
            compareLineState[areaId].metric = btn.getAttribute('data-pl-line-metric') || 'income';
            renderCompareLine(areaId, iso);
          }});
        }});
        mount.querySelectorAll('[data-pl-line-toggle]').forEach(function (box) {{
          box.addEventListener('change', function () {{
            var key = box.getAttribute('data-pl-line-toggle');
            if (key === 'last') compareLineState[areaId].showLast = !!box.checked;
            if (key === 'best') compareLineState[areaId].showBest = !!box.checked;
            renderCompareLine(areaId, iso);
          }});
        }});
        var chartWrap = mount.querySelector('.pl-compare-line__chart-wrap');
        bindArea1LineChartHover(chartWrap, {{
          w: w,
          h: h,
          padL: padL,
          padT: padT,
          plotW: plotW,
          plotH: plotH,
          yMax: yMax,
          daysInMonth: periodCount,
          dim: dim,
          axisMode: axisMode,
          metric: metric,
          isoParts: isoParts(iso),
          refYears: chartData.refYears || null,
          bestYear: chartData.refYears ? chartData.refYears.bestYear : area1BestYearNumber(iso),
          showLast: state.showLast,
          showBest: showBest,
          canShowBest: canShowBest,
          values: data,
        }});
      }}

      function renderCompareDaily(areaId, iso) {{
        var mount = document.getElementById('pl-compare-area-' + areaId + '-daily');
        if (!mount) return;
        var chartData = buildCompareChartData(areaId, iso);
        if (!chartData) {{
          mount.innerHTML = '<p class="pl-compare-hsnap__empty">' + L.compare_no_data + '</p>';
          return;
        }}
        var state = compareDailyState[areaId];
        var metric = state.metric;
        var canShowBest = area1CanShowBestYear(iso);
        var showBest = state.showBest && canShowBest;
        var dailyData = chartData.daily;
        var data = dailyData[metric] || dailyData.income;
        var periodCount = chartData.periodCount;
        var dim = chartData.dim;
        var axisMode = chartData.axisMode || 'day';
        var labels = compareAreaText(areaId);
        var yMax = 0;
        area1ChartMetrics().forEach(function (k) {{
          if (k === 'lastYear' && !state.showLast) return;
          if (k === 'bestYear' && !showBest) return;
          var arr = data[k];
          if (!arr || !arr.length) return;
          arr.forEach(function (v) {{
            if (v > yMax) yMax = v;
          }});
        }});
        if (!yMax) yMax = 1;
        yMax = Math.ceil(yMax / 1000) * 1000;
        var pad = area1ChartPad();
        var w = pad.w;
        var h = pad.h;
        var padL = pad.padL;
        var padR = pad.padR;
        var padT = pad.padT;
        var padB = pad.padB;
        var plotW = w - padL - padR;
        var plotH = h - padT - padB;
        var bars = renderArea1DailyBars(
          dailyData,
          metric,
          state.showLast,
          state.showBest,
          canShowBest,
          yMax,
          padL,
          padT,
          plotW,
          plotH,
          periodCount,
          dim
        );
        var xTickSvg = compareXTickSvgHtml(
          periodCount,
          compareXTicksForChart(chartData),
          padL,
          plotW,
          padT,
          plotH
        );
        var yTicks = [0, 0.25, 0.5, 0.75, 1]
          .map(function (r) {{
            var y = padT + (1 - r) * plotH;
            return '<span style="top:' + area1ChartPctY(y, h) + '">' + formatScale(yMax * r) + '</span>';
          }})
          .join('');
        var active = function (k) {{
          return metric === k ? ' is-active' : '';
        }};
        mount.innerHTML =
          '<section class="pl-compare-line pl-compare-daily">' +
          '<h4 class="pl-compare-line__title">' +
          labels.daily +
          '</h4>' +
          '<div class="pl-compare-line__date pl-compare-hsnap__date">' +
          fmtDate(iso) +
          '</div>' +
          '<div class="pl-compare-line__metric-tabs">' +
          '<button type="button" class="pl-compare-line__metric' +
          active('income') +
          '" data-pl-daily-metric="income">' +
          L.compare_income +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('expenses') +
          '" data-pl-daily-metric="expenses">' +
          L.compare_expenses +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('fixed') +
          '" data-pl-daily-metric="fixed">' +
          L.compare_fixed +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('expected') +
          '" data-pl-daily-metric="expected">' +
          L.compare_expected +
          '</button>' +
          '<button type="button" class="pl-compare-line__metric' +
          active('profit') +
          '" data-pl-daily-metric="profit">' +
          L.compare_profit +
          '</button>' +
          '</div>' +
          '<div class="pl-compare-line__chart-wrap">' +
          '<svg class="pl-compare-line__svg" viewBox="0 0 ' +
          w +
          ' ' +
          h +
          '" preserveAspectRatio="none" aria-hidden="true">' +
          '<line x1="' +
          padL +
          '" y1="' +
          padT +
          '" x2="' +
          padL +
          '" y2="' +
          (padT + plotH) +
          '" stroke="#58e1f3" stroke-width="1"/>' +
          '<line x1="' +
          padL +
          '" y1="' +
          (padT + plotH) +
          '" x2="' +
          (padL + plotW) +
          '" y2="' +
          (padT + plotH) +
          '" stroke="#58e1f3" stroke-width="1"/>' +
          bars +
          xTickSvg +
          '</svg>' +
          '<div class="pl-compare-line__y-ticks">' +
          yTicks +
          '</div>' +
          area1ChartHoverLayer(w, h, padL, padT, plotW, plotH, false) +
          '</div>' +
          area1LegendHtml(state, canShowBest, 'data-pl-daily-toggle') +
          '</section>';

        mount.querySelectorAll('[data-pl-daily-metric]').forEach(function (btn) {{
          btn.addEventListener('click', function () {{
            compareDailyState[areaId].metric = btn.getAttribute('data-pl-daily-metric') || 'income';
            renderCompareDaily(areaId, iso);
          }});
        }});
        mount.querySelectorAll('[data-pl-daily-toggle]').forEach(function (box) {{
          box.addEventListener('change', function () {{
            var key = box.getAttribute('data-pl-daily-toggle');
            if (key === 'last') compareDailyState[areaId].showLast = !!box.checked;
            if (key === 'best') compareDailyState[areaId].showBest = !!box.checked;
            renderCompareDaily(areaId, iso);
          }});
        }});
        var chartWrap = mount.querySelector('.pl-compare-line__chart-wrap');
        bindArea1DailyChartHover(chartWrap, {{
          w: w,
          h: h,
          padL: padL,
          padT: padT,
          plotW: plotW,
          plotH: plotH,
          yMax: yMax,
          daysInMonth: periodCount,
          dim: dim,
          axisMode: axisMode,
          metric: metric,
          isoParts: isoParts(iso),
          refYears: chartData.refYears || null,
          bestYear: chartData.refYears ? chartData.refYears.bestYear : area1BestYearNumber(iso),
          showLast: state.showLast,
          showBest: showBest,
          canShowBest: canShowBest,
          values: data,
        }});
      }}

      function renderCompareFl(areaId, iso) {{
        var mount = document.getElementById('pl-compare-area-' + areaId + '-fl');
        if (!mount) return;
        iso = iso || selectedIso || resolveIso();
        var parts = isoParts(iso);
        if (!parts) return;
        var pad2 = function (n) {{
          return n < 10 ? '0' + n : String(n);
        }};
        var current;
        var previous;
        var primaryLabel;
        var secondaryLabel;
        if (areaId === 1) {{
          var refIso = sameWeekdayLastYearIso(iso);
          current = fetchCurrentFlSnapshot(iso);
          previous = fetchPreviousFlSnapshot(refIso);
          primaryLabel = fmtDate(iso);
          secondaryLabel = L.compare_same_weekday_of + fmtDate(refIso);
        }} else if (areaId === 2) {{
          var lyIso = parts.year - 1 + '-' + pad2(parts.month) + '-' + pad2(parts.day);
          var tyIso = parts.year - 2 + '-' + pad2(parts.month) + '-' + pad2(parts.day);
          current = fetchCurrentFlSnapshot(lyIso);
          previous = fetchPreviousFlSnapshot(tyIso);
          primaryLabel = L.compare_area2_hsnap_primary + fmtDate(lyIso);
          secondaryLabel = L.compare_area2_hsnap_secondary + fmtDate(tyIso);
        }} else {{
          var lyYtdIso = parts.year - 1 + '-' + pad2(parts.month) + '-' + pad2(parts.day);
          current = fetchCurrentFlSnapshot(iso);
          previous = fetchPreviousFlSnapshot(lyYtdIso);
          primaryLabel = L.compare_area3_hsnap_primary + fmtDate(iso);
          secondaryLabel = L.compare_area3_hsnap_secondary + fmtDate(lyYtdIso);
        }}
        var maxIncome = current ? current.income : 0;
        if (previous && previous.income > maxIncome) maxIncome = previous.income;
        if (!maxIncome) maxIncome = 1;
        mount.innerHTML =
          renderHsnapBlock(primaryLabel, current, maxIncome, 0, false) +
          renderHsnapBlock(secondaryLabel, previous, maxIncome, 1, true);
      }}

      function renderAllCompareAreas(iso) {{
        iso = iso || selectedIso || resolveIso();
        [1, 2, 3].forEach(function (areaId) {{
          renderCompareFl(areaId, iso);
          renderCompareLine(areaId, iso);
          renderCompareDaily(areaId, iso);
        }});
      }}

      function fillDate(iso) {{
        iso = iso || resolveIso();
        selectedIso = iso;
        if (dateBtn) dateBtn.textContent = fmtDate(iso);
        if (todayBtn) todayBtn.hidden = iso === getTodayIso();
        if (dateInput) dateInput.value = iso;
        renderAllCompareAreas(iso);
      }}

      function openOverlay() {{
        if (!root) return;
        lastFocused = document.activeElement;
        try {{
          fillDate(selectedIso || resolveIso());
        }} catch (err) {{
          console.error('Compare overlay fillDate failed', err);
        }}
        root.hidden = false;
        document.body.classList.add('pl-graph-overlay-open');
        if (btnClose) btnClose.focus();
      }}

      function closeOverlay() {{
        if (!root) return;
        root.hidden = true;
        document.body.classList.remove('pl-graph-overlay-open');
        if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
      }}

      if (btnOpen) btnOpen.addEventListener('click', openOverlay);
      if (btnClose) {{
        btnClose.addEventListener('click', function (e) {{
          e.preventDefault();
          e.stopPropagation();
          closeOverlay();
        }});
      }}
      if (prevBtn) {{
        prevBtn.addEventListener('click', function () {{
          fillDate(shiftIso(selectedIso || resolveIso(), -1));
        }});
      }}
      if (nextBtn) {{
        nextBtn.addEventListener('click', function () {{
          fillDate(shiftIso(selectedIso || resolveIso(), 1));
        }});
      }}
      if (todayBtn) {{
        todayBtn.addEventListener('click', function () {{
          fillDate(getTodayIso());
        }});
      }}
      if (dateBtn && dateInput) {{
        dateBtn.addEventListener('click', function () {{
          if (dateInput.showPicker) dateInput.showPicker();
          else dateInput.click();
        }});
        dateInput.addEventListener('change', function () {{
          if (!dateInput.value) return;
          fillDate(dateInput.value);
        }});
      }}
      function scrollToCompareArea(target) {{
        if (!scrollEl || !target) return;
        var top =
          target.getBoundingClientRect().top -
          scrollEl.getBoundingClientRect().top +
          scrollEl.scrollTop;
        scrollEl.scrollTo({{
          top: Math.max(0, top),
          behavior: 'smooth',
        }});
      }}

      areaButtons.forEach(function (btn) {{
        btn.addEventListener('click', function () {{
          if (!contentEl || !scrollEl) return;
          var targetId = btn.getAttribute('data-pl-compare-jump');
          if (!targetId) return;
          var target = document.getElementById(targetId);
          if (!target) return;
          scrollToCompareArea(target);
        }});
      }});
      if (root) {{
        root.addEventListener('click', function (e) {{
          var btn =
            e.target && e.target.closest
              ? e.target.closest('[data-pl-graph-overlay-action="close"]')
              : null;
          if (!btn) return;
          e.preventDefault();
          closeOverlay();
        }});
      }}
      document.addEventListener('keydown', function (e) {{
        if (e.key === 'Escape' && root && !root.hidden) {{
          e.preventDefault();
          closeOverlay();
        }}
      }});
    }})();
"""


def pl_graph_overlay_html(L: dict) -> str:
    return f"""
  <div class="pl-graph-overlay" id="pl-graph-overlay" hidden>
    <div class="pl-graph-overlay__backdrop" data-pl-graph-overlay-action="close"></div>
    <section class="pl-graph-overlay__panel" role="dialog" aria-modal="true"
      aria-labelledby="pl-graph-overlay-title">
      <button type="button" class="pl-graph-overlay__close" id="pl-graph-overlay-close"
        data-pl-graph-overlay-action="close" aria-label="{L["graph_overlay_close_aria"]}">×</button>
      <header class="pl-compare-header">
        <h2 class="pl-graph-overlay__title" id="pl-graph-overlay-title">{L["toolbar_graph"]}</h2>
        <div class="pl-compare-toolbar">
          <div class="pl-compare-date-row">
            <button type="button" class="pl-compare-date-nav" id="pl-compare-prev-day"
              aria-label="{L["compare_prev_day_aria"]}">◀︎</button>
            <button type="button" class="pl-compare-date-btn" id="pl-compare-date-btn"
              aria-label="{L["compare_date_pick_aria"]}">—</button>
            <button type="button" class="pl-compare-date-nav" id="pl-compare-next-day"
              aria-label="{L["compare_next_day_aria"]}">▶︎</button>
            <button type="button" class="pl-compare-today" id="pl-compare-today">{L["compare_today"]}</button>
            <input type="date" class="pl-compare-date-input" id="pl-compare-date-input"
              aria-hidden="true" tabindex="-1">
          </div>
          <div class="pl-compare-area-nav" role="tablist" aria-label="Compare areas">
            <button type="button" class="pl-compare-area-tab" data-pl-compare-jump="pl-compare-area-1">Area 1</button>
            <button type="button" class="pl-compare-area-tab" data-pl-compare-jump="pl-compare-area-2">Area 2</button>
            <button type="button" class="pl-compare-area-tab" data-pl-compare-jump="pl-compare-area-3">Area 3</button>
          </div>
        </div>
        <div class="pl-compare-header__rule" aria-hidden="true"></div>
      </header>
      <div class="pl-graph-overlay__scroll" id="pl-compare-scroll">
        <div class="pl-compare-content" id="pl-compare-content">
          <section class="pl-compare-area" id="pl-compare-area-1">
            <h3 class="pl-compare-area-title">{L["compare_area1_title"]}</h3>
            <div class="pl-compare-area-fl" id="pl-compare-area-1-fl"></div>
            <div class="pl-compare-area-line" id="pl-compare-area-1-line"></div>
            <div class="pl-compare-area-daily" id="pl-compare-area-1-daily"></div>
          </section>
          <section class="pl-compare-area" id="pl-compare-area-2">
            <h3 class="pl-compare-area-title">{L["compare_area2_title"]}</h3>
            <div class="pl-compare-area-fl" id="pl-compare-area-2-fl"></div>
            <div class="pl-compare-area-line" id="pl-compare-area-2-line"></div>
            <div class="pl-compare-area-daily" id="pl-compare-area-2-daily"></div>
          </section>
          <section class="pl-compare-area" id="pl-compare-area-3">
            <h3 class="pl-compare-area-title">{L["compare_area3_title"]}</h3>
            <div class="pl-compare-area-fl" id="pl-compare-area-3-fl"></div>
            <div class="pl-compare-area-line" id="pl-compare-area-3-line"></div>
            <div class="pl-compare-area-daily" id="pl-compare-area-3-daily"></div>
          </section>
        </div>
      </div>
    </section>
  </div>"""


def pl_input_source_modal_html(L: dict) -> str:
    """Add-flow only (legacy). Label edit uses pl_expense_label_edit_modal_html."""
    return f"""
  <div class="pl-input-source-modal" id="pl-input-source-modal" hidden role="dialog"
    aria-modal="true" aria-labelledby="pl-input-source-modal-title">
    <div class="pl-input-source-modal__backdrop" data-pl-input-source-action="cancel"></div>
    <div class="pl-input-source-modal__panel">
      <h2 class="pl-input-source-modal__title" id="pl-input-source-modal-title">{L["input_source_title"]}</h2>
      <fieldset class="pl-input-source-modal__choices">
        <legend class="pl-input-source-modal__legend">{L["input_source_title"]}</legend>
        <label class="pl-input-source-modal__choice">
          <input type="radio" name="pl-input-source" value="daily">
          <span>{L["input_source_daily"]}</span>
        </label>
        <label class="pl-input-source-modal__choice">
          <input type="radio" name="pl-input-source" value="monthly">
          <span>{L["input_source_monthly"]}</span>
        </label>
      </fieldset>
      <div class="pl-input-source-modal__actions">
        <button type="button" class="pl-input-source-modal__btn pl-input-source-modal__btn--ghost"
          data-pl-input-source-action="cancel">{L["input_source_cancel"]}</button>
        <button type="button" class="pl-input-source-modal__btn pl-input-source-modal__btn--primary"
          data-pl-input-source-action="confirm">{L["input_source_confirm"]}</button>
      </div>
    </div>
  </div>"""


def pl_expense_label_edit_modal_html(L: dict) -> str:
    """Unified: label rename + input source (variable). No Don't-ask-again."""
    return f"""
  <div class="pl-input-source-modal pl-expense-label-edit-modal" id="pl-expense-label-edit-modal" hidden role="dialog"
    aria-modal="true" aria-labelledby="pl-expense-label-edit-modal-title">
    <div class="pl-input-source-modal__backdrop" data-pl-label-edit-action="cancel"></div>
    <div class="pl-input-source-modal__panel">
      <h2 class="pl-input-source-modal__title" id="pl-expense-label-edit-modal-title">{L["label_edit_modal_title"]}</h2>
      <label class="pl-expense-label-edit-modal__field">
        <span class="pl-expense-label-edit-modal__field-label">{L["label_edit_modal_label"]}</span>
        <input type="text" id="pl-expense-label-edit-input" class="pl-expense-label-edit-modal__input"
          autocomplete="off" maxlength="80">
      </label>
      <fieldset class="pl-input-source-modal__choices" id="pl-expense-label-edit-source" hidden>
        <legend class="pl-input-source-modal__legend">{L["label_edit_modal_source"]}</legend>
        <label class="pl-input-source-modal__choice">
          <input type="radio" name="pl-expense-label-edit-source" value="daily">
          <span>{L["input_source_daily"]}</span>
        </label>
        <label class="pl-input-source-modal__choice">
          <input type="radio" name="pl-expense-label-edit-source" value="monthly">
          <span>{L["input_source_monthly"]}</span>
        </label>
      </fieldset>
      <div class="pl-input-source-modal__actions">
        <button type="button" class="pl-input-source-modal__btn pl-input-source-modal__btn--ghost"
          data-pl-label-edit-action="cancel">{L["label_edit_modal_cancel"]}</button>
        <button type="button" class="pl-input-source-modal__btn pl-input-source-modal__btn--primary"
          data-pl-label-edit-action="confirm">{L["label_edit_modal_confirm"]}</button>
      </div>
    </div>
  </div>"""


def pl_expense_adj_modal_html(L: dict) -> str:
    """Daily Aggregate + Adjustment — edit monthly adjustment without overwriting daily."""
    return f"""
  <div class="pl-input-source-modal pl-expense-adj-modal" id="pl-expense-adj-modal" hidden role="dialog"
    aria-modal="true" aria-labelledby="pl-expense-adj-modal-title">
    <div class="pl-input-source-modal__backdrop" data-pl-adj-action="cancel"></div>
    <div class="pl-input-source-modal__panel">
      <h2 class="pl-input-source-modal__title" id="pl-expense-adj-modal-title">{L["adj_modal_title"]}</h2>
      <p class="pl-expense-adj-modal__hint">{L["adj_modal_hint"]}</p>
      <div class="pl-expense-adj-modal__rows">
        <div class="pl-expense-adj-modal__row">
          <span class="pl-expense-adj-modal__label">{L["adj_modal_daily"]}</span>
          <span class="pl-expense-adj-modal__value" id="pl-expense-adj-daily">—</span>
        </div>
        <label class="pl-expense-adj-modal__row pl-expense-adj-modal__row--input">
          <span class="pl-expense-adj-modal__label">{L["adj_modal_adj"]}</span>
          <input type="text" id="pl-expense-adj-input" class="pl-expense-adj-modal__input"
            inputmode="decimal" autocomplete="off">
        </label>
        <div class="pl-expense-adj-modal__row pl-expense-adj-modal__row--result">
          <span class="pl-expense-adj-modal__label">{L["adj_modal_result"]}</span>
          <span class="pl-expense-adj-modal__value" id="pl-expense-adj-result">—</span>
        </div>
      </div>
      <div class="pl-input-source-modal__actions">
        <button type="button" class="pl-input-source-modal__btn pl-input-source-modal__btn--ghost"
          data-pl-adj-action="cancel">{L["adj_modal_cancel"]}</button>
        <button type="button" class="pl-input-source-modal__btn pl-input-source-modal__btn--primary"
          data-pl-adj-action="confirm">{L["adj_modal_confirm"]}</button>
      </div>
    </div>
  </div>"""


def pl_expense_attribute_modal_html(L: dict, lang: str) -> str:
    def choice_rows(attrs: list[tuple[str, str, str]]) -> str:
        parts: list[str] = []
        for attr_id, ja, en in attrs:
            label = ja if lang == "ja" else en
            parts.append(
                f'<label class="pl-input-source-modal__choice">'
                f'<input type="radio" name="pl-expense-attribute" value="{attr_id}">'
                f"<span>{label}</span></label>"
            )
        return "\n".join(parts)

    fixed_html = choice_rows(FIXED_EXPENSE_ATTRIBUTES)
    variable_html = choice_rows(VARIABLE_EXPENSE_ATTRIBUTES)
    return f"""
  <div class="pl-input-source-modal pl-expense-attribute-modal" id="pl-expense-attribute-modal" hidden role="dialog"
    aria-modal="true" aria-labelledby="pl-expense-attribute-modal-title">
    <div class="pl-input-source-modal__backdrop" data-pl-expense-attribute-action="cancel"></div>
    <div class="pl-input-source-modal__panel">
      <h2 class="pl-input-source-modal__title" id="pl-expense-attribute-modal-title">{L["expense_attribute_title"]}</h2>
      <fieldset class="pl-input-source-modal__choices pl-expense-attribute-choices pl-expense-attribute-choices--fixed" data-pl-expense-attribute-bucket="fixed">
        <legend class="pl-input-source-modal__legend">{L["expense_attribute_title"]}</legend>
        {fixed_html}
      </fieldset>
      <fieldset class="pl-input-source-modal__choices pl-expense-attribute-choices pl-expense-attribute-choices--variable" data-pl-expense-attribute-bucket="variable" hidden>
        <legend class="pl-input-source-modal__legend">{L["expense_attribute_variable_title"]}</legend>
        {variable_html}
      </fieldset>
      <div class="pl-input-source-modal__actions">
        <button type="button" class="pl-input-source-modal__btn pl-input-source-modal__btn--ghost"
          data-pl-expense-attribute-action="cancel">{L["expense_attribute_cancel"]}</button>
        <button type="button" class="pl-input-source-modal__btn pl-input-source-modal__btn--primary"
          data-pl-expense-attribute-action="confirm">{L["expense_attribute_confirm"]}</button>
      </div>
    </div>
  </div>"""


def pl_hide_line_modal_html(L: dict) -> str:
    return f"""
  <div class="pl-hide-line-modal" id="pl-hide-line-modal" hidden role="dialog"
    aria-modal="true" aria-labelledby="pl-hide-line-modal-title">
    <div class="pl-hide-line-modal__backdrop" data-pl-hide-line-action="cancel"></div>
    <div class="pl-hide-line-modal__panel">
      <h2 class="pl-hide-line-modal__title" id="pl-hide-line-modal-title">{L["hide_line_confirm_title"]}</h2>
      <p class="pl-hide-line-modal__body" id="pl-hide-line-modal-body"></p>
      <div class="pl-hide-line-modal__actions">
        <button type="button" class="pl-hide-line-modal__btn pl-hide-line-modal__btn--ghost"
          data-pl-hide-line-action="cancel">{L["hide_line_confirm_cancel"]}</button>
        <button type="button" class="pl-hide-line-modal__btn pl-hide-line-modal__btn--primary"
          data-pl-hide-line-action="confirm">{L["hide_line_confirm_ok"]}</button>
      </div>
    </div>
  </div>"""


def pl_line_manage_modal_html(L: dict) -> str:
    return f"""
  <div class="pl-line-manage-modal" id="pl-line-manage-modal" hidden role="dialog"
    aria-modal="true" aria-labelledby="pl-line-manage-modal-title">
    <div class="pl-line-manage-modal__backdrop" data-pl-line-manage-action="close"></div>
    <div class="pl-line-manage-modal__panel">
      <h2 class="pl-line-manage-modal__title" id="pl-line-manage-modal-title">{L["line_manage_title"]}</h2>
      <div class="pl-line-manage__list" id="pl-line-manage-list"></div>
      <div class="pl-line-manage-modal__actions">
        <button type="button" class="pl-line-manage-modal__btn"
          data-pl-line-manage-action="close">{L["line_manage_close"]}</button>
      </div>
    </div>
  </div>"""


def pl_graph_dummy_months() -> list[dict]:
    """Dummy monthly graph inputs (phase A). Index 2 = deficit month (Figma March)."""
    surplus = {
        "sales": 123456,
        "expenseRatio": 0.70,
        "fixedRatio": 0.25,
        "expectedRatio": 0.35,
    }
    deficit = {
        "sales": 23456,
        "expenseRatio": 1.33,
        "fixedRatio": 0.46,
        "expectedRatio": 0.87,
    }
    out: list[dict] = []
    for i in range(12):
        out.append(dict(deficit if i == 2 else surplus))
    return out


def pl_graph_client_js(
    *,
    months_json: str,
    dummy_json: str,
    graph_band: str,
    monthly_sales_l: str,
    expenses_l: str,
    fixed_l: str,
    expected_l: str,
    is_ja: bool,
) -> str:
    money_sym = "¥" if is_ja else "$"
    return f"""
    (function () {{
      var isJa = {json.dumps(is_ja)};
      var MONTHS = {months_json};
      var DUMMY_MONTHS = {dummy_json};
      var BAR_H = 533;
      var LABELS = {{
        band: {json.dumps(graph_band, ensure_ascii=False)},
        monthlySales: {json.dumps(monthly_sales_l, ensure_ascii=False)},
        expenses: {json.dumps(expenses_l, ensure_ascii=False)},
        fixed: {json.dumps(fixed_l, ensure_ascii=False)},
        expected: {json.dumps(expected_l, ensure_ascii=False)},
      }};
      var body = document.getElementById('pl-graph-data-body');
      if (!body) return;

      function formatMoney(n) {{
        var v = Math.round(Number(n) || 0);
        if (isJa) return '¥' + v.toLocaleString('en-US');
        return '$' + v.toLocaleString('en-US');
      }}

      function pct(n) {{
        return Math.round(Number(n) || 0) + '%';
      }}

      function calcMetrics(raw) {{
        var sales = Number(raw.sales) || 0;
        var expenses =
          raw.expenses != null
            ? Number(raw.expenses)
            : sales * (Number(raw.expenseRatio) || 0);
        var fixed =
          raw.fixed != null ? Number(raw.fixed) : sales * (Number(raw.fixedRatio) || 0);
        var expected =
          raw.expected != null
            ? Number(raw.expected)
            : sales * (Number(raw.expectedRatio) || 0);
        if (sales <= 0) sales = 1;
        if (expenses <= 0) expenses = 1;
        var deficit = expenses > sales;
        var expensePct = (expenses / sales) * 100;
        var fixedPct = (fixed / sales) * 100;
        var expectedPct = (expected / sales) * 100;
        var redH;
        var greenH;
        var fixedH;
        var expectedH;
        if (!deficit) {{
          redH = Math.round((expenses / sales) * BAR_H);
          greenH = BAR_H - redH;
          fixedH = Math.round((fixed / expenses) * redH);
          expectedH = Math.max(0, redH - fixedH);
        }} else {{
          redH = BAR_H;
          greenH = Math.round((sales / expenses) * BAR_H);
          fixedH = Math.round((fixed / expenses) * BAR_H);
          expectedH = Math.max(0, redH - fixedH);
        }}
        return {{
          deficit: deficit,
          sales: sales,
          expenses: expenses,
          fixed: fixed,
          expected: expected,
          expensePct: expensePct,
          fixedPct: fixedPct,
          expectedPct: expectedPct,
          redH: redH,
          greenH: greenH,
          fixedH: fixedH,
          expectedH: expectedH,
        }};
      }}

      function legendBlock(cls, label, amount, percent, style) {{
        return (
          '<div class="pl-graph-legend ' +
          cls +
          '" style="' +
          (style || '') +
          '"><span class="pl-graph-legend__label">' +
          label +
          '</span><span class="pl-graph-legend__amt">' +
          formatMoney(amount) +
          '</span><span class="pl-graph-legend__pct">' +
          pct(percent) +
          '</span></div>'
        );
      }}

      function renderBars(m) {{
        if (!m.deficit) {{
          return (
            '<div class="pl-graph-unified pl-graph-unified--surplus" style="height:' +
            BAR_H +
            'px">' +
            '<div class="pl-graph-unified__income pl-graph-bar pl-graph-bar--green" style="height:' +
            m.greenH +
            'px"></div>' +
            '<div class="pl-graph-unified__split-row" style="height:' +
            m.redH +
            'px">' +
            '<div class="pl-graph-unified__half pl-graph-unified__half--expense">' +
            '<div class="pl-graph-bar pl-graph-bar--red"></div></div>' +
            '<div class="pl-graph-unified__half pl-graph-unified__stack">' +
            '<div class="pl-graph-bar pl-graph-bar--yellow" style="height:' +
            m.fixedH +
            'px"></div>' +
            '<div class="pl-graph-bar pl-graph-bar--orange" style="height:' +
            m.expectedH +
            'px"></div>' +
            '</div></div></div>'
          );
        }}
        return (
          '<div class="pl-graph-unified pl-graph-unified--deficit" style="height:' +
          BAR_H +
          'px">' +
          '<div class="pl-graph-unified__half pl-graph-unified__expense-host">' +
          '<div class="pl-graph-bar pl-graph-bar--red pl-graph-unified__expense-fill"></div>' +
          '<div class="pl-graph-unified__income-inner pl-graph-bar pl-graph-bar--green" style="height:' +
          m.greenH +
          'px"></div></div>' +
          '<div class="pl-graph-unified__half pl-graph-unified__stack">' +
          '<div class="pl-graph-bar pl-graph-bar--yellow" style="height:' +
          m.fixedH +
          'px"></div>' +
          '<div class="pl-graph-bar pl-graph-bar--orange" style="height:' +
          m.expectedH +
          'px"></div>' +
          '</div></div>'
        );
      }}

      function renderMonthCell(mi, raw) {{
        var m = calcMetrics(raw);
        var monthName = MONTHS[mi] || String(mi + 1);
        var expTop = m.deficit ? 0 : m.greenH;
        var expHeight = m.deficit ? BAR_H : m.redH;
        var fixedTop = m.deficit ? 0 : m.greenH;
        var expLegendStyle = 'top:' + expTop + 'px;height:' + expHeight + 'px';
        var fixedLegendStyle =
          'top:' + fixedTop + 'px;height:' + m.fixedH + 'px';
        var expectedLegendStyle =
          'top:' + (fixedTop + m.fixedH) + 'px;height:' + m.expectedH + 'px';
        return (
          '<td class="pl-graph-cell" colspan="2" data-month="' +
          mi +
          '" data-pl-graph-month="1">' +
          '<div class="pl-graph-month">' +
          '<div class="pl-graph-month__head">' +
          '<span class="pl-graph-month__name">' +
          monthName +
          '</span>' +
          '<span class="pl-graph-month__sales">' +
          '<span class="pl-graph-month__sales-label">' +
          LABELS.monthlySales +
          '</span> ' +
          '<span class="pl-graph-month__sales-amt">' +
          formatMoney(m.sales) +
          '</span></span></div>' +
          '<div class="pl-graph-month__stage">' +
          '<div class="pl-graph-month__aside pl-graph-month__aside--left">' +
          legendBlock(
            'pl-graph-legend--expenses',
            LABELS.expenses,
            m.expenses,
            m.expensePct,
            expLegendStyle
          ) +
          '</div>' +
          '<div class="pl-graph-month__bars-wrap">' +
          renderBars(m) +
          '</div>' +
          '<div class="pl-graph-month__aside pl-graph-month__aside--right">' +
          legendBlock(
            'pl-graph-legend--fixed',
            LABELS.fixed,
            m.fixed,
            m.fixedPct,
            fixedLegendStyle
          ) +
          legendBlock(
            'pl-graph-legend--expected',
            LABELS.expected,
            m.expected,
            m.expectedPct,
            expectedLegendStyle
          ) +
          '</div></div></div></td>'
        );
      }}

      function renderPlGraphs(monthData) {{
        var data = monthData || DUMMY_MONTHS;
        var html = '<tr class="pl-graph-data-row" data-pl-section="graph">';
        for (var mi = 0; mi < 12; mi++) {{
          html += renderMonthCell(mi, data[mi] || DUMMY_MONTHS[mi] || {{}});
        }}
        html +=
          '<td class="pl-graph-cell pl-graph-cell--year" colspan="2" data-month="year"></td>';
        html += '</tr>';
        body.innerHTML = html;
        window.dispatchEvent(new Event('pl-graph-rendered'));
      }}

      window.plGraphRender = renderPlGraphs;
      window.plGraphCalcMetrics = calcMetrics;
      renderPlGraphs(DUMMY_MONTHS);
    }})();
"""


def month_head_row_v1(lang: str) -> str:
    """Top month header cells (Jan–Dec) + year total, 260×30 each (colspan 2)."""
    L = LABELS_EN if lang == "en" else LABELS_JA
    months = MONTHS_EN if lang == "en" else MONTHS_JA
    parts: list[str] = []
    for i, m in enumerate(months, start=1):
        parts.append(
            f'<th class="pl-month-head" scope="colgroup" colspan="2" id="pl-month-head-{i}">'
            f'<span class="pl-month-head__text">{m}</span></th>'
        )
    parts.append(
        f'<th class="pl-month-head pl-month-head--year" scope="colgroup" colspan="2" '
        f'id="pl-month-head-year">'
        f'<span class="pl-month-head__text">{L["year_total_head"]}</span></th>'
    )
    return "".join(parts)


def month_subhead_row_v1(lang: str) -> str:
    """Amount / Ratio sub-header under each month (160×30 + 100×30 = 260)."""
    L = LABELS_EN if lang == "en" else LABELS_JA
    amt = L["amount"]
    ratio = L["ratio"]
    parts: list[str] = []
    for i in range(1, 13):
        parts.append(
            f'<th class="pl-sub-amt" scope="col" id="pl-sub-amt-{i}">'
            f'<span class="pl-sub-amt__text">{amt}</span></th>'
            f'<th class="pl-sub-ratio" scope="col" id="pl-sub-ratio-{i}">'
            f'<span class="pl-sub-ratio__text">{ratio}</span></th>'
        )
    parts.append(
        f'<th class="pl-sub-amt pl-sub-amt--year" scope="col" id="pl-sub-amt-year">'
        f'<span class="pl-sub-amt__text">{amt}</span></th>'
        f'<th class="pl-sub-ratio pl-sub-ratio--year" scope="col" id="pl-sub-ratio-year">'
        f'<span class="pl-sub-ratio__text">{ratio}</span></th>'
    )
    return "".join(parts)


def bizdays_label_row_v1(lang: str) -> str:
    L = LABELS_EN if lang == "en" else LABELS_JA
    label = L["bizdays_row"]
    return (
        f'<tr class="pl-data-row pl-data-row--bizdays" data-row="bizdays">'
        f'<th class="pl-row-label" scope="row" id="pl-row-bizdays" colspan="2">'
        f'<span class="pl-row-label__text">{label}</span></th></tr>'
    )


def bizdays_data_row_v1(lang: str) -> str:
    cells = [
        '<tr class="pl-data-row pl-data-row--bizdays" data-row="bizdays">',
    ]
    for mi in range(12):
        cells.append(
            f'<td class="pl-span-cell pl-bizdays-val" colspan="2" '
            f'data-pl-bizdays-month="{mi}">'
            f'<span class="pl-span-cell__text"></span></td>'
        )
    cells.append(
        '<td class="pl-span-cell pl-bizdays-val pl-bizdays-val--year" colspan="2" '
        'data-pl-bizdays-month="year">'
        '<span class="pl-span-cell__text"></span></td>'
    )
    cells.append("</tr>")
    return "".join(cells)


def month_headers(lang: str) -> str:
    months = MONTHS_EN if lang == "en" else MONTHS_JA
    corner = LABELS_EN["corner_title"] if lang == "en" else LABELS_JA["corner_title"]
    parts = [
        '<tr class="pl-head-months">',
        '<th class="pl-label pl-corner" rowspan="2">',
        '<span id="pl-store-name" class="pl-store-name"></span>',
        f'<span class="pl-corner-title">{corner}</span>',
        "</th>",
    ]
    for m in months:
        parts.append(f'<th colspan="2" class="pl-month">{m}</th>')
    total_l = LABELS_EN["total"] if lang == "en" else LABELS_JA["total"]
    parts.append(f'<th colspan="2" class="pl-month pl-month--total">{total_l}</th>')
    parts.append("</tr><tr class=\"pl-head-sub\">")
    amt = LABELS_EN["amount"] if lang == "en" else LABELS_JA["amount"]
    ratio = LABELS_EN["ratio"] if lang == "en" else LABELS_JA["ratio"]
    for _ in range(13):
        parts.append(f'<th class="pl-sub">{amt}</th><th class="pl-sub pl-sub--pct">{ratio}</th>')
    parts.append("</tr>")
    return "".join(parts)


def page_paths(lang: str) -> dict[str, str]:
    """Asset root + app URLs from profit/pl/index.html."""
    if lang == "en":
        return {
            "asset": "../../../../",
            "annual": "../../annual/index.html",
            "monthly": "../../monthly/index.html",
            "daily": "#",
            "insight": "../../monthly/index.html?open=insight",
            "insight_basic": "../../../setting/change_plan.html",
            "profit_hub": "../index.html",
            "pl_self": "index.html",
            "monthly_edit": "../../monthly/edit/index.html",
            "lang_en": "index.html",
            "lang_ja": "../../../../app/profit/pl/index.html",
            "setting": "../../../../en/setting/",
            "forge_url": "https://forge-laboratory.com/en",
        }
    return {
        "asset": "../../../",
        "annual": "../../annual/index.html",
        "monthly": "../../monthly/index.html",
        "daily": "#",
        "insight": "../../monthly/index.html?open=insight",
        "insight_basic": "../../../setting/change_plan.html",
        "profit_hub": "../index.html",
        "pl_self": "index.html",
        "monthly_edit": "../../monthly/edit/index.html",
        "lang_en": "../../../en/app/profit/pl/index.html",
        "lang_ja": "index.html",
        "setting": "../../../en/setting/",
        "forge_url": "https://forge-laboratory.com",
    }


def header_nav_html(lang: str, p: dict[str, str], L: dict) -> str:
    if lang == "ja":
        labels = ("年次", "月次", "日次", L["nav_insight"])
        aria = (
            "年間ビュー",
            "月間ビュー",
            "月次ページで日次ビューを開く",
            L["nav_insight_aria"],
        )
    else:
        labels = ("Annual", "Monthly", "Daily", L["nav_insight"])
        aria = (
            "Go to Annual view",
            "Go to Monthly view",
            "Open Daily on Monthly",
            L["nav_insight_aria"],
        )
    hrefs = (p["annual"], p["monthly"], p["daily"], p["insight"])
    lis = []
    for i, (href, text, alabel) in enumerate(zip(hrefs, labels, aria)):
        extra = ""
        if i == 2:
            extra = ' id="global-nav-daily-btn"'
        if i == 3:
            extra = (
                f' id="global-nav-index-btn" data-href-pro="{p["insight"]}"'
                f' data-href-basic="{p["insight_basic"]}"'
            )
        lis.append(
            f"""          <li class="global-nav-item">
            <a href="{href}" class="nav-frame-btn" data-pl-nav="1"{extra} aria-label="{alabel}">
              <span class="btn-mode-frame">
                <img src="{p['asset']}images/button_frame.svg" alt="" class="btn-mode-frame-img" aria-hidden="true">
                <span class="btn-mode-text nav-btn-text">{text}</span>
              </span>
            </a>
          </li>"""
        )
    return "\n".join(lis)


def render_page(lang: str, lang_switch: str) -> str:
    L = LABELS_EN if lang == "en" else LABELS_JA
    corner_title = L["corner_title"]
    label_colgroup = pl_label_colgroup()
    data_colgroup = pl_data_colgroup()
    month_heads = month_head_row_v1(lang)
    month_subheads = month_subhead_row_v1(lang)
    bizdays_label = bizdays_label_row_v1(lang)
    bizdays_data = bizdays_data_row_v1(lang)
    income_label_rows = income_label_rows_v1(lang)
    income_data_rows = income_data_rows_v1(lang)
    expenses_label_rows = expenses_label_rows_v1(lang)
    expenses_data_rows = expenses_data_rows_v1(lang)
    ref_budget_label_row = reference_budget_label_row_v1(lang)
    ref_budget_data_row = reference_budget_data_row_v1(lang)
    analyze_only_label_rows = analyze_label_rows_v1(lang)
    analyze_only_data_rows = analyze_data_rows_v1(lang)
    profit_label_row = profit_label_row_v1(lang)
    profit_data_row = profit_data_row_v1(lang)
    expenses_detail_header_label = expenses_detail_header_label_row(lang, L)
    expenses_detail_header_data = expenses_detail_header_data_row()
    analyze_band = L["analyze_band"]
    analyze_toggle_aria = L["analyze_toggle_aria"]
    expense_detail_label_colgroup = pl_expense_detail_label_colgroup()
    expense_catalog_json = json.dumps(expense_detail_default_catalog(), ensure_ascii=False)
    expense_detail_add_aria = L["expense_detail_add_aria"]
    expense_detail_hide_aria = L["expense_detail_hide_aria"]
    expense_detail_move_up_aria = L["expense_detail_move_up_aria"]
    expense_detail_move_down_aria = L["expense_detail_move_down_aria"]
    expense_detail_new_row = L["expense_detail_new_row"]
    expense_mid_fixed = EXPENSES_ROWS_V1[0][2] if lang == "en" else EXPENSES_ROWS_V1[0][1]
    expense_mid_var = EXPENSES_ROWS_V1[1][2] if lang == "en" else EXPENSES_ROWS_V1[1][1]
    label_edit_js = pl_label_edit_client_js(
        edit_aria=L["edit_label_aria"],
        expense_catalog_json=expense_catalog_json,
    )
    expense_detail_js = expense_detail_client_js(
        catalog_json=expense_catalog_json,
        mid_fixed=expense_mid_fixed,
        mid_var=expense_mid_var,
        add_aria=expense_detail_add_aria,
        hide_aria=expense_detail_hide_aria,
        hide_confirm_title=L["hide_line_confirm_title"],
        hide_confirm_body=L["hide_line_confirm_body"],
        hide_confirm_ok=L["hide_line_confirm_ok"],
        hide_confirm_cancel=L["hide_line_confirm_cancel"],
        delete_line_confirm_title=L["delete_line_confirm_title"],
        delete_line_confirm_body=L["delete_line_confirm_body"],
        delete_line_confirm_ok=L["delete_line_confirm_ok"],
        line_manage_title=L["line_manage_title"],
        line_manage_empty=L["line_manage_empty"],
        line_manage_restore=L["line_manage_restore"],
        line_manage_close=L["line_manage_close"],
        move_up_aria=expense_detail_move_up_aria,
        move_down_aria=expense_detail_move_down_aria,
        new_row=expense_detail_new_row,
        edit_aria=L["edit_label_aria"],
        expense_attribute_add_title=L["expense_attribute_title"],
        expense_attribute_variable_add_title=L["expense_attribute_variable_title"],
        expense_attribute_edit_title=L["expense_attribute_edit_title"],
        expense_attribute_btn_label=L["expense_attribute_btn"],
        expense_attribute_btn_aria=L["expense_attribute_btn_aria"],
        expense_attr_edit_toggle=L["expense_attr_edit_toggle"],
        expense_attr_edit_toggle_aria=L["expense_attr_edit_toggle_aria"],
        expense_attr_edit_on=L["expense_attr_edit_on"],
        expense_attr_edit_off=L["expense_attr_edit_off"],
        variable_mid_edit_tip=L["variable_mid_edit_tip"],
        schema_version=CATALOG_SCHEMA_VERSION,
        occupancy_aria=L["occupancy_aria"],
        occupancy_rent_option=L["occupancy_rent"],
        occupancy_owned_option=L["occupancy_owned"],
    )
    graph_months_json = json.dumps(
        MONTHS_EN if lang == "en" else MONTHS_JA, ensure_ascii=False
    )
    graph_dummy_json = json.dumps(pl_graph_dummy_months())
    graph_js = pl_graph_client_js(
        months_json=graph_months_json,
        dummy_json=graph_dummy_json,
        graph_band=L["graph_band"],
        monthly_sales_l=L["graph_monthly_sales"],
        expenses_l=L["graph_expenses"],
        fixed_l=L["fixed"],
        expected_l=EXPENSES_ROWS_V1[1][2] if lang == "en" else EXPENSES_ROWS_V1[1][1],
        is_ja=lang == "ja",
    )
    graph_band = L["graph_band"]
    input_source_modal_html = pl_input_source_modal_html(L)
    label_edit_modal_html = pl_expense_label_edit_modal_html(L)
    adj_modal_html = pl_expense_adj_modal_html(L)
    expense_attribute_modal_html = pl_expense_attribute_modal_html(L, lang)
    hide_line_modal_html = pl_hide_line_modal_html(L)
    line_manage_modal_html = pl_line_manage_modal_html(L)
    graph_overlay_html = pl_graph_overlay_html(L)
    p = page_paths(lang)
    compare_labels = {
        "compare_prev_day_aria": L["compare_prev_day_aria"],
        "compare_next_day_aria": L["compare_next_day_aria"],
        "compare_date_pick_aria": L["compare_date_pick_aria"],
        "compare_today": L["compare_today"],
        "compare_section1_title": L["compare_section1_title"],
        "compare_income": L["compare_income"],
        "compare_expenses": L["compare_expenses"],
        "compare_expected_fixed": L["compare_expected_fixed"],
        "compare_profit": L["compare_profit"],
        "compare_open_monthly_edit": L["compare_open_monthly_edit"],
        "compare_open_current_month": L["compare_open_current_month"],
        "compare_chart_open_aria": L["compare_chart_open_aria"],
        "compare_area1_title": L["compare_area1_title"],
        "compare_area2_title": L["compare_area2_title"],
        "compare_area3_title": L["compare_area3_title"],
        "compare_food_labor": L["compare_food_labor"],
        "compare_food_slash_labor": L["compare_food_slash_labor"],
        "compare_same_weekday_of": L["compare_same_weekday_of"],
        "compare_area2_hsnap_primary": L["compare_area2_hsnap_primary"],
        "compare_area2_hsnap_secondary": L["compare_area2_hsnap_secondary"],
        "compare_area3_hsnap_primary": L["compare_area3_hsnap_primary"],
        "compare_area3_hsnap_secondary": L["compare_area3_hsnap_secondary"],
        "compare_no_data": L["compare_no_data"],
        "compare_line_title": L["compare_line_title"],
        "compare_area2_line_title": L["compare_area2_line_title"],
        "compare_area3_line_title": L["compare_area3_line_title"],
        "compare_this_year": L["compare_this_year"],
        "compare_last_year": L["compare_last_year"],
        "compare_best_year": L["compare_best_year"],
        "compare_fixed": L["compare_fixed"],
        "compare_expected": L["compare_expected"],
        "compare_daily_title": L["compare_daily_title"],
        "compare_area2_daily_title": L["compare_area2_daily_title"],
        "compare_area3_daily_title": L["compare_area3_daily_title"],
    }
    compare_js = pl_compare_client_js(monthly_edit=p["monthly_edit"], labels=compare_labels)
    html_lang = "en" if lang == "en" else "ja"
    # Canonical Global Menu (single source: scripts/site_chrome.py). PL keeps its
    # page-specific wiring via overrides: pl-* classes for the PL CSS, a
    # data-pl-nav="1" leave-guard on every nav item, and the Insight deep link.
    # base is the language-root prefix (JA=repo root, EN=en/) — both 3 levels up
    # from app/profit/pl/. This also fixes the old JA→en/setting popup drift.
    header = build_header(
        lang, "../../../", p["asset"], None,
        daily_mode="overlay",
        header_class="pl-site-header",
        nav_class="pl-header-global-nav",
        nav_attr=' data-pl-nav="1"',
        profit_href=p["insight"],
    )
    if lang == "ja":
        office_aria_off = "Office Mode に切り替え"
        office_aria_on = "Sci-Fi Mode に切り替え"
    else:
        office_aria_off = "Switch to Office Mode"
        office_aria_on = "Switch to Sci-Fi Mode"
    return f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{L['title']} | KPI Navigator</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=BIZ+UDP+Gothic:wght@400;500;700&family=Orbitron:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{p['asset']}register/style.css">
  <link rel="stylesheet" href="{p['asset']}en/setting/style.css">
  <style>
    .profile-page.office-mode .global-nav-list .global-nav-item {{
      flex: 0 0 auto;
    }}
    .profile-page.office-mode .global-nav-list {{
      gap: 28px !important;
    }}
    .profile-page.office-mode .global-nav-list .nav-frame-btn {{
      display: inline-block !important;
      width: 120px !important;
    }}
    .profile-page.office-mode .global-nav-list .nav-frame-btn .btn-mode-frame {{
      position: relative !important;
      display: inline-flex !important;
      justify-content: center;
      align-items: center;
      width: 120px !important;
      max-width: 120px !important;
    }}
    .profile-page.office-mode .global-nav-list .nav-frame-btn .btn-mode-frame-img {{
      display: none !important;
    }}
    .profile-page.office-mode .global-nav-list .nav-frame-btn .btn-mode-text {{
      position: static !important;
      inset: auto !important;
      display: inline-block !important;
      white-space: nowrap;
      padding: 0 !important;
    }}
    html[lang='ja'] .si-fi:not(.office-mode) .profile-page .global-nav-list {{
      gap: 24px;
    }}
    html[lang='en'] .si-fi:not(.office-mode) .profile-page .global-nav-list {{
      gap: 28px;
    }}
    body.pl-page .page-wrap.profile-wrap {{
      max-width: none;
      width: 100%;
      margin: 0;
      padding: 0;
    }}
    body.pl-page .profile-main {{
      padding: 12px 0 0;
      align-items: stretch;
      width: 100%;
      max-width: none;
    }}
    .pl-wrap {{
      --pl-cyan: #58e1f3;
      --pl-toolbar-inset: 16px;
      position: relative;
      width: 100%;
      max-width: none;
      margin: 0;
      padding: 0 0 12px;
      box-sizing: border-box;
    }}
    .pl-toolbar {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      min-height: 48px;
      margin-bottom: 8px;
      padding: 0 var(--pl-toolbar-inset);
      box-sizing: border-box;
    }}
    .pl-toolbar__row {{
      display: flex;
      align-items: flex-start;
      width: 100%;
      gap: 12px;
    }}
    .pl-toolbar__left {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px 14px;
      flex: 0 1 auto;
      min-width: 0;
    }}
    .pl-toolbar__center {{
      flex: 1 1 auto;
      display: flex;
      align-items: center;
      justify-content: center;
      min-width: 0;
    }}
    .pl-toolbar__actions {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: flex-end;
      gap: 8px;
      flex: 0 1 auto;
    }}
    .pl-toolbar__actions-col {{
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 8px;
      flex: 0 0 auto;
      margin-left: auto;
    }}
    .pl-toolbar__zoom {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: rgba(88, 225, 243, 0.85);
    }}
    .pl-toolbar__zoom-controls {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 0 0 auto;
    }}
    .pl-toolbar__zoom-pct-wrap {{
      flex: 0 0 42px;
      width: 42px;
      text-align: right;
      font-variant-numeric: tabular-nums;
      line-height: 1.2;
    }}
    .pl-toolbar__zoom-pct-wrap #pl-table-zoom-pct {{
      display: block;
    }}
    .pl-toolbar__zoom-step {{
      flex: 0 0 auto;
      width: 28px;
      height: 28px;
      padding: 0;
      border: 1px solid rgba(88, 225, 243, 0.5);
      background: transparent;
      color: rgba(88, 225, 243, 0.9);
      font-size: 18px;
      line-height: 1;
      cursor: pointer;
      border-radius: 2px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-family: inherit;
      user-select: none;
      touch-action: manipulation;
    }}
    .pl-toolbar__zoom-step:hover:not(:disabled) {{
      background: rgba(88, 225, 243, 0.12);
    }}
    .pl-toolbar__zoom-step:active:not(:disabled) {{
      background: rgba(88, 225, 243, 0.25);
    }}
    .pl-toolbar__zoom-step:disabled {{
      opacity: 0.35;
      cursor: default;
    }}
    .pl-toolbar__zoom input[type='range'] {{
      width: 120px;
      accent-color: #58e1f3;
    }}
    .pl-toolbar__zoom-edit {{
      width: 100%;
      border: 1px solid rgba(88, 225, 243, 0.5);
      background: rgba(0, 0, 0, 0.3);
      color: #58e1f3;
      font: inherit;
      text-align: right;
      padding: 2px 5px;
      border-radius: 2px;
      box-sizing: border-box;
    }}
    .pl-toolbar__btn {{
      min-width: 76px;
      height: 32px;
      padding: 0 12px;
      border: 1px solid var(--pl-cyan);
      border-radius: 3px;
      background: rgba(88, 225, 243, 0.18);
      color: var(--pl-cyan);
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.02em;
      cursor: pointer;
      font-family: 'Orbitron', sans-serif;
      white-space: nowrap;
      box-sizing: border-box;
    }}
    .pl-toolbar__btn:hover:not(:disabled) {{
      background: rgba(88, 225, 243, 0.42);
    }}
    .pl-toolbar__btn:disabled {{
      opacity: 0.45;
      cursor: not-allowed;
    }}
    .pl-toolbar__btn--graph {{
      min-width: 148px;
      padding: 0 14px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.04em;
      background: rgba(88, 225, 243, 0.28);
    }}
    .pl-toolbar__btn--save {{
      min-width: 88px;
      font-weight: 700;
      letter-spacing: 0.04em;
      background: rgba(88, 225, 243, 0.35);
    }}
    /* KPI-CSV-UPLOAD-TOOLTIP */
    #pl-csv-upload[data-tooltip] {{
      z-index: 2;
    }}
    #pl-csv-upload[data-tooltip]:hover::after,
    #pl-csv-upload[data-tooltip]:focus-visible::after {{
      content: attr(data-tooltip);
      position: absolute;
      left: 50%;
      top: calc(100% + 8px);
      transform: translateX(-50%);
      padding: 8px 10px;
      border: 1px solid var(--pl-cyan);
      border-radius: 3px;
      background: #102932;
      color: var(--pl-cyan);
      font-size: 12px;
      font-weight: 400;
      line-height: 1.45;
      text-align: left;
      white-space: normal;
      width: max-content;
      max-width: min(300px, 85vw);
      z-index: 200;
      pointer-events: none;
      box-shadow: 0 4px 14px rgba(16, 0, 82, 0.35);
    }}
    /* END KPI-CSV-UPLOAD-TOOLTIP */
    .pl-year-label {{
      font-family: 'Orbitron', sans-serif;
      font-size: 12px;
      color: var(--pl-cyan);
      font-weight: 600;
    }}
    .pl-year-select {{
      min-width: 108px;
      height: 32px;
      padding: 0 10px;
      border: 1px solid rgba(88, 225, 243, 0.45);
      border-radius: 3px;
      background: rgba(8, 18, 22, 0.95);
      color: var(--pl-cyan);
      font-family: 'Orbitron', sans-serif;
      font-size: 13px;
      font-weight: 600;
    }}
    .pl-toolbar__back {{
      color: var(--pl-cyan);
      font-family: 'Orbitron', sans-serif;
      font-size: 0.88rem;
      font-weight: 600;
      text-decoration: none;
    }}
    .pl-toolbar__back:hover {{
      text-decoration: underline;
    }}
    .pl-toolbar__back[hidden] {{
      display: none !important;
    }}
    .pl-head-bar {{
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 12px 24px;
      margin-bottom: 10px;
    }}
    .pl-cell-editable {{
      cursor: text;
      outline: none;
    }}
    .pl-cell-editable:focus {{
      box-shadow: inset 0 0 0 1px rgba(88, 225, 243, 0.85);
      background-color: #152a32 !important;
    }}
    .pl-table tr[data-pl-expense="1"] .pl-cell-editable.pl-col-focus {{
      background-color: rgba(88, 225, 243, 0.14) !important;
    }}
    body.office-mode .pl-year-label,
    body.office-mode .pl-year-select,
    body.office-mode .pl-toolbar__btn {{
      font-family: 'BIZ UDP Gothic', sans-serif;
      color: #111;
    }}
    body.office-mode .pl-year-select {{
      background: #fff;
      border-color: #999;
    }}
    body.office-mode .pl-toolbar__btn--save {{
      background: #d8ece8;
      border-color: #0a5;
    }}
    body.office-mode .pl-toolbar__btn:not(.pl-toolbar__btn--save) {{
      background: #e8e8e8;
      border-color: #999;
    }}
    body.office-mode .pl-toolbar__btn--graph {{
      background: #dceef0;
      border-color: #089;
    }}
    body.office-mode .pl-toolbar__back {{
      color: #0a5;
      font-family: 'BIZ UDP Gothic', sans-serif;
    }}
    body.office-mode .pl-toolbar__zoom {{
      color: #333;
    }}
    body.office-mode .pl-toolbar__zoom-step {{
      border-color: #888;
      color: #333;
    }}
    body.office-mode .pl-toolbar__zoom-step:hover:not(:disabled) {{
      background: rgba(0, 0, 0, 0.06);
    }}
    body.office-mode .pl-toolbar__zoom-edit {{
      border-color: #888;
      background: #fff;
      color: #111;
    }}
    .pl-graph-overlay[hidden] {{
      display: none !important;
    }}
    .pl-graph-overlay {{
      position: fixed;
      inset: 0;
      z-index: 12000;
      display: flex;
      align-items: flex-start;
      justify-content: center;
      padding: 12px 0;
      box-sizing: border-box;
      overflow: auto;
    }}
    .pl-graph-overlay__backdrop {{
      position: absolute;
      inset: 0;
      background: rgba(2, 8, 12, 0.78);
    }}
    .pl-graph-overlay__panel {{
      position: relative;
      display: flex;
      flex-direction: column;
      width: 1100px;
      height: min(5681px, calc(100vh - 24px));
      border: 3px solid #0f9403;
      border-radius: 12px;
      background: #0c0c0c;
      box-sizing: border-box;
      overflow: hidden;
      color: #58e1f3;
      font-family: 'Orbitron', sans-serif;
      z-index: 1;
    }}
    html[lang='ja'] .pl-graph-overlay__panel {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-graph-overlay__close {{
      position: absolute;
      right: 14px;
      top: 12px;
      z-index: 10;
      width: 22px;
      height: 22px;
      box-sizing: border-box;
      border: 1px solid rgba(88, 225, 243, 0.8);
      border-radius: 2px;
      background: rgba(88, 225, 243, 0.2);
      color: #58e1f3;
      font-size: 16px;
      line-height: 1;
      padding: 0;
      margin: 0;
      cursor: pointer;
      appearance: none;
      -webkit-appearance: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-family: 'Orbitron', sans-serif;
      pointer-events: auto;
    }}
    html[lang='ja'] .pl-graph-overlay__close {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-compare-header {{
      flex: 0 0 auto;
      display: flex;
      flex-direction: column;
      position: relative;
      z-index: 2;
      --pl-compare-header-h: 170px;
      --pl-compare-tab-h: 40px;
      --pl-compare-rule-h: 0.5px;
      height: var(--pl-compare-header-h);
      box-sizing: border-box;
      background: #0c0c0c;
    }}
    .pl-graph-overlay__title {{
      margin: 0;
      padding-top: 47px;
      text-align: center;
      font-size: 23px;
      line-height: 1;
      color: #58e1f3;
      font-weight: 700;
      letter-spacing: 0.02em;
      white-space: nowrap;
      flex: 0 0 auto;
    }}
    html[lang='ja'] .pl-graph-overlay__title {{
      font-family: 'BIZ UDPGothic', sans-serif;
      font-weight: 700;
    }}
    .pl-compare-toolbar {{
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: var(--pl-compare-tab-h);
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 12px;
      margin-top: 0;
      padding: 0 30px 0 70px;
      box-sizing: border-box;
    }}
    .pl-compare-date-row {{
      display: flex;
      align-items: center;
      justify-content: flex-start;
      gap: 10px;
      min-height: 40px;
      box-sizing: border-box;
    }}
    .pl-compare-date-nav,
    .pl-compare-date-btn {{
      border: 0;
      padding: 0;
      margin: 0;
      background: transparent;
      color: #58e1f3;
      font-size: 16px;
      line-height: 1;
      cursor: pointer;
      font-family: 'Orbitron', sans-serif;
    }}
    html[lang='ja'] .pl-compare-date-nav,
    html[lang='ja'] .pl-compare-date-btn {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-compare-today {{
      min-height: 24px;
      padding: 0 10px;
      border: 1px solid #58e1f3;
      border-radius: 999px;
      background: rgba(88, 225, 243, 0.2);
      color: #58e1f3;
      font-size: 12px;
      display: inline-flex;
      align-items: center;
      cursor: pointer;
      font-family: 'Orbitron', sans-serif;
    }}
    html[lang='ja'] .pl-compare-today {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-compare-today[hidden] {{
      display: none !important;
    }}
    .pl-compare-date-input {{
      position: absolute;
      width: 1px;
      height: 1px;
      opacity: 0;
      pointer-events: none;
    }}
    .pl-compare-area-nav {{
      display: flex;
      align-items: flex-end;
      justify-content: flex-end;
      gap: 10px;
      position: relative;
      z-index: 1;
    }}
    .pl-compare-area-tab {{
      width: 120px;
      height: var(--pl-compare-tab-h);
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      appearance: none;
      -webkit-appearance: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-width: 0.5px;
      border-style: solid;
      border-color: #58e1f3;
      border-radius: 5px 5px 0 0;
      background: rgba(88, 225, 243, 0.08);
      color: #58e1f3;
      font-size: 15px;
      line-height: 1;
      cursor: pointer;
      font-family: 'Orbitron', sans-serif;
    }}
    html[lang='ja'] .pl-compare-area-tab {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-compare-header__rule {{
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: var(--pl-compare-rule-h);
      margin: 0;
      padding: 0;
      border: 0;
      background: #58e1f3;
      pointer-events: none;
      z-index: 2;
    }}
    .pl-graph-overlay__scroll {{
      flex: 1 1 auto;
      min-height: 0;
      overflow-x: hidden;
      overflow-y: auto;
      box-sizing: border-box;
    }}
    .pl-compare-content {{
      box-sizing: border-box;
    }}
    .pl-compare-area {{
      min-height: 900px;
      border-top: 0.5px solid rgba(88, 225, 243, 0.72);
      box-sizing: border-box;
    }}
    .pl-compare-area:last-child {{
      border-bottom: 0.5px solid rgba(88, 225, 243, 0.72);
    }}
    .pl-compare-area-title {{
      margin: 0;
      padding-top: 35px;
      padding-left: 55px;
      color: #58e1f3;
      font-size: 15px;
      font-weight: 700;
      line-height: 1.35;
      text-align: left;
      box-sizing: border-box;
      font-family: 'Orbitron', sans-serif;
    }}
    html[lang='ja'] .pl-compare-area-title {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-compare-area-fl {{
      margin-top: 30px;
      box-sizing: border-box;
    }}
    .pl-compare-hsnap + .pl-compare-hsnap {{
      margin-top: 127px;
    }}
    .pl-compare-hsnap__date {{
      margin: 0 0 28px;
      color: #58e1f3;
      font-size: 20px;
      font-weight: 500;
      line-height: 1.2;
      text-align: center;
      font-family: 'Orbitron', sans-serif;
    }}
    html[lang='ja'] .pl-compare-hsnap__date {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-compare-hsnap__rows {{
      --pl-hsnap-label-w: 185px;
      --pl-hsnap-gap-w: 35px;
      --pl-hsnap-track-w: 530px;
      --pl-hsnap-meta-min-w: 240px;
      width: calc(
        var(--pl-hsnap-label-w) + var(--pl-hsnap-gap-w) + var(--pl-hsnap-track-w) +
          var(--pl-hsnap-meta-min-w)
      );
      max-width: calc(100% - 60px);
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 0;
      box-sizing: border-box;
    }}
    .pl-compare-hsnap-row {{
      display: grid;
      grid-template-columns:
        var(--pl-hsnap-label-w)
        var(--pl-hsnap-gap-w)
        var(--pl-hsnap-track-w)
        minmax(var(--pl-hsnap-meta-min-w), max-content);
      align-items: stretch;
      height: 30px;
      box-sizing: border-box;
    }}
    .pl-compare-hsnap-row__label {{
      grid-column: 1;
      color: #58e1f3;
      font-size: 15px;
      line-height: 30px;
      text-align: right;
      white-space: nowrap;
      box-sizing: border-box;
      font-family: 'Orbitron', sans-serif;
    }}
    html[lang='ja'] .pl-compare-hsnap-row__label {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-compare-hsnap-row__track {{
      grid-column: 3;
      position: relative;
      width: var(--pl-hsnap-track-w);
      height: 30px;
      box-sizing: border-box;
    }}
    .pl-compare-hsnap-row__meta {{
      grid-column: 4;
      color: #58e1f3;
      font-size: 15px;
      line-height: 30px;
      text-align: right;
      white-space: nowrap;
      box-sizing: border-box;
      font-family: 'Orbitron', sans-serif;
      padding-left: 8px;
    }}
    html[lang='ja'] .pl-compare-hsnap-row__meta {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-compare-hbar {{
      display: block;
      height: 30px;
      min-width: 0;
      border-radius: 0;
    }}
    .pl-compare-hbar-stack {{
      display: flex;
      height: 30px;
      min-width: 0;
      align-items: stretch;
    }}
    .pl-compare-hbar--green {{
      background: #3cb878;
    }}
    .pl-compare-hbar--red {{
      background: #d64545;
    }}
    .pl-compare-hbar--orange {{
      background: #e8883a;
    }}
    .pl-compare-hbar--yellow {{
      background: #e8c547;
    }}
    .pl-compare-hsnap__empty {{
      margin: 0;
      padding: 24px 55px;
      color: rgba(88, 225, 243, 0.72);
      font-size: 15px;
      text-align: center;
      font-family: 'Orbitron', sans-serif;
    }}
    .pl-compare-hsnap__empty--solo {{
      padding-top: 48px;
    }}
    html[lang='ja'] .pl-compare-hsnap__empty {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-compare-area-line {{
      margin-top: 96px;
      padding: 0 55px 32px;
      box-sizing: border-box;
    }}
    .pl-compare-area-daily {{
      margin-top: 96px;
      padding: 0 55px 48px;
      box-sizing: border-box;
    }}
    .pl-compare-line__title {{
      margin: 0;
      color: #58e1f3;
      font-size: 15px;
      line-height: 1.35;
      text-align: center;
      font-family: 'Orbitron', sans-serif;
    }}
    .pl-compare-line__date {{
      margin: 0 0 20px;
      color: #58e1f3;
      font-size: 20px;
      font-weight: 500;
      line-height: 1.2;
      text-align: center;
      font-family: 'Orbitron', sans-serif;
    }}
    .pl-compare-line__date.pl-compare-hsnap__date {{
      margin-bottom: 20px;
    }}
    .pl-compare-line__metric-tabs {{
      display: flex;
      justify-content: center;
      gap: 10px;
      margin-bottom: 18px;
    }}
    .pl-compare-line__metric {{
      width: 130px;
      height: 25px;
      border: 0.5px solid #58e1f3;
      background: transparent;
      color: #58e1f3;
      font-size: 15px;
      font-weight: 500;
      line-height: 1;
      font-family: 'Orbitron', sans-serif;
      cursor: pointer;
      transform: scale(1);
      transform-origin: center;
    }}
    .pl-compare-line__metric.is-active {{
      background: rgba(88, 225, 243, 0.4);
      font-weight: 700;
      transform: scale(1.04);
    }}
    .pl-compare-line__chart-wrap {{
      position: relative;
      height: 420px;
    }}
    .pl-compare-line__hover-layer {{
      position: absolute;
      z-index: 3;
      cursor: crosshair;
    }}
    .pl-compare-line__guide-v {{
      position: absolute;
      top: 0;
      bottom: 34px;
      width: 1px;
      margin-left: -0.5px;
      background: rgba(88, 225, 243, 0.45);
      pointer-events: none;
      z-index: 2;
    }}
    .pl-compare-line__guide-v-svg {{
      stroke: #58e1f3;
      stroke-width: 1;
      vector-effect: non-scaling-stroke;
      stroke-dasharray: 4 3;
      opacity: 0;
    }}
    .pl-compare-line__guide-v-svg.is-visible {{
      opacity: 0.65;
    }}
    .pl-compare-line__hit-dot {{
      fill: #1e1e1e;
      stroke-width: 2;
      vector-effect: non-scaling-stroke;
      opacity: 0;
    }}
    .pl-compare-line__hit-dot.is-visible {{
      opacity: 1;
    }}
    .pl-compare-line__hit-dot--thisYear {{
      stroke: #66e7ff;
    }}
    .pl-compare-line__hit-dot--lastYear {{
      stroke: #e8e54b;
    }}
    .pl-compare-line__hit-dot--bestYear {{
      stroke: #16d33a;
    }}
    .pl-compare-chart-tooltip {{
      position: absolute;
      z-index: 5;
      min-width: 240px;
      max-width: 340px;
      padding: 12px 14px;
      border: 1px solid #0f9403;
      background: rgba(12, 12, 12, 0.96);
      box-sizing: border-box;
      pointer-events: none;
      font-family: 'Orbitron', sans-serif;
      visibility: hidden;
      opacity: 0;
      transition: opacity 0.12s ease;
    }}
    .pl-compare-chart-tooltip.is-visible {{
      visibility: visible;
      opacity: 1;
    }}
    .pl-compare-chart-tooltip__snap {{
      margin: 0 0 4px;
      color: #58e1f3;
      font-size: 13px;
      font-weight: 700;
      line-height: 1.35;
      text-align: center;
    }}
    .pl-compare-chart-tooltip__metric {{
      margin: 0 0 10px;
      color: rgba(88, 225, 243, 0.82);
      font-size: 11px;
      line-height: 1.3;
      text-align: center;
    }}
    .pl-compare-chart-tooltip__row {{
      margin: 0;
      display: flex;
      justify-content: space-between;
      gap: 12px;
      font-size: 11px;
      line-height: 1.45;
    }}
    .pl-compare-chart-tooltip__row + .pl-compare-chart-tooltip__row {{
      margin-top: 4px;
    }}
    .pl-compare-chart-tooltip__series {{
      flex: 1 1 auto;
      min-width: 0;
    }}
    .pl-compare-chart-tooltip__value {{
      flex: 0 0 auto;
      color: #58e1f3;
      white-space: nowrap;
    }}
    html[lang='ja'] .pl-compare-chart-tooltip,
    html[lang='ja'] .pl-compare-chart-tooltip__snap,
    html[lang='ja'] .pl-compare-chart-tooltip__metric,
    html[lang='ja'] .pl-compare-chart-tooltip__row,
    html[lang='ja'] .pl-compare-chart-tooltip__value {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    body.office-mode .pl-compare-chart-tooltip {{
      background: #fff;
      border-color: #999;
    }}
    body.office-mode .pl-compare-chart-tooltip__snap,
    body.office-mode .pl-compare-chart-tooltip__value {{
      color: #111;
    }}
    .pl-compare-line__svg {{
      display: block;
      width: 100%;
      height: 100%;
    }}
    .pl-compare-line__axis-label {{
      fill: #58e1f3;
      font-size: 12px;
      font-family: 'Orbitron', sans-serif;
    }}
    html[lang='ja'] .pl-compare-line__axis-label {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    body.office-mode .pl-compare-line__axis-label {{
      fill: #111;
    }}
    .pl-compare-line__y-ticks {{
      position: absolute;
      left: 0;
      right: 0;
      top: 0;
      bottom: 0;
      pointer-events: none;
    }}
    .pl-compare-line__y-ticks span {{
      position: absolute;
      left: 0;
      transform: translate(-6px, -50%);
      color: #58e1f3;
      font-size: 11px;
      font-family: 'Orbitron', sans-serif;
      opacity: 0.8;
    }}
    .pl-compare-line__legend {{
      display: flex;
      justify-content: center;
      gap: 22px;
      margin-top: 20px;
    }}
    .pl-compare-line__legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: #58e1f3;
      font-size: 15px;
      font-family: 'Orbitron', sans-serif;
    }}
    .pl-compare-line__legend-item input[type='checkbox'] {{
      width: 18px;
      height: 18px;
      accent-color: #16d33a;
      margin: 0;
    }}
    .pl-compare-line__swatch {{
      display: inline-block;
      width: 28px;
      height: 2px;
    }}
    .pl-compare-line__swatch--this {{ background: #66e7ff; }}
    .pl-compare-line__swatch--last {{ background: #e8e54b; }}
    .pl-compare-line__swatch--best {{ background: #16d33a; }}
    html[lang='ja'] .pl-compare-line__title,
    html[lang='ja'] .pl-compare-line__date,
    html[lang='ja'] .pl-compare-line__metric,
    html[lang='ja'] .pl-compare-line__y-ticks span,
    html[lang='ja'] .pl-compare-line__legend-item {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    body.office-mode .pl-compare-header {{
      background: #fff;
    }}
    body.office-mode .pl-compare-date-nav,
    body.office-mode .pl-compare-date-btn,
    body.office-mode .pl-compare-area-tab,
    body.office-mode .pl-compare-area-title,
    body.office-mode .pl-compare-hsnap__date,
    body.office-mode .pl-compare-hsnap-row__label,
    body.office-mode .pl-compare-hsnap-row__meta,
    body.office-mode .pl-compare-line__title,
    body.office-mode .pl-compare-line__date,
    body.office-mode .pl-compare-line__metric,
    body.office-mode .pl-compare-line__legend-item,
    body.office-mode .pl-compare-line__y-ticks span {{
      color: #111;
    }}
    body.office-mode .pl-compare-today {{
      border-color: #999;
      color: #111;
      background: #f0f0f0;
    }}
    body.office-mode .pl-compare-header__rule,
    body.office-mode .pl-compare-area {{
      border-color: #999;
    }}
    body.office-mode .pl-graph-overlay__panel {{
      background: #fff;
      border-color: #0f9403;
      color: #111;
      font-family: 'BIZ UDP Gothic', sans-serif;
    }}
    body.office-mode .pl-graph-overlay__close {{
      border-color: #999;
      background: #f0f0f0;
      color: #111;
    }}
    body.office-mode .pl-graph-overlay__title {{
      color: #111;
      font-family: 'BIZ UDP Gothic', sans-serif;
    }}
    body.pl-graph-overlay-open {{
      overflow: hidden;
    }}
    .pl-title {{
      margin: 0;
      font-family: 'Orbitron', sans-serif;
      font-size: 1.15rem;
      color: #58e1f3;
      font-weight: 600;
    }}
    .pl-meta {{
      margin: 0;
      color: rgba(255,255,255,0.82);
      font-size: 0.88rem;
    }}
    .pl-table-window {{
      /* ラベル帯: 中50 + 小350 = 400（支出詳細の小費目列は上部横ラベル300px + 50px） */
      --pl-label-band-w: 400px;
      --pl-v-major-w: 50px;
      --pl-v-mid-w: 50px;
      --pl-h-label-w: 300px;
      --pl-h-label-detail-w: 350px;
      --pl-corner-h: 60px;
      --pl-month-head-w: 260px;
      --pl-graph-cell-h: 700px;
      --pl-graph-bar-h: 533px;
      --pl-graph-bar-w: 30px;
      --pl-graph-half-w: 15px;
      --pl-graph-legend-gap: 20px;
      --pl-graph-legend-inset: calc(var(--pl-graph-legend-gap) + 4px);
      --pl-month-head-h: 30px;
      --pl-sub-amt-w: 160px;
      --pl-sub-ratio-w: 100px;
      --pl-row-label-h: 30px;
      --pl-analyze-band-h: 40px;
      --pl-analyze-bg: rgba(88, 225, 243, 0.3);
      --pl-cell-border-color: #58e1f3;
      --pl-cell-border: 1px solid var(--pl-cell-border-color);
      --pl-freeze-border: 3px double var(--pl-cell-border-color);
      /* ビューポート高固定 + 内側 zoom。Business Days 下のみ縦スクロール */
      --pl-viewport-h: calc(100vh - 132px);
      --pl-zoom-factor: 1;
      --pl-scrollbar-w: 8px;
      width: 100%;
      max-width: none;
      margin: 0;
      height: calc(var(--pl-viewport-h) / var(--pl-zoom-factor));
      min-height: 360px;
      background: transparent;
      border-radius: 0;
      box-sizing: border-box;
      overflow: hidden;
      position: relative;
    }}
    .pl-table-zoom-root {{
      display: flex;
      flex-direction: column;
      position: relative;
      width: 100%;
      height: 100%;
      min-height: 0;
      background: #1f1e1e;
      box-sizing: border-box;
    }}
    .pl-table-frozen {{
      flex: 0 0 auto;
      position: relative;
      z-index: 10;
      background: #1f1e1e;
      /* 下の縦スクロールバー幅分を確保し、月列の縦線を揃える */
      padding-right: var(--pl-scrollbar-w, 8px);
      box-sizing: border-box;
    }}
    .pl-table-scroll-y {{
      flex: 1 1 auto;
      min-height: 0;
      overflow-y: scroll;
      overflow-x: hidden;
      -webkit-overflow-scrolling: touch;
      background: #1f1e1e;
      scrollbar-gutter: stable;
      /* Business Days より下 — 縦ラベル用に行高を拡張（固定ペインは 30px のまま） */
      --pl-row-label-h: 40px;
      --pl-analyze-band-h: 40px;
    }}
    .pl-table-split {{
      display: flex;
      align-items: stretch;
      width: 100%;
      position: relative;
    }}
    .pl-split-seam {{
      position: absolute;
      top: 0;
      left: var(--pl-label-band-w);
      width: 0;
      border-left: var(--pl-cell-border);
      pointer-events: none;
      z-index: 25;
    }}
    .pl-table-zoom-root > .pl-split-seam {{
      bottom: 0;
      height: auto;
    }}
    .pl-label-pane {{
      flex: 0 0 var(--pl-label-band-w);
      width: var(--pl-label-band-w);
      z-index: 20;
      position: relative;
      border-left: var(--pl-cell-border);
      background: #1f1e1e;
      box-sizing: border-box;
    }}
    .pl-data-pane {{
      flex: 1 1 auto;
      min-width: 0;
      z-index: 1;
      overflow-x: auto;
      overflow-y: visible;
      -webkit-overflow-scrolling: touch;
      overscroll-behavior-x: contain;
      background: #1f1e1e;
      scrollbar-color: #58e1f3 #1f1e1e;
      scrollbar-width: thin;
    }}
    .pl-data-pane::-webkit-scrollbar {{
      height: 8px;
      width: 8px;
    }}
    .pl-data-pane::-webkit-scrollbar-track {{
      background: #1f1e1e;
    }}
    .pl-data-pane::-webkit-scrollbar-thumb {{
      background: #58e1f3;
    }}
    .pl-table-scroll-y {{
      scrollbar-color: #58e1f3 #1f1e1e;
      scrollbar-width: thin;
    }}
    .pl-table-scroll-y::-webkit-scrollbar {{
      width: 8px;
    }}
    .pl-table-scroll-y::-webkit-scrollbar-track {{
      background: #1f1e1e;
    }}
    .pl-table-scroll-y::-webkit-scrollbar-thumb {{
      background: #58e1f3;
    }}
    .pl-table--labels-body.pl-table--v1,
    .pl-table--data-body.pl-table--v1 {{
      border-top: none;
    }}
    .pl-table-frozen .pl-table.pl-table--v1 {{
      border-bottom: none;
    }}
    .pl-table-frozen .pl-data-row--bizdays > th,
    .pl-table-frozen .pl-data-row--bizdays > td {{
      border-bottom: var(--pl-freeze-border);
    }}
    body.office-mode .pl-table-frozen,
    body.office-mode .pl-table-scroll-y {{
      background: #f5f5f5;
    }}
    .pl-analyze-block {{
      width: 100%;
      flex-shrink: 0;
    }}
    .pl-analyze-band {{
      display: flex;
      align-items: center;
      gap: 8px;
      width: 100%;
      height: var(--pl-analyze-band-h);
      min-height: var(--pl-analyze-band-h);
      max-height: var(--pl-analyze-band-h);
      padding: 0 10px;
      box-sizing: border-box;
      border-left: var(--pl-cell-border);
      border-right: var(--pl-cell-border);
      border-bottom: var(--pl-cell-border);
      background: var(--pl-analyze-bg);
      color: #58e1f3;
      position: relative;
    }}
    .pl-analyze-band__text {{
      font-family: 'Orbitron', sans-serif;
      font-size: 15px;
      font-weight: 700;
      line-height: 1.2;
      letter-spacing: 0.02em;
    }}
    html[lang='ja'] .pl-analyze-band__text {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-analyze-toggle {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 20px;
      height: 20px;
      margin: 0;
      padding: 0;
      border: 0;
      background: transparent;
      color: #58e1f3;
      font-size: 11px;
      line-height: 1;
      cursor: pointer;
      flex-shrink: 0;
    }}
    .pl-analyze-collapsible.is-collapsed {{
      display: none;
    }}
    .pl-table--labels-analyze.pl-table--v1,
    .pl-table--data-analyze.pl-table--v1 {{
      border-top: none;
    }}
    .pl-data-row--profit > th,
    .pl-data-row--profit > td {{
      background: #1f1e1e !important;
    }}
    .pl-table--v1 .pl-h-label--profit {{
      width: var(--pl-label-band-w);
      min-width: var(--pl-label-band-w);
      max-width: var(--pl-label-band-w);
    }}
    body.office-mode .pl-data-row--profit > th,
    body.office-mode .pl-data-row--profit > td {{
      background: #fff !important;
    }}
    .pl-data-row--expenses-head > th,
    .pl-data-row--expenses-head > td {{
      background: #1f1e1e !important;
      height: var(--pl-row-label-h);
      min-height: var(--pl-row-label-h);
      max-height: var(--pl-row-label-h);
      box-sizing: border-box;
    }}
    .pl-expenses-head__data-band {{
      padding: 0;
      vertical-align: middle;
    }}
    .pl-table--v1 .pl-h-label--expenses-head {{
      width: var(--pl-h-label-detail-w);
      min-width: var(--pl-h-label-detail-w);
      max-width: var(--pl-h-label-detail-w);
      padding: 0 10px 0 8px;
      text-align: right;
    }}
    .pl-v-mid--expenses-head {{
      width: var(--pl-v-mid-w);
      min-width: var(--pl-v-mid-w);
      max-width: var(--pl-v-mid-w);
      padding: 0 2px;
      text-align: center;
      vertical-align: middle;
      border-right: none !important;
    }}
    .pl-expense-attr-toggle {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin: 0;
      padding: 2px 8px;
      border: 1px solid rgba(88, 225, 243, 0.45);
      border-radius: 3px;
      background: transparent;
      color: #58e1f3;
      font-size: 11px;
      line-height: 1.2;
      cursor: pointer;
      flex-shrink: 0;
      white-space: nowrap;
    }}
    html[lang='ja'] .pl-expense-attr-toggle {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-expense-detail-block.pl-expense-detail-block--attr-edit .pl-expense-attr-toggle {{
      border-color: #58e1f3;
      background: rgba(88, 225, 243, 0.12);
    }}
    .pl-expense-detail-block:not(.pl-expense-detail-block--attr-edit) .pl-row-attr {{
      display: none !important;
    }}
    body.office-mode .pl-data-row--expenses-head > th,
    body.office-mode .pl-data-row--expenses-head > td {{
      background: #fff !important;
    }}
    body.office-mode .pl-expense-attr-toggle {{
      border-color: #999;
      color: #111;
      font-family: 'BIZ UDP Gothic', sans-serif;
    }}
    body.office-mode .pl-expense-detail-block.pl-expense-detail-block--attr-edit .pl-expense-attr-toggle {{
      border-color: #333;
      background: rgba(0, 0, 0, 0.06);
    }}
    .pl-expense-detail-block {{
      width: 100%;
      flex-shrink: 0;
      position: relative;
    }}
    .pl-expense-hide-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin: 0 0 6px;
      padding: 8px 12px;
      border: 1px solid rgba(88, 225, 243, 0.45);
      border-radius: 4px;
      background: rgba(88, 225, 243, 0.08);
      color: #58e1f3;
      font-size: 12px;
      line-height: 1.35;
      box-sizing: border-box;
    }}
    .pl-expense-hide-bar[hidden] {{
      display: none !important;
    }}
    html[lang='ja'] .pl-expense-hide-bar {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-expense-hide-bar__cancel {{
      flex-shrink: 0;
      padding: 4px 10px;
      border: 1px solid rgba(88, 225, 243, 0.45);
      border-radius: 3px;
      background: transparent;
      color: #58e1f3;
      font-size: 12px;
      cursor: pointer;
    }}
    body.office-mode .pl-expense-hide-bar {{
      background: rgba(0, 0, 0, 0.04);
      border-color: #999;
      color: #111;
      font-family: 'BIZ UDP Gothic', sans-serif;
    }}
    body.office-mode .pl-expense-hide-bar__cancel {{
      border-color: #999;
      color: #111;
    }}
    .pl-expense-detail-block--hide-mode
      tr.pl-expense-detail-row--hide-pickable {{
      cursor: pointer;
    }}
    .pl-expense-detail-block--hide-mode
      tr.pl-expense-detail-row--hide-pickable:hover > th,
    .pl-expense-detail-block--hide-mode
      tr.pl-expense-detail-row--hide-pickable:hover > td {{
      background: rgba(88, 225, 243, 0.12) !important;
    }}
    tr.pl-expense-detail-row--hide-selected > th,
    tr.pl-expense-detail-row--hide-selected > td {{
      box-shadow: inset 0 0 0 2px #58e1f3;
    }}
    body.office-mode tr.pl-expense-detail-row--hide-selected > th,
    body.office-mode tr.pl-expense-detail-row--hide-selected > td {{
      box-shadow: inset 0 0 0 2px #333;
    }}
    .pl-v-mid__pm-btn--hide-armed {{
      background: rgba(88, 225, 243, 0.22) !important;
    }}
    body.office-mode .pl-v-mid__pm-btn--hide-armed {{
      background: rgba(0, 0, 0, 0.1) !important;
    }}
    .pl-table--labels-expense-detail.pl-table--v1,
    .pl-table--data-expense-detail.pl-table--v1 {{
      border-top: none;
    }}
    .pl-table--labels-expense-detail .pl-col-v-mid {{
      width: var(--pl-v-mid-w);
      min-width: var(--pl-v-mid-w);
      max-width: var(--pl-v-mid-w);
    }}
    .pl-table--labels-expense-detail .pl-col-h-label-detail {{
      width: var(--pl-h-label-detail-w);
      min-width: var(--pl-h-label-detail-w);
      max-width: var(--pl-h-label-detail-w);
    }}
    .pl-table--labels-expense-detail .pl-h-label {{
      width: var(--pl-h-label-detail-w);
      min-width: var(--pl-h-label-detail-w);
      max-width: var(--pl-h-label-detail-w);
      box-sizing: border-box;
    }}
    .pl-table--labels-expense-detail .pl-h-label--detail .pl-h-label__row {{
      max-width: 100%;
      min-width: 0;
      box-sizing: border-box;
    }}
    .pl-table--labels-expense-detail .pl-h-label--detail .pl-h-label__text {{
      flex: 1 1 auto;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .pl-expense-detail-block .pl-table--labels-expense-detail th:not(.pl-v-mid--expense-detail),
    .pl-expense-detail-block .pl-table--labels-expense-detail td:not(.pl-v-mid--expense-detail) {{
      border-right: none !important;
    }}
    .pl-expense-detail-block .pl-table--labels-expense-detail .pl-v-mid--expense-detail {{
      border-right: var(--pl-cell-border) !important;
    }}
    .pl-expense-detail-block .pl-table--labels-expense-detail .pl-v-mid--expenses-head {{
      border-right: none !important;
    }}
    .pl-expense-detail-block .pl-table--data-expense-detail tr.pl-data-row--expenses-head > td {{
      border-right: none;
    }}
    .pl-table--v1 .pl-v-mid--expense-detail {{
      width: var(--pl-v-mid-w);
      min-width: var(--pl-v-mid-w);
      max-width: var(--pl-v-mid-w);
      padding: 0;
      vertical-align: middle;
      text-align: center;
      position: relative;
      overflow: visible;
    }}
    .pl-table--v1 .pl-v-mid__inner {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      box-sizing: border-box;
    }}
    .pl-table--v1 .pl-v-mid__text {{
      position: absolute;
      left: 50%;
      top: 50%;
      display: inline-block;
      margin: 0;
      white-space: nowrap;
      transform: translate(-50%, -50%) rotate(-90deg);
      transform-origin: center center;
      font-size: 13px;
      font-weight: 400;
      line-height: 1;
      letter-spacing: 0.04em;
      color: #58e1f3;
      pointer-events: none;
    }}
    html[lang='ja'] .pl-table--v1 .pl-v-mid__text {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-table--v1 .pl-v-mid__pm {{
      position: absolute;
      right: 3px;
      bottom: 4px;
      display: flex;
      flex-direction: column;
      align-items: stretch;
      gap: 0;
      border: 1px solid rgba(88, 225, 243, 0.55);
      border-radius: 2px;
      overflow: hidden;
      background: rgba(88, 225, 243, 0.08);
      flex-shrink: 0;
      z-index: 1;
    }}
    .pl-table--v1 .pl-v-mid__pm-btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 16px;
      height: 13px;
      margin: 0;
      padding: 0;
      border: 0;
      border-bottom: 1px solid rgba(88, 225, 243, 0.55);
      border-radius: 0;
      background: transparent;
      color: #58e1f3;
      font-family: inherit;
      font-size: 11px;
      line-height: 1;
      cursor: pointer;
      flex-shrink: 0;
    }}
    .pl-table--v1 .pl-v-mid__pm-btn:last-child {{
      border-bottom: 0;
    }}
    .pl-table--v1 .pl-v-mid__pm-btn:disabled {{
      opacity: 0.35;
      cursor: not-allowed;
    }}
    .pl-table--v1 .pl-h-label--detail .pl-h-label__row {{
      width: 100%;
      justify-content: flex-end;
      gap: 4px;
    }}
    .pl-table--v1 .pl-occupancy-select-wrap {{
      display: inline-flex;
      flex: 0 0 auto;
      align-items: center;
      max-width: 72px;
    }}
    .pl-table--v1 .pl-occupancy-select {{
      width: 100%;
      max-width: 72px;
      height: 22px;
      margin: 0;
      padding: 0 2px;
      border: 1px solid rgba(88, 225, 243, 0.55);
      border-radius: 2px;
      background: rgba(8, 18, 22, 0.95);
      color: #58e1f3;
      font-family: inherit;
      font-size: 11px;
      line-height: 1.2;
      cursor: pointer;
    }}
    html[lang='ja'] .pl-table--v1 .pl-occupancy-select {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    body.office-mode .pl-table--v1 .pl-occupancy-select {{
      border-color: #94a3b8;
      background: #fff;
      color: #0f172a;
    }}
    .pl-table--v1 .pl-row-order {{
      display: inline-flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0;
      flex-shrink: 0;
      margin-left: 2px;
    }}
    .pl-table--v1 .pl-row-order__btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 14px;
      height: 11px;
      margin: 0;
      padding: 0;
      border: 0;
      background: transparent;
      color: #58e1f3;
      font-size: 8px;
      line-height: 1;
      cursor: pointer;
    }}
    .pl-table--v1 .pl-row-order__btn:disabled {{
      opacity: 0.3;
      cursor: not-allowed;
    }}
    .pl-table--v1 .pl-v-mid__pm--add-only .pl-v-mid__pm-btn {{
      border-bottom: 0;
    }}
    .pl-table--v1 .pl-row-hide {{
      display: inline-flex;
      flex-shrink: 0;
      border: 1px solid rgba(88, 225, 243, 0.55);
      border-radius: 2px;
      overflow: hidden;
      background: rgba(88, 225, 243, 0.08);
    }}
    .pl-table--v1 .pl-row-hide__btn {{
      border-bottom: 0 !important;
    }}
    .pl-table--v1 .pl-row-attr {{
      display: inline-flex;
      flex-shrink: 0;
    }}
    .pl-table--v1 .pl-row-attr__btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 28px;
      height: 13px;
      margin: 0;
      padding: 0 4px;
      border: 1px solid rgba(88, 225, 243, 0.45);
      border-radius: 2px;
      background: rgba(88, 225, 243, 0.08);
      color: #58e1f3;
      font-family: inherit;
      font-size: 9px;
      line-height: 1;
      letter-spacing: 0.02em;
      cursor: pointer;
      white-space: nowrap;
    }}
    body.office-mode .pl-table--v1 .pl-row-attr__btn {{
      border-color: #999;
      background: #f5f5f5;
      color: #111;
    }}
    .pl-table--v1 .pl-v-mid--expense-detail {{
      background: #1f1e1e !important;
    }}
    .pl-expense-detail-row--input-monthly > th.pl-h-label--detail,
    .pl-expense-detail-row--input-monthly > td {{
      background: rgba(20, 72, 52, 0.72) !important;
    }}
    .pl-expense-detail-row--input-daily > th.pl-h-label--detail,
    .pl-expense-detail-row--input-daily > td {{
      background: transparent;
    }}
    body.office-mode .pl-table--v1 .pl-v-mid__text {{
      font-family: 'BIZ UDP Gothic', sans-serif;
      color: #111;
    }}
    body.office-mode .pl-table--v1 .pl-v-mid__pm {{
      border-color: #999;
      background: #f5f5f5;
    }}
    body.office-mode .pl-table--v1 .pl-v-mid__pm-btn {{
      border-bottom-color: #999;
      color: #111;
      background: transparent;
    }}
    body.office-mode .pl-table--v1 .pl-row-order__btn {{
      color: #111;
    }}
    body.office-mode .pl-table--v1 .pl-v-mid--expense-detail {{
      background: #fff !important;
    }}
    body.office-mode .pl-expense-detail-row--input-monthly > th.pl-h-label--detail,
    body.office-mode .pl-expense-detail-row--input-monthly > td {{
      background: rgba(180, 220, 200, 0.45) !important;
    }}
    .pl-hide-line-modal,
    .pl-line-manage-modal {{
      position: fixed;
      inset: 0;
      z-index: 12000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      box-sizing: border-box;
    }}
    .pl-hide-line-modal[hidden],
    .pl-line-manage-modal[hidden] {{
      display: none !important;
    }}
    .pl-hide-line-modal__backdrop,
    .pl-line-manage-modal__backdrop {{
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.62);
    }}
    .pl-hide-line-modal__panel,
    .pl-line-manage-modal__panel {{
      position: relative;
      width: min(420px, 100%);
      padding: 22px 22px 18px;
      border: 1px solid rgba(88, 225, 243, 0.55);
      border-radius: 6px;
      background: #1f1e1e;
      color: #58e1f3;
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
      box-sizing: border-box;
    }}
    html[lang='ja'] .pl-hide-line-modal__panel,
    html[lang='ja'] .pl-line-manage-modal__panel {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-hide-line-modal__title,
    .pl-line-manage-modal__title {{
      margin: 0 0 12px;
      font-size: 15px;
      font-weight: 600;
      line-height: 1.45;
    }}
    .pl-hide-line-modal__body {{
      margin: 0 0 16px;
      font-size: 14px;
      line-height: 1.5;
      color: rgba(88, 225, 243, 0.92);
    }}
    .pl-hide-line-modal__actions,
    .pl-line-manage-modal__actions {{
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }}
    .pl-hide-line-modal__btn,
    .pl-line-manage-modal__btn {{
      min-width: 88px;
      min-height: 34px;
      padding: 6px 14px;
      border: 1px solid rgba(88, 225, 243, 0.55);
      border-radius: 4px;
      background: transparent;
      color: #58e1f3;
      font: inherit;
      font-size: 13px;
      cursor: pointer;
    }}
    .pl-hide-line-modal__btn--primary {{
      background: rgba(88, 225, 243, 0.18);
      font-weight: 700;
    }}
    .pl-line-manage__list {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-height: min(360px, 50vh);
      overflow-y: auto;
      margin: 0 0 16px;
    }}
    .pl-line-manage__empty {{
      margin: 0 0 16px;
      font-size: 14px;
      color: rgba(88, 225, 243, 0.72);
    }}
    .pl-line-manage__item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 8px 10px;
      border: 1px solid rgba(88, 225, 243, 0.28);
      border-radius: 4px;
      background: rgba(88, 225, 243, 0.06);
    }}
    .pl-line-manage__item-label {{
      flex: 1 1 auto;
      min-width: 0;
      font-size: 13px;
      line-height: 1.35;
    }}
    .pl-line-manage__restore {{
      flex: 0 0 auto;
      min-height: 28px;
      padding: 4px 10px;
      border: 1px solid rgba(88, 225, 243, 0.55);
      border-radius: 3px;
      background: rgba(88, 225, 243, 0.12);
      color: #58e1f3;
      font: inherit;
      font-size: 12px;
      cursor: pointer;
    }}
    body.office-mode .pl-expense-detail-row--input-pl > th,
    body.office-mode .pl-expense-detail-row--input-pl > td {{
      background: rgba(180, 220, 200, 0.45) !important;
    }}
    .pl-input-source-modal {{
      position: fixed;
      inset: 0;
      z-index: 12000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      box-sizing: border-box;
    }}
    .pl-input-source-modal[hidden] {{
      display: none !important;
    }}
    .pl-input-source-modal__backdrop {{
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.62);
    }}
    .pl-input-source-modal__panel {{
      position: relative;
      width: min(420px, 100%);
      padding: 22px 22px 18px;
      border: 1px solid rgba(88, 225, 243, 0.55);
      border-radius: 6px;
      background: #1f1e1e;
      color: #58e1f3;
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
      box-sizing: border-box;
    }}
    html[lang='ja'] .pl-input-source-modal__panel {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-input-source-modal__title {{
      margin: 0 0 16px;
      font-size: 15px;
      font-weight: 600;
      line-height: 1.45;
      letter-spacing: 0.02em;
    }}
    .pl-input-source-modal__choices {{
      margin: 0 0 14px;
      padding: 0;
      border: 0;
    }}
    .pl-input-source-modal__legend {{
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }}
    .pl-input-source-modal__choice {{
      display: flex;
      align-items: flex-start;
      gap: 10px;
      margin: 0 0 10px;
      font-size: 14px;
      line-height: 1.4;
      cursor: pointer;
    }}
    .pl-input-source-modal__choice input {{
      margin-top: 3px;
      flex-shrink: 0;
      accent-color: #58e1f3;
    }}
    .pl-input-source-modal__skip {{
      display: flex;
      align-items: flex-start;
      gap: 8px;
      margin: 0 0 18px;
      font-size: 12px;
      line-height: 1.35;
      color: rgba(88, 225, 243, 0.88);
      cursor: pointer;
    }}
    .pl-input-source-modal__skip input {{
      margin-top: 2px;
      accent-color: #58e1f3;
    }}
    .pl-input-source-modal__actions {{
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }}
    .pl-input-source-modal__btn {{
      min-width: 88px;
      padding: 8px 14px;
      border-radius: 4px;
      font-size: 13px;
      font-weight: 600;
      line-height: 1.2;
      cursor: pointer;
    }}
    .pl-input-source-modal__btn--ghost {{
      border: 1px solid rgba(88, 225, 243, 0.45);
      background: transparent;
      color: #58e1f3;
    }}
    .pl-input-source-modal__btn--primary {{
      border: 1px solid rgba(88, 225, 243, 0.75);
      background: rgba(88, 225, 243, 0.16);
      color: #58e1f3;
    }}
    body.office-mode .pl-input-source-modal__panel {{
      background: #fff;
      border-color: #999;
      color: #111;
      font-family: 'BIZ UDP Gothic', sans-serif;
    }}
    body.office-mode .pl-input-source-modal__choice input,
    body.office-mode .pl-input-source-modal__skip input {{
      accent-color: #333;
    }}
    body.office-mode .pl-input-source-modal__skip {{
      color: rgba(0, 0, 0, 0.72);
    }}
    body.office-mode .pl-input-source-modal__btn--ghost {{
      border-color: #999;
      color: #111;
    }}
    body.office-mode .pl-input-source-modal__btn--primary {{
      border-color: #666;
      background: #f0f0f0;
      color: #111;
    }}
    body.pl-input-source-modal-open,
    body.pl-expense-attribute-modal-open,
    body.pl-expense-label-edit-modal-open {{
      overflow: hidden;
    }}
    .pl-expense-label-edit-modal__field {{
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin: 0 0 16px;
    }}
    .pl-expense-label-edit-modal__field-label {{
      font-size: 12px;
      font-weight: 600;
      color: rgba(88, 225, 243, 0.88);
    }}
    .pl-expense-label-edit-modal__input {{
      width: 100%;
      box-sizing: border-box;
      padding: 8px 10px;
      border: 1px solid rgba(88, 225, 243, 0.45);
      border-radius: 4px;
      background: rgba(0, 0, 0, 0.35);
      color: #e8fbff;
      font-size: 14px;
      line-height: 1.3;
    }}
    .pl-expense-label-edit-modal__input:focus {{
      outline: 2px solid rgba(88, 225, 243, 0.55);
      outline-offset: 1px;
    }}
    body.office-mode .pl-expense-label-edit-modal__field-label {{
      color: #444;
    }}
    body.office-mode .pl-expense-label-edit-modal__input {{
      border-color: #999;
      background: #fff;
      color: #111;
      font-family: 'BIZ UDP Gothic', sans-serif;
    }}
    .pl-expense-adj-modal__hint {{
      margin: 0 0 14px;
      font-size: 12px;
      line-height: 1.45;
      color: rgba(210, 245, 255, 0.78);
    }}
    .pl-expense-adj-modal__rows {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin: 0 0 16px;
    }}
    .pl-expense-adj-modal__row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}
    .pl-expense-adj-modal__label {{
      font-size: 12px;
      font-weight: 600;
      color: rgba(88, 225, 243, 0.88);
      flex: 0 0 auto;
    }}
    .pl-expense-adj-modal__value {{
      font-size: 14px;
      color: #e8fbff;
      text-align: right;
    }}
    .pl-expense-adj-modal__row--result .pl-expense-adj-modal__value {{
      font-weight: 700;
      color: #58e1f3;
    }}
    .pl-expense-adj-modal__input {{
      width: 140px;
      box-sizing: border-box;
      padding: 8px 10px;
      border: 1px solid rgba(88, 225, 243, 0.45);
      border-radius: 4px;
      background: rgba(0, 0, 0, 0.35);
      color: #e8fbff;
      font-size: 14px;
      text-align: right;
    }}
    .pl-expense-adj-modal__input:focus {{
      outline: 2px solid rgba(88, 225, 243, 0.55);
      outline-offset: 1px;
    }}
    body.office-mode .pl-expense-adj-modal__hint {{
      color: #555;
    }}
    body.office-mode .pl-expense-adj-modal__label {{
      color: #444;
    }}
    body.office-mode .pl-expense-adj-modal__value {{
      color: #111;
    }}
    body.office-mode .pl-expense-adj-modal__row--result .pl-expense-adj-modal__value {{
      color: #0a5;
    }}
    body.office-mode .pl-expense-adj-modal__input {{
      border-color: #999;
      background: #fff;
      color: #111;
      font-family: 'BIZ UDP Gothic', sans-serif;
    }}
    .pl-graph-block {{
      width: 100%;
      flex-shrink: 0;
    }}
    .pl-table--labels-graph.pl-table--v1,
    .pl-table--data-graph.pl-table--v1 {{
      border-top: none;
    }}
    .pl-graph-label-row > th.pl-graph-band-label {{
      height: var(--pl-graph-cell-h);
      min-height: var(--pl-graph-cell-h);
      max-height: var(--pl-graph-cell-h);
      padding: 8px 10px 0 8px;
      vertical-align: top;
      text-align: right;
      font-size: 15px;
      font-weight: 700;
      color: #58e1f3;
      box-sizing: border-box;
    }}
    html[lang='ja'] .pl-graph-label-row > th.pl-graph-band-label {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-graph-data-row > td {{
      height: var(--pl-graph-cell-h);
      min-height: var(--pl-graph-cell-h);
      max-height: var(--pl-graph-cell-h);
      padding: 0;
      vertical-align: top;
    }}
    .pl-graph-cell {{
      width: var(--pl-month-head-w);
      min-width: var(--pl-month-head-w);
      max-width: var(--pl-month-head-w);
      box-sizing: border-box;
      border-left: none;
      background: #1f1e1e;
    }}
    .pl-graph-month {{
      display: flex;
      flex-direction: column;
      width: 100%;
      height: var(--pl-graph-cell-h);
      box-sizing: border-box;
      padding: 8px 4px 6px;
    }}
    .pl-graph-month__head {{
      flex: 0 0 auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      gap: 4px;
      min-height: calc(var(--pl-graph-cell-h) - var(--pl-graph-bar-h) - 14px);
      padding-bottom: 8px;
      text-align: center;
      color: #58e1f3;
      font-size: 12px;
      line-height: 1.25;
    }}
    html[lang='ja'] .pl-graph-month__head {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-graph-month__name {{
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.02em;
    }}
    .pl-graph-month__sales {{
      display: flex;
      flex-direction: column;
      gap: 2px;
      font-size: 11px;
      font-weight: 400;
    }}
    .pl-graph-month__sales-amt {{
      font-size: 12px;
      font-weight: 600;
    }}
    .pl-graph-month__stage {{
      position: relative;
      display: flex;
      align-items: flex-end;
      justify-content: center;
      gap: 4px;
      height: var(--pl-graph-bar-h);
      flex: 0 0 var(--pl-graph-bar-h);
    }}
    .pl-graph-month__aside {{
      position: relative;
      flex: 1 1 0;
      min-width: 0;
      height: var(--pl-graph-bar-h);
    }}
    .pl-graph-month__bars-wrap {{
      flex: 0 0 var(--pl-graph-bar-w);
      width: var(--pl-graph-bar-w);
      height: var(--pl-graph-bar-h);
    }}
    .pl-graph-unified {{
      display: flex;
      flex-direction: column;
      width: var(--pl-graph-bar-w);
      height: var(--pl-graph-bar-h);
      flex-shrink: 0;
    }}
    .pl-graph-unified--deficit {{
      flex-direction: row;
      align-items: stretch;
    }}
    .pl-graph-unified__income {{
      width: 100%;
      flex-shrink: 0;
    }}
    .pl-graph-unified__split-row {{
      display: flex;
      flex-direction: row;
      align-items: stretch;
      width: 100%;
      flex-shrink: 0;
    }}
    .pl-graph-unified__half {{
      width: var(--pl-graph-half-w);
      min-width: var(--pl-graph-half-w);
      max-width: var(--pl-graph-half-w);
      flex-shrink: 0;
    }}
    .pl-graph-unified__half--expense {{
      height: 100%;
    }}
    .pl-graph-unified__half--expense .pl-graph-bar--red {{
      width: 100%;
      height: 100%;
    }}
    .pl-graph-unified__stack {{
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      height: 100%;
    }}
    .pl-graph-unified__stack .pl-graph-bar {{
      width: 100%;
    }}
    .pl-graph-unified--deficit .pl-graph-unified__stack {{
      height: var(--pl-graph-bar-h);
    }}
    .pl-graph-unified__expense-host {{
      position: relative;
      height: var(--pl-graph-bar-h);
    }}
    .pl-graph-unified__expense-fill {{
      position: absolute;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
    }}
    .pl-graph-unified__income-inner {{
      position: absolute;
      left: 0;
      bottom: 0;
      width: 100%;
    }}
    .pl-graph-bar {{
      flex-shrink: 0;
      border-radius: 1px;
      box-sizing: border-box;
    }}
    .pl-graph-bar--green {{
      background: #3cb878;
    }}
    .pl-graph-bar--red {{
      background: #d64545;
    }}
    .pl-graph-bar--yellow {{
      background: #e8c547;
    }}
    .pl-graph-bar--orange {{
      background: #e8883a;
    }}
    .pl-graph-legend {{
      position: absolute;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 1px;
      width: max-content;
      max-width: calc(100% - var(--pl-graph-legend-inset));
      padding: 0;
      box-sizing: border-box;
      font-size: 9px;
      line-height: 1.15;
      text-align: center;
      color: #58e1f3;
      pointer-events: none;
    }}
    .pl-graph-month__aside--left .pl-graph-legend {{
      right: var(--pl-graph-legend-inset);
      left: auto;
    }}
    .pl-graph-month__aside--right .pl-graph-legend {{
      left: var(--pl-graph-legend-inset);
      right: auto;
    }}
    .pl-graph-legend__label {{
      font-size: 10px;
      font-weight: 600;
      letter-spacing: 0.02em;
    }}
    .pl-graph-legend__amt {{
      font-size: 9px;
      font-weight: 400;
      white-space: nowrap;
    }}
    .pl-graph-legend__pct {{
      font-size: 9px;
      font-weight: 600;
    }}
    html[lang='ja'] .pl-graph-legend {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    body.office-mode .pl-graph-cell,
    body.office-mode .pl-graph-label-row > th.pl-graph-band-label {{
      background: #fff;
      color: #111;
    }}
    body.office-mode .pl-graph-month__head,
    body.office-mode .pl-graph-legend {{
      color: #111;
      font-family: 'BIZ UDP Gothic', sans-serif;
    }}
    .pl-analyze-zone.pl-data-row > th,
    .pl-analyze-zone.pl-data-row > td,
    .pl-table--labels-analyze .pl-v-major--analyze,
    .pl-table--labels-analyze .pl-h-label {{
      background: var(--pl-analyze-bg);
    }}
    .pl-month-cell--analyze,
    .pl-amt-cell--analyze,
    .pl-ratio-cell--analyze {{
      background: var(--pl-analyze-bg);
    }}
    .pl-v-major--analyze {{
      position: relative;
      overflow: visible;
      padding: 0;
    }}
    .pl-v-major--analyze.pl-v-major--r3 {{
      height: calc(var(--pl-row-label-h) * 3);
      min-height: calc(var(--pl-row-label-h) * 3);
      max-height: calc(var(--pl-row-label-h) * 3);
    }}
    .pl-v-major--analyze.pl-v-major--r4 {{
      height: calc(var(--pl-row-label-h) * 4);
      min-height: calc(var(--pl-row-label-h) * 4);
      max-height: calc(var(--pl-row-label-h) * 4);
    }}
    body.office-mode .pl-analyze-band {{
      background: rgba(88, 225, 243, 0.18);
      color: #111;
    }}
    body.office-mode .pl-analyze-band__text {{
      color: #111;
      font-family: 'BIZ UDP Gothic', sans-serif;
    }}
    body.office-mode .pl-analyze-toggle {{
      color: #111;
    }}
    body.office-mode .pl-analyze-zone.pl-data-row > th,
    body.office-mode .pl-analyze-zone.pl-data-row > td,
    body.office-mode .pl-table--labels-analyze .pl-v-major--analyze,
    body.office-mode .pl-table--labels-analyze .pl-h-label,
    body.office-mode .pl-month-cell--analyze,
    body.office-mode .pl-amt-cell--analyze,
    body.office-mode .pl-ratio-cell--analyze {{
      background: rgba(88, 225, 243, 0.18);
    }}
    .pl-table.pl-table--v1 {{
      border-collapse: collapse;
      border-spacing: 0;
      table-layout: fixed;
      border-top: var(--pl-cell-border);
      border-bottom: var(--pl-cell-border);
      margin: 0;
      border-radius: 0;
      font-family: 'Orbitron', sans-serif;
    }}
    .pl-table--v1 thead tr {{
      height: var(--pl-month-head-h);
    }}
    .pl-table--v1 tbody tr {{
      height: var(--pl-row-label-h);
    }}
    .pl-table.pl-table--labels {{
      width: var(--pl-label-band-w);
    }}
    .pl-table.pl-table--data {{
      width: max-content;
      min-width: 100%;
    }}
    .pl-table--v1 .pl-col-v-major {{
      width: var(--pl-v-major-w);
    }}
    .pl-table--v1 .pl-col-v-mid {{
      width: var(--pl-v-mid-w);
    }}
    .pl-table--v1 .pl-col-h-label {{
      width: var(--pl-h-label-w);
    }}
    .pl-table--v1 .pl-col-h-label-detail {{
      width: var(--pl-h-label-detail-w);
    }}
    .pl-table--v1 .pl-col-amt {{
      width: var(--pl-sub-amt-w);
    }}
    .pl-table--v1 .pl-col-ratio {{
      width: var(--pl-sub-ratio-w);
    }}
    .pl-table--v1 .pl-month-head--year,
    .pl-table--v1 .pl-sub-amt--year,
    .pl-table--v1 .pl-sub-ratio--year,
    .pl-table--v1 .pl-amt-cell--year-total,
    .pl-table--v1 .pl-ratio-cell--year-total,
    .pl-table--v1 .pl-month-cell--year-total,
    .pl-table--v1 .pl-bizdays-val--year {{
      border-left: 2px solid rgba(88, 225, 243, 0.55);
    }}
    .pl-table--v1 th,
    .pl-table--v1 td {{
      border: none;
      border-right: var(--pl-cell-border);
      border-bottom: var(--pl-cell-border);
      padding: 0;
      margin: 0;
      box-sizing: border-box;
      color: #58e1f3;
      background: #1f1e1e;
      height: inherit;
      overflow: hidden;
    }}
    .pl-table--labels .pl-label-corner,
    .pl-table--labels .pl-row-label,
    .pl-table--labels .pl-v-major,
    .pl-table--labels .pl-v-mid,
    .pl-table--labels .pl-h-label {{
      border-left: none;
      border-right: none;
      background: #1f1e1e;
    }}
    .pl-table--labels .pl-v-mid {{
      border-right: var(--pl-cell-border);
      overflow: visible;
    }}
    .pl-table--labels .pl-v-major {{
      border-right: var(--pl-cell-border);
      overflow: visible;
    }}
    .pl-table--data th,
    .pl-table--data td {{
      border-left: none;
    }}
    .pl-table--data tr > th:first-child,
    .pl-table--data tr > td:first-child {{
      border-left: none;
    }}
    .pl-table--v1 .pl-v-major {{
      width: var(--pl-v-major-w);
      min-width: var(--pl-v-major-w);
      max-width: var(--pl-v-major-w);
      padding: 0;
      vertical-align: middle;
      text-align: center;
    }}
    .pl-table--v1 .pl-v-major__text {{
      display: inline-block;
      margin: 0;
      white-space: nowrap;
      transform: rotate(-90deg);
      transform-origin: center center;
      font-size: 13px;
      font-weight: 400;
      line-height: 1;
      letter-spacing: 0.04em;
      color: #58e1f3;
      text-align: center;
    }}
    html[lang='ja'] .pl-table--v1 .pl-v-major__text {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-table--v1 .pl-v-major--expenses {{
      position: relative;
      overflow: visible;
      height: calc(var(--pl-row-label-h) * 3);
      min-height: calc(var(--pl-row-label-h) * 3);
      max-height: calc(var(--pl-row-label-h) * 3);
      padding: 0;
    }}
    .pl-table--v1 .pl-v-major__text--multiline {{
      position: absolute;
      left: 50%;
      top: 50%;
      display: inline-flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 2px;
      margin: 0;
      line-height: 1;
      text-align: center;
      white-space: nowrap;
      transform: translate(-50%, -50%) rotate(-90deg);
      transform-origin: center center;
    }}
    .pl-table--v1 .pl-v-major__line {{
      display: block;
      font-size: 13px;
      font-weight: 400;
      letter-spacing: 0.04em;
      color: inherit;
      line-height: 1;
    }}
    html[lang='ja'] .pl-table--v1 .pl-v-major__line {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-table--v1 .pl-h-label {{
      width: var(--pl-h-label-w);
      min-width: var(--pl-h-label-w);
      max-width: var(--pl-h-label-w);
      height: var(--pl-row-label-h);
      min-height: var(--pl-row-label-h);
      max-height: var(--pl-row-label-h);
      padding: 0 10px 0 8px;
      vertical-align: middle;
      text-align: right;
      font-weight: 400;
      overflow-x: auto;
      overflow-y: hidden;
      -webkit-overflow-scrolling: touch;
    }}
    .pl-table--v1 .pl-h-label__text {{
      font-size: 13px;
      line-height: 1.2;
      letter-spacing: 0.02em;
      color: #58e1f3;
      white-space: nowrap;
    }}
    html[lang='ja'] .pl-table--v1 .pl-h-label__text {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-table--v1 .pl-h-label--total .pl-h-label__text {{
      font-size: 15px;
      font-weight: 700;
    }}
    .pl-table--v1 .pl-h-label__text--editable {{
      cursor: text;
      border-bottom: 1px dashed transparent;
      box-sizing: border-box;
    }}
    .pl-table--v1 .pl-h-label__text--editable:hover {{
      border-bottom-color: rgba(88, 225, 243, 0.45);
    }}
    .pl-table--v1 .pl-h-label__text--editable:focus {{
      outline: 1px solid rgba(88, 225, 243, 0.55);
      outline-offset: 1px;
    }}
    .pl-table--v1 .pl-h-label__text--editable.pl-h-label__text--editing {{
      border-bottom-color: #58e1f3;
      background: rgba(88, 225, 243, 0.1);
      outline: none;
    }}
    body.office-mode .pl-table--v1 .pl-h-label__text--editable:hover {{
      border-bottom-color: rgba(0, 0, 0, 0.35);
    }}
    body.office-mode .pl-table--v1 .pl-h-label__text--editable.pl-h-label__text--editing {{
      background: rgba(0, 0, 0, 0.06);
      border-bottom-color: #333;
    }}
    .pl-table--v1 .pl-h-label__row {{
      display: inline-flex;
      align-items: center;
      justify-content: flex-end;
      gap: 6px;
      min-width: min-content;
      height: var(--pl-row-label-h);
      box-sizing: border-box;
    }}
    .pl-table--v1 .pl-label-corner {{
      position: relative;
      width: var(--pl-label-band-w);
      min-width: var(--pl-label-band-w);
      max-width: var(--pl-label-band-w);
      height: var(--pl-corner-h);
      min-height: var(--pl-corner-h);
      max-height: var(--pl-corner-h);
      padding: 0;
      vertical-align: middle;
      text-align: center;
    }}
    .pl-table--v1 .pl-guide-toggle {{
      position: absolute;
      right: 6px;
      bottom: 6px;
      width: 20px;
      height: 20px;
      padding: 0;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 1px solid rgba(88, 225, 243, 0.45);
      border-radius: 3px;
      background: rgba(88, 225, 243, 0.08);
      color: #58e1f3;
      font-size: 15px;
      font-weight: 600;
      line-height: 1;
      cursor: pointer;
      transition: background-color 0.15s ease, border-color 0.15s ease;
    }}
    .pl-table--v1 .pl-guide-toggle:hover {{
      background: rgba(88, 225, 243, 0.2);
      border-color: rgba(88, 225, 243, 0.8);
    }}
    .pl-table--v1 .pl-guide-toggle[aria-pressed="true"] {{
      background: rgba(88, 225, 243, 0.85);
      border-color: rgba(88, 225, 243, 0.95);
      color: #0c1b1f;
    }}
    body.office-mode .pl-table--v1 .pl-guide-toggle {{
      border-color: rgba(37, 99, 235, 0.5);
      background: rgba(37, 99, 235, 0.08);
      color: #2563eb;
    }}
    body.office-mode .pl-table--v1 .pl-guide-toggle[aria-pressed="true"] {{
      background: #2563eb;
      border-color: #2563eb;
      color: #ffffff;
    }}
    /* 目安トグルのツールチップは body 直下の固定要素で描画（セルの overflow:hidden 回避） */
    .pl-guide-tip-pop {{
      position: fixed;
      z-index: 13000;
      max-width: min(300px, 80vw);
      padding: 9px 11px;
      border: 1px solid rgba(88, 225, 243, 0.85);
      border-radius: 4px;
      background: #102932;
      color: #58e1f3;
      font-size: 12px;
      font-weight: 400;
      line-height: 1.55;
      letter-spacing: 0.01em;
      text-align: left;
      white-space: normal;
      pointer-events: none;
      opacity: 0;
      transform: translateY(-4px);
      transition: opacity 0.12s ease, transform 0.12s ease;
      box-shadow: 0 8px 22px rgba(0, 0, 0, 0.5);
    }}
    .pl-guide-tip-pop.is-visible {{
      opacity: 1;
      transform: translateY(0);
    }}
    html[lang='ja'] .pl-guide-tip-pop {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    body.office-mode .pl-guide-tip-pop {{
      background: #ffffff;
      border-color: #2563eb;
      color: #1e293b;
      box-shadow: 0 8px 22px rgba(15, 23, 42, 0.22);
    }}
    .pl-table--labels thead {{
      height: var(--pl-corner-h);
    }}
    .pl-table--labels thead tr {{
      height: calc(var(--pl-corner-h) / 2);
      max-height: calc(var(--pl-corner-h) / 2);
    }}
    .pl-table--v1 .pl-label-corner__text {{
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: var(--pl-corner-h);
      margin: 0;
      font-size: 21px;
      font-weight: 600;
      line-height: 1.2;
      letter-spacing: 0.02em;
      color: #58e1f3;
      text-align: center;
    }}
    html[lang='ja'] .pl-table--v1 .pl-label-corner__text {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-table--v1 .pl-month-head {{
      width: var(--pl-month-head-w);
      min-width: var(--pl-month-head-w);
      max-width: var(--pl-month-head-w);
      height: var(--pl-month-head-h);
      min-height: var(--pl-month-head-h);
      max-height: var(--pl-month-head-h);
      padding: 0;
      vertical-align: middle;
      text-align: center;
      font-size: 13px;
      font-weight: 400;
      line-height: 1.2;
      letter-spacing: 0.02em;
      white-space: nowrap;
      background: #1f1e1e;
    }}
    .pl-table--v1 .pl-month-head__text {{
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: var(--pl-month-head-h);
      margin: 0;
      font-size: 13px;
      font-weight: inherit;
      line-height: 1.2;
      letter-spacing: inherit;
      color: #58e1f3;
      text-align: center;
    }}
    html[lang='ja'] .pl-table--v1 .pl-month-head__text {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-table--v1 .pl-head-sub {{
      height: var(--pl-month-head-h);
    }}
    .pl-table--labels .pl-head-sub--label-gap {{
      height: var(--pl-month-head-h);
      min-height: var(--pl-month-head-h);
    }}
    .pl-table--v1 .pl-sub-amt,
    .pl-table--v1 .pl-sub-ratio {{
      padding: 0;
      vertical-align: middle;
      text-align: center;
      font-size: 13px;
      font-weight: 400;
      line-height: 1.2;
      letter-spacing: 0.02em;
      white-space: nowrap;
      background: #1f1e1e;
    }}
    .pl-table--v1 .pl-sub-amt {{
      width: var(--pl-sub-amt-w);
      min-width: var(--pl-sub-amt-w);
      max-width: var(--pl-sub-amt-w);
      height: var(--pl-month-head-h);
      min-height: var(--pl-month-head-h);
      max-height: var(--pl-month-head-h);
    }}
    .pl-table--v1 .pl-sub-ratio {{
      width: var(--pl-sub-ratio-w);
      min-width: var(--pl-sub-ratio-w);
      max-width: var(--pl-sub-ratio-w);
      height: var(--pl-month-head-h);
      min-height: var(--pl-month-head-h);
      max-height: var(--pl-month-head-h);
    }}
    .pl-table--v1 .pl-sub-amt__text,
    .pl-table--v1 .pl-sub-ratio__text {{
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: var(--pl-month-head-h);
      margin: 0;
      font-size: 13px;
      font-weight: inherit;
      line-height: 1.2;
      letter-spacing: inherit;
      color: #58e1f3;
      text-align: center;
    }}
    html[lang='ja'] .pl-table--v1 .pl-sub-amt__text,
    html[lang='ja'] .pl-table--v1 .pl-sub-ratio__text {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-table--v1 .pl-row-label {{
      width: var(--pl-label-band-w);
      min-width: var(--pl-label-band-w);
      max-width: var(--pl-label-band-w);
      height: var(--pl-row-label-h);
      min-height: var(--pl-row-label-h);
      max-height: var(--pl-row-label-h);
      padding: 0 10px 0 8px;
      vertical-align: middle;
      text-align: right;
      overflow-x: auto;
      overflow-y: hidden;
      -webkit-overflow-scrolling: touch;
    }}
    .pl-table--v1 .pl-row-label__text {{
      display: flex;
      align-items: center;
      justify-content: flex-end;
      width: max-content;
      min-width: 100%;
      height: var(--pl-row-label-h);
      white-space: nowrap;
      margin: 0;
      font-size: 13px;
      font-weight: 400;
      line-height: 1.2;
      letter-spacing: 0.02em;
      color: #58e1f3;
      text-align: center;
    }}
    html[lang='ja'] .pl-table--v1 .pl-row-label__text {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-table--v1 .pl-month-cell {{
      width: var(--pl-month-head-w);
      min-width: var(--pl-month-head-w);
      max-width: var(--pl-month-head-w);
      height: var(--pl-row-label-h);
      min-height: var(--pl-row-label-h);
      max-height: var(--pl-row-label-h);
      padding: 0;
      vertical-align: middle;
      text-align: center;
      background: #1f1e1e;
    }}
    .pl-table--v1 .pl-month-cell__text {{
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: var(--pl-row-label-h);
      margin: 0;
      font-size: 13px;
      font-weight: 400;
      line-height: 1.2;
      letter-spacing: 0.02em;
      color: #58e1f3;
      text-align: center;
    }}
    html[lang='ja'] .pl-table--v1 .pl-month-cell__text {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-table--v1 .pl-data-row--total .pl-month-cell__text,
    .pl-table--v1 .pl-data-row--total .pl-amt-cell__text {{
      font-size: 15px;
      font-weight: 700;
    }}
    .pl-table--v1 .pl-amt-cell--income-store .pl-amt-cell__text,
    .pl-table--v1 .pl-amt-cell--income-stream .pl-amt-cell__text,
    .pl-table--v1 .pl-amt-cell--income-total .pl-amt-cell__text {{
      cursor: default;
    }}
    .pl-table--v1 .pl-data-row--ref-budget > th,
    .pl-table--v1 .pl-data-row--ref-budget > td {{
      background: rgba(88, 225, 243, 0.06) !important;
    }}
    .pl-table--v1 .pl-h-label--ref-budget .pl-h-label__text {{
      font-size: 12px;
      font-weight: 600;
      color: rgba(196, 246, 252, 0.88);
      opacity: 0.92;
    }}
    .pl-table--v1 .pl-amt-cell--ref-budget .pl-amt-cell__text,
    .pl-table--v1 .pl-ratio-cell--ref-budget .pl-ratio-cell__text {{
      color: rgba(180, 235, 245, 0.82);
      cursor: default;
      font-size: 12px;
    }}
    body.office-mode .pl-table--v1 .pl-data-row--ref-budget > th,
    body.office-mode .pl-table--v1 .pl-data-row--ref-budget > td {{
      background: rgba(200, 230, 220, 0.28) !important;
    }}
    body.office-mode .pl-table--v1 .pl-h-label--ref-budget .pl-h-label__text,
    body.office-mode .pl-table--v1 .pl-amt-cell--ref-budget .pl-amt-cell__text,
    body.office-mode .pl-table--v1 .pl-ratio-cell--ref-budget .pl-ratio-cell__text {{
      color: #2a5a4a;
    }}
    .pl-table--v1 .pl-amt-cell--expense-detail {{
      position: relative;
    }}
    /* 費目別参考予算(L2)は既定で非表示。コーナーの +/- で一括表示。
       行高の拡張は「目安が1つでも出せた時」だけ（データ皆無なら行高そのまま） */
    body.pl-guide-on.pl-guide-has-data .pl-table--labels-expense-detail,
    body.pl-guide-on.pl-guide-has-data .pl-table--data-expense-detail {{
      --pl-row-label-h: 52px;
    }}
    .pl-table--v1 .pl-amt-cell__l2 {{
      display: none;
      position: absolute;
      left: 2px;
      right: 2px;
      bottom: 3px;
      margin: 0;
      padding: 0;
      font-size: 9px;
      line-height: 1;
      letter-spacing: 0.01em;
      color: rgba(88, 225, 243, 0.72);
      text-align: center;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      pointer-events: none;
    }}
    body.pl-guide-on .pl-table--v1 .pl-amt-cell--has-l2 .pl-amt-cell__text {{
      padding-bottom: 12px;
      box-sizing: border-box;
    }}
    body.pl-guide-on .pl-table--v1 .pl-amt-cell--has-l2 .pl-amt-cell__l2 {{
      display: block;
    }}
    html[lang='ja'] .pl-table--v1 .pl-amt-cell__l2 {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    body.pl-guide-on .pl-table--v1 .pl-amt-cell--over-l2 {{
      box-shadow: inset 0 0 0 1px rgba(240, 160, 120, 0.85);
    }}
    body.pl-guide-on .pl-table--v1 .pl-amt-cell--over-l2 .pl-amt-cell__l2 {{
      color: rgba(240, 176, 128, 0.95);
    }}
    body.office-mode .pl-table--v1 .pl-amt-cell__l2 {{
      color: rgba(71, 85, 105, 0.9);
    }}
    body.office-mode.pl-guide-on .pl-table--v1 .pl-amt-cell--over-l2 {{
      box-shadow: inset 0 0 0 1px rgba(180, 83, 9, 0.7);
    }}
    body.office-mode.pl-guide-on .pl-table--v1 .pl-amt-cell--over-l2 .pl-amt-cell__l2 {{
      color: #b45309;
    }}
    .pl-table--v1 .pl-amt-cell,
    .pl-table--v1 .pl-ratio-cell {{
      padding: 0;
      vertical-align: middle;
      text-align: center;
      background: #1f1e1e;
    }}
    .pl-table--v1 .pl-amt-cell {{
      width: var(--pl-sub-amt-w);
      min-width: var(--pl-sub-amt-w);
      max-width: var(--pl-sub-amt-w);
      height: var(--pl-row-label-h);
      min-height: var(--pl-row-label-h);
      max-height: var(--pl-row-label-h);
    }}
    .pl-table--v1 .pl-ratio-cell {{
      width: var(--pl-sub-ratio-w);
      min-width: var(--pl-sub-ratio-w);
      max-width: var(--pl-sub-ratio-w);
      height: var(--pl-row-label-h);
      min-height: var(--pl-row-label-h);
      max-height: var(--pl-row-label-h);
    }}
    .pl-table--v1 .pl-amt-cell__text {{
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: var(--pl-row-label-h);
      margin: 0;
      font-size: 13px;
      font-weight: 400;
      line-height: 1.2;
      letter-spacing: 0.02em;
      color: #58e1f3;
      text-align: center;
    }}
    .pl-table--v1 .pl-amt-cell__text[data-pl-editable="1"] {{
      cursor: text;
      outline: none;
    }}
    .pl-table--v1 .pl-amt-cell__text[data-pl-editable="1"]:focus {{
      box-shadow: inset 0 0 0 1px rgba(88, 225, 243, 0.85);
      background-color: #152a32;
    }}
    .pl-table--v1 .pl-amt-cell--pl-daily-readonly .pl-amt-cell__text {{
      color: rgba(88, 225, 243, 0.45);
      cursor: default;
    }}
    html[lang='ja'] .pl-table--v1 .pl-amt-cell__text {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-table--v1 .pl-ratio-cell__text {{
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: var(--pl-row-label-h);
      margin: 0;
      font-size: 13px;
      font-weight: 400;
      line-height: 1.2;
      letter-spacing: 0.02em;
      color: #58e1f3;
      text-align: center;
    }}
    html[lang='ja'] .pl-table--v1 .pl-ratio-cell__text {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    .pl-table--v1 .pl-data-row--total .pl-ratio-cell__text {{
      font-size: 15px;
      font-weight: 700;
    }}
    .pl-table--v1 .pl-span-cell {{
      padding: 0;
      vertical-align: middle;
      text-align: center;
      height: var(--pl-row-label-h);
      min-height: var(--pl-row-label-h);
      background: #1f1e1e;
    }}
    .pl-table--v1 .pl-span-cell__text {{
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: var(--pl-row-label-h);
      margin: 0;
      font-size: 13px;
      font-weight: 400;
      line-height: 1.2;
      letter-spacing: 0.02em;
      color: #58e1f3;
      text-align: center;
    }}
    html[lang='ja'] .pl-table--v1 .pl-span-cell__text {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    body.office-mode .pl-table-window {{
      background: transparent;
      --pl-cell-border-color: #999;
    }}
    body.office-mode .pl-table-zoom-root {{
      background: #f5f5f5;
    }}
    body.office-mode .pl-label-pane {{
      background: #fff;
    }}
    body.office-mode .pl-table--v1 .pl-label-corner,
    body.office-mode .pl-table--v1 .pl-row-label,
    body.office-mode .pl-table--v1 .pl-v-major,
    body.office-mode .pl-table--v1 .pl-h-label {{
      background: #fff;
    }}
    body.office-mode .pl-table--v1 .pl-v-major__text,
    body.office-mode .pl-table--v1 .pl-v-major__line,
    body.office-mode .pl-table--v1 .pl-h-label__text {{
      font-family: 'BIZ UDP Gothic', sans-serif;
      color: #111;
    }}
    body.office-mode .pl-table--v1 th,
    body.office-mode .pl-table--v1 td {{
      background: #fff;
      color: #111;
    }}
    body.office-mode .pl-table--v1 .pl-label-corner__text {{
      font-family: 'BIZ UDP Gothic', sans-serif;
      color: #111;
    }}
    body.office-mode .pl-table--v1 .pl-month-head__text {{
      font-family: 'BIZ UDP Gothic', sans-serif;
      color: #111;
    }}
    body.office-mode .pl-table--v1 .pl-sub-amt__text,
    body.office-mode .pl-table--v1 .pl-sub-ratio__text {{
      font-family: 'BIZ UDP Gothic', sans-serif;
      color: #111;
    }}
    body.office-mode .pl-table--v1 .pl-row-label__text {{
      font-family: 'BIZ UDP Gothic', sans-serif;
      color: #111;
    }}
    body.office-mode .pl-table--v1 .pl-amt-cell__text {{
      font-family: 'BIZ UDP Gothic', sans-serif;
      color: #111;
    }}
    body.office-mode .pl-table--v1 .pl-ratio-cell__text {{
      font-family: 'BIZ UDP Gothic', sans-serif;
      color: #111;
    }}
    body.office-mode .pl-table--v1 .pl-month-cell,
    body.office-mode .pl-table--v1 .pl-month-cell__text {{
      background: #fff;
      color: #111;
      font-family: 'BIZ UDP Gothic', sans-serif;
    }}
    body.office-mode .pl-table--v1 .pl-span-cell__text {{
      font-family: 'BIZ UDP Gothic', sans-serif;
      color: #111;
    }}
    .pl-table:not(.pl-table--v1) {{
      border-collapse: separate;
      border-spacing: 0;
      font-size: 12px;
      font-family: 'Orbitron', sans-serif;
      min-width: 2400px;
    }}
    .pl-table:not(.pl-table--v1) th,
    .pl-table:not(.pl-table--v1) td {{
      border: 0.5px solid rgba(88, 225, 243, 0.35);
      padding: 4px 8px;
      white-space: nowrap;
      text-align: right;
      color: #58e1f3;
      font-weight: 400;
      background-color: #0a1418;
    }}
    .pl-table:not(.pl-table--v1) thead th {{
      background-color: #12252b;
    }}
    .pl-label {{
      position: sticky;
      left: 0;
      z-index: 3;
      min-width: 220px;
      max-width: 280px;
      text-align: left !important;
      background-color: #0f1a1e;
      font-weight: 500;
      box-shadow: 1px 0 0 rgba(88, 225, 243, 0.35);
    }}
    th.pl-label.pl-corner {{
      top: 0;
      left: 0;
      z-index: 7;
      vertical-align: bottom;
      font-size: 11px;
      line-height: 1.35;
      background-color: #0f1a1e;
      box-shadow: 1px 0 0 rgba(88, 225, 243, 0.35), 0 1px 0 rgba(88, 225, 243, 0.35);
    }}
    .pl-store-name:empty {{
      display: none;
    }}
    .pl-store-name:not(:empty) {{
      display: block;
      font-weight: 700;
      margin-bottom: 0.2em;
    }}
    .pl-table:not(.pl-table--v1) .pl-head-months th.pl-month {{
      position: sticky;
      top: 0;
      z-index: 5;
      text-align: center;
      background-color: #12252b;
      box-shadow: 0 1px 0 rgba(88, 225, 243, 0.4);
    }}
    .pl-table:not(.pl-table--v1) .pl-head-months th.pl-month.pl-month--total {{
      background-color: #1b3525;
      color: #b8ffb0;
    }}
    .pl-table:not(.pl-table--v1) .pl-head-sub th {{
      position: sticky;
      top: var(--pl-subhead-top, 31px);
      z-index: 5;
      background-color: #12252b;
      font-size: 10px;
      box-shadow: 0 1px 0 rgba(88, 225, 243, 0.4);
    }}
    .pl-table:not(.pl-table--v1) .pl-head-sub th:nth-last-child(-n+2) {{
      background-color: #1b3525;
      color: #b8ffb0;
    }}
    .pl-month--total {{
      color: #b8ffb0;
    }}
    .pl-month--total + .pl-month--total,
    .pl-table:not(.pl-table--v1) tr > td:nth-last-child(-n+2),
    .pl-table:not(.pl-table--v1) tr > th.pl-month--total ~ th {{
      /* annual pair highlighted via sibling cols (legacy table only) */
    }}
    .pl-table:not(.pl-table--v1) tbody tr > td:nth-last-child(-n+2) {{
      background-color: rgba(15, 148, 3, 0.12);
    }}
    .pl-section th {{
      background-color: #152a32;
      text-align: left;
      font-weight: 700;
    }}
    .pl-row-bold .pl-label,
    .pl-row-bold .pl-num,
    .pl-row-bold .pl-pct {{
      font-weight: 700;
    }}
    .pl-negative {{
      color: #ff6b6b !important;
    }}
    .pl-pct {{ opacity: 0.92; min-width: 52px; }}
    .pl-num {{ min-width: 88px; }}
    .pl-group-head .pl-label {{
      background: #152a32;
    }}
    .pl-group-toggle {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: none;
      background: transparent;
      color: inherit;
      font: inherit;
      cursor: pointer;
      padding: 0;
    }}
    .pl-group-head__hint {{
      text-align: left !important;
      font-size: 10px;
      opacity: 0.7;
    }}
    .pl-kpi-row .pl-label--kpi {{
      padding-left: 28px;
    }}
    body.pl-kpi-collapsed .pl-kpi-row {{
      display: none;
    }}
    body.pl-kpi-collapsed .pl-group-toggle__icon {{
      transform: rotate(-90deg);
      display: inline-block;
    }}
    body.office-mode .pl-scroll {{
      background: #f4f4f4;
      border-color: #999;
    }}
    body.office-mode .pl-table th,
    body.office-mode .pl-table td {{
      color: #111;
      border-color: #bbb;
      font-family: 'BIZ UDP Gothic', sans-serif;
      background-color: #fff;
    }}
    body.office-mode .pl-table thead th {{
      background-color: #ddd;
    }}
    body.office-mode .pl-label {{
      background-color: #e8e8e8;
    }}
    body.office-mode th.pl-label.pl-corner {{
      background-color: #e8e8e8;
    }}
    body.office-mode .pl-table:not(.pl-table--v1) .pl-head-months th.pl-month {{
      background-color: #ddd;
    }}
    body.office-mode .pl-table:not(.pl-table--v1) .pl-head-months th.pl-month.pl-month--total,
    body.office-mode .pl-table:not(.pl-table--v1) .pl-head-sub th:nth-last-child(-n+2) {{
      background-color: #d4e8d4;
    }}
    body.office-mode .pl-table:not(.pl-table--v1) .pl-head-sub th {{
      background-color: #ddd;
    }}
    body.office-mode .pl-title {{ color: #111; }}
    body.office-mode .pl-meta {{ color: #444; }}
    body.office-mode .pl-back {{ color: #0a5; }}
    body.office-mode .pl-negative {{ color: #c00 !important; }}
{CLOSE_CHOOSER_CSS}
  </style>
</head>
<body class="si-fi profile-page pl-page" id="body-el">
{header}
  <div class="page-wrap profile-wrap">
    <main class="profile-main">
      <div class="pl-wrap">
        <div class="pl-toolbar" role="toolbar" aria-label="{L['title']}">
          <div class="pl-toolbar__row">
            <div class="pl-toolbar__left">
              <label class="pl-year-label" for="pl-year-select">{L['year_label']}</label>
              <select id="pl-year-select" class="pl-year-select" aria-label="{L['year_aria']}"></select>
              <a class="pl-toolbar__back" id="pl-back-edit" href="{p['monthly_edit']}" hidden data-pl-nav="1" aria-label="{L['back_edit_aria']}">← {L['back_edit']}</a>
              <button type="button" class="pl-toolbar__btn" id="pl-line-manage-open"
                aria-label="{L['line_manage_title']}">{L['line_manage_btn']}</button>
            </div>
            <div class="pl-toolbar__center">
              <button type="button" class="pl-toolbar__btn pl-toolbar__btn--graph" id="pl-graph-open"
                aria-label="{L['toolbar_graph_aria']}">{L['toolbar_graph']}</button>
            </div>
            <div class="pl-toolbar__actions-col">
              <div class="pl-toolbar__actions">
                <button type="button" class="pl-toolbar__btn" id="pl-excel-download"
                  aria-label="{L['download_excel_aria']}">{L['download_excel']}</button>
                <button type="button" class="pl-toolbar__btn" id="pl-csv-upload"
                  aria-label="{L['csv_upload']}"
                  title="{L['csv_upload_tooltip']}"
                  data-tooltip="{L['csv_upload_tooltip']}">{L['csv_upload']}</button>
                <button type="button" class="pl-toolbar__btn" id="pl-undo"
                  aria-label="{L['undo']}" disabled>{L['undo']}</button>
                <button type="button" class="pl-toolbar__btn pl-toolbar__btn--save" id="pl-save">{L['save']}</button>
              </div>
              <div class="pl-toolbar__zoom">
                <div class="pl-toolbar__zoom-controls">
                  <label for="pl-table-zoom">{L['zoom_label']}</label>
                  <button type="button" class="pl-toolbar__zoom-step" id="pl-table-zoom-minus" aria-label="{L['zoom_out_aria']}">−</button>
                  <input type="range" id="pl-table-zoom" min="70" max="150" value="100" aria-valuemin="70" aria-valuemax="150" aria-valuenow="100" />
                  <button type="button" class="pl-toolbar__zoom-step" id="pl-table-zoom-plus" aria-label="{L['zoom_in_aria']}">+</button>
                </div>
                <div class="pl-toolbar__zoom-pct-wrap">
                  <span id="pl-table-zoom-pct" aria-hidden="true">100%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="pl-table-window" id="pl-table-window" role="region" aria-label="{L['title']}">
          <div class="pl-table-zoom-root" id="pl-table-zoom-root">
          <div class="pl-split-seam" aria-hidden="true"></div>
          <div class="pl-table-frozen" id="pl-table-frozen">
            <div class="pl-table-split">
              <div class="pl-label-pane">
                <table class="pl-table pl-table--v1 pl-table--labels pl-table--labels-frozen" id="pl-table-labels-frozen">
                  {label_colgroup}
                  <thead>
                    <tr class="pl-head-months">
                      <th class="pl-label-corner" scope="colgroup" colspan="2" id="pl-label-corner" rowspan="2">
                        <span class="pl-label-corner__text">{corner_title}</span>
                        <button type="button" class="pl-guide-toggle" id="pl-guide-toggle"
                          aria-pressed="false" aria-label="{L['guide_toggle_aria']}"
                          data-tooltip="{L['guide_toggle_tip']}">+</button>
                      </th>
                    </tr>
                    <tr class="pl-head-sub pl-head-sub--label-gap" aria-hidden="true"></tr>
                  </thead>
                  <tbody id="pl-table-label-frozen-body">
                    {bizdays_label}
                  </tbody>
                </table>
              </div>
              <div class="pl-data-pane pl-data-pane--frozen" id="pl-data-pane-frozen">
                <table class="pl-table pl-table--v1 pl-table--data pl-table--data-frozen" id="pl-table-frozen">
                  {data_colgroup}
                  <thead>
                    <tr class="pl-head-months">
                      {month_heads}
                    </tr>
                    <tr class="pl-head-sub">
                      {month_subheads}
                    </tr>
                  </thead>
                  <tbody id="pl-table-frozen-body">
                    {bizdays_data}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div class="pl-table-scroll-y" id="pl-table-scroll-y">
            <div class="pl-table-split">
              <div class="pl-label-pane">
                <table class="pl-table pl-table--v1 pl-table--labels pl-table--labels-body" id="pl-table-labels">
                  {label_colgroup}
                  <tbody id="pl-table-label-body">
                    {income_label_rows}
                    {expenses_label_rows}
                    {ref_budget_label_row}
                  </tbody>
                </table>
              </div>
              <div class="pl-data-pane" id="pl-data-pane">
                <table class="pl-table pl-table--v1 pl-table--data pl-table--data-body" id="pl-table">
                  {data_colgroup}
                  <tbody id="pl-table-body">
                    {income_data_rows}
                    {expenses_data_rows}
                    {ref_budget_data_row}
                  </tbody>
                </table>
              </div>
            </div>
            <div class="pl-analyze-block" id="pl-analyze-block" data-pl-section="analyze">
              <div class="pl-analyze-band" id="pl-analyze-band">
                <button type="button" class="pl-analyze-toggle" id="pl-analyze-toggle"
                  aria-expanded="true" aria-controls="pl-analyze-label-collapsible pl-analyze-data-collapsible"
                  aria-label="{analyze_toggle_aria}">▼</button>
                <span class="pl-analyze-band__text">{analyze_band}</span>
              </div>
              <div class="pl-table-split">
                <div class="pl-label-pane">
                  <table class="pl-table pl-table--v1 pl-table--labels pl-table--labels-analyze"
                    id="pl-table-labels-analyze">
                    {label_colgroup}
                    <tbody id="pl-analyze-label-collapsible" class="pl-analyze-collapsible">
                      {analyze_only_label_rows}
                    </tbody>
                    <tbody id="pl-table-label-profit-body">
                      {profit_label_row}
                    </tbody>
                  </table>
                </div>
                <div class="pl-data-pane pl-data-pane--analyze" id="pl-data-pane-analyze">
                  <table class="pl-table pl-table--v1 pl-table--data pl-table--data-analyze"
                    id="pl-table-analyze">
                    {data_colgroup}
                    <tbody id="pl-analyze-data-collapsible" class="pl-analyze-collapsible">
                      {analyze_only_data_rows}
                    </tbody>
                    <tbody id="pl-table-profit-body">
                      {profit_data_row}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            <div class="pl-expense-detail-block" id="pl-expense-detail-block" data-pl-section="expense-detail">
              <div class="pl-table-split">
                <div class="pl-label-pane">
                  <table class="pl-table pl-table--v1 pl-table--labels pl-table--labels-expense-detail"
                    id="pl-table-labels-expense-detail">
                    {expense_detail_label_colgroup}
                    <tbody id="pl-expense-detail-header-label">
                      {expenses_detail_header_label}
                    </tbody>
                    <tbody id="pl-expense-detail-label-body"></tbody>
                  </table>
                </div>
                <div class="pl-data-pane pl-data-pane--expense-detail" id="pl-data-pane-expense-detail">
                  <table class="pl-table pl-table--v1 pl-table--data pl-table--data-expense-detail"
                    id="pl-table-expense-detail">
                    {data_colgroup}
                    <tbody id="pl-expense-detail-header-data">
                      {expenses_detail_header_data}
                    </tbody>
                    <tbody id="pl-expense-detail-data-body"></tbody>
                  </table>
                </div>
              </div>
            </div>
            <div class="pl-graph-block" id="pl-graph-block" data-pl-section="graph">
              <div class="pl-table-split">
                <div class="pl-label-pane">
                  <table class="pl-table pl-table--v1 pl-table--labels pl-table--labels-graph"
                    id="pl-table-labels-graph">
                    {expense_detail_label_colgroup}
                    <tbody>
                      <tr class="pl-graph-label-row" data-pl-section="graph">
                        <th colspan="2" scope="row" class="pl-graph-band-label">{graph_band}</th>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="pl-data-pane pl-data-pane--graph" id="pl-data-pane-graph">
                  <table class="pl-table pl-table--v1 pl-table--data pl-table--data-graph"
                    id="pl-table-graph">
                    {data_colgroup}
                    <tbody id="pl-graph-data-body"></tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          </div>
        </div>
      </div>
    </main>
  </div>
{input_source_modal_html}
{label_edit_modal_html}
{adj_modal_html}
{expense_attribute_modal_html}
{hide_line_modal_html}
{line_manage_modal_html}
{graph_overlay_html}
  <footer class="site-footer">
    <button class="footer-backtotop" id="footerBackToTop" aria-label="{"ページ先頭へ" if lang == "ja" else "Back to top"}">
      <img src="{p['asset']}images/arrow_up.svg" alt="" class="footer-backtotop__icon" aria-hidden="true">
    </button>
    <div class="footer-separator"></div>
    <div class="footer-logo">
      <a href="{p['forge_url']}" class="logo-link" target="_blank" rel="noopener noreferrer">
        <img src="{p['asset']}images/forge_lab_logo.png" alt="FORGE LABORATORY" class="logo-img">
      </a>
    </div>
    <p class="footer-copy">© 2025 Forge-Laboratory. All rights reserved.</p>
  </footer>

{CLOSE_CHOOSER_HTML[lang]}
  <div class="lang-select-wrap" id="lang-select-wrap" {lang_switch}>
    <button type="button" class="lang-select-btn" id="lang-select-btn" aria-expanded="false" aria-haspopup="listbox" aria-label="{"言語を選択" if lang == "ja" else "Select language"}">
      <span class="lang-code" aria-hidden="true">{"JP" if lang == "ja" else "EN"}</span>
      <span class="lang-name">{"Japanese" if lang == "ja" else "English"}</span>
      <span class="lang-chevron" aria-hidden="true"></span>
    </button>
    <div class="lang-select-dropdown" id="lang-select-dropdown" role="listbox" hidden>
      <button type="button" class="lang-option lang-option-ja" role="option" data-lang="ja">JP - Japanese</button>
      <button type="button" class="lang-option lang-option-en" role="option" data-lang="en">EN - English</button>
    </div>
  </div>

  <script>
    (function () {{
      var STORAGE_KEY = 'kpi-office-mode';
      var bodyEl = document.getElementById('body-el');
      var btnModeToggle = document.getElementById('btn-mode-toggle');
      var btnModeText = document.getElementById('btn-mode-text');
      var settingsOfficeLabel = document.getElementById('settings-office-label');
      function updateModeButton() {{
        if (!btnModeText || !btnModeToggle) return;
        var isOffice = bodyEl && bodyEl.classList.contains('office-mode');
        btnModeText.textContent = isOffice ? 'SCI-FI MODE' : 'OFFICE MODE';
        btnModeToggle.setAttribute('aria-label', isOffice ? '{office_aria_on}' : '{office_aria_off}');
        if (settingsOfficeLabel) settingsOfficeLabel.textContent = isOffice ? 'Sci-Fi Mode' : 'Office Mode';
      }}
      if (bodyEl && btnModeToggle) {{
        if (sessionStorage.getItem(STORAGE_KEY) === '1') bodyEl.classList.add('office-mode');
        btnModeToggle.addEventListener('click', function (e) {{
          e.preventDefault();
          bodyEl.classList.toggle('office-mode');
          if (bodyEl.classList.contains('office-mode')) sessionStorage.setItem(STORAGE_KEY, '1');
          else sessionStorage.removeItem(STORAGE_KEY);
          updateModeButton();
        }});
        updateModeButton();
      }}
    }})();
    (function () {{
      var menuBtn = document.querySelector('.icon-button-menu');
      var dropdown = document.getElementById('settings-dropdown');
      var officeToggle = document.getElementById('settings-office-toggle');
      if (!menuBtn || !dropdown) return;
      menuBtn.addEventListener('click', function (e) {{
        e.stopPropagation();
        dropdown.hidden = !dropdown.hidden;
      }});
      if (officeToggle) {{
        officeToggle.addEventListener('click', function (e) {{
          e.preventDefault();
          e.stopPropagation();
          var modeBtn = document.getElementById('btn-mode-toggle');
          if (modeBtn) modeBtn.click();
        }});
      }}
      dropdown.addEventListener('click', function (e) {{ e.stopPropagation(); }});
      document.addEventListener('click', function () {{ dropdown.hidden = true; }});
    }})();
    (function () {{
      var gearBtn = document.getElementById('btn-account-settings');
      var accountPopup = document.getElementById('account-settings-popup');
      var menuDropdown = document.getElementById('settings-dropdown');
      if (!gearBtn || !accountPopup) return;
      gearBtn.addEventListener('click', function (e) {{
        e.stopPropagation();
        var isOpen = !accountPopup.hidden;
        accountPopup.hidden = isOpen;
        gearBtn.setAttribute('aria-expanded', !isOpen);
        if (!isOpen && menuDropdown) menuDropdown.hidden = true;
      }});
      accountPopup.addEventListener('click', function (e) {{ e.stopPropagation(); }});
      document.addEventListener('click', function () {{
        accountPopup.hidden = true;
        gearBtn.setAttribute('aria-expanded', 'false');
      }});
    }})();
    (function () {{
      var langBtn = document.getElementById('lang-select-btn');
      var langDropdown = document.getElementById('lang-select-dropdown');
      var langOptions = document.querySelectorAll('.lang-option');
      var langWrap = document.getElementById('lang-select-wrap');
      if (!langBtn || !langDropdown || !langWrap) return;
      langBtn.addEventListener('click', function (e) {{
        e.stopPropagation();
        var isOpen = !langDropdown.hidden;
        langDropdown.hidden = isOpen;
        langBtn.setAttribute('aria-expanded', !isOpen);
      }});
      document.addEventListener('click', function () {{
        langDropdown.hidden = true;
        langBtn.setAttribute('aria-expanded', 'false');
      }});
      var urlEn = langWrap.getAttribute('data-url-en');
      var urlJa = langWrap.getAttribute('data-url-ja');
      langOptions.forEach(function (opt) {{
        opt.addEventListener('click', function (e) {{
          e.stopPropagation();
          var bodyEl = document.getElementById('body-el');
          if (bodyEl && bodyEl.classList.contains('office-mode')) sessionStorage.setItem('kpi-office-mode', '1');
          var lang = this.getAttribute('data-lang');
          var href = lang === 'ja' && urlJa ? urlJa : lang === 'en' && urlEn ? urlEn : null;
          if (!href) return;
          var qs = window.location.search;
          if (qs) href += (href.indexOf('?') >= 0 ? '&' : '?') + qs.slice(1);
          if (typeof window.requestLeaveNavigation === 'function') {{
            window.requestLeaveNavigation().then(function (ok) {{
              if (ok) window.location.href = href;
            }});
          }} else {{
            window.location.href = href;
          }}
        }});
      }});
    }})();
    (function () {{
      var backTop = document.getElementById('footerBackToTop');
      if (backTop) backTop.addEventListener('click', function () {{ window.scrollTo({{ top: 0, behavior: 'smooth' }}); }});
    }})();
    (function () {{
      var headMonths = document.querySelector('.pl-head-months');
      function syncPlSubheadTop() {{
        if (!headMonths) return;
        var h = Math.ceil(headMonths.getBoundingClientRect().height);
        document.documentElement.style.setProperty('--pl-subhead-top', h + 'px');
      }}
      window.syncPlSubheadTop = syncPlSubheadTop;
      syncPlSubheadTop();
      window.addEventListener('resize', syncPlSubheadTop);
      if (document.fonts && document.fonts.ready) {{
        document.fonts.ready.then(syncPlSubheadTop);
      }}
    }})();
    (function () {{
      var windowEl = document.getElementById('pl-table-window');
      var zoomRoot = document.getElementById('pl-table-zoom-root');
      var seam = zoomRoot ? zoomRoot.querySelector('.pl-split-seam') : null;
      var frozenPane = document.getElementById('pl-data-pane-frozen');
      var bodyPane = document.getElementById('pl-data-pane');
      var analyzePane = document.getElementById('pl-data-pane-analyze');
      var expenseDetailPane = document.getElementById('pl-data-pane-expense-detail');
      var graphPane = document.getElementById('pl-data-pane-graph');
      var scrollLock = false;
      function syncPlDataScroll(src, dst) {{
        if (!src || !dst || scrollLock) return;
        scrollLock = true;
        dst.scrollLeft = src.scrollLeft;
        scrollLock = false;
      }}
      function syncPlDataScrollAll(src) {{
        if (!src || scrollLock) return;
        scrollLock = true;
        [frozenPane, bodyPane, analyzePane, expenseDetailPane, graphPane].forEach(function (pane) {{
          if (pane && pane !== src) pane.scrollLeft = src.scrollLeft;
        }});
        scrollLock = false;
      }}
      if (frozenPane) {{
        frozenPane.addEventListener('scroll', function () {{ syncPlDataScrollAll(frozenPane); }});
      }}
      if (bodyPane) {{
        bodyPane.addEventListener('scroll', function () {{ syncPlDataScrollAll(bodyPane); }});
      }}
      if (analyzePane) {{
        analyzePane.addEventListener('scroll', function () {{ syncPlDataScrollAll(analyzePane); }});
      }}
      if (expenseDetailPane) {{
        expenseDetailPane.addEventListener('scroll', function () {{ syncPlDataScrollAll(expenseDetailPane); }});
      }}
      if (graphPane) {{
        graphPane.addEventListener('scroll', function () {{ syncPlDataScrollAll(graphPane); }});
      }}
      function rowSyncHeight(row) {{
        return row ? row.offsetHeight || 0 : 0;
      }}

      function syncPlRowPair(labelSel, dataSel) {{
        var labelTable = document.querySelector(labelSel);
        var dataTable = document.querySelector(dataSel);
        if (!labelTable || !dataTable) return;
        var lRows = labelTable.querySelectorAll('tr');
        var dRows = dataTable.querySelectorAll('tr');
        var n = Math.min(lRows.length, dRows.length);
        for (var i = 0; i < n; i++) {{
          lRows[i].style.height = '';
          dRows[i].style.height = '';
        }}
        for (var j = 0; j < n; j++) {{
          var h = Math.max(rowSyncHeight(lRows[j]), rowSyncHeight(dRows[j]));
          if (h > 0) {{
            var px = Math.ceil(h) + 'px';
            lRows[j].style.height = px;
            dRows[j].style.height = px;
          }}
        }}
      }}
      function syncPlSplitLayout() {{
        syncPlRowPair('.pl-table--labels-frozen', '.pl-table--data-frozen');
        syncPlRowPair('.pl-table--labels-body', '.pl-table--data-body');
        syncPlRowPair('.pl-table--labels-analyze', '.pl-table--data-analyze');
        syncPlRowPair('.pl-table--labels-expense-detail', '.pl-table--data-expense-detail');
        syncPlRowPair('.pl-table--labels-graph', '.pl-table--data-graph');
        if (seam && zoomRoot) {{
          seam.style.height = zoomRoot.offsetHeight + 'px';
        }}
      }}
      syncPlSplitLayout();
      window.addEventListener('resize', syncPlSplitLayout);
      if (document.fonts && document.fonts.ready) {{
        document.fonts.ready.then(syncPlSplitLayout);
      }}
      if (typeof ResizeObserver !== 'undefined' && zoomRoot) {{
        var ro = new ResizeObserver(syncPlSplitLayout);
        ro.observe(zoomRoot);
        ['.pl-table--labels-frozen', '.pl-table--data-frozen', '.pl-table--labels-body', '.pl-table--data-body', '.pl-table--labels-analyze', '.pl-table--data-analyze', '.pl-table--labels-expense-detail', '.pl-table--data-expense-detail', '.pl-table--labels-graph', '.pl-table--data-graph'].forEach(function (sel) {{
          var el = document.querySelector(sel);
          if (el) ro.observe(el);
        }});
      }}
      window.addEventListener('pl-expense-detail-rendered', syncPlSplitLayout);
      window.addEventListener('pl-graph-rendered', syncPlSplitLayout);

      /* 費目別参考予算(L2)の +/- トグル: 一括表示・行高の拡張/縮小 */
      var PL_GUIDE_KEY = 'kpiNavigator.plGuideOn';
      var plGuideToggle = document.getElementById('pl-guide-toggle');
      var plGuideTipShow = {json.dumps(L["guide_toggle_tip"], ensure_ascii=False)};
      var plGuideTipHide = {json.dumps(L["guide_toggle_tip_on"], ensure_ascii=False)};
      var plGuideTipNoData = {json.dumps(L["guide_toggle_tip_nodata"], ensure_ascii=False)};
      function plGuideIsOn() {{
        try {{ return localStorage.getItem(PL_GUIDE_KEY) === '1'; }} catch (_e) {{ return false; }}
      }}
      function plGuideHasData() {{
        try {{ return document.body.classList.contains('pl-guide-has-data'); }} catch (_e) {{ return false; }}
      }}

      /* body 直下の固定ツールチップ（セルの overflow:hidden に切られない） */
      var plGuideTipEl = null;
      var plGuideTipTimer = null;
      function plGuideTipText() {{
        if (!plGuideIsOn()) return plGuideTipShow;
        return plGuideHasData() ? plGuideTipHide : plGuideTipNoData;
      }}
      function showPlGuideTip(autoHideMs) {{
        if (!plGuideToggle) return;
        if (!plGuideTipEl) {{
          plGuideTipEl = document.createElement('div');
          plGuideTipEl.className = 'pl-guide-tip-pop';
          plGuideTipEl.setAttribute('role', 'tooltip');
          document.body.appendChild(plGuideTipEl);
        }}
        if (plGuideTipTimer) {{ clearTimeout(plGuideTipTimer); plGuideTipTimer = null; }}
        plGuideTipEl.textContent = plGuideTipText();
        plGuideTipEl.style.visibility = 'hidden';
        plGuideTipEl.classList.add('is-visible');
        var r = plGuideToggle.getBoundingClientRect();
        var tw = plGuideTipEl.offsetWidth;
        var th = plGuideTipEl.offsetHeight;
        var vw = document.documentElement.clientWidth;
        var vh = document.documentElement.clientHeight;
        var left = r.left + r.width / 2 - tw / 2;
        left = Math.max(8, Math.min(left, vw - tw - 8));
        var top = r.bottom + 8;
        if (top + th > vh - 8) top = r.top - th - 8;
        plGuideTipEl.style.left = Math.round(left) + 'px';
        plGuideTipEl.style.top = Math.round(top) + 'px';
        plGuideTipEl.style.visibility = 'visible';
        if (autoHideMs && autoHideMs > 0) {{
          plGuideTipTimer = setTimeout(hidePlGuideTip, autoHideMs);
        }}
      }}
      function hidePlGuideTip() {{
        if (plGuideTipTimer) {{ clearTimeout(plGuideTipTimer); plGuideTipTimer = null; }}
        if (plGuideTipEl) plGuideTipEl.classList.remove('is-visible');
      }}

      function applyPlGuideState(on) {{
        document.body.classList.toggle('pl-guide-on', !!on);
        if (plGuideToggle) {{
          plGuideToggle.setAttribute('aria-pressed', on ? 'true' : 'false');
          plGuideToggle.textContent = on ? '\u2212' : '+';
          plGuideToggle.setAttribute('data-tooltip', on ? plGuideTipHide : plGuideTipShow);
        }}
        if (plGuideTipEl && plGuideTipEl.classList.contains('is-visible')) {{
          plGuideTipEl.textContent = plGuideTipText();
        }}
        if (typeof window.__plRefreshReferenceBudget === 'function') {{
          window.__plRefreshReferenceBudget();
        }}
        syncPlSplitLayout();
      }}
      if (plGuideToggle) {{
        plGuideToggle.addEventListener('click', function () {{
          var next = !plGuideIsOn();
          try {{ localStorage.setItem(PL_GUIDE_KEY, next ? '1' : '0'); }} catch (_e) {{}}
          applyPlGuideState(next);
          // ON にしたが目安が1つも出せない（過去データ皆無）→ 案内を少し長めに出す
          showPlGuideTip(next && !plGuideHasData() ? 4500 : 0);
        }});
        plGuideToggle.addEventListener('mouseenter', showPlGuideTip);
        plGuideToggle.addEventListener('mouseleave', hidePlGuideTip);
        plGuideToggle.addEventListener('focus', showPlGuideTip);
        plGuideToggle.addEventListener('blur', hidePlGuideTip);
        window.addEventListener('scroll', hidePlGuideTip, true);
      }}
      applyPlGuideState(plGuideIsOn());

      var zoom = document.getElementById('pl-table-zoom');
      var zoomMinus = document.getElementById('pl-table-zoom-minus');
      var zoomPlus = document.getElementById('pl-table-zoom-plus');
      var zoomPct = document.getElementById('pl-table-zoom-pct');
      var zoomRangeAlert = {json.dumps(L["zoom_range_alert"], ensure_ascii=False)};

      function setZoomValue(next) {{
        if (!zoom) return;
        var min = Number(zoom.min || 70);
        var max = Number(zoom.max || 150);
        var n = Math.round(Number(next));
        if (!Number.isFinite(n)) n = 100;
        n = Math.min(max, Math.max(min, n));
        zoom.value = String(n);
        applyPlTableZoom();
      }}

      function applyPlTableZoom() {{
        if (!zoom || !zoomRoot || !zoomPct) return;
        var v = Number(zoom.value);
        if (!Number.isFinite(v)) v = 100;
        var min = Number(zoom.min || 70);
        var max = Number(zoom.max || 150);
        var z = String(v / 100);
        var factor = v / 100;
        /* 内側 zoom + 外側 height 補正 → 下余白なし・固定ヘッダー維持 */
        zoomRoot.style.zoom = z;
        zoomRoot.style.transform = '';
        if (windowEl) {{
          windowEl.style.setProperty('--pl-zoom-factor', String(factor));
        }}
        zoomPct.textContent = Math.round(v) + '%';
        zoom.setAttribute('aria-valuenow', String(Math.round(v)));
        if (zoomMinus) zoomMinus.disabled = v <= min;
        if (zoomPlus) zoomPlus.disabled = v >= max;
        syncPlSplitLayout();
        if (typeof window.syncPlSubheadTop === 'function') window.syncPlSubheadTop();
      }}

      function bindPlZoomStepButton(btn, sign) {{
        if (!btn || !zoom) return;
        var active = false;
        var repeatTimer = null;
        var repeatCount = 0;
        function stop() {{
          active = false;
          if (repeatTimer) clearTimeout(repeatTimer);
          repeatTimer = null;
          repeatCount = 0;
        }}
        function tick() {{
          if (!active) return;
          var amount = 1;
          if (repeatCount >= 20) amount = 10;
          else if (repeatCount >= 12) amount = 5;
          else if (repeatCount >= 6) amount = 3;
          else if (repeatCount >= 2) amount = 2;
          setZoomValue(Number(zoom.value) + sign * amount);
          repeatCount++;
          var delay = repeatCount >= 20 ? 50 : repeatCount >= 12 ? 70 : repeatCount >= 6 ? 90 : 120;
          repeatTimer = setTimeout(tick, delay);
        }}
        btn.addEventListener('pointerdown', function (ev) {{
          ev.preventDefault();
          if (typeof ev.button === 'number' && ev.button !== 0) return;
          active = true;
          repeatCount = 0;
          try {{
            btn.setPointerCapture(ev.pointerId);
          }} catch (e1) {{}}
          setZoomValue(Number(zoom.value) + sign);
          repeatCount = 1;
          repeatTimer = setTimeout(tick, 400);
        }});
        btn.addEventListener('pointerup', stop);
        btn.addEventListener('pointercancel', stop);
        btn.addEventListener('lostpointercapture', stop);
      }}

      if (zoom) {{
        zoom.addEventListener('input', applyPlTableZoom);
        zoom.addEventListener('change', applyPlTableZoom);
        applyPlTableZoom();
      }}
      bindPlZoomStepButton(zoomMinus, -1);
      bindPlZoomStepButton(zoomPlus, 1);
      if (zoomPct && zoom) {{
        zoomPct.addEventListener('dblclick', function () {{
          var input = document.createElement('input');
          input.type = 'text';
          input.className = 'pl-toolbar__zoom-edit';
          input.value = String(Math.round(Number(zoom.value) || 100));
          zoomPct.replaceWith(input);
          input.focus();
          input.select();
          function commit() {{
            var raw = String(input.value || '').trim().replace(/%/g, '');
            var n = Number(raw);
            if (Number.isFinite(n)) {{
              var min = Number(zoom.min || 70);
              var max = Number(zoom.max || 150);
              if (n >= min && n <= max) {{
                zoom.value = String(Math.round(n));
                applyPlTableZoom();
              }} else {{
                window.alert(
                  zoomRangeAlert.replace('{{min}}', String(min)).replace('{{max}}', String(max))
                );
              }}
            }}
            input.replaceWith(zoomPct);
          }}
          input.addEventListener('blur', commit);
          input.addEventListener('keydown', function (ev) {{
            if (ev.key === 'Enter') commit();
            if (ev.key === 'Escape') input.replaceWith(zoomPct);
          }});
        }});
      }}
      window.applyPlTableZoom = applyPlTableZoom;
    }})();
    {label_edit_js}
    {expense_detail_js}
    {graph_js}
    {compare_js}
    (function () {{
      var analyzeToggle = document.getElementById('pl-analyze-toggle');
      var analyzeCollapsibles = document.querySelectorAll('.pl-analyze-collapsible');
      if (analyzeToggle && analyzeCollapsibles.length) {{
        analyzeToggle.addEventListener('click', function () {{
          var collapsed = !analyzeCollapsibles[0].classList.contains('is-collapsed');
          analyzeCollapsibles.forEach(function (el) {{
            el.classList.toggle('is-collapsed', collapsed);
          }});
          analyzeToggle.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
          analyzeToggle.textContent = collapsed ? '▶' : '▼';
        }});
      }}
    }})();
    (function () {{
      var isJa = document.documentElement.lang === 'ja';
      function t(ja, en) {{ return isJa ? ja : en; }}
      var PL_STORAGE_PREFIX = 'kpi-pl-expenses-v1:';
      var PL_RETURN_KEY = 'kpi-pl-edit-return-href';
      var FALLBACK_EDIT = '{p["monthly_edit"]}';
      var plParams = new URLSearchParams(window.location.search);
      var plYear = Number(plParams.get('year')) || new Date().getFullYear();
      var focusMonth = Number(plParams.get('month'));
      var plTouched = false;
      var plSaved = true;
      var confirmedSnapshot = '';
      var undoStack = [];
      var yearSelect = document.getElementById('pl-year-select');
      var btnSave = document.getElementById('pl-save');
      var btnUndo = document.getElementById('pl-undo');
      var btnCsv = document.getElementById('pl-csv-upload');
      var btnExcel = document.getElementById('pl-excel-download');
      var editBack = document.getElementById('pl-back-edit');
      var body = document.getElementById('body-el');

      function buildMonthlyEditHref(y, m) {{
        if (!y || !m) return FALLBACK_EDIT;
        return (
          FALLBACK_EDIT +
          '?year=' +
          encodeURIComponent(String(y)) +
          '&month=' +
          encodeURIComponent(String(m))
        );
      }}

      function setupEditBackLink() {{
        if (!editBack) return;
        if (plParams.get('from') !== 'monthly-edit') {{
          editBack.hidden = true;
          return;
        }}
        var m = plParams.get('month') || focusMonth;
        editBack.href = buildMonthlyEditHref(plYear, m);
        editBack.hidden = false;
      }}

      function populateYearSelect() {{
        if (!yearSelect) return;
        var now = new Date().getFullYear();
        yearSelect.innerHTML = '';
        for (var y = now - 8; y <= now + 4; y++) {{
          var opt = document.createElement('option');
          opt.value = String(y);
          opt.textContent = isJa ? y + '年' : String(y);
          if (y === plYear) opt.selected = true;
          yearSelect.appendChild(opt);
        }}
      }}

      function storageKey() {{
        return PL_STORAGE_PREFIX + plYear;
      }}

      function parseMoney(text) {{
        var raw = String(text || '').replace(/[^\\d.-]/g, '');
        if (!raw) return 0;
        var n = parseInt(raw, 10);
        return Number.isFinite(n) ? n : 0;
      }}

      function formatMoney(n) {{
        if (isJa) return '¥' + n.toLocaleString('en-US');
        return '$' + n.toLocaleString('en-US');
      }}

      function buildSnapshot() {{
        var cells = document.querySelectorAll('[data-pl-editable="1"]');
        var data = [];
        cells.forEach(function (cell) {{
          data.push([
            cell.getAttribute('data-row'),
            cell.getAttribute('data-month'),
            parseMoney(cell.textContent)
          ]);
        }});
        data.sort(function (a, b) {{
          if (a[0] !== b[0]) return a[0] < b[0] ? -1 : 1;
          return Number(a[1]) - Number(b[1]);
        }});
        return JSON.stringify(data);
      }}

      function hasUnsavedChanges() {{
        return plTouched && buildSnapshot() !== confirmedSnapshot;
      }}

      function syncUndoButton() {{
        if (btnUndo) btnUndo.disabled = undoStack.length === 0;
      }}

      function markTouched() {{
        plTouched = true;
        plSaved = false;
      }}

      function applyColumnFocus() {{
        document.querySelectorAll('.pl-col-focus').forEach(function (el) {{
          el.classList.remove('pl-col-focus');
        }});
        if (!Number.isFinite(focusMonth) || focusMonth < 1 || focusMonth > 12) return;
        var mi = focusMonth - 1;
        document.querySelectorAll('[data-pl-editable="1"][data-month="' + mi + '"]').forEach(function (el) {{
          el.classList.add('pl-col-focus');
        }});
      }}

      function loadSavedExpenses() {{
        try {{
          var raw = localStorage.getItem(storageKey());
          if (!raw) return;
          var map = JSON.parse(raw);
          if (!map || typeof map !== 'object') return;
          document.querySelectorAll('[data-pl-editable="1"]').forEach(function (cell) {{
            var row = cell.getAttribute('data-row');
            var month = cell.getAttribute('data-month');
            var key = row + ':' + month;
            if (Object.prototype.hasOwnProperty.call(map, key)) {{
              cell.textContent = formatMoney(map[key]);
            }}
          }});
        }} catch (_e) {{}}
      }}

      function isFixedExpenseEditableCell(cell) {{
        var tr = cell.closest && cell.closest('tr[data-pl-section="expense-detail"]');
        return !!(tr && tr.getAttribute('data-bucket') === 'fixed');
      }}

      function applyAmountToAllMonthsForRow(rowId, amount) {{
        document.querySelectorAll('[data-pl-editable="1"][data-row="' + rowId + '"]').forEach(function (c) {{
          c.textContent = formatMoney(amount);
        }});
        markTouched();
      }}

      function maybePropagateFixedMonthly(sourceCell, amount) {{
        if (!isFixedExpenseEditableCell(sourceCell)) return;
        if (amount === 0) return;
        var rowId = sourceCell.getAttribute('data-row');
        var month = sourceCell.getAttribute('data-month');
        var cells = Array.prototype.slice.call(
          document.querySelectorAll('[data-pl-editable="1"][data-row="' + rowId + '"]')
        );
        if (!cells.length) return;
        var allSame = cells.every(function (c) {{
          return parseMoney(c.textContent) === amount;
        }});
        if (allSame) return;
        var othersEmpty = cells.every(function (c) {{
          if (c.getAttribute('data-month') === month) return true;
          return parseMoney(c.textContent) === 0;
        }});
        if (othersEmpty) {{
          pushUndoSnapshot();
          applyAmountToAllMonthsForRow(rowId, amount);
          return;
        }}
        var msg = t(
          'この固定費を全ての月に同じ金額で反映しますか？',
          'Apply this fixed cost amount to all months?'
        );
        if (window.confirm(msg)) {{
          pushUndoSnapshot();
          applyAmountToAllMonthsForRow(rowId, amount);
        }}
      }}

      function bindPlEditableCells() {{
        document.querySelectorAll('[data-pl-editable="1"]').forEach(function (cell) {{
          if (cell.getAttribute('data-pl-bound') === '1') return;
          cell.setAttribute('data-pl-bound', '1');
          cell.addEventListener('focus', function () {{
            pushUndoSnapshot();
            markTouched();
          }});
          cell.addEventListener('input', function () {{
            markTouched();
          }});
          cell.addEventListener('blur', function () {{
            var n = parseMoney(cell.textContent);
            cell.textContent = formatMoney(n);
            maybePropagateFixedMonthly(cell, n);
            if (typeof refreshPlRatios === 'function') refreshPlRatios();
        if (typeof refreshPlYearTotals === 'function') refreshPlYearTotals();
            if (typeof refreshPlReferenceBudget === 'function') refreshPlReferenceBudget();
          }});
        }});
      }}

      function refreshPlExpenseAmountsFromStorage() {{
        loadSavedExpenses();
        bindPlEditableCells();
        applyColumnFocus();
        if (!plTouched) {{
          confirmedSnapshot = buildSnapshot();
          plSaved = true;
        }}
        syncUndoButton();
        if (typeof refreshPlRatios === 'function') refreshPlRatios();
        if (typeof refreshPlYearTotals === 'function') refreshPlYearTotals();
        if (typeof refreshPlReferenceBudget === 'function') refreshPlReferenceBudget();
      }}

      window.__plRefreshExpenseAmounts = refreshPlExpenseAmountsFromStorage;

      function plSave(showAlert) {{
        var map = {{}};
        document.querySelectorAll('[data-pl-editable="1"]').forEach(function (cell) {{
          var key = cell.getAttribute('data-row') + ':' + cell.getAttribute('data-month');
          map[key] = parseMoney(cell.textContent);
        }});
        try {{
          localStorage.setItem(storageKey(), JSON.stringify(map));
        }} catch (_e) {{}}
        confirmedSnapshot = buildSnapshot();
        plSaved = true;
        undoStack = [];
        syncUndoButton();
        try {{
          if (typeof writeMonthlyExpenseAllocationToMep === 'function') {{
            var mepResult = writeMonthlyExpenseAllocationToMep({{ year: plYear }});
            console.debug('[PL Phase C] monthly→MEP dailyExpenses write', mepResult);
          }} else if (typeof previewMonthlyExpenseAllocation === 'function') {{
            console.debug(
              '[PL Phase B] monthly→bizDay allocation preview (no MEP write)',
              previewMonthlyExpenseAllocation({{ year: plYear }})
            );
          }}
        }} catch (_mepErr) {{}}
        if (showAlert !== false) window.alert(t('保存しました。', 'Saved.'));
      }}

{close_chooser_js("plSave(false);", can_leave_without_chooser="plSaved && !hasUnsavedChanges()")}

      function isInternalLeaveLink(a) {{
        if (!a || !a.getAttribute) return false;
        if (a.id === 'global-nav-daily-btn') return true;
        var href = (a.getAttribute('href') || '').trim();
        if (!href || href === '#') return false;
        if (/^javascript:/i.test(href)) return false;
        if (a.target === '_blank') return false;
        if (/^https?:\\/\\//i.test(href)) return false;
        if (href.charAt(0) === '#') return false;
        if (a.classList && a.classList.contains('logo-link')) return false;
        return true;
      }}
      function resolveLeaveHref(a) {{
        if (a.id === 'global-nav-index-btn') {{
          var tierKey = 'kpiNavigator.subscriptionTier';
          try {{
            if ((sessionStorage.getItem(tierKey) || localStorage.getItem(tierKey)) === 'basic') {{
              var hrefBasic = a.getAttribute('data-href-basic');
              if (hrefBasic) return new URL(hrefBasic, window.location.href).href;
            }}
          }} catch (_e) {{}}
          var hrefPro = a.getAttribute('data-href-pro') || a.getAttribute('href') || '';
          if (hrefPro) return new URL(hrefPro, window.location.href).href;
        }}
        if (a.id === 'global-nav-daily-btn') {{
          return new URL({json.dumps(p["monthly"])} + '?open=daily', window.location.href).href;
        }}
        var href = a.getAttribute('href') || '';
        try {{
          return new URL(href, window.location.href).href;
        }} catch (_e) {{
          return href;
        }}
      }}
      function bindLeaveGuards() {{
        document.addEventListener(
          'click',
          function (e) {{
            var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
            if (!isInternalLeaveLink(a)) return;
            e.preventDefault();
            e.stopPropagation();
            var targetHref = resolveLeaveHref(a);
            requestLeaveNavigation().then(function (ok) {{
              if (ok) window.location.href = targetHref;
            }});
          }},
          true
        );
      }}

      function pushUndoSnapshot() {{
        var snap = [];
        document.querySelectorAll('[data-pl-editable="1"]').forEach(function (c) {{
          snap.push(c.textContent);
        }});
        if (undoStack.length) {{
          var top = undoStack[undoStack.length - 1];
          var same = top.length === snap.length;
          if (same) {{
            for (var i = 0; i < top.length; i++) {{
              if (top[i] !== snap[i]) {{ same = false; break; }}
            }}
          }}
          if (same) return;
        }}
        undoStack.push(snap);
        if (undoStack.length > 40) undoStack.shift();
        syncUndoButton();
      }}

      bindPlEditableCells();
      window.addEventListener('pl-expense-detail-rendered', function () {{
        refreshPlExpenseAmountsFromStorage();
        if (typeof fillDailyExpenseRowsFromMep === 'function') {{
          fillDailyExpenseRowsFromMep();
        }}
        if (typeof refreshPlRatios === 'function') refreshPlRatios();
        if (typeof refreshPlYearTotals === 'function') refreshPlYearTotals();
        if (typeof refreshPlReferenceBudget === 'function') refreshPlReferenceBudget();
      }});
      document.addEventListener('kpi:mepDataChanged', function (ev) {{
        var evYear = ev && ev.detail && Number(ev.detail.year);
        if (Number.isFinite(evYear) && evYear !== plYear) return;
        if (typeof fillDailyExpenseRowsFromMep === 'function') {{
          fillDailyExpenseRowsFromMep();
        }}
        if (typeof refreshIncomeBlock === 'function') {{
          refreshIncomeBlock();
        }}
        if (typeof refreshPlRatios === 'function') refreshPlRatios();
        if (typeof refreshPlYearTotals === 'function') refreshPlYearTotals();
        if (typeof refreshPlReferenceBudget === 'function') refreshPlReferenceBudget();
      }});
      document.addEventListener('kpi:dailySalesChanged', function () {{
        syncPlBusinessDays();
        if (typeof refreshIncomeBlock === 'function') {{
          refreshIncomeBlock();
        }}
        if (typeof refreshPlRatios === 'function') refreshPlRatios();
        if (typeof refreshPlYearTotals === 'function') refreshPlYearTotals();
        if (typeof refreshPlReferenceBudget === 'function') refreshPlReferenceBudget();
      }});

      if (btnUndo) {{
        btnUndo.addEventListener('click', function () {{
          if (!undoStack.length) return;
          var prev = undoStack.pop();
          document.querySelectorAll('[data-pl-editable="1"]').forEach(function (cell, idx) {{
            if (prev && prev[idx] !== undefined) cell.textContent = prev[idx];
          }});
          markTouched();
          syncUndoButton();
        }});
      }}

      if (btnSave) {{
        btnSave.addEventListener('click', function () {{
          plSave();
        }});
      }}

      // Upload CSV button is wired by pl_expense_import_client_js (income/expense chooser).

      function csvEscape(value) {{
        var text = String(value == null ? '' : value);
        if (/[",\\n\\r]/.test(text)) return '"' + text.replace(/"/g, '""') + '"';
        return text;
      }}

      function extractPlRowLabel(labelRow) {{
        if (!labelRow) return '';
        var editable = labelRow.querySelector('.pl-h-label__text');
        if (editable) return (editable.textContent || '').replace(/\\s+/g, ' ').trim();
        var th = labelRow.querySelector('th');
        if (th) return (th.textContent || '').replace(/\\s+/g, ' ').trim();
        return '';
      }}

      function extractPlDataCells(dataRow) {{
        if (!dataRow) return [];
        return Array.prototype.map.call(dataRow.querySelectorAll('td'), function (td) {{
          return (td.textContent || '').replace(/\\s+/g, ' ').trim();
        }});
      }}

      function appendPlExportPairs(rows, labelBodyId, dataBodyId) {{
        var labelBody = document.getElementById(labelBodyId);
        var dataBody = document.getElementById(dataBodyId);
        if (!labelBody || !dataBody) return;
        var labelRows = labelBody.querySelectorAll('tr');
        var dataRows = dataBody.querySelectorAll('tr');
        var count = Math.min(labelRows.length, dataRows.length);
        for (var i = 0; i < count; i++) {{
          var label = extractPlRowLabel(labelRows[i]);
          var cells = extractPlDataCells(dataRows[i]);
          if (!label && !cells.length) continue;
          rows.push([label].concat(cells));
        }}
      }}

      function buildPlExportCsv() {{
        var monthNames = isJa
          ? ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
          : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        var header = [''];
        monthNames.forEach(function (name) {{
          header.push(name + ' ' + t('金額', 'Amount'));
          header.push(name + ' ' + t('比率', 'Ratio'));
        }});
        var rows = [header];
        appendPlExportPairs(rows, 'pl-table-label-frozen-body', 'pl-table-frozen-body');
        appendPlExportPairs(rows, 'pl-table-label-body', 'pl-table-body');
        appendPlExportPairs(rows, 'pl-analyze-label-collapsible', 'pl-analyze-data-collapsible');
        appendPlExportPairs(rows, 'pl-table-label-profit-body', 'pl-table-profit-body');
        appendPlExportPairs(rows, 'pl-expense-detail-header-label', 'pl-expense-detail-header-data');
        appendPlExportPairs(rows, 'pl-expense-detail-label-body', 'pl-expense-detail-data-body');
        return rows
          .map(function (row) {{
            return row.map(csvEscape).join(',');
          }})
          .join('\\n');
      }}

      function downloadPlExcel() {{
        var csv = '\\uFEFF' + buildPlExportCsv();
        var blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8' }});
        var url = URL.createObjectURL(blob);
        var link = document.createElement('a');
        link.href = url;
        link.download = 'PL_' + plYear + '.csv';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }}

      if (btnExcel) {{
        btnExcel.addEventListener('click', downloadPlExcel);
      }}

      if (yearSelect) {{
        yearSelect.addEventListener('change', function () {{
          requestLeaveNavigation().then(function (ok) {{
            if (!ok) {{
              yearSelect.value = String(plYear);
              return;
            }}
            var next = new URLSearchParams(window.location.search);
            next.set('year', yearSelect.value);
            if (!next.get('from') && plParams.get('from')) next.set('from', plParams.get('from'));
            if (!next.get('month') && plParams.get('month')) next.set('month', plParams.get('month'));
            window.location.search = '?' + next.toString();
          }});
        }});
      }}

      window.addEventListener('beforeunload', function (ev) {{
        if (canLeaveWithoutChooser()) return;
        ev.preventDefault();
        ev.returnValue = '';
      }});

      document.addEventListener('keydown', function (ev) {{
        if (!(ev.ctrlKey || ev.metaKey) || ev.key !== 'z') return;
        if (!undoStack.length) return;
        ev.preventDefault();
        if (btnUndo) btnUndo.click();
      }});

      var ANNUAL_DAILY_KEY = 'kpiNavigator.annualDailyShared';

      window.__KPI_DATA_GATEWAY = window.__KPI_DATA_GATEWAY || {{
        getJson: function (key) {{
          try {{
            var raw = localStorage.getItem(key);
            if (!raw) return null;
            var parsed = JSON.parse(raw);
            return parsed && typeof parsed === 'object' ? parsed : null;
          }} catch (_e) {{
            return null;
          }}
        }},
        setJson: function (key, value) {{
          try {{
            localStorage.setItem(key, JSON.stringify(value));
            return true;
          }} catch (_e) {{
            return false;
          }}
        }}
      }};

      function pad2(n) {{
        return n < 10 ? '0' + n : String(n);
      }}

      function loadAnnualDailyMaps() {{
        var parsed = window.__KPI_DATA_GATEWAY.getJson(ANNUAL_DAILY_KEY) || {{}};
        return {{
          businessDayByDate: parsed.businessDayByDate || {{}},
          targetSalesByDate: parsed.targetSalesByDate || {{}}
        }};
      }}

      /** Monthly Edit 営業日チェックと同じ前提（未設定日は営業日扱い）。 */
      function isBizDayIso(iso, bmap, tmap) {{
        if (Object.prototype.hasOwnProperty.call(bmap, iso)) return !!bmap[iso];
        if (Object.prototype.hasOwnProperty.call(tmap, iso)) {{
          var n = Number(tmap[iso]);
          return Number.isFinite(n) ? n !== 0 : true;
        }}
        return true;
      }}

      function countBizDaysInMonth(year, month0, bmap, tmap) {{
        var daysInMonth = new Date(year, month0 + 1, 0).getDate();
        var count = 0;
        for (var day = 1; day <= daysInMonth; day++) {{
          var iso = year + '-' + pad2(month0 + 1) + '-' + pad2(day);
          if (isBizDayIso(iso, bmap, tmap)) count++;
        }}
        return count;
      }}

      var PL_YEAR_STORE_KEY = 'kpiNavigator.kpiYearStore';

      /** 営業日/日次売上の真実源（Annual・MEP・Insight と同一の kpiYearStore）。 */
      function plReadYearStore() {{
        try {{
          return window.__KPI_DATA_GATEWAY.getJson(PL_YEAR_STORE_KEY) || null;
        }} catch (_e) {{
          return null;
        }}
      }}

      /**
       * Annual/Insight/MEP と同一の営業日判定。
       * 優先順位: timeline.businessDays[iso] 明示 → dailySales[iso]===0 は休業
       *           → 上記なしは土日を既定休（平日は既定営業）。
       */
      function plIsCalendarBizDay(store, y, m0, day) {{
        var d = new Date(y, m0, day);
        if (d.getFullYear() !== y || d.getMonth() !== m0 || d.getDate() !== day) return false;
        var dow = d.getDay();
        var isWeekend = dow === 0 || dow === 6;
        var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
        var tl = (store && store.timeline) || {{}};
        var bmap = tl.businessDays || {{}};
        var smap = tl.dailySales || {{}};
        if (Object.prototype.hasOwnProperty.call(bmap, iso)) return !!bmap[iso];
        if (Object.prototype.hasOwnProperty.call(smap, iso)) {{
          var n = Number(smap[iso]);
          if (!Number.isFinite(n)) return !isWeekend;
          if (n === 0) return false;
          return true;
        }}
        return !isWeekend;
      }}

      function countBizDaysInMonthStore(store, year, month0) {{
        var daysInMonth = new Date(year, month0 + 1, 0).getDate();
        var count = 0;
        for (var day = 1; day <= daysInMonth; day++) {{
          if (plIsCalendarBizDay(store, year, month0, day)) count++;
        }}
        return count;
      }}

      function syncPlBusinessDays() {{
        var store = plReadYearStore();
        document.querySelectorAll('[data-pl-bizdays-month]').forEach(function (cell) {{
          var mi = Number(cell.getAttribute('data-pl-bizdays-month'));
          if (!Number.isFinite(mi) || mi < 0 || mi > 11) return;
          var span = cell.querySelector('.pl-span-cell__text, .pl-amt-cell__text');
          if (!span) return;
          span.textContent = String(countBizDaysInMonthStore(store, plYear, mi));
        }});
      }}

{pl_monthly_allocate_client_js()}
{pl_expense_import_client_js()}
{pl_income_client_js()}
{pl_ratio_client_js()}
{pl_reference_budget_client_js()}
{pl_year_total_client_js()}

      window.addEventListener('storage', function (ev) {{
        if (ev.key === ANNUAL_DAILY_KEY || ev.key === PL_YEAR_STORE_KEY) {{
          syncPlBusinessDays();
        }}
      }});
      document.addEventListener('annual:businessDayMapChanged', function () {{
        syncPlBusinessDays();
      }});
      document.addEventListener('kpi:businessDayChanged', function () {{
        syncPlBusinessDays();
      }});
      document.addEventListener('kpi:readSurfacesRefresh', function () {{
        syncPlBusinessDays();
      }});

      populateYearSelect();
      setupEditBackLink();
      syncPlBusinessDays();
      var cornerYear = document.getElementById('pl-corner-year');
      if (cornerYear) cornerYear.textContent = String(plYear);
      refreshPlExpenseAmountsFromStorage();
      if (typeof fillDailyExpenseRowsFromMep === 'function') {{
        fillDailyExpenseRowsFromMep();
      }}
      if (typeof refreshIncomeBlock === 'function') {{
        refreshIncomeBlock();
      }}
      if (typeof refreshPlRatios === 'function') {{
        refreshPlRatios();
      }}
      if (typeof refreshPlYearTotals === 'function') {{
        refreshPlYearTotals();
      }}
      if (typeof refreshPlReferenceBudget === 'function') {{
        refreshPlReferenceBudget();
      }}
      applyColumnFocus();
      var insightBtnInit = document.getElementById('global-nav-index-btn');
      if (insightBtnInit) {{
        var hrefProInit = insightBtnInit.getAttribute('data-href-pro');
        if (hrefProInit) insightBtnInit.setAttribute('href', hrefProInit);
      }}
      bindLeaveGuards();
      syncUndoButton();

      var tgl = document.getElementById('pl-kpi-toggle');
      if (tgl && body) {{
        tgl.addEventListener('click', function () {{
          var collapsed = body.classList.toggle('pl-kpi-collapsed');
          tgl.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
          var icon = tgl.querySelector('.pl-group-toggle__icon');
          if (icon) icon.textContent = collapsed ? '▶' : '▼';
        }});
      }}
    }})();
  </script>
</body>
</html>
"""


def main() -> None:
    ja_path = ROOT / "app/profit/pl/index.html"
    en_path = ROOT / "en/app/profit/pl/index.html"
    ja_path.parent.mkdir(parents=True, exist_ok=True)
    en_path.parent.mkdir(parents=True, exist_ok=True)
    ja_path.write_text(
        render_page(
            "ja",
            'data-url-en="../../../en/app/profit/pl/index.html" data-url-ja="index.html"',
        ),
        encoding="utf-8",
    )
    en_path.write_text(
        render_page(
            "en",
            'data-url-en="index.html" data-url-ja="../../../app/profit/pl/index.html"',
        ),
        encoding="utf-8",
    )
    print("Wrote", ja_path, en_path)


if __name__ == "__main__":
    main()
